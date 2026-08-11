from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V5_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-unlabeled-score-geometry-cutoff-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v5-unlabeled-score-geometry-cutoff-v1-manifest.json"
OUTER_FOLDS = 5
DIAGNOSTIC_Q = [0.025, 0.05, 0.075, 0.10, 0.125, 0.15, 0.20]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_q(scores: np.ndarray) -> dict[str, Any]:
    """Choose an operating fraction using held-out scores only, never labels."""
    s = np.asarray(scores, dtype=np.float64)
    n = len(s)
    if n < 8:
        return {"q": 0.05, "index": max(1, int(round(0.05 * n))), "gap": 0.0, "gapZ": 0.0}

    order = np.sort(s)[::-1]
    med = float(np.median(order))
    mad = float(np.median(np.abs(order - med)))
    scale = max(1e-12, 1.4826 * mad, float(np.std(order)) * 0.25)

    candidates: list[dict[str, Any]] = []
    for q in DIAGNOSTIC_Q:
        k = int(np.ceil(float(q) * n))
        k = min(max(k, 1), n - 1)
        gap = float(order[k - 1] - order[k])
        candidates.append({"q": float(q), "index": k, "gap": gap, "gapZ": gap / scale})

    # Score geometry alone decides. Prefer the strongest standardized gap;
    # on exact ties prefer the smaller selected fraction.
    return max(candidates, key=lambda r: (float(r["gapZ"]), -float(r["q"])))


def evaluate_q(scores: np.ndarray, labels: np.ndarray, q: float) -> dict[str, Any]:
    held = v1.select_top_fraction(scores, labels, q)
    base = v1.base_stats(labels)
    lift = float(held["precision"]) - float(base["precision"])
    return {
        "q": float(q),
        "true": int(held["true"]),
        "false": int(held["false"]),
        "precision": float(held["precision"]),
        "selectedPct": float(held["selectedPct"]),
        "basePrecision": float(base["precision"]),
        "lift": round(lift, 2),
        "passed": bool(int(held["true"]) > 0 and lift >= 5.0),
    }


def best_diagnostic_q(scores: np.ndarray, labels: np.ndarray) -> dict[str, Any]:
    rows = [evaluate_q(scores, labels, q) for q in DIAGNOSTIC_Q]
    # Post-hoc grading only. This is never used to choose the geometry cutoff.
    return max(rows, key=lambda r: (bool(r["passed"]), float(r["lift"]), int(r["true"]), -float(r["q"])))


