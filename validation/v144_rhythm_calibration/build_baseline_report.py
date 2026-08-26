from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_REFERENCE_SHA256 = "18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac"
EXPECTED_CANONICAL_EVENT_SHA256 = "7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1"
EXPECTED_GATED_METRICS = {
    "pitchContentF1": 0.2830626450116009,
    "pitchTimingTolerantF1": 0.044547563805104405,
    "stringFretTimingTolerantF1": 0.03062645011600928,
    "chordPitchSetTolerantF1": 0.022757697456492636,
    "exactVoicingTolerantF1": 0.022757697456492636,
    "measureCoverageRecall": 1.0,
    "pdfEventFidelity": 1.0,
}
EXPECTED_CRITICAL_MISMATCHES = 1875
EXPECTED_GROSS_UNMATCHED_GENERATED = 1069
EXPECTED_GROSS_UNMATCHED_REFERENCE = 806


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_exact_float(actual: Any, expected: float, label: str) -> None:
    value = float(actual)
    if value != expected:
        raise ValueError(f"{label} changed: {value!r} != {expected!r}")


def metric_bucket(metric: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(metric, dict):
        return {}
    return {
        key: metric[key]
        for key in (
            "matched",
            "generated",
            "reference",
            "falsePositive",
            "falseNegative",
            "precision",
            "recall",
            "f1",
        )
        if key in metric
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Relabel and verify the frozen V5 score as a V144 calibration baseline."
    )
    parser.add_argument("legacy_score", type=Path)
    parser.add_argument("gold_reference", type=Path)
    parser.add_argument("v5_final_result", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    legacy = load_json(args.legacy_score)
    final = load_json(args.v5_final_result)
    reference_sha = sha256_file(args.gold_reference)
    if reference_sha != EXPECTED_REFERENCE_SHA256:
        raise ValueError(f"gold reference SHA mismatch: {reference_sha}")

    if legacy.get("frozenEventSha256") != EXPECTED_CANONICAL_EVENT_SHA256:
        raise ValueError("legacy scorer did not score the immutable frozen V5 event stream")
    if legacy.get("pdfEventSha256") != EXPECTED_CANONICAL_EVENT_SHA256:
        raise ValueError("legacy scorer PDF event identity changed")
    if float(legacy.get("pdfEventFidelity") or 0.0) != 1.0:
        raise ValueError("baseline PDF event fidelity must remain exactly 1.0")

    gated = legacy.get("gatedMetrics") or {}
    for name, expected in EXPECTED_GATED_METRICS.items():
        require_exact_float(gated.get(name), expected, name)

    critical = int(legacy.get("criticalMismatchCount") or 0)
    if critical != EXPECTED_CRITICAL_MISMATCHES:
        raise ValueError(f"critical mismatch count changed: {critical}")
    breakdown = legacy.get("criticalMismatchBreakdown") or {}
    if int(breakdown.get("grossUnmatchedGeneratedNotes") or 0) != EXPECTED_GROSS_UNMATCHED_GENERATED:
        raise ValueError("gross unmatched generated-note count changed")
    if int(breakdown.get("grossUnmatchedReferenceNotes") or 0) != EXPECTED_GROSS_UNMATCHED_REFERENCE:
        raise ValueError("gross unmatched reference-note count changed")

    historical_gated = final.get("gatedMetrics") or {}
    for name, expected in EXPECTED_GATED_METRICS.items():
        require_exact_float(historical_gated.get(name), expected, f"historical.{name}")
    if int(final.get("criticalMismatchCount") or 0) != EXPECTED_CRITICAL_MISMATCHES:
        raise ValueError("immutable historical critical mismatch count changed")

    metrics = legacy.get("metrics") or {}
    measure_coverage = metrics.get("measureCoverage") or {}
    if measure_coverage.get("missingReferenceMeasures") != []:
        raise ValueError("baseline unexpectedly lost professional-reference measure coverage")

    report = {
        "schemaVersion": 14401,
        "classification": "v144-rhythm-gold-calibration-baseline",
        "instrument": "rhythm",
        "evaluationRole": "calibration-baseline-not-unseen-holdout",
        "sourceCandidateRole": "immutable-v5-read-only-baseline",
        "protocol": {
            "v5WorkflowRerun": False,
            "v5CandidateModified": False,
            "v5ThresholdModified": False,
            "v5ResultModified": False,
            "productionModified": False,
            "mainModified": False,
            "modalGpuInvoked": False,
            "goldReferenceMayBeUsedForV144Calibration": True,
            "mayClaimUnseenGeneralization": False,
            "legacyScorerTerminologyRetainedInternally": True,
            "legacyScoringMode": legacy.get("scoringMode"),
        },
        "identities": {
            "goldReferenceSha256": reference_sha,
            "frozenV5CanonicalEventSha256": legacy.get("frozenEventSha256"),
            "pdfEventSha256": legacy.get("pdfEventSha256"),
        },
        "baseline": {
            "generatedEventCount": legacy.get("generatedEventCount"),
            "referenceNoteCount": legacy.get("referenceNoteCount"),
            "gatedMetrics": gated,
            "criticalMismatchCount": critical,
            "criticalMismatchBreakdown": breakdown,
            "near100CalibrationTargetReached": False,
        },
        "diagnosticBuckets": {
            "pitchContent": metric_bucket(metrics.get("pitchContentByMeasure")),
            "pitchTiming": metric_bucket(metrics.get("tolerantPitchTiming")),
            "stringFretTiming": metric_bucket(metrics.get("tolerantStringFretTiming")),
            "chordPitchSet": metric_bucket(metrics.get("chordPitchSet")),
            "exactChordVoicing": metric_bucket(metrics.get("chordVoicing")),
            "technique": metric_bucket(metrics.get("techniques")),
            "measureCoverage": measure_coverage,
            "rendering": {
                "pdfEventFidelity": legacy.get("pdfEventFidelity"),
                "pdfEventSha256": legacy.get("pdfEventSha256"),
            },
        },
        "priorityOrder": [
            "pitch-content-and-chord-set",
            "timing-and-onset-alignment",
            "string-fret-voicing",
            "technique-notation",
        ],
        "reproducesImmutableHistoricalV5ScoreExactly": True,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
