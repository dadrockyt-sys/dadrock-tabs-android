from __future__ import annotations

import hashlib
import json
from collections import defaultdict
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
V128_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v127-guarded-v122-reserved-7mod16-over1024-confirmation-v128.json"
V130_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v129-failure-representation-rescue-ceiling-v130.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v130-structural-representation-utility-v131.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v130-structural-representation-utility-v131-manifest.json"

OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
REPRESENTATIONS = ("base", "phase_col3", "full_phase", "cosine", "v112_interactions")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def model_bits(row: dict) -> tuple[int, float]:
    model = row.get("chosenModel") or {}
    return int(model["pairRadius"]), float(model["lambda"])


def structural_key(row: dict) -> tuple[str, str, int, float]:
    radius, lam = model_bits(row)
    return (
        str(row.get("originalQBucket")),
        str(row.get("v96Decision")),
        radius,
        lam,
    )


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    v128 = json.loads(V128_PATH.read_text(encoding="utf-8"))
    v130 = json.loads(V130_PATH.read_text(encoding="utf-8"))
    if int(v128.get("schemaVersion", -1)) != 128 or not bool(v128.get("validatedNewChampion")):
        raise RuntimeError("Validated V128 output required")
    if int(v128.get("v128Passes", -1)) != 309 or int(v128.get("foldsTotal", -1)) != 320:
        raise RuntimeError("V128 must match frozen 309/320 guarded champion")
    if int(v130.get("schemaVersion", -1)) != 130:
        raise RuntimeError("V130 rescue-ceiling diagnostic required")

    # Restrict interventions to representations that rescued at least one of
    # the 11 already-exposed V128 failures in that exact structural group.
    candidates: dict[tuple[str, str, int, float], set[str]] = defaultdict(set)
    for row in v130.get("structuralRescueCounts") or []:
        key = (
            str(row.get("originalQBucket")),
            str(row.get("v96Decision")),
            int(row.get("pairRadius")),
            float(row.get("lambda")),
        )
        for rep, rescues in (row.get("rescuesByRepresentation") or {}).items():
            if int(rescues) > 0 and rep in REPRESENTATIONS:
                candidates[key].add(rep)
    if not candidates:
        raise RuntimeError("V130 supplied no structural rescue candidates")

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

    rows: list[dict] = []
    for scheme in v128.get("schemes") or []:
        phase = float(scheme["phase"])
        for r0 in scheme.get("folds") or []:
            r = dict(r0)
            r.setdefault("phase", phase)
            rows.append(r)
    if len(rows) != 320:
        raise RuntimeError(f"Expected 320 saved V128 rows, got {len(rows)}")

    stats = {
        (key, rep): {"rows": 0, "baselinePasses": 0, "candidatePasses": 0, "gains": 0, "losses": 0}
        for key, reps in candidates.items()
        for rep in reps
    }
    row_results: list[dict] = []

    print("GOMYWAY V131 STRUCTURAL REPRESENTATION UTILITY DIAGNOSTIC", flush=True)
    print("Evaluating only V130-motivated structural representation switches on the already-consumed V128 320 rows", flush=True)
    print(f"Structural groups: {len(candidates)}; interventions: {len(stats)}", flush=True)

    for idx, r in enumerate(rows, 1):
        key = structural_key(r)
        reps = candidates.get(key)
        if not reps:
            continue

        phase = float(r["phase"])
        fold = int(r["fold"])
        radius, lam = model_bits(r)
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

        baseline = bool(r.get("v128Passed"))
        rep_results = {}
        for rep in sorted(reps):
            x = matrices[rep]
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            scores = v2.scores_for(x[test], model)
            passed, lift, _, _ = v17.pass_at_q(scores, y[test], q_to_use)
            passed = bool(passed)
            s = stats[(key, rep)]
            s["rows"] += 1
            s["baselinePasses"] += int(baseline)
            s["candidatePasses"] += int(passed)
            s["gains"] += int(passed and not baseline)
            s["losses"] += int(baseline and not passed)
            rep_results[rep] = {"passed": passed, "lift": round(float(lift), 4)}

        row_results.append({
            "phase": phase,
            "fold": fold,
            "structuralKey": {
                "originalQBucket": key[0],
                "v96Decision": key[1],
                "pairRadius": key[2],
                "lambda": key[3],
            },
            "baselineV128Passed": baseline,
            "baselineFinalRepresentation": r.get("finalRepresentation"),
            "candidateRepresentations": rep_results,
        })
        if idx % 25 == 0:
            print(f"heartbeat saved-row {idx}/320", flush=True)

    intervention_rows = []
    for (key, rep), s in stats.items():
        net = int(s["gains"] - s["losses"])
        intervention_rows.append({
            "originalQBucket": key[0],
            "v96Decision": key[1],
            "pairRadius": key[2],
            "lambda": key[3],
            "representation": rep,
            **{k: int(v) for k, v in s.items()},
            "net": net,
        })
    intervention_rows.sort(key=lambda z: (-z["net"], -z["gains"], z["losses"], -z["rows"], z["representation"]))

    grouped: dict[tuple[str, str, int, float], list[dict]] = defaultdict(list)
    for row in intervention_rows:
        grouped[(row["originalQBucket"], row["v96Decision"], row["pairRadius"], row["lambda"])].append(row)

    best_by_group = []
    for key, options in grouped.items():
        best = sorted(options, key=lambda z: (-z["net"], -z["gains"], z["losses"], z["representation"]))[0]
        if int(best["net"]) > 0:
            best_by_group.append(best)

    # Structural groups are disjoint. One positive intervention per group can
    # therefore be combined arithmetically without double-counting rows.
    combined_gains = sum(int(r["gains"]) for r in best_by_group)
    combined_losses = sum(int(r["losses"]) for r in best_by_group)
    combined_passes = 309 + combined_gains - combined_losses

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V131")

    summary = {
        "foldsTotal": 320,
        "frozenV128Passes": 309,
        "frozenV128ScorePercent": 96.5625,
        "structuralGroupsEvaluated": len(candidates),
        "interventionsEvaluated": len(intervention_rows),
        "positiveBestPerGroupCount": len(best_by_group),
        "provisionalCombinedGains": int(combined_gains),
        "provisionalCombinedLosses": int(combined_losses),
        "provisionalCombinedNet": int(combined_gains - combined_losses),
        "provisionalCombinedPasses": int(combined_passes),
        "provisionalCombinedScorePercent": round(100.0 * combined_passes / 320.0, 4),
    }
    out = {
        "schemaVersion": 131,
        "profileType": "consumed-v128-structural-representation-gain-loss-utility-diagnostic",
        "summary": summary,
        "interventionUtility": intervention_rows,
        "positiveBestPerStructuralGroup": best_by_group,
        "rowResults": row_results,
        "derivedInteractionFeatures": interaction_names,
        "motivatedOnlyByV130ExposedFailureRescues": True,
        "evaluatesOnAlreadyConsumedV128Rows": True,
        "heldoutLabelsUsedForDiagnosisAndDevelopmentOnly": True,
        "newReservedPhaseFamilyReferenced": False,
        "newTuningPerformed": False,
        "candidatePolicyChanged": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(
        json.dumps({k: v for k, v in out.items() if k != "rowResults"}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("\nGOMYWAY V131 STRUCTURAL REPRESENTATION UTILITY COMPLETE")
    print("Frozen V128: 309/320 = 96.5625%")
    print("\n=== TOP INDIVIDUAL INTERVENTIONS ===")
    for row in intervention_rows[:20]:
        print(row)
    print("\n=== POSITIVE BEST PER STRUCTURAL GROUP ===")
    for row in best_by_group:
        print(row)
    print(
        f"\nProvisional disjoint combined policy: {combined_passes}/320 = "
        f"{100.0*combined_passes/320.0:.4f}% gains={combined_gains} losses={combined_losses} net={combined_gains-combined_losses:+d}"
    )
    print("Important: V131 is development-only on consumed V128 outcomes and is NOT a validated challenger")
    print("New reserved phase family referenced: False")
    print("Candidate policy changed: False")
    print("Validated new champion: False")
    print("Protected candidate unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
