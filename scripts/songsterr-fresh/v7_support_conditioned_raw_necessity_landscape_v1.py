#!/usr/bin/env python3
"""Synthetic-only support-conditioned raw necessity landscape diagnostics.

Prospectively frozen by
SONGSTERR_FRESH_V7_SUPPORT_CONDITIONED_RAW_NECESSITY_LANDSCAPE_PRE.md.

Every support-eligible MIDI is measured as a candidate inside the same frozen
all-49 fixed-feature raw NNLS problem. No threshold, rank cutoff, or final
classifier is defined.
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
import v7_gate_free_competition_diagnostics_v1 as gatefree

CONTRACT = "songsterr-fresh-v7-support-conditioned-raw-necessity-landscape-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_V3_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_V3_VERSION = 1
EXPECTED_BRIDGE_CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
EXPECTED_BRIDGE_VERSION = 2
EXPECTED_DUAL_CONTRACT = "songsterr-fresh-v7-dual-view-representation-diagnostic-v1"
EXPECTED_DUAL_VERSION = 1
EXPECTED_GATEFREE_CONTRACT = "songsterr-fresh-v7-gate-free-competition-diagnostic-v1"
EXPECTED_GATEFREE_VERSION = 1


class SupportConditionedRawLandscapeError(RuntimeError):
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
        and getattr(gatefree, "CONTRACT", None) == EXPECTED_GATEFREE_CONTRACT
        and getattr(gatefree, "VERSION", None) == EXPECTED_GATEFREE_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
    )


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise SupportConditionedRawLandscapeError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise SupportConditionedRawLandscapeError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise SupportConditionedRawLandscapeError("FREQUENCY_GRID_MISMATCH")
    if not np.allclose(hz, v3.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise SupportConditionedRawLandscapeError("V6_V3_FREQUENCY_GRID_MISMATCH")
    return hz


def evaluate_support_conditioned_raw_landscape(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return threshold-free support-conditioned raw competition measurements."""

    if not _contracts_ok():
        raise SupportConditionedRawLandscapeError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise SupportConditionedRawLandscapeError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise SupportConditionedRawLandscapeError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise SupportConditionedRawLandscapeError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise SupportConditionedRawLandscapeError(
            f"AUDIO_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise SupportConditionedRawLandscapeError("FINITE_MONO_AUDIO_REQUIRED")

    hz = _validated_frequencies(frequencies)

    try:
        onset = v6._onset_innovation_spectrum(values, onset_sample)
    except v6.CorroborationError as exc:
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "rawNecessityThresholdDefined": False,
            "rankCutoffDefined": False,
            "onsetAvailable": False,
            "onsetStatus": "CONTEXT_ERROR",
            "onsetReason": str(exc),
            "supportValidMidis": None,
            "fixedRawProblem": None,
            "landscapeRows": None,
            "selectedLandscapeRow": None,
        }

    if onset.get("status") != "OK":
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "rawNecessityThresholdDefined": False,
            "rankCutoffDefined": False,
            "onsetAvailable": False,
            "onsetStatus": str(onset.get("status", "UNKNOWN")),
            "onsetReason": str(onset.get("status", "UNKNOWN")),
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "supportValidMidis": None,
            "fixedRawProblem": None,
            "landscapeRows": None,
            "selectedLandscapeRow": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise SupportConditionedRawLandscapeError("INVALID_FROZEN_V6_RAW_INNOVATION")

    support = bridge.collapse_hann_lobes_to_peak_bands(raw)
    if support.shape != raw.shape or not np.all(np.isfinite(support)) or np.any(support < 0.0):
        raise SupportConditionedRawLandscapeError("INVALID_SUPPORT_VIEW")
    if np.any(support > raw):
        raise SupportConditionedRawLandscapeError("SUPPORT_VIEW_AMPLITUDE_EXCEEDS_RAW")
    if np.any((support > 0.0) & ~(raw > 0.0)):
        raise SupportConditionedRawLandscapeError("SUPPORT_VIEW_INVENTED_NONZERO_BIN")

    support_templates = {
        midi: dict(v3.evaluate_candidate_template(midi, support, hz))
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    support_valid_midis = sorted(
        midi for midi, row in support_templates.items() if row.get("valid") is True
    )

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
    expected_gate_free = list(range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1))
    if gate_free_midis != expected_gate_free:
        raise SupportConditionedRawLandscapeError("EXPECTED_ALL_49_GATE_FREE_CANDIDATES")

    fixed_feature_bins = sorted(
        {
            int(bin_index)
            for midi in gate_free_midis
            for bin_index in gate_free_templates[midi].get("bins", [])
        }
    )
    if not fixed_feature_bins:
        raise SupportConditionedRawLandscapeError("EMPTY_FIXED_FEATURE_UNIVERSE")
    if fixed_feature_bins[0] < 0 or fixed_feature_bins[-1] >= raw.size:
        raise SupportConditionedRawLandscapeError("FIXED_FEATURE_BIN_OUT_OF_RANGE")

    row_for_bin = {bin_index: row for row, bin_index in enumerate(fixed_feature_bins)}
    observed = np.asarray([raw[index] for index in fixed_feature_bins], dtype=np.float64)
    fixed_feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(fixed_feature_energy) or fixed_feature_energy < v6.MIN_INNOVATION_ENERGY:
        raise SupportConditionedRawLandscapeError("INSUFFICIENT_FIXED_FEATURE_ENERGY")

    dictionary = np.zeros((len(fixed_feature_bins), len(gate_free_midis)), dtype=np.float64)
    for column, midi in enumerate(gate_free_midis):
        template = gate_free_templates[midi]
        bins = list(template.get("bins", []))
        weights = list(template.get("weights", []))
        if len(bins) != len(weights):
            raise SupportConditionedRawLandscapeError(f"MALFORMED_GATE_FREE_TEMPLATE:{midi}")
        for bin_index, weight in zip(bins, weights):
            bin_index = int(bin_index)
            if bin_index not in row_for_bin:
                raise SupportConditionedRawLandscapeError(
                    f"TEMPLATE_BIN_OUTSIDE_FIXED_UNIVERSE:{midi}:{bin_index}"
                )
            dictionary[row_for_bin[bin_index], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        raise SupportConditionedRawLandscapeError(
            f"NNLS_FULL_FAILED:{type(exc).__name__}"
        ) from exc
    coefficients = np.asarray(coefficients, dtype=np.float64)
    full_residual = float(full_residual)
    if (
        coefficients.shape != (len(gate_free_midis),)
        or not np.all(np.isfinite(coefficients))
        or np.any(coefficients < 0.0)
        or not math.isfinite(full_residual)
    ):
        raise SupportConditionedRawLandscapeError("INVALID_FULL_NNLS_RESULT")

    landscape_rows: list[dict[str, Any]] = []
    for candidate_midi in support_valid_midis:
        column = gate_free_midis.index(candidate_midi)
        reduced = np.delete(dictionary, column, axis=1)
        try:
            _reduced_coefficients, without_residual = nnls(reduced, observed)
        except Exception as exc:
            raise SupportConditionedRawLandscapeError(
                f"NNLS_REDUCED_FAILED:{candidate_midi}:{type(exc).__name__}"
            ) from exc
        without_residual = float(without_residual)
        necessity = float(
            (without_residual - full_residual) / max(fixed_feature_energy, 1e-15)
        )
        coefficient = float(coefficients[column])
        if not all(math.isfinite(value) for value in (without_residual, necessity, coefficient)):
            raise SupportConditionedRawLandscapeError(
                f"NONFINITE_CANDIDATE_MEASUREMENT:{candidate_midi}"
            )

        template = support_templates[candidate_midi]
        evidence = dual._candidate_evidence_diagnostic(template, support)
        owners = dual._owner_diagnostics(candidate_midi, template, support_templates)
        if evidence.get("available") is not True or owners.get("available") is not True:
            raise SupportConditionedRawLandscapeError(
                f"SUPPORT_VALID_CANDIDATE_WITHOUT_PROTECTION_DIAGNOSTIC:{candidate_midi}"
            )

        landscape_rows.append(
            {
                "midi": int(candidate_midi),
                "selectedForFixture": bool(candidate_midi == selected_midi),
                "supportTemplate": dict(template),
                "candidateEvidence": evidence,
                "ownerDiagnostics": owners,
                "fullFitCoefficient": coefficient,
                "fullResidual": full_residual,
                "withoutCandidateResidual": without_residual,
                "rawNecessityFraction": necessity,
            }
        )

    for row in landscape_rows:
        necessity = float(row["rawNecessityFraction"])
        coefficient = float(row["fullFitCoefficient"])
        row["strictlyGreaterRawNecessityCount"] = sum(
            1
            for other in landscape_rows
            if float(other["rawNecessityFraction"]) > necessity
        )
        row["strictlyGreaterPositiveCoefficientCount"] = sum(
            1
            for other in landscape_rows
            if float(other["fullFitCoefficient"]) > coefficient
        )

    landscape_rows.sort(
        key=lambda row: (-float(row["rawNecessityFraction"]), int(row["midi"]))
    )
    selected_landscape_row = next(
        (dict(row) for row in landscape_rows if int(row["midi"]) == selected_midi),
        None,
    )

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "rawNecessityThresholdDefined": False,
        "rankCutoffDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "rawNorm": float(np.linalg.norm(raw)),
        "supportNorm": float(np.linalg.norm(support)),
        "supportValidMidis": [int(value) for value in support_valid_midis],
        "fixedRawProblem": {
            "candidateCount": len(gate_free_midis),
            "candidateMidis": [int(value) for value in gate_free_midis],
            "featureBinCount": len(fixed_feature_bins),
            "featureBins": [int(value) for value in fixed_feature_bins],
            "featureEnergy": fixed_feature_energy,
            "fullResidual": full_residual,
            "coefficientRows": [
                {"midi": int(midi), "coefficient": float(coefficients[index])}
                for index, midi in enumerate(gate_free_midis)
            ],
        },
        "landscapeRows": landscape_rows,
        "selectedLandscapeRow": selected_landscape_row,
    }
