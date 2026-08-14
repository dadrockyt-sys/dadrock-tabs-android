from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

import confirm_gomyway_3676_patch_rhythm24_v122_reserved_5mod16_over1024_v124 as v124

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V119_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
V124_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
V127_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v126-phasecol3-selected-guard-reverse-validation-v127.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128-manifest.json"

OUTER_FOLDS = v124.OUTER_FOLDS
ANCHOR_Q = v124.ANCHOR_Q
GATE_NUM = v124.GATE_NUM
GATE_DEN = v124.GATE_DEN
REPRESENTATIONS = v124.REPRESENTATIONS
EXPECTED = v124.EXPECTED

# Reserved in WORKFLOW_RECOVERY_CHECKPOINT.md before V125 interpretation.
# 64 odd numerators, all 7 mod 16 over 1024; disjoint from consumed
# 1-mod-16 V116, 3-mod-16 V119, and 5-mod-16 V124 families.
RESERVED_PHASES = tuple((7 + 16 * k) / 1024.0 for k in range(64))

GUARD_KEY = ("tight", "revert-tight-to-anchor-low-dispersion", 4, 1.0)
GUARD_REPRESENTATION = "phase_col3"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v124.v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v119 = json.loads(V119_PATH.read_text(encoding="utf-8"))
    v124_result = json.loads(V124_PATH.read_text(encoding="utf-8"))
    v127 = json.loads(V127_PATH.read_text(encoding="utf-8"))

    if int(v119.get("schemaVersion", -1)) != 119 or not bool(v119.get("validatedNewChampion")):
        raise RuntimeError("Validated V119 checkpoint required")
    if int(v124_result.get("schemaVersion", -1)) != 124 or not bool(v124_result.get("validatedNewChampion")):
        raise RuntimeError("Validated V124/V122 champion required")
    if int(v124_result.get("v122Passes", -1)) != 308 or int(v124_result.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V124 does not match frozen 308/320 V122 champion")
    if int(v127.get("schemaVersion", -1)) != 127:
        raise RuntimeError("Frozen V127 guard record required")
    s127 = v127.get("summary") or {}
    c127 = s127.get("v124Consumed") or {}
    r127 = s127.get("v116ReverseValidation") or {}
    if not (
        int(c127.get("gainsVsV122", -1)) == 2
        and int(c127.get("lossesVsV122", -1)) == 0
        and int(r127.get("gainsVsV122", -1)) == 2
        and int(r127.get("lossesVsV122", -1)) == 0
    ):
        raise RuntimeError("V127 corroboration does not match frozen +2/-0 guard evidence")

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
            raise RuntimeError(f"Unexpected frozen representation: {rep}")
        policy[key] = rep
    if len(policy) != 7:
        raise RuntimeError(f"Expected seven frozen V122 structural groups, got {len(policy)}")
    if policy.get(GUARD_KEY) != GUARD_REPRESENTATION:
        raise RuntimeError("V122 phase_col3 guard target is not frozen as expected")

    consumed = set()
    for src in (v119, v124_result):
        consumed |= {round(float(p), 12) for p in (src.get("reservedPhases") or [])}
    new_phases = {round(float(p), 12) for p in RESERVED_PHASES}
    if consumed & new_phases:
        raise RuntimeError("V128 reserve overlaps a previously consumed reserve")

    payload = json.loads(v124.SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
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

    gate_fit = v124.fit_frozen_gate_from_exposed(xb, names, pf, measures, lo, hi)

    # Freeze the V115/V118 gate on the complete untouched family before any held-out evaluation.
    fold_specs = []
    for phase in RESERVED_PHASES:
        ids = np.asarray(
            [v124.v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures],
            dtype=np.int16,
        )
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

    print("Starting V128 untouched confirmation of frozen V122 + V127 guard", flush=True)
    print("Fresh reserve: numerators 7 mod 16 over 1024 = 64 phases / 320 folds", flush=True)
    print("V122 structural policy and V127 selectedForV112 phase_col3 guard frozen before held-out evaluation", flush=True)
    print(f"V112 selected before held-out evaluation: {select_k}/{len(fold_specs)}", flush=True)

    totals = {k: 0 for k in ("v28", "v96", "v115", "v118", "v122", "v128")}
    gains128_vs122 = losses128_vs122 = 0
    gains128_vs118 = losses128_vs118 = 0
    gains128_vs96 = losses128_vs96 = 0
    rescues128_vs28 = regressions128_vs28 = 0
    v118_exclusions = 0
    structural_applied_count = 0
    guard_applied_count = 0
    applied_by_group: dict[str, int] = {}

    schemes_map = {
        float(p): {
            "phase": float(p),
            "v28Passes": 0,
            "v96Passes": 0,
            "v115Passes": 0,
            "v118Passes": 0,
            "v122Passes": 0,
            "v128Passes": 0,
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

        dangerous = bool(
            spec["selectedForV112"]
            and use_v96
            and v124.is_v118_dangerous_signature(bucket, decision, radius, lam)
        )
        if dangerous:
            v118_pass, v118_lift, v118_held, v118_stats = v96_pass, v96_lift, v96_held, v96_stats
            v118_rep = "v96-dangerous-signature-exclusion"
            v118_exclusions += 1
        else:
            v118_pass, v118_lift, v118_held, v118_stats = v115_pass, v115_lift, v115_held, v115_stats
            v118_rep = v115_rep

        key = v124.structural_key(bucket, decision, radius, lam)
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
            model = v124.v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v124.v2.scores_for(x[test], model)
            v122_pass, v122_lift, v122_held, v122_stats = v124.v17.pass_at_q(scores, y[test], q_to_use)
            v122_rep = rep
            structural_applied = True
            structural_applied_count += 1
            ktxt = f"{key}|{rep}"
            applied_by_group[ktxt] = applied_by_group.get(ktxt, 0) + 1

        # Frozen V127 guard: only inside the phase_col3 structural group, if the
        # pre-held-out V112 gate selected this fold, suppress phase_col3 and fall
        # back to the frozen V118 baseline.
        guard_applied = bool(
            key == GUARD_KEY
            and rep == GUARD_REPRESENTATION
            and bool(spec["selectedForV112"])
        )
        if guard_applied:
            v128_pass, v128_lift, v128_held, v128_stats = v118_pass, v118_lift, v118_held, v118_stats
            v128_rep = "v118-phasecol3-selected-guard"
            guard_applied_count += 1
        else:
            v128_pass, v128_lift, v128_held, v128_stats = v122_pass, v122_lift, v122_held, v122_stats
            v128_rep = v122_rep

        vals = {
            "v28": bool(v28_pass), "v96": bool(v96_pass), "v115": bool(v115_pass),
            "v118": bool(v118_pass), "v122": bool(v122_pass), "v128": bool(v128_pass),
        }
        for name, passed in vals.items():
            totals[name] += int(passed)

        gains128_vs122 += int(v128_pass and not v122_pass)
        losses128_vs122 += int(v122_pass and not v128_pass)
        gains128_vs118 += int(v128_pass and not v118_pass)
        losses128_vs118 += int(v118_pass and not v128_pass)
        gains128_vs96 += int(v128_pass and not v96_pass)
        losses128_vs96 += int(v96_pass and not v128_pass)
        rescues128_vs28 += int(v128_pass and not v28_pass)
        regressions128_vs28 += int(v28_pass and not v128_pass)

        scheme = schemes_map[phase]
        for name in ("v28", "v96", "v115", "v118", "v122", "v128"):
            scheme[f"{name}Passes"] += int(vals[name])
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
            "v127GuardApplied": guard_applied,
            "v28Passed": bool(v28_pass),
            "v96Passed": bool(v96_pass),
            "v115Passed": bool(v115_pass),
            "v118Passed": bool(v118_pass),
            "v122Passed": bool(v122_pass),
            "v128Passed": bool(v128_pass),
            "gainV128VsV122": bool(v128_pass and not v122_pass),
            "lossV128VsV122": bool(v122_pass and not v128_pass),
            "finalRepresentation": v128_rep,
            "heldoutPrecisionLift": round(float(v128_lift), 2),
            "heldoutCandidate": v128_held,
        })

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    schemes = [schemes_map[float(p)] for p in RESERVED_PHASES]
    min_phase_v128 = min(int(s["v128Passes"]) for s in schemes)
    min_phase_v122 = min(int(s["v122Passes"]) for s in schemes)
    bottlenecks_v128 = [float(s["phase"]) for s in schemes if int(s["v128Passes"]) == min_phase_v128]

    confirmation_success = bool(
        totals["v128"] > totals["v122"]
        and gains128_vs122 > losses128_vs122
        and min_phase_v128 >= 3
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V128")

    out = {
        "schemaVersion": 128,
        "profileType": "fresh-confirmation-of-frozen-v122-plus-v127-guard-on-reserved-7mod16-over1024",
        "reservedPhaseFamily": "numerators-7-mod-16-over-1024",
        "reservedPhases": list(RESERVED_PHASES),
        "foldsTotal": len(fold_specs),
        "gateFractionFrozen": "2/7",
        "selectedForV112BeforeHeldoutEvaluation": int(select_k),
        "frozenChampionBaseline": "V122/V124",
        "frozenGuard": {
            "structuralKey": {
                "originalQBucket": GUARD_KEY[0],
                "v96Decision": GUARD_KEY[1],
                "pairRadius": GUARD_KEY[2],
                "lambda": GUARD_KEY[3],
            },
            "representation": GUARD_REPRESENTATION,
            "condition": "selectedForV112 == true",
            "action": "fall back to frozen V118 baseline",
        },
        "v28Passes": totals["v28"],
        "v28ScorePercent": round(100.0 * totals["v28"] / len(fold_specs), 4),
        "v96Passes": totals["v96"],
        "v96ScorePercent": round(100.0 * totals["v96"] / len(fold_specs), 4),
        "v115Passes": totals["v115"],
        "v115ScorePercent": round(100.0 * totals["v115"] / len(fold_specs), 4),
        "v118Passes": totals["v118"],
        "v118ScorePercent": round(100.0 * totals["v118"] / len(fold_specs), 4),
        "v122Passes": totals["v122"],
        "v122ScorePercent": round(100.0 * totals["v122"] / len(fold_specs), 4),
        "v128Passes": totals["v128"],
        "v128ScorePercent": round(100.0 * totals["v128"] / len(fold_specs), 4),
        "gainsVsV122": gains128_vs122,
        "lossesVsV122": losses128_vs122,
        "netVsV122": gains128_vs122 - losses128_vs122,
        "gainsVsV118": gains128_vs118,
        "lossesVsV118": losses128_vs118,
        "netVsV118": gains128_vs118 - losses128_vs118,
        "gainsVsV96": gains128_vs96,
        "lossesVsV96": losses128_vs96,
        "netVsV96": gains128_vs96 - losses128_vs96,
        "rescuesVsV28": rescues128_vs28,
        "regressionsVsV28": regressions128_vs28,
        "v118DangerousSignatureExclusionsApplied": v118_exclusions,
        "structuralPolicyAppliedRows": structural_applied_count,
        "v127GuardAppliedRows": guard_applied_count,
        "appliedRowsByGroup": applied_by_group,
        "minimumV128PhasePasses": min_phase_v128,
        "minimumV122PhasePasses": min_phase_v122,
        "v128BottleneckPhases": bottlenecks_v128,
        "crosses95Percent": bool(100.0 * totals["v128"] / len(fold_specs) >= 95.0),
        "confirmationSuccess": confirmation_success,
        "validatedNewChampion": confirmation_success,
        "reservedUntouchedPhasesConsumed": True,
        "policyAndGuardFrozenBeforeV128HeldoutEvaluation": True,
        "v127GuardChosenFromConsumedV124AndCorroboratedOnV116": True,
        "newTuningPerformed": False,
        "candidateEventsModified": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
        "schemes": schemes,
        "derivedInteractionFeatures": interaction_names,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({k: v for k, v in out.items() if k != "schemes"}, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V128 FRESH CONFIRMATION COMPLETE")
    print(f"V122 baseline: {totals['v122']}/320 = {100.0*totals['v122']/320.0:.4f}%")
    print(f"V128 guarded:  {totals['v128']}/320 = {100.0*totals['v128']/320.0:.4f}%")
    print(f"V128 gains/losses vs V122: +{gains128_vs122}/-{losses128_vs122} net={gains128_vs122-losses128_vs122:+d}")
    print(f"V128 gains/losses vs V118: +{gains128_vs118}/-{losses128_vs118} net={gains128_vs118-losses128_vs118:+d}")
    print(f"V127 guard applied rows: {guard_applied_count}/320")
    print(f"Minimum V128 phase passes: {min_phase_v128}/5")
    print("V128 bottleneck phases:", bottlenecks_v128)
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
