#!/usr/bin/env python3
"""Execution wrapper for the frozen Songsterr Fresh GuitarSet V3 validation.

This wrapper does not score audio or change the preregistered method. It binds
one real external-validation execution to an exact clean Git source state,
pinned runtime, implementation identities, and the complete core V3 result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path

CONTRACT = "songsterr-fresh-guitarset-external-validation-execution-v3"
VERSION = 3
EXPECTED_BRANCH = "songsterr-fresh-pipeline-v1"
CORE_CONTRACT = "songsterr-fresh-guitarset-external-validation-v3"

REQUIRED_PYTHON_MAJOR_MINOR = (3, 10)
REQUIRED_PACKAGES = {
    "basic-pitch": "0.4.0",
    "numpy": "1.26.4",
    "soundfile": "0.13.1",
}
OPTIONAL_RECORDED_PACKAGES = (
    "scipy",
    "tensorflow",
    "tensorflow-cpu",
    "librosa",
)

IDENTITY_PATHS = (
    "scripts/songsterr-fresh/run_external_guitarset_validation_v3.py",
    "scripts/songsterr-fresh/external_guitarset_validation_v3.py",
    "scripts/songsterr-fresh/independent_pitch_corroboration_v2.py",
    "scripts/songsterr-fresh/transcribe_isolated_guitar_basic_pitch.py",
    "docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V3.md",
    "docs/checkpoints/SONGSTERR_FRESH_EXTERNAL_GUITARSET_VALIDATION_V3.md",
)


class ExecutionError(RuntimeError):
    pass


def canonical_json(value) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise ExecutionError(
            f"GIT_COMMAND_FAILED:{' '.join(args)}:{completed.stderr.strip()}"
        )
    return completed.stdout.strip()


def source_state(repo_root: Path) -> dict:
    branch = run_git(repo_root, "branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        raise ExecutionError(f"SOURCE_BRANCH_CHANGED:{branch}!={EXPECTED_BRANCH}")
    commit = run_git(repo_root, "rev-parse", "HEAD")
    if len(commit) != 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise ExecutionError("SOURCE_COMMIT_SHA_INVALID")
    status = run_git(repo_root, "status", "--porcelain")
    if status:
        raise ExecutionError("SOURCE_WORKTREE_MUST_BE_CLEAN")
    return {
        "branch": branch,
        "commitSha": commit,
        "worktreeClean": True,
    }


def distribution_version(name: str) -> str | None:
    try:
        return package_version(name)
    except PackageNotFoundError:
        return None


def runtime_state() -> dict:
    if sys.version_info[:2] != REQUIRED_PYTHON_MAJOR_MINOR:
        raise ExecutionError(
            "PYTHON_RUNTIME_CHANGED:"
            f"{sys.version_info.major}.{sys.version_info.minor}"
            f"!={REQUIRED_PYTHON_MAJOR_MINOR[0]}.{REQUIRED_PYTHON_MAJOR_MINOR[1]}"
        )
    packages = {}
    for name, expected in REQUIRED_PACKAGES.items():
        actual = distribution_version(name)
        if actual != expected:
            raise ExecutionError(f"PACKAGE_VERSION_CHANGED:{name}:{actual}!={expected}")
        packages[name] = actual
    for name in OPTIONAL_RECORDED_PACKAGES:
        actual = distribution_version(name)
        if actual is not None:
            packages[name] = actual
    return {
        "python": platform.python_version(),
        "pythonImplementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages": dict(sorted(packages.items())),
    }


def implementation_identities(repo_root: Path) -> dict:
    identities = {}
    for relative in IDENTITY_PATHS:
        path = repo_root / relative
        if not path.is_file():
            raise ExecutionError(f"IMPLEMENTATION_FILE_MISSING:{relative}")
        identities[relative] = sha256_file(path)
    return identities


def require_outside_repo(repo_root: Path, path: Path, label: str) -> None:
    resolved_repo = repo_root.resolve()
    resolved = path.resolve()
    if resolved == resolved_repo or resolved_repo in resolved.parents:
        raise ExecutionError(f"{label}_MUST_BE_OUTSIDE_REPOSITORY:{resolved}")


def validate_core_result(core: dict) -> None:
    if core.get("contract") != CORE_CONTRACT or core.get("version") != 3:
        raise ExecutionError("CORE_RESULT_CONTRACT_CHANGED")
    if core.get("status") != "V3_EXTERNAL_VALIDATION_COMPLETE":
        raise ExecutionError("CORE_RESULT_INCOMPLETE")
    hard_guards = core.get("hardGuards", {})
    expected_false = (
        "usesProtectedSong",
        "usesReferenceTab",
        "usesProfessionalScorer",
        "importsArchivedV143Logic",
        "usesGoatResearch",
        "usesBasicPitchConfidenceForClassification",
        "usesBasicPitchNoteEndForClassification",
        "usesDurationForClassification",
        "changesPitchIdentity",
        "changesOnsetIdentity",
        "dropsDecodedEvents",
        "tunesFrozenV2",
        "setsModelValidationComplete",
        "setsCustomerEligibility",
        "changesDurationAuthority",
    )
    for field in expected_false:
        if hard_guards.get(field) is not False:
            raise ExecutionError(f"CORE_HARD_GUARD_CHANGED:{field}")
    policy = core.get("policyBoundary", {})
    required_policy = {
        "admissionDecisionMade": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
        "separatePolicyReviewRequired": True,
    }
    for field, expected in required_policy.items():
        if policy.get(field) != expected:
            raise ExecutionError(f"CORE_POLICY_BOUNDARY_CHANGED:{field}")


def run_self_test(repo_root: Path) -> None:
    identities = implementation_identities(repo_root)
    source = source_state(repo_root)
    assert source["branch"] == EXPECTED_BRANCH
    assert source["worktreeClean"] is True
    assert len(source["commitSha"]) == 40
    assert len(identities) == len(IDENTITY_PATHS)
    assert REQUIRED_PACKAGES == {
        "basic-pitch": "0.4.0",
        "numpy": "1.26.4",
        "soundfile": "0.13.1",
    }
    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "selfTest": "PASS",
                "officialEvaluationExecuted": False,
                "guitarsetEvaluated": False,
                "protectedSongEvaluated": False,
                "sourceCommitBound": True,
                "runtimePinDeclared": True,
                "modelValidationComplete": False,
                "customerEligibleEvents": 0,
            }
        )
    )


def run_official(args: argparse.Namespace) -> dict:
    repo_root = Path(args.repo_root).resolve()
    annotation_zip = Path(args.annotation_zip).resolve()
    audio_zip = Path(args.audio_mic_zip).resolve()
    work_dir = Path(args.work_dir).resolve()
    output = Path(args.output).resolve()

    require_outside_repo(repo_root, work_dir, "WORK_DIR")
    require_outside_repo(repo_root, output, "OUTPUT")
    if output.exists():
        raise ExecutionError(f"OUTPUT_ALREADY_EXISTS:{output}")

    source = source_state(repo_root)
    runtime = runtime_state()
    identities = implementation_identities(repo_root)

    output.parent.mkdir(parents=True, exist_ok=True)
    core_output = output.with_name(f"{output.stem}.core.json")
    if core_output.exists():
        raise ExecutionError(f"CORE_OUTPUT_ALREADY_EXISTS:{core_output}")

    harness = repo_root / "scripts/songsterr-fresh/external_guitarset_validation_v3.py"
    command = [
        sys.executable,
        str(harness),
        "--repo-root",
        str(repo_root),
        "--annotation-zip",
        str(annotation_zip),
        "--audio-mic-zip",
        str(audio_zip),
        "--work-dir",
        str(work_dir),
        "--output",
        str(core_output),
        "--python-executable",
        sys.executable,
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if completed.returncode != 0:
        print(completed.stdout, end="", file=sys.stderr)
        raise ExecutionError(f"CORE_VALIDATION_EXECUTION_FAILED:{completed.returncode}")

    try:
        core = json.loads(core_output.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ExecutionError("CORE_RESULT_LOAD_FAILED") from exc
    validate_core_result(core)

    source_after = source_state(repo_root)
    if source_after != source:
        raise ExecutionError("SOURCE_STATE_CHANGED_DURING_EVALUATION")
    runtime_after = runtime_state()
    if runtime_after != runtime:
        raise ExecutionError("RUNTIME_STATE_CHANGED_DURING_EVALUATION")

    result = {
        "contract": CONTRACT,
        "version": VERSION,
        "status": "V3_EXTERNAL_VALIDATION_EXECUTION_COMPLETE",
        "source": source,
        "runtime": runtime,
        "implementationSha256": identities,
        "coreResult": core,
        "coreResultSha256": sha256_file(core_output),
        "coreResultPath": str(core_output),
        "policyBoundary": {
            "externalValidationPassed": bool(
                core.get("policyBoundary", {}).get("externalValidationPassed")
            ),
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "separatePolicyReviewRequired": True,
        },
    }
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(completed.stdout, end="")
    print(
        canonical_json(
            {
                "contract": CONTRACT,
                "output": str(output),
                "sourceCommitSha": source["commitSha"],
                "externalValidationPassed": result["policyBoundary"][
                    "externalValidationPassed"
                ],
                "modelValidationComplete": False,
                "customerEligibleEvents": 0,
                "mayAdvanceDelivery": False,
                "separatePolicyReviewRequired": True,
            }
        )
    )
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--annotation-zip")
    parser.add_argument("--audio-mic-zip")
    parser.add_argument("--work-dir")
    parser.add_argument("--output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    if args.self_test:
        run_self_test(repo_root)
        return 0
    required = (
        args.annotation_zip,
        args.audio_mic_zip,
        args.work_dir,
        args.output,
    )
    if not all(required):
        raise ExecutionError(
            "USAGE_REQUIRES_ANNOTATION_ZIP_AUDIO_MIC_ZIP_WORK_DIR_OUTPUT"
        )
    run_official(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ExecutionError as exc:
        print(f"V3_EXTERNAL_EXECUTION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
