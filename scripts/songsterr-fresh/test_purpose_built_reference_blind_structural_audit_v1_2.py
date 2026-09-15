#!/usr/bin/env python3
"""Synthetic-only contract tests for reference-blind structural audit V1.2."""
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


module = _load(
    "structural_audit_v12",
    "purpose_built_reference_blind_structural_audit_v1_2.py",
)
v1_fixture = _load(
    "structural_audit_v1_fixture_for_v12",
    "test_purpose_built_reference_blind_structural_audit_v1.py",
)
v23 = _load("capture_v23_for_v12", "purpose_built_capture_manifest_contract_v2_3.py")
v23_fixture = _load(
    "capture_v23_fixture_for_v12",
    "test_purpose_built_capture_manifest_contract_v2_3.py",
)
provenance = _load(
    "reference_calibration_package_provenance_v1_for_v12",
    "reference_calibration_package_provenance_v1.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _render(value: Any) -> bytes:
    return module.canonical_json_bytes(value)


def _admitted(manifest: dict[str, Any]) -> dict[str, Any]:
    return next(a for a in manifest["attempts"] if a.get("admitted") is True)


def _refresh_v23(chain: dict[str, Any], *, rehash_binding: bool = True) -> None:
    attempt = _admitted(chain["manifest"])
    if rehash_binding:
        chain["binding_sha"] = v23_fixture.rehash_binding(attempt)
    else:
        chain["binding_sha"] = attempt["reference"]["structuralAuditInputsSha256"]
    chain["binding"] = copy.deepcopy(attempt["reference"]["structuralAuditInputs"])
    result = v23.validate_manifest(chain["manifest"])
    assert result["contractValid"] is True, result
    chain["v23_result"] = result
    chain["v23_bytes"] = _render(result)
    chain["v23_sha"] = _sha(chain["v23_bytes"])
    chain["v23_population_sha"] = result["admittedPopulationManifestSha256"]


def _sync_source_hash_into_binding(chain: dict[str, Any], source_name: str) -> None:
    field = {
        "hardware": "hardwareSourceSha256",
        "birth": "birthStreamSha256",
        "pitchLatch": "pitchLatchStreamSha256",
        "clockSync": "clockSyncSourceSha256",
    }[source_name]
    chain["expected"][source_name] = _sha(chain["raw_sources"][source_name])
    attempt = _admitted(chain["manifest"])
    attempt["reference"]["structuralAuditInputs"][field] = chain["expected"][source_name]
    _refresh_v23(chain)


def build_valid_chain() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "package"
        package_manifest = provenance.build_synthetic_fixture(root)
        provenance_result = provenance.validate_package(package_manifest, root)
    assert provenance_result["contractValid"] is True, provenance_result
    provenance_bytes = _render(provenance_result)
    provenance_sha = _sha(provenance_bytes)

    manifest = v23_fixture.valid_manifest()
    manifest["corpus"]["referenceCalibrationPackage"]["validationResultSha256"] = provenance_sha

    hardware, births, latches, clock = v1_fixture.base_documents()
    corpus = manifest["corpus"]
    hardware["configurationId"] = corpus["hardware"]["configuration"]["configurationId"]
    hardware["calibrationId"] = corpus["referenceCalibration"]["calibrationId"]
    hardware["openStringMidi"] = copy.deepcopy(
        corpus["hardware"]["instrumentSetup"]["openStringMidi"]
    )
    clock["syncId"] = corpus["clockSync"]["syncId"]

    raw_sources = {
        "hardware": v1_fixture.render(hardware),
        "birth": v1_fixture.render(births),
        "pitchLatch": v1_fixture.render(latches),
        "clockSync": v1_fixture.render(clock),
    }
    expected = {name: _sha(data) for name, data in raw_sources.items()}

    attempt = _admitted(manifest)
    binding = attempt["reference"]["structuralAuditInputs"]
    binding["hardwareSourceSha256"] = expected["hardware"]
    binding["birthStreamSha256"] = expected["birth"]
    binding["pitchLatchStreamSha256"] = expected["pitchLatch"]
    binding["clockSyncSourceSha256"] = expected["clockSync"]
    binding_sha = v23_fixture.rehash_binding(attempt)

    v23_result = v23.validate_manifest(manifest)
    assert v23_result["contractValid"] is True, v23_result
    assert v23_result["calibrationPackageValidationResultSha256"] == provenance_sha
    v23_bytes = _render(v23_result)

    return {
        "raw_sources": raw_sources,
        "expected": expected,
        "provenance_result": provenance_result,
        "provenance_bytes": provenance_bytes,
        "provenance_sha": provenance_sha,
        "package_binding_sha": provenance_result["packageBindingSha256"],
        "manifest": manifest,
        "binding": copy.deepcopy(binding),
        "binding_sha": binding_sha,
        "v23_result": v23_result,
        "v23_bytes": v23_bytes,
        "v23_sha": _sha(v23_bytes),
        "v23_population_sha": v23_result["admittedPopulationManifestSha256"],
    }


def run_chain(chain: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    args = {
        "raw_sources": chain["raw_sources"],
        "expected_sha256": chain["expected"],
        "calibration_provenance_result": chain["provenance_bytes"],
        "expected_calibration_provenance_result_sha256": chain["provenance_sha"],
        "declared_provenance_result_sha256": chain["provenance_sha"],
        "declared_calibration_package_binding_sha256": chain["package_binding_sha"],
        "capture_manifest_v23_validation_result": chain["v23_bytes"],
        "expected_capture_manifest_v23_validation_result_sha256": chain["v23_sha"],
        "structural_audit_inputs": chain["binding"],
        "expected_structural_audit_inputs_sha256": chain["binding_sha"],
        "expected_capture_manifest_v23_admitted_population_sha256": chain[
            "v23_population_sha"
        ],
    }
    args.update(overrides)
    return module.audit_raw_sources_v1_2(**args)


def replace_v23_result(chain: dict[str, Any], result: dict[str, Any]) -> None:
    chain["v23_result"] = result
    chain["v23_bytes"] = _render(result)
    chain["v23_sha"] = _sha(chain["v23_bytes"])
    if isinstance(result.get("admittedPopulationManifestSha256"), str):
        chain["v23_population_sha"] = result["admittedPopulationManifestSha256"]


class StructuralAuditV12Tests(unittest.TestCase):
    def assert_fail(self, result: dict[str, Any]) -> None:
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

    def test_01_complete_v12_synthetic_chain_passes(self):
        chain = build_valid_chain()
        result = run_chain(chain)
        self.assertTrue(result["contractValid"], result)
        self.assertTrue(result["datasetStructurallySuitable"])
        self.assertEqual(result["capturePopulationBindingViolationCount"], 0)
        self.assertEqual(result["attemptId"], "slot-1-attempt-2")
        self.assertEqual(result["derivedNoteEventCount"], 2)
        self.assertTrue(result["inheritedV11DerivedPopulationSha256"])
        self.assertTrue(result["derivedPopulationSha256"])

    def test_02_v11_nominal_source_and_provenance_semantics_unchanged(self):
        chain = build_valid_chain()
        inherited = module.v11.audit_raw_sources_v1_1(
            raw_sources=chain["raw_sources"],
            expected_sha256=chain["expected"],
            calibration_provenance_result=chain["provenance_bytes"],
            expected_calibration_provenance_result_sha256=chain["provenance_sha"],
            declared_provenance_result_sha256=chain["provenance_sha"],
            declared_calibration_package_binding_sha256=chain["package_binding_sha"],
        )
        result = run_chain(chain)
        self.assertTrue(inherited["contractValid"] and result["contractValid"])
        self.assertEqual(result["sourceSha256"], inherited["sourceSha256"])
        self.assertEqual(result["derivedNoteEventCount"], inherited["derivedNoteEventCount"])
        self.assertEqual(
            result["inheritedV11DerivedPopulationSha256"],
            inherited["derivedPopulationSha256"],
        )

    def test_03_v23_result_raw_value_not_bytes_fails(self):
        chain = build_valid_chain()
        result = run_chain(chain, capture_manifest_v23_validation_result="not-bytes")
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_RESULT_NOT_BYTES", result["errors"])

    def test_04_malformed_v23_expected_result_sha_fails(self):
        chain = build_valid_chain()
        result = run_chain(chain, expected_capture_manifest_v23_validation_result_sha256="bad")
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_EXPECTED_SHA256_INVALID", result["errors"])

    def test_05_v23_result_hash_mismatch_short_circuits_before_parse(self):
        chain = build_valid_chain()
        raw = b"not json"
        result = run_chain(
            chain,
            capture_manifest_v23_validation_result=raw,
            expected_capture_manifest_v23_validation_result_sha256="0" * 64,
        )
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_RESULT_SHA256_MISMATCH", result["errors"])
        self.assertFalse(any("INVALID_JSON" in e for e in result["errors"]))

    def test_06_invalid_v23_utf8_or_json_fails_after_hash(self):
        for raw in (b"{not-json", b"\xff\xfe"):
            with self.subTest(raw=raw):
                chain = build_valid_chain()
                sha = _sha(raw)
                result = run_chain(
                    chain,
                    capture_manifest_v23_validation_result=raw,
                    expected_capture_manifest_v23_validation_result_sha256=sha,
                )
                self.assert_fail(result)
                self.assertTrue(any("CAPTURE_MANIFEST_V23_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_07_v23_result_contract_mismatch_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["contract"] = "wrong"
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_RESULT_CONTRACT_MISMATCH", result["errors"])

    def test_08_v23_contract_valid_false_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["contractValid"] = False
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_RESULT_CONTRACT_NOT_VALID", result["errors"])

    def test_09_nonempty_v23_errors_fail(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["errors"] = ["synthetic"]
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_RESULT_ERRORS_NOT_EMPTY", result["errors"])

    def test_10_v23_semantic_guard_false_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["v23SemanticGuardPassed"] = False
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_SEMANTIC_GUARD_NOT_PASSED", result["errors"])

    def test_11_v23_may_advance_false_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["mayAdvanceToReferenceBlindStructuralAudit"] = False
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_MAY_ADVANCE_NOT_TRUE", result["errors"])

    def test_12_v23_population_identity_version_mismatch_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["populationIdentityVersion"] = "wrong"
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_POPULATION_IDENTITY_VERSION_MISMATCH", result["errors"])

    def test_13_malformed_or_mismatched_v23_population_sha_fails(self):
        chain = build_valid_chain()
        result = run_chain(chain, expected_capture_manifest_v23_admitted_population_sha256="bad")
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_EXPECTED_POPULATION_SHA256_INVALID", result["errors"])

        chain = build_valid_chain()
        result = run_chain(chain, expected_capture_manifest_v23_admitted_population_sha256="0" * 64)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_POPULATION_SHA256_MISMATCH", result["errors"])

    def test_14_v23_structural_binding_contract_mismatch_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindingContract"] = "wrong"
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_BINDING_CONTRACT_MISMATCH", result["errors"])

    def test_15_malformed_binding_or_sha_or_canonical_hash_mismatch_fails(self):
        chain = build_valid_chain()
        result = run_chain(chain, structural_audit_inputs="bad")
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_AUDIT_INPUTS_OBJECT_REQUIRED", result["errors"])

        chain = build_valid_chain()
        result = run_chain(chain, expected_structural_audit_inputs_sha256="bad")
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_AUDIT_INPUTS_EXPECTED_SHA256_INVALID", result["errors"])

        chain = build_valid_chain()
        binding = copy.deepcopy(chain["binding"])
        binding["hardwareSourceSha256"] = "e" * 64
        result = run_chain(chain, structural_audit_inputs=binding)
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_AUDIT_INPUTS_SHA256_MISMATCH", result["errors"])

    def test_16_missing_or_duplicate_matching_v23_binding_entry_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindings"] = []
        obj["structuralAuditInputBindingCount"] = 0
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_AUDITED_ATTEMPT_BINDING_ENTRY_COUNT_INVALID", result["errors"])

        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindings"].append(copy.deepcopy(obj["structuralAuditInputBindings"][0]))
        obj["structuralAuditInputBindingCount"] = len(obj["structuralAuditInputBindings"])
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_AUDITED_ATTEMPT_BINDING_ENTRY_COUNT_INVALID", result["errors"])

    def test_17_v23_binding_count_mismatch_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindingCount"] += 1
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_BINDING_COUNT_MISMATCH", result["errors"])

    def test_18_v23_provenance_result_sha_mismatch_to_v11_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageValidationResultSha256"] = "e" * 64
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_PROVENANCE_RESULT_SHA256_MISMATCH", result["errors"])

    def test_19_v23_package_binding_sha_mismatch_to_v11_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageBindingSha256"] = "e" * 64
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_PACKAGE_BINDING_SHA256_MISMATCH", result["errors"])

    def test_20_v23_decoder_configuration_sha_mismatch_to_v11_fails(self):
        chain = build_valid_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageDecoderConfigurationSha256"] = "e" * 64
        replace_v23_result(chain, obj)
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("CAPTURE_MANIFEST_V23_DECODER_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_21_any_v23_downstream_authorization_true_or_nonzero_fails(self):
        for key, bad_value in (
            ("realCalibrationAuthorized", True),
            ("realHoldoutCaptureAuthorized", True),
            ("basicPitchAuthorized", True),
            ("v6Authorized", True),
            ("correctnessAuthorized", True),
            ("modelValidationComplete", True),
            ("mayAdvanceDelivery", True),
            ("customerEligibleEvents", 1),
        ):
            with self.subTest(key=key):
                chain = build_valid_chain()
                obj = copy.deepcopy(chain["v23_result"])
                obj[key] = bad_value
                replace_v23_result(chain, obj)
                result = run_chain(chain)
                self.assert_fail(result)

    def test_22_each_structural_source_sha_mismatch_fails(self):
        for field in (
            "hardwareSourceSha256",
            "birthStreamSha256",
            "pitchLatchStreamSha256",
            "clockSyncSourceSha256",
        ):
            with self.subTest(field=field):
                chain = build_valid_chain()
                attempt = _admitted(chain["manifest"])
                attempt["reference"]["structuralAuditInputs"][field] = "e" * 64
                _refresh_v23(chain)
                result = run_chain(chain)
                self.assert_fail(result)
                self.assertTrue(any(field.upper() in e and "ACTUAL_MISMATCH" in e for e in result["errors"]))

    def test_23_structural_hardware_configuration_id_mismatch_fails(self):
        chain = build_valid_chain()
        hardware = json.loads(chain["raw_sources"]["hardware"].decode("utf-8"))
        hardware["configurationId"] = "other-config"
        chain["raw_sources"]["hardware"] = v1_fixture.render(hardware)
        _sync_source_hash_into_binding(chain, "hardware")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_DECLARATION_CONFIGURATION_ID_MISMATCH", result["errors"])

    def test_24_structural_hardware_calibration_id_mismatch_fails(self):
        chain = build_valid_chain()
        hardware = json.loads(chain["raw_sources"]["hardware"].decode("utf-8"))
        hardware["calibrationId"] = "other-calibration"
        chain["raw_sources"]["hardware"] = v1_fixture.render(hardware)
        _sync_source_hash_into_binding(chain, "hardware")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_DECLARATION_CALIBRATION_ID_MISMATCH", result["errors"])

    def test_25_structural_tuning_mismatch_fails(self):
        chain = build_valid_chain()
        hardware = json.loads(chain["raw_sources"]["hardware"].decode("utf-8"))
        hardware["openStringMidi"] = [41, 45, 50, 55, 59, 64]
        chain["raw_sources"]["hardware"] = v1_fixture.render(hardware)
        _sync_source_hash_into_binding(chain, "hardware")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_DECLARATION_OPEN_STRING_MIDI_MISMATCH", result["errors"])

    def test_26_structural_event_semantics_mismatch_fails(self):
        chain = build_valid_chain()
        hardware = json.loads(chain["raw_sources"]["hardware"].decode("utf-8"))
        hardware["eventSemanticsVersion"] = "wrong"
        chain["raw_sources"]["hardware"] = v1_fixture.render(hardware)
        _sync_source_hash_into_binding(chain, "hardware")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertTrue(
            "INVALID_HARDWARE_OR_CALIBRATION_DECLARATION" in result["errors"]
            or "STRUCTURAL_DECLARATION_EVENT_SEMANTICS_VERSION_MISMATCH" in result["errors"]
        )

    def test_27_structural_clock_sync_id_mismatch_fails(self):
        chain = build_valid_chain()
        clock = json.loads(chain["raw_sources"]["clockSync"].decode("utf-8"))
        clock["syncId"] = "other-sync"
        chain["raw_sources"]["clockSync"] = v1_fixture.render(clock)
        _sync_source_hash_into_binding(chain, "clockSync")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_DECLARATION_CLOCK_SYNC_ID_MISMATCH", result["errors"])

    def test_28_binding_package_sha_mismatch_to_v11_fails(self):
        chain = build_valid_chain()
        binding = copy.deepcopy(chain["binding"])
        binding["calibrationPackageBindingSha256"] = "e" * 64
        binding_sha = module._canonical_sha256(binding)
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindings"][0]["structuralAuditInputsSha256"] = binding_sha
        replace_v23_result(chain, obj)
        result = run_chain(
            chain,
            structural_audit_inputs=binding,
            expected_structural_audit_inputs_sha256=binding_sha,
        )
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_AUDIT_INPUTS_PACKAGE_BINDING_SHA256_MISMATCH", result["errors"])

    def test_29_binding_derivation_configuration_sha_mismatch_to_v11_fails(self):
        chain = build_valid_chain()
        binding = copy.deepcopy(chain["binding"])
        binding["derivationConfigurationSha256"] = "e" * 64
        binding_sha = module._canonical_sha256(binding)
        obj = copy.deepcopy(chain["v23_result"])
        obj["structuralAuditInputBindings"][0]["structuralAuditInputsSha256"] = binding_sha
        replace_v23_result(chain, obj)
        result = run_chain(
            chain,
            structural_audit_inputs=binding,
            expected_structural_audit_inputs_sha256=binding_sha,
        )
        self.assert_fail(result)
        self.assertIn("STRUCTURAL_AUDIT_INPUTS_DERIVATION_CONFIGURATION_SHA256_MISMATCH", result["errors"])

    def test_30_inherited_v11_structural_blocker_still_fails(self):
        chain = build_valid_chain()
        latches = json.loads(chain["raw_sources"]["pitchLatch"].decode("utf-8"))
        latches["events"][0]["state"] = "AMBIGUOUS"
        chain["raw_sources"]["pitchLatch"] = v1_fixture.render(latches)
        _sync_source_hash_into_binding(chain, "pitchLatch")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertGreater(result["blockerCounts"]["ambiguousPitchStateCount"], 0)

    def test_31_v12_population_sha_changes_if_v23_result_bytes_change_semantically_harmlessly(self):
        chain_a = build_valid_chain()
        result_a = run_chain(chain_a)
        chain_b = build_valid_chain()
        obj = copy.deepcopy(chain_b["v23_result"])
        obj["syntheticV12Diagnostic"] = "harmless-extra-field"
        replace_v23_result(chain_b, obj)
        result_b = run_chain(chain_b)
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"], (result_a, result_b))
        self.assertNotEqual(
            result_a["captureManifestV23ValidationResultSha256"],
            result_b["captureManifestV23ValidationResultSha256"],
        )
        self.assertNotEqual(result_a["derivedPopulationSha256"], result_b["derivedPopulationSha256"])

    def test_32_v12_population_sha_changes_under_valid_regenerated_v23_binding_chain(self):
        chain_a = build_valid_chain()
        result_a = run_chain(chain_a)

        chain_b = build_valid_chain()
        clock = json.loads(chain_b["raw_sources"]["clockSync"].decode("utf-8"))
        clock["clockDomainId"] = "clock-synthetic-2"
        chain_b["raw_sources"]["clockSync"] = v1_fixture.render(clock)
        _sync_source_hash_into_binding(chain_b, "clockSync")
        result_b = run_chain(chain_b)
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"], (result_a, result_b))
        self.assertNotEqual(chain_a["binding_sha"], chain_b["binding_sha"])
        self.assertNotEqual(chain_a["v23_population_sha"], chain_b["v23_population_sha"])
        self.assertNotEqual(result_a["derivedPopulationSha256"], result_b["derivedPopulationSha256"])

    def test_33_inherited_v11_population_sha_unchanged_by_v12_only_result_identity_change(self):
        chain_a = build_valid_chain()
        result_a = run_chain(chain_a)
        chain_b = build_valid_chain()
        obj = copy.deepcopy(chain_b["v23_result"])
        obj["syntheticV12Diagnostic"] = "different-result-bytes"
        replace_v23_result(chain_b, obj)
        result_b = run_chain(chain_b)
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"])
        self.assertEqual(
            result_a["inheritedV11DerivedPopulationSha256"],
            result_b["inheritedV11DerivedPopulationSha256"],
        )

    def test_34_canonical_v12_result_is_byte_deterministic(self):
        chain = build_valid_chain()
        result_a = run_chain(copy.deepcopy(chain))
        result_b = run_chain(copy.deepcopy(chain))
        self.assertEqual(module.canonical_json_bytes(result_a), module.canonical_json_bytes(result_b))

    def test_35_all_authorization_remains_closed_on_pass(self):
        result = run_chain(build_valid_chain())
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
