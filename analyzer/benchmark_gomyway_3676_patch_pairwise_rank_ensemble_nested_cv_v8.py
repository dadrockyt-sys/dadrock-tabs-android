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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-ensemble-nested-cv-v8.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-ensemble-nested-cv-v8-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
TOP_K = 3
EPS = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_family(name: str) -> str:
    return v5.split_family(name)


def rank_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(row["sectionPassCount"]),
        float(row["sectionMeanLift"]),
        int(row["overallPassCount"]),
        float(row["overallMeanLift"]),
        int(row["sectionTrue"]) - int(row["sectionFalse"]),
        int(row["sectionTrue"]),
        -float(row["tailQuantile"]),
        -float(row["lambda"]),
        -int(row["pairRadius"]),
    )


def choose_top_models(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    total = len(v5.PAIR_RADII) * len(v5.LAMBDAS)
    done = 0
    for radius in v5.PAIR_RADII:
        for lam in v5.LAMBDAS:
            done += 1
            if done == 1 or done % 3 == 0 or done == total:
                print(f"    heartbeat ensemble base-model search {done}/{total}", flush=True)
            ev = v5.evaluate_radius_lambda(x, y, measures, radius, lam)
            q = ev["bestQ"]
            candidates.append({
                "pairRadius": int(radius),
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
            })
    candidates.sort(key=rank_key, reverse=True)
    return candidates[:TOP_K]


def normalized_scores(x_train: np.ndarray, x_test: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    train_scores = v2.scores_for(x_train, model)
    test_scores = v2.scores_for(x_test, model)
    mu = float(np.mean(train_scores)) if len(train_scores) else 0.0
    sd = float(np.std(train_scores)) if len(train_scores) else 1.0
    if sd < EPS:
        sd = 1.0
    return (test_scores - mu) / sd


def ensemble_scores(
    x_train: np.ndarray,
    y_train: np.ndarray,
    measures_train: np.ndarray,
    x_test: np.ndarray,
    specs: list[dict[str, Any]],
) -> tuple[np.ndarray, int]:
    parts: list[np.ndarray] = []
    pair_count = 0
    for spec in specs:
        model = v2.fit_pairwise_ranker(
            x_train,
            y_train,
            measures_train,
            int(spec["pairRadius"]),
            float(spec["lambda"]),
        )
        pair_count += int(model["pairCount"])
        parts.append(normalized_scores(x_train, x_test, model))
    if not parts:
        return np.zeros(len(x_test), dtype=np.float64), 0
    return np.mean(np.vstack(parts), axis=0), pair_count


def choose_ensemble_q(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    specs: list[dict[str, Any]],
) -> dict[str, Any]:
    by_q: list[dict[str, Any]] = []
    # Fit/score ensemble once per inner split, then grade every legal V5 q.
    split_cache: list[dict[str, Any]] = []
    for split_name, train, test in v1.inner_masks(measures):
        scores, pair_count = ensemble_scores(x[train], y[train], measures[train], x[test], specs)
        split_cache.append({
            "split": split_name,
            "family": split_family(split_name),
            "test": test,
            "scores": scores,
            "pairCount": pair_count,
        })

    for q in v5.TAIL_QUANTILES:
        folds: list[dict[str, Any]] = []
        for item in split_cache:
            test = item["test"]
            held = v1.select_top_fraction(item["scores"], y[test], q)
            base = v1.base_stats(y[test])
            lift = float(held["precision"]) - float(base["precision"])
            passed = held["true"] > 0 and lift >= 5.0
            folds.append({
                "split": item["split"],
                "family": item["family"],
                "pairCount": int(item["pairCount"]),
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
            "overallMeanLift": round(float(np.mean([float(f["lift"]) for f in folds])), 3) if folds else -999.0,
            "sectionPassCount": sum(bool(f["passed"]) for f in section),
            "sectionFoldCount": len(section),
            "sectionMeanLift": round(float(np.mean([float(f["lift"]) for f in section])), 3) if section else -999.0,
            "sectionTrue": sum(int(f["true"]) for f in section),
            "sectionFalse": sum(int(f["false"]) for f in section),
        })

    return max(
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
        specs = choose_top_models(x[train], y[train], measures[train])
        chosen_q = choose_ensemble_q(x[train], y[train], measures[train], specs)
        scores, pair_count = ensemble_scores(x[train], y[train], measures[train], x[test], specs)
        held = v1.select_top_fraction(scores, y[test], float(chosen_q["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "ensembleSize": len(specs),
            "baseModels": specs,
            "tailQuantile": float(chosen_q["tailQuantile"]),
            "innerSectionPassCount": int(chosen_q["sectionPassCount"]),
            "innerSectionFoldCount": int(chosen_q["sectionFoldCount"]),
            "innerSectionMeanLift": float(chosen_q["sectionMeanLift"]),
            "innerOverallPassCount": int(chosen_q["overallPassCount"]),
            "innerOverallFoldCount": int(chosen_q["overallFoldCount"]),
            "innerOverallMeanLift": float(chosen_q["overallMeanLift"]),
            "pairCountAcrossModels": int(pair_count),
            "scoreCombination": "mean-of-training-score-normalized-top3-pairwise-models",
            "operatingPointCalibration": "training-only-inner-contiguous-section-priority-v5-grid",
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": bool(passed),
        }
        rows.append(row)
        model_desc = ",".join(f"r{s['pairRadius']}/l{s['lambda']}" for s in specs)
        print(
            f"  ensemble=[{model_desc}] q={chosen_q['tailQuantile']} "
            f"innerSectionPass={chosen_q['sectionPassCount']}/{chosen_q['sectionFoldCount']} "
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
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V8 top-3 pairwise ensemble nested CV", flush=True)
    print("V5 q-grid/calibration retained; only ranking architecture changes to top-3 ensemble", flush=True)

    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass
    all_rows = normal + section + shifted
    total_passes = sum(bool(r["passed"]) for r in all_rows)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during V8 ensemble CV")

    output = {
        "schemaVersion": 8,
        "profileType": "36.76-patch-pairwise-rank-top3-ensemble-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "ensembleSize": TOP_K,
        "scoreCombination": "mean-of-training-score-normalized-top3-pairwise-models",
        "operatingPointCalibration": "training-only-inner-contiguous-section-priority-v5-grid",
        "outerFoldsPassed": total_passes,
        "outerFoldsTotal": len(all_rows),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankEnsembleV8Generalizes": generalizes,
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
        "schemaVersion": 8,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "outerFoldsPassed": total_passes,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankEnsembleV8Generalizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE RANK TOP-3 ENSEMBLE NESTED CV V8 COMPLETE")
    print("Outer folds passed:", total_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise-rank ensemble V8 generalizes:", generalizes)
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
