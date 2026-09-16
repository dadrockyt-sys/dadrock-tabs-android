#!/usr/bin/env python3
"""First-run synthetic-only gate for V7 candidate-competition diagnostics."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v7_candidate_competition_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"
REPRO_TOLERANCE = 1e-12


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


def _assert_midi_list(values: Any, path: str) -> list[int]:
    if not isinstance(values, list) or any(
        isinstance(value, bool) or not isinstance(value, int) for value in values
    ):
        raise MechanicalInvariantError(f"MIDI_LIST_TYPE:{path}")
    if values != sorted(set(values)):
        raise MechanicalInvariantError(f"MIDI_LIST_ORDER_UNIQUE:{path}")
    if any(value < v6.PLAYABLE_MIDI_MIN or value > v6.PLAYABLE_MIDI_MAX for value in values):
        raise MechanicalInvariantError(f"MIDI_LIST_RANGE:{path}")
    return values


def _assert_close(actual: Any, expected: Any, path: str) -> None:
    if isinstance(actual, bool) or isinstance(expected, bool):
        raise MechanicalInvariantError(f"NUMERIC_BOOL:{path}")
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        raise MechanicalInvariantError(f"NUMERIC_TYPE:{path}")
    if not math.isclose(
        float(actual),
        float(expected),
        rel_tol=REPRO_TOLERANCE,
        abs_tol=REPRO_TOLERANCE,
    ):
        raise MechanicalInvariantError(
            f"V6_REPRODUCTION:{path}:{actual}!={expected}"
        )


def _check_candidate_algebra(payload: dict[str, Any], fixture_id: str) -> None:
    if payload.get("onsetAvailable") is not True:
        if payload.get("candidateSets") is not None:
            raise MechanicalInvariantError(f"FABRICATED_CANDIDATE_SETS:{fixture_id}")
        return

    candidate_sets = payload.get("candidateSets")
    if not isinstance(candidate_sets, dict):
        raise MechanicalInvariantError(f"CANDIDATE_SETS_MISSING:{fixture_id}")
    raw_valid = _assert_midi_list(candidate_sets.get("rawValidMidis"), f"{fixture_id}.raw")
    support_valid = _assert_midi_list(
        candidate_sets.get("supportValidMidis"), f"{fixture_id}.support"
    )
    intersection = _assert_midi_list(
        candidate_sets.get("intersectionMidis"), f"{fixture_id}.intersection"
    )
    raw_only = _assert_midi_list(candidate_sets.get("rawOnlyMidis"), f"{fixture_id}.raw_only")
    support_only = _assert_midi_list(
        candidate_sets.get("supportOnlyMidis"), f"{fixture_id}.support_only"
    )

    if intersection != sorted(set(raw_valid).intersection(support_valid)):
        raise MechanicalInvariantError(f"INTERSECTION_ALGEBRA:{fixture_id}")
    if raw_only != sorted(set(raw_valid).difference(support_valid)):
        raise MechanicalInvariantError(f"RAW_ONLY_ALGEBRA:{fixture_id}")
    if support_only != sorted(set(support_valid).difference(raw_valid)):
        raise MechanicalInvariantError(f"SUPPORT_ONLY_ALGEBRA:{fixture_id}")

    selected = int(payload["selectedMidi"])
    if (payload.get("selectedRawEligible") is True) != (selected in raw_valid):
        raise MechanicalInvariantError(f"SELECTED_RAW_ELIGIBILITY:{fixture_id}")
    if (payload.get("selectedSupportEligible") is True) != (selected in support_valid):
        raise MechanicalInvariantError(f"SELECTED_SUPPORT_ELIGIBILITY:{fixture_id}")
    if (payload.get("candidateCompetitionComparable") is True) != (selected in intersection):
        raise MechanicalInvariantError(f"SELECTED_INTERSECTION_COMPARABLE:{fixture_id}")

    attribution = payload.get("excludedCandidateAttribution")
    if not isinstance(attribution, dict):
        raise MechanicalInvariantError(f"ATTRIBUTION_MISSING:{fixture_id}")
    add_rows = attribution.get("addOneRows")
    leave_rows = attribution.get("leaveOneOutRows")
    if not isinstance(add_rows, list) or not isinstance(leave_rows, list):
        raise MechanicalInvariantError(f"ATTRIBUTION_ROWS_TYPE:{fixture_id}")

    if attribution.get("available") is True:
        add_midis = [int(row["midi"]) for row in add_rows]
        leave_midis = [int(row["midi"]) for row in leave_rows]
        if add_midis != raw_only or leave_midis != raw_only:
            raise MechanicalInvariantError(f"ATTRIBUTION_ENUMERATION:{fixture_id}")
    elif add_rows or leave_rows:
        raise MechanicalInvariantError(f"ATTRIBUTION_ROWS_WHEN_UNAVAILABLE:{fixture_id}")

    raw_full = payload.get("rawFullFit")
    if isinstance(raw_full, dict) and raw_full.get("available") is True:
        if raw_full.get("candidateMidis") != raw_valid:
            raise MechanicalInvariantError(f"RAW_FULL_SET_CHANGED:{fixture_id}")
        if raw_full.get("candidateCount") != len(raw_valid):
            raise MechanicalInvariantError(f"RAW_FULL_COUNT:{fixture_id}")

    restricted = payload.get("rawSupportMidiRestrictedFit")
    if isinstance(restricted, dict) and restricted.get("available") is True:
        if restricted.get("candidateMidis") != intersection:
            raise MechanicalInvariantError(f"RESTRICTED_SET_CHANGED:{fixture_id}")
        if restricted.get("candidateCount") != len(intersection):
            raise MechanicalInvariantError(f"RESTRICTED_COUNT:{fixture_id}")


def _check_v6_reproduction(payload: dict[str, Any], fixture_id: str) -> None:
    if payload.get("onsetAvailable") is not True:
        return
    historical = payload.get("frozenV6HistoricalComponent")
    if not isinstance(historical, dict):
        raise MechanicalInvariantError(f"HISTORICAL_COMPONENT_MISSING:{fixture_id}")
    frozen_fit = historical.get("fit")
    if not isinstance(frozen_fit, dict) or frozen_fit.get("status") != "OK":
        return
    raw_full = payload.get("rawFullFit")
    if not isinstance(raw_full, dict) or raw_full.get("available") is not True:
        raise MechanicalInvariantError(f"RAW_FULL_NOT_AVAILABLE_FOR_V6_OK:{fixture_id}")

    if int(raw_full.get("candidateCount", -1)) != int(frozen_fit.get("validCandidateCount", -2)):
        raise MechanicalInvariantError(f"V6_REPRODUCTION_CANDIDATE_COUNT:{fixture_id}")
    for raw_key, frozen_key in (
        ("featureEnergy", "featureEnergy"),
        ("selectedCoefficient", "selectedCoefficient"),
        ("fullResidual", "fullResidual"),
        ("withoutSelectedResidual", "withoutSelectedResidual"),
        ("necessityFraction", "necessityFraction"),
    ):
        _assert_close(raw_full.get(raw_key), frozen_fit.get(frozen_key), f"{fixture_id}.{raw_key}")


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_candidate_competition_diagnostic(
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

    dual_reference = payload.get("dualViewReference")
    if isinstance(dual_reference, dict) and dual_reference.get("finalDecisionDefined") is not False:
        raise MechanicalInvariantError(f"DUAL_REFERENCE_DECISION:{fixture_id}")

    _check_finite(payload, fixture_id)
    _check_candidate_algebra(payload, fixture_id)
    _check_v6_reproduction(payload, fixture_id)

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

    if diagnostic.CONTRACT != "songsterr-fresh-v7-candidate-competition-diagnostic-v1":
        raise MechanicalInvariantError("DIAGNOSTIC_CONTRACT_CHANGED")
    if diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_VERSION_CHANGED")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if not np.allclose(frequencies, v3.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise MechanicalInvariantError("V6_V3_FREQUENCY_GRID_MISMATCH")

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
    comparable_count = sum(
        1 for row in rows if row["diagnostic"].get("candidateCompetitionComparable") is True
    )
    attribution_available_count = sum(
        1
        for row in rows
        if isinstance(row["diagnostic"].get("excludedCandidateAttribution"), dict)
        and row["diagnostic"]["excludedCandidateAttribution"].get("available") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-candidate-competition-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "candidateCompetitionComparableCount": comparable_count,
        "attributionAvailableCount": attribution_available_count,
        "v6ReproductionTolerance": REPRO_TOLERANCE,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "historicalV6ThresholdAdoptedAsSuccessorRule": False,
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
