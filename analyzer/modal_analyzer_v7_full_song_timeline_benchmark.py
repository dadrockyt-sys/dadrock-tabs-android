from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v7 as analyzer

app = modal.App("dadrock-v7-full-song-timeline-benchmark")
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
)


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_end(event: dict[str, Any]) -> float:
    start = event_start(event)
    return max(start, float(event.get("end") or event.get("end_time") or start))


def ordered_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        [event for event in (result.get("events") or []) if isinstance(event, dict)],
        key=event_start,
    )


def event_at(events: list[dict[str, Any]], index: Any) -> dict[str, Any] | None:
    try:
        resolved = int(index)
    except (TypeError, ValueError):
        return None
    if resolved < 0 or resolved >= len(events):
        return None
    return events[resolved]


def cluster_indices(
    indices: list[int],
    events: list[dict[str, Any]],
    maximum_gap_seconds: float = 0.9,
) -> list[dict[str, Any]]:
    located: list[tuple[int, float, float]] = []
    for index in sorted(set(indices)):
        event = event_at(events, index)
        if event is not None:
            located.append((index, event_start(event), event_end(event)))

    clusters: list[dict[str, Any]] = []
    for index, start, end in located:
        if clusters and start - float(clusters[-1]["end"]) <= maximum_gap_seconds:
            clusters[-1]["end"] = round(max(float(clusters[-1]["end"]), end), 4)
            clusters[-1]["eventIndices"].append(index)
            clusters[-1]["eventCount"] = len(clusters[-1]["eventIndices"])
        else:
            clusters.append(
                {
                    "start": round(start, 4),
                    "end": round(end, 4),
                    "eventIndices": [index],
                    "eventCount": 1,
                }
            )
    return clusters


def production_unchanged(generic: dict[str, Any], contextual: dict[str, Any]) -> bool:
    return (
        generic.get("generatedTab") == contextual.get("generatedTab")
        and generic.get("events") == contextual.get("events")
        and len(generic.get("events") or []) == len(contextual.get("events") or [])
    )


