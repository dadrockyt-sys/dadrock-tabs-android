from __future__ import annotations

import bisect
import json
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import (
    PHRASE_START_MEASURES,
    PROTECTED_SLOTS,
    REPO_ROOT,
)

SOURCE_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-full-song-winner-test-checkpoint.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-full-song-alignment-diagnosis.json"
)


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or 0.0)


def _event_pitch(event: dict[str, Any]) -> int:
    try:
        return int(event.get("midiPitch"))
    except (TypeError, ValueError):
        return -1


def _prepare_events(
    events: list[dict[str, Any]],
) -> tuple[list[float], list[int], list[dict[str, Any]]]:
    prepared = sorted(
        (
            (_event_start(event), _event_pitch(event), event)
            for event in events
            if _event_pitch(event) >= 0
        ),
        key=lambda item: item[0],
    )
    return (
        [item[0] for item in prepared],
        [item[1] for item in prepared],
        [item[2] for item in prepared],
    )


def _target_times(tempo: float, offset_seconds: float) -> list[tuple[dict[str, Any], int, float]]:
    measure_seconds = (60.0 / tempo) * 4.0
    targets: list[tuple[dict[str, Any], int, float]] = []
    for slot in PROTECTED_SLOTS:
        for phrase_start in PHRASE_START_MEASURES:
            measure_number = phrase_start + int(slot["measureOffset"])
            position = (int(slot["step"]) - 1) / 16.0
            target = (
                offset_seconds
                + ((measure_number - 1) * measure_seconds)
                + (position * measure_seconds)
            )
            targets.append((slot, phrase_start, target))
    return targets


def _fast_score(
    starts: list[float],
    pitches: list[int],
    tempo: float,
    offset_seconds: float,
    tolerance_seconds: float,
) -> tuple[int, int]:
    slot_presence: dict[tuple[str, int], bool] = {}
    total_matches = 0

    for slot, _phrase_start, target in _target_times(tempo, offset_seconds):
        key = (str(slot["patternId"]), int(slot["step"]))
        accepted = {int(value) for value in slot["acceptedMidi"]}
        left = bisect.bisect_left(starts, target - tolerance_seconds)
        right = bisect.bisect_right(starts, target + tolerance_seconds)
        for index in range(left, right):
            if pitches[index] in accepted:
                slot_presence[key] = True
                total_matches += 1

    return sum(1 for value in slot_presence.values() if value), total_matches


def _detailed_score(
    starts: list[float],
    pitches: list[int],
    events: list[dict[str, Any]],
    tempo: float,
    offset_seconds: float,
    tolerance_seconds: float,
) -> dict[str, Any]:
    correct_slots = 0
    total_matches = 0
    slot_reports: list[dict[str, Any]] = []

    for slot in PROTECTED_SLOTS:
        accepted = {int(value) for value in slot["acceptedMidi"]}
        matches: list[dict[str, Any]] = []
        nearby_histogram: dict[int, int] = {}

        for phrase_start in PHRASE_START_MEASURES:
            measure_seconds = (60.0 / tempo) * 4.0
            measure_number = phrase_start + int(slot["measureOffset"])
            position = (int(slot["step"]) - 1) / 16.0
            target = (
                offset_seconds
                + ((measure_number - 1) * measure_seconds)
                + (position * measure_seconds)
            )
            left = bisect.bisect_left(starts, target - tolerance_seconds)
            right = bisect.bisect_right(starts, target + tolerance_seconds)
            for index in range(left, right):
                pitch = pitches[index]
                nearby_histogram[pitch] = nearby_histogram.get(pitch, 0) + 1
                if pitch in accepted:
                    delta = abs(starts[index] - target)
                    matches.append(
                        {
                            "phraseStartMeasure": phrase_start,
                            "midiPitch": pitch,
                            "start": round(starts[index], 6),
                            "target": round(target, 6),
                            "delta": round(delta, 6),
                        }
                    )

        present = bool(matches)
        if present:
            correct_slots += 1
        total_matches += len(matches)
        slot_reports.append(
            {
                "patternId": slot["patternId"],
                "step": slot["step"],
                "acceptedMidiPitches": sorted(accepted),
                "correctCandidatePresent": present,
                "matchingOccurrences": len(matches),
                "matches": matches,
                "nearbyPitchHistogram": [
                    {"midiPitch": pitch, "support": count}
                    for pitch, count in sorted(
                        nearby_histogram.items(),
                        key=lambda item: (-item[1], item[0]),
                    )[:12]
                ],
            }
        )

    return {
        "tempo": round(tempo, 3),
        "offsetSeconds": round(offset_seconds, 3),
        "toleranceSeconds": round(tolerance_seconds, 3),
        "correctCandidateSlots": correct_slots,
        "totalMatchingOccurrences": total_matches,
        "slotReports": slot_reports,
    }


