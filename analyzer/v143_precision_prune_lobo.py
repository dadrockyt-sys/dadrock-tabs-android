#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

import v143_correlation_safe_fixed_count_reranker_freeze as freeze

CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
REFERENCE_PATH = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
REPORT_PATH = CAL / "precision-prune-lobo-report.json"

TARGET_MEASURES = set(range(17, 97))
BANDS = [(17, 32), (33, 48), (49, 64), (65, 80), (81, 96)]
EXPECTED_REFERENCE_COUNT = 431

# Interpretable pruning family: start from promoted base-0.27 events only.
# An event survives if its base score is strong enough OR the historical
# correlation-safe sequence model independently supports it.
BASE_FLOORS = (0.27, 0.30, 0.33, 0.36, 0.39, 0.42, 0.45, 0.50, 0.55)
SEQUENCE_FLOORS = (0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.70)


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def parse_reference_blind_safe(path: Path) -> tuple[set[tuple[int, int]], bool]:
    ref: set[tuple[int, int]] = set()
    current_measure: int | None = None
    hit_reserve_boundary = False
    measure_re = re.compile(r'"measureNumber"\s*:\s*(\d+)')
    step_re = re.compile(r'"quantizedStep"\s*:\s*(\d+)')

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            mm = measure_re.search(line)
            if mm:
                current_measure = int(mm.group(1))
                if current_measure >= 97:
                    hit_reserve_boundary = True
                    break
            sm = step_re.search(line)
            if sm and current_measure is not None and 17 <= current_measure <= 96:
                ref.add((current_measure, int(sm.group(1))))
    return ref, hit_reserve_boundary


def metrics(pred: set[tuple[int, int]], ref: set[tuple[int, int]]) -> dict[str, Any]:
    tp = len(pred & ref)
    fp = len(pred - ref)
    fn = len(ref - pred)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "predicted": len(pred),
        "reference": len(ref),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def subset(values: set[tuple[int, int]], measures: set[int]) -> set[tuple[int, int]]:
    return {key for key in values if key[0] in measures}


def band_set(lo: int, hi: int) -> set[int]:
    return set(range(lo, hi + 1))


def apply_rule(
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    measures: set[int],
    base_floor: float,
    sequence_floor: float,
) -> set[tuple[int, int]]:
    out: set[tuple[int, int]] = set()
    for key in base_active:
        if key[0] not in measures:
            continue
        strong_base = float(base_scores.get(key, -1e9)) >= float(base_floor)
        sequence_support = bool(sequence_evidence.get(key, False)) and float(sequence_scores.get(key, -1e9)) >= float(sequence_floor)
        if strong_base or sequence_support:
            out.add(key)
    return out


def evaluate_rule(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    measures: set[int],
    base_floor: float,
    sequence_floor: float,
) -> dict[str, Any]:
    ref = subset(reference, measures)
    base = subset(base_active, measures)
    cand = apply_rule(base_active, base_scores, sequence_scores, sequence_evidence, measures, base_floor, sequence_floor)
    bm = metrics(base, ref)
    cm = metrics(cand, ref)
    return {
        "baseFloor": float(base_floor),
        "sequenceFloor": float(sequence_floor),
        "base": bm,
        "candidate": cm,
        "delta": {
            "predicted": int(cm["predicted"] - bm["predicted"]),
            "tp": int(cm["tp"] - bm["tp"]),
            "fp": int(cm["fp"] - bm["fp"]),
            "fn": int(cm["fn"] - bm["fn"]),
            "precision": float(cm["precision"] - bm["precision"]),
            "recall": float(cm["recall"] - bm["recall"]),
            "f1": float(cm["f1"] - bm["f1"]),
        },
    }


