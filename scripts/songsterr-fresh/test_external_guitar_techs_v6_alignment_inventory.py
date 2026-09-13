#!/usr/bin/env python3
"""Controlled synthetic tests for the Guitar-TECHS V6 alignment audit."""

from __future__ import annotations

import importlib.util
import math
import tempfile
from pathlib import Path

import mido
import numpy as np

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "external_guitar_techs_v6_alignment_inventory.py"
spec = importlib.util.spec_from_file_location("guitar_techs_v6_audit", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def synth_onset(onset_seconds: float, *, duration_seconds: float = 1.2, midi: int = 64) -> np.ndarray:
    count = int(round(duration_seconds * module.SAMPLE_RATE if hasattr(module, "SAMPLE_RATE") else duration_seconds * 44100))
    sample_rate = 44100
    audio = np.zeros(count, dtype=np.float64)
    start = int(round(onset_seconds * sample_rate))
    t = np.arange(count - start, dtype=np.float64) / float(sample_rate)
    frequency = 440.0 * 2.0 ** ((float(midi) - 69.0) / 12.0)
    audio[start:] = np.sin(2.0 * math.pi * frequency * t) * np.exp(-2.0 * t)
    return audio


def assert_lag_close(actual_seconds: float, expected_seconds: float, hop_seconds: float) -> None:
    assert abs(actual_seconds - expected_seconds) <= hop_seconds + 1e-12, (actual_seconds, expected_seconds, hop_seconds)


def test_alignment_known_offsets() -> None:
    sample_rate = 44100
    midi_onset = 0.500
    for expected_offset in (0.0, 0.025, -0.040, 0.100):
        audio = synth_onset(midi_onset + expected_offset)
        result = module.estimate_constant_lag(audio, sample_rate, [midi_onset])
        assert result["status"] == "OK", result
        assert result["frameTimingAnchor"] == "center"
        assert_lag_close(result["lagSecondsAddedToMidi"], expected_offset, result["hopSeconds"])


def test_alignment_silence_fails_closed() -> None:
    audio = np.zeros(int(round(1.0 * 44100)), dtype=np.float64)
    result = module.estimate_constant_lag(audio, 44100, [0.5])
    assert result["status"] == "INSUFFICIENT_ZERO_AUDIO_NOVELTY", result


def test_midi_tempo_and_pairing() -> None:
    with tempfile.TemporaryDirectory(prefix="guitar-techs-v6-test-") as tmp:
        path = Path(tmp) / "midi_Test.mid"
        midi = mido.MidiFile(type=1, ticks_per_beat=480)
        tempo_track = mido.MidiTrack()
        note_track = mido.MidiTrack()
        midi.tracks.append(tempo_track)
        midi.tracks.append(note_track)
        tempo_track.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
        tempo_track.append(mido.MetaMessage("set_tempo", tempo=1000000, time=480))
        note_track.append(mido.Message("note_on", note=64, velocity=90, channel=0, time=240))
        note_track.append(mido.Message("note_off", note=64, velocity=0, channel=0, time=240))
        note_track.append(mido.Message("note_on", note=67, velocity=80, channel=1, time=240))
        note_track.append(mido.Message("note_off", note=67, velocity=0, channel=1, time=240))
        midi.save(path)

        parsed = module.parse_midi(path)
        assert parsed["format"] == 1
        assert parsed["ticksPerBeat"] == 480
        assert parsed["pairedEventCount"] == 2
        assert parsed["unmatchedNoteOffCount"] == 0
        assert parsed["unmatchedNoteOnCount"] == 0
        assert parsed["sameKeyOverlapCount"] == 0
        assert parsed["pitchMin"] == 64
        assert parsed["pitchMax"] == 67
        assert parsed["distinctOnsetCount"] == 2
        onsets = parsed["distinctOnsetSeconds"]
        assert abs(onsets[0] - 0.25) < 1e-12, onsets
        assert abs(onsets[1] - 1.0) < 1e-12, onsets


def test_packaging_and_semantic_keys() -> None:
    assert module.is_packaging_entry("P1_chords/__MACOSX/._junk")
    assert module.is_packaging_entry("P1_chords/audio/.DS_Store")
    assert module.semantic_key("P1_chords/audio/directinput/directinput_Set1_maj.wav", "directinput_") == "Set1_maj"
    assert module.semantic_key("P1_chords/midi/midi_Set1_maj.mid", "midi_") == "Set1_maj"


def main() -> int:
    test_alignment_known_offsets()
    test_alignment_silence_fails_closed()
    test_midi_tempo_and_pairing()
    test_packaging_and_semantic_keys()
    print("GUITAR_TECHS_V6_ALIGNMENT_AUDIT_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
