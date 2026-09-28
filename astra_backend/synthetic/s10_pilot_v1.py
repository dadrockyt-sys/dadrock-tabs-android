#!/usr/bin/env python3
"""Astra S10 identity-preserving state-head widening experiment."""
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
from synthetic.s2_pilot_v1 import dataset_array_hashes
from synthetic.s3_pilot_v1 import repeated_reference_diagnostics
from synthetic.s6_pilot_v1 import precompute_batches, batch_plan_sha256
from synthetic.s2_pilot_v1 import state_admission_diagnostics

SCHEMA="astra-synthetic-data-diversity-s10-pilot-v1"
STATE_ACTIVE_WEIGHT=9.0
ONSET_POS_WEIGHT=8.0
ONSET_LOSS_WEIGHT=4.0
CONTROL_WIDTH=128
WIDE_WIDTH=192
MAX_TOTAL_STEPS=1000

def _set_determinism():
    random.seed(ROOT_SEED+14001)
    np.random.seed(ROOT_SEED+14001)
    torch.manual_seed(ROOT_SEED+14001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))

class S10Model(nn.Module):
    def __init__(self,input_dim,width):
        super().__init__()
        if width not in (CONTROL_WIDTH,WIDE_WIDTH):
            raise ValueError("unsupported S10 width")
        self.width=int(width)
        self.encoder=nn.Sequential(nn.Linear(input_dim,128),nn.ReLU())
        self.state_hidden=nn.Linear(128,width)
        self.state_out=nn.Linear(width,NUM_STRINGS*NUM_CLASSES)
        self.onset_head=nn.Linear(128,NUM_STRINGS)

    def forward(self,x):
        h=self.encoder(x)
        state=self.state_out(F.relu(self.state_hidden(h)))
        return state,self.onset_head(h)

def module_sha(module):
    h=hashlib.sha256()
    for name,t in sorted(module.state_dict().items()):
        h.update(name.encode()); h.update(b"\0")
        h.update(np.ascontiguousarray(t.detach().cpu().numpy()).tobytes())
    return h.hexdigest()

def init_pair(input_dim):
    _set_determinism()
    control=S10Model(input_dim,CONTROL_WIDTH)
    wide=S10Model(input_dim,WIDE_WIDTH)

    torch.manual_seed(ROOT_SEED+14011)
    for m in control.encoder.modules():
        if isinstance(m,nn.Linear): m.reset_parameters()
    wide.encoder.load_state_dict(control.encoder.state_dict())

    torch.manual_seed(ROOT_SEED+14012)
    control.onset_head.reset_parameters()
    wide.onset_head.load_state_dict(control.onset_head.state_dict())

    torch.manual_seed(ROOT_SEED+14013)
    control.state_hidden.reset_parameters()
    torch.manual_seed(ROOT_SEED+14014)
    control.state_out.reset_parameters()

    with torch.no_grad():
        wide.state_hidden.weight[:CONTROL_WIDTH].copy_(control.state_hidden.weight)
        wide.state_hidden.bias[:CONTROL_WIDTH].copy_(control.state_hidden.bias)
        torch.manual_seed(ROOT_SEED+14015)
        extra_w=torch.empty_like(wide.state_hidden.weight[CONTROL_WIDTH:])
        nn.init.kaiming_uniform_(extra_w,a=math.sqrt(5))
        wide.state_hidden.weight[CONTROL_WIDTH:].copy_(extra_w)
        fan_in=wide.state_hidden.in_features
        bound=1/math.sqrt(fan_in)
        extra_b=torch.empty_like(wide.state_hidden.bias[CONTROL_WIDTH:])
        extra_b.uniform_(-bound,bound)
        wide.state_hidden.bias[CONTROL_WIDTH:].copy_(extra_b)

        wide.state_out.weight[:,:CONTROL_WIDTH].copy_(control.state_out.weight)
        wide.state_out.bias.copy_(control.state_out.bias)
        wide.state_out.weight[:,CONTROL_WIDTH:].zero_()

    return control,wide

