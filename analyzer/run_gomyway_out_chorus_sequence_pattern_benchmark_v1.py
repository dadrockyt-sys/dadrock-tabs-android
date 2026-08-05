from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "public" / "gomyway-chorus-soft-evidence-ranking-v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-out-chorus-sequence-pattern-benchmark-v1.json"

OUT_CHORUS_START = 103
OUT_CHORUS_END = 110
STEP_COUNT = 16


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input: {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def circular_distance(a: int, b: int) -> int:
    direct = abs(a - b)
    return min(direct, STEP_COUNT - direct)


def nearest_step_distance(step: int, steps: list[int]) -> int:
    if not steps:
        return STEP_COUNT // 2
    return min(circular_distance(step, other) for other in steps)


def pattern_similarity(first: dict[str, Any], second: dict[str, Any]) -> float:
    first_steps = first["allSteps"]
    second_steps = second["allSteps"]

    if not first_steps and not second_steps:
        return 1.0
    if not first_steps or not second_steps:
        return 0.0

    forward = sum(
        1.0 - nearest_step_distance(step, second_steps) / 8.0
        for step in first_steps
    ) / len(first_steps)
    backward = sum(
        1.0 - nearest_step_distance(step, first_steps) / 8.0
        for step in second_steps
    ) / len(second_steps)

    density_ratio = min(len(first_steps), len(second_steps)) / max(
        len(first_steps), len(second_steps)
    )

    return max(0.0, min(1.0, 0.4 * forward + 0.4 * backward + 0.2 * density_ratio))


def sequence_similarity(first: dict[str, Any], second: dict[str, Any]) -> float:
    left = pattern_similarity(first["firstMeasure"], second["firstMeasure"])
    right = pattern_similarity(first["secondMeasure"], second["secondMeasure"])
    transition = 1.0 - min(
        1.0,
        abs(first["densityDelta"] - second["densityDelta"]) / 8.0,
    )
    return 0.4 * left + 0.4 * right + 0.2 * transition


def measure_patterns(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[int(row["measureNumber"])].append(row)

    patterns: dict[int, dict[str, Any]] = {}
    for measure in range(OUT_CHORUS_START, OUT_CHORUS_END + 1):
        measure_rows = grouped.get(measure, [])
        all_steps = sorted({int(row["candidateStep"]) for row in measure_rows})
        positive_steps = sorted({
            int(row["candidateStep"])
            for row in measure_rows
            if row["referenceWithinOneStep"]
        })
        negative_steps = sorted({
            int(row["candidateStep"])
            for row in measure_rows
            if not row["referenceWithinOneStep"]
        })

        patterns[measure] = {
            "measureNumber": measure,
            "allSteps": all_steps,
            "positiveSteps": positive_steps,
            "negativeSteps": negative_steps,
            "candidateCount": len(measure_rows),
            "positiveCount": len(positive_steps),
            "negativeCount": len(negative_steps),
            "positiveFraction": (
                len(positive_steps) / len(all_steps)
                if all_steps
                else 0.0
            ),
        }

    return patterns


def adjacent_sequences(patterns: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    sequences = []
    for measure in range(OUT_CHORUS_START, OUT_CHORUS_END):
        first = patterns[measure]
        second = patterns[measure + 1]
        total_candidates = first["candidateCount"] + second["candidateCount"]
        total_positives = first["positiveCount"] + second["positiveCount"]
        quality = total_positives / total_candidates if total_candidates else 0.0

        sequences.append({
            "startMeasure": measure,
            "endMeasure": measure + 1,
            "firstMeasure": first,
            "secondMeasure": second,
            "densityDelta": second["candidateCount"] - first["candidateCount"],
            "positiveFraction": quality,
            "positiveSequence": quality >= 0.5,
        })
    return sequences


def evaluate_leave_one_out(sequences: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reports = []
    for held_out in sequences:
        training = [item for item in sequences if item is not held_out]
        if not training:
            continue

        scored = [
            (sequence_similarity(held_out, candidate), candidate)
            for candidate in training
        ]
        scored.sort(key=lambda item: (-item[0], item[1]["startMeasure"]))
        nearest_similarity, nearest = scored[0]
        prediction = bool(nearest["positiveSequence"])
        actual = bool(held_out["positiveSequence"])

        reports.append({
            "heldOutMeasures": [held_out["startMeasure"], held_out["endMeasure"]],
            "nearestTrainingMeasures": [nearest["startMeasure"], nearest["endMeasure"]],
            "nearestSimilarity": round(nearest_similarity, 6),
            "predictedPositiveSequence": prediction,
            "actualPositiveSequence": actual,
            "correct": prediction == actual,
        })
    return reports


def main() -> None:
    payload = load(INPUT_PATH)
    rows = [
        row
        for row in (payload.get("overallRanking") or [])
        if row.get("section") == "Out-Chorus"
    ]
    if not rows:
        raise ValueError("No Out-Chorus rows found")

    patterns = measure_patterns(rows)
    sequences = adjacent_sequences(patterns)
    holdouts = evaluate_leave_one_out(sequences)

    accuracies = [1.0 if item["correct"] else 0.0 for item in holdouts]
    accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
    median_similarity = median(
        [float(item["nearestSimilarity"]) for item in holdouts]
    ) if holdouts else 0.0

    stable = bool(
        len(holdouts) >= 5
        and accuracy >= 0.70
        and median_similarity >= 0.60
    )

    report = {
        "schemaVersion": 1,
        "benchmarkType": "out-chorus-adjacent-measure-pattern-nearest-neighbor",
        "input": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "measureRange": [OUT_CHORUS_START, OUT_CHORUS_END],
        "measurePatterns": [patterns[key] for key in sorted(patterns)],
        "adjacentSequences": sequences,
        "leaveOneSequenceOutReports": holdouts,
        "holdoutCount": len(holdouts),
        "holdoutAccuracy": round(accuracy, 6),
        "medianNearestSimilarity": round(median_similarity, 6),
        "sequencePatternStable": stable,
        "patternFamilyPromoted": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Out-Chorus sequence-pattern benchmark V1 complete")
    print("Measures:", len(patterns))
    print("Adjacent sequences:", len(sequences))
    print("Holdout accuracy:", report["holdoutAccuracy"])
    print("Median nearest similarity:", report["medianNearestSimilarity"])
    print("Sequence pattern stable:", stable)
    for item in holdouts:
        print(
            "heldOut=", item["heldOutMeasures"],
            "nearest=", item["nearestTrainingMeasures"],
            "similarity=", item["nearestSimilarity"],
            "correct=", item["correct"],
        )
    print("Pattern family promoted: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
