#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

import v143_correlation_safe_fixed_count_reranker_freeze as freeze

CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
REPORT_PATH = CAL / "contextual-prune-nested-lobo-report.json"

TARGET_MEASURES = set(range(17, 97))
BANDS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96)]
EXPECTED_REFERENCE_COUNT = 431

FEATURE_NAMES = [
    "baseScore",
    "sequenceScore",
    "sequenceEvidence",
    "stepSin",
    "stepCos",
    "strongBeat",
    "eighthGrid",
    "measureBaseCount",
    "neighborStepCount1",
    "neighborStepCount2",
    "sameStepAdjacentMeasures",
    "sameStepTwoMeasures",
    "sameStepFourMeasures",
    "sameStepWindow4Count",
    "baseSequenceInteraction",
]

L2_VALUES = (0.1, 1.0, 10.0)
PRUNE_FRACTIONS = (0.0, 0.025, 0.05, 0.075, 0.10, 0.15)


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_reference_blind_safe(path: Path) -> tuple[set[tuple[int, int]], bool]:
    ref: set[tuple[int, int]] = set()
    current_measure: int | None = None
    hit_reserve_boundary = False
    measure_re = re.compile(r'"measureNumber"\s*:\s*(\d+)')
    step_re = re.compile(r'"quantizedStep"\s*:\s*(\d+)')

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            mm = measure_re.search(line)
            if mm:
                current_measure = int(mm.group(1))
                if current_measure >= 97:
                    hit_reserve_boundary = True
                    break
            sm = step_re.search(line)
            if sm and current_measure is not None and 17 <= current_measure <= 96:
                ref.add((current_measure, int(sm.group(1))))
    return ref, hit_reserve_boundary


def metrics(pred: set[tuple[int, int]], ref: set[tuple[int, int]]) -> dict[str, Any]:
    tp = len(pred & ref)
    fp = len(pred - ref)
    fn = len(ref - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "predicted": len(pred),
        "reference": len(ref),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def subset(values: set[tuple[int, int]], measures: set[int]) -> set[tuple[int, int]]:
    return {key for key in values if key[0] in measures}


def band_set(lo: int, hi: int) -> set[int]:
    return set(range(lo, hi + 1))


def build_features(
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
) -> dict[tuple[int, int], list[float]]:
    measure_counts: dict[int, int] = {}
    for measure, _step in base_active:
        measure_counts[measure] = measure_counts.get(measure, 0) + 1

    features: dict[tuple[int, int], list[float]] = {}
    for key in sorted(base_active):
        measure, step = key
        base_score = float(base_scores.get(key, 0.0))
        seq_score = float(sequence_scores.get(key, 0.0))
        seq_evidence = 1.0 if bool(sequence_evidence.get(key, False)) else 0.0

        theta = 2.0 * math.pi * (step / 16.0)
        neighbor1 = float(sum((measure, s) in base_active for s in (step - 1, step + 1) if 0 <= s < 16))
        neighbor2 = float(sum((measure, s) in base_active for s in (step - 2, step + 2) if 0 <= s < 16))
        same1 = float(sum((measure + d, step) in base_active for d in (-1, 1)))
        same2 = float(sum((measure + d, step) in base_active for d in (-2, 2)))
        same4 = float(sum((measure + d, step) in base_active for d in (-4, 4)))
        same_window4 = float(sum((measure + d, step) in base_active for d in range(-4, 5) if d != 0))

        features[key] = [
            base_score,
            seq_score,
            seq_evidence,
            math.sin(theta),
            math.cos(theta),
            1.0 if step % 4 == 0 else 0.0,
            1.0 if step % 2 == 0 else 0.0,
            float(measure_counts.get(measure, 0)),
            neighbor1,
            neighbor2,
            same1,
            same2,
            same4,
            same_window4,
            base_score * seq_score,
        ]
    return features


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35.0, 35.0)))


