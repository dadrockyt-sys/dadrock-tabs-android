#!/usr/bin/env python3
"""Synthetic-only protection/raw-fit seam diagnostics.

Prospectively frozen by
SONGSTERR_FRESH_V7_PROTECTION_FIT_SEAM_DIAGNOSTIC_PRE.md.

This module defines no successor classifier. It places the already-frozen
support-side V3/dual-view measurements beside the already-frozen all-gate-free
fixed-feature raw NNLS fit, while carrying historical V7 only as a reference.
"""

from __future__ import annotations

from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import onset_birth_corroboration_v7 as historical_v7
import v7_dual_view_diagnostics_v1 as dual
import v7_fixed_feature_competition_diagnostics_v1 as fixed

CONTRACT = "songsterr-fresh-v7-protection-fit-seam-diagnostic-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_HISTORICAL_V7_CONTRACT = "songsterr-fresh-onset-birth-v3-successor-integration-research-v7"
EXPECTED_HISTORICAL_V7_VERSION = 7
EXPECTED_DUAL_CONTRACT = "songsterr-fresh-v7-dual-view-representation-diagnostic-v1"
EXPECTED_DUAL_VERSION = 1
EXPECTED_FIXED_CONTRACT = "songsterr-fresh-v7-fixed-feature-competition-diagnostic-v1"
EXPECTED_FIXED_VERSION = 1


class ProtectionFitSeamDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(historical_v7, "CONTRACT", None) == EXPECTED_HISTORICAL_V7_CONTRACT
        and getattr(historical_v7, "VERSION", None) == EXPECTED_HISTORICAL_V7_VERSION
        and getattr(dual, "CONTRACT", None) == EXPECTED_DUAL_CONTRACT
        and getattr(dual, "VERSION", None) == EXPECTED_DUAL_VERSION
        and getattr(fixed, "CONTRACT", None) == EXPECTED_FIXED_CONTRACT
        and getattr(fixed, "VERSION", None) == EXPECTED_FIXED_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
    )


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise ProtectionFitSeamDiagnosticError(
            f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise ProtectionFitSeamDiagnosticError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise ProtectionFitSeamDiagnosticError("FREQUENCY_GRID_MISMATCH")
    return hz


def evaluate_protection_fit_seam(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return frozen support protections beside frozen broad raw-fit evidence."""

    if not _contracts_ok():
        raise ProtectionFitSeamDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise ProtectionFitSeamDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise ProtectionFitSeamDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise ProtectionFitSeamDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise ProtectionFitSeamDiagnosticError(
            f"AUDIO_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise ProtectionFitSeamDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")

    hz = _validated_frequencies(frequencies)

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
            "supportMeasurements": None,
            "rawFixedFit": None,
            "historicalReferences": None,
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
            "supportMeasurements": None,
            "rawFixedFit": None,
            "historicalReferences": None,
        }

    raw = np.asarray(onset.get("innovation"), dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise ProtectionFitSeamDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")

    dual_payload = dual.evaluate_dual_view_diagnostics(selected_midi, raw, hz)
    if dual_payload.get("finalDecisionDefined") is not False:
        raise ProtectionFitSeamDiagnosticError("DUAL_VIEW_DEFINED_FINAL_DECISION")

    fixed_payload = fixed.evaluate_fixed_feature_competition_diagnostic(
        values,
        onset_sample,
        selected_midi,
        hz,
    )
    if fixed_payload.get("finalDecisionDefined") is not False:
        raise ProtectionFitSeamDiagnosticError("FIXED_FEATURE_DEFINED_FINAL_DECISION")
    if fixed_payload.get("onsetAvailable") is not True:
        raise ProtectionFitSeamDiagnosticError("FIXED_FEATURE_ONSET_AVAILABILITY_MISMATCH")

    support_view = dual_payload.get("supportView")
    if not isinstance(support_view, dict):
        raise ProtectionFitSeamDiagnosticError("DUAL_SUPPORT_VIEW_MISSING")
    owner_diagnostics = support_view.get("ownerDiagnostics")
    candidate_evidence = support_view.get("candidateEvidence")
    selected_template = support_view.get("selectedTemplate")
    if not isinstance(owner_diagnostics, dict):
        raise ProtectionFitSeamDiagnosticError("OWNER_DIAGNOSTICS_MISSING")
    if not isinstance(candidate_evidence, dict):
        raise ProtectionFitSeamDiagnosticError("CANDIDATE_EVIDENCE_MISSING")
    if not isinstance(selected_template, dict):
        raise ProtectionFitSeamDiagnosticError("SELECTED_SUPPORT_TEMPLATE_MISSING")

    fixed_fits = fixed_payload.get("fixedFeatureFits")
    if not isinstance(fixed_fits, dict):
        raise ProtectionFitSeamDiagnosticError("FIXED_FEATURE_FITS_MISSING")
    gate_free_fixed = fixed_fits.get("gateFree49FixedFit")
    if not isinstance(gate_free_fixed, dict):
        raise ProtectionFitSeamDiagnosticError("GATE_FREE_FIXED_FIT_MISSING")

    historical_v7_reference = historical_v7.evaluate_in_memory_innovation(
        selected_midi,
        raw,
        hz,
    )
    if not isinstance(historical_v7_reference, dict):
        raise ProtectionFitSeamDiagnosticError("HISTORICAL_V7_REFERENCE_NOT_MAPPING")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "supportMeasurements": {
            "rawView": dual_payload.get("rawView"),
            "supportNorm": support_view.get("norm"),
            "supportPositiveBinCount": support_view.get("positiveBinCount"),
            "retainedCenterCount": support_view.get("retainedCenterCount"),
            "retainedCenters": list(support_view.get("retainedCenters", [])),
            "selectedTemplate": dict(selected_template),
            "validCandidateCount": support_view.get("validCandidateCount"),
            "validCandidateMidis": list(support_view.get("validCandidateMidis", [])),
            "ownerDiagnostics": owner_diagnostics,
            "candidateEvidence": candidate_evidence,
        },
        "rawFixedFit": gate_free_fixed,
        "historicalReferences": {
            "dualViewPayload": dual_payload,
            "fixedFeaturePayload": fixed_payload,
            "historicalV7RawComposite": historical_v7_reference,
        },
    }
