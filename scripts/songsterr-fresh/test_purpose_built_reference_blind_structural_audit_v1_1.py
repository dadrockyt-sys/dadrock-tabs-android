#!/usr/bin/env python3
"""Synthetic-only contract tests for reference-blind structural audit V1.1."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bridge = _load(
    "structural_audit_v1_1",
    "purpose_built_reference_blind_structural_audit_v1_1.py",
)
v1_fixture = _load(
    "structural_audit_v1_fixture",
    "test_purpose_built_reference_blind_structural_audit_v1.py",
)
provenance = _load(
    "reference_calibration_package_provenance_v1_for_v11",
    "reference_calibration_package_provenance_v1.py",
)


def valid_v1_sources() -> tuple[dict[str, bytes], dict[str, str]]:
    hardware, births, latches, clock = v1_fixture.base_documents()
    raw = {
        "hardware": v1_fixture.render(hardware),
        "birth": v1_fixture.render(births),
        "pitchLatch": v1_fixture.render(latches),
        "clockSync": v1_fixture.render(clock),
    }
    expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    return raw, expected


def valid_provenance_result() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "package"
        manifest = provenance.build_synthetic_fixture(root)
        result = provenance.validate_package(manifest, root)
    assert result["contractValid"] is True, result
    return copy.deepcopy(result)


def render_provenance(value: Any) -> bytes:
    return bridge.canonical_json_bytes(value)


def run_bridge(
    *,
    raw_sources: dict[str, bytes] | None = None,
    expected_sha256: dict[str, str] | None = None,
    provenance_result: Any | None = None,
    provenance_raw: Any | None = None,
    expected_provenance_sha: Any | None = None,
    declared_provenance_sha: Any | None = None,
    declared_binding_sha: Any | None = None,
):
    if raw_sources is None or expected_sha256 is None:
        raw_sources, expected_sha256 = valid_v1_sources()
    if provenance_result is None:
        provenance_result = valid_provenance_result()
    if provenance_raw is None:
        provenance_raw = render_provenance(provenance_result)
    default_provenance_sha = (
        hashlib.sha256(provenance_raw).hexdigest()
        if isinstance(provenance_raw, bytes)
        else None
    )
    if expected_provenance_sha is None:
        expected_provenance_sha = default_provenance_sha
    if declared_provenance_sha is None:
        declared_provenance_sha = default_provenance_sha
    if declared_binding_sha is None:
        declared_binding_sha = provenance_result.get("packageBindingSha256")
    return bridge.audit_raw_sources_v1_1(
        raw_sources=raw_sources,
        expected_sha256=expected_sha256,
        calibration_provenance_result=provenance_raw,
        expected_calibration_provenance_result_sha256=expected_provenance_sha,
        declared_provenance_result_sha256=declared_provenance_sha,
        declared_calibration_package_binding_sha256=declared_binding_sha,
    )


def rebind_result(result: dict[str, Any]) -> None:
    result["packageBindingSha256"] = bridge.sha256_bytes(
        bridge.canonical_json_bytes(result["packageBinding"])
    )


class StructuralAuditV11Tests(unittest.TestCase):
    def assert_bridge_fail(self, result: dict[str, Any]) -> None:
        self.assertFalse(result["contractValid"])
        self.assertFalse(result["datasetStructurallySuitable"])
        self.assertFalse(result["authoritativeStructuralSuitabilityEstablished"])
        self.assertFalse(result["realCalibrationAuthorized"])
        self.assertFalse(result["realHoldoutCaptureAuthorized"])
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])

    def test_01_complete_v11_synthetic_inputs_pass(self):
        result = run_bridge()
        self.assertTrue(result["contractValid"], result)
        self.assertTrue(result["datasetStructurallySuitable"])
        self.assertTrue(result["authoritativeStructuralSuitabilityEstablished"])
        self.assertEqual(result["calibrationProvenanceBridgeViolationCount"], 0)
        self.assertEqual(result["derivedNoteEventCount"], 2)
        self.assertTrue(result["inheritedV1DerivedPopulationSha256"])
        self.assertTrue(result["derivedPopulationSha256"])
        self.assertEqual(result["populationIdentityVersion"], bridge.POPULATION_IDENTITY_VERSION)

    def test_02_original_v1_nominal_semantics_remain_identical(self):
        raw, expected = valid_v1_sources()
        inherited = bridge.v1.audit_raw_sources(raw_sources=raw, expected_sha256=expected)
        result = run_bridge(raw_sources=copy.deepcopy(raw), expected_sha256=copy.deepcopy(expected))
        self.assertTrue(inherited["contractValid"], inherited)
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["sourceSha256"], inherited["sourceSha256"])
        self.assertEqual(result["derivedNoteEventCount"], inherited["derivedNoteEventCount"])
        self.assertEqual(
            result["inheritedV1DerivedPopulationSha256"],
            inherited["derivedPopulationSha256"],
        )
        self.assertEqual(result["blockerCounts"], inherited["blockerCounts"])

    def test_03_provenance_raw_value_not_bytes_fails(self):
        result = run_bridge(provenance_raw="not-bytes")
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_RESULT_NOT_BYTES", result["errors"])

    def test_04_malformed_provenance_expected_sha_fails(self):
        result = run_bridge(expected_provenance_sha="bad")
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_EXPECTED_SHA256_INVALID", result["errors"])

    def test_05_provenance_hash_mismatch_short_circuits_before_parse(self):
        raw = b"deliberately not json"
        result = run_bridge(
            provenance_raw=raw,
            expected_provenance_sha="0" * 64,
            declared_provenance_sha="0" * 64,
        )
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_RESULT_SHA256_MISMATCH", result["errors"])
        self.assertFalse(any("INVALID_JSON" in e for e in result["errors"]))

    def test_06_malformed_declared_v22_provenance_sha_fails(self):
        result = run_bridge(declared_provenance_sha="bad")
        self.assert_bridge_fail(result)
        self.assertIn("DECLARED_PROVENANCE_RESULT_SHA256_INVALID", result["errors"])

    def test_07_malformed_declared_v22_package_binding_sha_fails(self):
        result = run_bridge(declared_binding_sha="bad")
        self.assert_bridge_fail(result)
        self.assertIn("DECLARED_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID", result["errors"])

    def test_08_expected_provenance_sha_must_equal_v22_declared_sha(self):
        result_obj = valid_provenance_result()
        raw = render_provenance(result_obj)
        actual = hashlib.sha256(raw).hexdigest()
        different = ("0" if actual[0] != "0" else "1") + actual[1:]
        result = run_bridge(
            provenance_result=result_obj,
            provenance_raw=raw,
            expected_provenance_sha=actual,
            declared_provenance_sha=different,
        )
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_EXPECTED_V22_SHA256_MISMATCH", result["errors"])

    def test_09_invalid_utf8_or_json_fails_after_successful_hash(self):
        for raw in (b"{not-json", b"\xff\xfe"):
            with self.subTest(raw=raw):
                sha = hashlib.sha256(raw).hexdigest()
                result = run_bridge(
                    provenance_raw=raw,
                    expected_provenance_sha=sha,
                    declared_provenance_sha=sha,
                )
                self.assert_bridge_fail(result)
                self.assertTrue(any("CALIBRATION_PROVENANCE_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_10_provenance_result_contract_mismatch_fails(self):
        obj = valid_provenance_result()
        obj["contract"] = "wrong"
        result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_RESULT_CONTRACT_MISMATCH", result["errors"])

    def test_11_contract_valid_false_provenance_result_fails(self):
        obj = valid_provenance_result()
        obj["contractValid"] = False
        result = run_bridge(provenance_result=obj)
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_RESULT_CONTRACT_NOT_VALID", result["errors"])

    def test_12_nonempty_provenance_result_errors_fail(self):
        obj = valid_provenance_result()
        obj["errors"] = ["synthetic-error"]
        result = run_bridge(provenance_result=obj)
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_RESULT_ERRORS_NOT_EMPTY", result["errors"])

    def test_13_malformed_parsed_package_binding_sha_fails(self):
        obj = valid_provenance_result()
        obj["packageBindingSha256"] = "bad"
        result = run_bridge(provenance_result=obj, declared_binding_sha="0" * 64)
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_PACKAGE_BINDING_SHA256_INVALID", result["errors"])

    def test_14_parsed_package_binding_sha_must_match_v22_declaration(self):
        obj = valid_provenance_result()
        result = run_bridge(provenance_result=obj, declared_binding_sha="0" * 64)
        self.assert_bridge_fail(result)
        self.assertIn(
            "CALIBRATION_PROVENANCE_PACKAGE_BINDING_SHA256_DECLARATION_MISMATCH",
            result["errors"],
        )

    def test_15_canonical_package_binding_hash_mismatch_fails(self):
        obj = valid_provenance_result()
        declared = obj["packageBindingSha256"]
        obj["packageBinding"]["decoder"]["softwareVersion"] = "changed-without-rebind"
        result = run_bridge(provenance_result=obj, declared_binding_sha=declared)
        self.assert_bridge_fail(result)
        self.assertIn(
            "CALIBRATION_PROVENANCE_PACKAGE_BINDING_CANONICAL_SHA256_MISMATCH",
            result["errors"],
        )

    def test_16_any_package_firewall_violation_fails(self):
        for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
            with self.subTest(field=field):
                obj = valid_provenance_result()
                obj["packageBinding"][field] = True
                rebind_result(obj)
                result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
                self.assert_bridge_fail(result)
                self.assertTrue(any(field.upper() in e for e in result["errors"]))

    def test_17_package_timing_above_25_ms_fails(self):
        obj = valid_provenance_result()
        obj["packageBinding"]["maxAbsoluteOnsetErrorSeconds"] = 0.026
        rebind_result(obj)
        result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_PACKAGE_TIMING_EXCEEDS_BOUND", result["errors"])

    def test_18_missing_calibration_id_fails(self):
        obj = valid_provenance_result()
        obj["packageBinding"]["calibrationId"] = ""
        rebind_result(obj)
        result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
        self.assert_bridge_fail(result)
        self.assertIn("CALIBRATION_PROVENANCE_PACKAGE_CALIBRATION_ID_REQUIRED", result["errors"])

    def test_19_missing_decoder_id_or_version_fails(self):
        for field, expected in (
            ("decoderId", "CALIBRATION_PROVENANCE_PACKAGE_DECODER_ID_REQUIRED"),
            ("softwareVersion", "CALIBRATION_PROVENANCE_PACKAGE_DECODER_SOFTWARE_VERSION_REQUIRED"),
        ):
            with self.subTest(field=field):
                obj = valid_provenance_result()
                obj["packageBinding"]["decoder"][field] = ""
                rebind_result(obj)
                result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
                self.assert_bridge_fail(result)
                self.assertIn(expected, result["errors"])

    def test_20_malformed_decoder_code_or_configuration_sha_fails(self):
        for key, expected in (
            ("code", "CALIBRATION_PROVENANCE_PACKAGE_DECODER_CODE_SHA256_INVALID"),
            ("configuration", "CALIBRATION_PROVENANCE_PACKAGE_DECODER_CONFIGURATION_SHA256_INVALID"),
        ):
            with self.subTest(key=key):
                obj = valid_provenance_result()
                obj["packageBinding"]["decoder"][key]["sha256"] = "bad"
                rebind_result(obj)
                result = run_bridge(provenance_result=obj, declared_binding_sha=obj["packageBindingSha256"])
                self.assert_bridge_fail(result)
                self.assertIn(expected, result["errors"])

    def test_21_original_v1_hash_mismatch_still_fails(self):
        raw, expected = valid_v1_sources()
        raw["hardware"] = b"not json"
        expected["hardware"] = "0" * 64
        result = run_bridge(raw_sources=raw, expected_sha256=expected)
        self.assert_bridge_fail(result)
        self.assertIn("SOURCE_SHA256_MISMATCH:hardware", result["errors"])
        self.assertGreater(result["blockerCounts"]["sourceSha256MismatchCount"], 0)

    def test_22_original_v1_structural_blocker_still_fails_with_valid_bridge(self):
        hardware, births, latches, clock = v1_fixture.base_documents()
        latches["events"][0]["state"] = "AMBIGUOUS"
        raw = {
            "hardware": v1_fixture.render(hardware),
            "birth": v1_fixture.render(births),
            "pitchLatch": v1_fixture.render(latches),
            "clockSync": v1_fixture.render(clock),
        }
        expected = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
        result = run_bridge(raw_sources=raw, expected_sha256=expected)
        self.assert_bridge_fail(result)
        self.assertGreater(result["blockerCounts"]["ambiguousPitchStateCount"], 0)
        self.assertEqual(result["calibrationProvenanceBridgeViolationCount"], 0)

    def test_23_augmented_population_sha_changes_with_provenance_result_identity(self):
        obj_a = valid_provenance_result()
        result_a = run_bridge(provenance_result=obj_a)
        self.assertTrue(result_a["contractValid"], result_a)

        obj_b = copy.deepcopy(obj_a)
        obj_b["syntheticBridgeDiagnostic"] = "changes-result-bytes-only"
        result_b = run_bridge(provenance_result=obj_b, declared_binding_sha=obj_b["packageBindingSha256"])
        self.assertTrue(result_b["contractValid"], result_b)
        self.assertEqual(
            result_a["calibrationPackageBindingSha256"],
            result_b["calibrationPackageBindingSha256"],
        )
        self.assertNotEqual(
            result_a["calibrationProvenanceResultSha256"],
            result_b["calibrationProvenanceResultSha256"],
        )
        self.assertNotEqual(result_a["derivedPopulationSha256"], result_b["derivedPopulationSha256"])

    def test_24_augmented_population_sha_changes_with_package_binding_identity(self):
        obj_a = valid_provenance_result()
        result_a = run_bridge(provenance_result=obj_a)
        self.assertTrue(result_a["contractValid"], result_a)

        obj_b = copy.deepcopy(obj_a)
        obj_b["packageBinding"]["decoder"]["softwareVersion"] = "2.0-synthetic"
        rebind_result(obj_b)
        result_b = run_bridge(provenance_result=obj_b, declared_binding_sha=obj_b["packageBindingSha256"])
        self.assertTrue(result_b["contractValid"], result_b)
        self.assertNotEqual(
            result_a["calibrationPackageBindingSha256"],
            result_b["calibrationPackageBindingSha256"],
        )
        self.assertNotEqual(result_a["derivedPopulationSha256"], result_b["derivedPopulationSha256"])

    def test_25_original_v1_population_sha_is_unchanged_by_bridge_identity(self):
        obj_a = valid_provenance_result()
        obj_b = copy.deepcopy(obj_a)
        obj_b["syntheticBridgeDiagnostic"] = "different-result-bytes"
        result_a = run_bridge(provenance_result=obj_a)
        result_b = run_bridge(provenance_result=obj_b, declared_binding_sha=obj_b["packageBindingSha256"])
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"])
        self.assertEqual(
            result_a["inheritedV1DerivedPopulationSha256"],
            result_b["inheritedV1DerivedPopulationSha256"],
        )

    def test_26_canonical_validation_output_is_byte_deterministic(self):
        result_a = run_bridge()
        result_b = run_bridge()
        self.assertEqual(bridge.canonical_json_bytes(result_a), bridge.canonical_json_bytes(result_b))

    def test_27_authorization_remains_closed_on_pass(self):
        result = run_bridge()
        self.assertTrue(result["contractValid"], result)
        for key in (
            "realCalibrationAuthorized",
            "realHoldoutCaptureAuthorized",
            "basicPitchAuthorized",
            "v6Authorized",
            "correctnessAuthorized",
            "modelValidationComplete",
            "mayAdvanceDelivery",
        ):
            self.assertFalse(result[key])
        self.assertEqual(result["customerEligibleEvents"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