def training_score(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    training_bands: list[tuple[int, int]],
    base_floor: float,
    sequence_floor: float,
) -> tuple[tuple[float, ...], dict[str, Any]]:
    per_band: dict[str, Any] = {}
    f1_deltas: list[float] = []
    precision_deltas: list[float] = []
    total_pruned = 0

    for lo, hi in training_bands:
        measures = band_set(lo, hi)
        result = evaluate_rule(reference, base_active, base_scores, sequence_scores, sequence_evidence, measures, base_floor, sequence_floor)
        name = f"{lo}-{hi}"
        per_band[name] = result
        f1_deltas.append(float(result["delta"]["f1"]))
        precision_deltas.append(float(result["delta"]["precision"]))
        total_pruned += -int(result["delta"]["predicted"])

    training_measures = set().union(*(band_set(lo, hi) for lo, hi in training_bands))
    pooled = evaluate_rule(reference, base_active, base_scores, sequence_scores, sequence_evidence, training_measures, base_floor, sequence_floor)

    # Safety-first selection on development data: maximize the worst block,
    # then mean block F1, then pooled F1, then precision. Prefer fewer changes
    # when candidates tie. The 0.27 base-floor option is a legal no-op.
    score = (
        min(f1_deltas),
        sum(f1_deltas) / len(f1_deltas),
        float(pooled["delta"]["f1"]),
        sum(precision_deltas) / len(precision_deltas),
        -float(total_pruned),
        -float(base_floor),
        -float(sequence_floor),
    )
    return score, {
        "baseFloor": float(base_floor),
        "sequenceFloor": float(sequence_floor),
        "perBand": per_band,
        "pooled": pooled,
        "trainingWorstF1Delta": min(f1_deltas),
        "trainingMeanF1Delta": sum(f1_deltas) / len(f1_deltas),
        "trainingMeanPrecisionDelta": sum(precision_deltas) / len(precision_deltas),
        "trainingPruned": total_pruned,
    }


def choose_rule(
    reference: set[tuple[int, int]],
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    training_bands: list[tuple[int, int]],
) -> dict[str, Any]:
    best_score: tuple[float, ...] | None = None
    best: dict[str, Any] | None = None
    for base_floor in BASE_FLOORS:
        for sequence_floor in SEQUENCE_FLOORS:
            score, result = training_score(reference, base_active, base_scores, sequence_scores, sequence_evidence, training_bands, base_floor, sequence_floor)
            if best_score is None or score > best_score:
                best_score = score
                best = result
    if best is None:
        raise RuntimeError("No precision-prune rule evaluated")
    return best


