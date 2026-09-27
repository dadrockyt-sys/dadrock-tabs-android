#!/usr/bin/env python3
"""Combined zero-optimizer P1/P2 diagnostic.

This package is intentionally descriptive. It reproduces the frozen scorer,
guards exact identities, keeps unmatched correspondences, separates attack /
sustain / silence controls, exposes frozen head projections and state margins,
and records fixed neighboring-frame deltas without fitting or threshold search.
"""
from __future__ import annotations

import argparse, json, math
from pathlib import Path
import numpy as np
import torch

from evaluation.event_contract_v2 import Event, score_events
from evaluation.event_decoder_v2 import (
    NUM_CLASSES, NUM_FRETS, NUM_STRINGS, SILENCE_CLASS,
    ONSET_THRESHOLD, STATE_ACTIVE_THRESHOLD, decode_event_list_v2,
)
from evaluation.tiny_fit_v3_diagnostic import boundary_exclusions
from tiny_fit_pilot_v1 import TinyEventFitModel, _sha256_file

SCHEMA="astra-p1-p2-combined-offline-diagnostic-v1"
FRAMES=200
FEATURE_DIM=192
WINDOW=2
P1_KEYS=(
"P1|chords|Drop3_7|directinput","P1|scales|Ab|directinput",
"P1|singlenotes|allsinglenotes|directinput","P1|techniques|PalmMute|directinput")
P2_KEYS=tuple(k.replace("P1|","P2|",1) for k in P1_KEYS)

def _event(r):
    return Event(r["id"],int(r["string"]),int(r["fret"]),float(r["start"]),float(r["end"]))

def _suffix_identity(e):
    rid=str(e["id"])
    cap=rid.split(":",1)
    return cap[1] if len(cap)==2 else rid

def load_population(root, performer, expected_keys):
    rows=[]
    for mp in sorted(Path(root).glob("*/meta.json")):
        m=json.loads(mp.read_text()); fp=mp.parent/"features.npy"
        if m.get("performer")!=performer: raise RuntimeError("performer identity mismatch")
        if m.get("captureKey") not in expected_keys: raise RuntimeError("capture identity mismatch")
        if m.get("captureView")!="directinput": raise RuntimeError("capture view mismatch")
        if int(m["prepared"].get("unresolvedLabelCount",-1))!=0: raise RuntimeError("unresolved selected labels")
        if _sha256_file(fp)!=m["featureSha256"]: raise RuntimeError("feature hash mismatch")
        x=np.load(fp,allow_pickle=False)
        if x.shape!=(FRAMES,FEATURE_DIM): raise RuntimeError("expected exact 200x192 feature crop")
        if not np.isfinite(x).all(): raise RuntimeError("non-finite feature array")
        rows.append((m,x.astype(np.float32,copy=False)))
    if {m["captureKey"] for m,_ in rows}!=set(expected_keys): raise RuntimeError("exact capture allowlist mismatch")
    return {m["category"]:(m,x) for m,x in rows}

def correspond(p1_events,p2_events):
    """Conservative identity match; never positional zip."""
    left={(_suffix_identity(e),int(e["string"]),int(e["fret"])):e for e in p1_events}
    right={(_suffix_identity(e),int(e["string"]),int(e["fret"])):e for e in p2_events}
    keys=sorted(set(left)&set(right))
    return {
      "matches":[{"identity":list(k),"p1Id":left[k]["id"],"p2Id":right[k]["id"]} for k in keys],
      "unmatchedP1":[e["id"] for k,e in left.items() if k not in right],
      "unmatchedP2":[e["id"] for k,e in right.items() if k not in left],
    }

def projection_identity(weight,bias,h1,h2):
    z1=float(np.dot(weight,h1)+bias); z2=float(np.dot(weight,h2)+bias)
    projected=float(np.dot(weight,h2-h1))
    return {"z1":z1,"z2":z2,"delta":z2-z1,"projectedDelta":projected,
            "biasCancelsError":float((z2-z1)-projected)}

def _outputs(model,x):
    xt=torch.as_tensor(x[None],dtype=torch.float32)
    with torch.no_grad():
        h=model.encoder(xt)[0]
        state=model.state_head(h)
        onset=model.onset_head(h)
    sp=torch.softmax(state.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1).cpu().numpy()
    op=torch.sigmoid(onset).cpu().numpy()
    return h.cpu().numpy(),state.cpu().numpy(),onset.cpu().numpy(),sp,op

