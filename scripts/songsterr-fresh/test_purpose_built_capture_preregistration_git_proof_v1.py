#!/usr/bin/env python3
"""Synthetic-only tests for the purpose-built preregistration Git proof."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

PROOF_PATH = HERE / "purpose_built_capture_preregistration_git_proof_v1.py"
proof_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_git_proof_v1", PROOF_PATH
)
assert proof_spec and proof_spec.loader
proof = importlib.util.module_from_spec(proof_spec)
proof_spec.loader.exec_module(proof)

BINDING_TEST_PATH = HERE / "test_purpose_built_capture_preregistration_binding_v1.py"
binding_test_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_binding_fixture", BINDING_TEST_PATH
)
assert binding_test_spec and binding_test_spec.loader
binding_fixture = importlib.util.module_from_spec(binding_test_spec)
binding_test_spec.loader.exec_module(binding_fixture)

PREREG_COMMIT = "617706bc6a70c2b95d4ee6bd751cdc23bd76cfda"
PLAN_ONLY_COMMIT = "31178d7eeb3908eb5b40782944ba3c0d383141c7"
PLAN_PATH = "scripts/songsterr-fresh/fixtures/purpose_built_synthetic_capture_plan_v1.json"
EVIDENCE_PATH = (
    "scripts/songsterr-fresh/fixtures/"
    "purpose_built_synthetic_preregistration_evidence_v1.json"
)


def valid_git_bound_inputs() -> tuple[dict, dict]:
    manifest, plan = binding_fixture.bound_manifest()
    manifest["corpus"]["capturePlanPath"] = PLAN_PATH
    manifest["corpus"]["capturePlanSha256"] = proof.base.sha256_bytes(
        proof.base.canonical_json(plan).encode("utf-8")
    )
    manifest["corpus"]["capturePreregistrationPath"] = EVIDENCE_PATH
    manifest["corpus"]["capturePreregistrationCommit"] = PREREG_COMMIT

    # Synthetic timestamps deliberately postdate the frozen Git fixture.
    manifest["attempts"][0]["capturedAtUtc"] = "2030-01-01T00:00:00Z"
    manifest["attempts"][1]["capturedAtUtc"] = "2030-01-01T00:02:00Z"
    manifest["attempts"][2]["capturedAtUtc"] = "2030-01-01T00:03:00Z"
    return manifest, plan


def test_valid_git_history_proof_allows_only_structural_audit() -> None:
    manifest, plan = valid_git_bound_inputs()
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is True, result
    assert result["errors"] == [], result
    assert result["manifestPlanBindingValid"] is True
    assert result["preregistrationCommitExists"] is True
    assert result["preregistrationCommitIsAncestorOfHead"] is True
    assert result["historicalCapturePlanSha256"] == manifest["corpus"]["capturePlanSha256"]
    assert result["preregistrationEvidenceBound"] is True
    assert result["allCaptureTimestampsAfterPreregistration"] is True
    assert result["gitPreregistrationBindingEstablished"] is True
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_current_plan_cannot_be_rewritten_after_preregistration() -> None:
    manifest, plan = valid_git_bound_inputs()
    plan["planId"] = "rewritten-after-freeze"
    manifest["corpus"]["capturePlanSha256"] = proof.base.sha256_bytes(
        proof.base.canonical_json(plan).encode("utf-8")
    )
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any("GIT_CAPTURE_PLAN_SHA256_MISMATCH" in error for error in result["errors"]), result
    assert any(
        "CURRENT_PLAN_DIFFERS_FROM_PREREGISTERED_GIT_PLAN" in error
        for error in result["errors"]
    ), result


def test_plan_path_must_exist_at_preregistration_commit() -> None:
    manifest, plan = valid_git_bound_inputs()
    manifest["corpus"]["capturePlanPath"] = "scripts/songsterr-fresh/fixtures/DOES_NOT_EXIST.json"
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any(
        "GIT_CAPTURE_PLAN_NOT_FOUND_AT_PREREGISTRATION_COMMIT" in error
        for error in result["errors"]
    ), result


def test_preregistration_evidence_must_exist_at_declared_commit() -> None:
    manifest, plan = valid_git_bound_inputs()
    manifest["corpus"]["capturePreregistrationCommit"] = PLAN_ONLY_COMMIT
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any(
        "GIT_PREREGISTRATION_EVIDENCE_NOT_FOUND_AT_PREREGISTRATION_COMMIT" in error
        for error in result["errors"]
    ), result


def test_preregistration_evidence_path_cannot_be_swapped() -> None:
    manifest, plan = valid_git_bound_inputs()
    manifest["corpus"]["capturePreregistrationPath"] = PLAN_PATH
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any(
        "GIT_PREREGISTRATION_EVIDENCE_CONTRACT_MISMATCH" in error
        for error in result["errors"]
    ), result


def test_capture_must_postdate_preregistration_commit() -> None:
    manifest, plan = valid_git_bound_inputs()
    manifest["attempts"][0]["capturedAtUtc"] = "2026-01-01T00:00:00Z"
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any(
        "CAPTURE_TIMESTAMP_NOT_AFTER_PREREGISTRATION_COMMIT:ATTEMPT[0]" in error
        for error in result["errors"]
    ), result
    assert result["allCaptureTimestampsAfterPreregistration"] is False


def test_unknown_preregistration_commit_fails_closed() -> None:
    manifest, plan = valid_git_bound_inputs()
    manifest["corpus"]["capturePreregistrationCommit"] = "2" * 40
    result = proof.validate_git_proof(manifest, plan, REPO_ROOT)
    assert result["gitProofValid"] is False, result
    assert any("GIT_PREREGISTRATION_COMMIT_NOT_FOUND" in error for error in result["errors"]), result


def main() -> int:
    test_valid_git_history_proof_allows_only_structural_audit()
    test_current_plan_cannot_be_rewritten_after_preregistration()
    test_plan_path_must_exist_at_preregistration_commit()
    test_preregistration_evidence_must_exist_at_declared_commit()
    test_preregistration_evidence_path_cannot_be_swapped()
    test_capture_must_postdate_preregistration_commit()
    test_unknown_preregistration_commit_fails_closed()
    print("PURPOSE_BUILT_CAPTURE_PREREGISTRATION_GIT_PROOF_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
