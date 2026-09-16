#!/usr/bin/env python3
"""Local synthetic/mechanical integration regression for V7 successor research.

The frozen V3 iteration-3 harness remains the fixture source. Its iteration-3
composite call is replaced in memory with a V7 adapter so the frozen synthetic
expectations exercise the successor mapping without editing any frozen file.
"""

from __future__ import annotations

import json
import math

import numpy as np

import onset_birth_corroboration_v6 as frozen_v6
import onset_birth_corroboration_v7 as v7
import physical_template_plausibility_v3 as base
import physical_template_plausibility_v3_iteration3 as frozen_v3
import test_physical_template_plausibility_v3_iteration3 as frozen_suite

EXPECTED_FIXTURE_COUNT = 34
EXPECTED_COMPOSITE_FIXTURE_COUNT = 33
EXPECTED_DIRECT_TEMPLATE_FIXTURE_COUNT = 1
EXPECTED_SCALE_OUTCOMES = {
    "low_scale_valid_harmonic_a4": True,
    "low_scale_broadband_noise": False,
    "high_scale_broadband_noise": False,
}


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


class _V7AsFrozenIteration3Adapter:
    CONTRACT = frozen_v3.CONTRACT
    VERSION = frozen_v3.VERSION
    MIN_CANDIDATE_EVIDENCE_FRACTION = frozen_v3.MIN_CANDIDATE_EVIDENCE_FRACTION

    @staticmethod
    def evaluate_evidence_significance_composite(selected_midi, innovation, frequencies):
        return v7.evaluate_in_memory_innovation(
            selected_midi,
            innovation,
            frequencies,
        )


def _install_v7_adapter() -> None:
    # In-memory test wiring only. The frozen iteration-3 source file is not edited.
    frozen_suite.iteration3 = _V7AsFrozenIteration3Adapter()


def _append_mismatch(mismatches: list[dict], name: str, reason: str, **details) -> None:
    row = {"name": name, "reason": reason}
    row.update(details)
    mismatches.append(row)


