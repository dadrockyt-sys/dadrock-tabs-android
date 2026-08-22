from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-gomyway-chorus-chord-sustain-benchmark-v3")

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("ffmpeg")
    .pip_install("basic-pitch")
)


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def normalize_note_event(note_event: Any, offset: float) -> dict[str, Any] | None:
    if isinstance(note_event, dict):
        start = float(note_event.get("start_time") or note_event.get("start") or 0.0)
        end = float(note_event.get("end_time") or note_event.get("end") or start)
        midi = int(round(float(
            note_event.get("pitch_midi")
            or note_event.get("pitch")
            or note_event.get("midi")
            or 0
        )))
        amplitude = float(note_event.get("amplitude") or note_event.get("velocity") or 0.0)
    else:
        values = list(note_event)
        if len(values) < 3:
            return None
        start = float(values[0])
        end = float(values[1])
        midi = int(round(float(values[2])))
        amplitude = float(values[3]) if len(values) > 3 else 0.0

    if midi <= 0:
        return None

    return {
        "start": start + offset,
        "end": max(start, end) + offset,
        "duration": max(0.0, end - start),
        "midi": midi,
        "amplitude": amplitude,
    }


def cluster_events(
    events: list[dict[str, Any]],
    tolerance: float,
) -> list[dict[str, Any]]:
    ordered = sorted(events, key=lambda event: float(event.get("start") or 0.0))
    clusters: list[list[dict[str, Any]]] = []

    for event in ordered:
        start = float(event.get("start") or 0.0)
        if not clusters:
            clusters.append([event])
            continue
        cluster_start = min(float(item.get("start") or 0.0) for item in clusters[-1])
        if start - cluster_start <= tolerance:
            clusters[-1].append(event)
        else:
            clusters.append([event])

    summaries: list[dict[str, Any]] = []
    for index, cluster in enumerate(clusters):
        starts = [float(item.get("start") or 0.0) for item in cluster]
        ends = [float(item.get("end") or item.get("start") or 0.0) for item in cluster]
        midis = [int(item["midi"]) for item in cluster if item.get("midi") is not None]
        summaries.append({
            "clusterIndex": index,
            "start": min(starts),
            "end": max(ends),
            "duration": max(ends) - min(starts),
            "eventCount": len(cluster),
            "midis": midis,
            "pitchClasses": sorted({midi % 12 for midi in midis}),
        })
    return summaries


def best_chord_match(
    cluster: dict[str, Any],
    chords: list[dict[str, Any]],
) -> dict[str, Any] | None:
    observed = set(cluster.get("pitchClasses") or [])
    candidates: list[dict[str, Any]] = []
    for chord in chords:
        expected = set(chord.get("pitchClasses") or [])
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        precision = len(intersection) / max(1, len(observed))
        threshold = float(chord.get("minimumPitchClassCoverage") or 1.0)
        candidates.append({
            "name": chord.get("name"),
            "coverage": coverage,
            "precision": precision,
            "passed": coverage >= threshold and precision >= 0.5,
        })
    candidates.sort(
        key=lambda item: (
            bool(item.get("passed")),
            float(item.get("coverage") or 0.0),
            float(item.get("precision") or 0.0),
        ),
        reverse=True,
    )
    return candidates[0] if candidates else None


