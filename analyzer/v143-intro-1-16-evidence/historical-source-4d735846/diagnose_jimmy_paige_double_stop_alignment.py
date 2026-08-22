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
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-double-stop-alignment-diagnosis.json"

TARGET_PITCHES = {58, 62}
SEARCH_RADIUS_SECONDS = 0.90
PAIR_MAX_SEPARATION_SECONDS = 0.18


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _target_time(measure: int, step: int, bounds: dict[int, tuple[float, float]]) -> float:
    begin, end = bounds[measure]
    return begin + (end - begin) * (step / 16.0)


def _nearest_pitch_event(
    events: list[dict[str, Any]],
    pitch: int,
    target: float,
) -> dict[str, Any] | None:
    candidates = [event for event in events if int(event.get("midiPitch", -999)) == pitch]
    if not candidates:
        return None
    event = min(candidates, key=lambda item: abs(_start(item) - target))
    return {
        "pitch": pitch,
        "start": round(_start(event), 6),
        "deltaSeconds": round(_start(event) - target, 6),
        "confidence": event.get("confidence"),
    }


def _best_pair(
    events: list[dict[str, Any]],
    target: float,
) -> dict[str, Any] | None:
    nearby = [
        event
        for event in events
        if abs(_start(event) - target) <= SEARCH_RADIUS_SECONDS
        and int(event.get("midiPitch", -999)) in TARGET_PITCHES
    ]
    pitch_58 = [event for event in nearby if int(event.get("midiPitch", -999)) == 58]
    pitch_62 = [event for event in nearby if int(event.get("midiPitch", -999)) == 62]

    best: tuple[float, float, dict[str, Any], dict[str, Any]] | None = None
    for first in pitch_58:
        for second in pitch_62:
            separation = abs(_start(first) - _start(second))
            center = (_start(first) + _start(second)) / 2.0
            distance = abs(center - target)
            candidate = (separation, distance, first, second)
            if best is None or candidate[:2] < best[:2]:
                best = candidate

    if best is None:
        return None

    separation, distance, first, second = best
    center = (_start(first) + _start(second)) / 2.0
    return {
        "pitch58Start": round(_start(first), 6),
        "pitch62Start": round(_start(second), 6),
        "separationSeconds": round(separation, 6),
        "pairCenterSeconds": round(center, 6),
        "pairCenterDeltaSeconds": round(center - target, 6),
        "within180ms": separation <= PAIR_MAX_SEPARATION_SECONDS,
        "distanceFromTargetSeconds": round(distance, 6),
    }


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    reports: list[dict[str, Any]] = []
    pair_center_deltas: list[float] = []
    separations: list[float] = []

    for measure in range(2, 17, 2):
        for step in (14, 15):
            target = _target_time(measure, step, bounds)
            nearby = [
                event
                for event in events
                if abs(_start(event) - target) <= SEARCH_RADIUS_SECONDS
            ]
            nearby_pitch_counts = Counter(
                int(event.get("midiPitch", -999)) for event in nearby
            )
            pair = _best_pair(events, target)
            if pair is not None:
                pair_center_deltas.append(float(pair["pairCenterDeltaSeconds"]))
                separations.append(float(pair["separationSeconds"]))

            reports.append(
                {
                    "measureNumber": measure,
                    "step": step,
                    "targetSeconds": round(target, 6),
                    "nearest58": _nearest_pitch_event(events, 58, target),
                    "nearest62": _nearest_pitch_event(events, 62, target),
                    "best58_62Pair": pair,
                    "nearbyPitchCounts": {
                        str(pitch): count
                        for pitch, count in sorted(nearby_pitch_counts.items())
                    },
                }
            )

    sorted_deltas = sorted(pair_center_deltas)
    median_delta = (
        sorted_deltas[len(sorted_deltas) // 2]
        if sorted_deltas
        else None
    )
    sorted_separations = sorted(separations)
    median_separation = (
        sorted_separations[len(sorted_separations) // 2]
        if sorted_separations
        else None
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-double-stop-alignment-diagnosis",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "targetPitches": sorted(TARGET_PITCHES),
        "searchRadiusSeconds": SEARCH_RADIUS_SECONDS,
        "pairMaximumSeparationSeconds": PAIR_MAX_SEPARATION_SECONDS,
        "targetReports": reports,
        "summary": {
            "targetsInspected": len(reports),
            "targetsWithAny58_62Pair": sum(
                1 for item in reports if item["best58_62Pair"] is not None
            ),
            "targetsWithPairWithin180ms": sum(
                1
                for item in reports
                if item["best58_62Pair"] is not None
                and item["best58_62Pair"]["within180ms"]
            ),
            "medianPairCenterDeltaSeconds": median_delta,
            "medianPairSeparationSeconds": median_separation,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Double-stop alignment diagnosis")
    print(f"Targets inspected: {len(reports)}")
    print(
        "Targets with any MIDI 58/62 pair inside +/-0.90s: "
        f"{report['summary']['targetsWithAny58_62Pair']}/{len(reports)}"
    )
    print(
        "Targets with pair separation <=180ms: "
        f"{report['summary']['targetsWithPairWithin180ms']}/{len(reports)}"
    )
    print(
        "Median pair-center timing delta: "
        f"{median_delta if median_delta is not None else 'none'} seconds"
    )
    print(
        "Median MIDI 58/62 attack separation: "
        f"{median_separation if median_separation is not None else 'none'} seconds"
    )

    for item in reports:
        pair = item["best58_62Pair"]
        if pair is None:
            print(
                f"Measure {item['measureNumber']:>2} step {item['step']}: "
                "no MIDI 58/62 pair found"
            )
        else:
            print(
                f"Measure {item['measureNumber']:>2} step {item['step']}: "
                f"centerDelta={pair['pairCenterDeltaSeconds']:+.3f}s | "
                f"separation={pair['separationSeconds']:.3f}s | "
                f"within180ms={pair['within180ms']}"
            )

    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
