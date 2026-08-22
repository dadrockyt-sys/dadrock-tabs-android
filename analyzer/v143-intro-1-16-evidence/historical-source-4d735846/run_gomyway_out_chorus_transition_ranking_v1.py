from __future__ import annotations

import json
from itertools import combinations, product
from pathlib import Path
from statistics import median
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-chorus-soft-evidence-ranking-v1.json"
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-out-chorus-transition-ranking-v1.json"
)

OUT_CHORUS_START = 103
OUT_CHORUS_END = 110

BASE_COMPONENTS = (
    "phraseSupport",
    "exactPhraseSupport",
    "registerCompatibility",
    "noteActivation",
    "onsetActivation",
)

DERIVED_COMPONENTS = (
    "sectionProgress",
    "endingProximity",
    "outerEdge",
    "nearEdge",
    "interior",
    "lateHalf",
    "finalTwoMeasures",
    "quarterPulseAffinity",
    "lateEdgeInteraction",
)

COMPONENT_NAMES = BASE_COMPONENTS + DERIVED_COMPONENTS
MAX_ACTIVE_COMPONENTS = 3
WEIGHT_VALUES = (1, 2, 3)
DIRECTIONS = (-1, 1)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing benchmark input: {path.relative_to(REPO_ROOT)}"
        )

    return json.loads(path.read_text(encoding="utf-8"))


def clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def circular_step_distance(first: int, second: int, step_count: int = 16) -> int:
    direct = abs(first - second)
    return min(direct, step_count - direct)


def enrich_row(row: dict[str, Any]) -> dict[str, Any]:
    measure = int(row["measureNumber"])
    step = int(row["candidateStep"])

    progress = clamp(
        (measure - OUT_CHORUS_START)
        / max(1, OUT_CHORUS_END - OUT_CHORUS_START)
    )

    outer_edge = 1.0 if step in {0, 1, 15} else 0.0
    near_edge = 1.0 if step in {2, 3, 13, 14} else 0.0
    interior = 1.0 if not outer_edge and not near_edge else 0.0
    late_half = 1.0 if measure >= 107 else 0.0
    final_two = 1.0 if measure >= 109 else 0.0

    quarter_distance = min(
        circular_step_distance(step, anchor)
        for anchor in (0, 4, 8, 12)
    )
    quarter_affinity = clamp(1.0 - quarter_distance / 2.0)

    soft = row.get("softComponents") or {}

    components = {
        "phraseSupport": float(soft.get("phraseSupport") or 0.0),
        "exactPhraseSupport": float(soft.get("exactPhraseSupport") or 0.0),
        "registerCompatibility": float(soft.get("registerCompatibility") or 0.0),
        "noteActivation": float(soft.get("noteActivation") or 0.0),
        "onsetActivation": float(soft.get("onsetActivation") or 0.0),
        "sectionProgress": progress,
        "endingProximity": 1.0 - progress,
        "outerEdge": outer_edge,
        "nearEdge": near_edge,
        "interior": interior,
        "lateHalf": late_half,
        "finalTwoMeasures": final_two,
        "quarterPulseAffinity": quarter_affinity,
        "lateEdgeInteraction": late_half * max(outer_edge, near_edge),
    }

    return {
        **row,
        "transitionComponents": {
            key: round(value, 6)
            for key, value in components.items()
        },
    }


def score_row(
    row: dict[str, Any],
    model: tuple[tuple[str, int, int], ...],
) -> float:
    components = row["transitionComponents"]
    weighted_sum = 0.0
    total_weight = 0

    for name, direction, weight in model:
        weighted_sum += float(components[name]) * direction * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight else 0.0


