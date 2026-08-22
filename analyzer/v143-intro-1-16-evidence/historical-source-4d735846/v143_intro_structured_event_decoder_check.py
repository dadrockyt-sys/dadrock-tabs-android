from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_constrained_count_reranker as constrained
import v143_intro_sequence_event_model as sequence
import v143_intro_onset_group_sequence_model as onset
import v143_intro_consensus_alignment_refinement as consensus
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


CONSTRAINED_MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-constrained-count-reranker-model.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-structured-event-decoder-check-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-structured-event-decoder-check-model.json"
)

COUNT_POLICIES = ("block", "per-measure")
COUNT_MULTIPLIERS = (0.90, 0.95, 1.00, 1.05, 1.10)
SEQUENCE_WEIGHTS = (0.0, 0.25, 0.5, 1.0)
RECURRENCE_WEIGHTS = (0.0, 0.25, 0.5, 1.0)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _rank_percentiles(
    values: dict[tuple[int, int], float],
    keys: list[tuple[int, int]],
    *,
    per_measure: bool,
) -> dict[tuple[int, int], float]:
    out: dict[tuple[int, int], float] = {}
    groups: dict[int, list[tuple[int, int]]] = {}
    if per_measure:
        for key in keys:
            groups.setdefault(int(key[0]), []).append(key)
    else:
        groups[0] = list(keys)

    for group_keys in groups.values():
        ranked = sorted(
            group_keys,
            key=lambda key: (float(values.get(key, 0.0)), key),
        )
        n = len(ranked)
        if n <= 1:
            for key in ranked:
                out[key] = 1.0
            continue
        for index, key in enumerate(ranked):
            out[key] = float(index) / float(n - 1)
    return out


def _recurrence_support(
    keys: list[tuple[int, int]],
    rerank_percentiles: dict[tuple[int, int], float],
) -> dict[tuple[int, int], float]:
    key_set = set(keys)
    measures = sorted({int(key[0]) for key in keys})
    result: dict[tuple[int, int], float] = {}
    for key in keys:
        measure, step = int(key[0]), int(key[1])
        all_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure and (other, step) in key_set
        ]
        phase2_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure
            and (other - 1) % 2 == (measure - 1) % 2
            and (other, step) in key_set
        ]
        phase4_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure
            and (other - 1) % 4 == (measure - 1) % 4
            and (other, step) in key_set
        ]
        candidates = []
        if all_peers:
            candidates.append(float(np.mean(all_peers)))
        if phase2_peers:
            candidates.append(float(np.mean(phase2_peers)))
        if phase4_peers:
            candidates.append(float(np.mean(phase4_peers)))
        result[key] = max(candidates) if candidates else 0.0
    return result


def _component_maps(
    ds: dict[str, Any],
    sequence_scores: dict[tuple[int, int], float],
    mean: np.ndarray,
    std: np.ndarray,
    weights: np.ndarray,
) -> tuple[
    list[tuple[int, int]],
    dict[tuple[int, int], float],
    dict[tuple[int, int], float],
    dict[tuple[int, int], float],
]:
    keys = [
        key
        for key, evidence in zip(ds["keys"], ds["evidence"])
        if bool(evidence)
    ]
    raw_scores = constrained._scores(ds["X"], mean, std, weights)
    rerank_values = {
        key: float(score)
        for key, score, evidence in zip(ds["keys"], raw_scores, ds["evidence"])
        if bool(evidence)
    }
    sequence_values = {
        key: float(sequence_scores.get(key, 0.0))
        for key in keys
    }
    rerank_pct = _rank_percentiles(rerank_values, keys, per_measure=True)
    sequence_pct = _rank_percentiles(sequence_values, keys, per_measure=True)
    recurrence = _recurrence_support(keys, rerank_pct)
    return keys, rerank_pct, sequence_pct, recurrence


def _combined_scores(
    keys: list[tuple[int, int]],
    rerank_pct: dict[tuple[int, int], float],
    sequence_pct: dict[tuple[int, int], float],
    recurrence: dict[tuple[int, int], float],
    sequence_weight: float,
    recurrence_weight: float,
) -> dict[tuple[int, int], float]:
    return {
        key: (
            float(rerank_pct.get(key, 0.0))
            + float(sequence_weight) * float(sequence_pct.get(key, 0.0))
            + float(recurrence_weight) * float(recurrence.get(key, 0.0))
        )
        for key in keys
    }


