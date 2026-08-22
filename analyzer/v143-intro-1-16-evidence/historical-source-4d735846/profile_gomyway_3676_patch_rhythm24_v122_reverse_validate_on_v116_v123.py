from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28
import profile_gomyway_3676_patch_rhythm24_v79_cosine_dual_dispersion_combined_v80 as v80
import profile_gomyway_3676_patch_rhythm24_v111_lowband_phase_interaction_augmentation_v112 as v112

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V116_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v115-reserved-1over1024-stride16-confirmation-v116.json"
V122_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v121-structural-representation-utility-v122.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reverse-validation-on-v116-v123.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reverse-validation-on-v116-v123-manifest.json"

OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def structural_key(row: dict) -> tuple[str, str, int, float]:
    model = row.get("chosenModel") or {}
    return (
        str(row.get("originalQBucket")),
        str(row.get("v96Decision")),
        int(model.get("pairRadius")),
        float(model.get("lambda")),
    )


def dangerous_v118_exclusion(row: dict) -> bool:
    key = structural_key(row)
    return bool(
        bool(row.get("selectedForV112"))
        and key == ("tight", "revert-tight-to-anchor-low-dispersion", 8, 1.0)
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))
    v122 = json.loads(V122_PATH.read_text(encoding="utf-8"))
    if int(v116.get("schemaVersion", -1)) != 116 or not bool(v116.get("validatedNewChampion")):
        raise RuntimeError("Validated V116 confirmation required")
    if int(v116.get("v115Passes", -1)) != 288 or int(v116.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V116 does not match frozen 288/320 result")
    if int(v122.get("schemaVersion", -1)) != 122:
        raise RuntimeError("V122 structural utility diagnostic required")

    policy = {}
    for row in v122.get("positiveBestPerStructuralGroup") or []:
        key = (
            str(row.get("originalQBucket")),
            str(row.get("v96Decision")),
            int(row.get("pairRadius")),
            float(row.get("lambda")),
        )
        policy[key] = str(row.get("representation"))
    if not policy:
        raise RuntimeError("V122 has no positive structural policy")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Source candidate slots missing")

    names = sorted((source_rows[0].get("features") or {}).keys())
    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in source_rows],
        dtype=np.float64,
    )
    pf = np.asarray(v17.phase_features(source_rows), dtype=np.float64)
    interactions, interaction_names = v112.build_phase_interactions(xb, names, pf)
    matrices = {
        "base": xb,
        "phase_col3": np.concatenate([xb, pf[:, [3]]], axis=1),
        "full_phase": np.concatenate([xb, pf], axis=1),
        "cosine": np.concatenate([xb, pf[:, [1, 3]]], axis=1),
        "v112_interactions": np.concatenate([xb, pf[:, [1, 3]], interactions], axis=1),
    }
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    rows = []
    for scheme in v116.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 V116 rows, got {len(rows)}")

    baseline_passes = 0
    candidate_passes = 0
    gains = losses = 0
    changed_rows = 0
    applied_by_group = {}

    print("GOMYWAY V123 REVERSE VALIDATION OF V122 POLICY ON PRIOR V116 FAMILY", flush=True)
    print("V122 policy frozen from consumed V119; V116 used only for reverse validation", flush=True)

    for idx, r in enumerate(rows, 1):
        key = structural_key(r)
        baseline = bool(r.get("v96Passed")) if dangerous_v118_exclusion(r) else bool(r.get("v115Passed"))
        baseline_passes += int(baseline)

        rep = policy.get(key)
        if rep is None:
            candidate = baseline
        else:
            phase = float(r["phase"])
            fold = int(r["fold"])
            model_bits = r.get("chosenModel") or {}
            radius = int(model_bits["pairRadius"])
            lam = float(model_bits["lambda"])
            ids = np.asarray(
                [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
                dtype=np.int16,
            )
            train = ids != fold
            test = ids == fold
            old_q = float(r.get("originalTrainingOnlyQ"))
            selector = r.get("selector") or {}
            candidate_q, _, _ = v80.selected_q({"outerQ": old_q, "selector": selector})
            bucket = str(r.get("originalQBucket"))
            decision = str(r.get("v96Decision"))
            q_to_use = candidate_q if bucket == "tight" else ANCHOR_Q
            if bucket == "broad" and decision == "keep-broad-low-dispersion":
                q_to_use = candidate_q

            x = matrices[rep]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            candidate, _, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            candidate = bool(candidate)
            changed_rows += 1
            ktxt = f"{key}|{rep}"
            applied_by_group[ktxt] = applied_by_group.get(ktxt, 0) + 1

        candidate_passes += int(candidate)
        gains += int(candidate and not baseline)
        losses += int(baseline and not candidate)

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V123")

    summary = {
        "foldsTotal": 320,
        "reverseValidationFamily": "V116 numerators-1-mod-16-over-1024",
        "baselineV118PassesReconstructed": int(baseline_passes),
        "baselineV118ScorePercent": round(100.0 * baseline_passes / 320.0, 4),
        "v122PolicyPasses": int(candidate_passes),
        "v122PolicyScorePercent": round(100.0 * candidate_passes / 320.0, 4),
        "gainsVsV118": int(gains),
        "lossesVsV118": int(losses),
        "netVsV118": int(gains - losses),
        "rowsPolicyApplied": int(changed_rows),
        "positiveStructuralGroupsFrozen": len(policy),
    }
    out = {
        "schemaVersion": 123,
        "profileType": "reverse-validation-of-v122-structural-policy-on-prior-v116-family",
        "summary": summary,
        "frozenPolicy": [
            {
                "originalQBucket": k[0],
                "v96Decision": k[1],
                "pairRadius": k[2],
                "lambda": k[3],
                "representation": rep,
            }
            for k, rep in sorted(policy.items())
        ],
        "appliedRowsByGroup": applied_by_group,
        "policyChosenWithoutUsingV116ForStructuralSelection": True,
        "v116PreviouslyConsumedForEarlierV115V118Development": True,
        "reverseValidationIsCorroborativeNotFreshConfirmation": True,
        "newReservedPhaseFamilyReferenced": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V123 REVERSE VALIDATION COMPLETE")
    print(f"Reconstructed frozen V118 baseline on V116: {baseline_passes}/320 = {100.0*baseline_passes/320.0:.4f}%")
    print(f"Frozen V122 structural policy on V116: {candidate_passes}/320 = {100.0*candidate_passes/320.0:.4f}%")
    print(f"Gains/losses vs V118: +{gains}/-{losses} net={gains-losses:+d}")
    print(f"Policy-applied rows: {changed_rows}/320")
    print("Important: V123 is corroborative reverse validation, NOT fresh confirmation")
    print("New reserved phase family referenced: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
