from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_sequence_event_model as seq
import v143_intro_onset_group_sequence_model as onset
from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as RAW_CACHE_PATH,
    REFERENCE_PATH,
    _grid_lookup,
)
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
    _predict_pitch_sets_for_assignments,
    _evaluate_end_to_end,
    _pct,
    _f1,
)
from v143_intro_repetition_recovery_event_selector import _score_measures


OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-consensus-alignment-refinement-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-consensus-alignment-refinement-model.json"
)

GROUP_WINDOWS_MS = (50, 75, 100, 125, 150, 200)
L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
META_THRESHOLDS = tuple(round(-0.10 + 0.05 * i, 2) for i in range(25))
ASSIGN_WINDOWS_MS = (75, 100, 125, 150, 175, 200)
RESIDUAL_PENALTIES = (0.0, 0.25, 0.5, 1.0, 2.0)


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


def _sequence_scores_for_measures(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    base_scores: dict[tuple[int, int], float],
    base_evidence: dict[tuple[int, int], bool],
    base_threshold: float,
    model: dict[str, Any],
) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], bool]]:
    ds = seq._dataset(
        rows_by_measure,
        grid,
        reference,
        measures,
        context_measures,
        base_scores,
        base_evidence,
        base_threshold,
    )
    mean = np.asarray(model["featureMean"], dtype=np.float64)
    std = np.asarray(model["featureStd"], dtype=np.float64)
    basis = np.asarray(model["pcaBasis"], dtype=np.float64)
    weights = np.asarray(model["ridgeWeights"], dtype=np.float64)
    z = seq._project(ds["X"], mean, std, basis)
    scores = z @ weights
    return (
        {key: float(score) for key, score in zip(ds["keys"], scores)},
        {key: bool(flag) for key, flag in zip(ds["keys"], ds["wideEvidence"])},
    )


def _onset_scores_for_measures(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    context_measures: set[int],
    spectrum_len: int,
    model: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[int, float]]:
    ds = onset._dataset(
        rows_by_measure,
        grid,
        {},
        measures,
        context_measures,
        spectrum_len,
        training=False,
    )
    mean = np.asarray(model["featureMean"], dtype=np.float64)
    std = np.asarray(model["featureStd"], dtype=np.float64)
    basis = np.asarray(model["basis"], dtype=np.float64)
    weights = np.asarray(model["weights"], dtype=np.float64)
    z = onset._project(ds["X"], mean, std, basis)
    scores = z @ weights
    by_id = {
        int(row.get("onsetGroupId") or 0): float(score)
        for row, score in zip(ds["rows"], scores)
    }
    return ds["rows"], by_id


