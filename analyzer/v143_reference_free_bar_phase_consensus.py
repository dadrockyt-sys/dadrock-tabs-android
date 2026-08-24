from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Any, Mapping, Sequence

import numpy as np
from scipy import signal

from v143_reference_free_timing import (
    STFT_HOP_SAMPLES,
    STFT_WINDOW_SAMPLES,
    TIMING_SAMPLE_RATE,
    _finite_audio,
    _normalized_onset_envelope,
    _resample_audio,
)


BEATS_PER_MEASURE = 4
MIN_BEATS = 24
EPSILON = 1.0e-9


@dataclass(frozen=True)
class BarPhaseConsensus:
    winner_downbeat_index_mod4: int
    winner_first_beat_in_measure: int
    confidence: float
    signal_winners: dict[str, int]
    candidates: tuple[dict[str, Any], ...]
    stable_across_halves: bool
    consensus_signal_count: int

    def diagnostics(self) -> dict[str, Any]:
        return {
            "winnerDownbeatIndexMod4": int(self.winner_downbeat_index_mod4),
            "winnerFirstBeatInMeasure": int(self.winner_first_beat_in_measure),
            "confidence": float(self.confidence),
            "signalWinners": dict(self.signal_winners),
            "stableAcrossHalves": bool(self.stable_across_halves),
            "consensusSignalCount": int(self.consensus_signal_count),
            "candidates": [dict(item) for item in self.candidates],
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    a = np.asarray(left, dtype=np.float64)
    b = np.asarray(right, dtype=np.float64)
    if a.shape != b.shape or a.size == 0:
        return 0.0
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na <= EPSILON or nb <= EPSILON:
        return 0.0
    similarity = float(np.dot(a, b) / (na * nb))
    return float(max(0.0, min(2.0, 1.0 - similarity)))


def _nearest_frame(frame_times: np.ndarray, time_seconds: float) -> int:
    position = int(np.searchsorted(frame_times, float(time_seconds)))
    options = [index for index in (position - 1, position) if 0 <= index < len(frame_times)]
    if not options:
        return 0
    return min(options, key=lambda index: abs(float(frame_times[index]) - float(time_seconds)))


def _band_vector(
    magnitude: np.ndarray,
    frequencies: np.ndarray,
    frame_times: np.ndarray,
    center_time: float,
    *,
    low_hz: float,
    high_hz: float,
    before_seconds: float = 0.14,
    after_seconds: float = 0.14,
) -> tuple[np.ndarray, np.ndarray]:
    mask = (frequencies >= float(low_hz)) & (frequencies <= float(high_hz))
    if not np.any(mask):
        return np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64)
    center = _nearest_frame(frame_times, center_time)
    hop_seconds = STFT_HOP_SAMPLES / float(TIMING_SAMPLE_RATE)
    before_frames = max(1, int(round(float(before_seconds) / hop_seconds)))
    after_frames = max(1, int(round(float(after_seconds) / hop_seconds)))
    before_lo = max(0, center - before_frames)
    before_hi = max(before_lo + 1, center)
    after_lo = min(magnitude.shape[1] - 1, center)
    after_hi = min(magnitude.shape[1], after_lo + after_frames)
    before = np.log1p(20.0 * magnitude[mask, before_lo:before_hi]).mean(axis=1)
    after = np.log1p(20.0 * magnitude[mask, after_lo:after_hi]).mean(axis=1)
    return np.asarray(before, dtype=np.float64), np.asarray(after, dtype=np.float64)


def _phase_contrast(values: Sequence[float], phase: int) -> float:
    downbeats = [float(value) for index, value in enumerate(values) if index % 4 == int(phase)]
    others = [float(value) for index, value in enumerate(values) if index % 4 != int(phase)]
    if len(downbeats) < 2 or len(others) < 2:
        return float("-inf")
    spread = max(float(pstdev(float(value) for value in values)), EPSILON)
    return float((mean(downbeats) - mean(others)) / spread)


def _rank_phase_signal(values: Sequence[float]) -> tuple[list[float], int, float]:
    scores = [_phase_contrast(values, phase) for phase in range(4)]
    ranked = sorted(range(4), key=lambda phase: (-scores[phase], phase))
    winner = int(ranked[0])
    separation = max(0.0, float(scores[ranked[0]] - scores[ranked[1]]))
    return scores, winner, separation


