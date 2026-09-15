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

VALIDATION_PATH = "calibration/reference-calibration-package-provenance-v1-result.json"
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
    corpus["hardware"]["configuration"]["configurationId"] = binding[
        "hardwareConfiguration"
    ]["configurationId"]
    corpus["hardware"]["configuration"]["sha256"] = binding[
        "hardwareConfiguration"
    ]["sha256"]
    corpus["hardware"]["instrumentSetup"]["setupSha256"] = binding[
        "instrumentSetupSha256"
    ]
    corpus["referenceCalibration"]["calibrationId"] = binding["calibrationId"]
    corpus["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"] = binding[
        "maxAbsoluteOnsetErrorSeconds"
    ]
    corpus["referenceCalibrationPackage"] = {
        "contract": module.PACKAGE_CONTRACT,
        "validationResultPath": VALIDATION_PATH,
        "validationResultSha256": VALIDATION_SHA,
        "packageBindingSha256": binding_sha,
        "packageBinding": binding,
    }

    decoder_configuration_sha = binding["decoder"]["configuration"]["sha256"]
    for attempt in manifest["attempts"]:
        if attempt.get("admitted") is True:
            reference = attempt["reference"]
            reference["configurationSha256"] = binding["hardwareConfiguration"][
                "sha256"
            ]
            reference["calibrationId"] = binding["calibrationId"]
            reference["calibrationPackageBindingSha256"] = binding_sha
            reference["derivationConfigurationSha256"] = decoder_configuration_sha
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
    def test_01_complete_v22_manifest_passes(self):
        result = module.validate_manifest(valid_manifest())
        self.assertTrue(result["contractValid"], result)
        self.assertTrue(result["packageBridgeValid"], result)
        self.assertTrue(result["mayAdvanceToReferenceBlindStructuralAudit"])
        self.assertEqual(
            result["populationIdentityVersion"],
            module.POPULATION_IDENTITY_VERSION,
        )
        self.assertEqual(len(result["calibrationPackageBindingSha256"]), 64)
        self.assertEqual(result["calibrationPackageValidationResultSha256"], VALIDATION_SHA)
        self.assertEqual(result["calibrationPackageValidationResultPath"], VALIDATION_PATH)
        self.assertTrue(result["calibrationPackageDecoderId"])
        self.assertTrue(result["calibrationPackageDecoderSoftwareVersion"])
        self.assertEqual(len(result["calibrationPackageDecoderCodeSha256"]), 64)
        self.assertEqual(len(result["calibrationPackageDecoderConfigurationSha256"]), 64)

    def test_02_v21_projection_fails_until_bridge_fields_are_added(self):
        manifest = v21_fixture.valid_manifest()
        manifest["contract"] = module.CONTRACT
        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_OBJECT_REQUIRED", result["errors"])

    def test_03_canonical_package_binding_hash_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"][
            "softwareVersion"
        ] = "changed-without-rebinding"
        result = module.validate_manifest(manifest)
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH", result["errors"])

    def test_04_malformed_package_binding_sha_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBindingSha256"] = "bad"
        result = module.validate_manifest(manifest)
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID", result["errors"])

    def test_05_malformed_validation_result_sha_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["validationResultSha256"] = "bad"
        result = module.validate_manifest(manifest)
        self.assertIn(
            "REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_SHA256_INVALID",
            result["errors"],
        )

    def test_06_unsafe_validation_result_path_fails(self):
        for unsafe in (
            "/absolute/result.json",
            "../result.json",
            "calibration/../result.json",
            "./result.json",
            "calibration\\result.json",
            "calibration//result.json",
            "calibration/",
        ):
            with self.subTest(path=unsafe):
                manifest = valid_manifest()
                manifest["corpus"]["referenceCalibrationPackage"]["validationResultPath"] = unsafe
                result = module.validate_manifest(manifest)
                self.assertIn(
                    "REFERENCE_CALIBRATION_PACKAGE_VALIDATION_RESULT_PATH_INVALID",
                    result["errors"],
                )

    def test_07_package_contract_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["contract"] = "wrong"
        result = module.validate_manifest(manifest)
        self.assertTrue(
            any(
                e.startswith("REFERENCE_CALIBRATION_PACKAGE_CONTRACT_MISMATCH")
                for e in result["errors"]
            )
        )

    def test_08_package_firewall_violation_fails(self):
        for field in ("usedHoldoutData", "usedModelOutputs", "derivedFromEvaluatedAudio"):
            with self.subTest(field=field):
                manifest = valid_manifest()
                manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][field] = True
                rebind(manifest)
                result = module.validate_manifest(manifest)
                self.assertFalse(result["contractValid"])
                self.assertTrue(any(field.upper() in e for e in result["errors"]))

    def test_09_package_calibration_id_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "calibrationId"
        ] = "other-calibration"
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_LEGACY_CALIBRATION_ID_MISMATCH", result["errors"])

    def test_10_hardware_configuration_id_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "hardwareConfiguration"
        ]["configurationId"] = "other-hardware-config"
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_ID_MISMATCH", result["errors"])

    def test_11_hardware_configuration_sha_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "hardwareConfiguration"
        ]["sha256"] = "1" * 64
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_HARDWARE_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_12_instrument_setup_sha_mismatch_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "instrumentSetupSha256"
        ] = "2" * 64
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_INSTRUMENT_SETUP_SHA256_MISMATCH", result["errors"])

    def test_13_package_timing_declaration_mismatch_fails(self):
        manifest = valid_manifest()
        legacy = float(
            manifest["corpus"]["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"]
        )
        replacement = 0.024 if legacy != 0.024 else 0.023
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "maxAbsoluteOnsetErrorSeconds"
        ] = replacement
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_LEGACY_TIMING_ERROR_MISMATCH", result["errors"])

    def test_14_package_timing_above_25_ms_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
            "maxAbsoluteOnsetErrorSeconds"
        ] = 0.026
        manifest["corpus"]["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"] = 0.026
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_BINDING_TIMING_ERROR_EXCEEDS_BOUND", result["errors"])

    def test_15_decoder_identity_and_version_are_required(self):
        for field, expected in (
            ("decoderId", "CALIBRATION_PACKAGE_DECODER_ID_REQUIRED"),
            ("softwareVersion", "CALIBRATION_PACKAGE_DECODER_SOFTWARE_VERSION_REQUIRED"),
        ):
            with self.subTest(field=field):
                manifest = valid_manifest()
                manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"][
                    "decoder"
                ][field] = ""
                rebind(manifest)
                result = module.validate_manifest(manifest)
                self.assertIn(expected, result["errors"])

    def test_16_malformed_decoder_code_sha_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"][
            "code"
        ]["sha256"] = "bad"
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn("CALIBRATION_PACKAGE_DECODER_CODE_SHA256_INVALID", result["errors"])

    def test_17_malformed_decoder_configuration_sha_fails(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"][
            "configuration"
        ]["sha256"] = "bad"
        rebind(manifest)
        result = module.validate_manifest(manifest)
        self.assertIn(
            "CALIBRATION_PACKAGE_DECODER_CONFIGURATION_SHA256_INVALID",
            result["errors"],
        )

    def test_18_admitted_reference_package_binding_is_required_and_must_match(self):
        manifest = valid_manifest()
        del manifest["attempts"][1]["reference"]["calibrationPackageBindingSha256"]
        result = module.validate_manifest(manifest)
        self.assertIn(
            "ATTEMPT[1]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID",
            result["errors"],
        )

        manifest = valid_manifest()
        manifest["attempts"][1]["reference"]["calibrationPackageBindingSha256"] = "0" * 64
        result = module.validate_manifest(manifest)
        self.assertIn(
            "ATTEMPT[1]_REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_MISMATCH",
            result["errors"],
        )

    def test_19_admitted_reference_derivation_config_must_match_package_decoder_config(self):
        manifest = valid_manifest()
        manifest["attempts"][1]["reference"]["derivationConfigurationSha256"] = "1" * 64
        result = module.validate_manifest(manifest)
        self.assertIn(
            "ATTEMPT[1]_REFERENCE_DERIVATION_CONFIGURATION_SHA256_MISMATCH",
            result["errors"],
        )

    def test_20_nonadmitted_attempt_does_not_require_bridge_fields(self):
        manifest = valid_manifest()
        self.assertFalse(manifest["attempts"][0]["admitted"])
        self.assertNotIn("reference", manifest["attempts"][0])
        result = module.validate_manifest(manifest)
        self.assertTrue(result["contractValid"], result)

    def test_21_inherited_retry_continuity_and_cross_slot_uniqueness_remain_enforced(self):
        manifest = valid_manifest()
        self.assertEqual(
            manifest["attempts"][0]["underlyingPerformanceId"],
            manifest["attempts"][1]["underlyingPerformanceId"],
        )
        self.assertTrue(module.validate_manifest(copy.deepcopy(manifest))["contractValid"])

        second = copy.deepcopy(manifest["attempts"][1])
        second["attemptId"] = "slot-2-attempt-1"
        second["slotId"] = "slot-2"
        second["playerId"] = "P02"
        second["exerciseId"] = "EX02"
        second["attemptNumber"] = 1
        second["capturedAtUtc"] = "2026-09-14T20:03:00Z"
        second["evaluatedAudio"] = {"path": "audio/slot-2.wav", "sha256": "6" * 64}
        second["pitchEvidence"] = {
            "path": "pitch/slot-2.bin",
            "sha256": "7" * 64,
            "derivedFromEvaluatedAudio": False,
        }
        second["birthEvidence"] = {
            "path": "birth/slot-2.bin",
            "sha256": "8" * 64,
            "derivedFromEvaluatedAudio": False,
        }
        second["reference"]["path"] = "reference/slot-2.json"
        second["reference"]["sha256"] = "9" * 64
        second["reference"]["pitchEvidenceSha256"] = "7" * 64
        second["reference"]["birthEvidenceSha256"] = "8" * 64
        manifest["attempts"].append(second)

        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertTrue(
            any(
                error.startswith(
                    "DUPLICATE_UNDERLYING_PERFORMANCE_ID_ACROSS_SLOTS:performance-1:"
                )
                for error in result["errors"]
            )
        )

    def test_22_augmented_population_sha_binds_package_and_validation_result_identities(self):
        manifest_a = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest_a))
        self.assertTrue(result_a["contractValid"], result_a)

        manifest_b = copy.deepcopy(manifest_a)
        manifest_b["corpus"]["referenceCalibrationPackage"]["validationResultSha256"] = "e" * 64
        result_b = module.validate_manifest(manifest_b)
        self.assertTrue(result_b["contractValid"], result_b)
        self.assertNotEqual(
            result_a["admittedPopulationManifestSha256"],
            result_b["admittedPopulationManifestSha256"],
        )

        manifest_c = copy.deepcopy(manifest_a)
        manifest_c["corpus"]["referenceCalibrationPackage"]["packageBinding"]["decoder"][
            "softwareVersion"
        ] = "2.0-synthetic"
        rebind(manifest_c)
        result_c = module.validate_manifest(manifest_c)
        self.assertTrue(result_c["contractValid"], result_c)
        self.assertNotEqual(
            result_a["admittedPopulationManifestSha256"],
            result_c["admittedPopulationManifestSha256"],
        )

    def test_23_canonical_validation_output_is_byte_deterministic(self):
        manifest = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest))
        result_b = module.validate_manifest(copy.deepcopy(manifest))
        self.assertEqual(module.canonical_json_bytes(result_a), module.canonical_json_bytes(result_b))
        self.assertEqual(
            result_a["admittedPopulationManifestSha256"],
            result_b["admittedPopulationManifestSha256"],
        )

    def test_24_authorization_boundary_remains_closed(self):
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
