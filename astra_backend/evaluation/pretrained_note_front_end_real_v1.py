#!/usr/bin/env python3
"""Authorized zero-optimizer Basic Pitch Stage-A feasibility runner."""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
from evaluation.pretrained_note_front_end_v1 import (
    P1_KEYS,P2_KEYS,BASIC_PITCH_VERSION,ONSET_THRESHOLD,FRAME_THRESHOLD,MIN_NOTE_LENGTH_MS,
    validate_meta,reference_pitch_events,basic_pitch_to_crop_events,score_pitch_events,
    run_basic_pitch,basic_pitch_model_identity,sha256_file,
)

EXPECTED_MODEL_SHA="3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676"

def load_meta(root,key):
    matches=[]
    for p in Path(root).glob("*/meta.json"):
        m=json.loads(p.read_text())
        if m.get("captureKey")==key:
            matches.append((p,m))
    if len(matches)!=1: raise RuntimeError(f"expected exactly one meta for {key}")
    _,m=matches[0]
    validate_meta(m,key)
    required=("audioSourceSha256","midiSourceSha256","featureSha256")
    if any(not m.get(k) for k in required): raise RuntimeError("missing prepared source identity")
    if not m["prepared"].get("sourceEventSha256") or not m["prepared"].get("targetSha256"):
        raise RuntimeError("missing prepared target/source-event identity")
    return m

def evaluate_capture(root,key,audio):
    m=load_meta(root,key)
    if sha256_file(audio)!=m["audioSourceSha256"]: raise RuntimeError("audio source identity mismatch")
    refs,amb=reference_pitch_events(m)
    crop=m["prepared"]["crop"]
    start=float(crop["startSeconds"]); end=float(crop["endSeconds"])
    notes=run_basic_pitch(audio)
    preds=basic_pitch_to_crop_events(notes,start,end)
    scores=score_pitch_events(preds,refs)
    return {
      "captureKey":key,"performer":m["performer"],"category":m["category"],
      "crop":{"startSeconds":start,"endSeconds":end,"frames":crop["frames"]},
      "identities":{
        "audioSourceSha256":m["audioSourceSha256"],"midiSourceSha256":m["midiSourceSha256"],
        "featureSha256":m["featureSha256"],"sourceEventSha256":m["prepared"]["sourceEventSha256"],
        "targetSha256":m["prepared"]["targetSha256"]
      },
      "rawBasicPitchNoteCount":len(notes),"cropPredictionCount":len(preds),
      "rawReferenceCount":len(refs),"duplicateSamePitchAmbiguityGroups":amb,
      "duplicateSamePitchAmbiguityGroupCount":len(amb),
      "scores":scores,
    }

def aggregate(rows):
    tp=fp=fn=0
    for r in rows:
        s=r["scores"]["pitchOnset"]; tp+=s["truePositive"]; fp+=s["falsePositive"]; fn+=s["falseNegative"]
    pred=tp+fp; ref=tp+fn
    p=tp/pred if pred else (1.0 if ref==0 else 0.0)
    rec=tp/ref if ref else 1.0
    f1=2*p*rec/(p+rec) if p+rec else 0.0
    return {"truePositive":tp,"falsePositive":fp,"falseNegative":fn,"precision":p,"recall":rec,"f1":f1}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p1-dir",required=True); ap.add_argument("--p2-dir",required=True)
    ap.add_argument("--audio-map",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args(); start=time.monotonic()
    identity=basic_pitch_model_identity()
    if identity["packageVersion"]!=BASIC_PITCH_VERSION or identity["modelSha256"]!=EXPECTED_MODEL_SHA:
        raise RuntimeError("Basic Pitch frozen model identity mismatch")
    amap=json.load(open(args.audio_map))
    expected=list(P1_KEYS)+list(P2_KEYS)
    if set(amap)!=set(expected): raise RuntimeError("audio map capture allowlist mismatch")
    rows=[]
    for key in expected:
        root=args.p1_dir if key.startswith("P1|") else args.p2_dir
        rows.append(evaluate_capture(root,key,amap[key]))
    by_perf={p:aggregate([r for r in rows if r["performer"]==p]) for p in ("P1","P2")}
    overall=aggregate(rows)
    pair_macro={}
    for cat in ("chords","scales","singlenotes","techniques"):
        vals=[r["scores"]["pitchOnset"]["f1"] for r in rows if r["category"]==cat]
        if len(vals)!=2: raise RuntimeError("content pair incomplete")
        pair_macro[cat]=sum(vals)/2
    p1p2gap=abs(by_perf["P1"]["f1"]-by_perf["P2"]["f1"])
    crit={
      "aggregatePitchOnsetF1AtLeast0_70":overall["f1"]>=.70,
      "aggregatePitchOnsetRecallAtLeast0_70":overall["recall"]>=.70,
      "p1AggregatePitchOnsetF1AtLeast0_60":by_perf["P1"]["f1"]>=.60,
      "p2AggregatePitchOnsetF1AtLeast0_60":by_perf["P2"]["f1"]>=.60,
      "eachContentPairMacroPitchOnsetF1AtLeast0_50":all(v>=.50 for v in pair_macro.values()),
      "absoluteP1P2F1GapAtMost0_15":p1p2gap<=.15,
      "zeroOptimizerAndZeroThresholdSearch":True,
      "allEightIdentitiesVerifiedAndUnresolvedZero":len(rows)==8,
    }
    result={
      "schema":"astra-pretrained-note-front-end-feasibility-result-v1",
      "frontEnd":{"name":"Basic Pitch","packageVersion":BASIC_PITCH_VERSION,**identity,
                  "onsetThreshold":ONSET_THRESHOLD,"frameThreshold":FRAME_THRESHOLD,
                  "minimumNoteLengthMs":MIN_NOTE_LENGTH_MS},
      "execution":{"optimizerStepsExecuted":0,"thresholdSearchExecuted":False,"thresholdsChanged":False,
                   "modelMutation":False,"automaticRetry":False,"p3Opened":False,
                   "runtimeSeconds":time.monotonic()-start},
      "aggregate":overall,"byPerformer":by_perf,"contentPairMacroF1":pair_macro,
      "absoluteP1P2F1Gap":p1p2gap,"criteria":crit,"positiveGate":all(crit.values()),
      "captures":rows,
      "claimBoundary":"Pitch/onset feasibility only; no string/fret, unseen-performer, P3, or customer-readiness claim."
    }
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
