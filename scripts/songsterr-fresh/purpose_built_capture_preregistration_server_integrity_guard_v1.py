#!/usr/bin/env python3
"""Fail-closed integrity guard for purpose-built preregistration server proof.

The base server proof establishes GitHub run identity, chronology, ancestry, and
plan/evidence continuity. This extra layer closes a descendant-tampering gap by
requiring the attestation workflow and generator at the cited run head to have
exactly the frozen hardened Git blob identities.

No candidate audio/MIDI, Basic Pitch/V6 output, or correctness is accessed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SERVER_PATH = HERE / "purpose_built_capture_preregistration_server_proof_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_server_proof_v1", SERVER_PATH
)
assert spec and spec.loader
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)
base = server.base

INTEGRITY_CONTRACT = "songsterr-fresh-purpose-built-preregistration-server-integrity-v1"
ATTESTATION_GENERATOR_PATH = (
    "scripts/songsterr-fresh/purpose_built_capture_preregistration_attestation_v1.py"
)
FROZEN_ATTESTATION_WORKFLOW_BLOB = "b8b5bd78abad1aa0cfa0cf3be9d4c8ab31ed178f"
FROZEN_ATTESTATION_GENERATOR_BLOB = "9172762fd86077701c20b77655f82e9307f00c5d"


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _blob_at(repo_root: Path, commit: str, path: str) -> str | None:
    if not base._is_commit(commit):
        return None
    result = _git(repo_root, "rev-parse", f"{commit}:{path}")
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value if base._is_commit(value) else None


def validate_server_integrity(
    manifest: Any,
    plan: Any,
    run_metadata: Any,
    *,
    repo_root: str | Path = ".",
    expected_repository: str,
    expected_run_id: str,
    allow_synthetic_fixture_for_tests: bool = False,
) -> dict[str, Any]:
    root = Path(repo_root).resolve()
    server_result = server.validate_server_proof(
        manifest,
        plan,
        run_metadata,
        repo_root=root,
        expected_repository=expected_repository,
        expected_run_id=expected_run_id,
        allow_synthetic_fixture_for_tests=allow_synthetic_fixture_for_tests,
    )
    errors = list(server_result.get("errors", []))

    head_sha = run_metadata.get("head_sha") if isinstance(run_metadata, dict) else None
    workflow_blob = _blob_at(root, head_sha, server.ATTESTATION_WORKFLOW_PATH)
    generator_blob = _blob_at(root, head_sha, ATTESTATION_GENERATOR_PATH)

    workflow_blob_frozen = workflow_blob == FROZEN_ATTESTATION_WORKFLOW_BLOB
    generator_blob_frozen = generator_blob == FROZEN_ATTESTATION_GENERATOR_BLOB

    if not workflow_blob_frozen:
        errors.append(
            "ATTESTATION_WORKFLOW_BLOB_NOT_FROZEN:"
            f"{workflow_blob!r}!={FROZEN_ATTESTATION_WORKFLOW_BLOB!r}"
        )
    if not generator_blob_frozen:
        errors.append(
            "ATTESTATION_GENERATOR_BLOB_NOT_FROZEN:"
            f"{generator_blob!r}!={FROZEN_ATTESTATION_GENERATOR_BLOB!r}"
        )

    merged_errors = sorted(set(errors))
    integrity_valid = bool(
        not merged_errors
        and server_result.get("serverProofValid") is True
        and workflow_blob_frozen
        and generator_blob_frozen
    )

    return {
        "contract": INTEGRITY_CONTRACT,
        "serverIntegrityValid": integrity_valid,
        "errors": merged_errors,
        "baseServerProofValid": server_result.get("serverProofValid") is True,
        "githubRunHeadSha": head_sha,
        "attestationWorkflowBlob": workflow_blob,
        "attestationWorkflowBlobFrozen": workflow_blob_frozen,
        "attestationGeneratorBlob": generator_blob,
        "attestationGeneratorBlobFrozen": generator_blob_frozen,
        "githubServerPreregistrationEstablished": integrity_valid,
        "mayAdvanceToReferenceBlindStructuralAudit": integrity_valid,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(base.REQUIRED_POLICY_BOUNDARY),
    }


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
    result = validate_server_integrity(
        manifest,
        plan,
        run_metadata,
        repo_root=args.repo_root,
        expected_repository=args.repository,
        expected_run_id=args.run_id,
    )
    rendered = base.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["serverIntegrityValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
