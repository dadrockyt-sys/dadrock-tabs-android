#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

class ContractError(ValueError): pass

def validate(c):
    if c.get("schema")!="astra-v13-active-nononset-mixture-contract-v1": raise ContractError("schema")
    if c.get("status")!="frozen-preparation-empirical-execution-not-authorized": raise ContractError("status")
    t=c["targetActiveNonOnsetSlots"]
    if t["total"]!=16000: raise ContractError("target total")
    if sum(v for k,v in t.items() if k!="total")!=16000: raise ContractError("target arithmetic")
    p=c["expectedV9ActiveNonOnsetPools"]
    if p["total"]!=10444: raise ContractError("pool total")
    f=c["fixed"]
    if f["models"]!=2 or f["optimizerStepsPerModel"]!=500 or f["maxOptimizerStepsTotal"]!=1000: raise ContractError("training")
    if f["thresholdSearch"] or f["automaticScientificRetries"]!=0: raise ContractError("search/retry")
    i=c["identity"]
    for k in ("positiveOnsetSelectionsIdentical","negativeStructureInactiveSelectionsIdentical","otherInactiveSelectionsIdentical","samePerStepPermutation","attackedNoteLabelExposureIdentical"):
        if not i[k]: raise ContractError("identity")
    if c["boundaries"]["empiricalExecutionAuthorized"]: raise ContractError("empirical auth")
    if c["evaluation"]["v2b"] or c["evaluation"]["realAudio"]: raise ContractError("real evaluation")
    return {"valid":True,"models":2,"maxOptimizerStepsTotal":1000,"empiricalExecutionAuthorized":False,"v2b":False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); a=ap.parse_args()
    print(json.dumps(validate(json.loads(Path(a.contract).read_text())),sort_keys=True))
if __name__=="__main__": main()
