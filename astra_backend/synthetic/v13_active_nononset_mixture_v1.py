#!/usr/bin/env python3
"""Astra V13 active-non-onset family-mixture isolation.

Preparation is model-free until a separately authorized empirical launch exists.

Both arms use the same regenerated executed-V9 arrays.
Control reproduces the executed V9 batch plan.
Intervention changes only active-non-onset selections to match the historical
2-second comparator family mixture. Positive-onset, negative-structure-inactive,
other-inactive selections and per-step shuffle are identical across arms.
"""
from __future__ import annotations
import argparse, hashlib, json, time
from pathlib import Path
import numpy as np
import torch

from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s6_pilot_v1 import initialize_arm, module_sha, evaluate_arm
from synthetic.v9_empirical_v1 import ROOT, MAX_STEPS, BATCH_SIZE, _dataset, _fit

SCHEMA="astra-v13-active-nononset-mixture-v1"
FIT_DEADLINE_SECONDS=3600.0
FAMILIES=("isolated","scales","chords","repeated","legato","palmmute","mixed")
TARGET_SLOTS={
    "isolated":2511,"scales":2569,"chords":2219,"repeated":2861,
    "legato":3037,"palmmute":1752,"mixed":1051,
}
TOTAL_ACTIVE_SLOTS=MAX_STEPS*32
MIXTURE_SEED=ROOT+23001

class V13Error(RuntimeError): pass

def _sha_array(a):
    x=np.ascontiguousarray(a); h=hashlib.sha256()
    h.update(str(x.dtype).encode()); h.update(b"\0")
    h.update(json.dumps(list(x.shape),separators=(",",":")).encode()); h.update(b"\0")
    h.update(x.tobytes())
    return h.hexdigest()

def static_summary():
    if sum(TARGET_SLOTS.values())!=TOTAL_ACTIVE_SLOTS:
        raise V13Error("target slot total mismatch")
    return {
      "schema":"astra-v13-active-nononset-mixture-static-v1",
      "targetActiveNonOnsetSlots":TARGET_SLOTS,
      "totalActiveNonOnsetSlots":TOTAL_ACTIVE_SLOTS,
      "waveformsRendered":0,"modelsTrained":0,"optimizerSteps":0,
      "modelInference":0,"v2bInference":0,
    }

def _family_pools(d,strata):
    frames=d["state"].shape[2]
    pools={}
    for fam in FAMILIES:
        rows=[]
        for idx in strata["activeNonOnset"]:
            clip=int(idx)//frames
            if str(d["family"][clip])==fam:
                rows.append(int(idx))
        pools[fam]=np.asarray(rows,dtype=np.int64)
        if len(pools[fam])==0:
            raise V13Error(f"empty active-non-onset pool {fam}")
    return pools

def _schedule():
    labels=[]
    for fam in FAMILIES:
        labels.extend([fam]*TARGET_SLOTS[fam])
    labels=np.asarray(labels,dtype=object)
    rng=np.random.RandomState(MIXTURE_SEED)
    return labels[rng.permutation(len(labels))]