def fit_logistic(
    keys: list[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
    reference: set[tuple[int, int]],
    l2: float,
) -> dict[str, Any]:
    if not keys:
        raise RuntimeError("No training events for contextual prune model")

    x = np.asarray([features[key] for key in keys], dtype=np.float64)
    y = np.asarray([1.0 if key in reference else 0.0 for key in keys], dtype=np.float64)
    mean = x.mean(axis=0)
    std = x.std(axis=0)
    std = np.where(std < 1e-9, 1.0, std)
    xs = (x - mean) / std
    a = np.column_stack([np.ones(len(xs), dtype=np.float64), xs])
    w = np.zeros(a.shape[1], dtype=np.float64)

    for _ in range(40):
        p = _sigmoid(a @ w)
        grad = a.T @ (p - y)
        grad[1:] += float(l2) * w[1:]
        variance = np.maximum(p * (1.0 - p), 1e-6)
        h = a.T @ (a * variance[:, None])
        h[1:, 1:] += float(l2) * np.eye(h.shape[0] - 1)
        h += 1e-8 * np.eye(h.shape[0])
        try:
            step = np.linalg.solve(h, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.lstsq(h, grad, rcond=None)[0]
        w -= step
        if float(np.max(np.abs(step))) < 1e-8:
            break

    return {
        "mean": mean,
        "std": std,
        "weights": w,
        "l2": float(l2),
    }


def predict_probabilities(
    model: dict[str, Any],
    keys: list[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
) -> dict[tuple[int, int], float]:
    if not keys:
        return {}
    x = np.asarray([features[key] for key in keys], dtype=np.float64)
    xs = (x - model["mean"]) / model["std"]
    a = np.column_stack([np.ones(len(xs), dtype=np.float64), xs])
    probs = _sigmoid(a @ model["weights"])
    return {key: float(prob) for key, prob in zip(keys, probs)}


def apply_prune_fraction(
    base_active: set[tuple[int, int]],
    measures: set[int],
    probabilities: dict[tuple[int, int], float],
    prune_fraction: float,
) -> set[tuple[int, int]]:
    keys = sorted(key for key in base_active if key[0] in measures)
    if prune_fraction <= 0.0 or not keys:
        return set(keys)
    prune_count = int(math.floor(len(keys) * float(prune_fraction)))
    if prune_count <= 0:
        return set(keys)
    ranked = sorted(keys, key=lambda key: (float(probabilities.get(key, 0.5)), key[0], key[1]))
    pruned = set(ranked[:prune_count])
    return set(keys) - pruned


def evaluate_split(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
    train_measures: set[int],
    eval_measures: set[int],
    l2: float,
    prune_fraction: float,
) -> dict[str, Any]:
    train_keys = sorted(key for key in base_active if key[0] in train_measures)
    eval_keys = sorted(key for key in base_active if key[0] in eval_measures)
    model = fit_logistic(train_keys, features, reference, l2)
    probs = predict_probabilities(model, eval_keys, features)
    candidate = apply_prune_fraction(base_active, eval_measures, probs, prune_fraction)
    base = subset(base_active, eval_measures)
    ref = subset(reference, eval_measures)
    bm = metrics(base, ref)
    cm = metrics(candidate, ref)
    return {
        "l2": float(l2),
        "pruneFraction": float(prune_fraction),
        "base": bm,
        "candidate": cm,
        "delta": {
            "predicted": int(cm["predicted"] - bm["predicted"]),
            "tp": int(cm["tp"] - bm["tp"]),
            "fp": int(cm["fp"] - bm["fp"]),
            "fn": int(cm["fn"] - bm["fn"]),
            "precision": float(cm["precision"] - bm["precision"]),
            "recall": float(cm["recall"] - bm["recall"]),
            "f1": float(cm["f1"] - bm["f1"]),
        },
    }


def cross_validate_params(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
    bands: list[tuple[int, int]],
    l2: float,
    prune_fraction: float,
) -> dict[str, Any]:
    fold_results: dict[str, Any] = {}
    fold_deltas: list[float] = []
    precision_deltas: list[float] = []
    pooled_candidate: set[tuple[int, int]] = set()
    pooled_base: set[tuple[int, int]] = set()
    pooled_ref: set[tuple[int, int]] = set()

    for holdout in bands:
        train_bands = [band for band in bands if band != holdout]
        train_measures = set().union(*(band_set(*band) for band in train_bands))
        eval_measures = band_set(*holdout)
        result = evaluate_split(
            reference,
            base_active,
            features,
            train_measures,
            eval_measures,
            l2,
            prune_fraction,
        )
        name = f"{holdout[0]}-{holdout[1]}"
        fold_results[name] = result
        fold_deltas.append(float(result["delta"]["f1"]))
        precision_deltas.append(float(result["delta"]["precision"]))

        eval_keys = subset(base_active, eval_measures)
        train_keys = sorted(key for key in base_active if key[0] in train_measures)
        model = fit_logistic(train_keys, features, reference, l2)
        probs = predict_probabilities(model, sorted(eval_keys), features)
        pooled_candidate |= apply_prune_fraction(base_active, eval_measures, probs, prune_fraction)
        pooled_base |= eval_keys
        pooled_ref |= subset(reference, eval_measures)

    pooled_base_metrics = metrics(pooled_base, pooled_ref)
    pooled_candidate_metrics = metrics(pooled_candidate, pooled_ref)
    pooled_delta_f1 = pooled_candidate_metrics["f1"] - pooled_base_metrics["f1"]

    return {
        "l2": float(l2),
        "pruneFraction": float(prune_fraction),
        "folds": fold_results,
        "worstF1Delta": min(fold_deltas),
        "meanF1Delta": sum(fold_deltas) / len(fold_deltas),
        "meanPrecisionDelta": sum(precision_deltas) / len(precision_deltas),
        "pooledBase": pooled_base_metrics,
        "pooledCandidate": pooled_candidate_metrics,
        "pooledF1Delta": pooled_delta_f1,
    }


def choose_params(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
    bands: list[tuple[int, int]],
) -> dict[str, Any]:
    best_score: tuple[float, ...] | None = None
    best: dict[str, Any] | None = None

    for l2 in L2_VALUES:
        for prune_fraction in PRUNE_FRACTIONS:
            result = cross_validate_params(reference, base_active, features, bands, l2, prune_fraction)
            score = (
                float(result["worstF1Delta"]),
                float(result["meanF1Delta"]),
                float(result["pooledF1Delta"]),
                float(result["meanPrecisionDelta"]),
                -float(prune_fraction),
                -float(l2),
            )
            if best_score is None or score > best_score:
                best_score = score
                best = result

    if best is None:
        raise RuntimeError("No contextual prune configuration evaluated")
    return best


def rounded(obj: Any) -> Any:
    if isinstance(obj, (float, np.floating)):
        return round(float(obj), 6)
    if isinstance(obj, np.ndarray):
        return [rounded(v) for v in obj.tolist()]
    if isinstance(obj, dict):
        return {k: rounded(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rounded(v) for v in obj]
    return obj


def main() -> None:
    reference, hit_boundary = parse_reference_blind_safe(REFERENCE_PATH)
    if not hit_boundary:
        raise RuntimeError("Did not encounter measure-97 reserve boundary")
    if len(reference) != EXPECTED_REFERENCE_COUNT:
        raise RuntimeError(f"Reference count changed: {len(reference)} != {EXPECTED_REFERENCE_COUNT}")

    base_model = load_json(freeze.BASE_MODEL_PATH)
    sequence_model = load_json(freeze.SEQUENCE_MODEL_PATH)
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected base threshold 0.27, got {base_model.get('threshold')}")
    if sequence_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Sequence model unexpectedly requires professional reference at runtime")

    rows_by_measure, grid = freeze._merge_fresh_caches()
    base_scores, base_evidence = freeze._score_measures(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        base_model,
    )
    base_active = freeze._active_from_scores(
        base_scores,
        base_evidence,
        TARGET_MEASURES,
        float(base_model["threshold"]),
    )
    if len(base_active) != 765:
        raise RuntimeError(f"Base replay count mismatch: {len(base_active)} != 765")

    sequence_scores, sequence_evidence = freeze._sequence_scores(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        TARGET_MEASURES,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    features = build_features(base_active, base_scores, sequence_scores, sequence_evidence)
    if len(features) != len(base_active):
        raise RuntimeError("Context feature count does not match base event count")

    outer_folds: list[dict[str, Any]] = []
    outer_deltas: list[float] = []
    outer_precision_deltas: list[float] = []
    stitched_candidate: set[tuple[int, int]] = set()

    for holdout in BANDS:
        outer_train_bands = [band for band in BANDS if band != holdout]
        chosen = choose_params(reference, base_active, features, outer_train_bands)
        train_measures = set().union(*(band_set(*band) for band in outer_train_bands))
        eval_measures = band_set(*holdout)
        heldout = evaluate_split(
            reference,
            base_active,
            features,
            train_measures,
            eval_measures,
            float(chosen["l2"]),
            float(chosen["pruneFraction"]),
        )

        train_keys = sorted(key for key in base_active if key[0] in train_measures)
        eval_keys = sorted(key for key in base_active if key[0] in eval_measures)
        model = fit_logistic(train_keys, features, reference, float(chosen["l2"]))
        probs = predict_probabilities(model, eval_keys, features)
        stitched_candidate |= apply_prune_fraction(
            base_active,
            eval_measures,
            probs,
            float(chosen["pruneFraction"]),
        )

        outer_deltas.append(float(heldout["delta"]["f1"]))
        outer_precision_deltas.append(float(heldout["delta"]["precision"]))
        outer_folds.append({
            "holdout": f"{holdout[0]}-{holdout[1]}",
            "selectedByInnerLOBO": chosen,
            "heldout": heldout,
        })

    stitched_base_metrics = metrics(base_active, reference)
    stitched_candidate_metrics = metrics(stitched_candidate, reference)
    stitched_delta_f1 = stitched_candidate_metrics["f1"] - stitched_base_metrics["f1"]

    final_cv = choose_params(reference, base_active, features, BANDS)
    final_l2 = float(final_cv["l2"])
    final_prune_fraction = float(final_cv["pruneFraction"])
    full_keys = sorted(base_active)
    final_model = fit_logistic(full_keys, features, reference, final_l2)
    final_probs = predict_probabilities(final_model, full_keys, features)
    final_candidate = apply_prune_fraction(
        base_active,
        TARGET_MEASURES,
        final_probs,
        final_prune_fraction,
    )

    final_band_results: dict[str, Any] = {}
    final_band_deltas: list[float] = []
    for lo, hi in BANDS:
        measures = band_set(lo, hi)
        bm = metrics(subset(base_active, measures), subset(reference, measures))
        cm = metrics(subset(final_candidate, measures), subset(reference, measures))
        delta = float(cm["f1"] - bm["f1"])
        final_band_deltas.append(delta)
        final_band_results[f"{lo}-{hi}"] = {
            "base": bm,
            "candidate": cm,
            "f1Delta": delta,
        }

    final_base = metrics(base_active, reference)
    final_metrics = metrics(final_candidate, reference)
    final_delta = {
        "predicted": int(final_metrics["predicted"] - final_base["predicted"]),
        "tp": int(final_metrics["tp"] - final_base["tp"]),
        "fp": int(final_metrics["fp"] - final_base["fp"]),
        "fn": int(final_metrics["fn"] - final_base["fn"]),
        "precision": float(final_metrics["precision"] - final_base["precision"]),
        "recall": float(final_metrics["recall"] - final_base["recall"]),
        "f1": float(final_metrics["f1"] - final_base["f1"]),
    }

    outer_all_nonnegative = all(delta >= -1e-12 for delta in outer_deltas)
    outer_mean_positive = (sum(outer_deltas) / len(outer_deltas)) > 1e-12
    stitched_positive = stitched_delta_f1 > 1e-12
    final_cv_all_nonnegative = float(final_cv["worstF1Delta"]) >= -1e-12
    final_cv_pooled_positive = float(final_cv["pooledF1Delta"]) > 1e-12
    final_dev_all_nonnegative = all(delta >= -1e-12 for delta in final_band_deltas)
    final_dev_pooled_positive = float(final_delta["f1"]) > 1e-12
    candidate_is_subset = final_candidate.issubset(base_active)

    promotion_eligible = (
        outer_all_nonnegative
        and outer_mean_positive
        and stitched_positive
        and final_cv_all_nonnegative
        and final_cv_pooled_positive
        and final_dev_all_nonnegative
        and final_dev_pooled_positive
        and candidate_is_subset
    )

    report = rounded({
        "schemaVersion": 1,
        "experiment": "v143-contextual-prune-nested-lobo",
        "purpose": "Learn context-dependent false-positive pruning from consumed development measures while preserving the promoted base-0.27 event set as the only source of candidate events.",
        "developmentMeasures": "17-96",
        "reserveMeasures": "97-113",
        "referenceCount": len(reference),
        "baseEventCount": len(base_active),
        "baseMetrics": final_base,
        "featureNames": FEATURE_NAMES,
        "hyperparameters": {
            "l2Values": list(L2_VALUES),
            "pruneFractions": list(PRUNE_FRACTIONS),
        },
        "outerNestedLOBO": outer_folds,
        "outerHeldoutF1Deltas": outer_deltas,
        "outerHeldoutPrecisionDeltas": outer_precision_deltas,
        "outerWorstHeldoutF1Delta": min(outer_deltas),
        "outerMeanHeldoutF1Delta": sum(outer_deltas) / len(outer_deltas),
        "stitchedOuterCandidate": {
            "base": stitched_base_metrics,
            "candidate": stitched_candidate_metrics,
            "f1Delta": stitched_delta_f1,
        },
        "finalParameterSelectionByFiveFoldCV": final_cv,
        "finalDevelopmentModel": {
            "l2": final_l2,
            "pruneFraction": final_prune_fraction,
            "weights": final_model["weights"],
            "featureMean": final_model["mean"],
            "featureStd": final_model["std"],
            "base": final_base,
            "candidate": final_metrics,
            "delta": final_delta,
            "bands": final_band_results,
        },
        "gate": {
            "outerAllHeldoutNonnegative": outer_all_nonnegative,
            "outerMeanHeldoutPositive": outer_mean_positive,
            "stitchedOuterF1Positive": stitched_positive,
            "finalCVWorstFoldNonnegative": final_cv_all_nonnegative,
            "finalCVPooledF1Positive": final_cv_pooled_positive,
            "finalDevelopmentAllBandsNonnegative": final_dev_all_nonnegative,
            "finalDevelopmentPooledF1Positive": final_dev_pooled_positive,
            "candidateSubsetOfBase": candidate_is_subset,
            "promotionEligible": promotion_eligible,
        },
        "invariants": {
            "candidateAddsEvents": False,
            "candidateRelocatesEvents": False,
            "measures97To113Opened": False,
            "reservePayloadOpened": False,
            "professionalReferenceUsedForDevelopmentOnly17To96": True,
            "productionModified": False,
        },
    })

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 CONTEXTUAL PRUNE NESTED LOBO ===")
    print("BASE", rounded(final_base))
    print("OUTER_HELDOUT_F1_DELTAS", rounded(outer_deltas))
    print("OUTER_WORST", round(min(outer_deltas), 6))
    print("OUTER_MEAN", round(sum(outer_deltas) / len(outer_deltas), 6))
    print("STITCHED", rounded({"base": stitched_base_metrics, "candidate": stitched_candidate_metrics, "f1Delta": stitched_delta_f1}))
    print("FINAL_PARAMS", rounded({"l2": final_l2, "pruneFraction": final_prune_fraction}))
    print("FINAL", rounded({"base": final_base, "candidate": final_metrics, "delta": final_delta}))
    print("PROMOTION_ELIGIBLE", promotion_eligible)
    print("MEASURES_97_113_OPENED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
