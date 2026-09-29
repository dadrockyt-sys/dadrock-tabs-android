#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from synthetic.s0_pilot_v1 import ROOT_SEED,FAMILIES,BASES_PER_FAMILY,VARIANTS_PER_BASE,build_template,_seed

TARGET={"rate":1.4905949321319818,"ioi50":0.2560000000000002,"ioi90":0.882358,"repeat250":0.47019867549668876}

def q(a,p):
    if not a:return None
    x=np.asarray(sorted(a),dtype=np.float64)
    return float(np.quantile(x,p))

def historical_attacks(t):
    return sorted(float(s["start"]) for s in t["segments"] if s["attack"])

def motif_relative(family,base):
    t=build_template(family,base)
    at=historical_attacks(t)
    if family=="repeated" and at:
        return [at[0]+0.18*i for i in range(len(at))]
    return at

def make_positive_clip(family,base,variant,arm):
    if arm=="L0":
        t=build_template(family,base)
        return historical_attacks(t),2.0,0
    motifs=2 if arm=="L1" else 3
    seconds=4.0 if arm=="L1" else 6.0
    starts=[]; cursor=0.20; fallbacks=0
    for m in range(motifs):
        b=(base+m)%BASES_PER_FAMILY
        rel=motif_relative(family,b)
        if not rel: continue
        # normalize motif start to zero
        r0=rel[0]
        rel=[x-r0 for x in rel]
        if m==0:
            motif_start=0.20
        else:
            rng=np.random.RandomState(_seed(ROOT_SEED,"v8-gap",arm,family,base,variant,m))
            gap=float(rng.uniform(.70,1.10))
            motif_start=starts[-1]+gap
        cand=[motif_start+x for x in rel]
        if cand and cand[-1] > seconds-0.12:
            # deterministic fallback to the latest valid placement preserving motif shape
            shift=(seconds-0.12)-cand[-1]
            cand=[x+shift for x in cand]
            fallbacks+=1
        if cand and cand[0] < 0:
            fallbacks+=1
            cand=[x-cand[0]+0.02 for x in cand]
        starts.extend(cand)
    starts=sorted(starts)
    return starts,seconds,fallbacks

def summarize(arm):
    rows=[]; all_ioi=[]; simultaneous=0; repeat=0; longn=0; pairn=0; fallbacks=0
    events=0; seconds=0.0; invalid=0
    for family in FAMILIES:
      for base in range(BASES_PER_FAMILY):
        t=build_template(family,base)
        if t["negativeOnly"]: continue
        for variant in range(VARIANTS_PER_BASE):
          at,dur,fb=make_positive_clip(family,base,variant,arm)
          fallbacks+=fb
          if any(x<0 or x>dur for x in at): invalid+=1
          io=[at[i]-at[i-1] for i in range(1,len(at))]
          all_ioi.extend(io); pairn+=len(io)
          simultaneous+=sum(1 for x in io if abs(x)<1e-9)
          repeat+=sum(1 for x in io if x<=.25)
          longn+=sum(1 for x in io if x>=.70)
          rows.append(len(at)/dur if dur else 0)
          events+=len(at); seconds+=dur
    s={
      "positiveClips":len(rows),"events":events,"positiveSeconds":seconds,
      "aggregateOnsetsPerSecond":events/seconds,
      "clipRateP10":q(rows,.1),"clipRateP50":q(rows,.5),"clipRateP90":q(rows,.9),
      "interOnsetIntervalP10":q(all_ioi,.1),"interOnsetIntervalP50":q(all_ioi,.5),"interOnsetIntervalP90":q(all_ioi,.9),
      "repeatedAttackFractionWithin250ms":repeat/pairn if pairn else 0,
      "fractionIoiAtLeast700ms":longn/pairn if pairn else 0,
      "simultaneousEventFraction":simultaneous/pairn if pairn else 0,
      "clipBoundaryFallbackCount":fallbacks,"invalidClipCount":invalid,
    }
    s["timingDistance"]=(
      abs(s["repeatedAttackFractionWithin250ms"]-TARGET["repeat250"]) +
      abs(s["interOnsetIntervalP50"]-TARGET["ioi50"])/TARGET["ioi50"] +
      abs(s["interOnsetIntervalP90"]-TARGET["ioi90"])/TARGET["ioi90"] +
      .5*abs(s["aggregateOnsetsPerSecond"]-TARGET["rate"])/TARGET["rate"]
    )
    return s

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",required=True)
    a=ap.parse_args()
    arms={x:summarize(x) for x in ("L0","L1","L2")}
    b=arms["L0"]
    for x in ("L1","L2"):
        z=arms[x]
        z["advancementChecks"]={
          "timingDistanceRelativeImprovementAtLeast0_35":(b["timingDistance"]-z["timingDistance"])/b["timingDistance"]>=.35,
          "repeatErrorImprovementAtLeast0_10":abs(b["repeatedAttackFractionWithin250ms"]-TARGET["repeat250"])-abs(z["repeatedAttackFractionWithin250ms"]-TARGET["repeat250"])>=.10,
          "ioiP90ErrorImprovementAtLeast0_25":abs(b["interOnsetIntervalP90"]-TARGET["ioi90"])-abs(z["interOnsetIntervalP90"]-TARGET["ioi90"])>=.25,
          "aggregateRateWithin15Percent":abs(z["aggregateOnsetsPerSecond"]-TARGET["rate"])/TARGET["rate"]<=.15,
          "fallbackRateAtMost0_02":z["clipBoundaryFallbackCount"]/z["positiveClips"]<=.02,
          "noInvalidClips":z["invalidClipCount"]==0,
        }
        z["qualifies"]=all(z["advancementChecks"].values())
    qarms=[x for x in ("L1","L2") if arms[x]["qualifies"]]
    selected=min(qarms,key=lambda x:arms[x]["timingDistance"]) if qarms else None
    out={"schema":"astra-v8a-long-duration-timing-screen-v1","target":TARGET,"arms":arms,"qualifyingArms":qarms,"selectedArm":selected,
         "execution":{"modelInferenceCount":0,"optimizerSteps":0,"waveformRenderCount":0,"parameterSearch":False}}
    Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("V8A="+json.dumps(out,sort_keys=True))
if __name__=="__main__": main()
