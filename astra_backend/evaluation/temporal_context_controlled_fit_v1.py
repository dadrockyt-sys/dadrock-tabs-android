#!/usr/bin/env python3
"""One authorized, capped temporal-context controlled intervention on P1/P2 development data."""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
import torch

from evaluation.p1_p2_combined_diagnostic_v1 import load_population, P1_KEYS, P2_KEYS
from evaluation.temporal_context_intervention_v1 import temporal_triplet, repeated_current, clone_identical_pair
from evaluation.event_contract_v2 import Event, score_events
from evaluation.event_decoder_v2 import decode_event_list_v2, NUM_CLASSES, NUM_FRETS, NUM_STRINGS, SILENCE_CLASS
from evaluation.tiny_fit_v3_diagnostic import boundary_exclusions
from tiny_fit_pilot_v1 import explicit_event_loss, repeated_reference_events

SEED=20260927
STEPS=125
LR=0.01
STATE_THRESHOLD=0.50
ONSET_THRESHOLD=0.50
CATEGORIES=("chords","scales","singlenotes","techniques")

def ev(r): return Event(r["id"],int(r["string"]),int(r["fret"]),float(r["start"]),float(r["end"]))
def ratio(a,b): return (a/b) if b else None

def load_all(p1_dir,p2_dir):
    p1=load_population(p1_dir,"P1",P1_KEYS); p2=load_population(p2_dir,"P2",P2_KEYS)
    rows=[]
    for performer,pop in (("P1",p1),("P2",p2)):
        for cat in CATEGORIES:
            m,x=pop[cat]
            if m["prepared"]["unresolvedLabelCount"]!=0: raise RuntimeError("unresolved labels")
            rows.append({"performer":performer,"category":cat,"meta":m,"x":x})
    if len(rows)!=8: raise RuntimeError("requires exactly eight captures")
    return rows

def tensors(rows, transform):
    xs=[]; states=[]; onsets=[]
    for r in rows:
        x=torch.tensor(r["x"][None],dtype=torch.float32)
        xs.append(transform(x)[0])
        states.append(torch.tensor(r["meta"]["prepared"]["state"],dtype=torch.long))
        onsets.append(torch.tensor(r["meta"]["prepared"]["onset"],dtype=torch.long))
    return torch.stack(xs),torch.stack(states),torch.stack(onsets)

def train(model,x,state,onset):
    opt=torch.optim.Adam(model.parameters(),lr=LR)
    losses=[]
    model.train()
    for step in range(STEPS):
        opt.zero_grad(set_to_none=True)
        out=model(x)
        loss,parts=explicit_event_loss(out,state,onset)
        if not torch.isfinite(loss): raise RuntimeError("non-finite loss")
        loss.backward(); opt.step()
        if step in (0,STEPS-1):
            losses.append({"step":step+1,"total":float(loss.detach()),"state":float(parts["state"].detach()),"onset":float(parts["onset"].detach())})
    return losses

