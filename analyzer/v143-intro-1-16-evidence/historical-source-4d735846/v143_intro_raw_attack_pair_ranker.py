from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH,
    REFERENCE_PATH,
    _cluster_events,
    _grid_lookup,
)
from v143_intro_supervised_temporal_assignment import (
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    REPO_ROOT,
    _fit_logistic,
    _grade,
    _predict,
    _reference_sets,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-pair-ranker-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-raw-attack-pair-ranker-model.json"
)

WINDOWS_MS = (75, 100, 125, 150, 200)
POSITIVE_WEIGHTS = (2.0, 4.0, 8.0, 12.0)
L2_VALUES = (0.001, 0.01, 0.05)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(15))
MAX_POLYPHONY_VALUES = (1, 2, 3)
NEGATIVE_MULTIPLIER = 50

FEATURE_NAMES = (
    "abs_residual_200ms",
    "signed_residual_200ms",
    "gaussian_25ms",
    "gaussian_50ms",
    "gaussian_75ms",
    "gaussian_100ms",
    "stem_support",
    "sweep_support",
    "detection_count",
    "max_amplitude",
    "mean_amplitude",
    "onset_spread_30ms",
    "production_accepted",
    "target_pitch_competition",
    "target_cluster_density",
    "midi_norm",
)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _gaussian(residual_seconds: float, sigma_seconds: float) -> float:
    return math.exp(-0.5 * (residual_seconds / sigma_seconds) ** 2)


def _grid_rows_for_measures(
    grid: dict[tuple[int, int], float], measures: set[int]
) -> list[tuple[int, int, float]]:
    return [
        (int(measure), int(step), float(time_seconds))
        for (measure, step), time_seconds in sorted(grid.items())
        if int(measure) in measures
    ]


