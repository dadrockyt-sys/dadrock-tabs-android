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


SPECTRUM_CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-spectrum-cache.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-learned-onset-spectral-set-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-learned-onset-spectral-set-model.json"
)

TRAIN_MEASURES = set(range(1, 9))
VALIDATION_MEASURES = set(range(9, 13))
DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))

WINDOWS_MS = (75, 100, 125, 150, 200)
PCA_COMPONENTS = (8, 12, 16, 24, 32, 48)
L2_VALUES = (0.01, 0.1, 1.0, 10.0)
CANDIDATE_PRIOR_WEIGHTS = (0.0, 0.10, 0.25, 0.50)
POLYPHONY_GAPS = (0.25, 0.50, 0.75, 1.00, 1.50)
MAX_POLYPHONY = 3


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


def _assign_rows_one_to_one(
    by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    window_ms: int,
) -> dict[tuple[int, int], dict[str, Any]]:
    window = float(window_ms) / 1000.0
    assigned: dict[tuple[int, int], dict[str, Any]] = {}
    for measure in sorted({key[0] for key in reference}):
        locations = [key for key in sorted(reference) if key[0] == measure]
        rows = by_measure.get(measure, [])
        edges: list[tuple[float, int, int, tuple[int, int], dict[str, Any]]] = []
        for key in locations:
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


def _vector(row: dict[str, Any], spectrum_len: int, residual_seconds: float, window_ms: int) -> np.ndarray:
    values: list[float] = []
    for view in ("viewA", "viewB"):
        for name in ("attackMax", "earlyMean", "sustainMean"):
            arr = np.asarray(((row.get(view) or {}).get(name) or []), dtype=np.float64)
            if arr.ndim != 1 or arr.size != spectrum_len:
                raise RuntimeError(
                    f"Bad spectral vector onsetGroupId={row.get('onsetGroupId')} {view}/{name}: {arr.shape}"
                )
            arr[~np.isfinite(arr)] = 0.0
            values.extend(arr.tolist())
    window_seconds = max(float(window_ms) / 1000.0, 1e-6)
    values.extend(
        [
            float(residual_seconds) / window_seconds,
            abs(float(residual_seconds)) / window_seconds,
            float(row.get("candidateCount") or 0) / 49.0,
            float(row.get("stemSupportMax") or 0) / 2.0,
            float(row.get("sweepSupportMax") or 0) / 4.0,
            min(float(row.get("detectionCountSum") or 0) / 32.0, 2.0),
        ]
    )
    return np.asarray(values, dtype=np.float64)


def _candidate_prior(row: dict[str, Any], guitar_min: int, guitar_max: int) -> np.ndarray:
    length = guitar_max - guitar_min + 1
    prior = np.zeros(length, dtype=np.float64)
    raw = {
        int(value)
        for value in (row.get("candidateMidis") or [])
        if guitar_min <= int(value) <= guitar_max
    }
    for midi in raw:
        prior[midi - guitar_min] = max(prior[midi - guitar_min], 1.0)
        if midi - 12 >= guitar_min:
            prior[midi - 12 - guitar_min] = max(prior[midi - 12 - guitar_min], 0.45)
        if midi - 19 >= guitar_min:
            prior[midi - 19 - guitar_min] = max(prior[midi - 19 - guitar_min], 0.25)
    return prior


