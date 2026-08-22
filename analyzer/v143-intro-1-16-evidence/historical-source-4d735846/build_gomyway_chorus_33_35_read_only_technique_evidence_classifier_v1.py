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
PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-final-post-correction-pitch-proof-v1.json"
CANDIDATE_PATH = PUBLIC / "gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1-manifest.json"

MIN_FRAMES = 6
MIN_BEND_EXCURSION_CENTS = 120.0
MIN_BEND_NET_CHANGE_CENTS = 90.0
MIN_BEND_DIRECTIONAL_RATIO = 0.70
MIN_VIBRATO_RANGE_CENTS = 35.0
MAX_VIBRATO_RANGE_CENTS = 350.0
MIN_VIBRATO_DIRECTION_CHANGES = 3
MIN_VIBRATO_ZERO_CROSSINGS = 3
MIN_VIBRATO_MODULATION_STD_CENTS = 12.0


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


def sign(value: float, epsilon: float = 1.0) -> int:
    if value > epsilon:
        return 1
    if value < -epsilon:
        return -1
    return 0


def direction_changes(values: list[float]) -> int:
    directions = [sign(right - left) for left, right in zip(values, values[1:])]
    directions = [value for value in directions if value != 0]
    return sum(left != right for left, right in zip(directions, directions[1:]))


def zero_crossings(values: list[float]) -> int:
    if not values:
        return 0
    center = statistics.median(values)
    centered_signs = [sign(value - center) for value in values]
    centered_signs = [value for value in centered_signs if value != 0]
    return sum(left != right for left, right in zip(centered_signs, centered_signs[1:]))


