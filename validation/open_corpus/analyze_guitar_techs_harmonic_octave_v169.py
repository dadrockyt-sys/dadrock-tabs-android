#!/usr/bin/env python3
"""Open-corpus V169-style study: harmonic evidence against octave confusion.

This script is deliberately outside V168. It uses permissively licensed public
Guitar-TECHS reference MIDI only for a parallel development study and must not
modify the frozen V168 policies or GOAT holdout selection.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pretty_midi
import soundfile as sf

EPS = 1e-12


def midi_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def band_energy_from_fft(
    freqs: np.ndarray,
    power: np.ndarray,
    target_hz: float,
    cents: float = 35.0,
) -> float:
    if target_hz <= 0.0 or target_hz > float(freqs[-1]):
        return 0.0
    ratio = 2.0 ** (cents / 1200.0)
    lo = target_hz / ratio
    hi = target_hz * ratio
    mask = (freqs >= lo) & (freqs <= hi)
    if not bool(np.any(mask)):
        index = int(np.argmin(np.abs(freqs - target_hz)))
        return float(power[index])
    return float(np.max(power[mask]))


def frame_features(
    audio: np.ndarray,
    sample_rate: int,
    midi: float,
    center_seconds: float,
    *,
    window_seconds: float = 0.186,
    cents: float = 35.0,
) -> dict[str, Any] | None:
    n = max(2048, int(round(window_seconds * sample_rate)))
    nfft = min(32768, 1 << (n - 1).bit_length())
    half = n // 2
    center = int(round(center_seconds * sample_rate))
    start = center - half
    end = start + n
    if start < 0 or end > len(audio):
        return None

    frame = np.asarray(audio[start:end], dtype=np.float64)
    frame = frame - np.mean(frame)
    frame *= np.hanning(len(frame))
    spectrum = np.fft.rfft(frame, n=nfft)
    power = spectrum.real**2 + spectrum.imag**2
    freqs = np.fft.rfftfreq(nfft, 1.0 / sample_rate)

    f0 = midi_hz(midi)
    energy = {
        harmonic: band_energy_from_fft(freqs, power, harmonic * f0, cents)
        for harmonic in range(1, 9)
    }
    total = sum(energy.values()) + EPS

    # True-f0 score uses the first six harmonics. The +12-semitone competitor
    # can only explain the even harmonics of the lower true fundamental.
    true_harmonic = (
        1.00 * energy[1]
        + 0.85 * energy[2]
        + 0.72 * energy[3]
        + 0.62 * energy[4]
        + 0.54 * energy[5]
        + 0.48 * energy[6]
    )
    octave_harmonic = (
        1.00 * energy[2]
        + 0.85 * energy[4]
        + 0.72 * energy[6]
        + 0.62 * energy[8]
    )
    odd_support = (
        energy[1]
        + 0.72 * energy[3]
        + 0.54 * energy[5]
        + 0.42 * energy[7]
    )
    even_support = (
        energy[2]
        + 0.72 * energy[4]
        + 0.54 * energy[6]
        + 0.42 * energy[8]
    )

    return {
        "energy": energy,
        "fundamentalToSecond": energy[1] / (energy[2] + EPS),
        "oddToEven": odd_support / (even_support + EPS),
        "trueHarmonicScore": true_harmonic / total,
        "octaveHarmonicScore": octave_harmonic / total,
        "trueMinusOctave": (true_harmonic - octave_harmonic) / total,
    }


def load_notes(midi_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    midi = pretty_midi.PrettyMIDI(str(midi_path))
    notes: list[dict[str, Any]] = []
    instruments: list[dict[str, Any]] = []
    for instrument_index, instrument in enumerate(midi.instruments):
        instruments.append(
            {
                "index": instrument_index,
                "name": instrument.name or "",
                "program": instrument.program,
                "isDrum": instrument.is_drum,
                "noteCount": len(instrument.notes),
            }
        )
        for note in instrument.notes:
            notes.append(
                {
                    "instrumentIndex": instrument_index,
                    "instrumentName": instrument.name or "",
                    "program": instrument.program,
                    "isDrum": instrument.is_drum,
                    "midi": note.pitch,
                    "onset": note.start,
                    "offset": note.end,
                }
            )
    notes.sort(key=lambda row: (row["onset"], row["midi"], row["instrumentIndex"]))
    return notes, instruments


def load_mono_audio(path: Path) -> tuple[np.ndarray, int]:
    audio, sample_rate = sf.read(str(path), always_2d=False)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    return np.asarray(audio, dtype=np.float32), int(sample_rate)


def percentage(rows: list[dict[str, Any]], predicate) -> float | None:
    if not rows:
        return None
    return 100.0 * sum(1 for row in rows if predicate(row)) / len(rows)


def analyze_capture(
    audio: np.ndarray,
    sample_rate: int,
    notes: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    # Guitar-TECHS documents possible <=100 ms signal misalignment. Estimate one
    # global MIDI->audio shift using ground-truth pitch energy only; this is a
    # development-corpus alignment step, not a deployable reference-facing rule.
    alignment_notes = [
        row
        for row in notes
        if 28 <= row["midi"] <= 96 and row["offset"] - row["onset"] >= 0.12
    ][:80]
    offsets = np.arange(-0.12, 0.1201, 0.01)
    alignment_scores: list[float] = []
    for offset in offsets:
        values: list[float] = []
        for row in alignment_notes:
            features = frame_features(
                audio,
                sample_rate,
                row["midi"],
                row["onset"] + float(offset) + 0.11,
                window_seconds=0.12,
            )
            if features:
                e = features["energy"]
                values.append(math.log10(e[1] + e[2] + e[3] + EPS))
        alignment_scores.append(float(np.median(values)) if values else -1e30)
    best_offset = float(offsets[int(np.argmax(alignment_scores))])

    per_note: list[dict[str, Any]] = []
    for row in notes:
        if not 28 <= row["midi"] <= 96:
            continue
        candidates: list[dict[str, Any]] = []
        for delta in (0.08, 0.13, 0.18, 0.24):
            features = frame_features(
                audio,
                sample_rate,
                row["midi"],
                row["onset"] + best_offset + delta,
            )
            if features:
                candidates.append(features)
        if not candidates:
            continue
        features = max(
            candidates,
            key=lambda item: sum(item["energy"][harmonic] for harmonic in range(1, 6)),
        )
        per_note.append(
            {
                "midi": row["midi"],
                "instrumentIndex": row["instrumentIndex"],
                "instrumentName": row["instrumentName"],
                "fundamentalToSecond": features["fundamentalToSecond"],
                "oddToEven": features["oddToEven"],
                "trueHarmonicScore": features["trueHarmonicScore"],
                "octaveHarmonicScore": features["octaveHarmonicScore"],
                "trueMinusOctave": features["trueMinusOctave"],
            }
        )

    weak = [row for row in per_note if row["fundamentalToSecond"] < 1.0]
    very_weak = [row for row in per_note if row["fundamentalToSecond"] < 0.5]
    summary = {
        "sampleRate": sample_rate,
        "durationSeconds": len(audio) / sample_rate,
        "estimatedMidiToAudioOffsetSeconds": best_offset,
        "analyzedNoteCount": len(per_note),
        "fundamentalWeakerThanSecondPct": percentage(
            per_note, lambda row: row["fundamentalToSecond"] < 1.0
        ),
        "fundamentalLessThanHalfSecondPct": percentage(
            per_note, lambda row: row["fundamentalToSecond"] < 0.5
        ),
        "harmonicScorePrefersTrueOverOctavePct": percentage(
            per_note, lambda row: row["trueMinusOctave"] > 0.0
        ),
        "weakFundamentalCount": len(weak),
        "weakFundamentalHarmonicScorePrefersTruePct": percentage(
            weak, lambda row: row["trueMinusOctave"] > 0.0
        ),
        "veryWeakFundamentalCount": len(very_weak),
        "veryWeakFundamentalHarmonicScorePrefersTruePct": percentage(
            very_weak, lambda row: row["trueMinusOctave"] > 0.0
        ),
        "medianTrueMinusOctave": (
            float(np.median([row["trueMinusOctave"] for row in per_note]))
            if per_note
            else None
        ),
        "medianOddToEven": (
            float(np.median([row["oddToEven"] for row in per_note])) if per_note else None
        ),
    }
    return summary, per_note


def self_test() -> dict[str, Any]:
    sample_rate = 44100
    t = np.arange(sample_rate, dtype=np.float64) / sample_rate
    f0 = 110.0
    # Deliberately make the fundamental much weaker than the second harmonic.
    # Strong 3rd/5th harmonics should still favor the lower true fundamental.
    audio = (
        0.08 * np.sin(2.0 * np.pi * f0 * t)
        + 1.00 * np.sin(2.0 * np.pi * 2.0 * f0 * t)
        + 0.75 * np.sin(2.0 * np.pi * 3.0 * f0 * t)
        + 0.10 * np.sin(2.0 * np.pi * 4.0 * f0 * t)
        + 0.55 * np.sin(2.0 * np.pi * 5.0 * f0 * t)
    )
    midi = 69.0 + 12.0 * np.log2(f0 / 440.0)
    features = frame_features(audio, sample_rate, midi, 0.5)
    if features is None:
        raise RuntimeError("synthetic self-test produced no frame")
    if not features["fundamentalToSecond"] < 0.1:
        raise RuntimeError("synthetic weak-fundamental condition was not created")
    if not features["trueMinusOctave"] > 0.0:
        raise RuntimeError("harmonic score failed weak-fundamental octave test")
    return {
        "status": "SELF_TEST_PASS",
        "fundamentalToSecond": features["fundamentalToSecond"],
        "oddToEven": features["oddToEven"],
        "trueMinusOctave": features["trueMinusOctave"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--midi", type=Path)
    parser.add_argument("--di", type=Path)
    parser.add_argument("--micamp", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if not all((args.midi, args.di, args.micamp, args.output)):
        raise SystemExit("--midi, --di, --micamp and --output are required")

    notes, instruments = load_notes(args.midi)
    report: dict[str, Any] = {
        "schema": "dadrock.tabs.open-corpus.harmonic-octave-study.v1",
        "dataset": "Guitar-TECHS",
        "scope": "P1_singlenotes",
        "midiNoteCount": len(notes),
        "midiInstruments": instruments,
        "captures": {},
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    for name, path in (("directInput", args.di), ("micAmp", args.micamp)):
        audio, sample_rate = load_mono_audio(path)
        summary, _ = analyze_capture(audio, sample_rate, notes)
        report["captures"][name] = summary

    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
