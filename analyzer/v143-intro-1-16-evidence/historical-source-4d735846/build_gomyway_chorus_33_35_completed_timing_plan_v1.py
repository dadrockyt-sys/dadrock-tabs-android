from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
BRIDGE_PATH = PUBLIC / "gomyway-chorus-33-35-measure-step-timing-bridge-v1.json"
DIAGNOSTIC_PATH = PUBLIC / "gomyway-chorus-33-35-missing-timing-diagnostic-v1.json"
ONSET_PATH = PUBLIC / "gomyway-chorus-35-step0-audio-onset-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-completed-timing-plan-v1-manifest.json"

STEPS_PER_MEASURE = 12


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def absolute_step(measure: int, step: int) -> int:
    return (measure - 1) * STEPS_PER_MEASURE + step


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def rounded(value: float | None) -> float | None:
    return round(value, 6) if value is not None else None


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    bridge = load(BRIDGE_PATH)
    diagnostic = load(DIAGNOSTIC_PATH)
    onset = load(ONSET_PATH)

    if len(source_rows(source)) != 949:
        raise RuntimeError("Protected source must contain exactly 949 events.")
    if bridge.get("passed") is not True:
        raise RuntimeError("Measure/step timing bridge is not green.")
    if int(bridge.get("chorusEventCount", -1)) != 30:
        raise RuntimeError("Expected 30 chorus bridge rows.")
    if diagnostic.get("passed") is not True:
        raise RuntimeError("Missing timing diagnostic is not green.")
    if int(diagnostic.get("boundedInterpolationCandidateCount", -1)) != 8:
        raise RuntimeError("Expected exactly eight bounded interpolation candidates.")
    if int(diagnostic.get("unresolvedTimingEventCount", -1)) != 1:
        raise RuntimeError("Expected exactly one unresolved boundary event.")
    if onset.get("passed") is not True:
        raise RuntimeError("Audio onset arbitration did not complete.")
    if onset.get("qualityGate") is not True:
        raise RuntimeError("Audio onset arbitration quality gate is not green.")
    if onset.get("readyForReadOnlyTimingCompletion") is not True:
        raise RuntimeError("Audio onset arbitration did not authorize timing completion.")

    interpolated = {
        (integer(row.get("measureNumber")), integer(row.get("quantizedStep"))): number(
            row.get("interpolatedStartSeconds")
        )
        for row in diagnostic.get("rows", [])
        if isinstance(row, dict)
        and row.get("interpolationReason") == "bounded-linear-interpolation"
        and row.get("interpolatedStartSeconds") is not None
    }
    onset_key = (integer(onset.get("targetMeasure")), integer(onset.get("targetStep")))
    onset_start = number(onset.get("resolvedStartSeconds"))
    if onset_key != (35, 0) or onset_start is None:
        raise RuntimeError("Expected an audio-onset resolution for measure 35 step 0.")

    completed_rows: list[dict[str, Any]] = []
    observed_count = 0
    interpolated_count = 0
    audio_onset_count = 0

    for row in bridge.get("rows", []):
        if not isinstance(row, dict):
            continue
        measure = integer(row.get("measureNumber"))
        step = integer(row.get("quantizedStep"))
        if measure is None or step is None:
            continue

        key = (measure, step)
        observed_start = number(row.get("resolvedStartSeconds"))
        if observed_start is not None:
            start = observed_start
            timing_source = "observed-measure-step-consensus"
            source_quality_gate = bool(row.get("timingConsensusPassed"))
            observed_count += 1
        elif key in interpolated and interpolated[key] is not None:
            start = float(interpolated[key])
            timing_source = "bounded-linear-interpolation"
            source_quality_gate = True
            interpolated_count += 1
        elif key == onset_key:
            start = onset_start
            timing_source = "audio-onset-arbitrated-boundary"
            source_quality_gate = True
            audio_onset_count += 1
        else:
            start = None
            timing_source = "unresolved"
            source_quality_gate = False

        completed_rows.append({
            "sourceEventIndex": row.get("sourceEventIndex"),
            "measureNumber": measure,
            "quantizedStep": step,
            "absoluteStep": absolute_step(measure, step),
            "notes": row.get("notes", []),
            "noteMultiplicity": row.get("noteMultiplicity", 0),
            "isSingleNoteTechniqueCandidate": bool(
                row.get("isSingleNoteTechniqueCandidate")
            ),
            "resolvedStartSeconds": rounded(start),
            "timingSource": timing_source,
            "timingQualityGate": source_quality_gate,
            "audioTechniqueSupportClaimed": False,
            "readOnly": True,
        })

    completed_rows.sort(key=lambda row: int(row["absoluteStep"]))

    # Close each feature window at the next event onset. The final row receives
    # a conservative 450 ms fallback duration. This creates analysis windows
    # only and never changes the protected event source.
    for index, row in enumerate(completed_rows):
        start = number(row.get("resolvedStartSeconds"))
        next_start = (
            number(completed_rows[index + 1].get("resolvedStartSeconds"))
            if index + 1 < len(completed_rows) else None
        )
        if start is None:
            end = None
        elif next_start is not None and next_start > start:
            end = next_start
        else:
            end = start + 0.45
        row["resolvedEndSeconds"] = rounded(end)
        row["analysisWindowStartSeconds"] = rounded(max(0.0, start - 0.04)) if start is not None else None
        row["analysisWindowEndSeconds"] = rounded(end + 0.12) if end is not None else None

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    resolved_count = sum(
        row.get("resolvedStartSeconds") is not None for row in completed_rows
    )
    quality_count = sum(bool(row.get("timingQualityGate")) for row in completed_rows)
    monotonic = all(
        float(left["resolvedStartSeconds"]) < float(right["resolvedStartSeconds"])
        for left, right in zip(completed_rows, completed_rows[1:])
        if left.get("resolvedStartSeconds") is not None
        and right.get("resolvedStartSeconds") is not None
    )
    ready = bool(
        source_unchanged
        and len(completed_rows) == 30
        and observed_count == 21
        and interpolated_count == 8
        and audio_onset_count == 1
        and resolved_count == 30
        and quality_count == 30
        and monotonic
    )

    output = {
        "schemaVersion": 1,
        "planType": "read-only-completed-chorus-audio-technique-timing",
        "passed": ready,
        "chorusEventCount": len(completed_rows),
        "observedConsensusTimingCount": observed_count,
        "boundedInterpolationTimingCount": interpolated_count,
        "audioOnsetBoundaryTimingCount": audio_onset_count,
        "resolvedTimingCount": resolved_count,
        "timingQualityGatePassedCount": quality_count,
        "strictlyMonotonicTiming": monotonic,
        "rows": completed_rows,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "audioTimingEvidenceClaimed": True,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
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
        "chorusEventCount": len(completed_rows),
        "observedConsensusTimingCount": observed_count,
        "boundedInterpolationTimingCount": interpolated_count,
        "audioOnsetBoundaryTimingCount": audio_onset_count,
        "resolvedTimingCount": resolved_count,
        "strictlyMonotonicTiming": monotonic,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 COMPLETED TIMING PLAN V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Chorus events:", len(completed_rows))
    print("Observed consensus timings:", observed_count)
    print("Bounded interpolation timings:", interpolated_count)
    print("Audio-onset boundary timings:", audio_onset_count)
    print("Resolved timings:", resolved_count)
    print("Timing quality gates passed:", quality_count)
    print("Strictly monotonic timing:", monotonic)
    print("Protected source event count: 949")
    print("Protected source hash unchanged:", source_unchanged)
    print("Audio technique support claimed: False")
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for audio technique feature extraction:", ready)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
