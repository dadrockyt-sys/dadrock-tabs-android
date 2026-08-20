from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_sequence_event_model as sequence
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH as INTRO_SPECTRUM_CACHE_PATH,
    _rows_by_measure,
)
from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as INTRO_RAW_CACHE_PATH,
    REFERENCE_PATH as INTRO_REFERENCE_PATH,
    _grid_lookup as intro_grid_lookup,
)
from v143_intro_repetition_recovery_event_selector import _score_measures
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets


CAL = REPO_ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"

BASE_MODEL_PATH = CAL / "intro-correlation-safe-grid-event-selector-model.json"
SEQUENCE_MODEL_PATH = CAL / "intro-correlation-safe-sequence-event-model.json"
FROZEN_SEQUENCE_17_96_PATH = CAL / "fresh-17-96-correlation-safe-sequence-frozen-events.json"

FRESH_CACHE_PATHS = [
    CAL / "fresh-verse1-reference-free-cache.json",
    CAL / "fresh-section2-reference-free-cache.json",
    CAL / "fresh-section3-reference-free-cache.json",
    CAL / "fresh-section4-reference-free-cache.json",
    CAL / "fresh-section5-reference-free-cache.json",
]

MODEL_PATH = CAL / "correlation-safe-fixed-count-reranker-model.json"
REPORT_PATH = CAL / "correlation-safe-fixed-count-reranker-training-report.json"
FROZEN_PATH = CAL / "fresh-17-96-correlation-safe-fixed-count-reranker-frozen-events.json"
MANIFEST_PATH = CAL / "fresh-17-96-correlation-safe-fixed-count-reranker-freeze-manifest.json"

TRAIN_MEASURES = set(range(1, 9))
VALIDATION_MEASURES = set(range(9, 13))
DEVELOPMENT_MEASURES = set(range(1, 13))
TARGET_MEASURES = set(range(17, 97))

# Small, preregistered validation grid. Selection uses only historical 9-12.
L2_VALUES = (0.01, 0.1, 1.0, 10.0, 100.0)
POSITIVE_WEIGHTS = (1.0, 2.0, 4.0)

FEATURE_NAMES = [
    "baseScore",
    "sequenceScore",
    "baseMargin",
    "sequenceMargin",
    "baseEvidence",
    "sequenceWideEvidence",
    "baseActive",
    "sequenceActive",
    "baseMeasurePercentile",
    "sequenceMeasurePercentile",
    "baseGlobalPercentile",
    "sequenceGlobalPercentile",
    "sequenceMinusBase",
    "measureRankAgreement",
    "measureRankMax",
    "measureRankMin",
]


def _load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _metrics(reference: dict[tuple[int, int], set[int]], active: set[tuple[int, int]]) -> dict[str, Any]:
    expected = set(reference)
    tp = len(expected & active)
    fp = len(active - expected)
    fn = len(expected - active)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)
    return {
        "predicted": len(active),
        "reference": len(expected),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "f1": round(float(f1), 6),
    }


def _metric_for_measure(
    reference: dict[tuple[int, int], set[int]],
    active: set[tuple[int, int]],
    measure: int,
) -> dict[str, Any]:
    ref = {key: value for key, value in reference.items() if int(key[0]) == int(measure)}
    pred = {key for key in active if int(key[0]) == int(measure)}
    return _metrics(ref, pred)


def _active_from_scores(
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    measures: set[int],
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key, score in scores.items()
        if key[0] in measures
        and evidence.get(key, False)
        and float(score) >= float(threshold)
    }


def _neutralize_sequence_grid_columns(
    X: np.ndarray,
    base_model: dict[str, Any],
    sequence_model: dict[str, Any],
) -> np.ndarray:
    out = np.asarray(X, dtype=np.float64).copy()
    grid_width = len(base_model["featureMean"])
    columns = [int(value) for value in sequence_model.get("neutralizedGridFeatureColumns", [])]
    raw_value = float(sequence_model.get("neutralizedRawValue", 1.0))

    if not columns:
        return out

    for window_index, _ in enumerate(sequence.WINDOWS_MS):
        offset = int(window_index) * int(grid_width)
        for column in columns:
            target = offset + int(column)
            if target >= out.shape[1]:
                raise RuntimeError(
                    f"Correlation-safe neutralization column {target} exceeds sequence feature width {out.shape[1]}"
                )
            out[:, target] = raw_value
    return out