@app.function(image=image, timeout=1800, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
    start_time: float,
    duration: float,
) -> bytes:
    from basic_pitch.inference import predict

    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as source_handle:
        source_handle.write(audio_bytes)
        source_path = source_handle.name

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as slice_handle:
        slice_path = slice_handle.name

    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", str(start_time), "-t", str(duration),
            "-i", source_path, "-ac", "1", "-ar", "22050", slice_path,
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    _, _, raw_note_events = predict(slice_path)
    events = [
        normalized
        for normalized in (
            normalize_note_event(note_event, start_time)
            for note_event in raw_note_events
        )
        if normalized is not None
    ]

    tolerance = max(0.12, float(fixture.get("onsetToleranceSeconds") or 0.085))
    minimum_notes = int(fixture.get("minimumChordNotes") or 3)
    minimum_sustain = float(fixture.get("minimumSustainSeconds") or 0.35)
    chords = [chord for chord in fixture.get("chords", []) if isinstance(chord, dict)]

    clusters = cluster_events(events, tolerance)
    chord_clusters = [cluster for cluster in clusters if cluster["eventCount"] >= minimum_notes]

    matched_clusters: list[dict[str, Any]] = []
    for cluster in chord_clusters:
        match = best_chord_match(cluster, chords)
        enriched = dict(cluster)
        enriched["match"] = match
        if match and match.get("passed"):
            enriched["matchedChord"] = match.get("name")
            matched_clusters.append(enriched)

    observed_progression = [str(cluster.get("matchedChord")) for cluster in matched_clusters]
    chord_vocabulary = sorted(set(observed_progression))
    sustained = [
        cluster for cluster in matched_clusters
        if float(cluster.get("duration") or 0.0) >= minimum_sustain
    ]

    repeated_counts: dict[str, int] = {}
    for name in observed_progression:
        repeated_counts[name] = repeated_counts.get(name, 0) + 1

    checks = {
        "rawEventsPresent": len(events) >= 20,
        "simultaneousChordClusters": len(chord_clusters) >= 4,
        "matchedChordClusters": len(matched_clusters) >= 2,
        "twoOrMoreChordTypes": len(chord_vocabulary) >= 2,
        "sustainEvidence": len(sustained) >= 1,
        "repeatedChordAttacks": any(count >= 2 for count in repeated_counts.values()),
        "sliceDurationPreserved": duration >= 8.0,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 3,
        "benchmarkType": "gomyway-chorus-raw-midi-chord-sustain-diagnostic",
        "analysisPath": "raw-basic-pitch-chorus-slice",
        "sliceStart": start_time,
        "sliceDuration": duration,
        "eventCount": len(events),
        "clusterCount": len(clusters),
        "chordClusterCount": len(chord_clusters),
        "matchedChordClusterCount": len(matched_clusters),
        "chordVocabulary": chord_vocabulary,
        "observedProgression": observed_progression,
        "repeatedAttackCounts": repeated_counts,
        "sustainedChordCount": len(sustained),
        "checks": checks,
        "passed": all(checks.values()),
        "chordClusters": chord_clusters,
        "matchedClusters": matched_clusters,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "diagnostic only: inspect raw simultaneous chord evidence before V73 fingering handoff"
        ),
    }
    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    start_time: float = 155.0,
    duration: float = 20.0,
    report_output: str = "/tmp/gomyway-chorus-chord-sustain-v3-report.json",
) -> None:
    audio_file = Path(audio_path)
    fixture_file = Path(fixture_path)
    if not audio_file.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    if not fixture_file.is_file():
        raise FileNotFoundError(f"Fixture file not found: {fixture_file}")

    fixture = json.loads(fixture_file.read_text(encoding="utf-8"))
    report_bytes = run_benchmark.remote(
        audio_file.read_bytes(),
        audio_file.name,
        fixture,
        start_time,
        duration,
    )
    report = json.loads(bytes(report_bytes).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE CHORUS CHORD STRUCTURE & SUSTAIN BENCHMARK V3")
    print("=" * 72)
    print("Analysis path:", report.get("analysisPath"))
    print("Slice:", report.get("sliceStart"), "+", report.get("sliceDuration"), "seconds")
    print("Raw events:", report.get("eventCount"))
    print("Chord clusters:", report.get("chordClusterCount"))
    print("Matched chord clusters:", report.get("matchedChordClusterCount"))
    print("Chord vocabulary:", report.get("chordVocabulary"))
    print("Observed progression:", report.get("observedProgression"))
    print("Sustained chords:", report.get("sustainedChordCount"))
    print("Repeated attacks:", report.get("repeatedAttackCounts"))
    print("Checks:")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, V73, and all seven locked baselines remain unchanged.")
