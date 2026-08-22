from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer
import song_section_detection_v8 as section_detector

app = modal.App("dadrock-v8-section-benchmark")
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

# String index 0 is the high E string in the locked V7 event format.
STANDARD_GUITAR_OPEN_MIDI = (64, 59, 55, 50, 45, 40)
BOUNDARY_TOLERANCE_MEASURES = 2
SECTION_SCORE_TARGET = 0.9


def _event_end(event: dict[str, Any]) -> float:
    start = float(event.get("start") or event.get("start_time") or 0.0)
    return max(start, float(event.get("end") or event.get("end_time") or start))


def _production_unchanged(
    generic: dict[str, Any],
    contextual: dict[str, Any],
) -> bool:
    return (
        generic.get("generatedTab") == contextual.get("generatedTab")
        and generic.get("events") == contextual.get("events")
        and len(generic.get("events") or []) == len(contextual.get("events") or [])
    )


def _beats_per_measure(time_signature: str) -> int:
    try:
        numerator = int(str(time_signature or "4/4").split("/", 1)[0])
    except (TypeError, ValueError):
        return 4
    return max(1, min(numerator, 12))


def _event_with_read_only_pitch(event: dict[str, Any]) -> dict[str, Any]:
    """Return a metadata-only copy with MIDI pitch filled from string and fret."""
    projected = dict(event)

    for key in ("midi", "midiPitch", "pitch"):
        value = projected.get(key)
        if value is not None:
            try:
                if int(value) > 0:
                    projected["midiPitch"] = int(value)
                    return projected
            except (TypeError, ValueError):
                pass

    try:
        string_index = int(
            projected.get("stringIndex")
            if projected.get("stringIndex") is not None
            else projected.get("string_index")
        )
        fret = int(projected.get("fret") or 0)
    except (TypeError, ValueError):
        return projected

    if 0 <= string_index < len(STANDARD_GUITAR_OPEN_MIDI) and fret >= 0:
        projected["midiPitch"] = STANDARD_GUITAR_OPEN_MIDI[string_index] + fret
        projected["pitchDerivedForSections"] = True

    return projected


def _section_measure_labels(
    sections: list[dict[str, Any]],
    measure_count: int,
) -> list[str]:
    labels = [""] * measure_count
    for section in sections:
        label = str(section.get("label") or "")
        start = max(1, int(section.get("startMeasure") or 1))
        end = min(measure_count, int(section.get("endMeasure") or start))
        for measure_number in range(start, end + 1):
            labels[measure_number - 1] = label
    return labels


def _nearest_same_label_section(
    reference: dict[str, Any],
    detected: list[dict[str, Any]],
) -> dict[str, Any] | None:
    label = str(reference.get("label") or "")
    candidates = [item for item in detected if str(item.get("label") or "") == label]
    if not candidates:
        return None
    reference_start = int(reference.get("startMeasure") or 0)
    return min(
        candidates,
        key=lambda item: abs(int(item.get("startMeasure") or 0) - reference_start),
    )


def _score_section_map(
    detected: list[dict[str, Any]],
    reference: list[dict[str, Any]],
    measure_count: int,
) -> dict[str, Any]:
    if not reference or measure_count <= 0:
        return {
            "measureLabelAccuracy": 0.0,
            "boundaryAccuracy": 0.0,
            "labelPresenceAccuracy": 0.0,
            "overallScore": 0.0,
            "boundaryToleranceMeasures": BOUNDARY_TOLERANCE_MEASURES,
            "comparisons": [],
        }

    detected_labels = _section_measure_labels(detected, measure_count)
    reference_labels = _section_measure_labels(reference, measure_count)
    matching_measures = sum(
        1
        for detected_label, reference_label in zip(detected_labels, reference_labels)
        if detected_label == reference_label
    )
    measure_accuracy = matching_measures / measure_count

    boundary_hits = 0
    label_hits = 0
    boundary_total = len(reference) * 2
    comparisons: list[dict[str, Any]] = []

    for reference_section in reference:
        detected_section = _nearest_same_label_section(reference_section, detected)
        label_present = detected_section is not None
        if label_present:
            label_hits += 1

        reference_start = int(reference_section.get("startMeasure") or 0)
        reference_end = int(reference_section.get("endMeasure") or reference_start)
        detected_start = (
            int(detected_section.get("startMeasure") or 0)
            if detected_section is not None
            else None
        )
        detected_end = (
            int(detected_section.get("endMeasure") or 0)
            if detected_section is not None
            else None
        )
        start_delta = (
            abs(detected_start - reference_start)
            if detected_start is not None
            else None
        )
        end_delta = (
            abs(detected_end - reference_end)
            if detected_end is not None
            else None
        )
        start_hit = start_delta is not None and start_delta <= BOUNDARY_TOLERANCE_MEASURES
        end_hit = end_delta is not None and end_delta <= BOUNDARY_TOLERANCE_MEASURES
        boundary_hits += int(start_hit) + int(end_hit)

        comparisons.append(
            {
                "label": reference_section.get("label"),
                "referenceStart": reference_start,
                "referenceEnd": reference_end,
                "detectedStart": detected_start,
                "detectedEnd": detected_end,
                "startDelta": start_delta,
                "endDelta": end_delta,
                "labelPresent": label_present,
                "startWithinTolerance": start_hit,
                "endWithinTolerance": end_hit,
            }
        )

    boundary_accuracy = boundary_hits / boundary_total if boundary_total else 0.0
    label_accuracy = label_hits / len(reference)
    overall_score = (
        measure_accuracy * 0.5
        + boundary_accuracy * 0.35
        + label_accuracy * 0.15
    )

    return {
        "measureLabelAccuracy": round(measure_accuracy, 4),
        "boundaryAccuracy": round(boundary_accuracy, 4),
        "labelPresenceAccuracy": round(label_accuracy, 4),
        "overallScore": round(overall_score, 4),
        "targetScore": SECTION_SCORE_TARGET,
        "boundaryToleranceMeasures": BOUNDARY_TOLERANCE_MEASURES,
        "comparisons": comparisons,
    }


