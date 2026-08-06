from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
FEATURE_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-features-v1.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1.json"
PLAUSIBILITY_PATH = PUBLIC / "gomyway-chorus-33-35-post-correction-pitch-plausibility-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-residual-corrected-pitch-contour-failures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-residual-corrected-pitch-contour-failures-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def key(row: dict[str, Any]) -> tuple[Any, Any]:
    return row.get("measureNumber"), row.get("quantizedStep")


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    features = load(FEATURE_PATH)
    candidate = load(CANDIDATE_PATH)
    plausibility = load(PLAUSIBILITY_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if plausibility.get("passed") is not True:
        raise RuntimeError("Post-correction plausibility diagnostic is not green.")
    if plausibility.get("recommendedNextAction") != "diagnose-residual-corrected-pitch-contour-failures":
        raise RuntimeError("Post-correction diagnostic did not authorize residual failure diagnosis.")

    feature_by_key = {
        key(row): row for row in features.get("rows", []) if isinstance(row, dict)
    }
    candidate_by_key = {
        key(row): row for row in candidate.get("rows", []) if isinstance(row, dict)
    }

    failures: list[dict[str, Any]] = []
    for row in plausibility.get("rows", []):
        if not isinstance(row, dict) or row.get("postCorrectionPitchPlausibilityGate") is True:
            continue
        row_key = key(row)
        feature_row = feature_by_key.get(row_key, {})
        feature_block = feature_row.get("features", {}) if isinstance(feature_row, dict) else {}
        candidate_row = candidate_by_key.get(row_key, {})

        frame_gate = row.get("frameCountGate") is True
        range_gate = row.get("correctedRangePlausibilityGate") is True
        jump_gate = row.get("correctedMedianJumpPlausibilityGate") is True
        candidate_gate = row.get("candidateCorrectionQualityGate") is True
        feature_gate = feature_block.get("featureQualityGate") is True if isinstance(feature_block, dict) else False

        failed_reasons: list[str] = []
        if not frame_gate:
            failed_reasons.append("insufficient-corrected-frames")
        if not range_gate:
            failed_reasons.append("corrected-range-implausible")
        if not jump_gate:
            failed_reasons.append("corrected-median-jump-implausible")
        if not candidate_gate:
            failed_reasons.append("candidate-correction-quality-gate-false")
        if not feature_gate:
            failed_reasons.append("original-feature-quality-gate-false")

        failures.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "voicedFrameCount": row.get("voicedFrameCount"),
            "correctedRobustPitchRangeCents": row.get("correctedRobustPitchRangeCents"),
            "correctedMedianContiguousJumpCents": row.get("correctedMedianContiguousJumpCents"),
            "frameCountGate": frame_gate,
            "correctedRangePlausibilityGate": range_gate,
            "correctedMedianJumpPlausibilityGate": jump_gate,
            "candidateCorrectionQualityGate": candidate_gate,
            "originalFeatureQualityGate": feature_gate,
            "correctionApplied": row.get("correctionApplied") is True,
            "failedReasons": failed_reasons,
            "readOnly": True,
        })

    only_candidate_gate_failures = bool(
        failures
        and all(
            failure["frameCountGate"]
            and failure["correctedRangePlausibilityGate"]
            and failure["correctedMedianJumpPlausibilityGate"]
            and not failure["candidateCorrectionQualityGate"]
            for failure in failures
        )
    )
    any_original_feature_failure = any(
        not failure["originalFeatureQualityGate"] for failure in failures
    )

    if only_candidate_gate_failures and any_original_feature_failure:
        recommended = "build-targeted-low-confidence-pitch-reextraction-plan-v1"
    elif only_candidate_gate_failures:
        recommended = "recompute-candidate-quality-gates-from-corrected-contours"
    else:
        recommended = "inspect-residual-corrected-contour-evidence"

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    expected_failures = int(plausibility.get("postCorrectionPlausibilityFailedCount", -1))
    passed = bool(source_unchanged and len(failures) == expected_failures and len(failures) > 0)

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-residual-post-correction-pitch-contour-failure-diagnostic",
        "passed": passed,
        "residualFailureCount": len(failures),
        "onlyCandidateQualityGateFailures": only_candidate_gate_failures,
        "anyOriginalFeatureQualityFailure": any_original_feature_failure,
        "rows": failures,
        "recommendedNextAction": recommended,
        "readyForTechniqueEvidenceClassification": False,
        "bendSupportClaimed": False,
        "vibratoSupportClaimed": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceEventCount": 949,
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "residualFailureCount": len(failures),
        "onlyCandidateQualityGateFailures": only_candidate_gate_failures,
        "anyOriginalFeatureQualityFailure": any_original_feature_failure,
        "recommendedNextAction": recommended,
        "readyForTechniqueEvidenceClassification": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 RESIDUAL CORRECTED PITCH CONTOUR FAILURES V1 COMPLETE")
    print("Passed:", passed)
    print("Residual failures:", len(failures))
    print("Only candidate quality-gate failures:", only_candidate_gate_failures)
    print("Any original feature-quality failure:", any_original_feature_failure)
    print("Recommended next action:", recommended)
    for failure in failures:
        print(
            f"measure={failure['measureNumber']} step={failure['quantizedStep']} "
            f"voicedFrames={failure['voicedFrameCount']} "
            f"rangeGate={failure['correctedRangePlausibilityGate']} "
            f"jumpGate={failure['correctedMedianJumpPlausibilityGate']} "
            f"candidateGate={failure['candidateCorrectionQualityGate']} "
            f"featureGate={failure['originalFeatureQualityGate']} "
            f"reasons={','.join(failure['failedReasons'])}"
        )
    print("Ready for technique evidence classification: False")
    print("Bend support claimed: False")
    print("Vibrato support claimed: False")
    print("Audio technique support claimed: False")
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
