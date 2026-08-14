from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

import confirm_gomyway_3676_patch_rhythm24_v122_reserved_5mod16_over1024_v124 as v124

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
V119_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
V124_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
V127_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v126-phasecol3-selected-guard-reverse-validation-v127.json"
V128_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
V133_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v132-selective-v112-guard-reverse-validation-v133.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v133-conjunction-guard-reserved-9mod16-over1024-confirmation-v134.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v133-conjunction-guard-reserved-9mod16-over1024-confirmation-v134-manifest.json"

OUTER_FOLDS = v124.OUTER_FOLDS
ANCHOR_Q = v124.ANCHOR_Q
GATE_NUM = v124.GATE_NUM
GATE_DEN = v124.GATE_DEN
REPRESENTATIONS = v124.REPRESENTATIONS
EXPECTED = v124.EXPECTED

# Predeclared in WORKFLOW_RECOVERY_CHECKPOINT.md before V129 interpretation.
RESERVED_PHASES = tuple((9 + 16 * k) / 1024.0 for k in range(64))

# Frozen V127 guard already validated by V128.
V127_GUARD_KEY = ("tight", "revert-tight-to-anchor-low-dispersion", 4, 1.0)
V127_GUARD_REP = "phase_col3"

# Frozen V134 selective intervention chosen after V133 corroboration.
V134_TARGET_KEY = ("anchor", "keep-anchor", 4, 1.0)
V134_TARGET_REP = "v112_interactions"
V134_GATE_THRESHOLD = -5.4
V134_PHASE_THRESHOLD = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def v134_selector(spec: dict, key: tuple[str, str, int, float]) -> bool:
    return bool(
        key == V134_TARGET_KEY
        and float(spec["gateScore"]) <= V134_GATE_THRESHOLD
        and float(spec["phase"]) < V134_PHASE_THRESHOLD
    )


