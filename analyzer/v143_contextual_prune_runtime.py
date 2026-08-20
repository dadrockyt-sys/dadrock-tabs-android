#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

import v143_correlation_safe_fixed_count_reranker_freeze as freeze


ROOT = Path(__file__).resolve().parents[1]
CAL = ROOT / "public" / "training" / "v143-musical-reconstruction-calibration"
CONTEXTUAL_MODEL_PATH = CAL / "contextual-prune-frozen-model.json"

FEATURE_NAMES = (
    "baseScore",
    "sequenceScore",
    "sequenceEvidence",
    "stepSin",
    "stepCos",
    "strongBeat",
    "eighthGrid",
    "measureBaseCount",
    "neighborStepCount1",
    "neighborStepCount2",
    "sameStepAdjacentMeasures",
    "sameStepTwoMeasures",
    "sameStepFourMeasures",
    "sameStepWindow4Count",
    "baseSequenceInteraction",
)


@dataclass(frozen=True)
class ContextualPruneResult:
    base_events: frozenset[tuple[int, int]]
    candidate_events: frozenset[tuple[int, int]]
    base_scores: dict[tuple[int, int], float]
    sequence_scores: dict[tuple[int, int], float]
    sequence_evidence: dict[tuple[int, int], bool]
    keep_probabilities: dict[tuple[int, int], float]
    base_threshold: float
    prune_fraction: float

    @property
    def pruned_events(self) -> frozenset[tuple[int, int]]:
        return frozenset(self.base_events - self.candidate_events)

    def diagnostics(self) -> dict[str, Any]:
        return {
            "baseEventCount": len(self.base_events),
            "candidateEventCount": len(self.candidate_events),
            "prunedEventCount": len(self.pruned_events),
            "baseThreshold": self.base_threshold,
            "pruneFraction": self.prune_fraction,
            "candidateSubsetOfBase": self.candidate_events.issubset(self.base_events),
            "candidateAddsEvents": False,
            "candidateRelocatesEvents": False,
            "professionalReferenceRequiredAtRuntime": False,
        }


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists() or path.stat().st_size <= 0:
        raise RuntimeError(f"Missing required V143 artifact: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path}")
    return payload


def _validate_models(
    base_model: dict[str, Any],
    sequence_model: dict[str, Any],
    contextual_model: dict[str, Any],
) -> tuple[float, float]:
    if float(base_model.get("threshold", -1.0)) != 0.27:
        raise RuntimeError(f"Unexpected contextual-prune base threshold: {base_model.get('threshold')}")
    if sequence_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Sequence scorer unexpectedly requires professional reference")
    if contextual_model.get("model") != "v143-contextual-prune":
        raise RuntimeError(f"Unexpected contextual model: {contextual_model.get('model')}")
    if tuple(contextual_model.get("featureNames", ())) != FEATURE_NAMES:
        raise RuntimeError("Frozen contextual feature schema changed")
    if contextual_model.get("professionalReferenceRequiredAtRuntime") is not False:
        raise RuntimeError("Contextual prune unexpectedly requires professional reference")
    if contextual_model.get("candidateAddsEvents") is not False:
        raise RuntimeError("Contextual prune unexpectedly adds events")
    if contextual_model.get("candidateRelocatesEvents") is not False:
        raise RuntimeError("Contextual prune unexpectedly relocates events")
    if contextual_model.get("measures97To113UsedForTraining") is not False:
        raise RuntimeError("Frozen contextual model claims reserve measures were used for training")
    if contextual_model.get("productionModified") is not False:
        raise RuntimeError("Frozen contextual model unexpectedly marks production modified")

    base_threshold = float(contextual_model.get("baseThreshold", -1.0))
    prune_fraction = float(contextual_model.get("pruneFraction", -1.0))
    if base_threshold != 0.27:
        raise RuntimeError(f"Frozen contextual base threshold changed: {base_threshold}")
    if prune_fraction != 0.15:
        raise RuntimeError(f"Frozen contextual prune fraction changed: {prune_fraction}")
    return base_threshold, prune_fraction


def _build_features(
    base_active: set[tuple[int, int]],
    base_scores: dict[tuple[int, int], float],
    sequence_scores: dict[tuple[int, int], float],
    sequence_evidence: dict[tuple[int, int], bool],
) -> dict[tuple[int, int], list[float]]:
    measure_counts: dict[int, int] = {}
    for measure, _step in base_active:
        measure_counts[measure] = measure_counts.get(measure, 0) + 1

    features: dict[tuple[int, int], list[float]] = {}
    for key in sorted(base_active):
        measure, step = key
        base_score = float(base_scores.get(key, 0.0))
        sequence_score = float(sequence_scores.get(key, 0.0))
        sequence_flag = 1.0 if bool(sequence_evidence.get(key, False)) else 0.0
        theta = 2.0 * math.pi * (step / 16.0)

        neighbor1 = float(
            sum((measure, s) in base_active for s in (step - 1, step + 1) if 0 <= s < 16)
        )
        neighbor2 = float(
            sum((measure, s) in base_active for s in (step - 2, step + 2) if 0 <= s < 16)
        )
        same1 = float(sum((measure + d, step) in base_active for d in (-1, 1)))
        same2 = float(sum((measure + d, step) in base_active for d in (-2, 2)))
        same4 = float(sum((measure + d, step) in base_active for d in (-4, 4)))
        same_window4 = float(
            sum((measure + d, step) in base_active for d in range(-4, 5) if d != 0)
        )

        features[key] = [
            base_score,
            sequence_score,
            sequence_flag,
            math.sin(theta),
            math.cos(theta),
            1.0 if step % 4 == 0 else 0.0,
            1.0 if step % 2 == 0 else 0.0,
            float(measure_counts.get(measure, 0)),
            neighbor1,
            neighbor2,
            same1,
            same2,
            same4,
            same_window4,
            base_score * sequence_score,
        ]
    return features


