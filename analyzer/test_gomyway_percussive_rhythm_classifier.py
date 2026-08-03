from __future__ import annotations

import copy
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
BEST_PATH = ROOT / "public" / "training" / "gomyway-rhythm-17-113-v3" / "best.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-percussive-rhythm-classifier-experiment.json"

TRAIN_MEASURES = {28, 58}
VALIDATION_MEASURES = {27, 42}
TARGET_MEASURES = TRAIN_MEASURES | VALIDATION_MEASURES
PERCUSSIVE_TECHNIQUES = {"dead-note", "muted-grace-rake"}


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def event_key(event: dict[str, Any]) -> tuple[int, int]:
    return int(event["measureNumber"]), int(event["quantizedStep"])


def reference_key(measure_number: int, event: dict[str, Any]) -> tuple[int, int]:
    return measure_number, int(event["quantizedStep"])


def is_reference_percussive(event: dict[str, Any] | None) -> bool:
    if not event:
        return False
    techniques = {str(value) for value in event.get("techniques", [])}
    notes = event.get("notes", [])
    return bool(techniques & PERCUSSIVE_TECHNIQUES) or any(int(note.get("fret", 0)) < 0 for note in notes)


def features(event: dict[str, Any]) -> list[float]:
    notes = event.get("notes", [])
    midis = [int(note.get("midi", 0)) for note in notes if note.get("midi") is not None]
    minimum = min(midis) if midis else 0
    maximum = max(midis) if midis else 0
    return [
        float(event.get("confidence") or 0.0),
        float(event.get("durationSteps") or 1),
        float(len(notes)),
        float(minimum),
        float(maximum),
        float(maximum - minimum),
        float(int(event.get("quantizedStep", 0)) % 4),
    ]


def mean(rows: list[list[float]]) -> list[float]:
    return [sum(values) / len(rows) for values in zip(*rows)]


def standard_deviation(rows: list[list[float]], centre: list[float]) -> list[float]:
    result: list[float] = []
    for index in range(len(centre)):
        variance = sum((row[index] - centre[index]) ** 2 for row in rows) / max(1, len(rows) - 1)
        result.append(max(math.sqrt(variance), 1e-6))
    return result


def distance(row: list[float], centre: list[float], scales: list[float]) -> float:
    return math.sqrt(sum(((value - centre[index]) / scales[index]) ** 2 for index, value in enumerate(row)))


def score_measure(
    measure_number: int,
    candidates: list[dict[str, Any]],
    references: list[dict[str, Any]],
) -> dict[str, int]:
    candidate_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    reference_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in candidates:
        candidate_by_step[int(event["quantizedStep"])].append(event)
    for event in references:
        reference_by_step[int(event["quantizedStep"])].append(event)

    result = {
        "measureNumber": measure_number,
        "referenceEvents": len(references),
        "candidateEvents": len(candidates),
        "matchedSteps": 0,
        "percussiveTruePositives": 0,
        "percussiveFalsePositives": 0,
        "percussiveFalseNegatives": 0,
        "exactTechniqueMatches": 0,
        "exactNoteFretMatches": 0,
    }
    for step in sorted(set(candidate_by_step) | set(reference_by_step)):
        refs = reference_by_step.get(step, [])
        cands = candidate_by_step.get(step, [])
        if not refs or not cands:
            for ref in refs:
                if is_reference_percussive(ref):
                    result["percussiveFalseNegatives"] += 1
            for cand in cands:
                if is_reference_percussive(cand):
                    result["percussiveFalsePositives"] += 1
            continue
        result["matchedSteps"] += 1
        ref = refs[0]
        cand = cands[0]
        ref_percussive = is_reference_percussive(ref)
        cand_percussive = is_reference_percussive(cand)
        if ref_percussive and cand_percussive:
            result["percussiveTruePositives"] += 1
        elif cand_percussive and not ref_percussive:
            result["percussiveFalsePositives"] += 1
        elif ref_percussive and not cand_percussive:
            result["percussiveFalseNegatives"] += 1
        if sorted(ref.get("techniques", [])) == sorted(cand.get("techniques", [])):
            result["exactTechniqueMatches"] += 1
        ref_notes = sorted((int(n["string"]), int(n["fret"])) for n in ref.get("notes", []))
        cand_notes = sorted((int(n["string"]), int(n["fret"])) for n in cand.get("notes", []))
        if ref_notes == cand_notes:
            result["exactNoteFretMatches"] += 1
    return result