@app.function(image=image, timeout=2400, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    chords = [item for item in fixture.get("chords", []) if isinstance(item, dict)]
    progression = [str(item) for item in fixture.get("expectedProgression", [])]

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
        lead_generic = analyzer.analyze_audio_file(audio_path, "lead")
        lead = analyzer.analyze_audio_file(
            audio_path,
            "lead",
            enable_reference_guided_lead_techniques=True,
            bend_evidence_present=True,
        )
        bass_generic = analyzer.analyze_audio_file(audio_path, "bass")
        bass = analyzer.analyze_audio_file(
            audio_path,
            "bass",
            enable_reference_guided_bass_techniques=True,
        )
    finally:
        Path(audio_path).unlink(missing_ok=True)

    rhythm_analysis = rhythm.get("chordAnalysis") or {}
    lead_analysis = lead.get("leadTechniqueAnalysis") or {}
    bass_analysis = bass.get("bassTechniqueAnalysis") or {}
    lead_events = ordered_events(lead)
    bass_events = ordered_events(bass)

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

    lead_release_ranges = [
        {
            "bendStart": float(item.get("bendStart") or 0.0),
            "releaseStart": float(item.get("releaseStart") or 0.0),
            "timeDelta": float(item.get("timeDelta") or 0.0),
            "bendFret": item.get("bendFret"),
            "releaseFret": item.get("releaseFret"),
        }
        for item in (lead_analysis.get("releasePairs") or [])
        if isinstance(item, dict)
    ]
    palm_indices = [int(value) for value in (lead_analysis.get("palmMutedEventIndices") or [])]
    palm_clusters = cluster_indices(palm_indices, lead_events)

    bass_points: dict[str, Any] = {}
    for label, key in (
        ("slide", "slideEventIndex"),
        ("mute", "muteEventIndex"),
        ("rest", "restEventIndex"),
    ):
        index = bass_analysis.get(key)
        event = event_at(bass_events, index)
        bass_points[label] = (
            {
                "eventIndex": int(index),
                "start": round(event_start(event), 4),
                "end": round(event_end(event), 4),
            }
            if event is not None
            else None
        )
    if bass_points.get("slide"):
        bass_points["slide"]["targetFret"] = bass_analysis.get("slideTargetFret")

    all_times = [event_end(event) for event in rhythm.get("events") or [] if isinstance(event, dict)]
    song_duration = round(max(all_times, default=0.0), 4)

    checks = {
        "rhythmProductionUnchanged": production_unchanged(rhythm_generic, rhythm),
        "leadProductionUnchanged": production_unchanged(lead_generic, lead),
        "bassProductionUnchanged": production_unchanged(bass_generic, bass),
        "harmonyTimelinePresent": bool(harmony_ranges),
        "leadReleaseTimelinePresent": bool(lead_release_ranges),
        "leadPalmMuteTimelinePresent": bool(palm_clusters),
        "bassSlideTimelinePresent": bass_points.get("slide") is not None,
        "bassMuteTimelinePresent": bass_points.get("mute") is not None,
        "bassRestTimelinePresent": bass_points.get("rest") is not None,
        "timelineWithinSong": all(
            0.0 <= value <= song_duration + 0.01
            for value in [
                *[float(item["start"]) for item in harmony_ranges],
                *[float(item["end"]) for item in harmony_ranges],
                *[float(item["bendStart"]) for item in lead_release_ranges],
                *[float(item["releaseStart"]) for item in lead_release_ranges],
                *[float(item["start"]) for item in palm_clusters],
                *[float(item["end"]) for item in palm_clusters],
                *[
                    float(point[field])
                    for point in bass_points.values()
                    if isinstance(point, dict)
                    for field in ("start", "end")
                ],
            ]
        ),
        "noSyntheticNotes": (
            rhythm_analysis.get("noSyntheticNotes") is True
            and int(lead_analysis.get("syntheticNoteCount") or 0) == 0
            and int(bass_analysis.get("syntheticNoteCount") or 0) == 0
        ),
    }

    report = {
        "benchmarkVersion": 7,
        "benchmarkType": "v7-full-song-read-only-diagnostic-timeline",
        "audioName": audio_name,
        "songDuration": song_duration,
        "rhythmVocabulary": rhythm_analysis.get("chordVocabulary") or [],
        "rhythmPromotions": rhythm_analysis.get("referenceAwarePromotions") or {},
        "harmonyRanges": harmony_ranges,
        "leadReleaseRanges": lead_release_ranges,
        "leadPalmMuteClusters": palm_clusters,
        "leadPalmMutedEventCount": len(palm_indices),
        "bassPoints": bass_points,
        "checks": checks,
        "passed": all(checks.values()),
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Timeline metadata is derived only from existing read-only diagnostics and "
            "production event timestamps. It must never alter tab, events, pitches, "
            "frets, timing, or note count."
        ),
    }
    return json.dumps(report, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    report_output: str = "/tmp/gomyway-full-song-v7-timeline-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    payload = run_benchmark.remote(audio_file.read_bytes(), audio_file.name, fixture)
    report = json.loads(bytes(payload).decode("utf-8"))
    Path(report_output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V7 FULL-SONG DIAGNOSTIC TIMELINE")
    print("=" * 72)
    print("Song duration:", report.get("songDuration"))
    print("Harmony ranges:", len(report.get("harmonyRanges") or []))
    print("Lead release ranges:", len(report.get("leadReleaseRanges") or []))
    print("Lead palm-mute clusters:", len(report.get("leadPalmMuteClusters") or []))
    print("Lead palm-muted events:", report.get("leadPalmMutedEventCount"))
    print("Bass points:", report.get("bassPoints"))
    print("\nChecks")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
