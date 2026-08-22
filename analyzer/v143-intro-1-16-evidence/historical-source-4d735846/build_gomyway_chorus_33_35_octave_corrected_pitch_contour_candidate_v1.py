from __future__ import annotations

import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
FEATURE_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-features-v1.json"
RELIABILITY_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-contour-reliability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-octave-corrected-pitch-contour-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-octave-corrected-pitch-contour-candidate-v1-manifest.json"

OCTAVE_CENTS = 1200.0
MAX_OCTAVE_SHIFT = 4
MAX_CONTIGUOUS_JUMP_CENTS = 700.0
MAX_OCTAVE_LIKE_ERROR_CENTS = 120.0
MIN_RELIABLE_FRAMES = 6
MAX_CORRECTED_ROBUST_RANGE_CENTS = 1200.0


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


def octave_correct(pitches: list[float]) -> tuple[list[float], list[int]]:
    if not pitches:
        return [], []
    corrected = [pitches[0]]
    shifts = [0]
    for pitch in pitches[1:]:
        previous = corrected[-1]
        candidates = [
            (pitch + shift * OCTAVE_CENTS, shift)
            for shift in range(-MAX_OCTAVE_SHIFT, MAX_OCTAVE_SHIFT + 1)
        ]
        selected_pitch, selected_shift = min(
            candidates,
            key=lambda item: (abs(item[0] - previous), abs(item[1])),
        )
        corrected.append(selected_pitch)
        shifts.append(selected_shift)

    # Preserve the original contour's central octave while removing local
    # octave branch changes. A uniform octave translation changes no contour
    # shape and makes the candidate easier to compare with the raw track.
    raw_median = statistics.median(pitches)
    corrected_median = statistics.median(corrected)
    uniform_shift = round((raw_median - corrected_median) / OCTAVE_CENTS)
    corrected = [value + uniform_shift * OCTAVE_CENTS for value in corrected]
    shifts = [shift + uniform_shift for shift in shifts]
    return corrected, shifts


