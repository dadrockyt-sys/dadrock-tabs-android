"""Cross-Stem Transcription Overlap / Role Ambiguity Diagnostic V1.

Descriptive-only S0 diagnostic. Untouched raw guitar and bass separator outputs are
independently transcribed with the frozen Basic Pitch configuration, then their
note-event streams are compared.

No thresholds are fitted. No audio is merged, muted, reassigned, cleaned, or
otherwise modified.
"""
from __future__ import annotations

import argparse
import json
import math
import tempfile
import time
from pathlib import Path

import numpy as np

from bs_roformer_sw_6stem_adapter_v1 import BsRoformer6StemOnnxAdapter, FP16_SHA256
import soundfile as sf

from stem_bleed_diagnostics_v1 import DiagnosticConfig, diagnose_stems
from evaluate_s0_transcription_failure_attribution_v1 import run_probe
from pretrained_note_front_end_v1 import (
    BASIC_PITCH_VERSION,
    FRAME_THRESHOLD,
    MIN_NOTE_LENGTH_MS,
    ONSET_THRESHOLD,
    basic_pitch_model_identity,
)

ONSET_TOLERANCE_SECONDS = 0.05


def load(path):
    return sf.read(path, always_2d=True, dtype="float32")


def truth_presence(directory):
    return {
        p.stem.split("_", 1)[1]
        for p in directory.glob("*.wav")
        if not p.name.endswith("_mix.wav")
    }


def energy(x):
    return float(np.mean(np.asarray(x, dtype=np.float64) ** 2))


def _candidate_pairs(a, b, predicate):
    out=[]
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            dt=abs(float(x["start"])-float(y["start"]))
            if dt <= ONSET_TOLERANCE_SECONDS and predicate(x,y):
                out.append((dt,i,j))
    return out


def _one_to_one(a,b,predicate):
    used_a=set(); used_b=set(); matches=[]
    for dt,i,j in sorted(_candidate_pairs(a,b,predicate), key=lambda z:(z[0],z[1],z[2])):
        if i in used_a or j in used_b:
            continue
        used_a.add(i); used_b.add(j)
        matches.append((i,j,dt))
    return matches


def _metrics(a,b,predicate):
    matches=_one_to_one(a,b,predicate)
    n=len(matches)
    na=len(a); nb=len(b)
    precision=n/na if na else None
    recall=n/nb if nb else None
    f1=(2*n/(na+nb)) if (na+nb) else None
    return {
        "matchCount":n,
        "guitarCoverage":n/na if na else None,
        "bassCoverage":n/nb if nb else None,
        "symmetricF1":f1,
        "jaccard":n/(na+nb-n) if (na+nb-n)>0 else None,
        "meanAbsoluteOnsetDifferenceSeconds":(
            float(np.mean([m[2] for m in matches])) if matches else None
        ),
    }


def _event_density_balance(a,b,duration):
    ga=len(a)/max(duration,1e-12)
    ba=len(b)/max(duration,1e-12)
    hi=max(ga,ba)
    return {
        "guitarEvents":len(a),
        "bassEvents":len(b),
        "guitarEventsPerSecond":ga,
        "bassEventsPerSecond":ba,
        "minMaxDensityRatio":min(ga,ba)/hi if hi>0 else 1.0,
        "absoluteDensityDifferencePerSecond":abs(ga-ba),
    }


