#!/usr/bin/env python3
"""V14 2-second matched-context bridge empirical runner.

Synthetic-only. Executes exactly two 2-second arms after the frozen pure
contract validator passes. No V2B or real-audio access.
"""
from __future__ import annotations
import argparse, hashlib, json, math, time
from pathlib import Path
import numpy as np
import torch

from astra_backend.synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE, build_template, _event,
    split_for_base, extract_cqt_features, rms_normalize, context5, CQT_BINS,
    HOP_LENGTH_SAMPLES, SAMPLE_RATE_HZ,
)
from astra_backend.synthetic.s1_pilot_v1 import build_sampling_strata
from astra_backend.synthetic.s6_pilot_v1 import initialize_arm, module_sha, weighted_loss, evaluate_arm
from astra_backend.synthetic.v9_empirical_v1 import _render_template
from astra_backend.synthetic.v14_contract_validator_v1 import build_schedule, validate as validate_contract

SCHEMA="astra-v14-matched-context-bridge-result-v1"
MAX_STEPS=500
BATCH_SIZE=128
DURATION=2.0
ROOT=20260929
BATCH_ROOT=20260927  # exact historical V9 paired-batch root

HIST_DUR={
 "isolated":1.03,"scales":.27,"chords":.48,"repeated":.31,
 "legato_attacked":.50,"legato_continuation":.74,"palmmute":.16,"mixed":.86
}

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def _schedule_map():
    rows,_=build_schedule()
    return {(r["family"],r["base"],r["variant"]):r for r in rows}

def _truncate_same_string(rows):
    rows=sorted(rows,key=lambda x:(x["start"],0 if x.get("attack",True) else 1,x["string"]))
    trunc=0
    for i,row in enumerate(rows):
        next_times=[z["start"] for z in rows[i+1:] if z["string"]==row["string"] and z["start"]>row["start"]+1e-12]
        if next_times:
            nxt=min(next_times)
            if row["end"]>nxt:
                row["end"]=nxt; trunc+=1
        row["end"]=min(float(row["end"]),DURATION)
        if row["end"]<=row["start"]:
            raise RuntimeError("non-positive state duration after deterministic truncation")
    return rows,trunc

def bridge_template(family,base,variant,smap):
    base_t=build_template(family,base)
    if base_t["negativeOnly"]:
        return base_t,0
    sch=smap[(family,base,variant)]
    times=list(sch["times"])
    attacked=[dict(x) for x in base_t["segments"] if x.get("attack",True)]
    if not attacked: raise RuntimeError("missing attacked prototype")
    rows=[]
    if family=="chords":
        if len(attacked)!=6: raise RuntimeError("unexpected chord prototype count")
        groups=[attacked[:3],attacked[3:6]]
        for gi,t in enumerate(times):
            for p in groups[gi%2]:
                rows.append(_event(p["string"],p["fret"],t,min(DURATION,t+HIST_DUR["chords"]),attack=True,palm=False,soft=False))
    elif family=="legato":
        p=attacked[0]
        # recover original continuation pitch/string relation from historical template
        cont=[dict(x) for x in base_t["segments"] if not x.get("attack",True)]
        rows.append(_event(p["string"],p["fret"],times[0],min(DURATION,times[0]+HIST_DUR["legato_attacked"]),attack=True,soft=False))
        if cont:
            c=cont[0]; st=min(DURATION,times[0]+HIST_DUR["legato_attacked"])
            if st<DURATION:
                rows.append(_event(c["string"],c["fret"],st,min(DURATION,st+HIST_DUR["legato_continuation"]),attack=False,soft=True))
    else:
        dur=HIST_DUR[family]
        for gi,t in enumerate(times):
            p=attacked[gi%len(attacked)]
            rows.append(_event(p["string"],p["fret"],t,min(DURATION,t+dur),attack=True,palm=p.get("palm",False),soft=p.get("soft",False)))
    rows,trunc=_truncate_same_string(rows)
    return {
      "family":family,"baseIndex":base,
      "templateId":f"v14-{family}:{base:02d}:{variant}",
      "split":split_for_base(base),"segments":rows,"negativeOnly":False,
      "hasNegativeStructure":base_t["hasNegativeStructure"],
    },trunc

def _targets(template,frames):
    from astra_backend.synthetic.s0_pilot_v1 import targets_for_template
    return targets_for_template(template,frames)

