#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

class ContractError(ValueError): pass

def validate(c):
    if c.get("schema")!="astra-v12-family-mixture-contract-v1": raise ContractError("schema")
    if c.get("status")!="frozen-preparation-empirical-execution-not-authorized": raise ContractError("status")
    if c["targetPositiveSlots"]["total"]!=16000: raise ContractError("target total")
    if sum(v for k,v in c["targetPositiveSlots"].items() if k!="total")!=16000: raise ContractError("target arithmetic")
    if c["expectedV9PositivePools"]["total"]!=1170: raise ContractError("pool total")
    if c["fixed"]["models"]!=2 or c["fixed"]["optimizerStepsPerModel"]!=500 or c["fixed"]["maxOptimizerStepsTotal"]!=1000: raise ContractError("training")
    if c["fixed"]["thresholdSearch"] or c["fixed"]["automaticScientificRetries"]!=0: raise ContractError("search/retry")
    if c["boundaries"]["empiricalExecutionAuthorized"]: raise ContractError("empirical auth")
    return {"valid":True,"models":2,"maxOptimizerStepsTotal":1000,"empiricalExecutionAuthorized":False,"v2b":False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); a=ap.parse_args()
    print(json.dumps(validate(json.loads(Path(a.contract).read_text())),sort_keys=True))
if __name__=="__main__": main()
