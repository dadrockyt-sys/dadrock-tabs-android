from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as RAW_CACHE_PATH,
    REFERENCE_PATH,
    _grid_lookup,
)
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_onset_spectral_set_model import (
    _candidate_prior,
    _predict_sets,
    _project,
    _vector as pitch_vector,
)


SPECTRUM_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-spectrum-cache.json"
)
PITCH_MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-learned-onset-spectral-set-model.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-learned-grid-event-selector-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-learned-grid-event-selector-model.json"
)

TRAIN_MEASURES = set(range(1, 9))
VALIDATION_MEASURES = set(range(9, 13))
DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
STEPS_PER_MEASURE = 16

WINDOWS_MS = (50, 75, 100, 125, 150, 200)
L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(17))


def _pct(numerator: float, denominator: float) -> float:
    return round(100.0 * float(numerator) / float(denominator), 3) if denominator else 0.0


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _rows_by_measure(rows: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    out: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        if 1 <= measure <= 16:
            out.setdefault(measure, []).append(row)
    for values in out.values():
        values.sort(key=lambda row: (float(row.get("onsetTime") or 0.0), int(row.get("onsetGroupId") or 0)))
    return out


def _array(row: dict[str, Any], view: str, name: str) -> np.ndarray:
    arr = np.asarray(((row.get(view) or {}).get(name) or []), dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0:
        return np.zeros(1, dtype=np.float64)
    arr[~np.isfinite(arr)] = 0.0
    return arr


def _spectral_summary(row: dict[str, Any]) -> list[float]:
    features: list[float] = []
    for name in ("attackMax", "earlyMean", "sustainMean"):
        a = _array(row, "viewA", name)
        b = _array(row, "viewB", name)
        length = min(a.size, b.size)
        a = a[:length]
        b = b[:length]
        pa = np.maximum(a, 0.0)
        pb = np.maximum(b, 0.0)
        mean_view = 0.5 * (pa + pb)
        norm_a = float(np.linalg.norm(pa))
        norm_b = float(np.linalg.norm(pb))
        corr = 0.0
        if norm_a > 1e-9 and norm_b > 1e-9:
            corr = float(np.dot(pa, pb) / (norm_a * norm_b))
        ordered = np.sort(mean_view)
        top1 = float(ordered[-1]) if ordered.size else 0.0
        top2 = float(ordered[-2]) if ordered.size >= 2 else 0.0
        features.extend(
            [
                float(np.mean(mean_view)) if mean_view.size else 0.0,
                float(np.std(mean_view)) if mean_view.size else 0.0,
                top1,
                top1 - top2,
                norm_a,
                norm_b,
                corr,
            ]
        )
    return features


def _grid_keys(measures: set[int]) -> list[tuple[int, int]]:
    return [(measure, step) for measure in sorted(measures) for step in range(STEPS_PER_MEASURE)]


def _nearby_rows(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    measure: int,
    target_time: float,
    window_ms: int,
) -> list[tuple[float, dict[str, Any]]]:
    window = float(window_ms) / 1000.0
    rows: list[tuple[float, dict[str, Any]]] = []
    for row in rows_by_measure.get(int(measure), []):
        residual = float(row.get("onsetTime") or 0.0) - float(target_time)
        if abs(residual) <= window:
            rows.append((residual, row))
    rows.sort(
        key=lambda item: (
            abs(item[0]),
            -int(item[1].get("stemSupportMax") or 0),
            -int(item[1].get("sweepSupportMax") or 0),
            -int(item[1].get("detectionCountSum") or 0),
            int(item[1].get("onsetGroupId") or 0),
        )
    )
    return rows


def _grid_feature(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    measure: int,
    step: int,
    target_time: float,
    window_ms: int,
) -> tuple[np.ndarray, dict[str, Any] | None]:
    nearby = _nearby_rows(rows_by_measure, measure, target_time, window_ms)
    window_seconds = max(float(window_ms) / 1000.0, 1e-6)
    if nearby:
        residual, nearest = nearby[0]
        supports = [item[1] for item in nearby]
        second_abs = abs(nearby[1][0]) if len(nearby) > 1 else window_seconds
        base = [
            1.0,
            float(residual) / window_seconds,
            abs(float(residual)) / window_seconds,
            float(second_abs) / window_seconds,
            min(len(nearby) / 8.0, 2.0),
            float(nearest.get("candidateCount") or 0) / 49.0,
            float(nearest.get("sourceClusterCount") or 0) / 16.0,
            float(nearest.get("stemSupportMax") or 0) / 2.0,
            float(nearest.get("sweepSupportMax") or 0) / 4.0,
            min(float(nearest.get("detectionCountSum") or 0) / 32.0, 2.0),
            max(float(row.get("stemSupportMax") or 0) for row in supports) / 2.0,
            max(float(row.get("sweepSupportMax") or 0) for row in supports) / 4.0,
            min(sum(float(row.get("detectionCountSum") or 0) for row in supports) / 96.0, 2.0),
        ]
        base.extend(_spectral_summary(nearest))
    else:
        nearest = None
        base = [0.0] * (13 + 21)

    angle = 2.0 * math.pi * float(step) / float(STEPS_PER_MEASURE)
    base.extend([math.sin(angle), math.cos(angle)])
    return np.asarray(base, dtype=np.float64), nearest


def _dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    window_ms: int,
) -> dict[str, Any]:
    xs: list[np.ndarray] = []
    ys: list[float] = []
    keys: list[tuple[int, int]] = []
    nearest_rows: list[dict[str, Any] | None] = []
    active = set(reference)
    for key in _grid_keys(measures):
        target_time = grid.get(key)
        if target_time is None:
            continue
        feature, nearest = _grid_feature(
            rows_by_measure,
            int(key[0]),
            int(key[1]),
            float(target_time),
            int(window_ms),
        )
        xs.append(feature)
        ys.append(1.0 if key in active else 0.0)
        keys.append(key)
        nearest_rows.append(nearest)
    feature_count = 36
    return {
        "X": np.stack(xs, axis=0) if xs else np.zeros((0, feature_count), dtype=np.float64),
        "Y": np.asarray(ys, dtype=np.float64),
        "keys": keys,
        "nearestRows": nearest_rows,
    }


def _fit_scaler(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = X.mean(axis=0) if X.size else np.zeros(X.shape[1], dtype=np.float64)
    std = X.std(axis=0) if X.size else np.ones(X.shape[1], dtype=np.float64)
    std = np.where(std < 1e-6, 1.0, std)
    return mean, std


def _design(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    z = (X - mean) / std
    return np.concatenate([np.ones((z.shape[0], 1), dtype=np.float64), z], axis=1)


def _fit_ridge(Z: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ y


def _evaluate_locations(
    keys: list[tuple[int, int]],
    scores: np.ndarray,
    threshold: float,
    reference: dict[tuple[int, int], set[int]],
) -> dict[str, Any]:
    expected = set(reference)
    predicted = {key for key, score in zip(keys, scores) if float(score) >= float(threshold)}
    correct = len(expected & predicted)
    precision = correct / len(predicted) if predicted else 0.0
    recall = correct / len(expected) if expected else 0.0
    return {
        "referenceLocationCount": len(expected),
        "predictedLocationCount": len(predicted),
        "correctLocationCount": correct,
        "locationPrecisionPercent": _pct(correct, len(predicted)),
        "locationRecallPercent": _pct(correct, len(expected)),
        "locationF1Percent": round(100.0 * _f1(precision, recall), 3),
        "predictedKeys": sorted(predicted),
    }


def _assign_groups_reference_free(
    active_keys: set[tuple[int, int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    window_ms: int,
) -> dict[tuple[int, int], dict[str, Any]]:
    window = float(window_ms) / 1000.0
    assigned: dict[tuple[int, int], dict[str, Any]] = {}
    for measure in sorted({key[0] for key in active_keys}):
        keys = [key for key in sorted(active_keys) if key[0] == measure]
        rows = rows_by_measure.get(measure, [])
        edges: list[tuple[float, int, int, tuple[int, int], dict[str, Any]]] = []
        for key in keys:
            target_time = grid.get(key)
            if target_time is None:
                continue
            for row in rows:
                residual = abs(float(row.get("onsetTime") or 0.0) - float(target_time))
                if residual <= window:
                    edges.append(
                        (
                            residual,
                            -int(row.get("stemSupportMax") or 0),
                            -int(row.get("detectionCountSum") or 0),
                            key,
                            row,
                        )
                    )
        edges.sort(key=lambda item: (item[0], item[1], item[2], item[3], int(item[4].get("onsetGroupId") or 0)))
        used_groups: set[int] = set()
        for _, _, _, key, row in edges:
            group_id = int(row.get("onsetGroupId") or 0)
            if key in assigned or group_id in used_groups:
                continue
            assigned[key] = row
            used_groups.add(group_id)
    return assigned


def _load_pitch_model() -> dict[str, Any]:
    if not PITCH_MODEL_PATH.exists():
        raise RuntimeError(
            "Missing learned spectral pitch model. Run analyzer/v143_intro_learned_onset_spectral_set_model.py first: "
            f"{PITCH_MODEL_PATH}"
        )
    return json.loads(PITCH_MODEL_PATH.read_text())


def _predict_pitch_sets_for_assignments(
    assignments: dict[tuple[int, int], dict[str, Any]],
    grid: dict[tuple[int, int], float],
    pitch_model: dict[str, Any],
) -> dict[tuple[int, int], set[int]]:
    if not assignments:
        return {}
    spectrum_min = int(pitch_model["spectrumMidiMin"])
    spectrum_max = int(pitch_model["spectrumMidiMax"])
    guitar_min = int(pitch_model["guitarMidiMin"])
    guitar_max = int(pitch_model["guitarMidiMax"])
    spectrum_len = spectrum_max - spectrum_min + 1
    pitch_window_ms = int(pitch_model["windowMs"])

    mean = np.asarray(pitch_model["featureMean"], dtype=np.float64)
    std = np.asarray(pitch_model["featureStd"], dtype=np.float64)
    basis = np.asarray(pitch_model["pcaBasis"], dtype=np.float64)
    weights = np.asarray(pitch_model["ridgeWeights"], dtype=np.float64)

    keys = sorted(assignments)
    xs: list[np.ndarray] = []
    priors: list[np.ndarray] = []
    valid_keys: list[tuple[int, int]] = []
    for key in keys:
        row = assignments[key]
        target_time = grid.get(key)
        if target_time is None:
            continue
        residual = float(row.get("onsetTime") or 0.0) - float(target_time)
        xs.append(pitch_vector(row, spectrum_len, residual, pitch_window_ms))
        priors.append(_candidate_prior(row, guitar_min, guitar_max))
        valid_keys.append(key)
    if not xs:
        return {}

    X = np.stack(xs, axis=0)
    P = np.stack(priors, axis=0)
    Z = _project(X, mean, std, basis)
    scores = Z @ weights
    predicted = _predict_sets(
        scores,
        P,
        float(pitch_model["candidatePriorWeight"]),
        float(pitch_model["polyphonyGapZ"]),
        guitar_min,
    )
    return {key: set(value) for key, value in zip(valid_keys, predicted)}


def _evaluate_end_to_end(
    reference: dict[tuple[int, int], set[int]],
    predicted: dict[tuple[int, int], set[int]],
) -> dict[str, Any]:
    reference_locations = len(reference)
    predicted_locations = len(predicted)
    exact_sets = 0
    reference_pitch_events = 0
    predicted_pitch_events = 0
    correct_pitch_events = 0
    correct_locations = 0
    for key in sorted(set(reference) | set(predicted)):
        expected = set(reference.get(key, set()))
        actual = set(predicted.get(key, set()))
        if key in reference and key in predicted:
            correct_locations += 1
        if key in reference:
            reference_pitch_events += len(expected)
            if actual == expected:
                exact_sets += 1
        predicted_pitch_events += len(actual)
        correct_pitch_events += len(expected & actual)
    precision = correct_pitch_events / predicted_pitch_events if predicted_pitch_events else 0.0
    recall = correct_pitch_events / reference_pitch_events if reference_pitch_events else 0.0
    return {
        "referenceLocationCount": reference_locations,
        "predictedLocationCount": predicted_locations,
        "correctLocationCount": correct_locations,
        "locationPrecisionPercent": _pct(correct_locations, predicted_locations),
        "locationRecallPercent": _pct(correct_locations, reference_locations),
        "referencePitchEventCount": reference_pitch_events,
        "predictedPitchEventCount": predicted_pitch_events,
        "correctPitchEventCount": correct_pitch_events,
        "pitchPrecisionPercent": round(100.0 * precision, 3),
        "pitchRecallPercent": round(100.0 * recall, 3),
        "pitchF1Percent": round(100.0 * _f1(precision, recall), 3),
        "exactPitchSetPercent": _pct(exact_sets, reference_locations),
    }


def main() -> None:
    for path in (SPECTRUM_CACHE_PATH, RAW_CACHE_PATH, REFERENCE_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing required file: {path}")

    spectrum_cache = json.loads(SPECTRUM_CACHE_PATH.read_text())
    raw_cache = json.loads(RAW_CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    pitch_model = _load_pitch_model()

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)
    train_reference = _reference_sets(reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    print("=== V143 LEARNED REFERENCE-FREE GRID EVENT SELECTOR ===")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Untouched holdout measures: 13-16")
    print("Pitch model: learned onset-level spectral pitch-set model")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    searched = 0
    total = len(WINDOWS_MS) * len(L2_VALUES) * len(THRESHOLDS)
    for window_ms in WINDOWS_MS:
        train = _dataset(rows_by_measure, grid, train_reference, TRAIN_MEASURES, window_ms)
        validation = _dataset(rows_by_measure, grid, validation_reference, VALIDATION_MEASURES, window_ms)
        mean, std = _fit_scaler(train["X"])
        z_train = _design(train["X"], mean, std)
        z_validation = _design(validation["X"], mean, std)
        for l2 in L2_VALUES:
            weights = _fit_ridge(z_train, train["Y"], l2)
            validation_scores = z_validation @ weights
            for threshold in THRESHOLDS:
                searched += 1
                metrics = _evaluate_locations(
                    validation["keys"],
                    validation_scores,
                    threshold,
                    validation_reference,
                )
                objective = float(metrics["locationF1Percent"])
                candidate = {
                    "windowMs": int(window_ms),
                    "l2": float(l2),
                    "threshold": float(threshold),
                    "validationObjectivePercent": round(objective, 3),
                    "validation": {key: value for key, value in metrics.items() if key != "predictedKeys"},
                }
                if best is None or (
                    objective,
                    float(metrics["locationRecallPercent"]),
                    float(metrics["locationPrecisionPercent"]),
                ) > (
                    float(best["validationObjectivePercent"]),
                    float(best["validation"]["locationRecallPercent"]),
                    float(best["validation"]["locationPrecisionPercent"]),
                ):
                    best = candidate
                if searched % 100 == 0:
                    print(f"searched {searched}/{total} selector configurations")

    if best is None:
        raise RuntimeError("No grid selector configuration evaluated")

    window_ms = int(best["windowMs"])
    development = _dataset(rows_by_measure, grid, development_reference, DEVELOPMENT_MEASURES, window_ms)
    holdout = _dataset(rows_by_measure, grid, holdout_reference, HOLDOUT_MEASURES, window_ms)
    mean, std = _fit_scaler(development["X"])
    z_development = _design(development["X"], mean, std)
    z_holdout = _design(holdout["X"], mean, std)
    weights = _fit_ridge(z_development, development["Y"], float(best["l2"]))
    dev_scores = z_development @ weights
    hold_scores = z_holdout @ weights

    development_location = _evaluate_locations(
        development["keys"], dev_scores, float(best["threshold"]), development_reference
    )
    holdout_location = _evaluate_locations(
        holdout["keys"], hold_scores, float(best["threshold"]), holdout_reference
    )

    dev_active = set(development_location.pop("predictedKeys"))
    hold_active = set(holdout_location.pop("predictedKeys"))
    dev_assignments = _assign_groups_reference_free(dev_active, rows_by_measure, grid, window_ms)
    hold_assignments = _assign_groups_reference_free(hold_active, rows_by_measure, grid, window_ms)
    dev_pitch_sets = _predict_pitch_sets_for_assignments(dev_assignments, grid, pitch_model)
    hold_pitch_sets = _predict_pitch_sets_for_assignments(hold_assignments, grid, pitch_model)
    development_e2e = _evaluate_end_to_end(development_reference, dev_pitch_sets)
    holdout_e2e = _evaluate_end_to_end(holdout_reference, hold_pitch_sets)

    report = {
        "model": "v143-learned-reference-free-grid-event-selector",
        "bestConfiguration": {key: value for key, value in best.items() if key != "validation"},
        "validationLocation": best["validation"],
        "developmentLocation": development_location,
        "holdoutLocation": holdout_location,
        "developmentEndToEnd": development_e2e,
        "holdoutEndToEnd": holdout_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "windowMs": window_ms,
                "l2": float(best["l2"]),
                "threshold": float(best["threshold"]),
                "featureMean": [round(float(value), 8) for value in mean],
                "featureStd": [round(float(value), 8) for value in std],
                "weights": [round(float(value), 8) for value in weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST SELECTOR CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["holdoutLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["holdoutEndToEnd"], indent=2))

    hold_loc_f1 = float(holdout_location["locationF1Percent"])
    hold_pitch_f1 = float(holdout_e2e["pitchF1Percent"])
    hold_exact = float(holdout_e2e["exactPitchSetPercent"])
    if hold_loc_f1 >= 85.0 and hold_pitch_f1 >= 80.0 and hold_exact >= 65.0:
        diagnosis = "reference-free-event-selection-plus-spectral-pitch-decoding-is-strong"
    elif hold_loc_f1 >= 75.0 and hold_pitch_f1 >= 65.0:
        diagnosis = "end-to-end-core-is-promising-refine-event-selector-before-voicing"
    else:
        diagnosis = "pitch-decoder-is-strong-conditionally-but-reference-free-event-selection-remains-bottleneck"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Selector model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
