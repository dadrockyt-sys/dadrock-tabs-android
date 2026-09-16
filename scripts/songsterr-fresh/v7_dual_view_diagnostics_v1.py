#!/usr/bin/env python3
"""Synthetic-only dual-view diagnostics for the frozen V6 -> V3 representation seam.

This module defines no classifier. Candidate eligibility/templates and owner
geometry come from the frozen iteration-2 peak-band support view. A second,
diagnostic-only NNLS fit uses the same support-derived dictionary against the
untouched raw V6 innovation at the same feature bins.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_DUAL_VIEW_DIAGNOSTIC_PRE.md
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

import physical_template_plausibility_v3 as base
import physical_template_plausibility_v3_iteration2 as owner_guard
import physical_template_plausibility_v3_iteration3 as evidence_guard
import v6_innovation_peak_band_bridge_v2 as support_bridge

CONTRACT = "songsterr-fresh-v7-dual-view-representation-diagnostic-v1"
VERSION = 1

EXPECTED_BASE_CONTRACT = "songsterr-fresh-v3-physical-template-synthetic-research-v1"
EXPECTED_BASE_VERSION = 1
EXPECTED_OWNER_CONTRACT = "songsterr-fresh-v3-physical-template-owner-aware-synthetic-research-v2"
EXPECTED_OWNER_VERSION = 2
EXPECTED_EVIDENCE_CONTRACT = "songsterr-fresh-v3-physical-template-evidence-significance-synthetic-research-v3"
EXPECTED_EVIDENCE_VERSION = 3
EXPECTED_BRIDGE_CONTRACT = "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
EXPECTED_BRIDGE_VERSION = 2


class DualViewDiagnosticError(RuntimeError):
    pass


def _dependency_contract_ok() -> bool:
    return bool(
        getattr(base, "CONTRACT", None) == EXPECTED_BASE_CONTRACT
        and getattr(base, "VERSION", None) == EXPECTED_BASE_VERSION
        and getattr(owner_guard, "CONTRACT", None) == EXPECTED_OWNER_CONTRACT
        and getattr(owner_guard, "VERSION", None) == EXPECTED_OWNER_VERSION
        and getattr(evidence_guard, "CONTRACT", None) == EXPECTED_EVIDENCE_CONTRACT
        and getattr(evidence_guard, "VERSION", None) == EXPECTED_EVIDENCE_VERSION
        and getattr(support_bridge, "CONTRACT", None) == EXPECTED_BRIDGE_CONTRACT
        and getattr(support_bridge, "VERSION", None) == EXPECTED_BRIDGE_VERSION
        and getattr(base, "NECESSITY_FRACTION_MIN", None) == 0.01
        and getattr(evidence_guard, "MIN_CANDIDATE_EVIDENCE_FRACTION", None) == 0.10
        and getattr(owner_guard, "OVERLAP_BIN_RADIUS", None) == 1
        and getattr(owner_guard, "MIN_OWNER_EXCLUSIVE_SUPPORTED", None) == 2
        and getattr(owner_guard, "MIN_SELECTED_EXCLUSIVE_SUPPORTED", None) == 2
        and getattr(support_bridge, "LINE_SUPPRESSION_RADIUS_BINS", None) == 8
        and getattr(support_bridge, "PEAK_BAND_RADIUS_BINS", None) == 1
    )


def _validated_raw(
    raw_innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> tuple[np.ndarray, np.ndarray]:
    if not _dependency_contract_ok():
        raise DualViewDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")

    try:
        raw = np.asarray(raw_innovation, dtype=np.float64)
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise DualViewDiagnosticError(f"INPUT_COERCION_FAILED:{type(exc).__name__}") from exc

    expected_hz = base.expected_frequencies()
    if raw.ndim != 1 or hz.ndim != 1:
        raise DualViewDiagnosticError("RAW_AND_FREQUENCIES_MUST_BE_1D")
    if raw.shape != hz.shape or raw.shape != expected_hz.shape:
        raise DualViewDiagnosticError("RAW_FREQUENCY_SHAPE_MISMATCH")
    if not np.all(np.isfinite(raw)) or not np.all(np.isfinite(hz)):
        raise DualViewDiagnosticError("NONFINITE_RAW_OR_FREQUENCY")
    if np.any(raw < 0.0):
        raise DualViewDiagnosticError("RAW_INNOVATION_MUST_BE_NONNEGATIVE")
    if not np.allclose(hz, expected_hz, rtol=0.0, atol=1e-12):
        raise DualViewDiagnosticError("FREQUENCY_GRID_MISMATCH")
    raw_norm = float(np.linalg.norm(raw))
    if not math.isfinite(raw_norm) or raw_norm < base.MIN_INNOVATION_NORM:
        raise DualViewDiagnosticError("RAW_INNOVATION_INSUFFICIENT")
    return raw, hz


def _candidate_evidence_diagnostic(
    selected_template: dict[str, Any],
    support: np.ndarray,
) -> dict[str, Any]:
    if selected_template.get("valid") is not True:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_SUPPORT_TEMPLATE_INELIGIBLE",
        }

    peaks = list(selected_template.get("observedHarmonicInnovation", []))
    thresholds = list(selected_template.get("supportThresholds", []))
    supported = list(selected_template.get("supported", []))
    if not peaks or len(peaks) != len(thresholds) or len(peaks) != len(supported):
        return {
            "available": False,
            "availabilityStatus": "MALFORMED_SELECTED_SUPPORT_TEMPLATE",
        }

    support_norm = float(np.linalg.norm(support))
    excess = [
        max(0.0, float(peak) - float(threshold)) if flag is True else 0.0
        for peak, threshold, flag in zip(peaks, thresholds, supported)
    ]
    excess_norm = float(np.linalg.norm(np.asarray(excess, dtype=np.float64)))
    fraction = float(excess_norm / support_norm) if support_norm > 0.0 else float("nan")
    if not (
        math.isfinite(support_norm)
        and support_norm > 0.0
        and math.isfinite(excess_norm)
        and math.isfinite(fraction)
        and fraction >= 0.0
    ):
        return {
            "available": False,
            "availabilityStatus": "NONFINITE_SUPPORT_EVIDENCE_DIAGNOSTIC",
        }
    return {
        "available": True,
        "availabilityStatus": "AVAILABLE",
        "supportNorm": support_norm,
        "supportedExcess": [float(value) for value in excess],
        "supportedExcessNorm": excess_norm,
        "candidateEvidenceFraction": fraction,
        "frozenReferenceMinimum": float(evidence_guard.MIN_CANDIDATE_EVIDENCE_FRACTION),
    }


def _owner_diagnostics(
    selected_midi: int,
    selected_template: dict[str, Any],
    templates: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    if selected_template.get("valid") is not True:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_SUPPORT_TEMPLATE_INELIGIBLE",
            "ownerRows": [],
            "credibleOwnerRows": [],
            "vetoOwnerRows": [],
        }

    owner_rows: list[dict[str, Any]] = []
    credible_rows: list[dict[str, Any]] = []
    veto_rows: list[dict[str, Any]] = []
    for owner_midi in range(base.PLAYABLE_MIDI_MIN, int(selected_midi)):
        owner_template = templates[owner_midi]
        if owner_template.get("valid") is not True:
            continue
        owner_exclusive = owner_guard._exclusive_supported_bins(owner_template, selected_template)
        selected_exclusive = owner_guard._exclusive_supported_bins(selected_template, owner_template)
        credible = len(owner_exclusive) >= owner_guard.MIN_OWNER_EXCLUSIVE_SUPPORTED
        veto = bool(
            credible
            and len(selected_exclusive) < owner_guard.MIN_SELECTED_EXCLUSIVE_SUPPORTED
        )
        row = {
            "ownerMidi": int(owner_midi),
            "ownerCents": float(owner_template.get("cents", 0.0)),
            "ownerExclusiveSupportedBins": [int(value) for value in owner_exclusive],
            "ownerExclusiveSupportedCount": len(owner_exclusive),
            "selectedExclusiveSupportedBins": [int(value) for value in selected_exclusive],
            "selectedExclusiveSupportedCount": len(selected_exclusive),
            "credible": bool(credible),
            "veto": bool(veto),
        }
        owner_rows.append(row)
        if credible:
            credible_rows.append(row)
        if veto:
            veto_rows.append(row)

    return {
        "available": True,
        "availabilityStatus": "AVAILABLE",
        "ownerRows": owner_rows,
        "credibleOwnerRows": credible_rows,
        "vetoOwnerRows": veto_rows,
    }


def _dual_view_fit(
    selected_midi: int,
    raw: np.ndarray,
    templates: dict[int, dict[str, Any]],
    valid_midis: list[int],
) -> dict[str, Any]:
    if int(selected_midi) not in valid_midis:
        return {
            "available": False,
            "availabilityStatus": "SELECTED_SUPPORT_TEMPLATE_INELIGIBLE",
        }

    feature_bins = sorted(
        {
            int(bin_index)
            for midi in valid_midis
            for bin_index in templates[midi].get("bins", [])
        }
    )
    if not feature_bins:
        return {
            "available": False,
            "availabilityStatus": "NO_SUPPORT_DERIVED_FEATURE_BINS",
        }
    if feature_bins[0] < 0 or feature_bins[-1] >= raw.size:
        raise DualViewDiagnosticError("SUPPORT_DERIVED_FEATURE_BIN_OUT_OF_RANGE")

    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([raw[index] for index in feature_bins], dtype=np.float64)
    raw_feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(raw_feature_energy) or raw_feature_energy < base.MIN_INNOVATION_NORM:
        return {
            "available": False,
            "availabilityStatus": "INSUFFICIENT_RAW_FEATURE_ENERGY",
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "rawFeatureEnergy": raw_feature_energy,
        }

    dictionary = np.zeros((len(feature_bins), len(valid_midis)), dtype=np.float64)
    for column, midi in enumerate(valid_midis):
        template = templates[midi]
        bins = list(template.get("bins", []))
        weights = list(template.get("weights", []))
        if len(bins) != len(weights):
            raise DualViewDiagnosticError(f"MALFORMED_SUPPORT_TEMPLATE:{midi}")
        for bin_index, weight in zip(bins, weights):
            dictionary[row_for_bin[int(bin_index)], column] += float(weight)

    try:
        coefficients, full_residual = nnls(dictionary, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_FULL_FAILED:{type(exc).__name__}",
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "rawFeatureEnergy": raw_feature_energy,
        }

    selected_column = valid_midis.index(int(selected_midi))
    reduced = np.delete(dictionary, selected_column, axis=1)
    if reduced.shape[1] == 0:
        return {
            "available": False,
            "availabilityStatus": "REDUCED_DICTIONARY_EMPTY",
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "rawFeatureEnergy": raw_feature_energy,
        }
    try:
        _without_coefficients, without_residual = nnls(reduced, observed)
    except Exception as exc:
        return {
            "available": False,
            "availabilityStatus": f"NNLS_REDUCED_FAILED:{type(exc).__name__}",
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "rawFeatureEnergy": raw_feature_energy,
        }

    selected_coefficient = float(coefficients[selected_column])
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    necessity_fraction = float(
        (without_residual - full_residual) / max(raw_feature_energy, 1e-15)
    )
    values = (selected_coefficient, full_residual, without_residual, necessity_fraction)
    if not all(math.isfinite(value) for value in values):
        return {
            "available": False,
            "availabilityStatus": "NONFINITE_DUAL_VIEW_FIT",
            "featureBinCount": len(feature_bins),
            "featureBins": feature_bins,
            "rawFeatureEnergy": raw_feature_energy,
        }

    return {
        "available": True,
        "availabilityStatus": "AVAILABLE",
        "validCandidateCount": len(valid_midis),
        "validCandidateMidis": [int(value) for value in valid_midis],
        "featureBinCount": len(feature_bins),
        "featureBins": feature_bins,
        "rawFeatureEnergy": raw_feature_energy,
        "selectedCoefficient": selected_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "rawNecessityFraction": necessity_fraction,
        "frozenReferenceNecessityMinimum": float(base.NECESSITY_FRACTION_MIN),
    }


def evaluate_dual_view_diagnostics(
    selected_midi: int,
    raw_innovation: np.ndarray | list[float],
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return diagnostics only. No combined dual-view verdict is defined."""

    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise DualViewDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    selected_midi = int(selected_midi)
    if not base.PLAYABLE_MIDI_MIN <= selected_midi <= base.PLAYABLE_MIDI_MAX:
        raise DualViewDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    raw, hz = _validated_raw(raw_innovation, frequencies)
    support = support_bridge.collapse_hann_lobes_to_peak_bands(raw)
    if support.shape != raw.shape or not np.all(np.isfinite(support)) or np.any(support < 0.0):
        raise DualViewDiagnosticError("INVALID_SUPPORT_VIEW")
    if np.any(support > raw):
        raise DualViewDiagnosticError("SUPPORT_VIEW_AMPLITUDE_EXCEEDS_RAW")
    if np.any((support > 0.0) & ~(raw > 0.0)):
        raise DualViewDiagnosticError("SUPPORT_VIEW_INVENTED_NONZERO_BIN")

    templates = {
        midi: base.evaluate_candidate_template(midi, support, hz)
        for midi in range(base.PLAYABLE_MIDI_MIN, base.PLAYABLE_MIDI_MAX + 1)
    }
    valid_midis = sorted(midi for midi, row in templates.items() if row.get("valid") is True)
    selected_template = templates[selected_midi]

    support_composite = evidence_guard.evaluate_evidence_significance_composite(
        selected_midi,
        support,
        hz,
    )
    owners = _owner_diagnostics(selected_midi, selected_template, templates)
    evidence = _candidate_evidence_diagnostic(selected_template, support)
    dual_fit = _dual_view_fit(selected_midi, raw, templates, valid_midis)
    bridge_info = support_bridge.bridge_diagnostics(raw)

    raw_norm = float(np.linalg.norm(raw))
    support_norm = float(np.linalg.norm(support))
    if not all(math.isfinite(value) and value >= 0.0 for value in (raw_norm, support_norm)):
        raise DualViewDiagnosticError("NONFINITE_VIEW_NORM")

    selected_template_copy = dict(selected_template)
    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "rawView": {
            "norm": raw_norm,
            "positiveBinCount": int(np.count_nonzero(raw > 0.0)),
        },
        "supportView": {
            "norm": support_norm,
            "positiveBinCount": int(np.count_nonzero(support > 0.0)),
            "retainedCenterCount": int(bridge_info["centerCount"]),
            "retainedCenters": list(bridge_info["centers"]),
            "selectedTemplate": selected_template_copy,
            "validCandidateCount": len(valid_midis),
            "validCandidateMidis": [int(value) for value in valid_midis],
            "frozenComposite": support_composite,
            "candidateEvidence": evidence,
            "ownerDiagnostics": owners,
        },
        "dualViewFit": dual_fit,
    }
