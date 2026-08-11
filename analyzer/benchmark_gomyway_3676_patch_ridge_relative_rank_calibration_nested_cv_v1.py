from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_ridge_recurrent_feature_gate_nested_cv_v1 as recur

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5

GATE_LAMBDAS = [1.0, 10.0, 100.0]
SUPPORT_LEVELS = [2, 3, 4]
FINAL_LAMBDAS = [1.0, 10.0, 100.0]
TAIL_QUANTILES = [0.05, 0.075, 0.10, 0.15]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision(t: int, f: int) -> float:
    return 100.0 * t / (t + f) if t + f else 0.0


def base_stats(y: np.ndarray) -> dict[str, Any]:
    t = int(np.sum(y))
    f = int(y.size - t)
    return {"true": t, "false": f, "precision": round(precision(t, f), 2)}


def rank_apply(scores: np.ndarray, y: np.ndarray, q: float) -> dict[str, Any]:
    """Select the top q fraction using only the unlabeled score distribution."""
    if scores.size == 0:
        return {"selected": 0, "true": 0, "false": 0, "precision": 0.0, "selectedPct": 0.0}
    threshold = float(np.quantile(scores, 1.0 - q))
    chosen = scores >= threshold
    selected = int(np.sum(chosen))
    t = int(np.sum(y[chosen]))
    f = selected - t
    return {
        "selected": selected,
        "true": t,
        "false": f,
        "precision": round(precision(t, f), 2),
        "selectedPct": round(100.0 * selected / scores.size, 2),
    }


def evaluate_inner_candidate(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    gate_indices: list[int],
    lam: float,
    q: float,
) -> dict[str, Any]:
    folds: list[dict[str, Any]] = []
    xx = x[:, gate_indices]
    for split_name, train_mask, test_mask in recur.inner_masks(measures):
        model = recur.ridge.fit_ridge(xx[train_mask], y[train_mask], lam)
        # Calibration uses only the held-out score distribution, never held-out labels.
        held = rank_apply(recur.ridge.scores_for(xx[test_mask], model), y[test_mask], q)
        base = base_stats(y[test_mask])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        folds.append({
            "split": split_name,
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
            gate_cache[(gate_lambda, support)] = recur.recurrent_gate(
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
                        print(f"    heartbeat rank-calibration search {done}/{total}", flush=True)
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
        raise RuntimeError("No relative-rank calibration candidates available")

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
        chosen = choose_outer_train_model(x[train_mask], y[train_mask], measures[train_mask], feature_names)

        gate = recur.recurrent_gate(
            x[train_mask], y[train_mask], measures[train_mask], feature_names,
            float(chosen["gateLambda"]), int(chosen["support"])
        )
        indices = list(gate["indices"])
        lam = float(chosen["lambda"])
        q = float(chosen["tailQuantile"])
        model = recur.ridge.fit_ridge(x[train_mask][:, indices], y[train_mask], lam)
        test_scores = recur.ridge.scores_for(x[test_mask][:, indices], model)
        held = rank_apply(test_scores, y[test_mask], q)
        base = base_stats(y[test_mask])
        lift = float(held["precision"]) - float(base["precision"])
        passed = held["true"] > 0 and lift >= 5.0
        pass_count += int(passed)

        local_names = [feature_names[j] for j in indices]
        weights = recur.ridge.top_weights(local_names, model[0], n=min(8, len(local_names)))
        rows.append({
            "scheme": name,
            "fold": fold,
            "trainRows": int(np.sum(train_mask)),
            "testRows": int(np.sum(test_mask)),
            "chosen": chosen,
            "featureGate": gate["features"],
            "lambda": lam,
            "tailQuantile": q,
            "topWeights": weights,
            "heldoutBase": base,
            "heldoutCandidate": held,
            "heldoutPrecisionLift": round(lift, 2),
            "passed": passed,
        })
        print(
            f"  gateLambda={chosen['gateLambda']} support={chosen['support']} features={len(indices)} "
            f"lambda={lam} q={q} held={held['true']}/{held['false']} selectedPct={held['selectedPct']} "
            f"precision={held['precision']} base={base['precision']} lift={round(lift, 2)} pass={passed}",
            flush=True,
        )

    return pass_count == OUTER_FOLDS, rows


def main() -> None:
    before = sha256(recur.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH)
    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    rows = list(payload.get("candidateSlots") or [])
    if not rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting relative-rank calibrated recurrent patch ridge nested CV V1", flush=True)
    print("Patch features:", len(feature_names), flush=True)
    normal_pass, normal = evaluate_scheme(x, y, measures, feature_names, "normal", lambda m: m % OUTER_FOLDS)
    section_pass, section = evaluate_scheme(x, y, measures, feature_names, "section", lambda m: recur.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted_pass, shifted = evaluate_scheme(x, y, measures, feature_names, "shiftedWindow", lambda m: recur.shifted_fold(m, lo, hi, OUTER_FOLDS))
    generalizes = normal_pass and section_pass and shifted_pass

    after = sha256(recur.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during relative-rank calibration CV")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-ridge-relative-rank-calibration-nested-cv-exploratory",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "normalCvPassed": normal_pass,
        "normalCv": normal,
        "sectionStabilityPassed": section_pass,
        "sectionCv": section,
        "shiftedWindowStabilityPassed": shifted_pass,
        "shiftedWindowCv": shifted,
        "relativeRankCalibrationGeneralizes": generalizes,
        "validatedNewChampion": False,
        "validationNote": "Exploratory event-slot validation only. Gate, ridge regularization and q are learned from training labels only. At held-out inference the q percentile is applied using only the unlabeled held-out score distribution. Held-out labels are grading only. No pitch recovery or champion promotion allowed.",
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
    MANIFEST_PATH.write_text(json.dumps({
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "relativeRankCalibrationGeneralizes": generalizes,
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH RIDGE RELATIVE RANK CALIBRATION NESTED CV V1 COMPLETE")
    print("Normal CV passed:", normal_pass)
    print("Section stability passed:", section_pass)
    print("Shifted-window stability passed:", shifted_pass)
    print("Relative-rank calibration generalizes:", generalizes)
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
