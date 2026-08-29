#!/usr/bin/env python3
"""Read-only V167 absolute-grid phase sweep.

The frozen V166 candidate is never modified. For each integer absolute-grid shift,
this diagnostic moves only event measure/step coordinates in memory, preserves MIDI
and event cardinality, and scores against the frozen professional reference.
V167 is explicitly a single-song calibration lane, so reference-guided parameter
selection is permitted and must not be presented as holdout/generalization.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

STEPS_PER_MEASURE = 16


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("v167_phase_scorer", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scorer: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def shift_events(events: Sequence[Mapping[str, Any]], shift: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for note in events:
        absolute = (int(note["measure"]) - 1) * STEPS_PER_MEASURE + int(note["step"])
        moved = absolute + shift
        if moved < 0:
            # The calibration song's generated events begin well after zero, but keep
            # this deterministic and explicit if a future input reaches the boundary.
            continue
        clone = dict(note)
        clone["measure"] = moved // STEPS_PER_MEASURE + 1
        clone["step"] = moved % STEPS_PER_MEASURE
        out.append(clone)
    return out


def score_stream(scorer, generated, reference, tolerance: float):
    pairs = scorer.optimal_one_to_one_match(generated, reference, tolerance)
    return scorer.prf(len(pairs), len(generated), len(reference))


def sweep_stream(scorer, generated, reference, lo: int, hi: int):
    rows = []
    for shift in range(lo, hi + 1):
        shifted = shift_events(generated, shift)
        primary = score_stream(scorer, shifted, reference, scorer.STEP_TOLERANCE)
        gross = score_stream(scorer, shifted, reference, scorer.GROSS_STEP_TOLERANCE)
        rows.append({
            "shiftGridSteps": shift,
            "primary": primary,
            "gross": gross,
            "generatedCountAfterShift": len(shifted),
        })
    best = max(rows, key=lambda row: (row["primary"]["f1"], row["primary"]["matched"], -abs(row["shiftGridSteps"]), -row["shiftGridSteps"]))
    baseline = next(row for row in rows if row["shiftGridSteps"] == 0)
    return {
        "baseline": baseline,
        "best": best,
        "deltaF1": best["primary"]["f1"] - baseline["primary"]["f1"],
        "deltaRecognitionPercent": (best["primary"]["f1"] - baseline["primary"]["f1"]) * 100.0,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--reference", type=Path, required=True)
    ap.add_argument("--scorer", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--min-shift", type=int, default=-16)
    ap.add_argument("--max-shift", type=int, default=16)
    args = ap.parse_args()
    if args.output.exists():
        raise RuntimeError(f"output already exists: {args.output}")
    if args.min_shift > 0 or args.max_shift < 0 or args.min_shift > args.max_shift:
        raise RuntimeError("sweep must include zero and have min <= max")

    scorer = load_module(args.scorer)
    generated_payload = scorer.load_json(args.candidate)
    reference_payload = scorer.load_json(args.reference)
    guitar, bass = scorer.load_generated(generated_payload)
    ref_guitar, ref_bass, ref_counts = scorer.load_reference(reference_payload)

    report = {
        "schema": "dadrock.tabs.v167.absolute-grid-phase-sweep.v1",
        "version": "V167",
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "stepsPerMeasure": STEPS_PER_MEASURE,
        "sweep": {"minShift": args.min_shift, "maxShift": args.max_shift, "unit": "absoluteGridStep"},
        "referenceCounts": ref_counts,
        "combinedGuitar": sweep_stream(scorer, guitar, ref_guitar, args.min_shift, args.max_shift),
        "bass": sweep_stream(scorer, bass, ref_bass, args.min_shift, args.max_shift),
        "policy": {
            "referenceFacing": True,
            "calibrationOnly": True,
            "candidateFileModified": False,
            "midiModified": False,
            "eventCardinalityIntentionallyModified": False,
            "directReferenceCopy": False,
            "generalizationClaim": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "combinedGuitar": {"baseline": report["combinedGuitar"]["baseline"]["primary"], "best": report["combinedGuitar"]["best"]},
        "bass": {"baseline": report["bass"]["baseline"]["primary"], "best": report["bass"]["best"]},
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
