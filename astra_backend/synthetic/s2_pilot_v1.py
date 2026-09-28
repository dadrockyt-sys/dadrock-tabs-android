#!/usr/bin/env python3
"""Astra S2 synthetic-only active-state weighting experiment.

Only active state-token loss weight differs between arms: 1.5 versus 6.0.
Data, initialization, minibatch indices, sampler, architecture, onset loss,
learning rate, thresholds, decoder, and optimizer-step budget are identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
import torch
import torch.nn.functional as F

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, BATCH_SIZE, LEARNING_RATE,
    NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD,
    ONSET_POS_WEIGHT, ONSET_LOSS_WEIGHT,
    HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ,
    EXAMPLES, AUDIO_SECONDS, MAX_FIT_EVAL_SECONDS,
    context5, FrameModel, evaluate_model,
)
from synthetic.s1_pilot_v1 import build_sampling_strata

SCHEMA="astra-synthetic-data-diversity-s2-pilot-v1"
CONTROL_WEIGHT=1.5
INTERVENTION_WEIGHT=6.0
MAX_TOTAL_STEPS=1000


def _set_determinism():
    random.seed(ROOT_SEED+8001)
    np.random.seed(ROOT_SEED+8001)
    torch.manual_seed(ROOT_SEED+8001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def array_content_sha256(array):
    a=np.ascontiguousarray(np.asarray(array))
    h=hashlib.sha256()
    h.update(str(a.dtype).encode("utf-8")); h.update(b"\0")
    h.update(",".join(str(x) for x in a.shape).encode("ascii")); h.update(b"\0")
    h.update(a.tobytes(order="C"))
    return h.hexdigest()


def dataset_array_hashes(d):
    keys=(
        "features","state","onset","family","split","template_id",
        "negative_only","has_negative_structure","refs_json",
    )
    return {key:array_content_sha256(d[key]) for key in keys}


def weighted_loss(state_logits,onset_logits,state_target,onset_target,active_weight):
    if active_weight not in (CONTROL_WEIGHT,INTERVENTION_WEIGHT):
        raise ValueError("state active weight outside frozen S2 arms")
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(
        state_logits.reshape(-1,NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(-1,NUM_STRINGS)
    weights=torch.ones_like(raw)
    weights[target!=SILENCE_CLASS]=float(active_weight)
    state_loss=(raw*weights).sum()/weights.sum()

    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,
        onset_target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )
    total=state_loss+ONSET_LOSS_WEIGHT*onset_loss
    return total,state_loss,onset_loss


def precompute_batches(state,onset,split,negative_structure):
    strata=build_sampling_strata(state,onset,split,negative_structure)
    rng=np.random.RandomState(ROOT_SEED+7001)
    batches=[]
    for _ in range(MAX_STEPS):
        chunks=[
            rng.choice(strata["positiveOnset"],size=32,replace=True),
            rng.choice(strata["activeNonOnset"],size=32,replace=True),
            rng.choice(strata["negativeStructureInactive"],size=32,replace=True),
            rng.choice(strata["otherInactive"],size=32,replace=True),
        ]
        idx=np.concatenate(chunks)
        idx=idx[rng.permutation(len(idx))]
        batches.append(idx.astype(np.int64,copy=False))
    return np.stack(batches),{k:int(len(v)) for k,v in strata.items()}


def batch_plan_sha256(batches):
    return array_content_sha256(np.asarray(batches,dtype=np.int64))


def fit_arm(features,state,onset,batches,*,active_weight,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)

    _set_determinism()
    model=FrameModel(xf.shape[1])
    initial_hash=hashlib.sha256()
    for name,tensor in sorted(model.state_dict().items()):
        initial_hash.update(name.encode("utf-8")); initial_hash.update(b"\0")
        initial_hash.update(np.ascontiguousarray(tensor.cpu().numpy()).tobytes())
    initial_sha=initial_hash.hexdigest()

    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic()
    steps=0
    stop="requested_steps_reached"
    first_loss=None
    last_loss=None
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"
            break
        idx=batches[step]
        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss,state_loss,onset_loss=weighted_loss(sl,ol,sb,ob,active_weight)
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite S2 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S2 gradient")
        opt.step()
        scalar={
            "total":float(loss.detach()),
            "state":float(state_loss.detach()),
            "onset":float(onset_loss.detach()),
        }
        if first_loss is None:
            first_loss=scalar
        last_loss=scalar
        steps+=1
    return model,{
        "activeStateWeight":float(active_weight),
        "optimizerSteps":steps,
        "requestedSteps":MAX_STEPS,
        "elapsedSeconds":time.monotonic()-started,
        "stopReason":stop,
        "initialModelSha256":initial_sha,
        "firstBatchLoss":first_loss,
        "lastBatchLoss":last_loss,
    }


def _stats(values):
    if not values:
        return None
    a=np.asarray(values,dtype=np.float64)
    return {
        "count":int(len(a)),
        "mean":float(a.mean()),
        "min":float(a.min()),
        "max":float(a.max()),
        "p25":float(np.quantile(a,.25)),
        "median":float(np.quantile(a,.5)),
        "p75":float(np.quantile(a,.75)),
    }


def state_admission_diagnostics(model,features,state,onset,split,split_name):
    xin=context5(features)
    indices=np.flatnonzero(np.asarray(split)==split_name)
    total=onset_pass=state_pass=joint=0
    onset_probs=[]
    true_probs=[]
    silence_probs=[]
    true_minus_silence=[]
    incorrect_probs=[]
    true_minus_incorrect=[]
    model.eval()
    with torch.no_grad():
        for i in indices:
            sl,ol=model(torch.from_numpy(xin[i]).float())
            sp=torch.softmax(sl.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1).cpu().numpy()
            op=torch.sigmoid(ol).cpu().numpy()
            for s in range(NUM_STRINGS):
                for frame in np.flatnonzero(onset[i,s]==1):
                    fret=int(state[i,s,frame])
                    if not 0<=fret<SILENCE_CLASS:
                        continue
                    total+=1
                    row=sp[frame,s]
                    true_p=float(row[fret])
                    silence_p=float(row[SILENCE_CLASS])
                    active=row[:SILENCE_CLASS].copy()
                    active[fret]=-1.0
                    strongest_incorrect=float(np.max(active))
                    best=int(np.argmax(row[:SILENCE_CLASS]))
                    onset_ok=bool(op[frame,s]>=ONSET_THRESHOLD)
                    state_ok=bool(
                        best==fret and true_p>=STATE_ACTIVE_THRESHOLD and true_p>silence_p
                    )
                    onset_pass+=int(onset_ok)
                    state_pass+=int(state_ok)
                    joint+=int(onset_ok and state_ok)
                    onset_probs.append(float(op[frame,s]))
                    true_probs.append(true_p)
                    silence_probs.append(silence_p)
                    true_minus_silence.append(true_p-silence_p)
                    incorrect_probs.append(strongest_incorrect)
                    true_minus_incorrect.append(true_p-strongest_incorrect)
    return {
        "positiveReferenceStringFrames":total,
        "onsetAdmissionFraction":onset_pass/total if total else None,
        "stateAdmissionFraction":state_pass/total if total else None,
        "jointAdmissionFraction":joint/total if total else None,
        "onsetProbability":_stats(onset_probs),
        "trueStateProbability":_stats(true_probs),
        "silenceProbability":_stats(silence_probs),
        "trueMinusSilenceMargin":_stats(true_minus_silence),
        "strongestIncorrectActiveProbability":_stats(incorrect_probs),
        "trueMinusStrongestIncorrectMargin":_stats(true_minus_incorrect),
    }


def evaluate_arm(model,d,split_name):
    features=d["features"].astype(np.float32,copy=False)
    base=evaluate_model(
        model,features,d["state"],d["onset"],d["family"],
        np.where(d["split"]==split_name,"test","other"),
        d["negative_only"],d["refs_json"],5
    )
    base["admission"]=state_admission_diagnostics(
        model,features,d["state"],d["onset"],d["split"],split_name
    )
    return base


def run(dataset,out,control_model,intervention_model,identity_out):
    started=time.monotonic()
    deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected S2 deterministic corpus")
    if not np.isfinite(d["features"]).all():
        raise RuntimeError("nonfinite S2 features")

    hashes=dataset_array_hashes(d)
    batches,strata=precompute_batches(
        d["state"],d["onset"],d["split"],d["has_negative_structure"]
    )
    identity={
        "schema":"astra-s2-array-identity-v1",
        "arrayContentSha256":hashes,
        "batchPlanSha256":batch_plan_sha256(batches),
        "batchShape":list(batches.shape),
        "stratumSizes":strata,
        "armsUseSameArrays":True,
        "armsUseSameBatchIndices":True,
    }
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    control,cf=fit_arm(
        d["features"].astype(np.float32,copy=False),d["state"],d["onset"],batches,
        active_weight=CONTROL_WEIGHT,deadline=deadline
    )
    intervention,wf=fit_arm(
        d["features"].astype(np.float32,copy=False),d["state"],d["onset"],batches,
        active_weight=INTERVENTION_WEIGHT,deadline=deadline
    )
    if cf["initialModelSha256"]!=wf["initialModelSha256"]:
        raise RuntimeError("S2 arms did not start from identical initialization")

    ctest=evaluate_arm(control,d,"test")
    wtest=evaluate_arm(intervention,d,"test")
    cval=evaluate_arm(control,d,"validation")
    wval=evaluate_arm(intervention,d,"validation")

    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={
        fam:ctest["familyPitchOnset"][fam]["f1"]-wtest["familyPitchOnset"][fam]["f1"]
        for fam in ctest["familyPitchOnset"]
    }
    criteria={
        "stateAdmissionGainAtLeast0_20":state_gain>=.20,
        "jointAdmissionGainAtLeast0_20":joint_gain>=.20,
        "onsetRecallGainAtLeast0_10":recall_gain>=.10,
        "onsetF1GainAtLeast0_08":f1_gain>=.08,
        "absoluteOnsetRecallAtLeast0_55":wtest["pitchOnset"]["recall"]>=.55,
        "absoluteOnsetF1AtLeast0_68":wtest["pitchOnset"]["f1"]>=.68,
        "onsetPrecisionAtLeast0_85":wtest["pitchOnset"]["precision"]>=.85,
        "repeatedRecallAtLeast0_55":(
            wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.55
        ),
        "onsetOffsetDeclineAtMost0_05":offset_decline<=.05,
        "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":(
            wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None
            and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10
        ),
        "noFamilyF1LossOver0_15":all(loss<=.15 for loss in family_losses.values()),
        "finiteBoth500StepsZeroThresholdSearch":(
            cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS
            and all(math.isfinite(float(v)) for v in (
                wtest["pitchOnset"]["precision"],wtest["pitchOnset"]["recall"],
                wtest["pitchOnset"]["f1"],state_gain,joint_gain
            ))
        ),
    }
    result={
        "schema":SCHEMA,
        "seed":ROOT_SEED,
        "dataset":{"examples":int(len(d["features"])),"audioSeconds":AUDIO_SECONDS,
                   "splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")},
                   "arrayContentSha256":hashes},
        "batchPlan":{"sha256":identity["batchPlanSha256"],"shape":identity["batchShape"],
                     "stratumSizes":strata,"identicalAcrossArms":True},
        "fixed":{"architecture":"five-frame-960x128","sampler":"onset-aware-32x4",
                 "learningRate":LEARNING_RATE,"batchSize":BATCH_SIZE,
                 "onsetPositiveWeight":ONSET_POS_WEIGHT,"onsetLossWeight":ONSET_LOSS_WEIGHT,
                 "onsetThreshold":ONSET_THRESHOLD,"stateThreshold":STATE_ACTIVE_THRESHOLD,
                 "thresholdSearch":False,"thresholdRetuning":False},
        "control":{"fit":cf,"validation":cval,"test":ctest},
        "weight6":{"fit":wf,"validation":wval,"test":wtest},
        "comparison":{
            "stateAdmissionGain":state_gain,
            "jointAdmissionGain":joint_gain,
            "onsetRecallGain":recall_gain,
            "onsetF1Gain":f1_gain,
            "onsetOffsetF1Decline":offset_decline,
            "familyF1LossVsControl":family_losses,
        },
        "criteria":criteria,
        "s2GatePassed":all(criteria.values()),
        "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
                     "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
        "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                  "productionMutation":False,"customerDeliveryEligible":False},
        "meaning":"Synthetic-only controlled state-weight experiment; no real-transfer, unseen-performer, or product claim."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"control-1.5","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"weight-6.0","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS:
        raise RuntimeError("S2 optimizer ceiling exceeded")
    print("S2_RESULT="+json.dumps(result,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--control-model",required=True)
    ap.add_argument("--intervention-model",required=True)
    ap.add_argument("--identity-out",required=True)
    args=ap.parse_args()
    run(args.dataset,args.out,args.control_model,args.intervention_model,args.identity_out)

if __name__=="__main__":
    main()
