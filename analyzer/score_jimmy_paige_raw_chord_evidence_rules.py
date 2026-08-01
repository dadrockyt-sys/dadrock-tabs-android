from __future__ import annotations

import json
from itertools import product
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-phase-local-raw-chord-evidence.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-raw-chord-evidence-rule-score.json"
)

EXPECTED = {2, 4, 6, 8, 10, 12, 14, 16}
NEGATIVE = {1, 3, 5, 7, 9, 11, 13, 15}

COACTIVATION_CUTOFFS = [0.10, 0.105, 0.11, 0.115, 0.12, 0.125, 0.13, 0.14, 0.15]
ONSET_MIN_CUTOFFS = [0.15, 0.20, 0.25, 0.30, 0.35, 0.40]
SAME_FRAME_MINIMUMS = [0, 1, 2, 3, 5, 8, 10]


def _metrics(predicted: set[int], measures: set[int]) -> dict[str, Any]:
    expected = EXPECTED & measures
    negative = NEGATIVE & measures
    tp_set = predicted & expected
    fp_set = predicted & negative
    fn_set = expected - predicted
    tn_set = negative - predicted

    tp = len(tp_set)
    fp = len(fp_set)
    fn = len(fn_set)
    tn = len(tn_set)
    precision = 100.0 * tp / (tp + fp) if tp + fp else 0.0
    recall = 100.0 * tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    accuracy = 100.0 * (tp + tn) / len(measures) if measures else 0.0
    return {
        "truePositive": tp,
        "falsePositive": fp,
        "falseNegative": fn,
        "trueNegative": tn,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "accuracyPercentage": round(accuracy, 2),
        "truePositiveMeasures": sorted(tp_set),
        "falsePositiveMeasures": sorted(fp_set),
        "missedProfessionalMeasures": sorted(fn_set),
        "trueNegativeMeasures": sorted(tn_set),
    }


def _predict(
    rows: dict[int, dict[str, Any]],
    rule: dict[str, Any],
    measures: set[int],
) -> set[int]:
    predicted: set[int] = set()
    for measure in measures:
        phase_rows = rows[measure]["phaseReports"]
        phase = next(
            item
            for item in phase_rows
            if float(item["phaseStart"]) == rule["phaseStart"]
            and float(item["phaseEnd"]) == rule["phaseEnd"]
        )
        threshold = phase["thresholdEvidence"][rule["frameThreshold"]]
        onset_min = min(
            float(phase["midi58OnsetMaximum"]),
            float(phase["midi62OnsetMaximum"]),
        )
        accepted = bool(
            float(phase["sameFrameMinimumMaximum"])
            >= rule["coactivationMinimum"]
            and int(threshold["sameFrameCount"])
            >= rule["sameFrameCountMinimum"]
            and onset_min >= rule["onsetMinimum"]
        )
        if accepted:
            predicted.add(measure)
    return predicted


def _candidate_rules(report: dict[str, Any]) -> list[dict[str, Any]]:
    phase_windows = [tuple(map(float, item)) for item in report["phaseWindows"]]
    frame_thresholds = [f"{float(item):.2f}" for item in report["thresholds"]]
    return [
        {
            "phaseStart": phase_start,
            "phaseEnd": phase_end,
            "frameThreshold": frame_threshold,
            "coactivationMinimum": coactivation,
            "sameFrameCountMinimum": same_frames,
            "onsetMinimum": onset_minimum,
        }
        for (
            (phase_start, phase_end),
            frame_threshold,
            coactivation,
            same_frames,
            onset_minimum,
        ) in product(
            phase_windows,
            frame_thresholds,
            COACTIVATION_CUTOFFS,
            SAME_FRAME_MINIMUMS,
            ONSET_MIN_CUTOFFS,
        )
    ]


def _ranking(metrics: dict[str, Any], rule: dict[str, Any]) -> tuple[Any, ...]:
    return (
        metrics["f1Percentage"],
        metrics["recallPercentage"],
        metrics["precisionPercentage"],
        -rule["sameFrameCountMinimum"],
        -rule["coactivationMinimum"],
    )


def main() -> None:
    if not INPUT_PATH.is_file():
        raise FileNotFoundError(f"Missing raw evidence JSON: {INPUT_PATH}")

    report = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = {
        int(item["measureNumber"]): item
        for item in report["measureReports"]
    }
    all_measures = set(rows)
    rules = _candidate_rules(report)

    best_rule: dict[str, Any] | None = None
    best_metrics: dict[str, Any] | None = None
    for rule in rules:
        predicted = _predict(rows, rule, all_measures)
        metrics = _metrics(predicted, all_measures)
        if (
            best_rule is None
            or _ranking(metrics, rule) > _ranking(best_metrics or {}, best_rule)
        ):
            best_rule = rule
            best_metrics = metrics

    leave_one_out: list[dict[str, Any]] = []
    held_out_correct = 0
    for held_out in sorted(all_measures):
        training = all_measures - {held_out}
        training_best_rule: dict[str, Any] | None = None
        training_best_metrics: dict[str, Any] | None = None
        for rule in rules:
            predicted = _predict(rows, rule, training)
            metrics = _metrics(predicted, training)
            if (
                training_best_rule is None
                or _ranking(metrics, rule)
                > _ranking(training_best_metrics or {}, training_best_rule)
            ):
                training_best_rule = rule
                training_best_metrics = metrics

        assert training_best_rule is not None
        prediction = held_out in _predict(rows, training_best_rule, {held_out})
        expected = held_out in EXPECTED
        correct = prediction == expected
        held_out_correct += int(correct)
        leave_one_out.append(
            {
                "heldOutMeasure": held_out,
                "expectedDoubleStop": expected,
                "predictedDoubleStop": prediction,
                "correct": correct,
                "trainingRule": training_best_rule,
                "trainingMetrics": training_best_metrics,
            }
        )

    assert best_rule is not None and best_metrics is not None
    loo_accuracy = round(100.0 * held_out_correct / len(all_measures), 2)
    output = {
        "benchmarkVersion": 1,
        "benchmarkType": "guarded-raw-chord-evidence-rule-score",
        "source": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "rulesTested": len(rules),
        "bestFullDatasetRule": best_rule,
        "bestFullDatasetMetrics": best_metrics,
        "leaveOneMeasureOut": leave_one_out,
        "leaveOneMeasureOutCorrect": held_out_correct,
        "leaveOneMeasureOutTotal": len(all_measures),
        "leaveOneMeasureOutAccuracyPercentage": loo_accuracy,
        "readyForProductionPromotion": False,
        "reasonProductionBlocked": (
            "Single-song raw-evidence rules require cross-song validation."
        ),
        "professionalPdfRemainsScoringAuthority": True,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Raw chord evidence rule scoring complete")
    print(f"Rules tested: {len(rules)}")
    print(f"Best rule: {best_rule}")
    print(
        "Full dataset | "
        f"TP={best_metrics['truePositive']}/8 | "
        f"FP={best_metrics['falsePositive']}/8 | "
        f"precision={best_metrics['precisionPercentage']}% | "
        f"recall={best_metrics['recallPercentage']}% | "
        f"F1={best_metrics['f1Percentage']}%"
    )
    print(
        "Leave-one-measure-out validation | "
        f"correct={held_out_correct}/{len(all_measures)} | "
        f"accuracy={loo_accuracy}%"
    )
    failed = [
        item["heldOutMeasure"]
        for item in leave_one_out
        if not item["correct"]
    ]
    print(f"Held-out errors: {failed}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
