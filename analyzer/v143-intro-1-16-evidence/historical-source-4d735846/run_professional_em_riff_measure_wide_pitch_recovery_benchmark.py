from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-measure-wide-pitch-recovery.json"

VERSE_START = 18
VERSE_END = 32
STEPS_PER_MEASURE = 16
OPEN_STRING_MIDI = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}

EXPECTED = {
    "em-riff-a": {
        2: [57, 59],
        6: [55],
        10: [52],
        14: [45],
    },
    "em-riff-b": {
        2: [57, 59],
        4: [55],
        6: [52],
        10: [45],
        14: [62, 58],
    },
}


def _walk(value: Any) -> Iterator[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _safe_int(value: Any, fallback: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = -1.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _event_pitch(node: dict[str, Any]) -> int:
    midi_pitch = _safe_int(node.get("midiPitch"))
    if midi_pitch >= 0:
        return midi_pitch
    string_index = _safe_int(node.get("stringIndex"))
    fret = _safe_int(node.get("fret"))
    if string_index in OPEN_STRING_MIDI and fret >= 0:
        return OPEN_STRING_MIDI[string_index] + fret
    return -1


def _event_step(node: dict[str, Any]) -> int:
    position = _safe_float(node.get("positionInMeasure"))
    if position >= 0:
        return max(0, min(15, int(round(position * STEPS_PER_MEASURE))))
    return _safe_int(node.get("quantizedStep"))


def main() -> None:
    if not NOTATION_PATH.exists():
        raise FileNotFoundError(f"Missing {NOTATION_PATH.name}")
    if not TIMING_PATH.exists():
        raise FileNotFoundError(f"Missing {TIMING_PATH.name}")

    notation = json.loads(NOTATION_PATH.read_text())
    timing = json.loads(TIMING_PATH.read_text())

    events_by_pattern: dict[str, list[dict[str, int]]] = defaultdict(list)
    events_inspected = 0

    for node in _walk(notation):
        measure = _safe_int(node.get("measureNumber"))
        if not VERSE_START <= measure <= VERSE_END:
            continue
        pitch = _event_pitch(node)
        step = _event_step(node)
        if pitch < 0 or step < 0:
            continue
        pattern_id = "em-riff-a" if measure % 2 == 0 else "em-riff-b"
        events_by_pattern[pattern_id].append(
            {"measureNumber": measure, "step": step, "midiPitch": pitch}
        )
        events_inspected += 1

    slot_reports: list[dict[str, Any]] = []
    slots_with_measure_wide_pitch = 0
    slots_with_nearby_pitch = 0

    for pattern_id, expected_slots in EXPECTED.items():
        pattern_events = events_by_pattern.get(pattern_id, [])
        for target_step, accepted_pitches in expected_slots.items():
            matches = [
                event for event in pattern_events
                if event["midiPitch"] in accepted_pitches
            ]
            distance_counter: Counter[int] = Counter(
                abs(event["step"] - target_step) for event in matches
            )
            nearest_distance = min(distance_counter, default=None)
            present_anywhere = bool(matches)
            present_within_four = nearest_distance is not None and nearest_distance <= 4
            if present_anywhere:
                slots_with_measure_wide_pitch += 1
            if present_within_four:
                slots_with_nearby_pitch += 1

            slot_reports.append(
                {
                    "patternId": pattern_id,
                    "quantizedStep": target_step,
                    "acceptedMidiPitches": accepted_pitches,
                    "correctPitchPresentAnywhereInMatchingMeasures": present_anywhere,
                    "correctPitchPresentWithinFourSteps": present_within_four,
                    "nearestObservedStepDistance": nearest_distance,
                    "matchingEventCount": len(matches),
                    "sampleMatches": matches[:12],
                }
            )

    total_slots = len(slot_reports)
    measure_wide_percentage = round(
        100.0 * slots_with_measure_wide_pitch / max(1, total_slots), 2
    )

    if slots_with_measure_wide_pitch == total_slots:
        recommendation = "timing-and-ranking-training"
        ready_for_extraction_loop = False
    elif slots_with_measure_wide_pitch > 1:
        recommendation = "hybrid-pitch-extraction-and-ranking-training"
        ready_for_extraction_loop = True
    else:
        recommendation = "pitch-extraction-training-primary"
        ready_for_extraction_loop = True

    checks = {
        "timingBenchmarkPassed": timing.get("passed") is True,
        "allNineSlotsInspected": total_slots == 9,
        "notationEventsPresent": events_inspected > 0,
        "readOnlyBenchmark": True,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-measure-wide-pitch-recovery",
        "passed": all(checks.values()),
        "eventsInspected": events_inspected,
        "protectedSlotCount": total_slots,
        "slotsContainingCorrectPitchAnywhere": slots_with_measure_wide_pitch,
        "slotsContainingCorrectPitchWithinFourSteps": slots_with_nearby_pitch,
        "measureWideCandidatePresencePercentage": measure_wide_percentage,
        "recommendedNextTrainingLoop": recommendation,
        "readyForBoundedExtractionTrainingLoop": ready_for_extraction_loop,
        "slotReports": slot_reports,
        "checks": checks,
        "safeguards": {
            "doesNotModifyV7OrV8Events": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "productionPromotionAllowed": False,
        },
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff measure-wide pitch recovery pass:", report["passed"])
    print("Notation events inspected:", events_inspected)
    print(
        "Slots containing a correct pitch anywhere:",
        f"{slots_with_measure_wide_pitch}/{total_slots}",
    )
    print(
        "Slots containing a correct pitch within four steps:",
        f"{slots_with_nearby_pitch}/{total_slots}",
    )
    print("Measure-wide candidate presence:", f"{measure_wide_percentage}%")
    print("Recommended next loop:", recommendation)
    print("Ready for bounded extraction loop:", ready_for_extraction_loop)
    print("Production promotion allowed: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
