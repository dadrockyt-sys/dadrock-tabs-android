from __future__ import annotations

import math
from statistics import median
from typing import Any, Mapping, Sequence


STRICT_MIN_STEM_SUPPORT = 2
STRICT_MIN_SWEEP_SUPPORT = 3
STRICT_MIN_DETECTION_COUNT = 4
RESIDUAL_WINDOWS_SECONDS = (0.03, 0.06, 0.10)
PATTERN_LAGS = (1, 2, 4)

EventKey = tuple[int, int]


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def _percentile(values: Sequence[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = max(0.0, min(1.0, float(fraction))) * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    alpha = position - lo
    return ordered[lo] * (1.0 - alpha) + ordered[hi] * alpha


def _strict_row(row: Mapping[str, Any]) -> bool:
    return (
        int(row.get("stemSupportMax") or 0) >= STRICT_MIN_STEM_SUPPORT
        and int(row.get("sweepSupportMax") or 0) >= STRICT_MIN_SWEEP_SUPPORT
        and int(row.get("detectionCountSum") or 0) >= STRICT_MIN_DETECTION_COUNT
    )


def _grid_by_measure(grid: Mapping[EventKey, float]) -> dict[int, list[tuple[int, float]]]:
    grouped: dict[int, list[tuple[int, float]]] = {}
    for raw_key, raw_time in grid.items():
        try:
            measure = int(raw_key[0])
            step = int(raw_key[1])
            time_value = float(raw_time)
        except (TypeError, ValueError, IndexError):
            continue
        if not math.isfinite(time_value):
            continue
        grouped.setdefault(measure, []).append((step, time_value))
    for values in grouped.values():
        values.sort(key=lambda item: item[0])
    return grouped


def _nearest_grid_residual(
    row: Mapping[str, Any],
    grid_by_measure: Mapping[int, Sequence[tuple[int, float]]],
) -> tuple[int, float] | None:
    try:
        measure = int(row["measure"])
        onset = float(row["onsetTime"])
    except (KeyError, TypeError, ValueError):
        return None
    if not math.isfinite(onset):
        return None
    options = grid_by_measure.get(measure) or ()
    if not options:
        return None
    step, grid_time = min(
        options,
        key=lambda item: (abs(onset - float(item[1])), int(item[0])),
    )
    return int(step), float(onset - float(grid_time))


def _residual_summary(values: Sequence[float]) -> dict[str, Any]:
    signed = [float(value) for value in values]
    absolute = [abs(value) for value in signed]
    count = len(signed)
    return {
        "count": count,
        "signedMeanSeconds": (sum(signed) / count) if count else 0.0,
        "signedMedianSeconds": float(median(signed)) if signed else 0.0,
        "absoluteP50Seconds": _percentile(absolute, 0.50),
        "absoluteP90Seconds": _percentile(absolute, 0.90),
        "absoluteP95Seconds": _percentile(absolute, 0.95),
        "absoluteMaxSeconds": max(absolute, default=0.0),
        "within30ms": (sum(value <= 0.03 for value in absolute) / count) if count else 0.0,
        "within60ms": (sum(value <= 0.06 for value in absolute) / count) if count else 0.0,
        "within100ms": (sum(value <= 0.10 for value in absolute) / count) if count else 0.0,
    }


def _jaccard(left: set[int], right: set[int]) -> float:
    union = left | right
    if not union:
        return 1.0
    return len(left & right) / len(union)


def _pattern_consistency(
    occupied: Mapping[int, set[int]],
) -> dict[str, Any]:
    measures = sorted(occupied)
    result: dict[str, Any] = {}
    for lag in PATTERN_LAGS:
        scores: list[float] = []
        for measure in measures:
            other = measure + lag
            if other not in occupied:
                continue
            scores.append(_jaccard(occupied[measure], occupied[other]))
        result[f"lag{lag}"] = {
            "pairCount": len(scores),
            "meanJaccard": (sum(scores) / len(scores)) if scores else 0.0,
            "medianJaccard": float(median(scores)) if scores else 0.0,
        }
    return result


def summarize_reference_free_timing_consistency(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    *,
    tempo_bpm: float,
    first_beat_in_measure: int,
    downbeat_index_mod4: int,
    beat_confidence: float,
    bar_confidence: float,
) -> dict[str, Any]:
    """Describe grid alignment/structural consistency without choosing a correction.

    This diagnostic is deliberately observational. It does not change tempo,
    downbeat phase, measure numbering, attack placement, or candidate selection.
    A later shadow may compare alternative timing hypotheses, but no phase is
    accepted merely because it improves a professional/reference score.
    """
    grid_by_measure = _grid_by_measure(grid)
    all_residuals: list[float] = []
    strict_residuals: list[float] = []
    strict_steps_by_measure: dict[int, set[int]] = {}
    row_steps: list[dict[str, Any]] = []

    for row in carrier_rows:
        nearest = _nearest_grid_residual(row, grid_by_measure)
        if nearest is None:
            continue
        step, residual = nearest
        measure = int(row["measure"])
        strict = _strict_row(row)
        all_residuals.append(residual)
        if strict:
            strict_residuals.append(residual)
            strict_steps_by_measure.setdefault(measure, set()).add(step)
        row_steps.append(
            {
                "measure": measure,
                "nearestStep": step,
                "signedResidualSeconds": residual,
                "strictPhysicalSupport": strict,
            }
        )

    per_measure_abs: dict[int, list[float]] = {}
    for item in row_steps:
        if not item["strictPhysicalSupport"]:
            continue
        per_measure_abs.setdefault(int(item["measure"]), []).append(
            abs(float(item["signedResidualSeconds"]))
        )
    measure_medians = {
        measure: float(median(values))
        for measure, values in per_measure_abs.items()
        if values
    }
    worst_measures = [
        {"measure": int(measure), "medianAbsoluteResidualSeconds": float(value)}
        for measure, value in sorted(
            measure_medians.items(),
            key=lambda item: (-item[1], item[0]),
        )[:12]
    ]

    return {
        "schemaVersion": 1,
        "mode": "v143-reference-free-timing-consistency-shadow",
        "timing": {
            "tempoBpm": float(tempo_bpm),
            "firstBeatInMeasure": int(first_beat_in_measure),
            "downbeatIndexMod4": int(downbeat_index_mod4),
            "beatConfidence": float(beat_confidence),
            "barConfidence": float(bar_confidence),
        },
        "rowCount": len(row_steps),
        "strictRowCount": len(strict_residuals),
        "allRowsResidual": _residual_summary(all_residuals),
        "strictRowsResidual": _residual_summary(strict_residuals),
        "strictPatternConsistency": _pattern_consistency(strict_steps_by_measure),
        "worstStrictMeasures": worst_measures,
        "invariants": {
            "tempoChanged": False,
            "barPhaseChanged": False,
            "attackTimingChanged": False,
            "candidateSelectionChanged": False,
            "pitchChanged": False,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        },
    }


__all__ = [
    "STRICT_MIN_STEM_SUPPORT",
    "STRICT_MIN_SWEEP_SUPPORT",
    "STRICT_MIN_DETECTION_COUNT",
    "RESIDUAL_WINDOWS_SECONDS",
    "PATTERN_LAGS",
    "summarize_reference_free_timing_consistency",
]
