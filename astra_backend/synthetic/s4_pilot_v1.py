#!/usr/bin/env python3
"""Astra S4 synthetic-only shared-encoder gradient-coupling experiment.

Only whether onset loss updates the shared encoder differs between arms.
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

SCHEMA="astra-synthetic-data-diversity-s4-pilot-v1"
STATE_ACTIVE_WEIGHT=6.0
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
MAX_TOTAL_STEPS=1000

def _set_determinism():
    random.seed(ROOT_SEED+10001)
    np.random.seed(ROOT_SEED+10001)
    torch.manual_seed(ROOT_SEED+10001)
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

def batch_plan_sha256(b): return array_content_sha256(np.asarray(b,dtype=np.int64))

def _state_loss(state_logits,target):
    target=target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(state_logits.reshape(-1,NUM_CLASSES),target.reshape(-1),reduction="none").reshape(-1,NUM_STRINGS)
    w=torch.ones_like(raw); w[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    return (raw*w).sum()/w.sum()

def _onset_loss(onset_logits,target):
    return F.binary_cross_entropy_with_logits(
        onset_logits,target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )

def forward_arm(model,x,detach_onset_encoder):
    h=model.encoder(x)
    state_logits=model.state_head(h)
    onset_logits=model.onset_head(h.detach() if detach_onset_encoder else h)
    return state_logits,onset_logits

def model_sha(model):
    h=hashlib.sha256()
    for name,t in sorted(model.state_dict().items()):
        h.update(name.encode()); h.update(b"\0"); h.update(np.ascontiguousarray(t.cpu().numpy()).tobytes())
    return h.hexdigest()

def grad_norm(params):
    total=0.0
    for p in params:
        if p.grad is not None:
            total += float(torch.sum(p.grad.detach()**2))
    return math.sqrt(total)

def gradient_contract(model,x,state,onset,detach):
    # forward identity is checked before any optimization externally
    model.zero_grad(set_to_none=True)
    sl,ol=forward_arm(model,x,detach)
    oloss=_onset_loss(ol,onset)
    oloss.backward()
    onset_encoder=grad_norm(model.encoder.parameters())
    onset_head=grad_norm(model.onset_head.parameters())

    model.zero_grad(set_to_none=True)
    sl,ol=forward_arm(model,x,detach)
    sloss=_state_loss(sl,state)
    sloss.backward()
    state_encoder=grad_norm(model.encoder.parameters())
    state_head=grad_norm(model.state_head.parameters())
    model.zero_grad(set_to_none=True)
    return {
      "onsetEncoderGradNorm":onset_encoder,
      "onsetHeadGradNorm":onset_head,
      "stateEncoderGradNorm":state_encoder,
      "stateHeadGradNorm":state_head,
    }

def fit_arm(features,state,onset,batches,detach,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2]); sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS); of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    _set_determinism()
    model=FrameModel(xf.shape[1])
    init_sha=model_sha(model)
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic(); steps=0; stop="requested_steps_reached"
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline: stop="fit_eval_time_ceiling"; break
        idx=batches[step]
        xb=torch.from_numpy(xf[idx]).float(); sb=torch.from_numpy(sf[idx]).long(); ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=forward_arm(model,xb,detach)
        loss=_state_loss(sl,sb)+ONSET_LOSS_WEIGHT*_onset_loss(ol,ob)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite gradient")
        opt.step(); steps+=1
    return model,{
      "detachOnsetEncoder":bool(detach),"optimizerSteps":steps,"requestedSteps":MAX_STEPS,
      "elapsedSeconds":time.monotonic()-started,"stopReason":stop,"initialModelSha256":init_sha
    }

def evaluate_arm(model,d,split_name):
    features=d["features"].astype(np.float32,copy=False)
    base=evaluate_model(model,features,d["state"],d["onset"],d["family"],
        np.where(d["split"]==split_name,"test","other"),d["negative_only"],d["refs_json"],5)
    base["admission"]=state_admission_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    base["repeatedReferenceOnset"]=repeated_reference_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    return base

def run(dataset,out,control_model,intervention_model,identity_out):
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0: raise RuntimeError("unexpected corpus")
    features=d["features"].astype(np.float32,copy=False)
    if not np.isfinite(features).all(): raise RuntimeError("nonfinite features")
    hashes=dataset_array_hashes(d)
    batches,strata=precompute_batches(d["state"],d["onset"],d["split"],d["has_negative_structure"])
    identity={"schema":"astra-s4-identity-v1","arrayContentSha256":hashes,"batchPlanSha256":batch_plan_sha256(batches),
              "batchShape":list(batches.shape),"stratumSizes":strata,"armsUseSameArrays":True,"armsUseSameBatchIndices":True}
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    # Gradient contract + pre-update forward identity on the same first minibatch.
    xin=context5(features); xf=xin.reshape(-1,xin.shape[2]); sf=d["state"].transpose(0,2,1).reshape(-1,NUM_STRINGS); of=d["onset"].transpose(0,2,1).reshape(-1,NUM_STRINGS)
    idx=batches[0]; xb=torch.from_numpy(xf[idx]).float(); sb=torch.from_numpy(sf[idx]).long(); ob=torch.from_numpy(of[idx]).long()
    _set_determinism(); mc=FrameModel(xf.shape[1])
    _set_determinism(); mi=FrameModel(xf.shape[1])
    with torch.no_grad():
        csl,col=forward_arm(mc,xb,False); isl,iol=forward_arm(mi,xb,True)
    if not torch.equal(csl,isl) or not torch.equal(col,iol): raise RuntimeError("pre-update logits differ")
    gc=gradient_contract(mc,xb,sb,ob,False); gi=gradient_contract(mi,xb,sb,ob,True)
    if not (gc["onsetEncoderGradNorm"]>0 and gc["onsetHeadGradNorm"]>0): raise RuntimeError("control onset gradient contract failed")
    if not (gi["onsetEncoderGradNorm"]==0 and gi["onsetHeadGradNorm"]>0): raise RuntimeError("detached onset gradient contract failed")
    if abs(gc["stateEncoderGradNorm"]-gi["stateEncoderGradNorm"])>1e-12: raise RuntimeError("state encoder gradient mismatch")

    control,cf=fit_arm(features,d["state"],d["onset"],batches,False,deadline)
    intervention,wf=fit_arm(features,d["state"],d["onset"],batches,True,deadline)
    if cf["initialModelSha256"]!=wf["initialModelSha256"]: raise RuntimeError("init mismatch")

    # Fixed post-fit diagnostic minibatch gradient measurements (no optimizer update).
    cpost=gradient_contract(control,xb,sb,ob,False)
    wpost=gradient_contract(intervention,xb,sb,ob,True)

    ctest=evaluate_arm(control,d,"test"); wtest=evaluate_arm(intervention,d,"test")
    cval=evaluate_arm(control,d,"validation"); wval=evaluate_arm(intervention,d,"validation")

    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    repeated_gain=(wtest["repeatedAttackRecall"] or 0)-(ctest["repeatedAttackRecall"] or 0)
    onset_adm_decline=ctest["admission"]["onsetAdmissionFraction"]-wtest["admission"]["onsetAdmissionFraction"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={f:ctest["familyPitchOnset"][f]["f1"]-wtest["familyPitchOnset"][f]["f1"] for f in ctest["familyPitchOnset"]}
    criteria={
      "stateAdmissionGainAtLeast0_08":state_gain>=.08,
      "jointAdmissionGainAtLeast0_08":joint_gain>=.08,
      "onsetF1GainAtLeast0_04":f1_gain>=.04,
      "onsetRecallGainAtLeast0_05":recall_gain>=.05,
      "repeatedRecallGainAtLeast0_05":repeated_gain>=.05,
      "absoluteOnsetF1AtLeast0_74":wtest["pitchOnset"]["f1"]>=.74,
      "absoluteOnsetRecallAtLeast0_63":wtest["pitchOnset"]["recall"]>=.63,
      "absoluteRepeatedRecallAtLeast0_62":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.62,
      "onsetAdmissionDeclineAtMost0_05":onset_adm_decline<=.05,
      "onsetPrecisionAtLeast0_85":wtest["pitchOnset"]["precision"]>=.85,
      "onsetOffsetDeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noFamilyF1LossOver0_15":all(v<=.15 for v in family_losses.values()),
      "finiteBoth500StepsIdentityZeroThresholdSearch":cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS and all(math.isfinite(float(v)) for v in (state_gain,joint_gain,f1_gain,recall_gain))
    }
    result={
      "schema":SCHEMA,"seed":ROOT_SEED,
      "dataset":{"examples":int(len(features)),"audioSeconds":AUDIO_SECONDS,"splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")},"arrayContentSha256":hashes},
      "batchPlan":{"sha256":identity["batchPlanSha256"],"shape":identity["batchShape"],"identicalAcrossArms":True,"stratumSizes":strata},
      "fixed":{"architecture":"five-frame-960x128","stateActiveWeight":STATE_ACTIVE_WEIGHT,"onsetPositiveWeight":ONSET_POS_WEIGHT,"onsetLossWeight":ONSET_LOSS_WEIGHT,
               "sampler":"onset-aware-32x4","learningRate":LEARNING_RATE,"batchSize":BATCH_SIZE,"stateThreshold":STATE_ACTIVE_THRESHOLD,"onsetThreshold":ONSET_THRESHOLD,
               "thresholdSearch":False,"thresholdRetuning":False},
      "gradientContract":{"preUpdateControl":gc,"preUpdateDetached":gi,"postFitControl":cpost,"postFitDetached":wpost,"preUpdateForwardLogitsIdentical":True},
      "control":{"fit":cf,"validation":cval,"test":ctest},
      "detachedOnset":{"fit":wf,"validation":wval,"test":wtest},
      "comparison":{"stateAdmissionGain":state_gain,"jointAdmissionGain":joint_gain,"onsetF1Gain":f1_gain,"onsetRecallGain":recall_gain,
                    "repeatedRecallGain":repeated_gain,"onsetAdmissionDecline":onset_adm_decline,"onsetOffsetF1Decline":offset_decline,"familyF1LossVsControl":family_losses},
      "criteria":criteria,"s4GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],"fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled gradient-coupling experiment; no real-transfer, unseen-performer, or product claim."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"control","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"detached-onset","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("optimizer ceiling")
    print("S4_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True); ap.add_argument("--out",required=True); ap.add_argument("--identity-out",required=True)
    ap.add_argument("--control-model",required=True); ap.add_argument("--intervention-model",required=True)
    a=ap.parse_args(); run(a.dataset,a.out,a.control_model,a.intervention_model,a.identity_out)

if __name__=="__main__": main()
