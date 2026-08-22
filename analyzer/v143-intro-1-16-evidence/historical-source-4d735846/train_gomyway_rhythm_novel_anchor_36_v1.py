from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REVIEW_PATH = PUBLIC / "gomyway-rhythm-next-novel-training-anchors-review-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-novel-anchor-36-training-v1-manifest.json"

EXPECTED_SOURCE_EVENT_COUNT = 949
TARGET_MEASURE = 36
QUEUED_AFTER = [51, 60, 73, 82, 91, 99, 101, 113]

TECHNIQUE_KEYS = (
    "technique",
    "techniques",
    "articulation",
    "articulations",
    "bend",
    "vibrato",
    "slide",
    "hammerOn",
    "pullOff",
    "palmMute",
    "harmonic",
    "pinchHarmonic",
    "tap",
)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def time_of(event: dict[str, Any]) -> float | None:
    for key in ("startTime", "start_time", "start", "timeSeconds", "time"):
        value = number(event.get(key))
        if value is not None:
            return value
    return None


def compact_event(event: dict[str, Any], source_index: int) -> dict[str, Any]:
    result: dict[str, Any] = {"sourceEventIndex": source_index}
    for key in (
        "measureNumber",
        "measure",
        "quantizedStep",
        "step",
        "stringIndex",
        "string",
        "fret",
        "midiPitch",
        "pitch",
        "startTime",
        "start_time",
        "start",
        "duration",
        "durationSeconds",
    ):
        if key in event:
            result[key] = event[key]
    return result


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    review = load(REVIEW_PATH)
    events = source_rows(source)

    if len(events) != EXPECTED_SOURCE_EVENT_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_SOURCE_EVENT_COUNT} protected source events, found {len(events)}."
        )
    if review.get("passed") is not True:
        raise RuntimeError("Novel training-anchor review V1 is not green.")
    if review.get("readyForNovelAnchor36Training") is not True:
        raise RuntimeError("Review is not ready for novel anchor 36 training.")
    if review.get("nextChronologicalTrainingAnchor") != TARGET_MEASURE:
        raise RuntimeError("Novel training target changed unexpectedly.")
    if review.get("queuedTrainingAnchorMeasures") != QUEUED_AFTER:
        raise RuntimeError("Queued training-anchor order changed unexpectedly.")
    if review.get("trainingTruthClaimed") is not False:
        raise RuntimeError("Review unexpectedly claims training truth.")
    if review.get("thresholdRelaxationAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows threshold relaxation.")
    if review.get("automaticApplyAllowed") is not False:
        raise RuntimeError("Review unexpectedly allows automatic application.")
    if review.get("protectedSourceHashUnchanged") is not True:
        raise RuntimeError("Review did not preserve protected source hash.")

    measure_events: list[tuple[int, dict[str, Any]]] = [
        (index, event)
        for index, event in enumerate(events)
        if measure_of(event) == TARGET_MEASURE
    ]
    if not measure_events:
        raise RuntimeError(f"No protected source events found for measure {TARGET_MEASURE}.")

    by_step: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    unquantized_count = 0
    for index, event in measure_events:
        step = step_of(event)
        if step is None:
            unquantized_count += 1
        else:
            by_step[step].append((index, event))

    occupied_steps = sorted(by_step)
    multiplicities = {str(step): len(by_step[step]) for step in occupied_steps}
    chord_steps = [step for step in occupied_steps if len(by_step[step]) > 1]
    max_step_multiplicity = max(multiplicities.values(), default=0)

    raw_times = [time_of(event) for _, event in measure_events]
    timing_values = [value for value in raw_times if value is not None]
    timing_values_sorted = sorted(timing_values)
    timing_observed_count = len(timing_values)
    timing_complete = timing_observed_count == len(measure_events)
    timing_non_decreasing = timing_values == sorted(timing_values) if timing_complete else False
    timing_strict_unique = len(set(timing_values_sorted)) == len(timing_values_sorted)

    explicit_technique_events: list[dict[str, Any]] = []
    technique_key_counts: Counter[str] = Counter()
    for index, event in measure_events:
        found: dict[str, Any] = {}
        for key in TECHNIQUE_KEYS:
            if key not in event:
                continue
            value = event.get(key)
            if value in (None, False, "", [], {}):
                continue
            found[key] = value
            technique_key_counts[key] += 1
        if found:
            explicit_technique_events.append(
                {"sourceEventIndex": index, "evidence": found}
            )

    rhythm_evidence_supported = bool(occupied_steps and unquantized_count == 0)
    chord_shape_observation_available = bool(chord_steps)
    timing_observation_available = bool(timing_values)
    technique_observation_available = bool(explicit_technique_events)

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(source_unchanged and rhythm_evidence_supported)

    recommended = (
        "review-gomyway-rhythm-novel-anchor-36-training-v1"
        if passed
        else "diagnose-gomyway-rhythm-novel-anchor-36-training-v1"
    )

    output = {
        "schemaVersion": 1,
        "trainingType": "read-only-novel-rhythm-anchor-evidence-training",
        "passed": passed,
        "measureNumber": TARGET_MEASURE,
        "sourceEventCountInMeasure": len(measure_events),
        "sourceEventIndexes": [index for index, _ in measure_events],
        "compactSourceEvents": [
            compact_event(event, index) for index, event in measure_events
        ],
        "rhythmEvidence": {
            "supported": rhythm_evidence_supported,
            "occupiedSteps": occupied_steps,
            "occupiedStepCount": len(occupied_steps),
            "unquantizedEventCount": unquantized_count,
            "stepMultiplicities": multiplicities,
        },
        "chordShapeEvidence": {
            "observationAvailable": chord_shape_observation_available,
            "multiNoteSteps": chord_steps,
            "multiNoteStepCount": len(chord_steps),
            "maxStepMultiplicity": max_step_multiplicity,
            "trainingTruthClaimed": False,
        },
        "timingEvidence": {
            "observationAvailable": timing_observation_available,
            "observedTimingCount": timing_observed_count,
            "allMeasureEventsHaveTiming": timing_complete,
            "sourceOrderNonDecreasing": timing_non_decreasing,
            "timingValuesStrictlyUnique": timing_strict_unique,
            "trainingTruthClaimed": False,
        },
        "techniqueEvidence": {
            "observationAvailable": technique_observation_available,
            "explicitTechniqueEventCount": len(explicit_technique_events),
            "techniqueKeyCounts": dict(sorted(technique_key_counts.items())),
            "explicitTechniqueEvents": explicit_technique_events,
            "trainingTruthClaimed": False,
        },
        "queuedTrainingAnchorMeasures": QUEUED_AFTER,
        "anchorTrainingClaimedAsTruth": False,
        "classificationClaimed": False,
        "rhythmTransferClaimed": False,
        "chordTransferClaimed": False,
        "timingTransferClaimed": False,
        "techniqueTransferClaimed": False,
        "thresholdRelaxationAllowed": False,
        "automaticApplyAllowed": False,
        "readOnlyTrainingEvidence": True,
        "readyForNovelAnchor36TrainingReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceEventCount": len(events),
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
        "measureNumber": TARGET_MEASURE,
        "sourceEventCountInMeasure": len(measure_events),
        "occupiedStepCount": len(occupied_steps),
        "multiNoteStepCount": len(chord_steps),
        "timingObservationAvailable": timing_observation_available,
        "explicitTechniqueEventCount": len(explicit_technique_events),
        "anchorTrainingClaimedAsTruth": False,
        "automaticApplyAllowed": False,
        "readyForNovelAnchor36TrainingReview": passed,
        "recommendedNextAction": recommended,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM NOVEL ANCHOR 36 TRAINING V1 COMPLETE")
    print("Passed:", passed)
    print("Measure:", TARGET_MEASURE)
    print("Source events in measure:", len(measure_events))
    print("Occupied steps:", occupied_steps)
    print("Step multiplicities:", multiplicities)
    print("Chord-shape observation available:", chord_shape_observation_available)
    print("Multi-note steps:", chord_steps)
    print("Timing observation available:", timing_observation_available)
    print("All measure events have timing:", timing_complete)
    print("Source-order timing non-decreasing:", timing_non_decreasing)
    print("Explicit technique events:", len(explicit_technique_events))
    print("Technique key counts:", dict(sorted(technique_key_counts.items())))
    print("Anchor training claimed as truth: False")
    print("Threshold relaxation allowed: False")
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for novel anchor 36 training review:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
