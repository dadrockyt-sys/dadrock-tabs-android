from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_3676_patch_v5_v9_hybrid_sectionpass_nested_cv_v10 as v10
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V10_PATH = PUBLIC / "gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-residual-score-distribution-signal-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-residual-score-distribution-signal-v1-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scheme_ids(measures: np.ndarray, scheme: str) -> np.ndarray:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    if scheme == "normal":
        return np.asarray([int(m) % OUTER_FOLDS for m in measures], dtype=np.int16)
    if scheme == "section":
        return np.asarray([v1.contiguous_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    if scheme == "shiftedWindow":
        return np.asarray([v1.shifted_fold(int(m), lo, hi, OUTER_FOLDS) for m in measures], dtype=np.int16)
    raise ValueError(scheme)


def score_geometry(scores: np.ndarray, q: float) -> dict[str, float | bool]:
    s = np.asarray(scores, dtype=np.float64)
    n = len(s)
    if n < 4:
        raise RuntimeError("Too few held-out scores for geometry diagnostic")
    ordered = np.sort(s)[::-1]
    mu = float(np.mean(s))
    sd = float(np.std(s))
    scale = sd if sd > 1e-12 else 1.0
    k = max(1, min(n - 1, int(np.ceil(float(q) * n))))
    boundary_hi = float(ordered[k - 1])
    boundary_lo = float(ordered[k])
    cutoff = 0.5 * (boundary_hi + boundary_lo)
    near = np.abs(s - cutoff) <= 0.10 * scale
    top5n = max(1, int(np.ceil(0.05 * n)))
    top10n = max(1, int(np.ceil(0.10 * n)))
    q50, q75, q90, q95, q99 = [float(np.quantile(s, z)) for z in (0.50, 0.75, 0.90, 0.95, 0.99)]
    top5_mean = float(np.mean(ordered[:top5n]))
    top10_mean = float(np.mean(ordered[:top10n]))
    selected_mean = float(np.mean(ordered[:k]))
    rest_mean = float(np.mean(ordered[k:])) if k < n else selected_mean
    return {
        "chosenQ": float(q),
        "gridEdgeQ": bool(abs(float(q) - 0.05) < 1e-9 or abs(float(q) - 0.15) < 1e-9),
        "scoreStd": sd,
        "boundaryGapZ": float((boundary_hi - boundary_lo) / scale),
        "boundaryDensityPct": float(100.0 * np.mean(near)),
        "selectedVsRestGapZ": float((selected_mean - rest_mean) / scale),
        "top5ConcentrationZ": float((top5_mean - mu) / scale),
        "top10ConcentrationZ": float((top10_mean - mu) / scale),
        "top5VsTop10GapZ": float((top5_mean - top10_mean) / scale),
        "upperTailSpreadZ": float((q99 - q90) / scale),
        "q95MinusMedianZ": float((q95 - q50) / scale),
        "q90MinusQ75Z": float((q90 - q75) / scale),
    }


def mean_metric(rows: list[dict[str, Any]], key: str) -> float:
    vals = [float(r["geometry"][key]) for r in rows]
    return float(np.mean(vals)) if vals else 0.0


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")
    slots = list(source.get("candidateSlots") or [])
    hybrid = json.loads(V10_PATH.read_text(encoding="utf-8"))
    features = sorted((slots[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in features] for r in slots], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)

    rows: list[dict[str, Any]] = []
    for scheme in ("normal", "section", "shiftedWindow"):
        ids = scheme_ids(measures, scheme)
        for row in list(hybrid.get(scheme) or []):
            fold = int(row["fold"])
            test = ids == fold
            train = ~test
            architecture = str(row.get("architectureChosen") or "v5")
            if architecture == "v9":
                chosen = dict(row.get("v9Choice") or row.get("chosen") or {})
                model = v9.fit_pointwise_ridge(x[train], y[train], float(chosen["lambda"]))
                scores = v9.scores_for(x[test], model)
                q = float(chosen["tailQuantile"])
            else:
                chosen = dict(row.get("v5Choice") or row.get("chosen") or {})
                model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"]))
                scores = v2.scores_for(x[test], model)
                q = float(chosen["tailQuantile"])
            rec = {
                "scheme": scheme,
                "fold": fold,
                "passed": bool(row.get("passed")),
                "architectureChosen": architecture,
                "geometry": score_geometry(scores, q),
            }
            rows.append(rec)
            print("GEOMETRY", rec, flush=True)

    passing = [r for r in rows if r["passed"]]
    failing = [r for r in rows if not r["passed"]]
    v5_passing = [r for r in passing if r["architectureChosen"] == "v5"]
    v5_failing = [r for r in failing if r["architectureChosen"] == "v5"]

    metric_names = [
        "boundaryGapZ", "boundaryDensityPct", "selectedVsRestGapZ", "top5ConcentrationZ",
        "top10ConcentrationZ", "top5VsTop10GapZ", "upperTailSpreadZ", "q95MinusMedianZ", "q90MinusQ75Z",
    ]
    comparisons: dict[str, Any] = {}
    active: list[str] = []
    for key in metric_names:
        p = mean_metric(v5_passing, key)
        f = mean_metric(v5_failing, key)
        delta = f - p
        pooled_vals = [float(r["geometry"][key]) for r in (v5_passing + v5_failing)]
        pooled_sd = float(np.std(pooled_vals)) if pooled_vals else 0.0
        effect = delta / pooled_sd if pooled_sd > 1e-12 else 0.0
        comparisons[key] = {
            "v5PassingMean": round(p, 6),
            "v5FailingMean": round(f, 6),
            "failureMinusPassDelta": round(delta, 6),
            "standardizedEffect": round(effect, 6),
        }
        if len(v5_failing) >= 2 and abs(effect) >= 1.0:
            active.append(key)

    passing_edge_pct = 100.0 * np.mean([bool(r["geometry"]["gridEdgeQ"]) for r in v5_passing]) if v5_passing else 0.0
    failing_edge_pct = 100.0 * np.mean([bool(r["geometry"]["gridEdgeQ"]) for r in v5_failing]) if v5_failing else 0.0
    if failing_edge_pct - passing_edge_pct >= 40.0:
        active.append("gridEdgeQ")

    ready = len(active) > 0
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during residual score-distribution diagnostic")

    summary = {
        "folds": len(rows),
        "passingFolds": len(passing),
        "failingFolds": len(failing),
        "v5PassingFolds": len(v5_passing),
        "v5FailingFolds": len(v5_failing),
        "v5PassingGridEdgePct": round(float(passing_edge_pct), 3),
        "v5FailingGridEdgePct": round(float(failing_edge_pct), 3),
        "activeSignals": active,
        "residualScoreDistributionSignalReady": bool(ready),
        "nextTarget": "predeclare-training-only-residual-selector-test" if ready else "retire-score-distribution-calibration-and-pivot-representation",
    }
    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-residual-score-distribution-signal",
        "importantCaveat": "Outer held-out pass/fail labels are used only to diagnose whether unlabeled score geometry differs between already-passing and already-failing V10 folds. This file must not itself define a production selector.",
        "summary": summary,
        "comparisons": comparisons,
        "rows": rows,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseThresholdOrSelector": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "activeSignals": active,
        "residualScoreDistributionSignalReady": bool(ready),
        "nextTarget": summary["nextTarget"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 RESIDUAL SCORE DISTRIBUTION SIGNAL V1 COMPLETE")
    print("V10 passes:", len(passing), "/", len(rows))
    print("Remaining failures:", len(failing))
    print("V5 passing folds:", len(v5_passing), "V5 failing folds:", len(v5_failing))
    print("Active residual score-distribution signals:", active)
    print("Residual score-distribution signal ready:", bool(ready))
    print("Next target:", summary["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose threshold or selector: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