def identity_contract(control,wide,x):
    with torch.no_grad():
        cs,co=control(x); ws,wo=wide(x)
    checks={
      "encoderIdentical":module_sha(control.encoder)==module_sha(wide.encoder),
      "onsetHeadIdentical":module_sha(control.onset_head)==module_sha(wide.onset_head),
      "hiddenFirst128WeightIdentical":bool(torch.equal(control.state_hidden.weight,wide.state_hidden.weight[:CONTROL_WIDTH])),
      "hiddenFirst128BiasIdentical":bool(torch.equal(control.state_hidden.bias,wide.state_hidden.bias[:CONTROL_WIDTH])),
      "outputFirst128Identical":bool(torch.equal(control.state_out.weight,wide.state_out.weight[:,:CONTROL_WIDTH])),
      "outputBiasIdentical":bool(torch.equal(control.state_out.bias,wide.state_out.bias)),
      "extraHiddenNonzero":bool(torch.count_nonzero(wide.state_hidden.weight[CONTROL_WIDTH:]).item()>0),
      "extraOutputExactlyZero":bool(torch.count_nonzero(wide.state_out.weight[:,CONTROL_WIDTH:]).item()==0),
      "stateLogitsIdentical":bool(torch.equal(cs,ws)),
      "onsetLogitsIdentical":bool(torch.equal(co,wo)),
    }
    if not all(checks.values()):
        raise RuntimeError("S10 identity-preserving widening contract failed: "+json.dumps(checks,sort_keys=True))
    return checks

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

def extra_path_norm(model):
    if model.width!=WIDE_WIDTH: return 0.0
    total=float(torch.sum(model.state_hidden.weight[CONTROL_WIDTH:]**2))
    total+=float(torch.sum(model.state_hidden.bias[CONTROL_WIDTH:]**2))
    total+=float(torch.sum(model.state_out.weight[:,CONTROL_WIDTH:]**2))
    return math.sqrt(total)

def fit_arm(model,features,state,onset,batches,deadline):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    started=time.monotonic(); steps=0; stop="requested_steps_reached"
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"; break
        idx=batches[step]
        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss,_,_=weighted_loss(sl,ol,sb,ob)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite S10 loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite S10 gradient")
        opt.step(); steps+=1
    return {
      "width":model.width,"optimizerSteps":steps,"requestedSteps":MAX_STEPS,
      "elapsedSeconds":time.monotonic()-started,"stopReason":stop,
      "encoderInitSha256":module_sha(model.encoder),
      "onsetHeadInitSha256":module_sha(model.onset_head),
      "extra64ParameterNormAfterTraining":extra_path_norm(model),
      "totalParameters":int(sum(p.numel() for p in model.parameters())),
    }

def evaluate_arm(model,d,split_name):
    features=d["features"].astype(np.float32,copy=False)
    base=evaluate_model(
        model,features,d["state"],d["onset"],d["family"],
        np.where(d["split"]==split_name,"test","other"),
        d["negative_only"],d["refs_json"],5
    )
    base["admission"]=state_admission_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    base["repeatedReferenceOnset"]=repeated_reference_diagnostics(model,features,d["state"],d["onset"],d["split"],split_name)
    return base

