from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
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
V119_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v118-reserved-3mod16-over1024-confirmation-v119.json"
V120_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v119-failure-anatomy-v120.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v120-failure-representation-rescue-ceiling-v121.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v120-failure-representation-rescue-ceiling-v121-manifest.json"

OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
ALT_REPS = ("base", "phase_col3", "full_phase", "cosine", "v112_interactions")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v119 = json.loads(V119_PATH.read_text(encoding="utf-8"))
    v120 = json.loads(V120_PATH.read_text(encoding="utf-8"))
    if int(v119.get("schemaVersion", -1)) != 119 or not bool(v119.get("validatedNewChampion")):
        raise RuntimeError("Validated V119 output required")
    if int(v119.get("v118Passes", -1)) != 293 or int(v119.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V119 must match frozen 293/320 V118 confirmation")
    if int(v120.get("schemaVersion", -1)) != 120:
        raise RuntimeError("V120 failure anatomy required")

    failures = list(v120.get("failureDetail") or [])
    if len(failures) != 27:
        raise RuntimeError(f"Expected 27 exposed V118 failures, got {len(failures)}")

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Source candidate slots missing")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
    pf = np.asarray(v17.phase_features(rows), dtype=np.float64)
    x_base = xb
    x_phase_col3 = np.concatenate([xb, pf[:, [3]]], axis=1)
    x_full = np.concatenate([xb, pf], axis=1)
    x_cos = np.concatenate([xb, pf[:, [1, 3]]], axis=1)
    interactions, interaction_names = v112.build_phase_interactions(xb, names, pf)
    x_v112 = np.concatenate([x_cos, interactions], axis=1)
    matrices = {
        "base": x_base,
        "phase_col3": x_phase_col3,
        "full_phase": x_full,
        "cosine": x_cos,
        "v112_interactions": x_v112,
    }

    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("GOMYWAY V121 EXPOSED V119 FAILURE REPRESENTATION RESCUE CEILING", flush=True)
    print("Evaluating only the 27 already-exposed V118 failures; no untouched reserve used", flush=True)

    rescue_counts = Counter()
    rescue_patterns = Counter()
    rescue_by_structure = defaultdict(Counter)
    detail = []

    for n, fr in enumerate(failures, 1):
        phase = float(fr["phase"])
        fold = int(fr["fold"])
        radius = int(fr["pairRadius"])
        lam = float(fr["lambda"])

        ids = np.asarray(
            [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, phase) for m in measures],
            dtype=np.int16,
        )
        train = ids != fold
        test = ids == fold

        # Reconstruct the frozen candidate q from training-only selector state in V119.
        old_q = None
        selector = None
        for scheme in v119.get("schemes") or []:
            if abs(float(scheme.get("phase")) - phase) > 1e-12:
                continue
            for r in scheme.get("folds") or []:
                if int(r.get("fold")) == fold:
                    old_q = float(r.get("originalTrainingOnlyQ"))
                    selector = r.get("selector") or {}
                    break
            if old_q is not None:
                break
        if old_q is None:
            raise RuntimeError(f"Could not reconstruct V119 row phase={phase} fold={fold}")

        candidate_q, decision, _ = v80.selected_q({"outerQ": old_q, "selector": selector})
        q_to_use = candidate_q if fr.get("originalQBucket") == "tight" else ANCHOR_Q
        if fr.get("originalQBucket") == "broad" and fr.get("v96Decision") == "keep-broad-low-dispersion":
            q_to_use = candidate_q

        rep_pass = {}
        rep_lift = {}
        for rep in ALT_REPS:
            x = matrices[rep]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            rep_pass[rep] = bool(passed)
            rep_lift[rep] = round(float(lift), 4)
            if passed:
                rescue_counts[rep] += 1

        rescued_by = [rep for rep in ALT_REPS if rep_pass[rep]]
        bits = "|".join(f"{rep}={int(rep_pass[rep])}" for rep in ALT_REPS)
        rescue_patterns[bits] += 1
        structure = (
            str(fr.get("originalQBucket")),
            str(fr.get("v96Decision")),
            radius,
            lam,
        )
        for rep in rescued_by:
            rescue_by_structure[structure][rep] += 1

        detail.append({
            **fr,
            "reconstructedDecision": decision,
            "qUsed": float(q_to_use),
            "representationPasses": rep_pass,
            "representationLift": rep_lift,
            "rescuedBy": rescued_by,
        })
        print(f"{n:02d}/27 phase={phase:.7f} fold={fold} rescuedBy={rescued_by}", flush=True)

    oracle_rescued = sum(bool(r["rescuedBy"]) for r in detail)
    remaining = len(detail) - oracle_rescued
    oracle_score = 293 + oracle_rescued

    structure_rows = []
    for structure, counts in rescue_by_structure.items():
        structure_rows.append({
            "originalQBucket": structure[0],
            "v96Decision": structure[1],
            "pairRadius": structure[2],
            "lambda": structure[3],
            "rescuesByRepresentation": dict(counts),
        })
    structure_rows.sort(
        key=lambda r: -max((r["rescuesByRepresentation"] or {"": 0}).values())
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V121")

    summary = {
        "exposedFailureRows": len(detail),
        "frozenV118Passes": 293,
        "frozenV118ScorePercent": 91.5625,
        "rescuedFailuresByRepresentation": {rep: int(rescue_counts[rep]) for rep in ALT_REPS},
        "oracleUnionRescuedFailures": int(oracle_rescued),
        "oracleUnionPasses": int(oracle_score),
        "oracleUnionScorePercent": round(100.0 * oracle_score / 320.0, 4),
        "remainingFailuresEvenWithPerFailureRepresentationOracle": int(remaining),
        "failureRescuePatterns": dict(rescue_patterns),
    }

    out = {
        "schemaVersion": 121,
        "profileType": "exposed-v119-failure-only-representation-rescue-ceiling-diagnostic",
        "summary": summary,
        "structuralRescueCounts": structure_rows,
        "failureDetail": detail,
        "derivedInteractionFeatures": interaction_names,
        "evaluatesOnlyAlreadyExposedV119Failures": True,
        "doesNotMeasureRepresentationLossesOnV118Passes": True,
        "heldoutLabelsUsedForDiagnosisOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(
        json.dumps({k: v for k, v in out.items() if k != "failureDetail"}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nGOMYWAY V121 FAILURE REPRESENTATION RESCUE CEILING COMPLETE")
    print("Frozen V118: 293/320 = 91.5625%")
    for rep in ALT_REPS:
        print(f"{rep}: rescues={rescue_counts[rep]}/27")
    print(f"Perfect per-failure representation oracle: {oracle_score}/320 = {100.0*oracle_score/320.0:.4f}%")
    print(f"Failures not rescued by ANY tested representation: {remaining}")
    print("\n=== FAILURE RESCUE PATTERNS ===")
    for pattern, count in rescue_patterns.most_common():
        print(pattern, count)
    print("\n=== STRUCTURAL RESCUE COUNTS ===")
    for row in structure_rows:
        print(row)
    print("\nImportant: V121 tests exposed failures only and does NOT measure losses on the 293 V118 passes")
    print("New reserved phase family referenced: False")
    print("Candidate policy changed: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
