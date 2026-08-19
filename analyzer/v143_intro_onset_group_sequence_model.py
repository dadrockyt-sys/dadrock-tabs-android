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
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    TRAIN_MEASURES,
    VALIDATION_MEASURES,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    _rows_by_measure,
    _predict_pitch_sets_for_assignments,
    _evaluate_end_to_end,
    _pct,
    _f1,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-group-sequence-model-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-onset-group-sequence-model.json"
)

PCA_COMPONENTS = (8, 12, 16, 24, 32, 48, 64)
L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
THRESHOLDS = tuple(round(-0.10 + 0.05 * index, 2) for index in range(19))
ASSIGN_WINDOWS_MS = (75, 100, 125, 150, 175, 200)
TEACHER_WINDOW_MS = 200
IGNORE_NEAR_REFERENCE_MS = 80


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _location_metrics(
    reference: dict[tuple[int, int], set[int]],
    assignments: dict[tuple[int, int], dict[str, Any]],
) -> dict[str, Any]:
    expected = set(reference)
    active = set(assignments)
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


def _measure_step_duration(
    grid: dict[tuple[int, int], float],
    measure: int,
) -> float:
    times = [
        float(grid[(measure, step)])
        for step in range(16)
        if (measure, step) in grid
    ]
    if len(times) < 2:
        return 0.116
    diffs = np.diff(np.asarray(times, dtype=np.float64))
    diffs = diffs[np.isfinite(diffs) & (diffs > 0)]
    return float(np.median(diffs)) if diffs.size else 0.116


def _nearest_grid(
    row: dict[str, Any],
    grid: dict[tuple[int, int], float],
) -> tuple[int, float, float]:
    measure = int(row.get("measure") or 0)
    onset = _safe_float(row.get("onsetTime"), -1.0)
    choices = [
        (step, float(grid[(measure, step)]))
        for step in range(16)
        if (measure, step) in grid
    ]
    if not choices or onset < 0.0:
        return 0, 0.0, 0.0
    step, target = min(choices, key=lambda item: (abs(onset - item[1]), item[0]))
    return int(step), float(target), float(onset - target)


def _spectral_vector(row: dict[str, Any], spectrum_len: int) -> list[float]:
    values: list[float] = []
    for view in ("viewA", "viewB"):
        payload = row.get(view) or {}
        for name in ("attackMax", "earlyMean", "sustainMean"):
            arr = np.asarray(payload.get(name) or [], dtype=np.float64)
            if arr.ndim != 1 or arr.size != spectrum_len:
                raise RuntimeError(
                    f"Bad spectrum onsetGroupId={row.get('onsetGroupId')} {view}/{name}: {arr.shape}"
                )
            arr = np.where(np.isfinite(arr), arr, 0.0)
            values.extend(arr.tolist())
    return values


def _nearest_peer_row(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measure: int,
    step: int,
) -> tuple[dict[str, Any] | None, float]:
    target = grid.get((measure, step))
    rows = rows_by_measure.get(measure, [])
    if target is None or not rows:
        return None, 999.0
    row = min(
        rows,
        key=lambda item: (
            abs(_safe_float(item.get("onsetTime"), -999.0) - float(target)),
            -int(item.get("stemSupportMax") or 0),
            -int(item.get("detectionCountSum") or 0),
        ),
    )
    return row, abs(_safe_float(row.get("onsetTime"), -999.0) - float(target))


