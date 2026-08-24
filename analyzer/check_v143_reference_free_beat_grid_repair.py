from __future__ import annotations

import math
import subprocess

import numpy as np

from v143_reference_free_beat_grid_repair import (
    BOUNDARY_LOOKAHEAD_BEATS,
    repair_reference_free_beat_grid_from_samples,
)
from v143_reference_free_timing import ReferenceFreeTimingEstimate


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _add_click(audio: np.ndarray, sample_rate: int, beat: float, *, amplitude: float = 1.0, frequency: float = 110.0) -> None:
    start = int(round(beat * sample_rate))
    length = int(0.08 * sample_rate)
    x = np.arange(length, dtype=np.float64) / sample_rate
    envelope = np.exp(-x * 40.0)
    pulse = amplitude * np.sin(2.0 * math.pi * frequency * x) * envelope
    hi = min(len(audio), start + length)
    if hi > start:
        audio[start:hi] += pulse[: hi - start]


def _synthetic_clicks(sample_rate: int = 22050):
    period = 0.5
    true_beats = [0.5 + index * period for index in range(40)]
    duration = true_beats[-1] + 0.35
    audio = np.zeros(int(math.ceil(duration * sample_rate)), dtype=np.float64)
    for index, beat in enumerate(true_beats):
        _add_click(
            audio,
            sample_rate,
            beat,
            amplitude=1.0 if index % 4 == 0 else 0.65,
            frequency=82.0 if index % 4 == 0 else 164.0,
        )
    raw = list(true_beats[:30])
    raw.extend([true_beats[10] + 0.25, true_beats[20] + 0.30])
    raw.sort()
    return audio, sample_rate, true_beats, raw


def _synthetic_one_bar_boundary_gap(sample_rate: int = 22050):
    period = 0.5
    raw_beats = [0.5 + index * period for index in range(20)]
    raw_last = raw_beats[-1]
    proved_future_beat = raw_last + 4.0 * period
    duration = proved_future_beat + 0.30
    audio = np.zeros(int(math.ceil(duration * sample_rate)), dtype=np.float64)
    for index, beat in enumerate(raw_beats):
        _add_click(
            audio,
            sample_rate,
            beat,
            amplitude=1.0 if index % 4 == 0 else 0.70,
            frequency=90.0 if index % 4 == 0 else 180.0,
        )
    # Deliberately leave three beat positions without transients, then provide a
    # strong physical onset on the fourth beat. A 4/4-aware one-bar lookahead may
    # bridge only because this later audio proves the pulse train continues.
    _add_click(audio, sample_rate, proved_future_beat, amplitude=1.25, frequency=90.0)
    return audio, sample_rate, raw_beats, proved_future_beat


def _timing(beat_times, sample_rate: int) -> ReferenceFreeTimingEstimate:
    return ReferenceFreeTimingEstimate(
        beat_times=tuple(beat_times),
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        tempo_bpm=120.0,
        beat_confidence=0.8,
        bar_confidence=0.5,
        source_sample_rate=sample_rate,
    )


def main() -> int:
    assert BOUNDARY_LOOKAHEAD_BEATS == 4

    audio, sample_rate, true_beats, raw = _synthetic_clicks()
    timing = _timing(raw, sample_rate)
    result = repair_reference_free_beat_grid_from_samples(audio, sample_rate, timing)
    diag = result.diagnostics()
    assert result.original_interval_outlier_count >= 2, diag
    assert result.repaired_interval_outlier_count == 0, diag
    assert len(result.repaired_beat_times) > len(raw), diag
    assert result.trailing_extended_beat_count >= 5, diag
    assert result.timing.first_beat_in_measure == timing.first_beat_in_measure
    assert result.timing.downbeat_index_mod4 == timing.downbeat_index_mod4
    assert abs(result.timing.tempo_bpm - timing.tempo_bpm) < 1e-12
    assert max(
        abs(repaired - truth)
        for repaired, truth in zip(result.repaired_beat_times[:30], true_beats[:30])
    ) < 0.12
    assert diag["referenceFree"] is True
    assert diag["barPhaseChanged"] is False
    assert diag["tempoChanged"] is False

    gap_audio, gap_sr, gap_raw, proved_future_beat = _synthetic_one_bar_boundary_gap()
    gap_result = repair_reference_free_beat_grid_from_samples(
        gap_audio,
        gap_sr,
        _timing(gap_raw, gap_sr),
    )
    gap_diag = gap_result.diagnostics()
    assert gap_result.repaired_interval_outlier_count == 0, gap_diag
    assert gap_result.lookahead_bridge_beat_count >= 3, gap_diag
    assert abs(gap_result.repaired_beat_times[-1] - proved_future_beat) < 0.12, gap_diag
    assert gap_result.repaired_beat_times[-1] > gap_raw[-1] + 3.5 * 0.5, gap_diag

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 reference-free beat grid repair checker: PASS")
    print(diag)
    print(gap_diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
