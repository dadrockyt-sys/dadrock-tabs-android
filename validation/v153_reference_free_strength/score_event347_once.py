#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
for entry in (ROOT / "validation/v144_rhythm_calibration", ROOT / "validation/rhythm_holdout"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

import score_selected_conjunction_candidate as historical_wrapper  # noqa: E402
from canonical import canonical_events, sha256_json  # noqa: E402

E = {
    "prereg": "debug/v153-reference-free-strength/phase-c-scoring-preregistration.json",
    "preregBlob": "361208d8e57c614e8a509eecb5680f0d6daf841b",
    "candidate": "debug/v153-reference-free-strength/candidate/candidate.json",
    "candidateBlob": "975ab36c234b423d1b56e59588e960f7d9d7103f",
    "candidateFileSha": "f90889acb034b61036951843846e2954d0c685f005a35eb667360a5a57391e67",
    "candidateEventSha": "df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b",
    "proof": "debug/v153-reference-free-strength/candidate/construction-proof.json",
    "proofBlob": "efe6107df544086f62babf737ef044116ed551f0",
    "proofSha": "8c4fe77799fb247c0a744d3650aed2f69ed44aa43d7ee5b2e97c5d4211deedc7",
    "pdf": "debug/v153-reference-free-strength/candidate/pdf-event-fidelity.json",
    "pdfBlob": "f6b1b7b463c9b55e2e70fb116d97f3508b6c269f",
    "pdfSha": "fe06f93619bbe51862933a1e235f7ff2f01356bcb02167b5b6b934a39784f33e",
    "manifest": "debug/v153-reference-free-strength/candidate/preservation-manifest.json",
    "manifestBlob": "f690aeefd81090b4f558353cb3f30b7fe4dca0b9",
    "manifestSha": "174c8b060b02c8eb1cb1b147c150d922f169d9cbfec2061640096efdd9e31149",
    "prior": "debug/v152-active-recurrence/phase-c-score/score-result.json",
    "priorBlob": "05042410ecd5b9793e1182a1bb1dd63ae949ab51",
    "priorSha": "cc549c6f0a33c0b90648433494ef36a31b5647191058e28b9ea089f12cab7ef4",
    "baseline": "debug/v144-rhythm-calibration/selected/v144-singleton-onset-replacement-selected-baseline.json",
    "baselineBlob": "acd12ab68ad16b8faabf38ddc9e1cc0c1e7c4b68",
    "wrapper": "validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py",
    "wrapperBlob": "1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb",
    "core": "validation/rhythm_holdout/score_rhythm_holdout.py",
    "coreBlob": "cc4bf61a99f22bf87a6c255e5a81220fbc82223b",
    "adapter": "validation/rhythm_holdout/canonical.py",
    "adapterBlob": "088d44827fb23e20d9aeeb4944a672989af5846c",
    "gold": "debug/v144-rhythm-calibration/reference/professional-rhythm-gold-reference.json",
    "goldSha": "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac",
}

METRICS = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "exactVoicingTolerantF1",
    "measureCoverageRecall",
)
DISPLAY = (
    "pitchContentF1",
    "pitchTimingTolerantF1",
    "stringFretTimingTolerantF1",
    "chordPitchSetTolerantF1",
    "measureCoverageRecall",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def load(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def require_blob(path: str, expected: str) -> None:
    actual = blob(path)
    if actual != expected:
        raise RuntimeError(f"blob mismatch {path}: {actual} != {expected}")


def vector(metrics: dict[str, Any]) -> list[float]:
    return [100.0 * float(metrics[key]) for key in DISPLAY] + [100.0]


def main() -> int:
    parser = argparse.ArgumentParser(description="One-use CPU Gold score for immutable V153 event-347 candidate")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if output.exists():
        raise RuntimeError("one-use output already exists")

    for path, expected in (
        (E["prereg"], E["preregBlob"]),
        (E["candidate"], E["candidateBlob"]),
        (E["proof"], E["proofBlob"]),
        (E["pdf"], E["pdfBlob"]),
        (E["manifest"], E["manifestBlob"]),
        (E["prior"], E["priorBlob"]),
        (E["baseline"], E["baselineBlob"]),
        (E["wrapper"], E["wrapperBlob"]),
        (E["core"], E["coreBlob"]),
        (E["adapter"], E["adapterBlob"]),
    ):
        require_blob(path, expected)

    prereg = load(E["prereg"])
    policy = prereg.get("authorizationPolicy") or {}
    rules = prereg.get("frozenRules") or {}
    if prereg.get("classification") != "cpu-only-one-use-gold-calibration-score-preregistration":
        raise RuntimeError("scoring preregistration classification mismatch")
    if policy.get("cpuScoringRequiresFreshAuthorization") is not False:
        raise RuntimeError("CPU scoring policy mismatch")
    if policy.get("modalL4CudaGpuRequiresFreshAuthorization") is not True:
        raise RuntimeError("GPU authorization policy mismatch")
    if int(rules.get("maximumScoreCalls", -1)) != 1:
        raise RuntimeError("score call limit mismatch")
    for key in (
        "candidateSearchAllowed",
        "alternateCandidateAllowed",
        "candidateModificationAllowed",
        "thresholdWeightFilterRuleTuningAllowed",
        "audioRecomputeAllowed",
        "modalL4CudaGpuAllowedWithoutFreshAuthorization",
        "productionPromotionAllowed",
        "automaticPromotion",
    ):
        if rules.get(key) is not False:
            raise RuntimeError(f"forbidden rule changed: {key}")

    candidate_bytes = (ROOT / E["candidate"]).read_bytes()
    proof_bytes = (ROOT / E["proof"]).read_bytes()
    pdf_bytes = (ROOT / E["pdf"]).read_bytes()
    manifest_bytes = (ROOT / E["manifest"]).read_bytes()
    prior_bytes = (ROOT / E["prior"]).read_bytes()
    if sha256_bytes(candidate_bytes) != E["candidateFileSha"]:
        raise RuntimeError("candidate file SHA mismatch")
    if sha256_bytes(proof_bytes) != E["proofSha"]:
        raise RuntimeError("construction proof SHA mismatch")
    if sha256_bytes(pdf_bytes) != E["pdfSha"]:
        raise RuntimeError("PDF evidence SHA mismatch")
    if sha256_bytes(manifest_bytes) != E["manifestSha"]:
        raise RuntimeError("preservation manifest SHA mismatch")
    if sha256_bytes(prior_bytes) != E["priorSha"]:
        raise RuntimeError("prior V152 score SHA mismatch")

    proof = json.loads(proof_bytes)
    pdf = json.loads(pdf_bytes)
    manifest = json.loads(manifest_bytes)
    prior = json.loads(prior_bytes)
    candidate = canonical_events(json.loads(candidate_bytes).get("renderEvents") or [])
    if len(candidate) != 1144 or sha256_json(candidate) != E["candidateEventSha"]:
        raise RuntimeError("candidate canonical identity mismatch")
    metrics = proof.get("metrics") or {}
    if proof.get("gate") != "GO" or proof.get("selectedEventIndex") != 347:
        raise RuntimeError("construction proof gate mismatch")
    if metrics.get("changedEventIndices") != [347] or metrics.get("changedEventCountVersusAccepted") != 1:
        raise RuntimeError("changed-event identity mismatch")
    if metrics.get("changedOnsetCountVersusAccepted") != 1 or metrics.get("polyphonicChangedEventsVersusAccepted") != 0:
        raise RuntimeError("changed-onset/polyphonic identity mismatch")
    if pdf.get("pdfEventFidelity") != 1.0 or manifest.get("referenceFacingScoringAuthorization") is not False:
        raise RuntimeError("construction preservation mismatch")

    baseline = load(E["baseline"])
    accepted = baseline.get("fullGoldCalibration") or {}
    baseline_metrics = accepted.get("gatedMetrics") or {}
    baseline_critical = int(accepted["criticalMismatchCount"])

    prior_score = prior.get("score") or {}
    prior_metrics = prior_score.get("gatedMetrics") or {}
    prior_critical = int(prior_score["criticalMismatchCount"])
    prior_reference_sha = str((prior.get("reference") or {}).get("sha256") or "")
    if prior_reference_sha != E["goldSha"]:
        raise RuntimeError("prior V152 reference identity mismatch")

    # CPU-only reference-facing scoring boundary. No Modal/L4/CUDA/GPU use.
    gold_bytes = (ROOT / E["gold"]).read_bytes()
    actual_gold_sha = sha256_bytes(gold_bytes)
    if actual_gold_sha != E["goldSha"]:
        raise RuntimeError(f"Gold SHA mismatch: {actual_gold_sha}")
    reference = historical_wrapper.scorer.validate_reference(json.loads(gold_bytes))
    score = historical_wrapper.score_full_candidate(candidate, reference)
    score_metrics = score["gatedMetrics"]

    report = {
        "schemaVersion": 15350,
        "classification": "v153-event347-cpu-single-gold-calibration-score",
        "evaluationRole": "full-gold-calibration-not-unseen-holdout",
        "authorizationPolicy": {
            "cpuScoringAtAssistantDiscretion": True,
            "modalL4CudaGpuFreshAuthorizationRequired": True,
        },
        "candidate": {
            "eventCount": 1144,
            "canonicalEventSha256": E["candidateEventSha"],
            "fileSha256": E["candidateFileSha"],
            "changedEventsVersusAccepted": 1,
            "changedEventIndices": [347],
            "changedOnsetsVersusAccepted": 1,
            "polyphonicChangedEventsVersusAccepted": 0,
            "pdfEventFidelity": 1.0,
        },
        "reference": {
            "role": "gold-calibration-reference-not-unseen-holdout",
            "sha256": actual_gold_sha,
            "identitySource": "sealed V152 score result and V153 scoring preregistration",
        },
        "score": score,
        "acceptedBaseline": {
            "name": baseline.get("name"),
            "gatedMetrics": baseline_metrics,
            "criticalMismatchCount": baseline_critical,
        },
        "priorV152": {
            "candidateEventSha256": (prior.get("candidate") or {}).get("canonicalEventSha256"),
            "gatedMetrics": prior_metrics,
            "criticalMismatchCount": prior_critical,
        },
        "comparison": {
            "candidateDisplayVectorPercent": vector(score_metrics),
            "acceptedBaselineDisplayVectorPercent": vector(baseline_metrics),
            "v152DisplayVectorPercent": vector(prior_metrics),
            "gatedMetricDeltasVsAcceptedBaseline": {
                key: float(score_metrics[key]) - float(baseline_metrics[key]) for key in METRICS
            },
            "gatedMetricDeltasVsV152": {
                key: float(score_metrics[key]) - float(prior_metrics[key]) for key in METRICS
            },
            "criticalMismatchDeltaVsAcceptedBaseline": int(score["criticalMismatchCount"]) - baseline_critical,
            "criticalMismatchDeltaVsV152": int(score["criticalMismatchCount"]) - prior_critical,
            "displayVectorOrder": [
                "pitch-content",
                "pitch-timing",
                "string-fret-timing",
                "chord-pitch-set",
                "measure-coverage",
                "pdf-event-fidelity",
            ],
        },
        "scoringChain": {
            "scoringPreregistrationGitBlob": E["preregBlob"],
            "fullCalibrationWrapperGitBlob": E["wrapperBlob"],
            "coreScorerGitBlob": E["coreBlob"],
            "canonicalAdapterGitBlob": E["adapterBlob"],
            "historicalFunction": "score_selected_conjunction_candidate.score_full_candidate",
            "scoreCallCount": 1,
        },
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "gitHead": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        },
        "safety": {
            "candidateSearchRun": False,
            "alternateCandidateConstructed": False,
            "candidateModified": False,
            "thresholdWeightFilterRuleTuning": False,
            "audioRecomputed": False,
            "modalL4CudaGpuUsed": False,
            "productionIntegrated": False,
            "automaticPromotion": False,
            "scoreCallCount": 1,
        },
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidateDisplayVectorPercent": report["comparison"]["candidateDisplayVectorPercent"],
        "acceptedBaselineDisplayVectorPercent": report["comparison"]["acceptedBaselineDisplayVectorPercent"],
        "v152DisplayVectorPercent": report["comparison"]["v152DisplayVectorPercent"],
        "criticalMismatchCount": score["criticalMismatchCount"],
        "criticalMismatchDeltaVsAcceptedBaseline": report["comparison"]["criticalMismatchDeltaVsAcceptedBaseline"],
        "criticalMismatchDeltaVsV152": report["comparison"]["criticalMismatchDeltaVsV152"],
        "scoreCallCount": 1,
        "modalL4CudaGpuUsed": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