def make_dataset(bridge):
    smap=_schedule_map()
    features=[]; states=[]; onsets=[]; families=[]; splits=[]; tids=[]; negs=[]; negstruct=[]; refs=[]
    frame_count=None; attack_groups=0; attacked_labels=0; truncations=0
    for fi,family in enumerate(FAMILIES):
      for base in range(BASES_PER_FAMILY):
        for variant in range(VARIANTS_PER_BASE):
          if bridge:
            template,tr=bridge_template(family,base,variant,smap); truncations+=tr
            timbre_tid=f"{family}:{base:02d}"
          else:
            template=build_template(family,base); timbre_tid=template["templateId"]
          key=fi*1000+base*10+variant
          audio=_render_template(template,variant,DURATION,timbre_tid,key)
          feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
          if feat.ndim!=2 or feat.shape[1]!=CQT_BINS or not np.isfinite(feat).all():
              raise RuntimeError("invalid features")
          if frame_count is None: frame_count=feat.shape[0]
          if feat.shape[0]!=frame_count: raise RuntimeError("frame-count drift")
          st,on,rr=_targets(template,frame_count)
          features.append(feat); states.append(st); onsets.append(on)
          families.append(family); splits.append(template["split"]); tids.append(template["templateId"])
          negs.append(template["negativeOnly"]); negstruct.append(template["hasNegativeStructure"])
          refs.append(json.dumps(rr,separators=(",",":"),sort_keys=True))
          attacked=[x for x in template["segments"] if x.get("attack",True)]
          attacked_labels+=len(attacked)
          attack_groups+=len(set((round(x["start"],9),) for x in attacked))
    d={
      "features":np.stack(features),"state":np.stack(states),"onset":np.stack(onsets),
      "family":np.asarray(families),"split":np.asarray(splits),"template_id":np.asarray(tids),
      "negative_only":np.asarray(negs,dtype=np.bool_),"has_negative_structure":np.asarray(negstruct,dtype=np.bool_),
      "refs_json":np.asarray(refs),
    }
    receipt={"examples":len(features),"seconds":len(features)*DURATION,"frameCount":frame_count,
             "attackGroups":attack_groups,"attackedNoteLabels":attacked_labels,"stateTruncations":truncations}
    return d,receipt

def flat(d):
    x=context5(d["features"].astype(np.float32,copy=False))
    return x.reshape(-1,x.shape[2]), d["state"].transpose(0,2,1).reshape(-1,6), d["onset"].transpose(0,2,1).reshape(-1,6)

def paired_batches(c,b):
    cs=build_sampling_strata(c["state"],c["onset"],c["split"],c["has_negative_structure"])
    bs=build_sampling_strata(b["state"],b["onset"],b["split"],b["has_negative_structure"])
    rng=np.random.RandomState(BATCH_ROOT+17001); cb=[]; bb=[]
    keys=("positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive")
    for _ in range(MAX_STEPS):
        cc=[]; ii=[]
        for k in keys:
            u=rng.random_sample(32)
            cc.append(cs[k][np.minimum((u*len(cs[k])).astype(int),len(cs[k])-1)])
            ii.append(bs[k][np.minimum((u*len(bs[k])).astype(int),len(bs[k])-1)])
        perm=rng.permutation(BATCH_SIZE)
        cb.append(np.concatenate(cc)[perm]); bb.append(np.concatenate(ii)[perm])
    return np.stack(cb),np.stack(bb),{k:int(len(v)) for k,v in cs.items()},{k:int(len(v)) for k,v in bs.items()}

def fit(d,batches):
    xf,sf,of=flat(d); model=initialize_arm(960,True); opt=torch.optim.Adam(model.parameters(),lr=.003)
    sampled_labels=0; sampled_attack_frames=0
    for step in range(MAX_STEPS):
        idx=batches[step]; ob=of[idx]
        sampled_labels+=int(ob.sum()); sampled_attack_frames+=int((ob==1).any(axis=1).sum())
        xb=torch.from_numpy(xf[idx]).float(); sb=torch.from_numpy(sf[idx]).long(); ot=torch.from_numpy(ob).long()
        opt.zero_grad(set_to_none=True); sl,ol=model(xb); loss,_,_=weighted_loss(sl,ol,sb,ot)
        if not torch.isfinite(loss): raise RuntimeError("nonfinite loss")
        loss.backward()
        if any(p.grad is not None and not torch.all(torch.isfinite(p.grad)) for p in model.parameters()):
            raise RuntimeError("nonfinite gradient")
        opt.step()
    return model,{"optimizerSteps":MAX_STEPS,"sampledFrames":MAX_STEPS*BATCH_SIZE,
                  "sampledAttackedNoteLabels":sampled_labels,"sampledAttackFrames":sampled_attack_frames}

