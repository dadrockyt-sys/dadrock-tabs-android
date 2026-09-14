#!/usr/bin/env python3
"""Git-history proof for a future purpose-built V6 capture preregistration.

This is the final declaration-layer proof before a raw-byte reference-blind
structural audit may begin. It verifies that the exact content-only capture plan
was already present in Git at the manifest-declared preregistration commit and
that a machine-readable evidence file at that same commit binds the plan path
and canonical SHA256.

The proof also requires the preregistration commit to be an ancestor of the
checked-out history and every declared capture timestamp to be strictly later
than the commit's committer timestamp. This is governance evidence, not an
external trusted timestamping service; it does not establish media truth.

No candidate audio/MIDI bytes, Basic Pitch/V6 output, or correctness observations
are opened or computed.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BINDING_PATH = HERE / "purpose_built_capture_preregistration_binding_v1.py"
spec = importlib.util.spec_from_file_location(
    "purpose_built_capture_preregistration_binding_v1", BINDING_PATH
)
assert spec and spec.loader
binding = importlib.util.module_from_spec(spec)
spec.loader.exec_module(binding)
base = binding.base

EVIDENCE_CONTRACT = "songsterr-fresh-purpose-built-preregistration-evidence-v1"


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def _parse_git_timestamp(value: Any) -> datetime | None:
    """Parse any timezone-aware Git ISO-8601 timestamp and normalize to UTC."""
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


def _load_historical_json(
    repo_root: Path,
    commit: str,
    path: str,
    errors: list[str],
    label: str,
) -> Any:
    shown = _git(repo_root, "show", f"{commit}:{path}")
    if shown.returncode != 0:
        errors.append(f"GIT_{label}_NOT_FOUND_AT_PREREGISTRATION_COMMIT:{path}")
        return None
    try:
        return json.loads(shown.stdout)
    except json.JSONDecodeError:
        errors.append(f"GIT_{label}_JSON_INVALID_AT_PREREGISTRATION_COMMIT:{path}")
        return None


def validate_git_proof(manifest: Any, plan: Any, repo_root: str | Path = ".") -> dict[str, Any]:
    root = Path(repo_root).resolve()
    binding_result = binding.validate_binding(manifest, plan)
    errors = list(binding_result.get("errors", []))

    plan_path = None
    plan_sha = None
    prereg_path = None
    prereg_commit = None
    if isinstance(manifest, dict) and isinstance(manifest.get("corpus"), dict):
        corpus = manifest["corpus"]
        plan_path = corpus.get("capturePlanPath")
        plan_sha = corpus.get("capturePlanSha256")
        prereg_path = corpus.get("capturePreregistrationPath")
        prereg_commit = corpus.get("capturePreregistrationCommit")

    repository_detected = _git(root, "rev-parse", "--is-inside-work-tree")
    if repository_detected.returncode != 0 or repository_detected.stdout.strip() != "true":
        errors.append("GIT_REPOSITORY_REQUIRED")

    commit_exists = False
    commit_is_ancestor = False
    commit_timestamp = None
    historical_plan_sha = None
    evidence_bound = False

    if base._is_commit(prereg_commit) and repository_detected.returncode == 0:
        commit_check = _git(root, "cat-file", "-e", f"{prereg_commit}^{{commit}}")
        commit_exists = commit_check.returncode == 0
        if not commit_exists:
            errors.append(f"GIT_PREREGISTRATION_COMMIT_NOT_FOUND:{prereg_commit}")
        else:
            ancestor = _git(root, "merge-base", "--is-ancestor", prereg_commit, "HEAD")
            commit_is_ancestor = ancestor.returncode == 0
            if not commit_is_ancestor:
                errors.append(f"GIT_PREREGISTRATION_COMMIT_NOT_ANCESTOR_OF_HEAD:{prereg_commit}")

            timestamp_result = _git(root, "show", "-s", "--format=%cI", prereg_commit)
            if timestamp_result.returncode != 0:
                errors.append("GIT_PREREGISTRATION_COMMIT_TIMESTAMP_UNAVAILABLE")
            else:
                commit_timestamp = _parse_git_timestamp(timestamp_result.stdout.strip())
                if commit_timestamp is None:
                    errors.append(
                        "GIT_PREREGISTRATION_COMMIT_TIMESTAMP_INVALID_OR_NAIVE:"
                        f"{timestamp_result.stdout.strip()!r}"
                    )

            if isinstance(plan_path, str) and plan_path.strip():
                historical_plan = _load_historical_json(
                    root,
                    prereg_commit,
                    plan_path,
                    errors,
                    "CAPTURE_PLAN",
                )
                if isinstance(historical_plan, dict):
                    historical_plan_sha = base.sha256_bytes(
                        base.canonical_json(historical_plan).encode("utf-8")
                    )
                    if historical_plan_sha != plan_sha:
                        errors.append(
                            "GIT_CAPTURE_PLAN_SHA256_MISMATCH:"
                            f"{historical_plan_sha}!={plan_sha}"
                        )
                    current_plan_sha = (
                        base.sha256_bytes(base.canonical_json(plan).encode("utf-8"))
                        if isinstance(plan, dict)
                        else None
                    )
                    if current_plan_sha != historical_plan_sha:
                        errors.append(
                            "CURRENT_PLAN_DIFFERS_FROM_PREREGISTERED_GIT_PLAN:"
                            f"{current_plan_sha}!={historical_plan_sha}"
                        )

            if isinstance(prereg_path, str) and prereg_path.strip():
                evidence = _load_historical_json(
                    root,
                    prereg_commit,
                    prereg_path,
                    errors,
                    "PREREGISTRATION_EVIDENCE",
                )
                if isinstance(evidence, dict):
                    if evidence.get("contract") != EVIDENCE_CONTRACT:
                        errors.append(
                            "GIT_PREREGISTRATION_EVIDENCE_CONTRACT_MISMATCH:"
                            f"{evidence.get('contract')!r}"
                        )
                    if evidence.get("capturePlanPath") != plan_path:
                        errors.append("GIT_PREREGISTRATION_EVIDENCE_PLAN_PATH_MISMATCH")
                    if evidence.get("capturePlanSha256") != plan_sha:
                        errors.append("GIT_PREREGISTRATION_EVIDENCE_PLAN_SHA256_MISMATCH")
                    evidence_bound = (
                        evidence.get("contract") == EVIDENCE_CONTRACT
                        and evidence.get("capturePlanPath") == plan_path
                        and evidence.get("capturePlanSha256") == plan_sha
                    )

    all_capture_timestamps_after_preregistration = True
    if commit_timestamp is None:
        all_capture_timestamps_after_preregistration = False
    elif isinstance(manifest, dict) and isinstance(manifest.get("attempts"), list):
        for index, attempt in enumerate(manifest["attempts"]):
            if not isinstance(attempt, dict):
                continue
            captured = base._parse_utc_timestamp(attempt.get("capturedAtUtc"))
            if captured is None:
                # Base validation already reports the malformed timestamp.
                all_capture_timestamps_after_preregistration = False
                continue
            if captured <= commit_timestamp:
                errors.append(
                    "CAPTURE_TIMESTAMP_NOT_AFTER_PREREGISTRATION_COMMIT:"
                    f"ATTEMPT[{index}]:{attempt.get('attemptId')}"
                )
                all_capture_timestamps_after_preregistration = False

    merged_errors = sorted(set(errors))
    git_binding_established = bool(
        not merged_errors
        and binding_result.get("bindingValid") is True
        and commit_exists
        and commit_is_ancestor
        and historical_plan_sha == plan_sha
        and evidence_bound
        and all_capture_timestamps_after_preregistration
    )

    return {
        "contract": EVIDENCE_CONTRACT,
        "gitProofValid": git_binding_established,
        "errors": merged_errors,
        "manifestPlanBindingValid": binding_result.get("bindingValid") is True,
        "preregistrationCommitExists": commit_exists,
        "preregistrationCommitIsAncestorOfHead": commit_is_ancestor,
        "historicalCapturePlanSha256": historical_plan_sha,
        "preregistrationEvidenceBound": evidence_bound,
        "allCaptureTimestampsAfterPreregistration": all_capture_timestamps_after_preregistration,
        "gitPreregistrationBindingEstablished": git_binding_established,
        "mayAdvanceToReferenceBlindStructuralAudit": git_binding_established,
        "authoritativeStructuralSuitabilityEstablished": False,
        "basicPitchAuthorized": False,
        "v6Authorized": False,
        "correctnessAuthorized": False,
        "policyBoundary": dict(base.REQUIRED_POLICY_BOUNDARY),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, help="Path to final capture manifest JSON")
    parser.add_argument("--capture-plan", required=True, help="Path to current capture-plan JSON")
    parser.add_argument("--repo-root", default=".", help="Git repository root")
    parser.add_argument("--output", help="Optional deterministic Git-proof result JSON path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    plan = json.loads(Path(args.capture_plan).read_text(encoding="utf-8"))
    result = validate_git_proof(manifest, plan, args.repo_root)
    rendered = base.canonical_json(result) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["gitProofValid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