def _sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -35.0, 35.0)))


def _predict_probabilities(
    contextual_model: dict[str, Any],
    keys: list[tuple[int, int]],
    features: dict[tuple[int, int], list[float]],
) -> dict[tuple[int, int], float]:
    if not keys:
        return {}
    x = np.asarray([features[key] for key in keys], dtype=np.float64)
    mean = np.asarray(contextual_model["featureMean"], dtype=np.float64)
    std = np.asarray(contextual_model["featureStd"], dtype=np.float64)
    weights = np.asarray(contextual_model["weights"], dtype=np.float64)
    if x.shape[1] != len(FEATURE_NAMES):
        raise RuntimeError(f"Contextual feature width changed: {x.shape[1]}")
    if mean.shape != std.shape or mean.shape != (len(FEATURE_NAMES),):
        raise RuntimeError("Contextual scaler dimensions changed")
    if weights.shape != (len(FEATURE_NAMES) + 1,):
        raise RuntimeError("Contextual weight dimensions changed")
    z = (x - mean) / std
    design = np.column_stack([np.ones(len(z), dtype=np.float64), z])
    probabilities = _sigmoid(design @ weights)
    return {key: float(value) for key, value in zip(keys, probabilities)}


def _prune(
    base_active: set[tuple[int, int]],
    target_measures: set[int],
    probabilities: dict[tuple[int, int], float],
    prune_fraction: float,
) -> set[tuple[int, int]]:
    keys = sorted(key for key in base_active if key[0] in target_measures)
    if not keys:
        return set()
    prune_count = int(math.floor(len(keys) * prune_fraction))
    if prune_count <= 0:
        return set(keys)
    ranked = sorted(
        keys,
        key=lambda key: (float(probabilities.get(key, 0.5)), key[0], key[1]),
    )
    return set(keys) - set(ranked[:prune_count])


def run_contextual_prune(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    target_measures: set[int],
    *,
    context_measures: set[int] | None = None,
) -> ContextualPruneResult:
    """Run the frozen contextual-prune selector without opening any reference labels."""
    targets = set(int(value) for value in target_measures)
    context = set(int(value) for value in (context_measures or targets))
    if not targets:
        raise ValueError("target_measures cannot be empty")
    if not targets.issubset(context):
        raise ValueError("target_measures must be contained in context_measures")

    base_model = _load_json(freeze.BASE_MODEL_PATH)
    sequence_model = _load_json(freeze.SEQUENCE_MODEL_PATH)
    contextual_model = _load_json(CONTEXTUAL_MODEL_PATH)
    base_threshold, prune_fraction = _validate_models(
        base_model,
        sequence_model,
        contextual_model,
    )

    base_scores, base_evidence = freeze._score_measures(
        rows_by_measure,
        grid,
        context,
        base_model,
    )
    base_active_context = freeze._active_from_scores(
        base_scores,
        base_evidence,
        context,
        base_threshold,
    )
    sequence_scores, sequence_evidence = freeze._sequence_scores(
        rows_by_measure,
        grid,
        context,
        context,
        base_scores,
        base_evidence,
        base_model,
        sequence_model,
    )

    features = _build_features(
        base_active_context,
        base_scores,
        sequence_scores,
        sequence_evidence,
    )
    target_base = {key for key in base_active_context if key[0] in targets}
    target_keys = sorted(target_base)
    probabilities = _predict_probabilities(contextual_model, target_keys, features)
    candidate = _prune(target_base, targets, probabilities, prune_fraction)

    expected_pruned = int(math.floor(len(target_base) * prune_fraction))
    if len(target_base) - len(candidate) != expected_pruned:
        raise RuntimeError("Contextual prune count invariant failed")
    if not candidate.issubset(target_base):
        raise RuntimeError("Contextual prune emitted an event outside the base selector")

    return ContextualPruneResult(
        base_events=frozenset(target_base),
        candidate_events=frozenset(candidate),
        base_scores={key: float(value) for key, value in base_scores.items()},
        sequence_scores={key: float(value) for key, value in sequence_scores.items()},
        sequence_evidence={key: bool(value) for key, value in sequence_evidence.items()},
        keep_probabilities=probabilities,
        base_threshold=base_threshold,
        prune_fraction=prune_fraction,
    )


__all__ = [
    "CONTEXTUAL_MODEL_PATH",
    "FEATURE_NAMES",
    "ContextualPruneResult",
    "run_contextual_prune",
]
