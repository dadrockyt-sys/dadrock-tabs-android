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
V83_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v82-old-tight-guarded-v80-summary-v83.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v83-reserved-1over128-confirmation-v84.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v83-reserved-1over128-confirmation-v84-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)

# Fresh confirmation family reserved before V83 interpretation.
# These are exactly the odd numerators over 128 and therefore do not overlap the
# previously consumed odd-offset 1/64 family used by V57.
RESERVED_PHASES = tuple(i / 128.0 for i in range(1, 128, 2))


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

    v83 = json.loads(V83_PATH.read_text(encoding="utf-8"))
    if int(v83.get("schemaVersion", -1)) != 83:
        raise RuntimeError("V83 output missing or wrong schema")
    if not bool(v83.get("requiresFreshUntouchedConfirmation")):
        raise RuntimeError("V83 did not request fresh confirmation")

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

    print("Starting V84 untouched confirmation of frozen V83 old-tight-guarded V80 architecture", flush=True)
    print("Fresh reserved 1/128 odd-numerator phase family is being consumed now for the first time", flush=True)
    print("V83 architecture is frozen; no parameter search, threshold search, or architecture change is permitted", flush=True)

    schemes = []
    total = base_total = rescues = regressions = folds_total = 0
    guarded_count = 0
    chosen_counts = {"tight": 0, "anchor": 0, "broad": 0}
    final_q_counts = {"tight": 0, "anchor": 0, "broad": 0}

    for phase in RESERVED_PHASES:
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        phase_rows = []
        phase_pass = phase_base = 0

        for fold in range(OUTER_FOLDS):
            print(f"phase={phase:.7f} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
            test = ids == fold
            train = ~test

            # Freeze the original V56/V57 training-only model-selection route on the
            # full V17 representation. Held-out labels are not used here.
            chosen_model = v5.choose_model(x_full[train], y[train], measures[train])
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])

            old_q, selector = v56.choose_q_train_only(x_full[train], y[train], measures[train], radius, lam)
            old_bucket = q_bucket(old_q)
            chosen_counts[old_bucket] += 1

            # Frozen V28 fallback/baseline: full V17 representation, same training-only
            # model choice, q=0.20.
            full_model = v2.fit_pairwise_ranker(x_full[train], y[train], measures[train], radius, lam)
            full_scores = v2.scores_for(x_full[test], full_model)
            base_pass, base_lift, base_held, base_stats = v17.pass_at_q(full_scores, y[test], ANCHOR_Q)

            # Frozen V83 guard: only folds whose original training-only selector branch
            # is tight receive V80. All others fall back exactly to V28.
            use_v80 = old_bucket == "tight"
            if use_v80:
                guarded_count += 1
                # V80 dual-dispersion q decision is computed exclusively from the
                # training-only V56 selector diagnostics.
                row_like = {"outerQ": float(old_q), "selector": selector}
                final_q, decision, dispersion = v80.selected_q(row_like)
                cos_model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
                cos_scores = v2.scores_for(x_cos[test], cos_model)
                final_pass, final_lift, final_held, final_base = v17.pass_at_q(cos_scores, y[test], final_q)
                representation = "cosine-only"
            else:
                final_q = ANCHOR_Q
                decision = "v83-fallback-v28"
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
                "guardAppliedV80": bool(use_v80),
                "finalRepresentation": representation,
                "finalQ": float(final_q),
                "finalQBucket": final_bucket,
                "v80Decision": decision,
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

            print(
                f"  old={old_bucket} guardV80={use_v80} finalQ={final_q:.3f} "
                f"decision={decision} pass={final_pass}; V28 pass={base_pass}",
                flush=True,
            )

        schemes.append({
            "phase": float(phase),
            "passes": int(phase_pass),
            "v28Passes": int(phase_base),
            "folds": phase_rows,
        })

    min_phase = min(s["passes"] for s in schemes)
    bottlenecks = [float(s["phase"]) for s in schemes if int(s["passes"]) == int(min_phase)]

    # Predeclared untouched-confirmation gate. This mirrors the conservative V57 gate:
    # the frozen challenger must beat V28 overall, achieve >=4/5 on every fresh phase,
    # and must not create more regressions than rescues.
    confirmation_success = total > base_total and min_phase >= 4 and regressions <= rescues

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V84")

    output = {
        "schemaVersion": 84,
        "profileType": "v83-frozen-old-tight-guarded-v80-reserved-1over128-confirmation",
        "reservedPhaseFamily": "odd-numerators-over-128",
        "reservedPhases": list(RESERVED_PHASES),
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "guardFrozenBeforeConfirmation": "apply-v80-only-when-original-training-only-q-bucket-is-tight-else-v28",
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
        "guardedV80Folds": int(guarded_count),
        "originalTrainingOnlyQCounts": chosen_counts,
        "finalQCounts": final_q_counts,
        "confirmationGate": {
            "requiresOverallImprovementVsV28": True,
            "minimumPhasePassesRequired": 4,
            "requiresRegressionsNoGreaterThanRescues": True,
        },
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "schemes": schemes,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 84,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "reservedPhaseFamily": "odd-numerators-over-128",
        "foldsPassed": int(total),
        "foldsTotal": int(folds_total),
        "minimumPhasePasses": int(min_phase),
        "bottleneckPhases": bottlenecks,
        "v28ComparisonPasses": int(base_total),
        "rescuesVsV28": int(rescues),
        "regressionsVsV28": int(regressions),
        "guardedV80Folds": int(guarded_count),
        "originalTrainingOnlyQCounts": chosen_counts,
        "finalQCounts": final_q_counts,
        "reservedUntouchedPhasesConsumed": True,
        "architectureFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "confirmationSuccess": bool(confirmation_success),
        "validatedNewChampion": bool(confirmation_success),
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V83 RESERVED 1/128 CONFIRMATION V84 COMPLETE")
    print("V84 folds passed:", total, "/", folds_total)
    print("Minimum V84 phase passes:", min_phase, "/ 5")
    print("Bottleneck phases:", bottlenecks)
    print("V28 comparison passes:", base_total, "/", folds_total)
    print("Rescues vs V28:", rescues)
    print("Regressions vs V28:", regressions)
    print("Guarded V80 folds:", guarded_count)
    print("Original training-only q counts:", chosen_counts)
    print("Final q counts:", final_q_counts)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