def _half_winner(values_by_signal: Mapping[str, Sequence[float]], start: int, end: int) -> int:
    combined = [0.0] * 4
    weights = {
        "accent": 0.30,
        "lowAccent": 0.15,
        "harmonicChange": 0.30,
        "bassChange": 0.25,
    }
    for name, values in values_by_signal.items():
        subset = list(values[start:end])
        if len(subset) < 12:
            continue
        scores, _winner, _sep = _rank_phase_signal(subset)
        weight = float(weights.get(name, 0.0))
        for phase in range(4):
            if math.isfinite(scores[phase]):
                combined[phase] += weight * float(scores[phase])
    return int(max(range(4), key=lambda phase: (combined[phase], -phase)))


def estimate_reference_free_bar_phase_consensus_from_samples(
    samples: Any,
    sample_rate: int,
    beat_times: Sequence[float],
) -> BarPhaseConsensus:
    """Score all four 4/4 bar phases from independent audio-only signals.

    Signals are deliberately generic: transient accent, low-band accent, broad
    harmonic change, and bass-band spectral change. No song, key, chord, section,
    target event count, or external label is accepted. A stable winner must also
    agree between the first and second halves of the tracked beat sequence.
    """
    beats = [float(value) for value in beat_times if math.isfinite(float(value))]
    if len(beats) < MIN_BEATS:
        raise ValueError(f"At least {MIN_BEATS} tracked beats are required")

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

    accent: list[float] = []
    low_accent: list[float] = []
    harmonic_change: list[float] = []
    bass_change: list[float] = []
    for beat_time in beats:
        onset_index = _nearest_frame(onset_times, beat_time)
        accent.append(float(onset[onset_index] + 0.25 * low_energy[onset_index]))
        low_accent.append(float(low_energy[onset_index]))

        before, after = _band_vector(
            magnitude,
            frequencies,
            frame_times,
            beat_time,
            low_hz=80.0,
            high_hz=2400.0,
        )
        harmonic_change.append(_cosine_distance(before, after))

        bass_before, bass_after = _band_vector(
            magnitude,
            frequencies,
            frame_times,
            beat_time,
            low_hz=40.0,
            high_hz=320.0,
            before_seconds=0.16,
            after_seconds=0.16,
        )
        bass_change.append(_cosine_distance(bass_before, bass_after))

    values_by_signal: dict[str, Sequence[float]] = {
        "accent": accent,
        "lowAccent": low_accent,
        "harmonicChange": harmonic_change,
        "bassChange": bass_change,
    }
    weights = {
        "accent": 0.30,
        "lowAccent": 0.15,
        "harmonicChange": 0.30,
        "bassChange": 0.25,
    }
    signal_scores: dict[str, list[float]] = {}
    signal_winners: dict[str, int] = {}
    signal_separations: dict[str, float] = {}
    combined = [0.0] * 4
    for name, values in values_by_signal.items():
        scores, winner, separation = _rank_phase_signal(values)
        signal_scores[name] = scores
        signal_winners[name] = winner
        signal_separations[name] = float(separation)
        for phase in range(4):
            if math.isfinite(scores[phase]):
                combined[phase] += float(weights[name]) * float(scores[phase])

    ranked = sorted(range(4), key=lambda phase: (-combined[phase], phase))
    winner = int(ranked[0])
    combined_separation = max(0.0, float(combined[ranked[0]] - combined[ranked[1]]))
    consensus_signal_count = sum(1 for value in signal_winners.values() if int(value) == winner)

    midpoint = len(beats) // 2
    first_half_winner = _half_winner(values_by_signal, 0, midpoint)
    second_half_winner = _half_winner(values_by_signal, midpoint, len(beats))
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

    candidates = []
    for phase in range(4):
        candidates.append(
            {
                "downbeatIndexMod4": int(phase),
                "firstBeatInMeasure": int((-phase) % 4),
                "combinedScore": float(combined[phase]),
                "accentScore": float(signal_scores["accent"][phase]),
                "lowAccentScore": float(signal_scores["lowAccent"][phase]),
                "harmonicChangeScore": float(signal_scores["harmonicChange"][phase]),
                "bassChangeScore": float(signal_scores["bassChange"][phase]),
            }
        )

    return BarPhaseConsensus(
        winner_downbeat_index_mod4=winner,
        winner_first_beat_in_measure=int((-winner) % 4),
        confidence=confidence,
        signal_winners=signal_winners,
        candidates=tuple(candidates),
        stable_across_halves=stable,
        consensus_signal_count=int(consensus_signal_count),
    )


__all__ = [
    "BarPhaseConsensus",
    "estimate_reference_free_bar_phase_consensus_from_samples",
]
