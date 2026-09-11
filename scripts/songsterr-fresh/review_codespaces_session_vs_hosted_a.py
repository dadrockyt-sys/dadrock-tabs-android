#!/usr/bin/env python3
"""Read-only model-evidence review for one already-qualified Policy C-S epoch.

Designed to be downloaded to /tmp and executed while the live Codespace remains
pinned to source commit b2f2467... . It does not modify the repository, invoke
Demucs/Basic Pitch, define admission thresholds, or promote model validation.
"""

from __future__ import annotations

import collections
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

EXPECTED_SOURCE_COMMIT = "b2f246769340e4f7f6929e679692956c731efd93"
BASELINE_COMMIT = "930e8f8af0fe87e4f992731754a90607c341f86b"
BASELINE_URL = (
    "https://raw.githubusercontent.com/dadrockyt-sys/dadrock-tabs-android/"
    f"{BASELINE_COMMIT}/docs/checkpoints/SONGSTERR_FRESH_HOSTED_A_SEMANTIC_BASELINE_V1.json"
)
BASELINE_EVIDENCE_SHA256 = "475c501a5d44b605eab623f2c5a6b22e962aaf13d7baa9a9d208566d01eca501"
BASELINE_EVENT_COUNT = 1138
WORKBENCH_ROOT = Path("/workspaces/.songsterr-fresh-workbench")
SESSION_ROOT = Path("/workspaces/.songsterr-fresh-session-authority")
REVIEW_ROOT = Path("/tmp/songsterr-qualified-model-review-v2")


def run(*args: str, capture: bool = False) -> str:
    completed = subprocess.run(
        list(args),
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=None,
    )
    return completed.stdout.strip() if capture else ""


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def semantic_key(event):
    return (float(event["nearestStructureSlot"]), int(event["selectedMidi"]))


