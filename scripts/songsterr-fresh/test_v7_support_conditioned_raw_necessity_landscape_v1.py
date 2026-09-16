#!/usr/bin/env python3
"""First-run synthetic-only gate for the support-conditioned raw landscape."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge
import v7_dual_view_diagnostics_v1 as dual
import v7_fixed_feature_competition_diagnostics_v1 as fixed
import v7_support_conditioned_raw_necessity_landscape_v1 as diagnostic

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


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    fixture_id = str(fixture["id"])
    selected_midi = int(fixture["selectedMidi"])
    audio = v6._fixture_audio(fixture)
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    payload = diagnostic.evaluate_support_conditioned_raw_landscape(
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
    if payload.get("rawNecessityThresholdDefined") is not False:
        raise MechanicalInvariantError(f"RAW_THRESHOLD_DEFINED:{fixture_id}")
    if payload.get("rankCutoffDefined") is not False:
        raise MechanicalInvariantError(f"RANK_CUTOFF_DEFINED:{fixture_id}")
    for forbidden in (
        "finalDecision",
        "successorClassification",
        "passed",
        "classification",
        "rawNecessityPassed",
        "topKPassed",
    ):
        if forbidden in payload:
            raise MechanicalInvariantError(f"FORBIDDEN_TOP_LEVEL_VERDICT:{fixture_id}:{forbidden}")

    _check_finite(payload, fixture_id)

    if payload.get("onsetAvailable") is True:
        onset = v6._onset_innovation_spectrum(audio, onset_sample)
        if onset.get("status") != "OK":
            raise MechanicalInvariantError(f"ONSET_RECONSTRUCTION:{fixture_id}")
        raw = np.asarray(onset["innovation"], dtype=np.float64)
        support = bridge.collapse_hann_lobes_to_peak_bands(raw)
        if np.any(support > raw) or np.any((support > 0.0) & ~(raw > 0.0)):
            raise MechanicalInvariantError(f"SUPPORT_BRIDGE_PROTECTION:{fixture_id}")

        expected_dual = dual.evaluate_dual_view_diagnostics(selected_midi, raw, frequencies)
        expected_support = expected_dual.get("supportView")
        if not isinstance(expected_support, dict):
            raise MechanicalInvariantError(f"EXPECTED_SUPPORT_VIEW_MISSING:{fixture_id}")
        expected_support_midis = list(expected_support.get("validCandidateMidis", []))
        if payload.get("supportValidMidis") != expected_support_midis:
            raise MechanicalInvariantError(f"SUPPORT_VALID_SET_MISMATCH:{fixture_id}")

        expected_fixed_payload = fixed.evaluate_fixed_feature_competition_diagnostic(
            audio,
            onset_sample,
            selected_midi,
            frequencies,
        )
        expected_fixed_fits = expected_fixed_payload.get("fixedFeatureFits")
        if not isinstance(expected_fixed_fits, dict):
            raise MechanicalInvariantError(f"EXPECTED_FIXED_FITS_MISSING:{fixture_id}")
        expected_all49 = expected_fixed_fits.get("gateFree49FixedFit")
        if not isinstance(expected_all49, dict) or expected_all49.get("available") is not True:
            raise MechanicalInvariantError(f"EXPECTED_ALL49_FIT_UNAVAILABLE:{fixture_id}")

        raw_problem = payload.get("fixedRawProblem")
        if not isinstance(raw_problem, dict):
            raise MechanicalInvariantError(f"FIXED_RAW_PROBLEM_MISSING:{fixture_id}")
        if raw_problem.get("candidateMidis") != expected_all49.get("candidateMidis"):
            raise MechanicalInvariantError(f"ALL49_CANDIDATES_MISMATCH:{fixture_id}")
        if int(raw_problem.get("candidateCount", -1)) != 49:
            raise MechanicalInvariantError(f"ALL49_CANDIDATE_COUNT:{fixture_id}")
        if raw_problem.get("featureBins") != expected_all49.get("fixedFeatureBins"):
            raise MechanicalInvariantError(f"FIXED_FEATURE_BINS_MISMATCH:{fixture_id}")
        if int(raw_problem.get("featureBinCount", -1)) != int(expected_all49.get("fixedFeatureBinCount", -2)):
            raise MechanicalInvariantError(f"FIXED_FEATURE_COUNT_MISMATCH:{fixture_id}")
        _assert_close(
            raw_problem.get("featureEnergy"),
            expected_all49.get("fixedFeatureEnergy"),
            f"{fixture_id}.featureEnergy",
        )
        _assert_close(
            raw_problem.get("fullResidual"),
            expected_all49.get("fullResidual"),
            f"{fixture_id}.fullResidual",
        )
        if _canonical(raw_problem.get("coefficientRows")) != _canonical(expected_all49.get("coefficientRows")):
            raise MechanicalInvariantError(f"ALL49_COEFFICIENT_ROWS_MISMATCH:{fixture_id}")

        support_templates = {
            midi: dict(v3.evaluate_candidate_template(midi, support, frequencies))
            for midi in range(v6.PLAYABLE_MIDI_MIN, v6.PLAYABLE_MIDI_MAX + 1)
        }
        landscape = payload.get("landscapeRows")
        if not isinstance(landscape, list):
            raise MechanicalInvariantError(f"LANDSCAPE_MISSING:{fixture_id}")
        observed_midis = sorted(int(row["midi"]) for row in landscape)
        if observed_midis != expected_support_midis:
            raise MechanicalInvariantError(f"LANDSCAPE_MEMBERSHIP:{fixture_id}")
        if len({int(row["midi"]) for row in landscape}) != len(landscape):
            raise MechanicalInvariantError(f"LANDSCAPE_DUPLICATE_MIDI:{fixture_id}")

        by_midi = {int(row["midi"]): row for row in landscape}
        coeff_by_midi = {
            int(row["midi"]): float(row["coefficient"])
            for row in raw_problem.get("coefficientRows", [])
        }
        for candidate_midi in expected_support_midis:
            row = by_midi[candidate_midi]
            if row.get("selectedForFixture") is not bool(candidate_midi == selected_midi):
                raise MechanicalInvariantError(f"SELECTED_FLAG:{fixture_id}:{candidate_midi}")
            if _canonical(row.get("supportTemplate")) != _canonical(support_templates[candidate_midi]):
                raise MechanicalInvariantError(f"SUPPORT_TEMPLATE:{fixture_id}:{candidate_midi}")
            expected_evidence = dual._candidate_evidence_diagnostic(
                support_templates[candidate_midi], support
            )
            expected_owners = dual._owner_diagnostics(
                candidate_midi,
                support_templates[candidate_midi],
                support_templates,
            )
            if _canonical(row.get("candidateEvidence")) != _canonical(expected_evidence):
                raise MechanicalInvariantError(f"EVIDENCE_DIAGNOSTIC:{fixture_id}:{candidate_midi}")
            if _canonical(row.get("ownerDiagnostics")) != _canonical(expected_owners):
                raise MechanicalInvariantError(f"OWNER_DIAGNOSTIC:{fixture_id}:{candidate_midi}")
            _assert_close(
                row.get("fullFitCoefficient"),
                coeff_by_midi[candidate_midi],
                f"{fixture_id}.{candidate_midi}.coefficient",
            )
            _assert_close(
                row.get("fullResidual"),
                raw_problem.get("fullResidual"),
                f"{fixture_id}.{candidate_midi}.fullResidual",
            )
            necessity = float(row["rawNecessityFraction"])
            coefficient = float(row["fullFitCoefficient"])
            expected_greater_necessity = sum(
                1
                for other in landscape
                if float(other["rawNecessityFraction"]) > necessity
            )
            expected_greater_coefficient = sum(
                1
                for other in landscape
                if float(other["fullFitCoefficient"]) > coefficient
            )
            if int(row.get("strictlyGreaterRawNecessityCount", -1)) != expected_greater_necessity:
                raise MechanicalInvariantError(f"NECESSITY_ORDER_COUNT:{fixture_id}:{candidate_midi}")
            if int(row.get("strictlyGreaterPositiveCoefficientCount", -1)) != expected_greater_coefficient:
                raise MechanicalInvariantError(f"COEFFICIENT_ORDER_COUNT:{fixture_id}:{candidate_midi}")

        expected_order = sorted(
            landscape,
            key=lambda row: (-float(row["rawNecessityFraction"]), int(row["midi"])),
        )
        if _canonical(landscape) != _canonical(expected_order):
            raise MechanicalInvariantError(f"LANDSCAPE_SERIAL_ORDER:{fixture_id}")

        selected_row = payload.get("selectedLandscapeRow")
        if selected_midi in expected_support_midis:
            if not isinstance(selected_row, dict):
                raise MechanicalInvariantError(f"SELECTED_LANDSCAPE_ROW_MISSING:{fixture_id}")
            if _canonical(selected_row) != _canonical(by_midi[selected_midi]):
                raise MechanicalInvariantError(f"SELECTED_LANDSCAPE_ROW_MISMATCH:{fixture_id}")
            _assert_close(
                selected_row.get("rawNecessityFraction"),
                expected_all49.get("necessityFraction"),
                f"{fixture_id}.selectedNecessity",
            )
            _assert_close(
                selected_row.get("fullFitCoefficient"),
                expected_all49.get("selectedCoefficient"),
                f"{fixture_id}.selectedCoefficient",
            )
        elif selected_row is not None:
            raise MechanicalInvariantError(f"SELECTED_ROW_FOR_SUPPORT_INELIGIBLE:{fixture_id}")
    else:
        for key in (
            "supportValidMidis",
            "fixedRawProblem",
            "landscapeRows",
            "selectedLandscapeRow",
        ):
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
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")

    if diagnostic.CONTRACT != "songsterr-fresh-v7-support-conditioned-raw-necessity-landscape-v1":
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
    selected_landscape_available_count = sum(
        1 for row in rows if isinstance(row["diagnostic"].get("selectedLandscapeRow"), dict)
    )
    landscape_candidate_row_count = sum(
        len(row["diagnostic"].get("landscapeRows") or []) for row in rows
    )

    output = {
        "contract": "songsterr-fresh-v7-support-conditioned-raw-necessity-landscape-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "selectedLandscapeAvailableCount": selected_landscape_available_count,
        "landscapeCandidateRowCount": landscape_candidate_row_count,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "rawNecessityThresholdDefined": False,
        "rankCutoffDefined": False,
        "temporalDiagnosticReconstructed": False,
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
