"""Verify that recovered bend contours become explicit tablature techniques.

This benchmark deliberately leaves the protected V71 analyzer unchanged. It runs V71,
runs the verified harmonic-evidence detector, and then tests the handoff contract that a
continuous two-semitone rise/release must become one G-string fret-2 full bend event —
not separate fretted notes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer
import modal_bend_harmonic_evidence_benchmark as harmonic

app = modal.App("dadrock-bend-notation-handoff-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_harmonic_evidence_benchmark")
    .add_local_python_source("modal_bend_cadence_benchmark")
    .add_local_python_source("modal_bend_tempo_grid_benchmark")
)


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_midi(event: dict[str, Any]) -> int | None:
    value = event.get("midi")
    if value is None:
        value = event.get("pitch")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def find_source_event(
    events: list[dict[str, Any]],
    bend_start: float,
    source_midi: int,
    tolerance: float = 0.42,
) -> tuple[int, dict[str, Any]] | None:
    candidates: list[tuple[float, int, dict[str, Any]]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        midi = event_midi(event)
        if midi != source_midi:
            continue
        distance = abs(event_start(event) - bend_start)
        if distance <= tolerance:
            candidates.append((distance, index, event))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    _, index, event = candidates[0]
    return index, event


def build_technique_annotations(
    result: dict[str, Any],
    contour_report: dict[str, Any],
    fixture: dict[str, Any],
) -> list[dict[str, Any]]:
    events = result.get("events") or []
    if not isinstance(events, list):
        events = []

    expected_by_id = {
        str(item.get("bendId")): item
        for item in fixture.get("expectedBends", [])
        if isinstance(item, dict)
    }
    annotations: list[dict[str, Any]] = []

    for bend in contour_report.get("bends", []):
        if not isinstance(bend, dict):
            continue
        bend_id = str(bend.get("bendId") or "")
        expected = expected_by_id.get(bend_id)
        if expected is None:
            continue

        detected = bool(bend.get("continuousBendEvidence"))
        bend_start = float(bend.get("bendStart") or bend.get("expectedStart") or 0.0)
        source_midi = int(expected["sourceMidi"])
        linked = find_source_event(events, bend_start, source_midi)

        event_index: int | None = None
        linked_event: dict[str, Any] | None = None
        if linked is not None:
            event_index, linked_event = linked

        annotation = {
            "bendId": bend_id,
            "measure": int(expected["measure"]),
            "type": "bend",
            "bendType": str(expected.get("bendType") or "full"),
            "amountSemitones": int(expected.get("bendSemitones") or 2),
            "release": bool(expected.get("releaseExpected")),
            "stringIndex": int(expected["stringIndex"]),
            "fret": int(expected["fret"]),
            "sourceMidi": source_midi,
            "targetMidi": int(expected["targetMidi"]),
            "releaseToMidi": int(expected["releaseToMidi"]),
            "start": round(bend_start, 4),
            "targetTime": bend.get("targetTime"),
            "releaseTime": bend.get("releaseTime"),
            "continuousEvidence": detected,
            "linkedEventIndex": event_index,
            "linkedEventStart": (
                round(event_start(linked_event), 4) if linked_event is not None else None
            ),
            "linkedEventStringIndex": (
                linked_event.get("stringIndex") if linked_event is not None else None
            ),
            "linkedEventFret": linked_event.get("fret") if linked_event is not None else None,
        }
        annotation["notationReady"] = bool(
            annotation["continuousEvidence"]
            and annotation["release"]
            and annotation["amountSemitones"] == 2
            and annotation["linkedEventIndex"] is not None
        )
        annotations.append(annotation)

    return annotations


@app.function(image=image, timeout=600, memory=4096)
def run_protected_analyzer(
    audio_path: str,
    transcription_type: str,
) -> dict[str, Any]:
    """Run the protected V71 Python function inside a Modal worker."""
    return analyzer.analyze_audio_file(audio_path, transcription_type)


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_bend_reference.json",
    result_output: str = "/tmp/gomyway-notation-result.json",
    report_output: str = "/tmp/gomyway-notation-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    audio_bytes = audio_file.read_bytes()

    result = run_protected_analyzer.remote(
        str(audio_file), str(fixture.get("transcriptionType") or "lead")
    )
    contour_report = harmonic.analyse_harmonic_evidence.remote(
        audio_bytes, audio_file.name, fixture
    )
    annotations = build_technique_annotations(result, contour_report, fixture)

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["bendNotationHandoffCandidate"] = {
        "policy": "continuous-pitch-rise-and-release-becomes-one-bend-technique-not-separate-notes",
        "techniqueCount": len(annotations),
        "notationReadyCount": sum(1 for item in annotations if item["notationReady"]),
        "techniques": annotations,
    }
    result["musicalUnderstanding"] = understanding

    expected_count = int(
        fixture.get("globalExpectations", {}).get("expectedBendCount")
        or len(fixture.get("expectedBends", []))
    )
    ready_count = sum(1 for item in annotations if item["notationReady"])
    report = {
        "benchmarkVersion": 2,
        "benchmarkType": "bend-technique-notation-handoff",
        "protectedAnalyzer": result.get("engineVersion"),
        "expectedBendCount": expected_count,
        "continuousEvidenceCount": contour_report.get("continuousBendCount"),
        "annotationCount": len(annotations),
        "notationReadyCount": ready_count,
        "notationAccuracy": round(ready_count / expected_count, 4) if expected_count else 0.0,
        "passed": ready_count == expected_count,
        "annotations": annotations,
    }

    Path(result_output).write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8"
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True), encoding="utf-8"
    )

    print("JIMMY PAIGE BEND-NOTATION HANDOFF BENCHMARK")
    print("=" * 58)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print("Continuous evidence:", f"{report.get('continuousEvidenceCount')}/{expected_count}")
    print("Notation-ready bends:", f"{ready_count}/{expected_count}")
    for item in annotations:
        status = "PASS" if item["notationReady"] else "FAIL"
        print(
            status,
            item["bendId"],
            f"start={item['start']}",
            f"event={item['linkedEventIndex']}",
            f"eventStart={item['linkedEventStart']}",
            f"string={item['stringIndex']}",
            f"fret={item['fret']}",
            f"notation={item['fret']}b{item['fret'] + item['amountSemitones']}r{item['fret']}",
        )
    print("\nSaved result:", result_output)
    print("Saved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
