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
V124_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v122-reserved-5mod16-over1024-confirmation-v124.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v126-phasecol3-selected-guard-reverse-validation-v127.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v126-phasecol3-selected-guard-reverse-validation-v127-manifest.json"

OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
TARGET = ("tight", "revert-tight-to-anchor-low-dispersion", 4, 1.0)


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
    return bool(
        bool(row.get("selectedForV112"))
        and structural_key(row) == ("tight", "revert-tight-to-anchor-low-dispersion", 8, 1.0)
    )


def phasecol3_selected_guard(row: dict, rep: str | None) -> bool:
    return bool(
        rep == "phase_col3"
        and structural_key(row) == TARGET
        and bool(row.get("selectedForV112"))
    )


def load_policy(v122: dict) -> dict:
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
    if policy.get(TARGET) != "phase_col3":
        raise RuntimeError("Frozen V122 target group is not phase_col3")
    return policy


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v116 = json.loads(V116_PATH.read_text(encoding="utf-8"))
    v122 = json.loads(V122_PATH.read_text(encoding="utf-8"))
    v124 = json.loads(V124_PATH.read_text(encoding="utf-8"))
    if int(v116.get("schemaVersion", -1)) != 116:
        raise RuntimeError("V116 result required")
    if int(v122.get("schemaVersion", -1)) != 122:
        raise RuntimeError("V122 utility result required")
    if int(v124.get("schemaVersion", -1)) != 124 or not bool(v124.get("validatedNewChampion")):
        raise RuntimeError("Validated V124 result required")

    policy = load_policy(v122)

    # Cheap consumed-V124 counterfactual using already stored outcomes.
    v124_rows = []
    for scheme in v124.get("schemes") or []:
        phase = float(scheme.get("phase"))
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            v124_rows.append(r)
    if len(v124_rows) != 320:
        raise RuntimeError(f"Expected 320 V124 rows, got {len(v124_rows)}")

    v124_v122_passes = sum(int(bool(r.get("v122Passed"))) for r in v124_rows)
    v124_guarded_passes = 0
    v124_gains = v124_losses = v124_guarded_rows = 0
    for r in v124_rows:
        rep = policy.get(structural_key(r))
        v122_pass = bool(r.get("v122Passed"))
        guarded = bool(r.get("v118Passed")) if phasecol3_selected_guard(r, rep) else v122_pass
        if phasecol3_selected_guard(r, rep):
            v124_guarded_rows += 1
        v124_guarded_passes += int(guarded)
        v124_gains += int(guarded and not v122_pass)
        v124_losses += int(v122_pass and not guarded)

    # Reverse-validate the frozen guard on the older consumed V116 family.
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Source candidate slots missing")

    names = sorted((source_rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in source_rows], dtype=np.float64)
    pf = np.asarray(v17.phase_features(source_rows), dtype=np.float64)
    interactions, _ = v112.build_phase_interactions(xb, names, pf)
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

    v116_v122_passes = 0
    v116_guarded_passes = 0
    v116_gains = v116_losses = v116_guarded_rows = 0

    print("GOMYWAY V127 PHASE_COL3 SELECTED-FOR-V112 GUARD REVERSE VALIDATION", flush=True)
    print("Guard frozen from consumed V124 diagnostic; V116 used only for reverse validation", flush=True)

    for idx, r in enumerate(rows, 1):
        key = structural_key(r)
        baseline = bool(r.get("v96Passed")) if dangerous_v118_exclusion(r) else bool(r.get("v115Passed"))
        rep = policy.get(key)

        if rep is None:
            v122_candidate = baseline
        else:
            phase = float(r["phase"])
            fold = int(r["fold"])
            model_bits = r.get("chosenModel") or {}
            radius = int(model_bits["pairRadius"])
            lam = float(model_bits["lambda"])
            ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures], dtype=np.int16)
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
            v122_candidate, _, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            v122_candidate = bool(v122_candidate)

        guarded = baseline if phasecol3_selected_guard(r, rep) else v122_candidate
        if phasecol3_selected_guard(r, rep):
            v116_guarded_rows += 1

        v116_v122_passes += int(v122_candidate)
        v116_guarded_passes += int(guarded)
        v116_gains += int(guarded and not v122_candidate)
        v116_losses += int(v122_candidate and not guarded)

        if idx % 40 == 0:
            print(f"heartbeat {idx}/320", flush=True)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V127")

    summary = {
        "guard": "within tight/revert-tight-to-anchor-low-dispersion/r4/lambda1 phase_col3 group, fall back to frozen V118 whenever selectedForV112 is true",
        "v124Consumed": {
            "v122Passes": int(v124_v122_passes),
            "guardedPasses": int(v124_guarded_passes),
            "gainsVsV122": int(v124_gains),
            "lossesVsV122": int(v124_losses),
            "netVsV122": int(v124_gains - v124_losses),
            "guardedRows": int(v124_guarded_rows),
        },
        "v116ReverseValidation": {
            "v122Passes": int(v116_v122_passes),
            "guardedPasses": int(v116_guarded_passes),
            "gainsVsV122": int(v116_gains),
            "lossesVsV122": int(v116_losses),
            "netVsV122": int(v116_gains - v116_losses),
            "guardedRows": int(v116_guarded_rows),
        },
    }

    out = {
        "schemaVersion": 127,
        "profileType": "phase-col3-selected-for-v112-guard-consumed-counterfactual-plus-reverse-validation",
        "summary": summary,
        "guardChosenFromConsumedV124Outcomes": True,
        "v116PreviouslyConsumed": True,
        "reverseValidationIsCorroborativeNotFreshConfirmation": True,
        "newReservedPhaseFamilyReferenced": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print("\nGOMYWAY V127 COMPLETE")
    print(f"Consumed V124: V122 {v124_v122_passes}/320 -> guarded {v124_guarded_passes}/320; +{v124_gains}/-{v124_losses} net={v124_gains-v124_losses:+d}")
    print(f"V124 guarded rows: {v124_guarded_rows}")
    print(f"Reverse V116: V122 {v116_v122_passes}/320 -> guarded {v116_guarded_passes}/320; +{v116_gains}/-{v116_losses} net={v116_gains-v116_losses:+d}")
    print(f"V116 guarded rows: {v116_guarded_rows}")
    print("Guard chosen from consumed V124 outcomes: True")
    print("New reserved phase family referenced: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
