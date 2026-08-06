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
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1.json"
FAILURE_PATH = PUBLIC / "gomyway-chorus-33-35-residual-corrected-pitch-contour-failures-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1-manifest.json"

MIN_RELIABLE_FRAMES = 6
MAX_ROBUST_RANGE_CENTS = 700.0
MAX_MEDIAN_JUMP_CENTS = 250.0


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


def percentile(values: list[float], fraction: float) -> float:
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
    candidate = load(CANDIDATE_PATH)
    failures = load(FAILURE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if features.get("passed") is not True or candidate.get("passed") is not True:
        raise RuntimeError("Corrected pitch prerequisites are not green.")
    if failures.get("passed") is not True:
        raise RuntimeError("Residual failure diagnostic is not green.")
    if failures.get("recommendedNextAction") != "recompute-candidate-quality-gates-from-corrected-contours":
        raise RuntimeError("Residual diagnostic did not authorize gate recomputation.")

    feature_by_key = {
        (row.get("measureNumber"), row.get("quantizedStep")): row
        for row in features.get("rows", []) if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    recomputed_count = 0
    passed_count = 0
    failed_count = 0

    for row in candidate.get("rows", []):
        if not isinstance(row, dict):
            continue
        key = (row.get("measureNumber"), row.get("quantizedStep"))
        feature_row = feature_by_key.get(key, {})
        feature_block = feature_row.get("features", {}) if isinstance(feature_row, dict) else {}
        feature_gate = feature_block.get("featureQualityGate") is True

        frames = [frame for frame in row.get("frames", []) if isinstance(frame, dict)]
        pitches = [
            value for value in (
                number(frame.get("correctedPitchCentsFromA4", frame.get("pitchCentsFromA4")))
                for frame in frames
            ) if value is not None
        ]
        jumps = [abs(right - left) for left, right in zip(pitches, pitches[1:])]
        robust_range = (
            percentile(pitches, 0.90) - percentile(pitches, 0.10)
            if pitches else 0.0
        )
        median_jump = statistics.median(jumps) if jumps else 0.0

        old_gate = row.get("correctedPitchContourQualityGate") is True
        frame_gate = len(pitches) >= MIN_RELIABLE_FRAMES
        range_gate = robust_range <= MAX_ROBUST_RANGE_CENTS
        jump_gate = median_jump <= MAX_MEDIAN_JUMP_CENTS
        new_gate = bool(feature_gate and frame_gate and range_gate and jump_gate)
        if new_gate != old_gate:
            recomputed_count += 1
        if new_gate:
            passed_count += 1
        else:
            failed_count += 1

        output_row = dict(row)
        output_row["previousCorrectedPitchContourQualityGate"] = old_gate
        output_row["featureQualityGate"] = feature_gate
        output_row["recomputedFrameCountGate"] = frame_gate
        output_row["recomputedRobustRangeCents"] = round(robust_range, 3)
        output_row["recomputedRangePlausibilityGate"] = range_gate
        output_row["recomputedMedianContiguousJumpCents"] = round(median_jump, 3)
        output_row["recomputedMedianJumpPlausibilityGate"] = jump_gate
        output_row["correctedPitchContourQualityGate"] = new_gate
        output_row["qualityGateRecomputedFromCorrectedContour"] = True
        rows.append(output_row)

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    expected_count = int(candidate.get("singleNoteCandidateCount", -1))
    all_pass = bool(rows and len(rows) == expected_count and failed_count == 0)
    ready = bool(source_unchanged and all_pass)

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-recomputed-corrected-pitch-quality-gates",
        "passed": source_unchanged and len(rows) == expected_count,
        "singleNoteCandidateCount": len(rows),
        "qualityGateChanges": recomputed_count,
        "correctedPitchQualityGatePassedCount": passed_count,
        "correctedPitchQualityGateFailedCount": failed_count,
        "allCorrectedPitchQualityGatesPassed": all_pass,
        "rows": rows,
        "readyForFinalPostCorrectionPlausibilityProof": ready,
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
        "qualityGateChanges": recomputed_count,
        "correctedPitchQualityGateFailedCount": failed_count,
        "allCorrectedPitchQualityGatesPassed": all_pass,
        "readyForFinalPostCorrectionPlausibilityProof": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 RECOMPUTED CORRECTED PITCH QUALITY CANDIDATE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Single-note candidates:", len(rows))
    print("Quality gate changes:", recomputed_count)
    print("Corrected pitch quality gates passed:", passed_count)
    print("Corrected pitch quality gates failed:", failed_count)
    print("All corrected pitch quality gates passed:", all_pass)
    for row in rows:
        if row["previousCorrectedPitchContourQualityGate"] == row["correctedPitchContourQualityGate"]:
            continue
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"oldGate={row['previousCorrectedPitchContourQualityGate']} "
            f"newGate={row['correctedPitchContourQualityGate']} "
            f"featureGate={row['featureQualityGate']} "
            f"frameGate={row['recomputedFrameCountGate']} "
            f"range={row['recomputedRobustRangeCents']} "
            f"rangeGate={row['recomputedRangePlausibilityGate']} "
            f"medianJump={row['recomputedMedianContiguousJumpCents']} "
            f"jumpGate={row['recomputedMedianJumpPlausibilityGate']}"
        )
    print("Ready for final post-correction plausibility proof:", ready)
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
