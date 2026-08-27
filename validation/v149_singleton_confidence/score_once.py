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
    "candidatePath": "debug/v149-singleton-confidence/candidate/candidate.json",
    "candidateGitBlob": "2590b7b00ad77bcb297d02764e9df556b5bb487a",
    "candidateFileSha256": "1add3ffacf9048dd597a47820baeb3ef8cb0e67fa83d12b1b8d8303a8d808278",
    "candidateCanonicalEventSha256": "4dd13556d580a315c728e7333823eec9644195da5a345689cc44a566ef33d998",
    "candidateEventCount": 1144,
    "constructionProofPath": "debug/v149-singleton-confidence/candidate/construction-proof.json",
    "constructionProofGitBlob": "86c61863721efd51f80583829020f20712b171f6",
    "constructionProofSha256": "1efae460dcb93129dcd6717ccad8eb9e496767a78a68eddddecd0121e1261d6e",
    "pdfEvidencePath": "debug/v149-singleton-confidence/candidate/pdf-event-fidelity.json",
    "pdfEvidenceGitBlob": "23480ccbc46633bc311b32b4356dba1dd257f503",
    "pdfEvidenceSha256": "23d087a2d902c6a4a10f80ffca9765139d7c021f8ac59996225c3ad7dcd478f9",
    "completionSentinelPath": "debug/v149-singleton-confidence/phase-b-complete-sentinel.json",
    "completionSentinelGitBlob": "6df0fcd825cbb4ed3302754b24af32a01a5b29ab",
    "authorizationPath": "debug/v149-singleton-confidence/phase-c-scoring-authorization.json",
    "authorizationGitBlob": "d6af61782ab9acea1a43a554a19846e58b3f3110",
    "goldPath": "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json",
    "goldSha256": "18fd868ae960dfcddc1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac",
    "wrapperPath": "validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py",
    "wrapperGitBlob": "1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb",
    "scorerPath": "validation/rhythm_holdout/score_rhythm_holdout.py",
    "scorerGitBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "adapterPath": "validation/rhythm_holdout/canonical.py",
    "adapterGitBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "acceptedBaselinePath": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
    "acceptedBaselineGitBlob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
    "v148ScorePath": "debug/v148-singleton-only/phase-c-score/score-result.json",
    "v148ScoreGitBlob": "95d29f742a85a4e701a767c8a339e09a65b59dcd",
    "v148ScoreFileSha256": "7ba84ac3e530e94b8d1e3b1b7d8d83902fe6f064acb4f423b37ef51e282f1638",
}

METRICS = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "exactVoicingTolerantF1",
    "measureCoverageRecall",
)
DISPLAY_KEYS = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "measureCoverageRecall",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def require_blob(path_key: str, blob_key: str) -> None:
    actual = git_blob(EXPECTED[path_key])
    if actual != EXPECTED[blob_key]:
        raise RuntimeError(f"Git blob mismatch for {EXPECTED[path_key]}: {actual} != {EXPECTED[blob_key]}")