def main() -> int:
    repo = Path(run("git", "rev-parse", "--show-toplevel", capture=True))
    os.chdir(repo)
    head = run("git", "rev-parse", "HEAD", capture=True)
    if head != EXPECTED_SOURCE_COMMIT:
        raise RuntimeError(f"SOURCE_COMMIT_CHANGED:{head}")

    python = WORKBENCH_ROOT / "venv/bin/python"
    enrollment_path = SESSION_ROOT / "session-enrollment.json"
    if not python.is_file() or not enrollment_path.is_file():
        raise RuntimeError("QUALIFIED_SESSION_FILES_MISSING")

    REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    verify_pre = REVIEW_ROOT / "verify-pre.json"
    verify_post = REVIEW_ROOT / "verify-post.json"
    trace_path = REVIEW_ROOT / "qualified-decoder-trace.json"
    pitch_path = REVIEW_ROOT / "qualified-pitch-support.json"
    baseline_path = REVIEW_ROOT / "hosted-a-semantic-baseline.json"

    run(
        str(python),
        "scripts/songsterr-fresh/codespaces_session_authority.py",
        "verify",
        "--enrollment",
        str(enrollment_path),
        "--output",
        str(verify_pre),
    )

    enrollment = load(enrollment_path)
    epoch = enrollment["authorityEpochId"]
    epoch_root = SESSION_ROOT / "epochs" / epoch
    qualification = load(epoch_root / "session-qualification.json")
    if qualification["measurement"]["sessionAuthoritySurfaceQualified"] is not True:
        raise RuntimeError("SESSION_NOT_QUALIFIED")
    if qualification["sourceCommitSha"] != EXPECTED_SOURCE_COMMIT:
        raise RuntimeError("QUALIFICATION_SOURCE_MISMATCH")

    model_log = (epoch_root / "canary-1-model.log").read_text(encoding="utf-8")
    summary_matches = re.findall(r"^summary=(.+)$", model_log, flags=re.MULTILINE)
    if not summary_matches:
        raise RuntimeError("CANARY_1_SUMMARY_PATH_MISSING")
    summary_path = Path(summary_matches[-1].strip())
    if not summary_path.is_file():
        raise RuntimeError("CANARY_1_SUMMARY_FILE_MISSING")
    run_dir = summary_path.parent

    evidence_path = run_dir / "evidence.json"
    activation_path = run_dir / "basic-pitch-note-activations.json"
    decision_path = run_dir / "basic-pitch-decision-surface.json"
    stem_path = run_dir / "separated/htdemucs_6s/separation/guitar.wav"
    for path in (evidence_path, activation_path, decision_path, stem_path):
        if not path.is_file():
            raise RuntimeError(f"MODEL_EVIDENCE_FILE_MISSING:{path}")

    with urllib.request.urlopen(BASELINE_URL, timeout=30) as response:
        baseline_bytes = response.read()
    baseline_path.write_bytes(baseline_bytes)
    baseline = load(baseline_path)
    if baseline.get("contract") != "songsterr-fresh-hosted-a-semantic-baseline-v1":
        raise RuntimeError("BASELINE_CONTRACT_CHANGED")
    if baseline.get("referenceBlind") is not True or baseline.get("measurementOnly") is not True:
        raise RuntimeError("BASELINE_GUARD_CHANGED")
    if baseline.get("eventCount") != BASELINE_EVENT_COUNT:
        raise RuntimeError("BASELINE_EVENT_COUNT_CHANGED")
    if baseline.get("canonicalEvidenceSha256") != BASELINE_EVIDENCE_SHA256:
        raise RuntimeError("BASELINE_EVIDENCE_IDENTITY_CHANGED")
    boundary = baseline.get("policyBoundary", {})
    if boundary.get("modelValidationComplete") is not False or boundary.get("customerEligibleEvents") != 0:
        raise RuntimeError("BASELINE_PROMOTION_GUARD_CHANGED")

    run(
        str(python),
        "scripts/songsterr-fresh/trace_basic_pitch_decoder_mechanisms.py",
        str(evidence_path),
        str(activation_path),
        str(decision_path),
        "--output",
        str(trace_path),
    )
    run(
        str(python),
        "scripts/songsterr-fresh/probe_independent_pitch_support.py",
        "--input",
        str(stem_path),
        "--evidence",
        str(evidence_path),
        "--output",
        str(pitch_path),
    )

    run(
        str(python),
        "scripts/songsterr-fresh/codespaces_session_authority.py",
        "verify",
        "--enrollment",
        str(enrollment_path),
        "--output",
        str(verify_post),
    )

    pre = load(verify_pre)
    post = load(verify_post)
    for field in (
        "authorityEpochId",
        "sessionFingerprintSha256",
        "baseComputeFingerprintSha256",
        "linuxBootIdSha256",
        "sourceCommitSha",
    ):
        if pre.get(field) != post.get(field):
            raise RuntimeError(f"SESSION_CHANGED_DURING_REVIEW:{field}")

    current = load(evidence_path)
    trace = load(trace_path)
    pitch = load(pitch_path)

    baseline_groups = {}
    for slot, midi, count, rows in baseline["groups"]:
        baseline_groups[(float(slot), int(midi))] = {
            "count": int(count),
            "events": rows,
        }

    current_groups = collections.defaultdict(list)
    for event in current["onsets"]:
        current_groups[semantic_key(event)].append(event)

    trace_groups = collections.defaultdict(list)
    for event in trace["events"]:
        trace_groups[semantic_key(event)].append(event)

    pitch_by_id = {event["onsetId"]: event for event in pitch["events"]}
    all_keys = sorted(set(baseline_groups) | set(current_groups))
    mismatches = []
    for key in all_keys:
        before = baseline_groups.get(key, {"count": 0, "events": []})
        after = current_groups.get(key, [])
        if before["count"] == len(after):
            continue

        current_rows = []
        for event in sorted(after, key=lambda item: (item["sourceStart"], item["onsetConfidence"], item["onsetId"])):
            support = pitch_by_id.get(event["onsetId"], {})
            selected = support.get("selectedPitch", {})
            local = support.get("localSemitoneComparison", {})
            octave = support.get("octaveComparison", {})
            alternative = support.get("bestAlternative", {})
            mechanisms = [
                {
                    "sourceStart": t["sourceStart"],
                    "decoderMechanism": t["decoderMechanism"],
                    "decoderStartFrame": t["decoderStartFrame"],
                    "decoderEndFrame": t["decoderEndFrame"],
                }
                for t in trace_groups.get(key, [])
            ]
            current_rows.append({
                "onsetId": event["onsetId"],
                "sourceStart": event["sourceStart"],
                "onsetConfidence": event["onsetConfidence"],
                "decoder": mechanisms,
                "independentPitchSupport": {
                    "selectedAboveFloorDb": selected.get("aboveFloorDb"),
                    "localSemitoneRank": local.get("rankAmongSelectedAndNeighbors"),
                    "selectedMinusBestSemitoneNeighborDb": local.get("selectedMinusBestNeighborDb"),
                    "octaveRank": octave.get("rankAmongAvailableSelectedAndOctaves"),
                    "selectedMinusBestComparedAlternativeDb": alternative.get("selectedMinusBestAlternativeDb"),
                },
            })

        mismatches.append({
            "nearestStructureSlot": key[0],
            "selectedMidi": key[1],
            "hostedAEventCount": before["count"],
            "qualifiedSessionEventCount": len(after),
            "hostedAEvents": [
                {"sourceStart": row[0], "onsetConfidence": row[1]}
                for row in before["events"]
            ],
            "qualifiedSessionEvents": current_rows,
        })

    result = {
        "status": "QUALIFIED_SESSION_MODEL_EVIDENCE_REVIEW_COMPLETE",
        "authorityEpochId": epoch,
        "sourceCommitSha": head,
        "sessionFingerprintSha256": pre["sessionFingerprintSha256"],
        "sessionVerifiedBeforeAndAfterReview": True,
        "eventCounts": {
            "hostedA": baseline["eventCount"],
            "qualifiedSession": len(current["onsets"]),
            "differenceQualifiedMinusHostedA": len(current["onsets"]) - baseline["eventCount"],
        },
        "qualifiedDecoderMechanismCounts": trace["mechanismCounts"],
        "semanticCountMismatchCount": len(mismatches),
        "semanticCountMismatches": mismatches,
        "independentPitchSupportGlobalSummary": pitch["summary"],
        "policyBoundary": {
            "referenceTabUsed": False,
            "professionalScorerUsed": False,
            "legacyV143ScorerImported": False,
            "thresholdSweepUsed": False,
            "admissionDecisionMade": False,
            "modelValidationComplete": False,
            "mayAdvanceDelivery": False,
            "durationAuthorityChanged": False,
            "customerEligibleEvents": 0,
        },
    }
    output = REVIEW_ROOT / "review-summary.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("MODEL_EVIDENCE_REVIEW_SUMMARY")
    print(json.dumps(result, indent=2, sort_keys=True))
    print(f"reviewSummary={output}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"QUALIFIED_SESSION_MODEL_REVIEW_ERROR:{exc}", file=sys.stderr)
        raise
