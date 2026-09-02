#!/usr/bin/env python3
"""Prospectively frozen V169-style harmonic candidate-ranking benchmark V2.

V2 is separate from V168. Public Guitar-TECHS MIDI defines controlled octave
candidate sets and evaluates correctness only after the audio-only winner is
selected. The V2 formula was frozen before any real P1/P2 ranking result.
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

WEIGHTS = np.asarray((1.00, 0.85, 0.72, 0.62, 0.54, 0.48, 0.42, 0.38), dtype=np.float64)
LOWER_ODD_WEIGHTS = np.asarray((1.00, 0.72, 0.54, 0.42), dtype=np.float64)
LOWER_ODD_MULTIPLIERS = (0.5, 1.5, 2.5, 3.5)
ROOT_EXPONENT = 0.25
LOWER_PENALTY = 0.50
WINDOW_SECONDS = 0.186
CENTS = 35.0
FRAME_DELTAS = (0.08, 0.13, 0.18, 0.24)
ALIGNMENT_OFFSETS = tuple(float(v) for v in np.arange(-0.12, 0.1201, 0.01))


class V2Error(RuntimeError):
    pass


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


def candidate_features(freqs: np.ndarray, power: np.ndarray, midi: int) -> dict[str, Any]:
    f = midi_hz(midi)
    harmonic = np.asarray(
        [band_energy_from_fft(freqs, power, (h + 1) * f, CENTS) for h in range(8)],
        dtype=np.float64,
    )
    maximum = max(float(np.max(harmonic)), EPS)
    compressed = np.power(harmonic / maximum, ROOT_EXPONENT)
    coverage = float(np.dot(WEIGHTS, compressed))

    lower_odd_power = np.asarray(
        [band_energy_from_fft(freqs, power, multiplier * f, CENTS) for multiplier in LOWER_ODD_MULTIPLIERS],
        dtype=np.float64,
    )
    lower_odd_compressed = np.power(lower_odd_power / maximum, ROOT_EXPONENT)
    lower_odd = float(np.dot(LOWER_ODD_WEIGHTS, lower_odd_compressed))

    score = coverage / (1.0 + LOWER_PENALTY * lower_odd / (coverage + EPS))
    return {
        "score": float(score),
        "coverage": coverage,
        "lowerOdd": lower_odd,
        "maximumHarmonicPower": maximum,
        "firstFiveRaw": float(np.sum(harmonic[:5])),
        "e1": float(harmonic[0]),
        "e2": float(harmonic[1]),
    }


def estimate_alignment(
    audio: np.ndarray,
    sample_rate: int,
    notes: list[dict[str, Any]],
) -> float:
    rows = [
        row
        for row in notes
        if 28 <= int(row["midi"]) <= 96 and float(row["offset"]) - float(row["onset"]) >= 0.12
    ][:80]
    scores: list[float] = []
    for offset in ALIGNMENT_OFFSETS:
        values: list[float] = []
        for row in rows:
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
                band_energy_from_fft(freqs, power, harmonic * f, CENTS)
                for harmonic in (1, 2, 3)
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
        features = candidate_features(freqs, power, midi)
        features["delta"] = delta
        rows.append(features)
    if not rows:
        return None
    return max(rows, key=lambda row: (row["firstFiveRaw"], -row["delta"]))


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    return float(np.quantile(np.asarray(values, dtype=np.float64), q))


def summarize_subset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    true_count = sum(row["direction"] == "true" for row in rows)
    low_count = sum(row["direction"] == "low" for row in rows)
    high_count = sum(row["direction"] == "high" for row in rows)
    return {
        "count": count,
        "trueWinnerCount": true_count,
        "trueWinnerPct": 100.0 * true_count / count if count else None,
        "falseLowCount": low_count,
        "falseLowPct": 100.0 * low_count / count if count else None,
        "falseHighCount": high_count,
        "falseHighPct": 100.0 * high_count / count if count else None,
    }


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
        candidates = (true_midi - 12, true_midi, true_midi + 12)
        features: dict[int, dict[str, Any]] = {}
        for candidate_midi in candidates:
            row = best_candidate_window(
                audio,
                sample_rate,
                float(note["onset"]),
                alignment,
                candidate_midi,
            )
            if row is None:
                features = {}
                break
            features[candidate_midi] = row
        if len(features) != 3:
            continue

        winner = sorted(candidates, key=lambda midi: (-features[midi]["score"], midi))[0]
        best_wrong = max(features[true_midi - 12]["score"], features[true_midi + 12]["score"])
        true_score = features[true_midi]["score"]
        margin = (true_score - best_wrong) / (abs(true_score) + abs(best_wrong) + EPS)
        true_features = features[true_midi]
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

    weak = [row for row in evaluated if row["weak"]]
    very_weak = [row for row in evaluated if row["veryWeak"]]
    margins = [float(row["margin"]) for row in evaluated]
    return {
        "sampleRate": sample_rate,
        "durationSeconds": len(audio) / sample_rate,
        "estimatedMidiToAudioOffsetSeconds": alignment,
        "overall": summarize_subset(evaluated),
        "weakFundamental": summarize_subset(weak),
        "veryWeakFundamental": summarize_subset(very_weak),
        "trueVsBestWrongMargin": {
            "median": percentile(margins, 0.50),
            "p10": percentile(margins, 0.10),
            "minimum": min(margins) if margins else None,
        },
    }


def synthetic_audio(amplitudes: tuple[float, ...], *, f0: float = 110.0, sample_rate: int = 48000) -> np.ndarray:
    t = np.arange(sample_rate, dtype=np.float64) / sample_rate
    result = np.zeros_like(t)
    for harmonic, amplitude in enumerate(amplitudes, start=1):
        result += float(amplitude) * np.sin(2.0 * np.pi * harmonic * f0 * t)
    return result


def score_synthetic_fixture(amplitudes: tuple[float, ...]) -> dict[str, Any]:
    sample_rate = 48000
    true_midi = 45
    audio = synthetic_audio(amplitudes, sample_rate=sample_rate)
    frame = fft_power_frame(audio, sample_rate, 0.5)
    if frame is None:
        raise V2Error("synthetic frame unavailable")
    freqs, power = frame
    candidates = (33, 45, 57)
    rows = {midi: candidate_features(freqs, power, midi) for midi in candidates}
    winner = sorted(candidates, key=lambda midi: (-rows[midi]["score"], midi))[0]
    return {
        "trueMidi": true_midi,
        "winnerMidi": winner,
        "scores": {str(midi): rows[midi]["score"] for midi in candidates},
    }


def self_test() -> dict[str, Any]:
    fixtures: dict[str, tuple[float, ...]] = {
        "normal-decay": (1.00, 0.70, 0.50, 0.35, 0.25, 0.18, 0.12, 0.08),
        "weak-fundamental": (0.08, 1.00, 0.75, 0.10, 0.55, 0.08, 0.35, 0.05),
        "even-heavy-distortion": (0.25, 1.00, 0.15, 0.70, 0.10, 0.45, 0.08, 0.30),
        "very-even-heavy": (0.10, 1.00, 0.05, 0.80, 0.02, 0.60, 0.01, 0.40),
    }
    results: dict[str, Any] = {}
    for name, amplitudes in fixtures.items():
        result = score_synthetic_fixture(amplitudes)
        results[name] = result
        if result["winnerMidi"] != result["trueMidi"]:
            raise V2Error(
                f"synthetic fixture {name} wrong winner: expected {result['trueMidi']}, got {result['winnerMidi']}"
            )
    return {
        "status": "SYNTHETIC_GUARDS_PASS",
        "formula": "C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25",
        "fixtures": results,
        "realP1RankingObserved": False,
        "realP2RankingObserved": False,
        "v168ReferenceFacingScoreCalls": 0,
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
        "schema": "dadrock.tabs.open-corpus.harmonic-candidate-ranking.v2",
        "captureLabel": args.capture_label,
        "candidateOffsetsSemitones": [-12, 0, 12],
        "tieBreak": "smallest-midi",
        "scoreFormula": "C/(1+0.50*L/(C+eps)); Q=(E/M)^0.25",
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
    try:
        raise SystemExit(main())
    except V2Error as exc:
        raise SystemExit(f"V2 synthetic guard failed: {exc}")
