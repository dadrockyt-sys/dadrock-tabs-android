from __future__ import annotations

import hashlib
import json
import math
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
import profile_gomyway_3676_patch_rhythm24_v109_lowband_cross_source_residual_predictability_v110 as v110
import profile_gomyway_3676_patch_rhythm24_v111_lowband_phase_interaction_augmentation_v112 as v112

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V112_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v111-lowband-phase-interaction-augmentation-v112.json"
V115_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v114-selective-v112-top2over7-challenger-v115.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
GATE_NUM = 2
GATE_DEN = 7
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
PHASE_LABELS = ["p2sin", "p2cos", "p4sin", "p4cos"]

# Compact fresh family: 64 evenly spread odd numerators over 1024, all congruent to
# 1 mod 16.  Because every numerator is odd, none reduces to any previously used
# /512-or-coarser dyadic phase.  64 phases x 5 folds = 320 confirmation folds.
RESERVED_PHASES = tuple((1 + 16 * k) / 1024.0 for k in range(64))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(q: float) -> str:
    if abs(float(q) - float(v56.TIGHT_Q)) < 1e-12:
        return "tight"
    if abs(float(q) - float(v56.BROAD_Q)) < 1e-12:
        return "broad"
    return "anchor"


def gate_features_for_mask(
    xb: np.ndarray,
    names: list[str],
    pf: np.ndarray,
    train: np.ndarray,
) -> list[float]:
    idx = {n: i for i, n in enumerate(names)}
    missing = [n for n in LOWBAND if n not in idx]
    if missing:
        raise RuntimeError(f"Missing V116 gate features: {missing}")
    vals: list[float] = []
    for n in LOWBAND:
        col = xb[train, idx[n]]
        vals.extend([float(np.mean(col)), float(np.std(col))])
    for n in LOWBAND:
        low = xb[train, idx[n]]
        for j in range(4):
            prod = low * pf[train, j]
            vals.extend([float(np.mean(prod)), float(np.std(prod))])
    return vals


