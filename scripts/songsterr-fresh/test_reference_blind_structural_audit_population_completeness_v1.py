#!/usr/bin/env python3
"""Synthetic-only tests for structural-audit population completeness V1."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
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
    "population_completeness_v1",
    "reference_blind_structural_audit_population_completeness_v1.py",
)
v12 = _load(
    "structural_audit_v12_for_population",
    "purpose_built_reference_blind_structural_audit_v1_2.py",
)
v12_fixture = _load(
    "structural_audit_v12_fixture_for_population",
    "test_purpose_built_reference_blind_structural_audit_v1_2.py",
)
v23 = _load(
    "capture_v23_for_population",
    "purpose_built_capture_manifest_contract_v2_3.py",
)
v23_fixture = _load(
    "capture_v23_fixture_for_population",
    "test_purpose_built_capture_manifest_contract_v2_3.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _render(value: Any) -> bytes:
    return module.canonical_json_bytes(value)


def _admitted_attempts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in manifest["attempts"] if a.get("admitted") is True]


def _add_second_admitted_attempt(
    manifest: dict[str, Any], source_hashes: dict[str, str], *, variant: str = "A"
) -> None:
    first = _admitted_attempts(manifest)[0]
    second = copy.deepcopy(first)
    suffix = "2" if variant == "A" else "3"
    second["attemptId"] = f"slot-{suffix}-attempt-1"
    second["slotId"] = f"slot-{suffix}"
    second["underlyingPerformanceId"] = f"performance-{suffix}"
    second["playerId"] = f"P0{suffix}"
    second["exerciseId"] = f"EX0{suffix}"
    second["attemptNumber"] = 1
    second["capturedAtUtc"] = f"2026-09-14T20:0{suffix}:00Z"
    second["evaluatedAudio"] = {
        "path": f"audio/slot-{suffix}.wav",
        "sha256": ("6" if variant == "A" else "a") * 64,
    }
    second["pitchEvidence"] = {
        "path": f"pitch/slot-{suffix}.bin",
        "sha256": ("7" if variant == "A" else "b") * 64,
        "derivedFromEvaluatedAudio": False,
    }
    second["birthEvidence"] = {
        "path": f"birth/slot-{suffix}.bin",
        "sha256": ("8" if variant == "A" else "c") * 64,
        "derivedFromEvaluatedAudio": False,
    }
    second["reference"]["path"] = f"reference/slot-{suffix}.json"
    second["reference"]["sha256"] = ("9" if variant == "A" else "d") * 64
    second["reference"]["pitchEvidenceSha256"] = second["pitchEvidence"]["sha256"]
    second["reference"]["birthEvidenceSha256"] = second["birthEvidence"]["sha256"]
    binding = v23_fixture.structural_binding(manifest, second)
    binding["hardwareSourceSha256"] = source_hashes["hardware"]
    binding["birthStreamSha256"] = source_hashes["birth"]
    binding["pitchLatchStreamSha256"] = source_hashes["pitchLatch"]
    binding["clockSyncSourceSha256"] = source_hashes["clockSync"]
    second["reference"]["structuralAuditInputs"] = binding
    second["reference"]["structuralAuditInputsSha256"] = v23._canonical_sha256(binding)
    manifest["attempts"].append(second)


def build_population(count: int = 2, *, variant: str = "A") -> dict[str, Any]:
    base = v12_fixture.build_valid_chain()
    manifest = copy.deepcopy(base["manifest"])
    if count == 2:
        _add_second_admitted_attempt(manifest, base["expected"], variant=variant)
    elif count != 1:
        raise ValueError("count must be 1 or 2")

    v23_result = v23.validate_manifest(manifest)
    assert v23_result["contractValid"] is True, v23_result
    v23_bytes = _render(v23_result)
    v23_sha = _sha(v23_bytes)
    population_sha = v23_result["admittedPopulationManifestSha256"]

    v12_results: list[dict[str, Any]] = []
    for attempt in _admitted_attempts(manifest):
        binding = copy.deepcopy(attempt["reference"]["structuralAuditInputs"])
        binding_sha = attempt["reference"]["structuralAuditInputsSha256"]
        result = v12.audit_raw_sources_v1_2(
            raw_sources=base["raw_sources"],
            expected_sha256=base["expected"],
            calibration_provenance_result=base["provenance_bytes"],
            expected_calibration_provenance_result_sha256=base["provenance_sha"],
            declared_provenance_result_sha256=base["provenance_sha"],
            declared_calibration_package_binding_sha256=base["package_binding_sha"],
            capture_manifest_v23_validation_result=v23_bytes,
            expected_capture_manifest_v23_validation_result_sha256=v23_sha,
            structural_audit_inputs=binding,
            expected_structural_audit_inputs_sha256=binding_sha,
            expected_capture_manifest_v23_admitted_population_sha256=population_sha,
        )
        assert result["contractValid"] is True, result
        raw = _render(result)
        v12_results.append({"result": result, "raw": raw, "sha": _sha(raw)})

    return {
        "manifest": manifest,
        "v23_result": v23_result,
        "v23_raw": v23_bytes,
        "v23_sha": v23_sha,
        "population_sha": population_sha,
        "v12": v12_results,
    }


def run_population(pop: dict[str, Any], *, v23_raw: Any = None, v23_sha: Any = None, pairs=None):
    if v23_raw is None:
        v23_raw = pop["v23_raw"]
    if v23_sha is None:
        v23_sha = pop["v23_sha"]
    if pairs is None:
        pairs = [(item["raw"], item["sha"]) for item in pop["v12"]]
    return module.aggregate_population(
        capture_manifest_v23_validation_result=v23_raw,
        expected_capture_manifest_v23_validation_result_sha256=v23_sha,
        v12_validation_results=pairs,
    )


def replace_v23(pop: dict[str, Any], result: dict[str, Any]) -> tuple[bytes, str]:
    raw = _render(result)
    return raw, _sha(raw)


def mutated_v12_pair(item: dict[str, Any], mutator) -> tuple[bytes, str]:
    result = copy.deepcopy(item["result"])
    mutator(result)
    raw = _render(result)
    return raw, _sha(raw)


class PopulationCompletenessV1Tests(unittest.TestCase):
    def assert_fail(self, result: dict[str, Any]) -> None:
        self.assertFalse(result["contractValid"])
        self.assertFalse(result["populationStructurallySuitable"])
        self.assertFalse(result["populationStructuralCompletenessEstablished"])
        self.assertIsNone(result["populationStructuralCompletenessSha256"])
        self.assertFalse(result["realCalibrationAuthorized"])
        self.assertFalse(result["realHoldoutCaptureAuthorized"])
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])

    def test_01_one_admitted_attempt_passes(self):
        result = run_population(build_population(1))
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["admittedBindingCount"], 1)
        self.assertEqual(result["verifiedV12ResultCount"], 1)
        self.assertTrue(result["populationStructuralCompletenessSha256"])

    def test_02_two_admitted_attempts_pass(self):
        result = run_population(build_population(2))
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["admittedBindingCount"], 2)
        self.assertEqual(result["verifiedV12ResultCount"], 2)
        self.assertEqual(result["admittedBindingKeys"], result["verifiedV12BindingKeys"])

    def test_03_v23_raw_not_bytes_fails(self):
        pop = build_population(2)
        result = run_population(pop, v23_raw="not-bytes")
        self.assert_fail(result)
        self.assertIn("V23_RESULT_NOT_BYTES", result["errors"])

    def test_04_malformed_v23_expected_sha_fails(self):
        pop = build_population(2)
        result = run_population(pop, v23_sha="bad")
        self.assert_fail(result)
        self.assertIn("V23_EXPECTED_SHA256_INVALID", result["errors"])

    def test_05_v23_hash_mismatch_short_circuits_before_parse(self):
        pop = build_population(2)
        raw = b"not-json"
        result = run_population(pop, v23_raw=raw, v23_sha="0" * 64)
        self.assert_fail(result)
        self.assertIn("V23_RESULT_SHA256_MISMATCH", result["errors"])
        self.assertFalse(any("V23_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_06_invalid_v23_json_after_hash_fails(self):
        pop = build_population(2)
        for raw in (b"{bad", b"\xff\xfe"):
            with self.subTest(raw=raw):
                result = run_population(pop, v23_raw=raw, v23_sha=_sha(raw))
                self.assert_fail(result)
                self.assertTrue(any("V23_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_07_v23_contract_pass_semantic_and_advance_failures_fail(self):
        for field, value in (
            ("contract", "wrong"),
            ("contractValid", False),
            ("v23SemanticGuardPassed", False),
            ("mayAdvanceToReferenceBlindStructuralAudit", False),
        ):
            with self.subTest(field=field):
                pop = build_population(2)
                obj = copy.deepcopy(pop["v23_result"])
                obj[field] = value
                raw, sha = replace_v23(pop, obj)
                result = run_population(pop, v23_raw=raw, v23_sha=sha)
                self.assert_fail(result)

    def test_08_v23_errors_nonempty_fails(self):
        pop = build_population(2)
        obj = copy.deepcopy(pop["v23_result"])
        obj["errors"] = ["synthetic"]
        raw, sha = replace_v23(pop, obj)
        result = run_population(pop, v23_raw=raw, v23_sha=sha)
        self.assert_fail(result)
        self.assertIn("V23_RESULT_ERRORS_NOT_EMPTY", result["errors"])

    def test_09_v23_population_version_or_sha_invalid_fails(self):
        for field, value in (
            ("populationIdentityVersion", "wrong"),
            ("admittedPopulationManifestSha256", "bad"),
        ):
            with self.subTest(field=field):
                pop = build_population(2)
                obj = copy.deepcopy(pop["v23_result"])
                obj[field] = value
                raw, sha = replace_v23(pop, obj)
                result = run_population(pop, v23_raw=raw, v23_sha=sha)
                self.assert_fail(result)

    def test_10_v23_binding_contract_mismatch_fails(self):
        pop = build_population(2)
        obj = copy.deepcopy(pop["v23_result"])
        obj["structuralAuditInputBindingContract"] = "wrong"
        raw, sha = replace_v23(pop, obj)
        self.assert_fail(run_population(pop, v23_raw=raw, v23_sha=sha))

    def test_11_v23_binding_count_mismatch_or_zero_fails(self):
        for value in (0, 99):
            with self.subTest(value=value):
                pop = build_population(2)
                obj = copy.deepcopy(pop["v23_result"])
                obj["structuralAuditInputBindingCount"] = value
                raw, sha = replace_v23(pop, obj)
                self.assert_fail(run_population(pop, v23_raw=raw, v23_sha=sha))

    def test_12_malformed_v23_binding_entry_fails(self):
        pop = build_population(2)
        obj = copy.deepcopy(pop["v23_result"])
        obj["structuralAuditInputBindings"][0]["structuralAuditInputsSha256"] = "bad"
        raw, sha = replace_v23(pop, obj)
        self.assert_fail(run_population(pop, v23_raw=raw, v23_sha=sha))

    def test_13_duplicate_v23_attempt_or_binding_key_fails(self):
        pop = build_population(2)
        obj = copy.deepcopy(pop["v23_result"])
        obj["structuralAuditInputBindings"][1] = copy.deepcopy(obj["structuralAuditInputBindings"][0])
        raw, sha = replace_v23(pop, obj)
        result = run_population(pop, v23_raw=raw, v23_sha=sha)
        self.assert_fail(result)
        self.assertTrue(any("V23_DUPLICATE" in e for e in result["errors"]))

    def test_14_v23_downstream_authorization_open_fails(self):
        pop = build_population(2)
        obj = copy.deepcopy(pop["v23_result"])
        obj["v6Authorized"] = True
        raw, sha = replace_v23(pop, obj)
        self.assert_fail(run_population(pop, v23_raw=raw, v23_sha=sha))

    def test_15_v12_raw_not_bytes_fails(self):
        pop = build_population(2)
        pairs = [("not-bytes", pop["v12"][0]["sha"]), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]
        result = run_population(pop, pairs=pairs)
        self.assert_fail(result)
        self.assertIn("V12[0]_RESULT_NOT_BYTES", result["errors"])

    def test_16_malformed_v12_expected_sha_fails(self):
        pop = build_population(2)
        pairs = [(pop["v12"][0]["raw"], "bad"), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]
        self.assert_fail(run_population(pop, pairs=pairs))

    def test_17_v12_hash_mismatch_short_circuits_all_v12_parse(self):
        pop = build_population(2)
        pairs = [(b"not-json", "0" * 64), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]
        result = run_population(pop, pairs=pairs)
        self.assert_fail(result)
        self.assertIn("V12[0]_RESULT_SHA256_MISMATCH", result["errors"])
        self.assertFalse(any("V12[0]_RESULT_INVALID_JSON" in e for e in result["errors"]))
        self.assertEqual(result["verifiedV12ResultCount"], 0)

    def test_18_invalid_v12_json_after_hash_fails(self):
        pop = build_population(2)
        raw = b"{bad"
        pairs = [(raw, _sha(raw)), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]
        result = run_population(pop, pairs=pairs)
        self.assert_fail(result)
        self.assertTrue(any("V12[0]_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_19_v12_contract_pass_or_suitability_failure_fails(self):
        cases = (
            ("contract", "wrong"),
            ("contractValid", False),
            ("datasetStructurallySuitable", False),
            ("authoritativeStructuralSuitabilityEstablished", False),
        )
        for field, value in cases:
            with self.subTest(field=field):
                pop = build_population(2)
                first = mutated_v12_pair(pop["v12"][0], lambda r, f=field, v=value: r.__setitem__(f, v))
                pairs = [first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]
                self.assert_fail(run_population(pop, pairs=pairs))

    def test_20_v12_errors_nonempty_fails(self):
        pop = build_population(2)
        first = mutated_v12_pair(pop["v12"][0], lambda r: r.__setitem__("errors", ["synthetic"]))
        self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_21_nonzero_v12_bridge_violation_fails(self):
        for field in ("capturePopulationBindingViolationCount", "calibrationProvenanceBridgeViolationCount"):
            with self.subTest(field=field):
                pop = build_population(2)
                first = mutated_v12_pair(pop["v12"][0], lambda r, f=field: r.__setitem__(f, 1))
                self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_22_nonzero_inherited_v1_blocker_fails(self):
        pop = build_population(2)
        def mutate(r):
            r["blockerCounts"]["sameKeyOverlapCount"] = 1
        first = mutated_v12_pair(pop["v12"][0], mutate)
        self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_23_v12_v23_result_sha_mismatch_fails(self):
        pop = build_population(2)
        first = mutated_v12_pair(pop["v12"][0], lambda r: r.__setitem__("captureManifestV23ValidationResultSha256", "0" * 64))
        self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_24_v12_v23_population_sha_mismatch_fails(self):
        pop = build_population(2)
        first = mutated_v12_pair(pop["v12"][0], lambda r: r.__setitem__("captureManifestV23AdmittedPopulationSha256", "0" * 64))
        self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_25_malformed_v12_attempt_binding_or_derived_identity_fails(self):
        cases = (
            ("attemptId", ""),
            ("structuralAuditInputsSha256", "bad"),
            ("derivedPopulationSha256", "bad"),
        )
        for field, value in cases:
            with self.subTest(field=field):
                pop = build_population(2)
                first = mutated_v12_pair(pop["v12"][0], lambda r, f=field, v=value: r.__setitem__(f, v))
                self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_26_v12_downstream_authorization_open_fails(self):
        pop = build_population(2)
        first = mutated_v12_pair(pop["v12"][0], lambda r: r.__setitem__("correctnessAuthorized", True))
        self.assert_fail(run_population(pop, pairs=[first, (pop["v12"][1]["raw"], pop["v12"][1]["sha"])]))

    def test_27_duplicate_v12_result_hash_fails(self):
        pop = build_population(2)
        pair = (pop["v12"][0]["raw"], pop["v12"][0]["sha"])
        result = run_population(pop, pairs=[pair, pair])
        self.assert_fail(result)
        self.assertIn("DUPLICATE_V12_RESULT_SHA256", result["errors"])

    def test_28_duplicate_v12_attempt_or_key_fails(self):
        pop = build_population(2)
        first_obj = copy.deepcopy(pop["v12"][0]["result"])
        second_obj = copy.deepcopy(pop["v12"][1]["result"])
        second_obj["attemptId"] = first_obj["attemptId"]
        second_obj["structuralAuditInputsSha256"] = first_obj["structuralAuditInputsSha256"]
        second_raw = _render(second_obj)
        pairs = [(pop["v12"][0]["raw"], pop["v12"][0]["sha"]), (second_raw, _sha(second_raw))]
        result = run_population(pop, pairs=pairs)
        self.assert_fail(result)
        self.assertTrue(any("DUPLICATE_V12" in e for e in result["errors"]))

    def test_29_missing_admitted_v12_result_fails(self):
        pop = build_population(2)
        result = run_population(pop, pairs=[(pop["v12"][0]["raw"], pop["v12"][0]["sha"])])
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("MISSING_V12_AUDIT") for e in result["errors"]))

    def test_30_extra_nonadmitted_v12_result_fails(self):
        pop = build_population(1)
        extra_obj = copy.deepcopy(pop["v12"][0]["result"])
        extra_obj["attemptId"] = "not-admitted"
        extra_obj["structuralAuditInputsSha256"] = "e" * 64
        extra_raw = _render(extra_obj)
        pairs = [(pop["v12"][0]["raw"], pop["v12"][0]["sha"]), (extra_raw, _sha(extra_raw))]
        result = run_population(pop, pairs=pairs)
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("EXTRA_V12_AUDIT") for e in result["errors"]))

    def test_31_admitted_binding_sha_mismatch_fails(self):
        pop = build_population(2)
        first_obj = copy.deepcopy(pop["v12"][0]["result"])
        first_obj["structuralAuditInputsSha256"] = "e" * 64
        raw = _render(first_obj)
        result = run_population(pop, pairs=[(raw, _sha(raw)), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])])
        self.assert_fail(result)

    def test_32_zero_v12_results_fails(self):
        result = run_population(build_population(1), pairs=[])
        self.assert_fail(result)
        self.assertIn("V12_RESULTS_REQUIRED", result["errors"])

    def test_33_completeness_sha_changes_with_valid_v12_result_byte_identity(self):
        pop = build_population(2)
        result_a = run_population(pop)
        first_obj = copy.deepcopy(pop["v12"][0]["result"])
        first_obj["syntheticCompletenessDiagnostic"] = "changes-result-bytes-only"
        first_raw = _render(first_obj)
        result_b = run_population(
            pop,
            pairs=[(first_raw, _sha(first_raw)), (pop["v12"][1]["raw"], pop["v12"][1]["sha"])],
        )
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"])
        self.assertNotEqual(result_a["populationStructuralCompletenessSha256"], result_b["populationStructuralCompletenessSha256"])

    def test_34_completeness_sha_changes_for_different_valid_two_attempt_population(self):
        result_a = run_population(build_population(2, variant="A"))
        result_b = run_population(build_population(2, variant="B"))
        self.assertTrue(result_a["contractValid"] and result_b["contractValid"])
        self.assertNotEqual(result_a["captureManifestV23AdmittedPopulationSha256"], result_b["captureManifestV23AdmittedPopulationSha256"])
        self.assertNotEqual(result_a["populationStructuralCompletenessSha256"], result_b["populationStructuralCompletenessSha256"])

    def test_35_input_order_does_not_change_completeness_sha(self):
        pop = build_population(2)
        pairs = [(item["raw"], item["sha"]) for item in pop["v12"]]
        a = run_population(pop, pairs=pairs)
        b = run_population(pop, pairs=list(reversed(pairs)))
        self.assertTrue(a["contractValid"] and b["contractValid"])
        self.assertEqual(a["populationStructuralCompletenessSha256"], b["populationStructuralCompletenessSha256"])

    def test_36_canonical_output_is_byte_deterministic(self):
        pop = build_population(2)
        a = run_population(pop)
        b = run_population(pop)
        self.assertEqual(module.canonical_json_bytes(a), module.canonical_json_bytes(b))

    def test_37_authorization_remains_closed_on_pass(self):
        result = run_population(build_population(2))
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
