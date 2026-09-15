#!/usr/bin/env python3
"""Synthetic-only tests for purpose-built capture-manifest V2.2."""
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


module = _load("capture_v22", "purpose_built_capture_manifest_contract_v2_2.py")
v21_fixture = _load(
    "capture_v21_fixture", "test_purpose_built_capture_manifest_contract_v2_1.py"
)
provenance = _load(
    "calibration_provenance", "reference_calibration_package_provenance_v1.py"
)

VALIDATION_SHA = "f" * 64


def valid_manifest() -> dict:
    manifest = v21_fixture.valid_manifest()
    manifest["contract"] = module.CONTRACT
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "package"
        package_manifest = provenance.build_synthetic_fixture(root)
        package_result = provenance.validate_package(package_manifest, root)
    assert package_result["contractValid"] is True, package_result
    binding = copy.deepcopy(package_result["packageBinding"])
    binding_sha = package_result["packageBindingSha256"]

    corpus = manifest["corpus"]
    corpus["hardware"]["configuration"]["sha256"] = binding["hardwareConfiguration"]["sha256"]
    corpus["hardware"]["instrumentSetup"]["setupSha256"] = binding["instrumentSetupSha256"]
    corpus["referenceCalibration"]["calibrationId"] = binding["calibrationId"]
    corpus["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"] = binding[
        "maxAbsoluteOnsetErrorSeconds"
    ]
    corpus["referenceCalibrationPackage"] = {
        "contract": module.PACKAGE_CONTRACT,
        "calibrationId": binding["calibrationId"],
        "packageBindingSha256": binding_sha,
        "validationResultSha256": VALIDATION_SHA,
        "packageBinding": binding,
    }

    for attempt in manifest["attempts"]:
        if attempt.get("admitted") is True:
            reference = attempt["reference"]
            reference["configurationSha256"] = binding["hardwareConfiguration"]["sha256"]
            reference["calibrationId"] = binding["calibrationId"]
            reference["calibrationPackageBindingSha256"] = binding_sha
    return manifest


def rebind(manifest: dict) -> str:
    package = manifest["corpus"]["referenceCalibrationPackage"]
    binding_sha = module._canonical_sha256(package["packageBinding"])
    package["packageBindingSha256"] = binding_sha
    for attempt in manifest["attempts"]:
        if attempt.get("admitted") is True:
            attempt["reference"]["calibrationPackageBindingSha256"] = binding_sha
    return binding_sha