def _scaled_count(count: int, multiplier: float, eligible_count: int) -> int:
    if count <= 0 or eligible_count <= 0:
        return 0
    target = int(round(float(count) * float(multiplier)))
    return max(1, min(target, eligible_count))


def _select(
    keys: list[tuple[int, int]],
    combined: dict[tuple[int, int], float],
    baseline_active: set[tuple[int, int]],
    policy: str,
    multiplier: float,
) -> set[tuple[int, int]]:
    if not keys:
        return set()
    if policy == "block":
        k = _scaled_count(len(baseline_active), multiplier, len(keys))
        ranked = sorted(keys, key=lambda key: (-combined[key], key))
        return set(ranked[:k])
    if policy == "per-measure":
        selected: set[tuple[int, int]] = set()
        measures = sorted({int(key[0]) for key in keys})
        for measure in measures:
            measure_keys = [key for key in keys if int(key[0]) == measure]
            baseline_count = sum(1 for key in baseline_active if int(key[0]) == measure)
            k = _scaled_count(baseline_count, multiplier, len(measure_keys))
            ranked = sorted(measure_keys, key=lambda key: (-combined[key], key))
            selected.update(ranked[:k])
        return selected
    raise ValueError(f"Unknown policy: {policy}")


def _objective(location: dict[str, Any], end_to_end: dict[str, Any]) -> float:
    precision = float(location["locationPrecisionPercent"])
    recall = float(location["locationRecallPercent"])
    location_f1 = float(location["locationF1Percent"])
    pitch_f1 = float(end_to_end["pitchF1Percent"])
    exact = float(end_to_end["exactPitchSetPercent"])
    score = (
        0.40 * pitch_f1
        + 0.30 * location_f1
        + 0.15 * precision
        + 0.10 * recall
        + 0.05 * exact
    )
    if precision < 75.0:
        score -= 1.5 * (75.0 - precision)
    if recall < 80.0:
        score -= 1.0 * (80.0 - recall)
    return float(score)


