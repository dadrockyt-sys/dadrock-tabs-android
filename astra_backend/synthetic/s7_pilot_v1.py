#!/usr/bin/env python3
"""Astra S7 synthetic-only zero-initialized residual state-capacity experiment."""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, BATCH_SIZE, LEARNING_RATE,
    NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD,
    EXAMPLES, AUDIO_SECONDS, MAX_FIT_EVAL_SECONDS,
    context5, evaluate_model,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import array_content_sha256, dataset_array_hashes, state_admission_diagnostics
from synthetic.s3_pilot_v1 import repeated_reference_diagnostics

SCHEMA="astra-synthetic-data-diversity-s7-pilot-v1"
STATE_ACTIVE_WEIGHT=9.0
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
MAX_TOTAL_STEPS=1000

def _set_determinism():
    random.seed(ROOT_SEED+13001)
    np.random.seed(ROOT_SEED+13001)
    torch.manual_seed(ROOT_SEED+13001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))

class S7Model(nn.Module):
    def __init__(self,input_dim,use_residual):
        super().__init__()
        self.encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.base_state_head=nn.Linear(128,NUM_STRINGS*NUM_CLASSES)
        self.onset_head=nn.Linear(128,NUM_STRINGS)
        self.use_residual=bool(use_residual)
        if self.use_residual:
            self.residual_hidden=nn.Linear(128,128)
            self.residual_out=nn.Linear(128,NUM_STRINGS*NUM_CLASSES)
        else:
            self.residual_hidden=None
            self.residual_out=None

    def forward(self,x):
        h=self.encoder(x)
        state=self.base_state_head(h)
        if self.use_residual:
            state=state+self.residual_out(F.relu(self.residual_hidden(h)))
        return state,self.onset_head(h)

def module_sha(module):
    h=hashlib.sha256()
    for name,t in sorted(module.state_dict().items()):
        h.update(name.encode()); h.update(b"\0")
        h.update(np.ascontiguousarray(t.detach().cpu().numpy()).tobytes())
    return h.hexdigest()

def parameter_count(module):
    return int(sum(p.numel() for p in module.parameters()))

def initialize_arm(input_dim,use_residual):
    _set_determinism()
    model=S7Model(input_dim,use_residual)
    torch.manual_seed(ROOT_SEED+13011)
    for m in model.encoder.modules():
        if isinstance(m,nn.Linear): m.reset_parameters()
    torch.manual_seed(ROOT_SEED+13012)
    model.onset_head.reset_parameters()
    torch.manual_seed(ROOT_SEED+13013)
    model.base_state_head.reset_parameters()
    if use_residual:
        torch.manual_seed(ROOT_SEED+13014)
        model.residual_hidden.reset_parameters()
        with torch.no_grad():
            model.residual_out.weight.zero_()
            model.residual_out.bias.zero_()
    return model

def residual_parameter_norm(model):
    if not model.use_residual:
        return 0.0
    total=0.0
    for p in list(model.residual_hidden.parameters())+list(model.residual_out.parameters()):
        total+=float(torch.sum(p.detach()**2))
    return math.sqrt(total)

def residual_output_zero(model):
    if not model.use_residual:
        return True
    return bool(torch.count_nonzero(model.residual_out.weight).item()==0 and torch.count_nonzero(model.residual_out.bias).item()==0)

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

def weighted_loss(state_logits,onset_logits,state_target,onset_target):
    target=state_target.clone()
    target[target==-1]=SILENCE_CLASS
    raw=F.cross_entropy(state_logits.reshape(-1,NUM_CLASSES),target.reshape(-1),reduction="none").reshape(-1,NUM_STRINGS)
    w=torch.ones_like(raw); w[target!=SILENCE_CLASS]=STATE_ACTIVE_WEIGHT
    state_loss=(raw*w).sum()/w.sum()
    onset_loss=F.binary_cross_entropy_with_logits(
        onset_logits,onset_target.float(),
        pos_weight=torch.tensor(ONSET_POS_WEIGHT,dtype=onset_logits.dtype),
    )
    return state_loss+ONSET_LOSS_WEIGHT*onset_loss,state_loss,onset_loss

