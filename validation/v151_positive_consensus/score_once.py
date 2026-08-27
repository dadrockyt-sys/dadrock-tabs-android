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
    "candidatePath": "debug/v151-positive-consensus/candidate/candidate.json",
    "candidateGitBlob": "28d10742fe9f4e27ac47a14df9151c5bc8a6eec0",
    "candidateFileSha256": "ac96ec4edc3e9b67c047e7e9012139bfa46d0d6d164ffa1443960f8fbcb19ae9",
    "candidateEventSha256": "e6c437f534dfb5523610797c67f8f69176be903456ef4940c3032567b949156b",
    "proofPath": "debug/v151-positive-consensus/candidate/construction-proof.json",
    "proofGitBlob": "0e090cf16534eb6f7f61b07bb1ae34f062f7fea8",
    "proofSha256": "187cb046988df7cc96ff1e909d2d76fd7ec9c4a802f93ceea1277085cf464342",
    "pdfPath": "debug/v151-positive-consensus/candidate/pdf-event-fidelity.json",
    "pdfGitBlob": "20a02fd7657166c7e6d2f33240b4d99e390c5604",
    "pdfSha256": "c594a733131af3e34e4c937b90d148cfd4b4673c5cb050def4293b6f97d290e7",
    "completionPath": "debug/v151-positive-consensus/phase-b-complete-sentinel.json",
    "completionGitBlob": "442453a8ba07808e9098bbfe446861c2c20f9b99",
    "authorizationPath": "debug/v151-positive-consensus/phase-c-scoring-authorization.json",
    "authorizationGitBlob": "6c40b25934f5fe83853ea47959fd765b6b7af5af",
    "goldPath": "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json",
    "wrapperPath": "validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py",
    "wrapperGitBlob": "1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb",
    "corePath": "validation/rhythm_holdout/score_rhythm_holdout.py",
    "coreGitBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "adapterPath": "validation/rhythm_holdout/canonical.py",
    "adapterGitBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "baselinePath": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
    "baselineGitBlob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
    "v150ScorePath": "debug/v150-contextual-singleton/phase-c-score/score-result.json",
    "v150ScoreGitBlob": "35d0953ae89cdad9c71542fb5801e2b9c4ca563d",
    "v150ScoreSha256": "c29c83571c68c8e850f3a2c30de0c9b0a706ab02e35342e8e39151949b576e40",
}
METRICS = ("pitchContentF1", "pitchTimingTolerantF1", "stringFretTimingTolerantF1", "chordPitchSetTolerantF1", "exactVoicingTolerantF1", "measureCoverageRecall")
DISPLAY = ("pitchContentF1", "pitchTimingTolerantF1", "stringFretTimingTolerantF1", "chordPitchSetTolerantF1", "measureCoverageRecall")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def require_blob(path_key: str, blob_key: str) -> None:
    actual = git_blob(EXPECTED[path_key])
    expected = EXPECTED[blob_key]
    if actual != expected:
        raise RuntimeError(f"Git blob mismatch for {EXPECTED[path_key]}: {actual} != {expected}")


