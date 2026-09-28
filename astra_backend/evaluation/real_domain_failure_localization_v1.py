#!/usr/bin/env python3
"""Zero-training localization of Astra real-domain failure modes."""
from __future__ import annotations

import argparse, json, math
from pathlib import Path
import numpy as np
import torch

from evaluation.p1_p2_transfer_evaluation_v1 import (
    TransferCandidate, load_population, EDGE_GUARD_SECONDS, OPEN_MIDI
)
from tiny_fit_pilot_v1 import TinyEventFitModel, _sha256_file, NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS
from synthetic.s0_pilot_v1 import context5
from tabcnn_runtime.preprocessing import HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ

SCHEMA="astra-real-domain-failure-localization-v1"
STATE_THRESHOLD=0.5
ONSET_THRESHOLD=0.5
WINDOWS=(1,2,4)

def _baseline_outputs(model,x):
    xt=torch.from_numpy(np.asarray(x,dtype=np.float32)[None]).float()
    with torch.no_grad():
        h=model.encoder(xt)
        s=model.state_head(h)[0]
        o=model.onset_head(h)[0]
    return s,o

def _candidate_outputs(model,x):
    xin=context5(np.asarray(x,dtype=np.float32)[None]).reshape(1,len(x),960)
    xt=torch.from_numpy(xin).float()
    with torch.no_grad():
        h=model.encoder(xt)
        s=model.state_head(h)[0]
        o=model.onset_head(h)[0]
    return s,o

def _model_outputs(kind,model,x):
    return _candidate_outputs(model,x) if kind=="candidate" else _baseline_outputs(model,x)

def _real_refs(meta):
    hop=float(meta["hopSeconds"])
    duration=float(meta["prepared"]["crop"]["frames"])*float(meta["prepared"]["crop"]["hopSeconds"])
    out=[]
    for e in meta["prepared"]["scorableEvents"]:
        start=float(e["start"])
        if start<EDGE_GUARD_SECONDS or start>duration-EDGE_GUARD_SECONDS:
            continue
        out.append({
          "id":e["id"],"frame":int(round(start/hop)),
          "string":int(e["string"]),"fret":int(e["fret"]),
          "pitch":int(OPEN_MIDI[int(e["string"])]+int(e["fret"])),
          "start":start,
        })
    return out

def _synthetic_refs(d):
    rows=[]
    for i in np.flatnonzero(d["split"]=="test"):
        for st in range(NUM_STRINGS):
            for fr in np.flatnonzero(d["onset"][i,st]==1):
                fret=int(d["state"][i,st,fr])
                if 0<=fret<SILENCE_CLASS:
                    rows.append({
                      "id":f"synthetic:{int(i)}:{st}:{int(fr)}",
                      "clipIndex":int(i),"frame":int(fr),"string":int(st),"fret":fret,
                      "pitch":int(OPEN_MIDI[st]+fret),"start":float(fr)*(HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ),
                    })
    return rows

def _state_probs(state_logits):
    return torch.softmax(state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1).detach().cpu().numpy()

def _onset_probs(onset_logits):
    return torch.sigmoid(onset_logits).detach().cpu().numpy()

def _state_correct(sp,frame,string,fret):
    if not (0<=frame<sp.shape[0]): return False
    row=sp[frame,string]
    best=int(np.argmax(row[:SILENCE_CLASS]))
    return bool(best==fret and row[fret]>=STATE_THRESHOLD and row[fret]>row[SILENCE_CLASS])

