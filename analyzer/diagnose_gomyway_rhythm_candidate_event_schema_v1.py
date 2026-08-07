from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
EXPECTED_EVENT_COUNT = 949


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing local artifact: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Expected top-level JSON object")
    return payload


def rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def nonempty(value: Any) -> bool:
    return value not in (None, False, "", [], {})


def main() -> None:
    payload = load(SOURCE_PATH)
    events = rows(payload)
    if len(events) != EXPECTED_EVENT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_EVENT_COUNT} events, found {len(events)}")

    top_keys = Counter()
    nonempty_keys = Counter()
    nested_dict_keys: dict[str, Counter[str]] = {}
    nested_list_dict_keys: dict[str, Counter[str]] = {}

    for event in events:
        for key, value in event.items():
            top_keys[key] += 1
            if nonempty(value):
                nonempty_keys[key] += 1
            if isinstance(value, dict):
                counter = nested_dict_keys.setdefault(key, Counter())
                for nested_key in value:
                    counter[nested_key] += 1
            elif isinstance(value, list):
                counter = nested_list_dict_keys.setdefault(key, Counter())
                for item in value:
                    if isinstance(item, dict):
                        for nested_key in item:
                            counter[nested_key] += 1

    interesting = [
        "string", "stringIndex", "fret", "midi", "midiPitch", "pitch",
        "note", "notes", "frequency", "hz", "quantizedStep", "step",
        "measure", "measureNumber", "startTime", "start_time", "duration",
        "durationSteps", "technique", "techniques",
    ]

    print("GOMYWAY RHYTHM CANDIDATE EVENT SCHEMA DIAGNOSTIC V1")
    print("Passed: True")
    print("Event count:", len(events))
    print("Top-level payload keys:", sorted(payload.keys()))
    print("Event key counts:")
    for key, count in sorted(top_keys.items()):
        print(f"  {key}: present={count} nonempty={nonempty_keys[key]}")

    print("Interesting field presence:")
    for key in interesting:
        print(f"  {key}: present={top_keys[key]} nonempty={nonempty_keys[key]}")

    print("Nested dict schemas:")
    if not nested_dict_keys:
        print("  none")
    else:
        for parent, counter in sorted(nested_dict_keys.items()):
            print(f"  {parent}: {dict(sorted(counter.items()))}")

    print("Nested list-of-dict schemas:")
    if not nested_list_dict_keys:
        print("  none")
    else:
        for parent, counter in sorted(nested_list_dict_keys.items()):
            print(f"  {parent}: {dict(sorted(counter.items()))}")

    print("Representative first 5 events:")
    for index, event in enumerate(events[:5]):
        print(f"  event[{index}]={json.dumps(event, sort_keys=True)}")

    pitch_like = any(nonempty_keys[key] > 0 for key in ("midi", "midiPitch", "pitch", "frequency", "hz", "note", "notes"))
    direct_tab_like = any(nonempty_keys[key] > 0 for key in ("string", "stringIndex", "fret"))

    if direct_tab_like:
        recommendation = "repair-professional-grader-to-read-existing-tab-fields-v1"
    elif pitch_like:
        recommendation = "grade-professional-reference-via-pitch-to-tab-normalization-v1"
    else:
        recommendation = "separate-rhythm-placement-grade-from-note-fret-grade-v1"

    print("Direct string/fret fields available:", direct_tab_like)
    print("Pitch-like fields available:", pitch_like)
    print("Recommended next action:", recommendation)


if __name__ == "__main__":
    main()
