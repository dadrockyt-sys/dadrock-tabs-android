from __future__ import annotations

import bisect
import json
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

ALIGNMENT_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-alignment-diagnosis.json"
)
FULL_SONG_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
)
CHECKPOINT_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-8-of-9-checkpoint.json"
)
MISS_DIAGNOSIS_PATH = (
    REPO_ROOT / "public" / "gomyway-jimmy-paige-em-riff-b-step-10-diagnosis.json"
)

TARGET_PATTERN = "em-riff-b"
TARGET_STEP = 10
TARGET_MIDI = 45


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_pitch(event: dict[str, Any]) -> int:
    try:
        return int(event.get("midiPitch"))
    except (TypeError, ValueError):
        return -1


def main() -> None:
    alignment = _load_json(ALIGNMENT_PATH)
    full_song = _load_json(FULL_SONG_PATH)

    best = alignment.get("best") or {}
    score = int(best.get("correctCandidateSlots") or 0)
    if score != 8:
        raise RuntimeError(
            f"Refusing to preserve unexpected score {score}/9; expected 8/9."
        )

    checkpoint = {
        "benchmarkVersion": 8,
        "checkpointType": "jimmy-paige-full-song-professional-reference-8-of-9",
        "status": "protected-training-checkpoint",
        "sourceAudio": full_song.get("source"),
        "sourceCallId": alignment.get("sourceCallId"),
        "eventCount": alignment.get("eventCount"),
        "winningFunction": full_song.get("functionName"),
        "winningParameters": full_song.get("parameters"),
        "professionalReferenceScore": "8/9",
        "bestAlignment": {
            "tempoBpm": best.get("tempo"),
            "offsetSeconds": best.get("offsetSeconds"),
            "toleranceSeconds": best.get("toleranceSeconds"),
            "matchingOccurrences": best.get("totalMatchingOccurrences"),
        },
        "remainingMiss": {
            "patternId": TARGET_PATTERN,
            "step": TARGET_STEP,
            "expectedMidiPitch": TARGET_MIDI,
        },
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    CHECKPOINT_PATH.write_text(json.dumps(checkpoint, indent=2) + "\n")

    call_id = alignment.get("sourceCallId")
    if not call_id:
        raise RuntimeError("Alignment report does not contain sourceCallId.")

    result_bytes = modal.FunctionCall.from_id(call_id).get(timeout=0)
    remote_result = json.loads(result_bytes.decode("utf-8"))
    events = sorted(
        [event for event in remote_result.get("events", []) if _event_pitch(event) >= 0],
        key=_event_start,
    )
    starts = [_event_start(event) for event in events]

    target_slot = None
    for slot in best.get("slotReports", []):
        if (
            slot.get("patternId") == TARGET_PATTERN
            and int(slot.get("step") or -1) == TARGET_STEP
        ):
            target_slot = slot
            break

    if target_slot is None:
        raise RuntimeError("Could not find em-riff-b step 10 in alignment report.")

    target_times = [
        float(match.get("target"))
        for match in target_slot.get("matches", [])
        if match.get("target") is not None
    ]

    # The missed slot has no matches, so reconstruct its candidate target times
    # from nearby slot metadata saved by the alignment diagnosis when available.
    if not target_times:
        tempo = float(best["tempo"])
        offset = float(best["offsetSeconds"])
        measure_seconds = (60.0 / tempo) * 4.0
        phrase_starts = [18, 34, 50, 66, 82, 98]
        measure_offset = 1
        position = (TARGET_STEP - 1) / 16.0
        target_times = [
            offset
            + ((phrase_start + measure_offset - 1) * measure_seconds)
            + (position * measure_seconds)
            for phrase_start in phrase_starts
        ]

    windows: list[dict[str, Any]] = []
    pitch_45_anywhere = 0
    for target in target_times:
        left = bisect.bisect_left(starts, target - 0.75)
        right = bisect.bisect_right(starts, target + 0.75)
        nearby = []
        for event in events[left:right]:
            pitch = _event_pitch(event)
            delta = _event_start(event) - target
            if pitch == TARGET_MIDI:
                pitch_45_anywhere += 1
            nearby.append(
                {
                    "midiPitch": pitch,
                    "start": round(_event_start(event), 6),
                    "deltaSeconds": round(delta, 6),
                    "confidence": event.get("confidence"),
                }
            )
        nearby.sort(key=lambda item: (abs(item["deltaSeconds"]), item["midiPitch"]))
        windows.append(
            {
                "target": round(target, 6),
                "windowSeconds": 0.75,
                "events": nearby[:40],
                "containsExpectedMidi45": any(
                    item["midiPitch"] == TARGET_MIDI for item in nearby
                ),
            }
        )

    diagnosis = {
        "benchmarkVersion": 8,
        "diagnosisType": "jimmy-paige-em-riff-b-step-10-final-miss",
        "protectedCheckpoint": str(CHECKPOINT_PATH.relative_to(REPO_ROOT)),
        "patternId": TARGET_PATTERN,
        "step": TARGET_STEP,
        "expectedMidiPitch": TARGET_MIDI,
        "targetOccurrencesInspected": len(target_times),
        "expectedPitchOccurrencesWithinPlusMinus075Seconds": pitch_45_anywhere,
        "classification": (
            "ranking-or-timing-problem"
            if pitch_45_anywhere > 0
            else "basic-pitch-candidate-missing"
        ),
        "windows": windows,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    MISS_DIAGNOSIS_PATH.write_text(json.dumps(diagnosis, indent=2) + "\n")

    print("Jimmy PAIge 8/9 checkpoint preserved: True")
    print(f"Checkpoint: {CHECKPOINT_PATH.relative_to(REPO_ROOT)}")
    print(
        "Final miss diagnosis: "
        f"{diagnosis['classification']} | "
        f"MIDI 45 nearby occurrences={pitch_45_anywhere}"
    )
    print(f"Diagnosis: {MISS_DIAGNOSIS_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