def linear_slope(values: list[float], times: list[float]) -> float:
    if len(values) < 2 or len(values) != len(times):
        return 0.0
    mean_x = statistics.mean(times)
    mean_y = statistics.mean(values)
    denominator = sum((x - mean_x) ** 2 for x in times)
    if denominator <= 0.0:
        return 0.0
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(times, values))
    return numerator / denominator


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    proof = load(PROOF_PATH)
    candidate = load(CANDIDATE_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if proof.get("passed") is not True:
        raise RuntimeError("Final post-correction pitch proof is not green.")
    if proof.get("readyForTechniqueEvidenceClassification") is not True:
        raise RuntimeError("Final pitch proof did not authorize technique classification.")
    if proof.get("recommendedNextAction") != "build-read-only-technique-evidence-classifier-v1":
        raise RuntimeError("Unexpected final pitch-proof recommendation.")
    if candidate.get("passed") is not True or candidate.get("allCorrectedPitchQualityGatesPassed") is not True:
        raise RuntimeError("Corrected pitch candidate is not fully green.")

    rows: list[dict[str, Any]] = []
    bend_evidence_count = 0
    vibrato_evidence_count = 0
    ambiguous_count = 0
    no_evidence_count = 0

    for row in candidate.get("rows", []):
        if not isinstance(row, dict):
            continue
        if row.get("correctedPitchContourQualityGate") is not True:
            raise RuntimeError("Classifier received a failed corrected pitch-quality row.")

        frames = [frame for frame in row.get("frames", []) if isinstance(frame, dict)]
        pitches: list[float] = []
        times: list[float] = []
        for index, frame in enumerate(frames):
            pitch = number(frame.get("correctedPitchCentsFromA4", frame.get("pitchCentsFromA4")))
            if pitch is None:
                continue
            time_value = number(
                frame.get("timeSeconds", frame.get("time", frame.get("relativeTimeSeconds")))
            )
            pitches.append(pitch)
            times.append(time_value if time_value is not None else float(index))

        if len(pitches) < MIN_FRAMES:
            raise RuntimeError("Corrected contour unexpectedly has too few voiced frames.")

        robust_low = percentile(pitches, 0.10)
        robust_high = percentile(pitches, 0.90)
        robust_range = robust_high - robust_low
        net_change = pitches[-1] - pitches[0]
        slope = linear_slope(pitches, times)
        changes = direction_changes(pitches)
        crossings = zero_crossings(pitches)
        modulation_std = statistics.pstdev(pitches) if len(pitches) > 1 else 0.0

        increments = [right - left for left, right in zip(pitches, pitches[1:])]
        nonzero_directions = [sign(value) for value in increments if sign(value) != 0]
        dominant_direction_ratio = (
            max(
                nonzero_directions.count(1),
                nonzero_directions.count(-1),
            ) / len(nonzero_directions)
            if nonzero_directions
            else 0.0
        )

        bend_gate = bool(
            robust_range >= MIN_BEND_EXCURSION_CENTS
            and abs(net_change) >= MIN_BEND_NET_CHANGE_CENTS
            and dominant_direction_ratio >= MIN_BEND_DIRECTIONAL_RATIO
            and changes <= 3
        )
        vibrato_gate = bool(
            MIN_VIBRATO_RANGE_CENTS <= robust_range <= MAX_VIBRATO_RANGE_CENTS
            and changes >= MIN_VIBRATO_DIRECTION_CHANGES
            and crossings >= MIN_VIBRATO_ZERO_CROSSINGS
            and modulation_std >= MIN_VIBRATO_MODULATION_STD_CENTS
            and abs(net_change) < max(100.0, robust_range * 0.65)
        )

        if bend_gate and vibrato_gate:
            evidence_class = "ambiguous-bend-and-vibrato-evidence"
            ambiguous_count += 1
        elif bend_gate:
            evidence_class = "bend-evidence-candidate"
            bend_evidence_count += 1
        elif vibrato_gate:
            evidence_class = "vibrato-evidence-candidate"
            vibrato_evidence_count += 1
        else:
            evidence_class = "no-technique-evidence"
            no_evidence_count += 1

        rows.append({
            "measureNumber": row.get("measureNumber"),
            "quantizedStep": row.get("quantizedStep"),
            "sourceEventIndex": row.get("sourceEventIndex"),
            "voicedFrameCount": len(pitches),
            "robustPitchRangeCents": round(robust_range, 3),
            "netPitchChangeCents": round(net_change, 3),
            "linearSlopeCentsPerSecond": round(slope, 3),
            "directionChangeCount": changes,
            "medianCenteredZeroCrossingCount": crossings,
            "modulationStandardDeviationCents": round(modulation_std, 3),
            "dominantDirectionRatio": round(dominant_direction_ratio, 6),
            "bendEvidenceGate": bend_gate,
            "vibratoEvidenceGate": vibrato_gate,
            "evidenceClass": evidence_class,
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    expected_count = int(candidate.get("singleNoteCandidateCount", -1))
    count_matches = len(rows) == expected_count
    classified_count = (
        bend_evidence_count
        + vibrato_evidence_count
        + ambiguous_count
        + no_evidence_count
    )
    ready = bool(
        source_unchanged
        and count_matches
        and classified_count == len(rows)
        and len(rows) > 0
    )

    output = {
        "schemaVersion": 1,
        "classifierType": "read-only-audio-pitch-contour-technique-evidence",
        "passed": ready,
        "singleNoteCandidateCount": len(rows),
        "candidateCountMatches": count_matches,
        "bendEvidenceCandidateCount": bend_evidence_count,
        "vibratoEvidenceCandidateCount": vibrato_evidence_count,
        "ambiguousTechniqueEvidenceCount": ambiguous_count,
        "noTechniqueEvidenceCount": no_evidence_count,
        "rows": rows,
        "readyForProfessionalLabelEvidenceBenchmark": ready,
        "recommendedNextAction": (
            "build-read-only-technique-evidence-professional-label-benchmark-v1"
            if ready
            else "diagnose-technique-evidence-classifier-failures"
        ),
        "professionalReferenceUsed": False,
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
        "passed": ready,
        "singleNoteCandidateCount": len(rows),
        "bendEvidenceCandidateCount": bend_evidence_count,
        "vibratoEvidenceCandidateCount": vibrato_evidence_count,
        "ambiguousTechniqueEvidenceCount": ambiguous_count,
        "noTechniqueEvidenceCount": no_evidence_count,
        "readyForProfessionalLabelEvidenceBenchmark": ready,
        "recommendedNextAction": output["recommendedNextAction"],
        "professionalReferenceUsed": False,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 READ-ONLY TECHNIQUE EVIDENCE CLASSIFIER V1 COMPLETE")
    print("Passed:", ready)
    print("Single-note candidates:", len(rows))
    print("Candidate count matches:", count_matches)
    print("Bend evidence candidates:", bend_evidence_count)
    print("Vibrato evidence candidates:", vibrato_evidence_count)
    print("Ambiguous technique evidence:", ambiguous_count)
    print("No technique evidence:", no_evidence_count)
    for row in rows:
        print(
            f"measure={row['measureNumber']} step={row['quantizedStep']} "
            f"range={row['robustPitchRangeCents']} "
            f"net={row['netPitchChangeCents']} "
            f"directionChanges={row['directionChangeCount']} "
            f"zeroCrossings={row['medianCenteredZeroCrossingCount']} "
            f"dominantRatio={row['dominantDirectionRatio']} "
            f"bendGate={row['bendEvidenceGate']} "
            f"vibratoGate={row['vibratoEvidenceGate']} "
            f"class={row['evidenceClass']}"
        )
    print("Ready for professional-label evidence benchmark:", ready)
    print("Recommended next action:", output["recommendedNextAction"])
    print("Professional reference used: False")
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

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