def _evaluate(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    onset_scores: dict[int, float],
    pitch_model: dict[str, Any],
    constrained_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return constrained._evaluate_selection(
        active,
        reference,
        rows_by_measure,
        grid,
        onset_scores,
        pitch_model,
        int(constrained_model["assignWindowMs"]),
        float(constrained_model["residualPenalty"]),
    )


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    sequence_model = _load_json(sequence.MODEL_PATH)
    onset_model = _load_json(onset.MODEL_PATH)
    constrained_model = _load_json(CONSTRAINED_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)
    spectrum_len = int(spectrum_cache.get("spectrumMidiMax") or 112) - int(
        spectrum_cache.get("spectrumMidiMin") or 28
    ) + 1

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

    mean = np.asarray(constrained_model["featureMean"], dtype=np.float64)
    std = np.asarray(constrained_model["featureStd"], dtype=np.float64)
    weights = np.asarray(constrained_model["weights"], dtype=np.float64)

    validation, val_seq, val_seq_evidence, val_onset = constrained._split_scores(
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
    development, dev_seq, dev_seq_evidence, dev_onset = constrained._split_scores(
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
    holdout, hold_seq, hold_seq_evidence, hold_onset = constrained._split_scores(
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

    val_baseline = constrained._baseline_active(
        validation["keys"], val_seq, val_seq_evidence, float(sequence_model["threshold"])
    )
    dev_baseline = constrained._baseline_active(
        development["keys"], dev_seq, dev_seq_evidence, float(sequence_model["threshold"])
    )
    hold_baseline = constrained._baseline_active(
        holdout["keys"], hold_seq, hold_seq_evidence, float(sequence_model["threshold"])
    )

    val_components = _component_maps(validation, val_seq, mean, std, weights)
    dev_components = _component_maps(development, dev_seq, mean, std, weights)
    hold_components = _component_maps(holdout, hold_seq, mean, std, weights)

    print("=== V143 FINAL STRUCTURED EVENT DECODER CHECK ===")
    print("Purpose: preserve the constrained reranker's precision while recovering omitted recurrent events")
    print("Configuration chosen on measures 9-12 only")
    print("Measures 13-16 are diagnostic only; not a fresh untouched holdout")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    searched = 0
    total = (
        len(COUNT_POLICIES)
        * len(COUNT_MULTIPLIERS)
        * len(SEQUENCE_WEIGHTS)
        * len(RECURRENCE_WEIGHTS)
    )
    val_keys, val_rerank, val_sequence, val_recurrence = val_components
    for policy in COUNT_POLICIES:
        for multiplier in COUNT_MULTIPLIERS:
            for sequence_weight in SEQUENCE_WEIGHTS:
                for recurrence_weight in RECURRENCE_WEIGHTS:
                    searched += 1
                    combined = _combined_scores(
                        val_keys,
                        val_rerank,
                        val_sequence,
                        val_recurrence,
                        sequence_weight,
                        recurrence_weight,
                    )
                    active = _select(
                        val_keys,
                        combined,
                        val_baseline,
                        policy,
                        multiplier,
                    )
                    loc, e2e = _evaluate(
                        active,
                        validation_reference,
                        rows_by_measure,
                        grid,
                        val_onset,
                        pitch_model,
                        constrained_model,
                    )
                    objective = _objective(loc, e2e)
                    candidate = {
                        "countPolicy": policy,
                        "countMultiplier": float(multiplier),
                        "sequenceWeight": float(sequence_weight),
                        "recurrenceWeight": float(recurrence_weight),
                        "validationObjectivePercent": round(objective, 3),
                        "validationLocation": loc,
                        "validationEndToEnd": e2e,
                    }
                    if best is None or (
                        objective,
                        float(e2e["pitchF1Percent"]),
                        float(loc["locationF1Percent"]),
                        float(loc["locationRecallPercent"]),
                        float(loc["locationPrecisionPercent"]),
                    ) > (
                        float(best["validationObjectivePercent"]),
                        float(best["validationEndToEnd"]["pitchF1Percent"]),
                        float(best["validationLocation"]["locationF1Percent"]),
                        float(best["validationLocation"]["locationRecallPercent"]),
                        float(best["validationLocation"]["locationPrecisionPercent"]),
                    ):
                        best = candidate
                    if searched % 40 == 0 or searched == total:
                        print(f"searched {searched}/{total} structured configurations")

    if best is None:
        raise RuntimeError("No structured configuration evaluated")

    def run_split(
        components: tuple[
            list[tuple[int, int]],
            dict[tuple[int, int], float],
            dict[tuple[int, int], float],
            dict[tuple[int, int], float],
        ],
        baseline: set[tuple[int, int]],
        reference: dict[tuple[int, int], set[int]],
        onset_scores: dict[int, float],
    ) -> tuple[set[tuple[int, int]], dict[str, Any], dict[str, Any]]:
        keys, rerank_pct, sequence_pct, recurrence = components
        combined = _combined_scores(
            keys,
            rerank_pct,
            sequence_pct,
            recurrence,
            float(best["sequenceWeight"]),
            float(best["recurrenceWeight"]),
        )
        active = _select(
            keys,
            combined,
            baseline,
            str(best["countPolicy"]),
            float(best["countMultiplier"]),
        )
        loc, e2e = _evaluate(
            active,
            reference,
            rows_by_measure,
            grid,
            onset_scores,
            pitch_model,
            constrained_model,
        )
        return active, loc, e2e

    dev_active, dev_loc, dev_e2e = run_split(
        dev_components, dev_baseline, development_reference, dev_onset
    )
    hold_active, hold_loc, hold_e2e = run_split(
        hold_components, hold_baseline, holdout_reference, hold_onset
    )

    report = {
        "model": "v143-final-structured-event-decoder-check",
        "bestConfiguration": {
            key: best[key]
            for key in (
                "countPolicy",
                "countMultiplier",
                "sequenceWeight",
                "recurrenceWeight",
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
        "structuredSelectedCounts": {
            "development": len(dev_active),
            "diagnosticHoldout": len(hold_active),
        },
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because architecture decisions have already inspected them. A fresh unseen song/section is mandatory before any production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                **report["bestConfiguration"],
                "assignWindowMs": int(constrained_model["assignWindowMs"]),
                "residualPenalty": float(constrained_model["residualPenalty"]),
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION STRUCTURED CONFIGURATION ===")
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
    print("Structured selected holdout count:", len(hold_active))

    precision = float(hold_loc["locationPrecisionPercent"])
    recall = float(hold_loc["locationRecallPercent"])
    pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 78.0:
        diagnosis = "structured-decoder-passes-calibration-gate-freeze-core-and-test-fresh-unseen-section"
    elif precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 75.0:
        diagnosis = "structured-decoder-near-gate-do-not-retune-on-this-diagnostic-move-to-fresh-section"
    else:
        diagnosis = "structured-decoder-insufficient-do-not-freeze-event-core"
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
