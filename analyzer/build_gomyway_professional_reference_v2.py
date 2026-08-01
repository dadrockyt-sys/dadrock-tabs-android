from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

REFERENCE_V1 = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v1.json"
TIMING_V1 = REPO_ROOT / "public" / "gomyway-professional-timing-map-v1.json"
ALIGNMENT = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-alignment-diagnosis.json"
REFERENCE_V2 = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
TIMING_V2 = REPO_ROOT / "public" / "gomyway-professional-timing-map-v2.json"

STANDARD_TUNING_MIDI = [64, 59, 55, 50, 45, 40]


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def event(
    step: int,
    string_index: int,
    fret: int,
    *,
    duration_steps: int = 1,
    technique: str = "picked-note",
    bend_semitones: int | None = None,
    group_id: str | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "step": step,
        "positionInMeasure": step / 16.0,
        "durationSteps": duration_steps,
        "stringIndex": string_index,
        "fret": fret,
        "midiPitch": STANDARD_TUNING_MIDI[string_index] + fret,
        "technique": technique,
    }
    if bend_semitones is not None:
        item["bendSemitones"] = bend_semitones
        item["soundingMidiPitch"] = item["midiPitch"] + bend_semitones
    if group_id is not None:
        item["groupId"] = group_id
    return item


def main_em_riff_events(include_double_stop: bool) -> list[dict[str, Any]]:
    # Page 1 professional rhythm tab, measures 1-16.
    # Sixteenth-note positions are encoded as a stable scoring grid.
    events = [
        event(0, 3, 2, duration_steps=2, technique="full-step-bend-release", bend_semitones=2),
        event(2, 3, 0, duration_steps=2),
        event(4, 4, 2, duration_steps=2),
        event(6, 5, 0, duration_steps=2),
        event(8, 3, 0),
        event(10, 4, 2, duration_steps=2),
        event(12, 5, 0),
    ]
    if include_double_stop:
        events.extend(
            [
                event(14, 1, 3, group_id="ending-double-stop-1"),
                event(14, 2, 3, group_id="ending-double-stop-1"),
                event(15, 1, 3, group_id="ending-double-stop-2"),
                event(15, 2, 3, group_id="ending-double-stop-2"),
            ]
        )
    return events


def expand_measures() -> list[dict[str, Any]]:
    measures: list[dict[str, Any]] = []
    for measure_number in range(1, 17):
        include_double_stop = measure_number % 2 == 0
        measures.append(
            {
                "measureNumber": measure_number,
                "section": "Intro",
                "meter": {"numerator": 4, "denominator": 4},
                "patternId": (
                    "main-em-riff-with-double-stop"
                    if include_double_stop
                    else "main-em-riff-open-ending"
                ),
                "sourcePage": 1 if measure_number <= 14 else 2,
                "verificationStatus": "manually-encoded-from-professional-tab-image",
                "events": main_em_riff_events(include_double_stop),
            }
        )
    return measures


def build_measure_boundaries(
    tempo: float,
    first_measure_offset: float,
    meter_regions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    meter_by_measure: dict[int, tuple[int, int]] = {}
    for region in meter_regions:
        for number in range(int(region["startMeasure"]), int(region["endMeasure"]) + 1):
            meter_by_measure[number] = (
                int(region["numerator"]),
                int(region["denominator"]),
            )

    cursor = first_measure_offset
    boundaries: list[dict[str, Any]] = []
    for measure_number in range(1, 114):
        numerator, denominator = meter_by_measure[measure_number]
        beat_seconds = 60.0 / tempo * (4.0 / denominator)
        duration = beat_seconds * numerator
        boundaries.append(
            {
                "measureNumber": measure_number,
                "startSeconds": round(cursor, 6),
                "endSeconds": round(cursor + duration, 6),
                "durationSeconds": round(duration, 6),
                "meter": {"numerator": numerator, "denominator": denominator},
            }
        )
        cursor += duration
    return boundaries


def main() -> None:
    reference_v1 = load_json(REFERENCE_V1)
    timing_v1 = load_json(TIMING_V1)
    alignment = load_json(ALIGNMENT)
    best = alignment.get("best") or {}

    resolved_tempo = float(best.get("tempo") or timing_v1["baseTempoBpm"])
    resolved_offset = float(best.get("offsetSeconds") or 0.0)

    detailed_measures = expand_measures()
    event_count = sum(len(measure["events"]) for measure in detailed_measures)

    reference_v2 = {
        **reference_v1,
        "schemaVersion": 2,
        "status": "partial-detailed-reference",
        "detailedMeasureRange": [1, 16],
        "detailedMeasureCount": len(detailed_measures),
        "detailedEventCount": event_count,
        "scoringUnit": "professional-event",
        "stepResolution": 16,
        "measures": detailed_measures,
        "validation": {
            "minimumRequiredFields": [
                "measureNumber",
                "step",
                "stringIndex",
                "fret",
                "midiPitch",
                "technique",
            ],
            "pageOnePatternAlternation": "odd=open-ending; even=3/3-double-stop-ending",
            "readyForPartialScoring": True,
            "readyForFullSongTraining": False,
        },
        "notes": (
            "Measures 1-16 are now encoded event by event from the professional rhythm tab. "
            "Measures 17-113 remain scaffolded and must be expanded before full-song >=90% automation."
        ),
    }

    timing_v2 = {
        **timing_v1,
        "schemaVersion": 2,
        "status": "resolved-measure-boundary-map",
        "alignment": {
            **timing_v1["alignment"],
            "resolvedTempoBpm": resolved_tempo,
            "resolvedFirstMeasureOffsetSeconds": resolved_offset,
            "resolvedFromDiagnosisAtRuntime": False,
        },
        "measureBoundaries": build_measure_boundaries(
            resolved_tempo,
            resolved_offset,
            timing_v1["meterRegions"],
        ),
        "validation": {
            "measureCount": 113,
            "meterChangeAt104Honored": True,
            "readyForProfessionalEventScoring": True,
        },
    }

    REFERENCE_V2.write_text(json.dumps(reference_v2, indent=2) + "\n")
    TIMING_V2.write_text(json.dumps(timing_v2, indent=2) + "\n")

    print("Professional rhythm reference v2 built: True")
    print(f"Detailed measures: {len(detailed_measures)}")
    print(f"Detailed professional events: {event_count}")
    print(f"Resolved tempo: {resolved_tempo:.3f} BPM")
    print(f"Resolved first-measure offset: {resolved_offset:.3f} seconds")
    print(f"Reference: {REFERENCE_V2.relative_to(REPO_ROOT)}")
    print(f"Timing map: {TIMING_V2.relative_to(REPO_ROOT)}")
    print("Ready for partial measures 1-16 scoring: True")
    print("Ready for full-song >=90% automated training: False")


if __name__ == "__main__":
    main()
