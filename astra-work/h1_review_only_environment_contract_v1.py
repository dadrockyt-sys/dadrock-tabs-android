"""Read-only synthetic-environment contract checker, NOT an execution environment.

No pip, network, Docker, GitHub Actions, model imports, media, optimizer,
repository changes, or launch receipt. A matching host is never clearance.
"""
from __future__ import annotations

import argparse
from importlib import metadata
import json
from pathlib import Path
import platform
import re
import sys

SCHEMA = "astra-h1-review-only-environment-contract-v1"
TARGET = {
    "operatingSystemId": "ubuntu", "operatingSystemVersion": "22.04",
    "architecture": "x86_64", "python": "3.10.15", "torch": "1.11.0+cpu",
    "numpy": "1.21.6", "cpuOnly": True,
}
ANCHORS = {
    "requirementsLockGitBlob": "174a5016cfe9e6c00816d2171210aa84c66081a8",
    "dormantWorkflowGitBlob": "90e8168fc1ca40738ba07291ca1001a36718f4e3",
    "draftSourceLockGitBlob": "f778836783c831224b5467d304353b9c73f0496e",
}
FORBIDDEN_ACTIONS = (
    "createOrEditBlockedLaunchJson", "triggerGitHubActions",
    "realP1P2P3OrProtectedMedia", "trainingOrRealInference", "paidCompute",
    "externalEnvironmentSafetyBypass", "modelWeightExport", "useAnySecretsOrTokens",
    "alterFrozenScienceOrProduction",
)
EVIDENCE = (
    "writtenSpecificPermissionForSyntheticOnlyComparableMeasurementSetting",
    "runnerImageAndProcessorIdentityAndSourceSHA256",
    "pinnedVersionsImportedAndCudaActuallyDisabled",
    "immutableExternalAMTToolSourceAndInternalDependencyReview",
    "verifiedTenModuleNoMediaSuiteInPermittedFullCheckout",
    "twoStepFullModelSyntheticOnlyParityInPinnedEnvironment",
    "sixActualRunnerDiskAndRamQuantitiesAndProvenance",
    "twelveDefensibleH1StageUpperDurationsAndReserve",
    "independentGlobalAtomicSingleUseSecurityApproval",
    "explicitWrittenSupportDispositionBeforeRestrictedOperation",
)


def validate_contract(c: dict) -> None:
    if not isinstance(c, dict) or c.get("schema") != SCHEMA:
        raise ValueError("UNRECOGNIZED_CONTRACT_SCHEMA")
    if c.get("state") != "DESIGN_ONLY_NO_RUNNER_PROVISIONED" or c.get("launchPermission") is not False:
        raise ValueError("CONTRACT_MUST_REMAIN_UNPROVISIONED_AND_NONAUTHORIZING")
    if c.get("branch") != "astra-work" or c.get("target") != TARGET or c.get("sourceAnchors") != ANCHORS:
        raise ValueError("TARGET_OR_SOURCE_IDENTITY_DRIFT")
    p = c.get("prohibitions")
    if not isinstance(p, dict) or set(p) != set(FORBIDDEN_ACTIONS) or any(p[k] is not True for k in FORBIDDEN_ACTIONS):
        raise ValueError("SAFETY_BOUNDARY_RELAXED")
    if c.get("requiredIndependentEvidence") != list(EVIDENCE):
        raise ValueError("INDEPENDENT_EVIDENCE_REQUIREMENTS_CHANGED")


def _os_release(path: Path = Path("/etc/os-release")) -> tuple[str, str]:
    try:
        fields = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                fields[k] = v.strip().strip('"').strip("'")
        return fields.get("ID", "UNAVAILABLE"), fields.get("VERSION_ID", "UNAVAILABLE")
    except OSError:
        return "UNAVAILABLE", "UNAVAILABLE"


def _version(package: str) -> str:
    try:
        return metadata.version(package)
    except metadata.PackageNotFoundError:
        return "UNAVAILABLE"


def inspect_local() -> dict:
    """Environment *hints*, not proof of imported versions, CPU-only execution or runner parity."""
    os_id, os_version = _os_release()
    return {
        "operatingSystemId": os_id,
        "operatingSystemVersion": os_version,
        "architecture": platform.machine(),
        "python": ".".join(map(str, sys.version_info[:3])),
        "torch": _version("torch"),
        "numpy": _version("numpy"),
        "cpuOnly": None,
    }


def review(c: dict, local: dict) -> dict:
    validate_contract(c)
    if not isinstance(local, dict):
        raise ValueError("INVALID_HOST_EVIDENCE")
    comparisons = {k: (type(local.get(k)) is type(v) and local.get(k) == v)
                   for k, v in TARGET.items()}
    # No automatic model/GPU execution: cpuOnly is deliberately UNKNOWN.
    return {
        "schema": "astra-h1-review-only-environment-compatibility-v1",
        "environmentConfiguration": c["state"],
        "observedLocalEnvironment": {k: local.get(k, "UNAVAILABLE") for k in TARGET},
        "expectedEnvironment": dict(TARGET),
        "literalPinMatches": comparisons,
        "allLiteralPinsMatch": all(comparisons.values()),
        "importedRuntimeAndCudaVerified": False,
        "independentlyAuthorizedMeasurementSetting": False,
        "actualRunnerPeakDiskAndRamMeasured": False,
        "allTwelveDurationBoundsMeasured": False,
        "globalAtomicOneUseApproved": False,
        "supportExecutionPermission": False,
        "readiness": "NO_GO_INSUFFICIENT_EVIDENCE",
        "launchPermission": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--contract", required=True, type=Path)
    opts = ap.parse_args()
    doc = json.loads(opts.contract.read_text(encoding="utf-8"))
    result = review(doc, inspect_local())
    print(json.dumps(result, sort_keys=True, indent=2))
    # This exit code never authorizes work; success only means syntax verified.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
