#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math
from pathlib import Path

class ContractError(ValueError): pass

def validate(c):
    if c.get("schema")!="astra-v11-state-semantics-contract-v1":
        raise ContractError("wrong schema")
    if c.get("status")!="frozen-preparation-empirical-execution-not-authorized":
        raise ContractError("contract must remain frozen and unauthorized")
    d=c["durationsSeconds"]; i=c["identity"]; t=c["training"]; b=c["baselineReproduction"]; g=c["supportGate"]
    expected={"isolated":1.03,"scales":0.27,"chords":0.48,"repeated":0.31,"legatoAttack":0.50,"legatoContinuation":0.74,"palmmute":0.16,"mixedPositive":0.86}
    if d!=expected: raise ContractError("duration constants changed")
    if (i["clips"],i["positiveClips"],i["negativeOnlyClips"])!=(294,273,21): raise ContractError("clip identity mismatch")
    if i["attackGroupsEachArm"]!=1638 or i["attackedNoteLabelsEachArm"]!=1806: raise ContractError("attack identity mismatch")
    if not all(i[k] for k in ("exactAttackedStringFretOnsetIdentity","requireAtLeastOneLegatoContinuation","zeroSameStringOverlap","negativeOnlyUnchanged")):
        raise ContractError("identity guard changed")
    if t["models"]!=2 or t["optimizerStepsPerModel"]!=500 or t["maxOptimizerStepsTotal"]!=1000:
        raise ContractError("training ceiling mismatch")
    if t["thresholdSearch"] or t["automaticScientificRetries"]!=0:
        raise ContractError("search/retry must remain disabled")
    if not math.isclose(b["tolerance"],1e-12,rel_tol=0,abs_tol=0): raise ContractError("baseline tolerance changed")
    if g["commonPrecisionGainAtLeast"]!=0.15 or g["commonF1GainAtLeast"]!=0.10:
        raise ContractError("primary material-recovery gate changed")
    if c["evaluation"]["v2b"] or c["evaluation"]["realAudio"]:
        raise ContractError("real evaluation out of scope")
    if c["boundaries"]["empiricalExecutionAuthorized"]:
        raise ContractError("empirical execution must remain unauthorized")
    return {"valid":True,"models":2,"maxOptimizerStepsTotal":1000,"empiricalExecutionAuthorized":False,"v2b":False}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); a=ap.parse_args()
    print(json.dumps(validate(json.loads(Path(a.contract).read_text())),sort_keys=True))

if __name__=="__main__": main()
