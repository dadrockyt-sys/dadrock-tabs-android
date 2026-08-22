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
import benchmark_gomyway_3676_patch_rhythm24_oof_conservative_allscheme_consensus_v34 as v34

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-exact-anchor-unanimous-training-tighten-v38.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-exact-anchor-unanimous-training-tighten-v38-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
CHALLENGE_PHASES = v28.CONFIRM_PHASES
ANCHOR_Q = float(v28.FROZEN_Q)
MIN_LIFT = 5.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pass_for_top_k(scores: np.ndarray, yy: np.ndarray, k: int) -> tuple[bool, float, dict[str, Any], dict[str, Any]]:
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.asarray(yy, dtype=bool)
    n = int(scores.size)
    k = max(1, min(int(k), n))
    order = np.argsort(-scores, kind="mergesort")[:k]
    true = int(np.sum(labels[order]))
    false = int(k - true)
    precision = 100.0 * true / k
    held = {"selected": k, "true": true, "false": false, "precision": round(float(precision), 2)}
    base = v1.base_stats(labels)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(true > 0 and lift >= MIN_LIFT), float(lift), held, base


def widest_passing_fraction(scores: np.ndarray, yy: np.ndarray) -> tuple[float | None, dict[str, Any]]:
    n = int(len(scores))
    best = None
    best_info = None
    for k in range(n, 0, -1):
        passed, lift, held, base = pass_for_top_k(scores, yy, k)
        if passed:
            best = float(k / n)
            best_info = {"k": int(k), "n": n, "fraction": best, "lift": round(lift, 2), "held": held, "base": base}
            break
    return best, best_info or {"n": n, "reason": "no-passing-selection"}


