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
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
V118_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v117-dangerous-signature-exclusion-counterfactual-v118.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
GATE_NUM = 2
GATE_DEN = 7
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]

# Pre-reserved before V117 interpretation in WORKFLOW_RECOVERY_CHECKPOINT.md.
# 64 odd numerators, all 3 mod 16 over 1024. This is disjoint from V116's
# 1-mod-16 family and was not inspected during V117/V118 development.
RESERVED_PHASES = tuple((3 + 16 * k) / 1024.0 for k in range(64))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(q: float) -> str:
    if abs(float(q) - float(v56.TIGHT_Q)) < 1e-12:
        return "tight"
    if abs(float(q) - float(v56.BROAD_Q)) < 1e-12:
        return "broad"
    return "anchor"


def is_dangerous_signature(old_bucket: str, decision: str, radius: int, lam: float) -> bool:
    return bool(
        old_bucket == "tight"
        and decision == "revert-tight-to-anchor-low-dispersion"
        and int(radius) == 8
        and abs(float(lam) - 1.0) < 1e-12
    )


def gate_features_for_mask(
    xb: np.ndarray,
    names: list[str],
    pf: np.ndarray,
    train: np.ndarray,
) -> list[float]:
    idx = {n: i for i, n in enumerate(names)}
    missing = [n for n in LOWBAND if n not in idx]
    if missing:
        raise RuntimeError(f"Missing V119 gate features: {missing}")
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
    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))
    v118 = json.loads(V118_PATH.read_text(encoding="utf-8"))

    if int(v115.get("schemaVersion", -1)) != 115:
        raise RuntimeError("Frozen V115 output missing or wrong schema")
    s115 = v115.get("summary") or {}
    if int(s115.get("v115Passes", -1)) != 251 or str(s115.get("gateFraction")) != "2/7":
        raise RuntimeError("Frozen V115 policy does not match expected 251/280 top-2/7 challenger")
    if int(v116.get("schemaVersion", -1)) != 116 or not bool(v116.get("validatedNewChampion")):
        raise RuntimeError("V116 validated V115 confirmation is required")
    if int(v116.get("v115Passes", -1)) != 288 or int(v116.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V116 confirmation does not match frozen 288/320 champion result")
    if int(v118.get("schemaVersion", -1)) != 118:
        raise RuntimeError("V118 counterfactual output missing or wrong schema")
    sig = v118.get("dangerousSignature") or {}
    expected_sig = {
        "originalQBucket": "tight",
        "v96Decision": "revert-tight-to-anchor-low-dispersion",
        "pairRadius": 8,
        "lambda": 1.0,
    }
    if sig != expected_sig:
        raise RuntimeError(f"Frozen V118 dangerous signature mismatch: {sig}")
    c118 = v118.get("consumedConfirmationCounterfactual") or {}
    if int(c118.get("v118CounterfactualPasses", -1)) != 290:
        raise RuntimeError("V118 counterfactual must match 290/320 on consumed V116")

    prior_phases = {round(float(p), 12) for p in (v116.get("reservedPhases") or [])}
    new_phases = {round(float(p), 12) for p in RESERVED_PHASES}
    overlap = sorted(prior_phases & new_phases)
    if overlap:
        raise RuntimeError(f"V119 reserve overlaps V116 reserve: {overlap[:3]}")

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

    gate_fit = fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)

    # Freeze selection before any V119 held-out evaluation.
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

    print("Starting V119 untouched confirmation of frozen V118 exclusion policy", flush=True)
    print("Fresh reserve: numerators 3 mod 16 over 1024 = 64 phases / 320 folds", flush=True)
    print("V115 gate and 2/7 fraction frozen; V118 dangerous-signature exclusion frozen", flush=True)
    print(f"V112 selected before held-out evaluation: {select_k}/{len(fold_specs)}", flush=True)

    total_v28 = total_v96 = total_v115 = total_v118 = 0
    gains118_vs_v115 = losses118_vs_v115 = 0
    gains118_vs_v96 = losses118_vs_v96 = 0
    rescues118_vs_v28 = regressions118_vs_v28 = 0
    excluded_selected = 0
    excluded_v115_gains = 0
    excluded_v115_losses = 0

    schemes_map: dict[float, dict] = {
        float(p): {
            "phase": float(p),
            "v28Passes": 0,
            "v96Passes": 0,
            "v115Passes": 0,
            "v118Passes": 0,
            "folds": [],
        }
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
        excluded_safe_broad = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
        use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

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
                v115_representation = "cosine-plus-lowband-phase-interactions"
            else:
                v115_pass, v115_lift, v115_held, v115_stats = (
                    v96_pass, v96_lift, v96_held, v96_stats
                )
                v115_representation = "cosine-only"
        else:
            v96_pass, v96_lift, v96_held, v96_stats = (
                v28_pass, v28_lift, v28_held, v28_stats
            )
            v115_pass, v115_lift, v115_held, v115_stats = (
                v28_pass, v28_lift, v28_held, v28_stats
            )
            v115_representation = "full-v17-fallback"

        dangerous = is_dangerous_signature(old_bucket, decision, radius, lam)
        exclusion_applied = bool(spec["selectedForV112"] and dangerous and use_v96)
        if exclusion_applied:
            v118_pass, v118_lift, v118_held, v118_stats = (
                v96_pass, v96_lift, v96_held, v96_stats
            )
            v118_representation = "v96-dangerous-signature-exclusion"
            excluded_selected += 1
            excluded_v115_gains += int(v115_pass and not v96_pass)
            excluded_v115_losses += int(v96_pass and not v115_pass)
        else:
            v118_pass, v118_lift, v118_held, v118_stats = (
                v115_pass, v115_lift, v115_held, v115_stats
            )
            v118_representation = v115_representation

        total_v28 += int(v28_pass)
        total_v96 += int(v96_pass)
        total_v115 += int(v115_pass)
        total_v118 += int(v118_pass)
        gains118_vs_v115 += int(v118_pass and not v115_pass)
        losses118_vs_v115 += int(v115_pass and not v118_pass)
        gains118_vs_v96 += int(v118_pass and not v96_pass)
        losses118_vs_v96 += int(v96_pass and not v118_pass)
        rescues118_vs_v28 += int(v118_pass and not v28_pass)
        regressions118_vs_v28 += int(v28_pass and not v118_pass)

        scheme = schemes_map[phase]
        scheme["v28Passes"] += int(v28_pass)
        scheme["v96Passes"] += int(v96_pass)
        scheme["v115Passes"] += int(v115_pass)
        scheme["v118Passes"] += int(v118_pass)
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
            "excludedSafeBroadR8Lambda1": excluded_safe_broad,
            "dangerousSignature": dangerous,
            "v118ExclusionApplied": exclusion_applied,
            "v28Passed": bool(v28_pass),
            "v96Passed": bool(v96_pass),
            "v115Passed": bool(v115_pass),
            "v118Passed": bool(v118_pass),
            "v118GainVsV115": bool(v118_pass and not v115_pass),
            "v118LossVsV115": bool(v115_pass and not v118_pass),
            "v118GainVsV96": bool(v118_pass and not v96_pass),
            "v118LossVsV96": bool(v96_pass and not v118_pass),
            "v115Representation": v115_representation,
            "v118Representation": v118_representation,
            "heldoutPrecisionLift": round(float(v118_lift), 2),
            "heldoutCandidate": v118_held,
        })

    schemes = [schemes_map[float(p)] for p in RESERVED_PHASES]
    min_phase_v118 = min(int(s["v118Passes"]) for s in schemes)
    min_phase_v115 = min(int(s["v115Passes"]) for s in schemes)
    bottlenecks_v118 = [float(s["phase"]) for s in schemes if int(s["v118Passes"]) == min_phase_v118]

    # Predeclared new-champion gate: V118 must improve over the already validated
    # V115 champion on this untouched family, gains over V115 must exceed losses,
    # and every phase slice must retain at least 3/5 passes.
    confirmation_success = bool(
        total_v118 > total_v115
        and gains118_vs_v115 > losses118_vs_v115
        and min_phase_v118 >= 3
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V119")

    output = {
        "schemaVersion": 119,
        "profileType": "frozen-v118-dangerous-signature-exclusion-fresh-confirmation",
        "reservedPhaseFamily": "numerators-3-mod-16-over-1024",
        "reservedPhases": list(RESERVED_PHASES),
        "foldsTotal": len(fold_specs),
        "gateFractionFrozen": "2/7",
        "dangerousSignatureFrozen": expected_sig,
        "selectedForV112BeforeHeldoutEvaluation": int(select_k),
        "gateFitUsesOnlyPreviouslyExposedV56V57": True,
        "v118PolicyFrozenBeforeConfirmation": True,
        "dangerousSignatureChosenFromConsumedV116": True,
        "parameterSearchPerformed": False,
        "thresholdSearchPerformed": False,
        "heldoutLabelsUsedToChooseGateOrFractionOnV119": False,
        "v28Passes": int(total_v28),
        "v96Passes": int(total_v96),
        "v115Passes": int(total_v115),
        "v118Passes": int(total_v118),
        "v28ScorePercent": round(100.0 * total_v28 / len(fold_specs), 4),
        "v96ScorePercent": round(100.0 * total_v96 / len(fold_specs), 4),
        "v115ScorePercent": round(100.0 * total_v115 / len(fold_specs), 4),
        "v118ScorePercent": round(100.0 * total_v118 / len(fold_specs), 4),
        "v118GainsVsV115": int(gains118_vs_v115),
        "v118LossesVsV115": int(losses118_vs_v115),
        "v118NetVsV115": int(gains118_vs_v115 - losses118_vs_v115),
        "v118GainsVsV96": int(gains118_vs_v96),
        "v118LossesVsV96": int(losses118_vs_v96),
        "v118NetVsV96": int(gains118_vs_v96 - losses118_vs_v96),
        "v118RescuesVsV28": int(rescues118_vs_v28),
        "v118RegressionsVsV28": int(regressions118_vs_v28),
        "excludedSelectedRows": int(excluded_selected),
        "excludedV115Gains": int(excluded_v115_gains),
        "excludedV115Losses": int(excluded_v115_losses),
        "minimumV118PhasePasses": int(min_phase_v118),
        "minimumV115PhasePasses": int(min_phase_v115),
        "v118BottleneckPhases": bottlenecks_v118,
        "derivedInteractionFeatures": interaction_names,
        "confirmationGate": {
            "requiresOverallImprovementVsValidatedV115": True,
            "requiresGainsGreaterThanLossesVsV115": True,
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
    MANIFEST_PATH.write_text(
        json.dumps({k: v for k, v in output.items() if k != "schemes"}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("GOMYWAY V119 FROZEN V118 FRESH CONFIRMATION COMPLETE")
    print(f"V28:  {total_v28}/{len(fold_specs)} = {100.0*total_v28/len(fold_specs):.4f}%")
    print(f"V96:  {total_v96}/{len(fold_specs)} = {100.0*total_v96/len(fold_specs):.4f}%")
    print(f"V115: {total_v115}/{len(fold_specs)} = {100.0*total_v115/len(fold_specs):.4f}%")
    print(f"V118: {total_v118}/{len(fold_specs)} = {100.0*total_v118/len(fold_specs):.4f}%")
    print(f"Selected for V112 before held-out evaluation: {select_k}/{len(fold_specs)}")
    print(f"Dangerous-signature exclusions applied: {excluded_selected}")
    print(f"Excluded V115 gains/losses: +{excluded_v115_gains}/-{excluded_v115_losses}")
    print(f"V118 gains/losses vs V115: +{gains118_vs_v115}/-{losses118_vs_v115} net={gains118_vs_v115-losses118_vs_v115:+d}")
    print(f"V118 gains/losses vs V96: +{gains118_vs_v96}/-{losses118_vs_v96} net={gains118_vs_v96-losses118_vs_v96:+d}")
    print(f"V118 rescues/regressions vs V28: +{rescues118_vs_v28}/-{regressions118_vs_v28}")
    print(f"Minimum V118 phase passes: {min_phase_v118}/5")
    print("V118 bottleneck phases:", bottlenecks_v118)
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
