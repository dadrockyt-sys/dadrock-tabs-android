#!/usr/bin/env python3
"""Synthetic-only V7 candidate-population / competition diagnostics.

Prospectively frozen by
SONGSTERR_FRESH_V7_CANDIDATE_COMPETITION_DIAGNOSTIC_PRE.md.

This module defines no successor classifier. It holds frozen V6 raw onset
innovation and raw V6 template semantics fixed while varying only the candidate
MIDI population used by diagnostic NNLS fits.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge
import v7_dual_view_diagnostics_v1 as dual

CONTRACT = "songsterr-fresh-v7-candidate-competition-diagnostic-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_V3_VERSION = 1
EXPECTED_BRIDGE_CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
EXPECTED_BRIDGE_VERSION = 2
EXPECTED_DUAL_CONTRACT = "songsterr-fresh-v7-dual-view-representation-diagnostic-v1"
EXPECTED_DUAL_VERSION = 1


class CandidateCompetitionDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(v3, "CONTRACT", None) == EXPECTED_V3_CONTRACT
        and getattr(v3, "VERSION", None) == EXPECTED_V3_VERSION
        and getattr(bridge, "CONTRACT", None) == EXPECTED_BRIDGE_CONTRACT
        and getattr(bridge, "VERSION", None) == EXPECTED_BRIDGE_VERSION
        and getattr(dual, "CONTRACT", None) == EXPECTED_DUAL_CONTRACT
        and getattr(dual, "VERSION", None) == EXPECTED_DUAL_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
        and getattr(v6, "TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN", None) == 0.20
        and getattr(v6, "NECESSITY_FRACTION_MIN", None) == 0.01
    )


def _finite_audio(audio: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise CandidateCompetitionDiagnosticError(
            f"AUDIO_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise CandidateCompetitionDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")
    return values


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise CandidateCompetitionDiagnosticError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise CandidateCompetitionDiagnosticError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise CandidateCompetitionDiagnosticError("FREQUENCY_GRID_MISMATCH")
    if not np.allclose(hz, v3.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise CandidateCompetitionDiagnosticError("V6_V3_FREQUENCY_GRID_MISMATCH")
    return hz


def _fit_raw_templates(
    selected_midi: int,
    raw: np.ndarray,
    raw_templates: dict[int, dict[str, Any]],
    candidate_midis: list[int],
) -> dict[str, Any]:
    midis = [int(value) for value in candidate_midis]
    if midis != sorted(set(midis)):
        raise CandidateCompetitionDiagnosticError("CANDIDATE_MIDIS_NOT_SORTED_UNIQUE")
    if any(midi < v6.PLAYABLE_MIDI_MIN or midi > v6.PLAYABLE_MIDI_MAX for midi in midis):
        raise CandidateCompetitionDiagnosticError("CANDIDATE_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if int(selected_midi) not in midis:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_MIDI_NOT_IN_CANDIDATE_SET",
            "candidateCount": len(midis),
            "candidateMidis": midis,
        }
    for midi in midis:
        template = raw_templates.get(midi)
        if not isinstance(template, dict) or template.get("valid") is not True:
            raise CandidateCompetitionDiagnosticError(f"NON_RAW_VALID_CANDIDATE:{midi}")

    feature_bins = sorted(
        {
            int(bin_index)
            for midi in midis
            for bin_index in raw_templates[midi].get("bins", [])
        }
    )
    if not feature_bins:
        return {
            "available": False,
            "availabilityStatus": "NO_FEATURE_BINS",
            "candidateCount": len(midis),
            "candidateMidis": midis,
        }
    if feature_bins[0] < 0 or feature_bins[-1] >= raw.size:
        raise CandidateCompetitionDiagnosticError("FEATURE_BIN_OUT_OF_RANGE")

    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([raw[index] for index in feature_bins], dtype=np.float64)
    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < v6.MIN_INNOVATION_ENERGY:
        return {
            "available": False,
            "availabilityStatus": "INSUFFICIENT_FEATURE_ENERGY",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }

    dictionary = np.zeros((len(feature_bins), len(midis)), dtype=np.float64)
    for column, midi in enumerate(midis):
        template = raw_templates[midi]
        bins = list(template.get("bins", []))
        weights = list(template.get("weights", []))
        if len(bins) != len(weights):
            raise CandidateCompetitionDiagnosticError(f"MALFORMED_RAW_TEMPLATE:{midi}")
        for bin_index, weight in zip(bins, weights):
            dictionary[row_for_bin[int(bin_index)], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_FULL_FAILED:{type(exc).__name__}",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }

    selected_column = midis.index(int(selected_midi))
    reduced = np.delete(dictionary, selected_column, axis=1)
    if reduced.shape[1] == 0:
        return {
            "available": False,
            "availabilityStatus": "REDUCED_DICTIONARY_EMPTY",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }
    try:
        _without_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_REDUCED_FAILED:{type(exc).__name__}",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }

    selected_coefficient = float(coefficients[selected_column])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float(
        (without_residual - full_residual) / max(feature_energy, 1e-15)
    )
    values = (selected_coefficient, full_residual, without_residual, necessity_fraction)
    if not all(math.isfinite(value) for value in values):
        return {
            "available": False,
            "availabilityStatus": "NONFINITE_FIT",
            "candidateCount": len(midis),
            "candidateMidis": midis,
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }

    return {
        "available": True,
        "availabilityStatus": "AVAILABLE",
        "candidateCount": len(midis),
        "candidateMidis": midis,
        "featureBinCount": len(feature_bins),
        "featureBins": feature_bins,
        "featureEnergy": feature_energy,
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "necessityFraction": necessity_fraction,
    }


def _largest_absolute_delta(rows: list[dict[str, Any]], field: str) -> dict[str, Any] | None:
    eligible = [
        row
        for row in rows
        if isinstance(row.get(field), (int, float)) and not isinstance(row.get(field), bool)
    ]
    if not eligible:
        return None
    ranked = sorted(eligible, key=lambda row: (-abs(float(row[field])), int(row["midi"])))
    row = ranked[0]
    return {"midi": int(row["midi"]), field: float(row[field])}


def evaluate_candidate_competition_diagnostic(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return candidate-population measurements only; no successor verdict."""

    if not _contracts_ok():
        raise CandidateCompetitionDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise CandidateCompetitionDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise CandidateCompetitionDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    onset_sample = int(onset_sample)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise CandidateCompetitionDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

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
            "rawFullFit": None,
            "rawSupportMidiRestrictedFit": None,
            "excludedCandidateAttribution": None,
            "dualViewReference": None,
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
            "rawFullFit": None,
            "rawSupportMidiRestrictedFit": None,
            "excludedCandidateAttribution": None,
            "dualViewReference": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise CandidateCompetitionDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")
    raw_norm = float(np.linalg.norm(raw))
    if not math.isfinite(raw_norm) or raw_norm < v6.MIN_INNOVATION_ENERGY:
        raise CandidateCompetitionDiagnosticError("UNEXPECTED_LOW_RAW_INNOVATION")

    support = bridge.collapse_hann_lobes_to_peak_bands(raw)
    if support.shape != raw.shape or not np.all(np.isfinite(support)) or np.any(support < 0.0):
        raise CandidateCompetitionDiagnosticError("INVALID_SUPPORT_VIEW")
    if np.any(support > raw):
        raise CandidateCompetitionDiagnosticError("SUPPORT_VIEW_AMPLITUDE_EXCEEDS_RAW")
    if np.any((support > 0.0) & ~(raw > 0.0)):
        raise CandidateCompetitionDiagnosticError("SUPPORT_VIEW_INVENTED_NONZERO_BIN")

    raw_templates = {
        midi: dict(v6._candidate_template(midi, raw, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    support_templates = {
        midi: dict(v3.evaluate_candidate_template(midi, support, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    raw_valid = sorted(midi for midi, row in raw_templates.items() if row.get("valid") is True)
    support_valid = sorted(
        midi for midi, row in support_templates.items() if row.get("valid") is True
    )
    intersection = sorted(set(raw_valid).intersection(support_valid))
    raw_only = sorted(set(raw_valid).difference(support_valid))
    support_only = sorted(set(support_valid).difference(raw_valid))

    raw_full_fit = _fit_raw_templates(selected_midi, raw, raw_templates, raw_valid)
    selected_support_eligible = selected_midi in support_valid
    if selected_midi in intersection:
        restricted_fit = _fit_raw_templates(
            selected_midi,
            raw,
            raw_templates,
            intersection,
        )
    else:
        restricted_fit = {
            "available": False,
            "availabilityStatus": "SELECTED_MIDI_NOT_IN_RAW_SUPPORT_INTERSECTION",
            "candidateCount": len(intersection),
            "candidateMidis": intersection,
        }

    add_one_rows: list[dict[str, Any]] = []
    leave_one_out_rows: list[dict[str, Any]] = []
    if restricted_fit.get("available") is True and raw_full_fit.get("available") is True:
        restricted_necessity = float(restricted_fit["necessityFraction"])
        full_necessity = float(raw_full_fit["necessityFraction"])
        for midi in raw_only:
            add_set = sorted(set(intersection).union({int(midi)}))
            add_fit = _fit_raw_templates(selected_midi, raw, raw_templates, add_set)
            add_necessity = (
                float(add_fit["necessityFraction"])
                if add_fit.get("available") is True
                else None
            )
            add_one_rows.append(
                {
                    "midi": int(midi),
                    "fitAvailable": add_fit.get("available") is True,
                    "fitStatus": add_fit.get("availabilityStatus"),
                    "necessityFraction": add_necessity,
                    "necessityDeltaFromRestricted": (
                        None
                        if add_necessity is None
                        else float(add_necessity - restricted_necessity)
                    ),
                }
            )

            leave_set = [candidate for candidate in raw_valid if candidate != midi]
            if selected_midi in leave_set and len(leave_set) >= 2:
                leave_fit = _fit_raw_templates(
                    selected_midi,
                    raw,
                    raw_templates,
                    leave_set,
                )
                leave_necessity = (
                    float(leave_fit["necessityFraction"])
                    if leave_fit.get("available") is True
                    else None
                )
                leave_one_out_rows.append(
                    {
                        "midi": int(midi),
                        "fitAvailable": leave_fit.get("available") is True,
                        "fitStatus": leave_fit.get("availabilityStatus"),
                        "necessityFraction": leave_necessity,
                        "necessityDeltaFromFull": (
                            None
                            if leave_necessity is None
                            else float(leave_necessity - full_necessity)
                        ),
                    }
                )
            else:
                leave_one_out_rows.append(
                    {
                        "midi": int(midi),
                        "fitAvailable": False,
                        "fitStatus": "LEAVE_ONE_OUT_SET_UNAVAILABLE",
                        "necessityFraction": None,
                        "necessityDeltaFromFull": None,
                    }
                )

    dual_reference = dual.evaluate_dual_view_diagnostics(selected_midi, raw, hz)
    if dual_reference.get("finalDecisionDefined") is not False:
        raise CandidateCompetitionDiagnosticError("DUAL_REFERENCE_DEFINED_FINAL_DECISION")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "rawInnovationNorm": raw_norm,
        "supportInnovationNorm": float(np.linalg.norm(support)),
        "selectedRawEligible": selected_midi in raw_valid,
        "selectedSupportEligible": selected_support_eligible,
        "candidateCompetitionComparable": bool(selected_midi in intersection),
        "candidateSets": {
            "rawValidMidis": raw_valid,
            "supportValidMidis": support_valid,
            "intersectionMidis": intersection,
            "rawOnlyMidis": raw_only,
            "supportOnlyMidis": support_only,
        },
        "rawFullFit": raw_full_fit,
        "rawSupportMidiRestrictedFit": restricted_fit,
        "excludedCandidateAttribution": {
            "available": bool(
                restricted_fit.get("available") is True
                and raw_full_fit.get("available") is True
            ),
            "addOneRows": add_one_rows,
            "leaveOneOutRows": leave_one_out_rows,
            "largestAbsoluteAddOneDelta": _largest_absolute_delta(
                add_one_rows, "necessityDeltaFromRestricted"
            ),
            "largestAbsoluteLeaveOneOutDelta": _largest_absolute_delta(
                leave_one_out_rows, "necessityDeltaFromFull"
            ),
        },
        "dualViewReference": dual_reference,
        "frozenV6HistoricalComponent": historical,
        "historicalV6NecessityThresholdReferenceOnly": float(v6.NECESSITY_FRACTION_MIN),
        "historicalV6FundamentalRatioThresholdReferenceOnly": float(
            v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN
        ),
    }
