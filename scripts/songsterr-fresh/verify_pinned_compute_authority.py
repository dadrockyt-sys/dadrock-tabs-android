#!/usr/bin/env python3

"""Fail-closed verifier for Songsterr Fresh Policy C pinned compute authority.

Policy C intentionally changes the execution authority rather than inventing a
floating-point tolerance. A model run is authority-eligible only when it runs on
an explicitly enrolled fixed self-hosted compute surface whose reproducibility
fingerprint exactly matches the branch-tracked manifest.

This is reproducibility binding, not security attestation. The probe deliberately
does not read machine-id, serial numbers, MAC addresses, IP addresses, usernames,
or other host secrets.
"""

import argparse
import contextlib
import copy
import hashlib
import importlib.metadata
import io
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

MANIFEST_CONTRACT = "songsterr-fresh-pinned-compute-authority-v1"
PROBE_CONTRACT = "songsterr-fresh-pinned-compute-authority-probe-v1"
DEFAULT_MANIFEST = Path(__file__).with_name("pinned_compute_authority_v1.json")
EXPECTED_POLICY = "POLICY_C_PINNED_COMPUTE_AUTHORITY"
REQUIRED_GUARDS = {
    "hostedModelRunsRemainMeasurementOnly": True,
    "fallbackToUnenrolledHardwareAllowed": False,
    "authorityDriftFailsClosed": True,
    "authorityIsReproducibilityScopeNotSecurityAttestation": True,
    "referenceTabUsed": False,
    "professionalScorerUsed": False,
    "legacyV143ScorerImported": False,
    "modelValidationComplete": False,
    "mayAdvanceDelivery": False,
    "durationAuthorityChanged": False,
    "customerEligibleEvents": 0,
}
PACKAGE_NAMES = (
    "numpy",
    "torch",
    "huggingface-hub",
    "safetensors",
    "sphn",
    "demucs",
    "basic-pitch",
    "librosa",
    "soundfile",
    "tflite-runtime",
)
ENV_KEYS = (
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
    "PYTHONHASHSEED",
)


class AuthorityError(RuntimeError):
    pass


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise AuthorityError("CANONICAL_JSON_FAILED") from exc


def digest_json(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_file(path):
    target = Path(path)
    if not target.is_file():
        return None
    digest = hashlib.sha256()
    with target.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(
                handle,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    AuthorityError(f"NONSTANDARD_JSON_CONSTANT:{value}")
                ),
            )
    except AuthorityError:
        raise
    except Exception as exc:
        raise AuthorityError(f"JSON_LOAD_FAILED:{path}") from exc


def require_sha256(value, label, *, nullable=False):
    if value is None and nullable:
        return None
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
        raise AuthorityError(f"{label}:SHA256_REQUIRED")
    return value


def command_output(command):
    executable = shutil.which(command[0])
    if not executable:
        return {"available": False, "executableSha256": None, "firstLine": None}
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=15,
        )
        text = result.stdout.strip()
    except Exception as exc:
        return {
            "available": True,
            "executableSha256": sha256_file(executable),
            "firstLine": None,
            "probeErrorType": type(exc).__name__,
        }
    return {
        "available": True,
        "executableSha256": sha256_file(executable),
        "firstLine": text.splitlines()[0] if text else "",
    }


def cpu_fingerprint():
    wanted = {
        "vendor_id": None,
        "model name": None,
        "cpu family": None,
        "model": None,
        "stepping": None,
        "microcode": None,
    }
    flags = []
    cpuinfo = Path("/proc/cpuinfo")
    if cpuinfo.is_file():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            if key in wanted and wanted[key] is None:
                wanted[key] = value
            if key in {"flags", "Features"} and not flags:
                flags = sorted(set(value.split()))
    return {
        "machine": platform.machine(),
        "processor": platform.processor() or None,
        "logicalCpuCount": os.cpu_count(),
        "vendorId": wanted["vendor_id"],
        "modelName": wanted["model name"],
        "cpuFamily": wanted["cpu family"],
        "cpuModel": wanted["model"],
        "stepping": wanted["stepping"],
        "microcode": wanted["microcode"],
        "cpuFlagsSha256": sha256_text("\n".join(flags)),
    }


