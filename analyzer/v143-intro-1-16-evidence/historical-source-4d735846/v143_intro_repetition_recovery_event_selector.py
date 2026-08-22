from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import CACHE_PATH as RAW_CACHE_PATH, REFERENCE_PATH, _grid_lookup
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    MODEL_PATH as SELECTOR_MODEL_PATH,
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

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-repetition-recovery-event-selector-report.json"
)

MARGINS = (0.05, 0.10, 0.15, 0.20, 0.30, 0.40)
MIN_SUPPORTS = (0.25, 0.40, 0.50, 0.60, 0.75)
PHASE_MODULI = (1, 2, 4)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _score_measures(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    selector_model: dict[str, Any],
) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], bool]]:
    window_ms = int(selector_model["windowMs"])
    mean = np.asarray(selector_model["featureMean"], dtype=np.float64)
    std = np.asarray(selector_model["featureStd"], dtype=np.float64)
    weights = np.asarray(selector_model["weights"], dtype=np.float64)

    score_by_key: dict[tuple[int, int], float] = {}
    evidence_by_key: dict[tuple[int, int], bool] = {}
    for key in _grid_keys(measures):
        target_time = grid.get(key)
        if target_time is None:
            continue
        feature, nearest = _grid_feature(
            rows_by_measure,
            int(key[0]),
            int(key[1]),
            float(target_time),
            window_ms,
        )
        z = (feature - mean) / std
        design = np.concatenate([np.ones(1, dtype=np.float64), z])
        score_by_key[key] = float(design @ weights)
        evidence_by_key[key] = nearest is not None
    return score_by_key, evidence_by_key


def _recurrence_support(
    key: tuple[int, int],
    seeds: set[tuple[int, int]],
    measures: set[int],
    phase_modulus: int,
) -> float:
    measure, step = key
    phase = (measure - 1) % max(int(phase_modulus), 1)
    peers = [
        other
        for other in sorted(measures)
        if other != measure and (other - 1) % max(int(phase_modulus), 1) == phase
    ]
    if not peers:
        return 0.0
    return sum((other, step) in seeds for other in peers) / float(len(peers))


def _recover(
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    measures: set[int],
    base_threshold: float,
    margin: float,
    min_support: float,
    phase_modulus: int,
) -> set[tuple[int, int]]:
    seeds = {
        key
        for key, score in scores.items()
        if key[0] in measures and evidence.get(key, False) and float(score) >= float(base_threshold)
    }
    active = set(seeds)
    low_threshold = float(base_threshold) - float(margin)

    # Two passes allow strong repeated locations recovered in the first pass to
    # reinforce the same rhythmic phase elsewhere, while every decision remains
    # based only on analyzer scores and repetition structure.
    for _ in range(2):
        additions: set[tuple[int, int]] = set()
        for key, score in scores.items():
            if key[0] not in measures or key in active or not evidence.get(key, False):
                continue
            if float(score) < low_threshold:
                continue
            support = _recurrence_support(key, active, measures, phase_modulus)
            if support >= float(min_support):
                additions.add(key)
        if not additions:
            break
        active |= additions
    return active


def _location_metrics(reference: dict[tuple[int, int], set[int]], active: set[tuple[int, int]]) -> dict[str, Any]:
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


