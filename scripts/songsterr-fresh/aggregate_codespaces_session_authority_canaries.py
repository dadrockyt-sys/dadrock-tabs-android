#!/usr/bin/env python3

"""Aggregate Policy C-S canaries for exactly one active Codespaces authority epoch."""

import argparse
import json
import sys
from pathlib import Path

POLICY = "POLICY_C_S_CODESPACES_SESSION_AUTHORITY"
CANARY_CONTRACT = "songsterr-fresh-codespaces-session-authority-canary-v1"
CONTRACT = "songsterr-fresh-codespaces-session-authority-qualification-v1"
EXACT_FIELDS = (
    "guitarStemSha256",
    "noteInferenceSha256",
    "activationBundleSha256",
    "decisionSurfaceSha256",
    "canonicalEvidenceSha256",
    "eventCount",
)


class AggregateError(RuntimeError):
    pass


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        raise AggregateError(f"JSON_LOAD_FAILED:{path}") from exc


def validate_canary(canary, label):
    if not isinstance(canary, dict) or canary.get("contract") != CANARY_CONTRACT or canary.get("version") != 1:
        raise AggregateError(f"{label}:CANARY_CONTRACT_CHANGED")
    if canary.get("policy") != POLICY:
        raise AggregateError(f"{label}:POLICY_CHANGED")
    if canary.get("authorityClass") != "codespaces-linux-boot-session":
        raise AggregateError(f"{label}:AUTHORITY_CLASS_CHANGED")
    if not isinstance(canary.get("localExecutionId"), int) or canary["localExecutionId"] <= 0:
        raise AggregateError(f"{label}:LOCAL_EXECUTION_ID_INVALID")
    if not isinstance(canary.get("sourceCommitSha"), str) or len(canary["sourceCommitSha"]) != 40:
        raise AggregateError(f"{label}:SOURCE_COMMIT_INVALID")
    for key in ("sessionFingerprintSha256", "baseComputeFingerprintSha256", "linuxBootIdSha256"):
        value = canary.get(key)
        if not isinstance(value, str) or len(value) != 64:
            raise AggregateError(f"{label}:{key}:INVALID")
    epoch = canary.get("authorityEpochId")
    if not isinstance(epoch, str) or not epoch:
        raise AggregateError(f"{label}:AUTHORITY_EPOCH_REQUIRED")

    guards = canary.get("policyBoundary", {})
    required_guards = {
        "sessionQualifiedByThisSingleCanary": False,
        "singleCanaryMayPromoteModelValidation": False,
        "newSessionInheritsThisCanary": False,
        "referenceTabUsed": False,
        "professionalScorerUsed": False,
        "legacyV143ScorerImported": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
        "customerEligibleEvents": 0,
    }
    for key, expected in required_guards.items():
        if guards.get(key) != expected:
            raise AggregateError(f"{label}:POLICY_GUARD_CHANGED:{key}")

    diagnostics = canary.get("executionDiagnostics", {})
    for key in (
        "authorityVerifiedBeforeModelExecution",
        "authorityVerifiedAfterModelExecution",
        "sourceBlobMatchesAuthorizedFixture",
        "frozenStructureIdentityMatched",
    ):
        if diagnostics.get(key) is not True:
            raise AggregateError(f"{label}:EXECUTION_DIAGNOSTIC_CHANGED:{key}")
    if diagnostics.get("workbenchHarnessAuthorityEligible") is not False:
        raise AggregateError(f"{label}:WORKBENCH_HARNESS_MUST_REMAIN_NON_AUTHORITY")

    fixed = canary.get("fixedInputIdentity")
    if not isinstance(fixed, dict):
        raise AggregateError(f"{label}:FIXED_INPUT_IDENTITY_REQUIRED")
    output = canary.get("outputIdentity")
    if not isinstance(output, dict):
        raise AggregateError(f"{label}:OUTPUT_IDENTITY_REQUIRED")
    for field in EXACT_FIELDS:
        if field not in output:
            raise AggregateError(f"{label}:OUTPUT_IDENTITY_MISSING:{field}")
    return canary


