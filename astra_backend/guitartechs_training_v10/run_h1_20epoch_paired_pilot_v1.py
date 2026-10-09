#!/usr/bin/env python3
"""Frozen paired H1 pilot driver. Never resumes, exports trained models, or changes V9."""
from __future__ import annotations
import argparse
import json
import platform
from pathlib import Path
import sys
import torch
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from guitartechs_training_v9 import train_v9_resumable as v9
from guitartechs_training_v9.paired_view import paired_tensor_views
from guitartechs_training_v10 import h1_pilot_core_v1 as core
from guitartechs_training_v10 import h1_pilot_readiness_v1 as safety
from guitartechs_training_v10 import h1_prepared_array_guard_v1 as prepared

CANDIDATE="astra_guitartechs_h1_perposition_kl_pilot_v1"
SCHEMA="astra-guitartechs-h1-original-vs-perposition-20epoch-pilot-v1"


def offline_test(source_root):
    v9._setup_determinism()
    model,_=v9._new_model_and_optimizer(source_root)
    model.train()
    baseline=v9.base.state_sha256(model)
    x=torch.rand((1,200,1,192,9),generator=torch.Generator().manual_seed(92841))
    labels=torch.full((1,6,200),-1,dtype=torch.long)
    labels[:,0,20:36]=3
    labels[:,1,60:80]=5
    labels[:,2,100:104]=-100
    a,b=paired_tensor_views(x,12345)
    o1,o2=model(a),model(b)
    sup,raw,orig,parts=core.losses(o1,o2,labels,1.125,False)
    _,_,normalized,_=core.losses(o1,o2,labels,1.125,True)
    assert raw>0 and torch.allclose(orig,normalized*1200,atol=1e-4,rtol=1e-5)
    reconstructed=1.125*sum(parts[k]*c for k,c in core.CWEIGHTS.items())
    assert torch.allclose(reconstructed,sup,atol=1e-5,rtol=1e-5)
    measured=core.probe(model,sup,orig)
    assert all(v["supervisedGradientL2"]>=0 and v["weightedKLGradientL2"]>=0 for v in measured.values())
    if v9.base.state_sha256(model)!=baseline:
        raise RuntimeError("offline fixture changed model without optimizer")
    print("H1_20EPOCH_PAIRED_PILOT_OFFLINE_PASS",flush=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",required=True)
    p.add_argument("--manifest")
    p.add_argument("--data-dir")
    p.add_argument("--out")
    p.add_argument("--offline-test",action="store_true")
    args=p.parse_args()
    if args.offline_test:
        offline_test(args.source_root)
        return
    if not args.manifest or not args.data_dir or not args.out:
        raise RuntimeError("manifest, data-dir and out required")
    v9._setup_determinism()
    rows=v9.base.load_manifest(args.manifest,args.data_dir)
    if len(rows)!=256 or len({r["key"] for r in rows})!=256:
        raise RuntimeError("frozen development population mismatch")
    counts={p:sum(r["performer"]==p for r in rows) for p in ("P1","P2")}
    if counts!={"P1":136,"P2":120}: raise RuntimeError("performer population mismatch")
    provenance=safety.verify_population(
        rows,args.data_dir,
        HERE.parents[1]/"docs/astra/GUITARTECHS_PRIMARY_ALIGNMENT_CORRECTIONS_V1.json")
    # All prepared features and labels must satisfy canonical frozen semantics
    # before the first optimizer call; bounded mmap scan, no media decoding.
    for row in rows:
        prepared.verify_prepared_pair(row["_features"],row["_labels"],row["frames"])
    receipt={
        "schema":SCHEMA,"candidateId":CANDIDATE,"protocol":"20-epoch 2-arm x 2 performer folds only",
        "seed":core.SEED,"epochsPerArmPerFold":core.EPOCHS,"dataCounts":counts,
        "consistencyWeight":core.KL_WEIGHT,"normalizationFactor":1200,
        "reportedModelComparison":"fixed epoch20 outcomes only, no checkpoint selection",
        "folds":{},
        "sourceAndData":{
            **provenance,"manifestSha256":safety.sha256_file(args.manifest),
            "pythonVersion":platform.python_version(),
            "torchVersion":torch.__version__,
            "numpyVersion":core.np.__version__,
            "torchNumThreads":torch.get_num_threads(),
            "platform":platform.platform(),
        },
        "guards":{"noP3":True,"noProtectedSong":True,"noStageBHoldout":True,
                  "noThresholdTuning":True,"noSeedSelection":True,
                  "noPaidCompute":True,"noMainOrProductionMutation":True,
                  "noTrainedWeightsExport":True},
    }
    journal=safety.ScalarProgress(
        Path(args.out).with_suffix(".progress.json"),
        {"candidateId":CANDIDATE,"sourceAndData":receipt["sourceAndData"]})
    initials={}
    try:
        # Both original controls must pass before either normalized treatment runs.
        for arm in ("original_batchmean","per_position_normalized"):
            if arm=="per_position_normalized" and len(journal.payload["controlsVerified"])!=2:
                raise RuntimeError("BOTH_ORIGINAL_CONTROLS_NOT_VERIFIED")
            for fold,train_person,val_person,groups,val_count,perf_count,control_sha in core.FOLDS:
                train=[r for r in rows if r["performer"]==train_person]
                validation=[r for r in rows if r["performer"]==val_person]
                group_count=len({(r["performer"],r["category"],r["performanceKey"]) for r in train})
                if group_count!=groups or len(validation)!=val_count:
                    raise RuntimeError("fold disjoint population mismatch")
                receipt["folds"].setdefault(fold,{})
                journal.phase(fold+"|"+arm+"|train")
                model,row=core.train_arm(
                    train,fold,arm,args.source_root,control_sha,
                    before_step=journal.before_step,on_step=journal.confirmed_step)
                try:
                    if arm=="original_batchmean":
                        if row["epoch20Sha256"]!=control_sha:
                            raise RuntimeError("ORIGINAL_EPOCH20_SHA_REPRODUCTION_FAILED")
                        initials[fold]=row["initialStateSha256"]
                    elif row["initialStateSha256"]!=initials[fold]:
                        raise RuntimeError("objective arms initial weights differ")
                    journal.phase(fold+"|"+arm+"|evaluate")
                    results=core.evaluate(model,validation,val_count,perf_count)
                    if arm=="original_batchmean":
                        safety.require_zero_control(results["metrics"],results["totals"])
                    row["validation"]=results
                    receipt["folds"][fold][arm]=row
                    journal.arm_result(
                        fold,arm,row["epoch20Sha256"],float(results["metrics"]["f1"]),
                        int(results["totals"]["predictedEvents"]),
                        int(results["totals"]["activeRunsAfterPrune"]))
                    if arm=="original_batchmean":
                        journal.control_verified(fold)
                    print("H1_PILOT_FOLD_ARM_RESULT="+json.dumps({
                        "fold":fold,"arm":arm,"stateSha256":row["epoch20Sha256"],
                        "f1":results["metrics"]["f1"],
                        "predictedEvents":results["totals"]["predictedEvents"],
                        "admittedV4Runs":results["totals"]["activeRunsAfterPrune"],
                        "steps":row["steps"]},sort_keys=True),flush=True)
                finally:
                    del model
        receipt["optimizerSteps"]=sum(
            arm["steps"] for arms in receipt["folds"].values() for arm in arms.values())
        if receipt["optimizerSteps"]!=160 or journal.payload["optimizerStepsConfirmed"]!=160:
            raise RuntimeError("study step cap mismatch")
        receipt["interpretation"]="Bounded H1 paired pilot, not full V10 or scientific advancement PASS. Exact original controls verified first. Both development folds exposed; no independent holdout."
        Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True,allow_nan=False)+"\n")
        journal.finish()
        print("H1_20EPOCH_PAIRED_PILOT_COMPLETE",flush=True)
    except Exception as error:
        journal.fail(error)
        raise


if __name__=="__main__":main()