def fit_frozen_gate_from_exposed(
    xb: np.ndarray,
    names: list[str],
    pf: np.ndarray,
    measures: np.ndarray,
    lo: int,
    hi: int,
):
    exposed = json.loads(V112_PATH.read_text(encoding="utf-8"))
    rows = list(exposed.get("rowsDetail") or [])
    if len(rows) != 280:
        raise RuntimeError(f"Expected frozen V112 280-row development set, got {len(rows)}")
    x_rows = []
    y_rows = []
    for r in rows:
        phase = float(r["phase"])
        fold = int(r["fold"])
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        train = ids != fold
        x_rows.append(gate_features_for_mask(xb, names, pf, train))
        y_rows.append(bool(r.get("gainVsV96")))
    return v110.fit_ridge_logistic(
        np.asarray(x_rows, dtype=np.float64),
        np.asarray(y_rows, dtype=bool),
        lam=8.0,
        steps=100,
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v115 = json.loads(V115_PATH.read_text(encoding="utf-8"))
    if int(v115.get("schemaVersion", -1)) != 115:
        raise RuntimeError("V115 output missing or wrong schema")
    v115_summary = v115.get("summary") or {}
    if int(v115_summary.get("v115Passes", -1)) != 251:
        raise RuntimeError("Frozen V115 development result does not match 251/280")
    if int(v115_summary.get("gainsVsV96", -1)) != 6 or int(v115_summary.get("lossesVsV96", -1)) != 2:
        raise RuntimeError("Frozen V115 development utility does not match +6/-2")
    if str(v115_summary.get("gateFraction")) != "2/7":
        raise RuntimeError("Frozen V115 gate fraction is not 2/7")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
    pf = np.asarray(v17.phase_features(rows), dtype=np.float64)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    interactions, interaction_names = v112.build_phase_interactions(xb, names, pf)
    x_v112 = np.concatenate([x_cos, interactions], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    # Gate is frozen from the complete previously exposed V112 development set.
    # No reserved-family outcome is used to fit it or choose the 2/7 fraction.
    gate_fit = fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)

    # Precompute every fresh fold's gate score using training-side context only,
    # then freeze the top-2/7 selection before any held-out pass result is evaluated.
    fold_specs = []
    for phase in RESERVED_PHASES:
        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures],
            dtype=np.int16,
        )
        for fold in range(OUTER_FOLDS):
            train = ids != fold
            gx = np.asarray([gate_features_for_mask(xb, names, pf, train)], dtype=np.float64)
            gate_score = float(v110.predict(gx, gate_fit)[0])
            fold_specs.append({
                "phase": float(phase),
                "fold": int(fold),
                "ids": ids,
                "gateScore": gate_score,
            })

    select_k = int(math.ceil(len(fold_specs) * GATE_NUM / GATE_DEN))
    order = np.argsort(-np.asarray([r["gateScore"] for r in fold_specs], dtype=np.float64))
    selected_indices = set(int(i) for i in order[:select_k])
    for i, spec in enumerate(fold_specs):
        spec["selectedForV112"] = i in selected_indices

    print("Starting V116 compact untouched confirmation of frozen V115 policy", flush=True)
    print("Fresh reserved 1/1024 stride-16 odd-numerator family: 64 phases / 320 folds", flush=True)
    print("Gate model, 2/7 fraction, V96 backbone, and V112 interaction family are frozen", flush=True)
    print(f"V112 selected before held-out evaluation: {select_k}/{len(fold_specs)}", flush=True)

    total_v115 = total_v96 = total_v28 = 0
    gains_vs_v96 = losses_vs_v96 = 0
    rescues_vs_v28 = regressions_vs_v28 = 0
    schemes_map: dict[float, dict] = {
        float(p): {"phase": float(p), "v115Passes": 0, "v96Passes": 0, "v28Passes": 0, "folds": []}
        for p in RESERVED_PHASES
    }

    for spec in fold_specs:
        phase = float(spec["phase"])
        fold = int(spec["fold"])
        ids = spec["ids"]
        test = ids == fold
        train = ~test

        print(f"phase={phase:.7f} outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)

        chosen_model = v5.choose_model(x_full[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])

        old_q, selector = v56.choose_q_train_only(
            x_full[train], y[train], measures[train], radius, lam
        )
        old_bucket = q_bucket(old_q)

        full_model = v2.fit_pairwise_ranker(x_full[train], y[train], measures[train], radius, lam)
        full_scores = v2.scores_for(x_full[test], full_model)
        v28_pass, v28_lift, v28_held, v28_stats = v17.pass_at_q(full_scores, y[test], ANCHOR_Q)

        row_like = {"outerQ": float(old_q), "selector": selector}
        candidate_q, decision, dispersion = v80.selected_q(row_like)
        use_tight = old_bucket == "tight"
        use_safe_broad = old_bucket == "broad" and decision == "keep-broad-low-dispersion"
        excluded = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
        use_v96 = use_tight or (use_safe_broad and not excluded)

        if use_v96:
            cos_model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
            cos_scores = v2.scores_for(x_cos[test], cos_model)
            v96_pass, v96_lift, v96_held, v96_stats = v17.pass_at_q(
                cos_scores, y[test], candidate_q
            )

            if bool(spec["selectedForV112"]):
                aug_model = v2.fit_pairwise_ranker(x_v112[train], y[train], measures[train], radius, lam)
                aug_scores = v2.scores_for(x_v112[test], aug_model)
                v115_pass, v115_lift, v115_held, v115_stats = v17.pass_at_q(
                    aug_scores, y[test], candidate_q
                )
                final_representation = "cosine-plus-lowband-phase-interactions"
            else:
                v115_pass, v115_lift, v115_held, v115_stats = (
                    v96_pass, v96_lift, v96_held, v96_stats
                )
                final_representation = "cosine-only"
        else:
            v96_pass, v96_lift, v96_held, v96_stats = (
                v28_pass, v28_lift, v28_held, v28_stats
            )
            v115_pass, v115_lift, v115_held, v115_stats = (
                v28_pass, v28_lift, v28_held, v28_stats
            )
            final_representation = "full-v17-fallback"

        total_v28 += int(v28_pass)
        total_v96 += int(v96_pass)
        total_v115 += int(v115_pass)
        gains_vs_v96 += int(v115_pass and not v96_pass)
        losses_vs_v96 += int(v96_pass and not v115_pass)
        rescues_vs_v28 += int(v115_pass and not v28_pass)
        regressions_vs_v28 += int(v28_pass and not v115_pass)

        scheme = schemes_map[phase]
        scheme["v28Passes"] += int(v28_pass)
        scheme["v96Passes"] += int(v96_pass)
        scheme["v115Passes"] += int(v115_pass)
        scheme["folds"].append({
            "phase": phase,
            "fold": fold,
            "gateScore": float(spec["gateScore"]),
            "selectedForV112": bool(spec["selectedForV112"]),
            "chosenModel": chosen_model,
            "originalTrainingOnlyQ": float(old_q),
            "originalQBucket": old_bucket,
            "selector": selector,
            "v96Decision": decision,
            "dispersion": None if dispersion is None else float(dispersion),
            "excludedSafeBroadR8Lambda1": excluded,
            "v28Passed": bool(v28_pass),
            "v96Passed": bool(v96_pass),
            "v115Passed": bool(v115_pass),
            "gainVsV96": bool(v115_pass and not v96_pass),
            "lossVsV96": bool(v96_pass and not v115_pass),
            "finalRepresentation": final_representation,
            "heldoutPrecisionLift": round(float(v115_lift), 2),
            "heldoutCandidate": v115_held,
        })

    schemes = [schemes_map[float(p)] for p in RESERVED_PHASES]
    min_phase_v115 = min(int(s["v115Passes"]) for s in schemes)
    min_phase_v96 = min(int(s["v96Passes"]) for s in schemes)
    bottlenecks_v115 = [float(s["phase"]) for s in schemes if int(s["v115Passes"]) == min_phase_v115]

    # Predeclared conservative confirmation gate.  V115 must improve on its own
    # V96 backbone on fresh folds, must not have more losses than gains vs V96,
    # and must keep at least 3/5 folds in every phase slice.
    confirmation_success = bool(
        total_v115 > total_v96
        and gains_vs_v96 > losses_vs_v96
        and min_phase_v115 >= 3
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V116")

    output = {
        "schemaVersion": 116,
        "profileType": "frozen-v115-selective-v112-compact-reserved-1over1024-stride16-confirmation",
        "reservedPhaseFamily": "numerators-1-mod-16-over-1024",
        "reservedPhases": list(RESERVED_PHASES),
        "foldsTotal": len(fold_specs),
        "gateFractionFrozen": "2/7",
        "selectedForV112BeforeHeldoutEvaluation": int(select_k),
        "gateFitUsesOnlyPreviouslyExposedV56V57": True,
        "gateFitLabel": "V112 gain over V96 on exposed development folds",
        "v115PolicyFrozenBeforeConfirmation": True,
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "heldoutLabelsUsedToChooseGateOrFraction": False,
        "v28Passes": int(total_v28),
        "v96Passes": int(total_v96),
        "v115Passes": int(total_v115),
        "v28ScorePercent": round(100.0 * total_v28 / len(fold_specs), 4),
        "v96ScorePercent": round(100.0 * total_v96 / len(fold_specs), 4),
        "v115ScorePercent": round(100.0 * total_v115 / len(fold_specs), 4),
        "gainsVsV96": int(gains_vs_v96),
        "lossesVsV96": int(losses_vs_v96),
        "netVsV96": int(gains_vs_v96 - losses_vs_v96),
        "rescuesVsV28": int(rescues_vs_v28),
        "regressionsVsV28": int(regressions_vs_v28),
        "minimumV115PhasePasses": int(min_phase_v115),
        "minimumV96PhasePasses": int(min_phase_v96),
        "v115BottleneckPhases": bottlenecks_v115,
        "derivedInteractionFeatures": interaction_names,
        "confirmationGate": {
            "requiresOverallImprovementVsV96": True,
            "requiresGainsGreaterThanLossesVsV96": True,
            "minimumPhasePassesRequired": 3,
        },
        "confirmationSuccess": confirmation_success,
        "validatedNewChampion": confirmation_success,
        "reservedUntouchedPhasesConsumed": True,
        "schemes": schemes,
        "v97OpenedConfirmationUsedForOutcomeSelection": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in output.items() if k != "schemes"}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY V116 FROZEN V115 COMPACT RESERVED 1/1024 CONFIRMATION COMPLETE")
    print(f"V28:  {total_v28}/{len(fold_specs)} = {100.0*total_v28/len(fold_specs):.4f}%")
    print(f"V96:  {total_v96}/{len(fold_specs)} = {100.0*total_v96/len(fold_specs):.4f}%")
    print(f"V115: {total_v115}/{len(fold_specs)} = {100.0*total_v115/len(fold_specs):.4f}%")
    print(f"Selected for V112 before held-out evaluation: {select_k}/{len(fold_specs)}")
    print(f"Gains vs V96: {gains_vs_v96}")
    print(f"Losses vs V96: {losses_vs_v96}")
    print(f"Net vs V96: {gains_vs_v96-losses_vs_v96:+d}")
    print(f"Rescues vs V28: {rescues_vs_v28}")
    print(f"Regressions vs V28: {regressions_vs_v28}")
    print(f"Minimum V115 phase passes: {min_phase_v115}/5")
    print("V115 bottleneck phases:", bottlenecks_v115)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
