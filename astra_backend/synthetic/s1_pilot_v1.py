#!/usr/bin/env python3
"""Astra S1 synthetic-only onset-aware sampling pilot.

Changes exactly one experimental variable relative to the frozen S1 design:
training-frame sampling policy. Both arms use the same five-frame model,
generator/split, loss, learning rate, decoder, thresholds, and step budget.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, BATCH_SIZE, LEARNING_RATE,
    NUM_STRINGS, NUM_CLASSES, SILENCE_CLASS,
    STATE_ACTIVE_THRESHOLD, ONSET_THRESHOLD,
    HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ,
    FAMILIES, EXAMPLES, AUDIO_SECONDS,
    MAX_FIT_EVAL_SECONDS,
    context5, FrameModel, _loss, evaluate_model,
)

SCHEMA="astra-synthetic-data-diversity-s1-pilot-v1"
MODELS=2
MAX_TOTAL_STEPS=1000


def _set_determinism():
    random.seed(ROOT_SEED+5001)
    np.random.seed(ROOT_SEED+5001)
    torch.manual_seed(ROOT_SEED+5001)
    torch.use_deterministic_algorithms(True)
    torch.set_num_threads(max(1,min(4,os.cpu_count() or 1)))


def build_sampling_strata(state,onset,split,has_negative_structure):
    """Return flattened training-frame indices for the four frozen strata."""
    state=np.asarray(state)
    onset=np.asarray(onset)
    split=np.asarray(split)
    neg=np.asarray(has_negative_structure,dtype=bool)
    if state.ndim!=3 or onset.shape!=state.shape:
        raise ValueError("target shape mismatch")
    n,strings,frames=state.shape
    if strings!=NUM_STRINGS:
        raise ValueError("unexpected string count")
    train_clip=(split=="train")
    clip_idx=np.repeat(np.arange(n),frames)
    frame_idx=np.tile(np.arange(frames),n)
    train=np.repeat(train_clip,frames)
    onset_frame=(onset==1).any(axis=1).reshape(-1)
    active_frame=((state>=0) & (state<SILENCE_CLASS)).any(axis=1).reshape(-1)
    neg_frame=np.repeat(neg,frames)

    positive=np.flatnonzero(train & onset_frame)
    active_non=np.flatnonzero(train & active_frame & ~onset_frame)
    neg_inactive=np.flatnonzero(train & ~active_frame & ~onset_frame & neg_frame)
    other_inactive=np.flatnonzero(train & ~active_frame & ~onset_frame & ~neg_frame)
    strata={
        "positiveOnset":positive,
        "activeNonOnset":active_non,
        "negativeStructureInactive":neg_inactive,
        "otherInactive":other_inactive,
    }
    if any(len(v)==0 for v in strata.values()):
        raise RuntimeError("one or more frozen S1 sampling strata are empty")
    return strata


def _flat_targets(features,state,onset):
    xin=context5(features)
    xf=xin.reshape(-1,xin.shape[2])
    sf=state.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    of=onset.transpose(0,2,1).reshape(-1,NUM_STRINGS)
    return xf,sf,of


def fit_arm(features,state,onset,split,has_negative_structure,*,sampler,deadline):
    xf,sf,of=_flat_targets(features,state,onset)
    train_mask=np.repeat(np.asarray(split)=="train",features.shape[1])
    train=np.flatnonzero(train_mask)
    strata=build_sampling_strata(state,onset,split,has_negative_structure)

    _set_determinism()
    model=FrameModel(xf.shape[1])
    opt=torch.optim.Adam(model.parameters(),lr=LEARNING_RATE)
    rng=np.random.RandomState(ROOT_SEED+7001)
    started=time.monotonic()
    steps=0
    stop="requested_steps_reached"

    while steps<MAX_STEPS:
        if time.monotonic()>=deadline:
            stop="fit_eval_time_ceiling"
            break
        if sampler=="uniform":
            idx=rng.choice(train,size=BATCH_SIZE,replace=True)
        elif sampler=="onset_aware_32x4":
            chunks=[
                rng.choice(strata["positiveOnset"],size=32,replace=True),
                rng.choice(strata["activeNonOnset"],size=32,replace=True),
                rng.choice(strata["negativeStructureInactive"],size=32,replace=True),
                rng.choice(strata["otherInactive"],size=32,replace=True),
            ]
            idx=np.concatenate(chunks)
            idx=idx[rng.permutation(len(idx))]
        else:
            raise ValueError("unknown sampler")

        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ob=torch.from_numpy(of[idx]).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss=_loss(sl,ol,sb,ob)
        if not torch.isfinite(loss):
            raise RuntimeError("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite gradient")
        opt.step()
        steps+=1

    return model,{
        "sampler":sampler,
        "optimizerSteps":steps,
        "requestedSteps":MAX_STEPS,
        "elapsedSeconds":time.monotonic()-started,
        "stopReason":stop,
        "stratumSizes":{k:int(len(v)) for k,v in strata.items()},
    }


def admission_diagnostics(model,features,state,onset,split_name,split):
    xin=context5(features)
    indices=np.flatnonzero(np.asarray(split)==split_name)
    total=on_pass=state_pass=joint=0
    logits=[]
    probs=[]
    model.eval()
    with torch.no_grad():
        for i in indices:
            x=torch.from_numpy(xin[i]).float()
            sl,ol=model(x)
            sp=torch.softmax(sl.reshape(-1,NUM_STRINGS,NUM_CLASSES),dim=-1).cpu().numpy()
            op=torch.sigmoid(ol).cpu().numpy()
            ol_np=ol.cpu().numpy()
            for s in range(NUM_STRINGS):
                frames=np.flatnonzero(onset[i,s]==1)
                for k in frames:
                    fret=int(state[i,s,k])
                    if not 0<=fret<SILENCE_CLASS:
                        continue
                    total+=1
                    onset_ok=bool(op[k,s]>=ONSET_THRESHOLD)
                    row=sp[k,s]
                    best=int(np.argmax(row[:SILENCE_CLASS]))
                    state_ok=bool(best==fret and row[fret]>=STATE_ACTIVE_THRESHOLD and row[fret]>row[SILENCE_CLASS])
                    on_pass+=int(onset_ok)
                    state_pass+=int(state_ok)
                    joint+=int(onset_ok and state_ok)
                    logits.append(float(ol_np[k,s]))
                    probs.append(float(op[k,s]))
    def stats(values):
        if not values:
            return None
        a=np.asarray(values,dtype=np.float64)
        return {"count":int(len(a)),"mean":float(a.mean()),"min":float(a.min()),"max":float(a.max()),
                "p25":float(np.quantile(a,.25)),"median":float(np.quantile(a,.5)),"p75":float(np.quantile(a,.75))}
    return {
        "positiveReferenceStringFrames":total,
        "onsetAdmissionFraction":on_pass/total if total else None,
        "stateAdmissionFraction":state_pass/total if total else None,
        "jointAdmissionFraction":joint/total if total else None,
        "onsetLogit":stats(logits),
        "onsetProbability":stats(probs),
    }


def evaluate_arm(model,d,split_name):
    base=evaluate_model(
        model,d["features"].astype(np.float32,copy=False),d["state"],d["onset"],
        d["family"],np.where(d["split"]==split_name,"test","other"),
        d["negative_only"],d["refs_json"],5
    )
    base["admission"]=admission_diagnostics(
        model,d["features"].astype(np.float32,copy=False),d["state"],d["onset"],
        split_name,d["split"]
    )
    return base


def run(dataset,out,uniform_model,balanced_model):
    started=time.monotonic()
    deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES:
        raise RuntimeError("unexpected deterministic S1 example count")
    if float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected deterministic S1 audio seconds")
    if not np.isfinite(d["features"]).all():
        raise RuntimeError("nonfinite synthetic features")

    uniform,uf=fit_arm(
        d["features"].astype(np.float32,copy=False),d["state"],d["onset"],d["split"],
        d["has_negative_structure"],sampler="uniform",deadline=deadline
    )
    balanced,bf=fit_arm(
        d["features"].astype(np.float32,copy=False),d["state"],d["onset"],d["split"],
        d["has_negative_structure"],sampler="onset_aware_32x4",deadline=deadline
    )
    utest=evaluate_arm(uniform,d,"test")
    btest=evaluate_arm(balanced,d,"test")
    uval=evaluate_arm(uniform,d,"validation")
    bval=evaluate_arm(balanced,d,"validation")

    f1_gain=btest["pitchOnset"]["f1"]-utest["pitchOnset"]["f1"]
    recall_gain=btest["pitchOnset"]["recall"]-utest["pitchOnset"]["recall"]
    repeated_gain=(btest["repeatedAttackRecall"] or 0)-(utest["repeatedAttackRecall"] or 0)
    precision_loss=utest["pitchOnset"]["precision"]-btest["pitchOnset"]["precision"]
    criteria={
      "onsetF1GainAtLeast0_15":f1_gain>=.15,
      "onsetRecallGainAtLeast0_20":recall_gain>=.20,
      "repeatedRecallGainAtLeast0_20":repeated_gain>=.20,
      "balancedPrecisionAtLeast0_80":btest["pitchOnset"]["precision"]>=.80,
      "precisionLossVsUniformAtMost0_10":precision_loss<=.10,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":(
          btest["negativeOnlyFalsePositiveEventsPerSecond"] is not None
          and btest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10
      ),
      "absoluteOnsetRecallAtLeast0_55":btest["pitchOnset"]["recall"]>=.55,
      "absoluteOnsetF1AtLeast0_60":btest["pitchOnset"]["f1"]>=.60,
      "repeatedRecallAtLeast0_50":(
          btest["repeatedAttackRecall"] is not None and btest["repeatedAttackRecall"]>=.50
      ),
      "finiteBoth500StepsZeroThresholdSearch":(
          uf["optimizerSteps"]==MAX_STEPS and bf["optimizerSteps"]==MAX_STEPS
          and all(math.isfinite(float(x)) for x in (
              btest["pitchOnset"]["precision"],btest["pitchOnset"]["recall"],btest["pitchOnset"]["f1"]
          ))
      ),
    }
    passed=all(criteria.values())
    result={
      "schema":SCHEMA,
      "seed":ROOT_SEED,
      "dataset":{"examples":int(len(d["features"])),"audioSeconds":AUDIO_SECONDS,
                 "splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")}},
      "execution":{"modelCount":MODELS,"optimizerStepsTotal":uf["optimizerSteps"]+bf["optimizerSteps"],
                   "fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "fixed":{"architecture":"five-frame-960x128","learningRate":LEARNING_RATE,
               "batchSize":BATCH_SIZE,"onsetThreshold":ONSET_THRESHOLD,
               "stateThreshold":STATE_ACTIVE_THRESHOLD,"thresholdSearch":False,"thresholdRetuning":False},
      "uniform":{"fit":uf,"validation":uval,"test":utest},
      "onsetAware":{"fit":bf,"validation":bval,"test":btest},
      "comparison":{"onsetF1Gain":f1_gain,"onsetRecallGain":recall_gain,
                    "repeatedRecallGain":repeated_gain,"precisionLossVsUniform":precision_loss},
      "criteria":criteria,
      "s1GatePassed":passed,
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,
                "productionMutation":False,"customerDeliveryEligible":False},
      "meaning":"Synthetic-only controlled sampling-policy test; no real-transfer, unseen-performer, or product claim."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"uniform","stateDict":uniform.state_dict(),"optimizerSteps":uf["optimizerSteps"]},uniform_model)
    torch.save({"schema":SCHEMA,"arm":"onsetAware","stateDict":balanced.state_dict(),"optimizerSteps":bf["optimizerSteps"]},balanced_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS:
        raise RuntimeError("total optimizer ceiling exceeded")
    print("S1_RESULT="+json.dumps(result,sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True)
    ap.add_argument("--out",required=True)
    ap.add_argument("--uniform-model",required=True)
    ap.add_argument("--balanced-model",required=True)
    args=ap.parse_args()
    run(args.dataset,args.out,args.uniform_model,args.balanced_model)

if __name__=="__main__":
    main()
