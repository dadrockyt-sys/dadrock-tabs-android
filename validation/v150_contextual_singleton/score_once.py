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
    "candidatePath": "debug/v150-contextual-singleton/candidate/candidate.json",
    "candidateGitBlob": "3dc0d09833fe236a5fdfdea0412b2bab74f00e65",
    "candidateFileSha256": "8366b8bd0f3df71ca38dee7ffd1274761e73521bfde740eff9c46637651187b5",
    "candidateEventSha256": "72a0582cfc7d03d84cd2f878f191a69b7262b200ce248d1a896207444a3c5e4e",
    "proofPath": "debug/v150-contextual-singleton/candidate/construction-proof.json",
    "proofGitBlob": "dd680f193f284b2a6874a148829c53aa8ed4f558",
    "proofSha256": "03713d17ef1d92a1542ef12980cee8f2072f36069df4c2cc49882f3fbae58f19",
    "pdfPath": "debug/v150-contextual-singleton/candidate/pdf-event-fidelity.json",
    "pdfGitBlob": "db5086140e6123fb863f316cac57eaeac853626c",
    "pdfSha256": "418cedbbad7c25d6099f8ccf3d11cc7fc4e5e3987c8aabae2b8a41441fcaf860",
    "completionPath": "debug/v150-contextual-singleton/phase-b-complete-sentinel.json",
    "completionGitBlob": "07403cf23bffad39b78de02aa70236a851380bf2",
    "authorizationPath": "debug/v150-contextual-singleton/phase-c-scoring-authorization.json",
    "authorizationGitBlob": "5fbf389df62c89702e911dc38097f5833e6e9b05",
    "identityAddendumPath": "debug/v150-contextual-singleton/phase-c-scoring-identity-addendum.json",
    "identityAddendumGitBlob": "f296197fc5738838d91b968a4fe0465121fa4f9c",
    "goldPath": "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json",
    "wrapperPath": "validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py",
    "wrapperGitBlob": "1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb",
    "corePath": "validation/rhythm_holdout/score_rhythm_holdout.py",
    "coreGitBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "adapterPath": "validation/rhythm_holdout/canonical.py",
    "adapterGitBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "baselinePath": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
    "baselineGitBlob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
    "v149ScorePath": "debug/v149-singleton-confidence/phase-c-score/score-result.json",
    "v149ScoreGitBlob": "efaaeb781e99d4d5e89e601f9e3167869a0de7ad",
    "v149ScoreSha256": "29c56823b4a3f81f5af6db20c562af9b3b59a646160711eb11ff368cbdd7b6df",
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
    parser = argparse.ArgumentParser(description="Run exactly one authorized V150 contextual singleton Gold score.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError(f"one-use output already exists: {output}")

    for path_key, blob_key in (
        ("candidatePath", "candidateGitBlob"), ("proofPath", "proofGitBlob"), ("pdfPath", "pdfGitBlob"),
        ("completionPath", "completionGitBlob"), ("authorizationPath", "authorizationGitBlob"),
        ("identityAddendumPath", "identityAddendumGitBlob"), ("wrapperPath", "wrapperGitBlob"),
        ("corePath", "coreGitBlob"), ("adapterPath", "adapterGitBlob"), ("baselinePath", "baselineGitBlob"),
        ("v149ScorePath", "v149ScoreGitBlob"),
    ):
        require_blob(path_key, blob_key)

    authorization = load_json(ROOT / EXPECTED["authorizationPath"])
    auth = authorization.get("authorization") or {}
    if authorization.get("classification") != "one-use-reference-facing-score-authorized" or auth.get("received") is not True or auth.get("scope") != "exactly-one-v150-contextual-singleton-gold-calibration-score":
        raise RuntimeError("V150 score authorization mismatch")
    for key in ("candidateSearchAllowed", "alternateCandidateAllowed", "alternateContextRuleAllowed", "alternateThresholdAllowed", "retuningAllowed", "audioRecomputeAllowed", "modalGpuAllowed", "productionPromotionAllowed"):
        if auth.get(key) is not False:
            raise RuntimeError(f"forbidden authorization flag changed: {key}")

    completion = load_json(ROOT / EXPECTED["completionPath"])
    if completion.get("status") != "COMPLETE_SEALED_STOP_BEFORE_SCORING" or completion.get("referenceFacingScoringAuthorization") is not False or completion.get("scoreCallCount") != 0:
        raise RuntimeError("V150 construction completion safety mismatch")

    proof_bytes = (ROOT / EXPECTED["proofPath"]).read_bytes()
    if sha256_bytes(proof_bytes) != EXPECTED["proofSha256"]:
        raise RuntimeError("V150 proof SHA mismatch")
    proof = json.loads(proof_bytes)
    metrics = proof.get("metrics") or {}
    if proof.get("gate") != "GO" or proof.get("deterministic") is not True or proof.get("pdfEventFidelity") != 1.0:
        raise RuntimeError("V150 proof gate mismatch")
    if metrics.get("changedEventCountVersusAccepted") != 33 or metrics.get("changedOnsetCountVersusAccepted") != 33 or metrics.get("polyphonicChangedEventsVersusAccepted") != 0 or metrics.get("revertedFromV149") != 21:
        raise RuntimeError("V150 structural proof mismatch")

    candidate_bytes = (ROOT / EXPECTED["candidatePath"]).read_bytes()
    if sha256_bytes(candidate_bytes) != EXPECTED["candidateFileSha256"]:
        raise RuntimeError("V150 candidate file SHA mismatch")
    candidate_doc = json.loads(candidate_bytes)
    canonical = canonical_events(candidate_doc.get("renderEvents") or [])
    if len(canonical) != 1144 or sha256_json(canonical) != EXPECTED["candidateEventSha256"]:
        raise RuntimeError("V150 candidate event identity mismatch")

    pdf_bytes = (ROOT / EXPECTED["pdfPath"]).read_bytes()
    if sha256_bytes(pdf_bytes) != EXPECTED["pdfSha256"]:
        raise RuntimeError("V150 PDF evidence SHA mismatch")
    pdf = json.loads(pdf_bytes)
    if pdf.get("pdfEventFidelity") != 1.0 or pdf.get("candidateEventSha256") != EXPECTED["candidateEventSha256"]:
        raise RuntimeError("V150 PDF identity mismatch")

    baseline = load_json(ROOT / EXPECTED["baselinePath"])
    accepted = baseline.get("fullGoldCalibration") or {}
    baseline_metrics = accepted.get("gatedMetrics") or {}
    baseline_critical = int(accepted.get("criticalMismatchCount"))

    v149_bytes = (ROOT / EXPECTED["v149ScorePath"]).read_bytes()
    if sha256_bytes(v149_bytes) != EXPECTED["v149ScoreSha256"]:
        raise RuntimeError("V149 score result SHA mismatch")
    v149_report = json.loads(v149_bytes)
    expected_gold_sha = str((v149_report.get("reference") or {}).get("sha256") or "")
    if len(expected_gold_sha) != 64 or any(ch not in "0123456789abcdef" for ch in expected_gold_sha):
        raise RuntimeError("V149 persisted reference SHA is not valid 64-char lowercase hex")
    v149_metrics = (v149_report.get("score") or {}).get("gatedMetrics") or {}
    v149_critical = int((v149_report.get("score") or {}).get("criticalMismatchCount"))

    # Authorized reference boundary begins here.
    gold_bytes = (ROOT / EXPECTED["goldPath"]).read_bytes()
    actual_gold_sha = sha256_bytes(gold_bytes)
    if actual_gold_sha != expected_gold_sha:
        raise RuntimeError(f"Gold SHA mismatch: {actual_gold_sha}")
    reference = historical_wrapper.scorer.validate_reference(json.loads(gold_bytes))
    candidate_score = historical_wrapper.score_full_candidate(canonical, reference)

    candidate_metrics = candidate_score["gatedMetrics"]
    deltas_baseline = {k: float(candidate_metrics[k]) - float(baseline_metrics[k]) for k in METRICS}
    deltas_v149 = {k: float(candidate_metrics[k]) - float(v149_metrics[k]) for k in METRICS}
    report = {
        "schemaVersion": 15050,
        "classification": "v150-contextual-singleton-authorized-single-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "authorizationScope": "exactly-one-v150-contextual-singleton-gold-calibration-score",
        "candidate": {"eventCount": 1144, "canonicalEventSha256": EXPECTED["candidateEventSha256"], "fileSha256": EXPECTED["candidateFileSha256"], "changedEventsVersusAccepted": 33, "changedOnsetsVersusAccepted": 33, "polyphonicChangedEventsVersusAccepted": 0, "revertedFromV149": 21, "pdfEventFidelity": 1.0, "pdfEvidenceSha256": EXPECTED["pdfSha256"]},
        "reference": {"role": "gold-calibration-reference-not-unseen-holdout", "sha256": actual_gold_sha, "identitySource": "persisted-v149-score-result-reference-sha256"},
        "scoringChain": {"fullCalibrationWrapperGitBlob": EXPECTED["wrapperGitBlob"], "coreScorerGitBlob": EXPECTED["coreGitBlob"], "canonicalAdapterGitBlob": EXPECTED["adapterGitBlob"], "historicalFunction": "score_selected_conjunction_candidate.score_full_candidate", "scoreCallCount": 1},
        "score": candidate_score,
        "acceptedBaseline": {"name": baseline.get("name"), "gatedMetrics": baseline_metrics, "criticalMismatchCount": baseline_critical},
        "priorV149": {"gatedMetrics": v149_metrics, "criticalMismatchCount": v149_critical},
        "comparison": {"candidateDisplayVectorPercent": display_vector(candidate_metrics), "acceptedBaselineDisplayVectorPercent": display_vector(baseline_metrics), "v149DisplayVectorPercent": display_vector(v149_metrics), "gatedMetricDeltasVsAcceptedBaseline": deltas_baseline, "gatedMetricDeltasVsV149": deltas_v149, "criticalMismatchDeltaVsAcceptedBaseline": int(candidate_score["criticalMismatchCount"]) - baseline_critical, "criticalMismatchDeltaVsV149": int(candidate_score["criticalMismatchCount"]) - v149_critical, "displayVectorOrder": ["pitch-content", "pitch-timing", "string-fret-timing", "chord-pitch-set", "measure-coverage", "pdf-event-fidelity"]},
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()},
        "safety": {"candidateSearchRun": False, "alternateCandidateConstructed": False, "alternateContextRuleTested": False, "alternateThresholdTested": False, "retuningRun": False, "audioRecomputed": False, "modalGpuUsed": False, "productionIntegrated": False, "automaticPromotionAllowed": False, "scoreCallCount": 1},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"candidateDisplayVectorPercent": report["comparison"]["candidateDisplayVectorPercent"], "acceptedBaselineDisplayVectorPercent": report["comparison"]["acceptedBaselineDisplayVectorPercent"], "v149DisplayVectorPercent": report["comparison"]["v149DisplayVectorPercent"], "criticalMismatchCount": candidate_score["criticalMismatchCount"], "criticalMismatchDeltaVsAcceptedBaseline": report["comparison"]["criticalMismatchDeltaVsAcceptedBaseline"], "criticalMismatchDeltaVsV149": report["comparison"]["criticalMismatchDeltaVsV149"], "scoreCallCount": 1}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
