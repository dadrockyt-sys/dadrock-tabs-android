from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


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
    / "intro-supervised-pitch-ranker-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-pitch-ranker-model.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
RADII = (1, 2)
POSITIVE_CLASS_WEIGHTS = (2.0, 4.0, 8.0, 12.0)
L2_VALUES = (0.001, 0.01, 0.05, 0.10)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(17))
TOP_K_VALUES = (1, 2, 3)

FEATURE_NAMES = (
    "exact_present",
    "nearest_support",
    "support_row_fraction",
    "distance_weighted_support",
    "max_source_count",
    "mean_source_count",
    "max_event_count",
    "max_amplitude",
    "mean_amplitude",
    "grid_accuracy",
    "max_duration",
    "dominant_exact",
    "dominant_support_fraction",
    "v143_rank_percentile",
    "v143_selected",
    "target_pitch_count",
    "same_step_measure_recurrence",
    "distance_from_target_dominant",
)


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _global_step(row: dict[str, Any]) -> int:
    measure = int(row.get("measure", row.get("measureNumber", 0)) or 0)
    step = int(row.get("step", 0) or 0)
    return (measure - 1) * 16 + step


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (
        int(row.get("measure", row.get("measureNumber", 0)) or 0),
        int(row.get("step", 0) or 0),
    )


def _reference_by_location(payload: dict[str, Any]) -> dict[tuple[int, int], set[int]]:
    out: dict[tuple[int, int], set[int]] = {}
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number < 1 or number > 16:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            midi = _int(event.get("midiPitch"))
            if midi is None:
                continue
            step = int(event.get("step") or 0)
            out.setdefault((number, step), set()).add(midi)
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


def _midi_set(row: dict[str, Any]) -> set[int]:
    return {int(item["midi"]) for item in _hypotheses(row)}


def _rank_percentile(row: dict[str, Any], total_rows: int) -> float:
    rank = _int(row.get("v143Rank"))
    if rank is None or total_rows <= 1:
        return 0.5
    return float(np.clip(1.0 - (rank - 1) / float(total_rows - 1), 0.0, 1.0))


