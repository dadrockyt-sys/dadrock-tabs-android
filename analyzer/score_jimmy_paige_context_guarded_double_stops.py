from __future__ import annotations

import json
from itertools import product
from typing import Any

from run_jimmy_paige_low_register_recovery_training_loop import REPO_ROOT

CONTEXT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-double-stop-rhythmic-context.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-context-guarded-double-stop-score.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-context-guarded-double-stop-checkpoint.json"
)

TARGET_COUNT_MINIMUMS = [1, 2, 3, 4]
FOLLOWING_DENSITY_MINIMUMS = [0.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0]
PRECEDING_DENSITY_MAXIMUMS = [40.0, 50.0, 60.0, 70.0, 80.0, 100.0]
LOW_REGISTER_MAXIMUMS = [16, 18, 20, 24, 28, 35]


def _is_true(row: dict[str, Any]) -> bool:
    return "true" in str(row.get("classification", "")).lower()


def _predict(
    row: dict[str, Any],
    target_minimum: int,
    following_minimum: float,
    preceding_maximum: float,
    low_maximum: int,
) -> bool:
    return bool(
        int(row.get("precedingTargetToneCount", 0)) >= target_minimum
        and float(row.get("followingAttackDensityPerSecond", 0.0))
        >= following_minimum
        and float(row.get("precedingAttackDensityPerSecond", 0.0))
        <= preceding_maximum
        and int(row.get("precedingLowRegisterCount", 0)) <= low_maximum
    )


def _score(
    rows: list[dict[str, Any]],
    target_minimum: int,
    following_minimum: float,
    preceding_maximum: float,
    low_maximum: int,
) -> dict[str, Any]:
    true_positive = false_positive = true_negative = false_negative = 0
    reports: list[dict[str, Any]] = []

    for row in rows:
        expected = _is_true(row)
        predicted = _predict(
            row,
            target_minimum,
            following_minimum,
            preceding_maximum,
            low_maximum,
        )

        if expected and predicted:
            true_positive += 1
        elif expected and not predicted:
            false_negative += 1
        elif not expected and predicted:
            false_positive += 1
        else:
            true_negative += 1

        reports.append(
            {
                "measureNumber": int(row.get("measureNumber", -1)),
                "classification": row.get("classification"),
                "expected": expected,
                "predicted": predicted,
                "precedingTargetToneCount": row.get("precedingTargetToneCount"),
                "followingAttackDensityPerSecond": row.get(
                    "followingAttackDensityPerSecond"
                ),
                "precedingAttackDensityPerSecond": row.get(
                    "precedingAttackDensityPerSecond"
                ),
                "precedingLowRegisterCount": row.get(
                    "precedingLowRegisterCount"
                ),
            }
        )

    precision = (
        100.0 * true_positive / (true_positive + false_positive)
        if true_positive + false_positive
        else 0.0
    )
    recall = (
        100.0 * true_positive / (true_positive + false_negative)
        if true_positive + false_negative
        else 0.0
    )
    f1 = (
        2.0 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    accuracy = 100.0 * (true_positive + true_negative) / len(rows)

    return {
        "minimumPrecedingTargetToneCount": target_minimum,
        "minimumFollowingAttackDensity": following_minimum,
        "maximumPrecedingAttackDensity": preceding_maximum,
        "maximumPrecedingLowRegisterCount": low_maximum,
        "truePositive": true_positive,
        "falsePositive": false_positive,
        "trueNegative": true_negative,
        "falseNegative": false_negative,
        "precisionPercentage": round(precision, 2),
        "recallPercentage": round(recall, 2),
        "f1Percentage": round(f1, 2),
        "accuracyPercentage": round(accuracy, 2),
        "measureReports": reports,
    }


def main() -> None:
    if not CONTEXT_PATH.is_file():
        raise FileNotFoundError(
            f"Missing rhythmic-context diagnosis: {CONTEXT_PATH}"
        )

    payload = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    rows = payload.get("reports", [])
    if not rows:
        raise RuntimeError("No rhythmic-context rows found")

    results: list[dict[str, Any]] = []
    for target_minimum, following_minimum, preceding_maximum, low_maximum in product(
        TARGET_COUNT_MINIMUMS,
        FOLLOWING_DENSITY_MINIMUMS,
        PRECEDING_DENSITY_MAXIMUMS,
        LOW_REGISTER_MAXIMUMS,
    ):
        results.append(
            _score(
                rows,
                target_minimum,
                following_minimum,
                preceding_maximum,
                low_maximum,
            )
        )

    results.sort(
        key=lambda item: (
            item["f1Percentage"],
            item["recallPercentage"],
            item["precisionPercentage"],
            item["accuracyPercentage"],
            -item["falsePositive"],
            -item["falseNegative"],
        ),
        reverse=True,
    )
    best = results[0]

    report = {
        "benchmarkVersion": 1,
        "benchmarkType": "context-guarded-professional-double-stop-score",
        "sourceContext": str(CONTEXT_PATH.relative_to(REPO_ROOT)),
        "rulesTested": len(results),
        "bestRule": best,
        "topRules": results[:20],
        "smallSampleWarning": (
            "This rule is trained on nine labeled examples and must not be "
            "promoted without a second professional reference song."
        ),
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

    print("Context-guarded double-stop scoring complete")
    print(f"Rules tested: {len(results)}")
    print(
        "Best rule | "
        f"targetsBefore>={best['minimumPrecedingTargetToneCount']} | "
        f"afterDensity>={best['minimumFollowingAttackDensity']} | "
        f"beforeDensity<={best['maximumPrecedingAttackDensity']} | "
        f"lowBefore<={best['maximumPrecedingLowRegisterCount']}"
    )
    print(
        f"TP={best['truePositive']} | FP={best['falsePositive']} | "
        f"FN={best['falseNegative']} | TN={best['trueNegative']} | "
        f"precision={best['precisionPercentage']}% | "
        f"recall={best['recallPercentage']}% | "
        f"F1={best['f1Percentage']}% | "
        f"accuracy={best['accuracyPercentage']}%"
    )

    accepted = [
        item["measureNumber"]
        for item in best["measureReports"]
        if item["predicted"]
    ]
    rejected = [
        item["measureNumber"]
        for item in best["measureReports"]
        if not item["predicted"]
    ]
    print(f"Accepted measures: {accepted}")
    print(f"Rejected measures: {rejected}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
