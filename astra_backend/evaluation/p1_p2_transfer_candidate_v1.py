#!/usr/bin/env python3
"""Train the single frozen synthetic candidate for a later authorized P1/P2 transfer check."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, torch
from evaluation.p1_p2_transfer_evaluation_v1 import TransferCandidate
from synthetic.s11_pilot_v1 import paired_batches, fit, RUN_SEEDS

SCHEMA="astra-p1-p2-transfer-candidate-v1"
FROZEN_RUN_SEED=20260927

def run(dataset,out):
    if FROZEN_RUN_SEED!=RUN_SEEDS[0]: raise RuntimeError("candidate seed must remain first frozen S11 seed")
    d=np.load(dataset,allow_pickle=False)
    batches,_=paired_batches(d["state"],d["onset"],d["split"],d["has_negative_structure"],FROZEN_RUN_SEED)
    from synthetic.s11_pilot_v1 import initialize_model
    model=initialize_model(FROZEN_RUN_SEED,960)
    fit_receipt=fit(model,d["features"].astype(np.float32,copy=False),d["state"],d["onset"],batches,10**18)
    if fit_receipt["optimizerSteps"]!=500: raise RuntimeError("candidate did not finish frozen 500 steps")
    torch.save({"schema":SCHEMA,"runSeed":FROZEN_RUN_SEED,"optimizerSteps":500,"stateDict":model.state_dict()},out)
    print("TRANSFER_CANDIDATE="+json.dumps({"runSeed":FROZEN_RUN_SEED,"optimizerSteps":500},sort_keys=True))
def main():
    p=argparse.ArgumentParser(); p.add_argument("--dataset",required=True); p.add_argument("--out",required=True); a=p.parse_args(); run(a.dataset,a.out)
if __name__=="__main__": main()