def build_paired_batch_plans(v9):
    strata=build_sampling_strata(v9["state"],v9["onset"],v9["split"],v9["has_negative_structure"])
    pools=_family_pools(v9,strata)
    schedule=_schedule()
    baseline_rng=np.random.RandomState(ROOT+17001)
    mix_rng=np.random.RandomState(MIXTURE_SEED+1)
    control=[]; intervention=[]
    observed={f:0 for f in FAMILIES}
    control_active_family={f:0 for f in FAMILIES}
    frames=v9["state"].shape[2]
    cursor=0
    keys=("positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive")

    for _ in range(MAX_STEPS):
        chunks=[]
        for k in keys:
            u=baseline_rng.random_sample(32)
            chunks.append(strata[k][np.minimum((u*len(strata[k])).astype(int),len(strata[k])-1)])
        perm=baseline_rng.permutation(BATCH_SIZE)

        for idx in chunks[1]:
            fam=str(v9["family"][int(idx)//frames]); control_active_family[fam]+=1

        fams=schedule[cursor:cursor+32]; cursor+=32
        mixed=[]
        for fam in fams:
            p=pools[str(fam)]
            j=min(int(mix_rng.random_sample()*len(p)),len(p)-1)
            mixed.append(p[j]); observed[str(fam)]+=1
        intervention_active=np.asarray(mixed,dtype=np.int64)

        c=np.concatenate(chunks)[perm].astype(np.int64,copy=False)
        i=np.concatenate([chunks[0],intervention_active,chunks[2],chunks[3]])[perm].astype(np.int64,copy=False)
        control.append(c); intervention.append(i)

    if observed!=TARGET_SLOTS:
        raise V13Error(f"target schedule mismatch {observed}")

    cb=np.stack(control); ib=np.stack(intervention)
    return cb,ib,{
      "strata":{k:int(len(v)) for k,v in strata.items()},
      "controlActiveNonOnsetFamilySlots":control_active_family,
      "interventionActiveNonOnsetFamilySlots":observed,
      "positiveOnsetSelectionsIdenticalAcrossArms":True,
      "negativeStructureInactiveSelectionsIdenticalAcrossArms":True,
      "otherInactiveSelectionsIdenticalAcrossArms":True,
      "samePerStepPermutationAcrossArms":True,
      "controlBatchPlanSha256":_sha_array(cb),
      "interventionBatchPlanSha256":_sha_array(ib),
    }

def _metric_view(x):
    return {
      "precision":float(x["pitchOnset"]["precision"]),
      "recall":float(x["pitchOnset"]["recall"]),
      "f1":float(x["pitchOnset"]["f1"]),
      "negativeFpPerSecond":float(x["negativeOnlyFalsePositiveEventsPerSecond"]),
      "stateAdmission":float(x["admission"]["stateAdmissionFraction"]),
      "onsetAdmission":float(x["admission"]["onsetAdmissionFraction"]),
      "jointAdmission":float(x["admission"]["jointAdmissionFraction"]),
    }

def run(outdir):
    started=time.monotonic(); deadline=started+FIT_DEADLINE_SECONDS
    out=Path(outdir); out.mkdir(parents=True,exist_ok=False)
    common,_=_dataset(2.0,False)
    v9,_=_dataset(4.0,True)
    cb,ib,identity=build_paired_batch_plans(v9)

    m0=initialize_arm(960,True); m1=initialize_arm(960,True)
    if module_sha(m0)!=module_sha(m1):
        raise V13Error("initialization mismatch")

    cm,cf=_fit(v9,cb,deadline)
    im,wf=_fit(v9,ib,deadline)
    cc=_metric_view(evaluate_arm(cm,common,"test"))
    ic=_metric_view(evaluate_arm(im,common,"test"))
    cv=_metric_view(evaluate_arm(cm,v9,"test"))
    iv=_metric_view(evaluate_arm(im,v9,"test"))

    frozen={"precision":0.3244274809160305,"recall":0.6589147286821705,"f1":0.43478260869565216}
    reproduced=all(abs(cc[k]-v)<=1e-12 for k,v in frozen.items())
    checks={
      "baselineReproducedExactly":reproduced,
      "commonPrecisionGainAtLeast0_15":ic["precision"]-cc["precision"]>=.15,
      "commonF1GainAtLeast0_10":ic["f1"]-cc["f1"]>=.10,
      "commonRecallDeclineAtMost0_05":cc["recall"]-ic["recall"]<=.05,
      "commonNegativeFpPerSecondAtMost0_10":ic["negativeFpPerSecond"]<=.10,
      "v9F1DeclineAtMost0_05":cv["f1"]-iv["f1"]<=.05,
      "exact500StepsPerModel":cf["optimizerSteps"]==500 and wf["optimizerSteps"]==500,
      "attackedNoteLabelExposureIdentical":cf["sampledAttackedNoteLabels"]==wf["sampledAttackedNoteLabels"],
    }

    result={
      "schema":SCHEMA,
      "identity":identity,
      "control":{"fit":cf,"commonComparatorTest":cc,"v9Test":cv},
      "historicalActiveNonOnsetMixture":{"fit":wf,"commonComparatorTest":ic,"v9Test":iv},
      "deltas":{
        "commonPrecision":ic["precision"]-cc["precision"],
        "commonRecall":ic["recall"]-cc["recall"],
        "commonF1":ic["f1"]-cc["f1"],
        "commonNegativeFpPerSecond":ic["negativeFpPerSecond"]-cc["negativeFpPerSecond"],
        "v9F1":iv["f1"]-cv["f1"],
      },
      "checks":checks,
      "activeNonOnsetFamilyMixtureHypothesisSupported":all(checks.values()),
      "execution":{
        "models":2,
        "optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
        "elapsedSeconds":time.monotonic()-started,
        "automaticScientificRetries":0,
        "thresholdSearch":False,
        "realAudioInference":0,
        "v2bInference":0,
      },
      "meaning":"Synthetic-only active-non-onset family-mixture diagnostic."
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"v9-control","stateDict":cm.state_dict()},out/"control.pt")
    torch.save({"schema":SCHEMA,"arm":"historical-active-nononset-mixture","stateDict":im.state_dict()},out/"intervention.pt")
    return result

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("static"); s.add_argument("--out",required=True)
    r=sub.add_parser("run"); r.add_argument("--outdir",required=True)
    a=ap.parse_args()
    if a.cmd=="static":
        x=static_summary(); Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps(x,sort_keys=True))
    else:
        print(json.dumps(run(a.outdir),sort_keys=True))

if __name__=="__main__": main()
