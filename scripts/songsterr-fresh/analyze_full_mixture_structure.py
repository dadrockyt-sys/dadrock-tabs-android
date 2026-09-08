#!/usr/bin/env python3
"""Reference-blind, CPU-only full-mixture timing analysis for the fresh pipeline.

This script intentionally stops at structure evidence. It does not infer notes,
strings/frets, or import any archived V143/Gomyway scorer or gate.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path
from typing import Iterable

import librosa
import numpy as np

HOP_LENGTH = 512
METER_NUMERATORS = (3, 4)
EPSILON = 1e-12


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return float(max(low, min(high, value)))


def finite(value: float, label: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def lag_correlation(values: np.ndarray, lag: int) -> float:
    if values.size < lag + 4:
        return 0.0
    left = values[:-lag].astype(float)
    right = values[lag:].astype(float)
    left -= float(np.mean(left))
    right -= float(np.mean(right))
    denom = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denom <= EPSILON:
        return 0.0
    return clamp(float(np.dot(left, right) / denom), -1.0, 1.0)


def softmax(values: Iterable[float], temperature: float = 1.0) -> np.ndarray:
    array = np.asarray(list(values), dtype=float)
    if array.size == 0:
        return array
    shifted = (array - float(np.max(array))) / max(float(temperature), EPSILON)
    exponent = np.exp(np.clip(shifted, -60.0, 60.0))
    total = float(np.sum(exponent))
    return exponent / total if total > EPSILON else np.full(array.shape, 1.0 / array.size)


def estimate_meter(beat_strengths: np.ndarray, tempo_confidence: float) -> tuple[dict, list[dict]]:
    if beat_strengths.size < 8:
        raise ValueError("INSUFFICIENT_BEATS_FOR_METER")

    global_mean = float(np.mean(beat_strengths))
    global_std = float(np.std(beat_strengths)) + EPSILON
    candidates: list[dict] = []

    for numerator in METER_NUMERATORS:
        best_phase = 0
        best_contrast = -math.inf
        phase_scores: list[float] = []

        for phase in range(numerator):
            mask = np.arange(beat_strengths.size) % numerator == phase
            downbeats = beat_strengths[mask]
            others = beat_strengths[~mask]
            if downbeats.size == 0 or others.size == 0:
                contrast = -10.0
            else:
                contrast = (float(np.mean(downbeats)) - float(np.mean(others))) / global_std
            phase_scores.append(float(contrast))
            if contrast > best_contrast:
                best_contrast = float(contrast)
                best_phase = phase

        periodicity = lag_correlation(beat_strengths, numerator)
        relative_downbeat_strength = (
            float(np.mean(beat_strengths[np.arange(beat_strengths.size) % numerator == best_phase]))
            / (global_mean + EPSILON)
        )
        score = 0.65 * best_contrast + 0.35 * periodicity
        candidates.append(
            {
                "numerator": numerator,
                "denominator": 4,
                "phaseBeatOffset": int(best_phase),
                "score": float(score),
                "downbeatContrast": float(best_contrast),
                "periodicity": float(periodicity),
                "relativeDownbeatStrength": float(relative_downbeat_strength),
                "phaseScores": phase_scores,
            }
        )

    probabilities = softmax((candidate["score"] for candidate in candidates), temperature=0.55)
    support = clamp(beat_strengths.size / 24.0)
    reliability = (0.45 + 0.55 * tempo_confidence) * (0.45 + 0.55 * support)
    for candidate, probability in zip(candidates, probabilities.tolist()):
        candidate["probability"] = float(probability)
        candidate["confidence"] = clamp(float(probability) * reliability, 0.05, 0.95)

    selected = max(candidates, key=lambda candidate: (candidate["probability"], candidate["score"], candidate["numerator"]))
    return dict(selected), candidates


def nearest_grid_distance(phase: float, grid: tuple[float, ...]) -> float:
    return min(abs(phase - slot) for slot in grid)


def estimate_feel(onset_times: np.ndarray, beat_times: np.ndarray) -> dict:
    phases: list[float] = []
    for onset in onset_times.tolist():
        index = int(np.searchsorted(beat_times, onset, side="right") - 1)
        if index < 0 or index >= beat_times.size - 1:
            continue
        start = float(beat_times[index])
        end = float(beat_times[index + 1])
        interval = end - start
        if interval <= EPSILON:
            continue
        phase = (float(onset) - start) / interval
        if 0.08 <= phase <= 0.92:
            phases.append(float(phase))

    if len(phases) < 6:
        return {
            "feel": "straight",
            "confidence": 0.2,
            "diagnostics": {
                "interiorOnsetCount": len(phases),
                "straightError": None,
                "tripletError": None,
                "reason": "INSUFFICIENT_INTERIOR_ONSETS",
            },
        }

    straight_grid = (0.0, 0.25, 0.5, 0.75, 1.0)
    triplet_grid = (0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0)
    straight_error = float(np.mean([nearest_grid_distance(phase, straight_grid) for phase in phases]))
    triplet_error = float(np.mean([nearest_grid_distance(phase, triplet_grid) for phase in phases]))
    feel = "straight" if straight_error <= triplet_error else "triplet"
    separation = abs(straight_error - triplet_error) / max(straight_error + triplet_error, EPSILON)
    support = clamp(len(phases) / 32.0)
    confidence = clamp(0.15 + 0.75 * separation * (0.5 + 0.5 * support), 0.15, 0.9)

    return {
        "feel": feel,
        "confidence": confidence,
        "diagnostics": {
            "interiorOnsetCount": len(phases),
            "straightError": straight_error,
            "tripletError": triplet_error,
            "separation": float(separation),
        },
    }


def analyze(input_path: Path, audio_source: str) -> dict:
    y, sample_rate = librosa.load(str(input_path), sr=None, mono=True)
    if y.size == 0:
        raise ValueError("EMPTY_AUDIO")

    duration_seconds = finite(librosa.get_duration(y=y, sr=sample_rate), "durationSeconds")
    if duration_seconds < 1.0:
        raise ValueError("AUDIO_TOO_SHORT_FOR_STRUCTURE_ANALYSIS")

    onset_envelope = librosa.onset.onset_strength(
        y=y,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
        aggregate=np.median,
    )
    tempo_estimate, beat_frames = librosa.beat.beat_track(
        y=y,
        sr=sample_rate,
        onset_envelope=onset_envelope,
        hop_length=HOP_LENGTH,
        trim=False,
        units="frames",
        sparse=True,
    )
    beat_frames = np.asarray(beat_frames, dtype=int).reshape(-1)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate, hop_length=HOP_LENGTH).astype(float)

    if beat_times.size < 8:
        raise ValueError("INSUFFICIENT_BEATS_FOR_STRUCTURE_ANALYSIS")

    beat_intervals = np.diff(beat_times)
    median_interval = float(np.median(beat_intervals))
    if median_interval <= EPSILON:
        raise ValueError("INVALID_BEAT_INTERVAL")

    indices = np.arange(beat_times.size, dtype=float)
    slope, intercept = np.polyfit(indices, beat_times, 1)
    beat_period = finite(slope, "beatPeriodSeconds")
    if beat_period <= EPSILON:
        raise ValueError("INVALID_BEAT_PERIOD")
    bpm = finite(60.0 / beat_period, "tempo.bpm")

    fitted_beats = intercept + slope * indices
    beat_fit_errors = beat_times - fitted_beats
    beat_fit_rmse = float(np.sqrt(np.mean(np.square(beat_fit_errors))))
    interval_cv = float(np.std(beat_intervals) / max(np.mean(beat_intervals), EPSILON))
    tempo_support = clamp(beat_times.size / 24.0)
    tempo_confidence = clamp(math.exp(-7.0 * interval_cv) * (0.55 + 0.45 * tempo_support), 0.05, 0.98)

    beat_strengths = np.asarray(onset_envelope[np.clip(beat_frames, 0, onset_envelope.size - 1)], dtype=float)
    selected_meter, meter_candidates = estimate_meter(beat_strengths, tempo_confidence)

    onset_times = np.asarray(
        librosa.onset.onset_detect(
            onset_envelope=onset_envelope,
            sr=sample_rate,
            hop_length=HOP_LENGTH,
            units="time",
            backtrack=False,
        ),
        dtype=float,
    )
    feel = estimate_feel(onset_times, beat_times)

    phase_index = int(selected_meter["phaseBeatOffset"])
    if phase_index >= beat_times.size:
        raise ValueError("DOWNBEAT_PHASE_OUTSIDE_AUDIO")
    first_downbeat_time = float(beat_times[phase_index])
    pickup_duration = 0.0 if first_downbeat_time < 0.03 else first_downbeat_time
    pickup_confidence = clamp(
        selected_meter["confidence"] * (0.65 + 0.35 * tempo_confidence),
        0.05,
        0.95,
    )

    overall_confidence = min(
        tempo_confidence,
        float(selected_meter["confidence"]),
        float(feel["confidence"]),
    )

    librosa_tempo = float(np.asarray(tempo_estimate, dtype=float).reshape(-1)[0])
    return {
        "version": 1,
        "referenceBlind": True,
        "audioSource": audio_source,
        "durationSeconds": duration_seconds,
        "sampleRate": int(sample_rate),
        "tempo": {
            "bpm": bpm,
            "beatUnit": "quarter-note",
            "confidence": tempo_confidence,
            "trackerBpm": librosa_tempo,
            "beatPeriodSeconds": beat_period,
        },
        "selectedMeter": {
            "numerator": int(selected_meter["numerator"]),
            "denominator": 4,
            "confidence": float(selected_meter["confidence"]),
            "phaseBeatOffset": phase_index,
            "score": float(selected_meter["score"]),
        },
        "meterCandidates": meter_candidates,
        "feel": feel,
        "pickup": {
            "durationSeconds": pickup_duration,
            "confidence": pickup_confidence,
            "firstDetectedDownbeatSeconds": first_downbeat_time,
            "basis": "selected-meter-accent-phase",
        },
        "beatTimes": [float(value) for value in beat_times.tolist()],
        "confidence": {
            "overall": overall_confidence,
            "tempo": tempo_confidence,
            "meter": float(selected_meter["confidence"]),
            "feel": float(feel["confidence"]),
            "downbeat": pickup_confidence,
        },
        "diagnostics": {
            "beatCount": int(beat_times.size),
            "onsetCount": int(onset_times.size),
            "medianBeatIntervalSeconds": median_interval,
            "beatIntervalCoefficientOfVariation": interval_cv,
            "beatFitRmseSeconds": beat_fit_rmse,
            "beatFitMaxAbsErrorSeconds": float(np.max(np.abs(beat_fit_errors))),
            "meterCandidateScope": ["3/4", "4/4"],
            "compoundMeterSupported": False,
        },
        "provenance": {
            "source": "songsterr-fresh-full-mixture-structure-cpu-v1",
            "referenceBlind": True,
            "noteInferenceUsed": False,
            "legacyV143ScorerImported": False,
            "python": platform.python_version(),
            "librosa": librosa.__version__,
            "numpy": np.__version__,
            "hopLength": HOP_LENGTH,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--audio-source", required=True)
    args = parser.parse_args()

    result = analyze(args.input, args.audio_source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "durationSeconds": result["durationSeconds"],
        "tempoBpm": result["tempo"]["bpm"],
        "tempoConfidence": result["tempo"]["confidence"],
        "meter": f"{result['selectedMeter']['numerator']}/{result['selectedMeter']['denominator']}",
        "meterConfidence": result["selectedMeter"]["confidence"],
        "feel": result["feel"]["feel"],
        "feelConfidence": result["feel"]["confidence"],
        "pickupDurationSeconds": result["pickup"]["durationSeconds"],
        "beatCount": result["diagnostics"]["beatCount"],
        "beatFitRmseSeconds": result["diagnostics"]["beatFitRmseSeconds"],
    }
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
