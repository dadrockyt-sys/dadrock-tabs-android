#!/usr/bin/env python3
"""Apply V167 calibration iteration 1: shared global grid phase -12.

This transform is deliberately simple and auditable. It starts from the immutable
V166 candidate, shifts every musical event dictionary that carries
absoluteGridStep/measure/step/midi by one shared integer offset, recomputes
measure/step from the fixed 16-step lattice, and preserves every other field.
No professional-reference event is read by this transform.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

STEPS_PER_MEASURE = 16


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_musical_event(value: Any) -> bool:
    return isinstance(value, dict) and all(
        key in value for key in ("absoluteGridStep", "measure", "step", "midi")
    )


def shift_event(event: dict[str, Any], shift: int) -> dict[str, Any]:
    old_abs = int(event["absoluteGridStep"])
    expected_abs = (int(event["measure"]) - 1) * STEPS_PER_MEASURE + int(event["step"])
    if expected_abs != old_abs:
        raise ValueError(
            f"event coordinate invariant failed before transform: abs={old_abs}, "
            f"measure={event['measure']}, step={event['step']}, expected={expected_abs}"
        )
    new_abs = old_abs + shift
    if new_abs < 0:
        raise ValueError(f"global shift would create negative grid step: {old_abs} + {shift}")
    out = dict(event)
    out["absoluteGridStep"] = new_abs
    out["measure"] = new_abs // STEPS_PER_MEASURE + 1
    out["step"] = new_abs % STEPS_PER_MEASURE
    if int(out["midi"]) != int(event["midi"]):
        raise AssertionError("MIDI changed unexpectedly")
    return out


def transform_tree(value: Any, shift: int, stats: dict[str, int]) -> Any:
    if is_musical_event(value):
        stats["eventDictionariesShifted"] += 1
        return shift_event(value, shift)
    if isinstance(value, dict):
        return {key: transform_tree(child, shift, stats) for key, child in value.items()}
    if isinstance(value, list):
        return [transform_tree(child, shift, stats) for child in value]
    return copy.deepcopy(value)


def scored_stream_counts(payload: dict[str, Any]) -> dict[str, int]:
    streams = payload.get("streams") or {}
    guitar = streams.get("combinedGuitar")
    bass = streams.get("bass")
    if not isinstance(guitar, list) or not isinstance(bass, list):
        raise ValueError("candidate missing scored streams")
    return {"combinedGuitar": len(guitar), "bass": len(bass)}


def scored_stream_midis(payload: dict[str, Any]) -> dict[str, list[int]]:
    streams = payload["streams"]
    return {
        "combinedGuitar": [int(row["midi"]) for row in streams["combinedGuitar"]],
        "bass": [int(row["midi"]) for row in streams["bass"]],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--shift", type=int, required=True)
    ap.add_argument("--source-blob", required=True)
    ap.add_argument("--phase-sweep-blob", required=True)
    args = ap.parse_args()

    if args.output.exists():
        raise RuntimeError(f"output already exists: {args.output}")
    if args.shift != -12:
        raise ValueError("V167 iteration 1 is pinned to the frozen shared optimum shift -12")

    source = json.loads(args.input.read_text(encoding="utf-8"))
    if source.get("version") != "V166":
        raise ValueError("iteration 1 input must be V166")
    before_counts = scored_stream_counts(source)
    before_midis = scored_stream_midis(source)

    stats = {"eventDictionariesShifted": 0}
    output = transform_tree(source, args.shift, stats)
    after_counts = scored_stream_counts(output)
    after_midis = scored_stream_midis(output)

    if after_counts != before_counts:
        raise AssertionError(f"scored stream counts changed: {before_counts} -> {after_counts}")
    if after_midis != before_midis:
        raise AssertionError("scored-stream MIDI sequence changed")
    if stats["eventDictionariesShifted"] < sum(before_counts.values()):
        raise AssertionError("fewer event dictionaries shifted than scored stream events")

    # Preserve the frozen scorer's safety contract while making calibration identity explicit.
    safety = output.get("safety") or {}
    if safety.get("referenceRead") is not False or safety.get("humanCorrection") is not False:
        raise ValueError("source candidate safety boundary is not scorer-compatible")

    output["schema"] = "dadrock.tabs.v167.single-song-calibrated-generated.v1"
    output["version"] = "V167"
    output["status"] = "CALIBRATION_ITERATION_001_GLOBAL_PHASE_APPLIED"
    output["calibration"] = {
        "label": "SINGLE_SONG_TRAINING_CALIBRATION",
        "iteration": 1,
        "parentVersion": "V166",
        "parentCandidateGitBlob": args.source_blob,
        "parentCandidateSha256": sha256(args.input),
        "phaseSweepGitBlob": args.phase_sweep_blob,
        "transform": {
            "name": "shared_absolute_grid_phase",
            "shiftGridSteps": args.shift,
            "stepsPerMeasure": STEPS_PER_MEASURE,
            "midiChanged": False,
            "scoredEventCardinalityChanged": False,
            "eventDictionariesShifted": stats["eventDictionariesShifted"],
        },
        "scoredStreamCountsBefore": before_counts,
        "scoredStreamCountsAfter": after_counts,
        "professionalReferenceReadByTransform": False,
        "directReferenceEventCopy": False,
        "humanCorrection": False,
        "generalizationClaim": False,
    }

    # Final coordinate audit on scored streams.
    for stream_name in ("combinedGuitar", "bass"):
        for row in output["streams"][stream_name]:
            absolute = int(row["absoluteGridStep"])
            if (int(row["measure"]) - 1) * STEPS_PER_MEASURE + int(row["step"]) != absolute:
                raise AssertionError(f"post-transform coordinate invariant failed in {stream_name}")
            if absolute < 0:
                raise AssertionError("negative absoluteGridStep after transform")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "shiftGridSteps": args.shift,
        "scoredStreamCounts": after_counts,
        "eventDictionariesShifted": stats["eventDictionariesShifted"],
        "outputSha256": sha256(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
