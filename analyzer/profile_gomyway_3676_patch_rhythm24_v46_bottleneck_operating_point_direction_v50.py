from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_shifted_only_q_selector_nested_cv_v17 as v17
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V46_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v45-strict-support-only-broaden-v46.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-operating-point-direction-v50.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v46-bottleneck-operating-point-direction-v50-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
BOTTLENECK_PHASE = 0.09375
ANCHOR_Q = 0.20
# Diagnostic-only sweep on already exposed held-out bottleneck failures.
# These q values are tainted and MUST NOT be copied into a future challenger.
DIAGNOSTIC_QS = tuple(round(float(q), 3) for q in np.arange(0.05, 0.401, 0.025))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(source.get("candidateSlots") or [])
    if not rows or tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    v46 = json.loads(V46_PATH.read_text(encoding="utf-8"))
    failed_folds = []
    for scheme in v46.get("schemes", []):
        if abs(float(scheme.get("phase")) - BOTTLENECK_PHASE) > 1e-12:
            continue
        for fold in scheme.get("folds", []):
            if not bool(fold.get("passed")):
                failed_folds.append(int(fold.get("fold")))
    failed_folds = sorted(set(failed_folds))
    if not failed_folds:
        raise RuntimeError("No V46 failures found on bottleneck phase")

    names = sorted((rows[0].get("features") or {}).keys())
    xb = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows], dtype=np.float64)
    x = np.concatenate([xb, v17.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)

    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, BOTTLENECK_PHASE) for m in measures], dtype=np.int16)

    diagnostics = []
    direction_counts = {"onlyBroaderThanAnchorRecovers": 0, "onlyTighterThanAnchorRecovers": 0,
                        "bothDirectionsRecover": 0, "noRecoveryInSweep": 0, "anchorAlreadyPasses": 0}

    for fold in failed_folds:
        print(f"phase={BOTTLENECK_PHASE} failed outer fold {fold + 1}/{OUTER_FOLDS} diagnostic sweep ...", flush=True)
        test = ids == fold
        train = ~test
        chosen_model = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen_model["pairRadius"])
        lam = float(chosen_model["lambda"])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)

        q_rows = []
        passing_qs = []
        for q in DIAGNOSTIC_QS:
            passed, lift, held, base = v17.pass_at_q(scores, y[test], float(q))
            q_rows.append({"q": float(q), "passed": bool(passed), "lift": round(float(lift), 2),
                           "held": held, "base": base})
            if passed:
                passing_qs.append(float(q))

        anchor = min(q_rows, key=lambda r: abs(float(r["q"]) - ANCHOR_Q))
        broader = [q for q in passing_qs if q > ANCHOR_Q + 1e-12]
        tighter = [q for q in passing_qs if q < ANCHOR_Q - 1e-12]
        if bool(anchor["passed"]):
            direction = "anchorAlreadyPasses"
        elif broader and tighter:
            direction = "bothDirectionsRecover"
        elif broader:
            direction = "onlyBroaderThanAnchorRecovers"
        elif tighter:
            direction = "onlyTighterThanAnchorRecovers"
        else:
            direction = "noRecoveryInSweep"
        direction_counts[direction] += 1

        diagnostics.append({
            "phase": BOTTLENECK_PHASE,
            "fold": int(fold),
            "chosenModel": chosen_model,
            "anchorQ": ANCHOR_Q,
            "anchorPassed": bool(anchor["passed"]),
            "recoveryDirection": direction,
            "passingQCount": len(passing_qs),
            "passingQRange": ([min(passing_qs), max(passing_qs)] if passing_qs else None),
            "broaderPassingQCount": len(broader),
            "tighterPassingQCount": len(tighter),
            "qSweep": q_rows,
        })

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V50")

    out = {
        "schemaVersion": 50,
        "profileType": "v46-bottleneck-operating-point-direction-diagnostic",
        "diagnosticScope": "already-exposed-v46-bottleneck-failures-only",
        "bottleneckPhase": BOTTLENECK_PHASE,
        "failedFolds": failed_folds,
        "anchorQ": ANCHOR_Q,
        "diagnosticQGrid": list(DIAGNOSTIC_QS),
        "directionCounts": direction_counts,
        "diagnostics": diagnostics,
        "heldoutLabelsUsedForDiagnosticSweep": True,
        "diagnosticQValuesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 50,
        "bottleneckPhase": BOTTLENECK_PHASE,
        "failedFolds": failed_folds,
        "directionCounts": direction_counts,
        "heldoutLabelsUsedForDiagnosticSweep": True,
        "diagnosticQValuesTaintedForSelection": True,
        "newTuningPerformed": False,
        "newReserved1over64OddPhasesReferenced": False,
        "reservedUntouchedPhasesConsumed": False,
        "validatedNewChampion": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V46 BOTTLENECK OPERATING-POINT DIRECTION V50 COMPLETE")
    print("Failed folds:", failed_folds)
    print("Recovery direction counts:", direction_counts)
    for d in diagnostics:
        print("Fold", d["fold"], "direction:", d["recoveryDirection"], "passing q range:", d["passingQRange"])
    print("Diagnostic q values tainted for selection: True")
    print("New reserved 1/64 odd phases referenced: False")
    print("New tuning performed: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
