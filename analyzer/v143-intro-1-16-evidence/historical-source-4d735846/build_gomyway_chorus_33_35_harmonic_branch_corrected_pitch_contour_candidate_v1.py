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
PLAUSIBILITY_PATH = PUBLIC / "gomyway-chorus-33-35-pitch-range-plausibility-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1-manifest.json"

OCTAVE_CENTS = 1200.0
MAX_OCTAVE_SHIFT = 4
SHIFT_CHANGE_PENALTY = 45.0
SHIFT_MAGNITUDE_PENALTY = 3.0
MAX_CORRECTED_ROBUST_RANGE_CENTS = 700.0
MAX_CORRECTED_MEDIAN_JUMP_CENTS = 250.0
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


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def metrics(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "rawRangeCents": 0.0,
            "robustRangeCents": 0.0,
            "medianContiguousJumpCents": 0.0,
            "maximumContiguousJumpCents": 0.0,
        }
    jumps = [abs(right - left) for left, right in zip(values, values[1:])]
    return {
        "rawRangeCents": round(max(values) - min(values), 3),
        "robustRangeCents": round(percentile(values, 0.90) - percentile(values, 0.10), 3),
        "medianContiguousJumpCents": round(statistics.median(jumps) if jumps else 0.0, 3),
        "maximumContiguousJumpCents": round(max(jumps) if jumps else 0.0, 3),
    }


