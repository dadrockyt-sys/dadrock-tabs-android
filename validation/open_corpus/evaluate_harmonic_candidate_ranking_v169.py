#!/usr/bin/env python3
"""Prospectively frozen V169-style harmonic octave-confusion ranking benchmark.

This is NOT V168 and cannot score V168. Public Guitar-TECHS reference MIDI is
used only to construct controlled candidate sets and evaluate the audio-only
winner afterward.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from analyze_guitar_techs_harmonic_octave_v169 import (
    EPS,
    band_energy_from_fft,
    load_mono_audio,
    load_notes,
    midi_hz,
)

WEIGHTS = (1.00, 0.85, 0.72, 0.62, 0.54, 0.48, 0.42, 0.38)
WINDOW_SECONDS = 0.186
CENTS = 35.0
FRAME_DELTAS = (0.08, 0.13, 0.18, 0.24)
ALIGNMENT_OFFSETS = tuple(float(v) for v in np.arange(-0.12, 0.1201, 0.01))


def fft_power_frame(
    audio: np.ndarray,
    sample_rate: int,
    center_seconds: float,
    window_seconds: float = WINDOW_SECONDS,
) -> tuple[np.ndarray, np.ndarray] | None:
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
    return freqs, power


def harmonic_vector(freqs: np.ndarray, power: np.ndarray, midi: int) -> dict[str, Any]:
    f = midi_hz(midi)
    energies = [band_energy_from_fft(freqs, power, (h + 1) * f, CENTS) for h in range(8)]
    sub = band_energy_from_fft(freqs, power, 0.5 * f, CENTS)
    total = sum(w * e for w, e in zip(WEIGHTS, energies))
    odd = (
        1.00 * energies[0]
        + 0.72 * energies[2]
        + 0.54 * energies[4]
        + 0.42 * energies[6]
    )
    sub_penalty = 1.0 + 0.75 * sub / (total + EPS)
    score = (total + odd) / sub_penalty
    first_five = sum(energies[:5])
    return {
        "score": float(score),
        "firstFive": float(first_five),
        "e1": float(energies[0]),
        "e2": float(energies[1]),
        "sub": float(sub),
        "total": float(total),
        "odd": float(odd),
    }


def estimate_alignment(
    audio: np.ndarray,
    sample_rate: int,
    notes: list[dict[str, Any]],
) -> float:
    alignment_notes = [
        row
        for row in notes
        if 28 <= int(row["midi"]) <= 96 and float(row["offset"]) - float(row["onset"]) >= 0.12
    ][:80]
    scores: list[float] = []
    for offset in ALIGNMENT_OFFSETS:
        values: list[float] = []
        for row in alignment_notes:
            frame = fft_power_frame(
                audio,
                sample_rate,
                float(row["onset"]) + offset + 0.11,
                window_seconds=0.12,
            )
            if frame is None:
                continue
            freqs, power = frame
            f = midi_hz(int(row["midi"]))
            energy = sum(
                band_energy_from_fft(freqs, power, h * f, CENTS)
                for h in (1, 2, 3)
            )
            values.append(math.log10(energy + EPS))
        scores.append(float(np.median(values)) if values else -1e30)
    return ALIGNMENT_OFFSETS[int(np.argmax(scores))]


def best_candidate_window(
    audio: np.ndarray,
    sample_rate: int,
    onset: float,
    alignment: float,
    midi: int,
) -> dict[str, Any] | None:
    rows: list[dict[str, Any]] = []
    for delta in FRAME_DELTAS:
        frame = fft_power_frame(audio, sample_rate, onset + alignment + delta)
        if frame is None:
            continue
        freqs, power = frame
        row = harmonic_vector(freqs, power, midi)
        row["delta"] = delta
        rows.append(row)
    if not rows:
        return None
    # Frozen framing rule: candidate may select the window with greatest
    # first-five-harmonic evidence, independent of reference correctness.
    return max(rows, key=lambda row: (row["firstFive"], -row["delta"]))


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    return float(np.quantile(np.asarray(values, dtype=np.float64), q))


def evaluate_capture(
    audio: np.ndarray,
    sample_rate: int,
    notes: list[dict[str, Any]],
) -> dict[str, Any]:
    alignment = estimate_alignment(audio, sample_rate, notes)
    evaluated: list[dict[str, Any]] = []

    for note in notes:
        true_midi = int(note["midi"])
        if not 12 <= true_midi <= 115:
            continue
        candidates = [true_midi - 12, true_midi, true_midi + 12]
        rows: dict[int, dict[str, Any]] = {}
        for midi in candidates:
            features = best_candidate_window(
                audio,
                sample_rate,
                float(note["onset"]),
                alignment,
                midi,
            )
            if features is None:
                rows = {}
                break
            rows[midi] = features
        if len(rows) != 3:
            continue

        # Audio-only winner. Smallest-MIDI tie break is frozen prospectively.
        winner = sorted(candidates, key=lambda midi: (-rows[midi]["score"], midi))[0]
        best_wrong = max(rows[true_midi - 12]["score"], rows[true_midi + 12]["score"])
        true_score = rows[true_midi]["score"]
        margin = (true_score - best_wrong) / (abs(true_score) + abs(best_wrong) + EPS)
        true_features = rows[true_midi]
        evaluated.append(
            {
                "trueMidi": true_midi,
                "winnerMidi": winner,
                "direction": "true" if winner == true_midi else ("low" if winner < true_midi else "high"),
                "margin": float(margin),
                "weak": bool(true_features["e1"] < true_features["e2"]),
                "veryWeak": bool(true_features["e1"] < 0.5 * true_features["e2"]),
            }
        )

    def subset_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(rows)
        true_count = sum(row["direction"] == "true" for row in rows)
        low_count = sum(row["direction"] == "low" for row in rows)
        high_count = sum(row["direction"] == "high" for row in rows)
        return {
            "count": n,
            "trueWinnerCount": true_count,
            "trueWinnerPct": (100.0 * true_count / n) if n else None,
            "falseLowCount": low_count,
            "falseLowPct": (100.0 * low_count / n) if n else None,
            "falseHighCount": high_count,
            "falseHighPct": (100.0 * high_count / n) if n else None,
        }

    margins = [float(row["margin"]) for row in evaluated]
    weak = [row for row in evaluated if row["weak"]]
    very_weak = [row for row in evaluated if row["veryWeak"]]
    return {
        "sampleRate": sample_rate,
        "durationSeconds": len(audio) / sample_rate,
        "estimatedMidiToAudioOffsetSeconds": alignment,
        "overall": subset_summary(evaluated),
        "weakFundamental": subset_summary(weak),
        "veryWeakFundamental": subset_summary(very_weak),
        "trueVsBestWrongMargin": {
            "median": percentile(margins, 0.50),
            "p10": percentile(margins, 0.10),
            "minimum": min(margins) if margins else None,
        },
    }


def self_test() -> dict[str, Any]:
    sample_rate = 48000
    t = np.arange(sample_rate, dtype=np.float64) / sample_rate
    f0 = 110.0
    # Weak literal fundamental but strong odd harmonic evidence.
    audio = (
        0.08 * np.sin(2 * np.pi * f0 * t)
        + 1.00 * np.sin(2 * np.pi * 2 * f0 * t)
        + 0.75 * np.sin(2 * np.pi * 3 * f0 * t)
        + 0.10 * np.sin(2 * np.pi * 4 * f0 * t)
        + 0.55 * np.sin(2 * np.pi * 5 * f0 * t)
    )
    midi = int(round(69 + 12 * np.log2(f0 / 440.0)))
    frame = fft_power_frame(audio, sample_rate, 0.5)
    if frame is None:
        raise RuntimeError("self-test frame missing")
    freqs, power = frame
    rows = {m: harmonic_vector(freqs, power, m) for m in (midi - 12, midi, midi + 12)}
    winner = sorted(rows, key=lambda m: (-rows[m]["score"], m))[0]
    if winner != midi:
        raise RuntimeError(f"self-test wrong winner: expected {midi}, got {winner}")
    return {
        "status": "SELF_TEST_PASS",
        "trueMidi": midi,
        "winnerMidi": winner,
        "scores": {str(k): rows[k]["score"] for k in sorted(rows)},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--midi", type=Path)
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--capture-label")
    ap.add_argument("--output", type=Path)
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        print(json.dumps(self_test(), indent=2, sort_keys=True))
        return 0
    if not all((args.midi, args.audio, args.capture_label, args.output)):
        raise SystemExit("--midi --audio --capture-label --output are required")

    notes, instruments = load_notes(args.midi)
    audio, sample_rate = load_mono_audio(args.audio)
    report = {
        "schema": "dadrock.tabs.open-corpus.harmonic-candidate-ranking.v1",
        "captureLabel": args.capture_label,
        "candidateOffsetsSemitones": [-12, 0, 12],
        "tieBreak": "smallest-midi",
        "scoreFormula": "(T + O) / (1 + 0.75*S/(T+eps))",
        "midiNoteCount": len(notes),
        "midiInstruments": instruments,
        "result": evaluate_capture(audio, sample_rate, notes),
        "v168ReferenceFacingScoreCalls": 0,
        "v168PoliciesModified": False,
        "goatHoldoutSelectionModified": False,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
