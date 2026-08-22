from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import CACHE_PATH as RAW_CACHE_PATH, REFERENCE_PATH, _grid_lookup
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    MODEL_PATH as BASE_SELECTOR_MODEL_PATH,
    TRAIN_MEASURES,
    VALIDATION_MEASURES,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    _rows_by_measure,
    _grid_keys,
    _grid_feature,
    _assign_groups_reference_free,
    _predict_pitch_sets_for_assignments,
    _evaluate_end_to_end,
    _pct,
    _f1,
)
from v143_intro_repetition_recovery_event_selector import _load_json, _score_measures


OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-sequence-event-model-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-sequence-event-model.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)
PCA_COMPONENTS = (8, 12, 16, 24, 32, 48, 64)
L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
THRESHOLDS = tuple(round(0.10 + 0.05 * index, 2) for index in range(17))


def _location_metrics(
    reference: dict[tuple[int, int], set[int]],
    active: set[tuple[int, int]],
) -> dict[str, Any]:
    expected = set(reference)
    correct = len(expected & active)
    precision = correct / len(active) if active else 0.0
    recall = correct / len(expected) if expected else 0.0
    return {
        "referenceLocationCount": len(expected),
        "predictedLocationCount": len(active),
        "correctLocationCount": correct,
        "locationPrecisionPercent": _pct(correct, len(active)),
        "locationRecallPercent": _pct(correct, len(expected)),
        "locationF1Percent": round(100.0 * _f1(precision, recall), 3),
    }


