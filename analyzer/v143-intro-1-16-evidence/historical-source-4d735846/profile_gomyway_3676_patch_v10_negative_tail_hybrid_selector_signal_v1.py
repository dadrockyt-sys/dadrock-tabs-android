from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

import numpy as np

import benchmark_gomyway_3676_patch_v5_v9_hybrid_sectionpass_nested_cv_v10 as v10
import benchmark_gomyway_3676_patch_pairwise_rank_section_calibrated_nested_cv_v5 as v5
import benchmark_gomyway_3676_patch_pointwise_ridge_section_calibrated_nested_cv_v9 as v9
import benchmark_gomyway_3676_patch_pairwise_rank_nested_cv_v1 as v1
import benchmark_gomyway_3676_patch_pairwise_rank_stratified_nested_cv_v2 as v2

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-negative-tail-hybrid-selector-signal-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-negative-tail-hybrid-selector-signal-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
INNER_FOLDS = 3
NEG_Q = 0.975


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def threshold_eval(scores: np.ndarray, y: np.ndarray, threshold: float) -> dict[str, Any]:
    scores = np.asarray(scores, dtype=np.float64)
    yy = np.asarray(y, dtype=bool)
    selected = scores >= float(threshold)
    true = int(np.sum(selected & yy))
    false = int(np.sum(selected & ~yy))
    total = true + false
    precision = 100.0 * true / total if total else 0.0
    return {"true": true, "false": false, "precision": float(precision)}


def passed_from_eval(held: dict[str, Any], y: np.ndarray) -> tuple[bool, float]:
    base = v1.base_stats(y)
    lift = float(held["precision"]) - float(base["precision"])
    return bool(held["true"] > 0 and lift >= 5.0), float(lift)


def inner_section_comparison(
    x: np.ndarray,
    y: np.ndarray,
    measures: np.ndarray,
    pair_radius: int,
    lam: float,
    baseline_q: float,
) -> dict[str, Any]:
    lo, hi = int(np.min(measures)), int(np.max(measures))
    ids = np.asarray([v1.contiguous_fold(int(m), lo, hi, INNER_FOLDS) for m in measures], dtype=np.int16)
    baseline_passes = 0
    neg_passes = 0
    baseline_lifts: list[float] = []
    neg_lifts: list[float] = []
    rows: list[dict[str, Any]] = []

    for fold in range(INNER_FOLDS):
        val = ids == fold
        tr = ~val
        if not np.any(val) or not np.any(tr):
            continue

        model = v2.fit_pairwise_ranker(x[tr], y[tr], measures[tr], int(pair_radius), float(lam))
        tr_scores = v2.scores_for(x[tr], model)
        val_scores = v2.scores_for(x[val], model)

        baseline = v1.select_top_fraction(val_scores, y[val], float(baseline_q))
        baseline_pass, baseline_lift = passed_from_eval(baseline, y[val])

        neg_scores = np.asarray(tr_scores, dtype=np.float64)[~np.asarray(y[tr], dtype=bool)]
        if len(neg_scores) == 0:
            raise RuntimeError("No negative scores available in inner training split")
        threshold = float(np.quantile(neg_scores, NEG_Q))
        neg = threshold_eval(val_scores, y[val], threshold)
        neg_pass, neg_lift = passed_from_eval(neg, y[val])

        baseline_passes += int(baseline_pass)
        neg_passes += int(neg_pass)
        baseline_lifts.append(float(baseline_lift))
        neg_lifts.append(float(neg_lift))
        rows.append({
            "fold": fold,
            "baselinePassed": baseline_pass,
            "baselineLift": round(baseline_lift, 3),
            "negativeTailPassed": neg_pass,
            "negativeTailLift": round(neg_lift, 3),
            "negativeTailThreshold": threshold,
        })

    return {
        "baselineSectionPassCount": baseline_passes,
        "negativeTailSectionPassCount": neg_passes,
        "baselineMeanLift": round(float(np.mean(baseline_lifts)) if baseline_lifts else 0.0, 3),
        "negativeTailMeanLift": round(float(np.mean(neg_lifts)) if neg_lifts else 0.0, 3),
        "innerRows": rows,
    }


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

        print("    heartbeat selector V5 model selection", flush=True)
        v5_choice = v5.choose_model(x[train], y[train], measures[train])
        print("    heartbeat selector V9 model selection", flush=True)
        v9_choice = v9.choose_model(x[train], y[train], measures[train])
        architecture = v10.choose_hybrid(v5_choice, v9_choice)
        base = v1.base_stats(y[test])

        if architecture == "v9":
            model9 = v9.fit_pointwise_ridge(x[train], y[train], float(v9_choice["lambda"]))
            scores9 = v9.scores_for(x[test], model9)
            held = v1.select_top_fraction(scores9, y[test], float(v9_choice["tailQuantile"]))
            lift = float(held["precision"]) - float(base["precision"])
            passed = held["true"] > 0 and lift >= 5.0
            rows.append({
                "scheme": name,
                "fold": fold,
                "architectureChosen": "v9",
                "eligibleForNegativeTail": False,
                "selectorChoosesNegativeTail": False,
                "baselinePassed": bool(passed),
                "hybridPassed": bool(passed),
                "innerComparison": None,
            })
            continue

        pair_radius = int(v5_choice["pairRadius"])
        lam = float(v5_choice["lambda"])
        baseline_q = float(v5_choice["tailQuantile"])

        inner = inner_section_comparison(x[train], y[train], measures[train], pair_radius, lam, baseline_q)
        use_neg = int(inner["negativeTailSectionPassCount"]) > int(inner["baselineSectionPassCount"])
        print(
            "    heartbeat negative-tail selector "
            f"baselineSectionPass={inner['baselineSectionPassCount']}/{INNER_FOLDS} "
            f"negSectionPass={inner['negativeTailSectionPassCount']}/{INNER_FOLDS} "
            f"chosen={'negQ0.975' if use_neg else 'v10Q'}",
            flush=True,
        )

        model5 = v2.fit_pairwise_ranker(x[train], y[train], measures[train], pair_radius, lam)
        train_scores = v2.scores_for(x[train], model5)
        held_scores = v2.scores_for(x[test], model5)

        baseline = v1.select_top_fraction(held_scores, y[test], baseline_q)
        baseline_lift = float(baseline["precision"]) - float(base["precision"])
        baseline_pass = baseline["true"] > 0 and baseline_lift >= 5.0

        neg_scores = np.asarray(train_scores, dtype=np.float64)[~np.asarray(y[train], dtype=bool)]
        threshold = float(np.quantile(neg_scores, NEG_Q))
        neg = threshold_eval(held_scores, y[test], threshold)
        neg_lift = float(neg["precision"]) - float(base["precision"])
        neg_pass = neg["true"] > 0 and neg_lift >= 5.0
        hybrid_pass = bool(neg_pass if use_neg else baseline_pass)

        rows.append({
            "scheme": name,
            "fold": fold,
            "architectureChosen": "v5",
            "eligibleForNegativeTail": True,
            "selectorChoosesNegativeTail": bool(use_neg),
            "v5Q": baseline_q,
            "negativeTailQuantile": NEG_Q,
            "negativeTailThreshold": threshold,
            "baselinePassed": bool(baseline_pass),
            "negativeTailPassed": bool(neg_pass),
            "hybridPassed": hybrid_pass,
            "baselineLift": round(baseline_lift, 2),
            "negativeTailLift": round(neg_lift, 2),
            "innerComparison": inner,
        })

    return rows


