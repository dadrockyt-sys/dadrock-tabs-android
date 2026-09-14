#!/usr/bin/env python3
"""Synthetic-only tests for preregistration server integrity guard."""

from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

GUARD_PATH = HERE / "purpose_built_capture_preregistration_server_integrity_guard_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_integrity_guard_v1", GUARD_PATH
)
assert spec and spec.loader
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)

SERVER_TEST_PATH = HERE / "test_purpose_built_capture_preregistration_server_proof_v1.py"
fixture_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_proof_fixture", SERVER_TEST_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def validate(manifest: dict, plan: dict, metadata: dict) -> dict:
    return guard.validate_server_integrity(
        manifest,
        plan,
        metadata,
        repo_root=REPO_ROOT,
        expected_repository=fixture.REPOSITORY,
        expected_run_id=fixture.RUN_ID,
        allow_synthetic_fixture_for_tests=True,
    )


def test_frozen_hardened_blobs_pass_integrity_guard() -> None:
    manifest, plan = fixture.fixture.valid_git_bound_inputs()
    result = validate(manifest, plan, fixture.valid_run_metadata())
    assert result["serverIntegrityValid"] is True, result
    assert result["baseServerProofValid"] is True
    assert result["attestationWorkflowBlob"] == guard.FROZEN_ATTESTATION_WORKFLOW_BLOB
    assert result["attestationWorkflowBlobFrozen"] is True
    assert result["attestationGeneratorBlob"] == guard.FROZEN_ATTESTATION_GENERATOR_BLOB
    assert result["attestationGeneratorBlobFrozen"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["correctnessAuthorized"] is False


def test_descendant_workflow_tampering_fails_closed() -> None:
    manifest, plan = fixture.fixture.valid_git_bound_inputs()
    original = guard._blob_at
    try:
        def fake_blob(root: Path, commit: str, path: str) -> str | None:
            if path == guard.server.ATTESTATION_WORKFLOW_PATH:
                return "0" * 40
            return original(root, commit, path)

        guard._blob_at = fake_blob
        result = validate(manifest, plan, fixture.valid_run_metadata())
    finally:
        guard._blob_at = original
    assert result["serverIntegrityValid"] is False, result
    assert result["baseServerProofValid"] is True
    assert result["attestationWorkflowBlobFrozen"] is False
    assert any("ATTESTATION_WORKFLOW_BLOB_NOT_FROZEN" in error for error in result["errors"])
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False


def test_descendant_generator_tampering_fails_closed() -> None:
    manifest, plan = fixture.fixture.valid_git_bound_inputs()
    original = guard._blob_at
    try:
        def fake_blob(root: Path, commit: str, path: str) -> str | None:
            if path == guard.ATTESTATION_GENERATOR_PATH:
                return "f" * 40
            return original(root, commit, path)

        guard._blob_at = fake_blob
        result = validate(manifest, plan, fixture.valid_run_metadata())
    finally:
        guard._blob_at = original
    assert result["serverIntegrityValid"] is False, result
    assert result["baseServerProofValid"] is True
    assert result["attestationGeneratorBlobFrozen"] is False
    assert any("ATTESTATION_GENERATOR_BLOB_NOT_FROZEN" in error for error in result["errors"])
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False


def test_base_server_failure_cannot_be_rescued_by_frozen_blobs() -> None:
    manifest, plan = fixture.fixture.valid_git_bound_inputs()
    metadata = fixture.valid_run_metadata()
    metadata["event"] = "push"
    result = validate(manifest, plan, metadata)
    assert result["serverIntegrityValid"] is False, result
    assert result["baseServerProofValid"] is False
    assert result["attestationWorkflowBlobFrozen"] is True
    assert result["attestationGeneratorBlobFrozen"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False


def main() -> int:
    test_frozen_hardened_blobs_pass_integrity_guard()
    test_descendant_workflow_tampering_fails_closed()
    test_descendant_generator_tampering_fails_closed()
    test_base_server_failure_cannot_be_rescued_by_frozen_blobs()
    print("PURPOSE_BUILT_PREREGISTRATION_SERVER_INTEGRITY_GUARD_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
