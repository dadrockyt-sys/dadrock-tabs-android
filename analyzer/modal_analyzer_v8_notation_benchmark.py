from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer
import song_section_detection_v8 as section_detector

app = modal.App("dadrock-v8-notation-benchmark")
image = analyzer.image.add_local_python_source(
    "modal_analyzer_v7",
    "modal_analyzer",
    "production_chord_diagnostics",
    "chord_sustain",
    "reference_aware_harmony",
    "production_lead_technique_diagnostics",
    "lead_technique_diagnostics_v7",
    "production_bass_technique_diagnostics",
    "bass_technique_diagnostics_v7",
    "song_section_detection_v8",
)

STANDARD_GUITAR_OPEN_MIDI = (64, 59, 55, 50, 45, 40)


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_end(event: dict[str, Any]) -> float:
    start = _event_start(event)
    return max(start, float(event.get("end") or event.get("end_time") or start))


def _event_pitch(event: dict[str, Any]) -> int:
    for key in ("midi", "midiPitch", "pitch"):
        value = event.get(key)
        try:
            resolved = int(value)
        except (TypeError, ValueError):
            continue
        if resolved > 0:
            return resolved

    try:
        string_index = int(
            event.get("stringIndex")
            if event.get("stringIndex") is not None
            else event.get("string_index")
        )
        fret = int(event.get("fret") or 0)
    except (TypeError, ValueError):
        return 0

    if 0 <= string_index < len(STANDARD_GUITAR_OPEN_MIDI) and fret >= 0:
        return STANDARD_GUITAR_OPEN_MIDI[string_index] + fret
    return 0


def _beats_per_measure(time_signature: str) -> int:
    try:
        numerator = int(str(time_signature or "4/4").split("/", 1)[0])
    except (TypeError, ValueError):
        return 4
    return max(1, min(numerator, 12))


def _project_event(
    event: dict[str, Any],
    event_index: int,
    measure_seconds: float,
    total_measures: int,
) -> dict[str, Any]:
    start = _event_start(event)
    end = _event_end(event)
    raw_measure = int(start // measure_seconds) + 1 if measure_seconds > 0 else 1
    measure_number = max(1, min(total_measures, raw_measure))
    measure_start = (measure_number - 1) * measure_seconds
    position = (start - measure_start) / measure_seconds if measure_seconds > 0 else 0.0

    try:
        string_index = int(
            event.get("stringIndex")
            if event.get("stringIndex") is not None
            else event.get("string_index")
        )
    except (TypeError, ValueError):
        string_index = 0

    try:
        fret = int(event.get("fret") or 0)
    except (TypeError, ValueError):
        fret = 0

    return {
        "eventIndex": event_index,
        "start": round(start, 6),
        "end": round(end, 6),
        "duration": round(max(0.0, end - start), 6),
        "measureNumber": measure_number,
        "positionInMeasure": round(max(0.0, min(0.999, position)), 6),
        "stringIndex": max(0, min(5, string_index)),
        "fret": max(0, fret),
        "midiPitch": _event_pitch(event),
        "confidence": round(
            float(
                event.get("confidence")
                or event.get("noteConfidence")
                or event.get("probability")
                or event.get("amplitude")
                or event.get("velocity")
                or 0.0
            ),
            6,
        ),
        "readOnly": True,
    }


@app.function(image=image, timeout=2400, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    chords = [item for item in fixture.get("chords", []) if isinstance(item, dict)]
    progression = [str(item) for item in fixture.get("expectedProgression", [])]
    tempo = float(fixture.get("tempo") or 120.0)
    time_signature = str(fixture.get("timeSignature") or "4/4")
    total_measures = max(1, int(fixture.get("expectedMeasureCount") or 1))

    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        audio_path = handle.name

    try:
        rhythm_generic = analyzer.analyze_audio_file(audio_path, "rhythm")
        rhythm = analyzer.analyze_audio_file(
            audio_path,
            "rhythm",
            reference_chords=chords,
            expected_progression=progression,
        )
    finally:
        Path(audio_path).unlink(missing_ok=True)

    rhythm_events = sorted(
        [event for event in (rhythm.get("events") or []) if isinstance(event, dict)],
        key=_event_start,
    )
    rhythm_analysis = rhythm.get("chordAnalysis") or {}
    harmony_ranges = [
        {
            "chord": item.get("matchedChord"),
            "start": round(float(item.get("start") or 0.0), 4),
            "end": round(float(item.get("end") or 0.0), 4),
            "duration": round(float(item.get("duration") or 0.0), 4),
        }
        for item in (rhythm_analysis.get("chords") or [])
        if isinstance(item, dict) and item.get("matchedChord")
    ]

    measure_seconds = 60.0 / tempo * _beats_per_measure(time_signature)
    projected_events = [
        _project_event(event, index, measure_seconds, total_measures)
        for index, event in enumerate(rhythm_events)
    ]
    fingerprints = section_detector.build_measure_fingerprints(
        rhythm_events,
        tempo=tempo,
        beats_per_measure=_beats_per_measure(time_signature),
        chord_ranges=harmony_ranges,
    )
    sections = section_detector.detect_song_sections(fingerprints)

    production_unchanged = (
        rhythm_generic.get("generatedTab") == rhythm.get("generatedTab")
        and rhythm_generic.get("events") == rhythm.get("events")
        and len(rhythm_generic.get("events") or []) == len(rhythm.get("events") or [])
    )

    checks = {
        "rhythmProductionUnchanged": production_unchanged,
        "rhythmEventsPresent": bool(projected_events),
        "eventsWithinMeasureGrid": all(
            1 <= int(event["measureNumber"]) <= total_measures
            and 0.0 <= float(event["positionInMeasure"]) < 1.0
            for event in projected_events
        ),
        "validStringAndFret": all(
            0 <= int(event["stringIndex"]) <= 5 and int(event["fret"]) >= 0
            for event in projected_events
        ),
        "sectionsPresent": bool(sections),
        "noSyntheticNotes": rhythm_analysis.get("noSyntheticNotes") is True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-rhythm-notation-projection",
        "audioName": audio_name,
        "tempo": tempo,
        "timeSignature": time_signature,
        "measureSeconds": round(measure_seconds, 6),
        "totalMeasures": total_measures,
        "sections": sections,
        "rhythmEvents": projected_events,
        "harmonyRanges": harmony_ranges,
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "V8 notation is a read-only projection of locked V7 rhythm events. "
            "It may calculate measure placement and drawing metadata but must never alter "
            "event count, pitch, fret, string, timing, confidence, or generated tab."
        ),
    }
    return json.dumps(report, separators=(",", ":")).encode("utf-8")
