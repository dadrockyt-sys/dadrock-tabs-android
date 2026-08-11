from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_onset_slot_spectro_temporal_patch_ridge_nested_cv_v1 as ridge

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3

GATE_LAMBDAS = [1.0, 10.0, 100.0]
FINAL_LAMBDAS = [1.0, 10.0, 100.0]
SUPPORT_LEVELS = [2, 3, 4]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15]
TOP_K = 8
MIN_SIGN_CONSISTENCY = 0.75
MIN_FEATURES = 4
MAX_FEATURES = 24


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


def base_stats(y: np.ndarray) -> dict[str, Any]:
    t = int(np.sum(y))
    f = int(y.size - t)
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def apply_scores(scores: np.ndarray, y: np.ndarray, threshold: float) -> dict[str, Any]:
    chosen = scores >= threshold
    selected = int(np.sum(chosen))
    t = int(np.sum(y[chosen]))
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


def recurrent_gate(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
    gate_lambda: float,
    support: int,
) -> dict[str, Any]:
    splits = inner_masks(measures)
    counts: Counter[int] = Counter()
    sign_counts: dict[int, Counter[int]] = defaultdict(Counter)
    abs_weight_sum: Counter[int] = Counter()

    for _, train_mask, _ in splits:
        model = ridge.fit_ridge(x[train_mask], y[train_mask], gate_lambda)
        coef = model[0]
        order = np.argsort(np.abs(coef))[::-1][:TOP_K]
        for idx in order:
            j = int(idx)
            w = float(coef[j])
            counts[j] += 1
            sign_counts[j][1 if w >= 0.0 else -1] += 1
            abs_weight_sum[j] += abs(w)

    ranked: list[tuple[int, int, float, float]] = []
    for j, count in counts.items():
        dominant = max(sign_counts[j].values()) if sign_counts[j] else 0
        consistency = dominant / count if count else 0.0
        mean_abs = abs_weight_sum[j] / count if count else 0.0
        if count >= support and consistency >= MIN_SIGN_CONSISTENCY:
            ranked.append((j, count, consistency, mean_abs))

    ranked.sort(key=lambda z: (-z[1], -z[2], -z[3], feature_names[z[0]]))
    if len(ranked) < MIN_FEATURES:
        fallback = sorted(
            ((j, c, max(sign_counts[j].values()) / c if c else 0.0, abs_weight_sum[j] / c) for j, c in counts.items()),
            key=lambda z: (-z[1], -z[2], -z[3], feature_names[z[0]]),
        )
        seen = {j for j, *_ in ranked}
        for item in fallback:
            if item[0] not in seen:
                ranked.append(item)
                seen.add(item[0])
            if len(ranked) >= MIN_FEATURES:
                break

    ranked = ranked[:MAX_FEATURES]
    indices = [j for j, *_ in ranked]
    details = [
        {
            "feature": feature_names[j],
            "support": count,
            "signConsistency": round(consistency, 3),
            "meanAbsWeight": round(mean_abs, 6),
        }
        for j, count, consistency, mean_abs in ranked
    ]
    return {"indices": indices, "features": details, "splitCount": len(splits)}


def evaluate_inner_candidate(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    gate_indices: list[int],
    lam: float,
    q: float,
) -> dict[str, Any]:
    splits = inner_masks(measures)
    folds: list[dict[str, Any]] = []
    xx = x[:, gate_indices]
    for split_name, train_mask, test_mask in splits:
        model = ridge.fit_ridge(xx[train_mask], y[train_mask], lam)
        tr_scores = ridge.scores_for(xx[train_mask], model)
        threshold = float(np.quantile(tr_scores, 1.0 - q)) if tr_scores.size else float("inf")
        held = apply_scores(ridge.scores_for(xx[test_mask], model), y[test_mask], threshold)
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
    return {
        "folds": folds,
        "passCount": sum(bool(f["passed"]) for f in folds),
        "meanLift": round(sum(float(f["lift"]) for f in folds) / len(folds), 3) if folds else -999.0,
        "trueTotal": sum(int(f["true"]) for f in folds),
        "falseTotal": sum(int(f["false"]) for f in folds),
    }