class CaptureManifestV22Tests(unittest.TestCase):
    def test_01_valid_v22_passes(self):
        result = module.validate_manifest(valid_manifest())
        self.assertTrue(result["contractValid"], result)
        self.assertTrue(result["mayAdvanceToReferenceBlindStructuralAudit"])
        self.assertEqual(
            result["calibrationPackageBridgeVersion"],
            "capture-manifest-calibration-package-bridge-v1",
        )
        self.assertEqual(len(result["calibrationPackageBindingSha256"]), 64)

    def test_02_same_slot_retry_continuity_still_passes(self):
        manifest = valid_manifest()
        self.assertEqual(
            manifest["attempts"][0]["underlyingPerformanceId"],
            manifest["attempts"][1]["underlyingPerformanceId"],
        )
        result = module.validate_manifest(manifest)
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["admittedUnderlyingPerformanceCount"], 1)

    def test_03_inherited_first_pass_rule_still_fails_closed(self):
        manifest = valid_manifest()
        manifest["attempts"][0]["acquisitionQa"] = {"status": "PASS", "reason": None}
        manifest["attempts"][0]["admitted"] = False
        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertTrue(any("PASS_ATTEMPT_MUST_BE_ADMITTED" in e for e in result["errors"]))

    def test_04_inherited_structural_blocker_still_blocks_advance(self):
        manifest = valid_manifest()
        manifest["attempts"][1]["reference"]["declaredStructuralSummary"]["sameKeyOverlapCount"] = 1
        result = module.validate_manifest(manifest)
        self.assertTrue(result["contractValid"], result)
        self.assertFalse(result["mayAdvanceToReferenceBlindStructuralAudit"])

    def test_05_inherited_policy_change_still_fails_closed(self):
        manifest = valid_manifest()
        manifest["policyBoundary"]["modelValidationComplete"] = True
        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertTrue(any("POLICY_BOUNDARY_CHANGED:modelValidationComplete" in e for e in result["errors"]))

    def test_06_wrong_or_missing_package_object_fails(self):
        manifest = valid_manifest()
        del manifest["corpus"]["referenceCalibrationPackage"]
        result = module.validate_manifest(manifest)
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_OBJECT_REQUIRED", result["errors"])
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["contract"] = "wrong"
        result = module.validate_manifest(manifest)
        self.assertTrue(any(e.startswith("REFERENCE_CALIBRATION_PACKAGE_CONTRACT_MISMATCH") for e in result["errors"]))

    def test_07_malformed_binding_or_validation_sha_fails(self):
        manifest = valid_manifest()
        package = manifest["corpus"]["referenceCalibrationPackage"]
        package["packageBindingSha256"] = "bad"
        package["validationResultSha256"] = "bad"
        result = module.validate_manifest(manifest)
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID", result["errors"])
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_SHA256_INVALID", result["errors"])

    def test_08_canonical_package_binding_hash_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"]["softwareVersion"] = "changed"
        result = module.validate_manifest(manifest)
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH", result["errors"])

    def test_09_calibration_id_linkage_mismatches_fail(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["calibrationId"] = "other"
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_BINDING_CALIBRATION_ID_MISMATCH", result["errors"])
        self.assertIn("CALIBRATION_PACKAGE_LEGACY_CALIBRATION_ID_MISMATCH", result["errors"])

    def test_10_hardware_configuration_sha_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["hardware"]["configuration"]["sha256"] = "1" * 64
        manifest["attempts"][1]["reference"]["configurationSha256"] = "1" * 64
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_11_instrument_setup_sha_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["hardware"]["instrumentSetup"]["setupSha256"] = "2" * 64
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_MISMATCH", result["errors"])

    def test_12_package_firewall_mismatch_fails(self):
        for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
            with self.subTest(field=field):
                manifest = valid_manifest()
                manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][field] = True
                rebind(manifest)
                result = module.validate_manifest(manifest)
                self.assertFalse(result["contractValid"])
                self.assertTrue(any(field.upper() in e for e in result["errors"]))

    def test_13_package_timing_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["maxAbsoluteOnsetErrorSeconds"] = 0.020
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_LEGACY_TIMING_ERROR_MISMATCH", result["errors"])

    def test_14_decoder_identity_and_hashes_required(self):
        manifest = valid_manifest()
        decoder = manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"]
        decoder["decoderId"] = ""
        decoder["code"]["sha256"] = "bad"
        decoder["configuration"]["sha256"] = "bad"
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_DECODER_ID_REQUIRED", result["errors"])
        self.assertIn("CALIBRATION_PACKAGE_DECODER_CODE_SHA256_INVALID", result["errors"])
        self.assertIn("CALIBRATION_PACKAGE_DECODER_CONFIGURATION_SHA256_INVALID", result["errors"])

    def test_15_admitted_reference_binding_required_and_must_match(self):
        manifest = valid_manifest()
        del manifest["attempts"][1]["reference"]["calibrationPackageBindingSha256"]
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID", result["errors"])
        manifest = valid_manifest()
        manifest["attempts"][1]["reference"]["calibrationPackageBindingSha256"] = "0" * 64
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH", result["errors"])

    def test_16_nonadmitted_attempt_may_omit_package_binding(self):
        manifest = valid_manifest()
        self.assertNotIn("reference", manifest["attempts"][0])
        result = module.validate_manifest(manifest)
        self.assertTrue(result["contractValid"], result)

    def test_17_population_sha_changes_with_package_identity_and_is_deterministic(self):
        manifest_a = valid_manifest()
        result_a1 = module.validate_manifest(copy.deepcopy(manifest_a))
        result_a2 = module.validate_manifest(copy.deepcopy(manifest_a))
        self.assertEqual(
            result_a1["admittedPopulationManifestSha256"],
            result_a2["admittedPopulationManifestSha256"],
        )
        manifest_b = copy.deepcopy(manifest_a)
        manifest_b["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"]["softwareVersion"] = "2.0-synthetic"
        rebind(manifest_b)
        result_b = module.validate_manifest(manifest_b)
        self.assertTrue(result_b["contractValid"], result_b)
        self.assertNotEqual(
            result_a1["admittedPopulationManifestSha256"],
            result_b["admittedPopulationManifestSha256"],
        )

    def test_18_authorization_boundary_remains_closed(self):
        result = module.validate_manifest(valid_manifest())
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
