from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import modal
import modal_analyzer_v73 as analyzer

app = modal.App("dadrock-gomyway-full-chord-sustain-benchmark")
image = (
    analyzer.image
    .add_local_python_source("modal_analyzer_v73")
    .add_local_python_source("modal_analyzer_v72")
)


def json_default(value: Any) -> Any:
    if hasattr(value, "item"):
        return value.item()
    if isinstance(value, set):
        return sorted(value)
    return str(value)


def event_start(event: dict[str, Any]) -> float:
    for key in ("start", "start_time", "startTime", "time"):
        value = event.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass
    return 0.0


def event_end(event: dict[str, Any]) -> float:
    start = event_start(event)
    for key in ("end", "end_time", "endTime"):
        value = event.get(key)
        if value is not None:
            try:
                return max(start, float(value))
            except (TypeError, ValueError):
                pass
    for key in ("duration", "durationSeconds"):
        value = event.get(key)
        if value is not None:
            try:
                return start + max(0.0, float(value))
            except (TypeError, ValueError):
                pass
    return start


def event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midi", "pitch", "midiPitch", "note"):
        value = event.get(key)
        if value is None:
            continue
        try:
            return int(round(float(value)))
        except (TypeError, ValueError):
            continue
    return None


def event_fret(event: dict[str, Any]) -> int | None:
    value = event.get("fret")
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def cluster_events(
    events: list[dict[str, Any]],
    tolerance: float,
) -> list[dict[str, Any]]:
    ordered = sorted(events, key=event_start)
    clusters: list[list[dict[str, Any]]] = []

    for event in ordered:
        start = event_start(event)
        if not clusters:
            clusters.append([event])
            continue
        cluster_start = min(event_start(item) for item in clusters[-1])
        if start - cluster_start <= tolerance:
            clusters[-1].append(event)
        else:
            clusters.append([event])

    summaries: list[dict[str, Any]] = []
    for index, cluster in enumerate(clusters):
        midis = [midi for midi in (event_midi(item) for item in cluster) if midi is not None]
        frets = [fret for fret in (event_fret(item) for item in cluster) if fret is not None]
        starts = [event_start(item) for item in cluster]
        ends = [event_end(item) for item in cluster]
        summaries.append(
            {
                "clusterIndex": index,
                "start": min(starts) if starts else 0.0,
                "end": max(ends) if ends else 0.0,
                "duration": (
                    max(ends) - min(starts)
                    if starts and ends
                    else 0.0
                ),
                "eventCount": len(cluster),
                "midis": midis,
                "pitchClasses": sorted({midi % 12 for midi in midis}),
                "frets": frets,
                "events": cluster,
            }
        )
    return summaries


def chord_match(
    cluster: dict[str, Any],
    chord: dict[str, Any],
) -> dict[str, Any]:
    observed = set(cluster.get("pitchClasses") or [])
    expected = set(chord.get("pitchClasses") or [])
    intersection = observed & expected
    coverage = len(intersection) / max(1, len(expected))
    precision = len(intersection) / max(1, len(observed))
    threshold = float(chord.get("minimumPitchClassCoverage") or 1.0)
    passed = coverage >= threshold and precision >= 0.6
    return {
        "name": chord.get("name"),
        "coverage": round(coverage, 4),
        "precision": round(precision, 4),
        "passed": passed,
        "expectedPitchClasses": sorted(expected),
        "observedPitchClasses": sorted(observed),
        "matchedPitchClasses": sorted(intersection),
    }


def best_chord_match(
    cluster: dict[str, Any],
    chords: list[dict[str, Any]],
) -> dict[str, Any] | None:
    candidates = [chord_match(cluster, chord) for chord in chords]
    candidates.sort(
        key=lambda item: (
            bool(item.get("passed")),
            float(item.get("coverage") or 0.0),
            float(item.get("precision") or 0.0),
        ),
        reverse=True,
    )
    return candidates[0] if candidates else None


def progression_subsequence_score(
    observed: list[str],
    expected: list[str],
) -> float:
    if not expected:
        return 1.0
    cursor = 0
    matched = 0
    for chord_name in observed:
        if cursor < len(expected) and chord_name == expected[cursor]:
            matched += 1
            cursor += 1
    return matched / len(expected)


def repeated_attack_score(
    matched_clusters: list[dict[str, Any]],
    minimum_attacks: int,
) -> tuple[float, dict[str, int]]:
    counts: dict[str, int] = {}
    for cluster in matched_clusters:
        name = str(cluster.get("matchedChord") or "")
        if name:
            counts[name] = counts.get(name, 0) + 1
    qualifying = sum(1 for count in counts.values() if count >= minimum_attacks)
    return min(1.0, qualifying / 3.0), counts


