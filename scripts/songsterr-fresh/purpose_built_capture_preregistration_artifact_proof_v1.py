#!/usr/bin/env python3
"""Verify the exact hosted attestation artifact for a purpose-built preregistration.

A successful workflow_dispatch run is not enough by itself: the cited run must
have attested the same frozen capture-plan path and SHA used by the manifest.
This layer verifies the downloaded Actions artifact payload from that exact run.

No candidate audio/MIDI, Basic Pitch/V6 output, or correctness is accessed.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
INTEGRITY_PATH = HERE / "purpose_built_capture_preregistration_server_integrity_guard_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_integrity_guard_v1", INTEGRITY_PATH
)
assert spec and spec.loader
integrity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integrity)
server = integrity.server
base = integrity.base
attestation = server.git_proof.binding

ARTIFACT_PROOF_CONTRACT = "songsterr-fresh-purpose-built-preregistration-artifact-proof-v1"
ATTESTATION_JSON_NAME = "attestation.json"
RUN_MODE_NAME = "run-mode.txt"


def fetch_run_artifacts(repository: str, run_id: str, token: str) -> dict[str, Any]:
    if not repository or "/" not in repository:
        raise RuntimeError("repository must be owner/name")
    if not run_id.isdigit():
        raise RuntimeError("run_id must be numeric")
    if not token:
        raise RuntimeError("GitHub token is required")
    url = f"https://api.github.com/repos/{repository}/actions/runs/{run_id}/artifacts"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "songsterr-fresh-purpose-built-artifact-proof-v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"failed to fetch GitHub Actions artifacts: {exc}") from exc


def download_artifact_zip(repository: str, artifact_id: int, token: str) -> bytes:
    if not token:
        raise RuntimeError("GitHub token is required")
    url = f"https://api.github.com/repos/{repository}/actions/artifacts/{artifact_id}/zip"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "songsterr-fresh-purpose-built-artifact-proof-v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"failed to download GitHub Actions artifact: {exc}") from exc


def parse_attestation_zip(payload: bytes) -> tuple[dict[str, Any] | None, str | None, list[str]]:
    errors: list[str] = []
    try:
        with zipfile.ZipFile(io.BytesIO(payload), "r") as archive:
            names = archive.namelist()
            if names.count(ATTESTATION_JSON_NAME) != 1:
                errors.append("ATTESTATION_ARTIFACT_JSON_MUST_EXIST_EXACTLY_ONCE")
            if names.count(RUN_MODE_NAME) != 1:
                errors.append("ATTESTATION_ARTIFACT_RUN_MODE_MUST_EXIST_EXACTLY_ONCE")
            if errors:
                return None, None, errors
            try:
                attestation_json = json.loads(
                    archive.read(ATTESTATION_JSON_NAME).decode("utf-8")
                )
            except (UnicodeDecodeError, json.JSONDecodeError, KeyError):
                errors.append("ATTESTATION_ARTIFACT_JSON_INVALID")
                attestation_json = None
            try:
                run_mode = archive.read(RUN_MODE_NAME).decode("utf-8").strip()
            except (UnicodeDecodeError, KeyError):
                errors.append("ATTESTATION_ARTIFACT_RUN_MODE_INVALID")
                run_mode = None
            return attestation_json, run_mode, errors
    except zipfile.BadZipFile:
        return None, None, ["ATTESTATION_ARTIFACT_ZIP_INVALID"]


def validate_artifact_proof(
    manifest: Any,
    plan: Any,
    run_metadata: Any,
    artifact_metadata: Any,
    attestation_payload: Any,
    run_mode: Any,
    *,
    repo_root: str | Path = ".",
    expected_repository: str,
    expected_run_id: str,
    allow_synthetic_fixture_for_tests: bool = False,
) -> dict[str, Any]:
    integrity_result = integrity.validate_server_integrity(
        manifest,
        plan,
        run_metadata,
        repo_root=repo_root,
        expected_repository=expected_repository,
        expected_run_id=expected_run_id,
        allow_synthetic_fixture_for_tests=allow_synthetic_fixture_for_tests,
    )
    errors = list(integrity_result.get("errors", []))

    plan_path = None
    plan_sha = None
    if isinstance(manifest, dict) and isinstance(manifest.get("corpus"), dict):
        plan_path = manifest["corpus"].get("capturePlanPath")
        plan_sha = manifest["corpus"].get("capturePlanSha256")

    expected_artifact_name = f"purpose-built-preregistration-attestation-{expected_run_id}"
    artifact_id = None
    artifact_name = None
    artifact_not_expired = False
    if not isinstance(artifact_metadata, dict):
        errors.append("ATTESTATION_ARTIFACT_METADATA_OBJECT_REQUIRED")
    else:
        artifact_id = artifact_metadata.get("id")
        artifact_name = artifact_metadata.get("name")
        if not isinstance(artifact_id, int) or isinstance(artifact_id, bool) or artifact_id <= 0:
            errors.append("ATTESTATION_ARTIFACT_ID_INVALID")
        if artifact_name != expected_artifact_name:
            errors.append(
                f"ATTESTATION_ARTIFACT_NAME_MISMATCH:{artifact_name!r}!={expected_artifact_name!r}"
            )
        artifact_not_expired = artifact_metadata.get("expired") is False
        if not artifact_not_expired:
            errors.append("ATTESTATION_ARTIFACT_EXPIRED_OR_EXPIRY_UNKNOWN")
        workflow_run = artifact_metadata.get("workflow_run")
        if isinstance(workflow_run, dict) and workflow_run.get("id") is not None:
            if str(workflow_run.get("id")) != str(expected_run_id):
                errors.append("ATTESTATION_ARTIFACT_RUN_ID_MISMATCH")

    if not isinstance(attestation_payload, dict):
        errors.append("ATTESTATION_ARTIFACT_PAYLOAD_OBJECT_REQUIRED")
        attestation_payload = {}

    expected_workflow_ref = (
        f"{expected_repository}/{server.ATTESTATION_WORKFLOW_PATH}@"
        f"refs/heads/{server.CANONICAL_BRANCH}"
    )
    expected_head = run_metadata.get("head_sha") if isinstance(run_metadata, dict) else None
    expected_attempt = run_metadata.get("run_attempt") if isinstance(run_metadata, dict) else None

    required_pairs = {
        "contract": server.HERE.joinpath(
            "purpose_built_capture_preregistration_attestation_v1.py"
        ) and "songsterr-fresh-purpose-built-preregistration-attestation-v1",
        "attestationValid": True,
        "mode": "real_preregistration",
        "repository": expected_repository,
        "headSha": expected_head,
        "runId": str(expected_run_id),
        "capturePlanPath": plan_path,
        "capturePlanSha256": plan_sha,
    }
    for key, expected in required_pairs.items():
        if attestation_payload.get(key) != expected:
            errors.append(
                f"ATTESTATION_ARTIFACT_FIELD_MISMATCH:{key}:"
                f"{attestation_payload.get(key)!r}!={expected!r}"
            )

    if attestation_payload.get("errors") != []:
        errors.append("ATTESTATION_ARTIFACT_ERRORS_NOT_EMPTY")
    if expected_attempt is not None and attestation_payload.get("runAttempt") != str(expected_attempt):
        errors.append("ATTESTATION_ARTIFACT_RUN_ATTEMPT_MISMATCH")
    if attestation_payload.get("workflowRef") != expected_workflow_ref:
        errors.append("ATTESTATION_ARTIFACT_WORKFLOW_REF_MISMATCH")
    if run_mode != "real_preregistration":
        errors.append(f"ATTESTATION_ARTIFACT_RUN_MODE_NOT_REAL:{run_mode!r}")

    merged_errors = sorted(set(errors))
    valid = bool(
        not merged_errors
        and integrity_result.get("serverIntegrityValid") is True
        and artifact_not_expired
    )

    return {
        "contract": ARTIFACT_PROOF_CONTRACT,
        "artifactProofValid": valid,
        "errors": merged_errors,
        "serverIntegrityValid": integrity_result.get("serverIntegrityValid") is True,
        "artifactId": artifact_id,
        "artifactName": artifact_name,
        "artifactNotExpired": artifact_not_expired,
        "attestedCapturePlanPath": attestation_payload.get("capturePlanPath"),
        "attestedCapturePlanSha256": attestation_payload.get("capturePlanSha256"),
        "attestationMode": attestation_payload.get("mode"),
        "runModeFile": run_mode,
        "githubHostedArtifactPreregistrationEstablished": valid,
        "mayAdvanceToReferenceBlindStructuralAudit": valid,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(base.REQUIRED_POLICY_BOUNDARY),
    }


def _select_artifact(response: Any, expected_name: str) -> dict[str, Any]:
    artifacts = response.get("artifacts") if isinstance(response, dict) else None
    if not isinstance(artifacts, list):
        raise RuntimeError("GitHub artifact listing is invalid")
    matches = [item for item in artifacts if isinstance(item, dict) and item.get("name") == expected_name]
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one attestation artifact named {expected_name!r}")
    return matches[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--capture-plan", required=True)
    parser.add_argument("--repository", required=True, help="owner/name")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.capture_plan).read_text(encoding="utf-8"))
    token = os.environ.get("GITHUB_TOKEN", "")
    run_metadata = server.fetch_run_metadata(args.repository, args.run_id, token)
    artifact_listing = fetch_run_artifacts(args.repository, args.run_id, token)
    expected_name = f"purpose-built-preregistration-attestation-{args.run_id}"
    artifact_metadata = _select_artifact(artifact_listing, expected_name)
    zip_bytes = download_artifact_zip(args.repository, int(artifact_metadata["id"]), token)
    payload, run_mode, parse_errors = parse_attestation_zip(zip_bytes)
    result = validate_artifact_proof(
        manifest,
        plan,
        run_metadata,
        artifact_metadata,
        payload,
        run_mode,
        repo_root=args.repo_root,
        expected_repository=args.repository,
        expected_run_id=args.run_id,
    )
    if parse_errors:
        result["errors"] = sorted(set(result["errors"] + parse_errors))
        result["artifactProofValid"] = False
        result["githubHostedArtifactPreregistrationEstablished"] = False
        result["mayAdvanceToReferenceBlindStructuralAudit"] = False
    rendered = base.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["artifactProofValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
