#!/usr/bin/env python3
"""First-run synthetic-only gate for V7 fixed-feature competition diagnostics."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge
import v7_fixed_feature_competition_diagnostics_v1 as diagnostic
import v7_gate_free_competition_diagnostics_v1 as gatefree

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
TOLERANCE = 1e-12
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"
EXPECTED_DIAGNOSTIC_CONTRACT = "songsterr-fresh-v7-fixed-feature-competition-diagnostic-v1"


class MechanicalInvariantError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _check_finite(value: Any, path: str = "root") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MechanicalInvariantError(f"NONFINITE:{path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_finite(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _check_finite(item, f"{path}.{key}")
        return
    raise MechanicalInvariantError(f"UNEXPECTED_TYPE:{path}:{type(value).__name__}")


def _assert_close(actual: Any, expected: Any, path: str) -> None:
    if isinstance(actual, bool) or isinstance(expected, bool):
        raise MechanicalInvariantError(f"NUMERIC_BOOL:{path}")
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        raise MechanicalInvariantError(f"NUMERIC_TYPE:{path}")
    if not math.isclose(
        float(actual),
        float(expected),
        rel_tol=TOLERANCE,
        abs_tol=TOLERANCE,
    ):
        raise MechanicalInvariantError(f"MISMATCH:{path}:{actual}!={expected}")


def _assert_sorted_unique_midis(values: Any, path: str) -> list[int]:
    if not isinstance(values, list) or any(
        isinstance(value, bool) or not isinstance(value, int) for value in values
    ):
        raise MechanicalInvariantError(f"MIDI_LIST_TYPE:{path}")
    observed = [int(value) for value in values]
    if observed != sorted(set(observed)):
        raise MechanicalInvariantError(f"MIDI_LIST_ORDER:{path}")
    if any(value < v6.PLAYABLE_MIDI_MIN or value > v6.PLAYABLE_MIDI_MAX for value in observed):
        raise MechanicalInvariantError(f"MIDI_LIST_RANGE:{path}")
    return observed


def _assert_sorted_unique_bins(values: Any, raw_size: int, path: str) -> list[int]:
    if not isinstance(values, list) or not values or any(
        isinstance(value, bool) or not isinstance(value, int) for value in values
    ):
        raise MechanicalInvariantError(f"BIN_LIST_TYPE:{path}")
    observed = [int(value) for value in values]
    if observed != sorted(set(observed)):
        raise MechanicalInvariantError(f"BIN_LIST_ORDER:{path}")
    if observed[0] < 0 or observed[-1] >= raw_size:
        raise MechanicalInvariantError(f"BIN_LIST_RANGE:{path}")
    return observed


def _fit_snapshot(fit: dict[str, Any]) -> tuple[Any, ...]:
    return (
        fit.get("selectedCoefficient"),
        fit.get("fullResidual"),
        fit.get("withoutSelectedResidual"),
        fit.get("necessityFraction"),
    )


def _check_fit_against_fixed_universe(
    fit: Any,
    candidate_midis: list[int],
    fixed_bins: list[int],
    fixed_energy: float,
    fixture_id: str,
    fit_name: str,
) -> None:
    if not isinstance(fit, dict):
        raise MechanicalInvariantError(f"FIT_TYPE:{fixture_id}:{fit_name}")
    if fit.get("candidateMidis") != candidate_midis:
        raise MechanicalInvariantError(f"FIT_CANDIDATES:{fixture_id}:{fit_name}")
    if int(fit.get("candidateCount", -1)) != len(candidate_midis):
        raise MechanicalInvariantError(f"FIT_CANDIDATE_COUNT:{fixture_id}:{fit_name}")
    if fit.get("fixedFeatureBins") != fixed_bins:
        raise MechanicalInvariantError(f"FIT_FEATURE_BINS:{fixture_id}:{fit_name}")
    if int(fit.get("fixedFeatureBinCount", -1)) != len(fixed_bins):
        raise MechanicalInvariantError(f"FIT_FEATURE_COUNT:{fixture_id}:{fit_name}")
    _assert_close(
        fit.get("fixedFeatureEnergy"),
        fixed_energy,
        f"{fixture_id}.{fit_name}.fixedFeatureEnergy",
    )

    if fit.get("available") is True:
        rows = fit.get("coefficientRows")
        if not isinstance(rows, list):
            raise MechanicalInvariantError(f"FIT_COEFFICIENT_ROWS:{fixture_id}:{fit_name}")
        if [row.get("midi") for row in rows] != candidate_midis:
            raise MechanicalInvariantError(f"FIT_COEFFICIENT_ORDER:{fixture_id}:{fit_name}")
        for row in rows:
            coefficient = row.get("coefficient")
            if (
                isinstance(coefficient, bool)
                or not isinstance(coefficient, (int, float))
                or not math.isfinite(float(coefficient))
                or float(coefficient) < 0.0
            ):
                raise MechanicalInvariantError(
                    f"FIT_COEFFICIENT_VALUE:{fixture_id}:{fit_name}"
                )
    elif fit.get("availabilityStatus") not in {
        "SELECTED_MIDI_NOT_IN_CANDIDATE_SET",
        "REDUCED_DICTIONARY_EMPTY",
        "INSUFFICIENT_FIXED_FEATURE_ENERGY",
    } and not str(fit.get("availabilityStatus", "")).startswith("NNLS_"):
        raise MechanicalInvariantError(
            f"FIT_UNEXPECTED_UNAVAILABLE:{fixture_id}:{fit_name}:{fit.get('availabilityStatus')}"
        )


def _check_geometry_equivalence(
    raw: np.ndarray,
    frequencies: np.ndarray,
    gate_free_midis: list[int],
    historical_midis: list[int],
    fixture_id: str,
) -> None:
    if gate_free_midis != list(range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)):
        raise MechanicalInvariantError(f"EXPECTED_ALL_49_GATE_FREE:{fixture_id}")

    for midi in historical_midis:
        frozen = dict(v6._candidate_template(midi, raw, frequencies))
        if frozen.get("valid") is not True:
            raise MechanicalInvariantError(f"HISTORICAL_SET_NOT_VALID:{fixture_id}:{midi}")
        open_template = gatefree.gate_free_competition_template(midi, raw, frequencies)
        if open_template.get("structurallyConstructible") is not True:
            raise MechanicalInvariantError(f"GATE_FREE_NOT_CONSTRUCTIBLE:{fixture_id}:{midi}")
        if int(open_template.get("fundamentalBin", -1)) != int(frozen.get("fundamentalBin", -2)):
            raise MechanicalInvariantError(f"GEOMETRY_FUNDAMENTAL_BIN:{fixture_id}:{midi}")
        _assert_close(
            open_template.get("fundamentalHz"),
            frozen.get("fundamentalHz"),
            f"{fixture_id}.{midi}.fundamentalHz",
        )
        if open_template.get("bins") != frozen.get("bins"):
            raise MechanicalInvariantError(f"GEOMETRY_BINS:{fixture_id}:{midi}")
        open_weights = open_template.get("weights")
        frozen_weights = frozen.get("weights")
        if not isinstance(open_weights, list) or not isinstance(frozen_weights, list):
            raise MechanicalInvariantError(f"GEOMETRY_WEIGHT_TYPE:{fixture_id}:{midi}")
        if len(open_weights) != len(frozen_weights):
            raise MechanicalInvariantError(f"GEOMETRY_WEIGHT_COUNT:{fixture_id}:{midi}")
        for index, (left, right) in enumerate(zip(open_weights, frozen_weights)):
            _assert_close(left, right, f"{fixture_id}.{midi}.weights[{index}]")


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_fixed_feature_competition_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if payload.get("contract") != EXPECTED_DIAGNOSTIC_CONTRACT or payload.get("version") != 1:
        raise MechanicalInvariantError(f"CONTRACT:{fixture_id}")
    if payload.get("selectedMidi") != selected_midi:
        raise MechanicalInvariantError(f"MIDI_IDENTITY:{fixture_id}")
    if payload.get("finalDecisionDefined") is not False:
        raise MechanicalInvariantError(f"FINAL_DECISION_DEFINED:{fixture_id}")
    if "finalDecision" in payload or "successorClassification" in payload:
        raise MechanicalInvariantError(f"FORBIDDEN_VERDICT_FIELD:{fixture_id}")
    _check_finite(payload, fixture_id)

    if payload.get("onsetAvailable") is not True:
        for key in (
            "candidateSets",
            "fixedFeatureUniverse",
            "fixedFeatureFits",
            "variableFeatureReferences",
            "diagnosticDeltas",
        ):
            if payload.get(key) is not None:
                raise MechanicalInvariantError(f"FABRICATED_UNAVAILABLE:{fixture_id}:{key}")
        return {
            "fixtureId": fixture_id,
            "selectedMidi": selected_midi,
            "referenceExpectedClassification": str(fixture["expectedClassification"]),
            "referenceExpectedUsedForComputation": False,
            "finalDecisionDefined": False,
            "diagnostic": payload,
        }

    onset = v6._onset_innovation_spectrum(audio, onset_sample)
    if onset.get("status") != "OK":
        raise MechanicalInvariantError(f"ONSET_RECONSTRUCTION:{fixture_id}")
    raw = np.asarray(onset["innovation"], dtype=np.float64)

    sets = payload.get("candidateSets")
    universe = payload.get("fixedFeatureUniverse")
    fixed = payload.get("fixedFeatureFits")
    variable = payload.get("variableFeatureReferences")
    deltas = payload.get("diagnosticDeltas")
    if not all(isinstance(item, dict) for item in (sets, universe, fixed, variable, deltas)):
        raise MechanicalInvariantError(f"PAYLOAD_NAMESPACE:{fixture_id}")

    gate_free_midis = _assert_sorted_unique_midis(sets.get("gateFree49Midis"), f"{fixture_id}.gateFree")
    historical_midis = _assert_sorted_unique_midis(
        sets.get("historicalRawValidMidis"), f"{fixture_id}.historical"
    )
    support_midis = _assert_sorted_unique_midis(
        sets.get("supportValidMidis"), f"{fixture_id}.support"
    )
    intersection_midis = _assert_sorted_unique_midis(
        sets.get("rawSupportIntersectionMidis"), f"{fixture_id}.intersection"
    )
    if intersection_midis != sorted(set(historical_midis).intersection(support_midis)):
        raise MechanicalInvariantError(f"INTERSECTION_SET:{fixture_id}")

    expected_historical = sorted(
        midi
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
        if v6._candidate_template(midi, raw, frequencies).get("valid") is True
    )
    if historical_midis != expected_historical:
        raise MechanicalInvariantError(f"HISTORICAL_SET:{fixture_id}")

    support_view = bridge.collapse_hann_lobes_to_peak_bands(raw)
    expected_support = sorted(
        midi
        for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
        if v3.evaluate_candidate_template(midi, support_view, frequencies).get("valid") is True
    )
    if support_midis != expected_support:
        raise MechanicalInvariantError(f"SUPPORT_SET:{fixture_id}")

    _check_geometry_equivalence(
        raw,
        frequencies,
        gate_free_midis,
        historical_midis,
        fixture_id,
    )

    fixed_bins = _assert_sorted_unique_bins(
        universe.get("featureBins"), raw.size, f"{fixture_id}.fixedFeatureBins"
    )
    if int(universe.get("featureBinCount", -1)) != len(fixed_bins):
        raise MechanicalInvariantError(f"FIXED_FEATURE_COUNT:{fixture_id}")
    expected_bins = sorted(
        {
            int(bin_index)
            for midi in gate_free_midis
            for bin_index in gatefree.gate_free_competition_template(
                midi, raw, frequencies
            ).get("bins", [])
        }
    )
    if fixed_bins != expected_bins:
        raise MechanicalInvariantError(f"FIXED_FEATURE_UNIVERSE:{fixture_id}")
    expected_energy = float(np.linalg.norm(raw[fixed_bins]))
    _assert_close(
        universe.get("featureEnergy"),
        expected_energy,
        f"{fixture_id}.fixedFeatureEnergy",
    )

    population_specs = (
        ("gateFree49FixedFit", gate_free_midis),
        ("historicalRawValidFixedFit", historical_midis),
        ("rawSupportIntersectionFixedFit", intersection_midis),
    )
    for fit_name, candidates in population_specs:
        _check_fit_against_fixed_universe(
            fixed.get(fit_name),
            candidates,
            fixed_bins,
            expected_energy,
            fixture_id,
            fit_name,
        )

    gate_fixed = fixed["gateFree49FixedFit"]
    gate_variable = variable.get("gateFree49VariableFit")
    if not isinstance(gate_variable, dict):
        raise MechanicalInvariantError(f"GATE_VARIABLE_TYPE:{fixture_id}")
    if gate_fixed.get("available") is not True or gate_variable.get("available") is not True:
        raise MechanicalInvariantError(f"GATE_FREE_REFERENCE_UNAVAILABLE:{fixture_id}")
    if gate_variable.get("candidateMidis") != gate_free_midis:
        raise MechanicalInvariantError(f"GATE_VARIABLE_CANDIDATES:{fixture_id}")
    if gate_variable.get("featureBins") != fixed_bins:
        raise MechanicalInvariantError(f"GATE_VARIABLE_FEATURE_BINS:{fixture_id}")
    _assert_close(
        gate_variable.get("featureEnergy"),
        expected_energy,
        f"{fixture_id}.gateVariableFeatureEnergy",
    )
    for index, (left, right) in enumerate(zip(_fit_snapshot(gate_fixed), _fit_snapshot(gate_variable))):
        _assert_close(left, right, f"{fixture_id}.gateFixedVariable[{index}]")

    gate_feature_delta = deltas.get("gateFreeFeatureUniverseDelta")
    _assert_close(gate_feature_delta, 0.0, f"{fixture_id}.gateFreeFeatureUniverseDelta")

    historical_variable = variable.get("historicalRawValidVariableFit")
    frozen_fit = variable.get("frozenV6HistoricalFit")
    if (
        isinstance(historical_variable, dict)
        and historical_variable.get("available") is True
        and isinstance(frozen_fit, dict)
        and frozen_fit.get("status") == "OK"
        and selected_midi in historical_midis
    ):
        for index, (left, right) in enumerate(
            zip(
                _fit_snapshot(historical_variable),
                (
                    frozen_fit.get("selectedCoefficient"),
                    frozen_fit.get("fullResidual"),
                    frozen_fit.get("withoutSelectedResidual"),
                    frozen_fit.get("necessityFraction"),
                ),
            )
        ):
            _assert_close(left, right, f"{fixture_id}.historicalVariableV6[{index}]")

    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": str(fixture["expectedClassification"]),
        "referenceExpectedUsedForComputation": False,
        "finalDecisionDefined": False,
        "diagnostic": payload,
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")
    if diagnostic.CONTRACT != EXPECTED_DIAGNOSTIC_CONTRACT or diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_CONTRACT_CHANGED")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if not np.allclose(frequencies, v3.expected_frequencies(), rtol=0.0, atol=TOLERANCE):
        raise MechanicalInvariantError("FREQUENCY_GRID_MISMATCH")

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise MechanicalInvariantError("NONDETERMINISTIC_OUTPUT")

    rows = repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    if [row["fixtureId"] for row in rows] != expected_ids:
        raise MechanicalInvariantError("FIXTURE_ORDER_CHANGED")

    onset_available_count = sum(
        1 for row in rows if row["diagnostic"].get("onsetAvailable") is True
    )
    all_49_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and row["diagnostic"]["candidateSets"]["gateFree49Midis"]
        == list(range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1))
    )
    fixed_gate_fit_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and row["diagnostic"]["fixedFeatureFits"]["gateFree49FixedFit"].get("available") is True
    )
    historical_fixed_fit_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and row["diagnostic"]["fixedFeatureFits"]["historicalRawValidFixedFit"].get("available") is True
    )
    intersection_fixed_fit_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and row["diagnostic"]["fixedFeatureFits"]["rawSupportIntersectionFixedFit"].get("available") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-fixed-feature-competition-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "all49GateFreeCount": all_49_count,
        "gateFreeFixedFitAvailableCount": fixed_gate_fit_count,
        "historicalFixedFitAvailableCount": historical_fixed_fit_count,
        "intersectionFixedFitAvailableCount": intersection_fixed_fit_count,
        "geometryAndFitTolerance": TOLERANCE,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "historicalV6RatioGateAdoptedAsCompetitionGate": False,
        "historicalV6NecessityThresholdAdoptedAsDecisionRule": False,
        "candidateSubsetSearchPerformed": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalDiagnosticStatus": "COMPLETE",
        "rows": rows,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
