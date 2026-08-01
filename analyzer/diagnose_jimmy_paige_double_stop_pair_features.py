from __future__ import annotations

import json
from statistics import median
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import (
    CALIBRATION_PATH,
    REPO_ROOT,
    _load_json,
    _measure_bounds,
)

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
PHASE_SCORE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-phase-aware-double-stop-score.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-double-stop-pair-feature-diagnosis.json"

TARGET_PITCHES = {58, 62}
BOUNDARY_SPILL_SECONDS = 0.18


def _start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _end(event: dict[str, Any]) -> float:
    for key in ("end", "end_time", "endTime"):
        if event.get(key) is not None:
            return float(event[key])
    duration = float(event.get("duration", event.get("duration_seconds", 0.0)) or 0.0)
    return _start(event) + duration


def _confidence(event: dict[str, Any]) -> float | None:
    for key in ("confidence", "amplitude", "velocity"):
        value = event.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def _phase(seconds: float, measure: int, bounds: dict[int, tuple[float, float]]) -> float:
    start, end = bounds[measure]
    duration = end - start
    return (seconds - start) / duration if duration > 0 else 0.0


def _candidate_events(
    events: list[dict[str, Any]],
    measure: int,
    bounds: dict[int, tuple[float, float]],
) -> list[dict[str, Any]]:
    start, end = bounds[measure]
    return [
        event
        for event in events
        if start - BOUNDARY_SPILL_SECONDS <= _start(event) <= end + BOUNDARY_SPILL_SECONDS
    ]


def _pair_features(
    events: list[dict[str, Any]],
    measure: int,
    bounds: dict[int, tuple[float, float]],
) -> list[dict[str, Any]]:
    pitch58 = [event for event in events if int(event.get("midiPitch", -999)) == 58]
    pitch62 = [event for event in events if int(event.get("midiPitch", -999)) == 62]
    pairs: list[dict[str, Any]] = []

    for first in pitch58:
        for second in pitch62:
            onset_separation = abs(_start(first) - _start(second))
            overlap = max(0.0, min(_end(first), _end(second)) - max(_start(first), _start(second)))
            center = (_start(first) + _start(second)) / 2.0
            center_phase = _phase(center, measure, bounds)
            first_duration = max(0.0, _end(first) - _start(first))
            second_duration = max(0.0, _end(second) - _start(second))
            nearby_attack_support = sum(
                1
                for event in events
                if abs(_start(event) - center) <= 0.12
                and int(event.get("midiPitch", -999)) not in TARGET_PITCHES
            )
            confidences = [value for value in (_confidence(first), _confidence(second)) if value is not None]

            pairs.append(
                {
                    "pitch58Start": round(_start(first), 6),
                    "pitch62Start": round(_start(second), 6),
                    "centerSeconds": round(center, 6),
                    "centerPhase": round(center_phase, 6),
                    "distanceFromExpectedEndingPhase": round(abs(center_phase - 0.875), 6),
                    "onsetSeparationSeconds": round(onset_separation, 6),
                    "sustainOverlapSeconds": round(overlap, 6),
                    "pitch58DurationSeconds": round(first_duration, 6),
                    "pitch62DurationSeconds": round(second_duration, 6),
                    "minimumDurationSeconds": round(min(first_duration, second_duration), 6),
                    "maximumDurationSeconds": round(max(first_duration, second_duration), 6),
                    "nearbyNonTargetAttackSupport": nearby_attack_support,
                    "minimumConfidence": round(min(confidences), 6) if confidences else None,
                    "meanConfidence": round(sum(confidences) / len(confidences), 6) if confidences else None,
                }
            )

    pairs.sort(
        key=lambda pair: (
            pair["distanceFromExpectedEndingPhase"],
            pair["onsetSeparationSeconds"],
            -pair["sustainOverlapSeconds"],
        )
    )
    return pairs


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    keys = [
        "centerPhase",
        "distanceFromExpectedEndingPhase",
        "onsetSeparationSeconds",
        "sustainOverlapSeconds",
        "minimumDurationSeconds",
        "maximumDurationSeconds",
        "nearbyNonTargetAttackSupport",
        "minimumConfidence",
        "meanConfidence",
    ]
    result: dict[str, Any] = {"count": len(rows)}
    for key in keys:
        values = [float(row[key]) for row in rows if row.get(key) is not None]
        if values:
            result[key] = {
                "minimum": round(min(values), 6),
                "median": round(median(values), 6),
                "maximum": round(max(values), 6),
            }
    return result


