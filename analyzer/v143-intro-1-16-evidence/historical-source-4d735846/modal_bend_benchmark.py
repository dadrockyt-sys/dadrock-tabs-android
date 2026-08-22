"""Inventory Jimmy PAIge's first bend-and-drums reference without changing V71."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer

app = modal.App("dadrock-bend-benchmark")
image = analyzer.image.add_local_python_source("modal_analyzer_v71")


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_end(event: dict[str, Any]) -> float:
    return float(
        event.get("end")
        or event.get("end_time")
        or event_start(event)
    )


def event_midi(event: dict[str, Any]) -> int | None:
    value = event.get("midi")
    if value is None:
        value = event.get("pitch")
    return int(value) if value is not None else None


def audio_duration(result: dict[str, Any], events: list[dict[str, Any]]) -> float:
    for container_name in ("audioMetadata", "normalizedAudio"):
        container = result.get(container_name)
        if isinstance(container, dict):
            for key in ("duration", "durationSeconds"):
                value = container.get(key)
                if value is not None:
                    return float(value)
    return max((event_end(event) for event in events), default=0.0)


def bend_window_report(
    events: list[dict[str, Any]],
    duration: float,
    expected: dict[str, Any],
) -> dict[str, Any]:
    start = float(expected["startProgress"]) * duration
    end = float(expected["endProgress"]) * duration
    source_midi = int(expected["sourceMidi"])
    target_midi = int(expected["targetMidi"])
    release_midi = int(expected["releaseToMidi"])

    selected = [
        event
        for event in events
        if start <= event_start(event) < end
    ]
    selected.sort(key=event_start)

    compact_events = [
        {
            "start": round(event_start(event), 4),
            "end": round(event_end(event), 4),
            "midi": event_midi(event),
            "stringIndex": event.get("stringIndex"),
            "fret": event.get("fret"),
        }
        for event in selected
    ]

    midi_sequence = [
        midi
        for midi in (event_midi(event) for event in selected)
        if midi is not None
    ]

    source_indices = [
        index for index, midi in enumerate(midi_sequence) if midi == source_midi
    ]
    target_indices = [
        index for index, midi in enumerate(midi_sequence) if midi == target_midi
    ]
    release_indices = [
        index for index, midi in enumerate(midi_sequence) if midi == release_midi
    ]

    ordered_rise = any(
        source_index < target_index
        for source_index in source_indices
        for target_index in target_indices
    )
    ordered_release = any(
        target_index < release_index
        for target_index in target_indices
        for release_index in release_indices
    )

    return {
        "bendId": expected["bendId"],
        "measure": expected["measure"],
        "start": round(start, 4),
        "end": round(end, 4),
        "sourceMidi": source_midi,
        "targetMidi": target_midi,
        "releaseMidi": release_midi,
        "eventCount": len(selected),
        "midiSequence": midi_sequence,
        "sourceDetected": bool(source_indices),
        "targetDetected": bool(target_indices),
        "releaseDetected": bool(release_indices),
        "orderedRiseEvidence": ordered_rise,
        "orderedReleaseEvidence": ordered_release,
        "discretePitchEvidenceComplete": ordered_rise and ordered_release,
        "events": compact_events,
    }


@app.function(image=image, timeout=900, memory=4096)
def analyze_bend_inventory(
    audio_bytes: bytes,
    filename: str,
    transcription_type: str,
    fixture: dict[str, Any],
) -> dict[str, Any]:
    suffix = Path(filename).suffix.lower() or ".audio"
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / f"source{suffix}"
        normalized = Path(temp_dir) / "normalized.wav"
        source.write_bytes(audio_bytes)

        original_metadata = analyzer.engine.inspect_audio_file(str(source))
        analyzer.engine.validate_audio_metadata(original_metadata)
        analyzer.engine.normalize_audio_file(str(source), str(normalized))
        normalized_metadata = analyzer.engine.inspect_audio_file(str(normalized))
        result = analyzer.analyze_audio_file(str(normalized), transcription_type)
        result["audioMetadata"] = original_metadata
        result["normalizedAudio"] = normalized_metadata

        events = [
            event for event in result.get("events", []) if isinstance(event, dict)
        ]
        duration = audio_duration(result, events)
        bends = [
            bend_window_report(events, duration, expected)
            for expected in fixture.get("expectedBends", [])
        ]
        complete = sum(
            1 for bend in bends if bend["discretePitchEvidenceComplete"]
        )

        report = {
            "benchmarkVersion": 1,
            "engineVersion": result.get("engineVersion"),
            "fixtureName": fixture.get("name"),
            "durationSeconds": round(duration, 4),
            "eventCount": len(events),
            "expectedBendCount": len(bends),
            "completeDiscretePitchEvidence": complete,
            "bendEvidenceAccuracy": (
                round(complete / len(bends), 4) if bends else 0.0
            ),
            "bends": bends,
            "importantLimitation": (
                "This inventories source-target-release note evidence only. "
                "It does not yet prove continuous pitch-contour bend detection."
            ),
        }
        return {
            "result": analyzer.to_json_safe(result),
            "report": analyzer.to_json_safe(report),
        }


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    transcription_type: str = "lead",
    result_output: str = "/tmp/gomyway-result.json",
    report_output: str = "/tmp/gomyway-bend-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)

    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload = analyze_bend_inventory.remote(
        audio_file.read_bytes(),
        audio_file.name,
        transcription_type,
        fixture,
    )
    result = dict(payload["result"])
    report = dict(payload["report"])

    Path(result_output).write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE GO MY WAY BEND INVENTORY")
    print("=" * 48)
    print("Engine:", report.get("engineVersion"))
    print("Duration:", report.get("durationSeconds"))
    print("Events:", report.get("eventCount"))
    print(
        "Discrete bend evidence:",
        f"{report.get('completeDiscretePitchEvidence')}/"
        f"{report.get('expectedBendCount')}",
    )

    for bend in report.get("bends", []):
        status = "PASS" if bend["discretePitchEvidenceComplete"] else "FAIL"
        print(
            status,
            bend["bendId"],
            "sequence=",
            bend["midiSequence"],
            "rise=",
            bend["orderedRiseEvidence"],
            "release=",
            bend["orderedReleaseEvidence"],
        )

    print("\nSaved files")
    print("Analyzer result:", result_output)
    print("Bend report:", report_output)
    print("\nV71 remains unchanged and protected by the Stairway guard.")
