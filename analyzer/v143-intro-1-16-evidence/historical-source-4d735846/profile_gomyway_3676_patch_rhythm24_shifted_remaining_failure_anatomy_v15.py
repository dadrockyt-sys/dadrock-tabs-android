from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-shifted-remaining-failure-anatomy-v15.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-rhythm24-shifted-remaining-failure-anatomy-v15-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PERIODS = (2, 4)
Q_SWEEP = (0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def phase_features(rows: list[dict[str, Any]]) -> tuple[np.ndarray, list[str]]:
    out = []
    names = []
    for p in PERIODS:
        names.extend([f"rhythmPhaseSinP{p}", f"rhythmPhaseCosP{p}"])
    for r in rows:
        step = int(r["step"])
        vals = []
        for p in PERIODS:
            a = 2.0 * math.pi * (step % p) / float(p)
            vals.extend([math.sin(a), math.cos(a)])
        out.append(vals)
    return np.asarray(out, dtype=np.float64), names


def auc_rank(y: np.ndarray, scores: np.ndarray) -> float:
    y = np.asarray(y, dtype=bool)
    scores = np.asarray(scores, dtype=np.float64)
    pos = scores[y]
    neg = scores[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    wins = 0.0
    for p in pos:
        wins += float(np.sum(p > neg)) + 0.5 * float(np.sum(p == neg))
    return wins / float(len(pos) * len(neg))


def score_geometry(scores: np.ndarray, q: float) -> dict[str, float]:
    s = np.sort(np.asarray(scores, dtype=np.float64))[::-1]
    n = len(s)
    k = max(1, int(math.ceil(q * n)))
    boundary = float(s[min(k - 1, n - 1)])
    next_score = float(s[k]) if k < n else boundary
    top5 = float(np.mean(s[: max(1, int(math.ceil(0.05 * n)))]))
    top10 = float(np.mean(s[: max(1, int(math.ceil(0.10 * n)))]))
    upper = s[: max(2, int(math.ceil(0.20 * n)))]
    return {
        "selectedCount": int(k),
        "boundaryScore": boundary,
        "boundaryGap": boundary - next_score,
        "top5VsTop10Gap": top5 - top10,
        "upperTailSpread": float(np.std(upper)),
        "scoreStd": float(np.std(s)),
    }


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows or tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source not anchored to frozen 36.76 champion")

    base_names = sorted((rows[0].get("features") or {}).keys())
    x_base = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in base_names] for r in rows], dtype=np.float64)
    x_phase, phase_names = phase_features(rows)
    x = np.concatenate([x_base, x_phase], axis=1)
    feature_names = base_names + phase_names

    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)

    results = []
    failures = []
    for fold in range(OUTER_FOLDS):
        print(f"shiftedWindow: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        chosen = v5.choose_model(x[train], y[train], measures[train])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"]))
        scores = v2.scores_for(x[test], model)
        q = float(chosen["tailQuantile"])
        held = v1.select_top_fraction(scores, y[test], q)
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0

        sweep = []
        recoverable = False
        best = None
        for qq in Q_SWEEP:
            h = v1.select_top_fraction(scores, y[test], qq)
            ll = float(h["precision"]) - float(base["precision"])
            pp = h["true"] > 0 and ll >= 5.0
            recoverable = recoverable or pp
            item = {"q": qq, "true": h["true"], "false": h["false"], "selectedPct": h["selectedPct"], "precision": h["precision"], "lift": round(ll, 2), "passed": bool(pp)}
            sweep.append(item)
            key = (int(pp), ll, -abs(qq - q))
            if best is None or key > best[0]:
                best = (key, item)

        coef = np.asarray(model["coef"], dtype=np.float64)
        phase_weights = []
        for j, name in enumerate(feature_names):
            if name.startswith("rhythmPhase"):
                phase_weights.append({"feature": name, "weight": round(float(coef[j]), 6)})

        row = {
            "scheme": "shiftedWindow",
            "fold": fold,
            "passed": bool(passed),
            "chosen": chosen,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "heldoutAuc": round(auc_rank(y[test], scores), 6),
            "scoreGeometry": score_geometry(scores, q),
            "phaseWeights": phase_weights,
            "operatingPointRecoverable": bool(recoverable),
            "bestSweepPoint": best[1],
            "qSweep": sweep,
        }
        results.append(row)
        if not passed:
            failures.append(row)
        print(f"  q={q} held={held['true']}/{held['false']} precision={held['precision']} base={base['precision']} lift={round(lift,2)} auc={row['heldoutAuc']} pass={passed}", flush=True)

    if len(failures) != 1:
        print(f"WARNING expected one shifted failure from V14 winner, observed {len(failures)}", flush=True)

    if failures:
        f = failures[0]
        if f["operatingPointRecoverable"]:
            failure_type = "operatingPointRecoverable"
            next_target = "training-only-q-selector-for-single-shifted-residual"
        elif f["heldoutAuc"] >= 0.55:
            failure_type = "rankingHasSignalButTailNotRecoverable"
            next_target = "training-only-rank-tail-shape-selector"
        else:
            failure_type = "rankingSeparationFailure"
            next_target = "new-rhythm-context-information-for-single-shifted-residual"
    else:
        failure_type = "none"
        next_target = "lock-rhythm24-15-of-15"

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V15")

    output = {
        "schemaVersion": 15,
        "profileType": "36.76-rhythm24-single-shifted-residual-failure-anatomy",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "periods": list(PERIODS),
        "shiftedPasses": sum(int(r["passed"]) for r in results),
        "shiftedTotal": len(results),
        "remainingFailures": len(failures),
        "failureType": failure_type,
        "nextTarget": next_target,
        "shiftedWindow": results,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({"schemaVersion": 15, "output": str(OUTPUT_PATH.relative_to(ROOT)), "remainingFailures": len(failures), "failureType": failure_type, "nextTarget": next_target, "validatedNewChampion": False, "productionPromotionAllowed": False}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 RHYTHM24 SHIFTED REMAINING FAILURE ANATOMY V15 COMPLETE")
    print("Shifted passes:", output["shiftedPasses"], "/", output["shiftedTotal"])
    print("Remaining failures:", len(failures))
    if failures:
        f = failures[0]
        print("Failing shifted fold:", f["fold"])
        print("Failure AUC:", f["heldoutAuc"])
        print("Chosen q:", f["chosen"]["tailQuantile"])
        print("Operating-point recoverable:", f["operatingPointRecoverable"])
        print("Best sweep point:", f["bestSweepPoint"])
        print("Score geometry:", f["scoreGeometry"])
        print("Phase weights:", f["phaseWeights"])
    print("Failure type:", failure_type)
    print("Next target:", next_target)
    print("Validated new champion: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