def correct_harmonic_branch(pitches: list[float]) -> tuple[list[float], list[int]]:
    if not pitches:
        return [], []

    shifts = list(range(-MAX_OCTAVE_SHIFT, MAX_OCTAVE_SHIFT + 1))
    costs: list[dict[int, float]] = []
    parents: list[dict[int, int | None]] = []

    first_costs: dict[int, float] = {}
    first_parents: dict[int, int | None] = {}
    for shift in shifts:
        first_costs[shift] = abs(shift) * SHIFT_MAGNITUDE_PENALTY
        first_parents[shift] = None
    costs.append(first_costs)
    parents.append(first_parents)

    for index in range(1, len(pitches)):
        row_costs: dict[int, float] = {}
        row_parents: dict[int, int | None] = {}
        for shift in shifts:
            current = pitches[index] + shift * OCTAVE_CENTS
            best_cost = float("inf")
            best_parent: int | None = None
            for previous_shift in shifts:
                previous = pitches[index - 1] + previous_shift * OCTAVE_CENTS
                transition = abs(current - previous)
                transition += abs(shift - previous_shift) * SHIFT_CHANGE_PENALTY
                transition += abs(shift) * SHIFT_MAGNITUDE_PENALTY
                candidate_cost = costs[index - 1][previous_shift] + transition
                if candidate_cost < best_cost:
                    best_cost = candidate_cost
                    best_parent = previous_shift
            row_costs[shift] = best_cost
            row_parents[shift] = best_parent
        costs.append(row_costs)
        parents.append(row_parents)

    final_shift = min(costs[-1], key=costs[-1].get)
    selected_shifts = [final_shift]
    for index in range(len(pitches) - 1, 0, -1):
        parent = parents[index][selected_shifts[-1]]
        if parent is None:
            parent = 0
        selected_shifts.append(parent)
    selected_shifts.reverse()

    corrected = [
        pitch + shift * OCTAVE_CENTS
        for pitch, shift in zip(pitches, selected_shifts)
    ]

    # A uniform octave translation does not alter contour shape. Keep the
    # corrected contour centered near the raw contour for easier inspection.
    raw_median = statistics.median(pitches)
    corrected_median = statistics.median(corrected)
    uniform_shift = round((raw_median - corrected_median) / OCTAVE_CENTS)
    corrected = [value + uniform_shift * OCTAVE_CENTS for value in corrected]
    selected_shifts = [shift + uniform_shift for shift in selected_shifts]
    return corrected, selected_shifts


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    features = load(FEATURE_PATH)
    plausibility = load(PLAUSIBILITY_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if features.get("passed") is not True or plausibility.get("passed") is not True:
        raise RuntimeError("Pitch-contour prerequisites are not green.")
    if plausibility.get("recommendedNextAction") != (
        "build-harmonic-branch-corrected-pitch-contour-candidate"
    ):
        raise RuntimeError("Pitch-range diagnostic did not authorize harmonic branch correction.")

    plausibility_by_key = {
        (row.get("measureNumber"), row.get("quantizedStep")): row
        for row in plausibility.get("rows", [])
        if isinstance(row, dict)
    }

    rows: list[dict[str, Any]] = []
    implausible_count = 0
    corrected_count = 0
    corrected_gate_count = 0

    for feature_row in features.get("rows", []):
        if not isinstance(feature_row, dict):
            continue
        key = (feature_row.get("measureNumber"), feature_row.get("quantizedStep"))
        plausibility_row = plausibility_by_key.get(key, {})
        feature_block = feature_row.get("features", {})
        frames = [row for row in feature_block.get("frames", []) if isinstance(row, dict)]
        raw_pitches = [
            value for value in (
                number(row.get("pitchCentsFromA4")) for row in frames
            ) if value is not None
        ]

        reliable = plausibility_row.get("pitchContourReliabilityGate") is True
        plausible = plausibility_row.get("pitchRangePlausibilityGate") is True
        needs_correction = bool(reliable and not plausible)
        if needs_correction:
            implausible_count += 1
            corrected_pitches, shifts = correct_harmonic_branch(raw_pitches)
        else:
            corrected_pitches = list(raw_pitches)
            shifts = [0] * len(raw_pitches)

        correction_applied = bool(needs_correction and any(shift != 0 for shift in shifts))
        if correction_applied:
            corrected_count += 1

        raw_metrics = metrics(raw_pitches)
        corrected_metrics = metrics(corrected_pitches)
        corrected_gate = bool(
            len(corrected_pitches) >= MIN_RELIABLE_FRAMES
            and corrected_metrics["robustRangeCents"] <= MAX_CORRECTED_ROBUST_RANGE_CENTS
            and corrected_metrics["medianContiguousJumpCents"] <= MAX_CORRECTED_MEDIAN_JUMP_CENTS
        )
        if needs_correction and corrected_gate:
            corrected_gate_count += 1

        corrected_frames: list[dict[str, Any]] = []
        for index, frame in enumerate(frames):
            output_frame = dict(frame)
            output_frame["rawPitchCentsFromA4"] = frame.get("pitchCentsFromA4")
            output_frame["harmonicBranchOctaveShift"] = shifts[index] if index < len(shifts) else 0
            output_frame["correctedPitchCentsFromA4"] = round(corrected_pitches[index], 3)
            corrected_frames.append(output_frame)

        rows.append({
            "measureNumber": feature_row.get("measureNumber"),
            "quantizedStep": feature_row.get("quantizedStep"),
            "sourceEventIndex": feature_row.get("sourceEventIndex"),
            "pitchContourReliabilityGate": reliable,
            "originalPitchRangePlausibilityGate": plausible,
            "harmonicBranchCorrectionRequired": needs_correction,
            "harmonicBranchCorrectionApplied": correction_applied,
            "nonzeroShiftFrameCount": sum(shift != 0 for shift in shifts),
            "rawMetrics": raw_metrics,
            "correctedMetrics": corrected_metrics,
            "correctedPitchContourQualityGate": corrected_gate if needs_correction else plausible,
            "frames": corrected_frames,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    all_corrected_pass = bool(
        implausible_count > 0
        and corrected_count == implausible_count
        and corrected_gate_count == implausible_count
    )
    ready = bool(
        source_unchanged
        and len(rows) == int(plausibility.get("singleNoteCandidateCount", -1))
        and implausible_count == int(plausibility.get("implausibleReliablePitchContourCount", -1))
        and all_corrected_pass
    )

    output = {
        "schemaVersion": 1,
        "candidateType": "read-only-harmonic-branch-corrected-pitch-contours",
        "passed": source_unchanged and len(rows) > 0,
        "singleNoteCandidateCount": len(rows),
        "implausibleReliablePitchContourCount": implausible_count,
        "harmonicBranchCorrectedContourCount": corrected_count,
        "correctedContourQualityGatePassedCount": corrected_gate_count,
        "allImplausibleContoursPassedCorrectionGate": all_corrected_pass,
        "rows": rows,
        "readyForPostCorrectionPlausibilityDiagnostic": ready,
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
        "implausibleReliablePitchContourCount": implausible_count,
        "harmonicBranchCorrectedContourCount": corrected_count,
        "allImplausibleContoursPassedCorrectionGate": all_corrected_pass,
        "readyForPostCorrectionPlausibilityDiagnostic": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 HARMONIC-BRANCH CORRECTED PITCH CONTOUR CANDIDATE V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Single-note candidates:", len(rows))
    print("Implausible reliable pitch contours:", implausible_count)
    print("Harmonic-branch corrected contours:", corrected_count)
    print("All implausible contours passed correction gate:", all_corrected_pass)
    for row in rows:
        if not row["harmonicBranchCorrectionRequired"]:
            continue
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"shiftedFrames={row['nonzeroShiftFrameCount']} "
            f"rawRange={row['rawMetrics']['robustRangeCents']} "
            f"correctedRange={row['correctedMetrics']['robustRangeCents']} "
            f"rawMedianJump={row['rawMetrics']['medianContiguousJumpCents']} "
            f"correctedMedianJump={row['correctedMetrics']['medianContiguousJumpCents']} "
            f"qualityGate={row['correctedPitchContourQualityGate']}"
        )
    print("Ready for post-correction plausibility diagnostic:", ready)
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
