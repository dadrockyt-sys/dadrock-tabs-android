#!/usr/bin/env python3
"""Astra V11 state-duration / legato-continuation isolation study.

Preparation is model-free until a separately authorized V11 empirical launch exists.

Control:
  exact executed V9 4-second dataset semantics.

Intervention:
  exact V9 attack times, attack counts, attacked note identities and timbre process,
  but restore S0 family-specific state/audio durations, with deterministic truncation
  at the next attack on the same string, and restore the S0 legato non-attacked
  continuation when temporal room exists.

No V2B or real audio is used here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from pathlib import Path

import numpy as np
import torch

from synthetic.s0_pilot_v1 import (
    FAMILIES, BASES_PER_FAMILY, VARIANTS_PER_BASE,
    _event, build_template, split_for_base,
)
from synthetic.s1_pilot_v1 import build_sampling_strata
from synthetic.s6_pilot_v1 import initialize_arm, module_sha, evaluate_arm
from synthetic.v9_empirical_v1 import (
    ROOT, DURATION, MAX_STEPS, BATCH_SIZE,
    attack_times, _positive_base, _v9_template, _dataset, _render_template,
    _targets, _flat, _fit,
)

SCHEMA="astra-v11-state-semantics-v1"
MAX_TOTAL_STEPS=1000
FIT_DEADLINE_SECONDS=3600.0

HISTORICAL_ATTACK_DURATION={
    "isolated":1.03,
    "scales":0.27,
    "chords":0.48,
    "repeated":0.31,
    "legato":0.50,
    "palmmute":0.16,
    "mixed":0.86,
}
LEGATO_CONTINUATION_DURATION=0.74


class V11Error(RuntimeError):
    pass


def _attacked_prototypes(base_t):
    p=[dict(x) for x in base_t["segments"] if x.get("attack",True)]
    if not p and base_t["segments"]:
        p=[dict(base_t["segments"][0])]
    return p


def _raw_attack_rows(family,base,variant):
    base_t=build_template(family,base)
    if base_t["negativeOnly"]:
        return base_t,[]
    times,_=attack_times(family,base,variant)
    protos=_attacked_prototypes(base_t)
    rows=[]
    if family=="chords":
        if len(protos)!=6:
            raise V11Error("unexpected chord prototype")
        groups=[protos[:3],protos[3:6]]
        for gi,t in enumerate(times):
            for p in groups[gi%2]:
                rows.append({
                    "string":int(p["string"]),"fret":int(p["fret"]),"start":float(t),
                    "palm":bool(p.get("palm",False)),"soft":bool(p.get("soft",False)),
                    "attack":True,
                })
    else:
        for gi,t in enumerate(times):
            p=protos[gi%len(protos)]
            rows.append({
                "string":int(p["string"]),"fret":int(p["fret"]),"start":float(t),
                "palm":bool(p.get("palm",False)),"soft":bool(p.get("soft",False)),
                "attack":True,
            })
    return base_t,rows


def _next_attack_same_string(raw_rows,index):
    row=raw_rows[index]
    later=[x["start"] for j,x in enumerate(raw_rows) if j!=index and x["string"]==row["string"] and x["start"]>row["start"]+1e-12]
    return min(later) if later else DURATION


def build_state_semantic_template(family,base,variant):
    """Build V11 intervention template without changing attacked onsets/note identity."""
    base_t,raw=_raw_attack_rows(family,base,variant)
    if base_t["negativeOnly"]:
        return base_t

    rows=[]
    continuation_proto=None
    if family=="legato":
        cont=[dict(x) for x in base_t["segments"] if not x.get("attack",True)]
        if len(cont)!=1:
            raise V11Error("expected exactly one historical legato continuation prototype")
        continuation_proto=cont[0]

    desired=HISTORICAL_ATTACK_DURATION[family]
    for i,r in enumerate(raw):
        next_attack=_next_attack_same_string(raw,i)
        attack_end=min(r["start"]+desired,next_attack,DURATION)
        if attack_end<=r["start"]:
            raise V11Error("nonpositive attacked state duration")
        rows.append(_event(
            r["string"],r["fret"],r["start"],attack_end,
            attack=True,palm=r["palm"],soft=r["soft"]
        ))

        if family=="legato":
            continuation_start=r["start"]+HISTORICAL_ATTACK_DURATION["legato"]
            continuation_end=min(
                continuation_start+LEGATO_CONTINUATION_DURATION,
                next_attack,
                DURATION,
            )
            if continuation_end>continuation_start+1e-12:
                rows.append(_event(
                    continuation_proto["string"],continuation_proto["fret"],
                    continuation_start,continuation_end,
                    attack=False,
                    palm=continuation_proto.get("palm",False),
                    soft=continuation_proto.get("soft",True),
                ))

    # No overlapping state labels on the same string.
    by_string={s:[] for s in range(6)}
    for r in rows:
        by_string[r["string"]].append(r)
    for s,items in by_string.items():
        items=sorted(items,key=lambda x:(x["start"],0 if x["attack"] else 1,x["end"]))
        for a,b in zip(items,items[1:]):
            if a["end"]>b["start"]+1e-12:
                raise V11Error(f"same-string state overlap on string {s}")

    return {
        "family":family,
        "baseIndex":base,
        "templateId":f"v11-state-{family}:{base:02d}:{variant}",
        "split":split_for_base(base),
        "segments":rows,
        "negativeOnly":False,
        "hasNegativeStructure":base_t["hasNegativeStructure"],
    }


def attacked_signature(template):
    return sorted(
        (int(x["string"]),int(x["fret"]),round(float(x["start"]),12))
        for x in template["segments"] if x.get("attack",True)
    )


def static_audit():
    clips=0; positive=0; negative=0
    control_attacks=0; intervention_attacks=0
    control_labels=0; intervention_labels=0
    continuation_events=0
    truncated_attacks=0
    family={f:{"positiveClips":0,"continuationEvents":0,"truncatedAttackedStates":0} for f in FAMILIES}
    signature_hash=hashlib.sha256()

    for f in FAMILIES:
      for b in range(BASES_PER_FAMILY):
        for v in range(VARIANTS_PER_BASE):
          clips+=1
          control=_v9_template(f,b,v)
          intervention=build_state_semantic_template(f,b,v)
          if control["negativeOnly"]:
              negative+=1
              if intervention["segments"]!=control["segments"]:
                  raise V11Error("negative-only intervention changed")
              continue
          positive+=1; family[f]["positiveClips"]+=1
          cs=attacked_signature(control); is_=attacked_signature(intervention)
          if cs!=is_:
              raise V11Error(f"attacked signature changed {f}/{b}/{v}")
          control_attacks+=len(set(t for _,_,t in cs))
          intervention_attacks+=len(set(t for _,_,t in is_))
          control_labels+=len(cs); intervention_labels+=len(is_)
          for item in is_:
              signature_hash.update(json.dumps([f,b,v,*item],separators=(",",":")).encode()+b"\n")

          cont=[x for x in intervention["segments"] if not x.get("attack",True)]
          continuation_events+=len(cont); family[f]["continuationEvents"]+=len(cont)

          # Count attacked events whose historical target had to end at retrigger/clip.
          desired=HISTORICAL_ATTACK_DURATION[f]
          for r in intervention["segments"]:
              if not r.get("attack",True): continue
              if r["end"] < min(r["start"]+desired,DURATION)-1e-12:
                  truncated_attacks+=1; family[f]["truncatedAttackedStates"]+=1

    if clips!=294 or positive!=273 or negative!=21:
        raise V11Error("clip identity mismatch")
    if control_attacks!=1638 or intervention_attacks!=1638:
        raise V11Error("attack-group identity mismatch")
    if control_labels!=1806 or intervention_labels!=1806:
        raise V11Error("attacked-note identity mismatch")
    if continuation_events<=0:
        raise V11Error("legato continuation restoration produced no events")

    return {
        "schema":"astra-v11-state-semantics-static-audit-v1",
        "clips":clips,
        "positiveClips":positive,
        "negativeOnlyClips":negative,
        "controlAttackGroups":control_attacks,
        "interventionAttackGroups":intervention_attacks,
        "controlAttackedNoteLabels":control_labels,
        "interventionAttackedNoteLabels":intervention_labels,
        "attackedSignatureSha256":signature_hash.hexdigest(),
        "restoredNonAttackedContinuationEvents":continuation_events,
        "truncatedAttackedStatesAtSameStringRetrigger":truncated_attacks,
        "perFamily":family,
        "waveformsRendered":0,
        "modelsTrained":0,
        "optimizerSteps":0,
        "modelInference":0,
        "v2bInference":0,
    }


def _semantic_dataset():
    features=[]; states=[]; onsets=[]; families=[]; splits=[]; tids=[]; negs=[]; negstruct=[]; refs=[]
    frame_count=None
    for fi,family in enumerate(FAMILIES):
      for base in range(BASES_PER_FAMILY):
        for variant in range(VARIANTS_PER_BASE):
          template=build_state_semantic_template(family,base,variant)
          key=fi*1000+base*10+variant
          audio=_render_template(template,variant,4.0,f"{family}:{base:02d}",key)
          # Reuse exact V9 feature pipeline through the private dataset helpers' imports.
          from synthetic.v9_empirical_v1 import extract_cqt_features, rms_normalize, CQT_BINS
          feat=extract_cqt_features(rms_normalize(audio)).squeeze(0).T.astype(np.float32,copy=False)
          if feat.ndim!=2 or feat.shape[1]!=CQT_BINS or not np.isfinite(feat).all():
              raise V11Error("invalid features")
          if frame_count is None: frame_count=feat.shape[0]
          if feat.shape[0]!=frame_count: raise V11Error("frame count mismatch")
          state,onset,rr=_targets(template,frame_count)
          features.append(feat); states.append(state); onsets.append(onset)
          families.append(family); splits.append(template["split"]); tids.append(template["templateId"])
          negs.append(template["negativeOnly"]); negstruct.append(template["hasNegativeStructure"])
          refs.append(json.dumps(rr,separators=(",",":"),sort_keys=True))
    return {
      "features":np.stack(features),"state":np.stack(states),"onset":np.stack(onsets),
      "family":np.asarray(families),"split":np.asarray(splits),"template_id":np.asarray(tids),
      "negative_only":np.asarray(negs,dtype=np.bool_),
      "has_negative_structure":np.asarray(negstruct,dtype=np.bool_),
      "refs_json":np.asarray(refs),
    }


def paired_batches(control,intervention):
    cs=build_sampling_strata(control["state"],control["onset"],control["split"],control["has_negative_structure"])
    is_=build_sampling_strata(intervention["state"],intervention["onset"],intervention["split"],intervention["has_negative_structure"])
    # Positive-onset indices must be exactly identical because attacks are frozen.
    if not np.array_equal(cs["positiveOnset"],is_["positiveOnset"]):
        raise V11Error("positive-onset frame identity changed")
    rng=np.random.RandomState(ROOT+17001)
    cb=[]; ib=[]
    keys=("positiveOnset","activeNonOnset","negativeStructureInactive","otherInactive")
    for _ in range(MAX_STEPS):
        cc=[]; ii=[]
        for k in keys:
            u=rng.random_sample(32)
            cc.append(cs[k][np.minimum((u*len(cs[k])).astype(int),len(cs[k])-1)])
            ii.append(is_[k][np.minimum((u*len(is_[k])).astype(int),len(is_[k])-1)])
        perm=rng.permutation(BATCH_SIZE)
        cb.append(np.concatenate(cc)[perm]); ib.append(np.concatenate(ii)[perm])
    return np.stack(cb),np.stack(ib),{
      "control":{k:int(len(v)) for k,v in cs.items()},
      "intervention":{k:int(len(v)) for k,v in is_.items()},
      "positiveOnsetIndicesIdentical":True,
    }


def _metric_view(x):
    return {
      "precision":float(x["pitchOnset"]["precision"]),
      "recall":float(x["pitchOnset"]["recall"]),
      "f1":float(x["pitchOnset"]["f1"]),
      "negativeFpPerSecond":float(x["negativeOnlyFalsePositiveEventsPerSecond"]),
      "stateAdmission":float(x["admission"]["stateAdmissionFraction"]),
      "onsetAdmission":float(x["admission"]["onsetAdmissionFraction"]),
      "jointAdmission":float(x["admission"]["jointAdmissionFraction"]),
    }


def run(outdir):
    """Future empirical entry point; requires a separately armed launch."""
    started=time.monotonic(); deadline=started+FIT_DEADLINE_SECONDS
    out=Path(outdir); out.mkdir(parents=True,exist_ok=False)

    common,_=_dataset(2.0,False)
    control,_=_dataset(4.0,True)
    intervention=_semantic_dataset()
    cb,ib,strata=paired_batches(control,intervention)

    m0=initialize_arm(960,True); m1=initialize_arm(960,True)
    if module_sha(m0)!=module_sha(m1):
        raise V11Error("initialization mismatch")

    control_model,cf=_fit(control,cb,deadline)
    intervention_model,wf=_fit(intervention,ib,deadline)

    c_common=_metric_view(evaluate_arm(control_model,common,"test"))
    i_common=_metric_view(evaluate_arm(intervention_model,common,"test"))
    c_v9=_metric_view(evaluate_arm(control_model,control,"test"))
    i_v9=_metric_view(evaluate_arm(intervention_model,control,"test"))

    frozen={"precision":0.3244274809160305,"recall":0.6589147286821705,"f1":0.43478260869565216}
    reproduced=all(abs(c_common[k]-v)<=1e-12 for k,v in frozen.items())

    checks={
      "baselineReproducedExactly":reproduced,
      "commonPrecisionGainAtLeast0_15":i_common["precision"]-c_common["precision"]>=.15,
      "commonF1GainAtLeast0_10":i_common["f1"]-c_common["f1"]>=.10,
      "commonRecallDeclineAtMost0_05":c_common["recall"]-i_common["recall"]<=.05,
      "commonJointAdmissionDeclineAtMost0_05":c_common["jointAdmission"]-i_common["jointAdmission"]<=.05,
      "commonNegativeFpPerSecondAtMost0_10":i_common["negativeFpPerSecond"]<=.10,
      "v9F1DeclineAtMost0_05":c_v9["f1"]-i_v9["f1"]<=.05,
      "exact500StepsPerModel":cf["optimizerSteps"]==500 and wf["optimizerSteps"]==500,
    }

    result={
      "schema":SCHEMA,
      "staticAudit":static_audit(),
      "strata":strata,
      "control":{"fit":cf,"commonComparatorTest":c_common,"v9Test":c_v9},
      "stateSemanticRestored":{"fit":wf,"commonComparatorTest":i_common,"v9Test":i_v9},
      "deltas":{
        "commonPrecision":i_common["precision"]-c_common["precision"],
        "commonRecall":i_common["recall"]-c_common["recall"],
        "commonF1":i_common["f1"]-c_common["f1"],
        "commonJointAdmission":i_common["jointAdmission"]-c_common["jointAdmission"],
        "v9F1":i_v9["f1"]-c_v9["f1"],
      },
      "checks":checks,
      "stateSemanticsHypothesisSupported":all(checks.values()),
      "execution":{
        "models":2,
        "optimizerStepsTotal":cf["optimizerSteps"]+wf["optimizerSteps"],
        "elapsedSeconds":time.monotonic()-started,
        "automaticScientificRetries":0,
        "thresholdSearch":False,
        "realAudioInference":0,
        "v2bInference":0,
      },
      "meaning":"Synthetic-only controlled state-duration/legato-continuation diagnostic; no real-transfer or product claim."
    }
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    torch.save({"schema":SCHEMA,"arm":"executed-v9-control","stateDict":control_model.state_dict()},out/"control.pt")
    torch.save({"schema":SCHEMA,"arm":"state-semantics-restored","stateDict":intervention_model.state_dict()},out/"intervention.pt")
    return result


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    s=sub.add_parser("static"); s.add_argument("--out",required=True)
    r=sub.add_parser("run"); r.add_argument("--outdir",required=True)
    a=ap.parse_args()
    if a.cmd=="static":
        x=static_audit(); Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n"); print(json.dumps(x,sort_keys=True))
    else:
        print(json.dumps(run(a.outdir),sort_keys=True))


if __name__=="__main__":
    main()
