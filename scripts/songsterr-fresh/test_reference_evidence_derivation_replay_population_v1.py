#!/usr/bin/env python3
"""Synthetic-only tests for Reference Evidence Derivation Replay Population V1."""
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
    "derivation_replay_population_v1",
    "reference_evidence_derivation_replay_population_v1.py",
)
provenance = _load(
    "provenance_for_derivation_replay",
    "reference_calibration_package_provenance_v1.py",
)
v23 = _load(
    "capture_v23_for_derivation_replay",
    "purpose_built_capture_manifest_contract_v2_3.py",
)
v23_fixture = _load(
    "capture_v23_fixture_for_derivation_replay",
    "test_purpose_built_capture_manifest_contract_v2_3.py",
)
v1_fixture = _load(
    "structural_v1_fixture_for_derivation_replay",
    "test_purpose_built_reference_blind_structural_audit_v1.py",
)
v12 = _load(
    "structural_v12_for_derivation_replay",
    "purpose_built_reference_blind_structural_audit_v1_2.py",
)
completeness = _load(
    "population_completeness_for_derivation_replay",
    "reference_blind_structural_audit_population_completeness_v1.py",
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _render(value: Any) -> bytes:
    return module.canonical_json_bytes(value)


NORMAL_DECODER = r'''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("--pitch-evidence", required=True)
p.add_argument("--birth-evidence", required=True)
p.add_argument("--configuration", required=True)
p.add_argument("--pitch-latch-output", required=True)
p.add_argument("--birth-output", required=True)
a=p.parse_args()
cfg=json.loads(Path(a.configuration).read_text(encoding="utf-8"))
sep=bytes.fromhex(cfg["separatorHex"])
def decode(src,dst):
    data=Path(src).read_bytes()
    if sep not in data:
        raise SystemExit(9)
    Path(dst).write_bytes(data.split(sep,1)[1])
decode(a.pitch_evidence,a.pitch_latch_output)
decode(a.birth_evidence,a.birth_output)
'''.encode("utf-8")

NONZERO_DECODER = b"raise SystemExit(7)\n"
TIMEOUT_DECODER = b"import time\ntime.sleep(60)\n"
MISSING_PITCH_DECODER = r'''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("--pitch-evidence",required=True); p.add_argument("--birth-evidence",required=True); p.add_argument("--configuration",required=True); p.add_argument("--pitch-latch-output",required=True); p.add_argument("--birth-output",required=True); a=p.parse_args()
cfg=json.loads(Path(a.configuration).read_text()); sep=bytes.fromhex(cfg["separatorHex"]); data=Path(a.birth_evidence).read_bytes(); Path(a.birth_output).write_bytes(data.split(sep,1)[1])
'''.encode("utf-8")
MISSING_BIRTH_DECODER = r'''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("--pitch-evidence",required=True); p.add_argument("--birth-evidence",required=True); p.add_argument("--configuration",required=True); p.add_argument("--pitch-latch-output",required=True); p.add_argument("--birth-output",required=True); a=p.parse_args()
cfg=json.loads(Path(a.configuration).read_text()); sep=bytes.fromhex(cfg["separatorHex"]); data=Path(a.pitch_evidence).read_bytes(); Path(a.pitch_latch_output).write_bytes(data.split(sep,1)[1])
'''.encode("utf-8")
BAD_PITCH_DECODER = r'''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("--pitch-evidence",required=True); p.add_argument("--birth-evidence",required=True); p.add_argument("--configuration",required=True); p.add_argument("--pitch-latch-output",required=True); p.add_argument("--birth-output",required=True); a=p.parse_args()
cfg=json.loads(Path(a.configuration).read_text()); sep=bytes.fromhex(cfg["separatorHex"])
pitch=Path(a.pitch_evidence).read_bytes().split(sep,1)[1]; birth=Path(a.birth_evidence).read_bytes().split(sep,1)[1]
obj=json.loads(pitch.decode("utf-8")); Path(a.pitch_latch_output).write_text(json.dumps(obj,sort_keys=True,indent=2),encoding="utf-8"); Path(a.birth_output).write_bytes(birth)
'''.encode("utf-8")
BAD_BIRTH_DECODER = r'''import argparse, json
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument("--pitch-evidence",required=True); p.add_argument("--birth-evidence",required=True); p.add_argument("--configuration",required=True); p.add_argument("--pitch-latch-output",required=True); p.add_argument("--birth-output",required=True); a=p.parse_args()
cfg=json.loads(Path(a.configuration).read_text()); sep=bytes.fromhex(cfg["separatorHex"])
pitch=Path(a.pitch_evidence).read_bytes().split(sep,1)[1]; birth=Path(a.birth_evidence).read_bytes().split(sep,1)[1]
obj=json.loads(birth.decode("utf-8")); Path(a.pitch_latch_output).write_bytes(pitch); Path(a.birth_output).write_text(json.dumps(obj,sort_keys=True,indent=2),encoding="utf-8")
'''.encode("utf-8")

CONFIG_BYTES = b'{"separatorHex":"0a0a"}'


def decoder_code_for_variant(variant: str) -> bytes:
    return {
        "normal": NORMAL_DECODER,
        "nonzero": NONZERO_DECODER,
        "timeout": TIMEOUT_DECODER,
        "missing-pitch": MISSING_PITCH_DECODER,
        "missing-birth": MISSING_BIRTH_DECODER,
        "bad-pitch": BAD_PITCH_DECODER,
        "bad-birth": BAD_BIRTH_DECODER,
    }[variant]


def _admitted_attempts(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [a for a in manifest["attempts"] if a.get("admitted") is True]


def _structural_documents_for_attempt(index: int, corpus: dict[str, Any]):
    hardware, births, latches, clock = v1_fixture.base_documents()
    hardware["configurationId"] = corpus["hardware"]["configuration"]["configurationId"]
    hardware["calibrationId"] = corpus["referenceCalibration"]["calibrationId"]
    hardware["openStringMidi"] = copy.deepcopy(
        corpus["hardware"]["instrumentSetup"]["openStringMidi"]
    )
    clock["syncId"] = corpus["clockSync"]["syncId"]
    if index:
        offset = float(index)
        for n, birth in enumerate(births["events"], start=1):
            birth["birthEventId"] = f"b{index+1}{n}"
            birth["onsetSeconds"] += offset
            birth["releaseSeconds"] += offset
        for n, latch in enumerate(latches["events"], start=1):
            latch["pitchLatchId"] = f"l{index+1}{n}"
            latch["birthEventId"] = births["events"][n-1]["birthEventId"]
            latch["timestampSeconds"] += offset
    return hardware, births, latches, clock


def _add_second_admitted_attempt(manifest: dict[str, Any]) -> None:
    first = _admitted_attempts(manifest)[0]
    second = copy.deepcopy(first)
    second["attemptId"] = "slot-2-attempt-1"
    second["slotId"] = "slot-2"
    second["underlyingPerformanceId"] = "performance-2"
    second["playerId"] = "P02"
    second["exerciseId"] = "EX02"
    second["attemptNumber"] = 1
    second["capturedAtUtc"] = "2026-09-14T20:02:00Z"
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
    manifest["attempts"].append(second)


def _make_executable_package(decoder_variant: str):
    code = decoder_code_for_variant(decoder_variant)
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "package"
        package_manifest = provenance.build_synthetic_fixture(root)
        package_manifest["decoder"]["decoderId"] = "synthetic-executable-reference-decoder-v1"
        package_manifest["decoder"]["softwareVersion"] = "1.0.0-executable-synthetic"
        code_path = root / package_manifest["decoder"]["code"]["path"]
        config_path = root / package_manifest["decoder"]["configuration"]["path"]
        code_path.write_bytes(code)
        config_path.write_bytes(CONFIG_BYTES)
        package_manifest["decoder"]["code"]["sha256"] = _sha(code)
        package_manifest["decoder"]["configuration"]["sha256"] = _sha(CONFIG_BYTES)
        result = provenance.validate_package(package_manifest, root)
    assert result["contractValid"] is True, result
    raw = _render(result)
    return result, raw, _sha(raw), code, CONFIG_BYTES


def build_chain(
    count: int = 2,
    *,
    decoder_variant: str = "normal",
    raw_salt: str = "A",
) -> dict[str, Any]:
    if count not in (1, 2):
        raise ValueError("count must be 1 or 2")
    prov_result, prov_raw, prov_sha, decoder_code, decoder_config = _make_executable_package(
        decoder_variant
    )
    package_binding = prov_result["packageBinding"]
    package_sha = prov_result["packageBindingSha256"]
    decoder_config_sha = package_binding["decoder"]["configuration"]["sha256"]

    manifest = v23_fixture.valid_manifest()
    corpus = manifest["corpus"]
    corpus["hardware"]["configuration"]["configurationId"] = package_binding[
        "hardwareConfiguration"
    ]["configurationId"]
    corpus["hardware"]["configuration"]["sha256"] = package_binding[
        "hardwareConfiguration"
    ]["sha256"]
    corpus["hardware"]["instrumentSetup"]["setupSha256"] = package_binding[
        "instrumentSetupSha256"
    ]
    corpus["referenceCalibration"]["calibrationId"] = package_binding["calibrationId"]
    corpus["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"] = package_binding[
        "maxAbsoluteOnsetErrorSeconds"
    ]
    corpus["referenceCalibrationPackage"] = {
        "contract": provenance.CONTRACT,
        "validationResultPath": "calibration/executable-provenance-result.json",
        "validationResultSha256": prov_sha,
        "packageBindingSha256": package_sha,
        "packageBinding": copy.deepcopy(package_binding),
    }

    if count == 2:
        _add_second_admitted_attempt(manifest)

    common_hardware = None
    common_clock = None
    attempts_data: list[dict[str, Any]] = []
    for index, attempt in enumerate(_admitted_attempts(manifest)):
        reference = attempt["reference"]
        reference["configurationSha256"] = package_binding["hardwareConfiguration"]["sha256"]
        reference["calibrationId"] = package_binding["calibrationId"]
        reference["calibrationPackageBindingSha256"] = package_sha
        reference["derivationConfigurationSha256"] = decoder_config_sha

        hardware, births, latches, clock = _structural_documents_for_attempt(index, corpus)
        hardware_raw = v1_fixture.render(hardware)
        birth_raw = v1_fixture.render(births)
        latch_raw = v1_fixture.render(latches)
        clock_raw = v1_fixture.render(clock)
        if common_hardware is None:
            common_hardware = hardware_raw
            common_clock = clock_raw
        else:
            assert hardware_raw == common_hardware
            assert clock_raw == common_clock

        pitch_evidence = f"PITCH|{raw_salt}|{index}\n\n".encode("utf-8") + latch_raw
        birth_evidence = f"BIRTH|{raw_salt}|{index}\n\n".encode("utf-8") + birth_raw
        attempt["pitchEvidence"]["sha256"] = _sha(pitch_evidence)
        attempt["birthEvidence"]["sha256"] = _sha(birth_evidence)
        reference["pitchEvidenceSha256"] = attempt["pitchEvidence"]["sha256"]
        reference["birthEvidenceSha256"] = attempt["birthEvidence"]["sha256"]
        reference["sha256"] = hashlib.sha256(f"reference-{raw_salt}-{index}".encode()).hexdigest()

        binding = v23_fixture.structural_binding(manifest, attempt)
        binding["hardwareSourceSha256"] = _sha(hardware_raw)
        binding["birthStreamSha256"] = _sha(birth_raw)
        binding["pitchLatchStreamSha256"] = _sha(latch_raw)
        binding["clockSyncSourceSha256"] = _sha(clock_raw)
        reference["structuralAuditInputs"] = binding
        binding_sha = v23._canonical_sha256(binding)
        reference["structuralAuditInputsSha256"] = binding_sha
        attempts_data.append(
            {
                "attempt": attempt,
                "binding": copy.deepcopy(binding),
                "binding_sha": binding_sha,
                "pitch_evidence": pitch_evidence,
                "birth_evidence": birth_evidence,
                "raw_sources": {
                    "hardware": hardware_raw,
                    "birth": birth_raw,
                    "pitchLatch": latch_raw,
                    "clockSync": clock_raw,
                },
            }
        )

    v23_result = v23.validate_manifest(manifest)
    assert v23_result["contractValid"] is True, v23_result
    assert v23_result["calibrationPackageValidationResultSha256"] == prov_sha
    v23_raw = _render(v23_result)
    v23_sha = _sha(v23_raw)
    v23_population_sha = v23_result["admittedPopulationManifestSha256"]

    v12_items = []
    for item in attempts_data:
        expected = {name: _sha(data) for name, data in item["raw_sources"].items()}
        result = v12.audit_raw_sources_v1_2(
            raw_sources=item["raw_sources"],
            expected_sha256=expected,
            calibration_provenance_result=prov_raw,
            expected_calibration_provenance_result_sha256=prov_sha,
            declared_provenance_result_sha256=prov_sha,
            declared_calibration_package_binding_sha256=package_sha,
            capture_manifest_v23_validation_result=v23_raw,
            expected_capture_manifest_v23_validation_result_sha256=v23_sha,
            structural_audit_inputs=item["binding"],
            expected_structural_audit_inputs_sha256=item["binding_sha"],
            expected_capture_manifest_v23_admitted_population_sha256=v23_population_sha,
        )
        assert result["contractValid"] is True, result
        result_raw = _render(result)
        v12_items.append({"result": result, "raw": result_raw, "sha": _sha(result_raw)})

    complete_result = completeness.aggregate_population(
        capture_manifest_v23_validation_result=v23_raw,
        expected_capture_manifest_v23_validation_result_sha256=v23_sha,
        v12_validation_results=[(item["raw"], item["sha"]) for item in v12_items],
    )
    assert complete_result["contractValid"] is True, complete_result
    complete_raw = _render(complete_result)
    complete_sha = _sha(complete_raw)

    replay_attempts = [
        {
            "structuralAuditInputs": copy.deepcopy(item["binding"]),
            "expectedStructuralAuditInputsSha256": item["binding_sha"],
            "pitchEvidence": item["pitch_evidence"],
            "birthEvidence": item["birth_evidence"],
        }
        for item in attempts_data
    ]

    return {
        "manifest": manifest,
        "provenance_result": prov_result,
        "provenance_raw": prov_raw,
        "provenance_sha": prov_sha,
        "package_binding_sha": package_sha,
        "decoder_code": decoder_code,
        "decoder_config": decoder_config,
        "v23_result": v23_result,
        "v23_raw": v23_raw,
        "v23_sha": v23_sha,
        "v23_population_sha": v23_population_sha,
        "v12": v12_items,
        "completeness_result": complete_result,
        "completeness_raw": complete_raw,
        "completeness_sha": complete_sha,
        "replay_attempts": replay_attempts,
    }


def run_chain(chain: dict[str, Any], **overrides: Any) -> dict[str, Any]:
    args = {
        "capture_manifest_v23_validation_result": chain["v23_raw"],
        "expected_capture_manifest_v23_validation_result_sha256": chain["v23_sha"],
        "structural_population_completeness_result": chain["completeness_raw"],
        "expected_structural_population_completeness_result_sha256": chain[
            "completeness_sha"
        ],
        "calibration_provenance_result": chain["provenance_raw"],
        "expected_calibration_provenance_result_sha256": chain["provenance_sha"],
        "decoder_code": chain["decoder_code"],
        "decoder_configuration": chain["decoder_config"],
        "replay_attempts": chain["replay_attempts"],
    }
    args.update(overrides)
    return module.replay_population(**args)


def replace_result(value: dict[str, Any]) -> tuple[bytes, str]:
    raw = _render(value)
    return raw, _sha(raw)


class DerivationReplayPopulationV1Tests(unittest.TestCase):
    def assert_fail(self, result: dict[str, Any]) -> None:
        self.assertFalse(result["contractValid"])
        self.assertFalse(result["populationDerivationReplayEstablished"])
        self.assertIsNone(result["populationDerivationReplaySha256"])
        self.assertFalse(result["realCalibrationAuthorized"])
        self.assertFalse(result["realHoldoutCaptureAuthorized"])
        self.assertFalse(result["basicPitchAuthorized"])
        self.assertFalse(result["v6Authorized"])
        self.assertFalse(result["correctnessAuthorized"])
        self.assertFalse(result["modelValidationComplete"])
        self.assertEqual(result["customerEligibleEvents"], 0)
        self.assertFalse(result["mayAdvanceDelivery"])

    def test_01_two_admitted_attempts_pass(self):
        result = run_chain(build_chain(2))
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["admittedBindingCount"], 2)
        self.assertEqual(result["verifiedReplayCount"], 2)
        self.assertTrue(result["populationDerivationReplaySha256"])

    def test_02_one_admitted_attempt_passes(self):
        result = run_chain(build_chain(1))
        self.assertTrue(result["contractValid"], result)
        self.assertEqual(result["verifiedReplayCount"], 1)

    def test_03_v23_raw_not_bytes_fails(self):
        chain = build_chain()
        result = run_chain(chain, capture_manifest_v23_validation_result="bad")
        self.assert_fail(result)
        self.assertIn("V23_RESULT_NOT_BYTES", result["errors"])

    def test_04_v23_expected_sha_invalid_fails(self):
        chain = build_chain()
        result = run_chain(chain, expected_capture_manifest_v23_validation_result_sha256="bad")
        self.assert_fail(result)

    def test_05_v23_hash_mismatch_short_circuits_parse(self):
        chain = build_chain()
        result = run_chain(
            chain,
            capture_manifest_v23_validation_result=b"not-json",
            expected_capture_manifest_v23_validation_result_sha256="0" * 64,
        )
        self.assert_fail(result)
        self.assertIn("V23_RESULT_SHA256_MISMATCH", result["errors"])
        self.assertFalse(any("V23_RESULT_INVALID_JSON" in e for e in result["errors"]))

    def test_06_completeness_hash_before_parse_boundaries_fail(self):
        chain = build_chain()
        for raw, sha in (("bad", chain["completeness_sha"]), (b"bad-json", "0" * 64)):
            with self.subTest(raw=raw):
                result = run_chain(
                    chain,
                    structural_population_completeness_result=raw,
                    expected_structural_population_completeness_result_sha256=sha,
                )
                self.assert_fail(result)

    def test_07_provenance_hash_before_parse_boundaries_fail(self):
        chain = build_chain()
        for raw, sha in (("bad", chain["provenance_sha"]), (b"bad-json", "0" * 64)):
            with self.subTest(raw=raw):
                result = run_chain(
                    chain,
                    calibration_provenance_result=raw,
                    expected_calibration_provenance_result_sha256=sha,
                )
                self.assert_fail(result)

    def test_08_v23_contract_guard_population_or_authorization_failure_fails(self):
        cases = (
            ("contract", "wrong"),
            ("contractValid", False),
            ("v23SemanticGuardPassed", False),
            ("mayAdvanceToReferenceBlindStructuralAudit", False),
            ("populationIdentityVersion", "wrong"),
            ("v6Authorized", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                chain = build_chain()
                obj = copy.deepcopy(chain["v23_result"])
                obj[field] = value
                raw, sha = replace_result(obj)
                self.assert_fail(run_chain(chain, capture_manifest_v23_validation_result=raw, expected_capture_manifest_v23_validation_result_sha256=sha))

    def test_09_completeness_contract_pass_identity_link_or_authorization_failure_fails(self):
        cases = (
            ("contract", "wrong"),
            ("contractValid", False),
            ("populationStructuralCompletenessEstablished", False),
            ("populationIdentityVersion", "wrong"),
            ("captureManifestV23ValidationResultSha256", "0" * 64),
            ("correctnessAuthorized", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                chain = build_chain()
                obj = copy.deepcopy(chain["completeness_result"])
                obj[field] = value
                raw, sha = replace_result(obj)
                self.assert_fail(run_chain(chain, structural_population_completeness_result=raw, expected_structural_population_completeness_result_sha256=sha))

    def test_10_provenance_contract_pass_errors_or_authorization_failure_fails(self):
        cases = (
            ("contract", "wrong"),
            ("contractValid", False),
            ("errors", ["synthetic"]),
            ("basicPitchAuthorized", True),
        )
        for field, value in cases:
            with self.subTest(field=field):
                chain = build_chain()
                obj = copy.deepcopy(chain["provenance_result"])
                obj[field] = value
                raw, sha = replace_result(obj)
                self.assert_fail(run_chain(chain, calibration_provenance_result=raw, expected_calibration_provenance_result_sha256=sha))

    def test_11_provenance_canonical_package_binding_mismatch_fails(self):
        chain = build_chain()
        obj = copy.deepcopy(chain["provenance_result"])
        obj["packageBinding"]["decoder"]["softwareVersion"] = "changed-without-rebind"
        raw, sha = replace_result(obj)
        self.assert_fail(run_chain(chain, calibration_provenance_result=raw, expected_calibration_provenance_result_sha256=sha))

    def test_12_v23_provenance_result_sha_mismatch_fails(self):
        chain = build_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageValidationResultSha256"] = "0" * 64
        raw, sha = replace_result(obj)
        self.assert_fail(run_chain(chain, capture_manifest_v23_validation_result=raw, expected_capture_manifest_v23_validation_result_sha256=sha))

    def test_13_v23_package_binding_mismatch_fails(self):
        chain = build_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageBindingSha256"] = "0" * 64
        raw, sha = replace_result(obj)
        self.assert_fail(run_chain(chain, capture_manifest_v23_validation_result=raw, expected_capture_manifest_v23_validation_result_sha256=sha))

    def test_14_v23_decoder_configuration_mismatch_fails(self):
        chain = build_chain()
        obj = copy.deepcopy(chain["v23_result"])
        obj["calibrationPackageDecoderConfigurationSha256"] = "0" * 64
        raw, sha = replace_result(obj)
        self.assert_fail(run_chain(chain, capture_manifest_v23_validation_result=raw, expected_capture_manifest_v23_validation_result_sha256=sha))

    def test_15_decoder_code_not_utf8_fails(self):
        chain = build_chain()
        self.assert_fail(run_chain(chain, decoder_code=b"\xff\xfe"))

    def test_16_decoder_code_sha_mismatch_fails_before_execution(self):
        chain = build_chain()
        result = run_chain(chain, decoder_code=chain["decoder_code"] + b"\n# changed")
        self.assert_fail(result)
        self.assertIn("DECODER_CODE_SHA256_MISMATCH", result["errors"])
        self.assertEqual(result["verifiedReplayCount"], 0)

    def test_17_decoder_configuration_sha_mismatch_fails_before_execution(self):
        chain = build_chain()
        result = run_chain(chain, decoder_configuration=chain["decoder_config"] + b" ")
        self.assert_fail(result)
        self.assertIn("DECODER_CONFIGURATION_SHA256_MISMATCH", result["errors"])
        self.assertEqual(result["verifiedReplayCount"], 0)

    def test_18_binding_nonobject_or_contract_mismatch_fails(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"] = "bad"
        self.assert_fail(run_chain(chain, replay_attempts=attempts))
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"]["contract"] = "wrong"
        attempts[0]["expectedStructuralAuditInputsSha256"] = _sha(_render(attempts[0]["structuralAuditInputs"]))
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_19_binding_canonical_sha_mismatch_fails(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"]["category"] = "changed"
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_20_binding_not_in_v23_or_completeness_set_fails(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"]["attemptId"] = "not-admitted"
        attempts[0]["expectedStructuralAuditInputsSha256"] = _sha(_render(attempts[0]["structuralAuditInputs"]))
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_21_binding_package_sha_mismatch_fails(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"]["calibrationPackageBindingSha256"] = "0" * 64
        attempts[0]["expectedStructuralAuditInputsSha256"] = _sha(_render(attempts[0]["structuralAuditInputs"]))
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_22_binding_derivation_configuration_sha_mismatch_fails(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["structuralAuditInputs"]["derivationConfigurationSha256"] = "0" * 64
        attempts[0]["expectedStructuralAuditInputsSha256"] = _sha(_render(attempts[0]["structuralAuditInputs"]))
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_23_malformed_raw_or_output_sha_identity_fails(self):
        for field in ("pitchEvidenceSha256", "birthEvidenceSha256", "pitchLatchStreamSha256", "birthStreamSha256"):
            with self.subTest(field=field):
                chain = build_chain()
                attempts = copy.deepcopy(chain["replay_attempts"])
                attempts[0]["structuralAuditInputs"][field] = "bad"
                attempts[0]["expectedStructuralAuditInputsSha256"] = _sha(_render(attempts[0]["structuralAuditInputs"]))
                self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_24_raw_pitch_evidence_sha_mismatch_fails_before_execution(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["pitchEvidence"] += b"changed"
        result = run_chain(chain, replay_attempts=attempts)
        self.assert_fail(result)
        self.assertEqual(result["verifiedReplayCount"], 0)

    def test_25_raw_birth_evidence_sha_mismatch_fails_before_execution(self):
        chain = build_chain()
        attempts = copy.deepcopy(chain["replay_attempts"])
        attempts[0]["birthEvidence"] += b"changed"
        result = run_chain(chain, replay_attempts=attempts)
        self.assert_fail(result)
        self.assertEqual(result["verifiedReplayCount"], 0)

    def test_26_missing_admitted_replay_fails(self):
        chain = build_chain(2)
        self.assert_fail(run_chain(chain, replay_attempts=chain["replay_attempts"][:1]))

    def test_27_extra_nonadmitted_replay_fails(self):
        chain = build_chain(1)
        attempts = copy.deepcopy(chain["replay_attempts"])
        extra = copy.deepcopy(attempts[0])
        extra["structuralAuditInputs"]["attemptId"] = "extra"
        extra["expectedStructuralAuditInputsSha256"] = _sha(_render(extra["structuralAuditInputs"]))
        attempts.append(extra)
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_28_duplicate_replay_attempt_or_key_fails(self):
        chain = build_chain(2)
        attempts = [copy.deepcopy(chain["replay_attempts"][0]), copy.deepcopy(chain["replay_attempts"][0])]
        self.assert_fail(run_chain(chain, replay_attempts=attempts))

    def test_29_replay_count_mismatch_fails(self):
        chain = build_chain(2)
        result = run_chain(chain, replay_attempts=[])
        self.assert_fail(result)
        self.assertTrue(any("REPLAY_ATTEMPT_COUNT_MISMATCH" in e for e in result["errors"]))

    def test_30_decoder_nonzero_exit_fails(self):
        chain = build_chain(2, decoder_variant="nonzero")
        result = run_chain(chain)
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("DECODER_NONZERO_EXIT") for e in result["errors"]))

    def test_31_decoder_timeout_fails(self):
        chain = build_chain(1, decoder_variant="timeout")
        original = module.DECODER_TIMEOUT_SECONDS
        module.DECODER_TIMEOUT_SECONDS = 0.05
        try:
            result = run_chain(chain)
        finally:
            module.DECODER_TIMEOUT_SECONDS = original
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("DECODER_TIMEOUT") for e in result["errors"]))

    def test_32_decoder_missing_pitch_latch_output_fails(self):
        result = run_chain(build_chain(1, decoder_variant="missing-pitch"))
        self.assert_fail(result)
        self.assertTrue(any("PITCH_LATCH_OUTPUT_MISSING" in e for e in result["errors"]))

    def test_33_decoder_missing_birth_output_fails(self):
        result = run_chain(build_chain(1, decoder_variant="missing-birth"))
        self.assert_fail(result)
        self.assertTrue(any("BIRTH_OUTPUT_MISSING" in e for e in result["errors"]))

    def test_34_replayed_pitch_latch_sha_mismatch_and_exact_byte_semantics_fail(self):
        result = run_chain(build_chain(1, decoder_variant="bad-pitch"))
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("REPLAYED_PITCH_LATCH_SHA256_MISMATCH") for e in result["errors"]))

    def test_35_replayed_birth_sha_mismatch_fails(self):
        result = run_chain(build_chain(1, decoder_variant="bad-birth"))
        self.assert_fail(result)
        self.assertTrue(any(e.startswith("REPLAYED_BIRTH_SHA256_MISMATCH") for e in result["errors"]))

    def test_36_population_sha_changes_with_valid_raw_identity_and_completeness_bytes(self):
        a_chain = build_chain(2, raw_salt="A")
        b_chain = build_chain(2, raw_salt="B")
        a = run_chain(a_chain)
        b = run_chain(b_chain)
        self.assertTrue(a["contractValid"] and b["contractValid"])
        self.assertNotEqual(a["populationDerivationReplaySha256"], b["populationDerivationReplaySha256"])

        c_chain = build_chain(2, raw_salt="A")
        c_obj = copy.deepcopy(c_chain["completeness_result"])
        c_obj["syntheticReplayDiagnostic"] = "harmless-result-byte-change"
        c_raw, c_sha = replace_result(c_obj)
        c = run_chain(
            c_chain,
            structural_population_completeness_result=c_raw,
            expected_structural_population_completeness_result_sha256=c_sha,
        )
        self.assertTrue(c["contractValid"], c)
        self.assertNotEqual(a["populationDerivationReplaySha256"], c["populationDerivationReplaySha256"])

    def test_37_attempt_order_invariance_and_canonical_determinism(self):
        chain = build_chain(2)
        a = run_chain(chain)
        b = run_chain(chain, replay_attempts=list(reversed(chain["replay_attempts"])))
        c = run_chain(chain)
        self.assertTrue(a["contractValid"] and b["contractValid"] and c["contractValid"])
        self.assertEqual(a["populationDerivationReplaySha256"], b["populationDerivationReplaySha256"])
        self.assertEqual(module.canonical_json_bytes(a), module.canonical_json_bytes(c))

    def test_38_authorization_remains_closed_on_pass(self):
        result = run_chain(build_chain(2))
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
