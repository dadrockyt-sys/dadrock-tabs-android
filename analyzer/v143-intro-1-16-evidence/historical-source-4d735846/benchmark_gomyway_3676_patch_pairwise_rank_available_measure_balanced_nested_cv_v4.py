from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-available-measure-balanced-nested-cv-v4.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-available-measure-balanced-nested-cv-v4-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
PAIR_RADII = [2, 4, 8]
LAMBDAS = [1.0, 10.0, 100.0]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15]
MAX_PAIRS = 6000
STRATA = 8
EPS = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def available_measure_balanced_pairs(y: np.ndarray, measures: np.ndarray, radius: int) -> list[tuple[int, int]]:
    """Build local true-vs-false pairs, then balance the cap across actual available positive measures.

    Unlike V2's fixed numeric min->max buckets, this creates strata by splitting the sorted
    unique positive measures that are actually present in the current training fold. This avoids
    wasting pair quota on a held-out contiguous section gap.
    """
    pos = np.flatnonzero(y)
    neg = np.flatnonzero(~y)
    by_measure: dict[int, list[tuple[int, int]]] = {}
    for i in pos:
        pm = int(measures[i])
        near = neg[np.abs(measures[neg] - pm) <= radius]
        if near.size:
            by_measure.setdefault(pm, []).extend((int(i), int(j)) for j in near)

    all_pairs = [p for m in sorted(by_measure) for p in by_measure[m]]
    if len(all_pairs) < 20:
        all_pairs = [(int(i), int(j)) for i in pos for j in neg]
        by_measure = {}
        for p in all_pairs:
            by_measure.setdefault(int(measures[p[0]]), []).append(p)
    if len(all_pairs) <= MAX_PAIRS:
        return all_pairs

    positive_measures = np.asarray(sorted(by_measure), dtype=np.int32)
    measure_groups = [g.tolist() for g in np.array_split(positive_measures, min(STRATA, len(positive_measures))) if len(g)]
    strata: list[list[tuple[int, int]]] = []
    for group in measure_groups:
        bucket: list[tuple[int, int]] = []
        for m in group:
            bucket.extend(by_measure[int(m)])
        strata.append(bucket)

    chosen: list[tuple[int, int]] = []
    quota = MAX_PAIRS // max(1, len(strata))
    leftovers: list[tuple[int, int]] = []
    for bucket in strata:
        if len(bucket) <= quota:
            chosen.extend(bucket)
            continue
        idx = np.linspace(0, len(bucket) - 1, quota, dtype=int)
        used = set(int(k) for k in idx)
        chosen.extend(bucket[int(k)] for k in idx)
        leftovers.extend(bucket[k] for k in range(len(bucket)) if k not in used)

    if len(chosen) < MAX_PAIRS and leftovers:
        need = MAX_PAIRS - len(chosen)
        if len(leftovers) <= need:
            chosen.extend(leftovers)
        else:
            idx = np.linspace(0, len(leftovers) - 1, need, dtype=int)
            chosen.extend(leftovers[int(k)] for k in idx)
    return chosen[:MAX_PAIRS]


def fit_pairwise_ranker(x: np.ndarray, y: np.ndarray, measures: np.ndarray, radius: int, lam: float) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < EPS, 1.0, scale)
    z = (x - mean) / scale
    pairs = available_measure_balanced_pairs(y, measures, radius)
    if not pairs:
        return {"mean": mean, "scale": scale, "coef": np.zeros(x.shape[1]), "pairCount": 0}
    d = np.asarray([z[i] - z[j] for i, j in pairs], dtype=np.float64)
    a = np.vstack([d, -d])
    target = np.concatenate([np.ones(len(d)), -np.ones(len(d))])
    gram = a.T @ a
    rhs = a.T @ target
    coef = np.linalg.solve(gram + lam * np.eye(gram.shape[0]), rhs)
    return {"mean": mean, "scale": scale, "coef": coef, "pairCount": len(pairs)}