def frame_metrics(state_logits,onset_logits,meta):
    state_p=torch.softmax(state_logits.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1).detach().cpu().numpy()
    onset_p=torch.sigmoid(onset_logits).detach().cpu().numpy()
    state=np.asarray(meta["prepared"]["state"])
    onset=np.asarray(meta["prepared"]["onset"])
    refs=meta["prepared"]["scorableEvents"]; hop=float(meta["hopSeconds"])
    exact_total=exact_hit=win_hit=attack_state_hit=0
    for e in refs:
        s=int(e["string"]); f=int(e["fret"]); k=max(0,min(state_p.shape[0]-1,int(round(float(e["start"])/hop))))
        exact_total+=1
        def admitted(j):
            row=state_p[j,s]; best=int(np.argmax(row[:NUM_FRETS]))
            return onset_p[j,s]>=ONSET_THRESHOLD and best==f and row[best]>=STATE_THRESHOLD and row[best]>row[SILENCE_CLASS]
        if admitted(k): exact_hit+=1
        if any(admitted(j) for j in range(max(0,k-2),min(state_p.shape[0],k+3))): win_hit+=1
        row=state_p[k,s]; best=int(np.argmax(row[:NUM_FRETS]))
        if best==f and row[best]>=STATE_THRESHOLD and row[best]>row[SILENCE_CLASS]: attack_state_hit+=1
    sustain_total=sustain_hit=inactive_total=inactive_admit=0
    for s in range(NUM_STRINGS):
        for k in range(state.shape[1]):
            if state[s,k] == -100: continue
            row=state_p[k,s]; best=int(np.argmax(row[:NUM_FRETS]))
            active=best<NUM_FRETS and row[best]>=STATE_THRESHOLD and row[best]>row[SILENCE_CLASS]
            admitted=active and onset_p[k,s]>=ONSET_THRESHOLD
            if state[s,k] >= 0 and onset[s,k] != 1:
                sustain_total+=1
                if best==int(state[s,k]) and active: sustain_hit+=1
            if state[s,k] == -1:
                inactive_total+=1
                if admitted: inactive_admit+=1
    return {
      "exactCenterOnsetRecall":ratio(exact_hit,exact_total),
      "fixedPlusMinus2OnsetRecall":ratio(win_hit,exact_total),
      "attackTrueStateAccuracy":ratio(attack_state_hit,exact_total),
      "sustainTrueStateAccuracy":ratio(sustain_hit,sustain_total),
      "inactiveAdmissionRate":ratio(inactive_admit,inactive_total),
      "counts":{"attackReferences":exact_total,"sustainFrames":sustain_total,"inactiveFrames":inactive_total,"inactiveAdmissions":inactive_admit}
    }

def evaluate_one(model,row,transform,prefix):
    x=transform(torch.tensor(row["x"][None],dtype=torch.float32))
    model.eval()
    with torch.no_grad(): out=model(x)
    sl=out["state"][0]; ol=out["onset"][0]; meta=row["meta"]; hop=float(meta["hopSeconds"])
    refs=[ev(e) for e in meta["prepared"]["scorableEvents"]]
    preds=decode_event_list_v2(sl,ol,hop_seconds=hop,id_prefix=prefix)
    exclusions,records=boundary_exclusions(meta["prepared"])
    score=score_events(preds,refs,onset_tolerance=.05,offset_tolerance=.05,excluded_intervals=exclusions)
    reps=repeated_reference_events(refs)
    rep=score_events(preds,reps,onset_tolerance=.05,offset_tolerance=.05,excluded_intervals=exclusions) if reps else None
    return {
      "captureKey":meta["captureKey"],"performer":row["performer"],"category":row["category"],
      "featureSha256":meta["featureSha256"],"targetSha256":meta["prepared"]["targetSha256"],
      "score":score,"frameMetrics":frame_metrics(sl,ol,meta),
      "repeatedReferenceAttackCount":len(reps),"repeatedAttackTruePositive":0 if rep is None else rep["truePositive"],
      "boundaryExclusions":records
    }

