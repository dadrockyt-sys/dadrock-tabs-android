#!/usr/bin/env python3
"""Deterministic synthetic hardware-marker clock-map harness V1.

SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY. Hardware-marker records only; no audio
content, corpus, network, model, or correctness input is permitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable

import numpy as np

CONTRACT_ID = "songsterr-fresh-synthetic-hardware-marker-clock-map-v1"
ALGORITHM_CONTRACT_ID = "hardware-marker-affine-ols-v1"
STUDY_STAGE = "SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY"
SAMPLE_RATE = 48000
FROZEN_STRUCTURAL_BOUND_SECONDS = 0.025
MARKER_TICKS = tuple(range(0, 10_000_001, 500_000))
EVALUATION_TICKS = tuple(range(0, 10_000_001, 250_000))
JITTER_SAMPLE_OFFSETS = (
    0, 48, -48, 24, -24, 36, -36, 12, -12, 48, -48,
    24, -24, 36, -36, 12, -12, 48, -48, 24, 0,
)
CASE_DEFINITIONS = (
    {"caseId": "exact_affine", "interceptSeconds": 0.250000, "baseSecondsPerTick": 1.000000e-6, "quadraticWarpSeconds": 0.0, "jitterSampleOffsets": None},
    {"caseId": "positive_100ppm", "interceptSeconds": 0.125000, "baseSecondsPerTick": 1.000100e-6, "quadraticWarpSeconds": 0.0, "jitterSampleOffsets": None},
    {"caseId": "negative_100ppm", "interceptSeconds": 0.375000, "baseSecondsPerTick": 0.999900e-6, "quadraticWarpSeconds": 0.0, "jitterSampleOffsets": None},
    {"caseId": "deterministic_marker_jitter_1ms", "interceptSeconds": 0.200000, "baseSecondsPerTick": 1.000000e-6, "quadraticWarpSeconds": 0.0, "jitterSampleOffsets": JITTER_SAMPLE_OFFSETS},
    {"caseId": "quadratic_warp_10ms", "interceptSeconds": 0.300000, "baseSecondsPerTick": 1.000000e-6, "quadraticWarpSeconds": 0.010, "jitterSampleOffsets": None},
    {"caseId": "quadratic_warp_180ms_stress", "interceptSeconds": 0.300000, "baseSecondsPerTick": 1.000000e-6, "quadraticWarpSeconds": 0.180, "jitterSampleOffsets": None},
)
AUTHORIZATION_BOUNDARY = {
    "basicPitchAuthorized": False,
    "v6Authorized": False,
    "correctnessAuthorized": False,
    "modelValidationComplete": False,
    "customerEligibleEvents": 0,
    "mayAdvanceDelivery": False,
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _require_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{field} must be an integer")
    return int(value)


def validate_markers(markers: list[dict[str, Any]], sample_rate: Any) -> tuple[np.ndarray, np.ndarray, int]:
    sr = _require_integer(sample_rate, "sampleRate")
    if sr <= 0:
        raise ValueError("sampleRate must be > 0")
    if not isinstance(markers, list) or len(markers) < 4:
        raise ValueError("at least 4 paired hardware markers are required")

    ticks: list[int] = []
    samples: list[int] = []
    for index, marker in enumerate(markers):
        if not isinstance(marker, dict):
            raise ValueError("each marker must be an object")
        marker_id = _require_integer(marker.get("markerId"), "markerId")
        logger_tick = _require_integer(marker.get("loggerTick"), "loggerTick")
        audio_sample = _require_integer(marker.get("audioSampleIndex"), "audioSampleIndex")
        if marker_id != index:
            raise ValueError("markerId sequence must be exactly 0..N-1 in supplied order")
        if logger_tick < 0 or audio_sample < 0:
            raise ValueError("loggerTick/audioSampleIndex must be nonnegative")
        ticks.append(logger_tick)
        samples.append(audio_sample)

    if any(b <= a for a, b in zip(ticks, ticks[1:])):
        raise ValueError("loggerTick values must be strictly increasing")
    if any(b <= a for a, b in zip(samples, samples[1:])):
        raise ValueError("audioSampleIndex values must be strictly increasing")
    if ticks[-1] - ticks[0] <= 0:
        raise ValueError("logger tick span must be positive")
    if samples[-1] - samples[0] <= 0:
        raise ValueError("audio sample span must be positive")

    return np.asarray(ticks, dtype=np.float64), np.asarray(samples, dtype=np.float64), sr


def fit_clock_map(markers: list[dict[str, Any]], sample_rate: Any) -> dict[str, Any]:
    x, sample_indices, sr = validate_markers(markers, sample_rate)
    y = sample_indices / float(sr)
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    x_centered = x - x_mean
    denominator = float(np.sum(x_centered * x_centered))
    if not np.isfinite(denominator) or denominator <= 0.0:
        raise ValueError("clock-map denominator must be finite and positive")
    slope = float(np.sum(x_centered * (y - y_mean)) / denominator)
    if not np.isfinite(slope) or slope <= 0.0:
        raise ValueError("secondsPerLoggerTick must be finite and positive")
    intercept = float(y_mean - slope * x_mean)
    if not np.isfinite(intercept):
        raise ValueError("interceptSeconds must be finite")
    predicted = intercept + slope * x
    residual = predicted - y
    if not np.all(np.isfinite(residual)):
        raise ValueError("marker residuals must be finite")
    max_abs = float(np.max(np.abs(residual)))
    rms = float(np.sqrt(np.mean(residual * residual)))
    input_identity = {"sampleRate": sr, "markers": markers}
    return {
        "algorithmContractId": ALGORITHM_CONTRACT_ID,
        "markerCount": len(markers),
        "sampleRate": sr,
        "interceptSeconds": intercept,
        "secondsPerLoggerTick": slope,
        "loggerTicksPerSecond": float(1.0 / slope),
        "firstLoggerTick": int(markers[0]["loggerTick"]),
        "lastLoggerTick": int(markers[-1]["loggerTick"]),
        "firstAudioSampleIndex": int(markers[0]["audioSampleIndex"]),
        "lastAudioSampleIndex": int(markers[-1]["audioSampleIndex"]),
        "markerResidualSeconds": [float(v) for v in residual],
        "maxAbsoluteMarkerResidualSeconds": max_abs,
        "rmsMarkerResidualSeconds": rms,
        "markerInputSha256": canonical_sha256(input_identity),
    }


def map_logger_ticks(transform: dict[str, Any], ticks: Iterable[Any]) -> np.ndarray:
    tick_list = list(ticks)
    values: list[int] = []
    for tick in tick_list:
        t = _require_integer(tick, "queryTick")
        if t < 0:
            raise ValueError("query ticks must be nonnegative")
        values.append(t)
    if any(b < a for a, b in zip(values, values[1:])):
        raise ValueError("query ticks must be nondecreasing")
    slope = float(transform["secondsPerLoggerTick"])
    intercept = float(transform["interceptSeconds"])
    if not np.isfinite(slope) or slope <= 0.0 or not np.isfinite(intercept):
        raise ValueError("invalid clock transform")
    arr = np.asarray(values, dtype=np.float64)
    mapped = intercept + slope * arr
    if not np.all(np.isfinite(mapped)):
        raise ValueError("mapped query times must be finite")
    return mapped


def half_away_nonnegative(value: float) -> int:
    v = float(value)
    if not np.isfinite(v) or v < 0.0:
        raise ValueError("half-away sample generation requires finite nonnegative value")
    return int(math.floor(v + 0.5))


def _case_definition(case_id: str) -> dict[str, Any]:
    for case in CASE_DEFINITIONS:
        if case["caseId"] == case_id:
            return case
    raise ValueError(f"unknown frozen synthetic case: {case_id}")


def truth_seconds(case: dict[str, Any], tick: int) -> float:
    t = float(tick)
    normalized = t / 10_000_000.0
    return float(
        float(case["interceptSeconds"])
        + float(case["baseSecondsPerTick"]) * t
        + float(case["quadraticWarpSeconds"]) * normalized * normalized
    )


def generate_case_markers(case_id: str) -> list[dict[str, int]]:
    case = _case_definition(case_id)
    jitter = case["jitterSampleOffsets"]
    if jitter is not None and len(jitter) != len(MARKER_TICKS):
        raise ValueError("frozen jitter pattern length mismatch")
    markers: list[dict[str, int]] = []
    for index, tick in enumerate(MARKER_TICKS):
        ideal_samples = float(SAMPLE_RATE) * truth_seconds(case, tick)
        audio_sample = half_away_nonnegative(ideal_samples)
        if jitter is not None:
            audio_sample += int(jitter[index])
        markers.append({"markerId": index, "loggerTick": tick, "audioSampleIndex": audio_sample})
    validate_markers(markers, SAMPLE_RATE)
    return markers


def evaluate_case(case_id: str) -> dict[str, Any]:
    case = _case_definition(case_id)
    markers = generate_case_markers(case_id)
    transform = fit_clock_map(markers, SAMPLE_RATE)
    mapped = map_logger_ticks(transform, EVALUATION_TICKS)
    truth = np.asarray([truth_seconds(case, tick) for tick in EVALUATION_TICKS], dtype=np.float64)
    error = mapped - truth
    if not np.all(np.isfinite(error)):
        raise ValueError("synthetic truth mapping errors must be finite")
    max_abs = float(np.max(np.abs(error)))
    rms = float(np.sqrt(np.mean(error * error)))
    return {
        "caseId": case_id,
        "syntheticTruth": {
            "interceptSeconds": float(case["interceptSeconds"]),
            "baseSecondsPerTick": float(case["baseSecondsPerTick"]),
            "quadraticWarpSeconds": float(case["quadraticWarpSeconds"]),
            "jitterSampleOffsets": None if case["jitterSampleOffsets"] is None else [int(v) for v in case["jitterSampleOffsets"]],
        },
        "markers": markers,
        "transform": transform,
        "truthMappingErrorSeconds": [float(v) for v in error],
        "maxAbsoluteTruthMappingErrorSeconds": max_abs,
        "rmsTruthMappingErrorSeconds": rms,
        "syntheticTruthWithinFrozen025SecondStructuralBound": max_abs <= FROZEN_STRUCTURAL_BOUND_SECONDS,
    }


def run_harness() -> dict[str, Any]:
    cases = [evaluate_case(case["caseId"]) for case in CASE_DEFINITIONS]
    return {
        "contract": CONTRACT_ID,
        "studyStage": STUDY_STAGE,
        "algorithmContractId": ALGORITHM_CONTRACT_ID,
        "numpyVersion": np.__version__,
        "sampleRate": SAMPLE_RATE,
        "markerTicks": list(MARKER_TICKS),
        "evaluationTicks": list(EVALUATION_TICKS),
        "frozenStructuralTimingBoundSeconds": FROZEN_STRUCTURAL_BOUND_SECONDS,
        "caseCount": len(cases),
        "allFinite": True,
        "cases": cases,
        "interpretation": "SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY",
        **AUTHORIZATION_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = run_harness()
    output_bytes = canonical_json_bytes(result)
    Path(args.output).write_bytes(output_bytes)
    print(output_bytes.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