def main() -> None:
    candidate_path = v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))
    v119 = json.loads(V119_PATH.read_text(encoding="utf-8"))
    v124_result = json.loads(V124_PATH.read_text(encoding="utf-8"))
    v127 = json.loads(V127_PATH.read_text(encoding="utf-8"))
    v128 = json.loads(V128_PATH.read_text(encoding="utf-8"))
    v133 = json.loads(V133_PATH.read_text(encoding="utf-8"))

    if int(v116.get("schemaVersion", -1)) != 116 or not bool(v116.get("validatedNewChampion")):
        raise RuntimeError("Validated V116 checkpoint required")
    if int(v119.get("schemaVersion", -1)) != 119 or not bool(v119.get("validatedNewChampion")):
        raise RuntimeError("Validated V119 checkpoint required")
    if int(v124_result.get("schemaVersion", -1)) != 124 or not bool(v124_result.get("validatedNewChampion")):
        raise RuntimeError("Validated V124/V122 checkpoint required")
    if int(v128.get("schemaVersion", -1)) != 128 or not bool(v128.get("validatedNewChampion")):
        raise RuntimeError("Validated V128 champion required")
    if int(v128.get("v128Passes", -1)) != 309 or int(v128.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V128 must match frozen 309/320 champion")
    if int(v127.get("schemaVersion", -1)) != 127:
        raise RuntimeError("Frozen V127 guard record required")
    if int(v133.get("schemaVersion", -1)) != 133:
        raise RuntimeError("V133 corroboration record required")

    # Verify V133 showed the exact frozen conjunction was +2/-0 on both exposed families.
    c133 = (v133.get("consumedV128Development") or {}).get("conjunction") or {}
    r133 = (v133.get("v116ReverseValidation") or {}).get("conjunction") or {}
    if not (
        int(c133.get("gains", -1)) == 2 and int(c133.get("losses", -1)) == 0
        and int(r133.get("gains", -1)) == 2 and int(r133.get("losses", -1)) == 0
        and int(c133.get("appliedRows", -1)) == 6 and int(r133.get("appliedRows", -1)) == 6
    ):
        raise RuntimeError("V133 conjunction evidence does not match frozen +2/-0, six-row corroboration")

    policy: dict[tuple[str, str, int, float], str] = {}
    for row in v124_result.get("frozenStructuralPolicy") or []:
        key = (
            str(row.get("originalQBucket")),
            str(row.get("v96Decision")),
            int(row.get("pairRadius")),
            float(row.get("lambda")),
        )
        rep = str(row.get("representation"))
        if rep not in REPRESENTATIONS:
            raise RuntimeError(f"Unexpected frozen representation {rep}")
        policy[key] = rep
    if len(policy) != 7:
        raise RuntimeError(f"Expected seven frozen V122 structural groups, got {len(policy)}")
    if policy.get(V127_GUARD_KEY) != V127_GUARD_REP:
        raise RuntimeError("Frozen V127 guard target mismatch")
    if policy.get(V134_TARGET_KEY) != "cosine":
        raise RuntimeError("V134 target must start from frozen V128 cosine representation")

    # Prove the new reserve is disjoint from all four previously consumed mod-16 families.
    consumed = set()
    for src in (v116, v119, v124_result, v128):
        consumed |= {round(float(p), 12) for p in (src.get("reservedPhases") or [])}
    new_phases = {round(float(p), 12) for p in RESERVED_PHASES}
    if consumed & new_phases:
        raise RuntimeError("V134 reserve overlaps a previously consumed reserve")

    payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    pf = np.asarray(v124.v17.phase_features(rows), dtype=np.float64)
    interactions, interaction_names = v124.v112.build_phase_interactions(xb, names, pf)
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

    # Fit frozen V115/V118 gate from exposed development only, then rank the whole
    # fresh family before any held-out fold is scored.
    gate_fit = v124.fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)
    fold_specs = []
    for phase in RESERVED_PHASES:
        ids = np.asarray([v124.v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        for fold in range(OUTER_FOLDS):
            train = ids != fold
            gx = np.asarray([v124.gate_features_for_mask(xb, names, pf, train)], dtype=np.float64)
            gate_score = float(v124.v110.predict(gx, gate_fit)[0])
            fold_specs.append({"phase": float(phase), "fold": int(fold), "ids": ids, "gateScore": gate_score})

    select_k = int(math.ceil(len(fold_specs) * GATE_NUM / GATE_DEN))
    order = np.argsort(-np.asarray([r["gateScore"] for r in fold_specs], dtype=np.float64))
    selected_indices = set(int(i) for i in order[:select_k])
    for i, spec in enumerate(fold_specs):
        spec["selectedForV112"] = i in selected_indices

    print("Starting V134 untouched confirmation of frozen V128 + V133 conjunction intervention", flush=True)
    print("Fresh reserve: numerators 9 mod 16 over 1024 = 64 phases / 320 folds", flush=True)
    print("Selector frozen before held-out evaluation: anchor/keep-anchor/r4/lambda1 AND gateScore<=-5.4 AND phase<0.5 -> v112_interactions", flush=True)
    print(f"V112 selected before held-out evaluation: {select_k}/{len(fold_specs)}", flush=True)

    totals = {k: 0 for k in ("v28", "v96", "v115", "v118", "v122", "v128", "v134")}
    gains134_vs128 = losses134_vs128 = 0
    gains134_vs122 = losses134_vs122 = 0
    gains134_vs118 = losses134_vs118 = 0
    structural_applied_count = 0
    v127_guard_count = 0
    v134_applied_count = 0

    schemes_map = {
        float(p): {
            "phase": float(p), "v122Passes": 0, "v128Passes": 0, "v134Passes": 0, "folds": []
        }
        for p in RESERVED_PHASES
    }

    for idx, spec in enumerate(fold_specs, 1):
        phase = float(spec["phase"])
        fold = int(spec["fold"])
        ids = spec["ids"]
        train = ids != fold
        test = ids == fold

        chosen_model = v124.v5.choose_model(x_full[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        old_q, selector = v124.v56.choose_q_train_only(x_full[train], y[train], measures[train], radius, lam)
        bucket = v124.q_bucket(old_q)

        full_model = v124.v2.fit_pairwise_ranker(x_full[train], y[train], measures[train], radius, lam)
        full_scores = v124.v2.scores_for(x_full[test], full_model)
        v28_pass, v28_lift, v28_held, v28_stats = v124.v17.pass_at_q(full_scores, y[test], ANCHOR_Q)

        candidate_q, decision, dispersion = v124.v80.selected_q({"outerQ": float(old_q), "selector": selector})
        use_tight = bucket == "tight"
        use_safe_broad = bucket == "broad" and decision == "keep-broad-low-dispersion"
        excluded_safe_broad = bool(use_safe_broad and radius == 8 and abs(lam - 1.0) < 1e-12)
        use_v96 = use_tight or (use_safe_broad and not excluded_safe_broad)

        if use_v96:
            cos_model = v124.v2.fit_pairwise_ranker(x_cos[train], y[train], measures[train], radius, lam)
            cos_scores = v124.v2.scores_for(x_cos[test], cos_model)
            v96_pass, v96_lift, v96_held, v96_stats = v124.v17.pass_at_q(cos_scores, y[test], candidate_q)
            if bool(spec["selectedForV112"]):
                aug_model = v124.v2.fit_pairwise_ranker(x_v112[train], y[train], measures[train], radius, lam)
                aug_scores = v124.v2.scores_for(x_v112[test], aug_model)
                v115_pass, v115_lift, v115_held, v115_stats = v124.v17.pass_at_q(aug_scores, y[test], candidate_q)
                v115_rep = "v112_interactions"
            else:
                v115_pass, v115_lift, v115_held, v115_stats = v96_pass, v96_lift, v96_held, v96_stats
                v115_rep = "cosine"
        else:
            v96_pass, v96_lift, v96_held, v96_stats = v28_pass, v28_lift, v28_held, v28_stats
            v115_pass, v115_lift, v115_held, v115_stats = v28_pass, v28_lift, v28_held, v28_stats
            v115_rep = "full_phase"

        dangerous = bool(spec["selectedForV112"] and use_v96 and v124.is_v118_dangerous_signature(bucket, decision, radius, lam))
        if dangerous:
            v118_pass, v118_lift, v118_held, v118_stats = v96_pass, v96_lift, v96_held, v96_stats
            v118_rep = "v96-dangerous-signature-exclusion"
        else:
            v118_pass, v118_lift, v118_held, v118_stats = v115_pass, v115_lift, v115_held, v115_stats
            v118_rep = v115_rep

        key = v124.structural_key(bucket, decision, radius, lam)
        rep = policy.get(key)
        q_to_use = candidate_q if bucket == "tight" else ANCHOR_Q
        if bucket == "broad" and decision == "keep-broad-low-dispersion":
            q_to_use = candidate_q

        if rep is None:
            v122_pass, v122_lift, v122_held, v122_stats = v118_pass, v118_lift, v118_held, v118_stats
            v122_rep = v118_rep
            structural_applied = False
        else:
            x = matrices[rep]
            model = v124.v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v124.v2.scores_for(x[test], model)
            v122_pass, v122_lift, v122_held, v122_stats = v124.v17.pass_at_q(scores, y[test], q_to_use)
            v122_rep = rep
            structural_applied = True
            structural_applied_count += 1

        v127_guard_applied = bool(key == V127_GUARD_KEY and rep == V127_GUARD_REP and bool(spec["selectedForV112"]))
        if v127_guard_applied:
            v128_pass, v128_lift, v128_held, v128_stats = v118_pass, v118_lift, v118_held, v118_stats
            v128_rep = "v118-phasecol3-selected-guard"
            v127_guard_count += 1
        else:
            v128_pass, v128_lift, v128_held, v128_stats = v122_pass, v122_lift, v122_held, v122_stats
            v128_rep = v122_rep

        selective_applied = v134_selector(spec, key)
        if selective_applied:
            alt_model = v124.v2.fit_pairwise_ranker(x_v112[train], y[train], measures[train], radius, lam)
            alt_scores = v124.v2.scores_for(x_v112[test], alt_model)
            v134_pass, v134_lift, v134_held, v134_stats = v124.v17.pass_at_q(alt_scores, y[test], q_to_use)
            v134_rep = V134_TARGET_REP
            v134_applied_count += 1
        else:
            v134_pass, v134_lift, v134_held, v134_stats = v128_pass, v128_lift, v128_held, v128_stats
            v134_rep = v128_rep

        vals = {
            "v28": bool(v28_pass), "v96": bool(v96_pass), "v115": bool(v115_pass),
            "v118": bool(v118_pass), "v122": bool(v122_pass), "v128": bool(v128_pass), "v134": bool(v134_pass),
        }
        for name, passed in vals.items():
            totals[name] += int(passed)

        gains134_vs128 += int(v134_pass and not v128_pass)
        losses134_vs128 += int(v128_pass and not v134_pass)
        gains134_vs122 += int(v134_pass and not v122_pass)
        losses134_vs122 += int(v122_pass and not v134_pass)
        gains134_vs118 += int(v134_pass and not v118_pass)
        losses134_vs118 += int(v118_pass and not v134_pass)

        scheme = schemes_map[phase]
        scheme["v122Passes"] += int(v122_pass)
        scheme["v128Passes"] += int(v128_pass)
        scheme["v134Passes"] += int(v134_pass)
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
            "structuralPolicyApplied": structural_applied,
            "structuralRepresentation": rep,
            "v127GuardApplied": v127_guard_applied,
            "v134SelectiveInterventionApplied": selective_applied,
            "v118Passed": bool(v118_pass),
            "v122Passed": bool(v122_pass),
            "v128Passed": bool(v128_pass),
            "v134Passed": bool(v134_pass),
            "gainV134VsV128": bool(v134_pass and not v128_pass),
            "lossV134VsV128": bool(v128_pass and not v134_pass),
            "finalRepresentation": v134_rep,
            "heldoutPrecisionLift": round(float(v134_lift), 2),
            "heldoutCandidate": v134_held,
        })

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    schemes = [schemes_map[float(p)] for p in RESERVED_PHASES]
    min_phase_v134 = min(int(s["v134Passes"]) for s in schemes)
    min_phase_v128 = min(int(s["v128Passes"]) for s in schemes)
    bottlenecks_v134 = [float(s["phase"]) for s in schemes if int(s["v134Passes"]) == min_phase_v134]

    confirmation_success = bool(
        totals["v134"] > totals["v128"]
        and gains134_vs128 > losses134_vs128
        and min_phase_v134 >= 3
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V134")

    out = {
        "schemaVersion": 134,
        "profileType": "fresh-confirmation-of-frozen-v128-plus-v133-conjunction-on-reserved-9mod16-over1024",
        "reservedPhaseFamily": "numerators-9-mod-16-over-1024",
        "reservedPhases": list(RESERVED_PHASES),
        "foldsTotal": len(fold_specs),
        "gateFractionFrozen": "2/7",
        "selectedForV112BeforeHeldoutEvaluation": int(select_k),
        "frozenChampionBaseline": "V127/V128",
        "frozenAdditionalIntervention": {
            "structuralKey": {"originalQBucket": V134_TARGET_KEY[0], "v96Decision": V134_TARGET_KEY[1], "pairRadius": V134_TARGET_KEY[2], "lambda": V134_TARGET_KEY[3]},
            "representation": V134_TARGET_REP,
            "selector": "gateScore <= -5.4 AND phase < 0.5",
            "chosenBecause": "same +2/-0 on consumed V128 and reverse V116 as broader selectors, but only 6 applied rows on each exposed family",
        },
        "v28Passes": totals["v28"],
        "v96Passes": totals["v96"],
        "v115Passes": totals["v115"],
        "v118Passes": totals["v118"],
        "v122Passes": totals["v122"],
        "v128Passes": totals["v128"],
        "v128ScorePercent": round(100.0 * totals["v128"] / len(fold_specs), 4),
        "v134Passes": totals["v134"],
        "v134ScorePercent": round(100.0 * totals["v134"] / len(fold_specs), 4),
        "gainsVsV128": gains134_vs128,
        "lossesVsV128": losses134_vs128,
        "netVsV128": gains134_vs128 - losses134_vs128,
        "gainsVsV122": gains134_vs122,
        "lossesVsV122": losses134_vs122,
        "netVsV122": gains134_vs122 - losses134_vs122,
        "gainsVsV118": gains134_vs118,
        "lossesVsV118": losses134_vs118,
        "netVsV118": gains134_vs118 - losses134_vs118,
        "structuralPolicyAppliedRows": structural_applied_count,
        "v127GuardAppliedRows": v127_guard_count,
        "v134SelectiveInterventionAppliedRows": v134_applied_count,
        "minimumV128PhasePasses": min_phase_v128,
        "minimumV134PhasePasses": min_phase_v134,
        "v134BottleneckPhases": bottlenecks_v134,
        "crosses95Percent": bool(100.0 * totals["v134"] / len(fold_specs) >= 95.0),
        "confirmationSuccess": confirmation_success,
        "validatedNewChampion": confirmation_success,
        "reservedUntouchedPhasesConsumed": True,
        "policyAndSelectorFrozenBeforeV134HeldoutEvaluation": True,
        "v133SelectorChosenFromConsumedV128AndCorroboratedOnV116": True,
        "newTuningPerformed": False,
        "candidateEventsModified": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
        "schemes": schemes,
        "derivedInteractionFeatures": interaction_names,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "schemes"}, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V134 FRESH CONFIRMATION COMPLETE")
    print(f"V128 baseline: {totals['v128']}/320 = {100.0*totals['v128']/320.0:.4f}%")
    print(f"V134 selective: {totals['v134']}/320 = {100.0*totals['v134']/320.0:.4f}%")
    print(f"V134 gains/losses vs V128: +{gains134_vs128}/-{losses134_vs128} net={gains134_vs128-losses134_vs128:+d}")
    print(f"V134 selective intervention applied rows: {v134_applied_count}/320")
    print(f"Minimum V134 phase passes: {min_phase_v134}/5")
    print("V134 bottleneck phases:", bottlenecks_v134)
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
