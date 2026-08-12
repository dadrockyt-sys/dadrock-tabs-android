from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_rhythm24_v17_fixed_policy_boundary_stress_v18 as v18
import benchmark_gomyway_3676_patch_rhythm24_quarter_phase_training_q_selector_v20 as v20

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v20-remaining-failure-anatomy-v21.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-v20-remaining-failure-anatomy-v21-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PHASE = 0.25
Q_SWEEP = (0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.075, 0.10, 0.125, 0.15)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_rank(scores: np.ndarray, y: np.ndarray) -> float:
    pos = np.flatnonzero(y)
    neg = np.flatnonzero(~y)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for i in pos:
        for j in neg:
            if scores[i] > scores[j]:
                wins += 1.0
            elif scores[i] == scores[j]:
                wins += 0.5
    return wins / float(len(pos) * len(neg))


def score_geometry(scores: np.ndarray, selected_q: float) -> dict[str, float]:
    s = np.asarray(scores, dtype=np.float64)
    if len(s) == 0:
        return {}
    order = np.sort(s)[::-1]
    n = len(order)
    k = max(1, int(np.ceil(selected_q * n)))
    cutoff = float(order[min(k - 1, n - 1)])
    next_score = float(order[k]) if k < n else cutoff
    top5 = float(np.mean(order[: max(1, int(np.ceil(0.05 * n)))]))
    top10 = float(np.mean(order[: max(1, int(np.ceil(0.10 * n)))]))
    return {
        "scoreStd": float(np.std(s)),
        "scoreMedian": float(np.median(s)),
        "scoreP90": float(np.quantile(s, 0.90)),
        "scoreP95": float(np.quantile(s, 0.95)),
        "selectedCutoff": cutoff,
        "boundaryGap": cutoff - next_score,
        "top5VsTop10Gap": top5 - top10,
        "upperTailSpread": float(np.quantile(s, 0.95) - np.median(s)),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in names] for r in rows],
        dtype=np.float64,
    )
    x = np.concatenate([x_base, v20.phase_features(rows)], axis=1)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray(
        [v18.phased_fold(int(m), lo, hi, OUTER_FOLDS, PHASE) for m in measures],
        dtype=np.int16,
    )

    print("Starting V21 V20 remaining quarter-phase failure anatomy", flush=True)
    print("Diagnostic only: no selector changes and no production changes", flush=True)

    results: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for fold in range(OUTER_FOLDS):
        print(f"quarterPhase0.25: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test

        chosen = v5.choose_model(x[train], y[train], measures[train])
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        base_q = float(chosen["tailQuantile"])
        selected_q, selector = v20.choose_q_train_only_quarter_phase(
            x[train], y[train], measures[train], radius, lam, base_q
        )

        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)
        passed, lift, held, base = v20.pass_at_q(scores, y[test], selected_q)

        sweep = []
        for q in Q_SWEEP:
            qp, qlift, qheld, _ = v20.pass_at_q(scores, y[test], q)
            sweep.append({
                "q": float(q),
                "passed": bool(qp),
                "lift": round(float(qlift), 2),
                "candidate": qheld,
            })
        passing_points = [s for s in sweep if s["passed"]]
        best_pass = passing_points[0] if passing_points else None

        row = {
            "phase": PHASE,
            "fold": fold,
            "baseQ": base_q,
            "selectedQ": float(selected_q),
            "selector": selector,
            "auc": round(float(auc_rank(scores, y[test])), 6),
            "scoreGeometry": score_geometry(scores, selected_q),
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(float(lift), 2),
            "passed": bool(passed),
            "qSweep": sweep,
            "operatingPointRecoverable": bool(passing_points),
            "bestPassingSweepPoint": best_pass,
        }
        results.append(row)
        if not passed:
            failures.append(row)

        print(
            f"  baseQ={base_q} chosenQ={selected_q} held={held['true']}/{held['false']} "
            f"lift={round(lift,2)} auc={row['auc']} pass={passed}",
            flush=True,
        )

    all_recoverable = bool(failures) and all(bool(f["operatingPointRecoverable"]) for f in failures)
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V21")

    output = {
        "schemaVersion": 21,
        "profileType": "36.76-rhythm24-v20-remaining-quarter-phase-failure-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "phase": PHASE,
        "failureCount": len(failures),
        "failures": failures,
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "results": results,
        "nextTarget": (
            "freeze-v20-and-test-unseen-phase-only-if-no-new-posthoc-selector-needed"
            if not failures else
            "diagnose-ranking-representation" if not all_recoverable else
            "seek-training-only-signal-without-adding-posthoc-q"
        ),
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseQ": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 21,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "failureCount": len(failures),
        "allFailuresOperatingPointRecoverable": all_recoverable,
        "nextTarget": output["nextTarget"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 V20 REMAINING FAILURE ANATOMY V21 COMPLETE")
    print("Remaining V20 failures:", len(failures))
    for f in failures:
        print("Failure: quarterPhase0.25 fold", f["fold"], "auc", f["auc"], "selectedQ", f["selectedQ"])
        print("  Operating-point recoverable:", f["operatingPointRecoverable"])
        print("  Best passing sweep point:", f["bestPassingSweepPoint"])
        print("  Score geometry:", f["scoreGeometry"])
    print("All failures operating-point recoverable:", all_recoverable)
    print("Next target:", output["nextTarget"])
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