def fit_arm(features,state,onset,batches,*,use_residual,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    model=initialize_arm(xf.shape[1],use_residual)
    init={
      "encoderInitSha256":module_sha(model.encoder),
      "onsetHeadInitSha256":module_sha(model.onset_head),
      "baseStateHeadInitSha256":module_sha(model.base_state_head),
      "residualOutputExactlyZeroAtInit":residual_output_zero(model),
      "totalParameters":parameter_count(model),
      "stateHeadParameters":parameter_count(model.base_state_head)+(parameter_count(model.residual_hidden)+parameter_count(model.residual_out) if use_residual else 0),
    }
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic(); steps=0; stop="requested_steps_reached"
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"; break
        idx=batches[step]
        xb=torch.from_numpy(xf[idx]).float(); sb=torch.from_numpy(sf[idx]).long(); ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss,_,_=weighted_loss(sl,ol,sb,ob)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite S7 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S7 gradient")
        opt.step(); steps+=1
    init.update({
      "useResidual":bool(use_residual),"optimizerSteps":steps,"requestedSteps":MAX_STEPS,
      "elapsedSeconds":time.monotonic()-started,"stopReason":stop,
      "residualParameterNormAfterTraining":residual_parameter_norm(model),
    })
    return model,init

def evaluate_arm(model,d,split_name):
    features=d["features"].astype(np.float32,copy=False)
    base=evaluate_model(
        model,features,d["state"],d["onset"],d["family"],
        np.where(d["split"]==split_name,"test","other"),d["negative_only"],d["refs_json"],5
    )
    base["admission"]=state_admission_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    base["repeatedReferenceOnset"]=repeated_reference_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    return base

def run(dataset,out,control_model,intervention_model,identity_out):
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0: raise RuntimeError("unexpected S7 corpus")
    features=d["features"].astype(np.float32,copy=False)
    if not np.isfinite(features).all(): raise RuntimeError("nonfinite S7 features")

    hashes=dataset_array_hashes(d)
    batches,strata=precompute_batches(d["state"],d["onset"],d["split"],d["has_negative_structure"])
    identity={"schema":"astra-s7-identity-v1","arrayContentSha256":hashes,"batchPlanSha256":batch_plan_sha256(batches),
              "batchShape":list(batches.shape),"stratumSizes":strata,"armsUseSameArrays":True,"armsUseSameBatchIndices":True}
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    xin=context5(features); xf=xin.reshape(-1,xin.shape[2]); idx=batches[0]
    xb=torch.from_numpy(xf[idx]).float()
    mc=initialize_arm(xf.shape[1],False); mi=initialize_arm(xf.shape[1],True)
    if module_sha(mc.encoder)!=module_sha(mi.encoder): raise RuntimeError("encoder init mismatch")
    if module_sha(mc.onset_head)!=module_sha(mi.onset_head): raise RuntimeError("onset head init mismatch")
    if module_sha(mc.base_state_head)!=module_sha(mi.base_state_head): raise RuntimeError("base state init mismatch")
    if not residual_output_zero(mi): raise RuntimeError("residual output not zero")
    with torch.no_grad():
        cstate,conset=mc(xb); istate,ionset=mi(xb)
    if not torch.equal(cstate,istate): raise RuntimeError("pre-update state logits differ")
    if not torch.equal(conset,ionset): raise RuntimeError("pre-update onset logits differ")

    control,cf=fit_arm(features,d["state"],d["onset"],batches,use_residual=False,deadline=deadline)
    intervention,wf=fit_arm(features,d["state"],d["onset"],batches,use_residual=True,deadline=deadline)
    for k in ("encoderInitSha256","onsetHeadInitSha256","baseStateHeadInitSha256"):
        if cf[k]!=wf[k]: raise RuntimeError(k+" mismatch")

    ctest=evaluate_arm(control,d,"test"); wtest=evaluate_arm(intervention,d,"test")
    cval=evaluate_arm(control,d,"validation"); wval=evaluate_arm(intervention,d,"validation")

    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    onset_adm_decline=ctest["admission"]["onsetAdmissionFraction"]-wtest["admission"]["onsetAdmissionFraction"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={f:ctest["familyPitchOnset"][f]["f1"]-wtest["familyPitchOnset"][f]["f1"] for f in ctest["familyPitchOnset"]}

    criteria={
      "stateAdmissionGainAtLeast0_07":state_gain>=.07,
      "jointAdmissionGainAtLeast0_06":joint_gain>=.06,
      "onsetRecallGainAtLeast0_04":recall_gain>=.04,
      "onsetF1GainAtLeast0_03":f1_gain>=.03,
      "absoluteStateAdmissionAtLeast0_40":wtest["admission"]["stateAdmissionFraction"]>=.40,
      "absoluteOnsetRecallAtLeast0_64":wtest["pitchOnset"]["recall"]>=.64,
      "absoluteOnsetF1AtLeast0_74":wtest["pitchOnset"]["f1"]>=.74,
      "repeatedRecallAtLeast0_60":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.60,
      "onsetPrecisionAtLeast0_85":wtest["pitchOnset"]["precision"]>=.85,
      "onsetAdmissionDeclineAtMost0_04":onset_adm_decline<=.04,
      "onsetOffsetDeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noFamilyF1LossOver0_15":all(v<=.15 for v in family_losses.values()),
      "residualParameterNormAfterTrainingPositive":wf["residualParameterNormAfterTraining"]>0,
      "finiteBoth500StepsIdentityZeroThresholdSearch":(
        cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS
        and cf["encoderInitSha256"]==wf["encoderInitSha256"]
        and cf["onsetHeadInitSha256"]==wf["onsetHeadInitSha256"]
        and cf["baseStateHeadInitSha256"]==wf["baseStateHeadInitSha256"]
        and wf["residualOutputExactlyZeroAtInit"] is True
        and all(math.isfinite(float(v)) for v in (state_gain,joint_gain,recall_gain,f1_gain,wtest["pitchOnset"]["precision"],wtest["pitchOnset"]["recall"],wtest["pitchOnset"]["f1"]))
      ),
    }

    result={
      "schema":SCHEMA,"seed":ROOT_SEED,
      "dataset":{"examples":int(len(features)),"audioSeconds":AUDIO_SECONDS,
                 "splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")},
                 "arrayContentSha256":hashes},
      "batchPlan":{"sha256":identity["batchPlanSha256"],"shape":identity["batchShape"],"stratumSizes":strata,"identicalAcrossArms":True},
      "fixed":{"sharedEncoder":"Linear(960,128)+ReLU","onsetHead":"Linear(128,6)","stateActiveWeight":STATE_ACTIVE_WEIGHT,
               "onsetPositiveWeight":ONSET_POS_WEIGHT,"onsetLossWeight":ONSET_LOSS_WEIGHT,"sampler":"onset-aware-32x4",
               "learningRate":LEARNING_RATE,"batchSize":BATCH_SIZE,"stateThreshold":STATE_ACTIVE_THRESHOLD,
               "onsetThreshold":ONSET_THRESHOLD,"thresholdSearch":False,"thresholdRetuning":False},
      "preUpdate":{"sharedEncoderIdentical":True,"onsetHeadIdentical":True,"baseStateHeadIdentical":True,
                   "residualOutputExactlyZero":True,"stateLogitsIdentical":True,"onsetLogitsIdentical":True},
      "control":{"fit":cf,"validation":cval,"test":ctest},
      "residualStateHead":{"fit":wf,"validation":wval,"test":wtest},
      "comparison":{"stateAdmissionGain":state_gain,"jointAdmissionGain":joint_gain,"onsetRecallGain":recall_gain,
                    "onsetF1Gain":f1_gain,"onsetAdmissionDecline":onset_adm_decline,
                    "onsetOffsetF1Decline":offset_decline,"familyF1LossVsControl":family_losses},
      "criteria":criteria,"s7GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled zero-initialized residual-state-capacity experiment."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"linear-control","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"residual-state","stateDict":intervention.state_dict(),"optimizerSteps":wf["optimizerSteps"]},intervention_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("S7 optimizer ceiling")
    print("S7_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True); ap.add_argument("--out",required=True); ap.add_argument("--identity-out",required=True)
    ap.add_argument("--control-model",required=True); ap.add_argument("--intervention-model",required=True)
    a=ap.parse_args(); run(a.dataset,a.out,a.control_model,a.intervention_model,a.identity_out)

if __name__=="__main__": main()