def _safe_score(scores: dict[tuple[int, int], float], key: tuple[int, int]) -> float:
    value = scores.get(key, 0.0)
    try:
        value = float(value)
        return value if math.isfinite(value) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _sequence_context(
    key: tuple[int, int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    context_measures: set[int],
    base_threshold: float,
) -> list[float]:
    measure, step = key
    values: list[float] = []

    # Local rhythmic context in the same measure.
    local_scores: list[float] = []
    local_evidence: list[float] = []
    for delta in (-3, -2, -1, 0, 1, 2, 3):
        source_step = step + delta
        if 0 <= source_step < 16:
            score = _safe_score(scores, (measure, source_step))
            has_evidence = 1.0 if evidence.get((measure, source_step), False) else 0.0
        else:
            score = 0.0
            has_evidence = 0.0
        values.extend([score, has_evidence])
        local_scores.append(score)
        local_evidence.append(has_evidence)

    local = np.asarray(local_scores, dtype=np.float64)
    values.extend(
        [
            float(np.mean(local)),
            float(np.std(local)),
            float(np.max(local)),
            float(np.min(local)),
            sum(score >= base_threshold for score in local_scores) / 7.0,
            sum(local_evidence) / 7.0,
        ]
    )

    # Same rhythmic position across the analyzed context. These are entirely
    # label-free recurrence features and can use the full uploaded section at runtime.
    peers = [other for other in sorted(context_measures) if other != measure]
    peer_scores = [_safe_score(scores, (other, step)) for other in peers]
    if peer_scores:
        peer = np.asarray(peer_scores, dtype=np.float64)
        values.extend(
            [
                float(np.mean(peer)),
                float(np.std(peer)),
                float(np.max(peer)),
                float(np.median(peer)),
                sum(score >= base_threshold for score in peer_scores) / len(peer_scores),
            ]
        )
    else:
        values.extend([0.0] * 5)

    for modulus in (2, 4):
        phase = (measure - 1) % modulus
        phase_peers = [
            other
            for other in sorted(context_measures)
            if other != measure and (other - 1) % modulus == phase
        ]
        phase_scores = [_safe_score(scores, (other, step)) for other in phase_peers]
        if phase_scores:
            arr = np.asarray(phase_scores, dtype=np.float64)
            values.extend(
                [
                    float(np.mean(arr)),
                    float(np.max(arr)),
                    float(np.median(arr)),
                    sum(score >= base_threshold for score in phase_scores) / len(phase_scores),
                ]
            )
        else:
            values.extend([0.0] * 4)

    # Adjacent-measure continuity at the same rhythmic position.
    for delta_measure in (-2, -1, 1, 2):
        other = measure + delta_measure
        if other in context_measures:
            values.extend(
                [
                    _safe_score(scores, (other, step)),
                    1.0 if evidence.get((other, step), False) else 0.0,
                ]
            )
        else:
            values.extend([0.0, 0.0])

    return values


def _feature_for_key(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    key: tuple[int, int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    context_measures: set[int],
    base_threshold: float,
) -> tuple[np.ndarray, bool]:
    target_time = grid.get(key)
    if target_time is None:
        raise RuntimeError(f"Missing grid time for {key}")

    features: list[float] = []
    wide_evidence = False
    # Multi-scale current-position evidence prevents the original selector's
    # narrow chosen window from imposing a hard recall ceiling.
    for window_ms in WINDOWS_MS:
        vector, nearest = _grid_feature(
            rows_by_measure,
            int(key[0]),
            int(key[1]),
            float(target_time),
            int(window_ms),
        )
        features.extend(np.asarray(vector, dtype=np.float64).tolist())
        wide_evidence = wide_evidence or nearest is not None

    current_score = _safe_score(scores, key)
    features.extend(
        [
            current_score,
            current_score - float(base_threshold),
            1.0 if evidence.get(key, False) else 0.0,
        ]
    )
    features.extend(
        _sequence_context(
            key,
            scores,
            evidence,
            context_measures,
            float(base_threshold),
        )
    )
    return np.asarray(features, dtype=np.float64), bool(wide_evidence)


def _dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    base_threshold: float,
) -> dict[str, Any]:
    active_reference = set(reference)
    xs: list[np.ndarray] = []
    ys: list[float] = []
    keys: list[tuple[int, int]] = []
    wide_evidence: list[bool] = []
    for key in _grid_keys(measures):
        if key not in grid:
            continue
        feature, has_wide_evidence = _feature_for_key(
            rows_by_measure,
            grid,
            key,
            scores,
            evidence,
            context_measures,
            base_threshold,
        )
        xs.append(feature)
        ys.append(1.0 if key in active_reference else 0.0)
        keys.append(key)
        wide_evidence.append(has_wide_evidence)
    if not xs:
        return {
            "X": np.zeros((0, 1), dtype=np.float64),
            "Y": np.zeros(0, dtype=np.float64),
            "keys": [],
            "wideEvidence": [],
        }
    return {
        "X": np.stack(xs, axis=0),
        "Y": np.asarray(ys, dtype=np.float64),
        "keys": keys,
        "wideEvidence": wide_evidence,
    }


def _fit_projection(
    X: np.ndarray,
    components: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    standardized = (X - mean) / std
    _, _, vt = np.linalg.svd(standardized, full_matrices=False)
    k = max(1, min(int(components), vt.shape[0], vt.shape[1]))
    basis = vt[:k].T
    return mean, std, basis


def _project(
    X: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    reduced = ((X - mean) / std) @ basis
    return np.concatenate([np.ones((reduced.shape[0], 1), dtype=np.float64), reduced], axis=1)


def _fit_ridge(Z: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ y


def _active_from_scores(
    keys: list[tuple[int, int]],
    scores: np.ndarray,
    wide_evidence: list[bool],
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key, score, has_evidence in zip(keys, scores, wide_evidence)
        if has_evidence and float(score) >= float(threshold)
    }


def _evaluate_e2e(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    pitch_model: dict[str, Any],
) -> dict[str, Any]:
    # Use the pitch model's own learned temporal window for one-to-one onset
    # assignment. Event selection itself already uses evidence out to 200 ms.
    assignments = _assign_groups_reference_free(
        active,
        rows_by_measure,
        grid,
        int(pitch_model["windowMs"]),
    )
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)
    return _evaluate_end_to_end(reference, pitch_sets)


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)

    train_reference = _reference_sets(reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    all_measures = set(range(1, 17))
    base_scores, base_evidence = _score_measures(
        rows_by_measure,
        grid,
        all_measures,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])

    print("=== V143 MULTISCALE SEQUENCE EVENT MODEL ===")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Measures 13-16: diagnostic only, not fresh untouched holdout")
    print("Windows:", WINDOWS_MS)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    train = _dataset(
        rows_by_measure,
        grid,
        train_reference,
        TRAIN_MEASURES,
        TRAIN_MEASURES,
        base_scores,
        base_evidence,
        base_threshold,
    )
    validation = _dataset(
        rows_by_measure,
        grid,
        validation_reference,
        VALIDATION_MEASURES,
        set(range(1, 13)),
        base_scores,
        base_evidence,
        base_threshold,
    )

    best: dict[str, Any] | None = None
    searched = 0
    total = len(PCA_COMPONENTS) * len(L2_VALUES) * len(THRESHOLDS)
    for components in PCA_COMPONENTS:
        mean, std, basis = _fit_projection(train["X"], components)
        z_train = _project(train["X"], mean, std, basis)
        z_validation = _project(validation["X"], mean, std, basis)
        for l2 in L2_VALUES:
            weights = _fit_ridge(z_train, train["Y"], l2)
            validation_scores = z_validation @ weights
            for threshold in THRESHOLDS:
                searched += 1
                active = _active_from_scores(
                    validation["keys"],
                    validation_scores,
                    validation["wideEvidence"],
                    threshold,
                )
                loc = _location_metrics(validation_reference, active)
                precision = float(loc["locationPrecisionPercent"])
                recall = float(loc["locationRecallPercent"])
                f1 = float(loc["locationF1Percent"])
                # Recall matters because the conditional pitch decoder is already
                # highly precise; keep enough precision that recovered events do not
                # overwhelm the tab with false attacks.
                objective = 0.55 * f1 + 0.30 * recall + 0.15 * precision
                if precision < 70.0:
                    objective -= (70.0 - precision) * 1.5
                candidate = {
                    "pcaComponents": int(components),
                    "l2": float(l2),
                    "threshold": float(threshold),
                    "validationObjectivePercent": round(objective, 3),
                    "validationLocation": loc,
                }
                if best is None or (
                    objective,
                    f1,
                    recall,
                    precision,
                ) > (
                    float(best["validationObjectivePercent"]),
                    float(best["validationLocation"]["locationF1Percent"]),
                    float(best["validationLocation"]["locationRecallPercent"]),
                    float(best["validationLocation"]["locationPrecisionPercent"]),
                ):
                    best = candidate
                if searched % 100 == 0 or searched == total:
                    print(f"searched {searched}/{total} sequence configurations")

    if best is None:
        raise RuntimeError("No sequence-event configuration evaluated")

    development = _dataset(
        rows_by_measure,
        grid,
        development_reference,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        base_scores,
        base_evidence,
        base_threshold,
    )
    holdout = _dataset(
        rows_by_measure,
        grid,
        holdout_reference,
        HOLDOUT_MEASURES,
        all_measures,
        base_scores,
        base_evidence,
        base_threshold,
    )

    mean, std, basis = _fit_projection(development["X"], int(best["pcaComponents"]))
    z_development = _project(development["X"], mean, std, basis)
    z_holdout = _project(holdout["X"], mean, std, basis)
    weights = _fit_ridge(z_development, development["Y"], float(best["l2"]))
    development_scores = z_development @ weights
    holdout_scores = z_holdout @ weights

    development_active = _active_from_scores(
        development["keys"],
        development_scores,
        development["wideEvidence"],
        float(best["threshold"]),
    )
    holdout_active = _active_from_scores(
        holdout["keys"],
        holdout_scores,
        holdout["wideEvidence"],
        float(best["threshold"]),
    )

    development_location = _location_metrics(development_reference, development_active)
    holdout_location = _location_metrics(holdout_reference, holdout_active)
    development_e2e = _evaluate_e2e(
        development_active,
        development_reference,
        rows_by_measure,
        grid,
        pitch_model,
    )
    holdout_e2e = _evaluate_e2e(
        holdout_active,
        holdout_reference,
        rows_by_measure,
        grid,
        pitch_model,
    )

    report = {
        "model": "v143-multiscale-sequence-event-model",
        "bestConfiguration": {
            "pcaComponents": best["pcaComponents"],
            "l2": best["l2"],
            "threshold": best["threshold"],
            "validationObjectivePercent": best["validationObjectivePercent"],
        },
        "validationLocation": best["validationLocation"],
        "developmentLocation": development_location,
        "developmentEndToEnd": development_e2e,
        "diagnosticHoldoutLocation": holdout_location,
        "diagnosticHoldoutEndToEnd": holdout_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because prior architecture iterations inspected them. Use a fresh song/section before production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "windowsMs": list(WINDOWS_MS),
                "baseSelectorThreshold": base_threshold,
                "pcaComponents": int(best["pcaComponents"]),
                "l2": float(best["l2"]),
                "threshold": float(best["threshold"]),
                "featureMean": [round(float(value), 8) for value in mean],
                "featureStd": [round(float(value), 8) for value in std],
                "pcaBasis": [[round(float(value), 8) for value in row] for row in basis.tolist()],
                "ridgeWeights": [round(float(value), 8) for value in weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION SEQUENCE CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutEndToEnd"], indent=2))

    loc_recall = float(holdout_location["locationRecallPercent"])
    loc_precision = float(holdout_location["locationPrecisionPercent"])
    pitch_f1 = float(holdout_e2e["pitchF1Percent"])
    if loc_recall >= 80.0 and loc_precision >= 75.0 and pitch_f1 >= 78.0:
        diagnosis = "multiscale-sequence-event-model-closes-core-selection-gap"
    elif loc_recall >= 70.0 and pitch_f1 >= 72.0:
        diagnosis = "sequence-model-promising-refine-before-fresh-song-gate"
    else:
        diagnosis = "event-selection-still-bottleneck-next-test-onset-group-sequence-model"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("NOTE: measures 13-16 are diagnostic, not a fresh untouched holdout anymore.")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
