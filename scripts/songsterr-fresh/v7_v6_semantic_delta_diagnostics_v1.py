#!/usr/bin/env python3
"""Synthetic-only semantic-delta diagnostics: frozen V6 versus V3/dual-view.

This module defines no successor decision rule. It exposes namespaced frozen V6
component outputs beside frozen V3/dual-view diagnostics for the same in-memory
audio event.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3_base
import v7_dual_view_diagnostics_v1 as dual

CONTRACT = "songsterr-fresh-v7-v6-semantic-delta-diagnostic-v1"
VERSION = 1

EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_DUAL_CONTRACT = "songsterr-fresh-v7-dual-view-representation-diagnostic-v1"
EXPECTED_DUAL_VERSION = 1


class SemanticDeltaDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(dual, "CONTRACT", None) == EXPECTED_DUAL_CONTRACT
        and getattr(dual, "VERSION", None) == EXPECTED_DUAL_VERSION
        and getattr(v6, "TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN", None) == 0.20
        and getattr(v6, "NECESSITY_FRACTION_MIN", None) == 0.01
    )


def _finite_audio(audio: np.ndarray | list[float]) -> np.ndarray:
    try:
        values = np.asarray(audio, dtype=np.float64)
    except Exception as exc:
        raise SemanticDeltaDiagnosticError(f"AUDIO_COERCION_FAILED:{type(exc).__name__}") from exc
    if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)):
        raise SemanticDeltaDiagnosticError("FINITE_MONO_AUDIO_REQUIRED")
    return values


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    try:
        hz = np.asarray(frequencies, dtype=np.float64)
    except Exception as exc:
        raise SemanticDeltaDiagnosticError(f"FREQUENCY_COERCION_FAILED:{type(exc).__name__}") from exc
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.ndim != 1 or hz.shape != expected.shape or not np.all(np.isfinite(hz)):
        raise SemanticDeltaDiagnosticError("INVALID_FREQUENCY_GRID")
    if not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise SemanticDeltaDiagnosticError("FREQUENCY_GRID_MISMATCH")
    if not np.allclose(hz, v3_base.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise SemanticDeltaDiagnosticError("V6_V3_FREQUENCY_GRID_MISMATCH")
    return hz


def _selected_raw_template(
    selected_midi: int,
    raw: np.ndarray,
    frequencies: np.ndarray,
) -> dict[str, Any]:
    row = dict(v6._candidate_template(selected_midi, raw, frequencies))
    if "observedHarmonicInnovation" in row:
        row["observedHarmonicInnovation"] = [
            float(value) for value in row["observedHarmonicInnovation"]
        ]
    if "weights" in row:
        row["weights"] = [float(value) for value in row["weights"]]
    if "bins" in row:
        row["bins"] = [int(value) for value in row["bins"]]
    return row


def evaluate_semantic_delta(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Return frozen component diagnostics only; no successor verdict is defined."""

    if not _contracts_ok():
        raise SemanticDeltaDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise SemanticDeltaDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise SemanticDeltaDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise SemanticDeltaDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    values = _finite_audio(audio)
    hz = _validated_frequencies(frequencies)

    historical = v6.classify_audio_event(values, onset_sample, selected_midi)
    historical_fit = historical.get("fit") if isinstance(historical.get("fit"), dict) else None

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
            "frozenV6FitComponent": historical_fit,
            "frozenV6SelectedRawTemplate": None,
            "dualViewDiagnostic": None,
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
            "frozenV6FitComponent": historical_fit,
            "frozenV6SelectedRawTemplate": None,
            "dualViewDiagnostic": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.ndim != 1 or raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise SemanticDeltaDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")
    raw_norm = float(np.linalg.norm(raw))
    if not math.isfinite(raw_norm) or raw_norm < v6.MIN_INNOVATION_ENERGY:
        raise SemanticDeltaDiagnosticError("UNEXPECTED_LOW_RAW_INNOVATION")

    selected_raw_template = _selected_raw_template(selected_midi, raw, hz)
    dual_payload = dual.evaluate_dual_view_diagnostics(selected_midi, raw, hz)
    if dual_payload.get("finalDecisionDefined") is not False:
        raise SemanticDeltaDiagnosticError("DUAL_DIAGNOSTIC_DEFINED_FINAL_DECISION")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "rawPositiveBinCount": int(np.count_nonzero(raw > 0.0)),
        "frozenV6HistoricalComponent": historical,
        "frozenV6FitComponent": historical_fit,
        "frozenV6SelectedRawTemplate": selected_raw_template,
        "dualViewDiagnostic": dual_payload,
        "historicalV6FundamentalRatioThresholdReferenceOnly": float(
            v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN
        ),
        "historicalV6NecessityThresholdReferenceOnly": float(v6.NECESSITY_FRACTION_MIN),
    }
