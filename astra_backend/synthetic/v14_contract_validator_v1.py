#!/usr/bin/env python3
"""Pure model-free validator for frozen V14 matched-context bridge."""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
import numpy as np

ROOT=20260929
FAMILIES=("isolated","scales","chords","repeated","legato","palmmute","mixed")
COUNTS={"isolated":1,"scales":4,"chords":2,"repeated":5,"legato":1,"palmmute":6,"mixed":1}
FIRST={
 "isolated":(.30,.34),"scales":(.20,.24),"chords":(.30,.34),
 "repeated":(.26,.30),"legato":(.26,.30),"palmmute":(.24,.26),"mixed":(.34,.38)
}
SUPPORT={"S":(.10,.13),"M":(.251,.260),"L":(.85,.95)}
TYPE_QUOTAS={
 "isolated":[("single",42)],
 "scales":[("L",16),("S2M1",16),("S1M2",10)],
 "chords":[("L",5),("S",19),("M",18)],
 "repeated":[("L",22),("S2M2",14),("S1M3",6)],
 "legato":[("single",42)],
 "palmmute":[("L",26),("S1M4",13),("S2M3",3)],
 "mixed":[("single",21)],
}
TARGET={"density":1.4905949321256224,"p50":.256,"p90":.882358,
        "repeat":0.47019867549668876,"long":0.12582781456953643}

def _h(*parts):
    return hashlib.sha256("|".join(str(x) for x in parts).encode()).digest()

def _u(*parts):
    return int.from_bytes(_h(*parts)[:8],"big")/2**64

def _clips(family):
    out=[]
    for base in range(14):
        if family=="mixed" and base%2==0:
            continue
        for variant in range(3):
            out.append((base,variant))
    return out

def _classes(family,kind):
    if kind=="single": return []
    maps={
      "scales":{"L":["S","M","L"],"S2M1":["S","S","M"],"S1M2":["S","M","M"]},
      "chords":{"L":["L"],"S":["S"],"M":["M"]},
      "repeated":{"L":["S","S","M","L"],"S2M2":["S","S","M","M"],"S1M3":["S","M","M","M"]},
      "palmmute":{"L":["S","S","S","M","L"],"S1M4":["S","M","M","M","M"],"S2M3":["S","S","M","M","M"]},
    }
    return list(maps[family][kind])

def linear_q(values,p):
    a=sorted(float(x) for x in values)
    h=(len(a)-1)*p
    lo=math.floor(h); hi=math.ceil(h)
    return a[lo]+(h-lo)*(a[hi]-a[lo])

def build_schedule():
    rows=[]; gaps=[]
    for family in FAMILIES:
        ids=_clips(family)
        ordered=sorted(ids,key=lambda bv:_h(ROOT,"type",family,bv[0],bv[1]))
        kinds={}; pos=0
        for kind,n in TYPE_QUOTAS[family]:
            for bv in ordered[pos:pos+n]:
                kinds[bv]=kind
            pos+=n
        if pos!=len(ids): raise RuntimeError("quota mismatch")
        for base,variant in ids:
            kind=kinds[(base,variant)]
            classes=_classes(family,kind)
            ordered_classes=[x[1] for x in sorted(
                [(_h(ROOT,"order",family,base,variant,j),c) for j,c in enumerate(classes)],
                key=lambda x:x[0]
            )]
            flo,fhi=FIRST[family]
            t=flo+_u(ROOT,"first",family,base,variant)*(fhi-flo)
            times=[t]; local=[]
            for j,c in enumerate(ordered_classes):
                lo,hi=SUPPORT[c]
                g=lo+_u(ROOT,"gap",family,base,variant,j,c)*(hi-lo)
                t+=g; times.append(t); gaps.append((c,g)); local.append((c,g))
            if len(times)!=COUNTS[family]: raise RuntimeError("attack count mismatch")
            rows.append({"family":family,"base":base,"variant":variant,"kind":kind,"times":times,"gaps":local})
    return rows,gaps

def timing_distance(summary):
    return (
      abs(summary["repeat250"]-TARGET["repeat"])
      +abs(summary["ioiP50"]-TARGET["p50"])/TARGET["p50"]
      +abs(summary["ioiP90"]-TARGET["p90"])/TARGET["p90"]
      +.5*abs(summary["density"]-TARGET["density"])/TARGET["density"]
      +.5*abs(summary["longGap700"]-TARGET["long"])/TARGET["long"]
    )