def main() -> None:
    candidate_path = v1.recurrent.ridge.patch.richer.onset.prof.recall.CANDIDATE_PATH
    before = sha256(candidate_path)

    payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = list(payload.get("candidateSlots") or [])
    if not source_rows:
        raise RuntimeError("Spectro-temporal candidateSlots missing")
    if tuple(payload.get("frozenChampionMatchedMissingExtra") or []) != EXPECTED:
        raise RuntimeError("Patch profile not anchored to frozen 36.76 champion")

    feature_names = sorted((source_rows[0].get("features") or {}).keys())
    x = np.asarray([[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows], dtype=np.float64)
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V10 negative-tail hybrid selector signal diagnostic", flush=True)
    print("Predeclared rule: use negQ0.975 only if it strictly wins inner contiguous-section pass count.", flush=True)

    normal = evaluate_scheme(x, y, measures, "normal", lambda m: m % OUTER_FOLDS)
    section = evaluate_scheme(x, y, measures, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted = evaluate_scheme(x, y, measures, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    all_rows = normal + section + shifted

    v10_passes = sum(int(bool(r["baselinePassed"])) for r in all_rows)
    hybrid_passes = sum(int(bool(r["hybridPassed"])) for r in all_rows)
    rescues = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if (not r["baselinePassed"]) and r["hybridPassed"]]
    collateral = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if r["baselinePassed"] and (not r["hybridPassed"])]
    selected = [{"scheme": r["scheme"], "fold": r["fold"]} for r in all_rows if r.get("selectorChoosesNegativeTail")]

    ready = hybrid_passes > v10_passes and len(collateral) == 0

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during negative-tail selector diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-negative-tail-hybrid-selector-signal",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "negativeTailQuantile": NEG_Q,
        "selectorRule": "use-negQ0.975-only-if-inner-section-pass-count-strictly-exceeds-v10-q",
        "selectorUsesOuterHeldoutLabels": False,
        "v10Passes": v10_passes,
        "hybridPasses": hybrid_passes,
        "selectorChosenFolds": selected,
        "rescues": rescues,
        "collateralLosses": collateral,
        "negativeTailHybridSelectorSignalReady": bool(ready),
        "nextTarget": "strict-v10-negative-tail-hybrid-nested-cv-v11" if ready else "retire-negative-tail-hybrid-selector-and-pivot-residual-strategy",
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
        "selectorRule": output["selectorRule"],
        "v10Passes": v10_passes,
        "hybridPasses": hybrid_passes,
        "rescues": rescues,
        "collateralLosses": collateral,
        "negativeTailHybridSelectorSignalReady": bool(ready),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 NEGATIVE-TAIL HYBRID SELECTOR SIGNAL V1 COMPLETE")
    print("V10 passes:", v10_passes, "/", len(all_rows))
    print("Hybrid passes:", hybrid_passes, "/", len(all_rows))
    print("Selector chose negative-tail folds:", selected)
    print("Rescues:", rescues)
    print("Collateral losses:", collateral)
    print("Negative-tail hybrid selector signal ready:", bool(ready))
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