def _feature_for_row(
    row: dict[str, Any],
    row_index: int,
    measure_rows: list[dict[str, Any]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    context_measures: set[int],
    spectrum_len: int,
) -> np.ndarray:
    measure = int(row.get("measure") or 0)
    onset = _safe_float(row.get("onsetTime"), 0.0)
    nearest_step, _, signed_residual = _nearest_grid(row, grid)
    step_duration = max(_measure_step_duration(grid, measure), 1e-6)

    values = _spectral_vector(row, spectrum_len)

    candidate_count = float(row.get("candidateCount") or 0)
    source_cluster_count = float(row.get("sourceClusterCount") or 0)
    stem_support = float(row.get("stemSupportMax") or 0)
    sweep_support = float(row.get("sweepSupportMax") or 0)
    detection_count = float(row.get("detectionCountSum") or 0)
    phase = 2.0 * math.pi * float(nearest_step) / 16.0
    values.extend(
        [
            signed_residual / step_duration,
            abs(signed_residual) / step_duration,
            candidate_count / 49.0,
            source_cluster_count / 32.0,
            stem_support / 2.0,
            sweep_support / 4.0,
            min(detection_count / 32.0, 3.0),
            math.sin(phase),
            math.cos(phase),
        ]
    )

    # Physical-onset sequence context. This is the key distinction from the
    # grid-slot classifier: neighbors are real detected attacks, not hypothetical
    # sixteenth positions.
    for delta in (-3, -2, -1, 1, 2, 3):
        index = row_index + delta
        if 0 <= index < len(measure_rows):
            peer = measure_rows[index]
            gap = _safe_float(peer.get("onsetTime"), onset) - onset
            _, _, peer_residual = _nearest_grid(peer, grid)
            values.extend(
                [
                    gap / step_duration,
                    abs(gap) / step_duration,
                    peer_residual / step_duration,
                    float(peer.get("stemSupportMax") or 0) / 2.0,
                    float(peer.get("sweepSupportMax") or 0) / 4.0,
                    min(float(peer.get("detectionCountSum") or 0) / 32.0, 3.0),
                ]
            )
        else:
            values.extend([0.0] * 6)

    # Local onset density around the physical attack.
    for window in (0.050, 0.100, 0.150, 0.200, 0.300):
        count = sum(
            1
            for peer in measure_rows
            if peer is not row
            and abs(_safe_float(peer.get("onsetTime"), onset) - onset) <= window
        )
        values.append(float(count) / max(len(measure_rows) - 1, 1))

    # Same grid phase across the analyzed context. Only analyzer evidence is used;
    # professional labels never enter these recurrence features.
    peer_residuals: list[float] = []
    peer_stem: list[float] = []
    peer_sweep: list[float] = []
    peer_detection: list[float] = []
    for other in sorted(context_measures):
        if other == measure:
            continue
        peer, residual = _nearest_peer_row(rows_by_measure, grid, other, nearest_step)
        if peer is None:
            continue
        peer_residuals.append(float(residual) / max(_measure_step_duration(grid, other), 1e-6))
        peer_stem.append(float(peer.get("stemSupportMax") or 0) / 2.0)
        peer_sweep.append(float(peer.get("sweepSupportMax") or 0) / 4.0)
        peer_detection.append(min(float(peer.get("detectionCountSum") or 0) / 32.0, 3.0))

    for series in (peer_residuals, peer_stem, peer_sweep, peer_detection):
        if series:
            arr = np.asarray(series, dtype=np.float64)
            values.extend(
                [
                    float(np.mean(arr)),
                    float(np.std(arr)),
                    float(np.median(arr)),
                    float(np.max(arr)),
                ]
            )
        else:
            values.extend([0.0] * 4)

    return np.asarray(values, dtype=np.float64)


def _teacher_positive_groups(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
) -> tuple[set[int], set[int]]:
    teacher_window = float(TEACHER_WINDOW_MS) / 1000.0
    ignore_window = float(IGNORE_NEAR_REFERENCE_MS) / 1000.0
    positive_ids: set[int] = set()
    near_reference_ids: set[int] = set()

    for measure in sorted(measures):
        rows = rows_by_measure.get(measure, [])
        keys = [key for key in sorted(reference) if key[0] == measure and key in grid]
        edges: list[tuple[float, tuple[int, int], dict[str, Any]]] = []
        for key in keys:
            target = float(grid[key])
            for row in rows:
                residual = abs(_safe_float(row.get("onsetTime"), -999.0) - target)
                if residual <= teacher_window:
                    edges.append((residual, key, row))
                if residual <= ignore_window:
                    near_reference_ids.add(int(row.get("onsetGroupId") or 0))
        edges.sort(
            key=lambda item: (
                item[0],
                -int(item[2].get("stemSupportMax") or 0),
                -int(item[2].get("detectionCountSum") or 0),
                item[1],
            )
        )
        used_keys: set[tuple[int, int]] = set()
        used_groups: set[int] = set()
        for _, key, row in edges:
            group_id = int(row.get("onsetGroupId") or 0)
            if key in used_keys or group_id in used_groups:
                continue
            used_keys.add(key)
            used_groups.add(group_id)
            positive_ids.add(group_id)

    return positive_ids, near_reference_ids


def _dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    spectrum_len: int,
    training: bool,
) -> dict[str, Any]:
    positives, near_reference = _teacher_positive_groups(
        rows_by_measure,
        grid,
        reference,
        measures,
    ) if training else (set(), set())

    xs: list[np.ndarray] = []
    ys: list[float] = []
    rows_out: list[dict[str, Any]] = []
    for measure in sorted(measures):
        measure_rows = rows_by_measure.get(measure, [])
        for index, row in enumerate(measure_rows):
            group_id = int(row.get("onsetGroupId") or 0)
            if training and group_id not in positives and group_id in near_reference:
                # Avoid teaching nearby duplicate detections as hard negatives.
                continue
            xs.append(
                _feature_for_row(
                    row,
                    index,
                    measure_rows,
                    rows_by_measure,
                    grid,
                    context_measures,
                    spectrum_len,
                )
            )
            ys.append(1.0 if group_id in positives else 0.0)
            rows_out.append(row)

    if not xs:
        return {
            "X": np.zeros((0, 1), dtype=np.float64),
            "Y": np.zeros(0, dtype=np.float64),
            "rows": [],
            "positiveCount": len(positives),
        }
    return {
        "X": np.stack(xs, axis=0),
        "Y": np.asarray(ys, dtype=np.float64),
        "rows": rows_out,
        "positiveCount": len(positives),
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
    return np.concatenate(
        [np.ones((reduced.shape[0], 1), dtype=np.float64), reduced],
        axis=1,
    )


def _fit_ridge(Z: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ y


def _assign_selected_groups(
    rows: list[dict[str, Any]],
    scores: np.ndarray,
    grid: dict[tuple[int, int], float],
    threshold: float,
    assign_window_ms: int,
) -> dict[tuple[int, int], dict[str, Any]]:
    window = float(assign_window_ms) / 1000.0
    selected = [
        (row, float(score))
        for row, score in zip(rows, scores)
        if float(score) >= float(threshold)
    ]
    by_measure: dict[int, list[tuple[dict[str, Any], float]]] = {}
    for row, score in selected:
        by_measure.setdefault(int(row.get("measure") or 0), []).append((row, score))

    assignments: dict[tuple[int, int], dict[str, Any]] = {}
    for measure, candidates in sorted(by_measure.items()):
        # Build all legal group->grid edges, then greedily take the closest edge.
        # Each physical onset and each grid position may be used only once.
        edges: list[tuple[float, float, int, tuple[int, int], dict[str, Any]]] = []
        for row, score in candidates:
            onset = _safe_float(row.get("onsetTime"), -999.0)
            group_id = int(row.get("onsetGroupId") or 0)
            for step in range(16):
                key = (measure, step)
                target = grid.get(key)
                if target is None:
                    continue
                residual = abs(onset - float(target))
                if residual <= window:
                    edges.append((residual, -score, group_id, key, row))
        edges.sort(key=lambda item: (item[0], item[1], item[2], item[3]))
        used_groups: set[int] = set()
        used_keys: set[tuple[int, int]] = set()
        for _, _, group_id, key, row in edges:
            if group_id in used_groups or key in used_keys:
                continue
            used_groups.add(group_id)
            used_keys.add(key)
            assignments[key] = row
    return assignments


def _evaluate(
    reference: dict[tuple[int, int], set[int]],
    assignments: dict[tuple[int, int], dict[str, Any]],
    grid: dict[tuple[int, int], float],
    pitch_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    loc = _location_metrics(reference, assignments)
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)
    e2e = _evaluate_end_to_end(reference, pitch_sets)
    return loc, e2e


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)
    spectrum_len = int(spectrum_cache.get("spectrumMidiMax") or 112) - int(
        spectrum_cache.get("spectrumMidiMin") or 28
    ) + 1

    train_reference = _reference_sets(reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    print("=== V143 ONSET-GROUP SEQUENCE EVENT MODEL ===")
    print("Primary objects: physical onset groups, not grid slots")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Measures 13-16: diagnostic only; not a fresh untouched holdout")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    train = _dataset(
        rows_by_measure,
        grid,
        train_reference,
        TRAIN_MEASURES,
        TRAIN_MEASURES,
        spectrum_len,
        training=True,
    )
    validation = _dataset(
        rows_by_measure,
        grid,
        validation_reference,
        VALIDATION_MEASURES,
        set(range(1, 13)),
        spectrum_len,
        training=False,
    )
    print("trainingPhysicalOnsets:", len(train["rows"]))
    print("trainingPositiveOnsets:", train["positiveCount"])
    print("validationPhysicalOnsets:", len(validation["rows"]))

    best: dict[str, Any] | None = None
    searched = 0
    total = len(PCA_COMPONENTS) * len(L2_VALUES) * len(THRESHOLDS) * len(ASSIGN_WINDOWS_MS)
    for components in PCA_COMPONENTS:
        mean, std, basis = _fit_projection(train["X"], components)
        z_train = _project(train["X"], mean, std, basis)
        z_validation = _project(validation["X"], mean, std, basis)
        for l2 in L2_VALUES:
            weights = _fit_ridge(z_train, train["Y"], l2)
            validation_scores = z_validation @ weights
            for threshold in THRESHOLDS:
                for assign_window_ms in ASSIGN_WINDOWS_MS:
                    searched += 1
                    assignments = _assign_selected_groups(
                        validation["rows"],
                        validation_scores,
                        grid,
                        threshold,
                        assign_window_ms,
                    )
                    loc, e2e = _evaluate(validation_reference, assignments, grid, pitch_model)
                    precision = float(loc["locationPrecisionPercent"])
                    recall = float(loc["locationRecallPercent"])
                    f1 = float(loc["locationF1Percent"])
                    pitch_f1 = float(e2e["pitchF1Percent"])
                    exact = float(e2e["exactPitchSetPercent"])
                    objective = 0.40 * pitch_f1 + 0.30 * f1 + 0.20 * recall + 0.10 * exact
                    if precision < 70.0:
                        objective -= 1.5 * (70.0 - precision)
                    candidate = {
                        "pcaComponents": int(components),
                        "l2": float(l2),
                        "threshold": float(threshold),
                        "assignWindowMs": int(assign_window_ms),
                        "validationObjectivePercent": round(float(objective), 3),
                        "validationLocation": loc,
                        "validationEndToEnd": e2e,
                    }
                    if best is None or (
                        objective,
                        pitch_f1,
                        f1,
                        recall,
                        precision,
                    ) > (
                        float(best["validationObjectivePercent"]),
                        float(best["validationEndToEnd"]["pitchF1Percent"]),
                        float(best["validationLocation"]["locationF1Percent"]),
                        float(best["validationLocation"]["locationRecallPercent"]),
                        float(best["validationLocation"]["locationPrecisionPercent"]),
                    ):
                        best = candidate
                    if searched % 500 == 0 or searched == total:
                        print(f"searched {searched}/{total} configurations")

    if best is None:
        raise RuntimeError("No onset-group sequence configuration evaluated")

    # Refit with measures 1-12 after validation has chosen only hyperparameters.
    development_train = _dataset(
        rows_by_measure,
        grid,
        development_reference,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        spectrum_len,
        training=True,
    )
    holdout = _dataset(
        rows_by_measure,
        grid,
        holdout_reference,
        HOLDOUT_MEASURES,
        set(range(1, 17)),
        spectrum_len,
        training=False,
    )
    mean, std, basis = _fit_projection(development_train["X"], int(best["pcaComponents"]))
    z_development = _project(development_train["X"], mean, std, basis)
    weights = _fit_ridge(z_development, development_train["Y"], float(best["l2"]))

    development_scores = z_development @ weights
    development_assignments = _assign_selected_groups(
        development_train["rows"],
        development_scores,
        grid,
        float(best["threshold"]),
        int(best["assignWindowMs"]),
    )
    dev_loc, dev_e2e = _evaluate(
        development_reference,
        development_assignments,
        grid,
        pitch_model,
    )

    z_holdout = _project(holdout["X"], mean, std, basis)
    holdout_scores = z_holdout @ weights
    holdout_assignments = _assign_selected_groups(
        holdout["rows"],
        holdout_scores,
        grid,
        float(best["threshold"]),
        int(best["assignWindowMs"]),
    )
    hold_loc, hold_e2e = _evaluate(
        holdout_reference,
        holdout_assignments,
        grid,
        pitch_model,
    )

    report = {
        "model": "v143-onset-group-sequence-event-model",
        "bestConfiguration": {
            "pcaComponents": best["pcaComponents"],
            "l2": best["l2"],
            "threshold": best["threshold"],
            "assignWindowMs": best["assignWindowMs"],
            "validationObjectivePercent": best["validationObjectivePercent"],
        },
        "validationLocation": best["validationLocation"],
        "validationEndToEnd": best["validationEndToEnd"],
        "developmentLocation": dev_loc,
        "developmentEndToEnd": dev_e2e,
        "holdoutLocation": hold_loc,
        "holdoutEndToEnd": hold_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because prior architecture iterations already inspected them. A fresh unseen song/section is required before production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "pcaComponents": int(best["pcaComponents"]),
                "l2": float(best["l2"]),
                "threshold": float(best["threshold"]),
                "assignWindowMs": int(best["assignWindowMs"]),
                "featureMean": [round(float(value), 8) for value in mean],
                "featureStd": [round(float(value), 8) for value in std],
                "basis": [[round(float(value), 8) for value in row] for row in basis.tolist()],
                "weights": [round(float(value), 8) for value in weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION ONSET-GROUP CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== VALIDATION END-TO-END 9-12 ===")
    print(json.dumps(report["validationEndToEnd"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["holdoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["holdoutEndToEnd"], indent=2))

    hold_loc_precision = float(hold_loc["locationPrecisionPercent"])
    hold_loc_recall = float(hold_loc["locationRecallPercent"])
    hold_pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if hold_loc_precision >= 75.0 and hold_loc_recall >= 80.0 and hold_pitch_f1 >= 78.0:
        diagnosis = "onset-group-sequence-core-is-promising-freeze-timing-pitch-and-test-fresh-section"
    elif hold_loc_recall >= 75.0 and hold_pitch_f1 >= 70.0:
        diagnosis = "onset-group-sequence-model-improves-core-but-needs-one-more-event-alignment-refinement"
    else:
        diagnosis = "onset-group-eventness-remains-insufficient-consider-temporal-alignment-decoder"
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