def _clusters_by_measure(clusters: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for cluster in clusters:
        out[int(cluster["measure"])].append(cluster)
    for rows in out.values():
        rows.sort(key=lambda row: (float(row["onsetTime"]), int(row["midi"]), int(row["clusterId"])))
    return out


def _pair_features(
    cluster: dict[str, Any],
    target_time: float,
    measure_clusters: list[dict[str, Any]],
    window_seconds: float,
) -> np.ndarray:
    residual = float(cluster["onsetTime"]) - float(target_time)
    abs_residual = abs(residual)
    nearby = [
        row
        for row in measure_clusters
        if abs(float(row["onsetTime"]) - float(target_time)) <= window_seconds
    ]
    nearby_midis = {int(row["midi"]) for row in nearby}
    same_midi = sum(1 for row in nearby if int(row["midi"]) == int(cluster["midi"]))
    spread = max(0.0, float(cluster["maxOnsetTime"]) - float(cluster["minOnsetTime"]))
    return np.asarray(
        [
            min(abs_residual / 0.200, 2.0),
            max(-2.0, min(2.0, residual / 0.200)),
            _gaussian(residual, 0.025),
            _gaussian(residual, 0.050),
            _gaussian(residual, 0.075),
            _gaussian(residual, 0.100),
            min(float(cluster["stemSupport"]) / 2.0, 1.0),
            min(float(cluster["sweepSupport"]) / 4.0, 1.0),
            min(float(cluster["detectionCount"]) / 8.0, 1.5),
            float(np.clip(_safe_float(cluster.get("maxAmplitude")), 0.0, 1.0)),
            float(np.clip(_safe_float(cluster.get("meanAmplitude")), 0.0, 1.0)),
            min(spread / 0.030, 2.0),
            1.0 if cluster.get("productionAccepted") else 0.0,
            min(float(same_midi) / 4.0, 1.0),
            min(float(len(nearby_midis)) / 24.0, 1.0),
            float(np.clip((int(cluster["midi"]) - 40) / 48.0, 0.0, 1.0)),
        ],
        dtype=np.float64,
    )


def _build_pairs(
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    window_ms: int,
    reference_sets: dict[tuple[int, int], set[int]] | None,
) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int, int, int]]]:
    window_seconds = float(window_ms) / 1000.0
    by_measure = _clusters_by_measure(clusters)
    features: list[np.ndarray] = []
    labels: list[float] = []
    keys: list[tuple[int, int, int, int]] = []

    for measure, step, target_time in _grid_rows_for_measures(grid, measures):
        measure_clusters = by_measure.get(measure, [])
        for cluster in measure_clusters:
            if abs(float(cluster["onsetTime"]) - target_time) > window_seconds:
                continue
            midi = int(cluster["midi"])
            features.append(
                _pair_features(cluster, target_time, measure_clusters, window_seconds)
            )
            positive = (
                reference_sets is not None
                and midi in reference_sets.get((measure, step), set())
            )
            labels.append(1.0 if positive else 0.0)
            keys.append((int(cluster["clusterId"]), measure, step, midi))

    if not features:
        raise RuntimeError(f"No raw attack pairs built for {window_ms} ms window")
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def _downsample_training(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    positives = np.flatnonzero(y > 0.5)
    negatives = np.flatnonzero(y <= 0.5)
    if len(positives) == 0:
        raise RuntimeError("No positive raw-attack training pairs")
    limit = min(len(negatives), len(positives) * NEGATIVE_MULTIPLIER)
    # Prefer hard negatives: strong time alignment and cross-view/sweep support.
    hardness = (
        x[negatives, 3]
        + x[negatives, 5]
        + x[negatives, 6]
        + x[negatives, 7]
        + 0.5 * x[negatives, 9]
    )
    order = np.argsort(-hardness, kind="stable")[:limit]
    selected = np.concatenate([positives, negatives[order]])
    return x[selected], y[selected]


def _decode(
    probabilities: np.ndarray,
    keys: list[tuple[int, int, int, int]],
    *,
    threshold: float,
    max_polyphony: int,
) -> dict[tuple[int, int], set[int]]:
    ranked = sorted(
        [
            (float(probability), cluster_id, measure, step, midi)
            for probability, (cluster_id, measure, step, midi) in zip(probabilities, keys)
            if float(probability) >= float(threshold)
        ],
        key=lambda item: (-item[0], item[2], item[3], item[4], item[1]),
    )
    used_clusters: set[int] = set()
    predicted: dict[tuple[int, int], set[int]] = defaultdict(set)
    for _probability, cluster_id, measure, step, midi in ranked:
        if cluster_id in used_clusters:
            continue
        location = (measure, step)
        if midi in predicted[location]:
            continue
        if len(predicted[location]) >= int(max_polyphony):
            continue
        predicted[location].add(midi)
        used_clusters.add(cluster_id)
    return dict(predicted)


def _availability_recall(
    clusters: list[dict[str, Any]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    window_ms: int,
) -> float:
    window = float(window_ms) / 1000.0
    by_measure = _clusters_by_measure(clusters)
    total = sum(len(midis) for midis in reference.values())
    hits = 0
    for (measure, step), midis in reference.items():
        target = grid.get((measure, step))
        if target is None:
            continue
        for midi in midis:
            if any(
                int(cluster["midi"]) == int(midi)
                and abs(float(cluster["onsetTime"]) - float(target)) <= window
                for cluster in by_measure.get(measure, [])
            ):
                hits += 1
    return round(100.0 * hits / max(total, 1), 3)


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    grid = _grid_lookup(cache)
    clusters = _cluster_events(cache)
    dev_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    print("=== V143 RAW ATTACK CONTINUOUS-TIME PAIR RANKER ===")
    print("physicalAttackClusterCount:", len(clusters))
    print("Professional reference used by analyzer: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    for window_ms in WINDOWS_MS:
        x_dev_all, y_dev_all, keys_dev = _build_pairs(
            clusters, grid, DEVELOPMENT_MEASURES, window_ms, dev_reference
        )
        x_train, y_train = _downsample_training(x_dev_all, y_dev_all)
        availability = _availability_recall(clusters, grid, dev_reference, window_ms)
        print(
            f"window {window_ms:>3}ms: devPairs={len(x_dev_all)} "
            f"positives={int(np.sum(y_dev_all))} availability={availability:.3f}%"
        )

        for positive_weight in POSITIVE_WEIGHTS:
            for l2 in L2_VALUES:
                model = _fit_logistic(
                    x_train,
                    y_train,
                    positive_weight=positive_weight,
                    l2=l2,
                    epochs=320,
                )
                probabilities = _predict(model, x_dev_all)
                for threshold in THRESHOLDS:
                    for max_polyphony in MAX_POLYPHONY_VALUES:
                        prediction = _decode(
                            probabilities,
                            keys_dev,
                            threshold=threshold,
                            max_polyphony=max_polyphony,
                        )
                        grade = _grade(dev_reference, prediction)
                        objective = (
                            0.82 * grade["pitchF1Percent"]
                            + 0.08 * grade["pitchRecallPercent"]
                            + 0.05 * grade["locationF1Percent"]
                            + 0.05 * grade["exactPitchSetPercent"]
                        )
                        trial = {
                            "windowMs": window_ms,
                            "positiveClassWeight": positive_weight,
                            "l2": l2,
                            "threshold": threshold,
                            "maxPolyphony": max_polyphony,
                            "developmentAvailabilityRecallPercent": availability,
                            "developmentObjectivePercent": round(objective, 3),
                            "development": grade,
                        }
                        if best is None or (
                            trial["developmentObjectivePercent"],
                            grade["pitchF1Percent"],
                            grade["pitchRecallPercent"],
                            -grade["predictedPitchEventCount"],
                        ) > (
                            best["trial"]["developmentObjectivePercent"],
                            best["trial"]["development"]["pitchF1Percent"],
                            best["trial"]["development"]["pitchRecallPercent"],
                            -best["trial"]["development"]["predictedPitchEventCount"],
                        ):
                            best = {"trial": trial, "model": model}

    if best is None:
        raise RuntimeError("No raw-attack pair-ranker trial completed")

    trial = best["trial"]
    model = best["model"]
    window_ms = int(trial["windowMs"])
    x_hold, _y_hold, keys_hold = _build_pairs(
        clusters, grid, HOLDOUT_MEASURES, window_ms, None
    )
    p_hold = _predict(model, x_hold)
    hold_prediction = _decode(
        p_hold,
        keys_hold,
        threshold=float(trial["threshold"]),
        max_polyphony=int(trial["maxPolyphony"]),
    )
    hold_grade = _grade(hold_reference, hold_prediction)
    hold_availability = _availability_recall(clusters, grid, hold_reference, window_ms)

    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    config = {k: v for k, v in trial.items() if k != "development"}
    report = {
        "reportVersion": 1,
        "scope": "raw-unaggregated-continuous-time-cluster-to-grid-ranking",
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "featureNames": list(FEATURE_NAMES),
        "bestConfiguration": config,
        "development": trial["development"],
        "holdoutAvailabilityRecallPercent": hold_availability,
        "holdout": hold_grade,
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:12]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "status": "development-only-not-promoted",
                "featureNames": list(FEATURE_NAMES),
                "windowMs": window_ms,
                "threshold": float(trial["threshold"]),
                "maxPolyphony": int(trial["maxPolyphony"]),
                "mean": [float(v) for v in model["mean"]],
                "scale": [float(v) for v in model["scale"]],
                "weights": [float(v) for v in model["weights"]],
                "bias": float(model["bias"]),
                "professionalReferenceRequiredAtRuntime": False,
                "productionPromotionAllowed": False,
            },
            indent=2,
        )
        + "\n"
    )

    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(config, indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(trial["development"], indent=2))
    print()
    print("HOLDOUT AVAILABILITY RECALL:", hold_availability)
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(hold_grade, indent=2))
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
