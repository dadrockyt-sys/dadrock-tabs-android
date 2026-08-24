from __future__ import annotations

import math
import subprocess

import numpy as np

from v143_reference_free_beat_grid_repair import repair_reference_free_beat_grid_from_samples
from v143_reference_free_timing import ReferenceFreeTimingEstimate


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _synthetic_clicks(sample_rate: int = 22050):
    period = 0.5
    true_beats = [0.5 + index * period for index in range(40)]
    duration = true_beats[-1] + 0.35
    audio = np.zeros(int(math.ceil(duration * sample_rate)), dtype=np.float64)
    for index, beat in enumerate(true_beats):
        start = int(round(beat * sample_rate))
        length = int(0.08 * sample_rate)
        x = np.arange(length, dtype=np.float64) / sample_rate
        freq = 82.0 if index % 4 == 0 else 164.0
        envelope = np.exp(-x * 40.0)
        pulse = (1.0 if index % 4 == 0 else 0.65) * np.sin(2.0 * math.pi * freq * x) * envelope
        hi = min(len(audio), start + length)
        audio[start:hi] += pulse[: hi - start]
    raw = list(true_beats[:30])
    raw.extend([true_beats[10] + 0.25, true_beats[20] + 0.30])
    raw.sort()
    return audio, sample_rate, true_beats, raw


def main() -> int:
    audio, sample_rate, true_beats, raw = _synthetic_clicks()
    timing = ReferenceFreeTimingEstimate(
        beat_times=tuple(raw),
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        tempo_bpm=120.0,
        beat_confidence=0.8,
        bar_confidence=0.5,
        source_sample_rate=sample_rate,
    )
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

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 reference-free beat grid repair checker: PASS")
    print(diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
