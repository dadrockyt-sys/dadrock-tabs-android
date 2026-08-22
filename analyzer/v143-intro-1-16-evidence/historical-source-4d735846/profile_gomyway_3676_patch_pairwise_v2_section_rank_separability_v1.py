from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-section-rank-separability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-section-rank-separability-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
Q_GRID = [0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20]
EPS = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def auc_from_scores(scores: np.ndarray, y: np.ndarray) -> float:
    pos = scores[y]
    neg = scores[~y]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    # Exact pairwise concordance; candidate sections are small enough for this diagnostic.
    diff = pos[:, None] - neg[None, :]
    wins = float(np.sum(diff > 0))
    ties = float(np.sum(diff == 0))
    return (wins + 0.5 * ties) / float(diff.size)


def separation_stats(scores: np.ndarray, y: np.ndarray) -> dict[str, Any]:
    pos = scores[y]
    neg = scores[~y]
    pos_med = float(np.median(pos)) if len(pos) else 0.0
    neg_med = float(np.median(neg)) if len(neg) else 0.0
    pooled = float(np.std(scores))
    effect = (pos_med - neg_med) / max(pooled, EPS)
    return {
        "auc": round(auc_from_scores(scores, y), 5),
        "positiveMedianScore": round(pos_med, 6),
        "negativeMedianScore": round(neg_med, 6),
        "medianScoreGap": round(pos_med - neg_med, 6),
        "medianGapStdUnits": round(effect, 5),
    }


def main() -> None:
    if not V2_PATH.exists():
        raise RuntimeError("V2 pairwise benchmark output missing; run V2 first")
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    bench = json.loads(V2_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v1.contiguous_fold(int(m), lo, hi, 5) for m in measures], dtype=np.int16)

    section_rows = list(bench.get("section") or [])
    by_fold = {int(r.get("fold")): r for r in section_rows}
    if len(by_fold) != 5:
        raise RuntimeError(f"Expected 5 V2 section folds, found {len(by_fold)}")

    diagnostics: list[dict[str, Any]] = []
    for fold in range(5):
        print(f"section separability fold {fold + 1}/5 ...", flush=True)
        test = ids == fold
        train = ~test
        saved = by_fold[fold]
        chosen = dict(saved.get("chosen") or {})
        radius = int(chosen["pairRadius"])
        lam = float(chosen["lambda"])
        chosen_q = float(chosen["tailQuantile"])

        # Detection-side model is fit from outer-training data only.
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        scores = v2.scores_for(x[test], model)

        # Everything below is downstream grading/diagnosis using held-out labels only.
        sep = separation_stats(scores, y[test])
        base = v1.base_stats(y[test])
        chosen_eval = v1.select_top_fraction(scores, y[test], chosen_q)
        chosen_lift = float(chosen_eval["precision"]) - float(base["precision"])

        q_rows: list[dict[str, Any]] = []
        for q in Q_GRID:
            ev = v1.select_top_fraction(scores, y[test], q)
            lift = float(ev["precision"]) - float(base["precision"])
            q_rows.append({
                "q": q,
                "true": int(ev["true"]),
                "false": int(ev["false"]),
                "precision": float(ev["precision"]),
                "selectedPct": float(ev["selectedPct"]),
                "lift": round(lift, 2),
                "wouldPassDiagnostic": bool(ev["true"] > 0 and lift >= 5.0),
            })
        oracle = max(q_rows, key=lambda r: (float(r["lift"]), int(r["true"]), -float(r["q"])))
        rank_signal = (
            "strong" if float(sep["auc"]) >= 0.60 else
            "weak-positive" if float(sep["auc"]) >= 0.53 else
            "chance" if float(sep["auc"]) >= 0.47 else
            "inverted"
        )
        failure_type = "passed"
        if not bool(saved.get("passed")):
            if float(sep["auc"]) >= 0.55 and bool(oracle["wouldPassDiagnostic"]):
                failure_type = "operating-point"
            elif float(sep["auc"]) >= 0.55:
                failure_type = "rank-signal-but-insufficient-tail"
            elif float(sep["auc"]) < 0.47:
                failure_type = "ranking-inversion"
            else:
                failure_type = "ranking-collapse"

        row = {
            "fold": fold,
            "measureMin": int(np.min(measures[test])),
            "measureMax": int(np.max(measures[test])),
            "testRows": int(np.sum(test)),
            "savedPassed": bool(saved.get("passed")),
            "pairRadius": radius,
            "lambda": lam,
            "chosenQ": chosen_q,
            "basePrecision": float(base["precision"]),
            "chosenTrue": int(chosen_eval["true"]),
            "chosenFalse": int(chosen_eval["false"]),
            "chosenPrecision": float(chosen_eval["precision"]),
            "chosenLift": round(chosen_lift, 2),
            **sep,
            "rankSignal": rank_signal,
            "failureType": failure_type,
            "oracleDiagnostic": oracle,
            "qSweep": q_rows,
        }
        diagnostics.append(row)
        print("SECTION", row, flush=True)

    failed = [r for r in diagnostics if not r["savedPassed"]]
    passed = [r for r in diagnostics if r["savedPassed"]]
    failed_auc = float(np.mean([r["auc"] for r in failed])) if failed else 0.0
    passed_auc = float(np.mean([r["auc"] for r in passed])) if passed else 0.0
    operating = sum(r["failureType"] == "operating-point" for r in failed)
    collapse = sum(r["failureType"] in {"ranking-collapse", "ranking-inversion"} for r in failed)
    insufficient = sum(r["failureType"] == "rank-signal-but-insufficient-tail" for r in failed)

    if operating >= 3:
        next_target = "training-only section-aware operating-point calibration"
    elif collapse >= 3:
        next_target = "new section-stable ranking representation/objective"
    elif insufficient >= 3:
        next_target = "stronger ranking features rather than threshold tuning"
    else:
        next_target = "mixed failure mechanisms; retire pairwise V2 tuning"

    summary = {
        "passingSectionFolds": len(passed),
        "failingSectionFolds": len(failed),
        "passingMeanAuc": round(passed_auc, 5),
        "failingMeanAuc": round(failed_auc, 5),
        "failedOperatingPointCount": operating,
        "failedRankingCollapseOrInversionCount": collapse,
        "failedRankSignalInsufficientTailCount": insufficient,
        "nextTarget": next_target,
    }
    print("SUMMARY", summary, flush=True)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during section separability diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-section-rank-separability-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "sections": diagnostics,
        "summary": summary,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-validation-only",
        "protected949CandidateHashUnchanged": before == after,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "nextTarget": next_target,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 SECTION RANK SEPARABILITY V1 COMPLETE")
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
