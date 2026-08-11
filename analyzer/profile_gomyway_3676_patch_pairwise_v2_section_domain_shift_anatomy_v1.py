from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PATCH_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
V2_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-section-domain-shift-anatomy-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-v2-section-domain-shift-anatomy-v1-manifest.json"
OUTER_FOLDS = 5
EPS = 1e-8


def contiguous_fold(measure: int, lo: int, hi: int, folds: int = OUTER_FOLDS) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def family(name: str) -> str:
    parts = name.split("::")
    if len(parts) >= 2:
        head, tail = parts[0], parts[1]
        # collapse exact time-bin coordinates so the report is readable
        for token in ("T0", "T1", "T2", "T3", "T4", "T5"):
            if tail.endswith(token):
                tail = tail[: -len(token)] + "timebin"
                break
        return f"{head}::{tail}"
    return name


def fold_shift(x_train: np.ndarray, x_test: np.ndarray, feature_names: list[str]) -> dict[str, Any]:
    mean = np.mean(x_train, axis=0)
    std = np.std(x_train, axis=0)
    std = np.where(std < EPS, 1.0, std)

    train_z = (x_train - mean) / std
    test_z = (x_test - mean) / std

    mean_shift = np.abs(np.mean(test_z, axis=0) - np.mean(train_z, axis=0))
    train_sd_z = np.std(train_z, axis=0)
    test_sd_z = np.std(test_z, axis=0)
    scale_shift = np.abs(np.log((test_sd_z + 0.05) / (train_sd_z + 0.05)))

    top_idx = np.argsort(mean_shift)[::-1][:12]
    top = [
        {
            "feature": feature_names[int(i)],
            "family": family(feature_names[int(i)]),
            "meanShift": round(float(mean_shift[int(i)]), 6),
            "scaleShift": round(float(scale_shift[int(i)]), 6),
        }
        for i in top_idx
    ]

    return {
        "meanAbsStandardizedMeanShift": round(float(np.mean(mean_shift)), 6),
        "medianAbsStandardizedMeanShift": round(float(np.median(mean_shift)), 6),
        "p90AbsStandardizedMeanShift": round(float(np.quantile(mean_shift, 0.90)), 6),
        "medianAbsLogScaleShift": round(float(np.median(scale_shift)), 6),
        "p90AbsLogScaleShift": round(float(np.quantile(scale_shift, 0.90)), 6),
        "topShiftedFeatures": top,
    }