def p1_state_event(sp,ref):
    f,s,fr=ref["frame"],ref["string"],ref["fret"]
    if not (0<=f<sp.shape[0]): return None
    active=sp[f,:,:SILENCE_CLASS]
    flat=active.reshape(-1)
    gidx=int(np.argmax(flat)); gs=gidx//SILENCE_CLASS; gf=gidx%SILENCE_CLASS
    gp=int(OPEN_MIDI[gs]+gf)
    truep=float(active[s,fr]); silence=float(sp[f,s,SILENCE_CLASS])
    same=active[s]
    same_rank=1+int(np.sum(same>truep))
    global_rank=1+int(np.sum(flat>truep))
    top_idx=np.argsort(flat)[::-1][:5]
    top=[]
    for idx in top_idx:
        ps=int(idx//SILENCE_CLASS); pf=int(idx%SILENCE_CLASS)
        top.append({"string":ps,"fret":pf,"pitch":int(OPEN_MIDI[ps]+pf),"probability":float(flat[idx])})
    true_pitch=ref["pitch"]
    return {
      **ref,
      "predString":gs,"predFret":gf,"predPitch":gp,
      "trueStateProbability":truep,"silenceProbability":silence,
      "trueMinusSilence":truep-silence,
      "sameStringTrueFretRank":same_rank,
      "globalTrueStateRank":global_rank,
      "semitoneError":gp-true_pitch,
      "absoluteSemitoneError":abs(gp-true_pitch),
      "sameStringBestFret":int(np.argmax(same)),
      "sameStringFretError":int(np.argmax(same))-fr,
      "exactStringFretTop1":bool(gs==s and gf==fr),
      "pitchOnlyTop1":bool(gp==true_pitch),
      "wrongStringCorrectPitchTop1":bool(gp==true_pitch and gs!=s),
      "trueClassTop1":bool(global_rank<=1),
      "trueClassTop3":bool(global_rank<=3),
      "trueClassTop5":bool(global_rank<=5),
      "top5ActiveStates":top,
    }

def summarize_p1(rows):
    if not rows: return {"count":0}
    abs_err=[r["absoluteSemitoneError"] for r in rows]
    return {
      "count":len(rows),
      "exactStringFretTop1Rate":float(np.mean([r["exactStringFretTop1"] for r in rows])),
      "pitchOnlyTop1Rate":float(np.mean([r["pitchOnlyTop1"] for r in rows])),
      "wrongStringCorrectPitchTop1Rate":float(np.mean([r["wrongStringCorrectPitchTop1"] for r in rows])),
      "medianAbsoluteSemitoneError":float(np.median(abs_err)),
      "meanAbsoluteSemitoneError":float(np.mean(abs_err)),
      "sameStringFretErrorMedian":float(np.median([r["sameStringFretError"] for r in rows])),
      "sameStringTrueFretRankMedian":float(np.median([r["sameStringTrueFretRank"] for r in rows])),
      "globalTrueStateRankMedian":float(np.median([r["globalTrueStateRank"] for r in rows])),
      "trueClassTop1Rate":float(np.mean([r["trueClassTop1"] for r in rows])),
      "trueClassTop3Rate":float(np.mean([r["trueClassTop3"] for r in rows])),
      "trueClassTop5Rate":float(np.mean([r["trueClassTop5"] for r in rows])),
      "trueStateProbabilityMean":float(np.mean([r["trueStateProbability"] for r in rows])),
      "silenceProbabilityMean":float(np.mean([r["silenceProbability"] for r in rows])),
    }

def spectral_novelty(x,frame,k):
    if frame<0 or frame>=len(x): return None
    prev=max(0,frame-k)
    diff=np.asarray(x[frame],dtype=np.float64)-np.asarray(x[prev],dtype=np.float64)
    return {
      "positiveFlux":float(np.maximum(diff,0).sum()),
      "l2Difference":float(np.linalg.norm(diff)),
    }

def onset_event(sp,op,x,ref):
    f,s,fr=ref["frame"],ref["string"],ref["fret"]
    if not (0<=f<op.shape[0]): return None
    row={**ref,"onsetProbabilityAtReference":float(op[f,s]),"stateCorrectAtReference":_state_correct(sp,f,s,fr)}
    for w in WINDOWS:
        lo=max(0,f-w); hi=min(op.shape[0],f+w+1)
        vals=op[lo:hi,s]
        rel=int(np.argmax(vals)); mf=lo+rel
        row[f"window{w}MaxOnsetProbability"]=float(vals[rel])
        row[f"window{w}MaxFrameOffset"]=int(mf-f)
        row[f"window{w}CrossesThreshold"]=bool(np.max(vals)>=ONSET_THRESHOLD)
        row[f"window{w}StateCorrectAtLocalMax"]=_state_correct(sp,mf,s,fr)
    for k in WINDOWS:
        nov=spectral_novelty(x,f,k)
        row[f"frameDiffL2_k{k}"]=nov["l2Difference"]
        row[f"positiveSpectralFlux_k{k}"]=nov["positiveFlux"]
    return row

def summarize_onset(rows):
    if not rows: return {"count":0}
    out={
      "count":len(rows),
      "onsetProbabilityAtReferenceMean":float(np.mean([r["onsetProbabilityAtReference"] for r in rows])),
      "stateCorrectAtReferenceRate":float(np.mean([r["stateCorrectAtReference"] for r in rows])),
    }
    for w in WINDOWS:
        out[f"window{w}MaxOnsetProbabilityMean"]=float(np.mean([r[f"window{w}MaxOnsetProbability"] for r in rows]))
        out[f"window{w}ThresholdCrossRate"]=float(np.mean([r[f"window{w}CrossesThreshold"] for r in rows]))
        out[f"window{w}AbsMaxFrameOffsetMedian"]=float(np.median([abs(r[f"window{w}MaxFrameOffset"]) for r in rows]))
        out[f"window{w}StateCorrectAtLocalMaxRate"]=float(np.mean([r[f"window{w}StateCorrectAtLocalMax"] for r in rows]))
        out[f"frameDiffL2_k{w}Mean"]=float(np.mean([r[f"frameDiffL2_k{w}"] for r in rows]))
        out[f"positiveSpectralFlux_k{w}Mean"]=float(np.mean([r[f"positiveSpectralFlux_k{w}"] for r in rows]))
    return out

def analyze_real_population(kind,model,pop):
    p1rows=[]; onsetrows=[]
    for meta,x in pop:
        s,o=_model_outputs(kind,model,x)
        sp=_state_probs(s); op=_onset_probs(o)
        refs=_real_refs(meta)
        for ref in refs:
            if meta["performer"]=="P1":
                r=p1_state_event(sp,ref)
                if r: p1rows.append({"captureKey":meta["captureKey"],**r})
            rr=onset_event(sp,op,x,ref)
            if rr: onsetrows.append({"captureKey":meta["captureKey"],**rr})
    return {"p1StateEvents":p1rows,"p1StateSummary":summarize_p1(p1rows),"onsetEvents":onsetrows,"onsetSummary":summarize_onset(onsetrows)}

def analyze_synthetic(kind,model,d):
    refs=_synthetic_refs(d); rows=[]
    by_clip={}
    for r in refs: by_clip.setdefault(r["clipIndex"],[]).append(r)
    for i,rs in by_clip.items():
        x=d["features"][i].astype(np.float32,copy=False)
        s,o=_model_outputs(kind,model,x); sp=_state_probs(s); op=_onset_probs(o)
        for ref in rs:
            rr=onset_event(sp,op,x,ref)
            if rr: rows.append(rr)
    return {"onsetEvents":rows,"onsetSummary":summarize_onset(rows)}

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
    p1=load_population(args.p1_dir,"P1"); p2=load_population(args.p2_dir,"P2")

    result={
      "schema":SCHEMA,
      "thresholds":{"state":STATE_THRESHOLD,"onset":ONSET_THRESHOLD},
      "edgeGuardSeconds":EDGE_GUARD_SECONDS,
      "models":{"baselineSha256":_sha256_file(args.baseline_model),"candidateSha256":_sha256_file(args.candidate_model)},
      "P1":{"baseline":analyze_real_population("baseline",baseline,p1),"candidate":analyze_real_population("candidate",candidate,p1)},
      "P2":{"baseline":analyze_real_population("baseline",baseline,p2),"candidate":analyze_real_population("candidate",candidate,p2)},
      "synthetic":{"baseline":analyze_synthetic("baseline",baseline,d),"candidate":analyze_synthetic("candidate",candidate,d)},
      "execution":{"optimizerSteps":0,"thresholdSearch":False,"thresholdRetuning":False,"modelWeightsChanged":False,"normalizationFedToModel":False,"p1Accessed":True,"p2Accessed":True,"p3Opened":False},
    }
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--synthetic-dataset",required=True); p.add_argument("--p1-dir",required=True); p.add_argument("--p2-dir",required=True)
    p.add_argument("--baseline-model",required=True); p.add_argument("--candidate-model",required=True); p.add_argument("--out",required=True)
    run(p.parse_args())
if __name__=="__main__": main()