def run(dataset,out,control_model,wide_model,identity_out):
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected S10 dataset")
    if int(np.sum((d["family"]=="chords")&(d["split"]=="train")))!=30:
        raise RuntimeError("S10 chord train count mismatch")

    batches,strata=precompute_batches(d["state"],d["onset"],d["split"],d["has_negative_structure"])
    features=d["features"].astype(np.float32,copy=False)
    xin=context5(features); xf=xin.reshape(-1,xin.shape[2])
    c,w=init_pair(xf.shape[1])
    preflight=identity_contract(c,w,torch.from_numpy(xf[batches[0]]).float())

    cfit=fit_arm(c,features,d["state"],d["onset"],batches,deadline)
    wfit=fit_arm(w,features,d["state"],d["onset"],batches,deadline)

    ctest=evaluate_arm(c,d,"test"); wtest=evaluate_arm(w,d,"test")
    cval=evaluate_arm(c,d,"validation"); wval=evaluate_arm(w,d,"validation")

    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    f1_decline=ctest["pitchOnset"]["f1"]-wtest["pitchOnset"]["f1"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    family_losses={f:ctest["familyPitchOnset"][f]["f1"]-wtest["familyPitchOnset"][f]["f1"] for f in ctest["familyPitchOnset"]}

    criteria={
      "stateAdmissionGainAtLeast0_04":state_gain>=.04,
      "jointAdmissionGainAtLeast0_03":joint_gain>=.03,
      "absoluteStateAdmissionAtLeast0_44":wtest["admission"]["stateAdmissionFraction"]>=.44,
      "absoluteJointAdmissionAtLeast0_42":wtest["admission"]["jointAdmissionFraction"]>=.42,
      "onsetRecallAtLeast0_72":wtest["pitchOnset"]["recall"]>=.72,
      "onsetF1AtLeast0_78":wtest["pitchOnset"]["f1"]>=.78,
      "chordF1AtLeast0_62":wtest["familyPitchOnset"]["chords"]["f1"]>=.62,
      "chordRecallAtLeast0_55":wtest["familyPitchOnset"]["chords"]["recall"]>=.55,
      "repeatedRecallAtLeast0_60":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.60,
      "onsetPrecisionAtLeast0_83":wtest["pitchOnset"]["precision"]>=.83,
      "onsetF1DeclineAtMost0_02":f1_decline<=.02,
      "onsetOffsetF1DeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noFamilyF1LossOver0_15":all(v<=.15 for v in family_losses.values()),
      "extra64PathwayLearned":wfit["extra64ParameterNormAfterTraining"]>0,
      "finiteBoth500StepsIdentityZeroThresholdSearch":(
        cfit["optimizerSteps"]==500 and wfit["optimizerSteps"]==500
        and all(preflight.values())
        and all(math.isfinite(float(v)) for v in (
          state_gain,joint_gain,wtest["pitchOnset"]["precision"],wtest["pitchOnset"]["recall"],wtest["pitchOnset"]["f1"]
        ))
      )
    }

    identity={
      "schema":"astra-s10-identity-v1",
      "datasetArrayContentSha256":dataset_array_hashes(d),
      "batchPlanSha256":batch_plan_sha256(batches),
      "batchShape":list(batches.shape),
      "stratumSizes":strata,
      "preUpdate":preflight,
    }
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    result={
      "schema":SCHEMA,"seed":ROOT_SEED,
      "fixed":{"dataset":"S9 30-unique-voicing intervention dataset","stateActiveWeight":9.0,"onsetPositiveWeight":8.0,
               "onsetLossWeight":4.0,"sampler":"uniform onset-aware 32/32/32/32","learningRate":LEARNING_RATE,
               "stateThreshold":STATE_ACTIVE_THRESHOLD,"onsetThreshold":ONSET_THRESHOLD,
               "thresholdSearch":False,"thresholdRetuning":False},
      "identity":identity,
      "control128":{"fit":cfit,"validation":cval,"test":ctest},
      "wide192":{"fit":wfit,"validation":wval,"test":wtest},
      "comparison":{"stateAdmissionGain":state_gain,"jointAdmissionGain":joint_gain,
                    "onsetF1Decline":f1_decline,"onsetOffsetF1Decline":offset_decline,
                    "familyF1LossVsControl":family_losses},
      "criteria":criteria,"s10GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cfit["optimizerSteps"]+wfit["optimizerSteps"],
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled identity-preserving state-head-width experiment."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"width-128","stateDict":c.state_dict(),"optimizerSteps":cfit["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"width-192","stateDict":w.state_dict(),"optimizerSteps":wfit["optimizerSteps"]},wide_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("S10 optimizer ceiling")
    print("S10_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True); ap.add_argument("--out",required=True); ap.add_argument("--identity-out",required=True)
    ap.add_argument("--control-model",required=True); ap.add_argument("--wide-model",required=True)
    a=ap.parse_args(); run(a.dataset,a.out,a.control_model,a.wide_model,a.identity_out)

if __name__=="__main__": main()
