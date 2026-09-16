#!/usr/bin/env python3
"""Synthetic-only V6 innovation peak-band representation bridge iteration 2.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE_ITERATION2.md

Local-max centers are separated with the geometry-derived Hann leakage radius,
then the exact original amplitudes in the frozen V3 +/-1 peak-support band are
retained. No energy is invented, boosted, shifted, interpolated or normalized.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6
import physical_template_plausibility_v3 as frozen_v3

CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
VERSION = 2

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_V3_VERSION = 1
EXPECTED_FRAME_SAMPLES = 2048
EXPECTED_FFT_SIZE = 8192
HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS = 2


class InnovationPeakBandBridgeError(RuntimeError):
    pass


def _frozen_geometry() -> tuple[int, int, int, int, int]:
    if (
        getattr(frozen_v6, "CONTRACT", None) != EXPECTED_V6_CONTRACT
        or getattr(frozen_v6, "VERSION", None) != EXPECTED_V6_VERSION
    ):
        raise InnovationPeakBandBridgeError("FROZEN_V6_CONTRACT_MISMATCH")
    if (
        getattr(frozen_v3, "CONTRACT", None) != EXPECTED_V3_CONTRACT
        or getattr(frozen_v3, "VERSION", None) != EXPECTED_V3_VERSION
    ):
        raise InnovationPeakBandBridgeError("FROZEN_V3_CONTRACT_MISMATCH")

    frame_samples = int(getattr(frozen_v6, "FRAME_SAMPLES", -1))
    fft_size = int(getattr(frozen_v6, "FFT_SIZE", -1))
    peak_radius = int(getattr(frozen_v3, "PEAK_BIN_RADIUS", -1))
    if frame_samples != EXPECTED_FRAME_SAMPLES or fft_size != EXPECTED_FFT_SIZE:
        raise InnovationPeakBandBridgeError("FROZEN_V6_GEOMETRY_MISMATCH")
    if peak_radius != 1:
        raise InnovationPeakBandBridgeError("FROZEN_V3_PEAK_RADIUS_MISMATCH")
    if fft_size % frame_samples != 0:
        raise InnovationPeakBandBridgeError("NONINTEGER_ZERO_PADDING_FACTOR")

    zero_padding_factor = fft_size // frame_samples
    suppression_radius = HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS * zero_padding_factor
    if zero_padding_factor != 4 or suppression_radius != 8:
        raise InnovationPeakBandBridgeError("UNEXPECTED_FROZEN_HANN_GEOMETRY")
    return frame_samples, fft_size, zero_padding_factor, suppression_radius, peak_radius


(
    FRAME_SAMPLES,
    FFT_SIZE,
    ZERO_PADDING_FACTOR,
    LINE_SUPPRESSION_RADIUS_BINS,
    PEAK_BAND_RADIUS_BINS,
) = _frozen_geometry()
EXPECTED_VECTOR_LENGTH = FFT_SIZE // 2 + 1


def _validated_innovation(innovation: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(innovation, dtype=np.float64)
    except Exception as exc:
        raise InnovationPeakBandBridgeError(
            f"INNOVATION_COERCION_FAILED:{type(exc).__name__}"
        ) from exc

    if values.ndim != 1:
        raise InnovationPeakBandBridgeError("INNOVATION_MUST_BE_ONE_DIMENSIONAL")
    if values.size != EXPECTED_VECTOR_LENGTH:
        raise InnovationPeakBandBridgeError(
            f"INNOVATION_LENGTH_MISMATCH:{values.size}!={EXPECTED_VECTOR_LENGTH}"
        )
    if not np.all(np.isfinite(values)):
        raise InnovationPeakBandBridgeError("INNOVATION_MUST_BE_FINITE")
    if np.any(values < 0.0):
        raise InnovationPeakBandBridgeError("INNOVATION_MUST_BE_NONNEGATIVE")
    return values


def _retained_centers(values: np.ndarray) -> list[int]:
    centers: list[int] = []
    radius = LINE_SUPPRESSION_RADIUS_BINS
    for index_value in np.flatnonzero(values > 0.0):
        index = int(index_value)
        left = max(0, index - radius)
        right = min(values.size, index + radius + 1)
        neighborhood = values[left:right]
        if left + int(np.argmax(neighborhood)) == index:
            centers.append(index)
    return centers


def collapse_hann_lobes_to_peak_bands(
    innovation: np.ndarray | list[float],
) -> np.ndarray:
    """Retain exact input amplitudes in +/-1 bands around deterministic centers."""

    values = _validated_innovation(innovation)
    output = np.zeros_like(values, dtype=np.float64)
    for center in _retained_centers(values):
        left = max(0, center - PEAK_BAND_RADIUS_BINS)
        right = min(values.size, center + PEAK_BAND_RADIUS_BINS + 1)
        output[left:right] = values[left:right]
    return output


def bridge_diagnostics(innovation: np.ndarray | list[float]) -> dict[str, Any]:
    values = _validated_innovation(innovation)
    centers = _retained_centers(values)
    bridged = collapse_hann_lobes_to_peak_bands(values)
    retained = np.flatnonzero(bridged > 0.0)
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "frameSamples": FRAME_SAMPLES,
        "fftSize": FFT_SIZE,
        "zeroPaddingFactor": ZERO_PADDING_FACTOR,
        "hannFirstNullNativeHalfWidthBins": HANN_FIRST_NULL_NATIVE_HALF_WIDTH_BINS,
        "lineSuppressionRadiusBins": LINE_SUPPRESSION_RADIUS_BINS,
        "peakBandRadiusBins": PEAK_BAND_RADIUS_BINS,
        "inputLength": int(values.size),
        "centerCount": len(centers),
        "centers": centers,
        "inputPositiveBinCount": int(np.count_nonzero(values > 0.0)),
        "retainedPositiveBinCount": int(retained.size),
        "retainedBins": [int(value) for value in retained],
        "inputNorm": float(np.linalg.norm(values)),
        "outputNorm": float(np.linalg.norm(bridged)),
        "amplitudeBoosted": bool(np.any(bridged > values)),
    }
