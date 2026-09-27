#!/usr/bin/env python3
"""Zero-optimizer P1-vs-P2 activation/domain-shift diagnostic.

Uses the frozen V3 model and decoder-V2 thresholds without fitting or threshold
search. Compares matched P1/P2 prepared crops, feature statistics, model-output
statistics, and reference-onset admission behavior.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import torch

from evaluation.event_decoder_v2 import (
    NUM_CLASSES, NUM_FRETS, NUM_STRINGS, SILENCE_CLASS,
    ONSET_THRESHOLD, STATE_ACTIVE_THRESHOLD, decode_event_list_v2,
)
from tiny_fit_pilot_v1 import TinyEventFitModel, _sha256_file

SCHEMA = "astra-p1-p2-activation-domain-shift-diagnostic-v1"
WINDOW_FRAMES = 2


def _q(a, q):
    a=np.asarray(a, dtype=np.float64).reshape(-1)
    return float(np.quantile(a, q)) if a.size else None


def summarize_array(a):
    a=np.asarray(a, dtype=np.float64)
    flat=a.reshape(-1)
    return {
        "count": int(flat.size),
        "mean": float(flat.mean()),
        "std": float(flat.std()),
        "min": float(flat.min()),
        "max": float(flat.max()),
        "p01": _q(flat,.01),
        "p10": _q(flat,.10),
        "p50": _q(flat,.50),
        "p90": _q(flat,.90),
        "p99": _q(flat,.99),
        "absMean": float(np.abs(flat).mean()),
        "l2Rms": float(np.sqrt(np.mean(flat*flat))),
    }


def _load_population(root, performer):
    root=Path(root)
    rows=[]
    for meta_path in sorted(root.glob("*/meta.json")):
        meta=json.loads(meta_path.read_text())
        if meta["performer"] != performer:
            raise RuntimeError(f"unexpected performer in {meta_path}")
        feature_path=meta_path.parent/"features.npy"
        if _sha256_file(feature_path) != meta["featureSha256"]:
            raise RuntimeError("prepared feature hash mismatch")
        x=np.load(feature_path, allow_pickle=False).astype(np.float32, copy=False)
        if x.ndim != 2 or x.shape[1] != 192:
            raise RuntimeError("unexpected prepared feature shape")
        rows.append((meta,x))
    if len(rows)!=4:
        raise RuntimeError(f"{performer} diagnostic requires exactly four examples")
    return rows


def _category_map(rows):
    out={}
    for meta,x in rows:
        cat=meta["category"]
        if cat in out:
            raise RuntimeError("duplicate category in diagnostic population")
        out[cat]=(meta,x)
    expected={"chords","scales","singlenotes","techniques"}
    if set(out)!=expected:
        raise RuntimeError(f"unexpected diagnostic categories: {sorted(out)}")
    return out


def _outputs(model, x):
    with torch.no_grad():
        out=model(torch.as_tensor(x[None,...], dtype=torch.float32))
    state_logits=out["state"][0].detach().cpu()
    onset_logits=out["onset"][0].detach().cpu()
    state_prob=torch.softmax(
        state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES), dim=-1
    ).numpy()
    onset_prob=torch.sigmoid(onset_logits).numpy()
    return state_logits.numpy(), onset_logits.numpy(), state_prob, onset_prob


def _references(meta):
    return list(meta["prepared"]["scorableEvents"])


def _admission_summary(state_prob,onset_prob):
    best=np.argmax(state_prob[:,:,:NUM_FRETS], axis=2)
    bestp=np.take_along_axis(
        state_prob[:,:,:NUM_FRETS], best[:,:,None], axis=2
    )[:,:,0]
    silence=state_prob[:,:,SILENCE_CLASS]
    onset_ok=onset_prob>=ONSET_THRESHOLD
    state_ok=(bestp>=STATE_ACTIVE_THRESHOLD)&(bestp>silence)
    joint=onset_ok&state_ok
    return {
        "frameStringCount": int(onset_ok.size),
        "onsetOnlyPassCount": int(onset_ok.sum()),
        "stateOnlyPassCount": int(state_ok.sum()),
        "jointAdmissionPassCount": int(joint.sum()),
        "onsetPassFraction": float(onset_ok.mean()),
        "statePassFraction": float(state_ok.mean()),
        "jointPassFraction": float(joint.mean()),
    }


def _probe_reference(event, hop, state_prob, onset_prob):
    string=int(event["string"]); fret=int(event["fret"])
    frame=int(round(float(event["start"])/hop))
    frame=max(0,min(state_prob.shape[0]-1,frame))
    lo=max(0,frame-WINDOW_FRAMES)
    hi=min(state_prob.shape[0],frame+WINDOW_FRAMES+1)

    def frame_row(k):
        row=state_prob[k,string]
        best=int(np.argmax(row[:NUM_FRETS]))
        bestp=float(row[best])
        silence=float(row[SILENCE_CLASS])
        onset=float(onset_prob[k,string])
        truep=float(row[fret])
        onset_ok=onset>=ONSET_THRESHOLD
        state_ok=(best==fret and truep>=STATE_ACTIVE_THRESHOLD and truep>silence)
        return {
            "frame":k,
            "timeSeconds":float(k*hop),
            "onsetProbability":onset,
            "onsetPass":bool(onset_ok),
            "trueFretProbability":truep,
            "silenceProbability":silence,
            "trueFretMinusSilence":float(truep-silence),
            "bestActiveFret":best,
            "bestActiveProbability":bestp,
            "trueStatePass":bool(state_ok),
            "jointTrueAdmission":bool(onset_ok and state_ok),
        }

    rows=[frame_row(k) for k in range(lo,hi)]
    center=frame_row(frame)
    best_onset=max(rows,key=lambda r:r["onsetProbability"])
    best_joint=max(rows,key=lambda r:(r["jointTrueAdmission"],r["onsetProbability"],r["trueFretProbability"]))
    return {
        "referenceId":event["id"],
        "string":string,
        "fret":fret,
        "referenceStartSeconds":float(event["start"]),
        "referenceFrame":frame,
        "center":center,
        "windowFrames":[lo,hi-1],
        "windowMaxOnsetProbability":float(best_onset["onsetProbability"]),
        "windowMaxOnsetFrame":int(best_onset["frame"]),
        "windowAnyOnsetPass":bool(any(r["onsetPass"] for r in rows)),
        "windowAnyTrueStatePass":bool(any(r["trueStatePass"] for r in rows)),
        "windowAnyJointTrueAdmission":bool(any(r["jointTrueAdmission"] for r in rows)),
        "bestWindowRow":best_joint,
    }


def _classify(probes):
    if not probes:
        return "no_reference_events"
    onset=sum(1 for p in probes if p["windowAnyOnsetPass"])
    state=sum(1 for p in probes if p["windowAnyTrueStatePass"])
    joint=sum(1 for p in probes if p["windowAnyJointTrueAdmission"])
    n=len(probes)
    if joint==0:
        if onset==0 and state==0:
            return "both_heads_or_representation_domain_collapse"
        if onset==0 and state>0:
            return "onset_head_generalization_failure"
        if state==0 and onset>0:
            return "state_head_or_representation_failure"
        return "onset_state_admission_misalignment"
    if joint<n:
        return "partial_generalization_failure"
    return "reference_admission_healthy"


def _one_example(model, meta, x):
    state_logits,onset_logits,state_prob,onset_prob=_outputs(model,x)
    hop=float(meta["hopSeconds"])
    probes=[_probe_reference(e,hop,state_prob,onset_prob) for e in _references(meta)]
    decoded=decode_event_list_v2(
        torch.as_tensor(state_logits), torch.as_tensor(onset_logits),
        hop_seconds=hop, id_prefix="diag"
    )
    return {
        "captureKey":meta["captureKey"],
        "category":meta["category"],
        "featureSha256":meta["featureSha256"],
        "targetSha256":meta["prepared"]["targetSha256"],
        "cropSelection":meta["cropSelection"],
        "referenceCount":len(probes),
        "decodedEventCount":len(decoded),
        "featureSummary":summarize_array(x),
        "onsetProbabilitySummary":summarize_array(onset_prob),
        "onsetLogitSummary":summarize_array(onset_logits),
        "stateLogitSummary":summarize_array(state_logits),
        "admission":_admission_summary(state_prob,onset_prob),
        "referenceProbes":probes,
        "referenceOnsetPassCount":sum(1 for p in probes if p["windowAnyOnsetPass"]),
        "referenceStatePassCount":sum(1 for p in probes if p["windowAnyTrueStatePass"]),
        "referenceJointAdmissionCount":sum(1 for p in probes if p["windowAnyJointTrueAdmission"]),
        "diagnosticClass":_classify(probes),
    }


def _paired_delta(p1,p2):
    def d(path):
        a=p1
        b=p2
        for key in path:
            a=a[key]; b=b[key]
        return {"p1":a,"p2":b,"deltaP2MinusP1":float(b-a)}
    return {
        "featureMean":d(["featureSummary","mean"]),
        "featureStd":d(["featureSummary","std"]),
        "featureAbsMean":d(["featureSummary","absMean"]),
        "featureL2Rms":d(["featureSummary","l2Rms"]),
        "onsetProbabilityMean":d(["onsetProbabilitySummary","mean"]),
        "onsetProbabilityP99":d(["onsetProbabilitySummary","p99"]),
        "onsetProbabilityMax":d(["onsetProbabilitySummary","max"]),
        "jointAdmissionPassFraction":d(["admission","jointPassFraction"]),
        "statePassFraction":d(["admission","statePassFraction"]),
        "onsetPassFraction":d(["admission","onsetPassFraction"]),
    }


def run(args):
    p1=_category_map(_load_population(args.p1_dir,"P1"))
    p2=_category_map(_load_population(args.p2_dir,"P2"))
    ckpt=torch.load(args.model,map_location="cpu")
    if ckpt.get("schema")!="astra-tiny-fit-pilot-v1":
        raise RuntimeError("unexpected V3 checkpoint schema")
    if ckpt.get("optimizerSteps")!=200:
        raise RuntimeError("unexpected frozen optimizer-step identity")
    model=TinyEventFitModel()
    model.load_state_dict(ckpt["stateDict"],strict=True)
    model.eval()

    pairs=[]
    all_p1=[]; all_p2=[]
    for cat in ("chords","scales","singlenotes","techniques"):
        m1,x1=p1[cat]; m2,x2=p2[cat]
        r1=_one_example(model,m1,x1)
        r2=_one_example(model,m2,x2)
        all_p1.append(r1); all_p2.append(r2)
        pairs.append({
            "category":cat,
            "p1":r1,
            "p2":r2,
            "pairedDeltas":_paired_delta(r1,r2),
        })

    p1_probes=[p for r in all_p1 for p in r["referenceProbes"]]
    p2_probes=[p for r in all_p2 for p in r["referenceProbes"]]
    p1_class=_classify(p1_probes)
    p2_class=_classify(p2_probes)

    receipt={
        "schema":SCHEMA,
        "sourceModel":{
            "runId":36280547470,
            "artifactId":10918434248,
            "modelSha256":_sha256_file(args.model),
        },
        "execution":{
            "optimizerStepsExecuted":0,
            "thresholdsChanged":False,
            "thresholdSearchExecuted":False,
            "modelWeightsChanged":False,
            "p1MediaAccessed":True,
            "p2MediaAccessed":True,
            "p3Opened":False,
        },
        "thresholds":{
            "stateActive":STATE_ACTIVE_THRESHOLD,
            "onset":ONSET_THRESHOLD,
            "referenceProbeWindowFrames":WINDOW_FRAMES,
        },
        "population":{
            "p1CaptureKeys":[r["captureKey"] for r in all_p1],
            "p2CaptureKeys":[r["captureKey"] for r in all_p2],
            "pairedByCategory":True,
            "examplesPerPerformer":4,
        },
        "summary":{
            "p1DiagnosticClass":p1_class,
            "p2DiagnosticClass":p2_class,
            "p1DecodedEventCount":sum(r["decodedEventCount"] for r in all_p1),
            "p2DecodedEventCount":sum(r["decodedEventCount"] for r in all_p2),
            "p1ReferenceCount":len(p1_probes),
            "p2ReferenceCount":len(p2_probes),
            "p1ReferenceOnsetPassCount":sum(1 for p in p1_probes if p["windowAnyOnsetPass"]),
            "p2ReferenceOnsetPassCount":sum(1 for p in p2_probes if p["windowAnyOnsetPass"]),
            "p1ReferenceStatePassCount":sum(1 for p in p1_probes if p["windowAnyTrueStatePass"]),
            "p2ReferenceStatePassCount":sum(1 for p in p2_probes if p["windowAnyTrueStatePass"]),
            "p1ReferenceJointAdmissionCount":sum(1 for p in p1_probes if p["windowAnyJointTrueAdmission"]),
            "p2ReferenceJointAdmissionCount":sum(1 for p in p2_probes if p["windowAnyJointTrueAdmission"]),
        },
        "pairs":pairs,
        "meaning":"Diagnostic only. No thresholds were searched or changed. Results identify where frozen P1-trained model admission fails on P2; they do not authorize training, P3, or production use.",
        "guards":{
            "automaticRetry":False,
            "fullTrainingAuthorized":False,
            "p3Opened":False,
            "customerDeliveryEligible":False,
        },
    }
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("P1_P2_ACTIVATION_DIAGNOSTIC="+json.dumps(receipt["summary"],sort_keys=True))


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p1-dir",required=True)
    p.add_argument("--p2-dir",required=True)
    p.add_argument("--model",required=True)
    p.add_argument("--out",required=True)
    run(p.parse_args())


if __name__=="__main__":
    main()
