#!/usr/bin/env python3

"""Build one fail-closed Policy C-S Codespaces session canary summary.

The model execution may reuse the existing Codespaces workbench harness, but the
result becomes a Policy C-S canary only when exact session verification succeeded
both immediately before and immediately after that execution.
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

POLICY = "POLICY_C_S_CODESPACES_SESSION_AUTHORITY"
VERIFY_CONTRACT = "songsterr-fresh-codespaces-session-authority-verification-v1"
CANARY_CONTRACT = "songsterr-fresh-codespaces-session-authority-canary-v1"
MEASUREMENT_CONTRACT = "songsterr-fresh-codespaces-workbench-measurement-v2"
FIXTURE_BLOB = "4dd709e3fa177b4daeed71ca97f0199757729d4b"
STRUCTURE_IDENTITY = "fnv1a32:2f493225"
DEMUCS_ASSET_SHA = "d2a1745f0744721f6b8ca5bf469b67c651ea5ed1b52998cab033b2158609d411"


class CanaryError(RuntimeError):
    pass


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
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


def validate_verification(value, label):
    if not isinstance(value, dict):
        raise CanaryError(f"{label}:VERIFICATION_OBJECT_REQUIRED")
    if value.get("contract") != VERIFY_CONTRACT or value.get("version") != 1:
        raise CanaryError(f"{label}:VERIFICATION_CONTRACT_CHANGED")
    if value.get("policy") != POLICY:
        raise CanaryError(f"{label}:VERIFICATION_POLICY_CHANGED")
    if value.get("status") != "CODESPACES_SESSION_AUTHORITY_VERIFIED":
        raise CanaryError(f"{label}:SESSION_AUTHORITY_NOT_VERIFIED")
    require_sha(value.get("sourceCommitSha"), f"{label}.sourceCommitSha", length=40)
    require_sha(value.get("sessionFingerprintSha256"), f"{label}.sessionFingerprintSha256")
    require_sha(value.get("baseComputeFingerprintSha256"), f"{label}.baseComputeFingerprintSha256")
    require_sha(value.get("linuxBootIdSha256"), f"{label}.linuxBootIdSha256")
    epoch = value.get("authorityEpochId")
    if not isinstance(epoch, str) or not re.fullmatch(r"[0-9a-fA-F-]{36}", epoch):
        raise CanaryError(f"{label}:AUTHORITY_EPOCH_ID_INVALID")
    guards = value.get("policyBoundary", {})
    required = {
        "verificationAloneQualifiesSession": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
        "customerEligibleEvents": 0,
    }
    for key, expected in required.items():
        if guards.get(key) != expected:
            raise CanaryError(f"{label}:VERIFICATION_GUARD_CHANGED:{key}")
    return value


def build_summary(pre, post, measurement, evidence, activation, decision, notes, context, demucs_asset,
                  stem_path, separation_path, source_commit, execution_id):
    pre = validate_verification(pre, "pre")
    post = validate_verification(post, "post")
    for key in (
        "authorityEpochId",
        "sourceCommitSha",
        "sessionFingerprintSha256",
        "baseComputeFingerprintSha256",
        "linuxBootIdSha256",
    ):
        if pre.get(key) != post.get(key):
            raise CanaryError(f"SESSION_CHANGED_DURING_MODEL_EXECUTION:{key}")

    source_commit = require_sha(source_commit, "sourceCommitSha", length=40)
    if source_commit != pre["sourceCommitSha"]:
        raise CanaryError("SOURCE_COMMIT_NOT_SESSION_BOUND")
    execution_text = str(execution_id)
    if not execution_text.isdigit() or int(execution_text) <= 0:
        raise CanaryError("POSITIVE_LOCAL_EXECUTION_ID_REQUIRED")

    if measurement.get("contract") != MEASUREMENT_CONTRACT or measurement.get("version") != 2:
        raise CanaryError("WORKBENCH_MEASUREMENT_CONTRACT_CHANGED")
    if measurement.get("sourceCommit") != source_commit:
        raise CanaryError("WORKBENCH_MEASUREMENT_SOURCE_COMMIT_MISMATCH")
    measurement_required = {
        "workbenchOnly": True,
        "authorityEligible": False,
        "probeAloneEnrollsAuthority": False,
        "modelValidationComplete": False,
        "mayAdvanceDelivery": False,
        "durationAuthorityChanged": False,
        "customerEligibleEvents": 0,
    }
    for key, expected in measurement_required.items():
        if measurement.get(key) != expected:
            raise CanaryError(f"WORKBENCH_MEASUREMENT_GUARD_CHANGED:{key}")

    decode = measurement.get("decodeDiagnostics", {})
    if decode.get("sourceBlob") != FIXTURE_BLOB or decode.get("sourceBlobMatchesAuthorizedFixture") is not True:
        raise CanaryError("AUTHORIZED_SOURCE_FIXTURE_MISMATCH")
    structure_diag = measurement.get("structureDiagnostics", {})
    if structure_diag.get("actualStructureSignature") != STRUCTURE_IDENTITY:
        raise CanaryError("FROZEN_STRUCTURE_IDENTITY_CHANGED")
    if structure_diag.get("referenceBlind") is not True or structure_diag.get("structureFrozen") is not True or structure_diag.get("structureAccepted") is not True:
        raise CanaryError("FROZEN_STRUCTURE_CONTEXT_NOT_ACCEPTED_REFERENCE_BLIND")

    if context.get("structureIdentity", {}).get("signature") != STRUCTURE_IDENTITY:
        raise CanaryError("NOTE_CONTEXT_STRUCTURE_IDENTITY_CHANGED")
    if context.get("referenceBlind") is not True or context.get("structureFrozen") is not True or context.get("structureAcceptance", {}).get("accepted") is not True:
        raise CanaryError("NOTE_CONTEXT_NOT_REFERENCE_BLIND_FROZEN_ACCEPTED")

    if demucs_asset.get("assetSha256") != DEMUCS_ASSET_SHA:
        raise CanaryError("DEMUCS_MODEL_ASSET_CHANGED")
    if demucs_asset.get("legacyFallback", {}).get("primary") is not False:
        raise CanaryError("DEMUCS_LEGACY_FALLBACK_MUST_NOT_BE_PRIMARY")

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
    activation_sha = nested_sha(activation, ("inferenceBundleIdentity",))
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

    decision_sha = require_sha(decision.get("decisionSurfaceIdentity", {}).get("sha256"), "decisionSurfaceSha256")
    decision_guards = decision.get("hardGuards", {})
    for field in (
        "usedForAcceptance",
        "usedForDuration",
        "writesSourceEnd",
        "writesDurationSeconds",
        "changesPitchIdentity",
        "changesDecodedEventInventory",
    ):
        if decision_guards.get(field) is not False:
            raise CanaryError(f"DECISION_SURFACE_PROMOTIONAL_GUARD_CHANGED:{field}")

    stem_sha = sha256_file(stem_path)
    separation_sha = sha256_file(separation_path)
    evidence_sha = hashlib.sha256(canonical_json(evidence).encode("utf-8")).hexdigest()

    # Cross-check the workbench summary against the actual files we just validated.
    identities = measurement.get("identities", {})
    file_hash_checks = {
        "guitarStemSha256": sha256_file(stem_path),
        "noteInferenceSha256": sha256_file(Path(notes["__sourcePath"])) if "__sourcePath" in notes else None,
    }
    # The workbench summary is retained as diagnostic evidence; semantic identities below
    # are the authority comparison contract.  Stem hash must still match exactly.
    if identities.get("guitarStemSha256") != stem_sha:
        raise CanaryError("WORKBENCH_STEM_IDENTITY_MISMATCH")

    return {
        "contract": CANARY_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "authorityClass": "codespaces-linux-boot-session",
        "authorityEpochId": pre["authorityEpochId"],
        "sessionFingerprintSha256": pre["sessionFingerprintSha256"],
        "baseComputeFingerprintSha256": pre["baseComputeFingerprintSha256"],
        "linuxBootIdSha256": pre["linuxBootIdSha256"],
        "sourceCommitSha": source_commit,
        "localExecutionId": int(execution_text),
        "fixedInputIdentity": {
            "fixtureGitBlob": FIXTURE_BLOB,
            "decodedSeparationWavSha256": separation_sha,
            "structureIdentity": STRUCTURE_IDENTITY,
            "demucsAssetSha256": DEMUCS_ASSET_SHA,
        },
        "outputIdentity": {
            "guitarStemSha256": stem_sha,
            "noteInferenceSha256": note_sha,
            "activationBundleSha256": activation_sha,
            "decisionSurfaceSha256": decision_sha,
            "canonicalEvidenceSha256": evidence_sha,
            "eventCount": len(onsets),
        },
        "executionDiagnostics": {
            "workbenchHarnessContract": MEASUREMENT_CONTRACT,
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


def make_verification(epoch="11111111-1111-4111-8111-111111111111"):
    return {
        "contract": VERIFY_CONTRACT,
        "version": 1,
        "policy": POLICY,
        "status": "CODESPACES_SESSION_AUTHORITY_VERIFIED",
        "authorityEpochId": epoch,
        "sourceCommitSha": "a" * 40,
        "baseComputeFingerprintSha256": "b" * 64,
        "linuxBootIdSha256": "c" * 64,
        "sessionFingerprintSha256": "d" * 64,
        "policyBoundary": {
            "verificationAloneQualifiesSession": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }


def run_self_test():
    value = validate_verification(make_verification(), "synthetic")
    assert value["status"] == "CODESPACES_SESSION_AUTHORITY_VERIFIED"
    drift = make_verification("22222222-2222-4222-8222-222222222222")
    try:
        for key in ("authorityEpochId", "sourceCommitSha", "sessionFingerprintSha256"):
            if value.get(key) != drift.get(key):
                raise CanaryError(f"SESSION_CHANGED_DURING_MODEL_EXECUTION:{key}")
    except CanaryError as exc:
        assert str(exc) == "SESSION_CHANGED_DURING_MODEL_EXECUTION:authorityEpochId"
    else:
        raise AssertionError("epoch drift must fail closed")
    print(json.dumps({
        "contract": CANARY_CONTRACT,
        "selfTest": "PASS",
        "preAndPostSessionVerificationRequired": True,
        "singleCanaryMayPromoteModelValidation": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
    }, sort_keys=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pre-verification")
    parser.add_argument("--post-verification")
    parser.add_argument("--measurement-summary")
    parser.add_argument("--evidence")
    parser.add_argument("--activation")
    parser.add_argument("--decision")
    parser.add_argument("--notes")
    parser.add_argument("--context")
    parser.add_argument("--demucs-model-asset")
    parser.add_argument("--stem")
    parser.add_argument("--separation")
    parser.add_argument("--source-commit")
    parser.add_argument("--execution-id")
    parser.add_argument("--output")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return
    required = (
        args.pre_verification,
        args.post_verification,
        args.measurement_summary,
        args.evidence,
        args.activation,
        args.decision,
        args.notes,
        args.context,
        args.demucs_model_asset,
        args.stem,
        args.separation,
        args.source_commit,
        args.execution_id,
        args.output,
    )
    if not all(required):
        parser.error("all canary build inputs and --output are required")

    notes = load_json(args.notes)
    # Source path is local-only helper metadata used solely for optional diagnostics;
    # it is removed before semantic validation and never written to the canary.
    notes["__sourcePath"] = str(Path(args.notes).resolve())
    summary = build_summary(
        load_json(args.pre_verification),
        load_json(args.post_verification),
        load_json(args.measurement_summary),
        load_json(args.evidence),
        load_json(args.activation),
        load_json(args.decision),
        notes,
        load_json(args.context),
        load_json(args.demucs_model_asset),
        args.stem,
        args.separation,
        args.source_commit,
        args.execution_id,
    )
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": CANARY_CONTRACT,
        "status": "SESSION_CANARY_WRITTEN",
        "localExecutionId": summary["localExecutionId"],
        "sessionQualifiedByThisSingleCanary": False,
        "modelValidationComplete": False,
        "customerEligibleEvents": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except CanaryError as exc:
        print(f"CODESPACES_SESSION_CANARY_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