def _safe_z(value, values):
    arr=np.asarray(values,dtype=np.float64)
    sd=float(np.std(arr))
    return None if sd<=1e-12 else float((value-float(np.mean(arr)))/sd)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--s0-root",required=True)
    ap.add_argument("--model",required=True)
    ap.add_argument("--output-json",required=True)
    args=ap.parse_args()

    bp=basic_pitch_model_identity()
    if bp["packageVersion"] != BASIC_PITCH_VERSION:
        raise RuntimeError("Basic Pitch version mismatch")
    if bp["modelSha256"] != "3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676":
        raise RuntimeError("Basic Pitch model SHA mismatch")

    sep=BsRoformer6StemOnnxAdapter(Path(args.model))
    diag_cfg=DiagnosticConfig()
    rows=[]

    prior_path=Path("docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json")
    prior=json.loads(prior_path.read_text())
    prior_duplicate_fixture=prior["keyFixture"]
    if prior_duplicate_fixture != "S0M10" or prior["duplicateCandidateCount"] != 1:
        raise RuntimeError("prior frozen duplicate-class context mismatch")
    started=time.perf_counter()

    with tempfile.TemporaryDirectory(prefix="astra_cross_stem_overlap_") as td:
        td=Path(td)
        for directory in sorted(Path(args.s0_root).glob("S0M*")):
            mixes=list(directory.glob("*_mix.wav"))
            if len(mixes)!=1:
                continue
            mix,fs=load(mixes[0])
            presence=truth_presence(directory)
            raw=sep.separate_array(mix,fs)
            diagnostics=diagnose_stems(mix,raw,fs,diag_cfg)

            guitar_events=run_probe(
                raw["guitar"],fs,td/f"{directory.name}_guitar.wav",
                f"{directory.name}:guitar"
            )
            bass_events=run_probe(
                raw["bass"],fs,td/f"{directory.name}_bass.wav",
                f"{directory.name}:bass"
            )
            duration=len(mix)/float(fs)

            exact=_metrics(
                guitar_events,bass_events,
                lambda x,y: int(x["midi"])==int(y["midi"])
            )
            pitch_class=_metrics(
                guitar_events,bass_events,
                lambda x,y: int(x["midi"])%12==int(y["midi"])%12
            )
            octave=_metrics(
                guitar_events,bass_events,
                lambda x,y: (
                    int(x["midi"]) != int(y["midi"])
                    and abs(int(x["midi"])-int(y["midi"]))>=12
                    and abs(int(x["midi"])-int(y["midi"]))%12==0
                )
            )
            onset_any=_metrics(guitar_events,bass_events,lambda x,y: True)

            row={
                "id":directory.name,
                "truthPresence":{
                    "guitar":"guitar" in presence,
                    "bass":"bass" in presence,
                },
                "priorFrozenPairContext":{
                    "duplicateCandidateReported": directory.name == prior_duplicate_fixture,
                    "reportedState": (
                        "duplicate_bass_candidate"
                        if directory.name == prior_duplicate_fixture else None
                    ),
                    "sourceRecord":"docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json",
                },
                "stemEnergy":{
                    "guitar":energy(raw["guitar"]),
                    "bass":energy(raw["bass"]),
                },
                "exactMidiOnsetOverlap":exact,
                "pitchClassOnsetOverlap":pitch_class,
                "octaveRelatedOnsetOverlap":octave,
                "anyPitchOnsetCoincidence":onset_any,
                "eventDensityBalance":_event_density_balance(
                    guitar_events,bass_events,duration
                ),
            }
            rows.append(row)

    both_present=[
        r for r in rows
        if r["truthPresence"]["guitar"] and r["truthPresence"]["bass"]
    ]
    ordinary=[
        r for r in both_present
        if r["id"]!="S0M10"
    ]
    target=next((r for r in rows if r["id"]=="S0M10"),None)

    metric_paths={
        "exactMidiF1":lambda r:r["exactMidiOnsetOverlap"]["symmetricF1"],
        "pitchClassF1":lambda r:r["pitchClassOnsetOverlap"]["symmetricF1"],
        "octaveRelatedF1":lambda r:r["octaveRelatedOnsetOverlap"]["symmetricF1"],
        "anyPitchOnsetCoincidenceF1":lambda r:r["anyPitchOnsetCoincidence"]["symmetricF1"],
        "eventDensityBalance":lambda r:r["eventDensityBalance"]["minMaxDensityRatio"],
    }

    comparison={}
    if target is not None:
        for name,getter in metric_paths.items():
            tv=getter(target)
            vals=[getter(r) for r in ordinary if getter(r) is not None]
            vals=[float(v) for v in vals if math.isfinite(float(v))]
            sorted_desc=sorted(
                [(r["id"],float(getter(r))) for r in ordinary if getter(r) is not None]
                + [(target["id"],float(tv))],
                key=lambda x:x[1], reverse=True
            )
            comparison[name]={
                "s0m10Value":tv,
                "ordinaryBothPresentCount":len(vals),
                "ordinaryMean":float(np.mean(vals)) if vals else None,
                "ordinaryMedian":float(np.median(vals)) if vals else None,
                "ordinaryMin":float(np.min(vals)) if vals else None,
                "ordinaryMax":float(np.max(vals)) if vals else None,
                "s0m10ZVsOrdinary":_safe_z(float(tv),vals) if vals else None,
                "descendingRankIncludingS0M10":(
                    next(i+1 for i,x in enumerate(sorted_desc) if x[0]=="S0M10")
                    if sorted_desc else None
                ),
                "rankedValues":sorted_desc,
            }

    result={
        "schemaVersion":1,
        "kind":"s0-cross-stem-transcription-overlap-role-ambiguity-v1",
        "descriptiveOnly":True,
        "thresholdFitPerformed":False,
        "automaticRoleDecisionDefined":False,
        "audioMutation":False,
        "separatorModelSha256":FP16_SHA256,
        "transcriber":{
            "name":"Basic Pitch",
            "packageVersion":BASIC_PITCH_VERSION,
            "modelSha256":bp["modelSha256"],
            "onsetThreshold":ONSET_THRESHOLD,
            "frameThreshold":FRAME_THRESHOLD,
            "minimumNoteLengthMs":MIN_NOTE_LENGTH_MS,
            "onsetToleranceSeconds":ONSET_TOLERANCE_SECONDS,
        },
        "priorFrozenPairContext":{
            "sourceRecord":"docs/astra/DUPLICATE_CLASS_ACTION_RESULT_V1.json",
            "duplicateCandidateCount":prior["duplicateCandidateCount"],
            "keyFixture":prior_duplicate_fixture,
            "reportedStateForKeyFixture":"duplicate_bass_candidate",
        },
        "mixtureCount":len(rows),
        "s0m10VsOrdinaryBothPresent":comparison,
        "results":rows,
        "totalWallSeconds":time.perf_counter()-started,
        "interpretationBoundary":(
            "S0 synthetic descriptive analysis only. No overlap cutoff, role reassignment, "
            "stem mutation, or production action is authorized from these same fixtures."
        ),
    }
    Path(args.output_json).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
