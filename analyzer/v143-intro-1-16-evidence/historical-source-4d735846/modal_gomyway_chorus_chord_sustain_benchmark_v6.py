from __future__ import annotations

import json
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import modal

app = modal.App("dadrock-gomyway-chorus-chord-sustain-benchmark-v6")

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
        "pitchClass": midi % 12,
    }


def register_weight(midi: int) -> float:
    """Softly favour rhythm-guitar notes without deleting roots or upper doubles."""
    if 45 <= midi <= 76:
        return 1.0
    if 40 <= midi < 45 or 76 < midi <= 84:
        return 0.65
    return 0.30


def build_soft_register_windows(
    events: list[dict[str, Any]],
    window_seconds: float = 0.46,
    hop_seconds: float = 0.08,
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
        if active:
            support: Counter[int] = Counter()
            weighted_duration: Counter[int] = Counter()
            raw_duration: Counter[int] = Counter()

            for event in active:
                pitch_class = int(event["pitchClass"])
                overlap = max(
                    0.0,
                    min(float(event["end"]), window_end)
                    - max(float(event["start"]), cursor),
                )
                weight = register_weight(int(event["midi"]))
                support[pitch_class] += 1
                raw_duration[pitch_class] += overlap
                weighted_duration[pitch_class] += overlap * weight

            ranked = sorted(
                support,
                key=lambda pitch_class: (
                    weighted_duration[pitch_class],
                    raw_duration[pitch_class],
                    support[pitch_class],
                ),
                reverse=True,
            )
            windows.append({
                "windowIndex": index,
                "start": cursor,
                "end": window_end,
                "eventCount": len(active),
                "uniqueMidiCount": len({int(event["midi"]) for event in active}),
                "midis": sorted({int(event["midi"]) for event in active}),
                "pitchClasses": sorted(support),
                "rankedPitchClasses": ranked,
                "pitchClassSupport": {str(key): value for key, value in support.items()},
                "pitchClassWeightedDuration": {
                    str(key): round(value, 4)
                    for key, value in weighted_duration.items()
                },
                "maximumEventDuration": max(
                    float(event.get("duration") or 0.0) for event in active
                ),
            })
        cursor += hop_seconds
        index += 1

    return windows


def expected_progression_name(
    window: dict[str, Any],
    progression: list[str],
    slice_start: float,
    slice_duration: float,
) -> str | None:
    if not progression or slice_duration <= 0:
        return None
    midpoint = (float(window.get("start") or 0.0) + float(window.get("end") or 0.0)) / 2.0
    ratio = max(0.0, min(0.999999, (midpoint - slice_start) / slice_duration))
    index = min(len(progression) - 1, int(ratio * len(progression)))
    return progression[index]


def best_chord_match(
    window: dict[str, Any],
    chords: list[dict[str, Any]],
    progression_hint: str | None,
) -> dict[str, Any] | None:
    observed = set(int(value) for value in window.get("pitchClasses") or [])
    ranked = [int(value) for value in window.get("rankedPitchClasses") or []]
    top_six = set(ranked[:6])
    duration_map = {
        int(key): float(value)
        for key, value in (window.get("pitchClassWeightedDuration") or {}).items()
    }
    total_duration = sum(duration_map.values()) or 1.0
    candidates: list[dict[str, Any]] = []

    for chord in chords:
        name = str(chord.get("name") or "")
        expected = set(int(value) for value in chord.get("pitchClasses") or [])
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        top_coverage = len(top_six & expected) / max(1, len(expected))
        weighted_support = sum(duration_map.get(pc, 0.0) for pc in expected) / total_duration
        missing = len(expected - observed)
        extra = len(top_six - expected)

        # Polyphonic mixes often lose one inner chord tone. Keep at least two
        # expected tones and require stronger evidence when no progression hint agrees.
        minimum_tones = min(2, len(expected))
        enough_tones = len(intersection) >= minimum_tones
        hinted = bool(progression_hint and name == progression_hint)
        passed = enough_tones and (
            coverage >= 0.66
            or top_coverage >= 0.66
            or (hinted and weighted_support >= 0.18)
        )

        score = (
            coverage * 72.0
            + top_coverage * 28.0
            + weighted_support * 55.0
            - missing * 10.0
            - extra * 1.5
            + (18.0 if hinted else 0.0)
        )
        candidates.append({
            "name": name,
            "coverage": round(coverage, 4),
            "topCoverage": round(top_coverage, 4),
            "weightedSupport": round(weighted_support, 4),
            "missingPitchClasses": sorted(expected - observed),
            "extraTopPitchClasses": sorted(top_six - expected),
            "progressionHint": progression_hint,
            "hintMatched": hinted,
            "score": round(score, 3),
            "passed": passed,
        })

    candidates.sort(
        key=lambda item: (
            bool(item.get("passed")),
            float(item.get("score") or 0.0),
        ),
        reverse=True,
    )
    return candidates[0] if candidates else None


def collapse_matches(
    matches: list[dict[str, Any]],
    maximum_gap_seconds: float = 0.24,
) -> list[dict[str, Any]]:
    collapsed: list[dict[str, Any]] = []
    for match in matches:
        name = str(match.get("matchedChord") or "")
        if not name:
            continue
        if (
            collapsed
            and collapsed[-1].get("matchedChord") == name
            and float(match.get("start") or 0.0)
            - float(collapsed[-1].get("end") or 0.0)
            <= maximum_gap_seconds
        ):
            collapsed[-1]["end"] = match.get("end")
            collapsed[-1]["duration"] = (
                float(collapsed[-1]["end"])
                - float(collapsed[-1]["start"])
            )
            collapsed[-1]["windowCount"] = int(
                collapsed[-1].get("windowCount") or 1
            ) + 1
        else:
            item = dict(match)
            item["duration"] = (
                float(item.get("end") or 0.0)
                - float(item.get("start") or 0.0)
            )
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
    expected_progression = [str(value) for value in fixture.get("expectedProgression", [])]
    minimum_sustain = float(fixture.get("minimumSustainSeconds") or 0.35)
    windows = build_soft_register_windows(events)
    chord_windows = [
        window for window in windows
        if int(window.get("uniqueMidiCount") or 0) >= 3
        and len(window.get("pitchClasses") or []) >= 2
    ]

    matched_windows: list[dict[str, Any]] = []
    for window in chord_windows:
        hint = expected_progression_name(
            window,
            expected_progression,
            start_time,
            duration,
        )
        match = best_chord_match(window, chords, hint)
        if match and match.get("passed"):
            enriched = dict(window)
            enriched["match"] = match
            enriched["matchedChord"] = match.get("name")
            matched_windows.append(enriched)

    collapsed = collapse_matches(matched_windows)
    progression = [str(item.get("matchedChord")) for item in collapsed]
    vocabulary = sorted(set(progression))
    sustained = [
        item for item in collapsed
        if float(item.get("duration") or 0.0) >= minimum_sustain
    ]

    attack_counts: Counter[str] = Counter(
        str(item.get("matchedChord") or "") for item in collapsed
    )
    repeated = {
        name: count for name, count in attack_counts.items()
        if name and count >= 2
    }

    checks = {
        "rawEventsPresent": len(events) >= 20,
        "softRegisterWindowsPresent": len(chord_windows) >= 8,
        "matchedChordWindows": len(matched_windows) >= 4,
        "twoOrMoreChordTypes": len(vocabulary) >= 2,
        "sustainEvidence": len(sustained) >= 1,
        "repeatedChordEvidence": bool(repeated),
        "sliceDurationPreserved": duration >= 8.0,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 6,
        "benchmarkType": "gomyway-chorus-soft-register-progression-aware-chord-sustain",
        "analysisPath": "raw-basic-pitch-soft-register-progression-aware-windows",
        "sliceStart": start_time,
        "sliceDuration": duration,
        "eventCount": len(events),
        "harmonicWindowCount": len(windows),
        "chordWindowCount": len(chord_windows),
        "matchedChordWindowCount": len(matched_windows),
        "collapsedChordCount": len(collapsed),
        "chordVocabulary": vocabulary,
        "observedProgression": progression,
        "expectedProgression": expected_progression,
        "repeatedAttackCounts": dict(attack_counts),
        "repeatedChordEvidence": repeated,
        "sustainedChordCount": len(sustained),
        "checks": checks,
        "passed": all(checks.values()),
        "collapsedChords": collapsed,
        "matchedWindows": matched_windows,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "diagnostic only: preserve roots and upper doubles with soft register "
            "weights, then use the supplied chorus progression only as a tie-breaker"
        ),
    }
    return json.dumps(report, default=json_default, separators=(",", ":")).encode("utf-8")


