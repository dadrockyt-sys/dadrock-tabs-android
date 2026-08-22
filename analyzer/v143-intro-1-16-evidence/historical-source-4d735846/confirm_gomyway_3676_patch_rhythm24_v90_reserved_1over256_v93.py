from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import benchmark_gomyway_3676_patch_rhythm24_v55_unanimous_tight_lift_escape_v56 as v56
import profile_gomyway_3676_patch_rhythm24_v79_cosine_dual_dispersion_combined_v80 as v80

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V90_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v89-tight-plus-safe-broad-v90.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v90-reserved-1over256-confirmation-v93.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v90-reserved-1over256-confirmation-v93-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)

# Fresh family reserved after V92 rejected fallback widening. Odd numerators over
# 256 do not overlap the previously consumed odd-numerator 1/128 family or the
# earlier odd-offset 1/64 family.
RESERVED_PHASES = tuple(i / 256.0 for i in range(1, 256, 2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(q: float) -> str:
    if abs(float(q) - float(v56.TIGHT_Q)) < 1e-12:
        return "tight"
    if abs(float(q) - float(v56.BROAD_Q)) < 1e-12:
        return "broad"
    return "anchor"


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v90 = json.loads(V90_PATH.read_text(encoding="utf-8"))
    if int(v90.get("schemaVersion", -1)) != 90:
        raise RuntimeError("V90 output missing or wrong schema")
    if int((v90.get("combined") or {}).get("v90Passes", -1)) != 247:
        raise RuntimeError("V90 frozen exposed result does not match expected 247/280")
    if int((v90.get("combined") or {}).get("v90RegressionsVsV28", -1)) != 0:
        raise RuntimeError("V90 frozen exposed result is not zero-regression")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V93 untouched confirmation of frozen V90 architecture", flush=True)
    print("Fresh reserved 1/256 odd-numerator phase family is being consumed now for the first time", flush=True)
    print("V90 architecture is frozen; no parameter, threshold, guard, or architecture search is permitted", flush=True)

    schemes = []
    total = base_total = rescues = regressions = folds_total = 0
    tight_guarded = safe_broad_guarded = 0
    original_q_counts = {"tight": 0, "anchor": 0, "broad": 0}
    final_q_counts = {"tight": 0, "anchor": 0, "broad": 0}

    for phase in RESERVED_PHASES:
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        phase_rows = []
        phase_pass = phase_base = 0

        for fold in range(OUTER_FOLDS):
            print(f"phase={phase:.7f} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test

            chosen_model = v5.choose_model(x_full[train], y[train], measures[train])
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])

            old_q, selector = v56.choose_q_train_only(x_full[train], y[train], measures[train], radius, lam)
            old_bucket = q_bucket(old_q)
            original_q_counts[old_bucket] += 1

            full_model = v2.fit_pairwise_ranker(x_full[train], y[train], measures[train], radius, lam)
            full_scores = v2.scores_for(x_full[test], full_model)
            base_pass, base_lift, base_held, base_stats = v17.pass_at_q(full_scores, y[test], ANCHOR_Q)

            row_like = {"outerQ": float(old_q), "selector": selector}
            candidate_q, decision, dispersion = v80.selected_q(row_like)
            use_tight = old_bucket == "tight"
            use_safe_broad = old_bucket == "broad" and decision == "keep-broad-low-dispersion"
            use_v90 = use_tight or use_safe_broad

            if use_v90:
                if use_tight:
                    tight_guarded += 1
                if use_safe_broad:
                    safe_broad_guarded += 1
                final_q = candidate_q
                cos_model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                cos_scores = v2.scores_for(x_cos[test], cos_model)
                final_pass, final_lift, final_held, final_base = v17.pass_at_q(cos_scores, y[test], final_q)
                representation = "cosine-only"
            else:
                final_q = ANCHOR_Q
                decision = "v90-fallback-v28"
                dispersion = None
                final_pass, final_lift, final_held, final_base = base_pass, base_lift, base_held, base_stats
                representation = "full-v17"

            final_bucket = q_bucket(final_q)
            final_q_counts[final_bucket] += 1

            phase_pass += int(final_pass)
            phase_base += int(base_pass)
            total += int(final_pass)
            base_total += int(base_pass)
            rescues += int(final_pass and not base_pass)
            regressions += int(base_pass and not final_pass)
            folds_total += 1

            phase_rows.append({
                "phase": float(phase),
                "fold": int(fold),
                "chosenModel": chosen_model,
                "originalTrainingOnlyQ": float(old_q),
                "originalQBucket": old_bucket,
                "selector": selector,
                "guardAppliedV90": bool(use_v90),
                "tightGuard": bool(use_tight),
                "safeBroadGuard": bool(use_safe_broad),
                "finalRepresentation": representation,
                "finalQ": float(final_q),
                "finalQBucket": final_bucket,
                "v90Decision": decision,
                "dispersion": None if dispersion is None else float(dispersion),
                "passed": bool(final_pass),
                "heldoutPrecisionLift": round(float(final_lift), 2),
                "heldoutCandidate": final_held,
                "heldoutBase": final_base,
                "v28Comparison": {
                    "frozenQ": ANCHOR_Q,
                    "passed": bool(base_pass),
                    "heldoutPrecisionLift": round(float(base_lift), 2),
                    "heldoutCandidate": base_held,
                },
            })

        schemes.append({
            "phase": float(phase),
            "passes": int(phase_pass),
            "v28Passes": int(phase_base),
            "folds": phase_rows,
        })

    min_phase = min(s["passes"] for s in schemes)
    bottlenecks = [float(s["phase"]) for s in schemes if int(s["passes"]) == int(min_phase)]

    # Same conservative gate used by V84. It is not altered after seeing V84.
    confirmation_success = total > base_total and min_phase >= 4 and regressions <= rescues

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V93")

    output = {
        "schemaVersion": 93,
        "profileType": "v90-frozen-tight-plus-safe-broad-reserved-1over256-confirmation",
        "reservedPhaseFamily": "odd-numerators-over-256",
        "reservedPhases": list(RESERVED_PHASES),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "guardFrozenBeforeConfirmation": "apply-cosine-challenger-on-original-tight-or-broad-with-keep-broad-low-dispersion-else-v28",
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "outerHeldoutLabelsUsedToChooseParameters": False,
        "foldsPassed": int(total),
        "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase),
        "bottleneckPhases": bottlenecks,
        "v28ComparisonPasses": int(base_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "tightGuardedFolds": int(tight_guarded),
        "safeBroadGuardedFolds": int(safe_broad_guarded),
        "originalTrainingOnlyQCounts": original_q_counts,
        "finalQCounts": final_q_counts,
        "confirmationGate": {
            "requiresOverallImprovementVsV28": True,
            "minimumPhasePassesRequired": 4,
            "requiresRegressionsNoGreaterThanRescues": True,
        },
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "schemes": schemes,
        "v84OpenedConfirmationReferencedForSelection": False,
        "v92FallbackWideningAdopted": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 93,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "reservedPhaseFamily": "odd-numerators-over-256",
        "foldsPassed": int(total),
        "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase),
        "bottleneckPhases": bottlenecks,
        "v28ComparisonPasses": int(base_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "tightGuardedFolds": int(tight_guarded),
        "safeBroadGuardedFolds": int(safe_broad_guarded),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "v84OpenedConfirmationReferencedForSelection": False,
        "v92FallbackWideningAdopted": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V90 RESERVED 1/256 CONFIRMATION V93 COMPLETE")
    print("V93 folds passed:", total, "/", folds_total)
    print("Minimum V93 phase passes:", min_phase, "/ 5")
    print("Bottleneck phases:", bottlenecks)
    print("V28 comparison passes:", base_total, "/", folds_total)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Tight-guarded folds:", tight_guarded)
    print("Safe-broad-guarded folds:", safe_broad_guarded)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
