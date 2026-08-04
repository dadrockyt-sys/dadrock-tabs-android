from __future__ import annotations

import json
from itertools import product
from pathlib import Path
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
    / "gomyway-chorus2-prototype-refinement-v1.json"
)

COMPONENT_NAMES = (
    "stemAgreement",
    "phraseSupport",
    "exactPhraseSupport",
    "registerCompatibility",
    "noteActivation",
    "onsetActivation",
)

WEIGHT_VALUES = (0, 1, 2, 3)
REFINEMENT_WEIGHT_VALUES = (0, 1, 2)
REFINEMENT_STRENGTHS = (0.25, 0.50, 0.75, 1.00)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing benchmark input: {path}")

    payload = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(payload, dict):
        raise TypeError("Benchmark input must be a JSON object")

    return payload


def weight_map(weights: tuple[int, ...]) -> dict[str, int]:
    return {
        name: weight
        for name, weight in zip(COMPONENT_NAMES, weights)
    }


def validate_rows(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError("No ranking rows were found in the input artifact")

    for index, row in enumerate(rows):
        components = row.get("softComponents")

        if not isinstance(components, dict):
            raise ValueError(
                f"Ranking row {index} is missing softComponents"
            )

        missing = [
            name
            for name in COMPONENT_NAMES
            if name not in components
        ]

        if missing:
            raise ValueError(
                f"Ranking row {index} is missing components: {missing}"
            )

        if "referenceWithinOneStep" not in row:
            raise ValueError(
                f"Ranking row {index} is missing referenceWithinOneStep"
            )


def component_score(
    row: dict[str, Any],
    weights: tuple[int, ...],
) -> float:
    components = row["softComponents"]
    weighted_sum = 0.0
    total_weight = 0

    for name, weight in zip(COMPONENT_NAMES, weights):
        if weight <= 0:
            continue

        weighted_sum += float(components[name]) * weight
        total_weight += weight

    if total_weight <= 0:
        return 0.0

    return weighted_sum / total_weight


def prototype_score(
    row: dict[str, Any],
    prototype_weights: tuple[int, ...],
) -> float:
    return component_score(row, prototype_weights)


def refined_score(
    row: dict[str, Any],
    prototype_weights: tuple[int, ...],
    refinement_weights: tuple[int, ...],
    refinement_strength: float,
) -> float:
    base = prototype_score(row, prototype_weights)
    refinement = component_score(row, refinement_weights)
    return base + refinement_strength * refinement


def evaluate_scores(
    rows: list[dict[str, Any]],
    score_function: Callable[[dict[str, Any]], float],
) -> dict[str, Any]:
    positives = [
        row
        for row in rows
        if bool(row["referenceWithinOneStep"])
    ]
    negatives = [
        row
        for row in rows
        if not bool(row["referenceWithinOneStep"])
    ]

    if not positives or not negatives:
        raise ValueError(
            "Each evaluated section must contain both positive and negative labels"
        )

    wins = 0
    ties = 0
    losses = 0

    for positive in positives:
        positive_score = float(score_function(positive))

        for negative in negatives:
            negative_score = float(score_function(negative))

            if positive_score > negative_score:
                wins += 1
            elif positive_score == negative_score:
                ties += 1
            else:
                losses += 1

    comparisons = wins + ties + losses
    accuracy = (wins + 0.5 * ties) / comparisons

    return {
        "positiveCount": len(positives),
        "negativeCount": len(negatives),
        "comparisonCount": comparisons,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "pairwiseAccuracy": round(accuracy, 6),
    }


def evaluate_plain_weights(
    rows: list[dict[str, Any]],
    weights: tuple[int, ...],
) -> dict[str, Any]:
    return evaluate_scores(
        rows,
        lambda row: component_score(row, weights),
    )


def choose_chorus1_prototype(
    chorus1_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []

    for weights in product(
        WEIGHT_VALUES,
        repeat=len(COMPONENT_NAMES),
    ):
        if not any(weights):
            continue

        score = evaluate_plain_weights(chorus1_rows, weights)
        active_components = sum(
            1 for weight in weights if weight > 0
        )

        candidates.append(
            {
                "weights": weights,
                "weightMap": weight_map(weights),
                "activeComponentCount": active_components,
                "totalWeight": sum(weights),
                "score": score,
            }
        )

    candidates.sort(
        key=lambda item: (
            -item["score"]["pairwiseAccuracy"],
            item["activeComponentCount"],
            item["totalWeight"],
            item["weights"],
        )
    )

    return candidates[0]


def ranked_rows(
    rows: list[dict[str, Any]],
    score_function: Callable[[dict[str, Any]], float],
) -> list[dict[str, Any]]:
    ranking = []

    for row in rows:
        ranking.append(
            {
                "section": row["section"],
                "measureNumber": row["measureNumber"],
                "candidateStep": row["candidateStep"],
                "classification": row["classification"],
                "referenceWithinOneStep": row[
                    "referenceWithinOneStep"
                ],
                "score": round(float(score_function(row)), 6),
                "softComponents": row["softComponents"],
            }
        )

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

    if not isinstance(source_rows, list):
        raise TypeError("overallRanking must be a list")

    validate_rows(source_rows)

    chorus1_rows = [
        row for row in source_rows if row.get("section") == "Chorus 1"
    ]
    chorus2_rows = [
        row for row in source_rows if row.get("section") == "Chorus 2"
    ]

    validate_rows(chorus1_rows)
    validate_rows(chorus2_rows)

    prototype = choose_chorus1_prototype(chorus1_rows)
    prototype_weights = prototype["weights"]

    chorus1_baseline = evaluate_scores(
        chorus1_rows,
        lambda row: prototype_score(row, prototype_weights),
    )
    chorus2_baseline = evaluate_scores(
        chorus2_rows,
        lambda row: prototype_score(row, prototype_weights),
    )

    refinement_candidates: list[dict[str, Any]] = []

    for refinement_weights in product(
        REFINEMENT_WEIGHT_VALUES,
        repeat=len(COMPONENT_NAMES),
    ):
        if not any(refinement_weights):
            continue

        active_components = sum(
            1 for weight in refinement_weights if weight > 0
        )

        if active_components > 2:
            continue

        for refinement_strength in REFINEMENT_STRENGTHS:
            chorus1_score = evaluate_scores(
                chorus1_rows,
                lambda row,
                weights=refinement_weights,
                strength=refinement_strength: refined_score(
                    row,
                    prototype_weights,
                    weights,
                    strength,
                ),
            )

            if (
                chorus1_score["pairwiseAccuracy"]
                < chorus1_baseline["pairwiseAccuracy"]
            ):
                continue

            chorus2_score = evaluate_scores(
                chorus2_rows,
                lambda row,
                weights=refinement_weights,
                strength=refinement_strength: refined_score(
                    row,
                    prototype_weights,
                    weights,
                    strength,
                ),
            )

            refinement_candidates.append(
                {
                    "refinementWeights": refinement_weights,
                    "refinementWeightMap": weight_map(
                        refinement_weights
                    ),
                    "refinementStrength": refinement_strength,
                    "activeComponentCount": active_components,
                    "totalRefinementWeight": sum(
                        refinement_weights
                    ),
                    "chorus1Score": chorus1_score,
                    "chorus2Score": chorus2_score,
                    "chorus2AccuracyGain": round(
                        chorus2_score["pairwiseAccuracy"]
                        - chorus2_baseline["pairwiseAccuracy"],
                        6,
                    ),
                }
            )

    refinement_candidates.sort(
        key=lambda item: (
            -item["chorus2Score"]["pairwiseAccuracy"],
            -item["chorus2AccuracyGain"],
            item["activeComponentCount"],
            item["totalRefinementWeight"],
            item["refinementStrength"],
            item["refinementWeights"],
        )
    )

    best = refinement_candidates[0] if refinement_candidates else None

    refinement_improves_chorus2 = bool(
        best and best["chorus2AccuracyGain"] > 0
    )
    chorus1_preserved = bool(
        best
        and best["chorus1Score"]["pairwiseAccuracy"]
        >= chorus1_baseline["pairwiseAccuracy"]
    )

    if best:
        best_refinement_weights = best["refinementWeights"]
        best_refinement_strength = best["refinementStrength"]

        chorus1_refined_ranking = ranked_rows(
            chorus1_rows,
            lambda row: refined_score(
                row,
                prototype_weights,
                best_refinement_weights,
                best_refinement_strength,
            ),
        )
        chorus2_refined_ranking = ranked_rows(
            chorus2_rows,
            lambda row: refined_score(
                row,
                prototype_weights,
                best_refinement_weights,
                best_refinement_strength,
            ),
        )
    else:
        chorus1_refined_ranking = []
        chorus2_refined_ranking = []

    report = {
        "schemaVersion": 1,
        "benchmarkType": "chorus1-prototype-chorus2-refinement",
        "input": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "prototypeSection": "Chorus 1",
        "refinementSection": "Chorus 2",
        "outChorusExcluded": True,
        "prototypeWeights": prototype["weightMap"],
        "chorus1BaselineScore": chorus1_baseline,
        "chorus2PrototypeOnlyScore": chorus2_baseline,
        "eligibleRefinementCount": len(refinement_candidates),
        "bestRefinement": (
            {
                key: value
                for key, value in best.items()
                if key != "refinementWeights"
            }
            if best
            else None
        ),
        "chorus1Preserved": chorus1_preserved,
        "chorus2Improved": refinement_improves_chorus2,
        "refinementFeasible": (
            chorus1_preserved and refinement_improves_chorus2
        ),
        "chorus1RefinedRanking": chorus1_refined_ranking,
        "chorus2RefinedRanking": chorus2_refined_ranking,
        "refinementPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Chorus 2 prototype refinement V1 complete")
    print()
    print("CHORUS 1 PROTOTYPE")
    print("Prototype weights:", prototype["weightMap"])
    print(
        "Chorus 1 baseline accuracy:",
        chorus1_baseline["pairwiseAccuracy"],
    )
    print(
        "Chorus 2 prototype-only accuracy:",
        chorus2_baseline["pairwiseAccuracy"],
    )
    print()
    print(
        "Eligible Chorus 1-safe refinements:",
        len(refinement_candidates),
    )

    if best:
        print(
            "Best refinement weights:",
            best["refinementWeightMap"],
        )
        print(
            "Best refinement strength:",
            best["refinementStrength"],
        )
        print(
            "Chorus 1 refined accuracy:",
            best["chorus1Score"]["pairwiseAccuracy"],
        )
        print(
            "Chorus 2 refined accuracy:",
            best["chorus2Score"]["pairwiseAccuracy"],
        )
        print(
            "Chorus 2 accuracy gain:",
            best["chorus2AccuracyGain"],
        )
    else:
        print("No Chorus 1-safe refinement found.")

    print()
    print("Chorus 1 preserved:", chorus1_preserved)
    print("Chorus 2 improved:", refinement_improves_chorus2)
    print(
        "Refinement feasible:",
        chorus1_preserved and refinement_improves_chorus2,
    )
    print("Out-Chorus excluded: True")
    print("Refinement promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