def main() -> None:
    if not EVENTS_PATH.is_file():
        raise FileNotFoundError(f"Missing protected event cache: {EVENTS_PATH}")
    if not PHASE_SCORE_PATH.is_file():
        raise FileNotFoundError(f"Missing phase-aware score: {PHASE_SCORE_PATH}")

    events = json.loads(EVENTS_PATH.read_text(encoding="utf-8"))
    phase_report = json.loads(PHASE_SCORE_PATH.read_text(encoding="utf-8"))
    calibration = _load_json(CALIBRATION_PATH)
    bounds = _measure_bounds(calibration)

    best = phase_report["bestPolicy"]
    selected_by_measure = {
        int(item["measureNumber"]): item
        for item in best["measureReports"]
    }

    measure_reports: list[dict[str, Any]] = []
    true_positive_features: list[dict[str, Any]] = []
    false_positive_features: list[dict[str, Any]] = []

    for measure in range(1, 17):
        candidates = _candidate_events(events, measure, bounds)
        pairs = _pair_features(candidates, measure, bounds)
        phase_item = selected_by_measure[measure]
        selected = phase_item.get("bestPair")
        expected = measure % 2 == 0
        predicted = bool(phase_item.get("predictedDoubleStopEnding"))

        selected_features = None
        if selected is not None:
            target_center = float(selected["pairCenterSeconds"])
            matching = sorted(
                pairs,
                key=lambda pair: abs(float(pair["centerSeconds"]) - target_center),
            )
            selected_features = matching[0] if matching else None

        classification = (
            "true-positive"
            if expected and predicted
            else "false-positive"
            if not expected and predicted
            else "false-negative"
            if expected and not predicted
            else "true-negative"
        )

        if selected_features is not None and classification == "true-positive":
            true_positive_features.append(selected_features)
        if selected_features is not None and classification == "false-positive":
            false_positive_features.append(selected_features)

        measure_reports.append(
            {
                "measureNumber": measure,
                "classification": classification,
                "expectedDoubleStopEnding": expected,
                "predictedDoubleStopEnding": predicted,
                "selectedPairFeatures": selected_features,
                "topThreeCandidatePairs": pairs[:3],
            }
        )

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "double-stop-pair-feature-diagnosis",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "sourcePhaseScore": str(PHASE_SCORE_PATH.relative_to(REPO_ROOT)),
        "bestPhasePolicy": {
            "phaseStart": best["phaseStart"],
            "phaseEnd": best["phaseEnd"],
            "pairWindowMilliseconds": best["pairWindowMilliseconds"],
        },
        "truePositiveFeatureSummary": _summary(true_positive_features),
        "falsePositiveFeatureSummary": _summary(false_positive_features),
        "measureReports": measure_reports,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Double-stop pair-feature diagnosis")
    print(f"True-positive measures: {[row['measureNumber'] for row in measure_reports if row['classification'] == 'true-positive']}")
    print(f"False-positive measures: {[row['measureNumber'] for row in measure_reports if row['classification'] == 'false-positive']}")
    print("\nTrue-positive feature summary:")
    print(json.dumps(report["truePositiveFeatureSummary"], indent=2))
    print("\nFalse-positive feature summary:")
    print(json.dumps(report["falsePositiveFeatureSummary"], indent=2))

    for row in measure_reports:
        if row["classification"] not in {"true-positive", "false-positive"}:
            continue
        features = row["selectedPairFeatures"] or {}
        print(
            f"{row['classification'].upper()} measure {row['measureNumber']:>2} | "
            f"phase={features.get('centerPhase')} | "
            f"sep={features.get('onsetSeparationSeconds')} | "
            f"overlap={features.get('sustainOverlapSeconds')} | "
            f"minDuration={features.get('minimumDurationSeconds')} | "
            f"support={features.get('nearbyNonTargetAttackSupport')} | "
            f"confidence={features.get('minimumConfidence')}"
        )

    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
