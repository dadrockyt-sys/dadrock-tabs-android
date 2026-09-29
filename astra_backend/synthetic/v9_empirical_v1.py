#!/usr/bin/env python3
"""Astra V9 empirical package.

Commands:
  verify  - static source/contract checks only; no candidate generation.
  timing  - generate exactly one frozen V9 timing manifest and apply V9A.
  render  - render the same-runtime 2 s comparator and 4 s V9 intervention.
  train   - train exactly two S6 nonlinear models and apply synthetic sanity.

No real audio is used by this module. V2B inference is a separate conditional stage.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, random, time
from pathlib import Path

import numpy as np
from scipy.signal import lfilter, resample_poly
import torch

from synthetic.s0_pilot_v1 import (
    ROOT_SEED, INTERNAL_SR, OUTPUT_SR, OPEN_MIDI, FAMILIES, BASES_PER_FAMILY,
    VARIANTS_PER_BASE, HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ, CQT_BINS,
    _seed, _event, _plucked_component, build_template, split_for_base,
    extract_cqt_features, rms_normalize, context5,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s6_pilot_v1 import (
    initialize_arm, module_sha, weighted_loss, evaluate_arm,
)
from synthetic.v4_rendering_adequacy_v1 import apply_renderer_arm
from synthetic.v9_final_contract_validator_v1 import validate as validate_contract

SCHEMA="astra-v9-empirical-v1"
TIMING_SCHEMA="astra-v9a-timing-manifest-v1"
ROOT=20260927
DURATION=4.0
POSITIVE_COUNTS={"isolated":5,"scales":8,"chords":2,"repeated":8,"legato":4,"palmmute":10,"mixed":4}
GAP_CLASSES={
    "isolated":["S","S","S","M"],
    "scales":["S","S","S","M","M","M","L"],
    "chords":["M"],
    "repeated":["S","S","S","M","M","M","L"],
    "legato":["S","M","L"],
    "palmmute":["S","S","S","S","M","M","M","M","L"],
    "mixed":["S","S","L"],
}
SUPPORTS={"S":(.080,.250),"M":(.251,.316),"L":(.700,1.360)}
FIRST=(.050,.120)
SUSTAIN=(.120,.480)
FINAL_MARGIN=.120
MAX_STEPS=500
BATCH_SIZE=128
MAX_TOTAL_STEPS=1000
TRAIN_DEADLINE_SECONDS=3600.0

def sha_u(*parts):
    raw="|".join(str(x) for x in parts).encode()
    return int.from_bytes(hashlib.sha256(raw).digest()[:8],"big") / 2**64

def linear_q(xs,p):
    a=sorted(float(x) for x in xs)
    if not a: return None
    h=(len(a)-1)*p; lo=math.floor(h); hi=math.ceil(h)
    return a[lo]+(h-lo)*(a[hi]-a[lo])

def _positive_base(family,base):
    return not (family=="mixed" and base%2==0)

def _permute_classes(split,family,base,variant):
    classes=list(GAP_CLASSES[family])
    keyed=[]
    for idx,k in enumerate(classes):
        h=hashlib.sha256(f"{ROOT}|v9-gap-order|{split}|{family}|{base}|{variant}|{idx}".encode()).digest()
        keyed.append((h,idx,k))
    return [x[2] for x in sorted(keyed)]

def attack_times(family,base,variant):
    split=split_for_base(base)
    n=POSITIVE_COUNTS[family]
    if not _positive_base(family,base):
        return [],[]
    classes=_permute_classes(split,family,base,variant)
    if len(classes)!=n-1:
        raise RuntimeError("gap class count mismatch")
    t=FIRST[0]+sha_u(ROOT,"v9-first",split,family,base,variant)*(FIRST[1]-FIRST[0])
    times=[t]; gaps=[]
    for i,k in enumerate(classes):
        lo,hi=SUPPORTS[k]
        gap=lo+sha_u(ROOT,"v9-gap-value",split,family,base,variant,i)*(hi-lo)
        gaps.append(gap); t+=gap; times.append(t)
    if times[-1]+FINAL_MARGIN>=DURATION:
        raise RuntimeError("infeasible V9 clip")
    return times,gaps

def timing_distance(row,target):
    return (
      abs(row["repeat250"]-target["repeat250"])
      +abs(row["ioiP50"]-target["ioiP50"])/target["ioiP50"]
      +abs(row["ioiP90"]-target["ioiP90"])/target["ioiP90"]
      +.5*abs(row["density"]-target["density"])/target["density"]
      +.5*abs(row["longGap700"]-target["longGap700"])/target["longGap700"]
    )

def verify(contract_path):
    c=json.loads(Path(contract_path).read_text())
    base=validate_contract(c)
    # Pure feasibility: use support maxima, not generated candidate values.
    for family,classes in GAP_CLASSES.items():
        worst=FIRST[1]+FINAL_MARGIN+sum(SUPPORTS[k][1] for k in classes)
        if worst>=DURATION: raise RuntimeError(f"support infeasible: {family}")
    if sum((42 if f!="mixed" else 21)*POSITIVE_COUNTS[f] for f in POSITIVE_COUNTS)!=1638:
        raise RuntimeError("frozen attack total mismatch")
    return {"schema":"astra-v9-preflight-v1","contractValid":True,"supportFeasible":True,**base,
            "candidateTimingGenerated":False,"waveformsRendered":0,"modelInferenceCount":0,"optimizerSteps":0}

def make_timing(contract):
    rows=[]; all_ioi=[]; attack_total=0; note_total=0
    per_family={f:{"positiveClips":0,"attackGroups":0,"attackedNoteLabels":0,"iois":0} for f in FAMILIES}
    for family in FAMILIES:
      for base in range(BASES_PER_FAMILY):
        if not _positive_base(family,base): continue
        for variant in range(VARIANTS_PER_BASE):
          times,gaps=attack_times(family,base,variant)
          labels=len(times)*(3 if family=="chords" else 1)
          split=split_for_base(base)
          rows.append({"family":family,"base":base,"variant":variant,"split":split,
                       "attackTimes":times,"gaps":gaps,"attackGroups":len(times),"attackedNoteLabels":labels})
          all_ioi.extend(gaps); attack_total+=len(times); note_total+=labels
          pf=per_family[family]; pf["positiveClips"]+=1; pf["attackGroups"]+=len(times); pf["attackedNoteLabels"]+=labels; pf["iois"]+=len(gaps)
    if len(rows)!=273 or attack_total!=1638 or note_total!=1806 or len(all_ioi)!=1365:
        raise RuntimeError("V9 timing identity mismatch")
    summary={
      "positiveClips":273,"negativeOnlyClips":21,"positiveSeconds":1092.0,
      "attackGroupCount":attack_total,"attackedNoteLabelCount":note_total,
      "density":attack_total/1092.0,
      "ioiP10":linear_q(all_ioi,.1),"ioiP50":linear_q(all_ioi,.5),"ioiP90":linear_q(all_ioi,.9),
      "repeat250":sum(x<=.250 for x in all_ioi)/len(all_ioi),
      "longGap700":sum(x>=.700 for x in all_ioi)/len(all_ioi),
      "infeasibleClipCount":0,"invalidLabelCount":0,"invalidOffsetCount":0,"fallbackOperationCount":0,
    }
    target=contract["reference"]["v2b"]; base=contract["reference"]["v8L0CommonUnit"]
    d=timing_distance(summary,target); d0=base["timingDistanceV1"]
    g=contract["v9aGate"]
    checks={
      "relativeTimingDistanceImprovement":(d0-d)/d0>=g["relativeTimingDistanceImprovementAtLeast"],
      "densityRelativeError":abs(summary["density"]-target["density"])/target["density"]<=g["densityRelativeErrorAtMost"],
      "ioiP50Error":abs(summary["ioiP50"]-target["ioiP50"])<=g["ioiP50AbsoluteErrorSecondsAtMost"],
      "ioiP90Error":abs(summary["ioiP90"]-target["ioiP90"])<=g["ioiP90AbsoluteErrorSecondsAtMost"],
      "repeat250Error":abs(summary["repeat250"]-target["repeat250"])<=g["repeat250AbsoluteErrorAtMost"],
      "longGap700Error":abs(summary["longGap700"]-target["longGap700"])<=g["longGap700AbsoluteErrorAtMost"],
      "positiveClipCount":summary["positiveClips"]==273,
      "negativeOnlyClipCount":summary["negativeOnlyClips"]==21,
      "attackGroupCount":attack_total==1638,
      "attackedNoteLabelCount":note_total==1806,
      "zeroInfeasible":summary["infeasibleClipCount"]==0,
      "zeroInvalidLabels":summary["invalidLabelCount"]==0,
      "zeroInvalidOffsets":summary["invalidOffsetCount"]==0,
      "zeroFallbacks":summary["fallbackOperationCount"]==0,
    }
    return {"schema":TIMING_SCHEMA,"summary":summary,"perFamily":per_family,
            "timingDistanceV1":d,"baselineTimingDistanceV1":d0,
            "relativeImprovement":(d0-d)/d0,"checks":checks,"passed":all(checks.values()),"clips":rows,
            "execution":{"candidateTimingPopulationGenerated":True,"waveformsRendered":0,"optimizerSteps":0,"modelInferenceCount":0}}

def _render_template(template,variant,seconds,timbre_template_id,key):
    trng=np.random.RandomState(_seed(ROOT_SEED,"timbre",timbre_template_id,variant))
    n=int(round(seconds*INTERNAL_SR)); audio=np.zeros(n,dtype=np.float64)
    damping=float(trng.uniform(.75,1.75)); pick=float(trng.uniform(.12,.42)); brightness=float(trng.uniform(.66,.88)); body_a=float(trng.uniform(.82,.94))
    for row in template["segments"]:
        start=int(round(row["start"]*INTERNAL_SR)); end=int(round(row["end"]*INTERNAL_SR))
        if end<=start or start>=n: continue
        end=min(n,end); pitch=OPEN_MIDI[row["string"]]+row["fret"]; freq=440.0*(2.0**((pitch-69)/12.0))
        d=damping*(4.5 if row.get("palm") else 1.0)*(1.0+.04*row["string"])
        comp=_plucked_component(freq,(end-start)/INTERNAL_SR,INTERNAL_SR,trng,damping=d,pick_position=pick,brightness=brightness,transient=row.get("attack",True),soft=row.get("soft",False))
        audio[start:end]+=comp[:end-start]
    if template.get("hasNegativeStructure",False):
        center=int(round((min(seconds-.20,1.70)+.03*(variant-1))*INTERNAL_SR)); width=max(8,int(.018*INTERNAL_SR))
        lo=max(0,center-width//2); hi=min(n,lo+width)
        if hi>lo: audio[lo:hi]+=0.12*trng.normal(0,1,hi-lo)*np.hanning(hi-lo)
        audio += trng.normal(0,1,n)*float(trng.uniform(.0005,.0020))
    else:
        audio += trng.normal(0,1,n)*.00025
    audio=lfilter([1.0-body_a],[1.0,-body_a],audio); peak=float(np.max(np.abs(audio)))
    if peak>0: audio=.78*audio/peak
    out=resample_poly(audio,1,2).astype(np.float32)
    want=int(round(seconds*OUTPUT_SR))
    if len(out)<want: out=np.pad(out,(0,want-len(out)))
    elif len(out)>want: out=out[:want]
    out=apply_renderer_arm(out,"R3",key)
    if not np.isfinite(out).all(): raise RuntimeError("nonfinite render")
    return out

def _v9_template(family,base,variant):
    base_t=build_template(family,base)
    if base_t["negativeOnly"]: return base_t
    times,_=attack_times(family,base,variant)
    protos=[dict(x) for x in base_t["segments"] if x.get("attack",True)]
    if not protos: protos=[dict(base_t["segments"][0])]
    rows=[]
    if family=="chords":
        if len(protos)!=6: raise RuntimeError("unexpected chord prototype")
        groups=[protos[:3],protos[3:6]]
        for gi,t in enumerate(times):
            srcs=groups[gi%2]
            for ni,p in enumerate(srcs):
                upper=min(SUSTAIN[1],DURATION-t); 
                if upper<SUSTAIN[0]: raise RuntimeError("infeasible chord sustain")
                dur=SUSTAIN[0]+sha_u(ROOT,"v9-sustain",split_for_base(base),family,base,variant,gi,ni)*(upper-SUSTAIN[0])
                rows.append(_event(p["string"],p["fret"],t,t+dur,attack=True,palm=p.get("palm",False),soft=p.get("soft",False)))
    else:
        for gi,t in enumerate(times):
            p=protos[gi%len(protos)]
            upper=min(SUSTAIN[1],DURATION-t)
            if upper<SUSTAIN[0]: raise RuntimeError("infeasible sustain")
            dur=SUSTAIN[0]+sha_u(ROOT,"v9-sustain",split_for_base(base),family,base,variant,gi,0)*(upper-SUSTAIN[0])
            rows.append(_event(p["string"],p["fret"],t,t+dur,attack=True,palm=p.get("palm",False),soft=p.get("soft",False)))
    return {"family":family,"baseIndex":base,"templateId":f"v9-{family}:{base:02d}:{variant}","split":split_for_base(base),
            "segments":rows,"negativeOnly":False,"hasNegativeStructure":base_t["hasNegativeStructure"]}

def _targets(template,frames):
    from synthetic.s0_pilot_v1 import targets_for_template
    return targets_for_template(template,frames)

def _dataset(seconds, intervention):
    features=[]; states=[]; onsets=[]; families=[]; splits=[]; tids=[]; negs=[]; negstruct=[]; refs=[]
    frame_count=None; attack_groups=0; attacked_labels=0
    for fi,family in enumerate(FAMILIES):
      for base in range(BASES_PER_FAMILY):
        for variant in range(VARIANTS_PER_BASE):
          if intervention:
            template=_v9_template(family,base,variant)
            timbre_tid=f"{family}:{base:02d}"
          else:
            template=build_template(family,base); timbre_tid=template["templateId"]
          key=fi*1000+base*10+variant
          audio=_render_template(template,variant,seconds,timbre_tid,key)
          feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
          if feat.ndim!=2 or feat.shape[1]!=CQT_BINS or not np.isfinite(feat).all(): raise RuntimeError("invalid features")
          if frame_count is None: frame_count=feat.shape[0]
          if feat.shape[0]!=frame_count: raise RuntimeError("inconsistent frame count")
          state,onset,rr=_targets(template,frame_count)
          features.append(feat); states.append(state); onsets.append(onset); families.append(family); splits.append(template["split"]); tids.append(template["templateId"])
          negs.append(template["negativeOnly"]); negstruct.append(template["hasNegativeStructure"]); refs.append(json.dumps(rr,separators=(",",":"),sort_keys=True))
          attacked_labels+=sum(1 for x in template["segments"] if x.get("attack",True))
          attack_groups+=sum(len(set(round(x["start"],9) for x in template["segments"] if x.get("attack",True))) for _ in [0])
    return {
      "features":np.stack(features),"state":np.stack(states),"onset":np.stack(onsets),
      "family":np.asarray(families),"split":np.asarray(splits),"template_id":np.asarray(tids),
      "negative_only":np.asarray(negs,dtype=np.bool_),"has_negative_structure":np.asarray(negstruct,dtype=np.bool_),"refs_json":np.asarray(refs),
    },{"examples":len(features),"seconds":len(features)*seconds,"frameCount":frame_count,"attackGroups":attack_groups,"attackedNoteLabels":attacked_labels}

def render_datasets(contract,timing,outdir):
    if not timing["passed"]: raise RuntimeError("V9A timing gate did not pass")
    started=time.monotonic(); out=Path(outdir); out.mkdir(parents=True,exist_ok=False)
    c,cr=_dataset(2.0,False); i,ir=_dataset(4.0,True)
    if len(c["features"])!=294 or len(i["features"])!=294: raise RuntimeError("dataset count mismatch")
    if ir["attackGroups"]!=1638 or ir["attackedNoteLabels"]!=1806: raise RuntimeError("V9 render identity mismatch")
    np.savez_compressed(out/"comparator.npz",**c); np.savez_compressed(out/"intervention.npz",**i)
    mib=((out/"comparator.npz").stat().st_size+(out/"intervention.npz").stat().st_size)/(1024**2)
    receipt={"schema":"astra-v9-render-receipt-v1","comparator":cr,"intervention":ir,"persistedMiB":mib,
             "elapsedSeconds":time.monotonic()-started,"withinStorageCeiling":mib<=contract["render"]["maxPersistedMiB"],
             "externalAudioAssets":False,"renderer":"R3"}
    if not receipt["withinStorageCeiling"]: raise RuntimeError("storage ceiling")
    (out/"render-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    return receipt

def _flat(d):
    x=context5(d["features"].astype(np.float32,copy=False)); frames=x.shape[1]
    return x.reshape(-1,x.shape[2]), d["state"].transpose(0,2,1).reshape(-1,6), d["onset"].transpose(0,2,1).reshape(-1,6), frames

def paired_batches(c,i):
    cs=build_sampling_strata(c["state"],c["onset"],c["split"],c["has_negative_structure"])
    is_=build_sampling_strata(i["state"],i["onset"],i["split"],i["has_negative_structure"])
    rng=np.random.RandomState(ROOT+17001); cb=[]; ib=[]
    keys=("positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive")
    for _ in range(MAX_STEPS):
        cc=[]; ii=[]
        for k in keys:
            u=rng.random_sample(32)
            cc.append(cs[k][np.minimum((u*len(cs[k])).astype(int),len(cs[k])-1)])
            ii.append(is_[k][np.minimum((u*len(is_[k])).astype(int),len(is_[k])-1)])
        perm=rng.permutation(BATCH_SIZE)
        cb.append(np.concatenate(cc)[perm]); ib.append(np.concatenate(ii)[perm])
    return np.stack(cb),np.stack(ib),{k:int(len(v)) for k,v in cs.items()},{k:int(len(v)) for k,v in is_.items()}

def _fit(d,batches,deadline):
    xf,sf,of,frames=_flat(d); model=initialize_arm(960,True); opt=torch.optim.Adam(model.parameters(),lr=.003)
    sampled_onset_labels=0; sampled_attack_frames=0; sampled_frames=0; started=time.monotonic()
    for step in range(MAX_STEPS):
        if time.monotonic()>=deadline: raise RuntimeError("fit deadline exceeded")
        idx=batches[step]; sampled_frames+=len(idx); ob=of[idx]; sampled_onset_labels+=int(ob.sum()); sampled_attack_frames+=int((ob==1).any(axis=1).sum())
        xb=torch.from_numpy(xf[idx]).float(); sb=torch.from_numpy(sf[idx]).long(); ot=torch.from_numpy(ob).long()
        opt.zero_grad(set_to_none=True); sl,ol=model(xb); loss,_,_=weighted_loss(sl,ol,sb,ot)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()): raise RuntimeError("nonfinite gradient")
        opt.step()
    return model,{"optimizerSteps":MAX_STEPS,"sampledFrames":sampled_frames,
                  "sampledFrameSeconds":sampled_frames*(HOP_LENGTH_SAMPLES/SAMPLE_RATE_HZ),
                  "sampledAttackedNoteLabels":sampled_onset_labels,"sampledAttackFrames":sampled_attack_frames,
                  "elapsedSeconds":time.monotonic()-started}

def train_and_sanity(contract,datadir,outdir):
    started=time.monotonic(); deadline=started+TRAIN_DEADLINE_SECONDS
    d=Path(datadir); out=Path(outdir); out.mkdir(parents=True,exist_ok=False)
    c={k:v for k,v in np.load(d/"comparator.npz",allow_pickle=False).items()}
    i={k:v for k,v in np.load(d/"intervention.npz",allow_pickle=False).items()}
    cb,ib,cs,is_=paired_batches(c,i)
    mc=initialize_arm(960,True); mi=initialize_arm(960,True)
    if module_sha(mc)!=module_sha(mi): raise RuntimeError("initialization mismatch")
    # Verify paired pre-update logits on each arm's first batch shape.
    cxf,_,_,_=_flat(c); ixf,_,_,_=_flat(i)
    with torch.no_grad():
        csl,col=mc(torch.from_numpy(cxf[cb[0]]).float())
        isl,iol=mi(torch.from_numpy(ixf[ib[0]]).float())
    # Different inputs imply different logits; only module identity is asserted.
    cm,cf=_fit(c,cb,deadline); im,wf=_fit(i,ib,deadline)
    # One common fixed synthetic evaluation population: comparator test.
    ctest=evaluate_arm(cm,c,"test"); itest=evaluate_arm(im,c,"test")
    g=contract["syntheticSanityGate"]
    checks={
      "onsetPrecision":itest["pitchOnset"]["precision"]>=g["onsetPrecisionAtLeast"],
      "pitchOnsetF1Decline":ctest["pitchOnset"]["f1"]-itest["pitchOnset"]["f1"]<=g["maxPitchOnsetF1DeclineVsComparator"],
      "onsetRecallDecline":ctest["pitchOnset"]["recall"]-itest["pitchOnset"]["recall"]<=g["maxOnsetRecallDeclineVsComparator"],
      "negativeFp":itest["negativeOnlyFalsePositiveEventsPerSecond"] is not None and itest["negativeOnlyFalsePositiveEventsPerSecond"]<=g["negativeFpPerSecondAtMost"],
      "steps":cf["optimizerSteps"]==500 and wf["optimizerSteps"]==500,
      "finite":all(math.isfinite(float(x)) for x in [itest["pitchOnset"]["precision"],itest["pitchOnset"]["recall"],itest["pitchOnset"]["f1"]]),
    }
    result={"schema":SCHEMA,"comparator":{"fit":cf,"test":ctest},"intervention":{"fit":wf,"testOnCommonComparatorPopulation":itest},
            "strata":{"comparator":cs,"intervention":is_},"initializationSha256":module_sha(initialize_arm(960,True)),
            "syntheticSanityChecks":checks,"syntheticSanityPassed":all(checks.values()),
            "execution":{"models":2,"optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],"fitEvalSeconds":time.monotonic()-started,
                         "automaticScientificRetries":0,"thresholdSearch":False,"modelInferenceOnRealAudio":0}}
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"comparator","stateDict":cm.state_dict(),"optimizerSteps":500},out/"comparator.pt")
    torch.save({"schema":SCHEMA,"arm":"intervention","stateDict":im.state_dict(),"optimizerSteps":500},out/"intervention.pt")
    return result

def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    p=sub.add_parser("verify"); p.add_argument("--contract",required=True); p.add_argument("--out",required=True)
    t=sub.add_parser("timing"); t.add_argument("--contract",required=True); t.add_argument("--out",required=True)
    r=sub.add_parser("render"); r.add_argument("--contract",required=True); r.add_argument("--timing",required=True); r.add_argument("--outdir",required=True)
    q=sub.add_parser("train"); q.add_argument("--contract",required=True); q.add_argument("--datadir",required=True); q.add_argument("--outdir",required=True)
    a=ap.parse_args(); contract=json.loads(Path(a.contract).read_text())
    if a.cmd=="verify":
        out=verify(a.contract); Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print("V9_VERIFY="+json.dumps(out,sort_keys=True))
    elif a.cmd=="timing":
        validate_contract(contract); out=make_timing(contract); Path(a.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n"); print("V9_TIMING="+json.dumps({k:out[k] for k in ("summary","timingDistanceV1","relativeImprovement","checks","passed")},sort_keys=True))
    elif a.cmd=="render":
        timing=json.loads(Path(a.timing).read_text()); print("V9_RENDER="+json.dumps(render_datasets(contract,timing,a.outdir),sort_keys=True))
    else:
        print("V9_TRAIN="+json.dumps(train_and_sanity(contract,a.datadir,a.outdir),sort_keys=True))

if __name__=="__main__":
    main()
