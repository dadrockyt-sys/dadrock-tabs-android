#!/usr/bin/env python3
"""Deterministic synthetic six-channel crosstalk/debleed harness V1.

SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY. No network, no corpus access, no model use.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

CONTRACT_ID = "songsterr-fresh-synthetic-six-channel-debleed-v1"
STUDY_STAGE = "SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY"
SOURCE_CONTRACT_ID = "synthetic-six-channel-source-bank-v1"
PERTURBATION_CONTRACT_ID = "synthetic-six-channel-perturbation-bank-v1"
CHANNEL_COUNT = 6
SAMPLE_COUNT = 8192
RIDGE_LAMBDA = 1e-4
DISTANCE_DECAY_LEVELS = (0.00, 0.02, 0.05, 0.10, 0.20, 0.35, 0.50)
PAIRED_CONDITIONING_LEVELS = (0.10, 0.30, 0.50, 0.70, 0.85, 0.95)
PERTURBATION_LEVELS = (0.0, 0.0001, 0.001, 0.01)
SOURCE_BINS = (
    (37, 211, 503),
    (53, 239, 557),
    (71, 283, 601),
    (89, 331, 653),
    (109, 379, 709),
    (131, 433, 761),
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


def array_sha256(value: np.ndarray) -> str:
    arr = np.asarray(value, dtype="<f8", order="C")
    return hashlib.sha256(arr.tobytes(order="C")).hexdigest()


def _normalize_rows_rms(matrix: np.ndarray) -> np.ndarray:
    x = np.asarray(matrix, dtype=np.float64).copy()
    x -= np.mean(x, axis=1, keepdims=True)
    rms = np.sqrt(np.mean(x * x, axis=1))
    if x.shape[0] != CHANNEL_COUNT or np.any(~np.isfinite(rms)) or np.any(rms <= 0.0):
        raise ValueError("each synthetic channel must have positive finite RMS")
    x /= rms[:, None]
    if not np.all(np.isfinite(x)):
        raise ValueError("normalized synthetic bank must be finite")
    return x


def generate_source_bank() -> np.ndarray:
    n = np.arange(SAMPLE_COUNT, dtype=np.float64)
    out = np.empty((CHANNEL_COUNT, SAMPLE_COUNT), dtype=np.float64)
    amps = (1.0, 0.6, 0.35)
    for c, bins in enumerate(SOURCE_BINS):
        phases = (0.10 * (c + 1), 0.30 + 0.07 * c, 0.50 + 0.11 * c)
        channel = np.zeros(SAMPLE_COUNT, dtype=np.float64)
        for amp, k, phase in zip(amps, bins, phases, strict=True):
            channel += amp * np.sin(2.0 * np.pi * float(k) * n / SAMPLE_COUNT + phase)
        out[c] = channel
    return _normalize_rows_rms(out)


def generate_perturbation_bank() -> np.ndarray:
    n = np.arange(SAMPLE_COUNT, dtype=np.float64)
    out = np.empty((CHANNEL_COUNT, SAMPLE_COUNT), dtype=np.float64)
    amps = (1.0, 0.7, 0.5, 0.3)
    for c in range(CHANNEL_COUNT):
        bins = (1009 + 17 * c, 1301 + 19 * c, 1601 + 23 * c, 1901 + 29 * c)
        phases = tuple(scale * (c + 1) for scale in (0.20, 0.40, 0.60, 0.80))
        channel = np.zeros(SAMPLE_COUNT, dtype=np.float64)
        for amp, k, phase in zip(amps, bins, phases, strict=True):
            channel += amp * np.cos(2.0 * np.pi * float(k) * n / SAMPLE_COUNT + phase)
        out[c] = channel
    return _normalize_rows_rms(out)


def distance_decay_weights() -> np.ndarray:
    w = np.zeros((CHANNEL_COUNT, CHANNEL_COUNT), dtype=np.float64)
    for i in range(CHANNEL_COUNT):
        for j in range(CHANNEL_COUNT):
            if i != j:
                w[i, j] = 1.0 / abs(i - j)
        row_sum = float(np.sum(w[i]))
        if not np.isfinite(row_sum) or row_sum <= 0.0:
            raise ValueError("invalid distance-decay weight row")
        w[i] /= row_sum
    return w


def build_distance_decay_matrix(level: float) -> np.ndarray:
    b = float(level)
    if b not in DISTANCE_DECAY_LEVELS:
        raise ValueError("unfrozen distance-decay bleed level")
    return np.eye(CHANNEL_COUNT, dtype=np.float64) + b * distance_decay_weights()


def build_paired_conditioning_matrix(level: float) -> np.ndarray:
    b = float(level)
    if b not in PAIRED_CONDITIONING_LEVELS:
        raise ValueError("unfrozen paired-conditioning bleed level")
    m = np.eye(CHANNEL_COUNT, dtype=np.float64)
    for a, c in ((0, 1), (2, 3), (4, 5)):
        m[a, c] = b
        m[c, a] = b
    return m


def nrmse_metrics(estimate: np.ndarray, source: np.ndarray) -> dict[str, Any]:
    e = np.asarray(estimate, dtype=np.float64)
    s = np.asarray(source, dtype=np.float64)
    if e.shape != (CHANNEL_COUNT, SAMPLE_COUNT) or s.shape != e.shape:
        raise ValueError("estimate/source shape mismatch")
    diff = e - s
    source_norms = np.linalg.norm(s, axis=1)
    channel = np.linalg.norm(diff, axis=1) / source_norms
    pooled = float(np.linalg.norm(diff) / np.linalg.norm(s))
    maximum = float(np.max(channel))
    if not np.all(np.isfinite(channel)) or not np.isfinite(pooled) or not np.isfinite(maximum):
        raise ValueError("NRMSE metrics must be finite")
    return {
        "perChannelNrmse": [float(v) for v in channel],
        "pooledNrmse": pooled,
        "maxChannelNrmse": maximum,
    }


def improvement_db(raw_pooled: float, recovered_pooled: float) -> float:
    raw = max(float(raw_pooled), 1e-15)
    recovered = max(float(recovered_pooled), 1e-15)
    value = 20.0 * math.log10(raw / recovered)
    if not np.isfinite(value):
        raise ValueError("improvement dB must be finite")
    return float(value)


def recover_direct(m: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.solve(m, y)


def recover_ridge(m: np.ndarray, y: np.ndarray) -> np.ndarray:
    identity = np.eye(CHANNEL_COUNT, dtype=np.float64)
    return np.linalg.solve(m.T @ m + RIDGE_LAMBDA * identity, m.T @ y)


def evaluate_matrix_case(family: str, level: float, m: np.ndarray, source: np.ndarray, perturbation: np.ndarray) -> dict[str, Any]:
    if m.shape != (CHANNEL_COUNT, CHANNEL_COUNT):
        raise ValueError("mixing matrix must be 6x6")
    condition = float(np.linalg.cond(m, 2))
    if not np.isfinite(condition):
        raise ValueError("condition number must be finite")

    runs: list[dict[str, Any]] = []
    for sigma in PERTURBATION_LEVELS:
        y = m @ source + float(sigma) * perturbation
        raw = nrmse_metrics(y, source)
        direct_estimate = recover_direct(m, y)
        ridge_estimate = recover_ridge(m, y)
        direct = nrmse_metrics(direct_estimate, source)
        ridge = nrmse_metrics(ridge_estimate, source)
        runs.append({
            "perturbationRmsScale": float(sigma),
            "raw": raw,
            "direct": {
                **direct,
                "improvementDbOverRaw": improvement_db(raw["pooledNrmse"], direct["pooledNrmse"]),
            },
            "ridge": {
                **ridge,
                "improvementDbOverRaw": improvement_db(raw["pooledNrmse"], ridge["pooledNrmse"]),
            },
        })

    return {
        "family": family,
        "bleedLevel": float(level),
        "conditionNumber2": condition,
        "matrixSha256": array_sha256(m),
        "runs": runs,
    }


def run_harness() -> dict[str, Any]:
    source = generate_source_bank()
    perturbation = generate_perturbation_bank()
    source_before = source.copy()
    perturbation_before = perturbation.copy()

    cases: list[dict[str, Any]] = []
    for level in DISTANCE_DECAY_LEVELS:
        m = build_distance_decay_matrix(level)
        cases.append(evaluate_matrix_case("distance_decay", level, m, source, perturbation))
    for level in PAIRED_CONDITIONING_LEVELS:
        m = build_paired_conditioning_matrix(level)
        cases.append(evaluate_matrix_case("paired_conditioning", level, m, source, perturbation))

    if not np.array_equal(source, source_before):
        raise ValueError("source bank mutated during harness")
    if not np.array_equal(perturbation, perturbation_before):
        raise ValueError("perturbation bank mutated during harness")

    expected_case_count = len(DISTANCE_DECAY_LEVELS) + len(PAIRED_CONDITIONING_LEVELS)
    if len(cases) != expected_case_count:
        raise ValueError("unexpected matrix case count")

    return {
        "contract": CONTRACT_ID,
        "studyStage": STUDY_STAGE,
        "numpyVersion": np.__version__,
        "sourceContractId": SOURCE_CONTRACT_ID,
        "perturbationContractId": PERTURBATION_CONTRACT_ID,
        "channelCount": CHANNEL_COUNT,
        "sampleCountPerChannel": SAMPLE_COUNT,
        "sourceSha256": array_sha256(source),
        "perturbationSha256": array_sha256(perturbation),
        "distanceDecayLevels": [float(v) for v in DISTANCE_DECAY_LEVELS],
        "pairedConditioningLevels": [float(v) for v in PAIRED_CONDITIONING_LEVELS],
        "perturbationLevels": [float(v) for v in PERTURBATION_LEVELS],
        "ridgeLambda": RIDGE_LAMBDA,
        "matrixCaseCount": expected_case_count,
        "runCaseCount": expected_case_count * len(PERTURBATION_LEVELS),
        "allFinite": True,
        "cases": cases,
        "interpretation": "SYNTHETIC_SOFTWARE_FEASIBILITY_ONLY",
        **AUTHORIZATION_BOUNDARY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Canonical result JSON output path")
    args = parser.parse_args()
    result = run_harness()
    output_bytes = canonical_json_bytes(result)
    Path(args.output).write_bytes(output_bytes)
    print(output_bytes.decode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
