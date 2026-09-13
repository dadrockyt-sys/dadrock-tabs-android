#!/usr/bin/env python3
"""Synthetic-only tests for the purpose-built capture manifest contract."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "purpose_built_capture_manifest_contract_v1.py"
spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_contract_v1", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

A64 = "a" * 64
B64 = "b" * 64
C64 = "c" * 64
D64 = "d" * 64
E64 = "e" * 64
F64 = "f" * 64
COMMIT = "1" * 40


def valid_manifest() -> dict:
    return {
        "contract": module.CONTRACT,
        "corpus": {
            "name": "synthetic-purpose-built-contract-fixture",
            "version": "v1",
            "capturePreregistrationPath": "docs/checkpoints/SYNTHETIC_ONLY.md",
            "capturePreregistrationCommit": COMMIT,
            "rights": {
                "documentId": "synthetic-rights-v1",
                "documentSha256": A64,
                "productValidationUseAuthorized": True,
                "protectedSongMaterialExcluded": True,
            },
            "hardware": {
                "evaluatedAudioPathId": "magnetic-di-v1",
                "independentReferencePathId": "fret-trigger-midi-v1",
                "evaluatedAudioIndependentFromReference": True,
                "configurationSha256": B64,
                "firmwareVersion": "synthetic-fw-1",
            },
        },
        "allowedAcquisitionFailureReasons": [
            "DEVICE_DISCONNECT",
            "TRUNCATED_AUDIO",
        ],
        "attempts": [
            {
                "attemptId": "slot-1-attempt-1",
                "slotId": "slot-1",
                "playerId": "P01",
                "exerciseId": "EX01",
                "category": "singlenotes",
                "attemptNumber": 1,
                "capturedAtUtc": "2026-09-13T20:00:00Z",
                "acquisitionQa": {"status": "FAIL", "reason": "DEVICE_DISCONNECT"},
                "admitted": False,
            },
            {
                "attemptId": "slot-1-attempt-2",
                "slotId": "slot-1",
                "playerId": "P01",
                "exerciseId": "EX01",
                "category": "singlenotes",
                "attemptNumber": 2,
                "capturedAtUtc": "2026-09-13T20:02:00Z",
                "acquisitionQa": {"status": "PASS", "reason": None},
                "admitted": True,
                "evaluatedAudio": {"path": "audio/slot-1.wav", "sha256": C64},
                "reference": {
                    "path": "reference/slot-1.mid",
                    "sha256": D64,
                    "format": "SMF1",
                    "configurationSha256": B64,
                    "calibrationId": "cal-P01-v1",
                    "derivedFromEvaluatedAudio": False,
                    "declaredStructuralSummary": {
                        "pairedEventCount": 125,
                        "unmatchedNoteOnCount": 0,
                        "unmatchedNoteOffCount": 0,
                        "sameKeyOverlapCount": 0,
                    },
                },
            },
            {
                "attemptId": "slot-2-attempt-1",
                "slotId": "slot-2",
                "playerId": "P02",
                "exerciseId": "EX02",
                "category": "chords",
                "attemptNumber": 1,
                "capturedAtUtc": "2026-09-13T20:03:00Z",
                "acquisitionQa": {"status": "PASS", "reason": ""},
                "admitted": True,
                "evaluatedAudio": {"path": "audio/slot-2.wav", "sha256": E64},
                "reference": {
                    "path": "reference/slot-2.mid",
                    "sha256": F64,
                    "format": "SMF1",
                    "configurationSha256": B64,
                    "calibrationId": "cal-P02-v1",
                    "derivedFromEvaluatedAudio": False,
                    "declaredStructuralSummary": {
                        "pairedEventCount": 75,
                        "unmatchedNoteOnCount": 0,
                        "unmatchedNoteOffCount": 0,
                        "sameKeyOverlapCount": 0,
                    },
                },
            },
        ],
        "policyBoundary": dict(module.REQUIRED_POLICY_BOUNDARY),
    }


def test_valid_manifest_is_reference_blind_and_not_correctness_authorized() -> None:
    result = module.validate_manifest(valid_manifest())
    assert result["contractValid"] is True, result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True, result
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False
    assert result["attemptStats"] == {
        "attemptCount": 3,
        "admittedCount": 2,
        "failedAcquisitionCount": 1,
    }
    assert result["declaredRawReferencePairedEventCountPlanningOnly"] == 200
    assert len(result["admittedPopulationManifestSha256"]) == 64


def test_first_transport_valid_attempt_cannot_be_replaced() -> None:
    manifest = valid_manifest()
    first = manifest["attempts"][0]
    first["acquisitionQa"] = {"status": "PASS", "reason": None}
    first["admitted"] = False
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("PASS_ATTEMPT_MUST_BE_ADMITTED" in error for error in result["errors"]), result
    assert any("ATTEMPTS_EXIST_AFTER_FIRST_ADMITTED_PASS" in error for error in result["errors"]), result


def test_post_admission_extra_take_fails_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"].append({
        "attemptId": "slot-2-attempt-2",
        "slotId": "slot-2",
        "playerId": "P02",
        "exerciseId": "EX02",
        "category": "chords",
        "attemptNumber": 2,
        "capturedAtUtc": "2026-09-13T20:04:00Z",
        "acquisitionQa": {"status": "FAIL", "reason": "TRUNCATED_AUDIO"},
        "admitted": False,
    })
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPTS_EXIST_AFTER_FIRST_ADMITTED_PASS:slot-2" in result["errors"], result


def test_nonfrozen_failure_reason_fails_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["acquisitionQa"]["reason"] = "PLAYER_DID_NOT_LIKE_TAKE"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("FAIL_REASON_NOT_FROZEN" in error for error in result["errors"]), result


def test_declared_reference_anomaly_blocks_audit_advance_without_claiming_correctness() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["declaredStructuralSummary"]["sameKeyOverlapCount"] = 1
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is True, result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False, result
    assert result["declaredStructuralBlockers"] == [
        "ATTEMPT[1]_REFERENCE:sameKeyOverlapCount=1"
    ]
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["correctnessAuthorized"] is False


def test_model_or_correctness_observation_fields_are_forbidden() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["v6Class"] = "onset-birth-corroborated-candidate"
    manifest["attempts"][2]["correctness"] = {"matched": True}
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("v6Class" in error for error in result["errors"]), result
    assert any("correctness" in error for error in result["errors"]), result


def test_hardware_configuration_identity_is_frozen() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["configurationSha256"] = A64
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("REFERENCE_CONFIGURATION_MISMATCH" in error for error in result["errors"]), result


def test_policy_boundary_cannot_be_promoted() -> None:
    manifest = valid_manifest()
    manifest["policyBoundary"]["modelValidationComplete"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("POLICY_BOUNDARY_CHANGED:modelValidationComplete" in error for error in result["errors"]), result


def test_population_manifest_hash_is_order_independent() -> None:
    manifest_a = valid_manifest()
    manifest_b = copy.deepcopy(manifest_a)
    manifest_b["attempts"] = list(reversed(manifest_b["attempts"]))
    result_a = module.validate_manifest(manifest_a)
    result_b = module.validate_manifest(manifest_b)
    assert result_a["contractValid"] is True, result_a
    assert result_b["contractValid"] is True, result_b
    assert result_a["admittedPopulationManifestSha256"] == result_b["admittedPopulationManifestSha256"]


def test_non_utc_offset_timestamp_fails_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-13T21:00:00+01:00"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert any("CAPTURED_AT_UTC_INVALID" in error for error in result["errors"]), result


def test_naive_timestamp_fails_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-13T20:00:00"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert any("CAPTURED_AT_UTC_INVALID" in error for error in result["errors"]), result


def test_explicit_zero_offset_timestamp_is_accepted() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-13T20:00:00+00:00"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is True, result


def test_noncontiguous_attempt_numbers_fail_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["attemptNumber"] = 3
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert "NONCONTIGUOUS_ATTEMPT_NUMBERS_IN_SLOT:slot-1:1,3" in result["errors"], result


def test_reversed_attempt_timestamps_fail_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-13T20:03:00Z"
    manifest["attempts"][1]["capturedAtUtc"] = "2026-09-13T20:02:00Z"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert (
        "ATTEMPT_TIMESTAMPS_NOT_STRICTLY_INCREASING:slot-1:"
        "slot-1-attempt-1->slot-1-attempt-2"
    ) in result["errors"], result


def test_equal_attempt_timestamps_fail_contract() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-13T20:02:00Z"
    manifest["attempts"][1]["capturedAtUtc"] = "2026-09-13T20:02:00Z"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert (
        "ATTEMPT_TIMESTAMPS_NOT_STRICTLY_INCREASING:slot-1:"
        "slot-1-attempt-1->slot-1-attempt-2"
    ) in result["errors"], result


def main() -> int:
    test_valid_manifest_is_reference_blind_and_not_correctness_authorized()
    test_first_transport_valid_attempt_cannot_be_replaced()
    test_post_admission_extra_take_fails_contract()
    test_nonfrozen_failure_reason_fails_contract()
    test_declared_reference_anomaly_blocks_audit_advance_without_claiming_correctness()
    test_model_or_correctness_observation_fields_are_forbidden()
    test_hardware_configuration_identity_is_frozen()
    test_policy_boundary_cannot_be_promoted()
    test_population_manifest_hash_is_order_independent()
    test_non_utc_offset_timestamp_fails_contract()
    test_naive_timestamp_fails_contract()
    test_explicit_zero_offset_timestamp_is_accepted()
    test_noncontiguous_attempt_numbers_fail_contract()
    test_reversed_attempt_timestamps_fail_contract()
    test_equal_attempt_timestamps_fail_contract()
    print("PURPOSE_BUILT_CAPTURE_MANIFEST_CONTRACT_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
