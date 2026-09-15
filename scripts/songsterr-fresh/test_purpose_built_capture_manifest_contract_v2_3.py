#!/usr/bin/env python3
"""Synthetic-only tests for purpose-built capture-manifest V2.3."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


module = _load("capture_v23", "purpose_built_capture_manifest_contract_v2_3.py")
v22_fixture = _load(
    "capture_v22_fixture", "test_purpose_built_capture_manifest_contract_v2_2.py"
)

HARDWARE_SOURCE_SHA = "a" * 64
BIRTH_STREAM_SHA = "b" * 64
PITCH_LATCH_STREAM_SHA = "c" * 64
CLOCK_SYNC_SOURCE_SHA = "d" * 64


def admitted_attempt(manifest: dict) -> dict:
    return next(attempt for attempt in manifest["attempts"] if attempt.get("admitted") is True)


def structural_binding(manifest: dict, attempt: dict) -> dict:
    corpus = manifest["corpus"]
    hardware = corpus["hardware"]
    reference = attempt["reference"]
    return {
        "contract": module.STRUCTURAL_INPUT_BINDING_CONTRACT,
        "attemptId": attempt["attemptId"],
        "slotId": attempt["slotId"],
        "underlyingPerformanceId": attempt["underlyingPerformanceId"],
        "playerId": attempt["playerId"],
        "exerciseId": attempt["exerciseId"],
        "category": attempt["category"],
        "hardwareSourceSha256": HARDWARE_SOURCE_SHA,
        "birthStreamSha256": BIRTH_STREAM_SHA,
        "pitchLatchStreamSha256": PITCH_LATCH_STREAM_SHA,
        "clockSyncSourceSha256": CLOCK_SYNC_SOURCE_SHA,
        "configurationId": hardware["configuration"]["configurationId"],
        "configurationSha256": hardware["configuration"]["sha256"],
        "instrumentSetupSha256": hardware["instrumentSetup"]["setupSha256"],
        "openStringMidi": copy.deepcopy(hardware["instrumentSetup"]["openStringMidi"]),
        "calibrationId": corpus["referenceCalibration"]["calibrationId"],
        "clockSyncId": corpus["clockSync"]["syncId"],
        "eventSemanticsVersion": module.EVENT_SEMANTICS_VERSION,
        "pitchEvidenceSha256": reference["pitchEvidenceSha256"],
        "birthEvidenceSha256": reference["birthEvidenceSha256"],
        "referenceArtifactSha256": reference["sha256"],
        "calibrationPackageBindingSha256": reference[
            "calibrationPackageBindingSha256"
        ],
        "derivationConfigurationSha256": reference[
            "derivationConfigurationSha256"
        ],
    }


def rehash_binding(attempt: dict) -> str:
    sha = module._canonical_sha256(attempt["reference"]["structuralAuditInputs"])
    attempt["reference"]["structuralAuditInputsSha256"] = sha
    return sha


def valid_manifest() -> dict:
    manifest = v22_fixture.valid_manifest()
    manifest["contract"] = module.CONTRACT
    for attempt in manifest["attempts"]:
        if attempt.get("admitted") is True:
            binding = structural_binding(manifest, attempt)
            attempt["reference"]["structuralAuditInputs"] = binding
            attempt["reference"]["structuralAuditInputsSha256"] = module._canonical_sha256(
                binding
            )
    return manifest


class CaptureManifestV23Tests(unittest.TestCase):
    def test_01_complete_v23_synthetic_manifest_passes(self):
        result = module.validate_manifest(valid_manifest())
        self.assertTrue(result["contractValid"], result)
        self.assertTrue(result["v23SemanticGuardPassed"])
        self.assertEqual(result["structuralAuditInputBindingCount"], 1)
        self.assertEqual(
            result["structuralAuditInputBindingContract"],
            module.STRUCTURAL_INPUT_BINDING_CONTRACT,
        )
        self.assertEqual(result["populationIdentityVersion"], module.POPULATION_IDENTITY_VERSION)
        self.assertTrue(result["inheritedV22AdmittedPopulationManifestSha256"])
        self.assertTrue(result["admittedPopulationManifestSha256"])
        self.assertTrue(result["mayAdvanceToReferenceBlindStructuralAudit"])

    def test_02_valid_v22_projection_fails_until_structural_binding_is_added(self):
        manifest = v22_fixture.valid_manifest()
        manifest["contract"] = module.CONTRACT
        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertTrue(
            any("STRUCTURAL_AUDIT_INPUTS_OBJECT_REQUIRED" in e for e in result["errors"])
        )

    def test_03_structural_binding_contract_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["contract"] = "wrong"
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_CONTRACT_MISMATCH", result["errors"])

    def test_04_missing_or_malformed_structural_binding_sha_fails(self):
        for value in (None, "bad"):
            with self.subTest(value=value):
                manifest = valid_manifest()
                attempt = admitted_attempt(manifest)
                if value is None:
                    del attempt["reference"]["structuralAuditInputsSha256"]
                else:
                    attempt["reference"]["structuralAuditInputsSha256"] = value
                result = module.validate_manifest(manifest)
                self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_SHA256_INVALID", result["errors"])

    def test_05_canonical_structural_binding_hash_mismatch_fails(self):
        manifest = valid_manifest()
        admitted_attempt(manifest)["reference"]["structuralAuditInputs"][
            "hardwareSourceSha256"
        ] = "e" * 64
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_SHA256_MISMATCH", result["errors"])

    def test_06_all_four_structural_source_sha_fields_must_be_valid(self):
        for field in module.STRUCTURAL_SOURCE_SHA_FIELDS:
            with self.subTest(field=field):
                manifest = valid_manifest()
                attempt = admitted_attempt(manifest)
                attempt["reference"]["structuralAuditInputs"][field] = "bad"
                rehash_binding(attempt)
                result = module.validate_manifest(manifest)
                self.assertTrue(any(field.upper() in e and e.endswith("_INVALID") for e in result["errors"]))

    def test_07_attempt_slot_and_underlying_identity_mismatch_fail(self):
        for field in ("attemptId", "slotId", "underlyingPerformanceId"):
            with self.subTest(field=field):
                manifest = valid_manifest()
                attempt = admitted_attempt(manifest)
                attempt["reference"]["structuralAuditInputs"][field] = "wrong"
                rehash_binding(attempt)
                result = module.validate_manifest(manifest)
                self.assertTrue(any(field.upper() in e and e.endswith("_MISMATCH") for e in result["errors"]))

    def test_08_player_exercise_and_category_identity_mismatch_fail(self):
        for field in ("playerId", "exerciseId", "category"):
            with self.subTest(field=field):
                manifest = valid_manifest()
                attempt = admitted_attempt(manifest)
                attempt["reference"]["structuralAuditInputs"][field] = "wrong"
                rehash_binding(attempt)
                result = module.validate_manifest(manifest)
                self.assertTrue(any(field.upper() in e and e.endswith("_MISMATCH") for e in result["errors"]))

    def test_09_hardware_configuration_id_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["configurationId"] = "wrong"
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_CONFIGURATION_ID_MISMATCH", result["errors"])

    def test_10_hardware_configuration_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["configurationSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_11_instrument_setup_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["instrumentSetupSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_INSTRUMENT_SETUP_SHA256_MISMATCH", result["errors"])

    def test_12_open_string_midi_mismatch_or_invalid_shape_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["openStringMidi"] = [41, 45, 50, 55, 59, 64]
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_OPEN_STRING_MIDI_MISMATCH", result["errors"])

        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["openStringMidi"] = [40, 45]
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_OPEN_STRING_MIDI_INVALID", result["errors"])

    def test_13_calibration_id_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["calibrationId"] = "wrong"
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_CALIBRATION_ID_MISMATCH", result["errors"])

    def test_14_clock_sync_id_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["clockSyncId"] = "wrong"
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_CLOCK_SYNC_ID_MISMATCH", result["errors"])

    def test_15_event_semantics_must_be_exact_and_match_reference(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["eventSemanticsVersion"] = "wrong"
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_EVENT_SEMANTICS_VERSION_INVALID", result["errors"])
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_EVENT_SEMANTICS_VERSION_MISMATCH", result["errors"])

    def test_16_pitch_evidence_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["pitchEvidenceSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_PITCH_EVIDENCE_SHA256_MISMATCH", result["errors"])

    def test_17_birth_evidence_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["birthEvidenceSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_BIRTH_EVIDENCE_SHA256_MISMATCH", result["errors"])

    def test_18_reference_artifact_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["referenceArtifactSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[1]_STRUCTURAL_AUDIT_INPUTS_REFERENCE_ARTIFACT_SHA256_MISMATCH", result["errors"])

    def test_19_calibration_package_binding_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["calibrationPackageBindingSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertTrue(any("CALIBRATION_PACKAGE_BINDING_SHA256" in e and "MISMATCH" in e for e in result["errors"]))

    def test_20_derivation_configuration_sha_mismatch_fails(self):
        manifest = valid_manifest()
        attempt = admitted_attempt(manifest)
        attempt["reference"]["structuralAuditInputs"]["derivationConfigurationSha256"] = "e" * 64
        rehash_binding(attempt)
        result = module.validate_manifest(manifest)
        self.assertTrue(any("DERIVATION_CONFIGURATION_SHA256" in e and "MISMATCH" in e for e in result["errors"]))

    def test_21_nonadmitted_attempt_must_not_carry_structural_binding(self):
        manifest = valid_manifest()
        failed = next(attempt for attempt in manifest["attempts"] if attempt.get("admitted") is not True)
        failed["reference"] = {
            "structuralAuditInputs": {"contract": module.STRUCTURAL_INPUT_BINDING_CONTRACT},
            "structuralAuditInputsSha256": "f" * 64,
        }
        result = module.validate_manifest(manifest)
        self.assertIn("ATTEMPT[0]_NONADMITTED_STRUCTURAL_AUDIT_INPUTS_FORBIDDEN", result["errors"])

    def test_22_inherited_v22_rules_remain_enforced(self):
        manifest = valid_manifest()
        manifest["corpus"]["referenceCalibrationPackage"]["packageBindingSha256"] = "bad"
        result = module.validate_manifest(manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("REFERENCE_CALIBRATION_PACKAGE_BINDING_SHA256_INVALID", result["errors"])

    def test_23_population_sha_changes_when_structural_source_sha_changes(self):
        manifest_a = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest_a))
        self.assertTrue(result_a["contractValid"], result_a)

        manifest_b = copy.deepcopy(manifest_a)
        attempt_b = admitted_attempt(manifest_b)
        attempt_b["reference"]["structuralAuditInputs"]["hardwareSourceSha256"] = "e" * 64
        rehash_binding(attempt_b)
        result_b = module.validate_manifest(manifest_b)
        self.assertTrue(result_b["contractValid"], result_b)
        self.assertNotEqual(result_a["admittedPopulationManifestSha256"], result_b["admittedPopulationManifestSha256"])

    def test_24_population_sha_changes_when_admitted_binding_identity_changes(self):
        manifest_a = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest_a))
        manifest_b = copy.deepcopy(manifest_a)
        attempt_b = admitted_attempt(manifest_b)
        attempt_b["attemptId"] = "slot-1-attempt-2-renamed"
        attempt_b["reference"]["structuralAuditInputs"]["attemptId"] = attempt_b["attemptId"]
        rehash_binding(attempt_b)
        result_b = module.validate_manifest(manifest_b)
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"], (result_a, result_b))
        self.assertNotEqual(result_a["admittedPopulationManifestSha256"], result_b["admittedPopulationManifestSha256"])

    def test_25_inherited_v22_population_sha_unchanged_when_only_v23_output_hash_changes(self):
        manifest_a = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest_a))
        manifest_b = copy.deepcopy(manifest_a)
        attempt_b = admitted_attempt(manifest_b)
        attempt_b["reference"]["structuralAuditInputs"]["pitchLatchStreamSha256"] = "e" * 64
        rehash_binding(attempt_b)
        result_b = module.validate_manifest(manifest_b)
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"], (result_a, result_b))
        self.assertEqual(
            result_a["inheritedV22AdmittedPopulationManifestSha256"],
            result_b["inheritedV22AdmittedPopulationManifestSha256"],
        )
        self.assertNotEqual(result_a["admittedPopulationManifestSha256"], result_b["admittedPopulationManifestSha256"])

    def test_26_canonical_validation_output_is_byte_deterministic(self):
        manifest = valid_manifest()
        result_a = module.validate_manifest(copy.deepcopy(manifest))
        result_b = module.validate_manifest(copy.deepcopy(manifest))
        self.assertEqual(module.canonical_json_bytes(result_a), module.canonical_json_bytes(result_b))

    def test_27_authorization_boundary_remains_closed_on_pass(self):
        result = module.validate_manifest(valid_manifest())
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
