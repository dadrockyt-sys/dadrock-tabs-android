from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-post-correction-pitch-plausibility-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-post-correction-pitch-plausibility-v1-manifest.json"

MAX_PLAUSIBLE_ROBUST_RANGE_CENTS = 700.0
MAX_PLAUSIBLE_MEDIAN_JUMP_CENTS = 250.0
MIN_RELIABLE_FRAMES = 6


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


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    candidate = load(CANDIDATE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if candidate.get("passed") is not True:
        raise RuntimeError("Harmonic-branch correction candidate is not green.")
    if candidate.get("readyForPostCorrectionPlausibilityDiagnostic") is not True:
        raise RuntimeError("Correction candidate did not authorize post-correction diagnosis.")
    if candidate.get("allImplausibleContoursPassedCorrectionGate") is not True:
        raise RuntimeError("Not all implausible contours passed the correction gate.")

    rows: list[dict[str, Any]] = []
    plausible_count = 0
    corrected_count = 0
    failed_count = 0

    for row in candidate.get("rows", []):
        if not isinstance(row, dict):
            continue
        frames = [frame for frame in row.get("frames", []) if isinstance(frame, dict)]
        pitches = [
            value
            for value in (
                number(frame.get("correctedPitchCentsFromA4", frame.get("pitchCentsFromA4")))
                for frame in frames
            )
            if value is not None
        ]
        jumps = [abs(right - left) for left, right in zip(pitches, pitches[1:])]
        median_jump = statistics.median(jumps) if jumps else 0.0

        corrected_metrics = row.get("correctedMetrics", {})
        robust_range = number(corrected_metrics.get("robustRangeCents"))
        if robust_range is None:
            robust_range = number(corrected_metrics.get("correctedRobustRangeCents"))
        if robust_range is None:
            robust_range = 0.0

        correction_applied = bool(
            row.get("harmonicBranchCorrectionApplied") is True
            or row.get("octaveCorrectionApplied") is True
            or int(row.get("nonzeroBranchShiftFrameCount", row.get("nonzeroOctaveShiftFrameCount", 0)) or 0) > 0
        )
        if correction_applied:
            corrected_count += 1

        frame_gate = len(pitches) >= MIN_RELIABLE_FRAMES
        range_gate = robust_range <= MAX_PLAUSIBLE_ROBUST_RANGE_CENTS
        jump_gate = median_jump <= MAX_PLAUSIBLE_MEDIAN_JUMP_CENTS
        candidate_gate = row.get("correctedPitchContourQualityGate") is True
        plausibility_gate = bool(frame_gate and range_gate and jump_gate and candidate_gate)
        if plausibility_gate:
            plausible_count += 1
        else:
            failed_count += 1

        rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "correctionApplied": correction_applied,
            "voicedFrameCount": len(pitches),
            "correctedRobustPitchRangeCents": round(robust_range, 3),
            "correctedMedianContiguousJumpCents": round(median_jump, 3),
            "frameCountGate": frame_gate,
            "correctedRangePlausibilityGate": range_gate,
            "correctedMedianJumpPlausibilityGate": jump_gate,
            "candidateCorrectionQualityGate": candidate_gate,
            "postCorrectionPitchPlausibilityGate": plausibility_gate,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    expected_count = int(candidate.get("singleNoteCandidateCount", -1))
    all_pass = bool(rows and len(rows) == expected_count and failed_count == 0)
    ready = bool(source_unchanged and all_pass)

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-post-harmonic-branch-correction-pitch-plausibility",
        "passed": source_unchanged and len(rows) == expected_count,
        "singleNoteCandidateCount": len(rows),
        "harmonicBranchCorrectedContourCount": corrected_count,
        "postCorrectionPlausibilityPassedCount": plausible_count,
        "postCorrectionPlausibilityFailedCount": failed_count,
        "allPitchContoursPassedPostCorrectionPlausibility": all_pass,
        "maximumPlausibleRobustRangeCents": MAX_PLAUSIBLE_ROBUST_RANGE_CENTS,
        "maximumPlausibleMedianJumpCents": MAX_PLAUSIBLE_MEDIAN_JUMP_CENTS,
        "rows": rows,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": (
            "build-read-only-technique-evidence-classifier-v1"
            if ready
            else "diagnose-residual-corrected-pitch-contour-failures"
        ),
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
        "passed": output["passed"],
        "singleNoteCandidateCount": len(rows),
        "harmonicBranchCorrectedContourCount": corrected_count,
        "postCorrectionPlausibilityPassedCount": plausible_count,
        "postCorrectionPlausibilityFailedCount": failed_count,
        "allPitchContoursPassedPostCorrectionPlausibility": all_pass,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": output["recommendedNextAction"],
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 POST-CORRECTION PITCH PLAUSIBILITY V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Single-note candidates:", len(rows))
    print("Harmonic-branch corrected contours:", corrected_count)
    print("Post-correction plausibility passed:", plausible_count)
    print("Post-correction plausibility failed:", failed_count)
    print("All pitch contours passed post-correction plausibility:", all_pass)
    print("Ready for technique evidence classification:", ready)
    print("Recommended next action:", output["recommendedNextAction"])
    for row in rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"corrected={row['correctionApplied']} "
            f"voicedFrames={row['voicedFrameCount']} "
            f"correctedRobustRange={row['correctedRobustPitchRangeCents']} "
            f"correctedMedianJump={row['correctedMedianContiguousJumpCents']} "
            f"rangeGate={row['correctedRangePlausibilityGate']} "
            f"jumpGate={row['correctedMedianJumpPlausibilityGate']} "
            f"qualityGate={row['postCorrectionPitchPlausibilityGate']}"
        )
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

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