def pairwise_accuracy(
    rows: list[dict[str, Any]],
    model: tuple[tuple[str, int, int], ...],
) -> dict[str, Any]:
    positives = [row for row in rows if row["referenceWithinOneStep"]]
    negatives = [row for row in rows if not row["referenceWithinOneStep"]]

    wins = 0
    ties = 0
    losses = 0

    for positive in positives:
        positive_score = score_row(positive, model)

        for negative in negatives:
            negative_score = score_row(negative, model)

            if positive_score > negative_score:
                wins += 1
            elif positive_score == negative_score:
                ties += 1
            else:
                losses += 1

    comparisons = wins + ties + losses
    accuracy = (
        (wins + 0.5 * ties) / comparisons
        if comparisons
        else 0.0
    )

    return {
        "positiveCount": len(positives),
        "negativeCount": len(negatives),
        "comparisonCount": comparisons,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "pairwiseAccuracy": round(accuracy, 6),
    }


def model_map(
    model: tuple[tuple[str, int, int], ...],
) -> list[dict[str, Any]]:
    return [
        {
            "component": name,
            "direction": "positive" if direction > 0 else "negative",
            "weight": weight,
        }
        for name, direction, weight in model
    ]


def generate_models() -> list[tuple[tuple[str, int, int], ...]]:
    models: list[tuple[tuple[str, int, int], ...]] = []

    for component_count in range(1, MAX_ACTIVE_COMPONENTS + 1):
        for names in combinations(COMPONENT_NAMES, component_count):
            for directions in product(DIRECTIONS, repeat=component_count):
                for weights in product(WEIGHT_VALUES, repeat=component_count):
                    models.append(
                        tuple(
                            (name, direction, weight)
                            for name, direction, weight
                            in zip(names, directions, weights)
                        )
                    )

    return models


def choose_best_model(
    rows: list[dict[str, Any]],
    models: list[tuple[tuple[str, int, int], ...]],
) -> dict[str, Any]:
    candidates = []

    for model in models:
        score = pairwise_accuracy(rows, model)

        candidates.append({
            "model": model,
            "modelMap": model_map(model),
            "activeComponentCount": len(model),
            "totalWeight": sum(item[2] for item in model),
            "trainingScore": score,
        })

    candidates.sort(
        key=lambda item: (
            -item["trainingScore"]["pairwiseAccuracy"],
            item["activeComponentCount"],
            item["totalWeight"],
            tuple(
                (entry["component"], entry["direction"], entry["weight"])
                for entry in item["modelMap"]
            ),
        )
    )

    return candidates[0]


def ranked_rows(
    rows: list[dict[str, Any]],
    model: tuple[tuple[str, int, int], ...],
) -> list[dict[str, Any]]:
    ranking = []

    for row in rows:
        ranking.append({
            "measureNumber": row["measureNumber"],
            "candidateStep": row["candidateStep"],
            "classification": row["classification"],
            "referenceWithinOneStep": row["referenceWithinOneStep"],
            "score": round(score_row(row, model), 6),
            "transitionComponents": row["transitionComponents"],
        })

    ranking.sort(
        key=lambda item: (
            -item["score"],
            item["measureNumber"],
            item["candidateStep"],
        )
    )

    return ranking


