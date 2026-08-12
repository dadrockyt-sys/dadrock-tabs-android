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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-oof-percentile-logit-calibration-v30-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
CHALLENGE_PHASES = v28.CONFIRM_PHASES
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
LOGIT_L2 = 1.0
LOGIT_MAX_ITER = 80
LOGIT_TOL = 1e-10
PROBABILITY_CUTOFF = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def empirical_percentile(reference_scores: np.ndarray, query_scores: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(reference_scores, dtype=np.float64))
    query = np.asarray(query_scores, dtype=np.float64)
    if ref.size == 0:
        raise RuntimeError("Empty percentile reference")
    left = np.searchsorted(ref, query, side="left")
    right = np.searchsorted(ref, query, side="right")
    mid = 0.5 * (left + right)
    return (mid + 0.5) / float(ref.size + 1)


def fit_balanced_logit(z: np.ndarray, labels: np.ndarray) -> dict[str, Any]:
    z = np.asarray(z, dtype=np.float64).reshape(-1)
    yy = np.asarray(labels, dtype=bool).reshape(-1)
    n_pos = int(np.sum(yy))
    n_neg = int(yy.size - n_pos)
    if z.size == 0 or n_pos == 0 or n_neg == 0:
        raise RuntimeError("OOF calibration requires both classes")

    weights = np.where(yy, 0.5 / n_pos, 0.5 / n_neg) * yy.size
    design = np.column_stack([np.ones(z.size, dtype=np.float64), z])
    beta = np.zeros(2, dtype=np.float64)
    penalty = np.diag([0.0, LOGIT_L2])

    for _ in range(LOGIT_MAX_ITER):
        eta = np.clip(design @ beta, -35.0, 35.0)
        prob = 1.0 / (1.0 + np.exp(-eta))
        grad = design.T @ (weights * (prob - yy.astype(np.float64))) + penalty @ beta
        curvature = weights * prob * (1.0 - prob)
        hess = design.T @ (design * curvature[:, None]) + penalty
        try:
            step = np.linalg.solve(hess, grad)
        except np.linalg.LinAlgError:
            step = np.linalg.pinv(hess) @ grad
        new_beta = beta - step
        if float(np.max(np.abs(new_beta - beta))) < LOGIT_TOL:
            beta = new_beta
            break
        beta = new_beta

    return {
        "intercept": float(beta[0]),
        "slope": float(beta[1]),
        "l2": LOGIT_L2,
        "classBalance": "equal-total-positive-negative-weight",
        "probabilityCutoff": PROBABILITY_CUTOFF,
    }


def predict_probability(percentiles: np.ndarray, calibrator: dict[str, Any]) -> np.ndarray:
    eta = float(calibrator["intercept"]) + float(calibrator["slope"]) * np.asarray(percentiles)
    eta = np.clip(eta, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-eta))


def inner_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % INNER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def build_calibrator(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    radius: int,
    lam: float,
) -> tuple[dict[str, Any], dict[str, Any]]:
    percentile_parts = []
    label_parts = []
    fold_details = []

    for scheme in INNER_SCHEMES:
        ids = inner_ids(measures_train, scheme)
        for fold in range(INNER_FOLDS):
            val = ids == fold
            subtrain = ~val
            if not np.any(val) or not np.any(subtrain):
                continue
            model = v2.fit_pairwise_ranker(
                x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam
            )
            subtrain_scores = v2.scores_for(x_train[subtrain], model)
            val_scores = v2.scores_for(x_train[val], model)
            pct = empirical_percentile(subtrain_scores, val_scores)
            percentile_parts.append(pct)
            label_parts.append(y_train[val])
            fold_details.append({
                "scheme": scheme,
                "fold": int(fold),
                "subtrainCount": int(np.sum(subtrain)),
                "validationCount": int(np.sum(val)),
                "validationTrue": int(np.sum(y_train[val])),
                "validationFalse": int(np.sum(~y_train[val])),
                "percentileMean": round(float(np.mean(pct)), 6),
            })

    z = np.concatenate(percentile_parts)
    yy = np.concatenate(label_parts)
    calibrator = fit_balanced_logit(z, yy)
    oof_prob = predict_probability(z, calibrator)
    chosen = oof_prob >= PROBABILITY_CUTOFF
    diagnostics = {
        "architecture": "training-only-cross-boundary-oof-empirical-percentile-balanced-logit",
        "innerSchemes": list(INNER_SCHEMES),
        "innerFoldsPerScheme": INNER_FOLDS,
        "oofRows": int(z.size),
        "oofTrue": int(np.sum(yy)),
        "oofFalse": int(np.sum(~yy)),
        "oofSelected": int(np.sum(chosen)),
        "oofSelectedTrue": int(np.sum(yy[chosen])) if np.any(chosen) else 0,
        "oofSelectedFalse": int(np.sum(~yy[chosen])) if np.any(chosen) else 0,
        "calibrator": calibrator,
        "folds": fold_details,
        "heldoutLabelsUsedForCalibrationFit": False,
        "qSearchPerformed": False,
    }
    return calibrator, diagnostics


