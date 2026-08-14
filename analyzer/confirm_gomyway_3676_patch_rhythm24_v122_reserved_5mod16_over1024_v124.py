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
V119_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
V122_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v121-structural-representation-utility-v122.json"
V123_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reverse-validation-on-v116-v123.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124-manifest.json"

EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
GATE_NUM = 2
GATE_DEN = 7
LOWBAND = ["mean::lowBurst", "mean::lowRise", "mean::lowDecay30", "mean::lowPostSlope"]
REPRESENTATIONS = ("base", "phase_col3", "full_phase", "cosine", "v112_interactions")

# Pre-reserved in WORKFLOW_RECOVERY_CHECKPOINT.md before V120 interpretation.
# 64 odd numerators, all 5 mod 16 over 1024; disjoint from the consumed
# 1-mod-16 V116 and 3-mod-16 V119 families.
RESERVED_PHASES = tuple((5 + 16 * k) / 1024.0 for k in range(64))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q_bucket(q: float) -> str:
    if abs(float(q) - float(v56.TIGHT_Q)) < 1e-12:
        return "tight"
    if abs(float(q) - float(v56.BROAD_Q)) < 1e-12:
        return "broad"
    return "anchor"


def structural_key(bucket: str, decision: str, radius: int, lam: float) -> tuple[str, str, int, float]:
    return (str(bucket), str(decision), int(radius), float(lam))


