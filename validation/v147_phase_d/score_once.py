#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
V144_DIR = ROOT / "validation" / "v144_rhythm_calibration"
HOLDOUT_DIR = ROOT / "validation" / "rhythm_holdout"
for entry in (V144_DIR, HOLDOUT_DIR):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_selected_conjunction_candidate as historical_wrapper  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402

EXPECTED = {
    "candidatePath": "debug/v147-phase-c-real-audio/preserved-run-33038518285/candidate.json",
    "candidateGitBlob": "3091d4b1468260746d6629af67b7b92599d5134e",
    "candidateFileSha256": "c0215690d5bfd9d2d47b8784eee886e942fbd28c499f25c643635c45ff7a9636",
    "candidateCanonicalEventSha256": "ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77",
    "candidateEventCount": 1144,
    "goldPath": "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json",
    "goldSha256": "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac",
    "wrapperPath": "validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py",
    "wrapperGitBlob": "1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb",
    "scorerPath": "validation/rhythm_holdout/score_rhythm_holdout.py",
    "scorerGitBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "adapterPath": "validation/rhythm_holdout/canonical.py",
    "adapterGitBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "authorizationPath": "debug/v147-phase-d-reference-free/phase-d-scoring-authorization.json",
    "authorizationGitBlob": "0ee49e632c0246667363672d35f7b28b1482730c",
    "provenancePath": "debug/v147-phase-d-reference-free/phase-d-provenance-recovery-1.json",
    "provenanceGitBlob": "ecb2539778fe5aa547a8fa88c1216b8562faaebc",
    "acceptedBaselinePath": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
    "acceptedBaselineGitBlob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
    "pdfEvidencePath": "debug/v147-phase-c-real-audio/preserved-run-33038518285/pdf-render-evidence.json",
    "pdfEvidenceSha256": "4d25a8346a40009ec5bdaf34c89f5d09e41ba9504e4264b0fd7cb21d7c25e4b9",
}

METRICS = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "exactVoicingTolerantF1",
    "measureCoverageRecall",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", path], cwd=ROOT, text=True
    ).strip()