def inner_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % INNER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def derive_q(x_train: np.ndarray, y_train: np.ndarray, measures_train: np.ndarray, radius: int, lam: float) -> tuple[float, dict[str, Any]]:
    scheme_rows = []
    scheme_medians = []
    all_scheme_support_tightening = True

    for scheme in INNER_SCHEMES:
        ids = inner_ids(measures_train, scheme)
        fractions = []
        fold_rows = []
        for fold in range(INNER_FOLDS):
            val = ids == fold
            subtrain = ~val
            if not np.any(val) or not np.any(subtrain):
                continue
            model = v2.fit_pairwise_ranker(x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam)
            val_scores = v2.scores_for(x_train[val], model)
            frac, info = widest_passing_fraction(val_scores, y_train[val])
            if frac is not None:
                fractions.append(float(frac))
            anchor_pass, anchor_lift, anchor_held, anchor_base = v17.pass_at_q(val_scores, y_train[val], ANCHOR_Q)
            fold_rows.append({
                "fold": int(fold),
                "widestPassingFraction": frac,
                "widestPassing": info,
                "anchorQ": ANCHOR_Q,
                "anchorPassed": bool(anchor_pass),
                "anchorLift": round(float(anchor_lift), 2),
                "anchorHeld": anchor_held,
                "anchorBase": anchor_base,
            })

        if not fractions:
            median_fraction = None
            all_scheme_support_tightening = False
        else:
            median_fraction = float(np.median(np.asarray(fractions, dtype=np.float64)))
            if not (median_fraction < ANCHOR_Q):
                all_scheme_support_tightening = False
            scheme_medians.append(median_fraction)
        scheme_rows.append({
            "scheme": scheme,
            "medianWidestPassingFraction": median_fraction,
            "folds": fold_rows,
        })

    if all_scheme_support_tightening and len(scheme_medians) == len(INNER_SCHEMES):
        # Require unanimous scheme-level evidence before deviating from the frozen V28 anchor.
        # Use the least aggressive tightening endorsed by all schemes: maximum scheme median.
        chosen_q = float(max(scheme_medians))
        tightened = True
    else:
        chosen_q = ANCHOR_Q
        tightened = False

    return chosen_q, {
        "architecture": "exact-v28-top-fraction-anchor-with-unanimous-training-only-tightening",
        "anchorQ": ANCHOR_Q,
        "schemeMedianWidestPassingFractions": scheme_medians,
        "allSchemesSupportTightening": bool(all_scheme_support_tightening),
        "chosenQ": float(chosen_q),
        "tightenedBelowAnchorQ": bool(tightened),
        "acrossSchemeRule": "tighten-only-if-all-three-scheme-medians-below-anchor; choose-max-scheme-median",
        "outerHeldoutLabelsUsed": False,
        "qSearchOnOuterHeldout": False,
        "v29DiagnosticQValuesUsed": False,
        "v31ObservedCutoffCopied": False,
        "v33ObservedNumericCutoffCopied": False,
        "v35ObservedNumericCutoffCopied": False,
        "v37ObservedNumericDeltaCopied": False,
        "schemes": scheme_rows,
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
        print("    heartbeat V38 frozen V17 representation/model-selection", flush=True)
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        print("    heartbeat V38 exact V28 anchor plus unanimous training-only tightening", flush=True)
        chosen_q, calibration = derive_q(x[train], y[train], measures[train], radius, lam)
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        test_scores = v2.scores_for(x[test], model)
        passed, lift, held, base = v17.pass_at_q(test_scores, y[test], chosen_q)
        v28_passed, v28_lift, v28_held, _ = v17.pass_at_q(test_scores, y[test], ANCHOR_Q)
        passes += int(passed)
        rows.append({
            "phase": float(phase), "fold": int(fold), "chosenModel": chosen_model,
            "trainingOnlyCalibration": calibration, "outerQ": float(chosen_q),
            "heldoutBase": base, "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2), "passed": bool(passed),
            "v28Comparison": {"frozenQ": ANCHOR_Q, "heldoutCandidate": v28_held,
                               "heldoutPrecisionLift": round(float(v28_lift), 2), "passed": bool(v28_passed)},
        })
        print(f"  V38 q={chosen_q:.6f} held={held['true']}/{held['false']} lift={round(lift,2)} pass={passed}; V28 pass={v28_passed}", flush=True)
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

    print("Starting V38 exact V28 anchor with unanimous training-only tightening", flush=True)
    print("V37 showed percentile>=0.80 is not equivalent to exact q=0.20 top-fraction selection", flush=True)
    print("V38 restores exact V28 selection semantics and only tightens on unanimous training-only evidence", flush=True)
    print("Reserved 1/32 confirmation phases are not referenced", flush=True)

    schemes = []
    total_passes = total_folds = v28_total = rescues = regressions = tightened = 0
    for phase in CHALLENGE_PHASES:
        phase_passes, phase_rows = evaluate_phase(x, y, measures, float(phase))
        v28_phase = sum(int(r["v28Comparison"]["passed"]) for r in phase_rows)
        schemes.append({"phase": float(phase), "passes": phase_passes, "v28Passes": v28_phase, "folds": phase_rows})
        total_passes += phase_passes
        v28_total += v28_phase
        total_folds += len(phase_rows)
        for row in phase_rows:
            vp, bp = bool(row["passed"]), bool(row["v28Comparison"]["passed"])
            rescues += int(vp and not bp)
            regressions += int(bp and not vp)
            tightened += int(row["trainingOnlyCalibration"]["tightenedBelowAnchorQ"])

    min_phase = min(s["passes"] for s in schemes)
    exploratory_promising = total_passes > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V38")

    output = {
        "schemaVersion": 38,
        "profileType": "36.76-rhythm24-exact-v28-anchor-unanimous-training-only-tighten",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "challengeSource": "already-exposed-V28-phases",
        "challengePhases": list(CHALLENGE_PHASES),
        "reservedUntouchedPhasesConsumed": False,
        "v28FrozenQAnchor": ANCHOR_Q,
        "exactV28TopFractionSemanticsRestored": True,
        "foldsTightenedBelowV28Q": int(tightened),
        "outerHeldoutQSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v37UsedOnlyAsSelectionSemanticsDiagnosis": True,
        "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
        "challengeHeldoutLabelsUsedForEvaluationOnly": True,
        "foldsPassed": int(total_passes), "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "exploratoryPromising": bool(exploratory_promising),
        "requiresUntouchedConfirmationBeforeValidation": True,
        "validatedNewChampion": False, "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False,
        "protectedBaselinesChanged": False, "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 38, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total_passes), "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "foldsTightenedBelowV28Q": int(tightened),
        "exploratoryPromising": bool(exploratory_promising),
        "reservedUntouchedPhasesConsumed": False,
        "outerHeldoutQSearchPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 EXACT-V28 ANCHOR UNANIMOUS TRAINING TIGHTEN V38 COMPLETE")
    print("V38 folds passed:", total_passes, "/", total_folds)
    print("Minimum V38 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", total_folds)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Folds tightened below V28 q:", tightened)
    print("Exploratory promising:", exploratory_promising)
    print("Reserved untouched phases consumed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
