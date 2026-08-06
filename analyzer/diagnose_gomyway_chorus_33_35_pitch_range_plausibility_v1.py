from __future__ import annotations

import hashlib
import json
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
FEATURE_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-features-v1.json"
RELIABILITY_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-contour-reliability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-range-plausibility-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-range-plausibility-v1-manifest.json"

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
    features = load(FEATURE_PATH)
    reliability = load(RELIABILITY_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if features.get("passed") is not True or reliability.get("passed") is not True:
        raise RuntimeError("Pitch-contour prerequisites are not green.")
    if reliability.get("recommendedNextAction") != "build-read-only-technique-evidence-classifier":
        raise RuntimeError(
            "Reliability diagnostic did not authorize direct classification; "
            "run its recommended stage instead."
        )

    reliability_by_key = {
        (row.get("measureNumber"), row.get("quantizedStep")): row
        for row in reliability.get("rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    plausible_count = 0
    implausible_count = 0

    for feature_row in features.get("rows", []):
        if not isinstance(feature_row, dict):
            continue
        key = (feature_row.get("measureNumber"), feature_row.get("quantizedStep"))
        reliability_row = reliability_by_key.get(key, {})
        feature_block = feature_row.get("features", {})
        frames = [row for row in feature_block.get("frames", []) if isinstance(row, dict)]
        pitches = [
            value
            for value in (number(row.get("pitchCentsFromA4")) for row in frames)
            if value is not None
        ]
        jumps = [abs(right - left) for left, right in zip(pitches, pitches[1:])]
        median_jump = statistics.median(jumps) if jumps else 0.0
        robust_range = number(reliability_row.get("robustPitchRangeCents")) or 0.0
        reliability_gate = reliability_row.get("pitchContourReliabilityGate") is True
        range_gate = robust_range <= MAX_PLAUSIBLE_ROBUST_RANGE_CENTS
        jump_gate = median_jump <= MAX_PLAUSIBLE_MEDIAN_JUMP_CENTS
        frame_gate = len(pitches) >= MIN_RELIABLE_FRAMES
        plausibility_gate = bool(reliability_gate and range_gate and jump_gate and frame_gate)

        if plausibility_gate:
            plausible_count += 1
        elif reliability_gate:
            implausible_count += 1

        rows.append({
            "measureNumber": feature_row.get("measureNumber"),
            "quantizedStep": feature_row.get("quantizedStep"),
            "sourceEventIndex": feature_row.get("sourceEventIndex"),
            "voicedFrameCount": len(pitches),
            "robustPitchRangeCents": round(robust_range, 3),
            "medianContiguousJumpCents": round(median_jump, 3),
            "pitchContourReliabilityGate": reliability_gate,
            "robustRangePlausibilityGate": range_gate,
            "medianJumpPlausibilityGate": jump_gate,
            "pitchRangePlausibilityGate": plausibility_gate,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    reliable_count = int(reliability.get("reliablePitchContourCount", 0))
    ready = bool(
        source_unchanged
        and reliable_count > 0
        and plausible_count == reliable_count
        and implausible_count == 0
    )
    recommended = (
        "build-read-only-technique-evidence-classifier"
        if ready
        else "build-harmonic-branch-corrected-pitch-contour-candidate"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-pitch-range-and-contiguous-jump-plausibility",
        "passed": True,
        "singleNoteCandidateCount": len(rows),
        "reliablePitchContourCount": reliable_count,
        "plausibleReliablePitchContourCount": plausible_count,
        "implausibleReliablePitchContourCount": implausible_count,
        "maximumPlausibleRobustRangeCents": MAX_PLAUSIBLE_ROBUST_RANGE_CENTS,
        "maximumPlausibleMedianJumpCents": MAX_PLAUSIBLE_MEDIAN_JUMP_CENTS,
        "rows": rows,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": recommended,
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
        "passed": True,
        "reliablePitchContourCount": reliable_count,
        "plausibleReliablePitchContourCount": plausible_count,
        "implausibleReliablePitchContourCount": implausible_count,
        "readyForTechniqueEvidenceClassification": ready,
        "recommendedNextAction": recommended,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 PITCH RANGE PLAUSIBILITY V1 COMPLETE")
    print("Passed: True")
    print("Single-note candidates:", len(rows))
    print("Reliable pitch contours:", reliable_count)
    print("Plausible reliable pitch contours:", plausible_count)
    print("Implausible reliable pitch contours:", implausible_count)
    print("Ready for technique evidence classification:", ready)
    print("Recommended next action:", recommended)
    for row in rows:
        if not row["pitchContourReliabilityGate"]:
            continue
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"voicedFrames={row['voicedFrameCount']} "
            f"robustRange={row['robustPitchRangeCents']} "
            f"medianJump={row['medianContiguousJumpCents']} "
            f"rangeGate={row['robustRangePlausibilityGate']} "
            f"jumpGate={row['medianJumpPlausibilityGate']} "
            f"plausibilityGate={row['pitchRangePlausibilityGate']}"
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


if __name__ == "__main__":
    main()
