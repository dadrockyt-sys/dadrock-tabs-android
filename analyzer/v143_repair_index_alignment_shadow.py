from __future__ import annotations

import bisect
import math
from statistics import mean, median
from typing import Any, Sequence


BEATS_PER_MEASURE = 4
MATCH_TOLERANCE_PERIOD_RATIO = 0.25


def summarize_repair_index_alignment(
    original_beat_times: Sequence[float],
    repaired_beat_times: Sequence[float],
    expected_period_seconds: float,
    *,
    tolerance_period_ratio: float = MATCH_TOLERANCE_PERIOD_RATIO,
) -> dict[str, Any]:
    """Trace raw-index offset along a repaired pulse train without labels.

    Each repaired beat is matched to its nearest raw tracked beat inside a fixed
    fraction of the expected beat period. A false inserted raw pulse causes later
    matched raw indices to advance by one relative to repaired indices; a dropped
    raw pulse causes the opposite. Runs of constant modulo-4 index offset expose
    exactly where raw bar-phase inheritance can become stale after repair.
    """
    original = tuple(float(value) for value in original_beat_times)
    repaired = tuple(float(value) for value in repaired_beat_times)
    period = float(expected_period_seconds)
    tolerance_ratio = float(tolerance_period_ratio)
    if not original or not repaired:
        raise ValueError("original and repaired beat sequences must be non-empty")
    if not math.isfinite(period) or period <= 0.0:
        raise ValueError("expected_period_seconds must be positive and finite")
    if not 0.0 < tolerance_ratio <= 0.5:
        raise ValueError("tolerance_period_ratio must be in (0, 0.5]")
    if any(right <= left for left, right in zip(original[:-1], original[1:])):
        raise ValueError("original beat times must be strictly increasing")
    if any(right <= left for left, right in zip(repaired[:-1], repaired[1:])):
        raise ValueError("repaired beat times must be strictly increasing")

    tolerance = tolerance_ratio * period
    matches: list[dict[str, Any]] = []
    for repaired_index, repaired_time in enumerate(repaired):
        position = bisect.bisect_left(original, repaired_time)
        options = [index for index in (position - 1, position) if 0 <= index < len(original)]
        if not options:
            continue
        raw_index = min(options, key=lambda index: (abs(original[index] - repaired_time), index))
        residual = float(original[raw_index] - repaired_time)
        if abs(residual) > tolerance:
            continue
        delta = int(raw_index - repaired_index)
        matches.append(
            {
                "repairedIndex": int(repaired_index),
                "rawIndex": int(raw_index),
                "repairedTime": float(repaired_time),
                "rawTime": float(original[raw_index]),
                "signedResidualSeconds": residual,
                "absoluteResidualSeconds": abs(residual),
                "rawMinusRepairedIndex": delta,
                "rawMinusRepairedIndexMod4": int(delta % BEATS_PER_MEASURE),
            }
        )

    runs: list[dict[str, Any]] = []
    current: list[dict[str, Any]] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        deltas = [int(item["rawMinusRepairedIndex"]) for item in current]
        modulo = int(current[0]["rawMinusRepairedIndexMod4"])
        runs.append(
            {
                "rawMinusRepairedIndexMod4": modulo,
                "matchCount": len(current),
                "startRepairedIndex": int(current[0]["repairedIndex"]),
                "endRepairedIndexExclusive": int(current[-1]["repairedIndex"] + 1),
                "startTimeSeconds": float(current[0]["repairedTime"]),
                "endTimeSeconds": float(current[-1]["repairedTime"]),
                "medianRawMinusRepairedIndex": float(median(deltas)),
                "minimumRawMinusRepairedIndex": int(min(deltas)),
                "maximumRawMinusRepairedIndex": int(max(deltas)),
            }
        )
        current = []

    for item in matches:
        if not current:
            current = [item]
            continue
        previous = current[-1]
        contiguous = (
            int(item["repairedIndex"]) == int(previous["repairedIndex"]) + 1
            and int(item["rawIndex"]) == int(previous["rawIndex"]) + 1
            and int(item["rawMinusRepairedIndexMod4"])
            == int(previous["rawMinusRepairedIndexMod4"])
        )
        if not contiguous:
            flush()
        current.append(item)
    flush()

    changes = []
    for left, right in zip(runs[:-1], runs[1:]):
        left_phase = int(left["rawMinusRepairedIndexMod4"])
        right_phase = int(right["rawMinusRepairedIndexMod4"])
        if left_phase == right_phase:
            continue
        changes.append(
            {
                "fromRawMinusRepairedIndexMod4": left_phase,
                "toRawMinusRepairedIndexMod4": right_phase,
                "leftEndRepairedIndexExclusive": int(left["endRepairedIndexExclusive"]),
                "rightStartRepairedIndex": int(right["startRepairedIndex"]),
                "rightStartTimeSeconds": float(right["startTimeSeconds"]),
            }
        )

    residuals = [float(item["absoluteResidualSeconds"]) for item in matches]
    return {
        "schemaVersion": 1,
        "originalBeatCount": len(original),
        "repairedBeatCount": len(repaired),
        "matchTolerancePeriodRatio": tolerance_ratio,
        "matchToleranceSeconds": float(tolerance),
        "matchedBeatCount": len(matches),
        "matchedBeatFraction": float(len(matches) / len(repaired)),
        "absoluteResidualMeanSeconds": float(mean(residuals)) if residuals else 0.0,
        "absoluteResidualMedianSeconds": float(median(residuals)) if residuals else 0.0,
        "offsetRuns": runs,
        "offsetChangePointCount": len(changes),
        "offsetChangePoints": changes,
        "multipleModuloOffsetsObserved": len({int(item["rawMinusRepairedIndexMod4"]) for item in runs}) > 1,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "runtimePhaseChanged": False,
        "productionModified": False,
    }


__all__ = [
    "BEATS_PER_MEASURE",
    "MATCH_TOLERANCE_PERIOD_RATIO",
    "summarize_repair_index_alignment",
]