def main() -> None:
    payload = load(INPUT_PATH)
    source_rows = payload.get("overallRanking") or []

    rows = [
        enrich_row(row)
        for row in source_rows
        if row.get("section") == "Out-Chorus"
    ]

    if not rows:
        raise ValueError("No Out-Chorus rows found in soft-evidence ranking input")

    positive_count = sum(1 for row in rows if row["referenceWithinOneStep"])
    negative_count = len(rows) - positive_count

    if positive_count == 0 or negative_count == 0:
        raise ValueError(
            "Out-Chorus benchmark requires both positive and negative labels"
        )

    models = generate_models()
    overall_best = choose_best_model(rows, models)
    overall_score = pairwise_accuracy(rows, overall_best["model"])

    measures = sorted({int(row["measureNumber"]) for row in rows})
    holdout_reports = []

    for held_out_measures in combinations(measures, 2):
        holdout_rows = [
            row
            for row in rows
            if int(row["measureNumber"]) in held_out_measures
        ]
        training_rows = [
            row
            for row in rows
            if int(row["measureNumber"]) not in held_out_measures
        ]

        holdout_positive = any(
            row["referenceWithinOneStep"]
            for row in holdout_rows
        )
        holdout_negative = any(
            not row["referenceWithinOneStep"]
            for row in holdout_rows
        )
        training_positive = any(
            row["referenceWithinOneStep"]
            for row in training_rows
        )
        training_negative = any(
            not row["referenceWithinOneStep"]
            for row in training_rows
        )

        if not (
            holdout_positive
            and holdout_negative
            and training_positive
            and training_negative
        ):
            continue

        best = choose_best_model(training_rows, models)
        holdout_score = pairwise_accuracy(holdout_rows, best["model"])

        holdout_reports.append({
            "heldOutMeasures": list(held_out_measures),
            "selectedModel": best["modelMap"],
            "trainingScore": best["trainingScore"],
            "holdoutScore": holdout_score,
            "holdoutRanking": ranked_rows(holdout_rows, best["model"]),
        })

    holdout_accuracies = [
        float(report["holdoutScore"]["pairwiseAccuracy"])
        for report in holdout_reports
    ]

    median_holdout_accuracy = (
        round(median(holdout_accuracies), 6)
        if holdout_accuracies
        else 0.0
    )

    holdouts_at_or_above_065 = sum(
        1 for accuracy in holdout_accuracies if accuracy >= 0.65
    )

    stable = bool(
        holdout_reports
        and median_holdout_accuracy >= 0.65
        and holdouts_at_or_above_065 >= max(1, int(len(holdout_reports) * 0.70))
    )

    report = {
        "schemaVersion": 1,
        "benchmarkType": "out-chorus-transition-ending-soft-ranking",
        "input": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "section": "Out-Chorus",
        "measureRange": [OUT_CHORUS_START, OUT_CHORUS_END],
        "candidateCount": len(rows),
        "positiveCount": positive_count,
        "negativeCount": negative_count,
        "componentNames": list(COMPONENT_NAMES),
        "modelCount": len(models),
        "overallBestModel": overall_best["modelMap"],
        "overallScore": overall_score,
        "overallRanking": ranked_rows(rows, overall_best["model"]),
        "eligibleTwoMeasureHoldoutCount": len(holdout_reports),
        "medianHoldoutAccuracy": median_holdout_accuracy,
        "holdoutsAtOrAbove065": holdouts_at_or_above_065,
        "holdoutReports": holdout_reports,
        "transitionRankingStable": stable,
        "rankingPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Out-Chorus transition ranking V1 complete")
    print("Candidates:", len(rows))
    print("Positive labels:", positive_count)
    print("Negative labels:", negative_count)
    print("Models tested:", len(models))

    print()
    print("OVERALL")
    print("Best model:", overall_best["modelMap"])
    print("Pairwise accuracy:", overall_score["pairwiseAccuracy"])
    print(
        "Wins:", overall_score["wins"],
        "ties:", overall_score["ties"],
        "losses:", overall_score["losses"],
    )

    print()
    print("TWO-MEASURE HOLDOUTS")
    print("Eligible holdouts:", len(holdout_reports))
    print("Median holdout accuracy:", median_holdout_accuracy)
    print(
        "Holdouts at or above 0.65:",
        holdouts_at_or_above_065,
        "/",
        len(holdout_reports),
    )
    print("Transition ranking stable:", stable)

    for holdout in holdout_reports:
        print()
        print("HELD OUT:", holdout["heldOutMeasures"])
        print("Selected model:", holdout["selectedModel"])
        print(
            "Training accuracy:",
            holdout["trainingScore"]["pairwiseAccuracy"],
        )
        print(
            "Holdout accuracy:",
            holdout["holdoutScore"]["pairwiseAccuracy"],
        )

    print()
    print("Ranking promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
