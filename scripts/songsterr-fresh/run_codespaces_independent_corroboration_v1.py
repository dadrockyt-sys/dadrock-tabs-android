#!/usr/bin/env python3
"""Run frozen independent corroboration inside an already-qualified Policy C-S epoch.

This wrapper is research-only. It verifies the session before and after, binds the
input stem/evidence to the exact qualification output identities, and never
promotes model validation/customer eligibility.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

WORKBENCH_ROOT = Path("/workspaces/.songsterr-fresh-workbench")
SESSION_ROOT = Path("/workspaces/.songsterr-fresh-session-authority")
REPO_ROOT = Path("/workspaces/dadrock-tabs-android")
CONTRACT = "songsterr-fresh-codespaces-independent-corroboration-run-v1"


class SessionResearchError(RuntimeError):
    pass


def run(*args: str, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        check=True,
        text=True,
        cwd=str(REPO_ROOT),
        stdout=subprocess.PIPE if capture else None,
        stderr=None,
    )
    return completed.stdout.strip() if capture else ""


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SessionResearchError(f"JSON_LOAD_FAILED:{path}") from exc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def qualification_exact_outputs(qualification: dict) -> dict[str, object]:
    exact = qualification.get("measurement", {}).get("exactOutputIdentity")
    if not isinstance(exact, dict):
        raise SessionResearchError("QUALIFICATION_EXACT_OUTPUT_IDENTITY_MISSING")
    values = {}
    for key, payload in exact.items():
        if isinstance(payload, dict) and "value" in payload:
            values[key] = payload["value"]
        else:
            values[key] = payload
    return values


def validate_qualification_policy_boundary(qualification: dict) -> None:
    """Validate the non-promotion boundary using the qualification v1 schema."""
    boundary = qualification.get("policyBoundary")
    if not isinstance(boundary, dict):
        raise SessionResearchError("QUALIFICATION_POLICY_BOUNDARY_MISSING")
    required = {
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
    }
    for field, expected in required.items():
        if boundary.get(field) != expected:
            raise SessionResearchError(f"QUALIFICATION_POLICY_GUARD_CHANGED:{field}")


def main() -> int:
    if not REPO_ROOT.is_dir():
        raise SessionResearchError("REPOSITORY_ROOT_MISSING")
    python = WORKBENCH_ROOT / "venv/bin/python"
    enrollment_path = SESSION_ROOT / "session-enrollment.json"
    verifier = REPO_ROOT / "scripts/songsterr-fresh/codespaces_session_authority.py"
    evaluator = REPO_ROOT / "scripts/songsterr-fresh/independent_pitch_corroboration_v1.py"
    for path in (python, enrollment_path, verifier, evaluator):
        if not path.exists():
            raise SessionResearchError(f"REQUIRED_PATH_MISSING:{path}")

    head = run("git", "rev-parse", "HEAD", capture=True)
    enrollment = load(enrollment_path)
    if enrollment.get("sourceCommitSha") != head:
        raise SessionResearchError("ENROLLMENT_SOURCE_COMMIT_DOES_NOT_MATCH_HEAD")

    epoch = enrollment.get("authorityEpochId")
    if not isinstance(epoch, str) or not epoch:
        raise SessionResearchError("AUTHORITY_EPOCH_ID_MISSING")
    epoch_root = SESSION_ROOT / "epochs" / epoch
    qualification_path = epoch_root / "session-qualification.json"
    if not qualification_path.is_file():
        raise SessionResearchError("SESSION_QUALIFICATION_MISSING")
    qualification = load(qualification_path)
    if qualification.get("sourceCommitSha") != head:
        raise SessionResearchError("QUALIFICATION_SOURCE_COMMIT_DOES_NOT_MATCH_HEAD")
    if qualification.get("measurement", {}).get("sessionAuthoritySurfaceQualified") is not True:
        raise SessionResearchError("SESSION_SURFACE_NOT_QUALIFIED")
    validate_qualification_policy_boundary(qualification)

    research_root = epoch_root / "independent-corroboration-v1"
    research_root.mkdir(parents=True, exist_ok=True)
    pre_path = research_root / "verify-pre.json"
    post_path = research_root / "verify-post.json"
    output_path = research_root / "independent-corroboration-v1.json"

    run(
        str(python),
        str(verifier.relative_to(REPO_ROOT)),
        "verify",
        "--enrollment",
        str(enrollment_path),
        "--output",
        str(pre_path),
    )

    model_log = (epoch_root / "canary-1-model.log").read_text(encoding="utf-8")
    summary_matches = re.findall(r"^summary=(.+)$", model_log, flags=re.MULTILINE)
    if not summary_matches:
        raise SessionResearchError("CANARY_1_MODEL_SUMMARY_PATH_MISSING")
    summary_path = Path(summary_matches[-1].strip())
    if not summary_path.is_file():
        raise SessionResearchError("CANARY_1_MODEL_SUMMARY_FILE_MISSING")
    run_dir = summary_path.parent
    evidence_path = run_dir / "evidence.json"
    stem_path = run_dir / "separated/htdemucs_6s/separation/guitar.wav"
    for path in (evidence_path, stem_path):
        if not path.is_file():
            raise SessionResearchError(f"QUALIFIED_MODEL_OUTPUT_MISSING:{path}")

    exact = qualification_exact_outputs(qualification)
    expected_stem = exact.get("guitarStemSha256")
    expected_evidence = exact.get("canonicalEvidenceSha256")
    expected_count = exact.get("eventCount")
    if not isinstance(expected_stem, str) or len(expected_stem) != 64:
        raise SessionResearchError("QUALIFICATION_GUITAR_STEM_IDENTITY_MISSING")
    if not isinstance(expected_evidence, str) or len(expected_evidence) != 64:
        raise SessionResearchError("QUALIFICATION_EVIDENCE_IDENTITY_MISSING")
    if sha256_file(stem_path) != expected_stem:
        raise SessionResearchError("QUALIFIED_GUITAR_STEM_HASH_MISMATCH")

    run(
        str(python),
        str(evaluator.relative_to(REPO_ROOT)),
        "--input-stem",
        str(stem_path),
        "--evidence",
        str(evidence_path),
        "--output",
        str(output_path),
    )

    result = load(output_path)
    identity = result.get("identityProof", {})
    if identity.get("inputStemSha256") != expected_stem:
        raise SessionResearchError("RESEARCH_STEM_IDENTITY_NOT_QUALIFICATION_BOUND")
    if identity.get("evidenceCanonicalSha256") != expected_evidence:
        raise SessionResearchError("RESEARCH_EVIDENCE_IDENTITY_NOT_QUALIFICATION_BOUND")
    if identity.get("eventCount") != expected_count:
        raise SessionResearchError("RESEARCH_EVENT_COUNT_NOT_QUALIFICATION_BOUND")
    if result.get("methodFrozenBeforeAuthorizedSongEvaluation") is not True:
        raise SessionResearchError("METHOD_FREEZE_GUARD_CHANGED")

    hard = result.get("hardGuards", {})
    for field in (
        "invokesDemucs",
        "invokesBasicPitch",
        "usesBasicPitchActivations",
        "usesBasicPitchDecisionSurface",
        "usesBasicPitchNoteSpanAmplitude",
        "usesBasicPitchDecodedNoteEnd",
        "usesReferenceTab",
        "usesProfessionalScorer",
        "importsArchivedV143Logic",
        "changesPitchIdentity",
        "writesDurationSeconds",
        "writesSourceEnd",
        "ownsAdmissionDecision",
        "setsModelValidationComplete",
        "setsCustomerEligibility",
    ):
        if hard.get(field) is not False:
            raise SessionResearchError(f"RESEARCH_HARD_GUARD_CHANGED:{field}")
    boundary = result.get("policyBoundary", {})
    if (
        boundary.get("admissionDecisionMade") is not False
        or boundary.get("modelValidationComplete") is not False
        or boundary.get("mayAdvanceDelivery") is not False
        or boundary.get("durationAuthorityChanged") is not False
        or boundary.get("customerEligibleEvents") != 0
    ):
        raise SessionResearchError("RESEARCH_POLICY_BOUNDARY_CHANGED")

    run(
        str(python),
        str(verifier.relative_to(REPO_ROOT)),
        "verify",
        "--enrollment",
        str(enrollment_path),
        "--output",
        str(post_path),
    )
    pre = load(pre_path)
    post = load(post_path)
    for field in (
        "authorityEpochId",
        "sessionFingerprintSha256",
        "baseComputeFingerprintSha256",
        "linuxBootIdSha256",
        "sourceCommitSha",
    ):
        if pre.get(field) != post.get(field):
            raise SessionResearchError(f"SESSION_CHANGED_DURING_RESEARCH:{field}")

    summary = {
        "contract": CONTRACT,
        "status": "QUALIFIED_SESSION_INDEPENDENT_CORROBORATION_RESEARCH_COMPLETE",
        "authorityEpochId": epoch,
        "sourceCommitSha": head,
        "sessionFingerprintSha256": pre.get("sessionFingerprintSha256"),
        "sessionVerifiedBeforeAndAfterResearch": True,
        "qualifiedEventCount": expected_count,
        "classificationCounts": result["summary"]["classificationCounts"],
        "researchOutput": str(output_path),
        "policyBoundary": {
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }
    summary_path_out = research_root / "research-summary.json"
    summary_path_out.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("CODESPACES_INDEPENDENT_CORROBORATION_RESEARCH_COMPLETE")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SessionResearchError, subprocess.CalledProcessError) as exc:
        print(f"CODESPACES_INDEPENDENT_CORROBORATION_ERROR:{exc}", file=sys.stderr)
        raise SystemExit(2)
