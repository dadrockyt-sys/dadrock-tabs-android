#!/usr/bin/env python3
"""Zero-optimizer synthetic-vs-real domain diagnostic for frozen Astra models."""
from __future__ import annotations

import argparse, json, math
from collections import Counter
from pathlib import Path

import numpy as np
import torch

from evaluation.event_decoder_v2 import decode_event_list_v2
from evaluation.p1_p2_transfer_evaluation_v1 import (
    TransferCandidate, load_population, EDGE_GUARD_SECONDS, OPEN_MIDI
)
from tiny_fit_pilot_v1 import TinyEventFitModel, _sha256_file, SILENCE_CLASS, NUM_CLASSES, NUM_STRINGS
from synthetic.s0_pilot_v1 import context5

SCHEMA="astra-synthetic-real-domain-diagnostic-v1"
STATE_THRESHOLD=0.5
ONSET_THRESHOLD=0.5

def _quantiles(x):
    a=np.asarray(x,dtype=np.float64).reshape(-1)
    if not len(a):
        return {"count":0}
    q=np.quantile(a,[.01,.05,.25,.5,.75,.95,.99])
    return {
      "count":int(a.size),"mean":float(a.mean()),"std":float(a.std()),
      "rms":float(np.sqrt(np.mean(a*a))),
      "q01":float(q[0]),"q05":float(q[1]),"q25":float(q[2]),"q50":float(q[3]),
      "q75":float(q[4]),"q95":float(q[5]),"q99":float(q[6]),
      "min":float(a.min()),"max":float(a.max()),
    }

def feature_stats(features):
    x=np.asarray(features,dtype=np.float32)
    flat=x.reshape(-1,x.shape[-1])
    qs=np.quantile(flat,[.05,.50,.95],axis=0)
    return {
      "global":_quantiles(flat),
      "centroid":[float(v) for v in flat.mean(axis=0)],
      "perBinStd":[float(v) for v in flat.std(axis=0)],
      "perBinQ05":[float(v) for v in qs[0]],
      "perBinQ50":[float(v) for v in qs[1]],
      "perBinQ95":[float(v) for v in qs[2]],
    }

def _candidate_outputs(model,x):
    xin=context5(np.asarray(x,dtype=np.float32)[None]).reshape(1,len(x),960)
    xt=torch.from_numpy(xin).float()
    with torch.no_grad():
        h=model.encoder(xt)
        state=model.state_head(h)
        onset=model.onset_head(h)
    return h[0],state[0],onset[0]

def _baseline_outputs(model,x):
    xt=torch.from_numpy(np.asarray(x,dtype=np.float32)[None]).float()
    with torch.no_grad():
        h=model.encoder(xt)
        state=model.state_head(h)
        onset=model.onset_head(h)
    return h[0],state[0],onset[0]

def _activation_stats(h):
    a=h.detach().cpu().numpy()
    return {
      "distribution":_quantiles(a),
      "zeroFraction":float(np.mean(a==0.0)),
      "nearZeroFraction":float(np.mean(np.abs(a)<1e-8)),
      "perUnitMean":[float(v) for v in a.reshape(-1,a.shape[-1]).mean(axis=0)],
      "perUnitStd":[float(v) for v in a.reshape(-1,a.shape[-1]).std(axis=0)],
    }

def _output_stats(state_logits,onset_logits):
    sl=state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES)
    sp=torch.softmax(sl,dim=-1)
    op=torch.sigmoid(onset_logits)
    best_active=sp[...,:SILENCE_CLASS].max(dim=-1).values
    silence=sp[...,SILENCE_CLASS]
    margin=best_active-silence
    return {
      "onsetLogit":_quantiles(onset_logits.detach().cpu().numpy()),
      "onsetProbability":_quantiles(op.detach().cpu().numpy()),
      "silenceProbability":_quantiles(silence.detach().cpu().numpy()),
      "bestActiveProbability":_quantiles(best_active.detach().cpu().numpy()),
      "bestActiveMinusSilence":_quantiles(margin.detach().cpu().numpy()),
    }

