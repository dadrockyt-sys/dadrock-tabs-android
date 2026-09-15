#!/usr/bin/env python3
from __future__ import annotations

import copy
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
TARGET = HERE / "reference_calibration_package_provenance_v1.py"
spec = importlib.util.spec_from_file_location("calibration_package_v1", TARGET)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CalibrationPackageProvenanceV1Tests(unittest.TestCase):
    def fixture(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name) / "pkg"
        manifest = m.build_synthetic_fixture(root)
        return td, root, manifest

    def validate(self, root, manifest):
        return m.validate_package(manifest, root)

    def test_01_valid_fixture_passes(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        result = self.validate(root, manifest)
        self.assertTrue(result["contractValid"], result["errors"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["verifiedFileCount"], 14)
        self.assertEqual(len(result["packageBindingSha256"]), 64)

    def test_02_repeated_validation_is_byte_deterministic(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        a = self.validate(root, manifest)
        b = self.validate(root, manifest)
        self.assertEqual(m.canonical_json_bytes(a), m.canonical_json_bytes(b))

    def test_03_binding_independent_of_absolute_root(self):
        a_td, a_root, a_manifest = self.fixture()
        b_td, b_root, b_manifest = self.fixture()
        self.addCleanup(a_td.cleanup)
        self.addCleanup(b_td.cleanup)
        a = self.validate(a_root, a_manifest)
        b = self.validate(b_root, b_manifest)
        self.assertEqual(a["packageBindingSha256"], b["packageBindingSha256"])
        self.assertEqual(a["packageBinding"], b["packageBinding"])

    def test_04_firewall_fields_fail_closed(self):
        for field, bad in (
            ("usedHoldoutData", True),
            ("usedModelOutputs", True),
            ("derivedFromEvaluatedAudio", True),
        ):
            with self.subTest(field=field):
                td, root, manifest = self.fixture()
                try:
                    manifest[field] = bad
                    self.assertFalse(self.validate(root, manifest)["contractValid"])
                finally:
                    td.cleanup()

    def test_05_timing_bound_equality_allowed_above_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["maxAbsoluteOnsetErrorSeconds"] = 0.025
        self.assertTrue(self.validate(root, manifest)["contractValid"])
        manifest["maxAbsoluteOnsetErrorSeconds"] = 0.025000001
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("MAX_ABSOLUTE_ONSET_ERROR_EXCEEDS_0_025", result["errors"])

    def test_06_malformed_hash_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["wiringTopology"]["sha256"] = "ABC"
        self.assertFalse(self.validate(root, manifest)["contractValid"])

    def test_07_hash_mismatch_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        path = root / manifest["calibrationFixture"]["path"]
        path.write_bytes(b"changed")
        result = self.validate(root, manifest)
        self.assertIn("CALIBRATION_FIXTURE_SHA256_MISMATCH", result["errors"])

    def test_08_missing_file_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        (root / manifest["decoder"]["code"]["path"]).unlink()
        result = self.validate(root, manifest)
        self.assertIn("DECODER_CODE_FILE_MISSING", result["errors"])

    def test_09_absolute_path_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["decoder"]["configuration"]["path"] = "/tmp/config.json"
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("DECODER_CONFIGURATION_PATH_UNSAFE", result["errors"])

    def test_10_traversal_path_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["wiringTopology"]["path"] = "../outside.txt"
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("WIRING_TOPOLOGY_PATH_UNSAFE", result["errors"])

    def test_11_duplicate_package_path_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["calibrationFixture"]["path"] = manifest["wiringTopology"]["path"]
        manifest["calibrationFixture"]["sha256"] = manifest["wiringTopology"]["sha256"]
        result = self.validate(root, manifest)
        self.assertTrue(any(e.startswith("DUPLICATE_PACKAGE_PATH:") for e in result["errors"]))

    def test_12_duplicate_hardware_identity_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["hardwareIdentities"][1]["immutableIdentity"] = manifest["hardwareIdentities"][0]["immutableIdentity"]
        result = self.validate(root, manifest)
        self.assertTrue(any(e.startswith("DUPLICATE_HARDWARE_IMMUTABLE_IDENTITY:") for e in result["errors"]))

    def test_13_duplicate_raw_source_id_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["rawSources"][1]["sourceId"] = manifest["rawSources"][0]["sourceId"]
        result = self.validate(root, manifest)
        self.assertTrue(any(e.startswith("DUPLICATE_RAW_SOURCE_ID:") for e in result["errors"]))

    def test_14_missing_required_raw_role_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["rawSources"] = [s for s in manifest["rawSources"] if "clock_sync" not in s["roles"]]
        result = self.validate(root, manifest)
        self.assertIn("MISSING_REQUIRED_RAW_ROLE:clock_sync", result["errors"])

    def test_15_unknown_raw_role_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["rawSources"][0]["roles"].append("evaluated_audio_guess")
        result = self.validate(root, manifest)
        self.assertTrue(any("UNKNOWN_ROLE:evaluated_audio_guess" in e for e in result["errors"]))

    def test_16_missing_and_duplicate_derived_role_rejected(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        first_role = manifest["derivedOutputs"][0]["role"]
        second_role = manifest["derivedOutputs"][1]["role"]
        manifest["derivedOutputs"][0]["role"] = second_role
        result = self.validate(root, manifest)
        self.assertIn(f"MISSING_DERIVED_OUTPUT_ROLE:{first_role}", result["errors"])
        self.assertIn(f"DUPLICATE_DERIVED_OUTPUT_ROLE:{second_role}", result["errors"])

    def test_17_decoder_identity_mandatory(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["decoder"]["decoderId"] = ""
        manifest["decoder"]["configuration"]["sha256"] = "0" * 64
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("DECODER_DECODERID_REQUIRED", result["errors"])
        self.assertIn("DECODER_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_18_hardware_fixture_topology_and_setup_identity_mandatory(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["hardwareConfiguration"]["configurationId"] = ""
        manifest["wiringTopology"]["topologyId"] = ""
        manifest["calibrationFixture"]["fixtureId"] = ""
        manifest["instrumentSetupSha256"] = "bad"
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertIn("HARDWARE_CONFIGURATION_ID_REQUIRED", result["errors"])
        self.assertIn("WIRING_TOPOLOGY_ID_REQUIRED", result["errors"])
        self.assertIn("CALIBRATION_FIXTURE_ID_REQUIRED", result["errors"])
        self.assertIn("INSTRUMENT_SETUP_SHA256_INVALID", result["errors"])

    def test_19_raw_source_firewall_mandatory(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        manifest["rawSources"][0]["nonHoldout"] = False
        manifest["rawSources"][1]["usedModelOutputs"] = True
        manifest["rawSources"][2]["derivedFromEvaluatedAudio"] = True
        result = self.validate(root, manifest)
        self.assertFalse(result["contractValid"])
        self.assertTrue(any("NON_HOLDOUT_MUST_BE_TRUE" in e for e in result["errors"]))
        self.assertTrue(any("USED_MODEL_OUTPUTS_MUST_BE_FALSE" in e for e in result["errors"]))
        self.assertTrue(any("DERIVED_FROM_EVALUATED_AUDIO_MUST_BE_FALSE" in e for e in result["errors"]))

    def test_20_authorization_boundary_closed(self):
        td, root, manifest = self.fixture()
        self.addCleanup(td.cleanup)
        result = self.validate(root, manifest)
        self.assertFalse(result["realCalibrationAuthorized"])
        self.assertFalse(result["realHoldoutCaptureAuthorized"])
        for key in ("basicPitchAuthorized", "v6Authorized", "correctnessAuthorized", "modelValidationComplete", "mayAdvanceDelivery"):
            self.assertFalse(result[key])
        self.assertEqual(result["customerEligibleEvents"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