def main() -> None:
    patch = json.loads(PATCH_PATH.read_text(encoding="utf-8"))
    v2 = json.loads(V2_PATH.read_text(encoding="utf-8"))

    slots = list(patch.get("candidateSlots") or [])
    if not slots:
        raise RuntimeError("candidateSlots missing from spectro-temporal patch profile")
    section_rows = list(v2.get("section") or [])
    if len(section_rows) != OUTER_FOLDS:
        raise RuntimeError(f"Expected {OUTER_FOLDS} V2 section folds, found {len(section_rows)}")

    feature_names = sorted((slots[0].get("features") or {}).keys())
    x = np.asarray(
        [[float((row.get("features") or {}).get(name, 0.0)) for name in feature_names] for row in slots],
        dtype=np.float64,
    )
    measures = np.asarray([int(row["measure"]) for row in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([contiguous_fold(int(m), lo, hi) for m in measures], dtype=np.int16)

    result_rows: list[dict[str, Any]] = []
    for fold in range(OUTER_FOLDS):
        test = ids == fold
        train = ~test
        v2row = next((r for r in section_rows if int(r.get("fold", -1)) == fold), None)
        if v2row is None:
            raise RuntimeError(f"Missing V2 section fold {fold}")
        shift = fold_shift(x[train], x[test], feature_names)
        test_measures = measures[test]
        row = {
            "fold": fold,
            "passed": bool(v2row.get("passed")),
            "heldoutPrecisionLift": float(v2row.get("heldoutPrecisionLift", 0.0)),
            "heldoutMeasureMin": int(np.min(test_measures)),
            "heldoutMeasureMax": int(np.max(test_measures)),
            "heldoutRows": int(np.sum(test)),
            "chosenPairRadius": int((v2row.get("chosen") or {}).get("pairRadius", 0)),
            "chosenLambda": float((v2row.get("chosen") or {}).get("lambda", 0.0)),
            "chosenTailQuantile": float((v2row.get("chosen") or {}).get("tailQuantile", 0.0)),
            **shift,
        }
        result_rows.append(row)
        print("SECTION", row, flush=True)

    passing = [r for r in result_rows if r["passed"]]
    failing = [r for r in result_rows if not r["passed"]]
    if len(passing) != 1 or len(failing) != 4:
        print(f"Warning: expected V2 section shape 1 pass / 4 fail, got {len(passing)} / {len(failing)}", flush=True)

    def avg(rows: list[dict[str, Any]], key: str) -> float:
        return float(np.mean([float(r[key]) for r in rows])) if rows else float("nan")

    pass_median = avg(passing, "medianAbsStandardizedMeanShift")
    fail_median = avg(failing, "medianAbsStandardizedMeanShift")
    pass_p90 = avg(passing, "p90AbsStandardizedMeanShift")
    fail_p90 = avg(failing, "p90AbsStandardizedMeanShift")

    sorted_by_shift = sorted(result_rows, key=lambda r: float(r["medianAbsStandardizedMeanShift"]))
    pass_shift_rank = None
    if passing:
        pass_fold = int(passing[0]["fold"])
        pass_shift_rank = next(i + 1 for i, r in enumerate(sorted_by_shift) if int(r["fold"]) == pass_fold)

    family_fail: dict[str, int] = {}
    family_pass: dict[str, int] = {}
    for row in result_rows:
        target = family_pass if row["passed"] else family_fail
        seen = set()
        for item in row["topShiftedFeatures"]:
            fam = str(item["family"])
            if fam not in seen:
                target[fam] = target.get(fam, 0) + 1
                seen.add(fam)

    family_signals = []
    for fam in sorted(set(family_fail) | set(family_pass)):
        family_signals.append({
            "family": fam,
            "failedTopShiftFolds": int(family_fail.get(fam, 0)),
            "passingTopShiftFolds": int(family_pass.get(fam, 0)),
        })
    family_signals.sort(key=lambda r: (r["failedTopShiftFolds"] - r["passingTopShiftFolds"], r["failedTopShiftFolds"]), reverse=True)

    ratio = (fail_median / pass_median) if passing and pass_median > EPS else 0.0
    domain_shift_ready = bool(
        passing
        and failing
        and pass_shift_rank is not None
        and pass_shift_rank <= 2
        and fail_median >= pass_median * 1.20
    )

    summary = {
        "passingSectionFolds": len(passing),
        "failingSectionFolds": len(failing),
        "passingMeanMedianShift": round(pass_median, 6) if passing else None,
        "failingMeanMedianShift": round(fail_median, 6) if failing else None,
        "failingVsPassingMedianShiftRatio": round(ratio, 3),
        "passingMeanP90Shift": round(pass_p90, 6) if passing else None,
        "failingMeanP90Shift": round(fail_p90, 6) if failing else None,
        "passingFoldShiftRankAmongFive": pass_shift_rank,
        "domainShiftHypothesisReady": domain_shift_ready,
    }

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-v2-section-domain-shift-anatomy",
        "analysisRole": "post-hoc-validation-diagnostic-only",
        "heldoutLabelsUsedToComputeShiftMetrics": False,
        "sectionRows": result_rows,
        "summary": summary,
        "topFamilyShiftSignals": family_signals[:15],
        "validatedNewChampion": False,
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
        "domainShiftHypothesisReady": domain_shift_ready,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE V2 SECTION DOMAIN SHIFT ANATOMY V1 COMPLETE")
    print("SUMMARY", summary)
    print("TOP FAMILY SHIFT SIGNALS")
    for row in family_signals[:10]:
        print("FAMILY", row)
    print("Domain-shift hypothesis ready:", domain_shift_ready)
    print("Validated new champion: False")
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