def run(contract_path,outdir):
    contract=json.loads(Path(contract_path).read_text())
    pre=validate_contract(contract)
    if not pre["passed"]: raise RuntimeError("contract preflight failed")
    out=Path(outdir); out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    c,cr=make_dataset(False); b,br=make_dataset(True)
    if cr["examples"]!=294 or br["examples"]!=294: raise RuntimeError("dataset size mismatch")
    if br["attackGroups"]!=819: raise RuntimeError("bridge attack-group mismatch")
    cb,bb,cs,bs=paired_batches(c,b)
    m0=initialize_arm(960,True); m1=initialize_arm(960,True)
    if module_sha(m0)!=module_sha(m1): raise RuntimeError("initialization mismatch")
    cm,cf=fit(c,cb); bm,bf=fit(b,bb)
    c_common=evaluate_arm(cm,c,"test")
    b_common=evaluate_arm(bm,c,"test")
    b_bridge=evaluate_arm(bm,b,"test")

    ref=contract["reference"]["successfulComparator"]
    # exact deterministic control reproduction guard
    repro={
      "precision":abs(c_common["pitchOnset"]["precision"]-ref["precision"])<=1e-12,
      "recall":abs(c_common["pitchOnset"]["recall"]-ref["recall"])<=1e-12,
      "f1":abs(c_common["pitchOnset"]["f1"]-ref["f1"])<=1e-12,
    }
    if not all(repro.values()):
        failure={
          "schema":"astra-v14-control-reproduction-failure-v1",
          "controlCommon":c_common,
          "expectedControl":ref,
          "reproductionChecks":repro,
          "batchRoot":BATCH_ROOT,
          "optimizerStepsTotal":cf["optimizerSteps"]+bf["optimizerSteps"],
          "scientificResultInterpretable":False,
        }
        (out/"control-reproduction-failure.json").write_text(json.dumps(failure,indent=2,sort_keys=True)+"\n")
        raise RuntimeError("control reproduction failed")

    g=contract["empiricalGate"]
    checks={
      "controlReproduced":all(repro.values()),
      "commonF1":b_common["pitchOnset"]["f1"]>=g["commonF1AtLeast"],
      "commonPrecision":b_common["pitchOnset"]["precision"]>=g["commonPrecisionAtLeast"],
      "commonRecallDecline":ref["recall"]-b_common["pitchOnset"]["recall"]<=g["maxRecallDeclineVsSuccessfulComparator"],
      "negativeFp":b_common["negativeOnlyFalsePositiveEventsPerSecond"] is not None and b_common["negativeOnlyFalsePositiveEventsPerSecond"]<=g["negativeFpPerSecondAtMost"],
      "steps":cf["optimizerSteps"]==500 and bf["optimizerSteps"]==500,
      "finite":all(math.isfinite(float(x)) for x in [
          b_common["pitchOnset"]["precision"],b_common["pitchOnset"]["recall"],b_common["pitchOnset"]["f1"]]),
      "thresholdSearchFalse":g["noThresholdSearch"] is True,
      "retryFalse":g["noAutomaticScientificRetry"] is True,
    }
    result={
      "schema":SCHEMA,"status":"complete",
      "contractSha256":sha256_file(contract_path),
      "render":{"control":cr,"bridge":br},
      "strata":{"control":cs,"bridge":bs},
      "fit":{"control":cf,"bridge":bf},
      "controlCommon":c_common,"bridgeCommon":b_common,"bridgeOwnTest":b_bridge,
      "controlReproduction":repro,"checks":checks,"supported":all(checks.values()),
      "deltas":{
        "precisionBridgeMinusControl":b_common["pitchOnset"]["precision"]-c_common["pitchOnset"]["precision"],
        "recallBridgeMinusControl":b_common["pitchOnset"]["recall"]-c_common["pitchOnset"]["recall"],
        "f1BridgeMinusControl":b_common["pitchOnset"]["f1"]-c_common["pitchOnset"]["f1"],
      },
      "recovery":{
        "f1FractionOfOriginalDeficit":(b_common["pitchOnset"]["f1"]-contract["reference"]["v9Common"]["f1"])/contract["reference"]["f1Deficit"],
        "precisionFractionOfOriginalDeficit":(b_common["pitchOnset"]["precision"]-contract["reference"]["v9Common"]["precision"])/contract["reference"]["precisionDeficit"],
      },
      "execution":{"models":2,"optimizerStepsTotal":1000,"waveformDatasets":2,
                   "thresholdSearch":False,"automaticScientificRetries":0,"v2b":False,"realAudio":False,
                   "elapsedSeconds":time.monotonic()-started}
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"control","stateDict":cm.state_dict(),"optimizerSteps":500},out/"control.pt")
    torch.save({"schema":SCHEMA,"arm":"bridge","stateDict":bm.state_dict(),"optimizerSteps":500},out/"bridge.pt")
    receipt={"schema":"astra-v14-execution-receipt-v1","resultSha256":sha256_file(out/"result.json"),
             "controlModelSha256":sha256_file(out/"control.pt"),"bridgeModelSha256":sha256_file(out/"bridge.pt"),
             "scientificRetry":False,"v2b":False,"realAudio":False}
    (out/"execution-receipt.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print("V14_RESULT="+json.dumps(result,sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--contract",required=True); ap.add_argument("--outdir",required=True)
    a=ap.parse_args(); run(a.contract,a.outdir)

if __name__=="__main__": main()
