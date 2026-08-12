from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import benchmark_gomyway_3676_patch_rhythm24_oof_percentile_logit_calibration_v30 as v30

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-conservative-allscheme-consensus-v34.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-conservative-allscheme-consensus-v34-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
CHALLENGE_PHASES = v28.CONFIRM_PHASES
MIN_LIFT = 5.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inner_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % INNER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def widest_passing_threshold(percentiles: np.ndarray, yy: np.ndarray) -> tuple[float | None, dict[str, Any]]:
    z = np.asarray(percentiles, dtype=np.float64)
    labels = np.asarray(yy, dtype=bool)
    if z.size == 0:
        return None, {"reason": "empty"}
    base = v1.base_stats(labels)
    candidates = np.unique(z)
    candidates.sort()
    for threshold in candidates:
        chosen = z >= float(threshold)
        selected = int(np.sum(chosen))
        if selected == 0:
            continue
        true = int(np.sum(labels[chosen]))
        false = int(selected - true)
        precision = 100.0 * true / selected
        lift = precision - float(base["precision"])
        if true > 0 and lift >= MIN_LIFT:
            return float(threshold), {
                "base": base,
                "passing": {
                    "selected": selected,
                    "true": true,
                    "false": false,
                    "precision": round(float(precision), 2),
                    "lift": round(float(lift), 2),
                },
            }
    return None, {"base": base, "passing": None}


def derive_training_only_cutoff(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    radius: int,
    lam: float,
) -> tuple[float, dict[str, Any]]:
    scheme_rows = []
    scheme_medians = []
    for scheme in INNER_SCHEMES:
        ids = inner_ids(measures_train, scheme)
        fold_rows = []
        thresholds = []
        for fold in range(INNER_FOLDS):
            val = ids == fold
            subtrain = ~val
            if not np.any(val) or not np.any(subtrain):
                continue
            model = v2.fit_pairwise_ranker(x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam)
            sub_scores = v2.scores_for(x_train[subtrain], model)
            val_scores = v2.scores_for(x_train[val], model)
            pct = v30.empirical_percentile(sub_scores, val_scores)
            threshold, info = widest_passing_threshold(pct, y_train[val])
            if threshold is not None:
                thresholds.append(float(threshold))
            fold_rows.append({
                "fold": int(fold),
                "threshold": threshold,
                "validationCount": int(np.sum(val)),
                "validationTrue": int(np.sum(y_train[val])),
                "diagnostic": info,
            })
        if thresholds:
            scheme_median = float(np.median(np.asarray(thresholds, dtype=np.float64)))
            scheme_medians.append(scheme_median)
        else:
            scheme_median = None
        scheme_rows.append({
            "scheme": scheme,
            "foldThresholds": thresholds,
            "schemeMedianThreshold": scheme_median,
            "folds": fold_rows,
        })

    if len(scheme_medians) != len(INNER_SCHEMES):
        raise RuntimeError("V34 requires a passing training-only threshold from every inner scheme")

    # V33 diagnosed a direction only (V32 regressions selected too broadly).
    # No V33 observed numeric cutoff is copied. V34 predeclares a conservative
    # all-scheme agreement rule: use the maximum of the three training-only
    # scheme medians, so a candidate must satisfy the strictest scheme median.
    cutoff = float(np.max(np.asarray(scheme_medians, dtype=np.float64)))
    return cutoff, {
        "architecture": "training-only-cross-boundary-conservative-all-scheme-consensus",
        "criterion": "widest-inner-validation-selection-with-lift-at-least-5",
        "withinSchemeAggregation": "median-of-passing-inner-fold-thresholds",
        "acrossSchemeAggregation": "maximum-of-three-scheme-medians",
        "interpretation": "strictest-training-only-scheme-median",
        "schemeMedians": scheme_medians,
        "derivedPercentileCutoff": cutoff,
        "innerSchemes": list(INNER_SCHEMES),
        "innerFoldsPerScheme": INNER_FOLDS,
        "outerHeldoutLabelsUsed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
    }


