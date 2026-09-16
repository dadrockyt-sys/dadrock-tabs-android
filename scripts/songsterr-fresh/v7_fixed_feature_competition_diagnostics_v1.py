#!/usr/bin/env python3
"""Synthetic-only fixed-feature candidate competition diagnostics.

Prospectively frozen by
SONGSTERR_FRESH_V7_FIXED_FEATURE_COMPETITION_DIAGNOSTIC_PRE.md.

The all-gate-free template union defines one raw observation feature universe.
Compared candidate populations change dictionary columns only; feature rows stay
fixed. No successor classifier or threshold is defined here.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge
import v7_gate_free_competition_diagnostics_v1 as gatefree

CONTRACT = "songsterr-fresh-v7-fixed-feature-competition-diagnostic-v1"
VERSION = 1
EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_V3_VERSION = 1
EXPECTED_BRIDGE_CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
EXPECTED_BRIDGE_VERSION = 2
EXPECTED_GATEFREE_CONTRACT = "songsterr-fresh-v7-gate-free-competition-diagnostic-v1"
EXPECTED_GATEFREE_VERSION = 1


class FixedFeatureCompetitionDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(v3, "CONTRACT", None) == EXPECTED_V3_CONTRACT
        and getattr(v3, "VERSION", None) == EXPECTED_V3_VERSION
        and getattr(bridge, "CONTRACT", None) == EXPECTED_BRIDGE_CONTRACT
        and getattr(bridge, "VERSION", None) == EXPECTED_BRIDGE_VERSION
        and getattr(gatefree, "CONTRACT", None) == EXPECTED_GATEFREE_CONTRACT
        and getattr(gatefree, "VERSION", None) == EXPECTED_GATEFREE_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
    )


def _finite_audio(audio: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise FixedFeatureCompetitionDiagnosticError(
            f"AUDIO_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise FixedFeatureCompetitionDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")
    return values


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise FixedFeatureCompetitionDiagnosticError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise FixedFeatureCompetitionDiagnosticError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise FixedFeatureCompetitionDiagnosticError("FREQUENCY_GRID_MISMATCH")
    if not np.allclose(hz, v3.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise FixedFeatureCompetitionDiagnosticError("V6_V3_FREQUENCY_GRID_MISMATCH")
    return hz


def _fit_on_fixed_feature_universe(
    selected_midi: int,
    raw: np.ndarray,
    templates: dict[int, dict[str, Any]],
    fixed_feature_bins: list[int],
    candidate_midis: list[int],
) -> dict[str, Any]:
    midis = [int(value) for value in candidate_midis]
    if midis != sorted(set(midis)):
        raise FixedFeatureCompetitionDiagnosticError("CANDIDATE_MIDIS_NOT_SORTED_UNIQUE")
    if any(
        midi < v6.PLAYABLE_MIDI_MIN or midi > v6.PLAYABLE_MIDI_MAX
        for midi in midis
    ):
        raise FixedFeatureCompetitionDiagnosticError("CANDIDATE_MIDI_OUTSIDE_PLAYABLE_RANGE")
    features = [int(value) for value in fixed_feature_bins]
    if features != sorted(set(features)):
        raise FixedFeatureCompetitionDiagnosticError("FIXED_FEATURE_BINS_NOT_SORTED_UNIQUE")
    if not features or features[0] < 0 or features[-1] >= raw.size:
        raise FixedFeatureCompetitionDiagnosticError("FIXED_FEATURE_BIN_OUT_OF_RANGE")

    observed = np.asarray([raw[index] for index in features], dtype=np.float64)
    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < v6.MIN_INNOVATION_ENERGY:
        return {
            "available": False,
            "availabilityStatus": "INSUFFICIENT_FIXED_FEATURE_ENERGY",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }
    if int(selected_midi) not in midis:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_MIDI_NOT_IN_CANDIDATE_SET",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }
    if len(midis) < 2:
        return {
            "available": False,
            "availabilityStatus": "REDUCED_DICTIONARY_EMPTY",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }

    row_for_bin = {bin_index: row for row, bin_index in enumerate(features)}
    dictionary = np.zeros((len(features), len(midis)), dtype=np.float64)
    for column, midi in enumerate(midis):
        template = templates.get(midi)
        if (
            not isinstance(template, dict)
            or template.get("structurallyConstructible") is not True
            or template.get("admittedToGateFreeCompetition") is not True
        ):
            raise FixedFeatureCompetitionDiagnosticError(
                f"NON_CONSTRUCTIBLE_TEMPLATE:{midi}"
            )
        bins = list(template.get("bins", []))
        weights = list(template.get("weights", []))
        if len(bins) != len(weights):
            raise FixedFeatureCompetitionDiagnosticError(f"MALFORMED_TEMPLATE:{midi}")
        for bin_index, weight in zip(bins, weights):
            bin_index = int(bin_index)
            if bin_index not in row_for_bin:
                raise FixedFeatureCompetitionDiagnosticError(
                    f"TEMPLATE_BIN_OUTSIDE_FIXED_UNIVERSE:{midi}:{bin_index}"
                )
            dictionary[row_for_bin[bin_index], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_FULL_FAILED:{type(exc).__name__}",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }

    selected_column = midis.index(int(selected_midi))
    reduced = np.delete(dictionary, selected_column, axis=1)
    try:
        _reduced_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_REDUCED_FAILED:{type(exc).__name__}",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }

    coefficients = np.asarray(coefficients, dtype=np.float64)
    selected_coefficient = float(coefficients[selected_column])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float(
        (without_residual - full_residual) / max(feature_energy, 1e-15)
    )
    scalar_values = (
        selected_coefficient,
        full_residual,
        without_residual,
        necessity_fraction,
    )
    if not all(math.isfinite(value) for value in scalar_values):
        return {
            "available": False,
            "availabilityStatus": "NONFINITE_FIT",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "fixedFeatureBinCount": len(features),
            "fixedFeatureBins": features,
            "fixedFeatureEnergy": feature_energy,
        }
    if not np.all(np.isfinite(coefficients)) or np.any(coefficients < 0.0):
        raise FixedFeatureCompetitionDiagnosticError("NONFINITE_OR_NEGATIVE_COEFFICIENT")

    return {
        "available": True,
        "availabilityStatus": "AVAILABLE",
        "candidateCount": len(midis),
        "candidateMidis": midis,
        "fixedFeatureBinCount": len(features),
        "fixedFeatureBins": features,
        "fixedFeatureEnergy": feature_energy,
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "necessityFraction": necessity_fraction,
        "coefficientRows": [
            {"midi": int(midi), "coefficient": float(coefficients[index])}
            for index, midi in enumerate(midis)
        ],
    }


def _fit_delta(left: dict[str, Any], right: dict[str, Any]) -> float | None:
    if left.get("available") is not True or right.get("available") is not True:
        return None
    return float(left["necessityFraction"] - right["necessityFraction"])


def evaluate_fixed_feature_competition_diagnostic(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return fixed-feature population measurements only; no successor verdict."""

    if not _contracts_ok():
        raise FixedFeatureCompetitionDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise FixedFeatureCompetitionDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise FixedFeatureCompetitionDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise FixedFeatureCompetitionDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    values = _finite_audio(audio)
    hz = _validated_frequencies(frequencies)
    historical = v6.classify_audio_event(values, onset_sample, selected_midi)

    try:
        onset = v6._onset_innovation_spectrum(values, onset_sample)
    except v6.CorroborationError as exc:
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "onsetAvailable": False,
            "onsetStatus": "CONTEXT_ERROR",
            "onsetReason": str(exc),
            "frozenV6HistoricalComponent": historical,
            "candidateSets": None,
            "fixedFeatureUniverse": None,
            "fixedFeatureFits": None,
            "variableFeatureReferences": None,
            "diagnosticDeltas": None,
        }

    if onset.get("status") != "OK":
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "onsetAvailable": False,
            "onsetStatus": str(onset.get("status", "UNKNOWN")),
            "onsetReason": str(onset.get("status", "UNKNOWN")),
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "frozenV6HistoricalComponent": historical,
            "candidateSets": None,
            "fixedFeatureUniverse": None,
            "fixedFeatureFits": None,
            "variableFeatureReferences": None,
            "diagnosticDeltas": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise FixedFeatureCompetitionDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")

    gate_free_templates = {
        midi: gatefree.gate_free_competition_template(midi, raw, hz)
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    gate_free_midis = sorted(
        midi
        for midi, row in gate_free_templates.items()
        if row.get("structurallyConstructible") is True
        and row.get("admittedToGateFreeCompetition") is True
    )
    historical_templates = {
        midi: dict(v6._candidate_template(midi, raw, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    historical_valid_midis = sorted(
        midi for midi, row in historical_templates.items() if row.get("valid") is True
    )

    support = bridge.collapse_hann_lobes_to_peak_bands(raw)
    if support.shape != raw.shape or not np.all(np.isfinite(support)) or np.any(support < 0.0):
        raise FixedFeatureCompetitionDiagnosticError("INVALID_SUPPORT_VIEW")
    if np.any(support > raw):
        raise FixedFeatureCompetitionDiagnosticError("SUPPORT_VIEW_AMPLITUDE_EXCEEDS_RAW")
    if np.any((support > 0.0) & ~(raw > 0.0)):
        raise FixedFeatureCompetitionDiagnosticError("SUPPORT_VIEW_INVENTED_NONZERO_BIN")

    support_templates = {
        midi: dict(v3.evaluate_candidate_template(midi, support, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    support_valid_midis = sorted(
        midi for midi, row in support_templates.items() if row.get("valid") is True
    )
    intersection_midis = sorted(
        set(historical_valid_midis).intersection(support_valid_midis)
    )

    fixed_feature_bins = sorted(
        {
            int(bin_index)
            for midi in gate_free_midis
            for bin_index in gate_free_templates[midi].get("bins", [])
        }
    )
    if not fixed_feature_bins:
        raise FixedFeatureCompetitionDiagnosticError("EMPTY_FIXED_FEATURE_UNIVERSE")
    fixed_observed = np.asarray([raw[index] for index in fixed_feature_bins], dtype=np.float64)
    fixed_feature_energy = float(np.linalg.norm(fixed_observed))
    if not math.isfinite(fixed_feature_energy):
        raise FixedFeatureCompetitionDiagnosticError("NONFINITE_FIXED_FEATURE_ENERGY")

    gate_free_fixed = _fit_on_fixed_feature_universe(
        selected_midi,
        raw,
        gate_free_templates,
        fixed_feature_bins,
        gate_free_midis,
    )
    historical_fixed = _fit_on_fixed_feature_universe(
        selected_midi,
        raw,
        gate_free_templates,
        fixed_feature_bins,
        historical_valid_midis,
    )
    intersection_fixed = _fit_on_fixed_feature_universe(
        selected_midi,
        raw,
        gate_free_templates,
        fixed_feature_bins,
        intersection_midis,
    )

    gate_free_variable = gatefree._fit_gate_free_templates(
        selected_midi,
        raw,
        gate_free_templates,
        gate_free_midis,
    )
    historical_variable = gatefree._fit_gate_free_templates(
        selected_midi,
        raw,
        gate_free_templates,
        historical_valid_midis,
    )
    intersection_variable = gatefree._fit_gate_free_templates(
        selected_midi,
        raw,
        gate_free_templates,
        intersection_midis,
    )

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "frozenV6HistoricalComponent": historical,
        "candidateSets": {
            "gateFree49Midis": gate_free_midis,
            "historicalRawValidMidis": historical_valid_midis,
            "supportValidMidis": support_valid_midis,
            "rawSupportIntersectionMidis": intersection_midis,
        },
        "fixedFeatureUniverse": {
            "featureBinCount": len(fixed_feature_bins),
            "featureBins": fixed_feature_bins,
            "featureEnergy": fixed_feature_energy,
        },
        "fixedFeatureFits": {
            "gateFree49FixedFit": gate_free_fixed,
            "historicalRawValidFixedFit": historical_fixed,
            "rawSupportIntersectionFixedFit": intersection_fixed,
        },
        "variableFeatureReferences": {
            "gateFree49VariableFit": gate_free_variable,
            "historicalRawValidVariableFit": historical_variable,
            "rawSupportIntersectionVariableFit": intersection_variable,
            "frozenV6HistoricalFit": historical.get("fit"),
        },
        "diagnosticDeltas": {
            "gateFreeVsHistoricalColumnDelta": _fit_delta(
                gate_free_fixed,
                historical_fixed,
            ),
            "historicalVsIntersectionColumnDelta": _fit_delta(
                historical_fixed,
                intersection_fixed,
            ),
            "historicalFeatureUniverseDelta": _fit_delta(
                historical_fixed,
                historical_variable,
            ),
            "intersectionFeatureUniverseDelta": _fit_delta(
                intersection_fixed,
                intersection_variable,
            ),
            "gateFreeFeatureUniverseDelta": _fit_delta(
                gate_free_fixed,
                gate_free_variable,
            ),
        },
        "historicalV6RatioGateReferenceOnly": float(
            v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN
        ),
        "historicalV6NecessityThresholdReferenceOnly": float(v6.NECESSITY_FRACTION_MIN),
    }
