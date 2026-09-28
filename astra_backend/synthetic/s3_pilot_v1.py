#!/usr/bin/env python3
"""Astra S3 synthetic-only onset-positive weighting experiment.

Only onset BCE positive-token weight differs between arms: 8 versus 16.
State weight, data, initialization, minibatch indices, sampler, architecture,
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
    ONSET_LOSS_WEIGHT, EXAMPLES, AUDIO_SECONDS, MAX_FIT_EVAL_SECONDS,
    context5, FrameModel, evaluate_model,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import (
    array_content_sha256, dataset_array_hashes, state_admission_diagnostics,
)

SCHEMA="astra-synthetic-data-diversity-s3-pilot-v1"
STATE_ACTIVE_WEIGHT=6.0
CONTROL_POS_WEIGHT=8.0
INTERVENTION_POS_WEIGHT=16.0
MAX_TOTAL_STEPS=1000


def _set_determinism():
    random.seed(ROOT_SEED+9001)
    np.random.seed(ROOT_SEED+9001)
    torch.manual_seed(ROOT_SEED+9001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def s3_loss(state_logits,onset_logits,state_target,onset_target,onset_pos_weight):
    if onset_pos_weight not in (CONTROL_POS_WEIGHT,INTERVENTION_POS_WEIGHT):
        raise ValueError("onset pos_weight outside frozen S3 arms")
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(
        state_logits.reshape(-1,NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(-1,NUM_STRINGS)
    weights=torch.ones_like(raw)
    weights[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    state_loss=(raw*weights).sum()/weights.sum()
    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,
        onset_target.float(),
        pos_weight=torch.tensor(float(onset_pos_weight),dtype=onset_logits.dtype),
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


def fit_arm(features,state,onset,batches,*,onset_pos_weight,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)

    _set_determinism()
    model=FrameModel(xf.shape[1])
    h=hashlib.sha256()
    for name,tensor in sorted(model.state_dict().items()):
        h.update(name.encode("utf-8")); h.update(b"\0")
        h.update(np.ascontiguousarray(tensor.cpu().numpy()).tobytes())
    init_sha=h.hexdigest()

    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic()
    steps=0
    stop="requested_steps_reached"
    first=None; last=None
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
        loss,state_loss,onset_loss=s3_loss(sl,ol,sb,ob,onset_pos_weight)
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite S3 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S3 gradient")
        opt.step()
        scalar={"total":float(loss.detach()),"state":float(state_loss.detach()),"onset":float(onset_loss.detach())}
        if first is None: first=scalar
        last=scalar
        steps+=1
    return model,{
        "onsetPositiveWeight":float(onset_pos_weight),
        "optimizerSteps":steps,
        "requestedSteps":MAX_STEPS,
        "elapsedSeconds":time.monotonic()-started,
        "stopReason":stop,
        "initialModelSha256":init_sha,
        "firstBatchLoss":first,
        "lastBatchLoss":last,
    }


def _stats(values):
    if not values:
        return None
    a=np.asarray(values,dtype=np.float64)
    return {
        "count":int(len(a)),"mean":float(a.mean()),"min":float(a.min()),"max":float(a.max()),
        "p25":float(np.quantile(a,.25)),"median":float(np.quantile(a,.5)),"p75":float(np.quantile(a,.75)),
    }


def repeated_reference_diagnostics(model,features,state,onset,split,split_name):
    xin=context5(features)
    indices=np.flatnonzero(np.asarray(split)==split_name)
    total=admitted=0
    current_probs=[]
    prev_probs=[]
    model.eval()
    with torch.no_grad():
        for i in indices:
            sl,ol=model(torch.from_numpy(xin[i]).float())
            probs=torch.sigmoid(ol).cpu().numpy()
            for s in range(NUM_STRINGS):
                attack_frames=list(map(int,np.flatnonzero(onset[i,s]==1)))
                if len(attack_frames)<2:
                    continue
                for frame in attack_frames[1:]:
                    total+=1
                    p=float(probs[frame,s])
                    pp=float(probs[frame-1,s]) if frame>0 else 0.0
                    current_probs.append(p); prev_probs.append(pp)
                    if p>=ONSET_THRESHOLD:
                        admitted+=1
    return {
        "repeatedReferenceCount":total,
        "onsetAdmissionCount":admitted,
        "onsetAdmissionFraction":admitted/total if total else None,
        "currentFrameOnsetProbability":_stats(current_probs),
        "precedingFrameOnsetProbability":_stats(prev_probs),
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
    base["repeatedReferenceOnset"]=repeated_reference_diagnostics(
        model,features,d["state"],d["onset"],d["split"],split_name
    )
    return base


def run(dataset,out,control_model,intervention_model,identity_out):
    started=time.monotonic()
    deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected S3 deterministic corpus")
    if not np.isfinite(d["features"]).all():
        raise RuntimeError("nonfinite S3 features")

    hashes=dataset_array_hashes(d)
    batches,strata=precompute_batches(
        d["state"],d["onset"],d["split"],d["has_negative_structure"]
    )
    identity={
        "schema":"astra-s3-array-identity-v1",
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
        onset_pos_weight=CONTROL_POS_WEIGHT,deadline=deadline
    )
    intervention,wf=fit_arm(
        d["features"].astype(np.float32,copy=False),d["state"],d["onset"],batches,
        onset_pos_weight=INTERVENTION_POS_WEIGHT,deadline=deadline
    )
    if cf["initialModelSha256"]!=wf["initialModelSha256"]:
        raise RuntimeError("S3 arms did not start from identical initialization")

    ctest=evaluate_arm(control,d,"test")
    wtest=evaluate_arm(intervention,d,"test")
    cval=evaluate_arm(control,d,"validation")
    wval=evaluate_arm(intervention,d,"validation")

    onset_adm_gain=wtest["admission"]["onsetAdmissionFraction"]-ctest["admission"]["onsetAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    repeated_gain=(wtest["repeatedAttackRecall"] or 0)-(ctest["repeatedAttackRecall"] or 0)
    state_decline=ctest["admission"]["stateAdmissionFraction"]-wtest["admission"]["stateAdmissionFraction"]
    joint_decline=ctest["admission"]["jointAdmissionFraction"]-wtest["admission"]["jointAdmissionFraction"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={
        fam:ctest["familyPitchOnset"][fam]["f1"]-wtest["familyPitchOnset"][fam]["f1"]
        for fam in ctest["familyPitchOnset"]
    }

    criteria={
        "onsetAdmissionGainAtLeast0_10":onset_adm_gain>=.10,
        "onsetRecallGainAtLeast0_08":recall_gain>=.08,
        "onsetF1GainAtLeast0_05":f1_gain>=.05,
        "repeatedRecallGainAtLeast0_10":repeated_gain>=.10,
        "absoluteOnsetRecallAtLeast0_65":wtest["pitchOnset"]["recall"]>=.65,
        "absoluteOnsetF1AtLeast0_72":wtest["pitchOnset"]["f1"]>=.72,
        "absoluteRepeatedRecallAtLeast0_60":(
            wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.60
        ),
        "onsetPrecisionAtLeast0_82":wtest["pitchOnset"]["precision"]>=.82,
        "stateAdmissionDeclineAtMost0_05":state_decline<=.05,
        "jointAdmissionDeclineAtMost0_05":joint_decline<=.05,
        "onsetOffsetDeclineAtMost0_05":offset_decline<=.05,
        "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":(
            wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None
            and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10
        ),
        "noFamilyF1LossOver0_15":all(loss<=.15 for loss in family_losses.values()),
        "finiteBoth500StepsIdentityZeroThresholdSearch":(
            cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS
            and cf["initialModelSha256"]==wf["initialModelSha256"]
            and all(math.isfinite(float(v)) for v in (
                wtest["pitchOnset"]["precision"],wtest["pitchOnset"]["recall"],
                wtest["pitchOnset"]["f1"],onset_adm_gain,recall_gain,f1_gain
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
                 "stateActiveWeight":STATE_ACTIVE_WEIGHT,"learningRate":LEARNING_RATE,
                 "batchSize":BATCH_SIZE,"onsetLossWeight":ONSET_LOSS_WEIGHT,
                 "onsetThreshold":ONSET_THRESHOLD,"stateThreshold":STATE_ACTIVE_THRESHOLD,
                 "thresholdSearch":False,"thresholdRetuning":False},
        "control":{"fit":cf,"validation":cval,"test":ctest},
        "weight16":{"fit":wf,"validation":wval,"test":wtest},
        "comparison":{
            "onsetAdmissionGain":onset_adm_gain,
            "onsetRecallGain":recall_gain,
            "onsetF1Gain":f1_gain,
            "repeatedRecallGain":repeated_gain,
            "stateAdmissionDecline":state_decline,
            "jointAdmissionDecline":joint_decline,
            "onsetOffsetF1Decline":offset_decline,
            "familyF1LossVsControl":family_losses,
        },
        "criteria":criteria,
        "s3GatePassed":all(criteria.values()),
        "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
                     "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
        "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                  "productionMutation":False,"customerDeliveryEligible":False},
        "meaning":"Synthetic-only controlled onset-positive-weight experiment; no real-transfer, unseen-performer, or product claim."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"pos-weight-8","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"pos-weight-16","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS:
        raise RuntimeError("S3 optimizer ceiling exceeded")
    print("S3_RESULT="+json.dumps(result,sort_keys=True))


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
