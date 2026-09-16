#!/usr/bin/env python3
"""Synthetic-only temporal/support diagnostic for the V7 representation seam.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REATTACK_TEMPORAL_SUPPORT_DIAGNOSTIC_PRE.md

This module defines no successor classification. It traces frozen V6 complex
prediction deviation through raw onset innovation, the frozen bridge-V2
representation and frozen V3 selected-MIDI anchor support semantics.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge

CONTRACT = "songsterr-fresh-v7-reattack-temporal-support-diagnostic-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_V3_VERSION = 1
EXPECTED_BRIDGE_CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
EXPECTED_BRIDGE_VERSION = 2


class ReattackTemporalSupportDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(v3, "CONTRACT", None) == EXPECTED_V3_CONTRACT
        and getattr(v3, "VERSION", None) == EXPECTED_V3_VERSION
        and getattr(bridge, "CONTRACT", None) == EXPECTED_BRIDGE_CONTRACT
        and getattr(bridge, "VERSION", None) == EXPECTED_BRIDGE_VERSION
    )


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise ReattackTemporalSupportDiagnosticError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = v3.expected_frequencies()
    if values.ndim != 1 or values.shape != expected.shape:
        raise ReattackTemporalSupportDiagnosticError("FREQUENCY_GRID_SHAPE_MISMATCH")
    if not np.all(np.isfinite(values)):
        raise ReattackTemporalSupportDiagnosticError("NONFINITE_FREQUENCY_GRID")
    if not np.allclose(values, expected, rtol=0.0, atol=1e-12):
        raise ReattackTemporalSupportDiagnosticError("FREQUENCY_GRID_MISMATCH")
    return values


def _frame_rms(audio: np.ndarray, onset_sample: int) -> list[float]:
    rows: list[float] = []
    for end_offset in v6.FRAME_END_OFFSETS:
        stop = int(onset_sample) + int(end_offset)
        frame = np.asarray(audio[stop - v6.FRAME_SAMPLES : stop], dtype=np.float64)
        demeaned = frame - float(np.mean(frame))
        value = float(np.sqrt(np.mean(np.square(demeaned))))
        if not math.isfinite(value):
            raise ReattackTemporalSupportDiagnosticError("NONFINITE_FRAME_RMS")
        rows.append(value)
    return rows


def _nearest_center(centers: list[int], bin_index: int) -> tuple[int | None, int | None]:
    if not centers:
        return None, None
    chosen = min(centers, key=lambda center: (abs(int(center) - int(bin_index)), int(center)))
    return int(chosen), int(chosen) - int(bin_index)


def _strongest_suppression_center(
    centers: list[int],
    raw_innovation: np.ndarray,
    bin_index: int,
) -> tuple[int | None, float | None]:
    radius = int(bridge.LINE_SUPPRESSION_RADIUS_BINS)
    eligible = [center for center in centers if abs(int(center) - int(bin_index)) <= radius]
    if not eligible:
        return None, None
    chosen = max(eligible, key=lambda center: (float(raw_innovation[int(center)]), -int(center)))
    return int(chosen), float(raw_innovation[int(chosen)])


def _anchor_trace(
    selected_midi: int,
    cents: float,
    raw_innovation: np.ndarray,
    bridged: np.ndarray,
    deviation: np.ndarray,
    pre_indices: np.ndarray,
    post_indices: np.ndarray,
    centers: list[int],
    retained_bins: set[int],
) -> dict[str, Any]:
    fundamental_hz = v3.midi_to_hz(float(selected_midi) + float(cents) / 100.0)
    harmonic_rows: list[dict[str, Any]] = []

    for harmonic in range(1, v3.HARMONIC_COUNT_MAX + 1):
        target_hz = float(harmonic) * fundamental_hz
        if target_hz >= v3.SAMPLE_RATE / 2.0:
            break
        position = target_hz * float(v3.FFT_SIZE) / float(v3.SAMPLE_RATE)
        nearest = int(math.floor(position + 0.5))
        nearest = max(0, min(int(raw_innovation.size - 1), nearest))

        peak_left = max(0, nearest - int(v3.PEAK_BIN_RADIUS))
        peak_right = min(int(raw_innovation.size - 1), nearest + int(v3.PEAK_BIN_RADIUS))
        raw_window = raw_innovation[peak_left : peak_right + 1]
        bridged_window = bridged[peak_left : peak_right + 1]
        raw_peak_bin = int(peak_left + int(np.argmax(raw_window)))
        bridged_peak_bin = int(peak_left + int(np.argmax(bridged_window)))
        raw_peak_value = float(raw_innovation[raw_peak_bin])
        bridged_peak_value = float(bridged[bridged_peak_bin])

        background_left = max(0, nearest - int(v3.BACKGROUND_BIN_RADIUS))
        background_right = min(int(bridged.size - 1), nearest + int(v3.BACKGROUND_BIN_RADIUS))
        background_indices = [
            index
            for index in range(background_left, background_right + 1)
            if index < peak_left or index > peak_right
        ]
        if not background_indices:
            raise ReattackTemporalSupportDiagnosticError("NO_LOCAL_BACKGROUND_BINS")
        background = float(
            np.median(bridged[np.asarray(background_indices, dtype=np.int64)])
        )

        pre_peak_deviation = float(
            np.max(deviation[np.ix_(pre_indices, np.arange(peak_left, peak_right + 1))])
        )
        post_peak_deviation = float(
            np.max(deviation[np.ix_(post_indices, np.arange(peak_left, peak_right + 1))])
        )
        nearest_center, signed_distance = _nearest_center(centers, raw_peak_bin)
        suppression_center, suppression_value = _strongest_suppression_center(
            centers,
            raw_innovation,
            raw_peak_bin,
        )

        harmonic_rows.append(
            {
                "harmonic": int(harmonic),
                "targetHz": float(target_hz),
                "nearestBin": int(nearest),
                "peakLeft": int(peak_left),
                "peakRight": int(peak_right),
                "rawPeakBin": raw_peak_bin,
                "rawPeakValue": raw_peak_value,
                "bridgedPeakBin": bridged_peak_bin,
                "bridgedPeakValue": bridged_peak_value,
                "backgroundLeft": int(background_left),
                "backgroundRight": int(background_right),
                "backgroundBinCount": len(background_indices),
                "bridgedMedianBackground": background,
                "prePeakDeviationMax": pre_peak_deviation,
                "postPeakDeviationMax": post_peak_deviation,
                "rawInnovationAtRawPeakBin": float(raw_innovation[raw_peak_bin]),
                "nearestRetainedCenter": nearest_center,
                "nearestRetainedCenterSignedDistanceBins": signed_distance,
                "nearestRetainedCenterAbsoluteDistanceBins": (
                    abs(int(signed_distance)) if signed_distance is not None else None
                ),
                "rawPeakBinSurvivesRetainedBand": bool(raw_peak_bin in retained_bins),
                "strongestCenterWithinSuppressionRadius": suppression_center,
                "strongestCenterWithinSuppressionRadiusRawInnovation": suppression_value,
            }
        )

    if len(harmonic_rows) < v3.MIN_SUPPORTED_HARMONICS:
        return {
            "cents": float(cents),
            "status": "FEWER_THAN_THREE_AVAILABLE_HARMONICS",
            "valid": False,
            "harmonics": harmonic_rows,
        }

    bridged_peaks = [float(row["bridgedPeakValue"]) for row in harmonic_rows]
    strongest = max(bridged_peaks)
    eps = max(strongest * 1e-12, 1e-15)
    supported: list[bool] = []
    thresholds: list[float] = []
    for row in harmonic_rows:
        threshold = max(
            float(v3.LOCAL_SNR_MULTIPLIER) * float(row["bridgedMedianBackground"]),
            float(v3.RELATIVE_HARMONIC_SUPPORT_FLOOR) * strongest,
            eps,
        )
        is_supported = bool(float(row["bridgedPeakValue"]) >= threshold)
        row["supportThreshold"] = float(threshold)
        row["supported"] = is_supported
        thresholds.append(float(threshold))
        supported.append(is_supported)

    raw_weights = [1.0 / float(row["harmonic"]) for row in harmonic_rows]
    total_weight = float(sum(raw_weights))
    supported_weight = float(
        sum(weight for weight, flag in zip(raw_weights, supported) if flag)
    )
    weighted_coverage = supported_weight / total_weight if total_weight > 0.0 else 0.0
    supported_count = int(sum(1 for flag in supported if flag))
    weighted_strength = float(
        sum(
            weight * (float(row["bridgedPeakValue"]) / strongest)
            for weight, row in zip(raw_weights, harmonic_rows)
        )
        / total_weight
    ) if strongest > 0.0 and total_weight > 0.0 else 0.0
    valid = bool(
        supported_count >= int(v3.MIN_SUPPORTED_HARMONICS)
        and weighted_coverage >= float(v3.MIN_WEIGHTED_HARMONIC_COVERAGE)
    )

    return {
        "cents": float(cents),
        "fundamentalHz": float(fundamental_hz),
        "valid": valid,
        "status": "ELIGIBLE" if valid else "INSUFFICIENT_MULTI_HARMONIC_SUPPORT",
        "supportedHarmonicCount": supported_count,
        "weightedHarmonicCoverage": float(weighted_coverage),
        "weightedNormalizedStrength": weighted_strength,
        "fundamentalToMaxHarmonicInnovationRatioDiagnostic": (
            float(bridged_peaks[0] / strongest) if strongest > 0.0 else 0.0
        ),
        "rawPeakSurvivalCount": int(
            sum(1 for row in harmonic_rows if row["rawPeakBinSurvivesRetainedBand"] is True)
        ),
        "harmonics": harmonic_rows,
    }


def evaluate_temporal_support_diagnostic(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return a deterministic trace with no successor decision."""

    if not _contracts_ok():
        raise ReattackTemporalSupportDiagnosticError("FROZEN_CONTRACT_MISMATCH")
    hz = _validated_frequencies(frequencies)
    values = np.asarray(audio, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ReattackTemporalSupportDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise ReattackTemporalSupportDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise ReattackTemporalSupportDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)

    historical = v6.classify_audio_event(values, onset_sample, selected_midi)
    base: dict[str, Any] = {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "frozenV6HistoricalClassification": historical.get("classification"),
        "frozenV6HistoricalReason": historical.get("reason"),
    }

    try:
        onset = v6._onset_innovation_spectrum(values, onset_sample)
    except v6.CorroborationError as exc:
        return {
            **base,
            "onsetAvailable": False,
            "onsetStatus": "CONTEXT_ERROR",
            "onsetReason": str(exc),
            "frameEndOffsets": list(v6.FRAME_END_OFFSETS),
            "frameRms": [],
            "frameDeviationNorms": [],
            "anchorTraces": [],
            "selectedTemplate": None,
            "bridgeDiagnostics": None,
        }

    if onset.get("status") != "OK":
        return {
            **base,
            "onsetAvailable": False,
            "onsetStatus": onset.get("status"),
            "onsetReason": onset.get("status"),
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "frameEndOffsets": list(v6.FRAME_END_OFFSETS),
            "frameRms": [],
            "frameDeviationNorms": [],
            "anchorTraces": [],
            "selectedTemplate": None,
            "bridgeDiagnostics": None,
        }

    spectra, offsets = v6._frame_complex_spectra(values, onset_sample)
    deviation = v6._complex_prediction_deviation(spectra)
    raw_innovation = np.asarray(onset["innovation"], dtype=np.float64)
    bridged = bridge.collapse_hann_lobes_to_peak_bands(raw_innovation)
    bridge_diag = bridge.bridge_diagnostics(raw_innovation)
    centers = [int(value) for value in bridge_diag["centers"]]
    retained_bins = {int(value) for value in bridge_diag["retainedBins"]}

    indices = np.arange(offsets.size, dtype=np.int64)
    pre_indices = indices[(offsets <= 0) & (indices >= 2)]
    post_indices = indices[(offsets > 0) & (offsets <= v6.POST_END_MAX)]
    if pre_indices.size == 0 or post_indices.size == 0:
        raise ReattackTemporalSupportDiagnosticError("PRE_POST_INDICES_REQUIRED")

    frame_rms = _frame_rms(values, onset_sample)
    deviation_norms = [float(np.linalg.norm(row)) for row in deviation]
    if not all(math.isfinite(value) for value in frame_rms + deviation_norms):
        raise ReattackTemporalSupportDiagnosticError("NONFINITE_TEMPORAL_DIAGNOSTIC")

    anchor_traces = [
        _anchor_trace(
            selected_midi,
            float(cents),
            raw_innovation,
            bridged,
            deviation,
            pre_indices,
            post_indices,
            centers,
            retained_bins,
        )
        for cents in v3.DETUNE_CENTS
    ]
    selected_template = v3.evaluate_candidate_template(selected_midi, bridged, hz)

    return {
        **base,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "rawInnovationNorm": float(np.linalg.norm(raw_innovation)),
        "bridgedInnovationNorm": float(np.linalg.norm(bridged)),
        "frameEndOffsets": [int(value) for value in offsets],
        "frameRms": frame_rms,
        "frameDeviationNorms": deviation_norms,
        "preFrameIndices": [int(value) for value in pre_indices],
        "postFrameIndices": [int(value) for value in post_indices],
        "bridgeDiagnostics": bridge_diag,
        "anchorTraces": anchor_traces,
        "selectedTemplate": selected_template,
    }
