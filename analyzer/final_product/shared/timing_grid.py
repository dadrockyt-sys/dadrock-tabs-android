from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from statistics import median
from typing import Any, Iterable, Sequence


DEFAULT_BEATS_PER_MEASURE = 4
DEFAULT_SUBDIVISIONS_PER_BEAT = 4
DEFAULT_MAX_GRID_ERROR_SECONDS = 0.10


@dataclass(frozen=True)
class TimingSlot:
    global_step: int
    measure: int
    step: int
    time_seconds: float


def _finite_float(value: Any, name: str) -> float:
    out = float(value)
    if not math.isfinite(out):
        raise ValueError(f"{name} must be finite")
    return out


def validate_beat_times(beat_times: Iterable[float]) -> list[float]:
    beats = [_finite_float(value, "beat time") for value in beat_times]
    if len(beats) < 2:
        raise ValueError("At least two beat times are required")
    if beats[0] < 0.0:
        raise ValueError("Beat times cannot be negative")
    for left, right in zip(beats[:-1], beats[1:]):
        if right <= left:
            raise ValueError("Beat times must be strictly increasing")
    return beats


def build_subdivision_grid(
    beat_times: Iterable[float],
    *,
    beats_per_measure: int = DEFAULT_BEATS_PER_MEASURE,
    subdivisions_per_beat: int = DEFAULT_SUBDIVISIONS_PER_BEAT,
    measure_start: int = 1,
    first_beat_in_measure: int = 0,
) -> list[TimingSlot]:
    """Build an instrument-agnostic authenticated subdivision grid.

    The caller supplies reference-free beat times and explicit bar phase. With
    the defaults this yields the sixteen within-measure steps used by the DadRock
    professional render contracts without assuming that uploaded audio starts on
    a downbeat.
    """
    beats = validate_beat_times(beat_times)
    beats_per_measure = int(beats_per_measure)
    subdivisions_per_beat = int(subdivisions_per_beat)
    measure_start = int(measure_start)
    first_beat_in_measure = int(first_beat_in_measure)

    if beats_per_measure <= 0 or subdivisions_per_beat <= 0:
        raise ValueError("Meter and subdivision counts must be positive")
    if measure_start < 1:
        raise ValueError("measure_start must be at least 1")
    if not 0 <= first_beat_in_measure < beats_per_measure:
        raise ValueError("first_beat_in_measure is outside the requested meter")

    intervals = [right - left for left, right in zip(beats[:-1], beats[1:])]
    tail_interval = float(median(intervals[-min(4, len(intervals)) :]))
    steps_per_measure = beats_per_measure * subdivisions_per_beat

    slots: list[TimingSlot] = []
    for beat_index, beat_time in enumerate(beats):
        interval = intervals[beat_index] if beat_index < len(intervals) else tail_interval
        absolute_beat = first_beat_in_measure + beat_index
        measure = measure_start + absolute_beat // beats_per_measure
        beat_in_measure = absolute_beat % beats_per_measure

        for subdivision in range(subdivisions_per_beat):
            step = beat_in_measure * subdivisions_per_beat + subdivision
            time_seconds = beat_time + interval * subdivision / float(
                subdivisions_per_beat
            )
            slots.append(
                TimingSlot(
                    global_step=len(slots),
                    measure=int(measure),
                    step=int(step),
                    time_seconds=float(time_seconds),
                )
            )

    if any(slot.step < 0 or slot.step >= steps_per_measure for slot in slots):
        raise RuntimeError("Generated timing grid contains an invalid step")
    if any(
        right.time_seconds <= left.time_seconds
        for left, right in zip(slots[:-1], slots[1:])
    ):
        raise RuntimeError("Generated timing grid is not strictly increasing")
    return slots


def nearest_timing_slot(
    onset_time: float,
    slots: Sequence[TimingSlot],
    *,
    max_grid_error_seconds: float = DEFAULT_MAX_GRID_ERROR_SECONDS,
) -> tuple[TimingSlot, float] | None:
    if not slots:
        return None
    onset = _finite_float(onset_time, "onset_time")
    maximum_error = _finite_float(max_grid_error_seconds, "max_grid_error_seconds")
    if maximum_error < 0.0:
        raise ValueError("max_grid_error_seconds cannot be negative")

    times = [slot.time_seconds for slot in slots]
    index = bisect_left(times, onset)
    candidates: list[TimingSlot] = []
    if index < len(slots):
        candidates.append(slots[index])
    if index > 0:
        candidates.append(slots[index - 1])
    if not candidates:
        return None

    best = min(
        candidates,
        key=lambda slot: (abs(slot.time_seconds - onset), slot.global_step),
    )
    error = abs(best.time_seconds - onset)
    if error > maximum_error:
        return None
    return best, float(error)


__all__ = [
    "DEFAULT_BEATS_PER_MEASURE",
    "DEFAULT_SUBDIVISIONS_PER_BEAT",
    "DEFAULT_MAX_GRID_ERROR_SECONDS",
    "TimingSlot",
    "validate_beat_times",
    "build_subdivision_grid",
    "nearest_timing_slot",
]