def _slot_feature(
    key: tuple[int, int],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    seq_scores: dict[tuple[int, int], float],
    seq_evidence: dict[tuple[int, int], bool],
    onset_scores: dict[int, float],
    seq_threshold: float,
    context_measures: set[int],
) -> tuple[np.ndarray, bool]:
    measure, step = key
    target = grid.get(key)
    if target is None:
        raise RuntimeError(f"Missing grid target for {key}")
    step_duration = max(onset._measure_step_duration(grid, measure), 1e-6)
    rows = rows_by_measure.get(measure, [])
    seq_score = float(seq_scores.get(key, 0.0))

    values: list[float] = [
        seq_score,
        seq_score - float(seq_threshold),
        1.0 if seq_evidence.get(key, False) else 0.0,
    ]
    any_group_evidence = False

    for window_ms in GROUP_WINDOWS_MS:
        window = float(window_ms) / 1000.0
        nearby: list[tuple[dict[str, Any], float, float]] = []
        for row in rows:
            residual = abs(_safe_float(row.get("onsetTime"), -999.0) - float(target))
            if residual <= window:
                group_id = int(row.get("onsetGroupId") or 0)
                nearby.append((row, float(onset_scores.get(group_id, 0.0)), residual))
        nearby.sort(key=lambda item: (-item[1], item[2], int(item[0].get("onsetGroupId") or 0)))
        if nearby:
            any_group_evidence = True
            best_row, best_score, best_residual = nearby[0]
            nearest_residual = min(item[2] for item in nearby)
            top_scores = [item[1] for item in nearby[:3]]
            values.extend(
                [
                    best_score,
                    float(np.mean(top_scores)),
                    best_residual / step_duration,
                    nearest_residual / step_duration,
                    min(len(nearby) / 12.0, 3.0),
                    float(best_row.get("stemSupportMax") or 0) / 2.0,
                    float(best_row.get("sweepSupportMax") or 0) / 4.0,
                    min(float(best_row.get("detectionCountSum") or 0) / 32.0, 3.0),
                ]
            )
        else:
            values.extend([0.0] * 8)

    phase = 2.0 * math.pi * float(step) / 16.0
    values.extend([math.sin(phase), math.cos(phase)])

    # Same-phase cross-measure consensus from both independently learned models.
    peer_seq: list[float] = []
    peer_onset: list[float] = []
    peer_residual: list[float] = []
    for other in sorted(context_measures):
        if other == measure:
            continue
        peer_key = (other, step)
        if peer_key not in grid:
            continue
        peer_seq.append(float(seq_scores.get(peer_key, 0.0)))
        target_other = float(grid[peer_key])
        candidates = rows_by_measure.get(other, [])
        if candidates:
            best = max(
                candidates,
                key=lambda row: (
                    float(onset_scores.get(int(row.get("onsetGroupId") or 0), 0.0)),
                    -abs(_safe_float(row.get("onsetTime"), -999.0) - target_other),
                ),
            )
            peer_onset.append(float(onset_scores.get(int(best.get("onsetGroupId") or 0), 0.0)))
            peer_residual.append(
                abs(_safe_float(best.get("onsetTime"), -999.0) - target_other)
                / max(onset._measure_step_duration(grid, other), 1e-6)
            )

    for series in (peer_seq, peer_onset, peer_residual):
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

    return np.asarray(values, dtype=np.float64), bool(any_group_evidence)


def _meta_dataset(
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    seq_scores: dict[tuple[int, int], float],
    seq_evidence: dict[tuple[int, int], bool],
    onset_scores: dict[int, float],
    seq_threshold: float,
) -> dict[str, Any]:
    xs: list[np.ndarray] = []
    ys: list[float] = []
    keys: list[tuple[int, int]] = []
    evidence: list[bool] = []
    for measure in sorted(measures):
        for step in range(16):
            key = (measure, step)
            if key not in grid:
                continue
            vector, has_evidence = _slot_feature(
                key,
                rows_by_measure,
                grid,
                seq_scores,
                seq_evidence,
                onset_scores,
                seq_threshold,
                context_measures,
            )
            xs.append(vector)
            ys.append(1.0 if key in reference else 0.0)
            keys.append(key)
            evidence.append(has_evidence)
    return {
        "X": np.stack(xs, axis=0),
        "Y": np.asarray(ys, dtype=np.float64),
        "keys": keys,
        "evidence": evidence,
    }


