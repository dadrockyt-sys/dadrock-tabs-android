#!/usr/bin/env python3
"""Astra S8 synthetic-only token-balanced positive-frame sampling experiment.

Only positive-onset frame sampling differs. Both arms use the frozen S6
nonlinear replacement state head and identical non-positive minibatch indices.
"""
from __future__ import annotations
import argparse, json, math, time
from pathlib import Path
import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, MAX_STEPS, NUM_STRINGS, EXAMPLES, AUDIO_SECONDS,
    MAX_FIT_EVAL_SECONDS, context5,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s2_pilot_v1 import array_content_sha256, dataset_array_hashes
from synthetic.s6_pilot_v1 import initialize_arm, module_sha, fit_arm, evaluate_arm

SCHEMA="astra-synthetic-data-diversity-s8-pilot-v1"
MAX_TOTAL_STEPS=1000

def batch_plan_sha256(b): return array_content_sha256(np.asarray(b,dtype=np.int64))

def positive_multiplicity(onset):
    return np.asarray(onset).transpose(0,2,1).reshape(-1,NUM_STRINGS).sum(axis=1).astype(np.int64)

def build_paired_batch_plans(state,onset,split,negative_structure):
    strata=build_sampling_strata(state,onset,split,negative_structure)
    positive=np.asarray(strata["positiveOnset"],dtype=np.int64)
    mult=positive_multiplicity(onset)
    pm=mult[positive]
    if np.any(pm<=0): raise RuntimeError("positive stratum contains zero-multiplicity frame")
    probs=pm.astype(np.float64); probs/=probs.sum()

    rng_pos_control=np.random.RandomState(ROOT_SEED+8001)
    rng_pos_weighted=np.random.RandomState(ROOT_SEED+8002)
    rng_nonpos=np.random.RandomState(ROOT_SEED+8003)
    rng_perm=np.random.RandomState(ROOT_SEED+8004)

    control=[]; weighted=[]; positive_position_masks=[]
    for _ in range(MAX_STEPS):
        pc=rng_pos_control.choice(positive,32,replace=True)
        pw=rng_pos_weighted.choice(positive,32,replace=True,p=probs)
        a=rng_nonpos.choice(strata["activeNonOnset"],32,replace=True)
        n=rng_nonpos.choice(strata["negativeStructureInactive"],32,replace=True)
        o=rng_nonpos.choice(strata["otherInactive"],32,replace=True)
        perm=rng_perm.permutation(128)
        c=np.concatenate([pc,a,n,o])[perm]
        w=np.concatenate([pw,a,n,o])[perm]
        mask=(perm<32)
        if not np.array_equal(c[~mask],w[~mask]):
            raise RuntimeError("paired non-positive indices differ")
        control.append(c.astype(np.int64,copy=False))
        weighted.append(w.astype(np.int64,copy=False))
        positive_position_masks.append(mask)
    control=np.stack(control); weighted=np.stack(weighted); masks=np.stack(positive_position_masks)

    def selected_stats(plan):
        vals=mult[plan[masks]]
        unique,counts=np.unique(vals,return_counts=True)
        return {
          "selectedPositiveFrames":int(vals.size),
          "meanPositiveStringsPerSelectedFrame":float(vals.mean()),
          "multiplicityCounts":{str(int(k)):int(v) for k,v in zip(unique,counts)},
        }

    accounting={
      "positiveFrames":int(len(positive)),
      "positiveStringTokens":int(pm.sum()),
      "sumMultiplicitySquared":int(np.sum(pm*pm)),
      "uniformExpectedPositiveStringsPerFrame":float(pm.mean()),
      "weightedExpectedPositiveStringsPerFrame":float(np.sum(pm*pm)/np.sum(pm)),
      "multiplicityFrameCounts":{str(int(k)):int(v) for k,v in zip(*np.unique(pm,return_counts=True))},
      "controlSelected":selected_stats(control),
      "weightedSelected":selected_stats(weighted),
    }
    return control,weighted,masks,{k:int(len(v)) for k,v in strata.items()},accounting