def _dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    window_ms: int,
    spectrum_len: int,
    guitar_min: int,
    guitar_max: int,
) -> dict[str, Any]:
    assigned = _assign_rows_one_to_one(rows_by_measure, grid, reference, window_ms)
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    priors: list[np.ndarray] = []
    keys: list[tuple[int, int]] = []
    covered_pitch_events = 0
    for key in sorted(reference):
        row = assigned.get(key)
        if row is None:
            continue
        target_time = grid.get(key)
        if target_time is None:
            continue
        residual = float(row.get("onsetTime") or 0.0) - float(target_time)
        xs.append(_vector(row, spectrum_len, residual, window_ms))
        label = np.zeros(guitar_max - guitar_min + 1, dtype=np.float64)
        for midi in reference[key]:
            if guitar_min <= int(midi) <= guitar_max:
                label[int(midi) - guitar_min] = 1.0
                covered_pitch_events += 1
        ys.append(label)
        priors.append(_candidate_prior(row, guitar_min, guitar_max))
        keys.append(key)
    feature_count = 6 * spectrum_len + 6
    return {
        "X": np.stack(xs, axis=0) if xs else np.zeros((0, feature_count), dtype=np.float64),
        "Y": np.stack(ys, axis=0) if ys else np.zeros((0, guitar_max - guitar_min + 1), dtype=np.float64),
        "P": np.stack(priors, axis=0) if priors else np.zeros((0, guitar_max - guitar_min + 1), dtype=np.float64),
        "keys": keys,
        "assigned": assigned,
        "referenceLocationCount": len(reference),
        "referencePitchEventCount": sum(len(value) for value in reference.values()),
        "coveredPitchEventCount": covered_pitch_events,
    }


