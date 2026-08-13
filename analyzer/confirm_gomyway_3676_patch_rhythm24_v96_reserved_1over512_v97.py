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
V96_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v95-safe-broad-r8-l1-guard-v96.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v96-reserved-1over512-confirmation-v97.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v96-reserved-1over512-confirmation-v97-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)

# Fresh deterministic family reserved only after V96 was frozen on already-exposed
# V56/V57 data. Odd numerators over 512 are disjoint from all previously consumed
# 1/256, 1/128, 1/64, 1/32, and coarser phase families.
RESERVED_PHASES = tuple(i / 512.0 for i in range(1, 512, 2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(q: float) -> str:
    if abs(float(q) - float(v56.TIGHT_Q)) < 1e-12:
        return "tight"
    if abs(float(q) - float(v56.BROAD_Q)) < 1e-12:
        return "broad"
    return "anchor"


def is_excluded_safe_broad_signature(use_safe_broad: bool, radius: int, lam: float) -> bool:
    return bool(use_safe_broad and radius == 8 and abs(float(lam) - 1.0) < 1e-12)


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v96 = json.loads(V96_PATH.read_text(encoding="utf-8"))
    if int(v96.get("schemaVersion", -1)) != 96:
        raise RuntimeError("V96 output missing or wrong schema")
    combined = v96.get("combined") or {}
    if int(combined.get("v96Passes", -1)) != 247:
        raise RuntimeError("Frozen V96 exposed result does not match expected 247/280")
    if int(combined.get("v96RegressionsVsV28", -1)) != 0:
        raise RuntimeError("Frozen V96 exposed result is not zero-regression")
    if int(combined.get("v96GainsVsV90", -1)) != 0 or int(combined.get("v96LossesVsV90", -1)) != 0:
        raise RuntimeError("Frozen V96 is not behaviorally identical to V90 on exposed data")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([
        [float((r.get("features") or {}).get(f, 0.0)) for f in names]
        for r in rows
    ], dtype=np.float64)
    pf = v17.phase_features(rows)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V97 untouched confirmation of frozen V96 architecture", flush=True)
    print("Fresh reserved 1/512 odd-numerator phase family is being consumed now for the first time", flush=True)
    print("V96 architecture is frozen; no parameter, threshold, guard, or architecture search is permitted", flush=True)

    schemes = []
    total = base_total = rescues = regressions = folds_total = 0
    tight_guarded = safe_broad_guarded = excluded_safe_broad_r8_l1 = 0
    original_q_counts = {"tight": 0, "anchor": 0, "broad": 0}
    final_q_counts = {"tight": 0, "anchor": 0, "broad": 0}

    for phase in RESERVED_PHASES:
        ids = np.asarray([
            v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase))
            for m in measures
        ], dtype=np.int16)
        phase_rows = []
        phase_pass = phase_base = 0

        for fold in range(OUTER_FOLDS):
            print(f"phase={phase:.7f} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test

            chosen_model = v5.choose_model(x_full[train], y[train], measures[train])
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])

            old_q, selector = v56.choose_q_train_only(
                x_full[train], y[train], measures[train], radius, lam
            )
            old_bucket = q_bucket(old_q)
            original_q_counts[old_bucket] += 1

            full_model = v2.fit_pairwise_ranker(
                x_full[train], y[train], measures[train], radius, lam
            )
            full_scores = v2.scores_for(x_full[test], full_model)
            base_pass, base_lift, base_held, base_stats = v17.pass_at_q(
                full_scores, y[test], ANCHOR_Q
            )

            row_like = {"outerQ": float(old_q), "selector": selector}
            candidate_q, decision, dispersion = v80.selected_q(row_like)
            use_tight = old_bucket == "tight"
            use_safe_broad = (
                old_bucket == "broad" and decision == "keep-broad-low-dispersion"
            )
            excluded = is_excluded_safe_broad_signature(use_safe_broad, radius, lam)
            use_v96 = use_tight or (use_safe_broad and not excluded)

            if excluded:
                excluded_safe_broad_r8_l1 += 1

            if use_v96:
                if use_tight:
                    tight_guarded += 1
                if use_safe_broad:
                    safe_broad_guarded += 1
                final_q = candidate_q
                cos_model = v2.fit_pairwise_ranker(
                    x_cos[train], y[train], measures[train], radius, lam
                )
                cos_scores = v2.scores_for(x_cos[test], cos_model)
                final_pass, final_lift, final_held, final_base = v17.pass_at_q(
                    cos_scores, y[test], final_q
                )
                representation = "cosine-only"
                final_decision = decision
            else:
                final_q = ANCHOR_Q
                if excluded:
                    final_decision = "v96-exclude-safe-broad-r8-lambda1-fallback-v28"
                else:
                    final_decision = "v96-fallback-v28"
                dispersion = None
                final_pass, final_lift, final_held, final_base = (
                    base_pass, base_lift, base_held, base_stats
                )
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
                "guardAppliedV96": bool(use_v96),
                "tightGuard": bool(use_tight),
                "safeBroadGuardBeforeExclusion": bool(use_safe_broad),
                "excludedSafeBroadR8Lambda1": bool(excluded),
                "finalRepresentation": representation,
                "finalQ": float(final_q),
                "finalQBucket": final_bucket,
                "v96Decision": final_decision,
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
    bottlenecks = [
        float(s["phase"]) for s in schemes
        if int(s["passes"]) == int(min_phase)
    ]

    # Same conservative confirmation gate used by V84 and V93.
    confirmation_success = (
        total > base_total and min_phase >= 4 and regressions <= rescues
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V97")

    output = {
        "schemaVersion": 97,
        "profileType": "v96-frozen-safe-broad-r8-lambda1-exclusion-reserved-1over512-confirmation",
        "reservedPhaseFamily": "odd-numerators-over-512",
        "reservedPhases": list(RESERVED_PHASES),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "guardFrozenBeforeConfirmation": (
            "V90 tight plus safe-broad architecture, except safe-broad chosen-model "
            "pairRadius=8 and lambda=1.0 falls back to frozen V28"
        ),
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
        "safeBroadGuardedFoldsAfterExclusion": int(safe_broad_guarded),
        "excludedSafeBroadR8Lambda1Folds": int(excluded_safe_broad_r8_l1),
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
        "v93OpenedConfirmationReferencedForOutcomeSelection": False,
        "v93UsedOnlyToMotivateSignatureThenSupportRequiredOnOlderExposedV56V57": True,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 97,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "reservedPhaseFamily": "odd-numerators-over-512",
        "foldsPassed": int(total),
        "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase),
        "bottleneckPhases": bottlenecks,
        "v28ComparisonPasses": int(base_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "tightGuardedFolds": int(tight_guarded),
        "safeBroadGuardedFoldsAfterExclusion": int(safe_broad_guarded),
        "excludedSafeBroadR8Lambda1Folds": int(excluded_safe_broad_r8_l1),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V96 RESERVED 1/512 CONFIRMATION V97 COMPLETE")
    print("V97 folds passed:", total, "/", folds_total)
    print("Minimum V97 phase passes:", min_phase, "/ 5")
    print("Bottleneck phases:", bottlenecks)
    print("V28 comparison passes:", base_total, "/", folds_total)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Tight-guarded folds:", tight_guarded)
    print("Safe-broad-guarded folds after exclusion:", safe_broad_guarded)
    print("Excluded safe-broad r8 lambda1 folds:", excluded_safe_broad_r8_l1)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
