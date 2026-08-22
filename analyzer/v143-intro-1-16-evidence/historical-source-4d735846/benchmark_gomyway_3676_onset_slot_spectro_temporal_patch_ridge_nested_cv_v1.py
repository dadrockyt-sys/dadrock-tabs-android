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
OUTPUT_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-ridge-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-ridge-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
LAMBDAS = [0.1, 1.0, 10.0, 100.0]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15]
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


def base_stats(labels: np.ndarray) -> dict[str, Any]:
    t = int(np.sum(labels))
    f = int(labels.size - t)
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def standardize_fit(x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < EPS, 1.0, scale)
    return mean, scale


def standardize_apply(x: np.ndarray, mean: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return (x - mean) / scale


def fit_ridge(x: np.ndarray, y: np.ndarray, lam: float) -> tuple[np.ndarray, float, np.ndarray, np.ndarray]:
    mean, scale = standardize_fit(x)
    z = standardize_apply(x, mean, scale)
    y_float = y.astype(np.float64)

    # Balance true/false training influence without exposing held-out labels.
    n_true = max(1, int(np.sum(y)))
    n_false = max(1, int(y.size - np.sum(y)))
    weights = np.where(y, 0.5 / n_true, 0.5 / n_false) * y.size

    z_aug = np.column_stack([np.ones(z.shape[0], dtype=np.float64), z])
    sw = np.sqrt(weights)[:, None]
    zw = z_aug * sw
    yw = y_float * sw[:, 0]
    reg = np.eye(z_aug.shape[1], dtype=np.float64) * float(lam)
    reg[0, 0] = 0.0
    lhs = zw.T @ zw + reg
    rhs = zw.T @ yw
    beta = np.linalg.solve(lhs, rhs)
    return beta[1:], float(beta[0]), mean, scale


def scores_for(x: np.ndarray, model: tuple[np.ndarray, float, np.ndarray, np.ndarray]) -> np.ndarray:
    coef, intercept, mean, scale = model
    return standardize_apply(x, mean, scale) @ coef + intercept


def apply_scores(scores: np.ndarray, labels: np.ndarray, threshold: float) -> dict[str, Any]:
    chosen = scores >= threshold
    selected = int(np.sum(chosen))
    t = int(np.sum(labels[chosen]))
    f = selected - t
    return {"selected": selected, "true": t, "false": f, "precision": round(precision(t, f), 2)}


def inner_masks(measures: np.ndarray) -> list[tuple[str, np.ndarray, np.ndarray]]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    schemes: list[tuple[str, Callable[[int], int]]] = [
        ("normal", lambda m: m % INNER_FOLDS),
        ("section", lambda m: contiguous_fold(m, lo, hi, INNER_FOLDS)),
        ("shifted", lambda m: shifted_fold(m, lo, hi, INNER_FOLDS)),
    ]
    out: list[tuple[str, np.ndarray, np.ndarray]] = []
    for name, fold_fn in schemes:
        ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
        for fold in range(INNER_FOLDS):
            test = ids == fold
            train = ~test
            if np.any(train) and np.any(test):
                out.append((f"{name}:{fold}", train, test))
    return out


def choose_hyperparameters(x: np.ndarray, y: np.ndarray, measures: np.ndarray) -> dict[str, Any]:
    splits = inner_masks(measures)
    candidates: list[dict[str, Any]] = []
    total = len(LAMBDAS) * len(TAIL_QUANTILES)
    done = 0
    for lam in LAMBDAS:
        for q in TAIL_QUANTILES:
            done += 1
            print(f"    heartbeat patch-ridge search {done}/{total}", flush=True)
            folds: list[dict[str, Any]] = []
            for split_name, train_mask, test_mask in splits:
                model = fit_ridge(x[train_mask], y[train_mask], lam)
                tr_scores = scores_for(x[train_mask], model)
                threshold = float(np.quantile(tr_scores, 1.0 - q)) if tr_scores.size else float("inf")
                held = apply_scores(scores_for(x[test_mask], model), y[test_mask], threshold)
                base = base_stats(y[test_mask])
                lift = float(held["precision"]) - float(base["precision"])
                passed = held["true"] > 0 and lift >= 5.0
                folds.append({
                    "split": split_name,
                    "true": held["true"],
                    "false": held["false"],
                    "precision": held["precision"],
                    "basePrecision": base["precision"],
                    "lift": round(lift, 2),
                    "passed": passed,
                })
            pass_count = sum(bool(r["passed"]) for r in folds)
            mean_lift = sum(float(r["lift"]) for r in folds) / len(folds) if folds else -999.0
            true_total = sum(int(r["true"]) for r in folds)
            false_total = sum(int(r["false"]) for r in folds)
            candidates.append({
                "lambda": lam,
                "tailQuantile": q,
                "innerPassCount": pass_count,
                "innerFoldCount": len(folds),
                "meanLift": round(mean_lift, 3),
                "innerTrue": true_total,
                "innerFalse": false_total,
                "folds": folds,
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
        ),
    )


def top_weights(feature_names: list[str], coef: np.ndarray, n: int = 8) -> list[dict[str, Any]]:
    order = np.argsort(np.abs(coef))[::-1][:n]
    return [{"feature": feature_names[int(i)], "weight": round(float(coef[int(i)]), 6)} for i in order]


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
    name: str,
    fold_fn: Callable[[int], int],
) -> tuple[bool, list[dict[str, Any]]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    out: list[dict[str, Any]] = []
    pass_count = 0
    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test_mask = ids == fold
        train_mask = ~test_mask
        chosen = choose_hyperparameters(x[train_mask], y[train_mask], measures[train_mask])
        lam = float(chosen["lambda"])
        q = float(chosen["tailQuantile"])
        model = fit_ridge(x[train_mask], y[train_mask], lam)
        tr_scores = scores_for(x[train_mask], model)
        threshold = float(np.quantile(tr_scores, 1.0 - q)) if tr_scores.size else float("inf")
        held = apply_scores(scores_for(x[test_mask], model), y[test_mask], threshold)
        base = base_stats(y[test_mask])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)
        weights = top_weights(feature_names, model[0])
        out.append({
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train_mask)),
            "testRows": int(np.sum(test_mask)),
            "chosen": chosen,
            "lambda": lam,
            "tailQuantile": q,
            "threshold": threshold,
            "topWeights": weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        })
        print(
            f"  lambda={lam} q={q} held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed} top={weights[:3]}",
            flush=True,
        )
    return pass_count == OUTER_FOLDS, out


def main() -> None:
    before = sha256(patch.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing; run the patch stability profiler first")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting strict nested spectro-temporal patch RIDGE CV V1", flush=True)
    print("Patch features:", len(feature_names), flush=True)
    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(patch.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during patch ridge nested CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-onset-slot-spectro-temporal-patch-ridge-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "featureCount": len(feature_names),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "spectroTemporalPatchRidgeGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Standardization, class-balanced ridge weights, regularization, and recovery threshold are learned using training data only inside each outer fold. Held-out labels are grading only. No pitch recovery or champion promotion allowed.",
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
        "spectroTemporalPatchRidgeGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 ONSET SLOT SPECTRO TEMPORAL PATCH RIDGE NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Spectro-temporal patch ridge generalizes:", generalizes)
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
