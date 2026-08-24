from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import median
from typing import Any, Sequence

import numpy as np

from v143_reference_free_timing import (
    TIMING_SAMPLE_RATE,
    ReferenceFreeTimingEstimate,
    _finite_audio,
    _normalized_onset_envelope,
    _resample_audio,
)


STABLE_INTERVAL_MIN_RATIO = 0.85
STABLE_INTERVAL_MAX_RATIO = 1.15
SEARCH_RADIUS_PERIOD_RATIO = 0.22
BOUNDARY_SEARCH_RADIUS_PERIOD_RATIO = 0.25
ENERGY_ACTIVE_LOW_FRACTION = 0.001
ENERGY_ACTIVE_HIGH_FRACTION = 0.999
MIN_STABLE_INTERVAL_RUN = 8
LOCAL_PERIOD_WINDOW = 12


@dataclass(frozen=True)
class BeatGridRepairResult:
    timing: ReferenceFreeTimingEstimate
    original_beat_times: tuple[float, ...]
    repaired_beat_times: tuple[float, ...]
    original_interval_outlier_count: int
    repaired_interval_outlier_count: int
    stable_anchor_start_index: int
    stable_anchor_end_index: int
    stable_anchor_period_seconds: float
    active_audio_start_seconds: float
    active_audio_end_seconds: float
    leading_extended_beat_count: int
    trailing_extended_beat_count: int
    continuity_only_beat_count: int
    snapped_beat_count: int
    boundary_evidence_floor: float

    def diagnostics(self) -> dict[str, Any]:
        expected_period = 60.0 / float(self.timing.tempo_bpm)
        original_intervals = [
            b - a for a, b in zip(self.original_beat_times[:-1], self.original_beat_times[1:])
        ]
        repaired_intervals = [
            b - a for a, b in zip(self.repaired_beat_times[:-1], self.repaired_beat_times[1:])
        ]

        def summary(values: Sequence[float]) -> dict[str, float | int]:
            if not values:
                return {
                    "count": 0,
                    "ratioP01": 0.0,
                    "ratioP05": 0.0,
                    "ratioP50": 0.0,
                    "ratioP95": 0.0,
                    "ratioP99": 0.0,
                }
            ratios = np.asarray(values, dtype=np.float64) / expected_period
            return {
                "count": len(values),
                "ratioP01": float(np.quantile(ratios, 0.01)),
                "ratioP05": float(np.quantile(ratios, 0.05)),
                "ratioP50": float(np.quantile(ratios, 0.50)),
                "ratioP95": float(np.quantile(ratios, 0.95)),
                "ratioP99": float(np.quantile(ratios, 0.99)),
            }

        return {
            "originalBeatCount": len(self.original_beat_times),
            "repairedBeatCount": len(self.repaired_beat_times),
            "originalIntervalOutlierCount": int(self.original_interval_outlier_count),
            "repairedIntervalOutlierCount": int(self.repaired_interval_outlier_count),
            "stableAnchorStartIndex": int(self.stable_anchor_start_index),
            "stableAnchorEndIndex": int(self.stable_anchor_end_index),
            "stableAnchorPeriodSeconds": float(self.stable_anchor_period_seconds),
            "activeAudioStartSeconds": float(self.active_audio_start_seconds),
            "activeAudioEndSeconds": float(self.active_audio_end_seconds),
            "leadingExtendedBeatCount": int(self.leading_extended_beat_count),
            "trailingExtendedBeatCount": int(self.trailing_extended_beat_count),
            "continuityOnlyBeatCount": int(self.continuity_only_beat_count),
            "snappedBeatCount": int(self.snapped_beat_count),
            "boundaryEvidenceFloor": float(self.boundary_evidence_floor),
            "originalIntervals": summary(original_intervals),
            "repairedIntervals": summary(repaired_intervals),
            "barPhaseChanged": False,
            "tempoChanged": False,
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _stable_anchor_run(beat_times: Sequence[float], expected_period: float) -> tuple[int, int, float]:
    intervals = [float(b - a) for a, b in zip(beat_times[:-1], beat_times[1:])]
    good = [
        STABLE_INTERVAL_MIN_RATIO <= interval / expected_period <= STABLE_INTERVAL_MAX_RATIO
        for interval in intervals
    ]
    best_start = best_end = -1
    current_start = 0
    for index, is_good in enumerate(good + [False]):
        if is_good:
            continue
        end = index
        if end - current_start > best_end - best_start:
            best_start, best_end = current_start, end
        current_start = index + 1
    if best_start < 0 or best_end - best_start < MIN_STABLE_INTERVAL_RUN:
        raise RuntimeError("No sufficiently long tempo-stable beat run was found")
    # Interval run [start,end) corresponds to beat indices [start,end].
    local = intervals[best_start:best_end]
    return int(best_start), int(best_end), float(median(local))


def _active_energy_bounds(audio: np.ndarray, sample_rate: int) -> tuple[float, float]:
    power = np.square(np.asarray(audio, dtype=np.float64))
    total = float(np.sum(power))
    duration = len(power) / float(sample_rate)
    if total <= 1.0e-12:
        return 0.0, duration
    cumulative = np.cumsum(power)
    lo = int(np.searchsorted(cumulative, ENERGY_ACTIVE_LOW_FRACTION * total))
    hi = int(np.searchsorted(cumulative, ENERGY_ACTIVE_HIGH_FRACTION * total))
    lo = max(0, min(len(power) - 1, lo))
    hi = max(lo, min(len(power) - 1, hi))
    return float(lo / sample_rate), float(hi / sample_rate)


def _nearest_accent_index(frame_times: np.ndarray, time_seconds: float) -> int:
    position = int(np.searchsorted(frame_times, float(time_seconds)))
    options = [index for index in (position - 1, position) if 0 <= index < len(frame_times)]
    if not options:
        return 0
    return min(options, key=lambda index: abs(float(frame_times[index]) - float(time_seconds)))


def _snap_prediction(
    predicted: float,
    period: float,
    frame_times: np.ndarray,
    accents: np.ndarray,
    *,
    boundary: bool,
) -> tuple[float, float, bool]:
    radius = period * (
        BOUNDARY_SEARCH_RADIUS_PERIOD_RATIO if boundary else SEARCH_RADIUS_PERIOD_RATIO
    )
    left = int(np.searchsorted(frame_times, predicted - radius, side="left"))
    right = int(np.searchsorted(frame_times, predicted + radius, side="right"))
    left = max(0, min(len(frame_times) - 1, left))
    right = max(left + 1, min(len(frame_times), right))
    candidate_times = frame_times[left:right]
    candidate_accents = accents[left:right]
    if len(candidate_times) == 0:
        index = _nearest_accent_index(frame_times, predicted)
        return float(frame_times[index]), float(accents[index]), False
    distances = np.abs(candidate_times - predicted) / max(radius, 1.0e-9)
    scores = candidate_accents - 0.55 * np.square(distances)
    winner = int(np.argmax(scores))
    chosen = float(candidate_times[winner])
    evidence = float(candidate_accents[winner])
    snapped = abs(chosen - predicted) <= radius
    return chosen, evidence, snapped


def _interval_outlier_count(beat_times: Sequence[float], expected_period: float) -> int:
    return sum(
        not (STABLE_INTERVAL_MIN_RATIO <= (b - a) / expected_period <= STABLE_INTERVAL_MAX_RATIO)
        for a, b in zip(beat_times[:-1], beat_times[1:])
    )


def repair_reference_free_beat_grid_from_samples(
    samples: Any,
    sample_rate: int,
    timing: ReferenceFreeTimingEstimate,
) -> BeatGridRepairResult:
    """Repair sub-beat duplicates and premature boundaries from audio only.

    The original tempo and 4/4 phase remain immutable. A longest tempo-stable
    region anchors a one-pulse-per-beat trajectory. Each next beat is predicted
    from recent stable intervals and may snap only to nearby full-mix transient
    evidence. Interior weak beats may use tempo continuity, because a musical beat
    need not contain a note onset. New leading/trailing beats are stricter: they
    are admitted only when local transient evidence exceeds an adaptive floor and
    they remain inside the cumulative-energy active range. No external labels,
    target measure counts, or song identity are accepted.
    """
    if not isinstance(timing, ReferenceFreeTimingEstimate):
        raise TypeError("timing must be ReferenceFreeTimingEstimate")
    original = tuple(float(value) for value in timing.beat_times)
    if len(original) < MIN_STABLE_INTERVAL_RUN + 2:
        raise ValueError("Not enough original beats for repair")
    expected_period = 60.0 / float(timing.tempo_bpm)
    if not math.isfinite(expected_period) or expected_period <= 0.0:
        raise ValueError("Invalid timing tempo")

    mono = _finite_audio(samples)
    analysis_audio = _resample_audio(mono, int(sample_rate), TIMING_SAMPLE_RATE)
    onset, low_energy, frame_times = _normalized_onset_envelope(
        analysis_audio,
        TIMING_SAMPLE_RATE,
    )
    accents = np.asarray(onset + 0.25 * low_energy, dtype=np.float64)
    active_start, active_end = _active_energy_bounds(analysis_audio, TIMING_SAMPLE_RATE)

    anchor_start, anchor_end, anchor_period = _stable_anchor_run(original, expected_period)
    anchor_index = (anchor_start + anchor_end) // 2
    anchor_time = float(original[anchor_index])

    raw_accent_values = [
        float(accents[_nearest_accent_index(frame_times, beat_time)]) for beat_time in original
    ]
    boundary_floor = max(
        float(np.quantile(accents, 0.70)),
        0.30 * float(median(raw_accent_values)),
    )

    accepted_forward: list[float] = [anchor_time]
    forward_intervals: list[float] = []
    snapped_count = 0
    continuity_only = 0
    trailing_extended = 0
    raw_last = float(original[-1])

    while True:
        local_period = (
            float(median(forward_intervals[-LOCAL_PERIOD_WINDOW:]))
            if forward_intervals
            else anchor_period
        )
        local_period = min(
            expected_period * STABLE_INTERVAL_MAX_RATIO,
            max(expected_period * STABLE_INTERVAL_MIN_RATIO, local_period),
        )
        predicted = accepted_forward[-1] + local_period
        if predicted > active_end + 0.10 * expected_period:
            break
        boundary = predicted > raw_last + 0.35 * expected_period
        chosen, evidence, snapped = _snap_prediction(
            predicted,
            local_period,
            frame_times,
            accents,
            boundary=boundary,
        )
        if boundary and evidence < boundary_floor:
            break
        interval = chosen - accepted_forward[-1]
        ratio = interval / expected_period
        if not (STABLE_INTERVAL_MIN_RATIO <= ratio <= STABLE_INTERVAL_MAX_RATIO):
            chosen = predicted
            interval = local_period
            snapped = False
        accepted_forward.append(float(chosen))
        forward_intervals.append(float(interval))
        snapped_count += int(snapped)
        continuity_only += int(not snapped)
        trailing_extended += int(chosen > raw_last + 0.35 * expected_period)
        if len(accepted_forward) > 10000:
            raise RuntimeError("Beat repair forward loop exceeded safety bound")

    accepted_backward: list[float] = []
    backward_intervals: list[float] = []
    leading_extended = 0
    raw_first = float(original[0])
    current = anchor_time
    while True:
        local_period = (
            float(median(backward_intervals[-LOCAL_PERIOD_WINDOW:]))
            if backward_intervals
            else anchor_period
        )
        local_period = min(
            expected_period * STABLE_INTERVAL_MAX_RATIO,
            max(expected_period * STABLE_INTERVAL_MIN_RATIO, local_period),
        )
        predicted = current - local_period
        if predicted < active_start - 0.10 * expected_period or predicted < 0.0:
            break
        boundary = predicted < raw_first - 0.35 * expected_period
        chosen, evidence, snapped = _snap_prediction(
            predicted,
            local_period,
            frame_times,
            accents,
            boundary=boundary,
        )
        if boundary and evidence < boundary_floor:
            break
        interval = current - chosen
        ratio = interval / expected_period
        if not (STABLE_INTERVAL_MIN_RATIO <= ratio <= STABLE_INTERVAL_MAX_RATIO):
            chosen = predicted
            interval = local_period
            snapped = False
        accepted_backward.append(float(chosen))
        backward_intervals.append(float(interval))
        snapped_count += int(snapped)
        continuity_only += int(not snapped)
        leading_extended += int(chosen < raw_first - 0.35 * expected_period)
        current = float(chosen)
        if len(accepted_backward) > 10000:
            raise RuntimeError("Beat repair backward loop exceeded safety bound")

    repaired = tuple(reversed(accepted_backward)) + tuple(accepted_forward)
    if len(repaired) < MIN_STABLE_INTERVAL_RUN + 2:
        raise RuntimeError("Beat repair produced too few beats")
    if any(b <= a for a, b in zip(repaired[:-1], repaired[1:])):
        raise RuntimeError("Beat repair produced non-increasing beat times")

    original_outliers = _interval_outlier_count(original, expected_period)
    repaired_outliers = _interval_outlier_count(repaired, expected_period)
    repaired_timing = ReferenceFreeTimingEstimate(
        beat_times=tuple(float(value) for value in repaired),
        first_beat_in_measure=int(timing.first_beat_in_measure),
        downbeat_index_mod4=int(timing.downbeat_index_mod4),
        tempo_bpm=float(timing.tempo_bpm),
        beat_confidence=float(timing.beat_confidence),
        bar_confidence=float(timing.bar_confidence),
        source_sample_rate=int(timing.source_sample_rate),
        analysis_sample_rate=int(timing.analysis_sample_rate),
    )
    return BeatGridRepairResult(
        timing=repaired_timing,
        original_beat_times=original,
        repaired_beat_times=tuple(float(value) for value in repaired),
        original_interval_outlier_count=int(original_outliers),
        repaired_interval_outlier_count=int(repaired_outliers),
        stable_anchor_start_index=int(anchor_start),
        stable_anchor_end_index=int(anchor_end),
        stable_anchor_period_seconds=float(anchor_period),
        active_audio_start_seconds=float(active_start),
        active_audio_end_seconds=float(active_end),
        leading_extended_beat_count=int(leading_extended),
        trailing_extended_beat_count=int(trailing_extended),
        continuity_only_beat_count=int(continuity_only),
        snapped_beat_count=int(snapped_count),
        boundary_evidence_floor=float(boundary_floor),
    )


__all__ = [
    "STABLE_INTERVAL_MIN_RATIO",
    "STABLE_INTERVAL_MAX_RATIO",
    "BeatGridRepairResult",
    "repair_reference_free_beat_grid_from_samples",
]