def is_v118_dangerous_signature(bucket: str, decision: str, radius: int, lam: float) -> bool:
    return structural_key(bucket, decision, radius, lam) == (
        "tight", "revert-tight-to-anchor-low-dispersion", 8, 1.0
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
        raise RuntimeError(f"Missing V124 gate features: {missing}")
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
    v119 = json.loads(V119_PATH.read_text(encoding="utf-8"))
    v122 = json.loads(V122_PATH.read_text(encoding="utf-8"))
    v123 = json.loads(V123_PATH.read_text(encoding="utf-8"))

    if int(v115.get("schemaVersion", -1)) != 115:
        raise RuntimeError("Frozen V115 output missing or wrong schema")
    if int((v115.get("summary") or {}).get("v115Passes", -1)) != 251:
        raise RuntimeError("Frozen V115 development result mismatch")
    if int(v119.get("schemaVersion", -1)) != 119 or not bool(v119.get("validatedNewChampion")):
        raise RuntimeError("Validated V119/V118 champion confirmation required")
    if int(v119.get("v118Passes", -1)) != 293 or int(v119.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V119 does not match frozen 293/320 V118 champion")
    if int(v122.get("schemaVersion", -1)) != 122:
        raise RuntimeError("Frozen V122 structural policy required")
    if int(v123.get("schemaVersion", -1)) != 123:
        raise RuntimeError("V123 reverse-validation record required")
    s123 = v123.get("summary") or {}
    if int(s123.get("v122PolicyPasses", -1)) != 307 or int(s123.get("netVsV118", -999)) != 17:
        raise RuntimeError("V123 corroboration does not match expected 307/320, net +17")

    policy: dict[tuple[str, str, int, float], str] = {}
    for row in v122.get("positiveBestPerStructuralGroup") or []:
        key = (
            str(row.get("originalQBucket")),
            str(row.get("v96Decision")),
            int(row.get("pairRadius")),
            float(row.get("lambda")),
        )
        rep = str(row.get("representation"))
        if rep not in REPRESENTATIONS:
            raise RuntimeError(f"Unexpected frozen representation: {rep}")
        policy[key] = rep
    if not policy:
        raise RuntimeError("V122 positive structural policy is empty")

    prior_v119 = {round(float(p), 12) for p in (v119.get("reservedPhases") or [])}
    new_phases = {round(float(p), 12) for p in RESERVED_PHASES}
    if prior_v119 & new_phases:
        raise RuntimeError("V124 reserve overlaps consumed V119 reserve")

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
    interactions, interaction_names = v112.build_phase_interactions(xb, names, pf)
    matrices = {
        "base": xb,
        "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
        "full_phase": np.concatenate([xb, pf], axis=1),
        "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
        "v112_interactions": np.concatenate([xb, pf[:, [1, 3]], interactions], axis=1),
    }
    x_full = matrices["full_phase"]
    x_cos = matrices["cosine"]
    x_v112 = matrices["v112_interactions"]
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    gate_fit = fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)

    # Freeze V115/V118 selection on the whole untouched family before evaluating held-out results.
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
            fold_specs.append({"phase": float(phase), "fold": int(fold), "ids": ids, "gateScore": gate_score})

    select_k = int(math.ceil(len(fold_specs) * GATE_NUM / GATE_DEN))
    order = np.argsort(-np.asarray([r["gateScore"] for r in fold_specs], dtype=np.float64))
    selected_indices = set(int(i) for i in order[:select_k])
    for i, spec in enumerate(fold_specs):
        spec["selectedForV112"] = i in selected_indices

    print("Starting V124 untouched confirmation of frozen V122 structural policy", flush=True)
    print("Fresh reserve: numerators 5 mod 16 over 1024 = 64 phases / 320 folds", flush=True)
    print("V118 baseline and V122 structural switches are frozen before held-out evaluation", flush=True)
    print(f"V112 selected before held-out evaluation: {select_k}/{len(fold_specs)}", flush=True)
    print(f"Frozen positive structural groups: {len(policy)}", flush=True)

    total_v28 = total_v96 = total_v115 = total_v118 = total_v122 = 0
    gains122_vs_v118 = losses122_vs_v118 = 0
    gains122_vs_v96 = losses122_vs_v96 = 0
    rescues122_vs_v28 = regressions122_vs_v28 = 0
    v118_exclusions = 0
    policy_applied = 0
    applied_by_group: dict[str, int] = {}

    schemes_map = {
        float(p): {
            "phase": float(p),
            "v28Passes": 0,
            "v96Passes": 0,
            "v115Passes": 0,
            "v118Passes": 0,
            "v122Passes": 0,
            "folds": [],
        }
        for p in RESERVED_PHASES
    }

    for idx, spec in enumerate(fold_specs, 1):
        phase = float(spec["phase"])
        fold = int(spec["fold"])
        ids = spec["ids"]
        train = ids != fold
        test = ids == fold

        chosen_model = v5.choose_model(x_full[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])

        old_q, selector = v56.choose_q_train_only(x_full[train], y[train], measures[train], radius, lam)
        bucket = q_bucket(old_q)
        full_model = v2.fit_pairwise_ranker(x_full[train], y[train], measures[train], radius, lam)
        full_scores = v2.scores_for(x_full[test], full_model)
        v28_pass, v28_lift, v28_held, v28_stats = v17.pass_at_q(full_scores, y[test], ANCHOR_Q)

        candidate_q, decision, dispersion = v80.selected_q({"outerQ": float(old_q), "selector": selector})
        use_tight = bucket == "tight"
        use_safe_broad = bucket == "broad" and decision == "keep-broad-low-dispersion"
        excluded_safe_broad = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
        use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

        if use_v96:
            cos_model = v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
            cos_scores = v2.scores_for(x_cos[test], cos_model)
            v96_pass, v96_lift, v96_held, v96_stats = v17.pass_at_q(cos_scores, y[test], candidate_q)
            if bool(spec["selectedForV112"]):
                aug_model = v2.fit_pairwise_ranker(x_v112[train], y[train], measures[train], radius, lam)
                aug_scores = v2.scores_for(x_v112[test], aug_model)
                v115_pass, v115_lift, v115_held, v115_stats = v17.pass_at_q(aug_scores, y[test], candidate_q)
                v115_rep = "v112_interactions"
            else:
                v115_pass, v115_lift, v115_held, v115_stats = v96_pass, v96_lift, v96_held, v96_stats
                v115_rep = "cosine"
        else:
            v96_pass, v96_lift, v96_held, v96_stats = v28_pass, v28_lift, v28_held, v28_stats
            v115_pass, v115_lift, v115_held, v115_stats = v28_pass, v28_lift, v28_held, v28_stats
            v115_rep = "full_phase"

        dangerous = bool(spec["selectedForV112"] and use_v96 and is_v118_dangerous_signature(bucket, decision, radius, lam))
        if dangerous:
            v118_pass, v118_lift, v118_held, v118_stats = v96_pass, v96_lift, v96_held, v96_stats
            v118_rep = "v96-dangerous-signature-exclusion"
            v118_exclusions += 1
        else:
            v118_pass, v118_lift, v118_held, v118_stats = v115_pass, v115_lift, v115_held, v115_stats
            v118_rep = v115_rep

        key = structural_key(bucket, decision, radius, lam)
        rep = policy.get(key)
        if rep is None:
            v122_pass, v122_lift, v122_held, v122_stats = v118_pass, v118_lift, v118_held, v118_stats
            v122_rep = v118_rep
            structural_applied = False
        else:
            q_to_use = candidate_q if bucket == "tight" else ANCHOR_Q
            if bucket == "broad" and decision == "keep-broad-low-dispersion":
                q_to_use = candidate_q
            x = matrices[rep]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            v122_pass, v122_lift, v122_held, v122_stats = v17.pass_at_q(scores, y[test], q_to_use)
            v122_rep = rep
            structural_applied = True
            policy_applied += 1
            ktxt = f"{key}|{rep}"
            applied_by_group[ktxt] = applied_by_group.get(ktxt, 0) + 1

        total_v28 += int(v28_pass)
        total_v96 += int(v96_pass)
        total_v115 += int(v115_pass)
        total_v118 += int(v118_pass)
        total_v122 += int(v122_pass)
        gains122_vs_v118 += int(v122_pass and not v118_pass)
        losses122_vs_v118 += int(v118_pass and not v122_pass)
        gains122_vs_v96 += int(v122_pass and not v96_pass)
        losses122_vs_v96 += int(v96_pass and not v122_pass)
        rescues122_vs_v28 += int(v122_pass and not v28_pass)
        regressions122_vs_v28 += int(v28_pass and not v122_pass)

        scheme = schemes_map[phase]
        scheme["v28Passes"] += int(v28_pass)
        scheme["v96Passes"] += int(v96_pass)
        scheme["v115Passes"] += int(v115_pass)
        scheme["v118Passes"] += int(v118_pass)
        scheme["v122Passes"] += int(v122_pass)
        scheme["folds"].append({
            "phase": phase,
            "fold": fold,
            "gateScore": float(spec["gateScore"]),
            "selectedForV112": bool(spec["selectedForV112"]),
            "chosenModel": chosen_model,
            "originalTrainingOnlyQ": float(old_q),
            "originalQBucket": bucket,
            "selector": selector,
            "v96Decision": decision,
            "dispersion": None if dispersion is None else float(dispersion),
            "excludedSafeBroadR8Lambda1": excluded_safe_broad,
            "v118DangerousSignatureExclusion": dangerous,
            "structuralPolicyApplied": structural_applied,
            "structuralRepresentation": rep,
            "v28Passed": bool(v28_pass),
            "v96Passed": bool(v96_pass),
            "v115Passed": bool(v115_pass),
            "v118Passed": bool(v118_pass),
            "v122Passed": bool(v122_pass),
            "gainVsV118": bool(v122_pass and not v118_pass),
            "lossVsV118": bool(v118_pass and not v122_pass),
            "finalRepresentation": v122_rep,
            "heldoutPrecisionLift": round(float(v122_lift), 2),
            "heldoutCandidate": v122_held,
        })

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    schemes = [schemes_map[float(p)] for p in RESERVED_PHASES]
    min_phase_v122 = min(int(s["v122Passes"]) for s in schemes)
    min_phase_v118 = min(int(s["v118Passes"]) for s in schemes)
    bottlenecks_v122 = [float(s["phase"]) for s in schemes if int(s["v122Passes"]) == min_phase_v122]

    confirmation_success = bool(
        total_v122 > total_v118
        and gains122_vs_v118 > losses122_vs_v118
        and min_phase_v122 >= 3
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V124")

    out = {
        "schemaVersion": 124,
        "profileType": "fresh-confirmation-of-frozen-v122-structural-policy-on-reserved-5mod16-over1024",
        "reservedPhaseFamily": "numerators-5-mod-16-over-1024",
        "reservedPhases": list(RESERVED_PHASES),
        "foldsTotal": len(fold_specs),
        "gateFractionFrozen": "2/7",
        "selectedForV112BeforeHeldoutEvaluation": int(select_k),
        "positiveStructuralGroupsFrozen": len(policy),
        "frozenStructuralPolicy": [
            {
                "originalQBucket": k[0],
                "v96Decision": k[1],
                "pairRadius": k[2],
                "lambda": k[3],
                "representation": rep,
            }
            for k, rep in sorted(policy.items())
        ],
        "v28Passes": int(total_v28),
        "v28ScorePercent": round(100.0 * total_v28 / len(fold_specs), 4),
        "v96Passes": int(total_v96),
        "v96ScorePercent": round(100.0 * total_v96 / len(fold_specs), 4),
        "v115Passes": int(total_v115),
        "v115ScorePercent": round(100.0 * total_v115 / len(fold_specs), 4),
        "v118Passes": int(total_v118),
        "v118ScorePercent": round(100.0 * total_v118 / len(fold_specs), 4),
        "v122Passes": int(total_v122),
        "v122ScorePercent": round(100.0 * total_v122 / len(fold_specs), 4),
        "gainsVsV118": int(gains122_vs_v118),
        "lossesVsV118": int(losses122_vs_v118),
        "netVsV118": int(gains122_vs_v118 - losses122_vs_v118),
        "gainsVsV96": int(gains122_vs_v96),
        "lossesVsV96": int(losses122_vs_v96),
        "netVsV96": int(gains122_vs_v96 - losses122_vs_v96),
        "rescuesVsV28": int(rescues122_vs_v28),
        "regressionsVsV28": int(regressions122_vs_v28),
        "v118DangerousSignatureExclusionsApplied": int(v118_exclusions),
        "structuralPolicyAppliedRows": int(policy_applied),
        "appliedRowsByGroup": applied_by_group,
        "minimumV122PhasePasses": int(min_phase_v122),
        "minimumV118PhasePasses": int(min_phase_v118),
        "v122BottleneckPhases": bottlenecks_v122,
        "crosses95Percent": bool(100.0 * total_v122 / len(fold_specs) >= 95.0),
        "confirmationSuccess": confirmation_success,
        "validatedNewChampion": confirmation_success,
        "reservedUntouchedPhasesConsumed": True,
        "policyFrozenBeforeV124HeldoutEvaluation": True,
        "v122ChosenFromConsumedV119AndCorroboratedOnV116": True,
        "newTuningPerformed": False,
        "candidateEventsModified": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
        "schemes": schemes,
        "derivedInteractionFeatures": interaction_names,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "schemes"}, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V124 FRESH CONFIRMATION COMPLETE")
    print(f"V28:  {total_v28}/320 = {100.0*total_v28/320.0:.4f}%")
    print(f"V96:  {total_v96}/320 = {100.0*total_v96/320.0:.4f}%")
    print(f"V115: {total_v115}/320 = {100.0*total_v115/320.0:.4f}%")
    print(f"V118: {total_v118}/320 = {100.0*total_v118/320.0:.4f}%")
    print(f"V122: {total_v122}/320 = {100.0*total_v122/320.0:.4f}%")
    print(f"V122 gains/losses vs V118: +{gains122_vs_v118}/-{losses122_vs_v118} net={gains122_vs_v118-losses122_vs_v118:+d}")
    print(f"V122 gains/losses vs V96: +{gains122_vs_v96}/-{losses122_vs_v96} net={gains122_vs_v96-losses122_vs_v96:+d}")
    print(f"Structural policy applied rows: {policy_applied}/320")
    print(f"Minimum V122 phase passes: {min_phase_v122}/5")
    print("V122 bottleneck phases:", bottlenecks_v122)
    print("Crosses 95 percent:", out["crosses95Percent"])
    print("Confirmation success:", confirmation_success)
    print("Validated new champion:", confirmation_success)
    print("Reserved untouched phases consumed: True")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
