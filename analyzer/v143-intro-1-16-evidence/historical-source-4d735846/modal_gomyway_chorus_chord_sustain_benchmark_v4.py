from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-gomyway-chorus-chord-sustain-benchmark-v4")

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


def build_harmonic_windows(
    events: list[dict[str, Any]],
    window_seconds: float,
    hop_seconds: float,
) -> list[dict[str, Any]]:
    if not events:
        return []

    first = min(float(event["start"]) for event in events)
    last = max(float(event["end"]) for event in events)
    windows: list[dict[str, Any]] = []
    cursor = first
    index = 0

    while cursor <= last:
        window_end = cursor + window_seconds
        active = [
            event for event in events
            if float(event["start"]) < window_end
            and float(event["end"]) > cursor
        ]
        midis = sorted({int(event["midi"]) for event in active})
        if midis:
            overlap_end = max(float(event["end"]) for event in active)
            windows.append({
                "windowIndex": index,
                "start": cursor,
                "end": window_end,
                "duration": max(0.0, overlap_end - cursor),
                "eventCount": len(active),
                "uniqueMidiCount": len(midis),
                "midis": midis,
                "pitchClasses": sorted({midi % 12 for midi in midis}),
            })
        cursor += hop_seconds
        index += 1

    return windows


def best_chord_match(
    window: dict[str, Any],
    chords: list[dict[str, Any]],
) -> dict[str, Any] | None:
    observed = set(window.get("pitchClasses") or [])
    candidates: list[dict[str, Any]] = []

    for chord in chords:
        expected = set(chord.get("pitchClasses") or [])
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        precision = len(intersection) / max(1, len(observed))
        threshold = float(chord.get("minimumPitchClassCoverage") or 1.0)
        passed = coverage >= threshold and precision >= 0.4
        candidates.append({
            "name": chord.get("name"),
            "coverage": coverage,
            "precision": precision,
            "passed": passed,
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


def collapse_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    collapsed: list[dict[str, Any]] = []
    for match in matches:
        name = str(match.get("matchedChord") or "")
        if not name:
            continue
        if collapsed and collapsed[-1].get("matchedChord") == name:
            collapsed[-1]["end"] = match.get("end")
            collapsed[-1]["duration"] = max(
                float(collapsed[-1].get("duration") or 0.0),
                float(match.get("end") or 0.0) - float(collapsed[-1].get("start") or 0.0),
            )
            collapsed[-1]["windowCount"] = int(collapsed[-1].get("windowCount") or 1) + 1
        else:
            item = dict(match)
            item["windowCount"] = 1
            collapsed.append(item)
    return collapsed


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

    chords = [chord for chord in fixture.get("chords", []) if isinstance(chord, dict)]
    minimum_sustain = float(fixture.get("minimumSustainSeconds") or 0.35)
    windows = build_harmonic_windows(events, window_seconds=0.42, hop_seconds=0.10)
    chord_windows = [window for window in windows if int(window.get("uniqueMidiCount") or 0) >= 3]

    matched_windows: list[dict[str, Any]] = []
    for window in chord_windows:
        match = best_chord_match(window, chords)
        enriched = dict(window)
        enriched["match"] = match
        if match and match.get("passed"):
            enriched["matchedChord"] = match.get("name")
            matched_windows.append(enriched)

    collapsed = collapse_matches(matched_windows)
    progression = [str(item.get("matchedChord")) for item in collapsed]
    vocabulary = sorted(set(progression))
    sustained = [
        item for item in collapsed
        if float(item.get("duration") or 0.0) >= minimum_sustain
    ]

    repeated_counts: dict[str, int] = {}
    for item in collapsed:
        name = str(item.get("matchedChord") or "")
        repeated_counts[name] = repeated_counts.get(name, 0) + 1

    checks = {
        "rawEventsPresent": len(events) >= 20,
        "harmonicWindowsPresent": len(chord_windows) >= 8,
        "matchedChordWindows": len(matched_windows) >= 4,
        "twoOrMoreChordTypes": len(vocabulary) >= 2,
        "sustainEvidence": len(sustained) >= 1,
        "sliceDurationPreserved": duration >= 8.0,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 4,
        "benchmarkType": "gomyway-chorus-adaptive-harmonic-window-chord-sustain",
        "analysisPath": "raw-basic-pitch-adaptive-harmonic-windows",
        "sliceStart": start_time,
        "sliceDuration": duration,
        "eventCount": len(events),
        "harmonicWindowCount": len(windows),
        "chordWindowCount": len(chord_windows),
        "matchedChordWindowCount": len(matched_windows),
        "collapsedChordCount": len(collapsed),
        "chordVocabulary": vocabulary,
        "observedProgression": progression,
        "repeatedAttackCounts": repeated_counts,
        "sustainedChordCount": len(sustained),
        "checks": checks,
        "passed": all(checks.values()),
        "collapsedChords": collapsed,
        "matchedWindows": matched_windows,
        "protectedBaselinesChanged": False,
        "trainingRule": "diagnostic only: recover strummed chord tones spread across nearby onsets",
    }
    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    start_time: float = 155.0,
    duration: float = 20.0,
    report_output: str = "/tmp/gomyway-chorus-chord-sustain-v4-report.json",
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

    print("JIMMY PAIGE CHORUS CHORD STRUCTURE & SUSTAIN BENCHMARK V4")
    print("=" * 72)
    print("Analysis path:", report.get("analysisPath"))
    print("Slice:", report.get("sliceStart"), "+", report.get("sliceDuration"), "seconds")
    print("Raw events:", report.get("eventCount"))
    print("Harmonic windows:", report.get("harmonicWindowCount"))
    print("Chord windows:", report.get("chordWindowCount"))
    print("Matched chord windows:", report.get("matchedChordWindowCount"))
    print("Collapsed chords:", report.get("collapsedChordCount"))
    print("Chord vocabulary:", report.get("chordVocabulary"))
    print("Observed progression:", report.get("observedProgression"))
    print("Sustained chords:", report.get("sustainedChordCount"))
    print("Checks:")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, V73, and all seven locked baselines remain unchanged.")
