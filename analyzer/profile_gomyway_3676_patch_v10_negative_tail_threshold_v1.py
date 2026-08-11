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
OUTPUT_PATH = PUBLIC / "gomyway-3676-patch-v10-negative-tail-threshold-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3676-patch-v10-negative-tail-threshold-v1-manifest.json"
EXPECTED = (272, 595, 341)
EXPECTED_F1 = 36.76
OUTER_FOLDS = 5
NEGATIVE_TAIL_QUANTILES = [0.90, 0.95, 0.975, 0.99]


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
    selected_pct = 100.0 * total / len(yy) if len(yy) else 0.0
    return {
        "true": true,
        "false": false,
        "precision": round(float(precision), 2),
        "selectedPct": round(float(selected_pct), 2),
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

        print("    heartbeat negative-tail V5 model selection", flush=True)
        v5_choice = v5.choose_model(x[train], y[train], measures[train])
        print("    heartbeat negative-tail V9 model selection", flush=True)
        v9_choice = v9.choose_model(x[train], y[train], measures[train])
        architecture = v10.choose_hybrid(v5_choice, v9_choice)

        base = v1.base_stats(y[test])

        if architecture == "v9":
            model9 = v9.fit_pointwise_ridge(x[train], y[train], float(v9_choice["lambda"]))
            held_scores = v9.scores_for(x[test], model9)
            baseline = v1.select_top_fraction(held_scores, y[test], float(v9_choice["tailQuantile"]))
            lift = float(baseline["precision"]) - float(base["precision"])
            baseline_pass = baseline["true"] > 0 and lift >= 5.0
            rows.append({
                "scheme": name,
                "fold": fold,
                "architectureChosen": "v9",
                "eligibleForNegativeTail": False,
                "baseline": {**baseline, "lift": round(lift, 2), "passed": bool(baseline_pass)},
                "policies": {},
            })
            continue

        model5 = v2.fit_pairwise_ranker(
            x[train], y[train], measures[train], int(v5_choice["pairRadius"]), float(v5_choice["lambda"])
        )
        train_scores = v2.scores_for(x[train], model5)
        held_scores = v2.scores_for(x[test], model5)

        baseline = v1.select_top_fraction(held_scores, y[test], float(v5_choice["tailQuantile"]))
        baseline_lift = float(baseline["precision"]) - float(base["precision"])
        baseline_pass = baseline["true"] > 0 and baseline_lift >= 5.0

        neg_scores = np.asarray(train_scores, dtype=np.float64)[~np.asarray(y[train], dtype=bool)]
        if len(neg_scores) == 0:
            raise RuntimeError("No negative training scores available for negative-tail calibration")

        policies: dict[str, Any] = {}
        for q in NEGATIVE_TAIL_QUANTILES:
            threshold = float(np.quantile(neg_scores, q))
            held = threshold_eval(held_scores, y[test], threshold)
            lift = float(held["precision"]) - float(base["precision"])
            passed = held["true"] > 0 and lift >= 5.0
            key = f"negQ{q:g}"
            policies[key] = {
                "negativeTailQuantile": float(q),
                "threshold": threshold,
                **held,
                "basePrecision": float(base["precision"]),
                "lift": round(lift, 2),
                "passed": bool(passed),
            }

        rows.append({
            "scheme": name,
            "fold": fold,
            "architectureChosen": "v5",
            "eligibleForNegativeTail": True,
            "v5Q": float(v5_choice["tailQuantile"]),
            "baseline": {**baseline, "lift": round(baseline_lift, 2), "passed": bool(baseline_pass)},
            "policies": policies,
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
    x = np.asarray(
        [[float((r.get("features") or {}).get(f, 0.0)) for f in feature_names] for r in source_rows],
        dtype=np.float64,
    )
    y = np.asarray([str(r.get("label")) == "true" for r in source_rows], dtype=bool)
    measures = np.asarray([int(r["measure"]) for r in source_rows], dtype=np.int32)
    lo, hi = int(np.min(measures)), int(np.max(measures))

    print("Starting V10 negative-tail threshold residual diagnostic", flush=True)
    print("V10 architecture selector remains fixed; only V5-selected folds test training-negative score thresholds.", flush=True)

    normal = evaluate_scheme(x, y, measures, "normal", lambda m: m % OUTER_FOLDS)
    section = evaluate_scheme(x, y, measures, "section", lambda m: v1.contiguous_fold(m, lo, hi, OUTER_FOLDS))
    shifted = evaluate_scheme(x, y, measures, "shiftedWindow", lambda m: v1.shifted_fold(m, lo, hi, OUTER_FOLDS))
    all_rows = normal + section + shifted

    v10_passes = sum(bool(r["baseline"]["passed"]) for r in all_rows)
    policy_summary: dict[str, Any] = {}
    supported: list[str] = []

    for q in NEGATIVE_TAIL_QUANTILES:
        key = f"negQ{q:g}"
        passes = 0
        rescues: list[dict[str, Any]] = []
        collateral: list[dict[str, Any]] = []
        for r in all_rows:
            base_pass = bool(r["baseline"]["passed"])
            if not bool(r["eligibleForNegativeTail"]):
                new_pass = base_pass
            else:
                new_pass = bool(r["policies"][key]["passed"])
            passes += int(new_pass)
            if (not base_pass) and new_pass:
                rescues.append({"scheme": r["scheme"], "fold": r["fold"]})
            if base_pass and (not new_pass):
                collateral.append({"scheme": r["scheme"], "fold": r["fold"]})

        is_supported = passes > v10_passes and len(collateral) == 0
        if is_supported:
            supported.append(key)
        policy_summary[key] = {
            "passes": passes,
            "rescues": rescues,
            "collateralLosses": collateral,
            "supported": bool(is_supported),
        }

    after = sha256(candidate_path)
    if before != after:
        raise RuntimeError("Protected candidate changed during negative-tail diagnostic")

    output = {
        "schemaVersion": 1,
        "profileType": "36.76-patch-v10-negative-tail-threshold-residual-diagnostic",
        "baselinePitchF1": EXPECTED_F1,
        "baselineMatchedMissingExtra": list(EXPECTED),
        "v10Passes": v10_passes,
        "negativeTailQuantiles": NEGATIVE_TAIL_QUANTILES,
        "policySummary": policy_summary,
        "supportedPolicies": supported,
        "negativeTailThresholdSignalReady": bool(supported),
        "nextTarget": "strict-training-only-negative-tail-threshold-v11" if supported else "retire-negative-tail-threshold-and-pivot-residual-strategy",
        "normal": normal,
        "section": section,
        "shiftedWindow": shifted,
        "validatedNewChampion": False,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceUsedToChooseThreshold": False,
        "protected949CandidateHashUnchanged": before == after,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "v10Passes": v10_passes,
        "supportedPolicies": supported,
        "negativeTailThresholdSignalReady": bool(supported),
        "validatedNewChampion": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 36.76 PATCH V10 NEGATIVE-TAIL THRESHOLD V1 COMPLETE")
    print("V10 passes:", v10_passes, "/", len(all_rows))
    for key, summary in policy_summary.items():
        print(
            f"{key} passes={summary['passes']} rescues={summary['rescues']} "
            f"collateralLosses={summary['collateralLosses']} supported={summary['supported']}"
        )
    print("Supported policies:", supported)
    print("Negative-tail threshold signal ready:", bool(supported))
    print("Next target:", output["nextTarget"])
    print("Validated new champion: False")
    print("Professional reference used during detection: False")
    print("Professional reference used to choose threshold: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