def choose_outer_train_model(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    feature_names: list[str],
) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    total = len(GATE_LAMBDAS) * len(SUPPORT_LEVELS) * len(FINAL_LAMBDAS) * len(TAIL_QUANTILES)
    done = 0

    gate_cache: dict[tuple[float, int], dict[str, Any]] = {}
    for gate_lambda in GATE_LAMBDAS:
        for support in SUPPORT_LEVELS:
            gate_cache[(gate_lambda, support)] = recurrent_gate(
                x, y, measures, feature_names, gate_lambda, support
            )

    for gate_lambda in GATE_LAMBDAS:
        for support in SUPPORT_LEVELS:
            gate = gate_cache[(gate_lambda, support)]
            indices = list(gate["indices"])
            if not indices:
                continue
            for lam in FINAL_LAMBDAS:
                for q in TAIL_QUANTILES:
                    done += 1
                    if done == 1 or done % 18 == 0 or done == total:
                        print(f"    heartbeat recurrent-gate search {done}/{total}", flush=True)
                    ev = evaluate_inner_candidate(x, y, measures, indices, lam, q)
                    candidates.append({
                        "gateLambda": gate_lambda,
                        "support": support,
                        "lambda": lam,
                        "tailQuantile": q,
                        "featureCount": len(indices),
                        "features": gate["features"],
                        "innerPassCount": ev["passCount"],
                        "innerFoldCount": len(ev["folds"]),
                        "meanLift": ev["meanLift"],
                        "innerTrue": ev["trueTotal"],
                        "innerFalse": ev["falseTotal"],
                        "folds": ev["folds"],
                    })

    if not candidates:
        raise RuntimeError("No recurrent-gate candidates were available")

    return max(
        candidates,
        key=lambda r: (
            int(r["innerPassCount"]),
            float(r["meanLift"]),
            int(r["innerTrue"]) - int(r["innerFalse"]),
            int(r["innerTrue"]),
            -int(r["featureCount"]),
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
    pass_count = 0

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test_mask = ids == fold
        train_mask = ~test_mask
        chosen = choose_outer_train_model(
            x[train_mask], y[train_mask], measures[train_mask], feature_names
        )

        final_gate = recurrent_gate(
            x[train_mask],
            y[train_mask],
            measures[train_mask],
            feature_names,
            float(chosen["gateLambda"]),
            int(chosen["support"]),
        )
        indices = list(final_gate["indices"])
        lam = float(chosen["lambda"])
        q = float(chosen["tailQuantile"])
        model = ridge.fit_ridge(x[train_mask][:, indices], y[train_mask], lam)
        tr_scores = ridge.scores_for(x[train_mask][:, indices], model)
        threshold = float(np.quantile(tr_scores, 1.0 - q)) if tr_scores.size else float("inf")
        held = apply_scores(
            ridge.scores_for(x[test_mask][:, indices], model), y[test_mask], threshold
        )
        base = base_stats(y[test_mask])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)

        local_names = [feature_names[j] for j in indices]
        weights = ridge.top_weights(local_names, model[0], n=min(8, len(local_names)))
        row = {
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train_mask)),
            "testRows": int(np.sum(test_mask)),
            "chosen": chosen,
            "featureGate": final_gate["features"],
            "lambda": lam,
            "tailQuantile": q,
            "threshold": threshold,
            "topWeights": weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        }
        rows.append(row)
        print(
            f"  gateLambda={chosen['gateLambda']} support={chosen['support']} features={len(indices)} "
            f"lambda={lam} q={q} held={held['true']}/{held['false']} precision={held['precision']} "
            f"base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )
        print("  gateTop=", final_gate["features"][:6], flush=True)

    return pass_count == OUTER_FOLDS, rows


def main() -> None:
    before = sha256(ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH)
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

    print("Starting recurrent-feature-gated patch ridge nested CV V1", flush=True)
    print("Patch features:", len(feature_names), flush=True)
    normal_pass, normal = evaluate_scheme(
        x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS
    )
    section_pass, section = evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "section",
        lambda m: contiguous_fold(m, lo, hi, OUTER_FOLDS),
    )
    shifted_pass, shifted = evaluate_scheme(
        x,
        y,
        measures,
        feature_names,
        "shiftedWindow",
        lambda m: shifted_fold(m, lo, hi, OUTER_FOLDS),
    )
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during recurrent feature gate CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-recurrent-feature-gate-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "recurrentFeatureGateGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Recurrent patch features are discovered from outer-training data via inner normal/section/shifted ridge fits. Gate support, ridge regularization, and recovery threshold are selected from outer-training data only. Outer held-out labels are grading only. No pitch recovery or champion promotion allowed.",
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
    MANIFEST_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "output": str(OUTPUT_PATH.relative_to(ROOT)),
                "candidateSha256": after,
                "recurrentFeatureGateGeneralizes": generalizes,
                "validatedNewChampion": False,
                "productionPromotionAllowed": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("GOMYWAY 36.76 PATCH RIDGE RECURRENT FEATURE GATE NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Recurrent feature gate generalizes:", generalizes)
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
