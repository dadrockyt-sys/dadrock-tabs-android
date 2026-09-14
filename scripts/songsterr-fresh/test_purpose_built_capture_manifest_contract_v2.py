#!/usr/bin/env python3
"""Synthetic-only tests for the purpose-built V2 capture manifest contract."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "purpose_built_capture_manifest_contract_v2.py"
spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_contract_v2", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

A64 = "a" * 64
B64 = "b" * 64
C64 = "c" * 64
D64 = "d" * 64
E64 = "e" * 64
F64 = "f" * 64
G64 = "0" * 64
H64 = "1" * 64
I64 = "2" * 64
J64 = "3" * 64
K64 = "4" * 64
COMMIT = "5" * 40


def valid_manifest() -> dict:
    return {
        "contract": module.CONTRACT,
        "corpus": {
            "name": "synthetic-purpose-built-v2",
            "version": "v2",
            "capturePreregistrationPath": "docs/checkpoints/SYNTHETIC_V2_ONLY.md",
            "capturePreregistrationCommit": COMMIT,
            "rights": {
                "documentId": "synthetic-rights-v2",
                "documentSha256": A64,
                "productValidationUseAuthorized": True,
                "protectedSongMaterialExcluded": True,
            },
            "hardware": {
                "evaluatedAudioPathId": "magnetic-di-v1",
                "pitchEvidencePathId": "physical-fret-position-v1",
                "birthEvidencePathId": "independent-trigger-v1",
                "evaluatedAudioIndependentFromPitchEvidence": True,
                "evaluatedAudioIndependentFromBirthEvidence": True,
                "configuration": {
                    "contract": module.HARDWARE_CONTRACT,
                    "configurationId": "hw-config-v1",
                    "path": "config/hardware-v1.json",
                    "sha256": B64,
                    "firmwareVersion": "synthetic-fw-2",
                },
                "instrumentSetup": {
                    "setupSha256": C64,
                    "openStringMidi": [40, 45, 50, 55, 59, 64],
                },
            },
            "referenceCalibration": {
                "contract": module.CALIBRATION_CONTRACT,
                "calibrationId": "calibration-v1",
                "path": "calibration/reference-v1.json",
                "sha256": D64,
                "usedHoldoutData": False,
                "usedModelOutputs": False,
                "derivedFromEvaluatedAudio": False,
                "maxAbsoluteOnsetErrorSeconds": 0.010,
            },
            "clockSync": {
                "syncId": "sync-v1",
                "sourceId": "hardware-clock-v1",
                "path": "sync/sync-v1.json",
                "sha256": E64,
                "derivedFromEvaluatedAudio": False,
                "usedModelOutputs": False,
                "maxAbsoluteErrorSeconds": 0.005,
            },
        },
        "allowedAcquisitionFailureReasons": [
            "DEVICE_DISCONNECT",
            "REFERENCE_SENSOR_DROPOUT",
        ],
        "attempts": [
            {
                "attemptId": "slot-1-attempt-1",
                "slotId": "slot-1",
                "underlyingPerformanceId": "performance-1",
                "playerId": "P01",
                "exerciseId": "EX01",
                "category": "singlenotes",
                "attemptNumber": 1,
                "capturedAtUtc": "2026-09-14T20:00:00Z",
                "acquisitionQa": {
                    "status": "FAIL",
                    "reason": "DEVICE_DISCONNECT",
                    "evidence": {
                        "machineVerifiable": True,
                        "evidenceType": "device-link-state",
                        "path": "qa/slot-1-attempt-1.json",
                        "sha256": F64,
                        "derivedFromEvaluatedAudioCorrectness": False,
                        "usedModelOutputs": False,
                    },
                },
                "admitted": False,
            },
            {
                "attemptId": "slot-1-attempt-2",
                "slotId": "slot-1",
                "underlyingPerformanceId": "performance-1",
                "playerId": "P01",
                "exerciseId": "EX01",
                "category": "singlenotes",
                "attemptNumber": 2,
                "capturedAtUtc": "2026-09-14T20:02:00Z",
                "acquisitionQa": {"status": "PASS", "reason": None},
                "admitted": True,
                "evaluatedAudio": {"path": "audio/slot-1.wav", "sha256": G64},
                "pitchEvidence": {
                    "path": "pitch/slot-1.bin",
                    "sha256": H64,
                    "derivedFromEvaluatedAudio": False,
                },
                "birthEvidence": {
                    "path": "birth/slot-1.bin",
                    "sha256": I64,
                    "derivedFromEvaluatedAudio": False,
                },
                "reference": {
                    "path": "reference/slot-1.json",
                    "sha256": J64,
                    "format": "purpose-built-note-events-v1",
                    "configurationSha256": B64,
                    "calibrationId": "calibration-v1",
                    "clockSyncId": "sync-v1",
                    "derivedFromEvaluatedAudio": False,
                    "pitchDerivedFromEvaluatedAudio": False,
                    "birthDerivedFromEvaluatedAudio": False,
                    "usedModelOutputs": False,
                    "pitchEvidenceSha256": H64,
                    "birthEvidenceSha256": I64,
                    "derivationConfigurationSha256": K64,
                    "eventSemanticsVersion": "physical-reference-semantics-v1",
                    "declaredStructuralSummary": {
                        "pairedEventCount": 100,
                        "unmatchedNoteOnCount": 0,
                        "unmatchedNoteOffCount": 0,
                        "sameKeyOverlapCount": 0,
                    },
                },
            },
        ],
        "policyBoundary": dict(module.v1.REQUIRED_POLICY_BOUNDARY),
    }


def test_valid_manifest_passes_but_remains_fail_closed_for_correctness() -> None:
    result = module.validate_manifest(valid_manifest())
    assert result["contractValid"] is True, result
    assert result["v2SemanticGuardPassed"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["admittedUnderlyingPerformanceCount"] == 1
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_first_pass_rule_is_inherited_from_v1() -> None:
    manifest = valid_manifest()
    manifest["attempts"][0]["acquisitionQa"] = {"status": "PASS", "reason": None}
    manifest["attempts"][0]["admitted"] = False
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("PASS_ATTEMPT_MUST_BE_ADMITTED" in error for error in result["errors"])


def test_pitch_reference_cannot_be_audio_derived() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["pitchEvidence"]["derivedFromEvaluatedAudio"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("PITCH_EVIDENCE_MUST_DECLARE_NOT_DERIVED" in error for error in result["errors"])


def test_birth_reference_cannot_be_audio_derived() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["birthEvidence"]["derivedFromEvaluatedAudio"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("BIRTH_EVIDENCE_MUST_DECLARE_NOT_DERIVED" in error for error in result["errors"])


def test_calibration_cannot_use_holdout() -> None:
    manifest = valid_manifest()
    manifest["corpus"]["referenceCalibration"]["usedHoldoutData"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "REFERENCE_CALIBRATION_MUST_NOT_USE_HOLDOUT_DATA" in result["errors"]


def test_calibration_cannot_use_model_outputs() -> None:
    manifest = valid_manifest()
    manifest["corpus"]["referenceCalibration"]["usedModelOutputs"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "REFERENCE_CALIBRATION_MUST_NOT_USE_MODEL_OUTPUTS" in result["errors"]


def test_calibration_timing_error_bound_is_enforced() -> None:
    manifest = valid_manifest()
    manifest["corpus"]["referenceCalibration"]["maxAbsoluteOnsetErrorSeconds"] = 0.026
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("REFERENCE_CALIBRATION_TIMING_ERROR_EXCEEDS_BOUND" in error for error in result["errors"])


def test_clock_sync_proof_is_required() -> None:
    manifest = valid_manifest()
    del manifest["corpus"]["clockSync"]
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "CLOCK_SYNC_OBJECT_REQUIRED" in result["errors"]


def test_clock_sync_cannot_be_audio_derived() -> None:
    manifest = valid_manifest()
    manifest["corpus"]["clockSync"]["derivedFromEvaluatedAudio"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "CLOCK_SYNC_MUST_NOT_BE_DERIVED_FROM_EVALUATED_AUDIO" in result["errors"]


def test_clock_sync_error_bound_is_enforced() -> None:
    manifest = valid_manifest()
    manifest["corpus"]["clockSync"]["maxAbsoluteErrorSeconds"] = 0.030
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("CLOCK_SYNC_ERROR_EXCEEDS_BOUND" in error for error in result["errors"])


def test_failed_attempt_requires_machine_verifiable_evidence() -> None:
    manifest = valid_manifest()
    del manifest["attempts"][0]["acquisitionQa"]["evidence"]
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[0]_FAILURE_EVIDENCE_OBJECT_REQUIRED" in result["errors"]


def test_pass_attempt_cannot_carry_failure_evidence() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["acquisitionQa"]["evidence"] = copy.deepcopy(
        manifest["attempts"][0]["acquisitionQa"]["evidence"]
    )
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_PASS_MUST_NOT_CARRY_FAILURE_EVIDENCE" in result["errors"]


def test_nonobjective_failure_reason_is_rejected() -> None:
    manifest = valid_manifest()
    manifest["allowedAcquisitionFailureReasons"].append("PLAYER_DID_NOT_LIKE_TAKE")
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ACQUISITION_FAILURE_REASON_NOT_OBJECTIVE_V2:PLAYER_DID_NOT_LIKE_TAKE" in result["errors"]


def test_failure_evidence_cannot_reference_model_outputs() -> None:
    manifest = valid_manifest()
    evidence = manifest["attempts"][0]["acquisitionQa"]["evidence"]
    evidence["usedModelOutputs"] = True
    evidence["detail"] = "Basic Pitch score was low"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("FAILURE_EVIDENCE_MUST_NOT_USE_MODEL_OUTPUTS" in error for error in result["errors"])
    assert any("FORBIDDEN_FAILURE_EVIDENCE_SEMANTIC" in error for error in result["errors"])


def test_duplicate_underlying_performance_is_rejected() -> None:
    manifest = valid_manifest()
    second = copy.deepcopy(manifest["attempts"][1])
    second["attemptId"] = "slot-2-attempt-1"
    second["slotId"] = "slot-2"
    second["playerId"] = "P02"
    second["exerciseId"] = "EX02"
    second["attemptNumber"] = 1
    second["capturedAtUtc"] = "2026-09-14T20:03:00Z"
    second["evaluatedAudio"] = {"path": "audio/slot-2.wav", "sha256": "6" * 64}
    second["pitchEvidence"] = {"path": "pitch/slot-2.bin", "sha256": "7" * 64, "derivedFromEvaluatedAudio": False}
    second["birthEvidence"] = {"path": "birth/slot-2.bin", "sha256": "8" * 64, "derivedFromEvaluatedAudio": False}
    second["reference"]["path"] = "reference/slot-2.json"
    second["reference"]["sha256"] = "9" * 64
    second["reference"]["pitchEvidenceSha256"] = "7" * 64
    second["reference"]["birthEvidenceSha256"] = "8" * 64
    manifest["attempts"].append(second)
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "DUPLICATE_UNDERLYING_PERFORMANCE_ID:performance-1" in result["errors"]


def test_underlying_performance_identity_cannot_change_between_retries() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["underlyingPerformanceId"] = "performance-changed"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_UNDERLYING_PERFORMANCE_ID_CHANGED_WITHIN_SLOT" in result["errors"]


def test_reference_must_bind_raw_pitch_hash() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["pitchEvidenceSha256"] = A64
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_REFERENCE_PITCH_EVIDENCE_HASH_MISMATCH" in result["errors"]


def test_reference_must_bind_raw_birth_hash() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["birthEvidenceSha256"] = A64
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_REFERENCE_BIRTH_EVIDENCE_HASH_MISMATCH" in result["errors"]


def test_reference_must_bind_hardware_configuration() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["configurationSha256"] = A64
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("REFERENCE_HARDWARE_CONFIGURATION_MISMATCH" in error for error in result["errors"])


def test_reference_must_bind_calibration() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["calibrationId"] = "other-calibration"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_REFERENCE_CALIBRATION_ID_MISMATCH" in result["errors"]


def test_reference_must_bind_clock_sync() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["clockSyncId"] = "other-sync"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_REFERENCE_CLOCK_SYNC_ID_MISMATCH" in result["errors"]


def test_evaluated_pitch_birth_sources_must_be_distinct() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["birthEvidence"]["path"] = manifest["attempts"][1]["pitchEvidence"]["path"]
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert "ATTEMPT[1]_AUDIO_PITCH_BIRTH_SOURCE_PATHS_MUST_BE_DISTINCT" in result["errors"]


def test_structural_declaration_blocks_advance_without_authorizing_correctness() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["declaredStructuralSummary"]["sameKeyOverlapCount"] = 1
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is True, result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False
    assert result["correctnessAuthorized"] is False


def test_policy_boundary_cannot_be_promoted() -> None:
    manifest = valid_manifest()
    manifest["policyBoundary"]["modelValidationComplete"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("POLICY_BOUNDARY_CHANGED:modelValidationComplete" in error for error in result["errors"])


def test_model_and_correctness_fields_remain_forbidden() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["v6Output"] = {"class": "candidate"}
    manifest["attempts"][1]["correctness"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any("v6Output" in error for error in result["errors"])
    assert any("correctness" in error for error in result["errors"])
