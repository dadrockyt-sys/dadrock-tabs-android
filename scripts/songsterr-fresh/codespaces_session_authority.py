#!/usr/bin/env python3

"""Fail-closed Policy C-S authority binding for one active GitHub Codespaces boot session.

This does not modify or enroll the persistent Policy C manifest.  It reuses the
Policy C compute/toolchain probe, then additionally binds authority to:

* GitHub Codespaces execution
* one exact repository commit with a clean worktree
* the current Linux boot session (hashed /proc boot_id)
* the exact Policy C compute/toolchain fingerprint

A stop/restart/rebuild or any compute/toolchain/source drift therefore fails
closed.  Re-enrollment creates a new authority epoch and never inherits model
validation or delivery authority.
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import os
import platform
import subprocess
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
PERSISTENT_MANIFEST = HERE / "pinned_compute_authority_v1.json"
PERSISTENT_VERIFIER = HERE / "verify_pinned_compute_authority.py"
DEFAULT_ROOT = Path(os.environ.get(
    "SONGSTERR_FRESH_SESSION_AUTHORITY_ROOT",
    "/workspaces/.songsterr-fresh-session-authority",
))
DEFAULT_PROBE = DEFAULT_ROOT / "session-probe.json"
DEFAULT_ENROLLMENT = DEFAULT_ROOT / "session-enrollment.json"

POLICY = "POLICY_C_S_CODESPACES_SESSION_AUTHORITY"
PROBE_CONTRACT = "songsterr-fresh-codespaces-session-authority-probe-v1"
ENROLLMENT_CONTRACT = "songsterr-fresh-codespaces-session-authority-enrollment-v1"
VERIFICATION_CONTRACT = "songsterr-fresh-codespaces-session-authority-verification-v1"
ACK_TEXT = "SESSION_BOUND_AUTHORITY_EXPIRES_ON_RESTART"


class SessionAuthorityError(RuntimeError):
    pass


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise SessionAuthorityError("CANONICAL_JSON_FAILED") from exc


def digest_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8", errors="strict")).hexdigest()


def require_sha(value, label, length=64):
    if not isinstance(value, str) or len(value) != length or any(ch not in "0123456789abcdef" for ch in value):
        raise SessionAuthorityError(f"{label}:HEX_DIGEST_REQUIRED")
    return value


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise SessionAuthorityError(f"JSON_LOAD_FAILED:{path}") from exc


def write_json(path, value):
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_persistent_verifier():
    spec = importlib.util.spec_from_file_location("songsterr_fresh_policy_c_verifier", PERSISTENT_VERIFIER)
    if spec is None or spec.loader is None:
        raise SessionAuthorityError("PERSISTENT_VERIFIER_IMPORT_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_git(*args):
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.STDOUT).strip()
    except subprocess.CalledProcessError as exc:
        raise SessionAuthorityError(f"GIT_COMMAND_FAILED:{' '.join(args)}") from exc


def current_source_state():
    commit = run_git("rev-parse", "HEAD")
    require_sha(commit, "sourceCommitSha", length=40)
    dirty = run_git("status", "--porcelain")
    if dirty:
        raise SessionAuthorityError("GIT_WORKTREE_MUST_BE_CLEAN")
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
    if branch != "songsterr-fresh-pipeline-v1":
        raise SessionAuthorityError(f"CANONICAL_BRANCH_REQUIRED:{branch}")
    return commit


def current_boot_id_sha256():
    path = Path("/proc/sys/kernel/random/boot_id")
    if not path.is_file():
        raise SessionAuthorityError("LINUX_BOOT_ID_UNAVAILABLE")
    boot_id = path.read_text(encoding="utf-8").strip()
    if not boot_id:
        raise SessionAuthorityError("LINUX_BOOT_ID_EMPTY")
    # Never write the raw boot id into evidence; only its SHA-256 binding.
    return sha256_text(boot_id)


def memory_total_kb():
    path = Path("/proc/meminfo")
    if not path.is_file():
        raise SessionAuthorityError("MEMINFO_UNAVAILABLE")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("MemTotal:"):
            fields = line.split()
            if len(fields) >= 2 and fields[1].isdigit():
                return int(fields[1])
    raise SessionAuthorityError("MEMTOTAL_UNAVAILABLE")


def require_codespaces_runtime():
    if os.environ.get("CODESPACES", "").lower() != "true":
        raise SessionAuthorityError("GITHUB_CODESPACES_RUNTIME_REQUIRED")
    if platform.system() != "Linux":
        raise SessionAuthorityError("LINUX_REQUIRED")
    if platform.machine().lower() not in {"x86_64", "amd64"}:
        raise SessionAuthorityError(f"X64_REQUIRED:{platform.machine()}")
    cpus = os.cpu_count()
    if not isinstance(cpus, int) or cpus < 4:
        raise SessionAuthorityError(f"MINIMUM_FOUR_LOGICAL_CPUS_REQUIRED:{cpus}")
    total_kb = memory_total_kb()
    if total_kb < 4 * 1024 * 1024:
        raise SessionAuthorityError(f"MINIMUM_FOUR_GIB_RAM_REQUIRED:{total_kb}")
    return cpus, total_kb


def collect_current_state():
    cpus, total_kb = require_codespaces_runtime()
    source_commit = current_source_state()
    verifier = load_persistent_verifier()
    manifest = verifier.validate_manifest(verifier.load_json(PERSISTENT_MANIFEST))
    # Persistent Policy C must remain untouched/un-enrolled for this alternate mode.
    if manifest.get("enrollmentStatus") != "UNENROLLED":
        raise SessionAuthorityError("PERSISTENT_POLICY_C_MUST_REMAIN_UNENROLLED_FOR_SESSION_MODE")
    base_probe = verifier.collect_probe(manifest["authorityId"])
    verifier.validate_probe_prerequisites(manifest, base_probe)
    boot_sha = current_boot_id_sha256()
    session_fingerprint = {
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "sourceCommitSha": source_commit,
        "baseComputeFingerprintSha256": base_probe["fingerprintSha256"],
        "linuxBootIdSha256": boot_sha,
        "machine": platform.machine(),
        "logicalCpuCount": cpus,
        "memoryTotalKb": total_kb,
    }
    session_sha = digest_json(session_fingerprint)
    return {
        "sourceCommitSha": source_commit,
        "baseProbe": base_probe,
        "baseComputeFingerprintSha256": base_probe["fingerprintSha256"],
        "linuxBootIdSha256": boot_sha,
        "sessionFingerprint": session_fingerprint,
        "sessionFingerprintSha256": session_sha,
        "logicalCpuCount": cpus,
        "memoryTotalKb": total_kb,
    }


def build_probe(current):
    return {
        "contract": PROBE_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "status": "SESSION_PROBE_PREREQUISITES_VALID",
        "sourceCommitSha": current["sourceCommitSha"],
        "baseComputeFingerprintSha256": current["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": current["linuxBootIdSha256"],
        "sessionFingerprintSha256": current["sessionFingerprintSha256"],
        "capacity": {
            "logicalCpuCount": current["logicalCpuCount"],
            "memoryTotalKb": current["memoryTotalKb"],
        },
        "containsRawBootId": False,
        "containsMachineId": False,
        "containsNetworkIdentity": False,
        "containsUserIdentity": False,
        "policyBoundary": {
            "probeAloneEnrollsAuthority": False,
            "probeAloneQualifiesSession": False,
            "reEnrollmentInheritsPriorModelValidation": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def build_enrollment(current):
    return {
        "contract": ENROLLMENT_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "enrollmentStatus": "ENROLLED",
        "authorityEpochId": str(uuid.uuid4()),
        "sourceCommitSha": current["sourceCommitSha"],
        "baseComputeFingerprintSha256": current["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": current["linuxBootIdSha256"],
        "sessionFingerprintSha256": current["sessionFingerprintSha256"],
        "enrolledAtUtc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "lifetime": {
            "boundToCurrentLinuxBoot": True,
            "boundToExactSourceCommit": True,
            "boundToExactComputeFingerprint": True,
            "stopRestartRebuildRequiresFreshEnrollment": True,
            "newEnrollmentCreatesNewAuthorityEpoch": True,
        },
        "qualificationRequirement": {
            "minimumDistinctCanaryExecutions": 3,
            "sameAuthorityEpochRequired": True,
            "sameSessionFingerprintRequired": True,
            "sameSourceCommitRequired": True,
            "exactFixedInputIdentityRequired": True,
            "exactOutputIdentityRequired": True,
        },
        "policyBoundary": {
            "enrollmentAloneQualifiesSession": False,
            "reEnrollmentInheritsPriorModelValidation": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def validate_enrollment(enrollment):
    if not isinstance(enrollment, dict):
        raise SessionAuthorityError("ENROLLMENT_OBJECT_REQUIRED")
    if enrollment.get("contract") != ENROLLMENT_CONTRACT or enrollment.get("version") != 1:
        raise SessionAuthorityError("ENROLLMENT_CONTRACT_CHANGED")
    if enrollment.get("policy") != POLICY:
        raise SessionAuthorityError("ENROLLMENT_POLICY_CHANGED")
    if enrollment.get("authorityClass") != "codespaces-linux-boot-session":
        raise SessionAuthorityError("ENROLLMENT_AUTHORITY_CLASS_CHANGED")
    if enrollment.get("enrollmentStatus") != "ENROLLED":
        raise SessionAuthorityError("SESSION_AUTHORITY_NOT_ENROLLED")
    epoch = enrollment.get("authorityEpochId")
    try:
        uuid.UUID(epoch)
    except Exception as exc:
        raise SessionAuthorityError("AUTHORITY_EPOCH_ID_INVALID") from exc
    require_sha(enrollment.get("sourceCommitSha"), "sourceCommitSha", length=40)
    require_sha(enrollment.get("baseComputeFingerprintSha256"), "baseComputeFingerprintSha256")
    require_sha(enrollment.get("linuxBootIdSha256"), "linuxBootIdSha256")
    require_sha(enrollment.get("sessionFingerprintSha256"), "sessionFingerprintSha256")
    lifetime = enrollment.get("lifetime", {})
    for key in (
        "boundToCurrentLinuxBoot",
        "boundToExactSourceCommit",
        "boundToExactComputeFingerprint",
        "stopRestartRebuildRequiresFreshEnrollment",
        "newEnrollmentCreatesNewAuthorityEpoch",
    ):
        if lifetime.get(key) is not True:
            raise SessionAuthorityError(f"SESSION_LIFETIME_GUARD_CHANGED:{key}")
    guards = enrollment.get("policyBoundary", {})
    required = {
        "enrollmentAloneQualifiesSession": False,
        "reEnrollmentInheritsPriorModelValidation": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
        "customerEligibleEvents": 0,
        "referenceTabUsed": False,
        "professionalScorerUsed": False,
        "legacyV143ScorerImported": False,
    }
    for key, expected in required.items():
        if guards.get(key) != expected:
            raise SessionAuthorityError(f"SESSION_POLICY_GUARD_CHANGED:{key}")
    return enrollment


def verify_enrollment_against_current(enrollment, current):
    enrollment = validate_enrollment(enrollment)
    comparisons = {
        "sourceCommitSha": current["sourceCommitSha"],
        "baseComputeFingerprintSha256": current["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": current["linuxBootIdSha256"],
        "sessionFingerprintSha256": current["sessionFingerprintSha256"],
    }
    for key, actual in comparisons.items():
        if enrollment.get(key) != actual:
            raise SessionAuthorityError(f"SESSION_AUTHORITY_DRIFT:{key}")
    return {
        "contract": VERIFICATION_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "status": "CODESPACES_SESSION_AUTHORITY_VERIFIED",
        "authorityEpochId": enrollment["authorityEpochId"],
        "sourceCommitSha": current["sourceCommitSha"],
        "baseComputeFingerprintSha256": current["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": current["linuxBootIdSha256"],
        "sessionFingerprintSha256": current["sessionFingerprintSha256"],
        "authorityVerifiedForCurrentBootSession": True,
        "policyBoundary": {
            "verificationAloneQualifiesSession": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def synthetic_current(source="a" * 40, base="b" * 64, boot="c" * 64):
    fingerprint = {
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "sourceCommitSha": source,
        "baseComputeFingerprintSha256": base,
        "linuxBootIdSha256": boot,
        "machine": "x86_64",
        "logicalCpuCount": 4,
        "memoryTotalKb": 8 * 1024 * 1024,
    }
    return {
        "sourceCommitSha": source,
        "baseComputeFingerprintSha256": base,
        "linuxBootIdSha256": boot,
        "sessionFingerprint": fingerprint,
        "sessionFingerprintSha256": digest_json(fingerprint),
        "logicalCpuCount": 4,
        "memoryTotalKb": 8 * 1024 * 1024,
    }


def run_self_test():
    current = synthetic_current()
    enrollment = build_enrollment(current)
    verified = verify_enrollment_against_current(enrollment, current)
    assert verified["status"] == "CODESPACES_SESSION_AUTHORITY_VERIFIED"
    assert verified["policyBoundary"]["modelValidationComplete"] is False

    drifted_boot = synthetic_current(boot="d" * 64)
    try:
        verify_enrollment_against_current(enrollment, drifted_boot)
    except SessionAuthorityError as exc:
        assert str(exc) in {
            "SESSION_AUTHORITY_DRIFT:linuxBootIdSha256",
            "SESSION_AUTHORITY_DRIFT:sessionFingerprintSha256",
        }
    else:
        raise AssertionError("boot-session drift must fail closed")

    drifted_source = synthetic_current(source="e" * 40)
    try:
        verify_enrollment_against_current(enrollment, drifted_source)
    except SessionAuthorityError as exc:
        assert str(exc) == "SESSION_AUTHORITY_DRIFT:sourceCommitSha"
    else:
        raise AssertionError("source-commit drift must fail closed")

    drifted_compute = synthetic_current(base="f" * 64)
    try:
        verify_enrollment_against_current(enrollment, drifted_compute)
    except SessionAuthorityError as exc:
        assert str(exc) == "SESSION_AUTHORITY_DRIFT:baseComputeFingerprintSha256"
    else:
        raise AssertionError("compute/toolchain drift must fail closed")

    print(json.dumps({
        "contract": VERIFICATION_CONTRACT,
        "selfTest": "PASS",
        "bootDriftFailsClosed": True,
        "sourceCommitDriftFailsClosed": True,
        "computeToolchainDriftFailsClosed": True,
        "reEnrollmentInheritsPriorModelValidation": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    p_probe = sub.add_parser("probe")
    p_probe.add_argument("--output", default=str(DEFAULT_PROBE))

    p_enroll = sub.add_parser("enroll")
    p_enroll.add_argument("--ack", required=True)
    p_enroll.add_argument("--output", default=str(DEFAULT_ENROLLMENT))
    p_enroll.add_argument("--probe-output", default=str(DEFAULT_PROBE))

    p_verify = sub.add_parser("verify")
    p_verify.add_argument("--enrollment", default=str(DEFAULT_ENROLLMENT))
    p_verify.add_argument("--output")

    sub.add_parser("self-test")

    args = parser.parse_args()
    if args.command == "self-test":
        run_self_test()
        return

    if args.command == "probe":
        current = collect_current_state()
        probe = build_probe(current)
        write_json(args.output, probe)
        print(json.dumps({
            "status": probe["status"],
            "sourceCommitSha": probe["sourceCommitSha"],
            "sessionFingerprintSha256": probe["sessionFingerprintSha256"],
            "probeAloneEnrollsAuthority": False,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
        }, sort_keys=True))
        return

    if args.command == "enroll":
        if args.ack != ACK_TEXT:
            raise SessionAuthorityError("EXPLICIT_SESSION_EXPIRY_ACK_REQUIRED")
        current = collect_current_state()
        probe = build_probe(current)
        enrollment = build_enrollment(current)
        write_json(args.probe_output, probe)
        write_json(args.output, enrollment)
        print(json.dumps({
            "status": "CODESPACES_SESSION_AUTHORITY_ENROLLED",
            "authorityEpochId": enrollment["authorityEpochId"],
            "sourceCommitSha": enrollment["sourceCommitSha"],
            "sessionFingerprintSha256": enrollment["sessionFingerprintSha256"],
            "enrollmentAloneQualifiesSession": False,
            "minimumDistinctCanaryExecutions": 3,
            "modelValidationComplete": False,
            "customerEligibleEvents": 0,
        }, sort_keys=True))
        return

    if args.command == "verify":
        current = collect_current_state()
        verification = verify_enrollment_against_current(load_json(args.enrollment), current)
        if args.output:
            write_json(args.output, verification)
        print(json.dumps(verification, sort_keys=True))
        return

    raise SessionAuthorityError("UNKNOWN_COMMAND")


if __name__ == "__main__":
    try:
        main()
    except SessionAuthorityError as exc:
        print(f"CODESPACES_SESSION_AUTHORITY_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
