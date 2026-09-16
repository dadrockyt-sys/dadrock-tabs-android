#!/usr/bin/env python3
"""First-run synthetic-only gate for V7 gate-free competition diagnostics."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import v7_gate_free_competition_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"
TOLERANCE = 1e-12


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


def _assert_float_list(actual: Any, expected: Any, path: str) -> None:
    if not isinstance(actual, list) or not isinstance(expected, list):
        raise MechanicalInvariantError(f"LIST_TYPE:{path}")
    if len(actual) != len(expected):
        raise MechanicalInvariantError(f"LIST_LENGTH:{path}")
    for index, (left, right) in enumerate(zip(actual, expected)):
        _assert_close(left, right, f"{path}[{index}]")


def _check_geometry_equivalence(
    payload: dict[str, Any],
    raw: np.ndarray,
    frequencies: np.ndarray,
    fixture_id: str,
) -> None:
    rows = payload.get("gateFreeTemplates")
    if not isinstance(rows, list):
        raise MechanicalInvariantError(f"TEMPLATE_ROWS_MISSING:{fixture_id}")
    by_midi: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("midi"), int):
            raise MechanicalInvariantError(f"TEMPLATE_ROW_TYPE:{fixture_id}")
        midi = int(row["midi"])
        if midi in by_midi:
            raise MechanicalInvariantError(f"DUPLICATE_TEMPLATE_MIDI:{fixture_id}:{midi}")
        by_midi[midi] = row

    expected_midis = list(range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1))
    if sorted(by_midi) != expected_midis:
        raise MechanicalInvariantError(f"TEMPLATE_MIDI_COVERAGE:{fixture_id}")

    historical_valid: list[int] = []
    for midi in expected_midis:
        gate_free = by_midi[midi]
        if gate_free.get("structurallyConstructible") is True:
            if gate_free.get("admittedToGateFreeCompetition") is not True:
                raise MechanicalInvariantError(
                    f"STRUCTURAL_TEMPLATE_NOT_ADMITTED:{fixture_id}:{midi}"
                )
            ratio = gate_free.get("fundamentalToMaxHarmonicInnovationRatio")
            if not isinstance(ratio, (int, float)) or isinstance(ratio, bool):
                raise MechanicalInvariantError(f"RATIO_TYPE:{fixture_id}:{midi}")
            expected_gate = bool(float(ratio) >= v6.TEMPLATE_FUNDAMENTAL_TO_MAX_HARMONIC_MIN)
            if gate_free.get("historicalV6RatioGateWouldPass") is not expected_gate:
                raise MechanicalInvariantError(
                    f"REFERENCE_GATE_METADATA:{fixture_id}:{midi}"
                )

        frozen = dict(v6._candidate_template(midi, raw, frequencies))
        if frozen.get("valid") is not True:
            continue
        historical_valid.append(midi)
        if gate_free.get("structurallyConstructible") is not True:
            raise MechanicalInvariantError(
                f"FROZEN_VALID_NOT_GATE_FREE_CONSTRUCTIBLE:{fixture_id}:{midi}"
            )
        if int(gate_free.get("fundamentalBin", -1)) != int(frozen.get("fundamentalBin", -2)):
            raise MechanicalInvariantError(f"FUNDAMENTAL_BIN:{fixture_id}:{midi}")
        _assert_close(
            gate_free.get("fundamentalHz"),
            frozen.get("fundamentalHz"),
            f"{fixture_id}.{midi}.fundamentalHz",
        )
        if gate_free.get("bins") != frozen.get("bins"):
            raise MechanicalInvariantError(f"HARMONIC_BINS:{fixture_id}:{midi}")
        _assert_float_list(
            gate_free.get("weights"),
            frozen.get("weights"),
            f"{fixture_id}.{midi}.weights",
        )
        _assert_float_list(
            gate_free.get("observedHarmonicInnovation"),
            frozen.get("observedHarmonicInnovation"),
            f"{fixture_id}.{midi}.observed",
        )
        _assert_close(
            gate_free.get("fundamentalToMaxHarmonicInnovationRatio"),
            frozen.get("fundamentalToMaxHarmonicInnovationRatio"),
            f"{fixture_id}.{midi}.ratio",
        )

    observed_historical = payload.get("historicalRawValidMidis")
    if observed_historical != historical_valid:
        raise MechanicalInvariantError(f"HISTORICAL_VALID_SET:{fixture_id}")

    gate_free_midis = payload.get("gateFreeMidis")
    if not isinstance(gate_free_midis, list):
        raise MechanicalInvariantError(f"GATE_FREE_MIDIS_TYPE:{fixture_id}")
    expected_gate_free = sorted(
        midi
        for midi, row in by_midi.items()
        if row.get("structurallyConstructible") is True
        and row.get("admittedToGateFreeCompetition") is True
    )
    if gate_free_midis != expected_gate_free:
        raise MechanicalInvariantError(f"GATE_FREE_SET:{fixture_id}")

    newly_admitted = payload.get("newlyAdmittedMidis")
    expected_new = sorted(set(expected_gate_free).difference(historical_valid))
    if newly_admitted != expected_new:
        raise MechanicalInvariantError(f"NEWLY_ADMITTED_SET:{fixture_id}")

    fit = payload.get("gateFreeFit")
    if not isinstance(fit, dict):
        raise MechanicalInvariantError(f"GATE_FREE_FIT_MISSING:{fixture_id}")
    if int(payload["selectedMidi"]) in expected_gate_free and fit.get("available") is True:
        if fit.get("candidateMidis") != expected_gate_free:
            raise MechanicalInvariantError(f"GATE_FREE_FIT_SET:{fixture_id}")
        if int(fit.get("candidateCount", -1)) != len(expected_gate_free):
            raise MechanicalInvariantError(f"GATE_FREE_FIT_COUNT:{fixture_id}")
        coefficient_rows = fit.get("coefficientRows")
        if not isinstance(coefficient_rows, list):
            raise MechanicalInvariantError(f"COEFFICIENT_ROWS:{fixture_id}")
        if [row.get("midi") for row in coefficient_rows] != expected_gate_free:
            raise MechanicalInvariantError(f"COEFFICIENT_ORDER:{fixture_id}")

    frozen_fit = payload.get("frozenV6HistoricalComponent", {}).get("fit")
    if (
        isinstance(frozen_fit, dict)
        and frozen_fit.get("status") == "OK"
        and int(frozen_fit.get("validCandidateCount", -1)) == 49
    ):
        if not isinstance(fit, dict) or fit.get("available") is not True:
            raise MechanicalInvariantError(f"FULL49_GATE_FREE_FIT_MISSING:{fixture_id}")
        for gate_key, frozen_key in (
            ("featureEnergy", "featureEnergy"),
            ("selectedCoefficient", "selectedCoefficient"),
            ("fullResidual", "fullResidual"),
            ("withoutSelectedResidual", "withoutSelectedResidual"),
            ("necessityFraction", "necessityFraction"),
        ):
            _assert_close(
                fit.get(gate_key),
                frozen_fit.get(frozen_key),
                f"{fixture_id}.full49.{gate_key}",
            )

    attribution = payload.get("newlyAdmittedAttribution")
    if not isinstance(attribution, dict):
        raise MechanicalInvariantError(f"ATTRIBUTION_MISSING:{fixture_id}")
    add_rows = attribution.get("addOneRows")
    leave_rows = attribution.get("leaveOneOutRows")
    if not isinstance(add_rows, list) or not isinstance(leave_rows, list):
        raise MechanicalInvariantError(f"ATTRIBUTION_ROWS_TYPE:{fixture_id}")
    if attribution.get("available") is True:
        if [int(row["midi"]) for row in add_rows] != expected_new:
            raise MechanicalInvariantError(f"ADD_ONE_ENUMERATION:{fixture_id}")
        if [int(row["midi"]) for row in leave_rows] != expected_new:
            raise MechanicalInvariantError(f"LEAVE_ONE_OUT_ENUMERATION:{fixture_id}")
    elif add_rows or leave_rows:
        raise MechanicalInvariantError(f"ATTRIBUTION_ROWS_WHEN_UNAVAILABLE:{fixture_id}")


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_gate_free_competition_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if payload.get("contract") != diagnostic.CONTRACT or payload.get("version") != diagnostic.VERSION:
        raise MechanicalInvariantError(f"CONTRACT:{fixture_id}")
    if payload.get("selectedMidi") != selected_midi:
        raise MechanicalInvariantError(f"MIDI_IDENTITY:{fixture_id}")
    if payload.get("finalDecisionDefined") is not False:
        raise MechanicalInvariantError(f"FINAL_DECISION_DEFINED:{fixture_id}")
    if "finalDecision" in payload or "successorClassification" in payload:
        raise MechanicalInvariantError(f"FORBIDDEN_VERDICT_FIELD:{fixture_id}")

    _check_finite(payload, fixture_id)

    if payload.get("onsetAvailable") is True:
        onset = v6._onset_innovation_spectrum(audio, onset_sample)
        if onset.get("status") != "OK":
            raise MechanicalInvariantError(f"ONSET_RECONSTRUCTION:{fixture_id}")
        raw = np.asarray(onset["innovation"], dtype=np.float64)
        _check_geometry_equivalence(payload, raw, frequencies, fixture_id)
    else:
        for key in (
            "gateFreeTemplates",
            "historicalRawValidMidis",
            "gateFreeMidis",
            "newlyAdmittedMidis",
            "gateFreeFit",
            "frozenGatedPopulationReconstruction",
            "newlyAdmittedAttribution",
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


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")

    if diagnostic.CONTRACT != "songsterr-fresh-v7-gate-free-competition-diagnostic-v1":
        raise MechanicalInvariantError("DIAGNOSTIC_CONTRACT_CHANGED")
    if diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_VERSION_CHANGED")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise MechanicalInvariantError("NONDETERMINISTIC_OUTPUT")

    rows = repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    observed_ids = [str(row["fixtureId"]) for row in rows]
    if observed_ids != expected_ids:
        raise MechanicalInvariantError("FIXTURE_ORDER_CHANGED")

    onset_available_count = sum(
        1 for row in rows if row["diagnostic"].get("onsetAvailable") is True
    )
    all_49_constructible_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and isinstance(row["diagnostic"].get("gateFreeMidis"), list)
        and len(row["diagnostic"]["gateFreeMidis"]) == 49
    )
    historical_full_49_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and isinstance(row["diagnostic"].get("historicalRawValidMidis"), list)
        and len(row["diagnostic"]["historicalRawValidMidis"]) == 49
    )
    selected_historical_invalid_gate_free_count = sum(
        1
        for row in rows
        if row["diagnostic"].get("onsetAvailable") is True
        and row["diagnostic"].get("selectedHistoricallyRawValid") is False
        and row["diagnostic"].get("selectedGateFreeConstructible") is True
    )
    attribution_available_count = sum(
        1
        for row in rows
        if isinstance(row["diagnostic"].get("newlyAdmittedAttribution"), dict)
        and row["diagnostic"]["newlyAdmittedAttribution"].get("available") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-gate-free-competition-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "all49StructurallyConstructibleCount": all_49_constructible_count,
        "historicalFull49CandidateCount": historical_full_49_count,
        "selectedHistoricalInvalidButGateFreeConstructibleCount": (
            selected_historical_invalid_gate_free_count
        ),
        "attributionAvailableCount": attribution_available_count,
        "geometryAndFitTolerance": TOLERANCE,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "historicalV6RatioGateAdoptedAsCompetitionGate": False,
        "historicalV6NecessityThresholdAdoptedAsDecisionRule": False,
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
