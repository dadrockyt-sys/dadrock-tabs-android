from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d


TIMING_SAMPLE_RATE = 22_050
STFT_WINDOW_SAMPLES = 1_024
STFT_HOP_SAMPLES = 256
MIN_TEMPO_BPM = 55.0
MAX_TEMPO_BPM = 210.0
BEATS_PER_MEASURE = 4
MIN_TRACKED_BEATS = 8
BAR_PHASE_MIN_SEPARATION_Z = 2.0


@dataclass(frozen=True)
class ReferenceFreeTimingEstimate:
    """Reference-free 4/4 timing metadata consumed by the V143 candidate adapter."""

    beat_times: tuple[float, ...]
    first_beat_in_measure: int
    downbeat_index_mod4: int
    tempo_bpm: float
    beat_confidence: float
    bar_confidence: float
    source_sample_rate: int
    analysis_sample_rate: int = TIMING_SAMPLE_RATE

    @property
    def bar_phase(self) -> int:
        """Compatibility alias for the adapter-facing first-beat position."""
        return int(self.first_beat_in_measure)

    def candidate_adapter_kwargs(self) -> dict[str, Any]:
        return {
            "beat_times": list(self.beat_times),
            "first_beat_in_measure": int(self.first_beat_in_measure),
        }


def _finite_audio(samples: Any) -> np.ndarray:
    audio = np.asarray(samples, dtype=np.float64)
    if audio.ndim == 2:
        # soundfile returns frames x channels. Also accept channels x frames for
        # direct/unit-test callers.
        if audio.shape[0] <= 8 and audio.shape[0] < audio.shape[1]:
            audio = np.mean(audio, axis=0)
        else:
            audio = np.mean(audio, axis=1)
    if audio.ndim != 1:
        raise ValueError("Audio must be mono or two-dimensional channel audio")
    if audio.size == 0:
        raise ValueError("Audio is empty")
    if not np.all(np.isfinite(audio)):
        raise ValueError("Audio contains non-finite samples")

    audio = audio - float(np.mean(audio))
    peak = float(np.max(np.abs(audio)))
    if peak < 1.0e-8:
        raise ValueError("Audio is silent or too close to silence for timing analysis")
    return audio


def _resample_audio(
    audio: np.ndarray,
    source_sample_rate: int,
    target_sample_rate: int = TIMING_SAMPLE_RATE,
) -> np.ndarray:
    source_sample_rate = int(source_sample_rate)
    target_sample_rate = int(target_sample_rate)
    if source_sample_rate <= 0 or target_sample_rate <= 0:
        raise ValueError("Sample rates must be positive")
    if source_sample_rate == target_sample_rate:
        return np.asarray(audio, dtype=np.float64)

    divisor = math.gcd(source_sample_rate, target_sample_rate)
    up = target_sample_rate // divisor
    down = source_sample_rate // divisor
    return np.asarray(signal.resample_poly(audio, up, down), dtype=np.float64)


