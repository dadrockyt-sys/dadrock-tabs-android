from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
CHECKPOINT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test-checkpoint.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"

PITCH_KEYS = {"midiPitch", "pitch_midi", "pitchMidi", "pitch"}
TIME_KEYS = {"start", "start_time", "startTime", "time"}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def looks_like_note_event_list(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False
    sample = [item for item in value[:50] if isinstance(item, dict)]
    if not sample:
        return False

    # A true Basic Pitch event list must contain both pitch and time fields.
    # Slot reports can contain nearby midiPitch values, but do not have event
    # start times; requiring both prevents those reports from being mistaken
    # for the 1,629 extracted note events.
    pitch_and_time = 0
    for item in sample:
        keys = set(item.keys())
        if keys.intersection(PITCH_KEYS) and keys.intersection(TIME_KEYS):
            pitch_and_time += 1
    return pitch_and_time >= max(1, len(sample) // 2)


def find_event_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        if looks_like_note_event_list(value):
            return [item for item in value if isinstance(item, dict)]
        for item in value:
            found = find_event_list(item)
            if found:
                return found
    elif isinstance(value, dict):
        for key in ("events", "noteEvents", "notes", "result", "output", "prediction"):
            if key in value:
                found = find_event_list(value[key])
                if found:
                    return found
        for item in value.values():
            found = find_event_list(item)
            if found:
                return found
    return []


def main() -> None:
    output = load_json(OUTPUT_PATH)
    checkpoint = load_json(CHECKPOINT_PATH)

    existing_events = find_event_list(output.get("events", []))
    expected_count = int(output.get("extractedEventCount") or 0)
    if existing_events and (expected_count == 0 or len(existing_events) == expected_count):
        print(f"Winner report already contains valid note events: {len(existing_events)}")
        return

    if output.get("events") and not existing_events:
        print(
            "Ignoring invalid events payload in winner report; "
            "it is not a timed Basic Pitch note-event list."
        )

    call_id = output.get("callId") or checkpoint.get("callId")
    if not call_id:
        raise RuntimeError(
            "No Modal call ID was found in the winner report or checkpoint."
        )

    print(f"Retrieving completed Modal result: {call_id}")
    call = modal.FunctionCall.from_id(str(call_id))
    result_bytes = call.get(timeout=30)

    if isinstance(result_bytes, bytes):
        result = json.loads(result_bytes.decode("utf-8"))
    elif isinstance(result_bytes, str):
        result = json.loads(result_bytes)
    elif isinstance(result_bytes, dict):
        result = result_bytes
    else:
        raise TypeError(f"Unexpected Modal result type: {type(result_bytes)!r}")

    events = find_event_list(result)
    if not events:
        raise RuntimeError("The completed Modal result did not contain timed note events.")

    cache = {
        "schemaVersion": 1,
        "sourceCallId": str(call_id),
        "eventCount": len(events),
        "events": events,
        "protectedReference": True,
        "productionPromotionAllowed": False,
    }
    EVENT_CACHE_PATH.write_text(json.dumps(cache, indent=2) + "\n")

    output["events"] = events
    output["extractedEventCount"] = len(events)
    output["eventCache"] = str(EVENT_CACHE_PATH.relative_to(REPO_ROOT))
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")

    print("Full-song winner events restored: True")
    print(f"Events: {len(events)}")
    print(f"Winner report: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print(f"Event cache: {EVENT_CACHE_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