def _frame_probe(k,string,fret,h,state_logits,onset_logits,sp,op,model):
    row=sp[k,string]; best=int(np.argmax(row[:NUM_FRETS]))
    incorrect=[i for i in range(NUM_FRETS) if i!=fret]
    strongest=max(incorrect,key=lambda i:float(row[i])) if incorrect else fret
    ow=model.onset_head.weight[string].detach().cpu().numpy()
    ob=float(model.onset_head.bias[string].detach().cpu())
    dot=float(np.dot(ow,h[k])); z=float(onset_logits[k,string])
    true_logit=float(state_logits[k,string*NUM_CLASSES+fret])
    silence_logit=float(state_logits[k,string*NUM_CLASSES+SILENCE_CLASS])
    wrong_logit=float(state_logits[k,string*NUM_CLASSES+strongest])
    return {
      "frame":int(k),"onsetProbability":float(op[k,string]),"onsetLogit":z,
      "onsetWdotH":dot,"onsetBias":ob,"projectionReconstructionError":float(z-(dot+ob)),
      "trueFretProbability":float(row[fret]),"silenceProbability":float(row[SILENCE_CLASS]),
      "strongestIncorrectFret":int(strongest),"strongestIncorrectProbability":float(row[strongest]),
      "trueVsSilenceLogitMargin":true_logit-silence_logit,
      "trueVsStrongestIncorrectLogitMargin":true_logit-wrong_logit,
      "onsetPass":bool(op[k,string]>=ONSET_THRESHOLD),
      "trueStatePass":bool(best==fret and row[fret]>=STATE_ACTIVE_THRESHOLD and row[fret]>row[SILENCE_CLASS]),
    }

def _control_frames(events,hop,nframes):
    active=set(); attacks=set(); sustain=[]
    for e in events:
        s=int(e["string"]); a=max(0,min(nframes-1,int(round(float(e["start"])/hop))))
        attacks.add((a,s))
        lo=max(0,int(math.floor(float(e["start"])/hop))); hi=min(nframes-1,int(math.ceil(float(e["end"])/hop)))
        for k in range(lo,hi+1): active.add((k,s))
        for k in range(a+3,hi-1):
            sustain.append((k,s,int(e["fret"])))
    silence=[(k,s) for k in range(nframes) for s in range(NUM_STRINGS) if (k,s) not in active]
    return sorted(attacks),sustain,silence

def _example(model,m,x):
    h,sl,ol,sp,op=_outputs(model,x); hop=float(m["hopSeconds"])
    refs=list(m["prepared"]["scorableEvents"])
    preds=decode_event_list_v2(torch.as_tensor(sl),torch.as_tensor(ol),hop_seconds=hop,id_prefix="combined")
    exclusions, exclusion_records=boundary_exclusions(m["prepared"])
    raw=score_events(preds,[_event(e) for e in refs],onset_tolerance=.05,offset_tolerance=.05)
    scored=score_events(preds,[_event(e) for e in refs],onset_tolerance=.05,offset_tolerance=.05,excluded_intervals=exclusions)
    attacks,sustain,silence=_control_frames(refs,hop,len(x))
    probes=[]
    for e in refs:
        k=max(0,min(len(x)-1,int(round(float(e["start"])/hop)))); s=int(e["string"]); f=int(e["fret"])
        exact=_frame_probe(k,s,f,h,sl,ol,sp,op,model)
        win=[_frame_probe(j,s,f,h,sl,ol,sp,op,model) for j in range(max(0,k-WINDOW),min(len(x),k+WINDOW+1))]
        dprev=float(np.linalg.norm(x[k]-x[k-1])) if k>0 else None
        dnext=float(np.linalg.norm(x[k+1]-x[k])) if k+1<len(x) else None
        probes.append({"id":e["id"],"string":s,"fret":f,"referenceFrame":k,
                       "exactCenter":exact,"fixedPlusMinus2":win,
                       "featureDeltaFromPreviousL2":dprev,"featureDeltaToNextL2":dnext})
    def ctrl(rows,kind):
        out=[]
        for item in rows[:64]:
            k,s=item[0],item[1]
            f=item[2] if len(item)>2 else 0
            p=_frame_probe(k,s,f,h,sl,ol,sp,op,model)
            out.append({"kind":kind,**p,
                        "featureDeltaFromPreviousL2":float(np.linalg.norm(x[k]-x[k-1])) if k>0 else None})
        return out
    return {
      "captureKey":m["captureKey"],"featureSha256":m["featureSha256"],
      "targetSha256":m["prepared"]["targetSha256"],"sourceEventSha256":m["prepared"].get("sourceEventSha256"),
      "cropSelection":m["cropSelection"],"rawReferenceCount":len(refs),"rawDecodedEventCount":len(preds),
      "rawScore":raw,"boundaryCorrectedScore":scored,"boundaryExclusionRecords":exclusion_records,
      "boundaryAccounting":{"referenceDelta":raw["referenceCount"]-scored["referenceCount"],
                            "predictionDelta":raw["predictionCount"]-scored["predictionCount"]},
      "referenceProbes":probes,
      "controls":{"sustain":ctrl(sustain,"sustain"),"silence":ctrl(silence,"silence")},
    }

