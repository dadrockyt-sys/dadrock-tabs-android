#!/usr/bin/env python3
"""Synthetic-only representation bridge from frozen V6 innovation to line evidence.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE.md

The bridge does not make a pitch decision. It collapses deterministic spectral
leakage from frozen 2048-sample Hann frames zero-padded to an 8192-point FFT by
retaining only deterministic local maxima on the unchanged FFT frequency grid.
No energy is boosted, shifted, interpolated, normalized or invented.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6

CONTRACT = "songsterr-fresh-v6-innovation-line-bridge-synthetic-research-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_FRAME_SAMPLES = 2048
EXPECTED_FFT_SIZE = 8192
HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS = 2


class InnovationLineBridgeError(RuntimeError):
    pass


def _frozen_geometry() -> tuple[int, int, int, int]:
    if (
        getattr(frozen_v6, "CONTRACT", None) != EXPECTED_V6_CONTRACT
        or getattr(frozen_v6, "VERSION", None) != EXPECTED_V6_VERSION
    ):
        raise InnovationLineBridgeError("FROZEN_V6_CONTRACT_MISMATCH")

    frame_samples = int(getattr(frozen_v6, "FRAME_SAMPLES", -1))
    fft_size = int(getattr(frozen_v6, "FFT_SIZE", -1))
    if frame_samples != EXPECTED_FRAME_SAMPLES or fft_size != EXPECTED_FFT_SIZE:
        raise InnovationLineBridgeError("FROZEN_V6_GEOMETRY_MISMATCH")
    if fft_size % frame_samples != 0:
        raise InnovationLineBridgeError("NONINTEGER_ZERO_PADDING_FACTOR")

    zero_padding_factor = fft_size // frame_samples
    radius = HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS * zero_padding_factor
    if zero_padding_factor != 4 or radius != 8:
        raise InnovationLineBridgeError("UNEXPECTED_FROZEN_HANN_GEOMETRY")
    return frame_samples, fft_size, zero_padding_factor, radius


FRAME_SAMPLES, FFT_SIZE, ZERO_PADDING_FACTOR, LINE_SUPPRESSION_RADIUS_BINS = _frozen_geometry()
EXPECTED_VECTOR_LENGTH = FFT_SIZE // 2 + 1


def _validated_innovation(innovation: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(innovation, dtype=np.float64)
    except Exception as exc:
        raise InnovationLineBridgeError(f"INNOVATION_COERCION_FAILED:{type(exc).__name__}") from exc

    if values.ndim != 1:
        raise InnovationLineBridgeError("INNOVATION_MUST_BE_ONE_DIMENSIONAL")
    if values.size != EXPECTED_VECTOR_LENGTH:
        raise InnovationLineBridgeError(
            f"INNOVATION_LENGTH_MISMATCH:{values.size}!={EXPECTED_VECTOR_LENGTH}"
        )
    if not np.all(np.isfinite(values)):
        raise InnovationLineBridgeError("INNOVATION_MUST_BE_FINITE")
    if np.any(values < 0.0):
        raise InnovationLineBridgeError("INNOVATION_MUST_BE_NONNEGATIVE")
    return values


def collapse_hann_main_lobes(innovation: np.ndarray | list[float]) -> np.ndarray:
    """Return deterministic local-max line evidence on the frozen FFT grid.

    A positive bin survives only when it is the first occurrence of the maximum
    value in its clipped +/-8-bin neighborhood. Surviving amplitudes are copied
    exactly from the input; every other output bin is zero.
    """

    values = _validated_innovation(innovation)
    output = np.zeros_like(values, dtype=np.float64)
    radius = LINE_SUPPRESSION_RADIUS_BINS

    positive_indices = np.flatnonzero(values > 0.0)
    for index_value in positive_indices:
        index = int(index_value)
        left = max(0, index - radius)
        right = min(values.size, index + radius + 1)
        neighborhood = values[left:right]
        local_offset = int(np.argmax(neighborhood))
        local_index = left + local_offset
        if local_index == index:
            output[index] = values[index]

    return output


def bridge_diagnostics(
    innovation: np.ndarray | list[float],
) -> dict[str, Any]:
    """Pure in-memory diagnostics for synthetic tests; no pitch decision."""

    values = _validated_innovation(innovation)
    bridged = collapse_hann_main_lobes(values)
    retained = np.flatnonzero(bridged > 0.0)
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "frameSamples": FRAME_SAMPLES,
        "fftSize": FFT_SIZE,
        "zeroPaddingFactor": ZERO_PADDING_FACTOR,
        "hannFirstNullNativeHalfWidthBins": HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS,
        "lineSuppressionRadiusBins": LINE_SUPPRESSION_RADIUS_BINS,
        "inputLength": int(values.size),
        "inputPositiveBinCount": int(np.count_nonzero(values > 0.0)),
        "retainedPositiveBinCount": int(retained.size),
        "retainedBins": [int(value) for value in retained],
        "inputNorm": float(np.linalg.norm(values)),
        "outputNorm": float(np.linalg.norm(bridged)),
        "amplitudeBoosted": bool(np.any(bridged > values)),
    }