def main() -> None:
    reference = load(REFERENCE_PATH)
    best = load(BEST_PATH)

    reference_events: dict[tuple[int, int], dict[str, Any]] = {}
    reference_measures: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for measure in reference.get("measures", []):
        number = int(measure["measureNumber"])
        if number not in TARGET_MEASURES:
            continue
        for event in measure.get("events", []):
            reference_events[reference_key(number, event)] = event
            reference_measures[number].append(event)

    candidate_measures: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in best.get("candidateEvents", []):
        number = int(event["measureNumber"])
        if number in TARGET_MEASURES:
            candidate_measures[number].append(copy.deepcopy(event))

    positive_rows: list[list[float]] = []
    negative_rows: list[list[float]] = []
    training_samples: list[dict[str, Any]] = []
    for number in sorted(TRAIN_MEASURES):
        for event in candidate_measures[number]:
            ref = reference_events.get(event_key(event))
            label = is_reference_percussive(ref)
            row = features(event)
            (positive_rows if label else negative_rows).append(row)
            training_samples.append({
                "measureNumber": number,
                "step": int(event["quantizedStep"]),
                "features": row,
                "percussive": label,
            })

    if not positive_rows or not negative_rows:
        raise RuntimeError("Training measures do not contain both percussive and pitched examples")

    all_rows = positive_rows + negative_rows
    global_centre = mean(all_rows)
    scales = standard_deviation(all_rows, global_centre)
    positive_centre = mean(positive_rows)
    negative_centre = mean(negative_rows)

    proposed_measures = copy.deepcopy(candidate_measures)
    predictions: list[dict[str, Any]] = []
    for number in sorted(TARGET_MEASURES):
        ordered = sorted(proposed_measures[number], key=lambda item: int(item["quantizedStep"]))
        for index, event in enumerate(ordered):
            row = features(event)
            positive_distance = distance(row, positive_centre, scales)
            negative_distance = distance(row, negative_centre, scales)
            predicted = positive_distance < negative_distance
            predictions.append({
                "measureNumber": number,
                "step": int(event["quantizedStep"]),
                "predictedPercussive": predicted,
                "positiveDistance": round(positive_distance, 6),
                "negativeDistance": round(negative_distance, 6),
            })
            if not predicted:
                continue

            next_step = int(ordered[index + 1]["quantizedStep"]) if index + 1 < len(ordered) else None
            grace_rake = next_step is not None and 0 < next_step - int(event["quantizedStep"]) <= 1 and len(event.get("notes", [])) >= 2
            stroke = "downstroke" if index % 2 == 0 else "upstroke"
            event["notes"] = [{"string": 3, "fret": -1}]
            event["techniques"] = ["muted-grace-rake" if grace_rake else "dead-note", stroke]
            event["durationSteps"] = min(2, max(1, int(event.get("durationSteps") or 1)))
            event["classification"] = "derived-percussive-rhythm-v1"

    before = {
        number: score_measure(number, candidate_measures[number], reference_measures[number])
        for number in sorted(TARGET_MEASURES)
    }
    after = {
        number: score_measure(number, proposed_measures[number], reference_measures[number])
        for number in sorted(TARGET_MEASURES)
    }

    def aggregate(scores: dict[int, dict[str, int]], measures: set[int]) -> dict[str, int]:
        keys = [
            "matchedSteps",
            "percussiveTruePositives",
            "percussiveFalsePositives",
            "percussiveFalseNegatives",
            "exactTechniqueMatches",
            "exactNoteFretMatches",
        ]
        return {key: sum(scores[number][key] for number in measures) for key in keys}

    validation_before = aggregate(before, VALIDATION_MEASURES)
    validation_after = aggregate(after, VALIDATION_MEASURES)
    validation_improved = (
        validation_after["percussiveTruePositives"] > validation_before["percussiveTruePositives"]
        and validation_after["percussiveFalsePositives"] <= validation_before["percussiveFalsePositives"] + 1
    )

    output = {
        "schemaVersion": 1,
        "title": "Gomyway percussive rhythm classifier experiment",
        "trainingMeasures": sorted(TRAIN_MEASURES),
        "validationMeasures": sorted(VALIDATION_MEASURES),
        "sourceBestAttempt": best.get("attempt"),
        "sourceBestCompositePercent": best.get("compositePercent"),
        "professionalReferenceReadOnly": True,
        "automaticPromotionAllowed": False,
        "protectedBaselinesChanged": False,
        "noSyntheticPitchedNotes": True,
        "classifier": {
            "type": "standardized-nearest-centroid",
            "positiveSampleCount": len(positive_rows),
            "negativeSampleCount": len(negative_rows),
            "positiveCentre": positive_centre,
            "negativeCentre": negative_centre,
            "scales": scales,
        },
        "trainingSamples": training_samples,
        "predictions": predictions,
        "before": before,
        "after": after,
        "validationBefore": validation_before,
        "validationAfter": validation_after,
        "validationImproved": validation_improved,
        "proposedCandidateEvents": [
            event
            for number in sorted(TARGET_MEASURES)
            for event in proposed_measures[number]
        ],
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Percussive rhythm classifier experiment complete")
    print("Training measures:", sorted(TRAIN_MEASURES))
    print("Validation measures:", sorted(VALIDATION_MEASURES))
    print("Positive training samples:", len(positive_rows))
    print("Negative training samples:", len(negative_rows))
    print("Validation before:", validation_before)
    print("Validation after:", validation_after)
    print("Validation improved:", validation_improved)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Automatic promotion allowed: False")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
