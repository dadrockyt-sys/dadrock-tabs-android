#!/usr/bin/env python3
"""V167 single-song calibration diagnostic.

This tool is intentionally reference-facing. V167 is a labeled training/calibration
lane, not a holdout experiment. It never writes corrections into a candidate.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Mapping, Sequence


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_frozen_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def nearest_reference(note: Mapping[str, Any], refs: Sequence[Mapping[str, Any]], *, step_limit: float = 0.5):
    candidates = []
    for idx, ref in enumerate(refs):
        if int(ref["measure"]) != int(note["measure"]):
            continue
        step_delta = abs(float(ref["step"]) - float(note["step"]))
        if step_delta > step_limit:
            continue
        midi_delta = int(note["midi"]) - int(ref["midi"])
        candidates.append((step_delta, abs(midi_delta), midi_delta, idx, ref))
    if not candidates:
        return None
    candidates.sort(key=lambda row: (row[0], row[1], row[2], row[3]))
    return candidates[0]


def classify_unmatched_generated(note: Mapping[str, Any], refs: Sequence[Mapping[str, Any]]) -> str:
    near = nearest_reference(note, refs)
    if near is None:
        return "noReferenceEventWithinHalfStepSameMeasure"
    _, _, midi_delta, _, ref = near
    if midi_delta == 0:
        return "samePitchLocalCollisionOrDuplicate"
    if midi_delta % 12 == 0:
        return "octaveOrRegisterError"
    if int(note["midi"]) % 12 == int(ref["midi"]) % 12:
        return "samePitchClassRegisterError"
    if abs(midi_delta) <= 2:
        return "nearSemitonePitchError"
    return "otherPitchErrorNearCorrectTime"


def classify_unmatched_reference(note: Mapping[str, Any], generated: Sequence[Mapping[str, Any]]) -> str:
    near = nearest_reference(note, generated)
    if near is None:
        return "noGeneratedEventWithinHalfStepSameMeasure"
    _, _, midi_delta, _, gen = near
    # nearest_reference computes note.midi - candidate.midi; sign is irrelevant here.
    if midi_delta == 0:
        return "samePitchLocalCollisionOrDuplicate"
    if midi_delta % 12 == 0:
        return "octaveOrRegisterError"
    if int(note["midi"]) % 12 == int(gen["midi"]) % 12:
        return "samePitchClassRegisterError"
    if abs(midi_delta) <= 2:
        return "nearSemitonePitchError"
    return "otherPitchErrorNearCorrectTime"


def top_counter(counter: Counter, limit: int = 20):
    return [{"key": str(key), "count": count} for key, count in counter.most_common(limit)]


def stream_diagnostic(scorer, generated, reference):
    primary_pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.STEP_TOLERANCE)
    gross_pairs = scorer.optimal_one_to_one_match(generated, reference, scorer.GROSS_STEP_TOLERANCE)
    primary_g = {g for g, _, _ in primary_pairs}
    primary_r = {r for _, r, _ in primary_pairs}
    gross_g = {g for g, _, _ in gross_pairs}
    gross_r = {r for _, r, _ in gross_pairs}

    unmatched_g = [i for i in range(len(generated)) if i not in primary_g]
    unmatched_r = [i for i in range(len(reference)) if i not in primary_r]

    gen_classes = Counter(classify_unmatched_generated(generated[i], reference) for i in unmatched_g)
    ref_classes = Counter(classify_unmatched_reference(reference[i], generated) for i in unmatched_r)

    primary_deltas = [delta for _, _, delta in primary_pairs]
    gross_only = [(g, r, d) for g, r, d in gross_pairs if g not in primary_g and r not in primary_r]

    fp_by_measure = Counter(int(generated[i]["measure"]) for i in unmatched_g)
    fn_by_measure = Counter(int(reference[i]["measure"]) for i in unmatched_r)
    generated_midi = Counter(int(n["midi"]) for n in generated)
    reference_midi = Counter(int(n["midi"]) for n in reference)

    measures = sorted(set(fp_by_measure) | set(fn_by_measure))
    measure_rows = [
        {
            "measure": m,
            "falsePositive": fp_by_measure[m],
            "falseNegative": fn_by_measure[m],
            "totalErrors": fp_by_measure[m] + fn_by_measure[m],
        }
        for m in measures
    ]
    measure_rows.sort(key=lambda row: (-row["totalErrors"], row["measure"]))

    exact_measure_pitch = scorer.pitch_content_diagnostic(generated, reference)
    return {
        "counts": {"generated": len(generated), "reference": len(reference)},
        "primary": scorer.prf(len(primary_pairs), len(generated), len(reference)),
        "gross": scorer.prf(len(gross_pairs), len(generated), len(reference)),
        "pitchContentByMeasure": exact_measure_pitch,
        "matchedTiming": {
            "primaryPairCount": len(primary_pairs),
            "grossPairCount": len(gross_pairs),
            "grossOnlySamePitchTimingDriftCount": len(gross_only),
            "primaryMedianAbsStepDelta": scorer.percentile(primary_deltas, 0.50),
            "primaryP90AbsStepDelta": scorer.percentile(primary_deltas, 0.90),
            "primaryMaxAbsStepDelta": max(primary_deltas) if primary_deltas else None,
        },
        "falsePositiveBuckets": dict(sorted(gen_classes.items())),
        "falseNegativeBuckets": dict(sorted(ref_classes.items())),
        "topErrorMeasures": measure_rows[:20],
        "topGeneratedMidi": top_counter(generated_midi),
        "topReferenceMidi": top_counter(reference_midi),
        "calibrationInterpretation": {
            "samePitchGrossTimingDrift": "same MIDI can match within 2 grid steps but not within the primary 0.5-step tolerance",
            "octaveOrRegisterError": "near-correct onset has a pitch separated by one or more octaves",
            "nearSemitonePitchError": "near-correct onset is within two semitones of nearest reference event",
            "noNearbyEvent": "no event exists within 0.5 grid step in the same measure; likely miss/extra, timebase displacement, or larger onset error"
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer", type=Path, required=True)
    ap.add_argument("--score-output", type=Path, required=True)
    ap.add_argument("--diagnostic-output", type=Path, required=True)
    args = ap.parse_args()

    for path in (args.score_output, args.diagnostic_output):
        if path.exists():
            raise RuntimeError(f"output already exists: {path}")

    subprocess.run(
        [sys.executable, str(args.scorer), str(args.candidate), str(args.reference), "--output", str(args.score_output)],
        check=True,
    )
    scorer = load_module(args.scorer)
    generated_payload = scorer.load_json(args.candidate)
    reference_payload = scorer.load_json(args.reference)
    generated_guitar, generated_bass = scorer.load_generated(generated_payload)
    reference_guitar, reference_bass, reference_counts = scorer.load_reference(reference_payload)
    score = scorer.load_json(args.score_output)

    report = {
        "schema": "dadrock.tabs.v167.single-song-calibration-diagnostic.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "candidate": str(args.candidate),
        "reference": str(args.reference),
        "scorer": str(args.scorer),
        "referenceCounts": reference_counts,
        "recognitionPercent": {
            "combinedGuitar": score["combinedGuitar"]["primaryTimingAwarePitch"]["f1"] * 100.0,
            "bass": score["bass"]["primaryTimingAwarePitch"]["f1"] * 100.0,
        },
        "combinedGuitar": stream_diagnostic(scorer, generated_guitar, reference_guitar),
        "bass": stream_diagnostic(scorer, generated_bass, reference_bass),
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "writesCandidateCorrections": False,
            "directReferenceCopyForbidden": True,
            "generalizationClaimForbidden": True,
        },
    }
    args.diagnostic_output.parent.mkdir(parents=True, exist_ok=True)
    args.diagnostic_output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
