#!/usr/bin/env python3
"""Prospectively frozen synthetic-only physical-template plausibility research V3.

This module is intentionally isolated from the frozen V6 classifier. It accepts
only in-memory innovation spectra on the frozen FFT grid. It exposes no audio,
model, network, subprocess, workflow, dataset, or repository-file loading path.

Frozen research contract:
  docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
VERSION = 1

SAMPLE_RATE = 44100
FFT_SIZE = 8192
PLAYABLE_MIDI_MIN = 40
PLAYABLE_MIDI_MAX = 88
HARMONIC_COUNT_MAX = 6
DETUNE_CENTS = tuple(float(value) for value in range(-40, 41, 5))
PEAK_BIN_RADIUS = 1
BACKGROUND_BIN_RADIUS = 6
LOCAL_SNR_MULTIPLIER = 3.0
RELATIVE_HARMONIC_SUPPORT_FLOOR = 0.10
MIN_SUPPORTED_HARMONICS = 3
MIN_WEIGHTED_HARMONIC_COVERAGE = 0.35
MIN_INNOVATION_NORM = 1e-6
NECESSITY_FRACTION_MIN = 0.01


def midi_to_hz(midi: float) -> float:
    return 440.0 * (2.0 ** ((float(midi) - 69.0) / 12.0))


def expected_frequencies() -> np.ndarray:
    return np.fft.rfftfreq(FFT_SIZE, d=1.0 / float(SAMPLE_RATE))


def _invalid(status: str, **diagnostics: Any) -> dict[str, Any]:
    row: dict[str, Any] = {"valid": False, "status": status}
    row.update(diagnostics)
    return row


def _validated_spectrum(
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> tuple[np.ndarray | None, np.ndarray | None, dict[str, Any] | None]:
    try:
        values = np.asarray(innovation, dtype=np.float64)
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        return None, None, _invalid("INPUT_COERCION_FAILED", errorType=type(exc).__name__)

    if values.ndim != 1 or hz.ndim != 1:
        return None, None, _invalid("SPECTRUM_AND_FREQUENCIES_MUST_BE_1D")
    if values.shape != hz.shape:
        return None, None, _invalid("SPECTRUM_FREQUENCY_SHAPE_MISMATCH")
    expected = expected_frequencies()
    if values.size != expected.size:
        return None, None, _invalid(
            "FREQUENCY_GRID_MISSING_BINS",
            expectedBins=int(expected.size),
            observedBins=int(values.size),
        )
    if not np.all(np.isfinite(values)) or not np.all(np.isfinite(hz)):
        return None, None, _invalid("NONFINITE_SPECTRUM_OR_FREQUENCY")
    if np.any(values < 0.0):
        return None, None, _invalid("NEGATIVE_INNOVATION_NOT_ALLOWED")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        return None, None, _invalid("FREQUENCY_GRID_MISMATCH")

    innovation_norm = float(np.linalg.norm(values))
    if not math.isfinite(innovation_norm) or innovation_norm < MIN_INNOVATION_NORM:
        return None, None, _invalid(
            "INSUFFICIENT_INNOVATION",
            innovationNorm=innovation_norm,
        )
    return values, hz, None


def _anchor_observation(
    midi: int,
    cents: float,
    innovation: np.ndarray,
    frequencies: np.ndarray,
) -> dict[str, Any]:
    fundamental_hz = midi_to_hz(float(midi) + float(cents) / 100.0)
    bins: list[int] = []
    peaks: list[float] = []
    backgrounds: list[float] = []
    harmonic_orders: list[int] = []

    for harmonic in range(1, HARMONIC_COUNT_MAX + 1):
        target_hz = float(harmonic) * fundamental_hz
        if target_hz >= SAMPLE_RATE / 2.0:
            break
        position = target_hz * float(FFT_SIZE) / float(SAMPLE_RATE)
        nearest = int(math.floor(position + 0.5))
        nearest = max(0, min(int(innovation.size - 1), nearest))

        peak_left = max(0, nearest - PEAK_BIN_RADIUS)
        peak_right = min(int(innovation.size - 1), nearest + PEAK_BIN_RADIUS)
        peak_window = innovation[peak_left : peak_right + 1]
        if peak_window.size == 0:
            return _invalid("EMPTY_HARMONIC_PEAK_WINDOW", cents=float(cents), harmonic=harmonic)
        chosen = int(peak_left + int(np.argmax(peak_window)))
        peak = float(innovation[chosen])

        background_left = max(0, nearest - BACKGROUND_BIN_RADIUS)
        background_right = min(int(innovation.size - 1), nearest + BACKGROUND_BIN_RADIUS)
        background_indices = [
            index
            for index in range(background_left, background_right + 1)
            if index < peak_left or index > peak_right
        ]
        if not background_indices:
            return _invalid("NO_LOCAL_BACKGROUND_BINS", cents=float(cents), harmonic=harmonic)
        background_values = innovation[np.asarray(background_indices, dtype=np.int64)]
        if background_values.size == 0 or not np.all(np.isfinite(background_values)):
            return _invalid("INVALID_LOCAL_BACKGROUND", cents=float(cents), harmonic=harmonic)
        background = float(np.median(background_values))

        harmonic_orders.append(harmonic)
        bins.append(chosen)
        peaks.append(peak)
        backgrounds.append(background)

    if len(harmonic_orders) < MIN_SUPPORTED_HARMONICS:
        return _invalid(
            "FEWER_THAN_THREE_AVAILABLE_HARMONICS",
            cents=float(cents),
            availableHarmonics=len(harmonic_orders),
        )
    if not all(math.isfinite(value) and value >= 0.0 for value in peaks + backgrounds):
        return _invalid("NONFINITE_HARMONIC_OBSERVATION", cents=float(cents))

    strongest = max(peaks)
    if not math.isfinite(strongest) or strongest <= 0.0:
        return _invalid("NO_POSITIVE_HARMONIC_SUPPORT", cents=float(cents))
    eps = max(strongest * 1e-12, 1e-15)

    supported: list[bool] = []
    support_thresholds: list[float] = []
    for peak, background in zip(peaks, backgrounds):
        threshold = max(
            LOCAL_SNR_MULTIPLIER * background,
            RELATIVE_HARMONIC_SUPPORT_FLOOR * strongest,
            eps,
        )
        support_thresholds.append(float(threshold))
        supported.append(bool(peak >= threshold))

    raw_weights = [1.0 / float(harmonic) for harmonic in harmonic_orders]
    total_weight = float(sum(raw_weights))
    supported_weight = float(
        sum(weight for weight, is_supported in zip(raw_weights, supported) if is_supported)
    )
    weighted_coverage = supported_weight / total_weight if total_weight > 0.0 else 0.0
    supported_count = int(sum(1 for value in supported if value))
    weighted_strength = float(
        sum(weight * (peak / strongest) for weight, peak in zip(raw_weights, peaks)) / total_weight
    )

    eligible = bool(
        supported_count >= MIN_SUPPORTED_HARMONICS
        and weighted_coverage >= MIN_WEIGHTED_HARMONIC_COVERAGE
    )
    return {
        "valid": eligible,
        "status": "ELIGIBLE" if eligible else "INSUFFICIENT_MULTI_HARMONIC_SUPPORT",
        "midi": int(midi),
        "cents": float(cents),
        "fundamentalHz": float(fundamental_hz),
        "harmonicOrders": harmonic_orders,
        "bins": bins,
        "observedHarmonicInnovation": peaks,
        "localBackground": backgrounds,
        "supportThresholds": support_thresholds,
        "supported": supported,
        "supportedHarmonicCount": supported_count,
        "weightedHarmonicCoverage": float(weighted_coverage),
        "weightedNormalizedStrength": weighted_strength,
        "fundamentalToMaxHarmonicInnovationRatioDiagnostic": float(peaks[0] / strongest),
    }


def evaluate_candidate_template(
    midi: int,
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    if isinstance(midi, bool) or not isinstance(midi, (int, np.integer)):
        return _invalid("MIDI_INTEGER_REQUIRED")
    midi = int(midi)
    if not PLAYABLE_MIDI_MIN <= midi <= PLAYABLE_MIDI_MAX:
        return _invalid("MIDI_OUTSIDE_PLAYABLE_RANGE", midi=midi)

    values, hz, error = _validated_spectrum(innovation, frequencies)
    if error is not None:
        error["midi"] = midi
        return error
    assert values is not None and hz is not None

    anchors = [_anchor_observation(midi, cents, values, hz) for cents in DETUNE_CENTS]
    eligible = [row for row in anchors if row.get("valid") is True]
    if not eligible:
        statuses: dict[str, int] = {}
        for row in anchors:
            status = str(row.get("status", "UNKNOWN"))
            statuses[status] = statuses.get(status, 0) + 1
        return _invalid(
            "NO_ELIGIBLE_DETUNING_ANCHOR",
            midi=midi,
            anchorStatusCounts=statuses,
        )

    def selection_key(row: dict[str, Any]) -> tuple[float, int, float, float, float]:
        cents = float(row["cents"])
        return (
            float(row["weightedHarmonicCoverage"]),
            int(row["supportedHarmonicCount"]),
            float(row["weightedNormalizedStrength"]),
            -abs(cents),
            -cents,
        )

    chosen = max(eligible, key=selection_key)
    raw_weights = np.asarray(
        [1.0 / float(harmonic) for harmonic in chosen["harmonicOrders"]],
        dtype=np.float64,
    )
    norm = float(np.linalg.norm(raw_weights))
    if not math.isfinite(norm) or norm <= 0.0:
        return _invalid("INVALID_TEMPLATE_NORM", midi=midi)

    return {
        "valid": True,
        "status": "ELIGIBLE",
        "midi": midi,
        "cents": float(chosen["cents"]),
        "fundamentalHz": float(chosen["fundamentalHz"]),
        "harmonicOrders": list(chosen["harmonicOrders"]),
        "bins": list(chosen["bins"]),
        "weights": [float(value / norm) for value in raw_weights],
        "observedHarmonicInnovation": list(chosen["observedHarmonicInnovation"]),
        "localBackground": list(chosen["localBackground"]),
        "supportThresholds": list(chosen["supportThresholds"]),
        "supported": list(chosen["supported"]),
        "supportedHarmonicCount": int(chosen["supportedHarmonicCount"]),
        "weightedHarmonicCoverage": float(chosen["weightedHarmonicCoverage"]),
        "weightedNormalizedStrength": float(chosen["weightedNormalizedStrength"]),
        "fundamentalToMaxHarmonicInnovationRatioDiagnostic": float(
            chosen["fundamentalToMaxHarmonicInnovationRatioDiagnostic"]
        ),
    }


def evaluate_composite_necessity(
    selected_midi: int,
    innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        return {"passed": False, "status": "MIDI_INTEGER_REQUIRED"}
    selected_midi = int(selected_midi)
    if not PLAYABLE_MIDI_MIN <= selected_midi <= PLAYABLE_MIDI_MAX:
        return {"passed": False, "status": "MIDI_OUTSIDE_PLAYABLE_RANGE", "selectedMidi": selected_midi}

    values, hz, error = _validated_spectrum(innovation, frequencies)
    if error is not None:
        return {
            "passed": False,
            "status": error["status"],
            "selectedMidi": selected_midi,
            "input": error,
        }
    assert values is not None and hz is not None

    templates = {
        midi: evaluate_candidate_template(midi, values, hz)
        for midi in range(PLAYABLE_MIDI_MIN, PLAYABLE_MIDI_MAX + 1)
    }
    valid_midis = sorted(midi for midi, row in templates.items() if row.get("valid") is True)
    selected_template = templates[selected_midi]
    if selected_midi not in valid_midis:
        return {
            "passed": False,
            "status": "SELECTED_TEMPLATE_INELIGIBLE",
            "selectedMidi": selected_midi,
            "selectedTemplate": selected_template,
            "validCandidateCount": len(valid_midis),
        }

    feature_bins = sorted(
        {bin_index for midi in valid_midis for bin_index in templates[midi]["bins"]}
    )
    if not feature_bins:
        return {"passed": False, "status": "NO_FEATURE_BINS", "selectedMidi": selected_midi}
    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([values[index] for index in feature_bins], dtype=np.float64)
    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < MIN_INNOVATION_NORM:
        return {
            "passed": False,
            "status": "INSUFFICIENT_FEATURE_ENERGY",
            "selectedMidi": selected_midi,
            "featureEnergy": feature_energy,
        }

    dictionary = np.zeros((len(feature_bins), len(valid_midis)), dtype=np.float64)
    for column, midi in enumerate(valid_midis):
        template = templates[midi]
        for bin_index, weight in zip(template["bins"], template["weights"]):
            dictionary[row_for_bin[int(bin_index)], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {
            "passed": False,
            "status": "NNLS_FULL_FAILED",
            "selectedMidi": selected_midi,
            "errorType": type(exc).__name__,
        }

    selected_column = valid_midis.index(selected_midi)
    reduced = np.delete(dictionary, selected_column, axis=1)
    if reduced.shape[1] == 0:
        return {"passed": False, "status": "REDUCED_DICTIONARY_EMPTY", "selectedMidi": selected_midi}
    try:
        _without_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {
            "passed": False,
            "status": "NNLS_REDUCED_FAILED",
            "selectedMidi": selected_midi,
            "errorType": type(exc).__name__,
        }

    selected_coefficient = float(coefficients[selected_column])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float(
        (without_residual - full_residual) / max(feature_energy, 1e-15)
    )
    if not all(
        math.isfinite(value)
        for value in (selected_coefficient, full_residual, without_residual, necessity_fraction)
    ):
        return {"passed": False, "status": "NONFINITE_FIT", "selectedMidi": selected_midi}

    passed = bool(
        selected_coefficient > 0.0
        and necessity_fraction >= NECESSITY_FRACTION_MIN
    )
    return {
        "passed": passed,
        "status": "PASS" if passed else "FAIL_NECESSITY",
        "selectedMidi": selected_midi,
        "validCandidateCount": len(valid_midis),
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "featureEnergy": feature_energy,
        "necessityFraction": necessity_fraction,
        "selectedTemplate": selected_template,
    }
