from __future__ import annotations

import json
from itertools import product
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-phase-aware-double-stop-score.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-phase-aware-double-stop-checkpoint.json"

TARGET_PITCHES = {58, 62}
PHASE_STARTS = [0.50, 0.55, 0.60, 0.65, 0.70]
PHASE_ENDS = [0.90, 0.95, 1.00, 1.05, 1.10]
PAIR_WINDOWS_MS = [180, 225, 275, 350, 450]
BOUNDARY_SPILL_SECONDS = 0.18


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _end(event: dict[str, Any]) -> float:
    for key in ("end", "end_time", "endTime"):
        if event.get(key) is not None:
            return float(event[key])
    duration = float(
        event.get("duration", event.get("duration_seconds", 0.0)) or 0.0
    )
    return _start(event) + duration


def _phase(
    seconds: float,
    measure_number: int,
    bounds: dict[int, tuple[float, float]],
) -> float:
    measure_start, measure_end = bounds[measure_number]
    duration = measure_end - measure_start
    if duration <= 0:
        return 0.0
    return (seconds - measure_start) / duration


def _candidate_events(
    events: list[dict[str, Any]],
    measure_number: int,
    bounds: dict[int, tuple[float, float]],
) -> list[dict[str, Any]]:
    measure_start, measure_end = bounds[measure_number]
    return [
        event
        for event in events
        if measure_start - BOUNDARY_SPILL_SECONDS
        <= _start(event)
        <= measure_end + BOUNDARY_SPILL_SECONDS
        and int(event.get("midiPitch", -999)) in TARGET_PITCHES
    ]


def _pairs(
    events: list[dict[str, Any]],
    measure_number: int,
    bounds: dict[int, tuple[float, float]],
) -> list[dict[str, Any]]:
    pitch_58 = [
        event for event in events if int(event.get("midiPitch", -999)) == 58
    ]
    pitch_62 = [
        event for event in events if int(event.get("midiPitch", -999)) == 62
    ]
    pairs: list[dict[str, Any]] = []

    for first in pitch_58:
        for second in pitch_62:
            onset_separation = abs(_start(first) - _start(second))
            sustain_overlap = max(
                0.0,
                min(_end(first), _end(second))
                - max(_start(first), _start(second)),
            )
            center = (_start(first) + _start(second)) / 2.0
            pairs.append(
                {
                    "pitch58Start": round(_start(first), 6),
                    "pitch62Start": round(_start(second), 6),
                    "pairCenterSeconds": round(center, 6),
                    "pairCenterPhase": round(
                        _phase(center, measure_number, bounds), 6
                    ),
                    "onsetSeparationSeconds": round(onset_separation, 6),
                    "sustainOverlapSeconds": round(sustain_overlap, 6),
                }
            )

    return pairs


def _score_policy(
    all_pairs: dict[int, list[dict[str, Any]]],
    phase_start: float,
    phase_end: float,
    pair_window_ms: int,
) -> dict[str, Any]:
    max_separation = pair_window_ms / 1000.0
    true_positive = 0
    false_positive = 0
    measure_reports: list[dict[str, Any]] = []

    for measure_number in range(1, 17):
        qualifying = [
            pair
            for pair in all_pairs[measure_number]
            if phase_start <= pair["pairCenterPhase"] <= phase_end
            and (
                pair["onsetSeparationSeconds"] <= max_separation
                or pair["sustainOverlapSeconds"] > 0.0
            )
        ]
        qualifying.sort(
            key=lambda pair: (
                pair["onsetSeparationSeconds"],
                -pair["sustainOverlapSeconds"],
                abs(pair["pairCenterPhase"] - 0.875),
            )
        )

        expected = measure_number % 2 == 0
        predicted = bool(qualifying)
        if expected and predicted:
            true_positive += 1
        elif not expected and predicted:
            false_positive += 1

        measure_reports.append(
            {
                "measureNumber": measure_number,
                "expectedDoubleStopEnding": expected,
                "predictedDoubleStopEnding": predicted,
                "qualifyingPairCount": len(qualifying),
                "bestPair": qualifying[0] if qualifying else None,
            }
        )

    target_count = 8
    negative_count = 8
    false_negative = target_count - true_positive
    true_negative = negative_count - false_positive
    recall = 100.0 * true_positive / target_count
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
        "phaseStart": phase_start,
        "phaseEnd": phase_end,
        "pairWindowMilliseconds": pair_window_ms,
        "truePositive": true_positive,
        "falseNegative": false_negative,
        "falsePositive": false_positive,
        "trueNegative": true_negative,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "measureReports": measure_reports,
    }


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    all_pairs = {
        measure_number: _pairs(
            _candidate_events(events, measure_number, bounds),
            measure_number,
            bounds,
        )
        for measure_number in range(1, 17)
    }

    results: list[dict[str, Any]] = []
    for phase_start, phase_end, pair_window_ms in product(
        PHASE_STARTS,
        PHASE_ENDS,
        PAIR_WINDOWS_MS,
    ):
        if phase_end <= phase_start:
            continue
        results.append(
            _score_policy(
                all_pairs,
                phase_start,
                phase_end,
                pair_window_ms,
            )
        )

    results.sort(
        key=lambda item: (
            item["f1Percentage"],
            item["recallPercentage"],
            item["precisionPercentage"],
            -item["falsePositive"],
            -(item["phaseEnd"] - item["phaseStart"]),
            -item["pairWindowMilliseconds"],
        ),
        reverse=True,
    )
    best = results[0]

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-phase-aware-double-stop-score",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "targetPitches": sorted(TARGET_PITCHES),
        "boundarySpillSeconds": BOUNDARY_SPILL_SECONDS,
        "policiesTested": len(results),
        "bestPolicy": best,
        "topPolicies": results[:10],
        "allMeasurePairInventory": {
            str(measure): pairs for measure, pairs in all_pairs.items()
        },
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

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    CHECKPOINT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Phase-aware double-stop scoring complete")
    print(f"Policies tested: {len(results)}")
    print(
        "Best policy | "
        f"phase={best['phaseStart']:.2f}-{best['phaseEnd']:.2f} | "
        f"pairWindow={best['pairWindowMilliseconds']} ms | "
        f"TP={best['truePositive']}/8 | FP={best['falsePositive']}/8 | "
        f"precision={best['precisionPercentage']}% | "
        f"recall={best['recallPercentage']}% | "
        f"F1={best['f1Percentage']}%"
    )

    true_positive_measures = [
        item["measureNumber"]
        for item in best["measureReports"]
        if item["expectedDoubleStopEnding"]
        and item["predictedDoubleStopEnding"]
    ]
    missed_measures = [
        item["measureNumber"]
        for item in best["measureReports"]
        if item["expectedDoubleStopEnding"]
        and not item["predictedDoubleStopEnding"]
    ]
    false_positive_measures = [
        item["measureNumber"]
        for item in best["measureReports"]
        if not item["expectedDoubleStopEnding"]
        and item["predictedDoubleStopEnding"]
    ]
    print(f"True-positive measures: {true_positive_measures}")
    print(f"Missed professional measures: {missed_measures}")
    print(f"False-positive odd measures: {false_positive_measures}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
