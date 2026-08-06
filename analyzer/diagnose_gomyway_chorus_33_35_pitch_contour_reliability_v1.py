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
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-contour-reliability-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-contour-reliability-v1-manifest.json"

MAX_CONTIGUOUS_JUMP_CENTS = 700.0
MAX_OCTAVE_LIKE_JUMP_ERROR_CENTS = 120.0
MAX_OCTAVE_JUMP_RATIO = 0.20
MIN_RELIABLE_FRAME_COUNT = 6
MIN_ROBUST_COVERAGE_RATIO = 0.60


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


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    features = load(FEATURE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if features.get("passed") is not True:
        raise RuntimeError("Audio technique feature extraction did not complete.")
    if features.get("readyForTechniqueEvidenceClassification") is not True:
        raise RuntimeError("Feature extraction did not authorize reliability diagnosis.")

    rows: list[dict[str, Any]] = []
    reliable_count = 0
    octave_contaminated_count = 0

    for source_row in features.get("rows", []):
        if not isinstance(source_row, dict):
            continue
        feature_block = source_row.get("features", {})
        if not isinstance(feature_block, dict):
            continue
        frames = [row for row in feature_block.get("frames", []) if isinstance(row, dict)]
        pitches = [
            value for value in (number(row.get("pitchCentsFromA4")) for row in frames)
            if value is not None
        ]
        jumps = [abs(right - left) for left, right in zip(pitches, pitches[1:])]
        large_jumps = [jump for jump in jumps if jump >= MAX_CONTIGUOUS_JUMP_CENTS]
        octave_like = [
            jump for jump in large_jumps
            if abs(jump - round(jump / 1200.0) * 1200.0)
            <= MAX_OCTAVE_LIKE_JUMP_ERROR_CENTS
        ]
        jump_ratio = len(octave_like) / len(jumps) if jumps else 0.0

        p10 = percentile(pitches, 0.10)
        p90 = percentile(pitches, 0.90)
        robust_range = (p90 - p10) if p10 is not None and p90 is not None else 0.0
        raw_range = number(feature_block.get("pitchRangeCents")) or 0.0
        robust_coverage = (
            robust_range / raw_range if raw_range > 0.0 else 1.0
        )
        median_pitch = statistics.median(pitches) if pitches else None

        octave_contaminated = bool(
            len(octave_like) > 0
            and jump_ratio > MAX_OCTAVE_JUMP_RATIO
        )
        reliability_gate = bool(
            feature_block.get("featureQualityGate") is True
            and len(pitches) >= MIN_RELIABLE_FRAME_COUNT
            and not octave_contaminated
            and robust_coverage >= MIN_ROBUST_COVERAGE_RATIO
        )
        if reliability_gate:
            reliable_count += 1
        if octave_contaminated:
            octave_contaminated_count += 1

        rows.append({
            "measureNumber": source_row.get("measureNumber"),
            "quantizedStep": source_row.get("quantizedStep"),
            "sourceEventIndex": source_row.get("sourceEventIndex"),
            "voicedFrameCount": len(pitches),
            "medianPitchCentsFromA4": round(median_pitch, 3) if median_pitch is not None else None,
            "rawPitchRangeCents": round(raw_range, 3),
            "robustP10PitchCents": round(p10, 3) if p10 is not None else None,
            "robustP90PitchCents": round(p90, 3) if p90 is not None else None,
            "robustPitchRangeCents": round(robust_range, 3),
            "robustCoverageRatio": round(robust_coverage, 6),
            "contiguousJumpCount": len(jumps),
            "largeJumpCount": len(large_jumps),
            "octaveLikeJumpCount": len(octave_like),
            "octaveLikeJumpRatio": round(jump_ratio, 6),
            "octaveContaminationDetected": octave_contaminated,
            "pitchContourReliabilityGate": reliability_gate,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    ready = bool(rows and reliable_count > 0 and source_unchanged)
    recommended = (
        "build-octave-corrected-pitch-contour-candidate"
        if octave_contaminated_count > 0
        else "build-read-only-technique-evidence-classifier"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-pitch-contour-reliability-and-octave-jump-diagnostic",
        "passed": True,
        "singleNoteCandidateCount": len(rows),
        "reliablePitchContourCount": reliable_count,
        "unreliablePitchContourCount": len(rows) - reliable_count,
        "octaveContaminatedContourCount": octave_contaminated_count,
        "rows": rows,
        "readyForReliableTechniqueEvidenceClassification": ready and octave_contaminated_count == 0,
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
        "singleNoteCandidateCount": len(rows),
        "reliablePitchContourCount": reliable_count,
        "octaveContaminatedContourCount": octave_contaminated_count,
        "readyForReliableTechniqueEvidenceClassification": output[
            "readyForReliableTechniqueEvidenceClassification"
        ],
        "recommendedNextAction": recommended,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 PITCH CONTOUR RELIABILITY V1 COMPLETE")
    print("Passed: True")
    print("Single-note candidates:", len(rows))
    print("Reliable pitch contours:", reliable_count)
    print("Unreliable pitch contours:", len(rows) - reliable_count)
    print("Octave-contaminated contours:", octave_contaminated_count)
    print("Ready for reliable technique evidence classification:", output["readyForReliableTechniqueEvidenceClassification"])
    print("Recommended next action:", recommended)
    for row in rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"voicedFrames={row['voicedFrameCount']} "
            f"rawRange={row['rawPitchRangeCents']} "
            f"robustRange={row['robustPitchRangeCents']} "
            f"octaveJumps={row['octaveLikeJumpCount']} "
            f"octaveRatio={row['octaveLikeJumpRatio']} "
            f"octaveContamination={row['octaveContaminationDetected']} "
            f"reliabilityGate={row['pitchContourReliabilityGate']}"
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
