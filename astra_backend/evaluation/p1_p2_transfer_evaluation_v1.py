#!/usr/bin/env python3
"""Prospective P1/P2 transfer evaluator. Does not acquire media or train models."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn

from evaluation.evaluation_protocol_v2 import EvalPitchEvent, score_pitch_events_v2
from evaluation.event_decoder_v2 import decode_event_list_v2
from tiny_fit_pilot_v1 import TinyEventFitModel, _sha256_file
from synthetic.s0_pilot_v1 import context5

SCHEMA="astra-p1-p2-transfer-evaluation-v1"
OPEN_MIDI=(40,45,50,55,59,64)
EDGE_GUARD_SECONDS=0.05
EXPECTED={
 "P1":("P1|chords|Drop3_7|directinput","P1|scales|Ab|directinput","P1|singlenotes|allsinglenotes|directinput","P1|techniques|PalmMute|directinput"),
 "P2":("P2|chords|Drop3_7|directinput","P2|scales|Ab|directinput","P2|singlenotes|allsinglenotes|directinput","P2|techniques|PalmMute|directinput"),
}

class TransferCandidate(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(960,128),nn.ReLU())
        self.state_head=nn.Sequential(nn.Linear(128,128),nn.ReLU(),nn.Linear(128,126))
        self.onset_head=nn.Linear(128,6)
    def forward(self,x):
        h=self.encoder(x)
        return self.state_head(h),self.onset_head(h)

def load_population(root,performer):
    rows=[]
    for mp in sorted(Path(root).glob("*/meta.json")):
        m=json.loads(mp.read_text()); fp=mp.parent/"features.npy"
        if m.get("performer")!=performer: raise RuntimeError("performer mismatch")
        if m.get("captureKey") not in EXPECTED[performer]: raise RuntimeError("capture allowlist mismatch")
        if m.get("captureView")!="directinput": raise RuntimeError("capture view mismatch")
        if m.get("prepared",{}).get("unresolvedLabelCount")!=0: raise RuntimeError("unresolved selected labels")
        if _sha256_file(fp)!=m.get("featureSha256"): raise RuntimeError("feature hash mismatch")
        x=np.load(fp,allow_pickle=False).astype(np.float32,copy=False)
        if x.shape!=(200,192) or not np.isfinite(x).all(): raise RuntimeError("unexpected prepared features")
        rows.append((m,x))
    if {m["captureKey"] for m,_ in rows}!=set(EXPECTED[performer]): raise RuntimeError("incomplete exact population")
    return rows

def _eval_event(event_id,string,fret,start,end,duration):
    pitch=OPEN_MIDI[int(string)]+int(fret)
    start=float(start); end=float(end)
    carry_in=start<EDGE_GUARD_SECONDS
    carry_out=end>duration-EDGE_GUARD_SECONDS
    return EvalPitchEvent(str(event_id),pitch,start,end,start,end,carry_in,carry_out,not carry_in,not carry_out)

def refs_from_meta(meta):
    duration=float(meta["prepared"]["crop"]["frames"])*float(meta["prepared"]["crop"]["hopSeconds"])
    return [_eval_event(e["id"],e["string"],e["fret"],e["start"],e["end"],duration) for e in meta["prepared"]["scorableEvents"]]

def preds_to_eval(preds,duration,prefix):
    return [_eval_event(f"{prefix}:{i}",e.string,e.fret,e.start,e.end,duration) for i,e in enumerate(preds)]

def baseline_logits(model,x):
    with torch.no_grad(): out=model(torch.as_tensor(x[None],dtype=torch.float32))
    return out["state"][0],out["onset"][0]

def candidate_logits(model,x):
    xx=context5(x[None]).reshape(1,x.shape[0],960)
    with torch.no_grad(): s,o=model(torch.as_tensor(xx,dtype=torch.float32))
    return s[0],o[0]

def repeated_ref_indices(refs):
    out=set(); seen=set()
    for i,e in sorted(enumerate(refs),key=lambda z:(z[1].pitch,z[1].start,z[1].end,z[1].id)):
        if not e.onset_eligible: continue
        if e.pitch in seen: out.add(i)
        seen.add(e.pitch)
    return out

def one(model_kind,model,meta,x):
    sl,ol=(baseline_logits(model,x) if model_kind=="baseline" else candidate_logits(model,x))
    hop=float(meta["hopSeconds"])
    pred=decode_event_list_v2(sl,ol,hop_seconds=hop,id_prefix=model_kind)
    duration=x.shape[0]*hop
    refs=refs_from_meta(meta); preds=preds_to_eval(pred,duration,model_kind)
    scored=score_pitch_events_v2(preds,refs)
    rep=repeated_ref_indices(refs)
    matched={j for _,j in scored["pitchOnset"]["matchedPairs"]}
    repeated_total=len(rep); repeated_tp=len(rep&matched)
    return {
      "captureKey":meta["captureKey"],"category":meta["category"],
      "featureSha256":meta["featureSha256"],"targetSha256":meta["prepared"]["targetSha256"],
      "edgeGuardSeconds":EDGE_GUARD_SECONDS,
      "pitchOnset":scored["pitchOnset"],"pitchOnsetOffset":scored["pitchOnsetOffset"],
      "eligibility":scored["eligibility"],
      "repeatedReferenceCount":repeated_total,
      "repeatedAttackRecall":(repeated_tp/repeated_total if repeated_total else None),
    }

def aggregate(rows,key):
    tp=sum(r[key]["truePositive"] for r in rows); fp=sum(r[key]["falsePositive"] for r in rows); fn=sum(r[key]["falseNegative"] for r in rows)
    p=tp/(tp+fp) if tp+fp else (1.0 if fn==0 else 0.0); rec=tp/(tp+fn) if tp+fn else 1.0
    f1=2*p*rec/(p+rec) if p+rec else 0.0
    return {"truePositive":tp,"falsePositive":fp,"falseNegative":fn,"precision":p,"recall":rec,"f1":f1}

def summarize(rows):
    rep_num=sum((r["repeatedAttackRecall"] or 0)*r["repeatedReferenceCount"] for r in rows)
    rep_den=sum(r["repeatedReferenceCount"] for r in rows)
    return {
      "pitchOnset":aggregate(rows,"pitchOnset"),
      "pitchOnsetOffset":aggregate(rows,"pitchOnsetOffset"),
      "repeatedReferenceCount":rep_den,
      "repeatedAttackRecall":(rep_num/rep_den if rep_den else None),
      "examplesWithTruePositive":sum(1 for r in rows if r["pitchOnset"]["truePositive"]>0),
    }

def run(args):
    bck=torch.load(args.baseline_model,map_location="cpu")
    if bck.get("schema")!="astra-tiny-fit-pilot-v1" or bck.get("optimizerSteps")!=200: raise RuntimeError("baseline checkpoint identity mismatch")
    baseline=TinyEventFitModel(); baseline.load_state_dict(bck["stateDict"],strict=True); baseline.eval()
    cck=torch.load(args.candidate_model,map_location="cpu")
    if cck.get("schema")!="astra-p1-p2-transfer-candidate-v1" or cck.get("optimizerSteps")!=500: raise RuntimeError("candidate checkpoint identity mismatch")
    candidate=TransferCandidate(); candidate.load_state_dict(cck["stateDict"],strict=True); candidate.eval()

    result={"schema":SCHEMA,"edgeGuardSeconds":EDGE_GUARD_SECONDS,"models":{
      "baselineSha256":_sha256_file(args.baseline_model),"candidateSha256":_sha256_file(args.candidate_model)},
      "populations":{},"execution":{"optimizerStepsExecutedDuringEvaluation":0,"thresholdSearchExecuted":False,"p1Accessed":True,"p2Accessed":True,"p3Opened":False}}
    for performer,root in (("P1",args.p1_dir),("P2",args.p2_dir)):
        pop=load_population(root,performer)
        br=[one("baseline",baseline,m,x) for m,x in pop]
        cr=[one("candidate",candidate,m,x) for m,x in pop]
        result["populations"][performer]={"baseline":{"examples":br,"summary":summarize(br)},"candidate":{"examples":cr,"summary":summarize(cr)}}

    p2b=result["populations"]["P2"]["baseline"]["summary"]["pitchOnset"]
    p2c=result["populations"]["P2"]["candidate"]["summary"]["pitchOnset"]
    transfer={
      "candidateP2F1":p2c["f1"],"candidateP2Recall":p2c["recall"],"candidateP2Precision":p2c["precision"],
      "p2F1GainVsBaseline":p2c["f1"]-p2b["f1"],
      "candidateP2ExamplesWithTruePositive":result["populations"]["P2"]["candidate"]["summary"]["examplesWithTruePositive"],
    }
    criteria={
      "candidateP2F1AtLeast0_35":transfer["candidateP2F1"]>=.35,
      "candidateP2RecallAtLeast0_35":transfer["candidateP2Recall"]>=.35,
      "candidateP2PrecisionAtLeast0_40":transfer["candidateP2Precision"]>=.40,
      "p2F1GainVsBaselineAtLeast0_25":transfer["p2F1GainVsBaseline"]>=.25,
      "truePositiveInAtLeast3of4P2Examples":transfer["candidateP2ExamplesWithTruePositive"]>=3,
    }
    result["transferEvidence"]=transfer
    result["transferGate"]={"passed":all(criteria.values()),"criteria":criteria,
      "meaning":"Development transfer evidence only; no P3 or production claim."}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--p1-dir",required=True); p.add_argument("--p2-dir",required=True)
    p.add_argument("--baseline-model",required=True); p.add_argument("--candidate-model",required=True); p.add_argument("--out",required=True)
    run(p.parse_args())
if __name__=="__main__": main()
