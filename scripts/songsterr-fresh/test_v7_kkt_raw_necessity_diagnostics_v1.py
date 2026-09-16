#!/usr/bin/env python3
"""First-run synthetic-only gate for KKT raw strict-necessity diagnostics."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import v7_fixed_feature_competition_diagnostics_v1 as fixed
import v7_kkt_raw_necessity_diagnostics_v1 as diagnostic
import v7_support_conditioned_raw_necessity_landscape_v1 as landscape

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


def _matrix_controls() -> list[dict[str, Any]]:
    root2 = math.sqrt(2.0)
    controls = [
        {
            "id": "unique_selected_direction",
            "dictionary": np.eye(3, dtype=np.float64),
            "observed": np.asarray([1.0, 1.0, 1.0], dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": True,
        },
        {
            "id": "selected_absent",
            "dictionary": np.eye(3, dtype=np.float64),
            "observed": np.asarray([1.0, 1.0, 0.0], dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": False,
        },
        {
            "id": "duplicate_selected_column",
            "dictionary": np.asarray([[1.0, 0.0, 0.0], [0.0, 1.0, 1.0]], dtype=np.float64),
            "observed": np.asarray([0.0, 1.0], dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": False,
        },
        {
            "id": "selected_in_cone_of_others",
            "dictionary": np.asarray(
                [[1.0, 0.0, 1.0 / root2], [0.0, 1.0, 1.0 / root2]],
                dtype=np.float64,
            ),
            "observed": np.asarray([1.0 / root2, 1.0 / root2], dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": False,
        },
        {
            "id": "weak_unique_selected_direction",
            "dictionary": np.eye(3, dtype=np.float64),
            "observed": np.asarray([1.0, 1.0, 1e-8], dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": True,
        },
        {
            "id": "zero_observation",
            "dictionary": np.eye(3, dtype=np.float64),
            "observed": np.zeros(3, dtype=np.float64),
            "selectedColumn": 2,
            "expectedCertified": False,
        },
    ]
    return controls


def _evaluate_matrix_control(control: dict[str, Any]) -> dict[str, Any]:
    payload = diagnostic.certify_omitted_column_nnls(
        control["dictionary"],
        control["observed"],
        int(control["selectedColumn"]),
    )
    _check_finite(payload, str(control["id"]))
    if payload.get("available") is not True or payload.get("consistencyOk") is not True:
        raise MechanicalInvariantError(f"MATRIX_CERTIFICATE_UNAVAILABLE:{control['id']}")
    observed = bool(payload.get("kktCertifiedStrictRawNecessity"))
    if observed is not bool(control["expectedCertified"]):
        raise MechanicalInvariantError(
            f"MATRIX_EXPECTATION:{control['id']}:{observed}!={control['expectedCertified']}"
        )
    lower = float(payload["selectedNormalizedCorrelationLowerBound"])
    floor = float(payload["reducedKktDefectFloor"])
    if observed and not (lower > max(0.0, floor)):
        raise MechanicalInvariantError(f"MATRIX_CERTIFICATE_ORDER:{control['id']}")
    if not observed and lower > max(0.0, floor):
        raise MechanicalInvariantError(f"MATRIX_FALSE_NEGATION:{control['id']}")
    if observed:
        if payload.get("selectedFullCoefficient", 0.0) <= 0.0:
            raise MechanicalInvariantError(f"MATRIX_CERTIFIED_ZERO_COEFF:{control['id']}")
        if payload.get("strictResidualImprovement") is not True:
            raise MechanicalInvariantError(f"MATRIX_CERTIFIED_NO_IMPROVEMENT:{control['id']}")
    return {
        "id": str(control["id"]),
        "expectedCertified": bool(control["expectedCertified"]),
        "diagnostic": payload,
    }


def _evaluate_audio_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))
    payload = diagnostic.evaluate_kkt_raw_necessity_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if payload.get("contract") != diagnostic.CONTRACT or payload.get("version") != diagnostic.VERSION:
        raise MechanicalInvariantError(f"CONTRACT:{fixture_id}")
    if payload.get("selectedMidi") != selected_midi:
        raise MechanicalInvariantError(f"MIDI_IDENTITY:{fixture_id}")
    for key in (
        "finalDecisionDefined",
        "rawMagnitudeThresholdDefined",
        "rankCutoffDefined",
        "historicalNecessityThresholdApplied",
        "reattackFallbackDefined",
    ):
        if payload.get(key) is not False:
            raise MechanicalInvariantError(f"FORBIDDEN_AUTHORITY:{fixture_id}:{key}")
    for forbidden in (
        "finalDecision",
        "classification",
        "successorClassification",
        "rawNecessityPassed",
        "rankPassed",
    ):
        if forbidden in payload:
            raise MechanicalInvariantError(f"FORBIDDEN_VERDICT:{fixture_id}:{forbidden}")
    _check_finite(payload, fixture_id)

    if payload.get("onsetAvailable") is True:
        fixed_payload = fixed.evaluate_fixed_feature_competition_diagnostic(
            audio,
            onset_sample,
            selected_midi,
            frequencies,
        )
        fits = fixed_payload.get("fixedFeatureFits")
        if not isinstance(fits, dict):
            raise MechanicalInvariantError(f"FIXED_FITS_MISSING:{fixture_id}")
        all49 = fits.get("gateFree49FixedFit")
        if not isinstance(all49, dict) or all49.get("available") is not True:
            raise MechanicalInvariantError(f"ALL49_UNAVAILABLE:{fixture_id}")

        raw_problem = payload.get("fixedRawProblem")
        cert = payload.get("kktCertificate")
        if not isinstance(raw_problem, dict) or not isinstance(cert, dict):
            raise MechanicalInvariantError(f"KKT_RAW_PAYLOAD_MISSING:{fixture_id}")
        if cert.get("available") is not True or cert.get("consistencyOk") is not True:
            raise MechanicalInvariantError(f"KKT_CERTIFICATE_UNAVAILABLE:{fixture_id}")
        if raw_problem.get("candidateMidis") != all49.get("candidateMidis"):
            raise MechanicalInvariantError(f"CANDIDATE_SET:{fixture_id}")
        if raw_problem.get("featureBins") != all49.get("fixedFeatureBins"):
            raise MechanicalInvariantError(f"FEATURE_BINS:{fixture_id}")
        if int(raw_problem.get("candidateCount", -1)) != 49:
            raise MechanicalInvariantError(f"CANDIDATE_COUNT:{fixture_id}")
        _assert_close(raw_problem.get("featureEnergy"), all49.get("fixedFeatureEnergy"), f"{fixture_id}.energy")
        _assert_close(cert.get("selectedFullCoefficient"), all49.get("selectedCoefficient"), f"{fixture_id}.coefficient")
        _assert_close(cert.get("fullResidual"), all49.get("fullResidual"), f"{fixture_id}.fullResidual")
        _assert_close(cert.get("withoutSelectedResidual"), all49.get("withoutSelectedResidual"), f"{fixture_id}.withoutResidual")
        _assert_close(cert.get("descriptiveRawNecessityFraction"), all49.get("necessityFraction"), f"{fixture_id}.necessity")

        lower = float(cert["selectedNormalizedCorrelationLowerBound"])
        floor = float(cert["reducedKktDefectFloor"])
        certified = bool(cert["kktCertifiedStrictRawNecessity"])
        if certified and not (lower > max(0.0, floor)):
            raise MechanicalInvariantError(f"CERTIFICATE_ORDER:{fixture_id}")
        if not certified and lower > max(0.0, floor):
            raise MechanicalInvariantError(f"CERTIFICATE_NEGATION:{fixture_id}")
        if certified:
            if cert.get("strictResidualImprovement") is not True:
                raise MechanicalInvariantError(f"CERTIFIED_NO_RESIDUAL_IMPROVEMENT:{fixture_id}")
            if float(cert.get("selectedFullCoefficient", 0.0)) <= 0.0:
                raise MechanicalInvariantError(f"CERTIFIED_ZERO_COEFFICIENT:{fixture_id}")

        landscape_payload = landscape.evaluate_support_conditioned_raw_landscape(
            audio,
            onset_sample,
            selected_midi,
            frequencies,
        )
        if landscape_payload.get("onsetAvailable") is not True:
            raise MechanicalInvariantError(f"LANDSCAPE_ONSET_MISMATCH:{fixture_id}")
        expected_support_midis = list(landscape_payload.get("supportValidMidis") or [])
        context = payload.get("supportContext")
        if not isinstance(context, dict):
            raise MechanicalInvariantError(f"SUPPORT_CONTEXT_MISSING:{fixture_id}")
        if context.get("supportValidMidis") != expected_support_midis:
            raise MechanicalInvariantError(f"SUPPORT_SET:{fixture_id}")
        if context.get("selectedSupportValid") is not bool(selected_midi in expected_support_midis):
            raise MechanicalInvariantError(f"SUPPORT_SELECTED_FLAG:{fixture_id}")
        selected_row = landscape_payload.get("selectedLandscapeRow")
        if isinstance(selected_row, dict):
            if _canonical(context.get("selectedCandidateEvidence")) != _canonical(selected_row.get("candidateEvidence")):
                raise MechanicalInvariantError(f"SUPPORT_EVIDENCE:{fixture_id}")
            if _canonical(context.get("selectedOwnerDiagnostics")) != _canonical(selected_row.get("ownerDiagnostics")):
                raise MechanicalInvariantError(f"SUPPORT_OWNERS:{fixture_id}")
        else:
            if context.get("selectedCandidateEvidence") is not None or context.get("selectedOwnerDiagnostics") is not None:
                raise MechanicalInvariantError(f"FABRICATED_SUPPORT_PROTECTION:{fixture_id}")
    else:
        for key in ("supportContext", "fixedRawProblem", "kktCertificate"):
            if payload.get(key) is not None:
                raise MechanicalInvariantError(f"FABRICATED_UNAVAILABLE:{fixture_id}:{key}")

    return {
        "fixtureId": fixture_id,
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": str(fixture["expectedClassification"]),
        "referenceExpectedUsedForComputation": False,
        "diagnostic": payload,
    }


def main() -> int:
    if diagnostic.CONTRACT != "songsterr-fresh-v7-kkt-raw-necessity-diagnostic-v1" or diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_IDENTITY_CHANGED")
    if not math.isclose(
        diagnostic.FLOAT64_UNIT_ROUNDOFF,
        np.finfo(np.float64).eps / 2.0,
        rel_tol=0.0,
        abs_tol=0.0,
    ):
        raise MechanicalInvariantError("UNIT_ROUNDOFF_CHANGED")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    controls = _matrix_controls()
    if len(controls) != 6:
        raise MechanicalInvariantError("EXPECTED_6_MATRIX_CONTROLS")

    matrix_repetitions: list[list[dict[str, Any]]] = []
    audio_repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        matrix_repetitions.append([_evaluate_matrix_control(control) for control in controls])
        audio_repetitions.append([_evaluate_audio_fixture(fixture, frequencies) for fixture in fixtures])

    matrix_canonical = [_canonical(rows) for rows in matrix_repetitions]
    audio_canonical = [_canonical(rows) for rows in audio_repetitions]
    matrix_deterministic = len(set(matrix_canonical)) == 1
    audio_deterministic = len(set(audio_canonical)) == 1
    if not matrix_deterministic:
        raise MechanicalInvariantError("MATRIX_NONDETERMINISTIC")
    if not audio_deterministic:
        raise MechanicalInvariantError("AUDIO_NONDETERMINISTIC")

    matrix_rows = matrix_repetitions[0]
    audio_rows = audio_repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    if [str(row["fixtureId"]) for row in audio_rows] != expected_ids:
        raise MechanicalInvariantError("FIXTURE_ORDER_CHANGED")

    onset_available_count = sum(
        1 for row in audio_rows if row["diagnostic"].get("onsetAvailable") is True
    )
    if onset_available_count != 19:
        raise MechanicalInvariantError(f"EXPECTED_19_ONSET_AVAILABLE:{onset_available_count}")
    certified_count = sum(
        1
        for row in audio_rows
        if isinstance(row["diagnostic"].get("kktCertificate"), dict)
        and row["diagnostic"]["kktCertificate"].get("kktCertifiedStrictRawNecessity") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-kkt-raw-necessity-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "matrixControlCount": len(matrix_rows),
        "fixtureCount": len(audio_rows),
        "repetitions": REPETITIONS,
        "matrixDeterministic": matrix_deterministic,
        "audioDeterministic": audio_deterministic,
        "onsetAvailableCount": onset_available_count,
        "kktCertifiedAudioCount": certified_count,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "rawMagnitudeThresholdDefined": False,
        "rankCutoffDefined": False,
        "historicalNecessityThresholdApplied": False,
        "reattackFallbackDefined": False,
        "temporalDiagnosticReconstructed": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalDiagnosticStatus": "COMPLETE",
        "matrixControls": matrix_rows,
        "rows": audio_rows,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
