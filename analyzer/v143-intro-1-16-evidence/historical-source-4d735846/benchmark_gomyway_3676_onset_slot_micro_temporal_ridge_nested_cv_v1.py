from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import profile_gomyway_3676_onset_slot_micro_temporal_shape_stability_v1 as micro

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-micro-temporal-shape-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-micro-temporal-ridge-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-micro-temporal-ridge-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
FEATURES = list(micro.FEATURES)
LAMBDAS = [0.1, 1.0, 10.0]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15, 0.20, 0.25]


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


def matrix(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in FEATURES] for r in rows], dtype=np.float64)


def labels(rows: list[dict[str, Any]]) -> np.ndarray:
    return np.asarray([1.0 if str(r.get("label")) == "true" else -1.0 for r in rows], dtype=np.float64)


def fit_model(rows: list[dict[str, Any]], lam: float) -> dict[str, Any]:
    x = matrix(rows)
    y = labels(rows)
    mean = np.mean(x, axis=0)
    std = np.std(x, axis=0)
    std = np.where(std < 1e-8, 1.0, std)
    z = (x - mean) / std

    pos = max(1, int(np.sum(y > 0)))
    neg = max(1, int(np.sum(y < 0)))
    w_pos = len(y) / (2.0 * pos)
    w_neg = len(y) / (2.0 * neg)
    weights = np.where(y > 0, w_pos, w_neg)
    sw = np.sqrt(weights)[:, None]
    zw = z * sw
    yw = y * sw[:, 0]

    gram = zw.T @ zw + float(lam) * np.eye(z.shape[1], dtype=np.float64)
    rhs = zw.T @ yw
    try:
        beta = np.linalg.solve(gram, rhs)
    except np.linalg.LinAlgError:
        beta = np.linalg.pinv(gram) @ rhs
    return {"mean": mean, "std": std, "beta": beta, "lambda": float(lam)}


def score(rows: list[dict[str, Any]], model: dict[str, Any]) -> np.ndarray:
    x = matrix(rows)
    z = (x - model["mean"]) / model["std"]
    return z @ model["beta"]


def threshold_for(rows: list[dict[str, Any]], model: dict[str, Any], q: float) -> float:
    s = score(rows, model)
    return float(np.quantile(s, 1.0 - q)) if s.size else float("inf")


def apply(rows: list[dict[str, Any]], model: dict[str, Any], threshold: float) -> dict[str, Any]:
    s = score(rows, model)
    mask = s >= threshold
    chosen = [r for r, keep in zip(rows, mask) if bool(keep)]
    t = sum(str(r.get("label")) == "true" for r in chosen)
    f = len(chosen) - t
    return {"selected": len(chosen), "true": t, "false": f, "precision": round(precision(t, f), 2)}


def base_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    t = sum(str(r.get("label")) == "true" for r in rows)
    f = len(rows) - t
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def inner_splits(train: list[dict[str, Any]]) -> list[tuple[str, list[dict[str, Any]], list[dict[str, Any]]]]:
    measures = [int(r["measure"]) for r in train]
    lo, hi = min(measures), max(measures)
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    out = []
    for name, fn in schemes:
        for fold in range(INNER_FOLDS):
            tr = [r for r in train if fn(int(r["measure"])) != fold]
            te = [r for r in train if fn(int(r["measure"])) == fold]
            if tr and te:
                out.append((f"{name}:{fold}", tr, te))
    return out


def choose_hyperparameters(train: list[dict[str, Any]]) -> dict[str, Any]:
    splits = inner_splits(train)
    candidates = []
    total = len(LAMBDAS) * len(TAIL_QUANTILES)
    done = 0
    for lam in LAMBDAS:
        for q in TAIL_QUANTILES:
            done += 1
            print(f"    heartbeat micro-ridge search {done}/{total}", flush=True)
            folds = []
            for split_name, tr, te in splits:
                model = fit_model(tr, lam)
                threshold = threshold_for(tr, model, q)
                held = apply(te, model, threshold)
                base = base_stats(te)
                lift = float(held["precision"]) - float(base["precision"])
                passed = held["true"] > 0 and lift >= 5.0
                folds.append({"split": split_name, "true": held["true"], "false": held["false"], "precision": held["precision"], "basePrecision": base["precision"], "lift": round(lift, 2), "passed": passed})
            pass_count = sum(bool(x["passed"]) for x in folds)
            mean_lift = sum(float(x["lift"]) for x in folds) / len(folds) if folds else -999.0
            true_total = sum(int(x["true"]) for x in folds)
            false_total = sum(int(x["false"]) for x in folds)
            candidates.append({"lambda": lam, "tailQuantile": q, "innerPassCount": pass_count, "innerFoldCount": len(folds), "meanLift": round(mean_lift, 3), "innerTrue": true_total, "innerFalse": false_total, "folds": folds})
    return max(candidates, key=lambda r: (int(r["innerPassCount"]), float(r["meanLift"]), int(r["innerTrue"]) - int(r["innerFalse"]), int(r["innerTrue"]), -float(r["tailQuantile"]), -float(r["lambda"])))


def evaluate_scheme(rows: list[dict[str, Any]], name: str, fold_fn: Callable[[int], int]) -> tuple[bool, list[dict[str, Any]]]:
    out = []
    passed_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        train = [r for r in rows if fold_fn(int(r["measure"])) != fold]
        test = [r for r in rows if fold_fn(int(r["measure"])) == fold]
        chosen = choose_hyperparameters(train)
        lam = float(chosen["lambda"])
        q = float(chosen["tailQuantile"])
        model = fit_model(train, lam)
        threshold = threshold_for(train, model, q)
        held = apply(test, model, threshold)
        base = base_stats(test)
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        passed_count += int(passed)
        top = np.argsort(np.abs(model["beta"]))[::-1][:5]
        top_weights = [{"feature": FEATURES[int(i)], "weight": round(float(model["beta"][int(i)]), 5)} for i in top]
        out.append({"scheme": name, "fold": fold, "trainRows": len(train), "testRows": len(test), "chosen": chosen, "lambda": lam, "tailQuantile": q, "threshold": threshold, "topWeights": top_weights, "heldoutBase": base, "heldoutCandidate": held, "heldoutPrecisionLift": round(lift, 2), "passed": passed})
        print(f"  lambda={lam} q={q} held={held['true']}/{held['false']} precision={held['precision']} base={base['precision']} lift={round(lift,2)} pass={passed} top={top_weights[:3]}", flush=True)
    return passed_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(micro.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Micro-temporal candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Micro-temporal source is not anchored to frozen 36.76 champion")

    measures = [int(r["measure"]) for r in rows]
    lo, hi = min(measures), max(measures)
    print("Starting strict nested micro-temporal ridge CV V1", flush=True)
    normal_pass, normal = evaluate_scheme(rows, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(rows, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(rows, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(micro.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during micro-temporal ridge nested CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-micro-temporal-ridge-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "features": FEATURES,
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "microTemporalRidgeGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Scaling, ridge weights, regularization, and tail threshold are learned from training data only. Held-out labels are grading only.",
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
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps({"schemaVersion": 1, "output": str(OUTPUT_PATH.relative_to(ROOT)), "candidateSha256": after, "microTemporalRidgeGeneralizes": generalizes, "validatedNewChampion": False, "productionPromotionAllowed": False}, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT MICRO TEMPORAL RIDGE NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Micro-temporal ridge generalizes:", generalizes)
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