def evaluate_phase(x: np.ndarray, y: np.ndarray, measures: np.ndarray, phase: float) -> tuple[int, list[dict[str, Any]]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
    rows = []
    passes = 0
    for fold in range(OUTER_FOLDS):
        print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        print("    heartbeat V34 frozen V17 representation/model-selection", flush=True)
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        print("    heartbeat V34 training-only conservative all-scheme consensus", flush=True)
        cutoff, calibration = derive_training_only_cutoff(x[train], y[train], measures[train], radius, lam)
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        train_scores = v2.scores_for(x[train], model)
        test_scores = v2.scores_for(x[test], model)
        test_pct = v30.empirical_percentile(train_scores, test_scores)
        chosen = test_pct >= cutoff
        true = int(np.sum(y[test][chosen]))
        false = int(np.sum(~y[test][chosen]))
        selected = int(np.sum(chosen))
        precision = 100.0 * true / selected if selected else 0.0
        held = {"selected": selected, "true": true, "false": false, "precision": round(float(precision), 2)}
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = bool(true > 0 and lift >= MIN_LIFT)
        v28_passed, v28_lift, v28_held, _ = v17.pass_at_q(test_scores, y[test], v28.FROZEN_Q)
        passes += int(passed)
        rows.append({
            "phase": float(phase),
            "fold": int(fold),
            "chosenModel": chosen_model,
            "trainingOnlyCalibration": calibration,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": passed,
            "v28Comparison": {
                "frozenQ": v28.FROZEN_Q,
                "heldoutCandidate": v28_held,
                "heldoutPrecisionLift": round(float(v28_lift), 2),
                "passed": bool(v28_passed),
            },
        })
        print(f"  V34 cutoff={cutoff:.6f} held={true}/{false} lift={round(lift,2)} pass={passed}; V28 pass={v28_passed}", flush=True)
    return passes, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    x = np.concatenate([x_base, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    print("Starting V34 conservative all-scheme percentile consensus challenger", flush=True)
    print("V28 phases are already exposed and evaluation-only", flush=True)
    print("Reserved 1/32 confirmation phases are not referenced", flush=True)
    print("V33 failure direction motivated conservatism; no V33 numeric cutoff is copied", flush=True)

    schemes = []
    total_passes = 0
    total_folds = 0
    v28_total = 0
    rescues = 0
    regressions = 0
    for phase in CHALLENGE_PHASES:
        phase_passes, phase_rows = evaluate_phase(x, y, measures, float(phase))
        v28_phase = sum(int(r["v28Comparison"]["passed"]) for r in phase_rows)
        schemes.append({"phase": float(phase), "passes": phase_passes, "v28Passes": v28_phase, "folds": phase_rows})
        total_passes += phase_passes
        v28_total += v28_phase
        total_folds += len(phase_rows)
        for row in phase_rows:
            vp = bool(row["passed"])
            bp = bool(row["v28Comparison"]["passed"])
            rescues += int(vp and not bp)
            regressions += int(bp and not vp)

    min_phase = min(s["passes"] for s in schemes)
    exploratory_promising = total_passes > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V34")

    output = {
        "schemaVersion": 34,
        "profileType": "36.76-rhythm24-training-only-oof-conservative-all-scheme-consensus",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "challengeSource": "already-exposed-V28-phases",
        "challengePhases": list(CHALLENGE_PHASES),
        "reservedUntouchedPhasesConsumed": False,
        "calibrationArchitecture": "cross-boundary-OOF-conservative-all-scheme-consensus",
        "qSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
        "v33FailureDirectionUsedOnlyAsArchitectureMotivation": True,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "challengeHeldoutLabelsUsedForEvaluationOnly": True,
        "foldsPassed": int(total_passes),
        "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase),
        "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "requiresUntouchedConfirmationBeforeValidation": True,
        "validatedNewChampion": False,
        "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 34,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total_passes),
        "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase),
        "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "reservedUntouchedPhasesConsumed": False,
        "qSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 OOF CONSERVATIVE ALL-SCHEME CONSENSUS V34 COMPLETE")
    print("V34 folds passed:", total_passes, "/", total_folds)
    print("Minimum V34 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", total_folds)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Exploratory promising:", exploratory_promising)
    print("Reserved untouched phases consumed: False")
    print("V29 diagnostic q values used: False")
    print("V31 observed cutoff copied: False")
    print("V33 observed numeric cutoff copied: False")
    print("Outer heldout labels used to choose calibration parameters: False")
    print("Validated new champion: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
