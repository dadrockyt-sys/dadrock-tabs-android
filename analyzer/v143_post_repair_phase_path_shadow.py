from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import signal

from v143_reference_free_bar_phase_consensus import (
    _band_vector,
    _cosine_distance,
    _half_winner,
    _nearest_frame,
    _rank_phase_signal,
)
from v143_reference_free_timing import (
    STFT_HOP_SAMPLES,
    STFT_WINDOW_SAMPLES,
    TIMING_SAMPLE_RATE,
    _finite_audio,
    _normalized_onset_envelope,
    _resample_audio,
)


BEATS_PER_MEASURE = 4
LOCAL_WINDOW_BEATS = 64
LOCAL_STRIDE_BEATS = 16
MIN_WINDOW_BEATS = 32
SIGNAL_WEIGHTS = {
    "accent": 0.30,
    "lowAccent": 0.15,
    "harmonicChange": 0.30,
    "bassChange": 0.25,
}


@dataclass(frozen=True)
class PhasePathWindow:
    name: str
    start_beat_index: int
    end_beat_index_exclusive: int
    winner_downbeat_index_mod4: int
    confidence: float
    consensus_signal_count: int
    stable_across_halves: bool
    signal_winners: dict[str, int]
    candidate_combined_scores: dict[int, float]

    @property
    def independent_signal_supported(self) -> bool:
        return int(self.consensus_signal_count) >= 2

    @property
    def strong(self) -> bool:
        # No fixture-tuned confidence threshold. A local window is strong only
        # when at least two independent signals select its winner and that winner
        # is stable between the window's two halves.
        return bool(self.independent_signal_supported and self.stable_across_halves)

    def diagnostics(self) -> dict[str, Any]:
        return {
            "name": str(self.name),
            "startBeatIndex": int(self.start_beat_index),
            "endBeatIndexExclusive": int(self.end_beat_index_exclusive),
            "beatCount": int(self.end_beat_index_exclusive - self.start_beat_index),
            "winnerDownbeatIndexMod4": int(self.winner_downbeat_index_mod4),
            "winnerFirstBeatInMeasure": int((-self.winner_downbeat_index_mod4) % BEATS_PER_MEASURE),
            "confidence": float(self.confidence),
            "consensusSignalCount": int(self.consensus_signal_count),
            "stableAcrossHalves": bool(self.stable_across_halves),
            "independentSignalSupported": bool(self.independent_signal_supported),
            "strong": bool(self.strong),
            "signalWinners": dict(self.signal_winners),
            "candidateCombinedScores": {
                str(int(phase)): float(score)
                for phase, score in sorted(self.candidate_combined_scores.items())
            },
        }


def _aligned_floor(value: int) -> int:
    return max(0, int(value) - (int(value) % BEATS_PER_MEASURE))


def local_window_specs(
    beat_count: int,
    *,
    window_beats: int = LOCAL_WINDOW_BEATS,
    stride_beats: int = LOCAL_STRIDE_BEATS,
) -> tuple[tuple[str, int, int], ...]:
    n = int(beat_count)
    window = _aligned_floor(int(window_beats))
    stride = _aligned_floor(int(stride_beats))
    if window < MIN_WINDOW_BEATS:
        raise ValueError(f"window_beats must be at least {MIN_WINDOW_BEATS}")
    if stride < BEATS_PER_MEASURE:
        raise ValueError("stride_beats must be at least one 4/4 measure")
    if n < MIN_WINDOW_BEATS:
        raise ValueError(f"At least {MIN_WINDOW_BEATS} repaired beats are required")

    specs: list[tuple[str, int, int]] = []
    if n <= window:
        return (("local-000", 0, n),)

    index = 0
    start = 0
    while start + window <= n:
        specs.append((f"local-{index:03d}", int(start), int(start + window)))
        index += 1
        start += stride

    # Include an aligned tail window so the end of the repaired pulse train is
    # represented even when its length is not an exact stride multiple.
    tail_start = _aligned_floor(n - window)
    tail = (f"local-{index:03d}-tail", int(tail_start), int(n))
    if not specs or (tail[1], tail[2]) != (specs[-1][1], specs[-1][2]):
        if tail[2] - tail[1] >= MIN_WINDOW_BEATS:
            specs.append(tail)

    seen: set[tuple[int, int]] = set()
    output: list[tuple[str, int, int]] = []
    for name, start, end in specs:
        if start % BEATS_PER_MEASURE != 0:
            raise RuntimeError("local phase window start escaped 4/4 residue alignment")
        key = (int(start), int(end))
        if key in seen:
            continue
        seen.add(key)
        output.append((name, int(start), int(end)))
    return tuple(output)


