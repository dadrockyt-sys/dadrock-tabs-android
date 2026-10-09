#!/usr/bin/env python3
"""Offline-only full frozen TemporalTabCNNV9 original/H1-control parity probe.

REQUIRES an independently staged, exact pinned AMT-Tools 4-file source tree.
Synthetic inputs only. Never downloads data, launches workflows, exports weights,
reads a P1/P2 manifest, or consumes the blocked training-launch receipt.
Exit nonzero on ANY parity/identity failure; do not treat unrun as passing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np
import torch

from guitartechs_training_v9 import train_v9_resumable as v9
from guitartechs_training_v7.objective_decoder import v7_sequence_loss
from guitartechs_training_v9.paired_view import paired_tensor_views, symmetric_kl_consistency
from guitartechs_training_v10 import h1_pilot_core_v1 as h1

FROZEN_UPSTREAM={
    "models/common.py":"84beb4cf251b9cb9274d10cf203318314181af31",
    "models/tabcnn.py":"e09856db2fffd77642e005ab509846acc894b886",
    "tools/instrument.py":"eddc48a8b95de057035cd11ea2d1951e754ef349",
    "tools/constants.py":"79666ea0c5b0214ca664da454069b8d286cc5c18",
}
STEPS=2
MICROBATCHES=2
T=200


def git_blob_id(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\\0"+raw).hexdigest()


def verify_upstream(source_root):
    root=Path(source_root).resolve(strict=True)
    for name,want in FROZEN_UPSTREAM.items():
        src=root/"amt_tools"/name
        if src.is_symlink() or not src.is_file() or src.resolve()!=src:
            raise RuntimeError("PINNED_UPSTREAM_FILE_MISSING:"+name)
        if git_blob_id(src.read_bytes())!=want:
            raise RuntimeError("PINNED_UPSTREAM_BLOB_MISMATCH:"+name)
    return root


def make_samples():
    g=torch.Generator(device="cpu").manual_seed(826146)
    examples=[]
    for i in range(STEPS*MICROBATCHES):
        x=torch.rand((1,T,1,192,9),generator=g)
        labels=torch.full((1,6,T),-1,dtype=torch.int64)
        labels[:,0,20+i:23+i]=3
        labels[:,1,80+i:84+i]=5
        labels[:,3,150:154]=-100
        item={"captureKey":"SYNTHETIC-NO-MEDIA-"+str(i),"startFrame":i,"endFrame":i+T}
        examples.append((x,labels,item))
    return examples


def optimizer_snapshot(optimizer):
    obj=optimizer.state_dict()
    return {
        "groups":obj["param_groups"],
        "state":{key:{field:value.detach().clone() if isinstance(value,torch.Tensor) else value
                       for field,value in entry.items()}
                 for key,entry in obj["state"].items()},
    }


def compare_optimizer(one,two):
    if one["groups"]!=two["groups"] or one["state"].keys()!=two["state"].keys():
        raise RuntimeError("V9_H1_OPTIMIZER_STRUCTURE_DRIFT")
    for index,entry in one["state"].items():
        if entry.keys()!=two["state"][index].keys():
            raise RuntimeError("V9_H1_OPTIMIZER_FIELDS_DRIFT")
        for field,value in entry.items():
            new=two["state"][index][field]
            if isinstance(value,torch.Tensor):
                if not isinstance(new,torch.Tensor) or not torch.equal(value,new):
                    raise RuntimeError("V9_H1_OPTIMIZER_TENSOR_DRIFT:"+str(field))
            elif value!=new:
                raise RuntimeError("V9_H1_OPTIMIZER_VALUE_DRIFT:"+str(field))


def run_one(source_root, instrumented, examples, wall_limit):
    v9._setup_determinism()
    model,optimizer=v9._new_model_and_optimizer(str(source_root))
    initial=v9.base.state_sha256(model)
    trace=[]
    start=time.monotonic()
    for step in range(STEPS):
        if time.monotonic()-start>wall_limit:
            raise RuntimeError("SYNTHETIC_FULL_MODEL_TIME_LIMIT")
        optimizer.zero_grad(set_to_none=True)
        model.train()
        for micro in range(MICROBATCHES):
            x,y,item=examples[step*MICROBATCHES+micro]
            salt=json.dumps({"epoch":step,"item":item},sort_keys=True).encode("utf-8")
            seed=int(hashlib.sha256(salt).hexdigest()[:16],16)
            aa,bb=paired_tensor_views(x,seed)
            oa,ob=model(aa),model(bb)
            if instrumented:
                sup,_,weighted,_=h1.losses(oa,ob,y,1.0,False)
                if step==0 and micro==0:
                    before=torch.get_rng_state().clone()
                    gradients=h1.probe(model,sup,weighted)
                    if not torch.equal(before,torch.get_rng_state()):
                        raise RuntimeError("H1_PROBE_MUTATED_TORCH_RNG")
                    if not all(group in gradients for group in h1.GROUPS):
                        raise RuntimeError("H1_PROBE_INCOMPLETE")
                loss=sup+weighted
            else:
                la,_=v7_sequence_loss(oa,y,content_weight=1.0)
                lb,_=v7_sequence_loss(ob,y,content_weight=1.0)
                logits_a=oa["tablature"].reshape(1,T,6,21)
                logits_b=ob["tablature"].reshape(1,T,6,21)
                consistency=symmetric_kl_consistency(logits_a,logits_b)
                loss=0.5*(la+lb)+0.10*consistency
            if not torch.isfinite(loss):
                raise RuntimeError("SYNTHETIC_NONFINITE_LOSS")
            (loss/MICROBATCHES).backward()
        optimizer.step()
        trace.append({
            "stateSha256":v9.base.state_sha256(model),
            "optimizer":optimizer_snapshot(optimizer),
            "torchRng":torch.get_rng_state().clone(),
            "pythonRng":random.getstate(),
            "numpyRng":np.random.get_state(),
        })
    return initial,trace,time.monotonic()-start


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root",required=True,help="Already staged, git-blob-verified upstream root; no auto-download.")
    p.add_argument("--max-wall-seconds",type=int,default=180)
    args=p.parse_args()
    if not 0<args.max_wall_seconds<=600:
        raise RuntimeError("UNBOUNDED_SYNTHETIC_RUNTIME_REQUEST")
    root=verify_upstream(args.source_root)
    samples=make_samples()
    original=run_one(root,False,samples,args.max_wall_seconds)
    instrumented=run_one(root,True,samples,args.max_wall_seconds)
    if original[0]!=instrumented[0]:
        raise RuntimeError("V9_H1_INITIAL_SHA_DRIFT")
    for step,(a,b) in enumerate(zip(original[1],instrumented[1]),1):
        if a["stateSha256"]!=b["stateSha256"]:
            raise RuntimeError("V9_H1_FULL_MODEL_STATE_SHA_DRIFT_STEP_"+str(step))
        compare_optimizer(a["optimizer"],b["optimizer"])
        if not torch.equal(a["torchRng"],b["torchRng"]):
            raise RuntimeError("V9_H1_FULL_MODEL_TORCH_RNG_DRIFT")
        if a["pythonRng"]!=b["pythonRng"]:
            raise RuntimeError("V9_H1_FULL_MODEL_PYTHON_RNG_DRIFT")
        ax,bx=a["numpyRng"],b["numpyRng"]
        if ax[0]!=bx[0] or not np.array_equal(ax[1],bx[1]) or ax[2:]!=bx[2:]:
            raise RuntimeError("V9_H1_FULL_MODEL_NUMPY_RNG_DRIFT")
    print(json.dumps({
        "schema":"astra-h1-full-v9-synthetic-parity-v1",
        "status":"PASS_SYNTHETIC_ONLY",
        "mode":"NO_MEDIA_NO_CHECKPOINT_NO_LAUNCH",
        "stepsPerPath":STEPS,
        "microbatchesPerStep":MICROBATCHES,
        "originalAndInstrumentedStateSha256":[x["stateSha256"] for x in original[1]],
        "initialStateSha256":original[0],
        "pythonTorchNumpyParity":True,
        "optimizerParity":True,
        "torchVersion":torch.__version__,
        "originalWallSeconds":original[2],
        "instrumentedWallSeconds":instrumented[2],
        "historicalEpoch20RealDataReproduced":False,
        "launchPermission":False,
    },sort_keys=True))


if __name__=="__main__":
    main()
