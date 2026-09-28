#!/usr/bin/env python3
"""Astra S5 synthetic-only active-state weighting experiment.

Only active-state token weight differs between arms: 6.0 versus 9.0.
Everything else is frozen and identical.
"""
from __future__ import annotations

import argparse, hashlib, json, math, os, random, time
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, BATCH_SIZE, LEARNING_RATE,
    NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD,
    EXAMPLES, AUDIO_SECONDS, MAX_FIT_EVAL_SECONDS,
    context5, FrameModel, evaluate_model,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import array_content_sha256, dataset_array_hashes, state_admission_diagnostics
from synthetic.s3_pilot_v1 import repeated_reference_diagnostics

SCHEMA="astra-synthetic-data-diversity-s5-pilot-v1"
CONTROL_STATE_WEIGHT=6.0
INTERVENTION_STATE_WEIGHT=9.0
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
MAX_TOTAL_STEPS=1000


def _set_determinism():
    random.seed(ROOT_SEED+11001)
    np.random.seed(ROOT_SEED+11001)
    torch.manual_seed(ROOT_SEED+11001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def precompute_batches(state,onset,split,negative_structure):
    strata=build_sampling_strata(state,onset,split,negative_structure)
    rng=np.random.RandomState(ROOT_SEED+7001)
    batches=[]
    for _ in range(MAX_STEPS):
        chunks=[
            rng.choice(strata["positiveOnset"],32,replace=True),
            rng.choice(strata["activeNonOnset"],32,replace=True),
            rng.choice(strata["negativeStructureInactive"],32,replace=True),
            rng.choice(strata["otherInactive"],32,replace=True),
        ]
        idx=np.concatenate(chunks)
        batches.append(idx[rng.permutation(len(idx))].astype(np.int64,copy=False))
    return np.stack(batches),{k:int(len(v)) for k,v in strata.items()}


def batch_plan_sha256(batches):
    return array_content_sha256(np.asarray(batches,dtype=np.int64))


def weighted_loss(state_logits,onset_logits,state_target,onset_target,state_weight):
    if state_weight not in (CONTROL_STATE_WEIGHT,INTERVENTION_STATE_WEIGHT):
        raise ValueError("state weight outside frozen S5 arms")
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(
        state_logits.reshape(-1,NUM_CLASSES),
        target.reshape(-1),
        reduction="none",
    ).reshape(-1,NUM_STRINGS)
    weights=torch.ones_like(raw)
    weights[target!=SILENCE_CLASS]=float(state_weight)
    state_loss=(raw*weights).sum()/weights.sum()
    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,
        onset_target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )
    return state_loss+ONSET_LOSS_WEIGHT*onset_loss,state_loss,onset_loss


def model_sha(model):
    h=hashlib.sha256()
    for name,tensor in sorted(model.state_dict().items()):
        h.update(name.encode("utf-8")); h.update(b"\0")
        h.update(np.ascontiguousarray(tensor.cpu().numpy()).tobytes())
    return h.hexdigest()


