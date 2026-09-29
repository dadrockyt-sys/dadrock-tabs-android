#!/usr/bin/env python3
"""Astra V10 synthetic exposure-isolation study.

Prospective question:
Does exact matching of sampled attacked-note-label exposure explain a material part
of the V9 synthetic precision/F1 collapse?

This file is preparation code only until a separately armed V10 execution launch
exists. It reuses the frozen V9 dataset construction and changes one training
variable: sampling inside the positive-onset stratum.

Control: exact frozen V9 positive-onset sampling.
Intervention: exact attacked-note-label exposure target (19,702 labels) by changing
only which positive-onset frames are sampled. Non-positive strata, batch size,
per-step shuffle, model, loss, thresholds, optimizer and update count stay fixed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s6_pilot_v1 import initialize_arm, module_sha, weighted_loss, evaluate_arm
from synthetic.v9_empirical_v1 import (
    ROOT,
    MAX_STEPS,
    BATCH_SIZE,
    _dataset,
    _flat,
)

SCHEMA="astra-v10-exposure-isolation-v1"
TARGET_POSITIVE_FRAMES=MAX_STEPS*32
TARGET_ATTACKED_NOTE_LABELS=19702
BASELINE_EXPECTED_ATTACKED_NOTE_LABELS=17676
MULTI_LABEL_VALUE=3
SINGLE_LABEL_VALUE=1
# labels = 16000 + 2 * multi_count => multi_count = 1851
TARGET_MULTI_POSITIVE_FRAMES=(TARGET_ATTACKED_NOTE_LABELS-TARGET_POSITIVE_FRAMES)//2
TARGET_SINGLE_POSITIVE_FRAMES=TARGET_POSITIVE_FRAMES-TARGET_MULTI_POSITIVE_FRAMES
BALANCE_SEED=ROOT+19001
FIT_DEADLINE_SECONDS=3600.0


class V10Error(RuntimeError):
    pass


def _sha_array(a):
    x=np.ascontiguousarray(a)
    h=hashlib.sha256()
    h.update(str(x.dtype).encode()); h.update(b"\0")
    h.update(json.dumps(list(x.shape),separators=(",",":")).encode()); h.update(b"\0")
    h.update(x.tobytes())
    return h.hexdigest()


def _positive_multiplicity(onset, flat_indices):
    """Number of attacked string labels in each flattened frame index."""
    onset=np.asarray(onset)
    if onset.ndim!=3 or onset.shape[1]!=6:
        raise V10Error("unexpected onset target shape")
    frames=onset.shape[2]
    clip=np.asarray(flat_indices,dtype=np.int64)//frames
    frame=np.asarray(flat_indices,dtype=np.int64)%frames
    return onset[clip,:,frame].sum(axis=1).astype(np.int64)


def _target_multi_schedule():
    """Exactly 351 four-multi batches + 149 three-multi batches, deterministically ordered."""
    if TARGET_MULTI_POSITIVE_FRAMES!=1851:
        raise V10Error("target multi-frame arithmetic changed")
    schedule=np.array([4]*351+[3]*149,dtype=np.int64)
    rng=np.random.RandomState(BALANCE_SEED)
    return schedule[rng.permutation(len(schedule))]


def build_paired_batch_plans(comparator, v9):
    """Reproduce V9 control plan and build exposure-balanced plan.

    The control path preserves the exact V9 RNG sequence. The intervention replaces
    only the 32 positive-onset selections before applying the same per-step shuffle.
    """
    cs=build_sampling_strata(comparator["state"],comparator["onset"],comparator["split"],comparator["has_negative_structure"])
    vs=build_sampling_strata(v9["state"],v9["onset"],v9["split"],v9["has_negative_structure"])

    pos=vs["positiveOnset"]
    mult=_positive_multiplicity(v9["onset"],pos)
    uniq=set(int(x) for x in np.unique(mult))
    if not uniq.issubset({SINGLE_LABEL_VALUE,MULTI_LABEL_VALUE}) or MULTI_LABEL_VALUE not in uniq or SINGLE_LABEL_VALUE not in uniq:
        raise V10Error(f"positive onset multiplicities must be exactly 1/3, got {sorted(uniq)}")
    single_pool=pos[mult==SINGLE_LABEL_VALUE]
    multi_pool=pos[mult==MULTI_LABEL_VALUE]
    if len(single_pool)==0 or len(multi_pool)==0:
        raise V10Error("missing single or multi positive pool")

    baseline_rng=np.random.RandomState(ROOT+17001)
    balance_rng=np.random.RandomState(BALANCE_SEED+1)
    schedule=_target_multi_schedule()
    control=[]; balanced=[]
    control_pos_labels=0; balanced_pos_labels=0
    nonpositive_identical=True

    keys=("positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive")
    for step in range(MAX_STEPS):
        control_chunks=[]
        v9_chunks=[]
        for k in keys:
            u=baseline_rng.random_sample(32)
            control_chunks.append(cs[k][np.minimum((u*len(cs[k])).astype(int),len(cs[k])-1)])
            v9_chunks.append(vs[k][np.minimum((u*len(vs[k])).astype(int),len(vs[k])-1)])
        perm=baseline_rng.permutation(BATCH_SIZE)
        base_chunks=[x.copy() for x in v9_chunks]

        n_multi=int(schedule[step]); n_single=32-n_multi
        bpos=np.concatenate([
            balance_rng.choice(multi_pool,size=n_multi,replace=True),
            balance_rng.choice(single_pool,size=n_single,replace=True),
        ])
        bpos=bpos[balance_rng.permutation(len(bpos))]
        bal_chunks=[bpos,base_chunks[1],base_chunks[2],base_chunks[3]]

        base_batch=np.concatenate(base_chunks)[perm].astype(np.int64,copy=False)
        bal_batch=np.concatenate(bal_chunks)[perm].astype(np.int64,copy=False)
        control.append(base_batch); balanced.append(bal_batch)

        control_pos_labels+=int(_positive_multiplicity(v9["onset"],base_chunks[0]).sum())
        balanced_pos_labels+=int(_positive_multiplicity(v9["onset"],bpos).sum())
        if any(not np.array_equal(base_chunks[j],bal_chunks[j]) for j in (1,2,3)):
            nonpositive_identical=False

    control=np.stack(control); balanced=np.stack(balanced)
    if balanced_pos_labels!=TARGET_ATTACKED_NOTE_LABELS:
        raise V10Error(f"balanced exposure mismatch {balanced_pos_labels}")
    if int(schedule.sum())!=TARGET_MULTI_POSITIVE_FRAMES:
        raise V10Error("multi-frame schedule mismatch")

    return control,balanced,{
        "controlBatchPlanSha256":_sha_array(control),
        "balancedBatchPlanSha256":_sha_array(balanced),
        "positiveSlotsPerArm":TARGET_POSITIVE_FRAMES,
        "controlSampledAttackedNoteLabels":control_pos_labels,
        "balancedSampledAttackedNoteLabels":balanced_pos_labels,
        "targetSampledAttackedNoteLabels":TARGET_ATTACKED_NOTE_LABELS,
        "balancedMultiPositiveFrames":int(schedule.sum()),
        "balancedSinglePositiveFrames":int(TARGET_SINGLE_POSITIVE_FRAMES),
        "nonPositiveSelectionsIdenticalAcrossArms":nonpositive_identical,
        "samePerStepPermutationAcrossArms":True,
        "strata":{"comparator":{k:int(len(v)) for k,v in cs.items()},"v9":{k:int(len(v)) for k,v in vs.items()}},
    }


def _fit(v9,batches,deadline):
    xf,sf,of,_=_flat(v9)
    model=initialize_arm(960,True)
    opt=torch.optim.Adam(model.parameters(),lr=.003)
    started=time.monotonic(); sampled_labels=0
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline:
            raise V10Error("fit deadline exceeded")
        idx=batches[step]
        ob=of[idx]
        sampled_labels+=int(ob.sum())
        xb=torch.from_numpy(xf[idx]).float()
        sb=torch.from_numpy(sf[idx]).long()
        ot=torch.from_numpy(ob).long()
        opt.zero_grad(set_to_none=True)
        sl,ol=model(xb)
        loss,_,_=weighted_loss(sl,ol,sb,ot)
        if not torch.isfinite(loss):
            raise V10Error("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise V10Error("nonfinite gradient")
        opt.step()
    return model,{
        "optimizerSteps":MAX_STEPS,
        "sampledFrames":int(MAX_STEPS*BATCH_SIZE),
        "sampledPositiveOnsetFrames":TARGET_POSITIVE_FRAMES,
        "sampledAttackedNoteLabels":sampled_labels,
        "elapsedSeconds":time.monotonic()-started,
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
    """Empirical entry point for a future separately authorized launch."""
    started=time.monotonic(); deadline=started+FIT_DEADLINE_SECONDS
    out=Path(outdir); out.mkdir(parents=True,exist_ok=False)

    comparator,_=_dataset(2.0,False)
    v9,_=_dataset(4.0,True)
    control_batches,balanced_batches,identity=build_paired_batch_plans(comparator,v9)

    # Frozen V9 baseline exposure is a validity check for exact reproduction.
    if identity["controlSampledAttackedNoteLabels"]!=BASELINE_EXPECTED_ATTACKED_NOTE_LABELS:
        raise V10Error(
            f"V9 baseline exposure reproduction mismatch: {identity['controlSampledAttackedNoteLabels']} "
            f"!= {BASELINE_EXPECTED_ATTACKED_NOTE_LABELS}"
        )

    m0=initialize_arm(960,True); m1=initialize_arm(960,True)
    if module_sha(m0)!=module_sha(m1):
        raise V10Error("model initialization mismatch")

    control,cf=_fit(v9,control_batches,deadline)
    balanced,bf=_fit(v9,balanced_batches,deadline)

    # Evaluate both on the exact same two fixed synthetic populations.
    c_common=evaluate_arm(control,comparator,"test")
    b_common=evaluate_arm(balanced,comparator,"test")
    c_v9=evaluate_arm(control,v9,"test")
    b_v9=evaluate_arm(balanced,v9,"test")

    common0=_metric_view(c_common); common1=_metric_view(b_common)
    v90=_metric_view(c_v9); v91=_metric_view(b_v9)

    baseline_target={"precision":0.3244274809160305,"recall":0.6589147286821705,"f1":0.43478260869565216}
    baseline_reproduced=all(abs(common0[k]-v)<=1e-12 for k,v in baseline_target.items())

    checks={
        "baselineReproducedExactly":baseline_reproduced,
        "balancedExposureExactly19702":bf["sampledAttackedNoteLabels"]==TARGET_ATTACKED_NOTE_LABELS,
        "controlExposureExactly17676":cf["sampledAttackedNoteLabels"]==BASELINE_EXPECTED_ATTACKED_NOTE_LABELS,
        "commonPrecisionGainAtLeast0_20":common1["precision"]-common0["precision"]>=.20,
        "commonF1GainAtLeast0_15":common1["f1"]-common0["f1"]>=.15,
        "commonRecallDeclineAtMost0_08":common0["recall"]-common1["recall"]<=.08,
        "commonNegativeFpPerSecondAtMost0_10":common1["negativeFpPerSecond"]<=.10,
        "v9PrecisionDeclineAtMost0_05":v90["precision"]-v91["precision"]<=.05,
        "v9F1DeclineAtMost0_05":v90["f1"]-v91["f1"]<=.05,
        "exact500StepsPerModel":cf["optimizerSteps"]==500 and bf["optimizerSteps"]==500,
    }
    supported=all(checks.values())

    result={
        "schema":SCHEMA,
        "identity":identity,
        "control":{"fit":cf,"commonComparatorTest":common0,"v9Test":v90},
        "exposureBalanced":{"fit":bf,"commonComparatorTest":common1,"v9Test":v91},
        "deltas":{
            "commonPrecision":common1["precision"]-common0["precision"],
            "commonRecall":common1["recall"]-common0["recall"],
            "commonF1":common1["f1"]-common0["f1"],
            "v9Precision":v91["precision"]-v90["precision"],
            "v9F1":v91["f1"]-v90["f1"],
        },
        "checks":checks,
        "exposureHypothesisSupported":supported,
        "execution":{
            "models":2,
            "optimizerStepsTotal":cf["optimizerSteps"]+bf["optimizerSteps"],
            "elapsedSeconds":time.monotonic()-started,
            "realAudioInference":0,
            "automaticScientificRetries":0,
            "thresholdSearch":False,
        },
        "meaning":"Synthetic-only causal diagnostic of positive-onset attacked-note-label exposure. No real-transfer or product claim.",
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"v9-control","stateDict":control.state_dict()},out/"control.pt")
    torch.save({"schema":SCHEMA,"arm":"exposure-balanced","stateDict":balanced.state_dict()},out/"balanced.pt")
    return result


def static_contract_summary():
    schedule=_target_multi_schedule()
    return {
        "schema":"astra-v10-exposure-isolation-static-v1",
        "positiveSlotsPerArm":TARGET_POSITIVE_FRAMES,
        "targetAttackedNoteLabels":TARGET_ATTACKED_NOTE_LABELS,
        "baselineExpectedAttackedNoteLabels":BASELINE_EXPECTED_ATTACKED_NOTE_LABELS,
        "multiPositiveFrames":int(schedule.sum()),
        "singlePositiveFrames":int(TARGET_SINGLE_POSITIVE_FRAMES),
        "fourMultiBatches":int(np.sum(schedule==4)),
        "threeMultiBatches":int(np.sum(schedule==3)),
        "optimizerStepsPlanned":0,
        "modelInferencePlanned":False,
    }


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("static"); s.add_argument("--out",required=True)
    r=sub.add_parser("run"); r.add_argument("--outdir",required=True)
    a=ap.parse_args()
    if a.cmd=="static":
        x=static_contract_summary(); Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps(x,sort_keys=True))
    else:
        print(json.dumps(run(a.outdir),sort_keys=True))


if __name__=="__main__":
    main()
