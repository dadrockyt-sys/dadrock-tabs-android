from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_v5_v9_hybrid_sectionpass_nested_cv_v10 as v10
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-residual-geometry-negative-tail-selector-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-residual-geometry-negative-tail-selector-v1-manifest.json"
EXPECTED = (272, 595, 341)
OUTER_FOLDS = 5
INNER_FOLDS = 3
NEG_Q = 0.975
ACTIVE_METRICS = ("top5VsTop10GapZ", "upperTailSpreadZ")
RISK_MARGIN = 0.5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score_geometry(scores: np.ndarray, q: float) -> dict[str, float]:
    s = np.asarray(scores, dtype=np.float64)
    n = len(s)
    if n < 4:
        raise RuntimeError("Too few scores for residual geometry selector")
    ordered = np.sort(s)[::-1]
    mu = float(np.mean(s))
    sd = float(np.std(s))
    scale = sd if sd > 1e-12 else 1.0
    k = max(1, min(n - 1, int(np.ceil(float(q) * n))))
    top5n = max(1, int(np.ceil(0.05 * n)))
    top10n = max(1, int(np.ceil(0.10 * n)))
    q90 = float(np.quantile(s, 0.90))
    q99 = float(np.quantile(s, 0.99))
    top5_mean = float(np.mean(ordered[:top5n]))
    top10_mean = float(np.mean(ordered[:top10n]))
    return {
        "chosenQ": float(q),
        "scoreStd": sd,
        "top5VsTop10GapZ": float((top5_mean - top10_mean) / scale),
        "upperTailSpreadZ": float((q99 - q90) / scale),
    }


def threshold_eval(scores: np.ndarray, y: np.ndarray, threshold: float) -> dict[str, Any]:
    scores = np.asarray(scores, dtype=np.float64)
    yy = np.asarray(y, dtype=bool)
    selected = scores >= float(threshold)
    true = int(np.sum(selected & yy))
    false = int(np.sum(selected & ~yy))
    total = true + false
    precision = 100.0 * true / total if total else 0.0
    return {"true": true, "false": false, "precision": float(precision)}


def passed_eval(held: dict[str, Any], y: np.ndarray) -> tuple[bool, float]:
    base = v1.base_stats(y)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(int(held["true"]) > 0 and lift >= 5.0), float(lift)


def inner_geometry_model(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    pair_radius: int,
    lam: float,
    q: float,
) -> dict[str, Any]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v1.contiguous_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []

    for fold in range(INNER_FOLDS):
        val = ids == fold
        tr = ~val
        if not np.any(val) or not np.any(tr):
            continue
        model = v2.fit_pairwise_ranker(x[tr], y[tr], measures[tr], int(pair_radius), float(lam))
        scores = v2.scores_for(x[val], model)
        held = v1.select_top_fraction(scores, y[val], float(q))
        passed, lift = passed_eval(held, y[val])
        rows.append({
            "fold": fold,
            "passed": bool(passed),
            "lift": round(lift, 3),
            "geometry": score_geometry(scores, q),
        })

    passing = [r for r in rows if r["passed"]]
    failing = [r for r in rows if not r["passed"]]
    all_rows = passing + failing
    model: dict[str, Any] = {
        "innerRows": rows,
        "innerPassCount": len(passing),
        "innerFailCount": len(failing),
        "usable": bool(passing and failing),
        "metrics": {},
    }
    if not passing or not failing:
        return model

    for key in ACTIVE_METRICS:
        vals = np.asarray([float(r["geometry"][key]) for r in all_rows], dtype=np.float64)
        mu = float(np.mean(vals))
        sd = float(np.std(vals))
        scale = sd if sd > 1e-12 else 1.0
        pass_mean = float(np.mean([float(r["geometry"][key]) for r in passing]))
        fail_mean = float(np.mean([float(r["geometry"][key]) for r in failing]))
        direction = 1.0 if fail_mean >= pass_mean else -1.0
        midpoint = 0.5 * (pass_mean + fail_mean)
        model["metrics"][key] = {
            "passMean": pass_mean,
            "failMean": fail_mean,
            "midpoint": midpoint,
            "direction": direction,
            "scale": scale,
        }
    return model


def geometry_risk(geometry: dict[str, float], model: dict[str, Any]) -> tuple[bool, float, dict[str, float]]:
    if not bool(model.get("usable")):
        return False, 0.0, {}
    components: dict[str, float] = {}
    for key in ACTIVE_METRICS:
        spec = dict(model["metrics"][key])
        value = float(geometry[key])
        signed = float(spec["direction"]) * (value - float(spec["midpoint"])) / float(spec["scale"])
        components[key] = signed
    risk_score = float(np.mean(list(components.values()))) if components else 0.0
    return bool(risk_score >= RISK_MARGIN), risk_score, components


