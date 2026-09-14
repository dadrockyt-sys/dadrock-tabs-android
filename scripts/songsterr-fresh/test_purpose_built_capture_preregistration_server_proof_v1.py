#!/usr/bin/env python3
"""Synthetic-only tests for GitHub-server preregistration proof semantics."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

SERVER_PATH = HERE / "purpose_built_capture_preregistration_server_proof_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_proof_v1", SERVER_PATH
)
assert spec and spec.loader
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)

GIT_PROOF_TEST_PATH = HERE / "test_purpose_built_capture_preregistration_git_proof_v1.py"
fixture_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_git_proof_fixture", GIT_PROOF_TEST_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)

REPOSITORY = "dadrockyt-sys/dadrock-tabs-android"
RUN_ID = "999999001"
ATTESTATION_HEAD = "933b20b1bd70761717645ab3c7c6b15b1721a7eb"


def valid_run_metadata() -> dict:
    return {
        "id": int(RUN_ID),
        "name": "Songsterr Purpose-Built Preregistration Attestation",
        "head_branch": server.CANONICAL_BRANCH,
        "head_sha": ATTESTATION_HEAD,
        "path": server.ATTESTATION_WORKFLOW_PATH,
        "event": "workflow_dispatch",
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-09-14T00:26:49Z",
        "run_started_at": "2026-09-14T00:26:50Z",
        "updated_at": "2026-09-14T00:27:03Z",
        "repository": {"full_name": REPOSITORY},
    }


def validate(manifest: dict, plan: dict, metadata: dict) -> dict:
    return server.validate_server_proof(
        manifest,
        plan,
        metadata,
        repo_root=REPO_ROOT,
        expected_repository=REPOSITORY,
        expected_run_id=RUN_ID,
    )


def test_valid_dispatched_server_attestation_allows_only_structural_audit() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    result = validate(manifest, plan, valid_run_metadata())
    assert result["serverProofValid"] is True, result
    assert result["errors"] == [], result
    assert result["localGitProofValid"] is True
    assert result["githubRunEventWorkflowDispatch"] is True
    assert result["githubRunCompletedSuccessfully"] is True
    assert result["preregistrationCommitIsAncestorOfAttestationHead"] is True
    assert result["attestationHeadIsAncestorOfCurrentHead"] is True
    assert result["attestationHeadPlanMatches"] is True
    assert result["attestationHeadEvidenceMatches"] is True
    assert result["attestationWorkflowPresentAtRunHead"] is True
    assert result["allCaptureTimestampsAfterServerAttestation"] is True
    assert result["githubServerPreregistrationEstablished"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_push_run_is_never_real_preregistration() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["event"] = "push"
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert "GITHUB_RUN_EVENT_NOT_WORKFLOW_DISPATCH:'push'" in result["errors"], result


def test_failed_or_incomplete_run_is_rejected() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["status"] = "completed"
    metadata["conclusion"] = "failure"
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert "GITHUB_RUN_CONCLUSION_NOT_SUCCESS:'failure'" in result["errors"], result


def test_wrong_repository_is_rejected() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["repository"] = {"full_name": "other/repository"}
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert any("GITHUB_RUN_REPOSITORY_MISMATCH" in error for error in result["errors"]), result


def test_wrong_workflow_path_is_rejected() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["path"] = ".github/workflows/unrelated.yml"
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert any("GITHUB_RUN_WORKFLOW_PATH_MISMATCH" in error for error in result["errors"]), result


def test_attestation_must_complete_before_every_capture() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-09-14T00:26:55Z"
    manifest["attempts"][1]["capturedAtUtc"] = "2026-09-14T00:26:57Z"
    manifest["attempts"][2]["capturedAtUtc"] = "2026-09-14T00:26:59Z"
    result = validate(manifest, plan, valid_run_metadata())
    assert result["serverProofValid"] is False, result
    assert any(
        "CAPTURE_TIMESTAMP_NOT_AFTER_GITHUB_ATTESTATION_COMPLETION" in error
        for error in result["errors"]
    ), result
    assert result["allCaptureTimestampsAfterServerAttestation"] is False


def test_attestation_head_must_descend_from_preregistration_commit() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["head_sha"] = fixture.PLAN_ONLY_COMMIT
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert "PREREGISTRATION_COMMIT_NOT_ANCESTOR_OF_ATTESTATION_HEAD" in result["errors"], result


def test_run_id_must_match_cited_run() -> None:
    manifest, plan = fixture.valid_git_bound_inputs()
    metadata = valid_run_metadata()
    metadata["id"] = 123
    result = validate(manifest, plan, metadata)
    assert result["serverProofValid"] is False, result
    assert any("GITHUB_RUN_ID_MISMATCH" in error for error in result["errors"]), result


def main() -> int:
    test_valid_dispatched_server_attestation_allows_only_structural_audit()
    test_push_run_is_never_real_preregistration()
    test_failed_or_incomplete_run_is_rejected()
    test_wrong_repository_is_rejected()
    test_wrong_workflow_path_is_rejected()
    test_attestation_must_complete_before_every_capture()
    test_attestation_head_must_descend_from_preregistration_commit()
    test_run_id_must_match_cited_run()
    print("PURPOSE_BUILT_PREREGISTRATION_SERVER_PROOF_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