def _fit_standardizer(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    return mean, std


def _design(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    z = (X - mean) / std
    return np.concatenate([np.ones((z.shape[0], 1), dtype=np.float64), z], axis=1)


def _fit_ridge(Z: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ y


def _active_keys(
    ds: dict[str, Any],
    scores: np.ndarray,
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key, score, has_evidence in zip(ds["keys"], scores, ds["evidence"])
        if has_evidence and float(score) >= float(threshold)
    }


def _assign_active_slots(
    active: set[tuple[int, int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    onset_scores: dict[int, float],
    assign_window_ms: int,
    residual_penalty: float,
) -> dict[tuple[int, int], dict[str, Any]]:
    window = float(assign_window_ms) / 1000.0
    assignments: dict[tuple[int, int], dict[str, Any]] = {}
    for measure in sorted({key[0] for key in active}):
        keys = sorted([key for key in active if key[0] == measure], key=lambda key: key[1])
        rows = rows_by_measure.get(measure, [])
        edges: list[tuple[float, float, int, tuple[int, int], dict[str, Any]]] = []
        for key in keys:
            target = grid.get(key)
            if target is None:
                continue
            step_duration = max(onset._measure_step_duration(grid, measure), 1e-6)
            for row in rows:
                residual = abs(_safe_float(row.get("onsetTime"), -999.0) - float(target))
                if residual > window:
                    continue
                group_id = int(row.get("onsetGroupId") or 0)
                group_score = float(onset_scores.get(group_id, 0.0))
                utility = group_score - float(residual_penalty) * residual / step_duration
                edges.append((-utility, residual, group_id, key, row))
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
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    seq_model = _load_json(seq.MODEL_PATH)
    onset_model = _load_json(onset.MODEL_PATH)

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

    all_measures = set(range(1, 17))
    base_scores, base_evidence = _score_measures(
        rows_by_measure,
        grid,
        all_measures,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])
    seq_threshold = float(seq_model["threshold"])

    print("=== V143 CONSENSUS EVENT ALIGNMENT REFINEMENT ===")
    print("Inputs: multiscale grid sequence score + physical-onset sequence score")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Measures 13-16: diagnostic only; not a fresh untouched holdout")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    # Generate score fields once using the two independently learned selectors.
    train_seq, train_seq_evidence = _sequence_scores_for_measures(
        rows_by_measure, grid, train_reference, TRAIN_MEASURES, TRAIN_MEASURES,
        base_scores, base_evidence, base_threshold, seq_model,
    )
    validation_seq, validation_seq_evidence = _sequence_scores_for_measures(
        rows_by_measure, grid, validation_reference, VALIDATION_MEASURES, set(range(1, 13)),
        base_scores, base_evidence, base_threshold, seq_model,
    )
    development_seq, development_seq_evidence = _sequence_scores_for_measures(
        rows_by_measure, grid, development_reference, DEVELOPMENT_MEASURES, DEVELOPMENT_MEASURES,
        base_scores, base_evidence, base_threshold, seq_model,
    )
    holdout_seq, holdout_seq_evidence = _sequence_scores_for_measures(
        rows_by_measure, grid, holdout_reference, HOLDOUT_MEASURES, all_measures,
        base_scores, base_evidence, base_threshold, seq_model,
    )

    _, train_onset = _onset_scores_for_measures(
        rows_by_measure, grid, TRAIN_MEASURES, TRAIN_MEASURES, spectrum_len, onset_model,
    )
    _, validation_onset = _onset_scores_for_measures(
        rows_by_measure, grid, VALIDATION_MEASURES, set(range(1, 13)), spectrum_len, onset_model,
    )
    _, development_onset = _onset_scores_for_measures(
        rows_by_measure, grid, DEVELOPMENT_MEASURES, DEVELOPMENT_MEASURES, spectrum_len, onset_model,
    )
    _, holdout_onset = _onset_scores_for_measures(
        rows_by_measure, grid, HOLDOUT_MEASURES, all_measures, spectrum_len, onset_model,
    )

    train = _meta_dataset(
        train_reference, TRAIN_MEASURES, TRAIN_MEASURES, rows_by_measure, grid,
        train_seq, train_seq_evidence, train_onset, seq_threshold,
    )
    validation = _meta_dataset(
        validation_reference, VALIDATION_MEASURES, set(range(1, 13)), rows_by_measure, grid,
        validation_seq, validation_seq_evidence, validation_onset, seq_threshold,
    )

    mean, std = _fit_standardizer(train["X"])
    z_train = _design(train["X"], mean, std)
    z_validation = _design(validation["X"], mean, std)

    best: dict[str, Any] | None = None
    searched = 0
    total = len(L2_VALUES) * len(META_THRESHOLDS) * len(ASSIGN_WINDOWS_MS) * len(RESIDUAL_PENALTIES)
    for l2 in L2_VALUES:
        weights = _fit_ridge(z_train, train["Y"], l2)
        validation_scores = z_validation @ weights
        for threshold in META_THRESHOLDS:
            active = _active_keys(validation, validation_scores, threshold)
            for assign_window_ms in ASSIGN_WINDOWS_MS:
                for residual_penalty in RESIDUAL_PENALTIES:
                    searched += 1
                    assignments = _assign_active_slots(
                        active,
                        rows_by_measure,
                        grid,
                        validation_onset,
                        assign_window_ms,
                        residual_penalty,
                    )
                    loc, e2e = _evaluate(validation_reference, assignments, grid, pitch_model)
                    precision = float(loc["locationPrecisionPercent"])
                    recall = float(loc["locationRecallPercent"])
                    f1 = float(loc["locationF1Percent"])
                    pitch_f1 = float(e2e["pitchF1Percent"])
                    exact = float(e2e["exactPitchSetPercent"])
                    objective = 0.40 * pitch_f1 + 0.30 * f1 + 0.20 * recall + 0.10 * exact
                    if precision < 75.0:
                        objective -= 2.0 * (75.0 - precision)
                    candidate = {
                        "l2": float(l2),
                        "threshold": float(threshold),
                        "assignWindowMs": int(assign_window_ms),
                        "residualPenalty": float(residual_penalty),
                        "validationObjectivePercent": round(float(objective), 3),
                        "validationLocation": loc,
                        "validationEndToEnd": e2e,
                        "weights": weights,
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
                        print(f"searched {searched}/{total} consensus configurations")

    if best is None:
        raise RuntimeError("No consensus-alignment configuration evaluated")

    # Refit the consensus layer on measures 1-12 after validation chose hyperparameters.
    development = _meta_dataset(
        development_reference, DEVELOPMENT_MEASURES, DEVELOPMENT_MEASURES, rows_by_measure, grid,
        development_seq, development_seq_evidence, development_onset, seq_threshold,
    )
    holdout = _meta_dataset(
        holdout_reference, HOLDOUT_MEASURES, all_measures, rows_by_measure, grid,
        holdout_seq, holdout_seq_evidence, holdout_onset, seq_threshold,
    )
    dev_mean, dev_std = _fit_standardizer(development["X"])
    z_dev = _design(development["X"], dev_mean, dev_std)
    z_holdout = _design(holdout["X"], dev_mean, dev_std)
    dev_weights = _fit_ridge(z_dev, development["Y"], float(best["l2"]))
    dev_scores = z_dev @ dev_weights
    hold_scores = z_holdout @ dev_weights

    dev_active = _active_keys(development, dev_scores, float(best["threshold"]))
    hold_active = _active_keys(holdout, hold_scores, float(best["threshold"]))
    dev_assignments = _assign_active_slots(
        dev_active,
        rows_by_measure,
        grid,
        development_onset,
        int(best["assignWindowMs"]),
        float(best["residualPenalty"]),
    )
    hold_assignments = _assign_active_slots(
        hold_active,
        rows_by_measure,
        grid,
        holdout_onset,
        int(best["assignWindowMs"]),
        float(best["residualPenalty"]),
    )
    dev_loc, dev_e2e = _evaluate(development_reference, dev_assignments, grid, pitch_model)
    hold_loc, hold_e2e = _evaluate(holdout_reference, hold_assignments, grid, pitch_model)

    report = {
        "model": "v143-consensus-event-alignment-refinement",
        "bestConfiguration": {
            "l2": best["l2"],
            "threshold": best["threshold"],
            "assignWindowMs": best["assignWindowMs"],
            "residualPenalty": best["residualPenalty"],
            "validationObjectivePercent": best["validationObjectivePercent"],
        },
        "validationLocation": best["validationLocation"],
        "validationEndToEnd": best["validationEndToEnd"],
        "developmentLocation": dev_loc,
        "developmentEndToEnd": dev_e2e,
        "diagnosticHoldoutLocation": hold_loc,
        "diagnosticHoldoutEndToEnd": hold_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only; a fresh unseen song/section is required before production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "groupWindowsMs": list(GROUP_WINDOWS_MS),
                "l2": float(best["l2"]),
                "threshold": float(best["threshold"]),
                "assignWindowMs": int(best["assignWindowMs"]),
                "residualPenalty": float(best["residualPenalty"]),
                "featureMean": [round(float(v), 8) for v in dev_mean],
                "featureStd": [round(float(v), 8) for v in dev_std],
                "weights": [round(float(v), 8) for v in dev_weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        ) + "\n"
    )

    print("\n=== BEST VALIDATION CONSENSUS CONFIGURATION ===")
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
    print(json.dumps(report["diagnosticHoldoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutEndToEnd"], indent=2))

    precision = float(hold_loc["locationPrecisionPercent"])
    recall = float(hold_loc["locationRecallPercent"])
    pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 78.0:
        diagnosis = "consensus-alignment-closes-timing-pitch-core-freeze-and-test-fresh-section"
    elif recall >= 80.0 and pitch_f1 >= 72.0:
        diagnosis = "consensus-alignment-recall-strong-but-false-events-remain-prune-with-sequence-decoder"
    else:
        diagnosis = "consensus-alignment-insufficient-do-not-freeze-core"
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