def display_vector(metrics: dict[str, Any]) -> list[float]:
    return [100.0 * float(metrics[k]) for k in DISPLAY] + [100.0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run exactly one authorized V151 positive-consensus Gold score.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"one-use output already exists: {output}")

    for path_key, blob_key in (
        ("candidatePath", "candidateGitBlob"),
        ("proofPath", "proofGitBlob"),
        ("pdfPath", "pdfGitBlob"),
        ("completionPath", "completionGitBlob"),
        ("authorizationPath", "authorizationGitBlob"),
        ("wrapperPath", "wrapperGitBlob"),
        ("corePath", "coreGitBlob"),
        ("adapterPath", "adapterGitBlob"),
        ("baselinePath", "baselineGitBlob"),
        ("v150ScorePath", "v150ScoreGitBlob"),
    ):
        require_blob(path_key, blob_key)

    authorization = load_json(ROOT / EXPECTED["authorizationPath"])
    auth = authorization.get("authorization") or {}
    if authorization.get("classification") != "one-use-reference-facing-score-authorized" or auth.get("received") is not True or auth.get("scope") != "exactly-one-v151-positive-consensus-gold-calibration-score":
        raise RuntimeError("V151 score authorization mismatch")
    for key in ("candidateSearchAllowed", "alternateCandidateAllowed", "alternateSubsetAllowed", "additionalFilterAllowed", "alternateThresholdAllowed", "retuningAllowed", "audioRecomputeAllowed", "modalGpuAllowed", "productionPromotionAllowed"):
        if auth.get(key) is not False:
            raise RuntimeError(f"forbidden authorization flag changed: {key}")

    completion = load_json(ROOT / EXPECTED["completionPath"])
    if completion.get("status") != "COMPLETE_SEALED_STOP_BEFORE_SCORING" or completion.get("referenceFacingScoringAuthorization") is not False or completion.get("scoreCallCount") != 0:
        raise RuntimeError("V151 construction completion safety mismatch")

    proof_bytes = (ROOT / EXPECTED["proofPath"]).read_bytes()
    if sha256_bytes(proof_bytes) != EXPECTED["proofSha256"]:
        raise RuntimeError("V151 proof SHA mismatch")
    proof = json.loads(proof_bytes)
    metrics = proof.get("metrics") or {}
    if proof.get("gate") != "GO" or proof.get("deterministic") is not True or proof.get("pdfEventFidelity") != 1.0:
        raise RuntimeError("V151 proof gate mismatch")
    if metrics.get("changedEventCountVersusAccepted") != 12 or metrics.get("changedOnsetCountVersusAccepted") != 12 or metrics.get("polyphonicChangedEventsVersusAccepted") != 0:
        raise RuntimeError("V151 structural proof mismatch")

    candidate_bytes = (ROOT / EXPECTED["candidatePath"]).read_bytes()
    if sha256_bytes(candidate_bytes) != EXPECTED["candidateFileSha256"]:
        raise RuntimeError("V151 candidate file SHA mismatch")
    candidate_doc = json.loads(candidate_bytes)
    canonical = canonical_events(candidate_doc.get("renderEvents") or [])
    if len(canonical) != 1144 or sha256_json(canonical) != EXPECTED["candidateEventSha256"]:
        raise RuntimeError("V151 candidate event identity mismatch")

    pdf_bytes = (ROOT / EXPECTED["pdfPath"]).read_bytes()
    if sha256_bytes(pdf_bytes) != EXPECTED["pdfSha256"]:
        raise RuntimeError("V151 PDF evidence SHA mismatch")
    pdf = json.loads(pdf_bytes)
    if pdf.get("pdfEventFidelity") != 1.0 or pdf.get("candidateEventSha256") != EXPECTED["candidateEventSha256"]:
        raise RuntimeError("V151 PDF identity mismatch")

    baseline = load_json(ROOT / EXPECTED["baselinePath"])
    accepted = baseline.get("fullGoldCalibration") or {}
    baseline_metrics = accepted.get("gatedMetrics") or {}
    baseline_critical = int(accepted.get("criticalMismatchCount"))

    prior_bytes = (ROOT / EXPECTED["v150ScorePath"]).read_bytes()
    if sha256_bytes(prior_bytes) != EXPECTED["v150ScoreSha256"]:
        raise RuntimeError("V150 score result SHA mismatch")
    prior_report = json.loads(prior_bytes)
    expected_gold_sha = str((prior_report.get("reference") or {}).get("sha256") or "")
    if len(expected_gold_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_gold_sha):
        raise RuntimeError("persisted V150 reference SHA is not valid 64-char lowercase hex")
    prior_metrics = (prior_report.get("score") or {}).get("gatedMetrics") or {}
    prior_critical = int((prior_report.get("score") or {}).get("criticalMismatchCount"))

    # Authorized reference boundary begins here.
    gold_bytes = (ROOT / EXPECTED["goldPath"]).read_bytes()
    actual_gold_sha = sha256_bytes(gold_bytes)
    if actual_gold_sha != expected_gold_sha:
        raise RuntimeError(f"Gold SHA mismatch: {actual_gold_sha}")
    reference = historical_wrapper.scorer.validate_reference(json.loads(gold_bytes))
    candidate_score = historical_wrapper.score_full_candidate(canonical, reference)

    candidate_metrics = candidate_score["gatedMetrics"]
    deltas_baseline = {k: float(candidate_metrics[k]) - float(baseline_metrics[k]) for k in METRICS}
    deltas_prior = {k: float(candidate_metrics[k]) - float(prior_metrics[k]) for k in METRICS}
    report = {
        "schemaVersion": 15150,
        "classification": "v151-positive-consensus-authorized-single-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "authorizationScope": "exactly-one-v151-positive-consensus-gold-calibration-score",
        "candidate": {
            "eventCount": 1144,
            "canonicalEventSha256": EXPECTED["candidateEventSha256"],
            "fileSha256": EXPECTED["candidateFileSha256"],
            "changedEventsVersusAccepted": 12,
            "changedOnsetsVersusAccepted": 12,
            "polyphonicChangedEventsVersusAccepted": 0,
            "retainedPercentOfV150Changes": 100.0 * 12 / 33,
            "pdfEventFidelity": 1.0,
            "pdfEvidenceSha256": EXPECTED["pdfSha256"],
        },
        "reference": {
            "role": "gold-calibration-reference-not-unseen-holdout",
            "sha256": actual_gold_sha,
            "identitySource": "persisted-v150-score-result-reference-sha256",
        },
        "scoringChain": {
            "fullCalibrationWrapperGitBlob": EXPECTED["wrapperGitBlob"],
            "coreScorerGitBlob": EXPECTED["coreGitBlob"],
            "canonicalAdapterGitBlob": EXPECTED["adapterGitBlob"],
            "historicalFunction": "score_selected_conjunction_candidate.score_full_candidate",
            "scoreCallCount": 1,
        },
        "score": candidate_score,
        "acceptedBaseline": {
            "name": baseline.get("name"),
            "gatedMetrics": baseline_metrics,
            "criticalMismatchCount": baseline_critical,
        },
        "priorV150": {
            "gatedMetrics": prior_metrics,
            "criticalMismatchCount": prior_critical,
        },
        "comparison": {
            "candidateDisplayVectorPercent": display_vector(candidate_metrics),
            "acceptedBaselineDisplayVectorPercent": display_vector(baseline_metrics),
            "v150DisplayVectorPercent": display_vector(prior_metrics),
            "gatedMetricDeltasVsAcceptedBaseline": deltas_baseline,
            "gatedMetricDeltasVsV150": deltas_prior,
            "criticalMismatchDeltaVsAcceptedBaseline": int(candidate_score["criticalMismatchCount"]) - baseline_critical,
            "criticalMismatchDeltaVsV150": int(candidate_score["criticalMismatchCount"]) - prior_critical,
            "displayVectorOrder": ["pitch-content", "pitch-timing", "string-fret-timing", "chord-pitch-set", "measure-coverage", "pdf-event-fidelity"],
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "safety": {
            "candidateSearchRun": False,
            "alternateCandidateConstructed": False,
            "alternateSubsetTested": False,
            "additionalFilterTested": False,
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
        "candidateDisplayVectorPercent": report["comparison"]["candidateDisplayVectorPercent"],
        "acceptedBaselineDisplayVectorPercent": report["comparison"]["acceptedBaselineDisplayVectorPercent"],
        "v150DisplayVectorPercent": report["comparison"]["v150DisplayVectorPercent"],
        "criticalMismatchCount": candidate_score["criticalMismatchCount"],
        "criticalMismatchDeltaVsAcceptedBaseline": report["comparison"]["criticalMismatchDeltaVsAcceptedBaseline"],
        "criticalMismatchDeltaVsV150": report["comparison"]["criticalMismatchDeltaVsV150"],
        "scoreCallCount": 1,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
