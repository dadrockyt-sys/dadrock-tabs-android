#!/usr/bin/env python3
"""Synthetic-only tests for hosted attestation artifact proof."""

from __future__ import annotations

import importlib.util
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

PROOF_PATH = HERE / "purpose_built_capture_preregistration_artifact_proof_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_artifact_proof_v1", PROOF_PATH
)
assert spec and spec.loader
proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proof)

SERVER_TEST_PATH = HERE / "test_purpose_built_capture_preregistration_server_proof_v1.py"
fixture_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_proof_fixture", SERVER_TEST_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def inputs() -> tuple[dict, dict, dict, dict, dict]:
    manifest, plan = fixture.fixture.valid_git_bound_inputs()
    metadata = fixture.valid_run_metadata()
    metadata["run_attempt"] = 1
    artifact = {
        "id": 555001,
        "name": f"purpose-built-preregistration-attestation-{fixture.RUN_ID}",
        "expired": False,
        "workflow_run": {"id": int(fixture.RUN_ID)},
    }
    payload = {
        "contract": "songsterr-fresh-purpose-built-preregistration-attestation-v1",
        "attestationValid": True,
        "errors": [],
        "mode": "real_preregistration",
        "repository": fixture.REPOSITORY,
        "headSha": metadata["head_sha"],
        "runId": fixture.RUN_ID,
        "runAttempt": "1",
        "workflowRef": (
            f"{fixture.REPOSITORY}/{proof.server.ATTESTATION_WORKFLOW_PATH}@"
            f"refs/heads/{proof.server.CANONICAL_BRANCH}"
        ),
        "capturePlanPath": manifest["corpus"]["capturePlanPath"],
        "capturePlanSha256": manifest["corpus"]["capturePlanSha256"],
        "plannedSlotCount": len(plan["plannedSlots"]),
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(proof.base.REQUIRED_POLICY_BOUNDARY),
    }
    return manifest, plan, metadata, artifact, payload


def validate(manifest: dict, plan: dict, metadata: dict, artifact: dict, payload: dict, mode: str):
    return proof.validate_artifact_proof(
        manifest,
        plan,
        metadata,
        artifact,
        payload,
        mode,
        repo_root=REPO_ROOT,
        expected_repository=fixture.REPOSITORY,
        expected_run_id=fixture.RUN_ID,
        allow_synthetic_fixture_for_tests=True,
    )


def test_exact_artifact_binds_dispatched_plan() -> None:
    manifest, plan, metadata, artifact, payload = inputs()
    result = validate(manifest, plan, metadata, artifact, payload, "real_preregistration")
    assert result["artifactProofValid"] is True, result
    assert result["serverIntegrityValid"] is True
    assert result["attestedCapturePlanPath"] == manifest["corpus"]["capturePlanPath"]
    assert result["attestedCapturePlanSha256"] == manifest["corpus"]["capturePlanSha256"]
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is True
    assert result["correctnessAuthorized"] is False


def test_successful_run_for_other_plan_cannot_be_reused() -> None:
    manifest, plan, metadata, artifact, payload = inputs()
    payload["capturePlanSha256"] = "0" * 64
    result = validate(manifest, plan, metadata, artifact, payload, "real_preregistration")
    assert result["artifactProofValid"] is False, result
    assert any(
        "ATTESTATION_ARTIFACT_FIELD_MISMATCH:capturePlanSha256" in error
        for error in result["errors"]
    )
    assert result["mayAdvanceToReferenceBlindStructuralAudit"] is False


def test_synthetic_run_mode_cannot_be_reused_for_real_preregistration() -> None:
    manifest, plan, metadata, artifact, payload = inputs()
    payload["mode"] = "synthetic_ci"
    result = validate(manifest, plan, metadata, artifact, payload, "synthetic_ci")
    assert result["artifactProofValid"] is False, result
    assert any("ATTESTATION_ARTIFACT_FIELD_MISMATCH:mode" in error for error in result["errors"])
    assert any("ATTESTATION_ARTIFACT_RUN_MODE_NOT_REAL" in error for error in result["errors"])


def test_wrong_or_expired_artifact_fails_closed() -> None:
    manifest, plan, metadata, artifact, payload = inputs()
    artifact["name"] = "some-other-artifact"
    artifact["expired"] = True
    result = validate(manifest, plan, metadata, artifact, payload, "real_preregistration")
    assert result["artifactProofValid"] is False, result
    assert any("ATTESTATION_ARTIFACT_NAME_MISMATCH" in error for error in result["errors"])
    assert "ATTESTATION_ARTIFACT_EXPIRED_OR_EXPIRY_UNKNOWN" in result["errors"]


def test_zip_parser_requires_exact_named_payload_files() -> None:
    manifest, plan, metadata, artifact, payload = inputs()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(proof.ATTESTATION_JSON_NAME, json.dumps(payload))
        archive.writestr(proof.RUN_MODE_NAME, "real_preregistration\n")
    parsed, mode, errors = proof.parse_attestation_zip(buffer.getvalue())
    assert errors == [], errors
    assert parsed == payload
    assert mode == "real_preregistration"

    bad = io.BytesIO()
    with zipfile.ZipFile(bad, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("wrong.json", "{}")
    parsed, mode, errors = proof.parse_attestation_zip(bad.getvalue())
    assert parsed is None
    assert mode is None
    assert "ATTESTATION_ARTIFACT_JSON_MUST_EXIST_EXACTLY_ONCE" in errors
    assert "ATTESTATION_ARTIFACT_RUN_MODE_MUST_EXIST_EXACTLY_ONCE" in errors


def main() -> int:
    test_exact_artifact_binds_dispatched_plan()
    test_successful_run_for_other_plan_cannot_be_reused()
    test_synthetic_run_mode_cannot_be_reused_for_real_preregistration()
    test_wrong_or_expired_artifact_fails_closed()
    test_zip_parser_requires_exact_named_payload_files()
    print("PURPOSE_BUILT_PREREGISTRATION_ARTIFACT_PROOF_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
