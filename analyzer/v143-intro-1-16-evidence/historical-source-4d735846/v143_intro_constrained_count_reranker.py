from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_consensus_alignment_refinement as consensus
import v143_intro_sequence_event_model as sequence
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
)


OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-constrained-count-reranker-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-constrained-count-reranker-model.json"
)

L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
POSITIVE_WEIGHTS = (1.0, 2.0, 4.0, 8.0)
COUNT_POLICIES = ("block", "per-measure")
COUNT_MULTIPLIERS = (0.90, 0.95, 1.00, 1.05, 1.10)
ASSIGN_WINDOWS_MS = (75, 100, 125, 150, 175, 200)
RESIDUAL_PENALTIES = (0.0, 0.25, 0.5, 1.0, 2.0)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _fit_weighted_ridge(
    X: np.ndarray,
    y: np.ndarray,
    l2: float,
    positive_weight: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean, std = consensus._fit_standardizer(X)
    Z = consensus._design(X, mean, std)
    sample_weight = np.where(y >= 0.5, float(positive_weight), 1.0)
    root = np.sqrt(sample_weight)
    Zw = Z * root[:, None]
    yw = y * root
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    weights = np.linalg.pinv(Zw.T @ Zw + reg) @ Zw.T @ yw
    return mean, std, weights


def _scores(
    X: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    weights: np.ndarray,
) -> np.ndarray:
    return consensus._design(X, mean, std) @ weights


def _baseline_active(
    keys: list[tuple[int, int]],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key in keys
        if sequence_evidence.get(key, False)
        and float(sequence_scores.get(key, 0.0)) >= float(threshold)
    }


def _scaled_count(count: int, multiplier: float, eligible_count: int) -> int:
    if count <= 0 or eligible_count <= 0:
        return 0
    target = int(round(float(count) * float(multiplier)))
    return max(1, min(target, eligible_count))


def _select_ranked(
    ds: dict[str, Any],
    scores: np.ndarray,
    baseline_active: set[tuple[int, int]],
    policy: str,
    multiplier: float,
) -> set[tuple[int, int]]:
    eligible = [
        (key, float(score))
        for key, score, evidence in zip(ds["keys"], scores, ds["evidence"])
        if bool(evidence)
    ]
    if not eligible:
        return set()

    if policy == "block":
        k = _scaled_count(len(baseline_active), multiplier, len(eligible))
        ranked = sorted(eligible, key=lambda item: (-item[1], item[0]))
        return {key for key, _ in ranked[:k]}

    if policy == "per-measure":
        selected: set[tuple[int, int]] = set()
        measures = sorted({key[0] for key, _ in eligible})
        for measure in measures:
            candidates = [(key, score) for key, score in eligible if key[0] == measure]
            baseline_count = sum(1 for key in baseline_active if key[0] == measure)
            k = _scaled_count(baseline_count, multiplier, len(candidates))
            ranked = sorted(candidates, key=lambda item: (-item[1], item[0]))
            selected.update(key for key, _ in ranked[:k])
        return selected

    raise ValueError(f"Unknown count policy: {policy}")


def _split_scores(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    spectrum_len: int,
    base_scores: dict[tuple[int, int], float],
    base_evidence: dict[tuple[int, int], bool],
    base_threshold: float,
    sequence_model: dict[str, Any],
    onset_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[tuple[int, int], float], dict[tuple[int, int], bool], dict[int, float]]:
    seq_scores, seq_evidence = consensus._sequence_scores_for_measures(
        rows_by_measure,
        grid,
        reference,
        measures,
        context_measures,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
    )
    _, onset_scores = consensus._onset_scores_for_measures(
        rows_by_measure,
        grid,
        measures,
        context_measures,
        spectrum_len,
        onset_model,
    )
    ds = consensus._meta_dataset(
        reference,
        measures,
        context_measures,
        rows_by_measure,
        grid,
        seq_scores,
        seq_evidence,
        onset_scores,
        float(sequence_model["threshold"]),
    )
    return ds, seq_scores, seq_evidence, onset_scores


def _evaluate_selection(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    onset_scores: dict[int, float],
    pitch_model: dict[str, Any],
    assign_window_ms: int,
    residual_penalty: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    assignments = consensus._assign_active_slots(
        active,
        rows_by_measure,
        grid,
        onset_scores,
        int(assign_window_ms),
        float(residual_penalty),
    )
    return consensus._evaluate(reference, assignments, grid, pitch_model)


def _objective(location: dict[str, Any], end_to_end: dict[str, Any]) -> float:
    precision = float(location["locationPrecisionPercent"])
    recall = float(location["locationRecallPercent"])
    f1 = float(location["locationF1Percent"])
    pitch_f1 = float(end_to_end["pitchF1Percent"])
    exact = float(end_to_end["exactPitchSetPercent"])
    score = 0.40 * pitch_f1 + 0.30 * f1 + 0.15 * precision + 0.10 * recall + 0.05 * exact
    if precision < 75.0:
        score -= 1.5 * (75.0 - precision)
    if recall < 75.0:
        score -= 0.75 * (75.0 - recall)
    return float(score)


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    sequence_model = _load_json(sequence.MODEL_PATH)
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
    base_scores, base_evidence = consensus._score_measures(
        rows_by_measure,
        grid,
        all_measures,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])

    print("=== V143 CONSTRAINED EVENT-COUNT RERANKER ===")
    print("Purpose: rerank high-recall onset proposals without allowing event-count explosion")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Measures 13-16: diagnostic only; not a fresh untouched holdout")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    train, train_seq, train_seq_evidence, train_onset = _split_scores(
        rows_by_measure,
        grid,
        train_reference,
        TRAIN_MEASURES,
        TRAIN_MEASURES,
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )
    validation, val_seq, val_seq_evidence, val_onset = _split_scores(
        rows_by_measure,
        grid,
        validation_reference,
        VALIDATION_MEASURES,
        set(range(1, 13)),
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )

    val_baseline = _baseline_active(
        validation["keys"],
        val_seq,
        val_seq_evidence,
        float(sequence_model["threshold"]),
    )
    print("validationSequenceBaselineCount:", len(val_baseline))

    best: dict[str, Any] | None = None
    searched = 0
    total = (
        len(L2_VALUES)
        * len(POSITIVE_WEIGHTS)
        * len(COUNT_POLICIES)
        * len(COUNT_MULTIPLIERS)
        * len(ASSIGN_WINDOWS_MS)
        * len(RESIDUAL_PENALTIES)
    )

    for l2 in L2_VALUES:
        for positive_weight in POSITIVE_WEIGHTS:
            mean, std, weights = _fit_weighted_ridge(
                train["X"],
                train["Y"],
                l2,
                positive_weight,
            )
            val_scores = _scores(validation["X"], mean, std, weights)
            for policy in COUNT_POLICIES:
                for multiplier in COUNT_MULTIPLIERS:
                    active = _select_ranked(
                        validation,
                        val_scores,
                        val_baseline,
                        policy,
                        multiplier,
                    )
                    for assign_window_ms in ASSIGN_WINDOWS_MS:
                        for residual_penalty in RESIDUAL_PENALTIES:
                            searched += 1
                            loc, e2e = _evaluate_selection(
                                active,
                                validation_reference,
                                rows_by_measure,
                                grid,
                                val_onset,
                                pitch_model,
                                assign_window_ms,
                                residual_penalty,
                            )
                            objective = _objective(loc, e2e)
                            candidate = {
                                "l2": float(l2),
                                "positiveWeight": float(positive_weight),
                                "countPolicy": policy,
                                "countMultiplier": float(multiplier),
                                "assignWindowMs": int(assign_window_ms),
                                "residualPenalty": float(residual_penalty),
                                "validationObjectivePercent": round(objective, 3),
                                "validationLocation": loc,
                                "validationEndToEnd": e2e,
                            }
                            if best is None or (
                                objective,
                                float(e2e["pitchF1Percent"]),
                                float(loc["locationF1Percent"]),
                                float(loc["locationPrecisionPercent"]),
                                float(loc["locationRecallPercent"]),
                            ) > (
                                float(best["validationObjectivePercent"]),
                                float(best["validationEndToEnd"]["pitchF1Percent"]),
                                float(best["validationLocation"]["locationF1Percent"]),
                                float(best["validationLocation"]["locationPrecisionPercent"]),
                                float(best["validationLocation"]["locationRecallPercent"]),
                            ):
                                best = candidate
                            if searched % 500 == 0 or searched == total:
                                print(f"searched {searched}/{total} constrained configurations")

    if best is None:
        raise RuntimeError("No constrained reranker configuration evaluated")

    development, dev_seq, dev_seq_evidence, dev_onset = _split_scores(
        rows_by_measure,
        grid,
        development_reference,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )
    holdout, hold_seq, hold_seq_evidence, hold_onset = _split_scores(
        rows_by_measure,
        grid,
        holdout_reference,
        HOLDOUT_MEASURES,
        all_measures,
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )

    mean, std, weights = _fit_weighted_ridge(
        development["X"],
        development["Y"],
        float(best["l2"]),
        float(best["positiveWeight"]),
    )
    dev_scores = _scores(development["X"], mean, std, weights)
    hold_scores = _scores(holdout["X"], mean, std, weights)

    dev_baseline = _baseline_active(
        development["keys"],
        dev_seq,
        dev_seq_evidence,
        float(sequence_model["threshold"]),
    )
    hold_baseline = _baseline_active(
        holdout["keys"],
        hold_seq,
        hold_seq_evidence,
        float(sequence_model["threshold"]),
    )

    dev_active = _select_ranked(
        development,
        dev_scores,
        dev_baseline,
        str(best["countPolicy"]),
        float(best["countMultiplier"]),
    )
    hold_active = _select_ranked(
        holdout,
        hold_scores,
        hold_baseline,
        str(best["countPolicy"]),
        float(best["countMultiplier"]),
    )

    dev_loc, dev_e2e = _evaluate_selection(
        dev_active,
        development_reference,
        rows_by_measure,
        grid,
        dev_onset,
        pitch_model,
        int(best["assignWindowMs"]),
        float(best["residualPenalty"]),
    )
    hold_loc, hold_e2e = _evaluate_selection(
        hold_active,
        holdout_reference,
        rows_by_measure,
        grid,
        hold_onset,
        pitch_model,
        int(best["assignWindowMs"]),
        float(best["residualPenalty"]),
    )

    report = {
        "model": "v143-constrained-event-count-reranker",
        "bestConfiguration": {
            key: best[key]
            for key in (
                "l2",
                "positiveWeight",
                "countPolicy",
                "countMultiplier",
                "assignWindowMs",
                "residualPenalty",
                "validationObjectivePercent",
            )
        },
        "validationLocation": best["validationLocation"],
        "validationEndToEnd": best["validationEndToEnd"],
        "developmentLocation": dev_loc,
        "developmentEndToEnd": dev_e2e,
        "diagnosticHoldoutLocation": hold_loc,
        "diagnosticHoldoutEndToEnd": hold_e2e,
        "sequenceBaselineCounts": {
            "validation": len(val_baseline),
            "development": len(dev_baseline),
            "diagnosticHoldout": len(hold_baseline),
        },
        "selectedCounts": {
            "development": len(dev_active),
            "diagnosticHoldout": len(hold_active),
        },
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because prior architecture iterations inspected them. A fresh unseen song/section is required before production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "l2": float(best["l2"]),
                "positiveWeight": float(best["positiveWeight"]),
                "countPolicy": str(best["countPolicy"]),
                "countMultiplier": float(best["countMultiplier"]),
                "assignWindowMs": int(best["assignWindowMs"]),
                "residualPenalty": float(best["residualPenalty"]),
                "sequenceThreshold": float(sequence_model["threshold"]),
                "featureMean": [round(float(value), 8) for value in mean],
                "featureStd": [round(float(value), 8) for value in std],
                "weights": [round(float(value), 8) for value in weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION CONSTRAINED CONFIGURATION ===")
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
    print("\nSequence baseline holdout count:", len(hold_baseline))
    print("Constrained selected holdout count:", len(hold_active))

    precision = float(hold_loc["locationPrecisionPercent"])
    recall = float(hold_loc["locationRecallPercent"])
    pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 78.0:
        diagnosis = "constrained-reranker-closes-event-selection-gap-freeze-core-and-test-fresh-section"
    elif precision >= 70.0 and recall >= 75.0 and pitch_f1 >= 72.0:
        diagnosis = "constrained-reranker-promising-one-final-structured-decoder-check"
    else:
        diagnosis = "count-constrained-reranking-insufficient-next-step-reference-free-beat-phase-sequence-decoder"
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
