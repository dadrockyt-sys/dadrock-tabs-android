from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_ridge_recurrent_feature_gate_nested_cv_v1 as recurrent

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-pairwise-rank-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
PAIR_RADII = [2, 4, 8]
LAMBDAS = [1.0, 10.0, 100.0]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15]
MAX_PAIRS = 6000
EPS = 1e-8


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def contiguous_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    return min(folds - 1, int(folds * (measure - lo) / span))


def shifted_fold(measure: int, lo: int, hi: int, folds: int) -> int:
    span = max(1, hi - lo + 1)
    width = span / folds
    pos = ((measure - lo) + width / 2.0) % span
    return min(folds - 1, int(pos / width))


def inner_masks(measures: np.ndarray) -> list[tuple[str, np.ndarray, np.ndarray]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    out: list[tuple[str, np.ndarray, np.ndarray]] = []
    for name, fn in schemes:
        ids = np.asarray([fn(int(m)) for m in measures], dtype=np.int16)
        for fold in range(INNER_FOLDS):
            test = ids == fold
            train = ~test
            if np.any(train) and np.any(test):
                out.append((f"{name}:{fold}", train, test))
    return out


def fit_pairwise_ranker(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    radius: int,
    lam: float,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < EPS, 1.0, scale)
    z = (x - mean) / scale

    pos = np.flatnonzero(y)
    neg = np.flatnonzero(~y)
    pairs: list[tuple[int, int]] = []
    for i in pos:
        near = neg[np.abs(measures[neg] - measures[i]) <= radius]
        for j in near:
            pairs.append((int(i), int(j)))
            if len(pairs) >= MAX_PAIRS:
                break
        if len(pairs) >= MAX_PAIRS:
            break

    if len(pairs) < 20:
        # Deterministic global fallback, still training labels only.
        pairs = []
        for i in pos:
            for j in neg:
                pairs.append((int(i), int(j)))
                if len(pairs) >= MAX_PAIRS:
                    break
            if len(pairs) >= MAX_PAIRS:
                break

    if not pairs:
        return {"mean": mean, "scale": scale, "coef": np.zeros(x.shape[1]), "pairCount": 0}

    d = np.asarray([z[i] - z[j] for i, j in pairs], dtype=np.float64)
    # Add reversed pairs so the least-squares target is centered and intercept-free.
    a = np.vstack([d, -d])
    target = np.concatenate([np.ones(len(d)), -np.ones(len(d))])
    gram = a.T @ a
    rhs = a.T @ target
    coef = np.linalg.solve(gram + lam * np.eye(gram.shape[0]), rhs)
    return {"mean": mean, "scale": scale, "coef": coef, "pairCount": len(pairs)}


def scores_for(x: np.ndarray, model: dict[str, Any]) -> np.ndarray:
    z = (x - model["mean"]) / model["scale"]
    return z @ model["coef"]


def select_top_fraction(scores: np.ndarray, y: np.ndarray, q: float) -> dict[str, Any]:
    n = int(scores.size)
    k = max(1, int(round(q * n))) if n else 0
    if k == 0:
        return {"selected": 0, "true": 0, "false": 0, "precision": 0.0, "selectedPct": 0.0}
    order = np.argsort(scores)[::-1]
    chosen = order[:k]
    t = int(np.sum(y[chosen]))
    f = int(k - t)
    return {
        "selected": k,
        "true": t,
        "false": f,
        "precision": round(precision(t, f), 2),
        "selectedPct": round(100.0 * k / n, 2),
    }


def base_stats(y: np.ndarray) -> dict[str, Any]:
    t = int(np.sum(y))
    f = int(y.size - t)
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def evaluate_inner_candidate(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    radius: int,
    lam: float,
    q: float,
) -> dict[str, Any]:
    folds: list[dict[str, Any]] = []
    for split_name, train, test in inner_masks(measures):
        model = fit_pairwise_ranker(x[train], y[train], measures[train], radius, lam)
        held = select_top_fraction(scores_for(x[test], model), y[test], q)
        base = base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        folds.append({
            "split": split_name,
            "pairCount": int(model["pairCount"]),
            "true": held["true"],
            "false": held["false"],
            "precision": held["precision"],
            "selectedPct": held["selectedPct"],
            "basePrecision": base["precision"],
            "lift": round(lift, 2),
            "passed": passed,
        })
    return {
        "folds": folds,
        "passCount": sum(bool(f["passed"]) for f in folds),
        "meanLift": round(float(np.mean([f["lift"] for f in folds])), 3) if folds else -999.0,
        "trueTotal": sum(int(f["true"]) for f in folds),
        "falseTotal": sum(int(f["false"]) for f in folds),
    }


def choose_model(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(PAIR_RADII) * len(LAMBDAS) * len(TAIL_QUANTILES)
    done = 0
    for radius in PAIR_RADII:
        for lam in LAMBDAS:
            for q in TAIL_QUANTILES:
                done += 1
                if done == 1 or done % 12 == 0 or done == total:
                    print(f"    heartbeat pairwise-rank search {done}/{total}", flush=True)
                ev = evaluate_inner_candidate(x, y, measures, radius, lam, q)
                candidates.append({
                    "pairRadius": radius,
                    "lambda": lam,
                    "tailQuantile": q,
                    "innerPassCount": ev["passCount"],
                    "innerFoldCount": len(ev["folds"]),
                    "meanLift": ev["meanLift"],
                    "innerTrue": ev["trueTotal"],
                    "innerFalse": ev["falseTotal"],
                    "folds": ev["folds"],
                })
    return max(
        candidates,
        key=lambda r: (
            int(r["innerPassCount"]),
            float(r["meanLift"]),
            int(r["innerTrue"]) - int(r["innerFalse"]),
            int(r["innerTrue"]),
            -float(r["tailQuantile"]),
            -float(r["lambda"]),
            -int(r["pairRadius"]),
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
        model = fit_pairwise_ranker(
            x[train], y[train], measures[train],
            int(chosen["pairRadius"]), float(chosen["lambda"]),
        )
        held = select_top_fraction(scores_for(x[test], model), y[test], float(chosen["tailQuantile"]))
        base = base_stats(y[test])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passes += int(passed)
        coef = np.asarray(model["coef"])
        top_idx = np.argsort(np.abs(coef))[::-1][:8]
        top_weights = [
            {"feature": feature_names[int(j)], "weight": round(float(coef[int(j)]), 6)}
            for j in top_idx
        ]
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train)),
            "testRows": int(np.sum(test)),
            "chosen": chosen,
            "pairCount": int(model["pairCount"]),
            "topWeights": top_weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        rows.append(row)
        print(
            f"  radius={chosen['pairRadius']} lambda={chosen['lambda']} q={chosen['tailQuantile']} "
            f"pairs={model['pairCount']} held={held['true']}/{held['false']} "
            f"selectedPct={held['selectedPct']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
    return passes == OUTER_FOLDS, rows


def main() -> None:
    candidate_path = recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
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

    print("Starting strict pairwise-ranking spectro-temporal patch nested CV V1", flush=True)
    print("Patch features:", len(feature_names), flush=True)
    print("Pair radii:", PAIR_RADII, "lambdas:", LAMBDAS, "tail quantiles:", TAIL_QUANTILES, flush=True)

    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during pairwise-rank CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-pairwise-rank-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "featureCount": len(feature_names),
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchGeneralizes": generalizes,
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
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "normalCvPassed": normal_pass,
        "sectionStabilityPassed": section_pass,
        "shiftedWindowStabilityPassed": shifted_pass,
        "pairwiseRankPatchGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH PAIRWISE RANK NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Pairwise-rank patch generalizes:", generalizes)
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