def package_versions():
    versions = {}
    for name in PACKAGE_NAMES:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def installed_distribution_lock():
    rows = []
    for dist in importlib.metadata.distributions():
        raw_name = dist.metadata.get("Name") or ""
        normalized_name = raw_name.strip().lower().replace("_", "-").replace(".", "-")
        record = dist.read_text("RECORD")
        direct_url = dist.read_text("direct_url.json")
        installer = dist.read_text("INSTALLER")
        rows.append({
            "name": normalized_name,
            "version": str(dist.version),
            "recordSha256": sha256_text(record) if record is not None else None,
            "directUrlSha256": sha256_text(direct_url) if direct_url is not None else None,
            "installerSha256": sha256_text(installer) if installer is not None else None,
        })
    rows.sort(key=canonical_json)
    return {"distributionCount": len(rows), "sha256": digest_json(rows)}


def numeric_library_configuration():
    result = {
        "numpyConfigSha256": None,
        "torchConfigSha256": None,
        "torchVersion": None,
    }
    try:
        import numpy as np
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            np.show_config()
        result["numpyConfigSha256"] = sha256_text(stream.getvalue())
    except Exception as exc:
        result["numpyConfigErrorType"] = type(exc).__name__
    try:
        import torch
        result["torchVersion"] = str(torch.__version__)
        result["torchConfigSha256"] = sha256_text(torch.__config__.show())
    except Exception as exc:
        result["torchConfigErrorType"] = type(exc).__name__
    return result


