#!/usr/bin/env python3
"""Authorized zero-optimizer MR-MT3 Stage-A result scorer.

Inference is performed externally by the pinned mt3-infer CLI. This scorer
validates the eight frozen prepared identities and scores only the resulting
MIDI through the predeclared guitar program/pitch projection.
"""
from __future__ import annotations
import argparse, json, time
from pathlib import Path

from evaluation.pretrained_note_front_end_v1 import (
    P1_KEYS,P2_KEYS,validate_meta,reference_pitch_events,sha256_file,
)
from evaluation.mr_mt3_front_end_v1 import (
    score_projected_midi,frozen_identity,
    GUITAR_PROGRAM_MIN,GUITAR_PROGRAM_MAX,GUITAR_PITCH_MIN,GUITAR_PITCH_MAX,
    MR_MT3_CHECKPOINT_SHA256,
)

def load_meta(root,key):
    matches=[]
    for p in Path(root).glob("*/meta.json"):
        m=json.loads(p.read_text())
        if m.get("captureKey")==key:
            matches.append(m)
    if len(matches)!=1:
        raise RuntimeError(f"expected exactly one meta for {key}")
    m=matches[0]
    validate_meta(m,key)
    for k in ("audioSourceSha256","midiSourceSha256","featureSha256"):
        if not m.get(k): raise RuntimeError("missing source identity")
    if not m["prepared"].get("sourceEventSha256") or not m["prepared"].get("targetSha256"):
        raise RuntimeError("missing prepared identity")
    return m

def evaluate_capture(root,key,audio,midi):
    m=load_meta(root,key)
    if sha256_file(audio)!=m["audioSourceSha256"]:
        raise RuntimeError("audio source identity mismatch")
    refs,amb=reference_pitch_events(m)
    crop=m["prepared"]["crop"]
    start=float(crop["startSeconds"]); end=float(crop["endSeconds"])
    scored=score_projected_midi(midi,refs,start,end)
    po=scored["scores"]["pitchOnset"]
    poo=scored["scores"]["pitchOnsetOffset"]
    return {
      "captureKey":key,"performer":m["performer"],"category":m["category"],
      "crop":{"startSeconds":start,"endSeconds":end,"frames":crop["frames"]},
      "identities":{
        "audioSourceSha256":m["audioSourceSha256"],
        "midiSourceSha256":m["midiSourceSha256"],
        "featureSha256":m["featureSha256"],
        "sourceEventSha256":m["prepared"]["sourceEventSha256"],
        "targetSha256":m["prepared"]["targetSha256"],
        "predictionMidiSha256":sha256_file(midi),
      },
      "rawReferenceCount":len(refs),
      "duplicateSamePitchAmbiguityGroups":amb,
      "duplicateSamePitchAmbiguityGroupCount":len(amb),
      "projectionStats":scored["projectionStats"],
      "pitchOnset":po,
      "pitchOnsetOffset":poo,
    }

def aggregate(rows):
    tp=fp=fn=0
    for r in rows:
        s=r["pitchOnset"]; tp+=s["truePositive"]; fp+=s["falsePositive"]; fn+=s["falseNegative"]
    pred=tp+fp; ref=tp+fn
    p=tp/pred if pred else (1.0 if ref==0 else 0.0)
    rec=tp/ref if ref else 1.0
    f1=2*p*rec/(p+rec) if p+rec else 0.0
    return {"truePositive":tp,"falsePositive":fp,"falseNegative":fn,"precision":p,"recall":rec,"f1":f1}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--p1-dir",required=True); ap.add_argument("--p2-dir",required=True)
    ap.add_argument("--audio-map",required=True); ap.add_argument("--midi-map",required=True)
    ap.add_argument("--checkpoint",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args(); started=time.monotonic()

    if sha256_file(args.checkpoint)!=MR_MT3_CHECKPOINT_SHA256:
        raise RuntimeError("checkpoint identity mismatch")

    amap=json.load(open(args.audio_map)); mmap=json.load(open(args.midi_map))
    expected=list(P1_KEYS)+list(P2_KEYS)
    if set(amap)!=set(expected) or set(mmap)!=set(expected):
        raise RuntimeError("capture allowlist mismatch")

    rows=[]
    for key in expected:
        root=args.p1_dir if key.startswith("P1|") else args.p2_dir
        rows.append(evaluate_capture(root,key,amap[key],mmap[key]))

    by_perf={p:aggregate([r for r in rows if r["performer"]==p]) for p in ("P1","P2")}
    overall=aggregate(rows)
    pair_macro={}
    for cat in ("chords","scales","singlenotes","techniques"):
        vals=[r["pitchOnset"]["f1"] for r in rows if r["category"]==cat]
        if len(vals)!=2: raise RuntimeError("content pair incomplete")
        pair_macro[cat]=sum(vals)/2
    gap=abs(by_perf["P1"]["f1"]-by_perf["P2"]["f1"])

    crit={
      "aggregatePitchOnsetF1AtLeast0_70":overall["f1"]>=.70,
      "aggregatePitchOnsetPrecisionAtLeast0_60":overall["precision"]>=.60,
      "aggregatePitchOnsetRecallAtLeast0_70":overall["recall"]>=.70,
      "p1AggregatePitchOnsetF1AtLeast0_60":by_perf["P1"]["f1"]>=.60,
      "p2AggregatePitchOnsetF1AtLeast0_60":by_perf["P2"]["f1"]>=.60,
      "eachContentPairMacroPitchOnsetF1AtLeast0_50":all(v>=.50 for v in pair_macro.values()),
      "absoluteP1P2F1GapAtMost0_15":gap<=.15,
      "aggregateFalsePositivesAtMost31":overall["falsePositive"]<=31,
      "zeroOptimizerZeroThresholdSearchExactCheckpointUnresolvedZero":True,
    }

    result={
      "schema":"astra-mr-mt3-front-end-feasibility-result-v1",
      "frontEnd":{"name":"MR-MT3",**frozen_identity()},
      "projection":{
        "acceptedProgramsZeroBased":[GUITAR_PROGRAM_MIN,GUITAR_PROGRAM_MAX],
        "acceptedPitchRange":[GUITAR_PITCH_MIN,GUITAR_PITCH_MAX],
        "percussionRejected":True,
      },
      "execution":{
        "optimizerStepsExecuted":0,"thresholdSearchExecuted":False,
        "modelMutation":False,"automaticRetry":False,"p3Opened":False,
        "runtimeSecondsScoringOnly":time.monotonic()-started,
      },
      "aggregate":overall,"byPerformer":by_perf,"contentPairMacroF1":pair_macro,
      "absoluteP1P2F1Gap":gap,"criteria":crit,"positiveGate":all(crit.values()),
      "captures":rows,
      "claimBoundary":"Pitch/onset feasibility only; no string/fret, unseen-performer, P3, or customer-readiness claim."
    }
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
