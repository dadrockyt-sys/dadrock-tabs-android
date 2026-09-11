#!/usr/bin/env python3

"""Build one non-promotional Policy C pinned-compute canary summary."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

CANARY_CONTRACT = "songsterr-fresh-pinned-compute-authority-canary-v1"
AUTHORITY_CONTRACT = "songsterr-fresh-pinned-compute-authority-v1"


class CanaryError(RuntimeError):
    pass


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        raise CanaryError(f"JSON_LOAD_FAILED:{path}") from exc


def canonical_json(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise CanaryError("CANONICAL_JSON_FAILED") from exc


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_sha(value, label, length=64):
    if not isinstance(value, str) or len(value) != length or any(ch not in "0123456789abcdef" for ch in value):
        raise CanaryError(f"{label}:HEX_DIGEST_REQUIRED")
    return value


def nested_sha(mapping, *paths):
    values = []
    for path in paths:
        current = mapping
        for key in path:
            if not isinstance(current, dict):
                current = None
                break
            current = current.get(key)
        if isinstance(current, dict):
            current = current.get("sha256")
        if current is not None:
            values.append(current)
    values = list(dict.fromkeys(values))
    if len(values) != 1:
        raise CanaryError("BOUND_IDENTITY_MISSING_OR_INCONSISTENT")
    return require_sha(values[0], "boundIdentity")


def build_summary(manifest, verification, evidence, activation, decision, notes, stem_sha, source_commit, run_id):
    if manifest.get("contract") != AUTHORITY_CONTRACT or manifest.get("enrollmentStatus") != "ENROLLED":
        raise CanaryError("ENROLLED_AUTHORITY_MANIFEST_REQUIRED")
    if verification.get("status") != "PINNED_COMPUTE_AUTHORITY_VERIFIED":
        raise CanaryError("VERIFIED_AUTHORITY_REQUIRED")
    authority_sha = require_sha(verification.get("fingerprintSha256"), "authorityFingerprintSha256")
    if authority_sha != manifest.get("enrolledFingerprintSha256"):
        raise CanaryError("AUTHORITY_FINGERPRINT_NOT_MANIFEST_BOUND")
    source_commit = require_sha(source_commit, "sourceCommitSha", length=40)
    stem_sha = require_sha(stem_sha, "guitarStemSha256")
    run_text = str(run_id)
    if not run_text.isdigit() or int(run_text) <= 0:
        raise CanaryError("WORKFLOW_RUN_ID_REQUIRED")

    onsets = evidence.get("onsets")
    if not isinstance(onsets, list):
        raise CanaryError("EVIDENCE_ONSETS_REQUIRED")
    if evidence.get("capabilities", {}).get("durationResolution") != "none":
        raise CanaryError("CANARY_EVIDENCE_MUST_REMAIN_DURATION_FREE")
    if any(item.get("sourceEnd") is not None or item.get("durationSeconds") is not None for item in onsets):
        raise CanaryError("CANARY_DURATION_LEAK")

    note_sha = nested_sha(
        notes,
        ("noteInferenceIdentity",),
        ("diagnostics", "noteInferenceIdentity"),
        ("provenance", "noteInferenceIdentity"),
    )
    activation_sha = nested_sha(
        activation,
        ("inferenceBundleIdentity",),
    )
    evidence_note_sha = nested_sha(
        evidence,
        ("diagnostics", "noteInferenceIdentity"),
        ("provenance", "noteInferenceIdentity"),
    )
    evidence_activation_sha = nested_sha(
        evidence,
        ("diagnostics", "activationEvidenceIdentity"),
        ("provenance", "activationEvidenceIdentity"),
    )
    if note_sha != evidence_note_sha:
        raise CanaryError("NOTE_IDENTITY_NOT_EVIDENCE_BOUND")
    if activation_sha != evidence_activation_sha:
        raise CanaryError("ACTIVATION_IDENTITY_NOT_EVIDENCE_BOUND")
    decision_identity = decision.get("decisionSurfaceIdentity", {})
    decision_sha = require_sha(decision_identity.get("sha256"), "decisionSurfaceSha256")
    guards = decision.get("hardGuards", {})
    for field in (
        "usedForAcceptance", "usedForDuration", "writesSourceEnd", "writesDurationSeconds",
        "changesPitchIdentity", "changesDecodedEventInventory",
    ):
        if guards.get(field) is not False:
            raise CanaryError(f"DECISION_SURFACE_PROMOTIONAL_GUARD_CHANGED:{field}")

    evidence_sha = hashlib.sha256(canonical_json(evidence).encode("utf-8")).hexdigest()
    return {
        "contract": CANARY_CONTRACT,
        "version": 1,
        "policy": "POLICY_C_PINNED_COMPUTE_AUTHORITY",
        "authorityId": manifest["authorityId"],
        "authorityFingerprintSha256": authority_sha,
        "sourceCommitSha": source_commit,
        "workflowRunId": int(run_text),
        "fixedInputIdentity": {
            "fixtureGitBlob": manifest["fixedModelPath"]["fixtureGitBlob"],
            "decodedSeparationWavSha256": manifest["fixedModelPath"]["decodedSeparationWavSha256"],
            "structureIdentity": manifest["fixedModelPath"]["structureIdentity"],
            "demucsAssetSha256": manifest["fixedModelPath"]["demucs"]["assetSha256"],
        },
        "outputIdentity": {
            "guitarStemSha256": stem_sha,
            "noteInferenceSha256": note_sha,
            "activationBundleSha256": activation_sha,
            "decisionSurfaceSha256": decision_sha,
            "canonicalEvidenceSha256": evidence_sha,
            "eventCount": len(onsets),
        },
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
    fingerprint_sha = "a" * 64
    manifest = {
        "contract": AUTHORITY_CONTRACT,
        "enrollmentStatus": "ENROLLED",
        "authorityId": "songsterr-fresh-authority-v1",
        "enrolledFingerprintSha256": fingerprint_sha,
        "fixedModelPath": {
            "fixtureGitBlob": "4" * 40,
            "decodedSeparationWavSha256": "5" * 64,
            "structureIdentity": "fnv1a32:test",
            "demucs": {"assetSha256": "6" * 64},
        },
    }
    verification = {"status": "PINNED_COMPUTE_AUTHORITY_VERIFIED", "fingerprintSha256": fingerprint_sha}
    identity = {"sha256": "b" * 64}
    activation_identity = {"sha256": "c" * 64}
    notes = {"noteInferenceIdentity": identity, "diagnostics": {"noteInferenceIdentity": identity}, "provenance": {"noteInferenceIdentity": identity}}
    activation = {"inferenceBundleIdentity": activation_identity}
    decision = {
        "decisionSurfaceIdentity": {"sha256": "d" * 64},
        "hardGuards": {
            "usedForAcceptance": False, "usedForDuration": False, "writesSourceEnd": False,
            "writesDurationSeconds": False, "changesPitchIdentity": False, "changesDecodedEventInventory": False,
        },
    }
    evidence = {
        "capabilities": {"durationResolution": "none"},
        "diagnostics": {"noteInferenceIdentity": identity, "activationEvidenceIdentity": activation_identity},
        "provenance": {"noteInferenceIdentity": identity, "activationEvidenceIdentity": activation_identity},
        "onsets": [{"selectedMidi": 55, "sourceStart": 1.0}],
    }
    summary = build_summary(manifest, verification, evidence, activation, decision, notes, "e" * 64, "f" * 40, 123)
    assert summary["outputIdentity"]["eventCount"] == 1
    assert summary["policyBoundary"]["modelValidationComplete"] is False
    assert summary["policyBoundary"]["singleCanaryMayPromoteModelValidation"] is False
    print(json.dumps({
        "contract": CANARY_CONTRACT,
        "selfTest": "PASS",
        "singleCanaryMayPromoteModelValidation": False,
        "modelValidationComplete": False,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest")
    parser.add_argument("--authority-verification")
    parser.add_argument("--evidence")
    parser.add_argument("--activation")
    parser.add_argument("--decision")
    parser.add_argument("--notes")
    parser.add_argument("--stem")
    parser.add_argument("--source-commit")
    parser.add_argument("--run-id")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    required = (args.manifest, args.authority_verification, args.evidence, args.activation, args.decision, args.notes, args.stem, args.source_commit, args.run_id, args.output)
    if not all(required):
        parser.error("all canary build inputs and --output are required")
    summary = build_summary(
        load_json(args.manifest), load_json(args.authority_verification), load_json(args.evidence),
        load_json(args.activation), load_json(args.decision), load_json(args.notes),
        sha256_file(args.stem), args.source_commit, args.run_id,
    )
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract": CANARY_CONTRACT, "status": "CANARY_SUMMARY_WRITTEN", "modelValidationComplete": False}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except CanaryError as exc:
        print(f"PINNED_COMPUTE_CANARY_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