def aggregate(canaries, minimum_runs=3):
    if len(canaries) < minimum_runs:
        raise AggregateError("MINIMUM_THREE_DISTINCT_SESSION_CANARIES_REQUIRED")
    validated = [validate_canary(item, f"canary{index}") for index, item in enumerate(canaries)]

    execution_ids = [item["localExecutionId"] for item in validated]
    if len(set(execution_ids)) != len(execution_ids):
        raise AggregateError("DUPLICATE_LOCAL_EXECUTION_ID")

    invariant_fields = (
        "authorityEpochId",
        "sessionFingerprintSha256",
        "baseComputeFingerprintSha256",
        "linuxBootIdSha256",
        "sourceCommitSha",
    )
    for field in invariant_fields:
        if len({item[field] for item in validated}) != 1:
            raise AggregateError(f"SESSION_CANARY_INVARIANT_MISMATCH:{field}")

    fixed_inputs = {
        json.dumps(item["fixedInputIdentity"], sort_keys=True, separators=(",", ":"))
        for item in validated
    }
    if len(fixed_inputs) != 1:
        raise AggregateError("FIXED_INPUT_IDENTITY_MISMATCH")

    exact = {}
    for field in EXACT_FIELDS:
        values = [item["outputIdentity"][field] for item in validated]
        same = len(set(values)) == 1
        exact[field] = {"exactAcrossCanaries": same, "value": values[0] if same else None}
    if not all(item["exactAcrossCanaries"] for item in exact.values()):
        raise AggregateError("SESSION_AUTHORITY_CANARIES_NOT_EXACT")

    first = validated[0]
    return {
        "contract": CONTRACT,
        "version": 1,
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "authorityEpochId": first["authorityEpochId"],
        "sessionFingerprintSha256": first["sessionFingerprintSha256"],
        "baseComputeFingerprintSha256": first["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": first["linuxBootIdSha256"],
        "sourceCommitSha": first["sourceCommitSha"],
        "localExecutionIds": sorted(execution_ids),
        "separateCanaryExecutionCount": len(validated),
        "measurement": {
            "minimumRequiredExecutions": minimum_runs,
            "allExecutionIdsDistinct": True,
            "sameAuthorityEpoch": True,
            "sameSessionFingerprint": True,
            "sameLinuxBootSession": True,
            "sameSourceCommit": True,
            "sameFixedInputIdentity": True,
            "exactOutputIdentity": exact,
            "sessionAuthoritySurfaceQualified": True,
        },
        "lifetime": {
            "qualificationBoundToCurrentLinuxBoot": True,
            "qualificationBoundToExactSourceCommit": True,
            "qualificationBoundToExactComputeFingerprint": True,
            "stopRestartRebuildInvalidatesQualification": True,
            "newEnrollmentMustRequalifyFromZero": True,
        },
        "policyBoundary": {
            "surfaceQualificationIsModelValidation": False,
            "newSessionInheritsQualification": False,
            "reproducibilityProofAlonePromotesModelValidation": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def make_canary(execution_id, suffix="a"):
    value = suffix * 64
    return {
        "contract": CANARY_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "authorityEpochId": "11111111-1111-4111-8111-111111111111",
        "sessionFingerprintSha256": "1" * 64,
        "baseComputeFingerprintSha256": "2" * 64,
        "linuxBootIdSha256": "3" * 64,
        "sourceCommitSha": "4" * 40,
        "localExecutionId": execution_id,
        "fixedInputIdentity": {
            "fixtureGitBlob": "5" * 40,
            "decodedSeparationWavSha256": "6" * 64,
            "structureIdentity": "fnv1a32:test",
            "demucsAssetSha256": "7" * 64,
        },
        "outputIdentity": {
            "guitarStemSha256": value,
            "noteInferenceSha256": value,
            "activationBundleSha256": value,
            "decisionSurfaceSha256": value,
            "canonicalEvidenceSha256": value,
            "eventCount": 1138,
        },
        "executionDiagnostics": {
            "workbenchHarnessContract": "songsterr-fresh-codespaces-workbench-measurement-v2",
            "workbenchHarnessAuthorityEligible": False,
            "authorityVerifiedBeforeModelExecution": True,
            "authorityVerifiedAfterModelExecution": True,
            "sourceBlobMatchesAuthorizedFixture": True,
            "frozenStructureIdentityMatched": True,
        },
        "policyBoundary": {
            "sessionQualifiedByThisSingleCanary": False,
            "singleCanaryMayPromoteModelValidation": False,
            "newSessionInheritsThisCanary": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def run_self_test():
    result = aggregate([make_canary(1), make_canary(2), make_canary(3)])
    assert result["measurement"]["sessionAuthoritySurfaceQualified"] is True
    assert result["policyBoundary"]["modelValidationComplete"] is False
    assert result["lifetime"]["stopRestartRebuildInvalidatesQualification"] is True

    drifted = [make_canary(11), make_canary(12), make_canary(13)]
    drifted[2]["outputIdentity"]["canonicalEvidenceSha256"] = "b" * 64
    try:
        aggregate(drifted)
    except AggregateError as exc:
        assert str(exc) == "SESSION_AUTHORITY_CANARIES_NOT_EXACT"
    else:
        raise AssertionError("output drift must fail closed")

    boot_drift = [make_canary(21), make_canary(22), make_canary(23)]
    boot_drift[2]["linuxBootIdSha256"] = "9" * 64
    try:
        aggregate(boot_drift)
    except AggregateError as exc:
        assert str(exc) == "SESSION_CANARY_INVARIANT_MISMATCH:linuxBootIdSha256"
    else:
        raise AssertionError("boot-session drift must fail closed")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "minimumDistinctCanaryExecutions": 3,
        "outputDriftFailsClosed": True,
        "bootSessionDriftFailsClosed": True,
        "sessionAuthoritySurfaceQualifiedByExactSetOnly": True,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("canary", nargs="*")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    if len(args.canary) < 3:
        raise AggregateError("MINIMUM_THREE_DISTINCT_SESSION_CANARIES_REQUIRED")
    result = aggregate([load_json(path) for path in args.canary])
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    try:
        main()
    except AggregateError as exc:
        print(f"CODESPACES_SESSION_AUTHORITY_AGGREGATE_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