def run(dataset,out,control_model,weighted_model,identity_out):
    started=time.monotonic(); deadline=started+MAX_FIT_EVAL_SECONDS
    d=np.load(dataset,allow_pickle=False)
    if len(d["features"])!=EXAMPLES or float(AUDIO_SECONDS)!=588.0:
        raise RuntimeError("unexpected S8 corpus")
    features=d["features"].astype(np.float32,copy=False)
    if not np.isfinite(features).all(): raise RuntimeError("nonfinite S8 features")

    hashes=dataset_array_hashes(d)
    control_batches,weighted_batches,masks,strata,accounting=build_paired_batch_plans(
        d["state"],d["onset"],d["split"],d["has_negative_structure"]
    )
    if accounting["positiveFrames"]!=525 or accounting["positiveStringTokens"]!=645 or accounting["sumMultiplicitySquared"]!=1005:
        raise RuntimeError("S8 frozen positive accounting mismatch")

    identity={
      "schema":"astra-s8-identity-v1",
      "arrayContentSha256":hashes,
      "controlBatchPlanSha256":batch_plan_sha256(control_batches),
      "weightedBatchPlanSha256":batch_plan_sha256(weighted_batches),
      "batchShape":list(control_batches.shape),
      "stratumSizes":strata,
      "pairedNonPositiveIndicesIdentical":bool(np.array_equal(control_batches[~masks],weighted_batches[~masks])),
      "positiveAccounting":accounting,
    }
    Path(identity_out).write_text(json.dumps(identity,indent=2,sort_keys=True)+"\n")

    xin=context5(features); xf=xin.reshape(-1,xin.shape[2]); xb=torch.from_numpy(xf[control_batches[0]]).float()
    mc=initialize_arm(xf.shape[1],True); mw=initialize_arm(xf.shape[1],True)
    if module_sha(mc)!=module_sha(mw): raise RuntimeError("S8 whole-model init mismatch")
    with torch.no_grad():
        cs,co=mc(xb); ws,wo=mw(xb)
    if not torch.equal(cs,ws) or not torch.equal(co,wo): raise RuntimeError("S8 pre-update logits differ")

    control,cf=fit_arm(features,d["state"],d["onset"],control_batches,nonlinear=True,deadline=deadline)
    weighted,wf=fit_arm(features,d["state"],d["onset"],weighted_batches,nonlinear=True,deadline=deadline)
    if cf["encoderInitSha256"]!=wf["encoderInitSha256"] or cf["onsetHeadInitSha256"]!=wf["onsetHeadInitSha256"] or cf["stateHeadInitSha256"]!=wf["stateHeadInitSha256"]:
        raise RuntimeError("S8 initialization mismatch")

    ctest=evaluate_arm(control,d,"test"); wtest=evaluate_arm(weighted,d,"test")
    cval=evaluate_arm(control,d,"validation"); wval=evaluate_arm(weighted,d,"validation")

    chord_c=ctest["familyPitchOnset"]["chords"]; chord_w=wtest["familyPitchOnset"]["chords"]
    chord_f1_gain=chord_w["f1"]-chord_c["f1"]
    chord_recall_gain=chord_w["recall"]-chord_c["recall"]
    state_gain=wtest["admission"]["stateAdmissionFraction"]-ctest["admission"]["stateAdmissionFraction"]
    joint_gain=wtest["admission"]["jointAdmissionFraction"]-ctest["admission"]["jointAdmissionFraction"]
    recall_gain=wtest["pitchOnset"]["recall"]-ctest["pitchOnset"]["recall"]
    f1_gain=wtest["pitchOnset"]["f1"]-ctest["pitchOnset"]["f1"]
    offset_decline=ctest["pitchOnsetOffset"]["f1"]-wtest["pitchOnsetOffset"]["f1"]
    non_chord_losses={f:ctest["familyPitchOnset"][f]["f1"]-wtest["familyPitchOnset"][f]["f1"] for f in ctest["familyPitchOnset"] if f!="chords"}

    criteria={
      "chordOnsetF1GainAtLeast0_15":chord_f1_gain>=.15,
      "chordRecallGainAtLeast0_15":chord_recall_gain>=.15,
      "stateAdmissionGainAtLeast0_06":state_gain>=.06,
      "jointAdmissionGainAtLeast0_05":joint_gain>=.05,
      "overallOnsetRecallGainAtLeast0_04":recall_gain>=.04,
      "overallOnsetF1GainAtLeast0_03":f1_gain>=.03,
      "absoluteStateAdmissionAtLeast0_42":wtest["admission"]["stateAdmissionFraction"]>=.42,
      "absoluteOnsetRecallAtLeast0_65":wtest["pitchOnset"]["recall"]>=.65,
      "absoluteOnsetF1AtLeast0_75":wtest["pitchOnset"]["f1"]>=.75,
      "repeatedRecallAtLeast0_55":wtest["repeatedAttackRecall"] is not None and wtest["repeatedAttackRecall"]>=.55,
      "onsetPrecisionAtLeast0_82":wtest["pitchOnset"]["precision"]>=.82,
      "onsetOffsetDeclineAtMost0_03":offset_decline<=.03,
      "negativeOnlyFalsePositiveRateAtMost0_10PerSecond":wtest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and wtest["negativeOnlyFalsePositiveEventsPerSecond"]<=.10,
      "noNonChordFamilyF1LossOver0_15":all(v<=.15 for v in non_chord_losses.values()),
      "finiteBoth500StepsIdentityPairedNonPositiveZeroThresholdSearch":(
        cf["optimizerSteps"]==MAX_STEPS and wf["optimizerSteps"]==MAX_STEPS
        and identity["pairedNonPositiveIndicesIdentical"]
        and cf["encoderInitSha256"]==wf["encoderInitSha256"]
        and cf["onsetHeadInitSha256"]==wf["onsetHeadInitSha256"]
        and cf["stateHeadInitSha256"]==wf["stateHeadInitSha256"]
        and all(math.isfinite(float(v)) for v in (chord_f1_gain,chord_recall_gain,state_gain,joint_gain,recall_gain,f1_gain))
      ),
    }

    result={
      "schema":SCHEMA,"seed":ROOT_SEED,
      "dataset":{"examples":int(len(features)),"audioSeconds":AUDIO_SECONDS,"splitCounts":{s:int(np.sum(d["split"]==s)) for s in ("train","validation","test")},"arrayContentSha256":hashes},
      "batchPlans":{
        "controlSha256":identity["controlBatchPlanSha256"],"weightedSha256":identity["weightedBatchPlanSha256"],
        "shape":identity["batchShape"],"pairedNonPositiveIndicesIdentical":identity["pairedNonPositiveIndicesIdentical"],
        "positiveAccounting":accounting,
      },
      "fixed":{"architecture":"five-frame shared encoder + nonlinear replacement state head","stateActiveWeight":9.0,"onsetPositiveWeight":8.0,
               "onsetLossWeight":4.0,"batchSize":128,"positiveFramesPerBatch":32,"nonPositiveFramesPerBatch":96,
               "learningRate":0.003,"stateThreshold":0.5,"onsetThreshold":0.5,"thresholdSearch":False,"thresholdRetuning":False},
      "preUpdate":{"wholeModelInitializationIdentical":True,"stateLogitsIdentical":True,"onsetLogitsIdentical":True},
      "controlUniformPositive":{"fit":cf,"validation":cval,"test":ctest},
      "tokenBalancedPositive":{"fit":wf,"validation":wval,"test":wtest},
      "comparison":{"chordOnsetF1Gain":chord_f1_gain,"chordRecallGain":chord_recall_gain,"stateAdmissionGain":state_gain,
                    "jointAdmissionGain":joint_gain,"onsetRecallGain":recall_gain,"onsetF1Gain":f1_gain,
                    "onsetOffsetF1Decline":offset_decline,"nonChordFamilyF1LossVsControl":non_chord_losses},
      "criteria":criteria,"s8GatePassed":all(criteria.values()),
      "execution":{"modelCount":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],"fitEvalSeconds":time.monotonic()-started,"automaticRetry":False,"paidComputeDollars":0},
      "guards":{"externalAudioAssets":False,"p1Accessed":False,"p2Accessed":False,"p3Opened":False,"codespacesUsed":False,"vercelUsed":False,"productionMutation":False},
      "meaning":"Synthetic-only controlled positive-frame multiplicity-weighting experiment."
    }
    Path(out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"uniform-positive","stateDict":control.state_dict(),"optimizerSteps":cf["optimizerSteps"]},control_model)
    torch.save({"schema":SCHEMA,"arm":"token-balanced-positive","stateDict":weighted.state_dict(),"optimizerSteps":wf["optimizerSteps"]},weighted_model)
    if result["execution"]["optimizerStepsTotal"]>MAX_TOTAL_STEPS: raise RuntimeError("S8 optimizer ceiling")
    print("S8_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset",required=True); ap.add_argument("--out",required=True); ap.add_argument("--identity-out",required=True)
    ap.add_argument("--control-model",required=True); ap.add_argument("--weighted-model",required=True)
    a=ap.parse_args(); run(a.dataset,a.out,a.control_model,a.weighted_model,a.identity_out)

if __name__=="__main__": main()