def rounded(obj: Any) -> Any:
    if isinstance(obj, float):
        return round(obj, 6)
    if isinstance(obj, dict):
        return {k: rounded(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [rounded(v) for v in obj]
    return obj


def main() -> None:
    reference, hit_boundary = parse_reference_blind_safe(REFERENCE_PATH)
    if not hit_boundary:
        raise RuntimeError("Did not encounter measure-97 reserve boundary")
    if len(reference) != EXPECTED_REFERENCE_COUNT:
        raise RuntimeError(f"Reference count changed: {len(reference)} != {EXPECTED_REFERENCE_COUNT}")

    base_model = load_json(freeze.BASE_MODEL_PATH)
    sequence_model = load_json(freeze.SEQUENCE_MODEL_PATH)
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected base threshold 0.27, got {base_model.get('threshold')}")
    if sequence_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Sequence model unexpectedly requires professional reference at runtime")

    rows_by_measure, grid = freeze._merge_fresh_caches()
    base_scores, base_evidence = freeze._score_measures(rows_by_measure, grid, TARGET_MEASURES, base_model)
    base_active = freeze._active_from_scores(base_scores, base_evidence, TARGET_MEASURES, float(base_model["threshold"]))
    if len(base_active) != 765:
        raise RuntimeError(f"Base replay count mismatch: {len(base_active)} != 765")

    sequence_scores, sequence_evidence = freeze._sequence_scores(
        rows_by_measure,
        grid,
        TARGET_MEASURES,
        TARGET_MEASURES,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    outer_folds: list[dict[str, Any]] = []
    heldout_deltas: list[float] = []
    heldout_precision_deltas: list[float] = []

    for holdout in BANDS:
        training_bands = [band for band in BANDS if band != holdout]
        chosen = choose_rule(reference, base_active, base_scores, sequence_scores, sequence_evidence, training_bands)
        holdout_measures = band_set(*holdout)
        heldout = evaluate_rule(
            reference,
            base_active,
            base_scores,
            sequence_scores,
            sequence_evidence,
            holdout_measures,
            float(chosen["baseFloor"]),
            float(chosen["sequenceFloor"]),
        )
        heldout_deltas.append(float(heldout["delta"]["f1"]))
        heldout_precision_deltas.append(float(heldout["delta"]["precision"]))
        outer_folds.append({
            "holdout": f"{holdout[0]}-{holdout[1]}",
            "selectedFromOtherFourBands": chosen,
            "heldout": heldout,
        })

    final_rule = choose_rule(reference, base_active, base_scores, sequence_scores, sequence_evidence, BANDS)
    final_band_results: dict[str, Any] = {}
    final_band_deltas: list[float] = []
    for lo, hi in BANDS:
        result = evaluate_rule(
            reference,
            base_active,
            base_scores,
            sequence_scores,
            sequence_evidence,
            band_set(lo, hi),
            float(final_rule["baseFloor"]),
            float(final_rule["sequenceFloor"]),
        )
        final_band_results[f"{lo}-{hi}"] = result
        final_band_deltas.append(float(result["delta"]["f1"]))

    final_all = evaluate_rule(
        reference,
        base_active,
        base_scores,
        sequence_scores,
        sequence_evidence,
        TARGET_MEASURES,
        float(final_rule["baseFloor"]),
        float(final_rule["sequenceFloor"]),
    )

    outer_all_nonnegative = all(delta >= -1e-12 for delta in heldout_deltas)
    outer_mean_positive = (sum(heldout_deltas) / len(heldout_deltas)) > 1e-12
    final_all_bands_nonnegative = all(delta >= -1e-12 for delta in final_band_deltas)
    final_pooled_positive = float(final_all["delta"]["f1"]) > 1e-12
    candidate_is_subset = apply_rule(
        base_active,
        base_scores,
        sequence_scores,
        sequence_evidence,
        TARGET_MEASURES,
        float(final_rule["baseFloor"]),
        float(final_rule["sequenceFloor"]),
    ).issubset(base_active)

    promotion_eligible = (
        outer_all_nonnegative
        and outer_mean_positive
        and final_all_bands_nonnegative
        and final_pooled_positive
        and candidate_is_subset
    )

    report = rounded({
        "schemaVersion": 1,
        "experiment": "v143-precision-prune-lobo",
        "purpose": "Reduce false positives by pruning only promoted base-0.27 events; never add or relocate events.",
        "developmentMeasures": "17-96",
        "reserveMeasures": "97-113",
        "referenceCount": len(reference),
        "baseEventCount": len(base_active),
        "baseMetrics": metrics(base_active, reference),
        "ruleFamily": {
            "keepIf": "baseScore >= baseFloor OR (sequenceEvidence AND sequenceScore >= sequenceFloor)",
            "baseFloors": list(BASE_FLOORS),
            "sequenceFloors": list(SEQUENCE_FLOORS),
        },
        "outerLeaveOne16MeasureBlockOut": outer_folds,
        "outerHeldoutF1Deltas": heldout_deltas,
        "outerHeldoutPrecisionDeltas": heldout_precision_deltas,
        "outerWorstHeldoutF1Delta": min(heldout_deltas),
        "outerMeanHeldoutF1Delta": sum(heldout_deltas) / len(heldout_deltas),
        "finalDevelopmentRule": final_rule,
        "finalDevelopmentBandResults": final_band_results,
        "finalDevelopmentCombined": final_all,
        "gate": {
            "outerAllHeldoutNonnegative": outer_all_nonnegative,
            "outerMeanHeldoutPositive": outer_mean_positive,
            "finalRuleAllDevelopmentBandsNonnegative": final_all_bands_nonnegative,
            "finalRulePooledF1Positive": final_pooled_positive,
            "candidateSubsetOfBase": candidate_is_subset,
            "promotionEligible": promotion_eligible,
        },
        "invariants": {
            "measures97To113Opened": False,
            "reservePayloadOpened": False,
            "professionalReferenceUsedForDevelopmentOnly17To96": True,
            "productionModified": False,
        },
    })

    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("=== V143 PRECISION PRUNE LOBO ===")
    print("BASE", rounded(metrics(base_active, reference)))
    print("OUTER_HELDOUT_F1_DELTAS", rounded(heldout_deltas))
    print("OUTER_WORST", round(min(heldout_deltas), 6))
    print("OUTER_MEAN", round(sum(heldout_deltas) / len(heldout_deltas), 6))
    print("FINAL_RULE", {"baseFloor": final_rule["baseFloor"], "sequenceFloor": final_rule["sequenceFloor"]})
    print("FINAL", rounded(final_all))
    print("PROMOTION_ELIGIBLE", promotion_eligible)
    print("MEASURES_97_113_OPENED", False)
    print(f"WROTE={REPORT_PATH}")


if __name__ == "__main__":
    main()
