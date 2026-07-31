from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import (
    MEASURE_SECONDS,
    PHRASE_START_MEASURES,
    PROTECTED_SLOTS,
    REPO_ROOT,
    TIMING_TOLERANCE_SECONDS,
)

INPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-deployed-training.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-deployed-training-relative-score.json"


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or 0.0)


def _event_pitch(event: dict[str, Any]) -> int:
    try:
        return int(event.get("midiPitch"))
    except (TypeError, ValueError):
        return -1


def _absolute_slot_time(phrase_start_measure: int, slot: dict[str, Any]) -> float:
    measure_number = phrase_start_measure + int(slot["measureOffset"])
    position = (int(slot["step"]) - 1) / 16.0
    return ((measure_number - 1) * MEASURE_SECONDS) + (position * MEASURE_SECONDS)


def _candidate_offsets(events: list[dict[str, Any]]) -> list[float]:
    offsets: set[float] = set()
    for slot in PROTECTED_SLOTS:
        accepted = {int(value) for value in slot["acceptedMidi"]}
        for phrase_start in PHRASE_START_MEASURES:
            target = _absolute_slot_time(phrase_start, slot)
            for event in events:
                if _event_pitch(event) not in accepted:
                    continue
                offsets.add(round(target - _event_start(event), 3))
    return sorted(offsets)


def _score_at_offset(events: list[dict[str, Any]], offset: float) -> dict[str, Any]:
    slot_reports: list[dict[str, Any]] = []
    correct_slots = 0
    total_matching_occurrences = 0

    for slot in PROTECTED_SLOTS:
        accepted = {int(value) for value in slot["acceptedMidi"]}
        matches: list[dict[str, Any]] = []

        for phrase_start in PHRASE_START_MEASURES:
            relative_target = _absolute_slot_time(phrase_start, slot) - offset
            for event in events:
                if _event_pitch(event) not in accepted:
                    continue
                delta = abs(_event_start(event) - relative_target)
                if delta <= TIMING_TOLERANCE_SECONDS:
                    matches.append(
                        {
                            "phraseStartMeasure": phrase_start,
                            "midiPitch": _event_pitch(event),
                            "eventStart": round(_event_start(event), 6),
                            "relativeTarget": round(relative_target, 6),
                            "deltaSeconds": round(delta, 6),
                        }
                    )

        present = bool(matches)
        if present:
            correct_slots += 1
        total_matching_occurrences += len(matches)
        slot_reports.append(
            {
                "patternId": slot["patternId"],
                "step": slot["step"],
                "acceptedMidiPitches": sorted(accepted),
                "correctCandidatePresent": present,
                "matchingOccurrences": len(matches),
                "matches": matches[:20],
            }
        )

    return {
        "timelineOffsetSeconds": round(offset, 6),
        "correctCandidateSlots": correct_slots,
        "candidatePresencePercentage": round(correct_slots / len(PROTECTED_SLOTS), 6),
        "totalMatchingOccurrences": total_matching_occurrences,
        "slotReports": slot_reports,
    }


def _best_relative_score(events: list[dict[str, Any]]) -> dict[str, Any]:
    candidates = _candidate_offsets(events)
    if not candidates:
        return {
            "timelineOffsetSeconds": None,
            "correctCandidateSlots": 0,
            "candidatePresencePercentage": 0.0,
            "totalMatchingOccurrences": 0,
            "slotReports": [],
            "candidateOffsetsTested": 0,
        }

    scores = [_score_at_offset(events, offset) for offset in candidates]
    best = max(
        scores,
        key=lambda item: (
            int(item["correctCandidateSlots"]),
            int(item["totalMatchingOccurrences"]),
            -abs(float(item["timelineOffsetSeconds"])),
        ),
    )
    best["candidateOffsetsTested"] = len(candidates)
    return best


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Missing deployed training report: {INPUT_PATH}")

    original = json.loads(INPUT_PATH.read_text())
    rescored_attempts: list[dict[str, Any]] = []

    for attempt in original.get("attempts", []):
        call_id = attempt.get("callId")
        if not call_id:
            continue

        call = modal.FunctionCall.from_id(str(call_id))
        result_bytes = call.get(timeout=0)
        result = json.loads(result_bytes.decode("utf-8"))
        events = result.get("events", [])
        relative_score = _best_relative_score(events)

        rescored = {
            **attempt,
            "extractedEventCount": len(events),
            "relativeTimelineScore": relative_score,
        }
        rescored_attempts.append(rescored)
        print(
            f"Attempt {attempt.get('attemptNumber')} {attempt.get('name')}: "
            f"relative={relative_score['correctCandidateSlots']}/9 | "
            f"offset={relative_score['timelineOffsetSeconds']}s | "
            f"matches={relative_score['totalMatchingOccurrences']}"
        )

    best_attempt = None
    if rescored_attempts:
        best_attempt = max(
            rescored_attempts,
            key=lambda item: (
                int(item["relativeTimelineScore"]["correctCandidateSlots"]),
                int(item["relativeTimelineScore"]["totalMatchingOccurrences"]),
            ),
        )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-deployed-training-relative-timeline-rescore",
        "sourceReport": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "reason": (
            "The V7 snippet starts at local time zero, while the original scorer used "
            "full-song absolute measure timestamps. This report estimates the snippet "
            "timeline offset and rescores the already-completed Modal results."
        ),
        "attemptsRescored": len(rescored_attempts),
        "bestCorrectCandidateSlots": (
            best_attempt["relativeTimelineScore"]["correctCandidateSlots"]
            if best_attempt
            else 0
        ),
        "bestAttempt": best_attempt,
        "attempts": rescored_attempts,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print(
        "Relative-timeline rescore complete | "
        f"best={report['bestCorrectCandidateSlots']}/9"
    )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