def outer_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % OUTER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def main() -> None:
    before = sha256(V5_PATH)
    v5_payload = json.loads(V5_PATH.read_text(encoding="utf-8"))
    if int(v5_payload.get("outerFoldsPassed", -1)) != 11:
        raise RuntimeError("Expected V5 11/15 baseline before score-geometry diagnostic")

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(source.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")

    feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)

    rows: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        ids = outer_ids(measures, scheme)
        saved_rows = {int(r.get("fold", -1)): r for r in (v5_payload.get(scheme) or [])}
        if len(saved_rows) != OUTER_FOLDS:
            raise RuntimeError(f"Expected {OUTER_FOLDS} saved V5 rows for {scheme}")

        for fold in range(OUTER_FOLDS):
            saved = saved_rows[fold]
            chosen = saved.get("chosen") or {}
            test = ids == fold
            train = ~test

            model = v2.fit_pairwise_ranker(
                x[train], y[train], measures[train],
                int(chosen["pairRadius"]), float(chosen["lambda"]),
            )
            scores = v2.scores_for(x[test], model)
            labels = y[test]

            geom = geometry_q(scores)
            geom_eval = evaluate_q(scores, labels, float(geom["q"]))
            diagnostic_best = best_diagnostic_q(scores, labels)
            saved_q = float(chosen["tailQuantile"])
            saved_eval = evaluate_q(scores, labels, saved_q)

            rec = {
                "scheme": scheme,
                "fold": fold,
                "v5Passed": bool(saved.get("passed")),
                "v5Lift": float(saved.get("heldoutPrecisionLift", 0.0)),
                "v5Q": saved_q,
                "geometryQ": float(geom["q"]),
                "geometryGap": round(float(geom["gap"]), 8),
                "geometryGapZ": round(float(geom["gapZ"]), 4),
                "geometryEvaluation": geom_eval,
                "diagnosticBestQ": float(diagnostic_best["q"]),
                "diagnosticBestLift": float(diagnostic_best["lift"]),
                "diagnosticBestPassed": bool(diagnostic_best["passed"]),
                "geometryQDistanceFromDiagnosticBest": round(abs(float(geom["q"]) - float(diagnostic_best["q"])), 3),
                "geometryFlip": (
                    "failToPass" if (not bool(saved.get("passed")) and bool(geom_eval["passed"]))
                    else "passToFail" if (bool(saved.get("passed")) and not bool(geom_eval["passed"]))
                    else "none"
                ),
                "professionalLabelsUsedToChooseGeometryQ": False,
            }
            rows.append(rec)
            print("GEOMETRY", rec)

    v5_passes = sum(bool(r["v5Passed"]) for r in rows)
    geometry_passes = sum(bool(r["geometryEvaluation"]["passed"]) for r in rows)
    fail_to_pass = sum(r["geometryFlip"] == "failToPass" for r in rows)
    pass_to_fail = sum(r["geometryFlip"] == "passToFail" for r in rows)
    failed = [r for r in rows if not r["v5Passed"]]
    failed_alignment = float(np.mean([r["geometryQDistanceFromDiagnosticBest"] for r in failed])) if failed else 999.0

    scheme_summary: dict[str, Any] = {}
    for scheme in ("normal", "section", "shiftedWindow"):
        rs = [r for r in rows if r["scheme"] == scheme]
        scheme_summary[scheme] = {
            "folds": len(rs),
            "v5Passes": sum(bool(r["v5Passed"]) for r in rs),
            "geometryPasses": sum(bool(r["geometryEvaluation"]["passed"]) for r in rs),
            "failToPass": sum(r["geometryFlip"] == "failToPass" for r in rs),
            "passToFail": sum(r["geometryFlip"] == "passToFail" for r in rs),
        }

    geometry_signal = (
        len(rows) == 15
        and fail_to_pass >= 2
        and pass_to_fail <= 1
        and geometry_passes > v5_passes
    )

    summary = {
        "folds": len(rows),
        "v5Passes": v5_passes,
        "geometryPasses": geometry_passes,
        "failToPass": fail_to_pass,
        "passToFail": pass_to_fail,
        "remainingFailureMeanAbsQDistanceToDiagnosticBest": round(failed_alignment, 3),
        "schemeSummary": scheme_summary,
    }

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v5-unlabeled-score-geometry-cutoff-diagnostic",
        "method": "heldout-score-only-largest-standardized-gap-over-q-grid",
        "rows": rows,
        "summary": summary,
        "unlabeledScoreGeometryHypothesisReady": bool(geometry_signal),
        "nextTarget": "test-unlabeled-score-geometry-operating-point-in-strict-nested-cv" if geometry_signal else "retire-score-geometry-cutoff-and-pivot-architecture",
        "validatedNewChampion": False,
        "professionalReferenceUsedToChooseCutoff": False,
        "professionalReferenceUsedDuringDetection": False,
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
        "unlabeledScoreGeometryHypothesisReady": bool(geometry_signal),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    after = sha256(V5_PATH)
    if before != after:
        raise RuntimeError("V5 result changed during score-geometry diagnostic")

    print("GOMYWAY 36.76 PATCH PAIRWISE V5 UNLABELED SCORE GEOMETRY CUTOFF V1 COMPLETE")
    print("SUMMARY", summary)
    print("Unlabeled score geometry hypothesis ready:", bool(geometry_signal))
    print("Next target:", output["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used to choose cutoff: False")
    print("Professional reference used during detection: False")
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