def _decode(state_logits,onset_logits,hop):
    events=decode_event_list_v2(state_logits,onset_logits,hop_seconds=float(hop),id_prefix="diag")
    hist=Counter(str(OPEN_MIDI[e.string]+e.fret) for e in events)
    return {"eventCount":len(events),"pitchHistogram":dict(sorted(hist.items(),key=lambda kv:int(kv[0])))}

def _reference_diag(state_logits,onset_logits,refs):
    sl=state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES)
    sp=torch.softmax(sl,dim=-1).detach().cpu().numpy()
    op=torch.sigmoid(onset_logits).detach().cpu().numpy()
    total=on_ok=state_ok=joint=0
    truep=[]; silencep=[]; margins=[]; ranks=[]; onsetp=[]
    for frame,string,fret in refs:
        if frame<0 or frame>=sp.shape[0] or not (0<=string<NUM_STRINGS) or not (0<=fret<SILENCE_CLASS):
            continue
        row=sp[frame,string]
        tp=float(row[fret]); sil=float(row[SILENCE_CLASS])
        active=row[:SILENCE_CLASS]
        best=int(np.argmax(active))
        rank=1+int(np.sum(active>tp))
        oo=bool(op[frame,string]>=ONSET_THRESHOLD)
        so=bool(best==fret and tp>=STATE_THRESHOLD and tp>sil)
        total+=1; on_ok+=int(oo); state_ok+=int(so); joint+=int(oo and so)
        truep.append(tp); silencep.append(sil); margins.append(tp-sil); ranks.append(rank); onsetp.append(float(op[frame,string]))
    return {
      "referenceStringFrames":total,
      "onsetAdmissionFraction":on_ok/total if total else None,
      "stateAdmissionFraction":state_ok/total if total else None,
      "jointAdmissionFraction":joint/total if total else None,
      "trueStateProbability":_quantiles(truep),
      "silenceProbabilityAtReference":_quantiles(silencep),
      "trueMinusSilenceMargin":_quantiles(margins),
      "trueStateRankAmongActive":_quantiles(ranks),
      "onsetProbabilityAtReference":_quantiles(onsetp),
    }

def _synthetic_refs(d):
    refs={}
    for i in np.flatnonzero(d["split"]=="test"):
        rows=[]
        for s in range(NUM_STRINGS):
            for f in np.flatnonzero(d["onset"][i,s]==1):
                fret=int(d["state"][i,s,f])
                if 0<=fret<SILENCE_CLASS:
                    rows.append((int(f),int(s),fret))
        refs[int(i)]=rows
    return refs

def _real_refs(meta):
    hop=float(meta["hopSeconds"])
    duration=float(meta["prepared"]["crop"]["frames"])*float(meta["prepared"]["crop"]["hopSeconds"])
    rows=[]
    for e in meta["prepared"]["scorableEvents"]:
        start=float(e["start"])
        if start<EDGE_GUARD_SECONDS or start>duration-EDGE_GUARD_SECONDS:
            continue
        rows.append((int(round(start/hop)),int(e["string"]),int(e["fret"])))
    return rows

def population(model_kind,model,items):
    feats=[]; hs=[]; states=[]; onsets=[]; ref_rows=[]; decode_rows=[]
    for name,x,hop,refs in items:
        h,s,o=(_candidate_outputs(model,x) if model_kind=="candidate" else _baseline_outputs(model,x))
        feats.append(x); hs.append(h.detach().cpu().numpy()); states.append(s); onsets.append(o)
        rd=_reference_diag(s,o,refs)
        ref_rows.append({"id":name,**rd})
        decode_rows.append({"id":name,**_decode(s,o,hop)})
    fcat=np.concatenate(feats,axis=0)
    hcat=np.concatenate(hs,axis=0)
    scat=torch.cat(states,dim=0); ocat=torch.cat(onsets,dim=0)
    totals=sum(r["referenceStringFrames"] for r in ref_rows)
    def weighted(field):
        if not totals: return None
        return sum((r[field] or 0)*r["referenceStringFrames"] for r in ref_rows)/totals
    return {
      "feature":feature_stats(fcat),
      "encoderHidden":{
        "distribution":_quantiles(hcat),
        "zeroFraction":float(np.mean(hcat==0.0)),
        "nearZeroFraction":float(np.mean(np.abs(hcat)<1e-8)),
        "perUnitMean":[float(v) for v in hcat.mean(axis=0)],
        "perUnitStd":[float(v) for v in hcat.std(axis=0)],
      },
      "outputs":_output_stats(scat,ocat),
      "reference":{
        "totalReferenceStringFrames":totals,
        "onsetAdmissionFraction":weighted("onsetAdmissionFraction"),
        "stateAdmissionFraction":weighted("stateAdmissionFraction"),
        "jointAdmissionFraction":weighted("jointAdmissionFraction"),
        "examples":ref_rows,
      },
      "decoded":{
        "eventCount":sum(r["eventCount"] for r in decode_rows),
        "examples":decode_rows,
      },
    }