def aggregate(examples):
    t={"reference":0,"prediction":0,"tp":0,"fp":0,"fn":0,"offset":0}
    f1s=[]; rep_ref=rep_tp=0; sustain_hit_weight=0; sustain_n=0; inactive_admit=inactive_n=0
    for e in examples:
        s=e["score"]; t["reference"]+=s["referenceCount"]; t["prediction"]+=s["predictionCount"]; t["tp"]+=s["truePositive"]; t["fp"]+=s["falsePositive"]; t["fn"]+=s["falseNegative"]; t["offset"]+=s["matchedOffsetWithinTolerance"]
        f1s.append(float(s["f1"] or 0.0)); rep_ref+=e["repeatedReferenceAttackCount"]; rep_tp+=e["repeatedAttackTruePositive"]
        fm=e["frameMetrics"]; n=fm["counts"]["sustainFrames"]; sustain_n+=n; sustain_hit_weight+=(fm["sustainTrueStateAccuracy"] or 0)*n
        inactive_n+=fm["counts"]["inactiveFrames"]; inactive_admit+=fm["counts"]["inactiveAdmissions"]
    p=ratio(t["tp"],t["prediction"]); r=ratio(t["tp"],t["reference"]); f=ratio(2*p*r,p+r) if p is not None and r is not None and p+r else 0.0
    return {"counts":t,"precision":p or 0.0,"recall":r or 0.0,"f1":f,"macroF1":sum(f1s)/len(f1s),
            "minCaptureF1":min(f1s),"repeatedAttackRecall":ratio(rep_tp,rep_ref),
            "repeatedAttackReferenceCount":rep_ref,"repeatedAttackTruePositive":rep_tp,
            "sustainTrueStateAccuracy":ratio(sustain_hit_weight,sustain_n),
            "inactiveAdmissionRate":ratio(inactive_admit,inactive_n)}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--p1-dir",required=True); ap.add_argument("--p2-dir",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args(); torch.manual_seed(SEED); torch.use_deterministic_algorithms(True); torch.set_num_threads(max(1,min(4,torch.get_num_threads())))
    rows=load_all(args.p1_dir,args.p2_dir); start=time.monotonic(); folds=[]; cand_evals=[]; ctrl_evals=[]; total_steps=0
    for fi,held in enumerate(CATEGORIES):
        train_rows=[r for r in rows if r["category"]!=held]; eval_rows=[r for r in rows if r["category"]==held]
        a,b=clone_identical_pair(SEED+fi)
        xa,st,on=tensors(train_rows,temporal_triplet); xb,st2,on2=tensors(train_rows,repeated_current)
        if not torch.equal(st,st2) or not torch.equal(on,on2): raise RuntimeError("candidate/comparator targets differ")
        la=train(a,xa,st,on); lb=train(b,xb,st,on); total_steps+=2*STEPS
        ea=[evaluate_one(a,r,temporal_triplet,f"cand:{held}:{r['performer']}") for r in eval_rows]
        eb=[evaluate_one(b,r,repeated_current,f"ctrl:{held}:{r['performer']}") for r in eval_rows]
        cand_evals.extend(ea); ctrl_evals.extend(eb)
        folds.append({"heldOutCategory":held,"trainCaptureKeys":[r["meta"]["captureKey"] for r in train_rows],
                      "evalCaptureKeys":[r["meta"]["captureKey"] for r in eval_rows],"candidateLoss":la,"comparatorLoss":lb,
                      "candidate":ea,"comparator":eb})
    ca=aggregate(cand_evals); co=aggregate(ctrl_evals)
    rep_ok=True if ca["repeatedAttackReferenceCount"]==0 else ca["repeatedAttackRecall"]>=.60
    inactive_ok=(ca["inactiveAdmissionRate"] or 0)<=((co["inactiveAdmissionRate"] or 0)+.01)
    sustain_ok=(ca["sustainTrueStateAccuracy"] or 0)>=((co["sustainTrueStateAccuracy"] or 0)-.02)
    crit={
      "macroF1DeltaAtLeast0_10":ca["macroF1"]>=co["macroF1"]+.10,
      "aggregatePrecisionAtLeast0_75":ca["precision"]>=.75,
      "aggregateRecallAtLeast0_60":ca["recall"]>=.60,
      "aggregateF1AtLeast0_67":ca["f1"]>=.67,
      "everyHeldOutCaptureF1AtLeast0_55":ca["minCaptureF1"]>=.55,
      "repeatedAttackRecallAtLeast0_60WhenPresent":rep_ok,
      "inactiveAdmissionNotWorseByMoreThan0_01":inactive_ok,
      "sustainStateNotWorseByMoreThan0_02":sustain_ok,
      "allMetricsFiniteAndUnresolvedZero":all(math.isfinite(float(v)) for v in [ca["precision"],ca["recall"],ca["f1"],ca["macroF1"],co["macroF1"]])
    }
    result={
      "schema":"astra-temporal-context-controlled-intervention-result-v1",
      "execution":{"optimizerStepsExecuted":total_steps,"maxAuthorized":1000,"thresholdSearchExecuted":False,"thresholdsChanged":False,"automaticRetry":False,"p3Opened":False,"runtimeSeconds":time.monotonic()-start},
      "split":{"method":"four-fold leave-one-content-group-out","performerHoldout":False,"unseenContentOnly":True},
      "candidateAggregate":ca,"comparatorAggregate":co,"criteria":crit,"positiveProbe":all(crit.values()),"folds":folds,
      "claimBoundary":"P1/P2 development-only unseen-content controlled intervention; no unseen-performer or customer-readiness claim."
    }
    if total_steps!=1000: raise RuntimeError("optimizer step accounting mismatch")
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
