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
import benchmark_gomyway_3676_patch_rhythm24_v28_exact_anchor_unanimous_training_tighten_v38 as v38

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-trainingonly-one-step-broaden-v40.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-trainingonly-one-step-broaden-v40-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
CHALLENGE_PHASES = v28.CONFIRM_PHASES
ANCHOR_Q = float(v28.FROZEN_Q)
# Predeclared one-step broadening candidate. This is a fixed architecture constant,
# not copied from V29 or any held-out diagnostic. V39 supplied only training-only
# directional evidence that tightening was unsupported.
BROAD_Q = 0.225


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_q_train_only(x_train: np.ndarray, y_train: np.ndarray, measures_train: np.ndarray, radius: int, lam: float) -> tuple[float, dict[str, Any]]:
    scheme_rows = []
    all_schemes_prefer_broad = True
    for scheme in INNER_SCHEMES:
        ids = v38.inner_ids(measures_train, scheme)
        anchor_passes = 0
        broad_passes = 0
        folds = []
        for fold in range(INNER_FOLDS):
            val = ids == fold
            subtrain = ~val
            if not np.any(val) or not np.any(subtrain):
                continue
            model = v2.fit_pairwise_ranker(x_train[subtrain], y_train[subtrain], measures_train[subtrain], radius, lam)
            scores = v2.scores_for(x_train[val], model)
            ap, al, ah, ab = v17.pass_at_q(scores, y_train[val], ANCHOR_Q)
            bp, bl, bh, _ = v17.pass_at_q(scores, y_train[val], BROAD_Q)
            anchor_passes += int(ap)
            broad_passes += int(bp)
            folds.append({
                "fold": int(fold),
                "anchorQ": ANCHOR_Q,
                "anchorPassed": bool(ap),
                "anchorLift": round(float(al), 2),
                "anchorHeld": ah,
                "broadQ": BROAD_Q,
                "broadPassed": bool(bp),
                "broadLift": round(float(bl), 2),
                "broadHeld": bh,
                "base": ab,
            })
        prefers_broad = broad_passes > anchor_passes
        all_schemes_prefer_broad = all_schemes_prefer_broad and prefers_broad
        scheme_rows.append({
            "scheme": scheme,
            "anchorPasses": int(anchor_passes),
            "broadPasses": int(broad_passes),
            "strictlyPrefersBroad": bool(prefers_broad),
            "folds": folds,
        })

    chosen_q = BROAD_Q if all_schemes_prefer_broad else ANCHOR_Q
    return float(chosen_q), {
        "architecture": "exact-v28-anchor-with-unanimous-training-only-one-step-broadening",
        "anchorQ": ANCHOR_Q,
        "broadQ": BROAD_Q,
        "allSchemesStrictlyPreferBroad": bool(all_schemes_prefer_broad),
        "chosenQ": float(chosen_q),
        "broadenedAboveAnchorQ": bool(chosen_q > ANCHOR_Q),
        "outerHeldoutLabelsUsed": False,
        "outerHeldoutQSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v39UsedOnlyForTrainingOnlyDirection": True,
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
        print("    heartbeat V40 frozen V17 representation/model-selection", flush=True)
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        print("    heartbeat V40 exact V28 anchor plus unanimous one-step broadening", flush=True)
        chosen_q, selector = choose_q_train_only(x[train], y[train], measures[train], radius, lam)
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        test_scores = v2.scores_for(x[test], model)
        passed, lift, held, base = v17.pass_at_q(test_scores, y[test], chosen_q)
        v28_passed, v28_lift, v28_held, _ = v17.pass_at_q(test_scores, y[test], ANCHOR_Q)
        passes += int(passed)
        rows.append({
            "phase": float(phase), "fold": int(fold), "chosenModel": chosen_model,
            "trainingOnlySelector": selector, "outerQ": float(chosen_q),
            "heldoutBase": base, "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2), "passed": bool(passed),
            "v28Comparison": {"frozenQ": ANCHOR_Q, "heldoutCandidate": v28_held,
                               "heldoutPrecisionLift": round(float(v28_lift), 2), "passed": bool(v28_passed)},
        })
        print(f"  V40 q={chosen_q:.3f} held={held['true']}/{held['false']} lift={round(lift,2)} pass={passed}; V28 pass={v28_passed}", flush=True)
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

    print("Starting V40 exact V28 anchor with unanimous training-only one-step broadening", flush=True)
    print("Candidates are fixed q=0.20 anchor and predeclared q=0.225 broad step", flush=True)
    print("Outer held-out labels do not choose q; reserved 1/32 phases are not referenced", flush=True)

    schemes = []
    total_passes = total_folds = v28_total = rescues = regressions = broadened = 0
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
            broadened += int(row["trainingOnlySelector"]["broadenedAboveAnchorQ"])

    min_phase = min(s["passes"] for s in schemes)
    exploratory_promising = total_passes > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V40")

    output = {
        "schemaVersion": 40,
        "profileType": "36.76-rhythm24-exact-v28-anchor-training-only-one-step-broaden",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "frozenReferenceRepresentation": "V17-rhythm24",
        "challengeSource": "already-exposed-V28-phases",
        "challengePhases": list(CHALLENGE_PHASES),
        "reservedUntouchedPhasesConsumed": False,
        "anchorQ": ANCHOR_Q,
        "broadQ": BROAD_Q,
        "foldsBroadenedAboveV28Q": int(broadened),
        "outerHeldoutQSearchPerformed": False,
        "v29DiagnosticQValuesUsed": False,
        "v39UsedOnlyForTrainingOnlyDirection": True,
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
        "schemaVersion": 40, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": int(total_passes), "foldsTotal": int(total_folds),
        "minimumPhasePasses": int(min_phase), "v28ComparisonPasses": int(v28_total),
        "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
        "foldsBroadenedAboveV28Q": int(broadened),
        "exploratoryPromising": bool(exploratory_promising),
        "reservedUntouchedPhasesConsumed": False,
        "outerHeldoutQSearchPerformed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V28-ANCHOR TRAINING-ONLY ONE-STEP BROADEN V40 COMPLETE")
    print("V40 folds passed:", total_passes, "/", total_folds)
    print("Minimum V40 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", total_folds)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Folds broadened above V28 q:", broadened)
    print("Exploratory promising:", exploratory_promising)
    print("Reserved untouched phases consumed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