def fit_arm(features,state,onset,batches,*,state_weight,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)

    _set_determinism()
    model=FrameModel(xf.shape[1])
    init_sha=model_sha(model)
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)

    started=time.monotonic()
    steps=0
    stop="requested_steps_reached"
    first=None
    last=None
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
        loss,state_loss,onset_loss=weighted_loss(sl,ol,sb,ob,state_weight)
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite S5 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S5 gradient")
        opt.step()
        scalar={"total":float(loss.detach()),"state":float(state_loss.detach()),"onset":float(onset_loss.detach())}
        if first is None:
            first=scalar
        last=scalar
        steps+=1
    return model,{
        "activeStateWeight":float(state_weight),
        "optimizerSteps":steps,
        "requestedSteps":MAX_STEPS,
        "elapsedSeconds":time.monotonic()-started,
        "stopReason":stop,
        "initialModelSha256":init_sha,
        "firstBatchLoss":first,
        "lastBatchLoss":last,
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
        raise RuntimeError("unexpected S5 deterministic corpus")
    features=d["features"].astype(np.float32,copy=False)
    if not np.isfinite(features).all():
        raise RuntimeError("nonfinite S5 features")

    hashes=dataset_array_hashes(d)
    batches,strata=precompute_batches(
        d["state"],d["onset"],d["split"],d["has_negative_structure"]
    )
    identity={
        "schema":"astra-s5-identity-v1",
        "arrayContentSha256":hashes,
        "batchPlanSha256":batch_plan_sha256(batches),
        "batchShape":list(batches.shape),
        "stratumSizes":strata,
        "armsUseSameArrays":True,
        "armsUseSameBatchIndices":True,
    }
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    # Pre-update forward identity.
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    idx=batches[0]
    xb=torch.from_numpy(xf[idx]).float()
    _set_determinism(); mc=FrameModel(xf.shape[1])
    _set_determinism(); mi=FrameModel(xf.shape[1])
    with torch.no_grad():
        csl,col=mc(xb); isl,iol=mi(xb)
    if not torch.equal(csl,isl) or not torch.equal(col,iol):
        raise RuntimeError("pre-update logits differ")

    control,cf=fit_arm(features,d["state"],d["onset"],batches,state_weight=CONTROL_STATE_WEIGHT,deadline=deadline)
    intervention,wf=fit_arm(features,d["state"],d["onset"],batches,state_weight=INTERVENTION_STATE_WEIGHT,deadline=deadline)
    if cf["initialModelSha256"]!=wf["initialModelSha256"]:
        raise RuntimeError("S5 initialization mismatch")

    ctest=evaluate_arm(control,d,"test")
    wtest=evaluate_arm(intervention,d,"test")
    cval=evaluate_arm(control,d,"validation")
    wval=evaluate_arm(intervention,d,"validation")

    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    onset_adm_decline=ctest["admission"]["onsetAdmissionFraction"]-wtest["admission"]["onsetAdmissionFraction"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={
        fam:ctest["familyPitchOnset"][fam]["f1"]-wtest["familyPitchOnset"][fam]["f1"]
        for fam in ctest["familyPitchOnset"]
    }

    criteria={
      "stateAdmissionGainAtLeast0_06":state_gain>=.06,
      "jointAdmissionGainAtLeast0_06":joint_gain>=.06,
      "onsetRecallGainAtLeast0_05":recall_gain>=.05,
      "onsetF1GainAtLeast0_04":f1_gain>=.04,
      "absoluteStateAdmissionAtLeast0_40":wtest["admission"]["stateAdmissionFraction"]>=.40,
      "absoluteOnsetRecallAtLeast0_65":wtest["pitchOnset"]["recall"]>=.65,
      "absoluteOnsetF1AtLeast0_74":wtest["pitchOnset"]["f1"]>=.74,
      "repeatedRecallAtLeast0_60":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.60,
      "onsetPrecisionAtLeast0_82":wtest["pitchOnset"]["precision"]>=.82,
      "onsetAdmissionDeclineAtMost0_05":onset_adm_decline<=.05,
      "onsetOffsetDeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noFamilyF1LossOver0_15":all(v<=.15 for v in family_losses.values()),
      "finiteBoth500StepsIdentityZeroThresholdSearch":(
        cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS
        and cf["initialModelSha256"]==wf["initialModelSha256"]
        and all(math.isfinite(float(v)) for v in (
          state_gain,joint_gain,recall_gain,f1_gain,wtest["pitchOnset"]["precision"],wtest["pitchOnset"]["recall"],wtest["pitchOnset"]["f1"]
        ))
      ),
    }

    result={
      "schema":SCHEMA,
      "seed":ROOT_SEED,
      "dataset":{"examples":int(len(features)),"audioSeconds":AUDIO_SECONDS,
                 "splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")},
                 "arrayContentSha256":hashes},
      "batchPlan":{"sha256":identity["batchPlanSha256"],"shape":identity["batchShape"],"stratumSizes":strata,"identicalAcrossArms":True},
      "fixed":{"architecture":"five-frame-960x128","sampler":"onset-aware-32x4",
               "onsetPositiveWeight":ONSET_POS_WEIGHT,"onsetLossWeight":ONSET_LOSS_WEIGHT,
               "learningRate":LEARNING_RATE,"batchSize":BATCH_SIZE,
               "stateThreshold":STATE_ACTIVE_THRESHOLD,"onsetThreshold":ONSET_THRESHOLD,
               "thresholdSearch":False,"thresholdRetuning":False},
      "preUpdateForwardLogitsIdentical":True,
      "control":{"fit":cf,"validation":cval,"test":ctest},
      "weight9":{"fit":wf,"validation":wval,"test":wtest},
      "comparison":{"stateAdmissionGain":state_gain,"jointAdmissionGain":joint_gain,
                    "onsetRecallGain":recall_gain,"onsetF1Gain":f1_gain,
                    "onsetAdmissionDecline":onset_adm_decline,"onsetOffsetF1Decline":offset_decline,
                    "familyF1LossVsControl":family_losses},
      "criteria":criteria,
      "s5GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled state-weight experiment; no real-transfer, unseen-performer, or product claim."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"state-weight-6","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"state-weight-9","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS:
        raise RuntimeError("S5 optimizer ceiling exceeded")
    print("S5_RESULT="+json.dumps(result,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--identity-out",required=True)
    ap.add_argument("--control-model",required=True)
    ap.add_argument("--intervention-model",required=True)
    a=ap.parse_args()
    run(a.dataset,a.out,a.control_model,a.intervention_model,a.identity_out)

if __name__=="__main__":
    main()
