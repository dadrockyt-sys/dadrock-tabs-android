#!/usr/bin/env python3
"""Synthetic-only gate-free candidate competition diagnostics.

Prospectively frozen by
SONGSTERR_FRESH_V7_GATE_FREE_COMPETITION_DIAGNOSTIC_PRE.md.

This module defines no successor classifier. It reproduces frozen V6 raw
harmonic template geometry while removing the historical fundamental-ratio
validity gate from *competition-column admission only*.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

import onset_birth_corroboration_v6 as v6

CONTRACT = "songsterr-fresh-v7-gate-free-competition-diagnostic-v1"
VERSION = 1
EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6


class GateFreeCompetitionDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
        and getattr(v6, "HARMONIC_COUNT_MAX", None) == 6
        and getattr(v6, "TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN", None) == 0.20
        and getattr(v6, "NECESSITY_FRACTION_MIN", None) == 0.01
    )


def _finite_audio(audio: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise GateFreeCompetitionDiagnosticError(
            f"AUDIO_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise GateFreeCompetitionDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")
    return values


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise GateFreeCompetitionDiagnosticError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise GateFreeCompetitionDiagnosticError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise GateFreeCompetitionDiagnosticError("FREQUENCY_GRID_MISMATCH")
    return hz


def gate_free_competition_template(
    midi: int,
    innovation: np.ndarray,
    frequencies: np.ndarray,
) -> dict[str, Any]:
    """Reproduce V6 template geometry without ratio-based admission rejection."""

    if isinstance(midi, bool) or not isinstance(midi, (int, np.integer)):
        raise GateFreeCompetitionDiagnosticError("MIDI_INTEGER_REQUIRED")
    midi = int(midi)
    if not v6.PLAYABLE_MIDI_MIN <= midi <= v6.PLAYABLE_MIDI_MAX:
        raise GateFreeCompetitionDiagnosticError("MIDI_OUTSIDE_PLAYABLE_RANGE")

    low_hz = v6.midi_to_hz(float(midi) - 0.5)
    high_hz = v6.midi_to_hz(float(midi) + 0.5)
    fundamental_indices = np.flatnonzero(
        (frequencies >= low_hz) & (frequencies < high_hz)
    )
    if fundamental_indices.size == 0:
        return {
            "structurallyConstructible": False,
            "reason": "NO_FUNDAMENTAL_CELL_BIN",
            "midi": midi,
        }

    local = innovation[fundamental_indices]
    fundamental_bin = int(fundamental_indices[int(np.argmax(local))])
    fundamental_hz = float(frequencies[fundamental_bin])
    if not math.isfinite(fundamental_hz) or fundamental_hz <= 0.0:
        return {
            "structurallyConstructible": False,
            "reason": "INVALID_FUNDAMENTAL_FREQUENCY",
            "midi": midi,
        }

    bins: list[int] = []
    weights: list[float] = []
    observed: list[float] = []
    for harmonic in range(1, v6.HARMONIC_COUNT_MAX + 1):
        target_hz = float(harmonic) * fundamental_hz
        if target_hz >= v6.SAMPLE_RATE / 2.0:
            break
        position = target_hz * float(v6.FFT_SIZE) / float(v6.SAMPLE_RATE)
        nearest = int(math.floor(position + 0.5))
        left = max(0, nearest - 1)
        right = min(innovation.size - 1, nearest + 1)
        search = innovation[left : right + 1]
        chosen = int(left + int(np.argmax(search)))
        bins.append(chosen)
        weights.append(1.0 / float(harmonic))
        observed.append(float(innovation[chosen]))

    if len(bins) < 3:
        return {
            "structurallyConstructible": False,
            "reason": "FEWER_THAN_THREE_HARMONICS",
            "midi": midi,
        }
    if not all(math.isfinite(value) and value >= 0.0 for value in observed):
        return {
            "structurallyConstructible": False,
            "reason": "NONFINITE_HARMONIC_INNOVATION",
            "midi": midi,
        }

    maximum = max(observed)
    ratio = 0.0 if maximum <= 0.0 else float(observed[0] / maximum)

    norm = float(np.linalg.norm(np.asarray(weights, dtype=np.float64)))
    if not math.isfinite(norm) or norm <= 0.0:
        return {
            "structurallyConstructible": False,
            "reason": "INVALID_TEMPLATE_NORM",
            "midi": midi,
        }
    normalized = [float(weight / norm) for weight in weights]

    return {
        "structurallyConstructible": True,
        "reason": "STRUCTURALLY_CONSTRUCTIBLE",
        "midi": midi,
        "fundamentalBin": fundamental_bin,
        "fundamentalHz": fundamental_hz,
        "bins": [int(value) for value in bins],
        "weights": normalized,
        "observedHarmonicInnovation": observed,
        "fundamentalToMaxHarmonicInnovationRatio": ratio,
        "historicalV6RatioGateReferenceOnly": float(
            v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN
        ),
        "historicalV6RatioGateWouldPass": bool(
            ratio >= float(v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN)
        ),
        "admittedToGateFreeCompetition": True,
    }


def _fit_gate_free_templates(
    selected_midi: int,
    raw: np.ndarray,
    templates: dict[int, dict[str, Any]],
    candidate_midis: list[int],
) -> dict[str, Any]:
    midis = [int(value) for value in candidate_midis]
    if midis != sorted(set(midis)):
        raise GateFreeCompetitionDiagnosticError("CANDIDATE_MIDIS_NOT_SORTED_UNIQUE")
    if any(
        midi < v6.PLAYABLE_MIDI_MIN or midi > v6.PLAYABLE_MIDI_MAX
        for midi in midis
    ):
        raise GateFreeCompetitionDiagnosticError("CANDIDATE_MIDI_OUTSIDE_PLAYABLE_RANGE")
    if int(selected_midi) not in midis:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_MIDI_NOT_IN_CANDIDATE_SET",
            "candidateCount": len(midis),
            "candidateMidis": midis,
        }
    for midi in midis:
        template = templates.get(midi)
        if (
            not isinstance(template, dict)
            or template.get("structurallyConstructible") is not True
            or template.get("admittedToGateFreeCompetition") is not True
        ):
            raise GateFreeCompetitionDiagnosticError(
                f"NON_CONSTRUCTIBLE_GATE_FREE_CANDIDATE:{midi}"
            )

    feature_bins = sorted(
        {
            int(bin_index)
            for midi in midis
            for bin_index in templates[midi].get("bins", [])
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
        raise GateFreeCompetitionDiagnosticError("FEATURE_BIN_OUT_OF_RANGE")

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
        template = templates[midi]
        bins = list(template.get("bins", []))
        weights = list(template.get("weights", []))
        if len(bins) != len(weights):
            raise GateFreeCompetitionDiagnosticError(
                f"MALFORMED_GATE_FREE_TEMPLATE:{midi}"
            )
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
        _reduced_coefficients, without_residual = nnls(reduced, observed)
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
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "featureEnergy": feature_energy,
        }
    if not np.all(np.isfinite(coefficients)) or np.any(coefficients < 0.0):
        raise GateFreeCompetitionDiagnosticError("NONFINITE_OR_NEGATIVE_COEFFICIENT")

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
        "coefficientRows": [
            {"midi": int(midi), "coefficient": float(coefficients[index])}
            for index, midi in enumerate(midis)
        ],
    }


def _largest_absolute_delta(
    rows: list[dict[str, Any]],
    field: str,
) -> dict[str, Any] | None:
    eligible = [
        row
        for row in rows
        if isinstance(row.get(field), (int, float))
        and not isinstance(row.get(field), bool)
    ]
    if not eligible:
        return None
    ranked = sorted(
        eligible,
        key=lambda row: (-abs(float(row[field])), int(row["midi"])),
    )
    row = ranked[0]
    return {"midi": int(row["midi"]), field: float(row[field])}


def evaluate_gate_free_competition_diagnostic(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return gate-free competition measurements only; no successor verdict."""

    if not _contracts_ok():
        raise GateFreeCompetitionDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise GateFreeCompetitionDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise GateFreeCompetitionDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise GateFreeCompetitionDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

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
            "gateFreeTemplates": None,
            "historicalRawValidMidis": None,
            "gateFreeMidis": None,
            "newlyAdmittedMidis": None,
            "gateFreeFit": None,
            "frozenGatedPopulationReconstruction": None,
            "newlyAdmittedAttribution": None,
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
            "gateFreeTemplates": None,
            "historicalRawValidMidis": None,
            "gateFreeMidis": None,
            "newlyAdmittedMidis": None,
            "gateFreeFit": None,
            "frozenGatedPopulationReconstruction": None,
            "newlyAdmittedAttribution": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise GateFreeCompetitionDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")

    gate_free_templates = {
        midi: gate_free_competition_template(midi, raw, hz)
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    frozen_templates = {
        midi: dict(v6._candidate_template(midi, raw, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }

    gate_free_midis = sorted(
        midi
        for midi, row in gate_free_templates.items()
        if row.get("structurallyConstructible") is True
        and row.get("admittedToGateFreeCompetition") is True
    )
    historical_valid_midis = sorted(
        midi for midi, row in frozen_templates.items() if row.get("valid") is True
    )
    newly_admitted_midis = sorted(
        set(gate_free_midis).difference(historical_valid_midis)
    )

    gate_free_fit = _fit_gate_free_templates(
        selected_midi,
        raw,
        gate_free_templates,
        gate_free_midis,
    )

    if selected_midi in historical_valid_midis:
        frozen_population_reconstruction = _fit_gate_free_templates(
            selected_midi,
            raw,
            gate_free_templates,
            historical_valid_midis,
        )
    else:
        frozen_population_reconstruction = {
            "available": False,
            "availabilityStatus": "SELECTED_MIDI_NOT_HISTORICALLY_RAW_VALID",
            "candidateCount": len(historical_valid_midis),
            "candidateMidis": historical_valid_midis,
        }

    add_one_rows: list[dict[str, Any]] = []
    leave_one_out_rows: list[dict[str, Any]] = []
    attribution_available = bool(
        selected_midi in historical_valid_midis
        and frozen_population_reconstruction.get("available") is True
        and gate_free_fit.get("available") is True
    )
    if attribution_available:
        gated_necessity = float(frozen_population_reconstruction["necessityFraction"])
        gate_free_necessity = float(gate_free_fit["necessityFraction"])
        for midi in newly_admitted_midis:
            add_set = sorted(set(historical_valid_midis).union({int(midi)}))
            add_fit = _fit_gate_free_templates(
                selected_midi,
                raw,
                gate_free_templates,
                add_set,
            )
            add_necessity = (
                float(add_fit["necessityFraction"])
                if add_fit.get("available") is True
                else None
            )
            add_one_rows.append(
                {
                    "midi": int(midi),
                    "historicalRatio": float(
                        gate_free_templates[midi][
                            "fundamentalToMaxHarmonicInnovationRatio"
                        ]
                    ),
                    "fitAvailable": add_fit.get("available") is True,
                    "fitStatus": add_fit.get("availabilityStatus"),
                    "necessityFraction": add_necessity,
                    "necessityDeltaFromFrozenGatedPopulation": (
                        None
                        if add_necessity is None
                        else float(add_necessity - gated_necessity)
                    ),
                }
            )

            leave_set = [candidate for candidate in gate_free_midis if candidate != midi]
            if selected_midi in leave_set and len(leave_set) >= 2:
                leave_fit = _fit_gate_free_templates(
                    selected_midi,
                    raw,
                    gate_free_templates,
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
                        "historicalRatio": float(
                            gate_free_templates[midi][
                                "fundamentalToMaxHarmonicInnovationRatio"
                            ]
                        ),
                        "fitAvailable": leave_fit.get("available") is True,
                        "fitStatus": leave_fit.get("availabilityStatus"),
                        "necessityFraction": leave_necessity,
                        "necessityDeltaFromGateFreePopulation": (
                            None
                            if leave_necessity is None
                            else float(leave_necessity - gate_free_necessity)
                        ),
                    }
                )
            else:
                leave_one_out_rows.append(
                    {
                        "midi": int(midi),
                        "historicalRatio": float(
                            gate_free_templates[midi][
                                "fundamentalToMaxHarmonicInnovationRatio"
                            ]
                        ),
                        "fitAvailable": False,
                        "fitStatus": "LEAVE_ONE_OUT_SET_UNAVAILABLE",
                        "necessityFraction": None,
                        "necessityDeltaFromGateFreePopulation": None,
                    }
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
        "gateFreeTemplates": [gate_free_templates[midi] for midi in sorted(gate_free_templates)],
        "historicalRawValidMidis": historical_valid_midis,
        "gateFreeMidis": gate_free_midis,
        "newlyAdmittedMidis": newly_admitted_midis,
        "selectedHistoricallyRawValid": selected_midi in historical_valid_midis,
        "selectedGateFreeConstructible": selected_midi in gate_free_midis,
        "gateFreeFit": gate_free_fit,
        "frozenGatedPopulationReconstruction": frozen_population_reconstruction,
        "newlyAdmittedAttribution": {
            "available": attribution_available,
            "addOneRows": add_one_rows,
            "leaveOneOutRows": leave_one_out_rows,
            "largestAbsoluteAddOneDelta": _largest_absolute_delta(
                add_one_rows,
                "necessityDeltaFromFrozenGatedPopulation",
            ),
            "largestAbsoluteLeaveOneOutDelta": _largest_absolute_delta(
                leave_one_out_rows,
                "necessityDeltaFromGateFreePopulation",
            ),
        },
        "historicalV6RatioGateReferenceOnly": float(
            v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN
        ),
        "historicalV6NecessityThresholdReferenceOnly": float(v6.NECESSITY_FRACTION_MIN),
    }