def scores_for(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    return ((x - model["mean"]) / model["scale"]) @ model["coef"]


def evaluate_inner_candidate(x: np.ndarray, y: np.ndarray, measures: np.ndarray, radius: int, lam: float, q: float) -> dict[str, Any]:
    folds: list[dict[str, Any]] = []
    for split_name, train, test in v1.inner_masks(measures):
        model = fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        held = v1.select_top_fraction(scores_for(x[test], model), y[test], q)
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        folds.append({"split": split_name, "pairCount": int(model["pairCount"]), "true": held["true"], "false": held["false"], "precision": held["precision"], "selectedPct": held["selectedPct"], "basePrecision": base["precision"], "lift": round(lift, 2), "passed": passed})
    return {"folds": folds, "passCount": sum(bool(f["passed"]) for f in folds), "meanLift": round(float(np.mean([f["lift"] for f in folds])), 3) if folds else -999.0, "trueTotal": sum(int(f["true"]) for f in folds), "falseTotal": sum(int(f["false"]) for f in folds)}


def choose_model(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(PAIR_RADII) * len(LAMBDAS) * len(TAIL_QUANTILES)
    done = 0
    for radius in PAIR_RADII:
        for lam in LAMBDAS:
            for q in TAIL_QUANTILES:
                done += 1
                if done == 1 or done % 12 == 0 or done == total:
                    print(f"    heartbeat available-measure pair search {done}/{total}", flush=True)
                ev = evaluate_inner_candidate(x, y, measures, radius, lam, q)
                candidates.append({"pairRadius": radius, "lambda": lam, "tailQuantile": q, "innerPassCount": ev["passCount"], "innerFoldCount": len(ev["folds"]), "meanLift": ev["meanLift"], "innerTrue": ev["trueTotal"], "innerFalse": ev["falseTotal"], "folds": ev["folds"]})
    return max(candidates, key=lambda r: (int(r["innerPassCount"]), float(r["meanLift"]), int(r["innerTrue"]) - int(r["innerFalse"]), int(r["innerTrue"]), -float(r["tailQuantile"]), -float(r["lambda"]), -int(r["pairRadius"])))


def evaluate_scheme(x: np.ndarray, y: np.ndarray, measures: np.ndarray, feature_names: list[str], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []
    passes = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        chosen = choose_model(x[train], y[train], measures[train])
        model = fit_pairwise_ranker(x[train], y[train], measures[train], int(chosen["pairRadius"]), float(chosen["lambda"]))
        held = v1.select_top_fraction(scores_for(x[test], model), y[test], float(chosen["tailQuantile"]))
        base = v1.base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)
        coef = np.asarray(model["coef"])
        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [{"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)} for j in top_idx]
        rows.append({"scheme": name, "fold": fold, "trainRows": int(np.sum(train)), "testRows": int(np.sum(test)), "chosen": chosen, "pairCount": int(model["pairCount"]), "sampler": "available-positive-measure-balanced", "topWeights": top_weights, "heldoutBase": base, "heldoutCandidate": held, "heldoutPrecisionLift": round(lift, 2), "passed": passed})
        print(f"  radius={chosen['pairRadius']} lambda={chosen['lambda']} q={chosen['tailQuantile']} pairs={model['pairCount']} held={held['true']}/{held['false']} selectedPct={held['selectedPct']} precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed}", flush=True)
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
    print("Starting available-positive-measure-balanced pairwise-ranking patch nested CV V4", flush=True)
    print("Sampler: actual available positive measures; max pairs:", MAX_PAIRS, "strata:", STRATA, flush=True)
    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass
    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during available-measure-balanced pairwise CV")
    all_rows = normal + section + shifted
    outer_passes = sum(bool(r.get("passed")) for r in all_rows)
    output = {"schemaVersion": 4, "profileType": "36.76-patch-pairwise-rank-available-positive-measure-balanced-nested-cv-exploratory", "baselinePitchF1": EXPECTED_F1, "baselineMatchedMissingExtra": list(EXPECTED), "pairSampler": "available-positive-measure-balanced", "maxPairs": MAX_PAIRS, "strata": STRATA, "outerFoldsPassed": outer_passes, "outerFoldCount": len(all_rows), "normalCvPassed": normal_pass, "sectionStabilityPassed": section_pass, "shiftedWindowStabilityPassed": shifted_pass, "pairwiseRankPatchV4Generalizes": generalizes, "normal": normal, "section": section, "shiftedWindow": shifted, "validatedNewChampion": False, "professionalReferenceUsedDuringDetection": False, "professionalReferenceRole": "downstream-grading-training-label-validation-only", "protected949CandidateHashUnchanged": before == after, "candidateEventsModified": False, "v7EventsModified": False, "rendererModified": False, "protectedBaselinesChanged": False, "productionSeparatorChanged": False, "productionPromotionAllowed": False}
    manifest = {"schemaVersion": 4, "output": str(OUTPUT_PATH.relative_to(ROOT)), "outerFoldsPassed": outer_passes, "normalCvPassed": normal_pass, "sectionStabilityPassed": section_pass, "shiftedWindowStabilityPassed": shifted_pass, "pairwiseRankPatchV4Generalizes": generalizes, "validatedNewChampion": False, "productionPromotionAllowed": False}
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print("GOMYWAY 36.76 PATCH AVAILABLE-MEASURE BALANCED PAIRWISE RANK NESTED CV V4 COMPLETE")
    print("Outer folds passed:", outer_passes, "/", len(all_rows))
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise-rank patch V4 generalizes:", generalizes)
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