def contour_metrics(pitches: list[float]) -> dict[str, Any]:
    if not pitches:
        return {
            "rawRangeCents": 0.0,
            "robustRangeCents": 0.0,
            "largeJumpCount": 0,
            "octaveLikeJumpCount": 0,
        }
    jumps = [abs(right - left) for left, right in zip(pitches, pitches[1:])]
    large = [jump for jump in jumps if jump >= MAX_CONTIGUOUS_JUMP_CENTS]
    octave_like = [
        jump for jump in large
        if abs(jump - round(jump / OCTAVE_CENTS) * OCTAVE_CENTS)
        <= MAX_OCTAVE_LIKE_ERROR_CENTS
    ]
    return {
        "rawRangeCents": round(max(pitches) - min(pitches), 3),
        "robustRangeCents": round(percentile(pitches, 0.90) - percentile(pitches, 0.10), 3),
        "largeJumpCount": len(large),
        "octaveLikeJumpCount": len(octave_like),
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    features = load(FEATURE_PATH)
    reliability = load(RELIABILITY_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if features.get("passed") is not True or reliability.get("passed") is not True:
        raise RuntimeError("Pitch feature prerequisites are not green.")
    if reliability.get("recommendedNextAction") != "build-octave-corrected-pitch-contour-candidate":
        raise RuntimeError("Reliability diagnostic did not authorize octave correction.")

    feature_by_key = {
        (row.get("measureNumber"), row.get("quantizedStep")): row
        for row in features.get("rows", [])
        if isinstance(row, dict)
    }
    reliability_by_key = {
        (row.get("measureNumber"), row.get("quantizedStep")): row
        for row in reliability.get("rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    corrected_count = 0
    corrected_gate_count = 0

    for key, feature_row in feature_by_key.items():
        reliability_row = reliability_by_key.get(key, {})
        feature_block = feature_row.get("features", {})
        frames = [row for row in feature_block.get("frames", []) if isinstance(row, dict)]
        raw_pitches = [
            value for value in (number(row.get("pitchCentsFromA4")) for row in frames)
            if value is not None
        ]
        contaminated = reliability_row.get("octaveContaminationDetected") is True
        corrected_pitches, octave_shifts = (
            octave_correct(raw_pitches) if contaminated else (list(raw_pitches), [0] * len(raw_pitches))
        )
        raw_metrics = contour_metrics(raw_pitches)
        corrected_metrics = contour_metrics(corrected_pitches)
        correction_applied = bool(contaminated and any(shift != 0 for shift in octave_shifts))
        if correction_applied:
            corrected_count += 1

        corrected_gate = bool(
            len(corrected_pitches) >= MIN_RELIABLE_FRAMES
            and corrected_metrics["octaveLikeJumpCount"] == 0
            and corrected_metrics["robustRangeCents"] <= MAX_CORRECTED_ROBUST_RANGE_CENTS
        )
        if corrected_gate:
            corrected_gate_count += 1

        corrected_frames: list[dict[str, Any]] = []
        for index, frame in enumerate(frames):
            row = dict(frame)
            row["rawPitchCentsFromA4"] = row.get("pitchCentsFromA4")
            row["octaveShiftCount"] = octave_shifts[index] if index < len(octave_shifts) else 0
            row["correctedPitchCentsFromA4"] = round(corrected_pitches[index], 3)
            corrected_frames.append(row)

        rows.append({
            "measureNumber": feature_row.get("measureNumber"),
            "quantizedStep": feature_row.get("quantizedStep"),
            "sourceEventIndex": feature_row.get("sourceEventIndex"),
            "octaveContaminationDetected": contaminated,
            "octaveCorrectionApplied": correction_applied,
            "correctedFrameCount": len(corrected_frames),
            "nonzeroOctaveShiftFrameCount": sum(shift != 0 for shift in octave_shifts),
            "rawMetrics": raw_metrics,
            "correctedMetrics": corrected_metrics,
            "correctedPitchContourQualityGate": corrected_gate,
            "frames": corrected_frames,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    contaminated_count = int(reliability.get("octaveContaminatedContourCount", 0))
    contaminated_rows = [row for row in rows if row["octaveContaminationDetected"]]
    contaminated_gates_pass = all(
        row["correctedPitchContourQualityGate"] for row in contaminated_rows
    )
    ready = bool(
        source_unchanged
        and len(rows) == int(reliability.get("singleNoteCandidateCount", -1))
        and contaminated_count == len(contaminated_rows)
        and contaminated_count > 0
        and corrected_count == contaminated_count
        and contaminated_gates_pass
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-octave-corrected-single-note-pitch-contours",
        "passed": source_unchanged and len(rows) > 0,
        "singleNoteCandidateCount": len(rows),
        "octaveContaminatedContourCount": contaminated_count,
        "octaveCorrectedContourCount": corrected_count,
        "correctedContourQualityGatePassedCount": corrected_gate_count,
        "allContaminatedContoursPassedCorrectionGate": contaminated_gates_pass,
        "rows": rows,
        "readyForPostCorrectionReliabilityDiagnostic": ready,
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
        "octaveContaminatedContourCount": contaminated_count,
        "octaveCorrectedContourCount": corrected_count,
        "allContaminatedContoursPassedCorrectionGate": contaminated_gates_pass,
        "readyForPostCorrectionReliabilityDiagnostic": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 OCTAVE-CORRECTED PITCH CONTOUR CANDIDATE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Single-note candidates:", len(rows))
    print("Octave-contaminated contours:", contaminated_count)
    print("Octave-corrected contours:", corrected_count)
    print("All contaminated contours passed correction gate:", contaminated_gates_pass)
    for row in rows:
        if not row["octaveContaminationDetected"]:
            continue
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"shiftedFrames={row['nonzeroOctaveShiftFrameCount']} "
            f"rawRange={row['rawMetrics']['rawRangeCents']} "
            f"correctedRange={row['correctedMetrics']['rawRangeCents']} "
            f"correctedRobustRange={row['correctedMetrics']['robustRangeCents']} "
            f"rawOctaveJumps={row['rawMetrics']['octaveLikeJumpCount']} "
            f"correctedOctaveJumps={row['correctedMetrics']['octaveLikeJumpCount']} "
            f"qualityGate={row['correctedPitchContourQualityGate']}"
        )
    print("Ready for post-correction reliability diagnostic:", ready)
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
