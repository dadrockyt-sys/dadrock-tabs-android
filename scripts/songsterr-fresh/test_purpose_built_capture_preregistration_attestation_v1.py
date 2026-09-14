#!/usr/bin/env python3
"""Synthetic-only tests for the GitHub preregistration attestation payload."""

from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent

ATTEST_PATH = HERE / "purpose_built_capture_preregistration_attestation_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_attestation_v1", ATTEST_PATH
)
assert spec and spec.loader
attest = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attest)

BINDING_TEST_PATH = HERE / "test_purpose_built_capture_preregistration_binding_v1.py"
fixture_spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_binding_fixture", BINDING_TEST_PATH
)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)

PLAN_PATH = "scripts/songsterr-fresh/fixtures/purpose_built_synthetic_capture_plan_v1.json"


def valid_evidence(plan: dict) -> dict:
    return {
        "contract": attest.EVIDENCE_CONTRACT,
        "capturePlanPath": PLAN_PATH,
        "capturePlanSha256": attest.base.sha256_bytes(
            attest.base.canonical_json(plan).encode("utf-8")
        ),
        "purpose": "synthetic",
    }


def build(plan: dict | None = None, evidence: dict | None = None) -> dict:
    plan = copy.deepcopy(plan or fixture.valid_plan())
    evidence = copy.deepcopy(evidence or valid_evidence(plan))
    return attest.build_attestation(
        plan,
        evidence,
        plan_repo_path=PLAN_PATH,
        repository="dadrockyt-sys/dadrock-tabs-android",
        head_sha="1" * 40,
        run_id="123456789",
        run_attempt="1",
        workflow_ref=(
            "dadrockyt-sys/dadrock-tabs-android/"
            ".github/workflows/songsterr-purpose-built-preregistration-attestation.yml@refs/heads/"
            "songsterr-fresh-pipeline-v1"
        ),
        mode="synthetic_ci",
    )


def test_valid_attestation_payload_is_fail_closed_for_model_work() -> None:
    result = build()
    assert result["attestationValid"] is True, result
    assert result["errors"] == [], result
    assert result["mode"] == "synthetic_ci"
    assert result["plannedSlotCount"] == 2
    assert result["failureCriteriaBound"] is True
    assert result["authoritativeStructuralSuitabilityEstablished"] is False
    assert result["basicPitchAuthorized"] is False
    assert result["v6Authorized"] is False
    assert result["correctnessAuthorized"] is False


def test_real_mode_rejects_synthetic_fixture_plan() -> None:
    plan = fixture.valid_plan()
    evidence = valid_evidence(plan)
    result = attest.build_attestation(
        plan,
        evidence,
        plan_repo_path=PLAN_PATH,
        repository="dadrockyt-sys/dadrock-tabs-android",
        head_sha="1" * 40,
        run_id="123456789",
        run_attempt="1",
        workflow_ref="workflow-ref",
        mode="real_preregistration",
    )
    assert result["attestationValid"] is False, result
    assert "REAL_PREREGISTRATION_CANNOT_USE_SYNTHETIC_PLAN_FIXTURE" in result["errors"], result
    assert "REAL_PREREGISTRATION_CANNOT_USE_SYNTHETIC_PLAN_ID" in result["errors"], result
    assert "REAL_PREREGISTRATION_CANNOT_USE_SYNTHETIC_EVIDENCE_BINDING" in result["errors"], result


def test_evidence_plan_hash_mismatch_fails() -> None:
    plan = fixture.valid_plan()
    evidence = valid_evidence(plan)
    evidence["capturePlanSha256"] = "0" * 64
    result = build(plan, evidence)
    assert result["attestationValid"] is False, result
    assert "PREREGISTRATION_EVIDENCE_PLAN_SHA256_MISMATCH" in result["errors"], result


def test_evidence_plan_path_mismatch_fails() -> None:
    plan = fixture.valid_plan()
    evidence = valid_evidence(plan)
    evidence["capturePlanPath"] = "other.json"
    result = build(plan, evidence)
    assert result["attestationValid"] is False, result
    assert "PREREGISTRATION_EVIDENCE_PLAN_PATH_MISMATCH" in result["errors"], result


def test_subjective_failure_class_fails_attestation() -> None:
    plan = fixture.valid_plan()
    plan["allowedAcquisitionFailureReasons"].append("PLAYER_WANTS_RETAKE")
    plan["acquisitionFailureCriteria"]["PLAYER_WANTS_RETAKE"] = "Player asks for another take."
    evidence = valid_evidence(plan)
    result = build(plan, evidence)
    assert result["attestationValid"] is False, result
    assert "CAPTURE_PLAN_FAILURE_REASON_NOT_OBJECTIVE:PLAYER_WANTS_RETAKE" in result["errors"], result


def test_invalid_actions_identity_fails() -> None:
    plan = fixture.valid_plan()
    evidence = valid_evidence(plan)
    result = attest.build_attestation(
        plan,
        evidence,
        plan_repo_path=PLAN_PATH,
        repository="",
        head_sha="bad",
        run_id="not-a-number",
        run_attempt="x",
        workflow_ref="",
        mode="synthetic_ci",
    )
    assert result["attestationValid"] is False, result
    for expected in (
        "GITHUB_REPOSITORY_INVALID",
        "GITHUB_HEAD_SHA_INVALID",
        "GITHUB_RUN_ID_INVALID",
        "GITHUB_RUN_ATTEMPT_INVALID",
        "GITHUB_WORKFLOW_REF_REQUIRED",
    ):
        assert expected in result["errors"], result


def test_unknown_attestation_mode_fails() -> None:
    plan = fixture.valid_plan()
    evidence = valid_evidence(plan)
    result = attest.build_attestation(
        plan,
        evidence,
        plan_repo_path=PLAN_PATH,
        repository="dadrockyt-sys/dadrock-tabs-android",
        head_sha="1" * 40,
        run_id="123456789",
        run_attempt="1",
        workflow_ref="workflow-ref",
        mode="unknown",
    )
    assert result["attestationValid"] is False, result
    assert "ATTESTATION_MODE_INVALID:'unknown'" in result["errors"], result


def main() -> int:
    test_valid_attestation_payload_is_fail_closed_for_model_work()
    test_real_mode_rejects_synthetic_fixture_plan()
    test_evidence_plan_hash_mismatch_fails()
    test_evidence_plan_path_mismatch_fails()
    test_subjective_failure_class_fails_attestation()
    test_invalid_actions_identity_fails()
    test_unknown_attestation_mode_fails()
    print("PURPOSE_BUILT_PREREGISTRATION_ATTESTATION_V1_SYNTHETIC_TESTS_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