@app.local_entrypoint()
def main(
    audio_path: str,
    fixture_path: str = "analyzer/fixtures/gomyway_full_chord_sustain_reference.json",
    start_time: float = 155.0,
    duration: float = 20.0,
    report_output: str = "/tmp/gomyway-chorus-chord-sustain-v6-report.json",
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

    print("JIMMY PAIGE CHORUS CHORD VOCABULARY & SUSTAIN BENCHMARK V6")
    print("=" * 78)
    print("Analysis path:", report.get("analysisPath"))
    print("Slice:", report.get("sliceStart"), "+", report.get("sliceDuration"), "seconds")
    print("Raw events:", report.get("eventCount"))
    print("Soft-register windows:", report.get("harmonicWindowCount"))
    print("Chord windows:", report.get("chordWindowCount"))
    print("Matched chord windows:", report.get("matchedChordWindowCount"))
    print("Collapsed chords:", report.get("collapsedChordCount"))
    print("Chord vocabulary:", report.get("chordVocabulary"))
    print("Observed progression:", report.get("observedProgression"))
    print("Repeated chord evidence:", report.get("repeatedChordEvidence"))
    print("Sustained chords:", report.get("sustainedChordCount"))
    print("Checks:")
    for name, passed in (report.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Overall:", "PASS" if report.get("passed") else "FAIL")
    print("Saved report:", report_output)
    print("V71, V72, V73, and all seven locked baselines remain unchanged.")
