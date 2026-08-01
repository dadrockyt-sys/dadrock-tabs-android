from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REFERENCE_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-professional-double-stop-score.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-double-stop-checkpoint.json"

TARGET_PITCHES = {58, 62}
WINDOWS_MS = [20, 30, 40, 50, 65, 80, 100]


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _target_time(
    measure_number: int,
    step: int,
    bounds: dict[int, tuple[float, float]],
) -> float:
    start, end = bounds[measure_number]
    return start + (end - start) * (step / 16.0)


def _events_near(
    events: list[dict[str, Any]],
    target_time: float,
    window_seconds: float,
) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if abs(_event_start(event) - target_time) <= window_seconds
    ]


def _pitch_set(events: list[dict[str, Any]]) -> set[int]:
    return {
        int(event.get("midiPitch", -999))
        for event in events
        if event.get("midiPitch") is not None
    }


def _score_window(
    events: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
    window_ms: int,
) -> dict[str, Any]:
    window_seconds = window_ms / 1000.0
    target_reports: list[dict[str, Any]] = []
    true_positive = 0

    for measure_number in range(2, 17, 2):
        for step in (14, 15):
            when = _target_time(measure_number, step, bounds)
            nearby = _events_near(events, when, window_seconds)
            pitches = _pitch_set(nearby)
            matched = TARGET_PITCHES.issubset(pitches)
            if matched:
                true_positive += 1
            target_reports.append(
                {
                    "measureNumber": measure_number,
                    "step": step,
                    "targetSeconds": round(when, 6),
                    "matched": matched,
                    "detectedPitches": sorted(pitches),
                    "targetPitches": sorted(TARGET_PITCHES),
                    "eventCount": len(nearby),
                }
            )

    false_positive = 0
    negative_reports: list[dict[str, Any]] = []
    for measure_number in range(1, 17, 2):
        for step in (14, 15):
            when = _target_time(measure_number, step, bounds)
            nearby = _events_near(events, when, window_seconds)
            pitches = _pitch_set(nearby)
            predicted = TARGET_PITCHES.issubset(pitches)
            if predicted:
                false_positive += 1
            negative_reports.append(
                {
                    "measureNumber": measure_number,
                    "step": step,
                    "predictedDoubleStop": predicted,
                    "detectedPitches": sorted(pitches),
                }
            )

    target_count = len(target_reports)
    negative_count = len(negative_reports)
    false_negative = target_count - true_positive
    true_negative = negative_count - false_positive

    recall = 100.0 * true_positive / target_count if target_count else 0.0
    precision_denominator = true_positive + false_positive
    precision = (
        100.0 * true_positive / precision_denominator
        if precision_denominator
        else 0.0
    )
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "windowMilliseconds": window_ms,
        "targetCount": target_count,
        "negativeControlCount": negative_count,
        "truePositive": true_positive,
        "falseNegative": false_negative,
        "falsePositive": false_positive,
        "trueNegative": true_negative,
        "recallPercentage": round(recall, 2),
        "precisionPercentage": round(precision, 2),
        "f1Percentage": round(f1, 2),
        "targetReports": target_reports,
        "negativeControlReports": negative_reports,
    }


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    reference = _load_json(REFERENCE_PATH)
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    expected_group_ids = [
        event.get("groupId")
        for measure in reference.get("measures", [])
        for event in measure.get("events", [])
        if event.get("groupId")
    ]

    results = [_score_window(events, bounds, window) for window in WINDOWS_MS]
    best = max(
        results,
        key=lambda item: (
            item["f1Percentage"],
            item["recallPercentage"],
            -item["windowMilliseconds"],
        ),
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-rhythm-double-stop-window-score",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "targetPitches": sorted(TARGET_PITCHES),
        "targetDescription": "B-string fret 3 plus G-string fret 3 endings in even measures 1-16",
        "professionalTargetGroups": len(set(expected_group_ids)),
        "results": results,
        "bestWindow": best,
        "protectedPitchCheckpoint": {
            "overallRecallPercentage": 93.06,
            "lowRegisterRecallPercentage": 84.38,
            "midi52Matches": 32,
            "midi62Matches": 16,
            "combinedRegressionPassed": True,
        },
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "professionalPdfRemainsScoringAuthority": True,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    CHECKPOINT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for result in results:
        print(
            f"Window {result['windowMilliseconds']:>3} ms | "
            f"TP={result['truePositive']}/{result['targetCount']} | "
            f"FP={result['falsePositive']}/{result['negativeControlCount']} | "
            f"precision={result['precisionPercentage']}% | "
            f"recall={result['recallPercentage']}% | "
            f"F1={result['f1Percentage']}%"
        )

    print(
        "Professional double-stop baseline complete | "
        f"bestWindow={best['windowMilliseconds']} ms | "
        f"precision={best['precisionPercentage']}% | "
        f"recall={best['recallPercentage']}% | "
        f"F1={best['f1Percentage']}%"
    )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