def evaluate(
    result: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    events = [
        event
        for event in (result.get("events") or [])
        if isinstance(event, dict)
    ]
    tolerance = float(fixture.get("onsetToleranceSeconds") or 0.085)
    minimum_notes = int(fixture.get("minimumChordNotes") or 3)
    minimum_sustain = float(fixture.get("minimumSustainSeconds") or 0.35)
    minimum_attacks = int(fixture.get("minimumRepeatedAttacks") or 3)
    chords = [
        chord
        for chord in (fixture.get("chords") or [])
        if isinstance(chord, dict)
    ]

    clusters = cluster_events(events, tolerance)
    chord_clusters = [
        cluster
        for cluster in clusters
        if int(cluster.get("eventCount") or 0) >= minimum_notes
    ]

    matched_clusters: list[dict[str, Any]] = []
    for cluster in chord_clusters:
        match = best_chord_match(cluster, chords)
        if match and match.get("passed"):
            matched = dict(cluster)
            matched["matchedChord"] = match.get("name")
            matched["match"] = match
            matched_clusters.append(matched)

    observed_progression = [
        str(cluster.get("matchedChord"))
        for cluster in matched_clusters
    ]
    expected_progression = [str(name) for name in (fixture.get("expectedProgression") or [])]
    progression_score = progression_subsequence_score(
        observed_progression,
        expected_progression,
    )

    sustain_expected = {
        str(chord.get("name"))
        for chord in chords
        if bool(chord.get("expectsSustain"))
    }
    sustained_matches = [
        cluster
        for cluster in matched_clusters
        if str(cluster.get("matchedChord")) in sustain_expected
        and float(cluster.get("duration") or 0.0) >= minimum_sustain
    ]
    sustain_score = min(1.0, len(sustained_matches) / max(1, len(sustain_expected)))

    repeat_score, repeated_counts = repeated_attack_score(
        matched_clusters,
        minimum_attacks,
    )
    chord_vocabulary = sorted(set(observed_progression))
    vocabulary_score = len(chord_vocabulary) / max(1, len(chords))
    simultaneous_score = min(1.0, len(chord_clusters) / 8.0)

    full_song_duration = max(
        [event_end(event) for event in events] or [0.0]
    )
    timeline_score = 1.0 if full_song_duration >= 30.0 else min(1.0, full_song_duration / 30.0)

    score = round(
        100.0
        * (
            0.25 * vocabulary_score
            + 0.25 * progression_score
            + 0.20 * sustain_score
            + 0.15 * repeat_score
            + 0.10 * simultaneous_score
            + 0.05 * timeline_score
        ),
        2,
    )

    checks = {
        "fullSongTimeline": full_song_duration >= 30.0,
        "simultaneousChordClusters": len(chord_clusters) >= 8,
        "threeOrMoreChordTypes": len(chord_vocabulary) >= 3,
        "sustainEvidence": len(sustained_matches) >= 2,
        "repeatedChordAttacks": repeat_score > 0.0,
        "progressionEvidence": progression_score >= 0.4,
        "noSyntheticNotes": int(
            (
                (result.get("musicalUnderstanding") or {})
                .get("learnedVoicingTechniqueHandoff", {})
                .get("diagnostics", {})
                .get("syntheticNoteCount", 0)
            )
            or 0
        ) == 0,
    }

    return {
        "benchmarkVersion": 1,
        "benchmarkType": "gomyway-full-song-chord-structure-sustain-diagnostic",
        "engineVersion": result.get("engineVersion"),
        "instrumentSeparationMode": result.get("instrumentSeparationMode"),
        "voicingTechniqueHandoffMode": result.get("voicingTechniqueHandoffMode"),
        "eventCount": len(events),
        "fullSongDuration": round(full_song_duration, 4),
        "clusterCount": len(clusters),
        "chordClusterCount": len(chord_clusters),
        "matchedChordClusterCount": len(matched_clusters),
        "chordVocabulary": chord_vocabulary,
        "observedProgression": observed_progression,
        "expectedProgression": expected_progression,
        "repeatedAttackCounts": repeated_counts,
        "sustainedChordCount": len(sustained_matches),
        "scores": {
            "overall": score,
            "vocabulary": round(vocabulary_score, 4),
            "progression": round(progression_score, 4),
            "sustain": round(sustain_score, 4),
            "repeatedAttacks": round(repeat_score, 4),
            "simultaneousClusters": round(simultaneous_score, 4),
            "timeline": round(timeline_score, 4),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "matchedClusters": matched_clusters,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "diagnostic only: learn full chord structures and sustain without changing "
            "V71, V72, V73, or any of the seven locked baselines"
        ),
    }


@app.function(image=image, timeout=3600, memory=4096)
def run_benchmark(
    audio_bytes: bytes,
    audio_name: str,
    fixture: dict[str, Any],
) -> bytes:
    suffix = Path(audio_name).suffix or ".m4a"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as handle:
        handle.write(audio_bytes)
        audio_path = handle.name

    result = analyzer.analyze_audio_file(audio_path, "rhythm")
    report = evaluate(result, fixture)
    return json.dumps(
        report,
        default=json_default,
        separators=(",", ":"),
    ).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    report_output: str = "/tmp/gomyway-full-chord-sustain-report.json",
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
    )
    report = json.loads(bytes(report_bytes).decode("utf-8"))
    Path(report_output).write_text(
        json.dumps(report, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE FULL-SONG CHORD STRUCTURE & SUSTAIN BENCHMARK V1")
    print("=" * 72)
    print("Engine:", report.get("engineVersion"))
    print("Duration:", report.get("fullSongDuration"))
    print("Events:", report.get("eventCount"))
    print("Chord clusters:", report.get("chordClusterCount"))
    print("Matched chord clusters:", report.get("matchedChordClusterCount"))
    print("Chord vocabulary:", report.get("chordVocabulary"))
    print("Observed progression:", report.get("observedProgression"))
    print("Repeated attacks:", report.get("repeatedAttackCounts"))
    print("Sustained chords:", report.get("sustainedChordCount"))
    print("Scores:", report.get("scores"))
    print()
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, V73, and all seven locked baselines remain unchanged.")