def _rank_key(result: dict[str, Any]) -> tuple[int, int, float]:
    return (
        int(result["correctCandidateSlots"]),
        int(result["totalMatchingOccurrences"]),
        -abs(float(result["tempo"]) - 129.0),
    )


def main() -> None:
    state_path = SOURCE_PATH if SOURCE_PATH.exists() else CHECKPOINT_PATH
    state = json.loads(state_path.read_text())
    call_id = state.get("callId")
    if not call_id:
        raise RuntimeError(f"No callId found in {state_path}")

    call = modal.FunctionCall.from_id(call_id)
    result_bytes = call.get(timeout=0)
    remote_result = json.loads(result_bytes.decode("utf-8"))
    raw_events = remote_result.get("events", [])
    if not raw_events:
        raise RuntimeError("Completed Modal result contained no events.")

    starts, pitches, events = _prepare_events(raw_events)

    candidates: list[dict[str, Any]] = []
    for tempo_tenths in range(1240, 1341):
        tempo = tempo_tenths / 10.0
        for offset_hundredths in range(-800, 801, 5):
            offset = offset_hundredths / 100.0
            correct, matches = _fast_score(
                starts,
                pitches,
                tempo,
                offset,
                0.18,
            )
            candidates.append(
                {
                    "tempo": round(tempo, 3),
                    "offsetSeconds": round(offset, 3),
                    "toleranceSeconds": 0.18,
                    "correctCandidateSlots": correct,
                    "totalMatchingOccurrences": matches,
                }
            )

    candidates.sort(key=_rank_key, reverse=True)
    best_summary = candidates[0]
    best = _detailed_score(
        starts,
        pitches,
        events,
        float(best_summary["tempo"]),
        float(best_summary["offsetSeconds"]),
        0.18,
    )
    top = candidates[:20]

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "jimmy-paige-full-song-alignment-diagnosis",
        "sourceCallId": call_id,
        "eventCount": len(events),
        "search": {
            "tempoRangeBpm": [124.0, 134.0],
            "tempoStepBpm": 0.1,
            "offsetRangeSeconds": [-8.0, 8.0],
            "offsetStepSeconds": 0.05,
            "toleranceSeconds": 0.18,
        },
        "best": best,
        "topCandidates": top,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge full-song alignment diagnosis")
    print(f"Events inspected: {len(events)}")
    print(
        "Best alignment: "
        f"tempo={best['tempo']} BPM | "
        f"offset={best['offsetSeconds']}s | "
        f"score={best['correctCandidateSlots']}/9 | "
        f"matches={best['totalMatchingOccurrences']}"
    )
    print("Slot findings:")
    for slot in best["slotReports"]:
        status = "PASS" if slot["correctCandidatePresent"] else "MISS"
        print(
            f"- {slot['patternId']} step {slot['step']}: {status} | "
            f"matches={slot['matchingOccurrences']} | "
            f"accepted={slot['acceptedMidiPitches']} | "
            f"nearby={slot['nearbyPitchHistogram'][:5]}"
        )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