def _evaluate_candidate(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    selector_model: dict[str, Any],
    pitch_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    loc = _location_metrics(reference, active)
    assignments = _assign_groups_reference_free(
        active,
        rows_by_measure,
        grid,
        int(selector_model["windowMs"]),
    )
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)
    e2e = _evaluate_end_to_end(reference, pitch_sets)
    return loc, e2e


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    selector_model = _load_json(SELECTOR_MODEL_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)

    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    all_measures = set(range(1, 17))
    scores_all, evidence_all = _score_measures(rows_by_measure, grid, all_measures, selector_model)
    base_threshold = float(selector_model["threshold"])

    print("=== V143 REPETITION-AWARE EVENT RECOVERY SELECTOR ===")
    print("Base selector threshold:", base_threshold)
    print("Configuration chosen on measures 9-12 only")
    print("Measures 13-16 used only as diagnostic evaluation")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    searched = 0
    validation_context = set(range(1, 13))
    for margin in MARGINS:
        for min_support in MIN_SUPPORTS:
            for phase_modulus in PHASE_MODULI:
                searched += 1
                recovered_context = _recover(
                    scores_all,
                    evidence_all,
                    validation_context,
                    base_threshold,
                    margin,
                    min_support,
                    phase_modulus,
                )
                active_validation = {key for key in recovered_context if key[0] in VALIDATION_MEASURES}
                loc, e2e = _evaluate_candidate(
                    active_validation,
                    validation_reference,
                    rows_by_measure,
                    grid,
                    selector_model,
                    pitch_model,
                )
                objective = (
                    0.70 * float(e2e["pitchF1Percent"])
                    + 0.20 * float(loc["locationF1Percent"])
                    + 0.10 * float(e2e["exactPitchSetPercent"])
                )
                candidate = {
                    "margin": float(margin),
                    "minimumRecurrenceSupport": float(min_support),
                    "phaseModulus": int(phase_modulus),
                    "validationObjectivePercent": round(objective, 3),
                    "validationLocation": loc,
                    "validationEndToEnd": e2e,
                }
                if best is None or (
                    objective,
                    float(e2e["pitchF1Percent"]),
                    float(loc["locationRecallPercent"]),
                    float(loc["locationPrecisionPercent"]),
                ) > (
                    float(best["validationObjectivePercent"]),
                    float(best["validationEndToEnd"]["pitchF1Percent"]),
                    float(best["validationLocation"]["locationRecallPercent"]),
                    float(best["validationLocation"]["locationPrecisionPercent"]),
                ):
                    best = candidate

    if best is None:
        raise RuntimeError("No repetition-recovery configuration evaluated")

    development_context = set(range(1, 13))
    development_active_all = _recover(
        scores_all,
        evidence_all,
        development_context,
        base_threshold,
        float(best["margin"]),
        float(best["minimumRecurrenceSupport"]),
        int(best["phaseModulus"]),
    )
    development_active = {key for key in development_active_all if key[0] in DEVELOPMENT_MEASURES}
    dev_loc, dev_e2e = _evaluate_candidate(
        development_active,
        development_reference,
        rows_by_measure,
        grid,
        selector_model,
        pitch_model,
    )

    # Holdout remains label-free during inference. Repetition support may use the
    # entire analyzed intro, exactly as a production decoder can use the full song
    # after upload; only the grading below touches professional labels.
    full_active = _recover(
        scores_all,
        evidence_all,
        all_measures,
        base_threshold,
        float(best["margin"]),
        float(best["minimumRecurrenceSupport"]),
        int(best["phaseModulus"]),
    )
    holdout_active = {key for key in full_active if key[0] in HOLDOUT_MEASURES}
    hold_loc, hold_e2e = _evaluate_candidate(
        holdout_active,
        holdout_reference,
        rows_by_measure,
        grid,
        selector_model,
        pitch_model,
    )

    report = {
        "model": "v143-repetition-aware-event-recovery-selector",
        "baseSelectorThreshold": base_threshold,
        "bestConfiguration": {
            "margin": best["margin"],
            "minimumRecurrenceSupport": best["minimumRecurrenceSupport"],
            "phaseModulus": best["phaseModulus"],
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
        "evaluationNote": "Measures 13-16 are now diagnostic holdout because prior architecture iterations have already inspected them; use a fresh song/section before promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("\n=== BEST VALIDATION RECOVERY CONFIGURATION ===")
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

    hold_loc_recall = float(hold_loc["locationRecallPercent"])
    hold_pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if hold_loc_recall >= 80.0 and hold_pitch_f1 >= 80.0:
        diagnosis = "repetition-recovery-closes-most-of-event-selection-gap"
    elif hold_loc_recall >= 70.0 and hold_pitch_f1 >= 72.0:
        diagnosis = "repetition-recovery-helps-but-event-selector-still-needs-sequence-model"
    else:
        diagnosis = "simple-repetition-recovery-insufficient-build-sequence-event-model"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("NOTE: measures 13-16 are diagnostic, not a fresh untouched holdout anymore.")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
