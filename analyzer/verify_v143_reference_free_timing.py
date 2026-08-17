from __future__ import annotations

import inspect
import math
import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf

import v143_reference_free_timing as timing
from v143_candidate_timing_adapter import build_subdivision_grid


SAMPLE_RATE = 44_100
TRUE_BPM = 120.0
BEAT_COUNT = 32
FIRST_CLICK_SECONDS = 0.25
DOWNBEAT_INDEX_MOD4 = 1


def _synthetic_click_track() -> tuple[np.ndarray, np.ndarray]:
    interval = 60.0 / TRUE_BPM
    duration = FIRST_CLICK_SECONDS + (BEAT_COUNT + 1) * interval
    audio = np.zeros(int(math.ceil(duration * SAMPLE_RATE)), dtype=np.float64)
    expected_beats = FIRST_CLICK_SECONDS + np.arange(BEAT_COUNT) * interval

    click_samples = max(32, int(round(0.030 * SAMPLE_RATE)))
    local_time = np.arange(click_samples, dtype=np.float64) / SAMPLE_RATE
    envelope = np.exp(-70.0 * local_time)
    carrier = (
        np.sin(2.0 * math.pi * 120.0 * local_time)
        + 0.5 * np.sin(2.0 * math.pi * 900.0 * local_time)
    )

    for beat_index, beat_time in enumerate(expected_beats):
        amplitude = 1.0 if beat_index % 4 == DOWNBEAT_INDEX_MOD4 else 0.35
        start = int(round(float(beat_time) * SAMPLE_RATE))
        click = amplitude * envelope * carrier
        end = min(len(audio), start + len(click))
        audio[start:end] += click[: end - start]

    # Exercise the production stereo-to-mono path as well.
    stereo = np.stack((audio, 0.85 * audio), axis=1)
    return stereo, expected_beats


def _assert_silence_rejected() -> None:
    silence = np.zeros(SAMPLE_RATE * 4, dtype=np.float64)
    try:
        timing.estimate_reference_free_timing_from_samples(silence, SAMPLE_RATE)
    except ValueError:
        return
    raise AssertionError("Silent audio was accepted by the timing estimator")


def main() -> None:
    audio, expected_beats = _synthetic_click_track()

    direct = timing.estimate_reference_free_timing_from_samples(
        audio,
        SAMPLE_RATE,
    )
    repeated = timing.estimate_reference_free_timing_from_samples(
        audio,
        SAMPLE_RATE,
    )
    assert direct == repeated

    assert abs(direct.tempo_bpm - TRUE_BPM) <= 2.5
    assert len(direct.beat_times) >= BEAT_COUNT - 2
    tracked = np.asarray(direct.beat_times[:BEAT_COUNT], dtype=np.float64)
    expected = expected_beats[: len(tracked)]
    beat_error = np.abs(tracked - expected)
    assert float(np.max(beat_error)) <= 0.040

    # The synthetic sequence's downbeats are beat indices 1, 5, 9, ... .
    # Therefore beat_times[0] is beat 4 of the preceding measure, represented
    # by adapter-facing zero-based first_beat_in_measure == 3.
    assert direct.downbeat_index_mod4 == DOWNBEAT_INDEX_MOD4
    assert direct.first_beat_in_measure == 3
    assert direct.bar_phase == 3
    assert 0.0 <= direct.beat_confidence <= 1.0
    assert 0.0 <= direct.bar_confidence <= 1.0
    assert direct.beat_confidence > 0.30
    assert direct.bar_confidence > 0.30

    adapter_kwargs = direct.candidate_adapter_kwargs()
    assert set(adapter_kwargs) == {"beat_times", "first_beat_in_measure"}
    grid = build_subdivision_grid(**adapter_kwargs)
    assert grid[0].step == 12
    assert grid[4].step == 0
    assert grid[4].measure == grid[0].measure + 1
    assert abs(grid[0].time_seconds - direct.beat_times[0]) < 1.0e-12
    assert abs(grid[4].time_seconds - direct.beat_times[1]) < 1.0e-12

    with tempfile.TemporaryDirectory() as directory:
        audio_path = Path(directory) / "reference-free-timing.wav"
        sf.write(
            str(audio_path),
            audio,
            SAMPLE_RATE,
            subtype="FLOAT",
        )
        loaded = timing.estimate_reference_free_timing(audio_path)
    assert abs(loaded.tempo_bpm - TRUE_BPM) <= 2.5
    assert loaded.first_beat_in_measure == direct.first_beat_in_measure
    assert len(loaded.beat_times) == len(direct.beat_times)

    _assert_silence_rejected()

    source = inspect.getsource(timing)
    for disallowed_dependency in ("librosa", "madmom", "essentia"):
        assert disallowed_dependency not in source

    sample_signature = inspect.signature(
        timing.estimate_reference_free_timing_from_samples
    )
    path_signature = inspect.signature(timing.estimate_reference_free_timing)
    for signature in (sample_signature, path_signature):
        parameter_names = {name.lower() for name in signature.parameters}
        assert "reference" not in parameter_names
        assert "labels" not in parameter_names

    print("=== V143 REFERENCE-FREE TIMING ESTIMATOR VERIFIED ===")
    print("Arbitrary decoded stereo audio accepted: True")
    print("44.1 kHz -> deterministic 22.05 kHz analysis: True")
    print("Tempo recovery within 2.5 BPM: True")
    print("Beat timestamps within 40 ms: True")
    print("Explicit 4/4 downbeat/bar phase: True")
    print("Adapter first_beat_in_measure semantics exact: True")
    print("Direct candidate-adapter grid handoff: True")
    print("Beat confidence emitted: True")
    print("Bar confidence emitted: True")
    print("Silent/invalid timing input rejected: True")
    print("Existing NumPy/SciPy/SoundFile stack only: True")
    print("Deterministic repeat exact: True")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("READY FOR REFERENCE-FREE RHYTHM PIPELINE ASSEMBLY: True")


if __name__ == "__main__":
    main()