def run(args):
    p1=load_population(args.p1_dir,"P1",P1_KEYS); p2=load_population(args.p2_dir,"P2",P2_KEYS)
    ck=torch.load(args.model,map_location="cpu")
    if ck.get("schema")!="astra-tiny-fit-pilot-v1" or ck.get("optimizerSteps")!=200:
        raise RuntimeError("frozen model identity mismatch")
    model=TinyEventFitModel(); model.load_state_dict(ck["stateDict"],strict=True); model.eval()
    pairs=[]; total_scored_p1_pred=0
    for cat in ("chords","scales","singlenotes","techniques"):
        m1,x1=p1[cat]; m2,x2=p2[cat]
        a=_example(model,m1,x1); b=_example(model,m2,x2)
        corr=correspond(m1["prepared"]["scorableEvents"],m2["prepared"]["scorableEvents"])
        total_scored_p1_pred+=a["boundaryCorrectedScore"]["predictionCount"]
        proj=[]
        h1,_,_,_,_=_outputs(model,x1); h2,_,_,_,_=_outputs(model,x2)
        by1={p["id"]:p for p in a["referenceProbes"]}; by2={p["id"]:p for p in b["referenceProbes"]}
        e1={e["id"]:e for e in m1["prepared"]["scorableEvents"]}; e2={e["id"]:e for e in m2["prepared"]["scorableEvents"]}
        for mm in corr["matches"]:
            q1=e1[mm["p1Id"]]; q2=e2[mm["p2Id"]]; s=int(q1["string"])
            k1=max(0,min(FRAMES-1,int(round(float(q1["start"])/float(m1["hopSeconds"])))))
            k2=max(0,min(FRAMES-1,int(round(float(q2["start"])/float(m2["hopSeconds"])))))
            w=model.onset_head.weight[s].detach().cpu().numpy(); bias=float(model.onset_head.bias[s].detach().cpu())
            pi=projection_identity(w,bias,h1[k1],h2[k2])
            pi.update({"p1Id":q1["id"],"p2Id":q2["id"],"string":s,"fret":int(q1["fret"])})
            proj.append(pi)
        pairs.append({"category":cat,"p1":a,"p2":b,"correspondence":corr,"matchedOnsetProjectionDeltas":proj})
    reproduction_ok=(total_scored_p1_pred==16)
    matched=sum(len(p["correspondence"]["matches"]) for p in pairs)
    outcome="inconclusive"
    if not reproduction_ok: outcome="reproduction_failure"
    elif matched==0: outcome="insufficient_correspondence"
    receipt={
      "schema":SCHEMA,
      "sourceModel":{"modelSha256":_sha256_file(args.model),"runId":36280547470,"artifactId":10918434248},
      "execution":{"optimizerStepsExecuted":0,"thresholdSearchExecuted":False,"thresholdsChanged":False,
                   "modelWeightsChanged":False,"p3Opened":False},
      "reproduction":{"p1BoundaryCorrectedDecodedPredictionCount":total_scored_p1_pred,
                      "expectedFromFrozenDecoderV2Receipt":16,"passed":reproduction_ok,
                      "numericalFeatureEquivalenceToPriorArrays":"unverified_unless_original_arrays_are_supplied"},
      "correspondence":{"matchedCount":matched,
                        "rule":"exact source-event suffix identity plus string/fret; unmatched events retained; never array-position zip"},
      "pairs":pairs,
      "decision":{"outcome":outcome,
                  "allowedOutcomes":["reproduction_failure","insufficient_correspondence","descriptive_evidence_supports_bounded_probe","inconclusive"],
                  "causalClaimAllowed":False,
                  "automaticFitAuthorized":False},
      "guards":{"p3Sealed":True,"automaticRetry":False,"customerDeliveryEligible":False},
    }
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p1-dir",required=True); p.add_argument("--p2-dir",required=True)
    p.add_argument("--model",required=True); p.add_argument("--out",required=True)
    run(p.parse_args())
if __name__=="__main__": main()
