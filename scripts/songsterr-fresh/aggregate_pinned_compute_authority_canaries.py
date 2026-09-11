#!/usr/bin/env python3

"""Aggregate separate Policy C canaries without auto-promoting model validation."""

import argparse
import json
import sys
from pathlib import Path

CANARY_CONTRACT = "songsterr-fresh-pinned-compute-authority-canary-v1"
CONTRACT = "songsterr-fresh-pinned-compute-authority-canary-set-v1"
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
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        raise AggregateError(f"JSON_LOAD_FAILED:{path}") from exc


def validate_canary(canary, label):
    if not isinstance(canary, dict) or canary.get("contract") != CANARY_CONTRACT or canary.get("version") != 1:
        raise AggregateError(f"{label}:CANARY_CONTRACT_CHANGED")
    if canary.get("policy") != "POLICY_C_PINNED_COMPUTE_AUTHORITY":
        raise AggregateError(f"{label}:POLICY_CHANGED")
    guards = canary.get("policyBoundary", {})
    required = {
        "authorityVerifiedBeforeModelExecution": True,
        "reproducibilityDemonstratedByThisSingleRun": False,
        "singleCanaryMayPromoteModelValidation": False,
        "referenceTabUsed": False,
        "professionalScorerUsed": False,
        "legacyV143ScorerImported": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
    }
    for key, expected in required.items():
        if guards.get(key) != expected:
            raise AggregateError(f"{label}:POLICY_GUARD_CHANGED:{key}")
    if not isinstance(canary.get("workflowRunId"), int) or canary["workflowRunId"] <= 0:
        raise AggregateError(f"{label}:WORKFLOW_RUN_ID_INVALID")
    if not isinstance(canary.get("sourceCommitSha"), str) or len(canary["sourceCommitSha"]) != 40:
        raise AggregateError(f"{label}:SOURCE_COMMIT_INVALID")
    if not isinstance(canary.get("authorityFingerprintSha256"), str) or len(canary["authorityFingerprintSha256"]) != 64:
        raise AggregateError(f"{label}:AUTHORITY_FINGERPRINT_INVALID")
    output = canary.get("outputIdentity")
    if not isinstance(output, dict):
        raise AggregateError(f"{label}:OUTPUT_IDENTITY_REQUIRED")
    for field in EXACT_FIELDS:
        if field not in output:
            raise AggregateError(f"{label}:OUTPUT_IDENTITY_MISSING:{field}")
    return canary


def aggregate(canaries, minimum_runs=3):
    if len(canaries) < minimum_runs:
        raise AggregateError("MINIMUM_THREE_SEPARATE_CANARIES_REQUIRED")
    validated = [validate_canary(item, f"canary{index}") for index, item in enumerate(canaries)]
    run_ids = [item["workflowRunId"] for item in validated]
    if len(set(run_ids)) != len(run_ids):
        raise AggregateError("DUPLICATE_WORKFLOW_RUN_ID")
    commits = {item["sourceCommitSha"] for item in validated}
    if len(commits) != 1:
        raise AggregateError("SOURCE_COMMIT_MISMATCH")
    fingerprints = {item["authorityFingerprintSha256"] for item in validated}
    if len(fingerprints) != 1:
        raise AggregateError("AUTHORITY_FINGERPRINT_MISMATCH")
    authority_ids = {item["authorityId"] for item in validated}
    if len(authority_ids) != 1:
        raise AggregateError("AUTHORITY_ID_MISMATCH")
    fixed_inputs = {json.dumps(item["fixedInputIdentity"], sort_keys=True, separators=(",", ":")) for item in validated}
    if len(fixed_inputs) != 1:
        raise AggregateError("FIXED_INPUT_IDENTITY_MISMATCH")

    exact = {}
    for field in EXACT_FIELDS:
        values = [item["outputIdentity"][field] for item in validated]
        exact[field] = {
            "exactAcrossCanaries": len(set(values)) == 1,
            "value": values[0] if len(set(values)) == 1 else None,
        }
    reproducible = all(item["exactAcrossCanaries"] for item in exact.values())
    if not reproducible:
        raise AggregateError("PINNED_AUTHORITY_CANARIES_NOT_EXACT")

    return {
        "contract": CONTRACT,
        "version": 1,
        "policy": "POLICY_C_PINNED_COMPUTE_AUTHORITY",
        "authorityId": validated[0]["authorityId"],
        "authorityFingerprintSha256": validated[0]["authorityFingerprintSha256"],
        "sourceCommitSha": validated[0]["sourceCommitSha"],
        "workflowRunIds": sorted(run_ids),
        "separateCanaryRunCount": len(validated),
        "measurement": {
            "minimumRequiredRuns": minimum_runs,
            "allRunsDistinct": True,
            "sameSourceCommit": True,
            "sameAuthorityFingerprint": True,
            "exactOutputIdentity": exact,
            "pinnedAuthorityReproducibilityDemonstrated": True,
        },
        "policyBoundary": {
            "reproducibilityDemonstrated": True,
            "reproducibilityProofAlonePromotesModelValidation": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
        },
    }


def make_canary(run_id, suffix="x"):
    value = (suffix * 64)[:64]
    output = {
        "guitarStemSha256": value,
        "noteInferenceSha256": value,
        "activationBundleSha256": value,
        "decisionSurfaceSha256": value,
        "canonicalEvidenceSha256": value,
        "eventCount": 1138,
    }
    return {
        "contract": CANARY_CONTRACT,
        "version": 1,
        "policy": "POLICY_C_PINNED_COMPUTE_AUTHORITY",
        "authorityId": "songsterr-fresh-authority-v1",
        "authorityFingerprintSha256": "a" * 64,
        "sourceCommitSha": "b" * 40,
        "workflowRunId": run_id,
        "fixedInputIdentity": {"fixture": "fixed"},
        "outputIdentity": output,
        "policyBoundary": {
            "authorityVerifiedBeforeModelExecution": True,
            "reproducibilityDemonstratedByThisSingleRun": False,
            "singleCanaryMayPromoteModelValidation": False,
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
        },
    }


def run_self_test():
    canaries = [make_canary(101), make_canary(102), make_canary(103)]
    result = aggregate(canaries)
    assert result["measurement"]["pinnedAuthorityReproducibilityDemonstrated"] is True
    assert result["policyBoundary"]["modelValidationComplete"] is False
    assert result["policyBoundary"]["reproducibilityProofAlonePromotesModelValidation"] is False

    drifted = [make_canary(201), make_canary(202), make_canary(203)]
    drifted[2]["outputIdentity"]["canonicalEvidenceSha256"] = "d" * 64
    try:
        aggregate(drifted)
    except AggregateError as exc:
        assert str(exc) == "PINNED_AUTHORITY_CANARIES_NOT_EXACT"
    else:
        raise AssertionError("output drift must fail closed")

    duplicate = [make_canary(301), make_canary(301), make_canary(303)]
    try:
        aggregate(duplicate)
    except AggregateError as exc:
        assert str(exc) == "DUPLICATE_WORKFLOW_RUN_ID"
    else:
        raise AssertionError("duplicate canary runs must fail closed")

    print(json.dumps({
        "contract": CONTRACT,
        "selfTest": "PASS",
        "minimumSeparateCanaries": 3,
        "outputDriftFailsClosed": True,
        "reproducibilityProofAlonePromotesModelValidation": False,
        "modelValidationComplete": False,
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
        raise AggregateError("MINIMUM_THREE_SEPARATE_CANARIES_REQUIRED")
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
        print(f"PINNED_AUTHORITY_AGGREGATE_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