def _mechanical_checks(mismatches: list[dict]) -> list[dict]:
    checks: list[dict] = []

    dependency_ok = bool(v7._dependency_contract_ok())
    checks.append({"name": "frozen_dependency_contracts", "passed": dependency_ok})
    if not dependency_ok:
        _append_mismatch(mismatches, "__mechanical__", "FROZEN_DEPENDENCY_CONTRACT_MISMATCH")

    v7_grid = v7.expected_frequency_grid()
    base_grid = base.expected_frequencies()
    grid_ok = bool(
        v7_grid.shape == base_grid.shape
        and np.allclose(v7_grid, base_grid, rtol=0.0, atol=1e-12)
        and v7_grid.size == frozen_v6.FFT_SIZE // 2 + 1
    )
    checks.append({"name": "frozen_frequency_grid", "passed": grid_ok})
    if not grid_ok:
        _append_mismatch(mismatches, "__mechanical__", "FREQUENCY_GRID_CHANGED")

    invalid_midi = v7.evaluate_in_memory_innovation(
        True,
        np.zeros(base.FFT_SIZE // 2 + 1, dtype=np.float64),
        base_grid,
    )
    invalid_midi_ok = bool(
        invalid_midi.get("passed") is False
        and invalid_midi.get("status") == "MIDI_INTEGER_REQUIRED"
    )
    checks.append({"name": "boolean_midi_fail_closed", "passed": invalid_midi_ok})
    if not invalid_midi_ok:
        _append_mismatch(
            mismatches,
            "__mechanical__",
            "BOOLEAN_MIDI_NOT_FAIL_CLOSED",
            actualStatus=invalid_midi.get("status"),
        )

    boundary_audio = np.zeros(frozen_v6.SAMPLE_RATE, dtype=np.float64)
    boundary = v7.evaluate_in_memory_audio_event(boundary_audio, 0, 69)
    boundary_ok = bool(
        boundary.get("passed") is False
        and boundary.get("status") == "REQUIRED_PRE_POST_CONTEXT_OUTSIDE_AUDIO"
        and boundary.get("selectedMidi") == 69
    )
    checks.append({"name": "v6_context_boundary_fail_closed", "passed": boundary_ok})
    if not boundary_ok:
        _append_mismatch(
            mismatches,
            "__mechanical__",
            "V6_CONTEXT_BOUNDARY_CHANGED",
            actualStatus=boundary.get("status"),
        )

    return checks


def collect_v7_mismatches(report: dict) -> tuple[list[dict], list[dict]]:
    mismatches = list(report.get("mismatches", []))
    records = list(report.get("fixtures", []))

    if report.get("fixtureCount") != EXPECTED_FIXTURE_COUNT or len(records) != EXPECTED_FIXTURE_COUNT:
        _append_mismatch(
            mismatches,
            "__suite__",
            "FIXTURE_COUNT_MISMATCH",
            expected=EXPECTED_FIXTURE_COUNT,
            observed=len(records),
        )

    composite_records = [row for row in records if row.get("kind") == "composite"]
    direct_records = [row for row in records if row.get("kind") == "direct-template"]
    if len(composite_records) != EXPECTED_COMPOSITE_FIXTURE_COUNT:
        _append_mismatch(
            mismatches,
            "__suite__",
            "COMPOSITE_FIXTURE_COUNT_MISMATCH",
            expected=EXPECTED_COMPOSITE_FIXTURE_COUNT,
            observed=len(composite_records),
        )
    if len(direct_records) != EXPECTED_DIRECT_TEMPLATE_FIXTURE_COUNT:
        _append_mismatch(
            mismatches,
            "__suite__",
            "DIRECT_TEMPLATE_FIXTURE_COUNT_MISMATCH",
            expected=EXPECTED_DIRECT_TEMPLATE_FIXTURE_COUNT,
            observed=len(direct_records),
        )

    for record in composite_records:
        name = str(record.get("name"))
        actual = record.get("actual")
        if not isinstance(actual, dict):
            _append_mismatch(mismatches, name, "ACTUAL_NOT_MAPPING")
            continue

        if actual.get("successorContract") != v7.CONTRACT:
            _append_mismatch(
                mismatches,
                name,
                "FIXTURE_DID_NOT_ROUTE_THROUGH_V7",
                successorContract=actual.get("successorContract"),
            )

        v3_result = actual.get("v3Composite")
        if not isinstance(v3_result, dict):
            _append_mismatch(mismatches, name, "V3_COMPOSITE_NOT_PRESERVED")
        elif v3_result.get("passed") is not True and actual.get("passed") is True:
            _append_mismatch(mismatches, name, "ILLEGAL_PROMOTION_OF_V3_FAILURE")

        selected_midi = record.get("selectedMidi")
        if selected_midi is not None and actual.get("selectedMidi") != int(selected_midi):
            _append_mismatch(
                mismatches,
                name,
                "SELECTED_MIDI_IDENTITY_CHANGED",
                expected=int(selected_midi),
                observed=actual.get("selectedMidi"),
            )

        if actual.get("passed") is True:
            necessity = actual.get("necessityFraction")
            evidence = actual.get("candidateEvidenceFraction")
            if not isinstance(necessity, (int, float)) or not math.isfinite(float(necessity)):
                _append_mismatch(mismatches, name, "PASS_WITHOUT_FINITE_NECESSITY")
            elif float(necessity) < v7.EXPECTED_NECESSITY_FRACTION_MIN:
                _append_mismatch(
                    mismatches,
                    name,
                    "PASS_BELOW_NECESSITY_THRESHOLD",
                    necessityFraction=float(necessity),
                )
            if not isinstance(evidence, (int, float)) or not math.isfinite(float(evidence)):
                _append_mismatch(mismatches, name, "PASS_WITHOUT_FINITE_CANDIDATE_EVIDENCE")
            elif float(evidence) < v7.EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN:
                _append_mismatch(
                    mismatches,
                    name,
                    "PASS_BELOW_CANDIDATE_EVIDENCE_THRESHOLD",
                    candidateEvidenceFraction=float(evidence),
                )
            if actual.get("vetoingOwners") != []:
                _append_mismatch(mismatches, name, "PASS_WITH_VETOING_OWNER")

    if direct_records:
        direct = direct_records[0]
        actual = direct.get("actual", {})
        if (
            direct.get("name") != "input_fewer_than_three_available_harmonics"
            or actual.get("valid") is not False
            or actual.get("status") != "FEWER_THAN_THREE_AVAILABLE_HARMONICS"
        ):
            _append_mismatch(
                mismatches,
                "input_fewer_than_three_available_harmonics",
                "FROZEN_DIRECT_TEMPLATE_CONTROL_CHANGED",
                actual=actual,
            )

    alias = next(
        (row for row in records if row.get("name") == "octave_alias_lower_a3_selected_a4"),
        None,
    )
    if not isinstance(alias, dict):
        _append_mismatch(mismatches, "octave_alias_lower_a3_selected_a4", "ALIAS_FIXTURE_MISSING")
    else:
        actual = alias.get("actual", {})
        owners = [int(row.get("ownerMidi")) for row in actual.get("vetoingOwners", [])]
        if actual.get("passed") is not False or actual.get("status") != "LOWER_OWNER_EXPLAINS_SELECTED" or 57 not in owners:
            _append_mismatch(
                mismatches,
                "octave_alias_lower_a3_selected_a4",
                "LOWER_OWNER_ALIAS_PROTECTION_CHANGED",
                actualStatus=actual.get("status"),
                owners=owners,
            )

    by_name = {str(row.get("name")): row for row in records}
    for name, expected_pass in EXPECTED_SCALE_OUTCOMES.items():
        row = by_name.get(name)
        actual = row.get("actual", {}) if isinstance(row, dict) else {}
        if not isinstance(row, dict) or (actual.get("passed") is True) is not expected_pass:
            _append_mismatch(
                mismatches,
                name,
                "SCALE_CONTROL_CHANGED",
                expectedPass=expected_pass,
                observedPass=actual.get("passed") is True,
            )

    mechanical_checks = _mechanical_checks(mismatches)
    return mismatches, mechanical_checks


def run_integration_suite() -> dict:
    _install_v7_adapter()
    frozen_report = frozen_suite.run_fixture_suite()
    mismatches, mechanical_checks = collect_v7_mismatches(frozen_report)
    records = list(frozen_report.get("fixtures", []))
    return {
        "contract": "songsterr-fresh-v7-successor-integration-synthetic-test-v1",
        "fixtureCount": len(records),
        "compositeFixtureCount": sum(1 for row in records if row.get("kind") == "composite"),
        "directTemplateFixtureCount": sum(1 for row in records if row.get("kind") == "direct-template"),
        "mismatchCount": len(mismatches),
        "mismatches": mismatches,
        "mechanicalChecks": mechanical_checks,
        "fixtures": records,
        "successorContract": v7.CONTRACT,
        "frozenV3Contract": frozen_v3.CONTRACT,
    }


def main() -> int:
    reports = [run_integration_suite() for _ in range(3)]
    serializations = [canonical_json(report) for report in reports]
    deterministic = bool(serializations[0] == serializations[1] == serializations[2])
    first = reports[0]
    passed = bool(deterministic and first["mismatchCount"] == 0)
    summary = {
        "contract": first["contract"],
        "fixtureCount": first["fixtureCount"],
        "compositeFixtureCount": first["compositeFixtureCount"],
        "directTemplateFixtureCount": first["directTemplateFixtureCount"],
        "mechanicalCheckCount": len(first["mechanicalChecks"]),
        "mismatchCount": first["mismatchCount"],
        "mismatches": first["mismatches"],
        "repetitions": 3,
        "deterministic": deterministic,
        "result": "PASS" if passed else "FAIL",
    }
    print(canonical_json(summary))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
