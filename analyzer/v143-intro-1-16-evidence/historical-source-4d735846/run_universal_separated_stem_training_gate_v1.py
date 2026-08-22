from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PARTS = {"rhythm", "bass", "lead"}
PART_LIMITS = {
    "rhythm": {"strings": 6, "max_fret": 24, "min_midi": 40, "max_midi": 88},
    "lead": {"strings": 6, "max_fret": 24, "min_midi": 40, "max_midi": 96},
    "bass": {"strings": 4, "max_fret": 24, "min_midi": 28, "max_midi": 67},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Protected quality gate for any separated instrument stem and its transcription events."
    )
    parser.add_argument("--stem", required=True, help="Separated WAV/MP3/M4A/AAC stem")
    parser.add_argument("--events", required=True, help="Transcription-event JSON produced from the stem")
    parser.add_argument("--part", required=True, choices=sorted(PARTS))
    parser.add_argument("--output", help="Audit JSON path; defaults beside the event file")
    parser.add_argument("--expected-measures", type=int, default=0)
    parser.add_argument("--minimum-events", type=int, default=8)
    parser.add_argument("--minimum-duration", type=float, default=2.0)
    parser.add_argument("--maximum-duplicate-ratio", type=float, default=0.40)
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ffprobe_audio(path: Path) -> dict[str, Any]:
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("ffprobe is required but was not found in PATH")
    command = [
        ffprobe,
        "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,sample_rate,channels,duration:format=duration",
        "-of", "json",
        str(path),
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(completed.stdout)
    streams = payload.get("streams") or []
    if not streams:
        raise RuntimeError("No audio stream found")
    stream = streams[0]
    duration_raw = stream.get("duration") or (payload.get("format") or {}).get("duration") or 0
    return {
        "codec": stream.get("codec_name"),
        "sampleRate": int(stream.get("sample_rate") or 0),
        "channels": int(stream.get("channels") or 0),
        "durationSeconds": float(duration_raw or 0),
    }


def load_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        rows = payload
        metadata: dict[str, Any] = {}
    elif isinstance(payload, dict):
        rows = None
        for key in ("events", "candidates", "rhythmEvents", "renderEvents", "noteEvents"):
            value = payload.get(key)
            if isinstance(value, list):
                rows = value
                break
        if rows is None:
            raise RuntimeError("Event JSON contains no recognized event list")
        metadata = {key: value for key, value in payload.items() if key not in {"events", "candidates", "rhythmEvents", "renderEvents", "noteEvents"}}
    else:
        raise RuntimeError("Event JSON must contain an object or list")
    return [row for row in rows if isinstance(row, dict)], metadata


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


def measure(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    if isinstance(value, list):
        return [note for note in value if isinstance(note, dict)]
    if any(key in event for key in ("fret", "string", "stringIndex", "midi", "pitch")):
        return [event]
    return []


def event_signature(event: dict[str, Any]) -> tuple[Any, ...]:
    normalized_notes: list[tuple[Any, ...]] = []
    for note in notes(event):
        normalized_notes.append((
            integer(note.get("string", note.get("stringIndex"))),
            integer(note.get("fret")),
            integer(note.get("midi", note.get("pitch"))),
        ))
    return (
        measure(event),
        step(event),
        tuple(sorted(normalized_notes)),
        integer(event.get("durationSteps", event.get("duration", 1))),
    )


def main() -> None:
    args = parse_args()
    stem = Path(args.stem).expanduser().resolve()
    event_path = Path(args.events).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else event_path.with_name(f"{event_path.stem}-{args.part}-training-gate-v1.json")
    )

    if not stem.exists() or not stem.is_file():
        raise FileNotFoundError(f"Separated stem not found: {stem}")
    if not event_path.exists() or not event_path.is_file():
        raise FileNotFoundError(f"Event JSON not found: {event_path}")

    audio = ffprobe_audio(stem)
    events, metadata = load_events(event_path)
    limits = PART_LIMITS[args.part]

    invalid_timing: list[int] = []
    invalid_notes: list[dict[str, Any]] = []
    empty_note_events: list[int] = []
    covered_measures: set[int] = set()
    timed_events = 0
    note_count = 0
    traceable_events = 0

    for index, event in enumerate(events):
        event_measure = measure(event)
        event_step = step(event)
        event_time = number(event.get("startTime", event.get("start", event.get("time"))))
        if event_measure is not None and event_measure > 0:
            covered_measures.add(event_measure)
        if event_step is not None or event_time is not None:
            timed_events += 1
        else:
            invalid_timing.append(index)
        if any(key in event for key in ("source", "sourceEventIndex", "trace", "origin", "confidence")):
            traceable_events += 1

        event_notes = notes(event)
        if not event_notes:
            empty_note_events.append(index)
            continue
        note_count += len(event_notes)
        for note in event_notes:
            string_value = integer(note.get("string", note.get("stringIndex")))
            fret_value = integer(note.get("fret"))
            midi_value = integer(note.get("midi", note.get("pitch")))
            valid_string = string_value is not None and 1 <= string_value <= limits["strings"]
            valid_fret = fret_value is not None and 0 <= fret_value <= limits["max_fret"]
            valid_midi = midi_value is None or limits["min_midi"] <= midi_value <= limits["max_midi"]
            if not (valid_string and valid_fret and valid_midi):
                invalid_notes.append({
                    "eventIndex": index,
                    "string": string_value,
                    "fret": fret_value,
                    "midi": midi_value,
                })

    signatures = [event_signature(event) for event in events]
    counts = Counter(signatures)
    duplicate_instances = sum(count - 1 for count in counts.values() if count > 1)
    duplicate_ratio = duplicate_instances / len(events) if events else 1.0

    expected_measures = args.expected_measures
    missing_measures = (
        sorted(set(range(1, expected_measures + 1)) - covered_measures)
        if expected_measures > 0
        else []
    )

    checks = {
        "stemExists": stem.exists(),
        "stemDurationValid": audio["durationSeconds"] >= args.minimum_duration,
        "stemSampleRateValid": audio["sampleRate"] >= 16000,
        "stemChannelsValid": 1 <= audio["channels"] <= 2,
        "eventCountValid": len(events) >= args.minimum_events,
        "allEventsTimed": len(invalid_timing) == 0,
        "allEventsContainNotes": len(empty_note_events) == 0,
        "allNotesPlayableForPart": len(invalid_notes) == 0,
        "duplicateRatioValid": duplicate_ratio <= args.maximum_duplicate_ratio,
        "expectedMeasureCoverageValid": not missing_measures,
        "traceabilityPresent": traceable_events > 0,
        "protectedPromotionDisabled": True,
    }
    passed = all(checks.values())

    report = {
        "schemaVersion": 1,
        "gateType": "universal-separated-stem-training-gate",
        "part": args.part,
        "passed": passed,
        "stem": {
            "path": str(stem),
            "sha256": sha256(stem),
            "bytes": stem.stat().st_size,
            **audio,
        },
        "eventSource": {
            "path": str(event_path),
            "sha256": sha256(event_path),
            "eventCount": len(events),
            "noteCount": note_count,
            "timedEvents": timed_events,
            "traceableEvents": traceable_events,
            "coveredMeasures": sorted(covered_measures),
            "coveredMeasureCount": len(covered_measures),
            "missingMeasures": missing_measures,
            "duplicateInstances": duplicate_instances,
            "duplicateRatio": duplicate_ratio,
            "metadata": metadata,
        },
        "failures": {
            "invalidTimingEventIndexes": invalid_timing[:100],
            "emptyNoteEventIndexes": empty_note_events[:100],
            "invalidNotes": invalid_notes[:100],
        },
        "thresholds": {
            "minimumEvents": args.minimum_events,
            "minimumDurationSeconds": args.minimum_duration,
            "maximumDuplicateRatio": args.maximum_duplicate_ratio,
            "expectedMeasures": expected_measures,
            **limits,
        },
        "checks": checks,
        "readyForPartTraining": passed,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Universal separated-stem training gate V1 complete")
    print("Part:", args.part)
    print("Passed:", passed)
    print("Stem duration:", round(audio["durationSeconds"], 3))
    print("Sample rate:", audio["sampleRate"])
    print("Channels:", audio["channels"])
    print("Events:", len(events))
    print("Notes:", note_count)
    print("Covered measures:", len(covered_measures))
    print("Missing measures:", missing_measures)
    print("Invalid timing events:", len(invalid_timing))
    print("Empty-note events:", len(empty_note_events))
    print("Invalid notes:", len(invalid_notes))
    print("Duplicate ratio:", round(duplicate_ratio, 6))
    print("Traceable events:", traceable_events)
    print("Ready for part training:", passed)
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", output_path)

    if not passed:
        raise SystemExit("Separated-stem training gate did not pass")


if __name__ == "__main__":
    main()