def _normalized_onset_envelope(
    audio: np.ndarray,
    sample_rate: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if audio.size < STFT_WINDOW_SAMPLES * 2:
        raise ValueError("Audio is too short for timing analysis")

    frequencies, frame_times, spectrum = signal.stft(
        audio,
        fs=int(sample_rate),
        window="hann",
        nperseg=STFT_WINDOW_SAMPLES,
        noverlap=STFT_WINDOW_SAMPLES - STFT_HOP_SAMPLES,
        nfft=STFT_WINDOW_SAMPLES,
        boundary=None,
        padded=False,
    )

    timing_band = (frequencies >= 60.0) & (frequencies <= 8_000.0)
    if not np.any(timing_band):
        raise RuntimeError("Timing STFT did not contain the expected analysis band")

    magnitude = np.abs(spectrum[timing_band])
    log_magnitude = np.log1p(20.0 * magnitude)
    spectral_flux = np.maximum(
        np.diff(log_magnitude, axis=1, prepend=log_magnitude[:, :1]),
        0.0,
    ).mean(axis=0)
    spectral_flux = gaussian_filter1d(spectral_flux, sigma=1.0, mode="nearest")

    floor = float(np.quantile(spectral_flux, 0.20))
    onset = np.maximum(spectral_flux - floor, 0.0)
    scale = float(np.quantile(onset, 0.95))
    if scale < 1.0e-10:
        raise ValueError("Audio has insufficient transient activity for beat estimation")
    onset = np.clip(onset / scale, 0.0, 4.0)

    low_band = (frequencies >= 40.0) & (frequencies <= 250.0)
    if np.any(low_band):
        low_energy = np.sqrt(np.mean(np.abs(spectrum[low_band]) ** 2, axis=0))
        low_energy = gaussian_filter1d(low_energy, sigma=1.0, mode="nearest")
        low_scale = float(np.quantile(low_energy, 0.95))
        if low_scale > 1.0e-12:
            low_energy = np.clip(low_energy / low_scale, 0.0, 4.0)
        else:
            low_energy = np.zeros_like(onset)
    else:
        low_energy = np.zeros_like(onset)

    return (
        np.asarray(onset, dtype=np.float64),
        np.asarray(low_energy, dtype=np.float64),
        np.asarray(frame_times, dtype=np.float64),
    )


def _autocorrelation(signal_values: np.ndarray) -> np.ndarray:
    values = np.asarray(signal_values, dtype=np.float64)
    values = values - float(np.mean(values))
    count = int(values.size)
    fft_size = 1 << (2 * count - 1).bit_length()
    spectrum = np.fft.rfft(values, fft_size)
    ac = np.fft.irfft(spectrum * np.conj(spectrum), fft_size)[:count].real
    ac /= np.maximum(np.arange(count, 0, -1, dtype=np.float64), 1.0)
    if ac[0] > 0.0:
        ac /= float(ac[0])
    return ac


def _tempo_from_onsets(
    onset: np.ndarray,
    hop_seconds: float,
    *,
    min_tempo_bpm: float,
    max_tempo_bpm: float,
) -> tuple[float, int, float]:
    if not 0.0 < min_tempo_bpm < max_tempo_bpm:
        raise ValueError("Tempo bounds must be positive and increasing")

    autocorrelation = _autocorrelation(onset)
    min_lag = max(2, int(math.floor(60.0 / (max_tempo_bpm * hop_seconds))))
    max_lag = min(
        len(autocorrelation) - 2,
        int(math.ceil(60.0 / (min_tempo_bpm * hop_seconds))),
    )
    if max_lag <= min_lag:
        raise ValueError("Audio is too short for the requested tempo range")

    lags = np.arange(min_lag, max_lag + 1, dtype=int)
    periodicity = np.maximum(autocorrelation[lags], 0.0)
    if float(np.max(periodicity)) > 0.0:
        periodicity /= float(np.max(periodicity))

    prominence = max(0.08, 0.15 * float(np.std(onset)))
    peaks, _ = signal.find_peaks(
        onset,
        distance=max(1, int(round(0.10 / hop_seconds))),
        prominence=prominence,
    )

    ioi_scores = np.zeros(len(lags), dtype=np.float64)
    if len(peaks) >= 2:
        intervals = np.diff(peaks).astype(np.float64)
        weights = np.minimum(onset[peaks[:-1]], onset[peaks[1:]])
        weight_scale = float(np.quantile(weights, 0.90))
        if weight_scale > 1.0e-12:
            weights = np.clip(weights / weight_scale, 0.0, 2.0)
        else:
            weights = np.ones_like(intervals)

        # Consecutive transient intervals help reject the common half-tempo error
        # caused by stronger bar-level accents. Fractional/multiple terms keep the
        # score useful when the audio contains eighth-note subdivisions or a
        # missed beat.
        ratio_weights = (
            (1.0, 1.00),
            (0.5, 0.40),
            (1.0 / 3.0, 0.18),
            (2.0, 0.55),
        )
        for index, lag in enumerate(lags):
            score = 0.0
            for ratio, weight in ratio_weights:
                target = float(lag) * ratio
                tolerance = max(1.0, 0.07 * target)
                closeness = np.exp(
                    -0.5 * ((intervals - target) / tolerance) ** 2
                )
                score += weight * float(np.sum(weights * closeness))
            ioi_scores[index] = score

        if float(np.max(ioi_scores)) > 0.0:
            ioi_scores /= float(np.max(ioi_scores))

    bpms = 60.0 / (lags.astype(np.float64) * hop_seconds)
    # This is intentionally weak: it only breaks octave-level ties instead of
    # forcing uploaded songs toward a known/training-song tempo.
    broad_tempo_prior = np.exp(
        -0.5 * (np.log2(bpms / 115.0) / 0.90) ** 2
    )
    combined = (
        0.52 * periodicity
        + 0.42 * ioi_scores
        + 0.06 * broad_tempo_prior
    )
    best_index = int(np.argmax(combined))
    best_lag = int(lags[best_index])
    tempo_bpm = float(60.0 / (best_lag * hop_seconds))

    sorted_scores = np.sort(combined)
    runner_up = float(sorted_scores[-2]) if len(sorted_scores) >= 2 else 0.0
    separation = max(0.0, float(combined[best_index]) - runner_up)
    confidence = float(
        np.clip(0.5 * combined[best_index] + 2.0 * separation, 0.0, 1.0)
    )
    return tempo_bpm, best_lag, confidence


def _dynamic_beat_frames(
    onset: np.ndarray,
    period_frames: int,
) -> np.ndarray:
    period_frames = int(period_frames)
    if period_frames <= 1:
        raise ValueError("Estimated beat period is invalid")

    activity = np.maximum(np.asarray(onset, dtype=np.float64), 0.0)
    scale = float(np.quantile(activity, 0.95))
    if scale <= 1.0e-12:
        raise ValueError("Onset activity is too weak for beat tracking")
    activity = np.clip(activity / scale, 0.0, 2.5)

    min_interval = max(1, int(round(0.55 * period_frames)))
    max_interval = max(
        min_interval + 1,
        int(round(1.95 * period_frames)),
    )
    intervals = np.arange(min_interval, max_interval + 1, dtype=int)
    transition_penalty = 0.75 * (
        np.log2(intervals.astype(np.float64) / float(period_frames)) ** 2
    )

    cumulative = np.empty(len(activity), dtype=np.float64)
    backlink = np.full(len(activity), -1, dtype=int)

    for frame in range(len(activity)):
        valid = intervals <= frame
        best_predecessor_score = 0.0
        best_predecessor = -1
        if np.any(valid):
            predecessors = frame - intervals[valid]
            candidate_scores = cumulative[predecessors] - transition_penalty[valid]
            winner = int(np.argmax(candidate_scores))
            if float(candidate_scores[winner]) > 0.0:
                best_predecessor_score = float(candidate_scores[winner])
                best_predecessor = int(predecessors[winner])

        cumulative[frame] = activity[frame] + best_predecessor_score
        backlink[frame] = best_predecessor

    energy_cumulative = np.cumsum(activity)
    if energy_cumulative[-1] <= 0.0:
        raise ValueError("No usable onset activity was found")
    active_end = int(
        np.searchsorted(energy_cumulative, 0.995 * energy_cumulative[-1])
    )
    search_start = max(0, active_end - int(round(2.5 * period_frames)))
    endpoint = search_start + int(
        np.argmax(cumulative[search_start : active_end + 1])
    )

    path: list[int] = []
    cursor = int(endpoint)
    while cursor >= 0 and len(path) <= len(activity):
        path.append(cursor)
        cursor = int(backlink[cursor])
    path.reverse()

    frames = np.asarray(path, dtype=int)
    if len(frames) < MIN_TRACKED_BEATS:
        raise ValueError(
            f"Only {len(frames)} beats were tracked; at least "
            f"{MIN_TRACKED_BEATS} are required for 4/4 bar-phase estimation"
        )
    return frames


def _refine_beat_frames(
    frames: np.ndarray,
    onset: np.ndarray,
    period_frames: int,
) -> np.ndarray:
    radius = max(1, int(round(0.12 * period_frames)))
    refined: list[int] = []
    for frame in frames:
        left = max(0, int(frame) - radius)
        right = min(len(onset), int(frame) + radius + 1)
        candidate = left + int(np.argmax(onset[left:right]))
        if refined and candidate <= refined[-1]:
            candidate = int(frame)
        if refined and candidate <= refined[-1]:
            candidate = refined[-1] + 1
        if candidate >= len(onset):
            break
        refined.append(candidate)
    return np.asarray(refined, dtype=int)


def _paired_phase_separation_z(
    accents: np.ndarray,
    best_phase: int,
    runner_up_phase: int,
) -> float:
    """Return repeatability of the best-vs-runner accent difference across bars."""
    differences: list[float] = []
    for base in range(0, len(accents), BEATS_PER_MEASURE):
        best_index = base + int(best_phase)
        runner_index = base + int(runner_up_phase)
        if best_index < len(accents) and runner_index < len(accents):
            differences.append(float(accents[best_index] - accents[runner_index]))

    if len(differences) < 2:
        return 0.0
    values = np.asarray(differences, dtype=np.float64)
    mean_difference = float(np.mean(values))
    if mean_difference <= 0.0:
        return 0.0
    standard_error = float(np.std(values, ddof=1)) / math.sqrt(len(values))
    if standard_error <= 1.0e-12:
        return float("inf")
    return float(mean_difference / standard_error)


def _bar_phase_from_accents(
    beat_accents: np.ndarray,
) -> tuple[int, int, float]:
    accents = np.asarray(beat_accents, dtype=np.float64)
    if len(accents) < MIN_TRACKED_BEATS:
        raise ValueError("Not enough beats to estimate 4/4 bar phase")

    sequence_indices = np.arange(len(accents), dtype=int)
    phase_scores: list[float] = []
    for downbeat_phase in range(BEATS_PER_MEASURE):
        downbeat_mask = (sequence_indices % BEATS_PER_MEASURE) == downbeat_phase
        if int(np.sum(downbeat_mask)) < 2 or int(np.sum(~downbeat_mask)) < 2:
            phase_scores.append(float("-inf"))
            continue
        phase_scores.append(
            float(
                np.mean(accents[downbeat_mask])
                - np.mean(accents[~downbeat_mask])
            )
        )

    phase_order = sorted(
        range(BEATS_PER_MEASURE),
        key=lambda phase: phase_scores[phase],
        reverse=True,
    )
    strongest_phase = int(phase_order[0])
    runner_up_phase = int(phase_order[1])
    separation_z = _paired_phase_separation_z(
        accents,
        strongest_phase,
        runner_up_phase,
    )

    # Nonzero bar rotation is a destructive relabeling of every downstream
    # event. Keep the tracked sequence's first beat as the conservative prior
    # unless the nonzero phase repeatedly separates from the runner-up by about
    # two standard errors across complete 4-beat cycles. This is a generic
    # evidence test, not a song/reference-specific threshold.
    downbeat_index_mod4 = strongest_phase
    if (
        strongest_phase != 0
        and separation_z < BAR_PHASE_MIN_SEPARATION_Z
    ):
        downbeat_index_mod4 = 0
    first_beat_in_measure = int((-downbeat_index_mod4) % BEATS_PER_MEASURE)

    finite_scores = np.asarray(
        [score for score in phase_scores if math.isfinite(score)],
        dtype=np.float64,
    )
    ordered = np.sort(finite_scores)
    top = float(ordered[-1])
    runner_up = float(ordered[-2]) if len(ordered) >= 2 else top
    spread = max(float(np.std(accents)), 1.0e-9)
    confidence = float(np.clip((top - runner_up) / spread, 0.0, 1.0))
    if downbeat_index_mod4 != strongest_phase:
        confidence = 0.0
    return first_beat_in_measure, downbeat_index_mod4, confidence


def estimate_reference_free_timing_from_samples(
    samples: Any,
    sample_rate: int,
    *,
    min_tempo_bpm: float = MIN_TEMPO_BPM,
    max_tempo_bpm: float = MAX_TEMPO_BPM,
) -> ReferenceFreeTimingEstimate:
    """
    Estimate beat times and 4/4 bar phase without labels or a human reference.

    Production orchestration should prefer the normalized full mix for this
    timing stage because drums/bass provide stronger beat/downbeat evidence.
    The separated guitar stems remain the inputs to the exact V143 carrier
    feature extraction.
    """
    source_sample_rate = int(sample_rate)
    if source_sample_rate <= 0:
        raise ValueError("sample_rate must be positive")

    mono = _finite_audio(samples)
    analysis_audio = _resample_audio(
        mono,
        source_sample_rate,
        TIMING_SAMPLE_RATE,
    )
    onset, low_energy, frame_times = _normalized_onset_envelope(
        analysis_audio,
        TIMING_SAMPLE_RATE,
    )
    hop_seconds = STFT_HOP_SAMPLES / float(TIMING_SAMPLE_RATE)

    tempo_bpm, period_frames, tempo_confidence = _tempo_from_onsets(
        onset,
        hop_seconds,
        min_tempo_bpm=float(min_tempo_bpm),
        max_tempo_bpm=float(max_tempo_bpm),
    )
    beat_frames = _dynamic_beat_frames(onset, period_frames)
    beat_frames = _refine_beat_frames(beat_frames, onset, period_frames)
    if len(beat_frames) < MIN_TRACKED_BEATS:
        raise ValueError("Beat refinement left too few beats for bar-phase estimation")

    beat_times = frame_times[beat_frames]
    if np.any(np.diff(beat_times) <= 0.0):
        raise RuntimeError("Estimated beat times are not strictly increasing")
    if float(beat_times[0]) < 0.0:
        raise RuntimeError("Estimated beat times cannot be negative")

    beat_accents = onset[beat_frames] + 0.25 * low_energy[beat_frames]
    (
        first_beat_in_measure,
        downbeat_index_mod4,
        bar_confidence,
    ) = _bar_phase_from_accents(beat_accents)

    beat_activity = float(np.mean(onset[beat_frames]))
    background_activity = float(np.mean(onset))
    alignment_ratio = beat_activity / max(background_activity, 1.0e-9)
    alignment_confidence = float(
        np.clip((alignment_ratio - 1.0) / 2.0, 0.0, 1.0)
    )
    beat_confidence = float(
        np.clip(
            0.65 * tempo_confidence + 0.35 * alignment_confidence,
            0.0,
            1.0,
        )
    )

    return ReferenceFreeTimingEstimate(
        beat_times=tuple(float(value) for value in beat_times),
        first_beat_in_measure=int(first_beat_in_measure),
        downbeat_index_mod4=int(downbeat_index_mod4),
        tempo_bpm=float(tempo_bpm),
        beat_confidence=float(beat_confidence),
        bar_confidence=float(bar_confidence),
        source_sample_rate=source_sample_rate,
    )


def estimate_reference_free_timing(
    audio_path: str | Path,
    *,
    min_tempo_bpm: float = MIN_TEMPO_BPM,
    max_tempo_bpm: float = MAX_TEMPO_BPM,
) -> ReferenceFreeTimingEstimate:
    """Load decoded audio with SoundFile and run the reference-free estimator."""
    try:
        import soundfile as sf
    except ImportError as exc:
        raise RuntimeError(
            "soundfile is required to load production audio for timing analysis"
        ) from exc

    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    samples, sample_rate = sf.read(
        str(path),
        dtype="float32",
        always_2d=False,
    )
    return estimate_reference_free_timing_from_samples(
        samples,
        int(sample_rate),
        min_tempo_bpm=min_tempo_bpm,
        max_tempo_bpm=max_tempo_bpm,
    )


__all__ = [
    "TIMING_SAMPLE_RATE",
    "STFT_WINDOW_SAMPLES",
    "STFT_HOP_SAMPLES",
    "MIN_TEMPO_BPM",
    "MAX_TEMPO_BPM",
    "BEATS_PER_MEASURE",
    "MIN_TRACKED_BEATS",
    "BAR_PHASE_MIN_SEPARATION_Z",
    "ReferenceFreeTimingEstimate",
    "estimate_reference_free_timing_from_samples",
    "estimate_reference_free_timing",
]