def evaluate_scheme(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    name: str,
    fold_fn: Callable[[int], int],
) -> list[dict[str, Any]]:
    ids = np.asarray([fold_fn(int(m)) for m in measures], dtype=np.int16)
    rows: list[dict[str, Any]] = []

    for fold in range(OUTER_FOLDS):
        print(f"{name}: outer fold {fold + 1}/{OUTER_FOLDS} ...", flush=True)
        test = ids == fold
        train = ~test
        print("    heartbeat residual-selector V5 model selection", flush=True)
        v5_choice = v5.choose_model(x[train], y[train], measures[train])
        print("    heartbeat residual-selector V9 model selection", flush=True)
        v9_choice = v9.choose_model(x[train], y[train], measures[train])
        architecture = v10.choose_hybrid(v5_choice, v9_choice)
        base = v1.base_stats(y[test])

        if architecture == "v9":
            model9 = v9.fit_pointwise_ridge(x[train], y[train], float(v9_choice["lambda"]))
            scores9 = v9.scores_for(x[test], model9)
            held = v1.select_top_fraction(scores9, y[test], float(v9_choice["tailQuantile"]))
            passed, lift = passed_eval(held, y[test])
            rows.append({
                "scheme": name,
                "fold": fold,
                "architectureChosen": "v9",
                "baselinePassed": bool(passed),
                "selectorFlagsRisk": False,
                "selectorUsesNegativeTail": False,
                "hybridPassed": bool(passed),
                "baselineLift": round(lift, 2),
            })
            continue

        pair_radius = int(v5_choice["pairRadius"])
        lam = float(v5_choice["lambda"])
        q = float(v5_choice["tailQuantile"])
        inner_model = inner_geometry_model(x[train], y[train], measures[train], pair_radius, lam, q)

        model5 = v2.fit_pairwise_ranker(x[train], y[train], measures[train], pair_radius, lam)
        train_scores = v2.scores_for(x[train], model5)
        held_scores = v2.scores_for(x[test], model5)
        geometry = score_geometry(held_scores, q)
        risky, risk_score, components = geometry_risk(geometry, inner_model)

        baseline = v1.select_top_fraction(held_scores, y[test], q)
        baseline_pass, baseline_lift = passed_eval(baseline, y[test])

        neg_train = np.asarray(train_scores, dtype=np.float64)[~np.asarray(y[train], dtype=bool)]
        if len(neg_train) == 0:
            raise RuntimeError("No outer-training negative scores for negative-tail threshold")
        threshold = float(np.quantile(neg_train, NEG_Q))
        neg = threshold_eval(held_scores, y[test], threshold)
        neg_pass, neg_lift = passed_eval(neg, y[test])
        hybrid_pass = bool(neg_pass if risky else baseline_pass)

        print(
            "    heartbeat residual geometry selector "
            f"innerPass={inner_model['innerPassCount']}/{len(inner_model['innerRows'])} "
            f"riskScore={risk_score:.3f} risky={risky} "
            f"chosen={'negQ0.975' if risky else 'v10Q'}",
            flush=True,
        )

        rows.append({
            "scheme": name,
            "fold": fold,
            "architectureChosen": "v5",
            "v5Q": q,
            "baselinePassed": bool(baseline_pass),
            "baselineLift": round(baseline_lift, 2),
            "negativeTailPassed": bool(neg_pass),
            "negativeTailLift": round(neg_lift, 2),
            "negativeTailThreshold": threshold,
            "selectorFlagsRisk": bool(risky),
            "selectorUsesNegativeTail": bool(risky),
            "riskScore": round(risk_score, 6),
            "riskComponents": {k: round(v, 6) for k, v in components.items()},
            "heldoutGeometry": geometry,
            "innerGeometryModel": inner_model,
            "hybridPassed": bool(hybrid_pass),
        })

    return rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if tuple(source.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Source profile not anchored to frozen 36.76 champion")
    slots = list(source.get("candidateSlots") or [])
    if not slots:
        raise RuntimeError("candidateSlots missing")

    features = sorted((slots[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in features] for r in slots], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in slots], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in slots], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V10 residual geometry -> negative-tail selector diagnostic", flush=True)
    print("Predeclared metrics:", list(ACTIVE_METRICS), flush=True)
    print("Outer held-out labels are grading-only; geometry risk model is fit on inner outer-training folds.", flush=True)

    normal = evaluate_scheme(x, y, measures, "normal", lambda m: m % OUTER_FOLDS)
    section = evaluate_scheme(x, y, measures, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted = evaluate_scheme(x, y, measures, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    all_rows = normal + section + shifted

    baseline_passes = sum(int(bool(r["baselinePassed"])) for r in all_rows)
    hybrid_passes = sum(int(bool(r["hybridPassed"])) for r in all_rows)
    selected = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if r.get("selectorUsesNegativeTail")]
    rescues = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if (not r["baselinePassed"]) and r["hybridPassed"]]
    collateral = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if r["baselinePassed"] and (not r["hybridPassed"])]
    ready = bool(hybrid_passes > baseline_passes and len(collateral) == 0)

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during residual geometry selector diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-residual-geometry-negative-tail-selector",
        "predeclaredMetrics": list(ACTIVE_METRICS),
        "riskMargin": RISK_MARGIN,
        "negativeTailQuantile": NEG_Q,
        "selectorUsesOuterHeldoutLabels": False,
        "baselineV10Passes": baseline_passes,
        "hybridPasses": hybrid_passes,
        "selectorChosenFolds": selected,
        "rescues": rescues,
        "collateralLosses": collateral,
        "residualGeometrySelectorSignalReady": ready,
        "nextTarget": "strict-v10-residual-geometry-negative-tail-nested-cv-v11" if ready else "retire-residual-geometry-selector-and-pivot-representation",
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseThresholdOrSelector": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "baselineV10Passes": baseline_passes,
        "hybridPasses": hybrid_passes,
        "rescues": rescues,
        "collateralLosses": collateral,
        "residualGeometrySelectorSignalReady": ready,
        "nextTarget": output["nextTarget"],
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 RESIDUAL GEOMETRY NEGATIVE-TAIL SELECTOR V1 COMPLETE")
    print("V10 passes:", baseline_passes, "/", len(all_rows))
    print("Hybrid passes:", hybrid_passes, "/", len(all_rows))
    print("Selector chose negative-tail folds:", selected)
    print("Rescues:", rescues)
    print("Collateral losses:", collateral)
    print("Residual geometry selector signal ready:", ready)
    print("Next target:", output["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose threshold or selector: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
