from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_global_q020_unseen_phase_confirmation_v28 as v28

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V57_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v56-reserved-1over64-confirmation-v57.json"
V71_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v70-bottleneck-representation-ablation-v71.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v71-phase-feature-group-ablation-v72.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v71-phase-feature-group-ablation-v72-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
ANCHOR_Q = float(v28.FROZEN_Q)
BOTTLENECK_PHASES = (0.328125, 0.703125, 0.984375)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v57 = json.loads(V57_PATH.read_text(encoding="utf-8"))
    v71 = json.loads(V71_PATH.read_text(encoding="utf-8"))

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    xp = np.asarray(v17.phase_features(rows), dtype=np.float64)
    if xp.ndim != 2 or xp.shape[0] != xb.shape[0]:
        raise RuntimeError("Unexpected phase feature shape")

    # Diagnostic-only coarse grouping: each phase-feature column is tested independently
    # and cumulatively against the frozen source representation. No held-out labels are used
    # to choose a production architecture; all outcomes are tainted for selection.
    reps: dict[str, np.ndarray] = {"base": xb, "fullPhase": np.concatenate([xb, xp], axis=1)}
    for j in range(xp.shape[1]):
        reps[f"basePlusPhaseCol{j}"] = np.concatenate([xb, xp[:, [j]]], axis=1)
    if xp.shape[1] > 1:
        for k in range(1, xp.shape[1] + 1):
            reps[f"basePlusFirst{k}PhaseCols"] = np.concatenate([xb, xp[:, :k]], axis=1)

    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    v57_by = {}
    for s in v57.get("schemes") or []:
        phase = float(s["phase"])
        if phase not in BOTTLENECK_PHASES:
            continue
        for f in s.get("folds") or []:
            v57_by[(phase, int(f["fold"]))] = f

    results = []
    pass_counts = {name: 0 for name in reps}

    for phase in BOTTLENECK_PHASES:
        lo, hi = int(np.min(measures)), int(np.max(measures))
        ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, float(phase)) for m in measures], dtype=np.int16)
        for fold in range(OUTER_FOLDS):
            frozen = v57_by[(phase, fold)]
            chosen_model = frozen["chosenModel"]
            radius = int(chosen_model["pairRadius"])
            lam = float(chosen_model["lambda"])
            test = ids == fold
            train = ~test

            row: dict[str, Any] = {"phase": phase, "fold": fold, "pairRadius": radius, "lambda": lam, "representations": {}}
            for name, x in reps.items():
                model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
                scores = v2.scores_for(x[test], model)
                passed, lift, held, base = v17.pass_at_q(scores, y[test], ANCHOR_Q)
                row["representations"][name] = {
                    "passed": bool(passed),
                    "heldoutPrecisionLift": round(float(lift), 2),
                    "heldoutCandidate": held,
                    "heldoutBase": base,
                }
                pass_counts[name] += int(passed)
            results.append(row)

    ranked = sorted(pass_counts.items(), key=lambda kv: (-kv[1], kv[0]))
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V72")

    out = {
        "schemaVersion": 72,
        "profileType": "v71-phase-feature-column-ablation-diagnostic",
        "diagnosticScope": "already-exposed-v57-bottleneck-phases-only",
        "phaseFeatureColumnCount": int(xp.shape[1]),
        "passCounts": pass_counts,
        "rankedRepresentations": ranked,
        "rows": results,
        "v71Summary": {
            "baseRepresentationPasses": v71.get("baseRepresentationPasses"),
            "phaseAugmentedRepresentationPasses": v71.get("phaseAugmentedRepresentationPasses"),
            "flipCounts": v71.get("flipCounts"),
        },
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 72,
        "phaseFeatureColumnCount": int(xp.shape[1]),
        "passCounts": pass_counts,
        "rankedRepresentations": ranked,
        "diagnosticOutcomesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over128OddNumeratorPhasesReferenced": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V71 PHASE FEATURE GROUP ABLATION V72 COMPLETE")
    print("Phase feature columns:", xp.shape[1])
    print("Pass counts:")
    for name, count in ranked:
        print(" ", name, count, "/", len(results))
    print("Diagnostic outcomes tainted for selection: True")
    print("New reserved 1/128 odd-numerator phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Validated new champion: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
