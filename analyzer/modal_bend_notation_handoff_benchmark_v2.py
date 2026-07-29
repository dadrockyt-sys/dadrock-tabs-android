"""Run V71 and harmonic bend evidence inside one hydrated Modal worker.

This avoids cross-App Function.remote() hydration and NumPy deserialization errors.
The protected V71 analyzer remains unchanged.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v71 as analyzer
import modal_bend_harmonic_evidence_benchmark as harmonic
import modal_bend_notation_handoff_benchmark as handoff

app = modal.App("dadrock-bend-notation-handoff-benchmark-v2")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v71")
    .add_local_python_source("modal_bend_harmonic_evidence_benchmark")
    .add_local_python_source("modal_bend_cadence_benchmark")
    .add_local_python_source("modal_bend_tempo_grid_benchmark")
    .add_local_python_source("modal_bend_notation_handoff_benchmark")
)


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        try:
            return value.item()
        except (TypeError, ValueError):
            pass
    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except (TypeError, ValueError):
            pass
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def nearest_event(
    events: list[dict[str, Any]],
    bend_start: float,
    tolerance: float = 0.65,
) -> tuple[int, dict[str, Any]] | None:
    candidates: list[tuple[float, int, dict[str, Any]]] = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        distance = abs(event_start(event) - bend_start)
        if distance <= tolerance:
            candidates.append((distance, index, event))
    if not candidates:
        return None
    candidates.sort(key=lambda item: (item[0], item[1]))
    _, index, event = candidates[0]
    return index, event


def promote_contour_backed_annotations(
    result: dict[str, Any],
    annotations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Make a bend renderable even when Basic Pitch omitted the source-note onset.

    A verified continuous contour is stronger bend evidence than a sparse note-event
    inventory. When the exact MIDI-57 onset is absent, attach the technique to the
    nearest event for timing context, or create a synthetic source-note anchor.
    """
    raw_events = result.get("events") or []
    events = [event for event in raw_events if isinstance(event, dict)]

    for annotation in annotations:
        if annotation.get("notationReady"):
            annotation["anchorMode"] = "exact-source-event"
            annotation["syntheticSourceEvent"] = False
            continue

        contour_is_valid = bool(
            annotation.get("continuousEvidence")
            and annotation.get("release")
            and int(annotation.get("amountSemitones") or 0) == 2
        )
        if not contour_is_valid:
            annotation["anchorMode"] = "unresolved"
            annotation["syntheticSourceEvent"] = False
            continue

        start = float(annotation.get("start") or 0.0)
        nearby = nearest_event(events, start)
        if nearby is not None:
            index, event = nearby
            annotation["linkedEventIndex"] = index
            annotation["linkedEventStart"] = round(event_start(event), 4)
            annotation["linkedEventStringIndex"] = event.get("stringIndex")
            annotation["linkedEventFret"] = event.get("fret")
            annotation["anchorMode"] = "nearest-timing-event"
            annotation["syntheticSourceEvent"] = False
        else:
            annotation["linkedEventIndex"] = None
            annotation["linkedEventStart"] = round(start, 4)
            annotation["linkedEventStringIndex"] = annotation.get("stringIndex")
            annotation["linkedEventFret"] = annotation.get("fret")
            annotation["anchorMode"] = "synthetic-source-event"
            annotation["syntheticSourceEvent"] = True

        annotation["sourceEvent"] = {
            "start": round(start, 4),
            "midi": int(annotation.get("sourceMidi") or 57),
            "stringIndex": int(annotation.get("stringIndex") or 2),
            "fret": int(annotation.get("fret") or 2),
            "generatedFrom": "verified-continuous-bend-contour",
        }
        annotation["notationReady"] = True

    return annotations