def collect_probe(authority_id="songsterr-fresh-authority-v1"):
    libc_name, libc_version = platform.libc_ver()
    executable = Path(sys.executable).resolve()
    fingerprint = {
        "authorityId": authority_id,
        "hardware": cpu_fingerprint(),
        "operatingSystem": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "libcName": libc_name or None,
            "libcVersion": libc_version or None,
        },
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executableSha256": sha256_file(executable),
        },
        "toolchain": {
            "node": command_output(["node", "--version"]),
            "ffmpeg": command_output(["ffmpeg", "-version"]),
        },
        "packages": package_versions(),
        "pythonDistributionLock": installed_distribution_lock(),
        "numericLibraries": numeric_library_configuration(),
        "deterministicEnvironment": {key: os.environ.get(key) for key in ENV_KEYS},
    }
    return {
        "contract": PROBE_CONTRACT,
        "version": 1,
        "containsMachineId": False,
        "containsNetworkIdentity": False,
        "containsUserIdentity": False,
        "fingerprint": fingerprint,
        "fingerprintSha256": digest_json(fingerprint),
        "policyBoundary": {
            "probeAloneEnrollsAuthority": False,
            "probeAloneValidatesModel": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def validate_manifest(manifest):
    if not isinstance(manifest, dict):
        raise AuthorityError("MANIFEST_OBJECT_REQUIRED")
    if manifest.get("contract") != MANIFEST_CONTRACT or manifest.get("version") != 1:
        raise AuthorityError("MANIFEST_CONTRACT_CHANGED")
    if manifest.get("policy") != EXPECTED_POLICY:
        raise AuthorityError("MANIFEST_POLICY_CHANGED")
    if manifest.get("authorityClass") != "fixed-self-hosted-machine":
        raise AuthorityError("AUTHORITY_CLASS_CHANGED")
    authority_id = manifest.get("authorityId")
    if not isinstance(authority_id, str) or not authority_id:
        raise AuthorityError("AUTHORITY_ID_REQUIRED")
    labels = manifest.get("requiredRunnerLabels")
    if not isinstance(labels, list) or labels != ["self-hosted", "linux", "x64", authority_id]:
        raise AuthorityError("REQUIRED_RUNNER_LABELS_CHANGED")
    required_env = manifest.get("requiredEnvironment")
    if not isinstance(required_env, dict) or required_env != {key: "1" for key in ENV_KEYS[:-1]} | {"PYTHONHASHSEED": "0"}:
        raise AuthorityError("REQUIRED_DETERMINISTIC_ENVIRONMENT_CHANGED")

    expected_packages = {
        "numpy": "1.26.4",
        "torch": "2.14.0",
        "huggingface-hub": "1.30.0",
        "safetensors": "0.8.0",
        "sphn": "0.2.1",
        "demucs": "4.1.0",
        "basic-pitch": "0.4.0",
        "librosa": "0.11.0",
        "soundfile": "0.13.1",
        "tflite-runtime": "2.14.0",
    }
    if manifest.get("requiredPackageVersions") != expected_packages:
        raise AuthorityError("REQUIRED_PACKAGE_VERSION_SET_CHANGED")

    fixed = manifest.get("fixedModelPath")
    if not isinstance(fixed, dict):
        raise AuthorityError("FIXED_MODEL_PATH_REQUIRED")
    if fixed.get("fixtureGitBlob") != "4dd709e3fa177b4daeed71ca97f0199757729d4b":
        raise AuthorityError("FIXTURE_IDENTITY_CHANGED")
    require_sha256(fixed.get("decodedSeparationWavSha256"), "decodedSeparationWavSha256")
    if fixed.get("structureIdentity") != "fnv1a32:2f493225":
        raise AuthorityError("STRUCTURE_IDENTITY_CHANGED")
    demucs = fixed.get("demucs", {})
    expected_demucs = {
        "packageVersion": "4.1.0",
        "modelName": "htdemucs_6s",
        "device": "cpu",
        "shifts": 0,
        "overlap": 0.25,
        "segmentSeconds": 7,
        "assetSha256": "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411",
    }
    if demucs != expected_demucs:
        raise AuthorityError("DEMUCS_CONTRACT_CHANGED")
    basic_pitch = fixed.get("basicPitch", {})
    expected_bp = {
        "packageVersion": "0.4.0",
        "minimumMidi": 40,
        "maximumMidi": 88,
        "onsetThreshold": 0.5,
        "frameThreshold": 0.3,
        "minimumNoteLengthMs": 127.7,
    }
    if basic_pitch != expected_bp:
        raise AuthorityError("BASIC_PITCH_CONTRACT_CHANGED")

    repro = manifest.get("reproducibilityRequirement")
    expected_repro = {
        "minimumSeparateCanaryRuns": 3,
        "sameSourceCommitRequired": True,
        "sameAuthorityFingerprintRequired": True,
        "exactGuitarStemSha256Required": True,
        "exactNoteInferenceSha256Required": True,
        "exactActivationBundleSha256Required": True,
        "exactDecisionSurfaceSha256Required": True,
        "exactCanonicalEvidenceSha256Required": True,
    }
    if repro != expected_repro:
        raise AuthorityError("REPRODUCIBILITY_REQUIREMENT_CHANGED")
    policy = manifest.get("policyBoundary")
    if not isinstance(policy, dict):
        raise AuthorityError("POLICY_BOUNDARY_REQUIRED")
    for key, expected in REQUIRED_GUARDS.items():
        if policy.get(key) != expected:
            raise AuthorityError(f"POLICY_GUARD_CHANGED:{key}")

    state = manifest.get("enrollmentStatus")
    enrolled = manifest.get("enrolledFingerprint")
    enrolled_sha = manifest.get("enrolledFingerprintSha256")
    if state == "UNENROLLED":
        if enrolled is not None or enrolled_sha is not None:
            raise AuthorityError("UNENROLLED_MANIFEST_MUST_NOT_CONTAIN_FINGERPRINT")
    elif state == "ENROLLED":
        if not isinstance(enrolled, dict):
            raise AuthorityError("ENROLLED_FINGERPRINT_OBJECT_REQUIRED")
        require_sha256(enrolled_sha, "enrolledFingerprintSha256")
        if digest_json(enrolled) != enrolled_sha:
            raise AuthorityError("ENROLLED_FINGERPRINT_DIGEST_MISMATCH")
        if enrolled.get("authorityId") != authority_id:
            raise AuthorityError("ENROLLED_AUTHORITY_ID_MISMATCH")
    else:
        raise AuthorityError("ENROLLMENT_STATUS_INVALID")
    return manifest


def validate_probe_prerequisites(manifest, probe):
    if probe.get("contract") != PROBE_CONTRACT or probe.get("version") != 1:
        raise AuthorityError("PROBE_CONTRACT_CHANGED")
    fingerprint = probe.get("fingerprint")
    if not isinstance(fingerprint, dict):
        raise AuthorityError("PROBE_FINGERPRINT_REQUIRED")
    if digest_json(fingerprint) != probe.get("fingerprintSha256"):
        raise AuthorityError("PROBE_FINGERPRINT_DIGEST_MISMATCH")
    if fingerprint.get("authorityId") != manifest.get("authorityId"):
        raise AuthorityError("PROBE_AUTHORITY_ID_MISMATCH")
    env = fingerprint.get("deterministicEnvironment")
    if env != manifest.get("requiredEnvironment"):
        raise AuthorityError("DETERMINISTIC_ENVIRONMENT_MISMATCH")
    packages = fingerprint.get("packages")
    if not isinstance(packages, dict):
        raise AuthorityError("PACKAGE_VERSION_MAP_REQUIRED")
    if packages != manifest.get("requiredPackageVersions"):
        raise AuthorityError("PINNED_PACKAGE_VERSION_SET_MISMATCH")
    distribution_lock = fingerprint.get("pythonDistributionLock")
    if not isinstance(distribution_lock, dict):
        raise AuthorityError("PYTHON_DISTRIBUTION_LOCK_REQUIRED")
    count = distribution_lock.get("distributionCount")
    if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
        raise AuthorityError("PYTHON_DISTRIBUTION_COUNT_INVALID")
    require_sha256(distribution_lock.get("sha256"), "pythonDistributionLock.sha256")
    python = fingerprint.get("python", {})
    require_sha256(python.get("executableSha256"), "python.executableSha256")
    tools = fingerprint.get("toolchain", {})
    for tool in ("node", "ffmpeg"):
        item = tools.get(tool, {})
        if item.get("available") is not True:
            raise AuthorityError(f"REQUIRED_TOOL_UNAVAILABLE:{tool}")
        require_sha256(item.get("executableSha256"), f"toolchain.{tool}.executableSha256")
    numeric = fingerprint.get("numericLibraries", {})
    require_sha256(numeric.get("numpyConfigSha256"), "numericLibraries.numpyConfigSha256")
    require_sha256(numeric.get("torchConfigSha256"), "numericLibraries.torchConfigSha256")
    return fingerprint


def verify_probe(manifest, probe):
    manifest = validate_manifest(manifest)
    fingerprint = validate_probe_prerequisites(manifest, probe)
    if manifest["enrollmentStatus"] != "ENROLLED":
        raise AuthorityError("AUTHORITY_UNENROLLED")
    if fingerprint != manifest["enrolledFingerprint"]:
        raise AuthorityError("AUTHORITY_FINGERPRINT_DRIFT")
    if probe["fingerprintSha256"] != manifest["enrolledFingerprintSha256"]:
        raise AuthorityError("AUTHORITY_FINGERPRINT_DIGEST_DRIFT")
    return {
        "contract": MANIFEST_CONTRACT,
        "authorityId": manifest["authorityId"],
        "status": "PINNED_COMPUTE_AUTHORITY_VERIFIED",
        "fingerprintSha256": probe["fingerprintSha256"],
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
    }


def synthetic_fingerprint():
    return {
        "authorityId": "songsterr-fresh-authority-v1",
        "hardware": {
            "machine": "x86_64", "processor": "synthetic", "logicalCpuCount": 8,
            "vendorId": "Synthetic", "modelName": "Fixed CPU", "cpuFamily": "6",
            "cpuModel": "1", "stepping": "1", "microcode": "0x1",
            "cpuFlagsSha256": "1" * 64,
        },
        "operatingSystem": {
            "system": "Linux", "release": "fixed", "version": "fixed",
            "libcName": "glibc", "libcVersion": "fixed",
        },
        "python": {"version": "3.10.0", "implementation": "CPython", "executableSha256": "2" * 64},
        "toolchain": {
            "node": {"available": True, "executableSha256": "3" * 64, "firstLine": "v22.0.0"},
            "ffmpeg": {"available": True, "executableSha256": "4" * 64, "firstLine": "ffmpeg fixed"},
        },
        "packages": {
            "numpy": "1.26.4", "torch": "2.14.0", "huggingface-hub": "1.30.0",
            "safetensors": "0.8.0", "sphn": "0.2.1", "demucs": "4.1.0",
            "basic-pitch": "0.4.0", "librosa": "0.11.0", "soundfile": "0.13.1",
            "tflite-runtime": "2.14.0",
        },
        "pythonDistributionLock": {"distributionCount": 42, "sha256": "7" * 64},
        "numericLibraries": {"numpyConfigSha256": "5" * 64, "torchConfigSha256": "6" * 64, "torchVersion": "2.14.0"},
        "deterministicEnvironment": {
            "OMP_NUM_THREADS": "1", "MKL_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
            "NUMEXPR_NUM_THREADS": "1", "PYTHONHASHSEED": "0",
        },
    }


def synthetic_manifest():
    base = load_json(DEFAULT_MANIFEST)
    fingerprint = synthetic_fingerprint()
    base["enrollmentStatus"] = "ENROLLED"
    base["enrolledFingerprint"] = copy.deepcopy(fingerprint)
    base["enrolledFingerprintSha256"] = digest_json(fingerprint)
    return base


def run_self_test():
    unenrolled = load_json(DEFAULT_MANIFEST)
    validate_manifest(unenrolled)
    fingerprint = synthetic_fingerprint()
    probe = {
        "contract": PROBE_CONTRACT,
        "version": 1,
        "fingerprint": fingerprint,
        "fingerprintSha256": digest_json(fingerprint),
    }
    try:
        verify_probe(unenrolled, probe)
    except AuthorityError as exc:
        assert str(exc) == "AUTHORITY_UNENROLLED"
    else:
        raise AssertionError("unenrolled authority must fail closed")

    enrolled = synthetic_manifest()
    verified = verify_probe(enrolled, probe)
    assert verified["status"] == "PINNED_COMPUTE_AUTHORITY_VERIFIED"
    assert verified["modelValidationComplete"] is False

    hardware_drift = copy.deepcopy(probe)
    hardware_drift["fingerprint"]["hardware"]["microcode"] = "0x2"
    hardware_drift["fingerprintSha256"] = digest_json(hardware_drift["fingerprint"])
    try:
        verify_probe(enrolled, hardware_drift)
    except AuthorityError as exc:
        assert str(exc) == "AUTHORITY_FINGERPRINT_DRIFT"
    else:
        raise AssertionError("hardware drift must fail closed")

    software_drift = copy.deepcopy(probe)
    software_drift["fingerprint"]["packages"]["numpy"] = "1.26.5"
    software_drift["fingerprintSha256"] = digest_json(software_drift["fingerprint"])
    try:
        verify_probe(enrolled, software_drift)
    except AuthorityError as exc:
        assert str(exc) == "PINNED_PACKAGE_VERSION_SET_MISMATCH"
    else:
        raise AssertionError("software drift must fail closed")

    transitive_drift = copy.deepcopy(probe)
    transitive_drift["fingerprint"]["pythonDistributionLock"]["sha256"] = "8" * 64
    transitive_drift["fingerprintSha256"] = digest_json(transitive_drift["fingerprint"])
    try:
        verify_probe(enrolled, transitive_drift)
    except AuthorityError as exc:
        assert str(exc) == "AUTHORITY_FINGERPRINT_DRIFT"
    else:
        raise AssertionError("transitive distribution drift must fail closed")

    print(json.dumps({
        "contract": MANIFEST_CONTRACT,
        "selfTest": "PASS",
        "unenrolledFailsClosed": True,
        "hardwareDriftFailsClosed": True,
        "softwareDriftFailsClosed": True,
        "transitiveDistributionDriftFailsClosed": True,
        "modelValidationComplete": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--validate-manifest", action="store_true")
    parser.add_argument("--probe-output")
    parser.add_argument("--verify-current", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return

    manifest = validate_manifest(load_json(args.manifest))
    if args.validate_manifest:
        print(json.dumps({
            "contract": MANIFEST_CONTRACT,
            "manifest": "VALID",
            "enrollmentStatus": manifest["enrollmentStatus"],
            "modelValidationComplete": False,
        }, sort_keys=True))
        if not args.probe_output and not args.verify_current:
            return

    if args.probe_output or args.verify_current:
        probe = collect_probe(manifest["authorityId"])
        if args.probe_output:
            Path(args.probe_output).write_text(json.dumps(probe, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validate_probe_prerequisites(manifest, probe)
        if args.verify_current:
            print(json.dumps(verify_probe(manifest, probe), sort_keys=True))
        else:
            print(json.dumps({
                "contract": PROBE_CONTRACT,
                "probe": "PREREQUISITES_VALID",
                "fingerprintSha256": probe["fingerprintSha256"],
                "enrollmentStatus": manifest["enrollmentStatus"],
                "probeAloneEnrollsAuthority": False,
            }, sort_keys=True))
        return

    if not args.validate_manifest:
        parser.error("choose --validate-manifest, --probe-output, --verify-current, or --self-test")


if __name__ == "__main__":
    try:
        main()
    except AuthorityError as exc:
        print(f"PINNED_COMPUTE_AUTHORITY_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