def _build_feature_context(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_global = {_global_step(row): row for row in rows}
    by_location = {_location(row): row for row in rows}
    total_rows = len(rows)
    return {
        "rows": rows,
        "byGlobal": by_global,
        "byLocation": by_location,
        "totalRows": total_rows,
    }


def _candidate_midis_for_target(
    target: dict[str, Any],
    context: dict[str, Any],
    radius: int,
) -> set[int]:
    center = _global_step(target)
    values: set[int] = set()
    for delta in range(-radius, radius + 1):
        row = context["byGlobal"].get(center + delta)
        if row is not None:
            values.update(_midi_set(row))
    return values


def _features_for_candidate(
    target: dict[str, Any],
    midi: int,
    context: dict[str, Any],
    radius: int,
) -> np.ndarray:
    center = _global_step(target)
    observations: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    dominant_support = 0
    exact_present = 0.0
    dominant_exact = 0.0

    for delta in range(-radius, radius + 1):
        row = context["byGlobal"].get(center + delta)
        if row is None:
            continue
        if _int(row.get("dominantMidi")) == midi:
            dominant_support += 1
            if delta == 0:
                dominant_exact = 1.0
        for hypothesis in _hypotheses(row):
            if int(hypothesis["midi"]) == midi:
                observations.append((delta, hypothesis, row))
                if delta == 0:
                    exact_present = 1.0

    if not observations:
        raise ValueError("candidate MIDI has no supporting observation")

    abs_deltas = [abs(delta) for delta, _hyp, _row in observations]
    support_deltas = {delta for delta, _hyp, _row in observations}
    nearest_delta = min(abs_deltas)
    normalizer = sum(1.0 / (1.0 + abs(delta)) for delta in range(-radius, radius + 1))
    weighted_support = sum(1.0 / (1.0 + abs(delta)) for delta in support_deltas)

    source_counts = [_float(hyp.get("sourceCount")) for _d, hyp, _r in observations]
    event_counts = [_float(hyp.get("eventCount")) for _d, hyp, _r in observations]
    max_amplitudes = [_float(hyp.get("maxAmplitude")) for _d, hyp, _r in observations]
    mean_amplitudes = [_float(hyp.get("meanAmplitude")) for _d, hyp, _r in observations]
    grid_errors = [_float(hyp.get("minGridError"), 0.10) for _d, hyp, _r in observations]
    durations = [_float(hyp.get("maxDuration")) for _d, hyp, _r in observations]

    target_measure, target_step = _location(target)
    recurrence_hits = 0
    recurrence_total = 0
    for measure_delta in (-2, -1, 1, 2):
        measure = target_measure + measure_delta
        if measure < 1 or measure > 16:
            continue
        recurrence_total += 1
        row = context["byLocation"].get((measure, target_step))
        if row is not None and midi in _midi_set(row):
            recurrence_hits += 1

    target_dominant = _int(target.get("dominantMidi"))
    dominant_distance = (
        min(1.0, abs(midi - target_dominant) / 12.0)
        if target_dominant is not None
        else 1.0
    )

    target_pitch_count = max(1, int(target.get("candidatePitchCount") or len(_hypotheses(target)) or 1))
    neighborhood_size = float(2 * radius + 1)

    return np.asarray(
        [
            exact_present,
            1.0 / (1.0 + nearest_delta),
            len(support_deltas) / neighborhood_size,
            weighted_support / max(normalizer, 1e-9),
            min(1.0, max(source_counts, default=0.0) / 2.0),
            min(1.0, (sum(source_counts) / max(len(source_counts), 1)) / 2.0),
            min(1.0, max(event_counts, default=0.0) / 4.0),
            float(np.clip(max(max_amplitudes, default=0.0), 0.0, 1.0)),
            float(np.clip(max(mean_amplitudes, default=0.0), 0.0, 1.0)),
            float(np.clip(1.0 - min(grid_errors, default=0.10) / 0.10, 0.0, 1.0)),
            float(np.clip(max(durations, default=0.0) / 1.0, 0.0, 1.0)),
            dominant_exact,
            dominant_support / neighborhood_size,
            _rank_percentile(target, int(context["totalRows"])),
            1.0 if target.get("v143Selected") is True else 0.0,
            float(np.clip(target_pitch_count / 8.0, 0.0, 1.0)),
            recurrence_hits / float(max(recurrence_total, 1)),
            dominant_distance,
        ],
        dtype=np.float64,
    )


def _dataset(
    rows: list[dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    radius: int,
) -> tuple[np.ndarray, np.ndarray, list[tuple[tuple[int, int], int]]]:
    context = _build_feature_context(rows)
    features: list[np.ndarray] = []
    labels: list[float] = []
    keys: list[tuple[tuple[int, int], int]] = []

    for target in rows:
        location = _location(target)
        if location[0] not in measures:
            continue
        positives = reference_by_loc.get(location, set())
        for midi in sorted(_candidate_midis_for_target(target, context, radius)):
            features.append(_features_for_candidate(target, midi, context, radius))
            labels.append(1.0 if midi in positives else 0.0)
            keys.append((location, midi))

    if not features:
        raise RuntimeError("No pitch-ranking examples were built")
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    positive_weight: float,
    l2: float,
    epochs: int = 800,
    learning_rate: float = 0.08,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    xn = (x - mean) / scale

    weights = np.zeros(xn.shape[1], dtype=np.float64)
    bias = 0.0
    sample_weight = np.where(y > 0.5, float(positive_weight), 1.0)
    denom = float(np.sum(sample_weight))

    for epoch in range(epochs):
        probabilities = _sigmoid(xn @ weights + bias)
        error = (probabilities - y) * sample_weight
        gradient = (xn.T @ error) / denom + float(l2) * weights
        bias_gradient = float(np.sum(error) / denom)
        step = learning_rate / math.sqrt(1.0 + epoch / 200.0)
        weights -= step * gradient
        bias -= step * bias_gradient

    return {
        "mean": mean,
        "scale": scale,
        "weights": weights,
        "bias": float(bias),
    }


def _predict(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xn = (x - model["mean"]) / model["scale"]
    return _sigmoid(xn @ model["weights"] + float(model["bias"]))


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _percent(value: float) -> float:
    return round(100.0 * value, 3)


def _evaluate(
    probabilities: np.ndarray,
    keys: list[tuple[tuple[int, int], int]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    *,
    threshold: float,
    top_k: int,
) -> dict[str, Any]:
    grouped: dict[tuple[int, int], list[tuple[int, float]]] = {}
    for probability, (location, midi) in zip(probabilities, keys):
        grouped.setdefault(location, []).append((midi, float(probability)))

    predicted: dict[tuple[int, int], set[int]] = {}
    for location, candidates in grouped.items():
        selected = [item for item in sorted(candidates, key=lambda item: (-item[1], item[0])) if item[1] >= threshold]
        if selected:
            predicted[location] = {int(midi) for midi, _score in selected[:top_k]}

    reference = {
        location: set(midis)
        for location, midis in reference_by_loc.items()
        if location[0] in measures
    }
    reference_locations = set(reference)
    predicted_locations = set(predicted)
    location_hits = len(reference_locations & predicted_locations)
    location_precision = location_hits / max(len(predicted_locations), 1)
    location_recall = location_hits / max(len(reference_locations), 1)

    reference_event_count = sum(len(values) for values in reference.values())
    predicted_event_count = sum(len(values) for values in predicted.values())
    pitch_hits = sum(len(predicted.get(location, set()) & expected) for location, expected in reference.items())
    pitch_precision = pitch_hits / max(predicted_event_count, 1)
    pitch_recall = pitch_hits / max(reference_event_count, 1)

    exact_sets = sum(1 for location, expected in reference.items() if predicted.get(location, set()) == expected)
    exact_set_rate = exact_sets / max(len(reference), 1)

    return {
        "referenceLocationCount": len(reference_locations),
        "predictedLocationCount": len(predicted_locations),
        "locationPrecisionPercent": _percent(location_precision),
        "locationRecallPercent": _percent(location_recall),
        "locationF1Percent": _percent(_f1(location_precision, location_recall)),
        "referencePitchEventCount": reference_event_count,
        "predictedPitchEventCount": predicted_event_count,
        "pitchPrecisionPercent": _percent(pitch_precision),
        "pitchRecallPercent": _percent(pitch_recall),
        "pitchF1Percent": _percent(_f1(pitch_precision, pitch_recall)),
        "exactPitchSetPercent": _percent(exact_set_rate),
    }


def _oracle_recall(
    rows: list[dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    radius: int,
) -> float:
    context = _build_feature_context(rows)
    hits = 0
    total = 0
    rows_by_loc = {_location(row): row for row in rows}
    for location, expected in reference_by_loc.items():
        if location[0] not in measures:
            continue
        target = rows_by_loc.get(location)
        for midi in expected:
            total += 1
            if target is not None and midi in _candidate_midis_for_target(target, context, radius):
                hits += 1
    return _percent(hits / max(total, 1))


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    rows = [dict(row) for row in cache.get("analysis", {}).get("introRows", []) or []]
    if not rows:
        raise RuntimeError("Analysis cache contains no intro rows")

    reference_by_loc = _reference_by_location(reference_payload)
    best: dict[str, Any] | None = None
    trials: list[dict[str, Any]] = []

    for radius in RADII:
        x_dev, y_dev, keys_dev = _dataset(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius)
        x_hold, _y_hold, keys_hold = _dataset(rows, reference_by_loc, HOLDOUT_MEASURES, radius)

        for positive_weight in POSITIVE_CLASS_WEIGHTS:
            for l2 in L2_VALUES:
                model = _fit_logistic(
                    x_dev,
                    y_dev,
                    positive_weight=positive_weight,
                    l2=l2,
                )
                p_dev = _predict(model, x_dev)
                p_hold = _predict(model, x_hold)

                for threshold in THRESHOLDS:
                    for top_k in TOP_K_VALUES:
                        development = _evaluate(
                            p_dev,
                            keys_dev,
                            reference_by_loc,
                            DEVELOPMENT_MEASURES,
                            threshold=threshold,
                            top_k=top_k,
                        )
                        objective = (
                            0.75 * development["pitchF1Percent"]
                            + 0.15 * development["locationF1Percent"]
                            + 0.10 * development["exactPitchSetPercent"]
                        )
                        trial = {
                            "radius": radius,
                            "positiveClassWeight": positive_weight,
                            "l2": l2,
                            "threshold": threshold,
                            "topK": top_k,
                            "developmentObjectivePercent": round(objective, 3),
                            "development": development,
                        }
                        trials.append(trial)
                        if best is None or (
                            trial["developmentObjectivePercent"],
                            development["pitchF1Percent"],
                            development["pitchRecallPercent"],
                            -development["predictedPitchEventCount"],
                        ) > (
                            best["trial"]["developmentObjectivePercent"],
                            best["trial"]["development"]["pitchF1Percent"],
                            best["trial"]["development"]["pitchRecallPercent"],
                            -best["trial"]["development"]["predictedPitchEventCount"],
                        ):
                            best = {
                                "trial": trial,
                                "model": model,
                                "holdout": _evaluate(
                                    p_hold,
                                    keys_hold,
                                    reference_by_loc,
                                    HOLDOUT_MEASURES,
                                    threshold=threshold,
                                    top_k=top_k,
                                ),
                            }

    if best is None:
        raise RuntimeError("No supervised pitch-ranker configuration was evaluated")

    trial = best["trial"]
    model = best["model"]
    holdout = best["holdout"]
    radius = int(trial["radius"])

    model_payload = {
        "schemaVersion": 1,
        "status": "development-only-not-promoted",
        "featureNames": list(FEATURE_NAMES),
        "radiusSteps": radius,
        "threshold": float(trial["threshold"]),
        "topK": int(trial["topK"]),
        "mean": [float(value) for value in model["mean"]],
        "scale": [float(value) for value in model["scale"]],
        "weights": [float(value) for value in model["weights"]],
        "bias": float(model["bias"]),
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "professionalReferenceUsedForTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionPromotionAllowed": False,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(model_payload, indent=2) + "\n")

    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    report = {
        "reportVersion": 1,
        "scope": "professional-intro-pitch-ranking",
        "oraclePitchRecallPercent": {
            "development": _oracle_recall(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius),
            "holdout": _oracle_recall(rows, reference_by_loc, HOLDOUT_MEASURES, radius),
        },
        "bestConfiguration": {
            key: value
            for key, value in trial.items()
            if key not in {"development"}
        },
        "development": trial["development"],
        "holdout": holdout,
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:10]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "modelPath": str(MODEL_PATH.relative_to(REPO_ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 SUPERVISED PITCH EVIDENCE RANKER ===")
    print("rows:", len(rows))
    print("developmentPositiveExamples:", int(sum(_dataset(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius)[1])))
    print("oraclePitchRecallPercent:", report["oraclePitchRecallPercent"])
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print()
    print("DEVELOPMENT:")
    print(json.dumps(report["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(report["holdout"], indent=2))
    print()
    print("TOP MODEL COEFFICIENTS:")
    print(json.dumps(report["topCoefficients"], indent=2))
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