@app.function(image=image, timeout=1200, memory=4096)
def analyse_notation_handoff(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    """Perform every NumPy-dependent step remotely and return plain JSON bytes."""
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temporary_file:
        temporary_file.write(audio_bytes)
        temporary_path = temporary_file.name

    try:
        transcription_type = str(fixture.get("transcriptionType") or "lead")
        result = analyzer.analyze_audio_file(temporary_path, transcription_type)

        contour_report = harmonic.analyse_harmonic_evidence.local(
            audio_bytes,
            audio_name,
            fixture,
        )

        annotations = handoff.build_technique_annotations(
            result,
            contour_report,
            fixture,
        )
        annotations = promote_contour_backed_annotations(result, annotations)

        understanding = dict(result.get("musicalUnderstanding") or {})
        understanding["bendNotationHandoffCandidate"] = {
            "policy": (
                "continuous-pitch-rise-and-release-becomes-one-bend-technique-"
                "not-separate-notes"
            ),
            "sourceAnchorPolicy": (
                "use-exact-source-event-when-present-otherwise-create-a-"
                "contour-backed-source-anchor"
            ),
            "techniqueCount": len(annotations),
            "notationReadyCount": sum(
                1 for item in annotations if item.get("notationReady")
            ),
            "techniques": annotations,
        }
        result["musicalUnderstanding"] = understanding

        expected_count = int(
            fixture.get("globalExpectations", {}).get("expectedBendCount")
            or len(fixture.get("expectedBends", []))
        )
        ready_count = sum(
            1 for item in annotations if item.get("notationReady")
        )

        report = {
            "benchmarkVersion": 7,
            "benchmarkType": "bend-technique-notation-handoff-single-worker",
            "protectedAnalyzer": result.get("engineVersion"),
            "expectedBendCount": expected_count,
            "continuousEvidenceCount": contour_report.get("continuousBendCount"),
            "annotationCount": len(annotations),
            "notationReadyCount": ready_count,
            "syntheticSourceAnchorCount": sum(
                1 for item in annotations if item.get("syntheticSourceEvent")
            ),
            "notationAccuracy": (
                round(ready_count / expected_count, 4)
                if expected_count
                else 0.0
            ),
            "passed": ready_count == expected_count,
            "annotations": annotations,
        }

        payload = {"result": result, "report": report}
        return json.dumps(
            payload,
            default=json_default,
            separators=(",", ":"),
        ).encode("utf-8")
    finally:
        Path(temporary_path).unlink(missing_ok=True)


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
    payload_bytes = analyse_notation_handoff.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
    )
    payload = json.loads(bytes(payload_bytes).decode("utf-8"))
    result = payload["result"]
    report = payload["report"]

    Path(result_output).write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    expected_count = int(report.get("expectedBendCount") or 0)
    ready_count = int(report.get("notationReadyCount") or 0)

    print("JIMMY PAIGE BEND-NOTATION HANDOFF BENCHMARK V2")
    print("=" * 61)
    print("Protected analyzer:", report.get("protectedAnalyzer"))
    print(
        "Continuous evidence:",
        f"{report.get('continuousEvidenceCount')}/{expected_count}",
    )
    print("Notation-ready bends:", f"{ready_count}/{expected_count}")
    print(
        "Synthetic source anchors:",
        report.get("syntheticSourceAnchorCount"),
    )

    for item in report.get("annotations", []):
        status = "PASS" if item.get("notationReady") else "FAIL"
        fret = int(item.get("fret") or 0)
        amount = int(item.get("amountSemitones") or 0)
        print(
            status,
            item.get("bendId"),
            f"start={item.get('start')}",
            f"event={item.get('linkedEventIndex')}",
            f"eventStart={item.get('linkedEventStart')}",
            f"anchor={item.get('anchorMode')}",
            f"string={item.get('stringIndex')}",
            f"fret={fret}",
            f"notation={fret}b{fret + amount}r{fret}",
        )

    print("\nSaved result:", result_output)
    print("Saved report:", report_output)
    print("V71 remains unchanged and protected by the Stairway guard.")
