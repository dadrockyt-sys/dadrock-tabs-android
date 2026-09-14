#!/usr/bin/env python3
"""Synthetic-only tests for the purpose-built manifest semantic guard."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent

GUARD_PATH = HERE / "purpose_built_capture_manifest_semantic_guard_v1.py"
guard_spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_semantic_guard_v1", GUARD_PATH)
assert guard_spec and guard_spec.loader
guard = importlib.util.module_from_spec(guard_spec)
guard_spec.loader.exec_module(guard)

FIXTURE_PATH = HERE / "test_purpose_built_capture_manifest_contract_v1.py"
fixture_spec = importlib.util.spec_from_file_location("purpose_built_capture_manifest_fixture", FIXTURE_PATH)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def test_valid_manifest_passes_semantic_guard_without_authorizing_models() -> None:
    result = guard.validate_manifest(fixture.valid_manifest())
    assert result["contractValid"] is True, result
    assert result["semanticGuardPassed"] is True, result
    assert result["semanticGuardErrors"] == [], result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True, result
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_hardware_audio_and_reference_path_ids_must_differ() -> None:
    manifest = fixture.valid_manifest()
    hardware = manifest["corpus"]["hardware"]
    hardware["independentReferencePathId"] = hardware["evaluatedAudioPathId"]
    result = guard.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False, result
    assert "HARDWARE_AUDIO_REFERENCE_PATH_IDS_MUST_DIFFER" in result["errors"], result


def test_slot_retry_cannot_change_player_identity() -> None:
    manifest = fixture.valid_manifest()
    manifest["attempts"][1]["playerId"] = "P99"
    result = guard.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert "SLOT_IDENTITY_CHANGED:slot-1:playerId" in result["errors"], result


def test_slot_retry_cannot_change_exercise_identity() -> None:
    manifest = fixture.valid_manifest()
    manifest["attempts"][1]["exerciseId"] = "EX99"
    result = guard.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert "SLOT_IDENTITY_CHANGED:slot-1:exerciseId" in result["errors"], result


def test_slot_retry_cannot_change_category_identity() -> None:
    manifest = fixture.valid_manifest()
    manifest["attempts"][1]["category"] = "chords"
    result = guard.validate_manifest(manifest)
    assert result["contractValid"] is False, result
    assert "SLOT_IDENTITY_CHANGED:slot-1:category" in result["errors"], result


def main() -> int:
    test_valid_manifest_passes_semantic_guard_without_authorizing_models()
    test_hardware_audio_and_reference_path_ids_must_differ()
    test_slot_retry_cannot_change_player_identity()
    test_slot_retry_cannot_change_exercise_identity()
    test_slot_retry_cannot_change_category_identity()
    print("PURPOSE_BUILT_CAPTURE_MANIFEST_SEMANTIC_GUARD_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