def summarize():
    rows,gaps=build_schedule()
    vals=[g for _,g in gaps]
    counts={k:sum(c==k for c,_ in gaps) for k in ("S","M","L")}
    attack_count=sum(len(r["times"]) for r in rows)
    out={
      "positiveClipCount":len(rows),"attackGroupCount":attack_count,"gapCount":len(vals),
      "gapClassCounts":counts,"density":attack_count/(273*2.0),
      "ioiP10":linear_q(vals,.1),"ioiP50":linear_q(vals,.5),"ioiP90":linear_q(vals,.9),
      "repeat250":sum(g<=.25 for g in vals)/len(vals),
      "longGap700":sum(g>=.7 for g in vals)/len(vals),
      "maximumLastAttackSeconds":max(r["times"][-1] for r in rows),
      "minimumPostLastAttackMarginSeconds":min(2.0-r["times"][-1] for r in rows),
    }
    out["timingDistanceV1"]=timing_distance(out)
    return out

def validate(contract):
    if contract.get("schema")!="astra-v14-matched-context-bridge-contract-v1":
        raise ValueError("schema mismatch")
    if contract["status"]!="frozen-prospective-contract-empirical-execution-not-authorized":
        raise ValueError("status mismatch")
    if contract["authorization"]["empiricalRenderingTrainingAuthorized"] is not False:
        raise ValueError("empirical authorization must be false")
    if contract["bridge"]["rootSeed"]!=ROOT or contract["bridge"]["clipSeconds"]!=2.0:
        raise ValueError("identity mismatch")
    if contract["bridge"]["attackGroupsPerPositiveClip"]!=COUNTS:
        raise ValueError("attack counts mismatch")
    if contract["bridge"]["gapClassTotals"]!={"S":252,"M":225,"L":69,"total":546}:
        raise ValueError("gap totals mismatch")
    s=summarize()
    exp=contract["modelFreeExpected"]["deterministicMeasuredExpected"]
    exact={
      "positiveClips":s["positiveClipCount"]==273,
      "attackGroups":s["attackGroupCount"]==819,
      "gaps":s["gapCount"]==546,
      "classes":s["gapClassCounts"]=={"S":252,"M":225,"L":69},
      "density":abs(s["density"]-1.5)<=1e-15,
      "repeat":abs(s["repeat250"]-0.46153846153846156)<=1e-15,
      "long":abs(s["longGap700"]-0.12637362637362637)<=1e-15,
      "p10":abs(s["ioiP10"]-exp["ioiP10Seconds"])<=1e-15,
      "p50":abs(s["ioiP50"]-exp["ioiP50Seconds"])<=1e-15,
      "p90":abs(s["ioiP90"]-exp["ioiP90Seconds"])<=1e-15,
      "last":abs(s["maximumLastAttackSeconds"]-exp["maximumLastAttackSeconds"])<=1e-15,
      "margin":abs(s["minimumPostLastAttackMarginSeconds"]-exp["minimumPostLastAttackMarginSeconds"])<=1e-15,
      "distance":abs(s["timingDistanceV1"]-exp["timingDistanceV1"])<=1e-15,
      "requiredMargin":s["minimumPostLastAttackMarginSeconds"]>=contract["bridge"]["finalRequiredMarginSeconds"],
      "f1Gate":abs(contract["empiricalGate"]["commonF1AtLeast"]-0.586490016794178)<=1e-15,
      "precisionGate":abs(contract["empiricalGate"]["commonPrecisionAtLeast"]-0.5756752789195302)<=1e-15,
      "noSearch":contract["empiricalGate"]["noThresholdSearch"] is True and contract["empiricalGate"]["noAutomaticScientificRetry"] is True,
      "noReal":contract["executionCeilings"]["v2b"] is False and contract["executionCeilings"]["realAudio"] is False,
    }
    if not all(exact.values()):
        raise ValueError("V14 preflight validation failed: "+json.dumps(exact,sort_keys=True))
    return {"schema":"astra-v14-model-free-preflight-v1","passed":True,"checks":exact,"summary":s,
            "execution":{"waveformRenders":0,"datasetsGenerated":0,"modelsTrained":0,"optimizerSteps":0,
                         "modelInference":0,"v2bInference":0,"realAudioAccess":0}}

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); ap.add_argument("--out")
    a=ap.parse_args(); c=json.loads(Path(a.contract).read_text()); r=validate(c)
    if a.out: Path(a.out).write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    print(json.dumps(r,sort_keys=True))

if __name__=="__main__": main()