def _sequence_scores(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    context_measures: set[int],
    base_scores: dict[tuple[int, int], float],
    base_evidence: dict[tuple[int, int], bool],
    base_model: dict[str, Any],
    sequence_model: dict[str, Any],
) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], bool]]:
    # Reference is intentionally empty. In v143_intro_sequence_event_model._dataset,
    # professional reference contributes only Y labels; X is entirely analyzer/context data.
    ds = sequence._dataset(
        rows_by_measure,
        grid,
        {},
        measures,
        context_measures,
        base_scores,
        base_evidence,
        float(base_model["threshold"]),
    )
    X = _neutralize_sequence_grid_columns(ds["X"], base_model, sequence_model)
    mean = np.asarray(sequence_model["featureMean"], dtype=np.float64)
    std = np.asarray(sequence_model["featureStd"], dtype=np.float64)
    basis = np.asarray(sequence_model["pcaBasis"], dtype=np.float64)
    weights = np.asarray(sequence_model["ridgeWeights"], dtype=np.float64)

    if X.shape[1] != mean.shape[0]:
        raise RuntimeError(f"Sequence feature width mismatch: X={X.shape[1]} model={mean.shape[0]}")
    if basis.shape[0] != mean.shape[0]:
        raise RuntimeError(f"Sequence PCA basis mismatch: basis={basis.shape} mean={mean.shape}")

    scores = sequence._project(X, mean, std, basis) @ weights
    return (
        {key: float(score) for key, score in zip(ds["keys"], scores)},
        {key: bool(value) for key, value in zip(ds["keys"], ds["wideEvidence"])},
    )


def _percentiles(
    keys: list[tuple[int, int]],
    scores: dict[tuple[int, int], float],
    per_measure: bool,
) -> dict[tuple[int, int], float]:
    groups: dict[int, list[tuple[int, int]]] = {}
    if per_measure:
        for key in keys:
            groups.setdefault(int(key[0]), []).append(key)
    else:
        groups[0] = list(keys)

    out: dict[tuple[int, int], float] = {}
    for group_keys in groups.values():
        ranked = sorted(group_keys, key=lambda key: (float(scores.get(key, 0.0)), key))
        n = len(ranked)
        if n <= 1:
            for key in ranked:
                out[key] = 1.0
            continue
        for index, key in enumerate(ranked):
            out[key] = float(index) / float(n - 1)
    return out


