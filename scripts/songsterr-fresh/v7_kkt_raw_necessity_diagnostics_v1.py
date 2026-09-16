#!/usr/bin/env python3
"""Synthetic-only KKT strict-necessity diagnostics for broad raw NNLS.

Prospectively frozen by
SONGSTERR_FRESH_V7_KKT_RAW_NECESSITY_DIAGNOSTIC_PRE.md.

This module defines no final successor classifier and applies no scientific
raw-magnitude threshold.  It asks whether the omitted selected raw template is
an NNLS descent direction beyond the reduced solver's own KKT stationarity
floor plus deterministic float64 arithmetic bounds.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy.optimize import nnls

import onset_birth_corroboration_v6 as v6
import v7_gate_free_competition_diagnostics_v1 as gatefree
import v7_support_conditioned_raw_necessity_landscape_v1 as landscape

CONTRACT = "songsterr-fresh-v7-kkt-raw-necessity-diagnostic-v1"
VERSION = 1
EXPECTED_V6_CONTRACT = "songsterr-fresh-onset-birth-complex-harmonic-corroboration-research-v6"
EXPECTED_V6_VERSION = 6
EXPECTED_GATEFREE_CONTRACT = "songsterr-fresh-v7-gate-free-competition-diagnostic-v1"
EXPECTED_GATEFREE_VERSION = 1
EXPECTED_LANDSCAPE_CONTRACT = "songsterr-fresh-v7-support-conditioned-raw-necessity-landscape-v1"
EXPECTED_LANDSCAPE_VERSION = 1
FLOAT64_UNIT_ROUNDOFF = float(np.finfo(np.float64).eps / 2.0)


class KktRawNecessityDiagnosticError(RuntimeError):
    pass


def _contracts_ok() -> bool:
    return bool(
        getattr(v6, "CONTRACT", None) == EXPECTED_V6_CONTRACT
        and getattr(v6, "VERSION", None) == EXPECTED_V6_VERSION
        and getattr(gatefree, "CONTRACT", None) == EXPECTED_GATEFREE_CONTRACT
        and getattr(gatefree, "VERSION", None) == EXPECTED_GATEFREE_VERSION
        and getattr(landscape, "CONTRACT", None) == EXPECTED_LANDSCAPE_CONTRACT
        and getattr(landscape, "VERSION", None) == EXPECTED_LANDSCAPE_VERSION
        and getattr(v6, "PLAYABLE_MIDI_MIN", None) == 40
        and getattr(v6, "PLAYABLE_MIDI_MAX", None) == 88
    )


def _gamma(count: int) -> float:
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)):
        raise KktRawNecessityDiagnosticError("GAMMA_COUNT_INTEGER_REQUIRED")
    count = int(count)
    if count < 0:
        raise KktRawNecessityDiagnosticError("GAMMA_COUNT_NONNEGATIVE_REQUIRED")
    product = float(count) * FLOAT64_UNIT_ROUNDOFF
    if product >= 1.0:
        raise KktRawNecessityDiagnosticError("GAMMA_COUNT_TOO_LARGE")
    if count == 0:
        return 0.0
    return float(product / (1.0 - product))


def _finite_vector(value: np.ndarray | list[float], name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except Exception as exc:
        raise KktRawNecessityDiagnosticError(
            f"{name}_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if array.ndim != 1 or not np.all(np.isfinite(array)):
        raise KktRawNecessityDiagnosticError(f"FINITE_VECTOR_REQUIRED:{name}")
    return array


def _finite_matrix(value: np.ndarray | list[list[float]], name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except Exception as exc:
        raise KktRawNecessityDiagnosticError(
            f"{name}_COERCION_FAILED:{type(exc).__name__}"
        ) from exc
    if array.ndim != 2 or not np.all(np.isfinite(array)):
        raise KktRawNecessityDiagnosticError(f"FINITE_MATRIX_REQUIRED:{name}")
    return array


def _fsum_dot(left: np.ndarray, right: np.ndarray) -> float:
    if left.shape != right.shape or left.ndim != 1:
        raise KktRawNecessityDiagnosticError("FSUM_DOT_SHAPE_MISMATCH")
    return float(math.fsum(float(a) * float(b) for a, b in zip(left, right)))


def _column_norm(column: np.ndarray) -> float:
    squared = math.fsum(float(value) * float(value) for value in column)
    norm = float(math.sqrt(max(0.0, squared)))
    if not math.isfinite(norm) or norm <= 0.0:
        raise KktRawNecessityDiagnosticError("NONPOSITIVE_COLUMN_NORM")
    return norm


def _reduced_residual_with_bounds(
    reduced: np.ndarray,
    coefficients: np.ndarray,
    observed: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rows, columns = reduced.shape
    if coefficients.shape != (columns,) or observed.shape != (rows,):
        raise KktRawNecessityDiagnosticError("REDUCED_RESIDUAL_SHAPE_MISMATCH")
    gamma_columns = _gamma(columns)
    fitted = np.zeros(rows, dtype=np.float64)
    residual = np.zeros(rows, dtype=np.float64)
    residual_bound = np.zeros(rows, dtype=np.float64)

    for row in range(rows):
        products = [
            float(reduced[row, column]) * float(coefficients[column])
            for column in range(columns)
        ]
        predicted = float(math.fsum(products))
        sum_abs = float(math.fsum(abs(value) for value in products))
        prediction_bound = float(gamma_columns * sum_abs)
        remainder = float(observed[row] - predicted)
        subtraction_bound = float(
            FLOAT64_UNIT_ROUNDOFF
            * (abs(float(observed[row])) + abs(predicted) + prediction_bound)
        )
        bound = float(prediction_bound + subtraction_bound)
        if not all(math.isfinite(value) and value >= 0.0 for value in (sum_abs, prediction_bound, subtraction_bound, bound)):
            raise KktRawNecessityDiagnosticError("NONFINITE_RESIDUAL_ERROR_BOUND")
        if not math.isfinite(predicted) or not math.isfinite(remainder):
            raise KktRawNecessityDiagnosticError("NONFINITE_RECOMPUTED_RESIDUAL")
        fitted[row] = predicted
        residual[row] = remainder
        residual_bound[row] = bound

    return fitted, residual, residual_bound


def _correlation_interval(
    column: np.ndarray,
    residual: np.ndarray,
    residual_bound: np.ndarray,
) -> dict[str, float]:
    if column.shape != residual.shape or residual.shape != residual_bound.shape:
        raise KktRawNecessityDiagnosticError("CORRELATION_SHAPE_MISMATCH")
    products = [float(a) * float(r) for a, r in zip(column, residual)]
    correlation = float(math.fsum(products))
    sum_abs_products = float(math.fsum(abs(value) for value in products))
    propagated_residual_bound = float(
        math.fsum(
            abs(float(a)) * float(bound)
            for a, bound in zip(column, residual_bound)
        )
    )
    arithmetic_bound = float(
        _gamma(column.size) * sum_abs_products + propagated_residual_bound
    )
    scale = _column_norm(column)
    values = (correlation, sum_abs_products, propagated_residual_bound, arithmetic_bound, scale)
    if not all(math.isfinite(value) and value >= 0.0 for value in values[1:]):
        raise KktRawNecessityDiagnosticError("NONFINITE_CORRELATION_BOUND")
    if not math.isfinite(correlation):
        raise KktRawNecessityDiagnosticError("NONFINITE_CORRELATION")
    return {
        "correlation": correlation,
        "sumAbsProducts": sum_abs_products,
        "propagatedResidualBound": propagated_residual_bound,
        "arithmeticBound": arithmetic_bound,
        "columnNorm": scale,
        "normalizedLowerBound": float((correlation - arithmetic_bound) / scale),
        "normalizedUpperBound": float((correlation + arithmetic_bound) / scale),
    }


def certify_omitted_column_nnls(
    dictionary: np.ndarray | list[list[float]],
    observed: np.ndarray | list[float],
    selected_column: int,
) -> dict[str, Any]:
    """Return a KKT strict-necessity certificate for one omitted NNLS column."""

    matrix = _finite_matrix(dictionary, "DICTIONARY")
    target = _finite_vector(observed, "OBSERVED")
    rows, columns = matrix.shape
    if rows == 0 or columns < 2 or target.shape != (rows,):
        raise KktRawNecessityDiagnosticError("NNLS_PROBLEM_SHAPE_INVALID")
    if np.any(matrix < 0.0) or np.any(target < 0.0):
        raise KktRawNecessityDiagnosticError("NONNEGATIVE_NNLS_INPUT_REQUIRED")
    if isinstance(selected_column, bool) or not isinstance(selected_column, (int, np.integer)):
        raise KktRawNecessityDiagnosticError("SELECTED_COLUMN_INTEGER_REQUIRED")
    selected_column = int(selected_column)
    if not 0 <= selected_column < columns:
        raise KktRawNecessityDiagnosticError("SELECTED_COLUMN_OUT_OF_RANGE")
    for index in range(columns):
        _column_norm(matrix[:, index])

    try:
        full_coefficients, full_residual = nnls(matrix, target)
    except Exception as exc:
        raise KktRawNecessityDiagnosticError(
            f"NNLS_FULL_FAILED:{type(exc).__name__}"
        ) from exc
    reduced = np.delete(matrix, selected_column, axis=1)
    try:
        reduced_coefficients, without_residual = nnls(reduced, target)
    except Exception as exc:
        raise KktRawNecessityDiagnosticError(
            f"NNLS_REDUCED_FAILED:{type(exc).__name__}"
        ) from exc

    full_coefficients = np.asarray(full_coefficients, dtype=np.float64)
    reduced_coefficients = np.asarray(reduced_coefficients, dtype=np.float64)
    full_residual = float(full_residual)
    without_residual = float(without_residual)
    if (
        full_coefficients.shape != (columns,)
        or reduced_coefficients.shape != (columns - 1,)
        or not np.all(np.isfinite(full_coefficients))
        or not np.all(np.isfinite(reduced_coefficients))
        or np.any(full_coefficients < 0.0)
        or np.any(reduced_coefficients < 0.0)
        or not math.isfinite(full_residual)
        or not math.isfinite(without_residual)
    ):
        raise KktRawNecessityDiagnosticError("INVALID_NNLS_RESULT")

    _fitted, residual, residual_bound = _reduced_residual_with_bounds(
        reduced,
        reduced_coefficients,
        target,
    )

    reduced_original_indices = [index for index in range(columns) if index != selected_column]
    reduced_rows: list[dict[str, Any]] = []
    reduced_floor = 0.0
    for reduced_index, original_index in enumerate(reduced_original_indices):
        interval = _correlation_interval(
            matrix[:, original_index],
            residual,
            residual_bound,
        )
        coefficient = float(reduced_coefficients[reduced_index])
        if coefficient > 0.0:
            defect = float(
                (abs(interval["correlation"]) + interval["arithmeticBound"])
                / interval["columnNorm"]
            )
            activity = "ACTIVE"
        else:
            defect = float(max(0.0, interval["normalizedUpperBound"]))
            activity = "INACTIVE"
        if not math.isfinite(defect) or defect < 0.0:
            raise KktRawNecessityDiagnosticError("INVALID_REDUCED_KKT_DEFECT")
        reduced_floor = max(reduced_floor, defect)
        reduced_rows.append(
            {
                "originalColumn": int(original_index),
                "reducedCoefficient": coefficient,
                "activity": activity,
                "correlation": interval["correlation"],
                "correlationArithmeticBound": interval["arithmeticBound"],
                "normalizedCorrelationLowerBound": interval["normalizedLowerBound"],
                "normalizedCorrelationUpperBound": interval["normalizedUpperBound"],
                "normalizedKktDefectUpperBound": defect,
            }
        )

    selected_interval = _correlation_interval(
        matrix[:, selected_column],
        residual,
        residual_bound,
    )
    selected_lower = float(selected_interval["normalizedLowerBound"])
    certified = bool(selected_lower > max(0.0, reduced_floor))
    selected_full_coefficient = float(full_coefficients[selected_column])
    strict_residual_improvement = bool(without_residual > full_residual)
    consistency_ok = bool(
        (not certified)
        or (selected_full_coefficient > 0.0 and strict_residual_improvement)
    )

    feature_energy = float(np.linalg.norm(target))
    descriptive_necessity = None
    if math.isfinite(feature_energy) and feature_energy > 0.0:
        descriptive_necessity = float(
            (without_residual - full_residual) / feature_energy
        )
        if not math.isfinite(descriptive_necessity):
            raise KktRawNecessityDiagnosticError("NONFINITE_DESCRIPTIVE_NECESSITY")

    return {
        "available": bool(consistency_ok),
        "availabilityStatus": (
            "AVAILABLE"
            if consistency_ok
            else "KKT_CERTIFICATE_FULL_FIT_INCONSISTENT"
        ),
        "rowCount": int(rows),
        "columnCount": int(columns),
        "selectedColumn": int(selected_column),
        "float64UnitRoundoff": FLOAT64_UNIT_ROUNDOFF,
        "featureEnergy": feature_energy,
        "selectedFullCoefficient": selected_full_coefficient,
        "fullResidual": full_residual,
        "withoutSelectedResidual": without_residual,
        "strictResidualImprovement": strict_residual_improvement,
        "descriptiveRawNecessityFraction": descriptive_necessity,
        "selectedCorrelation": selected_interval["correlation"],
        "selectedCorrelationArithmeticBound": selected_interval["arithmeticBound"],
        "selectedNormalizedCorrelationLowerBound": selected_lower,
        "selectedNormalizedCorrelationUpperBound": selected_interval["normalizedUpperBound"],
        "reducedKktDefectFloor": float(reduced_floor),
        "kktCertifiedStrictRawNecessity": certified,
        "consistencyOk": consistency_ok,
        "reducedColumnDiagnostics": reduced_rows,
    }


def _validated_frequencies(frequencies: np.ndarray | list[float]) -> np.ndarray:
    hz = _finite_vector(frequencies, "FREQUENCIES")
    expected = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if hz.shape != expected.shape or not np.allclose(hz, expected, rtol=0.0, atol=1e-12):
        raise KktRawNecessityDiagnosticError("FREQUENCY_GRID_MISMATCH")
    return hz


def _build_all49_fixed_problem(
    raw: np.ndarray,
    frequencies: np.ndarray,
) -> tuple[list[int], list[int], np.ndarray, np.ndarray]:
    templates = {
        midi: gatefree.gate_free_competition_template(midi, raw, frequencies)
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
    }
    midis = sorted(
        midi
        for midi, row in templates.items()
        if row.get("structurallyConstructible") is True
        and row.get("admittedToGateFreeCompetition") is True
    )
    expected = list(range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1))
    if midis != expected:
        raise KktRawNecessityDiagnosticError("EXPECTED_ALL_49_GATE_FREE_CANDIDATES")
    feature_bins = sorted(
        {
            int(bin_index)
            for midi in midis
            for bin_index in templates[midi].get("bins", [])
        }
    )
    if not feature_bins or feature_bins[0] < 0 or feature_bins[-1] >= raw.size:
        raise KktRawNecessityDiagnosticError("INVALID_FIXED_FEATURE_UNIVERSE")
    row_for_bin = {bin_index: row for row, bin_index in enumerate(feature_bins)}
    observed = np.asarray([raw[index] for index in feature_bins], dtype=np.float64)
    dictionary = np.zeros((len(feature_bins), len(midis)), dtype=np.float64)
    for column, midi in enumerate(midis):
        bins = list(templates[midi].get("bins", []))
        weights = list(templates[midi].get("weights", []))
        if len(bins) != len(weights):
            raise KktRawNecessityDiagnosticError(f"MALFORMED_TEMPLATE:{midi}")
        for bin_index, weight in zip(bins, weights):
            index = int(bin_index)
            if index not in row_for_bin:
                raise KktRawNecessityDiagnosticError(
                    f"TEMPLATE_BIN_OUTSIDE_FIXED_UNIVERSE:{midi}:{index}"
                )
            dictionary[row_for_bin[index], column] += float(weight)
    return midis, feature_bins, observed, dictionary


def evaluate_kkt_raw_necessity_diagnostic(
    audio: np.ndarray | list[float],
    onset_sample: int,
    selected_midi: int,
    frequencies: np.ndarray | list[float],
) -> dict[str, Any]:
    """Evaluate broad raw KKT necessity only; define no final successor verdict."""

    if not _contracts_ok():
        raise KktRawNecessityDiagnosticError("FROZEN_DEPENDENCY_CONTRACT_MISMATCH")
    if isinstance(onset_sample, bool) or not isinstance(onset_sample, (int, np.integer)):
        raise KktRawNecessityDiagnosticError("ONSET_SAMPLE_INTEGER_REQUIRED")
    if isinstance(selected_midi, bool) or not isinstance(selected_midi, (int, np.integer)):
        raise KktRawNecessityDiagnosticError("SELECTED_MIDI_INTEGER_REQUIRED")
    onset_sample = int(onset_sample)
    selected_midi = int(selected_midi)
    if not v6.PLAYABLE_MIDI_MIN <= selected_midi <= v6.PLAYABLE_MIDI_MAX:
        raise KktRawNecessityDiagnosticError("SELECTED_MIDI_OUTSIDE_PLAYABLE_RANGE")

    values = _finite_vector(audio, "AUDIO")
    if values.size == 0:
        raise KktRawNecessityDiagnosticError("NONEMPTY_AUDIO_REQUIRED")
    hz = _validated_frequencies(frequencies)

    try:
        onset = v6._onset_innovation_spectrum(values, onset_sample)
    except v6.CorroborationError as exc:
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "rawMagnitudeThresholdDefined": False,
            "rankCutoffDefined": False,
            "historicalNecessityThresholdApplied": False,
            "reattackFallbackDefined": False,
            "onsetAvailable": False,
            "onsetStatus": "CONTEXT_ERROR",
            "onsetReason": str(exc),
            "supportContext": None,
            "fixedRawProblem": None,
            "kktCertificate": None,
        }
    if onset.get("status") != "OK":
        return {
            "contract": CONTRACT,
            "version": VERSION,
            "selectedMidi": selected_midi,
            "finalDecisionDefined": False,
            "rawMagnitudeThresholdDefined": False,
            "rankCutoffDefined": False,
            "historicalNecessityThresholdApplied": False,
            "reattackFallbackDefined": False,
            "onsetAvailable": False,
            "onsetStatus": str(onset.get("status", "UNKNOWN")),
            "onsetReason": str(onset.get("status", "UNKNOWN")),
            "analysisRms": onset.get("analysisRms"),
            "innovationEnergy": onset.get("innovationEnergy"),
            "supportContext": None,
            "fixedRawProblem": None,
            "kktCertificate": None,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    if raw.shape != hz.shape or not np.all(np.isfinite(raw)) or np.any(raw < 0.0):
        raise KktRawNecessityDiagnosticError("INVALID_FROZEN_V6_RAW_INNOVATION")

    midis, feature_bins, observed, dictionary = _build_all49_fixed_problem(raw, hz)
    selected_column = midis.index(selected_midi)
    certificate = certify_omitted_column_nnls(dictionary, observed, selected_column)

    support_payload = landscape.evaluate_support_conditioned_raw_landscape(
        values,
        onset_sample,
        selected_midi,
        hz,
    )
    if support_payload.get("onsetAvailable") is not True:
        raise KktRawNecessityDiagnosticError("LANDSCAPE_ONSET_AVAILABILITY_MISMATCH")
    support_midis = list(support_payload.get("supportValidMidis") or [])
    selected_landscape_row = support_payload.get("selectedLandscapeRow")
    support_context = {
        "selectedSupportValid": bool(selected_midi in support_midis),
        "supportValidMidis": [int(value) for value in support_midis],
        "selectedCandidateEvidence": (
            selected_landscape_row.get("candidateEvidence")
            if isinstance(selected_landscape_row, dict)
            else None
        ),
        "selectedOwnerDiagnostics": (
            selected_landscape_row.get("ownerDiagnostics")
            if isinstance(selected_landscape_row, dict)
            else None
        ),
    }

    feature_energy = float(np.linalg.norm(observed))
    if not math.isfinite(feature_energy) or feature_energy < v6.MIN_INNOVATION_ENERGY:
        raise KktRawNecessityDiagnosticError("INSUFFICIENT_FIXED_FEATURE_ENERGY")

    return {
        "contract": CONTRACT,
        "version": VERSION,
        "selectedMidi": selected_midi,
        "finalDecisionDefined": False,
        "rawMagnitudeThresholdDefined": False,
        "rankCutoffDefined": False,
        "historicalNecessityThresholdApplied": False,
        "historicalNecessityThresholdReferenceOnly": float(v6.NECESSITY_FRACTION_MIN),
        "reattackFallbackDefined": False,
        "onsetAvailable": True,
        "onsetStatus": "OK",
        "analysisRms": float(onset["analysisRms"]),
        "innovationEnergy": float(onset["innovationEnergy"]),
        "supportContext": support_context,
        "fixedRawProblem": {
            "candidateCount": len(midis),
            "candidateMidis": [int(value) for value in midis],
            "featureBinCount": len(feature_bins),
            "featureBins": [int(value) for value in feature_bins],
            "featureEnergy": feature_energy,
        },
        "kktCertificate": certificate,
    }
