#!/usr/bin/env python3
"""Pure validator for the frozen V10 exposure-isolation contract."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

class ContractError(ValueError):
    pass

def validate(c):
    if c.get("schema")!="astra-v10-exposure-isolation-contract-v1":
        raise ContractError("wrong schema")
    if c.get("status")!="frozen-preparation-empirical-execution-not-authorized":
        raise ContractError("contract must be frozen and unauthorized")
    f=c["fixed"]; e=c["interventionExposure"]; r=c["reproductionGate"]; g=c["supportGate"]
    if f["models"]!=2 or f["optimizerStepsPerModel"]!=500 or f["maxOptimizerStepsTotal"]!=1000:
        raise ContractError("training ceiling mismatch")
    if f["positiveOnsetSlotsPerBatch"]*f["optimizerStepsPerModel"]!=f["positiveOnsetSlotsTotal"]:
        raise ContractError("positive slot arithmetic mismatch")
    if e["targetMultiLabelPositiveFrames"]+e["targetSingleLabelPositiveFrames"]!=f["positiveOnsetSlotsTotal"]:
        raise ContractError("positive frame partition mismatch")
    labels=e["targetSingleLabelPositiveFrames"]+3*e["targetMultiLabelPositiveFrames"]
    if labels!=e["targetSampledAttackedNoteLabels"] or labels!=19702:
        raise ContractError("target label arithmetic mismatch")
    if e["batchesWith4MultiFrames"]+e["batchesWith3MultiFrames"]!=500:
        raise ContractError("batch schedule count mismatch")
    multi=4*e["batchesWith4MultiFrames"]+3*e["batchesWith3MultiFrames"]
    if multi!=e["targetMultiLabelPositiveFrames"]:
        raise ContractError("multi-frame schedule mismatch")
    if r["controlSampledAttackedNoteLabelsExactly"]!=17676:
        raise ContractError("control exposure mismatch")
    if g["balancedSampledAttackedNoteLabelsExactly"]!=19702 or g["controlSampledAttackedNoteLabelsExactly"]!=17676:
        raise ContractError("gate exposure mismatch")
    if f["thresholdSearch"] or f["automaticScientificRetries"]!=0:
        raise ContractError("search/retry must remain disabled")
    if c["boundaries"]["empiricalExecutionAuthorized"]:
        raise ContractError("empirical execution must remain unauthorized")
    return {
        "valid":True,
        "positiveOnsetSlotsTotal":f["positiveOnsetSlotsTotal"],
        "targetAttackedNoteLabels":labels,
        "targetMultiLabelPositiveFrames":multi,
        "models":f["models"],
        "maxOptimizerStepsTotal":f["maxOptimizerStepsTotal"],
        "empiricalExecutionAuthorized":False,
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); a=ap.parse_args()
    print(json.dumps(validate(json.loads(Path(a.contract).read_text())),sort_keys=True))

if __name__=="__main__":
    main()
