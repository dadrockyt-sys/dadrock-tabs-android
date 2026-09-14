#!/usr/bin/env python3
"""Synthetic-only tests for purpose-built capture preregistration binding."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent

BINDING_PATH = HERE / "purpose_built_capture_preregistration_binding_v1.py"
binding_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_binding_v1", BINDING_PATH
)
assert binding_spec and binding_spec.loader
binding = importlib.util.module_from_spec(binding_spec)
binding_spec.loader.exec_module(binding)

FIXTURE_PATH = HERE / "test_purpose_built_capture_manifest_contract_v1.py"
fixture_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_manifest_fixture", FIXTURE_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def valid_plan() -> dict:
    return {
        "contract": binding.PLAN_CONTRACT,
        "capturePreregistrationPath": "docs/checkpoints/SYNTHETIC_ONLY.md",
        "capturePreregistrationCommit": fixture.COMMIT,
        "allowedAcquisitionFailureReasons": [
            "DEVICE_DISCONNECT",
            "TRUNCATED_AUDIO",
        ],
        "plannedSlots": [
            {
                "slotId": "slot-1",
                "playerId": "P01",
                "exerciseId": "EX01",
                "category": "singlenotes",
            },
            {
                "slotId": "slot-2",
                "playerId": "P02",
                "exerciseId": "EX02",
                "category": "chords",
            },
        ],
    }


def bound_manifest(plan: dict | None = None) -> tuple[dict, dict]:
    plan = copy.deepcopy(plan or valid_plan())
    manifest = fixture.valid_manifest()
    manifest["corpus"]["capturePlanPath"] = "docs/checkpoints/SYNTHETIC_CAPTURE_PLAN.json"
    manifest["corpus"]["capturePlanSha256"] = binding.base.sha256_bytes(
        binding.base.canonical_json(plan).encode("utf-8")
    )
    return manifest, plan


def test_valid_binding_allows_only_reference_blind_structural_audit() -> None:
    manifest, plan = bound_manifest()
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is True, result
    assert result["errors"] == [], result
    assert result["plannedSlotCount"] == 2
    assert result["capturedSlotCount"] == 2
    assert result["failureReasonVocabularyBound"] is True
    assert result["slotRosterExactlyBound"] is True
    assert result["manifestSemanticGuardPassed"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_manifest_cannot_choose_new_failure_reason_after_preregistration() -> None:
    manifest, plan = bound_manifest()
    manifest["allowedAcquisitionFailureReasons"].append("PLAYER_DID_NOT_LIKE_TAKE")
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert any("CAPTURE_PLAN_FAILURE_REASONS_MISMATCH" in error for error in result["errors"]), result


def test_preregistered_slot_cannot_be_silently_omitted() -> None:
    manifest, plan = bound_manifest()
    manifest["attempts"] = [row for row in manifest["attempts"] if row["slotId"] != "slot-2"]
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert "CAPTURE_PLAN_SLOT_MISSING_FROM_MANIFEST:slot-2" in result["errors"], result


def test_unplanned_extra_slot_cannot_be_added() -> None:
    manifest, plan = bound_manifest()
    extra = copy.deepcopy(manifest["attempts"][2])
    extra["attemptId"] = "slot-3-attempt-1"
    extra["slotId"] = "slot-3"
    extra["playerId"] = "P03"
    extra["exerciseId"] = "EX03"
    extra["attemptNumber"] = 1
    extra["capturedAtUtc"] = "2026-09-13T20:05:00Z"
    extra["evaluatedAudio"]["path"] = "audio/slot-3.wav"
    extra["evaluatedAudio"]["sha256"] = "2" * 64
    extra["reference"]["path"] = "reference/slot-3.mid"
    extra["reference"]["sha256"] = "3" * 64
    manifest["attempts"].append(extra)
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert "MANIFEST_SLOT_NOT_IN_CAPTURE_PLAN:slot-3" in result["errors"], result


def test_slot_identity_must_match_frozen_plan() -> None:
    manifest, plan = bound_manifest()
    plan["plannedSlots"][1]["exerciseId"] = "EX-FROZEN-DIFFERENT"
    manifest["corpus"]["capturePlanSha256"] = binding.base.sha256_bytes(
        binding.base.canonical_json(plan).encode("utf-8")
    )
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert any(
        error.startswith("CAPTURE_PLAN_SLOT_IDENTITY_MISMATCH:slot-2:exerciseId:")
        for error in result["errors"]
    ), result


def test_capture_plan_hash_is_immutable_binding() -> None:
    manifest, plan = bound_manifest()
    plan["plannedSlots"][0]["playerId"] = "P99"
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert any("CAPTURE_PLAN_SHA256_MISMATCH" in error for error in result["errors"]), result


def test_preregistration_commit_must_match_manifest() -> None:
    manifest, plan = bound_manifest()
    plan["capturePreregistrationCommit"] = "2" * 40
    manifest["corpus"]["capturePlanSha256"] = binding.base.sha256_bytes(
        binding.base.canonical_json(plan).encode("utf-8")
    )
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert "CAPTURE_PLAN_PREREGISTRATION_COMMIT_MISMATCH" in result["errors"], result


def test_preregistration_path_must_match_manifest() -> None:
    manifest, plan = bound_manifest()
    plan["capturePreregistrationPath"] = "docs/checkpoints/OTHER.md"
    manifest["corpus"]["capturePlanSha256"] = binding.base.sha256_bytes(
        binding.base.canonical_json(plan).encode("utf-8")
    )
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert "CAPTURE_PLAN_PREREGISTRATION_PATH_MISMATCH" in result["errors"], result


def test_duplicate_plan_slot_id_is_rejected() -> None:
    plan = valid_plan()
    plan["plannedSlots"].append(copy.deepcopy(plan["plannedSlots"][0]))
    manifest, plan = bound_manifest(plan)
    result = binding.validate_binding(manifest, plan)
    assert result["bindingValid"] is False, result
    assert "CAPTURE_PLAN_DUPLICATE_SLOT_ID:slot-1" in result["errors"], result


def main() -> int:
    test_valid_binding_allows_only_reference_blind_structural_audit()
    test_manifest_cannot_choose_new_failure_reason_after_preregistration()
    test_preregistered_slot_cannot_be_silently_omitted()
    test_unplanned_extra_slot_cannot_be_added()
    test_slot_identity_must_match_frozen_plan()
    test_capture_plan_hash_is_immutable_binding()
    test_preregistration_commit_must_match_manifest()
    test_preregistration_path_must_match_manifest()
    test_duplicate_plan_slot_id_is_rejected()
    print("PURPOSE_BUILT_CAPTURE_PREREGISTRATION_BINDING_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
