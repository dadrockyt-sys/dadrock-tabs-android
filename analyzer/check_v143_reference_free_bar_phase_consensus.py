from __future__ import annotations

import math
import subprocess

import numpy as np

from v143_reference_free_bar_phase_consensus import estimate_reference_free_bar_phase_consensus_from_samples


EXPECTED_PROTECTED_BLOB = "7f72f8ed9b14af8bc93e95544195204d99c6bec1"


def _click_track(sample_rate: int = 22050, bars: int = 20, phase_offset_beats: int = 0):
    bpm = 120.0
    beat_seconds = 60.0 / bpm
    total_beats = bars * 4
    duration = (total_beats + 1) * beat_seconds
    audio = np.zeros(int(round(duration * sample_rate)), dtype=np.float64)
    beat_times = []
    for index in range(total_beats):
        t = (index + 0.25) * beat_seconds
        beat_times.append(t)
        center = int(round(t * sample_rate))
        beat_in_measure = (phase_offset_beats + index) % 4
        amp = 1.0 if beat_in_measure == 0 else 0.35
        # Low-frequency downbeat pulse plus a weaker upper pulse on all beats.
        length = int(0.08 * sample_rate)
        x = np.arange(length, dtype=np.float64) / sample_rate
        tone = amp * np.sin(2.0 * math.pi * (82.0 if beat_in_measure == 0 else 164.0) * x)
        env = np.exp(-x * 35.0)
        lo = center
        hi = min(len(audio), center + length)
        audio[lo:hi] += tone[: hi - lo] * env[: hi - lo]
    return audio, sample_rate, beat_times


def main() -> int:
    audio, sample_rate, beats = _click_track(phase_offset_beats=3)
    result = estimate_reference_free_bar_phase_consensus_from_samples(audio, sample_rate, beats)
    # With the first tracked beat being beat 4, downbeats occur at sequence index 1.
    assert result.winner_downbeat_index_mod4 == 1, result.diagnostics()
    assert result.winner_first_beat_in_measure == 3
    assert result.consensus_signal_count >= 2
    diag = result.diagnostics()
    assert diag["referenceFree"] is True
    assert diag["runtimeLabelsRequired"] is False
    assert diag["productionModified"] is False

    protected = subprocess.check_output(
        ["git", "hash-object", "analyzer/v143_reference_free_rhythm_pipeline.py"],
        text=True,
    ).strip()
    assert protected == EXPECTED_PROTECTED_BLOB, protected
    print("V143 reference-free bar phase consensus checker: PASS")
    print(diag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