def _strong_runs(windows: Sequence[PhasePathWindow]) -> tuple[dict[str, Any], ...]:
    runs: list[dict[str, Any]] = []
    current: list[PhasePathWindow] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        phase = int(current[0].winner_downbeat_index_mod4)
        runs.append(
            {
                "phase": phase,
                "firstBeatInMeasure": int((-phase) % BEATS_PER_MEASURE),
                "windowCount": len(current),
                "startBeatIndex": int(current[0].start_beat_index),
                "endBeatIndexExclusive": int(current[-1].end_beat_index_exclusive),
                "minimumConfidence": float(min(item.confidence for item in current)),
                "meanConfidence": float(sum(item.confidence for item in current) / len(current)),
            }
        )
        current = []

    for window in windows:
        if not window.strong:
            flush()
            continue
        if current and int(current[-1].winner_downbeat_index_mod4) != int(window.winner_downbeat_index_mod4):
            flush()
        current.append(window)
    flush()
    return tuple(runs)


def summarize_phase_path(windows: Sequence[PhasePathWindow]) -> dict[str, Any]:
    values = tuple(windows)
    if not values:
        raise ValueError("phase path requires at least one local window")
    phase_counts = Counter(int(item.winner_downbeat_index_mod4) for item in values)
    strong_values = tuple(item for item in values if item.strong)
    strong_phase_counts = Counter(int(item.winner_downbeat_index_mod4) for item in strong_values)
    runs = _strong_runs(values)
    transitions = []
    for left, right in zip(runs[:-1], runs[1:]):
        if int(left["phase"]) == int(right["phase"]):
            continue
        transitions.append(
            {
                "fromPhase": int(left["phase"]),
                "toPhase": int(right["phase"]),
                "leftEndBeatIndexExclusive": int(left["endBeatIndexExclusive"]),
                "rightStartBeatIndex": int(right["startBeatIndex"]),
            }
        )
    return {
        "windowCount": len(values),
        "strongWindowCount": len(strong_values),
        "phaseWindowCounts": {str(key): int(value) for key, value in sorted(phase_counts.items())},
        "strongPhaseWindowCounts": {str(key): int(value) for key, value in sorted(strong_phase_counts.items())},
        "strongRuns": [dict(item) for item in runs],
        "strongTransitionCount": len(transitions),
        "strongTransitions": transitions,
        "multipleStrongPhasesObserved": len(strong_phase_counts) > 1,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def _beat_signal_values(
    samples: Any,
    sample_rate: int,
    beat_times: Sequence[float],
) -> dict[str, list[float]]:
    """Compute the same generic phase signals once for the whole repaired grid."""
    mono = _finite_audio(samples)
    audio = _resample_audio(mono, int(sample_rate), TIMING_SAMPLE_RATE)
    onset, low_energy, onset_times = _normalized_onset_envelope(audio, TIMING_SAMPLE_RATE)
    frequencies, frame_times, spectrum = signal.stft(
        audio,
        fs=TIMING_SAMPLE_RATE,
        window="hann",
        nperseg=STFT_WINDOW_SAMPLES,
        noverlap=STFT_WINDOW_SAMPLES - STFT_HOP_SAMPLES,
        nfft=STFT_WINDOW_SAMPLES,
        boundary=None,
        padded=False,
    )
    magnitude = np.abs(spectrum).astype(np.float64)

    values: dict[str, list[float]] = {
        "accent": [],
        "lowAccent": [],
        "harmonicChange": [],
        "bassChange": [],
    }
    for beat_time in beat_times:
        onset_index = _nearest_frame(onset_times, float(beat_time))
        values["accent"].append(float(onset[onset_index] + 0.25 * low_energy[onset_index]))
        values["lowAccent"].append(float(low_energy[onset_index]))

        before, after = _band_vector(
            magnitude,
            frequencies,
            frame_times,
            float(beat_time),
            low_hz=80.0,
            high_hz=2400.0,
        )
        values["harmonicChange"].append(_cosine_distance(before, after))

        bass_before, bass_after = _band_vector(
            magnitude,
            frequencies,
            frame_times,
            float(beat_time),
            low_hz=40.0,
            high_hz=320.0,
            before_seconds=0.16,
            after_seconds=0.16,
        )
        values["bassChange"].append(_cosine_distance(bass_before, bass_after))
    return values


def _window_from_precomputed_signals(
    name: str,
    start: int,
    end: int,
    values_by_signal: Mapping[str, Sequence[float]],
) -> PhasePathWindow:
    combined = [0.0] * BEATS_PER_MEASURE
    signal_winners: dict[str, int] = {}
    for signal_name, all_values in values_by_signal.items():
        subset = list(all_values[start:end])
        scores, winner, _separation = _rank_phase_signal(subset)
        signal_winners[signal_name] = int(winner)
        weight = float(SIGNAL_WEIGHTS[signal_name])
        for phase in range(BEATS_PER_MEASURE):
            if math.isfinite(scores[phase]):
                combined[phase] += weight * float(scores[phase])

    ranked = sorted(range(BEATS_PER_MEASURE), key=lambda phase: (-combined[phase], phase))
    winner = int(ranked[0])
    combined_separation = max(0.0, float(combined[ranked[0]] - combined[ranked[1]]))
    consensus_signal_count = sum(1 for value in signal_winners.values() if int(value) == winner)

    midpoint = start + ((end - start) // 2)
    first_half_winner = _half_winner(values_by_signal, start, midpoint)
    second_half_winner = _half_winner(values_by_signal, midpoint, end)
    stable = first_half_winner == winner and second_half_winner == winner
    confidence = float(
        max(
            0.0,
            min(
                1.0,
                0.45 * min(1.0, combined_separation)
                + 0.35 * (consensus_signal_count / 4.0)
                + 0.20 * (1.0 if stable else 0.0),
            ),
        )
    )
    return PhasePathWindow(
        name=str(name),
        start_beat_index=int(start),
        end_beat_index_exclusive=int(end),
        winner_downbeat_index_mod4=winner,
        confidence=confidence,
        consensus_signal_count=int(consensus_signal_count),
        stable_across_halves=bool(stable),
        signal_winners=signal_winners,
        candidate_combined_scores={phase: float(combined[phase]) for phase in range(BEATS_PER_MEASURE)},
    )


def assess_post_repair_phase_path_from_samples(
    samples: Any,
    sample_rate: int,
    repaired_beat_times: Sequence[float],
    *,
    window_beats: int = LOCAL_WINDOW_BEATS,
    stride_beats: int = LOCAL_STRIDE_BEATS,
) -> dict[str, Any]:
    """Trace local 4/4 phase preference along a repaired beat grid using audio only.

    Diagnostic-only: this does not choose a runtime phase or mutate beat times.
    The expensive audio features are computed once, then sliced across aligned
    local windows. No song identity, section label, target count, or professional
    reference enters the path.
    """
    beats = tuple(float(value) for value in repaired_beat_times)
    if any(not math.isfinite(value) for value in beats):
        raise ValueError("repaired beat times must be finite")
    if any(right <= left for left, right in zip(beats[:-1], beats[1:])):
        raise ValueError("repaired beat times must be strictly increasing")

    specs = local_window_specs(
        len(beats),
        window_beats=int(window_beats),
        stride_beats=int(stride_beats),
    )
    values_by_signal = _beat_signal_values(samples, int(sample_rate), beats)
    windows = tuple(
        _window_from_precomputed_signals(name, start, end, values_by_signal)
        for name, start, end in specs
    )
    summary = summarize_phase_path(windows)
    return {
        "schemaVersion": 2,
        "mode": "v143-post-repair-local-phase-path-shadow",
        "windowBeats": int(_aligned_floor(window_beats)),
        "strideBeats": int(_aligned_floor(stride_beats)),
        "beatCount": len(beats),
        "featureExtractionPassCount": 1,
        "windows": [item.diagnostics() for item in windows],
        "summary": summary,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "runtimePhaseChanged": False,
        "liveRhythmOutputChanged": False,
        "productionModified": False,
    }


__all__ = [
    "BEATS_PER_MEASURE",
    "LOCAL_WINDOW_BEATS",
    "LOCAL_STRIDE_BEATS",
    "MIN_WINDOW_BEATS",
    "PhasePathWindow",
    "local_window_specs",
    "summarize_phase_path",
    "assess_post_repair_phase_path_from_samples",
]
