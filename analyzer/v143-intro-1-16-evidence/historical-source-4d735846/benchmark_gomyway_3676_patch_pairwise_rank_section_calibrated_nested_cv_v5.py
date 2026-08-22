from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PAIR_RADII = list(v2.PAIR_RADII)
LAMBDAS = list(v2.LAMBDAS)
TAIL_QUANTILES = list(v2.TAIL_QUANTILES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_family(name: str) -> str:
    s = str(name).lower()
    if "shift" in s:
        return "shiftedWindow"
    if "section" in s or "contig" in s:
        return "section"
    return "normal"


def evaluate_radius_lambda(x: np.ndarray, y: np.ndarray, measures: np.ndarray, radius: int, lam: float) -> dict[str, Any]:
    # Evaluate every q on the exact V2 inner masks. Held-out outer data never enters here.
    by_q: list[dict[str, Any]] = []
    for q in TAIL_QUANTILES:
        folds: list[dict[str, Any]] = []
        for split_name, train, test in v1.inner_masks(measures):
            model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
            held = v1.select_top_fraction(v2.scores_for(x[test], model), y[test], q)
            base = v1.base_stats(y[test])
            lift = float(held["precision"]) - float(base["precision"])
            passed = held["true"] > 0 and lift >= 5.0
            folds.append({
                "split": split_name,
                "family": split_family(split_name),
                "pairCount": int(model["pairCount"]),
                "true": int(held["true"]),
                "false": int(held["false"]),
                "precision": held["precision"],
                "selectedPct": held["selectedPct"],
                "basePrecision": base["precision"],
                "lift": round(lift, 2),
                "passed": bool(passed),
            })
        section = [f for f in folds if f["family"] == "section"]
        overall_pass = sum(bool(f["passed"]) for f in folds)
        section_pass = sum(bool(f["passed"]) for f in section)
        overall_lift = float(np.mean([float(f["lift"]) for f in folds])) if folds else -999.0
        section_lift = float(np.mean([float(f["lift"]) for f in section])) if section else -999.0
        section_true = sum(int(f["true"]) for f in section)
        section_false = sum(int(f["false"]) for f in section)
        by_q.append({
            "tailQuantile": q,
            "folds": folds,
            "overallPassCount": overall_pass,
            "overallFoldCount": len(folds),
            "overallMeanLift": round(overall_lift, 3),
            "sectionPassCount": section_pass,
            "sectionFoldCount": len(section),
            "sectionMeanLift": round(section_lift, 3),
            "sectionTrue": section_true,
            "sectionFalse": section_false,
        })
    # Section-aware operating-point calibration: section pass count/lift lead;
    # broad overall behavior and precision balance are tie-breakers only.
    best_q = max(
        by_q,
        key=lambda r: (
            int(r["sectionPassCount"]),
            float(r["sectionMeanLift"]),
            int(r["overallPassCount"]),
            float(r["overallMeanLift"]),
            int(r["sectionTrue"]) - int(r["sectionFalse"]),
            int(r["sectionTrue"]),
            -float(r["tailQuantile"]),
        ),
    )
    return {"radius": radius, "lambda": lam, "bestQ": best_q, "qDiagnostics": by_q}


def choose_model(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(PAIR_RADII) * len(LAMBDAS)
    done = 0
    for radius in PAIR_RADII:
        for lam in LAMBDAS:
            done += 1
            if done == 1 or done % 3 == 0 or done == total:
                print(f"    heartbeat section-calibration model search {done}/{total}", flush=True)
            ev = evaluate_radius_lambda(x, y, measures, radius, lam)
            q = ev["bestQ"]
            candidates.append({
                "pairRadius": radius,
                "lambda": lam,
                "tailQuantile": float(q["tailQuantile"]),
                "sectionPassCount": int(q["sectionPassCount"]),
                "sectionFoldCount": int(q["sectionFoldCount"]),
                "sectionMeanLift": float(q["sectionMeanLift"]),
                "overallPassCount": int(q["overallPassCount"]),
                "overallFoldCount": int(q["overallFoldCount"]),
                "overallMeanLift": float(q["overallMeanLift"]),
                "sectionTrue": int(q["sectionTrue"]),
                "sectionFalse": int(q["sectionFalse"]),
                "qDiagnostics": ev["qDiagnostics"],
            })
    # Radius/lambda are still judged on both section robustness and broad inner behavior.
    return max(
        candidates,
        key=lambda r: (
            int(r["sectionPassCount"]),
            float(r["sectionMeanLift"]),
            int(r["overallPassCount"]),
            float(r["overallMeanLift"]),
            int(r["sectionTrue"]) - int(r["sectionFalse"]),
            int(r["sectionTrue"]),
            -float(r["tailQuantile"]),
            -float(r["lambda"]),
            -int(r["pairRadius"]),
        ),
    )


def evaluate_scheme(x: np.ndarray, y: np.ndarray, measures: np.ndarray, feature_names: list[str], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    passes = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        chosen = choose_model(x[train], y[train], measures[train])
        model = v2.fit_pairwise_ranker(x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"]))
        held = v1.select_top_fraction(v2.scores_for(x[test], model), y[test], float(chosen["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)
        coef = np.asarray(model["coef"])
        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [{"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)} for j in top_idx]
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "chosen": chosen,
            "pairCount": int(model["pairCount"]),
            "sampler": "measure-stratified-deterministic-v2",
            "operatingPointCalibration": "training-only-inner-contiguous-section-priority",
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        }
        rows.append(row)
        print(
            f"  radius={chosen['pairRadius']} lambda={chosen['lambda']} q={chosen['tailQuantile']} "
            f"innerSectionPass={chosen['sectionPassCount']}/{chosen['sectionFoldCount']} "
            f"pairs={model['pairCount']} held={held['true']}/{held['false']} selectedPct={held['selectedPct']} "
            f"precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed}",
            flush=True,
        )
    return passes == OUTER_FOLDS, rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V5 training-only section-aware operating-point calibration", flush=True)
    print("Ranker/sampler/features unchanged from V2; q calibrated on inner contiguous sections only", flush=True)

    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass
    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V5 section-aware calibration CV")

    output = {
        "schemaVersion": 5,
        "profileType": "36.76-patch-pairwise-rank-section-calibrated-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "pairSampler": "deterministic-measure-stratified-v2",
        "operatingPointCalibration": "training-only-inner-contiguous-section-priority",
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchV5Generalizes": generalizes,
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
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
        "schemaVersion": 5,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchV5Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE RANK SECTION-CALIBRATED NESTED CV V5 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise-rank patch V5 generalizes:", generalizes)
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
