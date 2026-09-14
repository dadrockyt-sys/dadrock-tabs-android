#!/usr/bin/env python3
"""GitHub-server preregistration proof for a future purpose-built V6 holdout.

This mandatory governance layer strengthens the local Git proof with GitHub-hosted
Actions metadata. A real capture preregistration must cite a successful
workflow_dispatch run of the dedicated read-only attestation workflow. The
platform-reported run completion time must be strictly earlier than every capture
timestamp, and the run head must contain the same frozen plan/evidence plus the
hardened real-vs-synthetic attestation workflow semantics.

The GitHub timestamp is stronger evidence than self-authored Git commit dates but
is still governance evidence, not proof of physical capture time or source truth.
No candidate audio/MIDI, Basic Pitch/V6 output, or correctness is accessed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
GIT_PROOF_PATH = HERE / "purpose_built_capture_preregistration_git_proof_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_git_proof_v1", GIT_PROOF_PATH
)
assert spec and spec.loader
git_proof = importlib.util.module_from_spec(spec)
spec.loader.exec_module(git_proof)
base = git_proof.base

SERVER_PROOF_CONTRACT = "songsterr-fresh-purpose-built-preregistration-server-proof-v1"
ATTESTATION_WORKFLOW_PATH = ".github/workflows/songsterr-purpose-built-preregistration-attestation.yml"
CANONICAL_BRANCH = "songsterr-fresh-pipeline-v1"
SYNTHETIC_FIXTURE_PREFIX = "scripts/songsterr-fresh/fixtures/"
# First commit whose workflow_dispatch path has no synthetic defaults, emits
# mode=real_preregistration, and passes that mode to the generator.
HARDENED_ATTESTATION_MIN_COMMIT = "e3d90f275dc92e1d705bf7db78f0b4d6622a324a"


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _parse_server_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _historical_json(repo_root: Path, commit: str, path: str) -> Any:
    shown = _git(repo_root, "show", f"{commit}:{path}")
    if shown.returncode != 0:
        return None
    try:
        return json.loads(shown.stdout)
    except json.JSONDecodeError:
        return None


def fetch_run_metadata(repository: str, run_id: str, token: str) -> dict[str, Any]:
    if not repository or "/" not in repository:
        raise RuntimeError("repository must be owner/name")
    if not run_id.isdigit():
        raise RuntimeError("run_id must be numeric")
    if not token:
        raise RuntimeError("GitHub token is required")
    url = f"https://api.github.com/repos/{repository}/actions/runs/{run_id}"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "songsterr-fresh-purpose-built-server-proof-v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"failed to fetch GitHub Actions run metadata: {exc}") from exc


def validate_server_proof(
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
    local_git_result = git_proof.validate_git_proof(manifest, plan, root)
    errors = list(local_git_result.get("errors", []))

    prereg_commit = None
    plan_path = None
    plan_sha = None
    prereg_path = None
    if isinstance(manifest, dict) and isinstance(manifest.get("corpus"), dict):
        corpus = manifest["corpus"]
        prereg_commit = corpus.get("capturePreregistrationCommit")
        plan_path = corpus.get("capturePlanPath")
        plan_sha = corpus.get("capturePlanSha256")
        prereg_path = corpus.get("capturePreregistrationPath")

    synthetic_fixture_rejected = False
    if not allow_synthetic_fixture_for_tests:
        if isinstance(plan_path, str) and plan_path.startswith(SYNTHETIC_FIXTURE_PREFIX):
            errors.append("SERVER_PROOF_REJECTS_SYNTHETIC_PLAN_FIXTURE")
            synthetic_fixture_rejected = True
        if isinstance(prereg_path, str) and prereg_path.startswith(SYNTHETIC_FIXTURE_PREFIX):
            errors.append("SERVER_PROOF_REJECTS_SYNTHETIC_PREREGISTRATION_EVIDENCE_FIXTURE")
            synthetic_fixture_rejected = True
        if isinstance(plan, dict) and str(plan.get("planId", "")).lower().startswith("synthetic"):
            errors.append("SERVER_PROOF_REJECTS_SYNTHETIC_PLAN_ID")
            synthetic_fixture_rejected = True

    if not isinstance(run_metadata, dict):
        errors.append("GITHUB_RUN_METADATA_OBJECT_REQUIRED")
        run_metadata = {}

    run_id = run_metadata.get("id")
    if str(run_id) != str(expected_run_id):
        errors.append(f"GITHUB_RUN_ID_MISMATCH:{run_id!r}!={expected_run_id!r}")

    repository = run_metadata.get("repository")
    repository_full_name = repository.get("full_name") if isinstance(repository, dict) else None
    if repository_full_name != expected_repository:
        errors.append(
            f"GITHUB_RUN_REPOSITORY_MISMATCH:{repository_full_name!r}!={expected_repository!r}"
        )

    if run_metadata.get("event") != "workflow_dispatch":
        errors.append(f"GITHUB_RUN_EVENT_NOT_WORKFLOW_DISPATCH:{run_metadata.get('event')!r}")
    if run_metadata.get("status") != "completed":
        errors.append(f"GITHUB_RUN_STATUS_NOT_COMPLETED:{run_metadata.get('status')!r}")
    if run_metadata.get("conclusion") != "success":
        errors.append(f"GITHUB_RUN_CONCLUSION_NOT_SUCCESS:{run_metadata.get('conclusion')!r}")
    if run_metadata.get("path") != ATTESTATION_WORKFLOW_PATH:
        errors.append(f"GITHUB_RUN_WORKFLOW_PATH_MISMATCH:{run_metadata.get('path')!r}")
    if run_metadata.get("head_branch") != CANONICAL_BRANCH:
        errors.append(f"GITHUB_RUN_HEAD_BRANCH_MISMATCH:{run_metadata.get('head_branch')!r}")

    head_sha = run_metadata.get("head_sha")
    if not base._is_commit(head_sha):
        errors.append(f"GITHUB_RUN_HEAD_SHA_INVALID:{head_sha!r}")

    head_exists = False
    hardened_attestation_workflow_bound = False
    prereg_is_ancestor_of_head = False
    head_is_ancestor_of_current = False
    historical_plan_matches = False
    historical_evidence_matches = False
    workflow_present_at_head = False

    if base._is_commit(head_sha):
        head_exists = _git(root, "cat-file", "-e", f"{head_sha}^{{commit}}").returncode == 0
        if not head_exists:
            errors.append(f"GITHUB_RUN_HEAD_SHA_NOT_IN_LOCAL_HISTORY:{head_sha}")
        else:
            hardened_attestation_workflow_bound = (
                _git(
                    root,
                    "merge-base",
                    "--is-ancestor",
                    HARDENED_ATTESTATION_MIN_COMMIT,
                    head_sha,
                ).returncode
                == 0
            )
            if not hardened_attestation_workflow_bound:
                errors.append("ATTESTATION_RUN_HEAD_PREDATES_HARDENED_REAL_MODE_WORKFLOW")

            if base._is_commit(prereg_commit):
                prereg_is_ancestor_of_head = (
                    _git(root, "merge-base", "--is-ancestor", prereg_commit, head_sha).returncode == 0
                )
                if not prereg_is_ancestor_of_head:
                    errors.append("PREREGISTRATION_COMMIT_NOT_ANCESTOR_OF_ATTESTATION_HEAD")
            head_is_ancestor_of_current = (
                _git(root, "merge-base", "--is-ancestor", head_sha, "HEAD").returncode == 0
            )
            if not head_is_ancestor_of_current:
                errors.append("ATTESTATION_HEAD_NOT_ANCESTOR_OF_CURRENT_HEAD")

            if isinstance(plan_path, str) and plan_path:
                historical_plan = _historical_json(root, head_sha, plan_path)
                if isinstance(historical_plan, dict):
                    historical_plan_sha = base.sha256_bytes(
                        base.canonical_json(historical_plan).encode("utf-8")
                    )
                    historical_plan_matches = historical_plan_sha == plan_sha
                if not historical_plan_matches:
                    errors.append("ATTESTATION_HEAD_CAPTURE_PLAN_MISMATCH")

            if isinstance(prereg_path, str) and prereg_path:
                historical_evidence = _historical_json(root, head_sha, prereg_path)
                if isinstance(historical_evidence, dict):
                    historical_evidence_matches = (
                        historical_evidence.get("contract") == git_proof.EVIDENCE_CONTRACT
                        and historical_evidence.get("capturePlanPath") == plan_path
                        and historical_evidence.get("capturePlanSha256") == plan_sha
                    )
                if not historical_evidence_matches:
                    errors.append("ATTESTATION_HEAD_PREREGISTRATION_EVIDENCE_MISMATCH")

            workflow_present_at_head = (
                _git(root, "cat-file", "-e", f"{head_sha}:{ATTESTATION_WORKFLOW_PATH}").returncode == 0
            )
            if not workflow_present_at_head:
                errors.append("ATTESTATION_WORKFLOW_NOT_PRESENT_AT_RUN_HEAD")

    server_times: list[datetime] = []
    for field in ("created_at", "run_started_at", "updated_at"):
        parsed = _parse_server_timestamp(run_metadata.get(field))
        if parsed is None:
            errors.append(f"GITHUB_RUN_{field.upper()}_INVALID:{run_metadata.get(field)!r}")
        else:
            server_times.append(parsed)
    run_completion_time = max(server_times) if len(server_times) == 3 else None

    all_capture_timestamps_after_server_attestation = run_completion_time is not None
    if run_completion_time is not None and isinstance(manifest, dict):
        attempts = manifest.get("attempts")
        if isinstance(attempts, list):
            for index, attempt in enumerate(attempts):
                if not isinstance(attempt, dict):
                    continue
                captured = base._parse_utc_timestamp(attempt.get("capturedAtUtc"))
                if captured is None:
                    all_capture_timestamps_after_server_attestation = False
                    continue
                if captured <= run_completion_time:
                    errors.append(
                        "CAPTURE_TIMESTAMP_NOT_AFTER_GITHUB_ATTESTATION_COMPLETION:"
                        f"ATTEMPT[{index}]:{attempt.get('attemptId')}"
                    )
                    all_capture_timestamps_after_server_attestation = False

    merged_errors = sorted(set(errors))
    server_proof_valid = bool(
        not merged_errors
        and local_git_result.get("gitProofValid") is True
        and head_exists
        and hardened_attestation_workflow_bound
        and prereg_is_ancestor_of_head
        and head_is_ancestor_of_current
        and historical_plan_matches
        and historical_evidence_matches
        and workflow_present_at_head
        and all_capture_timestamps_after_server_attestation
    )

    return {
        "contract": SERVER_PROOF_CONTRACT,
        "serverProofValid": server_proof_valid,
        "errors": merged_errors,
        "localGitProofValid": local_git_result.get("gitProofValid") is True,
        "githubRunId": str(run_id) if run_id is not None else None,
        "githubRunHeadSha": head_sha,
        "githubRunEventWorkflowDispatch": run_metadata.get("event") == "workflow_dispatch",
        "githubRunCompletedSuccessfully": (
            run_metadata.get("status") == "completed" and run_metadata.get("conclusion") == "success"
        ),
        "syntheticFixtureRejected": synthetic_fixture_rejected,
        "hardenedAttestationWorkflowBound": hardened_attestation_workflow_bound,
        "preregistrationCommitIsAncestorOfAttestationHead": prereg_is_ancestor_of_head,
        "attestationHeadIsAncestorOfCurrentHead": head_is_ancestor_of_current,
        "attestationHeadPlanMatches": historical_plan_matches,
        "attestationHeadEvidenceMatches": historical_evidence_matches,
        "attestationWorkflowPresentAtRunHead": workflow_present_at_head,
        "allCaptureTimestampsAfterServerAttestation": all_capture_timestamps_after_server_attestation,
        "githubServerPreregistrationEstablished": server_proof_valid,
        "mayAdvanceToReferenceBlindStructuralAudit": server_proof_valid,
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
    run_metadata = fetch_run_metadata(args.repository, args.run_id, token)
    result = validate_server_proof(
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
    return 0 if result["serverProofValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
