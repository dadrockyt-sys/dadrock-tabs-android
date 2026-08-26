#!/usr/bin/env python3
"""Post-holdout calibration diagnostics for DadRock Rhythm V5.

The professional reference used here is ALREADY CONSUMED and is calibration data,
not an unseen holdout. This tool never edits analyzer output; it emits aggregates
that help distinguish timing/alignment failures from pitch/voicing failures.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
if str(HOLDOUT_DIR) not in sys.path:
    sys.path.insert(0, str(HOLDOUT_DIR))

from canonical import canonical_events  # noqa: E402


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def prf(matched: int, generated: int, reference: int) -> dict[str, Any]:
    precision = 1.0 if generated == 0 else matched / generated
    recall = 1.0 if reference == 0 else matched / reference
    f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return {
        "matched": matched,
        "generated": generated,
        "reference": reference,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def counter_metric(generated: Iterable[Any], reference: Iterable[Any]) -> dict[str, Any]:
    g = Counter(generated)
    r = Counter(reference)
    return prf(sum((g & r).values()), sum(g.values()), sum(r.values()))


def build_reference(source: Mapping[str, Any]) -> list[dict[str, int]]:
    tuning = source.get("tuning")
    measures = source.get("measures")
    if tuning != [64, 59, 55, 50, 45, 40]:
        raise ValueError(f"unexpected calibration tuning {tuning!r}")
    if not isinstance(measures, list) or len(measures) != 113:
        raise ValueError("expected exact 113-measure calibration source")

    notes: list[dict[str, int]] = []
    for measure_number, measure in enumerate(measures, 1):
        for voice in measure.get("voices") or []:
            pos = Fraction(0, 1)
            for beat in voice.get("beats") or []:
                step = max(0, min(15, int(round(float(pos * 16)))))
                for note in beat.get("notes") or []:
                    if not isinstance(note, Mapping):
                        continue
                    if note.get("rest") or note.get("dead") or note.get("tie"):
                        continue
                    string_index = note.get("string")
                    fret = note.get("fret")
                    if (
                        isinstance(string_index, int)
                        and isinstance(fret, int)
                        and 0 <= string_index <= 5
                        and 0 <= fret <= 36
                    ):
                        notes.append(
                            {
                                "measure": measure_number,
                                "step": step,
                                "absStep": (measure_number - 1) * 16 + step,
                                "stringIndex": string_index,
                                "fret": fret,
                                "midi": int(tuning[string_index]) + fret,
                            }
                        )
                duration = beat.get("duration") or [1, 4]
                pos += Fraction(int(duration[0]), int(duration[1]))
    if len(notes) != 946:
        raise ValueError(f"expected 946 calibration notes, got {len(notes)}")
    return notes


def build_generated(stream: Mapping[str, Any]) -> list[dict[str, int]]:
    events = canonical_events(stream.get("events") or [])
    if len(events) != 1209:
        raise ValueError(f"expected frozen V5 1209 events, got {len(events)}")
    result: list[dict[str, int]] = []
    for event in events:
        result.append(
            {
                "measure": int(event["measure"]),
                "step": int(event["step"]),
                "absStep": (int(event["measure"]) - 1) * 16 + int(event["step"]),
                "stringIndex": int(event["stringIndex"]),
                "fret": int(event["fret"]),
                "midi": int(event["midi"]),
            }
        )
    return result


def shifted_timing_metric(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
    step_delta: int,
    semitone_delta: int = 0,
) -> dict[str, Any]:
    return counter_metric(
        ((n["absStep"] + step_delta, n["midi"] + semitone_delta) for n in generated),
        ((n["absStep"], n["midi"]) for n in reference),
    )


def best_shift(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
    low: int,
    high: int,
    *,
    pitch: bool,
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for delta in range(low, high + 1):
        if pitch:
            metric = shifted_timing_metric(generated, reference, delta)
        else:
            metric = counter_metric(
                (n["absStep"] + delta for n in generated),
                (n["absStep"] for n in reference),
            )
        row = {"stepDelta": delta, **metric}
        if best is None or (row["matched"], -abs(delta)) > (best["matched"], -abs(best["stepDelta"])):
            best = row
    assert best is not None
    return best


def best_pitch_shift(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for semitones in range(-24, 25):
        metric = counter_metric(
            (n["midi"] + semitones for n in generated),
            (n["midi"] for n in reference),
        )
        row = {"semitoneDelta": semitones, **metric}
        if best is None or (row["matched"], -abs(semitones)) > (
            best["matched"],
            -abs(best["semitoneDelta"]),
        ):
            best = row
    assert best is not None
    return best


def best_joint_shift(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
) -> dict[str, Any]:
    best: dict[str, Any] | None = None
    for semitones in range(-12, 13):
        for step_delta in range(-64, 65):
            metric = shifted_timing_metric(generated, reference, step_delta, semitones)
            row = {"stepDelta": step_delta, "semitoneDelta": semitones, **metric}
            if best is None or (
                row["matched"],
                -abs(semitones),
                -abs(step_delta),
            ) > (
                best["matched"],
                -abs(best["semitoneDelta"]),
                -abs(best["stepDelta"]),
            ):
                best = row
    assert best is not None
    return best


def segment_alignment(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
) -> list[dict[str, Any]]:
    segments = [(1, 28), (29, 56), (57, 84), (85, 113)]
    rows: list[dict[str, Any]] = []
    for first, last in segments:
        g = [n for n in generated if first <= n["measure"] <= last]
        r = [n for n in reference if first <= n["measure"] <= last]
        rows.append(
            {
                "firstMeasure": first,
                "lastMeasure": last,
                "generatedNotes": len(g),
                "referenceNotes": len(r),
                "bestPitchTimingShift": best_shift(g, r, -32, 32, pitch=True),
                "bestOnsetShift": best_shift(g, r, -32, 32, pitch=False),
            }
        )
    return rows


def measure_density(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
) -> dict[str, Any]:
    g_notes = Counter(n["measure"] for n in generated)
    r_notes = Counter(n["measure"] for n in reference)
    g_onsets = Counter((n["measure"], n["step"]) for n in generated)
    r_onsets = Counter((n["measure"], n["step"]) for n in reference)
    g_onset_measure = Counter(m for m, _ in g_onsets)
    r_onset_measure = Counter(m for m, _ in r_onsets)

    note_rows = []
    onset_rows = []
    for measure in range(1, 114):
        note_rows.append(
            {
                "measure": measure,
                "generated": g_notes[measure],
                "reference": r_notes[measure],
                "delta": g_notes[measure] - r_notes[measure],
            }
        )
        onset_rows.append(
            {
                "measure": measure,
                "generated": g_onset_measure[measure],
                "reference": r_onset_measure[measure],
                "delta": g_onset_measure[measure] - r_onset_measure[measure],
            }
        )

    def summary(rows: Sequence[Mapping[str, int]]) -> dict[str, Any]:
        abs_errors = [abs(row["delta"]) for row in rows]
        return {
            "meanAbsoluteDelta": sum(abs_errors) / len(abs_errors),
            "overGeneratedMeasures": sum(1 for row in rows if row["delta"] > 0),
            "underGeneratedMeasures": sum(1 for row in rows if row["delta"] < 0),
            "exactMeasures": sum(1 for row in rows if row["delta"] == 0),
            "worstMeasures": sorted(rows, key=lambda row: (-abs(row["delta"]), row["measure"]))[:12],
        }

    return {"noteDensity": summary(note_rows), "onsetDensity": summary(onset_rows)}


def pitch_discrepancy(
    generated: Sequence[Mapping[str, int]],
    reference: Sequence[Mapping[str, int]],
) -> dict[str, Any]:
    g = Counter(n["midi"] for n in generated)
    r = Counter(n["midi"] for n in reference)
    rows = [
        {
            "midi": midi,
            "generated": g[midi],
            "reference": r[midi],
            "delta": g[midi] - r[midi],
        }
        for midi in sorted(set(g) | set(r))
    ]
    return {
        "largestAbsoluteDeltas": sorted(rows, key=lambda row: (-abs(row["delta"]), row["midi"]))[:16],
        "generatedMidiRange": [min(g), max(g)],
        "referenceMidiRange": [min(r), max(r)],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("candidate_stream", type=Path)
    parser.add_argument("structured_source", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    generated = build_generated(load_json(args.candidate_stream))
    reference = build_reference(load_json(args.structured_source))

    generated_onsets = sorted(set((n["measure"], n["step"]) for n in generated))
    reference_onsets = sorted(set((n["measure"], n["step"]) for n in reference))

    report = {
        "schemaVersion": 1,
        "classification": "v144-post-holdout-rhythm-calibration-diagnostics",
        "calibrationReferenceUsed": True,
        "unseenHoldout": False,
        "candidateModified": False,
        "modalInvoked": False,
        "productionModified": False,
        "generatedNoteCount": len(generated),
        "referenceNoteCount": len(reference),
        "generatedOnsetCount": len(generated_onsets),
        "referenceOnsetCount": len(reference_onsets),
        "baseline": {
            "pitchContent": counter_metric((n["midi"] for n in generated), (n["midi"] for n in reference)),
            "pitchClassContent": counter_metric((n["midi"] % 12 for n in generated), (n["midi"] % 12 for n in reference)),
            "measurePitch": counter_metric(
                ((n["measure"], n["midi"]) for n in generated),
                ((n["measure"], n["midi"]) for n in reference),
            ),
            "pitchTimingExact": counter_metric(
                ((n["absStep"], n["midi"]) for n in generated),
                ((n["absStep"], n["midi"]) for n in reference),
            ),
            "positionContent": counter_metric(
                ((n["stringIndex"], n["fret"], n["midi"]) for n in generated),
                ((n["stringIndex"], n["fret"], n["midi"]) for n in reference),
            ),
            "positionTimingExact": counter_metric(
                ((n["absStep"], n["stringIndex"], n["fret"], n["midi"]) for n in generated),
                ((n["absStep"], n["stringIndex"], n["fret"], n["midi"]) for n in reference),
            ),
            "onsets": counter_metric(generated_onsets, reference_onsets),
        },
        "alignmentSearch": {
            "bestGlobalPitchTimingStepShift": best_shift(generated, reference, -64, 64, pitch=True),
            "bestGlobalOnsetStepShift": best_shift(generated, reference, -64, 64, pitch=False),
            "bestPitchSemitoneShiftIgnoringTiming": best_pitch_shift(generated, reference),
            "bestJointPitchAndTimingShift": best_joint_shift(generated, reference),
            "quarterSongSegments": segment_alignment(generated, reference),
        },
        "density": measure_density(generated, reference),
        "pitchDiscrepancy": pitch_discrepancy(generated, reference),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
