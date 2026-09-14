#!/usr/bin/env python3
"""Synthetic-only tests for purpose-built capture-manifest V2.1."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "purpose_built_capture_manifest_contract_v2_1.py"
V2_TEST_PATH = HERE / "test_purpose_built_capture_manifest_contract_v2.py"

spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_contract_v2_1", MODULE_PATH
)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

fixture_spec = importlib.util.spec_from_file_location(
    "test_purpose_built_capture_manifest_contract_v2_fixture", V2_TEST_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def valid_manifest() -> dict:
    manifest = fixture.valid_manifest()
    manifest["contract"] = module.CONTRACT
    return manifest


def test_same_slot_failed_attempt_and_retry_share_identity() -> None:
    result = module.validate_manifest(valid_manifest())
    assert result["contractValid"] is True, result
    assert result["identitySemanticsVersion"] == (
        "same-slot-retry-continuity-cross-slot-unique-v1"
    )
    assert result["admittedUnderlyingPerformanceCount"] == 1
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["correctnessAuthorized"] is False


def test_underlying_identity_change_within_slot_is_rejected() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["underlyingPerformanceId"] = "performance-changed"
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any(
        error.startswith("UNDERLYING_PERFORMANCE_ID_CHANGED_WITHIN_SLOT:slot-1:")
        for error in result["errors"]
    )
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False


def test_same_underlying_identity_across_distinct_slots_is_rejected() -> None:
    manifest = valid_manifest()
    second = copy.deepcopy(manifest["attempts"][1])
    second["attemptId"] = "slot-2-attempt-1"
    second["slotId"] = "slot-2"
    second["playerId"] = "P02"
    second["exerciseId"] = "EX02"
    second["attemptNumber"] = 1
    second["capturedAtUtc"] = "2026-09-14T20:03:00Z"
    second["evaluatedAudio"] = {
        "path": "audio/slot-2.wav",
        "sha256": "6" * 64,
    }
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
    assert result["contractValid"] is False
    assert any(
        error.startswith(
            "DUPLICATE_UNDERLYING_PERFORMANCE_ID_ACROSS_SLOTS:performance-1:"
        )
        for error in result["errors"]
    )
    assert result["admittedUnderlyingPerformanceCount"] == 1


def test_v2_fail_closed_correctness_boundary_is_preserved() -> None:
    manifest = valid_manifest()
    manifest["policyBoundary"]["modelValidationComplete"] = True
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is False
    assert any(
        "POLICY_BOUNDARY_CHANGED:modelValidationComplete" in error
        for error in result["errors"]
    )
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_structural_blocker_still_prevents_advance() -> None:
    manifest = valid_manifest()
    manifest["attempts"][1]["reference"]["declaredStructuralSummary"][
        "sameKeyOverlapCount"
    ] = 1
    result = module.validate_manifest(manifest)
    assert result["contractValid"] is True, result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False
    assert result["correctnessAuthorized"] is False