def selected_stats(probabilities: np.ndarray, yy: np.ndarray) -> tuple[dict[str, Any], dict[str, Any], float, bool]:
    chosen = np.asarray(probabilities) >= PROBABILITY_CUTOFF
    true = int(np.sum(yy[chosen]))
    false = int(np.sum(~yy[chosen]))
    selected = int(np.sum(chosen))
    precision = 100.0 * true / selected if selected else 0.0
    held = {"selected": selected, "true": true, "false": false, "precision": round(precision, 2)}
    base = v1.base_stats(yy)
    lift = float(held["precision"]) - float(base["precision"])
    passed = true > 0 and lift >= 5.0
    return held, base, lift, bool(passed)


def evaluate_phase(x: np.ndarray, y: np.ndarray, measures: np.ndarray, phase: float) -> tuple[int, list[dict[str, Any]]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
    rows = []
    passes = 0

    for fold in range(OUTER_FOLDS):
        print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        print("    heartbeat V30 frozen V17 representation/model-selection", flush=True)
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])

        print("    heartbeat V30 training-only cross-boundary OOF calibration", flush=True)
        calibrator, calibration = build_calibrator(x[train], y[train], measures[train], radius, lam)
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        train_scores = v2.scores_for(x[train], model)
        test_scores = v2.scores_for(x[test], model)
        test_pct = empirical_percentile(train_scores, test_scores)
        probabilities = predict_probability(test_pct, calibrator)
        held, base, lift, passed = selected_stats(probabilities, y[test])

        v28_passed, v28_lift, v28_held, _ = v17.pass_at_q(test_scores, y[test], v28.FROZEN_Q)
        passes += int(passed)
        rows.append({
            "phase": float(phase),
            "fold": int(fold),
            "chosenModel": chosen_model,
            "calibration": calibration,
            "fixedProbabilityCutoff": PROBABILITY_CUTOFF,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": bool(passed),
            "v28Comparison": {
                "frozenQ": v28.FROZEN_Q,
                "heldoutCandidate": v28_held,
                "heldoutPrecisionLift": round(float(v28_lift), 2),
                "passed": bool(v28_passed),
            },
        })
        print(
            f"  V30 held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}; V28 pass={v28_passed}",
            flush=True,
        )
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

    print("Starting V30 training-only OOF percentile/logit calibration challenger", flush=True)
    print("Ranking/representation: frozen V17 architecture", flush=True)
    print("No q search; no heldout labels used to fit calibration", flush=True)
    print("V28 phases are already exposed and evaluation-only in V30", flush=True)

    schemes = []
    total_passes = 0
    total_folds = 0
    v28_total_passes = 0
    for phase in CHALLENGE_PHASES:
        phase_passes, phase_rows = evaluate_phase(x, y, measures, float(phase))
        v28_phase_passes = sum(int(r["v28Comparison"]["passed"]) for r in phase_rows)
        schemes.append({"phase": float(phase), "passes": phase_passes, "v28Passes": v28_phase_passes, "folds": phase_rows})
        total_passes += phase_passes
        v28_total_passes += v28_phase_passes
        total_folds += len(phase_rows)

    min_phase_passes = min(s["passes"] for s in schemes)
    v28_min_phase_passes = min(s["v28Passes"] for s in schemes)
    rescues = 0
    regressions = 0
    for scheme in schemes:
        for row in scheme["folds"]:
            vp = bool(row["passed"])
            bp = bool(row["v28Comparison"]["passed"])
            rescues += int(vp and not bp)
            regressions += int(bp and not vp)

    exploratory_promising = total_passes > v28_total_passes and min_phase_passes >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V30")

    output = {
        "schemaVersion": 30,
        "profileType": "36.76-rhythm24-training-only-oof-percentile-logit-calibration",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "challengeSource": "already-exposed-V28-phases",
        "challengePhases": list(CHALLENGE_PHASES),
        "calibrationArchitecture": "cross-boundary-OOF-empirical-percentile-balanced-logit",
        "innerSchemes": list(INNER_SCHEMES),
        "innerFoldsPerScheme": INNER_FOLDS,
        "logitL2": LOGIT_L2,
        "fixedProbabilityCutoff": PROBABILITY_CUTOFF,
        "qSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "outerHeldoutLabelsUsedToFitCalibration": False,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "challengeHeldoutLabelsUsedForEvaluationOnly": True,
        "foldsPassed": int(total_passes),
        "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase_passes),
        "v28ComparisonPasses": int(v28_total_passes),
        "v28ComparisonMinimumPhasePasses": int(v28_min_phase_passes),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "requiresUntouchedConfirmationBeforeValidation": True,
        "schemes": schemes,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedForCalibration": False,
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
        "schemaVersion": 30,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total_passes),
        "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase_passes),
        "v28ComparisonPasses": int(v28_total_passes),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "qSearchPerformed": False,
        "outerHeldoutLabelsUsedToFitCalibration": False,
        "v29DiagnosticQValuesUsed": False,
        "requiresUntouchedConfirmationBeforeValidation": True,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 OOF PERCENTILE LOGIT CALIBRATION V30 COMPLETE")
    print("V30 folds passed:", total_passes, "/", total_folds)
    for s in schemes:
        print("phase", s["phase"], "V30 passes:", s["passes"], "/ 5", "V28 passes:", s["v28Passes"], "/ 5")
    print("Minimum V30 phase passes:", min_phase_passes, "/ 5")
    print("V28 comparison passes:", v28_total_passes, "/", total_folds)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Exploratory promising:", exploratory_promising)
    print("q search performed: False")
    print("V29 diagnostic q values used: False")
    print("Outer heldout labels used to fit calibration: False")
    print("Requires untouched confirmation before validation: True")
    print("Validated new champion: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