def _feature_dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    context_measures: set[int],
    base_model: dict[str, Any],
    sequence_model: dict[str, Any],
    reference: dict[tuple[int, int], set[int]] | None,
) -> dict[str, Any]:
    base_scores, base_evidence = _score_measures(
        rows_by_measure,
        grid,
        context_measures,
        base_model,
    )
    seq_scores, seq_evidence = _sequence_scores(
        rows_by_measure,
        grid,
        measures,
        context_measures,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    base_threshold = float(base_model["threshold"])
    sequence_threshold = float(sequence_model["threshold"])
    base_active = _active_from_scores(base_scores, base_evidence, measures, base_threshold)
    seq_active = _active_from_scores(seq_scores, seq_evidence, measures, sequence_threshold)

    keys = [
        (measure, step)
        for measure in sorted(measures)
        for step in range(16)
        if (measure, step) in grid
        and (base_evidence.get((measure, step), False) or seq_evidence.get((measure, step), False))
    ]
    if not keys:
        raise RuntimeError(f"No eligible fixed-count reranker keys for measures {min(measures)}-{max(measures)}")

    missing_baseline = sorted(base_active - set(keys))
    if missing_baseline:
        raise RuntimeError(f"Baseline active keys unexpectedly absent from reranker pool: {missing_baseline[:10]}")

    base_measure_pct = _percentiles(keys, base_scores, True)
    seq_measure_pct = _percentiles(keys, seq_scores, True)
    base_global_pct = _percentiles(keys, base_scores, False)
    seq_global_pct = _percentiles(keys, seq_scores, False)

    rows: list[np.ndarray] = []
    labels: list[float] = []
    expected = set(reference or {})
    for key in keys:
        bm = float(base_measure_pct[key])
        sm = float(seq_measure_pct[key])
        base_score = float(base_scores.get(key, 0.0))
        seq_score = float(seq_scores.get(key, 0.0))
        rows.append(
            np.asarray(
                [
                    base_score,
                    seq_score,
                    base_score - base_threshold,
                    seq_score - sequence_threshold,
                    1.0 if base_evidence.get(key, False) else 0.0,
                    1.0 if seq_evidence.get(key, False) else 0.0,
                    1.0 if key in base_active else 0.0,
                    1.0 if key in seq_active else 0.0,
                    bm,
                    sm,
                    float(base_global_pct[key]),
                    float(seq_global_pct[key]),
                    seq_score - base_score,
                    bm * sm,
                    max(bm, sm),
                    min(bm, sm),
                ],
                dtype=np.float64,
            )
        )
        labels.append(1.0 if key in expected else 0.0)

    return {
        "X": np.stack(rows, axis=0),
        "Y": np.asarray(labels, dtype=np.float64),
        "keys": keys,
        "baseActive": base_active,
        "sequenceActive": seq_active,
        "baseScores": base_scores,
        "sequenceScores": seq_scores,
        "baseEvidence": base_evidence,
        "sequenceEvidence": seq_evidence,
    }


def _fit_weighted_ridge(
    X: np.ndarray,
    Y: np.ndarray,
    l2: float,
    positive_weight: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    Z = np.concatenate([np.ones((X.shape[0], 1), dtype=np.float64), (X - mean) / std], axis=1)
    sample_weight = np.where(Y > 0.5, float(positive_weight), 1.0)
    root_weight = np.sqrt(sample_weight)
    Zw = Z * root_weight[:, None]
    Yw = Y * root_weight
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    weights = np.linalg.pinv(Zw.T @ Zw + reg) @ Zw.T @ Yw
    return mean, std, weights


def _predict(X: np.ndarray, mean: np.ndarray, std: np.ndarray, weights: np.ndarray) -> np.ndarray:
    Z = np.concatenate([np.ones((X.shape[0], 1), dtype=np.float64), (X - mean) / std], axis=1)
    return Z @ weights


def _select_fixed_count(
    keys: list[tuple[int, int]],
    scores: np.ndarray,
    base_active: set[tuple[int, int]],
    measures: set[int],
) -> set[tuple[int, int]]:
    score_map = {key: float(score) for key, score in zip(keys, scores)}
    selected: set[tuple[int, int]] = set()
    for measure in sorted(measures):
        candidates = [key for key in keys if int(key[0]) == int(measure)]
        target_count = sum(1 for key in base_active if int(key[0]) == int(measure))
        if target_count <= 0:
            continue
        if len(candidates) < target_count:
            raise RuntimeError(
                f"Measure {measure}: only {len(candidates)} reranker candidates for baseline count {target_count}"
            )
        ranked = sorted(candidates, key=lambda key: (-score_map[key], key))
        selected.update(ranked[:target_count])
    if len(selected) != len(base_active):
        raise RuntimeError(
            f"Fixed-count invariant failed: selected={len(selected)} baseline={len(base_active)}"
        )
    return selected


def _extract_event_set(payload: Any) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "measure" in value and "step" in value:
                try:
                    measure = int(value["measure"])
                    step = int(value["step"])
                    if measure in TARGET_MEASURES and 0 <= step < 16:
                        found.add((measure, step))
                except (TypeError, ValueError):
                    pass
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return found


def _merge_fresh_caches() -> tuple[dict[int, list[dict[str, Any]]], dict[tuple[int, int], float]]:
    rows_by_measure: dict[int, list[dict[str, Any]]] = {}
    grid: dict[tuple[int, int], float] = {}
    group_offset = 0

    for cache_index, path in enumerate(FRESH_CACHE_PATHS):
        cache = _load_json(path)
        if cache.get("referenceFree") is not True:
            raise RuntimeError(f"Fresh cache is not marked referenceFree=true: {path}")
        if cache.get("professionalReferenceUsedByAnalyzer") is not False:
            raise RuntimeError(f"Fresh cache does not assert professionalReferenceUsedByAnalyzer=false: {path}")

        for raw in cache.get("rows", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or raw.get("nearestMeasure") or 0)
            if measure not in TARGET_MEASURES:
                continue
            row = dict(raw)
            row["measure"] = measure
            # Avoid cross-cache identifier collisions. The numeric ID is not a model feature.
            if row.get("onsetGroupId") is not None:
                row["onsetGroupId"] = int(row.get("onsetGroupId") or 0) + group_offset
            rows_by_measure.setdefault(measure, []).append(row)

        for raw in cache.get("grid", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or 0)
            step = int(raw.get("step") or 0)
            if measure not in TARGET_MEASURES or not 0 <= step < 16:
                continue
            key = (measure, step)
            time_seconds = float(raw.get("timeSeconds") or 0.0)
            if key in grid and abs(grid[key] - time_seconds) > 1e-6:
                raise RuntimeError(f"Conflicting grid time for {key}: {grid[key]} vs {time_seconds}")
            grid[key] = time_seconds

        group_offset += 1_000_000

    for values in rows_by_measure.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )

    expected_grid = len(TARGET_MEASURES) * 16
    if len(grid) != expected_grid:
        missing = [
            (measure, step)
            for measure in sorted(TARGET_MEASURES)
            for step in range(16)
            if (measure, step) not in grid
        ]
        raise RuntimeError(f"17-96 grid incomplete: {len(grid)}/{expected_grid}; missing={missing[:12]}")
    if set(rows_by_measure) != TARGET_MEASURES:
        missing_measures = sorted(TARGET_MEASURES - set(rows_by_measure))
        raise RuntimeError(f"17-96 fresh rows missing measures: {missing_measures}")
    return rows_by_measure, grid


def main() -> None:
    base_model = _load_json(BASE_MODEL_PATH)
    sequence_model = _load_json(SEQUENCE_MODEL_PATH)

    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected promoted base threshold 0.27, got {base_model.get('threshold')}")
    if sequence_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Correlation-safe sequence model unexpectedly requires professional reference at runtime")

    print("=== V143 CORRELATION-SAFE FIXED-COUNT RERANKER ===")
    print("Goal: use sequence signal only to SWAP event locations, never inflate incumbent event count")
    print("Training reference: historical measures 1-8")
    print("Validation/reference selection: historical measures 9-12")
    print("Target 17-96 professional reference opened: False")
    print("Measures 97-113 opened: False")
    print("Production modified: False")

    # ------------------------------------------------------------------
    # 0) Prove our correlation-safe sequence replay exactly matches the
    # already-frozen 17-96 sequence predictions before any new training.
    # ------------------------------------------------------------------
    target_rows, target_grid = _merge_fresh_caches()
    target_base_scores, target_base_evidence = _score_measures(
        target_rows,
        target_grid,
        TARGET_MEASURES,
        base_model,
    )
    target_seq_scores, target_seq_evidence = _sequence_scores(
        target_rows,
        target_grid,
        TARGET_MEASURES,
        TARGET_MEASURES,
        target_base_scores,
        target_base_evidence,
        base_model,
        sequence_model,
    )
    replay_active = _active_from_scores(
        target_seq_scores,
        target_seq_evidence,
        TARGET_MEASURES,
        float(sequence_model["threshold"]),
    )
    frozen_sequence_payload = _load_json(FROZEN_SEQUENCE_17_96_PATH)
    frozen_sequence_active = _extract_event_set(frozen_sequence_payload)
    if not frozen_sequence_active:
        raise RuntimeError("Could not extract event locations from frozen 17-96 sequence artifact")
    if replay_active != frozen_sequence_active:
        added = sorted(replay_active - frozen_sequence_active)
        missing = sorted(frozen_sequence_active - replay_active)
        raise RuntimeError(
            "Correlation-safe sequence replay mismatch; refusing to continue. "
            f"replay={len(replay_active)} frozen={len(frozen_sequence_active)} "
            f"added={added[:12]} missing={missing[:12]}"
        )
    print("Sequence replay exact match:", True, f"({len(replay_active)} events)")

    # ------------------------------------------------------------------
    # 1) Historical-only training and validation. No 17-96 labels are read.
    # ------------------------------------------------------------------
    intro_spectrum = _load_json(INTRO_SPECTRUM_CACHE_PATH)
    intro_raw = _load_json(INTRO_RAW_CACHE_PATH)
    intro_reference_payload = _load_json(INTRO_REFERENCE_PATH)
    intro_rows = [dict(row) for row in (intro_spectrum.get("rows") or []) if isinstance(row, dict)]
    intro_rows_by_measure = _rows_by_measure(intro_rows)
    intro_grid = intro_grid_lookup(intro_raw)

    train_reference = _reference_sets(intro_reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(intro_reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(intro_reference_payload, DEVELOPMENT_MEASURES)

    train_ds = _feature_dataset(
        intro_rows_by_measure,
        intro_grid,
        TRAIN_MEASURES,
        TRAIN_MEASURES,
        base_model,
        sequence_model,
        train_reference,
    )
    validation_ds = _feature_dataset(
        intro_rows_by_measure,
        intro_grid,
        VALIDATION_MEASURES,
        DEVELOPMENT_MEASURES,
        base_model,
        sequence_model,
        validation_reference,
    )

    base_validation = _metrics(validation_reference, validation_ds["baseActive"])
    candidates: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    for l2 in L2_VALUES:
        for positive_weight in POSITIVE_WEIGHTS:
            mean, std, weights = _fit_weighted_ridge(
                train_ds["X"],
                train_ds["Y"],
                float(l2),
                float(positive_weight),
            )
            validation_scores = _predict(validation_ds["X"], mean, std, weights)
            active = _select_fixed_count(
                validation_ds["keys"],
                validation_scores,
                validation_ds["baseActive"],
                VALIDATION_MEASURES,
            )
            pooled = _metrics(validation_reference, active)
            per_measure: dict[str, Any] = {}
            deltas: list[float] = []
            worsened = 0
            for measure in sorted(VALIDATION_MEASURES):
                base_m = _metric_for_measure(validation_reference, validation_ds["baseActive"], measure)
                cand_m = _metric_for_measure(validation_reference, active, measure)
                delta = float(cand_m["f1"]) - float(base_m["f1"])
                if delta < -1e-12:
                    worsened += 1
                deltas.append(delta)
                per_measure[str(measure)] = {
                    "base": base_m,
                    "candidate": cand_m,
                    "f1Delta": round(delta, 6),
                }
            candidate = {
                "l2": float(l2),
                "positiveWeight": float(positive_weight),
                "pooled": pooled,
                "perMeasure": per_measure,
                "worsenedMeasures": int(worsened),
                "meanMeasureF1Delta": round(float(np.mean(deltas)), 6),
                "worstMeasureF1Delta": round(float(min(deltas)), 6),
            }
            candidates.append(candidate)
            key = (
                float(pooled["f1"]),
                -int(worsened),
                float(candidate["meanMeasureF1Delta"]),
                float(candidate["worstMeasureF1Delta"]),
                -float(l2),
                -float(positive_weight),
            )
            if best is None or key > best["_key"]:
                best = {**candidate, "_key": key}

    if best is None:
        raise RuntimeError("No fixed-count reranker configuration evaluated")

    validation_tp_gain = int(best["pooled"]["tp"]) - int(base_validation["tp"])
    validation_f1_delta = float(best["pooled"]["f1"]) - float(base_validation["f1"])
    validation_pass = (
        validation_tp_gain > 0
        and validation_f1_delta > 0.0
        and int(best["worsenedMeasures"]) <= 1
    )

    report: dict[str, Any] = {
        "model": "v143-correlation-safe-fixed-count-reranker",
        "purpose": "Use current correlation-safe sequence evidence to replace weak base-0.27 locations while preserving the exact base event count per measure.",
        "featureNames": FEATURE_NAMES,
        "selectionPolicy": "per-measure-exact-base-count",
        "countMultiplier": 1.0,
        "trainingMeasures": "1-8",
        "validationMeasures": "9-12",
        "targetMeasures": "17-96",
        "baseValidation": base_validation,
        "bestValidationConfiguration": {key: value for key, value in best.items() if key != "_key"},
        "validationTpGain": int(validation_tp_gain),
        "validationF1Delta": round(float(validation_f1_delta), 6),
        "validationGate": {
            "requiresTpGain": True,
            "requiresPositivePooledF1Delta": True,
            "maximumWorsenedMeasures": 1,
            "passed": bool(validation_pass),
        },
        "allValidationConfigurations": candidates,
        "correlationSafeSequenceReplayExactBeforeTraining": True,
        "targetProfessionalReferenceOpened": False,
        "measures97To113Opened": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("\n=== VALIDATION 9-12 ===")
    print("Base 0.27:", json.dumps(base_validation, sort_keys=True))
    print(
        "Best fixed-count reranker:",
        json.dumps(best["pooled"], sort_keys=True),
        "l2=", best["l2"],
        "positiveWeight=", best["positiveWeight"],
    )
    print("Validation TP gain:", validation_tp_gain)
    print("Validation F1 delta:", f"{validation_f1_delta:+.6f}")
    print("Validation worsened measures:", best["worsenedMeasures"], "/ 4")
    print("VALIDATION GATE PASSED:", validation_pass)

    if not validation_pass:
        print("\nSTOP: current fixed-count reranker does not robustly beat base 0.27 on historical validation.")
        print("17-96 reranker predictions frozen: False")
        print("Target professional reference opened: False")
        print("Measures 97-113 opened: False")
        print("Production modified: False")
        print("Report:", REPORT_PATH.relative_to(REPO_ROOT))
        return

    # ------------------------------------------------------------------
    # 2) Refit the accepted ranking rule on historical development 1-12.
    # ------------------------------------------------------------------
    development_ds = _feature_dataset(
        intro_rows_by_measure,
        intro_grid,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        base_model,
        sequence_model,
        development_reference,
    )
    mean, std, weights = _fit_weighted_ridge(
        development_ds["X"],
        development_ds["Y"],
        float(best["l2"]),
        float(best["positiveWeight"]),
    )

    model = {
        "model": "v143-correlation-safe-fixed-count-reranker",
        "baseSelectorModel": str(BASE_MODEL_PATH.name),
        "sequenceModel": str(SEQUENCE_MODEL_PATH.name),
        "trainingMeasures": "1-8",
        "validationMeasures": "9-12",
        "developmentMeasures": "1-12",
        "countPolicy": "per-measure-exact-base-count",
        "countMultiplier": 1.0,
        "l2": float(best["l2"]),
        "positiveWeight": float(best["positiveWeight"]),
        "featureNames": FEATURE_NAMES,
        "featureMean": [round(float(value), 10) for value in mean],
        "featureStd": [round(float(value), 10) for value in std],
        "weights": [round(float(value), 10) for value in weights],
        "validationGatePassed": True,
        "professionalReferenceRequiredAtRuntime": False,
        "target17To96ReferenceUsedForTraining": False,
        "measures97To113Used": False,
        "productionModified": False,
    }
    MODEL_PATH.write_text(json.dumps(model, indent=2) + "\n")

    # ------------------------------------------------------------------
    # 3) Freeze 17-96 predictions using ONLY reference-free caches and the
    # already-selected historical model. Event count is exactly the base 0.27
    # count in every measure, so sequence evidence can only swap locations.
    # ------------------------------------------------------------------
    target_ds = _feature_dataset(
        target_rows,
        target_grid,
        TARGET_MEASURES,
        TARGET_MEASURES,
        base_model,
        sequence_model,
        None,
    )
    target_scores = _predict(target_ds["X"], mean, std, weights)
    target_active = _select_fixed_count(
        target_ds["keys"],
        target_scores,
        target_ds["baseActive"],
        TARGET_MEASURES,
    )
    target_score_map = {key: float(score) for key, score in zip(target_ds["keys"], target_scores)}

    per_measure: dict[str, Any] = {}
    for measure in sorted(TARGET_MEASURES):
        base_keys = {key for key in target_ds["baseActive"] if key[0] == measure}
        candidate_keys = {key for key in target_active if key[0] == measure}
        if len(base_keys) != len(candidate_keys):
            raise RuntimeError(
                f"Measure {measure} fixed-count invariant failed: base={len(base_keys)} candidate={len(candidate_keys)}"
            )
        per_measure[str(measure)] = {
            "baseCount": len(base_keys),
            "candidateCount": len(candidate_keys),
            "swappedInCount": len(candidate_keys - base_keys),
            "swappedOutCount": len(base_keys - candidate_keys),
        }

    predictions = []
    for key in sorted(target_active):
        predictions.append(
            {
                "measure": int(key[0]),
                "step": int(key[1]),
                "baseActive": key in target_ds["baseActive"],
                "sequenceActive": key in target_ds["sequenceActive"],
                "baseScore": round(float(target_ds["baseScores"].get(key, 0.0)), 8),
                "sequenceScore": round(float(target_ds["sequenceScores"].get(key, 0.0)), 8),
                "rerankerScore": round(float(target_score_map[key]), 8),
            }
        )

    frozen = {
        "schemaVersion": 1,
        "model": "v143-correlation-safe-fixed-count-reranker",
        "measureRange": "17-96",
        "baseSelectorThreshold": float(base_model["threshold"]),
        "sequenceThreshold": float(sequence_model["threshold"]),
        "countPolicy": "per-measure-exact-base-count",
        "countMultiplier": 1.0,
        "baseEventCount": len(target_ds["baseActive"]),
        "candidateEventCount": len(target_active),
        "sequenceEventCount": len(target_ds["sequenceActive"]),
        "swappedInCount": len(target_active - target_ds["baseActive"]),
        "swappedOutCount": len(target_ds["baseActive"] - target_active),
        "perMeasure": per_measure,
        "events": predictions,
        "referenceFree": True,
        "targetProfessionalReferenceOpened": False,
        "measures97To113Opened": False,
        "predictionsFrozenBeforeGrading": True,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    FROZEN_PATH.write_text(json.dumps(frozen, indent=2) + "\n")

    fingerprints = {
        "baseSelector": {"path": str(BASE_MODEL_PATH.relative_to(REPO_ROOT)), "sha256": _sha256(BASE_MODEL_PATH)},
        "sequenceModel": {"path": str(SEQUENCE_MODEL_PATH.relative_to(REPO_ROOT)), "sha256": _sha256(SEQUENCE_MODEL_PATH)},
        "rerankerModel": {"path": str(MODEL_PATH.relative_to(REPO_ROOT)), "sha256": _sha256(MODEL_PATH)},
        "frozenPredictions": {"path": str(FROZEN_PATH.relative_to(REPO_ROOT)), "sha256": _sha256(FROZEN_PATH)},
        "historicalFrozenSequence": {
            "path": str(FROZEN_SEQUENCE_17_96_PATH.relative_to(REPO_ROOT)),
            "sha256": _sha256(FROZEN_SEQUENCE_17_96_PATH),
        },
        "freshCaches": [
            {"path": str(path.relative_to(REPO_ROOT)), "sha256": _sha256(path)}
            for path in FRESH_CACHE_PATHS
        ],
    }
    manifest = {
        "schemaVersion": 1,
        "experiment": "v143-correlation-safe-fixed-count-reranker",
        "measureRange": "17-96",
        "candidateSelectedUsingOnlyHistoricalMeasures1To12": True,
        "sequenceReplayMatchedPreviouslyFrozen17To96Predictions": True,
        "predictionsFrozenBeforeGrading": True,
        "targetProfessionalReferenceOpened": False,
        "measures97To113Opened": False,
        "productionModified": False,
        "fingerprints": fingerprints,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")

    print("\n=== 17-96 FIXED-COUNT PREDICTIONS FROZEN ===")
    print("Base 0.27 event count:", len(target_ds["baseActive"]))
    print("Candidate event count:", len(target_active))
    print("Historical sequence event count:", len(target_ds["sequenceActive"]))
    print("Swapped in:", len(target_active - target_ds["baseActive"]))
    print("Swapped out:", len(target_ds["baseActive"] - target_active))
    print("Exact base count preserved in every measure: True")
    print("Target professional reference opened: False")
    print("Measures 97-113 opened: False")
    print("Predictions frozen before grading: True")
    print("Production modified: False")
    print("READY TO COMMIT BEFORE GRADING: True")
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))
    print("Report:", REPORT_PATH.relative_to(REPO_ROOT))
    print("Frozen:", FROZEN_PATH.relative_to(REPO_ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
