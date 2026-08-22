from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-pitch-recovery-neighbor-sweep.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
Q_VALUES = (0.95, 1.00)
RADII = (0, 1, 2)
TOP_K_VALUES = (1, 2, 3)
SECOND_RATIO_VALUES = (0.0, 0.72, 0.84)
RECURRENCE_WEIGHTS = (0.0, 0.75, 1.5, 2.5)
DISTANCE_PENALTIES = (0.4, 0.9, 1.4)
SOURCE_WEIGHTS = (0.75, 1.25)
AMPLITUDE_WEIGHTS = (0.5, 1.0)


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (
        int(row.get("measure", row.get("measureNumber", 0)) or 0),
        int(row.get("step", 0) or 0),
    )


def _reference_events(payload: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number < 1 or number > 16:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            event = dict(raw)
            event["measureNumber"] = number
            out.append(event)
    return out


def _hypotheses(row: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for raw in row.get("pitchHypotheses", []) or []:
        if not isinstance(raw, dict):
            continue
        midi = _int(raw.get("midi"))
        if midi is None:
            continue
        item = dict(raw)
        item["midi"] = midi
        values.append(item)
    return values


def _percent(n: int, d: int) -> float:
    return round(100.0 * n / d, 3) if d else 100.0


def _f1(precision: float, recall: float) -> float:
    if precision + recall <= 0.0:
        return 0.0
    return round(2.0 * precision * recall / (precision + recall), 3)


def _retained_rows(rows: list[dict[str, Any]], q: float) -> list[dict[str, Any]]:
    ordered = sorted(
        rows,
        key=lambda row: (
            _float(row.get("v143Score"), -1e30),
            -int(row.get("measure") or 0),
            -int(row.get("step") or 0),
        ),
        reverse=True,
    )
    k = max(1, int(round(float(q) * len(ordered))))
    return ordered[:k]


def _rows_by_measure(rows: Iterable[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        out[int(row.get("measure") or 0)].append(row)
    for measure_rows in out.values():
        measure_rows.sort(key=lambda row: int(row.get("step") or 0))
    return out


def _recurrence_support(
    all_rows: list[dict[str, Any]],
    radius: int,
) -> dict[tuple[int, int], float]:
    """Reference-free support for MIDI recurring near the same within-measure step."""
    by_measure = _rows_by_measure(all_rows)
    measures = sorted(m for m in by_measure if 1 <= m <= 16)
    support: dict[tuple[int, int], float] = {}
    for target_step in range(16):
        midi_to_measures: dict[int, set[int]] = defaultdict(set)
        for measure in measures:
            for row in by_measure[measure]:
                step = int(row.get("step") or 0)
                if abs(step - target_step) > radius:
                    continue
                for hypothesis in _hypotheses(row):
                    midi_to_measures[int(hypothesis["midi"])].add(measure)
        denom = max(1, len(measures))
        for midi, found in midi_to_measures.items():
            support[(target_step, midi)] = len(found) / float(denom)
    return support


def _predict(
    rows: list[dict[str, Any]],
    *,
    q: float,
    radius: int,
    top_k: int,
    second_ratio: float,
    recurrence_weight: float,
    distance_penalty: float,
    source_weight: float,
    amplitude_weight: float,
) -> tuple[set[tuple[int, int]], set[tuple[int, int, int]]]:
    retained = _retained_rows(rows, q)
    retained_locations = {_location(row) for row in retained}
    all_by_measure = _rows_by_measure(rows)
    recurrence = _recurrence_support(rows, radius)

    predicted_pitches: set[tuple[int, int, int]] = set()
    for row in retained:
        measure, target_step = _location(row)
        aggregate: dict[int, float] = defaultdict(lambda: -1e30)
        evidence_count: dict[int, int] = defaultdict(int)

        for neighbor in all_by_measure.get(measure, []):
            neighbor_step = int(neighbor.get("step") or 0)
            delta = abs(neighbor_step - target_step)
            if delta > radius:
                continue
            for hypothesis in _hypotheses(neighbor):
                midi = int(hypothesis["midi"])
                source_count = _float(hypothesis.get("sourceCount"))
                max_amp = _float(hypothesis.get("maxAmplitude"))
                mean_amp = _float(hypothesis.get("meanAmplitude"))
                max_duration = min(1.5, _float(hypothesis.get("maxDuration")))
                min_grid_error = min(0.20, _float(hypothesis.get("minGridError")))
                recurrence_value = recurrence.get((target_step, midi), 0.0)

                score = (
                    source_weight * source_count
                    + amplitude_weight * max_amp
                    + 0.25 * mean_amp
                    + 0.35 * max_duration
                    - 3.0 * min_grid_error
                    - distance_penalty * float(delta)
                    + recurrence_weight * recurrence_value
                )
                aggregate[midi] = max(aggregate[midi], score)
                evidence_count[midi] += 1

        if not aggregate:
            continue
        ordered = sorted(
            aggregate,
            key=lambda midi: (
                aggregate[midi] + 0.08 * max(0, evidence_count[midi] - 1),
                recurrence.get((target_step, midi), 0.0),
                -midi,
            ),
            reverse=True,
        )
        best_score = aggregate[ordered[0]]
        selected: list[int] = []
        for midi in ordered:
            if len(selected) >= top_k:
                break
            if selected and second_ratio > 0.0:
                # Shift scores positive before applying a relative second-note gate.
                denom = max(1e-6, abs(best_score) + 1.0)
                relative_gap = (best_score - aggregate[midi]) / denom
                if relative_gap > (1.0 - second_ratio):
                    continue
            selected.append(midi)
        for midi in selected:
            predicted_pitches.add((measure, target_step, midi))

    return retained_locations, predicted_pitches


def _grade(
    reference_events: list[dict[str, Any]],
    predicted_locations: set[tuple[int, int]],
    predicted_pitches: set[tuple[int, int, int]],
    measures: set[int],
) -> dict[str, float | int]:
    reference_subset = [
        event for event in reference_events
        if int(event["measureNumber"]) in measures
    ]
    reference_locations = {
        (int(event["measureNumber"]), int(event.get("step") or 0))
        for event in reference_subset
    }
    reference_pitches = {
        (
            int(event["measureNumber"]),
            int(event.get("step") or 0),
            int(event.get("midiPitch") or 0),
        )
        for event in reference_subset
    }
    predicted_locations_subset = {
        value for value in predicted_locations if value[0] in measures
    }
    predicted_pitches_subset = {
        value for value in predicted_pitches if value[0] in measures
    }

    loc_tp = len(reference_locations & predicted_locations_subset)
    pitch_tp = len(reference_pitches & predicted_pitches_subset)
    loc_precision = _percent(loc_tp, len(predicted_locations_subset))
    loc_recall = _percent(loc_tp, len(reference_locations))
    pitch_precision = _percent(pitch_tp, len(predicted_pitches_subset))
    pitch_recall = _percent(pitch_tp, len(reference_pitches))

    return {
        "referenceLocationCount": len(reference_locations),
        "predictedLocationCount": len(predicted_locations_subset),
        "locationPrecisionPercent": loc_precision,
        "locationRecallPercent": loc_recall,
        "locationF1Percent": _f1(loc_precision, loc_recall),
        "referencePitchEventCount": len(reference_pitches),
        "predictedPitchEventCount": len(predicted_pitches_subset),
        "pitchPrecisionPercent": pitch_precision,
        "pitchRecallPercent": pitch_recall,
        "pitchF1Percent": _f1(pitch_precision, pitch_recall),
    }


def _oracle_recall(
    rows: list[dict[str, Any]],
    reference_events: list[dict[str, Any]],
    radius: int,
    measures: set[int],
) -> float:
    by_measure = _rows_by_measure(rows)
    hits = 0
    total = 0
    for event in reference_events:
        measure = int(event["measureNumber"])
        if measure not in measures:
            continue
        total += 1
        target_step = int(event.get("step") or 0)
        midi = int(event.get("midiPitch") or 0)
        found = False
        for row in by_measure.get(measure, []):
            if abs(int(row.get("step") or 0) - target_step) > radius:
                continue
            if any(int(h["midi"]) == midi for h in _hypotheses(row)):
                found = True
                break
        hits += int(found)
    return _percent(hits, total)


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    rows = [
        dict(row)
        for row in ((cache.get("analysis") or {}).get("introRows") or [])
        if isinstance(row, dict)
    ]
    if not rows:
        raise RuntimeError("Analysis cache contains no intro rows")
    refs = _reference_events(reference)

    results: list[dict[str, Any]] = []
    for q in Q_VALUES:
        for radius in RADII:
            for top_k in TOP_K_VALUES:
                for second_ratio in SECOND_RATIO_VALUES:
                    for recurrence_weight in RECURRENCE_WEIGHTS:
                        for distance_penalty in DISTANCE_PENALTIES:
                            for source_weight in SOURCE_WEIGHTS:
                                for amplitude_weight in AMPLITUDE_WEIGHTS:
                                    locations, pitches = _predict(
                                        rows,
                                        q=q,
                                        radius=radius,
                                        top_k=top_k,
                                        second_ratio=second_ratio,
                                        recurrence_weight=recurrence_weight,
                                        distance_penalty=distance_penalty,
                                        source_weight=source_weight,
                                        amplitude_weight=amplitude_weight,
                                    )
                                    dev = _grade(refs, locations, pitches, DEVELOPMENT_MEASURES)
                                    holdout = _grade(refs, locations, pitches, HOLDOUT_MEASURES)
                                    objective = round(
                                        0.72 * float(dev["pitchF1Percent"])
                                        + 0.28 * float(dev["locationF1Percent"]),
                                        3,
                                    )
                                    results.append(
                                        {
                                            "configuration": {
                                                "q": q,
                                                "radius": radius,
                                                "topK": top_k,
                                                "secondRatio": second_ratio,
                                                "recurrenceWeight": recurrence_weight,
                                                "distancePenalty": distance_penalty,
                                                "sourceWeight": source_weight,
                                                "amplitudeWeight": amplitude_weight,
                                            },
                                            "development": dev,
                                            "holdout": holdout,
                                            "developmentObjectivePercent": objective,
                                        }
                                    )

    results.sort(
        key=lambda row: (
            float(row["developmentObjectivePercent"]),
            float(row["holdout"]["pitchF1Percent"]),
            float(row["holdout"]["pitchRecallPercent"]),
        ),
        reverse=True,
    )
    best = results[0]

    report = {
        "sweepVersion": 1,
        "scope": "professional-intro-measures-1-16",
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "rawRowCount": len(rows),
        "oraclePitchRecallPercent": {
            str(radius): {
                "development": _oracle_recall(rows, refs, radius, DEVELOPMENT_MEASURES),
                "holdout": _oracle_recall(rows, refs, radius, HOLDOUT_MEASURES),
            }
            for radius in RADII
        },
        "bestDevelopmentConfiguration": best,
        "topDevelopmentRows": results[:20],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedByOfflineDevelopmentGrader": True,
        "productionModified": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 LOCAL NEIGHBOR PITCH RECOVERY SWEEP ===")
    print("rows:", len(rows))
    print("oraclePitchRecallPercent:", report["oraclePitchRecallPercent"])
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(best["configuration"], indent=2))
    print("DEVELOPMENT:")
    print(json.dumps(best["development"], indent=2))
    print("HOLDOUT (measures 13-16, not used to choose weights):")
    print(json.dumps(best["holdout"], indent=2))
    print("developmentObjectivePercent:", best["developmentObjectivePercent"])
    print("Professional reference used by analyzer: False")
    print("Production modified: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
