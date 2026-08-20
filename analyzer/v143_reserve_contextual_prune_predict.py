#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

import v143_contextual_prune_lobo as contextual
import v143_correlation_safe_fixed_count_reranker_freeze as freeze

CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
SECTION5_CACHE_PATH = CAL / "fresh-section5-reference-free-cache.json"
RESERVE_CACHE_PATH = CAL / "reserve-97-113-reference-free-cache.json"
SECTION5_BASE_FROZEN_PATH = CAL / "fresh-section5-base027-frozen-events.json"
FROZEN_MODEL_PATH = CAL / "contextual-prune-frozen-model.json"
FREEZE_MANIFEST_PATH = CAL / "contextual-prune-freeze-manifest.json"
BASE_OUTPUT_PATH = CAL / "reserve-97-113-base027-frozen-events.json"
CANDIDATE_OUTPUT_PATH = CAL / "reserve-97-113-contextual-prune-frozen-events.json"
PREDICTION_MANIFEST_PATH = CAL / "reserve-97-113-contextual-prune-prediction-manifest.json"

SECTION5_MEASURES = set(range(81, 97))
TARGET_MEASURES = set(range(97, 114))
CONTEXT_MEASURES = set(range(81, 114))


def load_json(path: Path) -> Any:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required artifact: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_events(payload: Any, allowed_measures: set[int]) -> set[tuple[int, int]]:
    found: set[tuple[int, int]] = set()

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            if "measure" in value and ("step" in value or "quantizedStep" in value):
                try:
                    measure = int(value["measure"])
                    step = int(value.get("step", value.get("quantizedStep")))
                    if measure in allowed_measures and 0 <= step < 16:
                        found.add((measure, step))
                except (TypeError, ValueError):
                    pass
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payload)
    return found


def merge_reference_free_context() -> tuple[dict[int, list[dict[str, Any]]], dict[tuple[int, int], float]]:
    rows_by_measure: dict[int, list[dict[str, Any]]] = {}
    grid: dict[tuple[int, int], float] = {}
    group_offset = 0

    for path in (SECTION5_CACHE_PATH, RESERVE_CACHE_PATH):
        cache = load_json(path)
        if cache.get("referenceFree") is not True:
            raise RuntimeError(f"Cache is not referenceFree=true: {path}")
        if cache.get("professionalReferenceUsedByAnalyzer") is not False:
            raise RuntimeError(f"Cache does not assert professionalReferenceUsedByAnalyzer=false: {path}")
        if cache.get("professionalReferenceRequiredAtRuntime") is not False:
            raise RuntimeError(f"Cache unexpectedly requires professional reference at runtime: {path}")
        if cache.get("productionModified") is not False:
            raise RuntimeError(f"Cache unexpectedly marks productionModified=true: {path}")

        for raw in cache.get("rows", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or raw.get("nearestMeasure") or 0)
            if measure not in CONTEXT_MEASURES:
                continue
            row = dict(raw)
            row["measure"] = measure
            if row.get("onsetGroupId") is not None:
                row["onsetGroupId"] = int(row.get("onsetGroupId") or 0) + group_offset
            rows_by_measure.setdefault(measure, []).append(row)

        for raw in cache.get("grid", []) or []:
            if not isinstance(raw, dict):
                continue
            measure = int(raw.get("measure") or 0)
            step = int(raw.get("step") or 0)
            if measure not in CONTEXT_MEASURES or not 0 <= step < 16:
                continue
            key = (measure, step)
            time_seconds = float(raw.get("timeSeconds") or 0.0)
            if key in grid and abs(grid[key] - time_seconds) > 1e-6:
                raise RuntimeError(f"Conflicting grid time for {key}: {grid[key]} vs {time_seconds}")
            grid[key] = time_seconds

        group_offset += 1_000_000

    for values in rows_by_measure.values():
        values.sort(
            key=lambda row: (
                float(row.get("onsetTime") or 0.0),
                int(row.get("onsetGroupId") or 0),
            )
        )

    expected_grid = len(CONTEXT_MEASURES) * 16
    if len(grid) != expected_grid:
        missing = [
            (measure, step)
            for measure in sorted(CONTEXT_MEASURES)
            for step in range(16)
            if (measure, step) not in grid
        ]
        raise RuntimeError(
            f"81-113 context grid incomplete: {len(grid)}/{expected_grid}; missing={missing[:12]}"
        )
    if set(rows_by_measure) != CONTEXT_MEASURES:
        missing_measures = sorted(CONTEXT_MEASURES - set(rows_by_measure))
        raise RuntimeError(f"81-113 reference-free rows missing measures: {missing_measures}")

    return rows_by_measure, grid


