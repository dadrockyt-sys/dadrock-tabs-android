from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_spectro_temporal_patch_stability_v1 as patch

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-local-context-distribution-shift-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-local-context-distribution-shift-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
RADII = [2, 4, 8]
EPS = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def robust_local_normalize(x: np.ndarray, measures: np.ndarray, radius: int) -> np.ndarray:
    out = np.zeros_like(x, dtype=np.float64)
    for i, measure in enumerate(measures):
        mask = np.abs(measures - int(measure)) <= radius
        local = x[mask]
        median = np.median(local, axis=0)
        mad = np.median(np.abs(local - median), axis=0) * 1.4826
        mad = np.where(mad < EPS, 1.0, mad)
        out[i] = (x[i] - median) / mad
    return out


def shift_stats(train: np.ndarray, test: np.ndarray) -> dict[str, Any]:
    mean = np.mean(train, axis=0)
    scale = np.std(train, axis=0)
    scale = np.where(scale < EPS, 1.0, scale)
    abs_smd = np.abs((np.mean(test, axis=0) - mean) / scale)
    q = np.quantile(abs_smd, [0.5, 0.75, 0.9, 0.95])
    return {
        "meanAbsSmd": round(float(np.mean(abs_smd)), 6),
        "medianAbsSmd": round(float(q[0]), 6),
        "p75AbsSmd": round(float(q[1]), 6),
        "p90AbsSmd": round(float(q[2]), 6),
        "p95AbsSmd": round(float(q[3]), 6),
        "maxAbsSmd": round(float(np.max(abs_smd)), 6),
    }


def evaluate_scheme(
    representations: dict[str, np.ndarray],
    measures: np.ndarray,
    name: str,
    fold_fn: Callable[[int], int],
) -> dict[str, Any]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    folds: list[dict[str, Any]] = []
    for fold in range(OUTER_FOLDS):
        test = ids == fold
        train = ~test
        row: dict[str, Any] = {
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "representations": {},
        }
        for rep_name, xx in representations.items():
            row["representations"][rep_name] = shift_stats(xx[train], xx[test])
        folds.append(row)

    summary: dict[str, Any] = {}
    for rep_name in representations:
        medians = [float(f["representations"][rep_name]["medianAbsSmd"]) for f in folds]
        p90s = [float(f["representations"][rep_name]["p90AbsSmd"]) for f in folds]
        means = [float(f["representations"][rep_name]["meanAbsSmd"]) for f in folds]
        summary[rep_name] = {
            "meanFoldMeanAbsSmd": round(float(np.mean(means)), 6),
            "meanFoldMedianAbsSmd": round(float(np.mean(medians)), 6),
            "meanFoldP90AbsSmd": round(float(np.mean(p90s)), 6),
        }
    return {"scheme": name, "folds": folds, "summary": summary}


def main() -> None:
    candidate_path = patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows],
        dtype=np.float64,
    )
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("GOMYWAY 36.76 PATCH LOCAL CONTEXT DISTRIBUTION SHIFT V1", flush=True)
    print("Rows:", len(rows), "features:", len(feature_names), flush=True)
    print("Labels used by this diagnostic: False", flush=True)

    representations: dict[str, np.ndarray] = {"raw": x}
    for radius in RADII:
        print(f"heartbeat local normalization radius={radius}", flush=True)
        representations[f"localRobustR{radius}"] = robust_local_normalize(x, measures, radius)

    schemes = [
        evaluate_scheme(representations, measures, "normal", lambda m: m % OUTER_FOLDS),
        evaluate_scheme(
            representations,
            measures,
            "section",
            lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS),
        ),
        evaluate_scheme(
            representations,
            measures,
            "shiftedWindow",
            lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS),
        ),
    ]

    for result in schemes:
        print("SCHEME", result["scheme"], result["summary"], flush=True)

    target_schemes = [s for s in schemes if s["scheme"] in {"section", "shiftedWindow"}]
    aggregate: dict[str, dict[str, float]] = {}
    for rep_name in representations:
        median_shift = float(
            np.mean([s["summary"][rep_name]["meanFoldMedianAbsSmd"] for s in target_schemes])
        )
        p90_shift = float(
            np.mean([s["summary"][rep_name]["meanFoldP90AbsSmd"] for s in target_schemes])
        )
        aggregate[rep_name] = {
            "sectionShiftedMeanMedianAbsSmd": round(median_shift, 6),
            "sectionShiftedMeanP90AbsSmd": round(p90_shift, 6),
        }

    raw_median = aggregate["raw"]["sectionShiftedMeanMedianAbsSmd"]
    for rep_name, stats in aggregate.items():
        stats["medianShiftReductionPctVsRaw"] = round(
            100.0 * (raw_median - stats["sectionShiftedMeanMedianAbsSmd"]) / raw_median,
            2,
        ) if raw_median > EPS else 0.0

    best = min(
        aggregate,
        key=lambda name: (
            aggregate[name]["sectionShiftedMeanMedianAbsSmd"],
            aggregate[name]["sectionShiftedMeanP90AbsSmd"],
        ),
    )
    meaningful = (
        best != "raw" and aggregate[best]["medianShiftReductionPctVsRaw"] >= 20.0
    )

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during distribution-shift diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-local-context-distribution-shift-label-free-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "featureCount": len(feature_names),
        "rowCount": len(rows),
        "labelsUsed": False,
        "radii": RADII,
        "schemes": schemes,
        "aggregate": aggregate,
        "bestRepresentation": best,
        "localNormalizationMeaningfullyReducesShift": meaningful,
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
        "candidateSha256": after,
        "bestRepresentation": best,
        "localNormalizationMeaningfullyReducesShift": meaningful,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("AGGREGATE", aggregate, flush=True)
    print("Best representation:", best)
    print("Local normalization meaningfully reduces shift:", meaningful)
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
