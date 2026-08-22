from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-diagnosis.json"

VERSE_START = 18
VERSE_END = 32
STEPS_PER_MEASURE = 16
MATCH_RADIUS_STEPS = 1

# Standard guitar tuning, stringIndex 0 = high e, 5 = low E.
OPEN_STRING_MIDI = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}

# Professional source identities already manually verified from the uploaded score.
# Bend slots accept both the fretted source pitch and the full-step sounding pitch.
EXPECTED = {
    "em-riff-a": {
        2: {"sourceMidi": 57, "acceptedMidi": [57, 59], "label": "G-string fret 2 full-step bend"},
        6: {"sourceMidi": 55, "acceptedMidi": [55], "label": "open G bend-release target"},
        10: {"sourceMidi": 52, "acceptedMidi": [52], "label": "D-string fret 2"},
        14: {"sourceMidi": 45, "acceptedMidi": [45], "label": "open A"},
    },
    "em-riff-b": {
        2: {"sourceMidi": 57, "acceptedMidi": [57, 59], "label": "G-string fret 2 full-step bend"},
        4: {"sourceMidi": 55, "acceptedMidi": [55], "label": "open G bend-release target"},
        6: {"sourceMidi": 52, "acceptedMidi": [52], "label": "D-string fret 2"},
        10: {"sourceMidi": 45, "acceptedMidi": [45], "label": "open A"},
        14: {"sourceMidi": [62, 58], "acceptedMidi": [62, 58], "label": "B/G fret-3 double-stop"},
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


def _event_step(event: dict[str, Any]) -> int:
    position = _safe_float(event.get("positionInMeasure"))
    if position >= 0.0:
        return max(0, min(15, int(round(position * STEPS_PER_MEASURE))))
    return _safe_int(event.get("quantizedStep"))


def main() -> None:
    if not NOTATION_PATH.exists():
        raise FileNotFoundError(f"Missing {NOTATION_PATH.name}")
    if not TIMING_PATH.exists():
        raise FileNotFoundError(f"Missing {TIMING_PATH.name}")

    notation = json.loads(NOTATION_PATH.read_text())
    timing = json.loads(TIMING_PATH.read_text())
    protected_steps = {
        pattern_id: [int(step) for step in item.get("quantizedOnsetSteps") or []]
        for pattern_id, item in (timing.get("patternTiming") or {}).items()
        if isinstance(item, dict)
    }

    slot_pitch_support: dict[str, dict[int, Counter[int]]] = {
        "em-riff-a": defaultdict(Counter),
        "em-riff-b": defaultdict(Counter),
    }
    events_inspected = 0
    matched_events = 0

    for node in _walk(notation):
        measure = _safe_int(node.get("measureNumber"))
        if not VERSE_START <= measure <= VERSE_END:
            continue
        midi_pitch = _safe_int(node.get("midiPitch"))
        if midi_pitch < 0:
            string_index = _safe_int(node.get("stringIndex"))
            fret = _safe_int(node.get("fret"))
            if string_index in OPEN_STRING_MIDI and fret >= 0:
                midi_pitch = OPEN_STRING_MIDI[string_index] + fret
        step = _event_step(node)
        if midi_pitch < 0 or step < 0:
            continue

        events_inspected += 1
        pattern_id = "em-riff-a" if measure % 2 == 0 else "em-riff-b"
        targets = protected_steps.get(pattern_id) or []
        nearest = min(targets, key=lambda target: abs(target - step), default=None)
        if nearest is None or abs(nearest - step) > MATCH_RADIUS_STEPS:
            continue
        slot_pitch_support[pattern_id][nearest][midi_pitch] += 1
        matched_events += 1

    slot_reports: list[dict[str, Any]] = []
    pitch_supported_slots = 0
    for pattern_id in ("em-riff-a", "em-riff-b"):
        for step in protected_steps.get(pattern_id) or []:
            expected = EXPECTED[pattern_id][step]
            ranked = slot_pitch_support[pattern_id][step].most_common(8)
            observed = [{"midiPitch": pitch, "support": count} for pitch, count in ranked]
            accepted = set(expected["acceptedMidi"])
            accepted_support = sum(count for pitch, count in ranked if pitch in accepted)
            has_pitch_support = accepted_support > 0
            if has_pitch_support:
                pitch_supported_slots += 1
            slot_reports.append({
                "patternId": pattern_id,
                "quantizedStep": step,
                "professionalLabel": expected["label"],
                "acceptedMidiPitches": expected["acceptedMidi"],
                "observedMidiCandidates": observed,
                "acceptedPitchSupport": accepted_support,
                "pitchEvidencePresent": has_pitch_support,
                "diagnosis": (
                    "string-fret-assignment-error-likely"
                    if has_pitch_support
                    else "pitch-detection-and-string-assignment-both-need-training"
                ),
            })

    total_slots = sum(len(steps) for steps in protected_steps.values())
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-read-only-pitch-diagnosis",
        "passed": timing.get("passed") is True and events_inspected > 0 and total_slots == 9,
        "readyForExactScoring": False,
        "eventsInspected": events_inspected,
        "matchedProtectedEvents": matched_events,
        "protectedSlotCount": total_slots,
        "slotsWithCorrectPitchEvidence": pitch_supported_slots,
        "pitchEvidencePercentage": round(100.0 * pitch_supported_slots / max(1, total_slots), 2),
        "slotReports": slot_reports,
        "safeguards": {
            "readOnlyDiagnosis": True,
            "doesNotModifyV7OrV8Events": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
            "noSyntheticNotes": True,
        },
        "nextStep": (
            "Use this diagnosis to determine whether the next training loop should focus on "
            "pitch detection or on string/fret assignment. Do not promote any event yet."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff pitch diagnosis pass:", report["passed"])
    print("Protected slots diagnosed:", total_slots)
    print("Slots with correct pitch evidence:", f"{pitch_supported_slots}/{total_slots}")
    print("Pitch evidence percentage:", f"{report['pitchEvidencePercentage']}%")
    for item in slot_reports:
        leading = item["observedMidiCandidates"][:3]
        print(
            f"- {item['patternId']} step {item['quantizedStep']}: "
            f"{item['diagnosis']} observed={leading} expected={item['acceptedMidiPitches']}"
        )
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
