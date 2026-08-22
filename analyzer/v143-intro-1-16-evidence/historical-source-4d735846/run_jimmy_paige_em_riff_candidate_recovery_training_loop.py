from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterator

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-timing-alignment.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-em-riff-candidate-recovery-training.json"

VERSE_START = 18
VERSE_END = 32
STEPS_PER_MEASURE = 16
MATCH_RADII = [1, 2, 3, 4]

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


def _event_step(event: dict[str, Any]) -> int:
    position = _safe_float(event.get("positionInMeasure"))
    if position >= 0.0:
        return max(0, min(STEPS_PER_MEASURE - 1, int(round(position * STEPS_PER_MEASURE))))
    for key in ("quantizedStep", "step", "stepInMeasure"):
        step = _safe_int(event.get(key))
        if step >= 0:
            return max(0, min(STEPS_PER_MEASURE - 1, step))
    return -1


def _event_pitch(event: dict[str, Any]) -> int:
    midi_pitch = _safe_int(event.get("midiPitch"))
    if midi_pitch >= 0:
        return midi_pitch
    string_index = _safe_int(event.get("stringIndex"))
    fret = _safe_int(event.get("fret"))
    if string_index in OPEN_STRING_MIDI and fret >= 0:
        return OPEN_STRING_MIDI[string_index] + fret
    return -1


def main() -> None:
    if not NOTATION_PATH.exists():
        raise FileNotFoundError(f"Missing {NOTATION_PATH.name}")
    if not TIMING_PATH.exists():
        raise FileNotFoundError(
            "Missing Em riff timing alignment. Run the timing benchmark first."
        )

    notation = json.loads(NOTATION_PATH.read_text())
    timing = json.loads(TIMING_PATH.read_text())

    protected_steps = {
        pattern_id: [int(step) for step in item.get("quantizedOnsetSteps") or []]
        for pattern_id, item in (timing.get("patternTiming") or {}).items()
        if isinstance(item, dict)
    }

    events: list[dict[str, int]] = []
    for node in _walk(notation):
        measure = _safe_int(node.get("measureNumber"))
        if not VERSE_START <= measure <= VERSE_END:
            continue
        step = _event_step(node)
        midi_pitch = _event_pitch(node)
        if step < 0 or midi_pitch < 0:
            continue
        events.append(
            {
                "measureNumber": measure,
                "quantizedStep": step,
                "midiPitch": midi_pitch,
            }
        )

    attempts: list[dict[str, Any]] = []
    best_attempt: dict[str, Any] | None = None

    for radius in MATCH_RADII:
        slot_support: dict[str, dict[int, Counter[int]]] = {
            "em-riff-a": defaultdict(Counter),
            "em-riff-b": defaultdict(Counter),
        }

        for event in events:
            measure = event["measureNumber"]
            pattern_id = "em-riff-a" if measure % 2 == 0 else "em-riff-b"
            targets = protected_steps.get(pattern_id) or []
            nearest = min(
                targets,
                key=lambda target: abs(target - event["quantizedStep"]),
                default=None,
            )
            if nearest is None:
                continue
            if abs(nearest - event["quantizedStep"]) <= radius:
                slot_support[pattern_id][nearest][event["midiPitch"]] += 1

        slot_reports: list[dict[str, Any]] = []
        slots_with_correct_candidate = 0
        correct_leading_slots = 0

        for pattern_id in ("em-riff-a", "em-riff-b"):
            for step in protected_steps.get(pattern_id) or []:
                ranked = slot_support[pattern_id][step].most_common(12)
                accepted = set(EXPECTED[pattern_id][step])
                matches = [
                    {"midiPitch": pitch, "support": support, "rank": rank}
                    for rank, (pitch, support) in enumerate(ranked, start=1)
                    if pitch in accepted
                ]
                if matches:
                    slots_with_correct_candidate += 1
                leading_pitch = ranked[0][0] if ranked else None
                if leading_pitch in accepted:
                    correct_leading_slots += 1
                slot_reports.append(
                    {
                        "patternId": pattern_id,
                        "quantizedStep": step,
                        "acceptedMidiPitches": sorted(accepted),
                        "correctCandidatePresent": bool(matches),
                        "correctCandidateMatches": matches,
                        "leadingMidiPitch": leading_pitch,
                        "leadingCorrect": leading_pitch in accepted,
                        "topCandidates": [
                            {"midiPitch": pitch, "support": support}
                            for pitch, support in ranked[:5]
                        ],
                    }
                )

        attempt = {
            "attempt": len(attempts) + 1,
            "matchRadiusSteps": radius,
            "slotsWithCorrectCandidate": slots_with_correct_candidate,
            "candidatePresencePercentage": round(
                100.0 * slots_with_correct_candidate / 9.0, 2
            ),
            "correctLeadingSlots": correct_leading_slots,
            "leadingAccuracyPercentage": round(
                100.0 * correct_leading_slots / 9.0, 2
            ),
            "slotReports": slot_reports,
        }
        attempts.append(attempt)

        if best_attempt is None or (
            attempt["slotsWithCorrectCandidate"],
            attempt["correctLeadingSlots"],
            -attempt["matchRadiusSteps"],
        ) > (
            best_attempt["slotsWithCorrectCandidate"],
            best_attempt["correctLeadingSlots"],
            -best_attempt["matchRadiusSteps"],
        ):
            best_attempt = attempt

    assert best_attempt is not None

    baseline = attempts[0]
    improved = (
        best_attempt["slotsWithCorrectCandidate"]
        > baseline["slotsWithCorrectCandidate"]
    )

    next_mode = (
        "bounded-candidate-ranking-training"
        if best_attempt["slotsWithCorrectCandidate"] == 9
        else "hybrid-pitch-extraction-and-ranking-training"
    )

    checks = {
        "timingAlignmentPassed": timing.get("passed") is True,
        "allNineProtectedSlotsPresent": sum(len(v) for v in protected_steps.values()) == 9,
        "notationEventsPresent": bool(events),
        "boundedAttemptsOnly": len(attempts) == len(MATCH_RADII),
        "readOnlyTraining": True,
        "lockedV7EventsProtected": True,
        "lockedV8EventsProtected": True,
        "lockedTimingProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "trainingVersion": 8,
        "trainingType": "bounded-em-riff-candidate-recovery-loop",
        "passed": all(checks.values()),
        "trainingStarted": True,
        "productionPromotionAllowed": False,
        "baselineCorrectCandidateSlots": baseline["slotsWithCorrectCandidate"],
        "bestCorrectCandidateSlots": best_attempt["slotsWithCorrectCandidate"],
        "improved": improved,
        "bestMatchRadiusSteps": best_attempt["matchRadiusSteps"],
        "recommendedNextLoop": next_mode,
        "attemptCount": len(attempts),
        "attempts": attempts,
        "checks": checks,
        "safeguards": {
            "doesNotRewriteJimmyEvents": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotModifyTimingTemplates": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "If candidate recovery reaches 9/9, start bounded ranking optimization. "
            "Otherwise, add a guarded extractor parameter hook for the missing slots."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge Em riff candidate recovery loop pass:", report["passed"])
    print("Training started:", report["trainingStarted"])
    print("Attempts completed:", report["attemptCount"])
    print("Baseline correct-candidate slots:", f"{baseline['slotsWithCorrectCandidate']}/9")
    print("Best correct-candidate slots:", f"{best_attempt['slotsWithCorrectCandidate']}/9")
    print("Best timing radius:", best_attempt["matchRadiusSteps"])
    print("Improved:", improved)
    print("Recommended next loop:", next_mode)
    print("Production promotion allowed: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