def centroid_distance(a,b):
    x=np.asarray(a,dtype=np.float64); y=np.asarray(b,dtype=np.float64)
    l2=float(np.linalg.norm(x-y))
    denom=float(np.linalg.norm(x)*np.linalg.norm(y))
    cosine=float(np.dot(x,y)/denom) if denom else None
    return {"l2":l2,"cosineSimilarity":cosine,"cosineDistance":(1-cosine if cosine is not None else None)}

def run(args):
    bck=torch.load(args.baseline_model,map_location="cpu")
    if bck.get("schema")!="astra-tiny-fit-pilot-v1" or bck.get("optimizerSteps")!=200:
        raise RuntimeError("baseline checkpoint mismatch")
    baseline=TinyEventFitModel(); baseline.load_state_dict(bck["stateDict"],strict=True); baseline.eval()

    cck=torch.load(args.candidate_model,map_location="cpu")
    if cck.get("schema")!="astra-p1-p2-transfer-candidate-v1" or cck.get("optimizerSteps")!=500:
        raise RuntimeError("candidate checkpoint mismatch")
    candidate=TransferCandidate(); candidate.load_state_dict(cck["stateDict"],strict=True); candidate.eval()

    d=np.load(args.synthetic_dataset,allow_pickle=False)
    srefs=_synthetic_refs(d)
    synthetic=[(f"synthetic:{i}",d["features"][i].astype(np.float32,copy=False),256/22050,srefs[int(i)]) for i in np.flatnonzero(d["split"]=="test")]

    p1=[(m["captureKey"],x,float(m["hopSeconds"]),_real_refs(m)) for m,x in load_population(args.p1_dir,"P1")]
    p2=[(m["captureKey"],x,float(m["hopSeconds"]),_real_refs(m)) for m,x in load_population(args.p2_dir,"P2")]

    pops={"synthetic":synthetic,"P1":p1,"P2":p2}
    result={
      "schema":SCHEMA,
      "thresholds":{"state":STATE_THRESHOLD,"onset":ONSET_THRESHOLD},
      "edgeGuardSeconds":EDGE_GUARD_SECONDS,
      "models":{
        "baselineSha256":_sha256_file(args.baseline_model),
        "candidateSha256":_sha256_file(args.candidate_model),
      },
      "populations":{},
      "execution":{"optimizerSteps":0,"thresholdSearch":False,"modelWeightsChanged":False,"p1Accessed":True,"p2Accessed":True,"p3Opened":False},
    }
    for pname,items in pops.items():
        result["populations"][pname]={
          "baseline":population("baseline",baseline,items),
          "candidate":population("candidate",candidate,items),
        }

    for model in ("baseline","candidate"):
        syn=result["populations"]["synthetic"][model]["feature"]["centroid"]
        p1c=result["populations"]["P1"][model]["feature"]["centroid"]
        p2c=result["populations"]["P2"][model]["feature"]["centroid"]
        result.setdefault("featureCentroidDistances",{})[model]={
          "syntheticToP1":centroid_distance(syn,p1c),
          "syntheticToP2":centroid_distance(syn,p2c),
          "P1ToP2":centroid_distance(p1c,p2c),
        }

    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic-dataset",required=True)
    p.add_argument("--p1-dir",required=True); p.add_argument("--p2-dir",required=True)
    p.add_argument("--baseline-model",required=True); p.add_argument("--candidate-model",required=True)
    p.add_argument("--out",required=True)
    run(p.parse_args())
if __name__=="__main__": main()
