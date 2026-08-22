from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
RIDGE_LAMBDAS = [0.1, 1.0, 10.0, 100.0]
TAIL_QUANTILES = list(v5.TAIL_QUANTILES)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_family(name: str) -> str:
    s = str(name).lower()
    if "shift" in s:
        return "shiftedWindow"
    if "section" in s or "contig" in s:
        return "section"
    return "normal"


def fit_pointwise_ridge(x: np.ndarray, y: np.ndarray, lam: float) -> dict[str, Any]:
    x = np.asarray(x, dtype=np.float64)
    y01 = np.asarray(y, dtype=np.float64)
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale > 1e-8, scale, 1.0)
    z = (x - mean) / scale

    # Class-balanced candidate-level fit. This changes the learning objective from
    # pairwise preference to direct true-event scoring while keeping all fitting
    # statistics strictly inside the training partition.
    pos = max(1, int(np.sum(y01 > 0.5)))
    neg = max(1, int(np.sum(y01 <= 0.5)))
    n = len(y01)
    pos_w = n / (2.0 * pos)
    neg_w = n / (2.0 * neg)
    w = np.where(y01 > 0.5, pos_w, neg_w)

    design = np.column_stack([np.ones(n, dtype=np.float64), z])
    sw = np.sqrt(w)
    dw = design * sw[:, None]
    yw = y01 * sw
    penalty = np.eye(design.shape[1], dtype=np.float64) * float(lam)
    penalty[0, 0] = 0.0
    lhs = dw.T @ dw + penalty
    rhs = dw.T @ yw
    try:
        beta = np.linalg.solve(lhs, rhs)
    except np.linalg.LinAlgError:
        beta = np.linalg.pinv(lhs) @ rhs
    return {
        "intercept": float(beta[0]),
        "coef": np.asarray(beta[1:], dtype=np.float64),
        "mean": mean,
        "scale": scale,
        "lambda": float(lam),
        "positiveRows": pos,
        "negativeRows": neg,
    }


def scores_for(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    z = (np.asarray(x, dtype=np.float64) - np.asarray(model["mean"])) / np.asarray(model["scale"])
    return float(model["intercept"]) + z @ np.asarray(model["coef"])


def evaluate_lambda(x: np.ndarray, y: np.ndarray, measures: np.ndarray, lam: float) -> dict[str, Any]:
    # Same V5 section-aware q selection; only the learned ranking representation changes.
    by_q: list[dict[str, Any]] = []
    inner_cache: list[tuple[str, np.ndarray, dict[str, Any], dict[str, Any]]] = []
    for split_name, train, test in v1.inner_masks(measures):
        model = fit_pointwise_ridge(x[train], y[train], lam)
        test_scores = scores_for(x[test], model)
        base = v1.base_stats(y[test])
        inner_cache.append((split_name, test_scores, base, {"y": y[test]}))

    for q in TAIL_QUANTILES:
        folds: list[dict[str, Any]] = []
        for split_name, test_scores, base, extra in inner_cache:
            yy = np.asarray(extra["y"], dtype=bool)
            held = v1.select_top_fraction(test_scores, yy, q)
            lift = float(held["precision"]) - float(base["precision"])
            passed = held["true"] > 0 and lift >= 5.0
            folds.append({
                "split": split_name,
                "family": split_family(split_name),
                "true": int(held["true"]),
                "false": int(held["false"]),
                "precision": held["precision"],
                "selectedPct": held["selectedPct"],
                "basePrecision": base["precision"],
                "lift": round(lift, 2),
                "passed": bool(passed),
            })
        section = [f for f in folds if f["family"] == "section"]
        by_q.append({
            "tailQuantile": float(q),
            "folds": folds,
            "overallPassCount": sum(bool(f["passed"]) for f in folds),
            "overallFoldCount": len(folds),
            "overallMeanLift": round(float(np.mean([float(f["lift"]) for f in folds])), 3),
            "sectionPassCount": sum(bool(f["passed"]) for f in section),
            "sectionFoldCount": len(section),
            "sectionMeanLift": round(float(np.mean([float(f["lift"]) for f in section])), 3),
            "sectionTrue": sum(int(f["true"]) for f in section),
            "sectionFalse": sum(int(f["false"]) for f in section),
        })

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
    return {"lambda": float(lam), "bestQ": best_q, "qDiagnostics": by_q}


def choose_model(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(RIDGE_LAMBDAS)
    for i, lam in enumerate(RIDGE_LAMBDAS, start=1):
        print(f"    heartbeat pointwise-ridge model search {i}/{total}", flush=True)
        ev = evaluate_lambda(x, y, measures, lam)
        q = ev["bestQ"]
        candidates.append({
            "lambda": float(lam),
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
        ),
    )


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    passes = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        chosen = choose_model(x[train], y[train], measures[train])
        model = fit_pointwise_ridge(x[train], y[train], float(chosen["lambda"]))
        held = v1.select_top_fraction(scores_for(x[test], model), y[test], float(chosen["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)

        coef = np.asarray(model["coef"])
        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [
            {"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)}
            for j in top_idx
        ]
        rows.append({
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "chosen": chosen,
            "learner": "class-balanced-pointwise-ridge-v1",
            "standardization": "training-only-zscore",
            "operatingPointCalibration": "v5-training-only-inner-contiguous-section-priority",
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        })
        print(
            f"  lambda={chosen['lambda']} q={chosen['tailQuantile']} "
            f"innerSectionPass={chosen['sectionPassCount']}/{chosen['sectionFoldCount']} "
            f"held={held['true']}/{held['false']} selectedPct={held['selectedPct']} "
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
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V9 pointwise ridge architecture pivot", flush=True)
    print("Direct candidate-level scoring; V5 section-aware operating-point calibration retained", flush=True)

    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(
        x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS)
    )
    shifted_pass, shifted = evaluate_scheme(
        x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS)
    )
    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V9 pointwise ridge CV")

    output = {
        "schemaVersion": 9,
        "profileType": "36.76-patch-pointwise-ridge-section-calibrated-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "learner": "class-balanced-pointwise-ridge-v1",
        "standardization": "training-only-zscore",
        "ridgeLambdas": RIDGE_LAMBDAS,
        "tailQuantiles": TAIL_QUANTILES,
        "operatingPointCalibration": "v5-training-only-inner-contiguous-section-priority",
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pointwiseRidgePatchV9Generalizes": generalizes,
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
        "schemaVersion": 9,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pointwiseRidgePatchV9Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH POINTWISE RIDGE SECTION-CALIBRATED NESTED CV V9 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pointwise ridge patch V9 generalizes:", generalizes)
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