def runtime_contextual_model(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "mean": np.asarray(payload["featureMean"], dtype=np.float64),
        "std": np.asarray(payload["featureStd"], dtype=np.float64),
        "weights": np.asarray(payload["weights"], dtype=np.float64),
        "l2": float(payload["l2"]),
    }


def event_payload(
    events: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    base_evidence: dict[tuple[int, int], bool],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
    probabilities: dict[tuple[int, int], float],
) -> list[dict[str, Any]]:
    return [
        {
            "measure": int(measure),
            "quantizedStep": int(step),
            "baseScore": float(base_scores.get((measure, step), 0.0)),
            "baseEvidence": bool(base_evidence.get((measure, step), False)),
            "sequenceScore": float(sequence_scores.get((measure, step), 0.0)),
            "sequenceEvidence": bool(sequence_evidence.get((measure, step), False)),
            "contextualKeepProbability": float(probabilities.get((measure, step), 0.5)),
        }
        for measure, step in sorted(events)
    ]


def main() -> None:
    freeze_manifest = load_json(FREEZE_MANIFEST_PATH)
    frozen_model = load_json(FROZEN_MODEL_PATH)
    section5_cache = load_json(SECTION5_CACHE_PATH)
    reserve_cache = load_json(RESERVE_CACHE_PATH)

    if freeze_manifest.get("predictionsFrozenBeforeReserveGrading") is not True:
        raise RuntimeError("Development freeze does not assert predictionsFrozenBeforeReserveGrading=true")
    for key in ("targetReserveReferenceOpened", "measures97To113Opened", "reservePayloadOpened"):
        if freeze_manifest.get(key) is not False:
            raise RuntimeError(f"Development freeze invariant changed: {key}={freeze_manifest.get(key)!r}")
    if freeze_manifest.get("productionModified") is not False:
        raise RuntimeError("Development freeze unexpectedly marks productionModified=true")

    if frozen_model.get("model") != "v143-contextual-prune":
        raise RuntimeError(f"Unexpected frozen model: {frozen_model.get('model')}")
    if frozen_model.get("trainingMeasures") != "17-96":
        raise RuntimeError(f"Unexpected training measures: {frozen_model.get('trainingMeasures')}")
    if frozen_model.get("reserveMeasures") != "97-113":
        raise RuntimeError(f"Unexpected reserve measures: {frozen_model.get('reserveMeasures')}")
    if frozen_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Frozen contextual model unexpectedly requires professional reference")
    if frozen_model.get("measures97To113UsedForTraining") is not False:
        raise RuntimeError("Frozen contextual model claims reserve measures were used for training")
    if frozen_model.get("productionModified") is not False:
        raise RuntimeError("Frozen contextual model unexpectedly marks productionModified=true")
    if frozen_model.get("candidateAddsEvents") is not False:
        raise RuntimeError("Frozen contextual model unexpectedly adds events")
    if frozen_model.get("candidateRelocatesEvents") is not False:
        raise RuntimeError("Frozen contextual model unexpectedly relocates events")
    if list(frozen_model.get("featureNames", [])) != list(contextual.FEATURE_NAMES):
        raise RuntimeError("Frozen contextual feature names do not match source feature names")

    prune_fraction = float(frozen_model.get("pruneFraction", -1.0))
    if prune_fraction != 0.15:
        raise RuntimeError(f"Unexpected frozen prune fraction: {prune_fraction}")
    if float(frozen_model.get("baseThreshold", -1.0)) != 0.27:
        raise RuntimeError(f"Unexpected frozen base threshold: {frozen_model.get('baseThreshold')}")

    for label, cache in (("section5", section5_cache), ("reserve", reserve_cache)):
        if cache.get("referenceFree") is not True:
            raise RuntimeError(f"{label} cache is not referenceFree=true")
        if cache.get("professionalReferenceUsedByAnalyzer") is not False:
            raise RuntimeError(f"{label} cache does not assert professionalReferenceUsedByAnalyzer=false")
        if cache.get("professionalReferenceRequiredAtRuntime") is not False:
            raise RuntimeError(f"{label} cache unexpectedly requires professional reference")
        if cache.get("productionModified") is not False:
            raise RuntimeError(f"{label} cache unexpectedly marks productionModified=true")

    reserve_section = reserve_cache.get("section", {})
    if int(reserve_section.get("startMeasure", 0)) != 97 or int(reserve_section.get("endMeasure", 0)) != 113:
        raise RuntimeError(f"Reserve cache section bounds changed: {reserve_section}")

    base_model = load_json(freeze.BASE_MODEL_PATH)
    sequence_model = load_json(freeze.SEQUENCE_MODEL_PATH)
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Expected promoted base threshold 0.27, got {base_model.get('threshold')}")
    if sequence_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Sequence model unexpectedly requires professional reference at runtime")

    rows_by_measure, grid = merge_reference_free_context()

    base_scores, base_evidence = freeze._score_measures(
        rows_by_measure,
        grid,
        CONTEXT_MEASURES,
        base_model,
    )
    base_active_context = freeze._active_from_scores(
        base_scores,
        base_evidence,
        CONTEXT_MEASURES,
        float(base_model["threshold"]),
    )

    historical_section5 = extract_events(load_json(SECTION5_BASE_FROZEN_PATH), SECTION5_MEASURES)
    replayed_section5 = {key for key in base_active_context if key[0] in SECTION5_MEASURES}
    if replayed_section5 != historical_section5:
        missing = sorted(historical_section5 - replayed_section5)
        added = sorted(replayed_section5 - historical_section5)
        raise RuntimeError(
            "Section-5 base replay mismatch before reserve prediction: "
            f"historical={len(historical_section5)} replay={len(replayed_section5)} "
            f"missing={missing[:12]} added={added[:12]}"
        )

    sequence_scores, sequence_evidence = freeze._sequence_scores(
        rows_by_measure,
        grid,
        CONTEXT_MEASURES,
        CONTEXT_MEASURES,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    base_target = {key for key in base_active_context if key[0] in TARGET_MEASURES}
    if not base_target:
        raise RuntimeError("Reserve base-0.27 replay produced zero events")

    features = contextual.build_features(
        base_active_context,
        base_scores,
        sequence_scores,
        sequence_evidence,
    )
    target_keys = sorted(base_target)
    probabilities = contextual.predict_probabilities(
        runtime_contextual_model(frozen_model),
        target_keys,
        features,
    )
    candidate = contextual.apply_prune_fraction(
        base_active_context,
        TARGET_MEASURES,
        probabilities,
        prune_fraction,
    )

    expected_pruned = int(math.floor(len(base_target) * prune_fraction))
    expected_candidate = len(base_target) - expected_pruned
    if len(candidate) != expected_candidate:
        raise RuntimeError(
            f"Reserve prune-count invariant failed: candidate={len(candidate)} expected={expected_candidate}"
        )
    if not candidate.issubset(base_target):
        raise RuntimeError("Reserve contextual candidate is not a strict subset/equal subset of base-0.27 events")

    base_output = {
        "schemaVersion": 1,
        "artifact": "v143-reserve-97-113-base027-frozen-events",
        "measures": "97-113",
        "contextMeasures": "81-113",
        "threshold": 0.27,
        "eventCount": len(base_target),
        "events": event_payload(
            base_target,
            base_scores,
            base_evidence,
            sequence_scores,
            sequence_evidence,
            probabilities,
        ),
        "predictionFrozenBeforeReserveGrading": True,
        "professionalReferenceUsedForPrediction": False,
        "targetReserveReferenceOpened": False,
        "reservePayloadOpened": False,
        "productionModified": False,
    }
    BASE_OUTPUT_PATH.write_text(json.dumps(base_output, indent=2) + "\n", encoding="utf-8")

    candidate_output = {
        "schemaVersion": 1,
        "artifact": "v143-reserve-97-113-contextual-prune-frozen-events",
        "measures": "97-113",
        "contextMeasures": "81-113",
        "baseThreshold": 0.27,
        "pruneFraction": prune_fraction,
        "baseEventCount": len(base_target),
        "prunedEventCount": expected_pruned,
        "eventCount": len(candidate),
        "events": event_payload(
            candidate,
            base_scores,
            base_evidence,
            sequence_scores,
            sequence_evidence,
            probabilities,
        ),
        "candidateAddsEvents": False,
        "candidateRelocatesEvents": False,
        "predictionFrozenBeforeReserveGrading": True,
        "professionalReferenceUsedForPrediction": False,
        "targetReserveReferenceOpened": False,
        "reservePayloadOpened": False,
        "productionModified": False,
    }
    CANDIDATE_OUTPUT_PATH.write_text(json.dumps(candidate_output, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schemaVersion": 1,
        "freeze": "v143-contextual-prune-reserve-predictions-before-grading",
        "developmentMeasures": "17-96",
        "contextMeasures": "81-113",
        "reserveMeasures": "97-113",
        "contextPolicy": "Use frozen reference-free section-5 features as left context plus the sealed reserve reference-free cache; no reserve labels or professional reference are opened.",
        "frozenParameters": {
            "baseThreshold": 0.27,
            "l2": float(frozen_model["l2"]),
            "pruneFraction": prune_fraction,
        },
        "invariants": {
            "developmentPredictionsFrozenBeforeReserveGrading": True,
            "section5BaseReplayMatchedHistoricalFreeze": True,
            "reserveCacheReferenceFree": True,
            "professionalReferenceUsedForPrediction": False,
            "targetReserveReferenceOpened": False,
            "reservePayloadOpened": False,
            "candidateAddsEvents": False,
            "candidateRelocatesEvents": False,
            "productionModified": False,
        },
        "counts": {
            "section5HistoricalBaseEvents": len(historical_section5),
            "section5ReplayedBaseEvents": len(replayed_section5),
            "reserveBaseEvents": len(base_target),
            "reservePrunedEvents": expected_pruned,
            "reserveContextualEvents": len(candidate),
        },
        "fingerprints": {
            "section5ReferenceFreeCacheSha256": sha256(SECTION5_CACHE_PATH),
            "reserveReferenceFreeCacheSha256": sha256(RESERVE_CACHE_PATH),
            "section5HistoricalBaseFreezeSha256": sha256(SECTION5_BASE_FROZEN_PATH),
            "developmentFreezeManifestSha256": sha256(FREEZE_MANIFEST_PATH),
            "frozenContextualModelSha256": sha256(FROZEN_MODEL_PATH),
            "baseModelSha256": sha256(freeze.BASE_MODEL_PATH),
            "sequenceModelSha256": sha256(freeze.SEQUENCE_MODEL_PATH),
            "frozenBaseReserveEventsSha256": sha256(BASE_OUTPUT_PATH),
            "frozenContextualReserveEventsSha256": sha256(CANDIDATE_OUTPUT_PATH),
        },
    }
    PREDICTION_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("=== V143 SEALED RESERVE FROZEN-MODEL PREDICTION ===")
    print("CONTEXT_MEASURES", "81-113")
    print("TARGET_MEASURES", "97-113")
    print("SECTION5_BASE_REPLAY_MATCH", True)
    print("SECTION5_BASE_COUNT", len(replayed_section5))
    print("RESERVE_BASE_COUNT", len(base_target))
    print("RESERVE_PRUNED_COUNT", expected_pruned)
    print("RESERVE_CONTEXTUAL_COUNT", len(candidate))
    print("PROFESSIONAL_REFERENCE_USED_FOR_PREDICTION", False)
    print("TARGET_RESERVE_REFERENCE_OPENED", False)
    print("RESERVE_PAYLOAD_OPENED", False)
    print("PRODUCTION_MODIFIED", False)
    print(f"WROTE_BASE={BASE_OUTPUT_PATH}")
    print(f"WROTE_CANDIDATE={CANDIDATE_OUTPUT_PATH}")
    print(f"WROTE_MANIFEST={PREDICTION_MANIFEST_PATH}")


if __name__ == "__main__":
    main()