def _fit_projection(X: np.ndarray, components: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X.mean(axis=0) if X.size else np.zeros(X.shape[1], dtype=np.float64)
    std = X.std(axis=0) if X.size else np.ones(X.shape[1], dtype=np.float64)
    std = np.where(std < 1e-6, 1.0, std)
    standardized = (X - mean) / std
    if standardized.shape[0] == 0:
        return mean, std, np.zeros((X.shape[1], 0), dtype=np.float64)
    _, _, vt = np.linalg.svd(standardized, full_matrices=False)
    k = max(1, min(int(components), vt.shape[0], vt.shape[1]))
    basis = vt[:k].T
    return mean, std, basis


def _project(X: np.ndarray, mean: np.ndarray, std: np.ndarray, basis: np.ndarray) -> np.ndarray:
    standardized = (X - mean) / std
    reduced = standardized @ basis
    return np.concatenate([np.ones((reduced.shape[0], 1), dtype=np.float64), reduced], axis=1)


def _fit_ridge(Z: np.ndarray, Y: np.ndarray, l2: float) -> np.ndarray:
    if Z.shape[0] == 0:
        return np.zeros((Z.shape[1], Y.shape[1]), dtype=np.float64)
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ Y


def _predict_sets(
    scores: np.ndarray,
    priors: np.ndarray,
    prior_weight: float,
    polyphony_gap: float,
    guitar_min: int,
) -> list[set[int]]:
    combined = scores + float(prior_weight) * priors
    predicted: list[set[int]] = []
    for row in combined:
        if row.size == 0:
            predicted.append(set())
            continue
        row_mean = float(np.mean(row))
        row_std = float(np.std(row))
        z = (row - row_mean) / max(row_std, 1e-6)
        order = np.argsort(-z)
        best = float(z[order[0]])
        selected = [int(order[0])]
        for index in order[1:MAX_POLYPHONY]:
            if best - float(z[index]) <= float(polyphony_gap):
                selected.append(int(index))
            else:
                break
        predicted.append({guitar_min + index for index in selected})
    return predicted


def _evaluate_dataset(
    data: dict[str, Any],
    reference: dict[tuple[int, int], set[int]],
    predicted_sets: list[set[int]],
) -> dict[str, Any]:
    by_key = {key: pred for key, pred in zip(data["keys"], predicted_sets)}
    reference_locations = len(reference)
    covered_locations = len(data["keys"])
    exact_sets = 0
    reference_pitch_events = 0
    predicted_pitch_events = 0
    correct_pitch_events = 0
    for key, expected in sorted(reference.items()):
        reference_pitch_events += len(expected)
        predicted = by_key.get(key, set())
        predicted_pitch_events += len(predicted)
        correct_pitch_events += len(predicted & set(expected))
        if predicted == set(expected):
            exact_sets += 1
    precision = correct_pitch_events / predicted_pitch_events if predicted_pitch_events else 0.0
    recall = correct_pitch_events / reference_pitch_events if reference_pitch_events else 0.0
    return {
        "referenceLocationCount": reference_locations,
        "coveredLocationCount": covered_locations,
        "referenceLocationCoveragePercent": _pct(covered_locations, reference_locations),
        "referencePitchEventCount": reference_pitch_events,
        "predictedPitchEventCount": predicted_pitch_events,
        "correctPitchEventCount": correct_pitch_events,
        "pitchPrecisionPercent": round(100.0 * precision, 3),
        "pitchRecallPercent": round(100.0 * recall, 3),
        "pitchF1Percent": round(100.0 * _f1(precision, recall), 3),
        "exactPitchSetPercent": _pct(exact_sets, reference_locations),
    }


def _objective(metrics: dict[str, Any]) -> float:
    return 0.75 * float(metrics["pitchF1Percent"]) + 0.25 * float(metrics["exactPitchSetPercent"])


def main() -> None:
    if not SPECTRUM_CACHE_PATH.exists():
        raise RuntimeError(f"Missing onset spectrum cache: {SPECTRUM_CACHE_PATH}")
    if not RAW_CACHE_PATH.exists():
        raise RuntimeError(f"Missing raw attack cache: {RAW_CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    spectrum_cache = json.loads(SPECTRUM_CACHE_PATH.read_text())
    raw_cache = json.loads(RAW_CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)

    train_reference = _reference_sets(reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    spectrum_min = int(spectrum_cache.get("spectrumMidiMin") or 28)
    spectrum_max = int(spectrum_cache.get("spectrumMidiMax") or 112)
    guitar_min = int(spectrum_cache.get("guitarMidiMin") or 40)
    guitar_max = int(spectrum_cache.get("guitarMidiMax") or 88)
    spectrum_len = spectrum_max - spectrum_min + 1

    print("=== V143 LEARNED ONSET-LEVEL SPECTRAL PITCH-SET MODEL ===")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Untouched holdout measures: 13-16")
    print("Output pitch range:", f"{guitar_min}..{guitar_max}")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    total = len(WINDOWS_MS) * len(PCA_COMPONENTS) * len(L2_VALUES) * len(CANDIDATE_PRIOR_WEIGHTS) * len(POLYPHONY_GAPS)
    count = 0

    for window_ms in WINDOWS_MS:
        train = _dataset(rows_by_measure, grid, train_reference, window_ms, spectrum_len, guitar_min, guitar_max)
        validation = _dataset(rows_by_measure, grid, validation_reference, window_ms, spectrum_len, guitar_min, guitar_max)
        if train["X"].shape[0] < 8 or validation["X"].shape[0] < 4:
            continue
        for components in PCA_COMPONENTS:
            mean, std, basis = _fit_projection(train["X"], components)
            z_train = _project(train["X"], mean, std, basis)
            z_validation = _project(validation["X"], mean, std, basis)
            for l2 in L2_VALUES:
                weights = _fit_ridge(z_train, train["Y"], l2)
                validation_scores = z_validation @ weights
                for prior_weight in CANDIDATE_PRIOR_WEIGHTS:
                    for gap in POLYPHONY_GAPS:
                        count += 1
                        predicted = _predict_sets(
                            validation_scores,
                            validation["P"],
                            prior_weight,
                            gap,
                            guitar_min,
                        )
                        metrics = _evaluate_dataset(validation, validation_reference, predicted)
                        objective = _objective(metrics)
                        candidate = {
                            "windowMs": int(window_ms),
                            "pcaComponents": int(min(components, basis.shape[1])),
                            "l2": float(l2),
                            "candidatePriorWeight": float(prior_weight),
                            "polyphonyGapZ": float(gap),
                            "validationObjectivePercent": round(objective, 3),
                            "validation": metrics,
                        }
                        if best is None or (
                            objective,
                            metrics["pitchF1Percent"],
                            metrics["exactPitchSetPercent"],
                            -predicted.__len__(),
                        ) > (
                            float(best["validationObjectivePercent"]),
                            float(best["validation"]["pitchF1Percent"]),
                            float(best["validation"]["exactPitchSetPercent"]),
                            -len(predicted),
                        ):
                            best = candidate
                        if count % 500 == 0:
                            print(f"searched {count}/{total} configurations")

    if best is None:
        raise RuntimeError("No learned spectral configuration evaluated")

    # Retrain the selected architecture on all development measures, then touch
    # the holdout exactly once.
    window_ms = int(best["windowMs"])
    development = _dataset(rows_by_measure, grid, development_reference, window_ms, spectrum_len, guitar_min, guitar_max)
    holdout = _dataset(rows_by_measure, grid, holdout_reference, window_ms, spectrum_len, guitar_min, guitar_max)
    mean, std, basis = _fit_projection(development["X"], int(best["pcaComponents"]))
    z_development = _project(development["X"], mean, std, basis)
    z_holdout = _project(holdout["X"], mean, std, basis)
    weights = _fit_ridge(z_development, development["Y"], float(best["l2"]))

    dev_scores = z_development @ weights
    hold_scores = z_holdout @ weights
    dev_pred = _predict_sets(
        dev_scores,
        development["P"],
        float(best["candidatePriorWeight"]),
        float(best["polyphonyGapZ"]),
        guitar_min,
    )
    hold_pred = _predict_sets(
        hold_scores,
        holdout["P"],
        float(best["candidatePriorWeight"]),
        float(best["polyphonyGapZ"]),
        guitar_min,
    )
    development_metrics = _evaluate_dataset(development, development_reference, dev_pred)
    holdout_metrics = _evaluate_dataset(holdout, holdout_reference, hold_pred)

    report = {
        "model": "v143-learned-onset-level-spectral-multilabel-ridge",
        "bestConfiguration": {key: value for key, value in best.items() if key != "validation"},
        "validation": best["validation"],
        "development": development_metrics,
        "holdout": holdout_metrics,
        "developmentLocationCoveragePercent": development_metrics["referenceLocationCoveragePercent"],
        "holdoutLocationCoveragePercent": holdout_metrics["referenceLocationCoveragePercent"],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    model_payload = {
        "model": report["model"],
        "windowMs": window_ms,
        "spectrumMidiMin": spectrum_min,
        "spectrumMidiMax": spectrum_max,
        "guitarMidiMin": guitar_min,
        "guitarMidiMax": guitar_max,
        "featureMean": [round(float(value), 8) for value in mean],
        "featureStd": [round(float(value), 8) for value in std],
        "pcaBasis": [[round(float(value), 8) for value in row] for row in basis],
        "ridgeWeights": [[round(float(value), 8) for value in row] for row in weights],
        "candidatePriorWeight": float(best["candidatePriorWeight"]),
        "polyphonyGapZ": float(best["polyphonyGapZ"]),
        "professionalReferenceRequiredAtRuntime": False,
    }
    MODEL_PATH.write_text(json.dumps(model_payload, separators=(",", ":")) + "\n")

    print("\n=== BEST DEVELOPMENT CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION 9-12 ===")
    print(json.dumps(report["validation"], indent=2))
    print("\n=== DEVELOPMENT 1-12 ===")
    print(json.dumps(report["development"], indent=2))
    print("\n=== HOLDOUT 13-16 (never used to choose configuration) ===")
    print(json.dumps(report["holdout"], indent=2))

    hold_f1 = float(holdout_metrics["pitchF1Percent"])
    exact = float(holdout_metrics["exactPitchSetPercent"])
    if hold_f1 >= 45.0 and exact >= 30.0:
        diagnosis = "learned-onset-spectral-set-model-is-promising"
    elif hold_f1 >= 25.0:
        diagnosis = "learned-spectrum-helps-but-needs-stronger-sequence-structure"
    else:
        diagnosis = "single-song-supervision-insufficient-expand-training-or-use-sequence-model"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
