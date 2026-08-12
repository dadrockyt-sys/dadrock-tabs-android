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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-two-of-three-soft-broaden-v42.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v28-anchor-two-of-three-soft-broaden-v42-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 4
INNER_SCHEMES = ("normal", "section", "shiftedWindow")
CHALLENGE_PHASES = v28.CONFIRM_PHASES
ANCHOR_Q = float(v28.FROZEN_Q)
BROAD_Q = 0.225
MIN_SOFT_SUPPORT = 2


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def choose_q_train_only(x_train: np.ndarray, y_train: np.ndarray, measures_train: np.ndarray, radius: int, lam: float) -> tuple[float, dict[str, Any]]:
    scheme_rows = []
    soft_support = 0
    for scheme in INNER_SCHEMES:
        ids = v38.inner_ids(measures_train, scheme)
        anchor_passes = broad_passes = 0
        anchor_lifts = []
        broad_lifts = []
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
            anchor_passes += int(ap); broad_passes += int(bp)
            anchor_lifts.append(float(al)); broad_lifts.append(float(bl))
            folds.append({"fold": int(fold), "anchorPassed": bool(ap), "broadPassed": bool(bp),
                          "anchorLift": round(float(al), 2), "broadLift": round(float(bl), 2),
                          "anchorHeld": ah, "broadHeld": bh, "base": ab})
        strict = broad_passes > anchor_passes
        tied_lift = broad_passes == anchor_passes and float(np.mean(broad_lifts)) > float(np.mean(anchor_lifts))
        supports = strict or tied_lift
        soft_support += int(supports)
        scheme_rows.append({"scheme": scheme, "anchorPasses": int(anchor_passes), "broadPasses": int(broad_passes),
                            "strictPassPreferenceForBroad": bool(strict), "equalPassesButMeanLiftHigher": bool(tied_lift),
                            "softSupportsBroad": bool(supports), "meanAnchorLift": float(np.mean(anchor_lifts)),
                            "meanBroadLift": float(np.mean(broad_lifts)), "folds": folds})
    chosen_q = BROAD_Q if soft_support >= MIN_SOFT_SUPPORT else ANCHOR_Q
    return chosen_q, {"architecture": "exact-v28-anchor-two-of-three-training-soft-support-one-step-broadening",
                      "anchorQ": ANCHOR_Q, "broadQ": BROAD_Q, "minimumSoftSupport": MIN_SOFT_SUPPORT,
                      "softSupportCount": int(soft_support), "chosenQ": float(chosen_q),
                      "broadenedAboveAnchorQ": bool(chosen_q > ANCHOR_Q), "outerHeldoutLabelsUsed": False,
                      "outerHeldoutQSearchPerformed": False, "v29DiagnosticQValuesUsed": False,
                      "v41UsedOnlyToPredeclareTwoOfThreeSoftGate": True, "schemes": scheme_rows}


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

    schemes = []
    total = v28_total = rescues = regressions = broadened = folds_total = 0
    for phase in CHALLENGE_PHASES:
        lo, hi = int(np.min(measures)), int(np.max(measures))
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        phase_rows = []; phase_pass = phase_v28 = 0
        for fold in range(OUTER_FOLDS):
            print(f"phase={phase} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold; train = ~test
            print("    heartbeat V42 frozen V17 representation/model-selection", flush=True)
            chosen_model = v5.choose_model(x[train], y[train], measures[train])
            radius = int(chosen_model["pairRadius"]); lam = float(chosen_model["lambda"])
            print("    heartbeat V42 two-of-three training-only soft-support gate", flush=True)
            q, selector = choose_q_train_only(x[train], y[train], measures[train], radius, lam)
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, held, base = v17.pass_at_q(scores, y[test], q)
            vp, vl, vh, _ = v17.pass_at_q(scores, y[test], ANCHOR_Q)
            phase_pass += int(passed); phase_v28 += int(vp); broadened += int(selector["broadenedAboveAnchorQ"])
            rescues += int(passed and not vp); regressions += int(vp and not passed)
            phase_rows.append({"phase": float(phase), "fold": int(fold), "chosenModel": chosen_model,
                               "trainingOnlySelector": selector, "outerQ": float(q), "heldoutBase": base,
                               "heldoutCandidate": held, "heldoutPrecisionLift": round(float(lift), 2), "passed": bool(passed),
                               "v28Comparison": {"frozenQ": ANCHOR_Q, "heldoutCandidate": vh,
                                                   "heldoutPrecisionLift": round(float(vl), 2), "passed": bool(vp)}})
            print(f"  V42 q={q:.3f} softSupport={selector['softSupportCount']}/3 held={held['true']}/{held['false']} lift={round(lift,2)} pass={passed}; V28 pass={vp}", flush=True)
        schemes.append({"phase": float(phase), "passes": phase_pass, "v28Passes": phase_v28, "folds": phase_rows})
        total += phase_pass; v28_total += phase_v28; folds_total += len(phase_rows)

    min_phase = min(s["passes"] for s in schemes)
    promising = total > v28_total and min_phase >= 4 and regressions <= rescues
    after = sha256(candidate_path)
    if before != after: raise RuntimeError("Protected candidate changed during V42")
    output = {"schemaVersion": 42, "profileType": "36.76-rhythm24-v28-anchor-two-of-three-soft-broaden",
              "baselinePitchF1": EXPECTED_F1, "baselineMatchedMissingExtra": list(EXPECTED),
              "challengeSource": "already-exposed-V28-phases", "challengePhases": list(CHALLENGE_PHASES),
              "reservedUntouchedPhasesConsumed": False, "anchorQ": ANCHOR_Q, "broadQ": BROAD_Q,
              "minimumSoftSupport": MIN_SOFT_SUPPORT, "foldsBroadenedAboveV28Q": int(broadened),
              "foldsPassed": int(total), "foldsTotal": int(folds_total), "minimumPhasePasses": int(min_phase),
              "v28ComparisonPasses": int(v28_total), "rescuesVsV28": int(rescues), "regressionsVsV28": int(regressions),
              "exploratoryPromising": bool(promising), "outerHeldoutLabelsUsedToChooseCalibrationParameters": False,
              "challengeHeldoutLabelsUsedForEvaluationOnly": True, "requiresUntouchedConfirmationBeforeValidation": True,
              "validatedNewChampion": False, "schemes": schemes, "protected949CandidateHashUnchanged": before == after,
              "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False,
              "protectedBaselinesChanged": False, "productionSeparatorChanged": False, "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({"schemaVersion": 42, "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "foldsPassed": total, "foldsTotal": folds_total, "minimumPhasePasses": min_phase,
        "v28ComparisonPasses": v28_total, "rescuesVsV28": rescues, "regressionsVsV28": regressions,
        "foldsBroadenedAboveV28Q": broadened, "exploratoryPromising": promising,
        "reservedUntouchedPhasesConsumed": False, "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after, "productionPromotionAllowed": False}, indent=2) + "\n", encoding="utf-8")
    print("GOMYWAY 36.76 RHYTHM24 V28-ANCHOR TWO-OF-THREE SOFT BROADEN V42 COMPLETE")
    print("V42 folds passed:", total, "/", folds_total)
    print("Minimum V42 phase passes:", min_phase, "/ 5")
    print("V28 comparison passes:", v28_total, "/", folds_total)
    print("Rescues vs V28:", rescues); print("Regressions vs V28:", regressions)
    print("Folds broadened above V28 q:", broadened); print("Exploratory promising:", promising)
    print("Reserved untouched phases consumed: False"); print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False"); print("Output:", OUTPUT_PATH.relative_to(ROOT)); print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

if __name__ == "__main__": main()
