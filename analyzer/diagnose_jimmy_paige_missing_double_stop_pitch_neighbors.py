from __future__ import annotations

import json
from collections import Counter
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-missing-double-stop-pitch-neighbors.json"

MISSED_MEASURES = [6, 8, 12, 14, 16]
FALSE_POSITIVE_MEASURES = [5, 9]
TARGET_PITCHES = {58, 62}
NEIGHBOR_PITCHES = set(range(55, 65))
ZONE_START_FRACTION = 0.55
ZONE_END_FRACTION = 1.12


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _end(event: dict[str, Any]) -> float:
    for key in ("end", "end_time", "endTime"):
        if event.get(key) is not None:
            return float(event[key])
    duration = float(event.get("duration", event.get("duration_seconds", 0.0)) or 0.0)
    return _start(event) + duration


def _zone(measure: int, bounds: dict[int, tuple[float, float]]) -> tuple[float, float]:
    start, end = bounds[measure]
    duration = end - start
    return (
        start + duration * ZONE_START_FRACTION,
        start + duration * ZONE_END_FRACTION,
    )


def _events_in_zone(
    events: list[dict[str, Any]],
    zone: tuple[float, float],
) -> list[dict[str, Any]]:
    start, end = zone
    return [
        event
        for event in events
        if _start(event) <= end and _end(event) >= start
    ]


def _summarize_measure(
    measure: int,
    events: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
) -> dict[str, Any]:
    zone = _zone(measure, bounds)
    nearby = _events_in_zone(events, zone)
    pitch_counts = Counter(
        int(event.get("midiPitch", -999))
        for event in nearby
        if event.get("midiPitch") is not None
    )

    neighbor_events = []
    for event in nearby:
        pitch = int(event.get("midiPitch", -999))
        if pitch not in NEIGHBOR_PITCHES:
            continue
        neighbor_events.append(
            {
                "midiPitch": pitch,
                "start": round(_start(event), 6),
                "end": round(_end(event), 6),
                "duration": round(max(0.0, _end(event) - _start(event)), 6),
                "confidence": event.get("confidence"),
            }
        )

    neighbor_events.sort(key=lambda item: (item["start"], item["midiPitch"]))

    closest_to_58 = sorted(
        neighbor_events,
        key=lambda item: (abs(item["midiPitch"] - 58), item["start"]),
    )[:6]
    closest_to_62 = sorted(
        neighbor_events,
        key=lambda item: (abs(item["midiPitch"] - 62), item["start"]),
    )[:6]

    return {
        "measureNumber": measure,
        "zoneStartSeconds": round(zone[0], 6),
        "zoneEndSeconds": round(zone[1], 6),
        "targetPitchCounts": {
            "58": pitch_counts.get(58, 0),
            "62": pitch_counts.get(62, 0),
        },
        "neighborPitchCounts": {
            str(pitch): pitch_counts.get(pitch, 0)
            for pitch in sorted(NEIGHBOR_PITCHES)
            if pitch_counts.get(pitch, 0)
        },
        "closestTo58": closest_to_58,
        "closestTo62": closest_to_62,
        "neighborEvents": neighbor_events,
    }


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    missed = [
        _summarize_measure(measure, events, bounds)
        for measure in MISSED_MEASURES
    ]
    false_positive = [
        _summarize_measure(measure, events, bounds)
        for measure in FALSE_POSITIVE_MEASURES
    ]

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "missing-double-stop-pitch-neighbor-diagnosis",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "targetPitches": sorted(TARGET_PITCHES),
        "neighborPitchRange": [min(NEIGHBOR_PITCHES), max(NEIGHBOR_PITCHES)],
        "zoneFraction": [ZONE_START_FRACTION, ZONE_END_FRACTION],
        "missedProfessionalMeasures": missed,
        "falsePositiveOddMeasures": false_positive,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protected93_06CheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Missing double-stop pitch-neighbor diagnosis")
    for item in missed:
        print(
            f"MISS measure {item['measureNumber']:>2} | "
            f"targets={item['targetPitchCounts']} | "
            f"neighbors={item['neighborPitchCounts']}"
        )
    for item in false_positive:
        print(
            f"FALSE POSITIVE measure {item['measureNumber']:>2} | "
            f"targets={item['targetPitchCounts']} | "
            f"neighbors={item['neighborPitchCounts']}"
        )

    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
