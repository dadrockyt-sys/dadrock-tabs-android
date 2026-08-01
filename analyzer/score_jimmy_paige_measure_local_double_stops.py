from __future__ import annotations

import json
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-measure-local-double-stop-score.json"

TARGET_PITCHES = {58, 62}
ENDING_ZONE_START = 0.70
ENDING_ZONE_END = 1.05
PAIR_WINDOWS_MS = [180, 225, 275, 350, 450]


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _end(event: dict[str, Any]) -> float:
    for key in ("end", "end_time", "endTime"):
        if event.get(key) is not None:
            return float(event[key])
    duration = float(event.get("duration", event.get("duration_seconds", 0.0)) or 0.0)
    return _start(event) + duration


def _measure_zone(
    measure_number: int,
    bounds: dict[int, tuple[float, float]],
) -> tuple[float, float]:
    start, end = bounds[measure_number]
    duration = end - start
    return (
        start + duration * ENDING_ZONE_START,
        start + duration * ENDING_ZONE_END,
    )


def _events_in_zone(
    events: list[dict[str, Any]],
    zone: tuple[float, float],
) -> list[dict[str, Any]]:
    start, end = zone
    return [event for event in events if start <= _start(event) <= end]


def _pair_candidates(
    events: list[dict[str, Any]],
    max_separation_seconds: float,
) -> list[dict[str, Any]]:
    pitch_58 = [event for event in events if int(event.get("midiPitch", -999)) == 58]
    pitch_62 = [event for event in events if int(event.get("midiPitch", -999)) == 62]
    pairs: list[dict[str, Any]] = []

    for first in pitch_58:
        for second in pitch_62:
            onset_separation = abs(_start(first) - _start(second))
            sustain_overlap = max(
                0.0,
                min(_end(first), _end(second)) - max(_start(first), _start(second)),
            )
            qualifies = onset_separation <= max_separation_seconds or sustain_overlap > 0.0
            if not qualifies:
                continue
            pairs.append(
                {
                    "pitch58Start": round(_start(first), 6),
                    "pitch62Start": round(_start(second), 6),
                    "onsetSeparationSeconds": round(onset_separation, 6),
                    "sustainOverlapSeconds": round(sustain_overlap, 6),
                    "pairCenterSeconds": round((_start(first) + _start(second)) / 2.0, 6),
                }
            )

    pairs.sort(
        key=lambda item: (
            item["onsetSeparationSeconds"],
            -item["sustainOverlapSeconds"],
        )
    )
    return pairs


def _score_window(
    events: list[dict[str, Any]],
    bounds: dict[int, tuple[float, float]],
    window_ms: int,
) -> dict[str, Any]:
    max_separation = window_ms / 1000.0
    positive_reports: list[dict[str, Any]] = []
    negative_reports: list[dict[str, Any]] = []
    true_positive = 0
    false_positive = 0

    for measure_number in range(1, 17):
        zone = _measure_zone(measure_number, bounds)
        nearby = _events_in_zone(events, zone)
        pairs = _pair_candidates(nearby, max_separation)
        expected = measure_number % 2 == 0
        predicted = len(pairs) >= 1

        report = {
            "measureNumber": measure_number,
            "expectedDoubleStopEnding": expected,
            "predictedDoubleStopEnding": predicted,
            "zoneStartSeconds": round(zone[0], 6),
            "zoneEndSeconds": round(zone[1], 6),
            "midi58Count": sum(1 for event in nearby if int(event.get("midiPitch", -999)) == 58),
            "midi62Count": sum(1 for event in nearby if int(event.get("midiPitch", -999)) == 62),
            "qualifyingPairCount": len(pairs),
            "bestPair": pairs[0] if pairs else None,
        }

        if expected:
            positive_reports.append(report)
            if predicted:
                true_positive += 1
        else:
            negative_reports.append(report)
            if predicted:
                false_positive += 1

    target_count = len(positive_reports)
    negative_count = len(negative_reports)
    false_negative = target_count - true_positive
    true_negative = negative_count - false_positive
    recall = 100.0 * true_positive / target_count if target_count else 0.0
    precision = (
        100.0 * true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )

    return {
        "pairWindowMilliseconds": window_ms,
        "truePositive": true_positive,
        "falseNegative": false_negative,
        "falsePositive": false_positive,
        "trueNegative": true_negative,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "positiveMeasureReports": positive_reports,
        "negativeMeasureReports": negative_reports,
    }


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    results = [
        _score_window(events, bounds, window_ms)
        for window_ms in PAIR_WINDOWS_MS
    ]
    best = max(
        results,
        key=lambda item: (
            item["f1Percentage"],
            item["recallPercentage"],
            item["precisionPercentage"],
            -item["pairWindowMilliseconds"],
        ),
    )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-measure-local-double-stop-score",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "targetPitches": sorted(TARGET_PITCHES),
        "endingZoneFraction": [ENDING_ZONE_START, ENDING_ZONE_END],
        "pairWindowsMilliseconds": PAIR_WINDOWS_MS,
        "results": results,
        "bestWindow": best,
        "protectedPitchCheckpoint": {
            "overallRecallPercentage": 93.06,
            "lowRegisterRecallPercentage": 84.38,
            "midi52Matches": 32,
            "midi62Matches": 16,
            "combinedRegressionPassed": True,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    for result in results:
        print(
            f"Window {result['pairWindowMilliseconds']:>3} ms | "
            f"TP={result['truePositive']}/8 | "
            f"FP={result['falsePositive']}/8 | "
            f"precision={result['precisionPercentage']}% | "
            f"recall={result['recallPercentage']}% | "
            f"F1={result['f1Percentage']}%"
        )

    print(
        "Measure-local double-stop scoring complete | "
        f"bestWindow={best['pairWindowMilliseconds']} ms | "
        f"precision={best['precisionPercentage']}% | "
        f"recall={best['recallPercentage']}% | "
        f"F1={best['f1Percentage']}%"
    )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