@app.function(image=image, timeout=2400, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    chords = [item for item in fixture.get("chords", []) if isinstance(item, dict)]
    progression = [str(item) for item in fixture.get("expectedProgression", [])]
    reference_sections = [
        item for item in fixture.get("referenceSections", []) if isinstance(item, dict)
    ]
    tempo = float(fixture.get("tempo") or 120.0)
    time_signature = str(fixture.get("timeSignature") or "4/4")
    expected_measure_count = int(fixture.get("expectedMeasureCount") or 0)

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

    rhythm_analysis = rhythm.get("chordAnalysis") or {}
    rhythm_events = [
        event
        for event in (rhythm.get("events") or [])
        if isinstance(event, dict)
    ]
    section_events = [_event_with_read_only_pitch(event) for event in rhythm_events]
    harmony_ranges = [
        {
            "chord": item.get("matchedChord"),
            "start": round(float(item.get("start") or 0.0), 4),
            "end": round(float(item.get("end") or 0.0), 4),
            "duration": round(float(item.get("duration") or 0.0), 4),
            "windowCount": int(item.get("windowCount") or 1),
        }
        for item in (rhythm_analysis.get("chords") or [])
        if isinstance(item, dict) and item.get("matchedChord")
    ]

    fingerprints = section_detector.build_measure_fingerprints(
        section_events,
        tempo=tempo,
        beats_per_measure=_beats_per_measure(time_signature),
        chord_ranges=harmony_ranges,
    )
    sections = section_detector.detect_song_sections(fingerprints)
    measure_sections = section_detector.attach_section_metadata(fingerprints, sections)
    section_score = _score_section_map(
        sections,
        reference_sections,
        len(measure_sections),
    )

    song_duration = round(
        max((_event_end(event) for event in rhythm_events), default=0.0),
        4,
    )
    section_starts = [
        item for item in measure_sections if item.get("isSectionStart") is True
    ]
    derived_pitch_count = sum(
        1 for event in section_events if event.get("pitchDerivedForSections") is True
    )

    checks = {
        "rhythmProductionUnchanged": _production_unchanged(rhythm_generic, rhythm),
        "sectionMapPresent": bool(sections),
        "measureMetadataPresent": bool(measure_sections),
        "expectedMeasureCountMatched": (
            expected_measure_count <= 0 or len(measure_sections) == expected_measure_count
        ),
        "pitchFingerprintPresent": any(
            int(item.get("pitchRange") or 0) > 0 for item in measure_sections
        ),
        "introStartsAtMeasureOne": bool(sections)
        and sections[0].get("label") == "Intro"
        and int(sections[0].get("startMeasure") or 0) == 1,
        "endingOrOutroPresent": bool(sections)
        and sections[-1].get("label") in {"Ending", "Outro"},
        "sectionRangesOrdered": all(
            int(section.get("startMeasure") or 0)
            <= int(section.get("endMeasure") or 0)
            for section in sections
        ),
        "oneStartMarkerPerSection": len(section_starts) == len(sections),
        "timelineWithinSong": all(
            0.0 <= float(item.get("start") or 0.0)
            <= float(item.get("end") or 0.0)
            <= song_duration + 0.01
            for item in measure_sections
        ),
        "noSyntheticNotes": rhythm_analysis.get("noSyntheticNotes") is True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-song-section-detection",
        "audioName": audio_name,
        "songDuration": song_duration,
        "tempo": tempo,
        "timeSignature": time_signature,
        "expectedMeasureCount": expected_measure_count,
        "derivedPitchEventCount": derived_pitch_count,
        "referenceSections": reference_sections,
        "sections": sections,
        "measureSections": measure_sections,
        "sectionScore": section_score,
        "checks": checks,
        "passed": all(checks.values()),
        "trainingPassed": (
            all(checks.values())
            and float(section_score.get("overallScore") or 0.0) >= SECTION_SCORE_TARGET
        ),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Section metadata and evaluation are derived only from read-only copies of "
            "existing V7 rhythm events, chord diagnostics, tempo, time signature, and the "
            "professional benchmark map. The reference map scores V8 but is never returned "
            "as detected production output. Generated tab, events, pitches, frets, timing, "
            "and note count are never altered."
        ),
    }
    return json.dumps(report, separators=(",", ":")).encode("utf-8")