def display_vector(metrics: dict[str, Any]) -> list[float]:
    return [100.0 * float(metrics[key]) for key in DISPLAY_KEYS] + [100.0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run exactly one authorized V149 high-confidence singleton Gold calibration score.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"one-use score output already exists: {output}")

    # Everything in this block is reference-free. Gold bytes are not touched yet.
    for path_key, blob_key in (
        ("candidatePath", "candidateGitBlob"),
        ("constructionProofPath", "constructionProofGitBlob"),
        ("pdfEvidencePath", "pdfEvidenceGitBlob"),
        ("completionSentinelPath", "completionSentinelGitBlob"),
        ("authorizationPath", "authorizationGitBlob"),
        ("wrapperPath", "wrapperGitBlob"),
        ("scorerPath", "scorerGitBlob"),
        ("adapterPath", "adapterGitBlob"),
        ("acceptedBaselinePath", "acceptedBaselineGitBlob"),
        ("v148ScorePath", "v148ScoreGitBlob"),
    ):
        require_blob(path_key, blob_key)

    if len(EXPECTED["goldSha256"]) != 64 or any(ch not in "0123456789abcdef" for ch in EXPECTED["goldSha256"]):
        raise RuntimeError("frozen Gold SHA constant is not a valid 64-character lowercase SHA256")

    authorization = load_json(ROOT / EXPECTED["authorizationPath"])
    if authorization.get("classification") != "one-use-reference-facing-score-authorized":
        raise RuntimeError("authorization classification mismatch")
    auth = authorization.get("authorization") or {}
    if auth.get("received") is not True or auth.get("scope") != "exactly-one-v149-high-confidence-singleton-gold-calibration-score":
        raise RuntimeError("fresh V149 score authorization missing")
    for forbidden in (
        "candidateSearchAllowed",
        "alternateCandidateAllowed",
        "alternateThresholdAllowed",
        "retuningAllowed",
        "audioRecomputeAllowed",
        "modalGpuAllowed",
        "productionPromotionAllowed",
    ):
        if auth.get(forbidden) is not False:
            raise RuntimeError(f"forbidden authorization flag changed: {forbidden}")

    completion = load_json(ROOT / EXPECTED["completionSentinelPath"])
    if completion.get("status") != "COMPLETE_SEALED_STOP_BEFORE_SCORING":
        raise RuntimeError("V149 construction completion status mismatch")
    if completion.get("referenceFacingScoringAuthorization") is not False or completion.get("scoreCallCount") != 0:
        raise RuntimeError("V149 construction completion safety state mismatch")
    if completion.get("candidateEventSha256") != EXPECTED["candidateCanonicalEventSha256"]:
        raise RuntimeError("V149 completion candidate identity mismatch")

    proof_path = ROOT / EXPECTED["constructionProofPath"]
    proof_bytes = proof_path.read_bytes()
    if sha256_bytes(proof_bytes) != EXPECTED["constructionProofSha256"]:
        raise RuntimeError("V149 construction proof SHA256 mismatch")
    proof = json.loads(proof_bytes)
    metrics = proof.get("metrics") or {}
    if proof.get("gate") != "GO" or proof.get("deterministic") is not True or proof.get("pdfEventFidelity") != 1.0:
        raise RuntimeError("V149 construction proof gate mismatch")
    if metrics.get("changedEventCountVersusAccepted") != 54 or metrics.get("changedOnsetCountVersusAccepted") != 54:
        raise RuntimeError("V149 changed count mismatch")
    if metrics.get("polyphonicChangedEventsVersusAccepted") != 0 or float(metrics.get("thresholdDb")) != 3.0:
        raise RuntimeError("V149 policy/structure mismatch")
    if metrics.get("timingMetadataInvariantViolations") != 0 or metrics.get("positionIdentityViolations") != 0:
        raise RuntimeError("V149 construction invariant violation")

    candidate_path = ROOT / EXPECTED["candidatePath"]
    candidate_bytes = candidate_path.read_bytes()
    if sha256_bytes(candidate_bytes) != EXPECTED["candidateFileSha256"]:
        raise RuntimeError("V149 candidate file SHA256 mismatch")
    candidate_doc = json.loads(candidate_bytes)
    if candidate_doc.get("instrument") != "rhythm":
        raise RuntimeError("candidate instrument mismatch")
    canonical = canonical_events(candidate_doc.get("renderEvents") or [])
    if len(canonical) != EXPECTED["candidateEventCount"]:
        raise RuntimeError("candidate event count mismatch")
    candidate_sha = sha256_json(canonical)
    if candidate_sha != EXPECTED["candidateCanonicalEventSha256"]:
        raise RuntimeError(f"candidate canonical event SHA mismatch: {candidate_sha}")

    pdf_bytes = (ROOT / EXPECTED["pdfEvidencePath"]).read_bytes()
    if sha256_bytes(pdf_bytes) != EXPECTED["pdfEvidenceSha256"]:
        raise RuntimeError("V149 PDF evidence SHA256 mismatch")
    pdf = json.loads(pdf_bytes)
    if pdf.get("pdfEventFidelity") != 1.0 or pdf.get("candidateEventSha256") != candidate_sha:
        raise RuntimeError("V149 PDF fidelity identity mismatch")

    baseline = load_json(ROOT / EXPECTED["acceptedBaselinePath"])
    if baseline.get("name") != "singleton-onset-replace-be9e9aa7a734e3cd":
        raise RuntimeError("accepted baseline identity mismatch")
    accepted_calibration = baseline.get("fullGoldCalibration") or {}
    baseline_metrics = accepted_calibration.get("gatedMetrics") or {}
    baseline_critical = int(accepted_calibration.get("criticalMismatchCount"))

    v148_bytes = (ROOT / EXPECTED["v148ScorePath"]).read_bytes()
    if sha256_bytes(v148_bytes) != EXPECTED["v148ScoreFileSha256"]:
        raise RuntimeError("V148 score result SHA256 mismatch")
    v148_report = json.loads(v148_bytes)
    v148_metrics = (v148_report.get("score") or {}).get("gatedMetrics") or {}
    v148_critical = int((v148_report.get("score") or {}).get("criticalMismatchCount"))

    # Authorized reference-facing boundary begins here.
    gold_path = ROOT / EXPECTED["goldPath"]
    gold_bytes = gold_path.read_bytes()
    gold_sha = sha256_bytes(gold_bytes)
    if gold_sha != EXPECTED["goldSha256"]:
        raise RuntimeError(f"Gold SHA256 mismatch: {gold_sha}")
    reference = historical_wrapper.scorer.validate_reference(json.loads(gold_bytes))

    # Exactly one historical score call. No candidate search, variants, threshold changes or retry.
    candidate_score = historical_wrapper.score_full_candidate(canonical, reference)

    candidate_metrics = candidate_score["gatedMetrics"]
    baseline_deltas = {name: float(candidate_metrics[name]) - float(baseline_metrics[name]) for name in METRICS}
    v148_deltas = {name: float(candidate_metrics[name]) - float(v148_metrics[name]) for name in METRICS}
    critical_delta_baseline = int(candidate_score["criticalMismatchCount"]) - baseline_critical
    critical_delta_v148 = int(candidate_score["criticalMismatchCount"]) - v148_critical

    candidate_vector = display_vector(candidate_metrics)
    baseline_vector = display_vector(baseline_metrics)
    v148_vector = display_vector(v148_metrics)

    report = {
        "schemaVersion": 14950,
        "classification": "v149-high-confidence-singleton-authorized-single-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "authorizationScope": "exactly-one-v149-high-confidence-singleton-gold-calibration-score",
        "candidate": {
            "eventCount": len(canonical),
            "canonicalEventSha256": candidate_sha,
            "fileSha256": EXPECTED["candidateFileSha256"],
            "changedEventsVersusAccepted": 54,
            "changedOnsetsVersusAccepted": 54,
            "polyphonicChangedEventsVersusAccepted": 0,
            "thresholdDb": 3.0,
            "retainedPercentOfV148Changes": 100.0 * 54.0 / 106.0,
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
        "priorV148": {
            "candidateCanonicalEventSha256": (v148_report.get("candidate") or {}).get("canonicalEventSha256"),
            "gatedMetrics": v148_metrics,
            "criticalMismatchCount": v148_critical,
        },
        "comparison": {
            "gatedMetricDeltasVsAcceptedBaseline": baseline_deltas,
            "gatedMetricDeltasVsV148": v148_deltas,
            "criticalMismatchDeltaVsAcceptedBaseline": critical_delta_baseline,
            "criticalMismatchDeltaVsV148": critical_delta_v148,
            "candidateDisplayVectorPercent": candidate_vector,
            "acceptedBaselineDisplayVectorPercent": baseline_vector,
            "v148DisplayVectorPercent": v148_vector,
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
            "alternateThresholdTested": False,
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
        "v148DisplayVectorPercent": v148_vector,
        "criticalMismatchCount": candidate_score["criticalMismatchCount"],
        "criticalMismatchDeltaVsAcceptedBaseline": critical_delta_baseline,
        "criticalMismatchDeltaVsV148": critical_delta_v148,
        "scoreCallCount": 1,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