def require_blob(path_key: str, blob_key: str) -> None:
    actual = git_blob(EXPECTED[path_key])
    if actual != EXPECTED[blob_key]:
        raise RuntimeError(
            f"Git blob mismatch for {EXPECTED[path_key]}: {actual} != {EXPECTED[blob_key]}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the authorized V147 Phase-D Gold score exactly once.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"one-use score output already exists: {output}")

    # Reference-free identity checks first. No Gold bytes are touched above or in this block.
    for path_key, blob_key in (
        ("candidatePath", "candidateGitBlob"),
        ("wrapperPath", "wrapperGitBlob"),
        ("scorerPath", "scorerGitBlob"),
        ("adapterPath", "adapterGitBlob"),
        ("authorizationPath", "authorizationGitBlob"),
        ("provenancePath", "provenanceGitBlob"),
        ("acceptedBaselinePath", "acceptedBaselineGitBlob"),
    ):
        require_blob(path_key, blob_key)

    authorization = load_json(ROOT / EXPECTED["authorizationPath"])
    if authorization.get("classification") != "one-use-reference-facing-score-authorized":
        raise RuntimeError("authorization classification mismatch")
    auth = authorization.get("authorization") or {}
    if auth.get("received") is not True or auth.get("scope") != "exactly-one-phase-d-v147-gold-calibration-score":
        raise RuntimeError("fresh one-use score authorization missing")
    for forbidden in (
        "candidateSearchAllowed",
        "alternateCandidateAllowed",
        "retuningAllowed",
        "audioRecomputeAllowed",
        "modalGpuAllowed",
        "productionPromotionAllowed",
    ):
        if auth.get(forbidden) is not False:
            raise RuntimeError(f"forbidden authorization flag changed: {forbidden}")

    candidate_path = ROOT / EXPECTED["candidatePath"]
    candidate_bytes = candidate_path.read_bytes()
    if sha256_bytes(candidate_bytes) != EXPECTED["candidateFileSha256"]:
        raise RuntimeError("candidate file SHA256 mismatch")
    candidate = json.loads(candidate_bytes)
    if candidate.get("instrument") != "rhythm":
        raise RuntimeError("candidate instrument mismatch")
    events = candidate.get("renderEvents")
    if not isinstance(events, list):
        raise RuntimeError("candidate renderEvents missing")
    canonical = canonical_events(events)
    if len(canonical) != EXPECTED["candidateEventCount"]:
        raise RuntimeError("candidate event count mismatch")
    canonical_sha = sha256_json(canonical)
    if canonical_sha != EXPECTED["candidateCanonicalEventSha256"]:
        raise RuntimeError(f"candidate canonical event SHA mismatch: {canonical_sha}")

    pdf_bytes = (ROOT / EXPECTED["pdfEvidencePath"]).read_bytes()
    if sha256_bytes(pdf_bytes) != EXPECTED["pdfEvidenceSha256"]:
        raise RuntimeError("preserved PDF evidence SHA256 mismatch")

    baseline = load_json(ROOT / EXPECTED["acceptedBaselinePath"])
    if baseline.get("name") != "singleton-onset-replace-be9e9aa7a734e3cd":
        raise RuntimeError("accepted baseline identity mismatch")
    accepted = baseline.get("fullGoldCalibration") or {}
    baseline_metrics = accepted.get("gatedMetrics") or {}
    baseline_critical = int(accepted.get("criticalMismatchCount"))

    # Authorized reference-facing boundary begins here: verify Gold bytes before parsing.
    gold_path = ROOT / EXPECTED["goldPath"]
    gold_bytes = gold_path.read_bytes()
    gold_sha = sha256_bytes(gold_bytes)
    if gold_sha != EXPECTED["goldSha256"]:
        raise RuntimeError(f"Gold SHA256 mismatch: {gold_sha}")
    reference = historical_wrapper.scorer.validate_reference(json.loads(gold_bytes))

    # Exactly one historical scoring call. No search, variants, retuning, or second call.
    candidate_score = historical_wrapper.score_full_candidate(canonical, reference)

    deltas = {
        name: float(candidate_score["gatedMetrics"][name]) - float(baseline_metrics[name])
        for name in METRICS
    }
    critical_delta = int(candidate_score["criticalMismatchCount"]) - baseline_critical

    display_keys = (
        "pitchContentF1",
        "pitchTimingTolerantF1",
        "stringFretTimingTolerantF1",
        "chordPitchSetTolerantF1",
        "measureCoverageRecall",
    )
    candidate_vector = [100.0 * float(candidate_score["gatedMetrics"][k]) for k in display_keys] + [100.0]
    baseline_vector = [100.0 * float(baseline_metrics[k]) for k in display_keys] + [100.0]

    report = {
        "schemaVersion": 14750,
        "classification": "v147-phase-d-authorized-single-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "authorizationScope": "exactly-one-phase-d-v147-gold-calibration-score",
        "candidate": {
            "eventCount": len(canonical),
            "canonicalEventSha256": canonical_sha,
            "fileSha256": EXPECTED["candidateFileSha256"],
            "pdfEventFidelity": 1.0,
            "pdfEvidenceSha256": EXPECTED["pdfEvidenceSha256"],
        },
        "reference": {
            "role": "gold-calibration-reference-not-unseen-holdout",
            "sha256": gold_sha,
        },
        "scoringChain": {
            "fullCalibrationWrapperGitBlob": EXPECTED["wrapperGitBlob"],
            "coreScorerGitBlob": EXPECTED["scorerGitBlob"],
            "canonicalAdapterGitBlob": EXPECTED["adapterGitBlob"],
            "historicalFunction": "score_selected_conjunction_candidate.score_full_candidate",
            "scoreCallCount": 1,
        },
        "score": candidate_score,
        "acceptedBaseline": {
            "name": baseline.get("name"),
            "eventSha256": (baseline.get("selectedCandidate") or {}).get("eventSha256"),
            "gatedMetrics": baseline_metrics,
            "criticalMismatchCount": baseline_critical,
        },
        "comparison": {
            "gatedMetricDeltas": deltas,
            "criticalMismatchDelta": critical_delta,
            "candidateDisplayVectorPercent": candidate_vector,
            "acceptedBaselineDisplayVectorPercent": baseline_vector,
            "displayVectorOrder": [
                "pitch-content",
                "pitch-timing",
                "string-fret-timing",
                "chord-pitch-set",
                "measure-coverage",
                "pdf-event-fidelity",
            ],
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "safety": {
            "candidateSearchRun": False,
            "alternateCandidateConstructed": False,
            "retuningRun": False,
            "audioRecomputed": False,
            "modalGpuUsed": False,
            "productionIntegrated": False,
            "automaticPromotionAllowed": False,
            "scoreCallCount": 1,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": report["classification"],
        "candidateDisplayVectorPercent": candidate_vector,
        "acceptedBaselineDisplayVectorPercent": baseline_vector,
        "gatedMetricDeltas": deltas,
        "criticalMismatchDelta": critical_delta,
        "scoreCallCount": 1,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
