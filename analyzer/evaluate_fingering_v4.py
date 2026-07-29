#!/usr/bin/env python3
"""Evaluate fingering on a non-overlapping harmonic-window timeline."""

from __future__ import annotations

import statistics
from typing import Any

import evaluate_fingering_v3 as previous

legacy = previous.legacy
LOW_BASS_MIDI_MAX = previous.LOW_BASS_MIDI_MAX
LARGE_SHIFT_FRETS = previous.LARGE_SHIFT_FRETS
CHORD_ZONES = previous.CHORD_ZONES


def load_json(path: str) -> dict[str, Any]:
    return previous.load_json(path)


def _window_chord(window: dict[str, Any]) -> str:
    return previous._window_chord(window)


def _window_confidence(window: dict[str, Any]) -> float:
    chord = window.get("chord")
    values = [
        window.get("confidence"),
        window.get("chordConfidence"),
        chord.get("confidence") if isinstance(chord, dict) else None,
    ]
    for value in values:
        try:
            if value is not None:
                return float(value)
        except (TypeError, ValueError):
            continue
    return 0.0


def _canonical_segments(result: dict[str, Any]) -> list[dict[str, Any]]:
    understanding = result.get("musicalUnderstanding")
    windows = (
        understanding.get("harmonicWindows", [])
        if isinstance(understanding, dict)
        else []
    )

    usable: list[dict[str, Any]] = []
    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        chord = _window_chord(window)
        if chord not in CHORD_ZONES:
            continue
        start = float(window.get("start") or 0.0)
        end = float(window.get("end") or start)
        if end <= start:
            continue
        usable.append(
            {
                "sourceWindowIndex": index,
                "start": start,
                "end": end,
                "duration": end - start,
                "chord": chord,
                "confidence": _window_confidence(window),
                "chosenAnchor": window.get("chosenAnchor"),
            }
        )

    boundaries = sorted(
        {
            round(float(item[key]), 6)
            for item in usable
            for key in ("start", "end")
        }
    )

    raw_segments: list[dict[str, Any]] = []
    for start, end in zip(boundaries, boundaries[1:]):
        if end <= start:
            continue
        midpoint = (start + end) / 2.0
        active = [
            item
            for item in usable
            if item["start"] <= midpoint < item["end"]
        ]
        if not active:
            continue

        # Prefer the most specific window. Confidence and later source order
        # break ties without allowing a long parent window to double-score a
        # nested child window.
        winner = min(
            active,
            key=lambda item: (
                item["duration"],
                -item["confidence"],
                -item["sourceWindowIndex"],
            ),
        )
        raw_segments.append(
            {
                **winner,
                "start": start,
                "end": end,
                "overlapCandidateCount": len(active),
            }
        )

    merged: list[dict[str, Any]] = []
    for segment in raw_segments:
        if (
            merged
            and merged[-1]["chord"] == segment["chord"]
            and abs(float(merged[-1]["end"]) - float(segment["start"])) < 0.00001
            and merged[-1]["sourceWindowIndex"] == segment["sourceWindowIndex"]
        ):
            merged[-1]["end"] = segment["end"]
            merged[-1]["overlapCandidateCount"] = max(
                int(merged[-1]["overlapCandidateCount"]),
                int(segment["overlapCandidateCount"]),
            )
        else:
            merged.append(dict(segment))

    return merged


def _timeline_report(result: dict[str, Any]) -> dict[str, Any]:
    events = legacy.flatten_events(result)
    segments = _canonical_segments(result)

    scored: list[dict[str, Any]] = []
    high_failures = 0
    low_failures = 0
    open_failures = 0

    for index, segment in enumerate(segments):
        start = float(segment["start"])
        end = float(segment["end"])
        chord = str(segment["chord"])
        current = previous._events_in_window(events, start, end)
        center = legacy.median_upper_fret(current)
        lower, upper, allow_open = CHORD_ZONES[chord]
        open_upper = sum(
            1
            for event in current
            if (legacy.event_midi(event) or -999) > LOW_BASS_MIDI_MAX
            and legacy.event_fret(event) == 0
        )
        in_zone = center is None or lower <= center <= upper

        if center is not None and center > upper:
            high_failures += 1
        if center is not None and center < lower:
            low_failures += 1
        if open_upper and not allow_open:
            open_failures += 1

        scored.append(
            {
                "segmentIndex": index,
                "sourceWindowIndex": segment["sourceWindowIndex"],
                "start": round(start, 4),
                "end": round(end, 4),
                "chord": chord,
                "eventCount": len(current),
                "upperMedianFret": round(center, 2) if center is not None else None,
                "preferredRange": [lower, upper],
                "inPreferredZone": in_zone,
                "disallowedOpenUpperNotes": open_upper if not allow_open else 0,
                "overlapCandidateCount": segment["overlapCandidateCount"],
                "chosenAnchor": segment.get("chosenAnchor"),
            }
        )

    usable = [item for item in scored if item["upperMedianFret"] is not None]
    accuracy = (
        sum(1 for item in usable if item["inPreferredZone"]) / len(usable)
        if usable
        else 0.0
    )
    centers = [float(item["upperMedianFret"]) for item in usable]
    shifts = sum(
        1
        for first, second in zip(centers, centers[1:])
        if abs(second - first) >= LARGE_SHIFT_FRETS
    )

    score = 100.0
    score -= (1.0 - accuracy) * 70.0
    score -= high_failures * 3.0
    score -= low_failures * 3.0
    score -= open_failures * 7.0

    return {
        "benchmarkScore": round(max(0.0, min(100.0, score)), 2),
        "positionZoneAccuracy": round(accuracy, 4),
        "largeUpperPositionShifts": shifts,
        "unnecessaryOpenCollapses": open_failures,
        "highPositionOvercorrections": high_failures,
        "lowPositionUndercorrections": low_failures,
        "segmentCount": len(usable),
        "segments": scored,
    }


def evaluate(result: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    harmonic_report = previous.evaluate(result, fixture)
    timeline = _timeline_report(result)
    return {
        **harmonic_report,
        "overlappingWindowBenchmark": harmonic_report,
        "benchmarkScore": timeline["benchmarkScore"],
        "positionZoneAccuracy": timeline["positionZoneAccuracy"],
        "largeUpperPositionShifts": timeline["largeUpperPositionShifts"],
        "unnecessaryOpenCollapses": timeline["unnecessaryOpenCollapses"],
        "highPositionOvercorrections": timeline["highPositionOvercorrections"],
        "lowPositionUndercorrections": timeline["lowPositionUndercorrections"],
        "canonicalSegmentCount": timeline["segmentCount"],
        "canonicalSegments": timeline["segments"],
        "benchmarkMethod": "non-overlapping-harmonic-timeline-v4",
    }


def print_report(report: dict[str, Any]) -> None:
    overlapping = report.get("overlappingWindowBenchmark", {})
    legacy_report = report.get("legacyProgressBenchmark", {})

    print("\nJIMMY PAIGE NON-OVERLAPPING HARMONIC TIMELINE")
    print("=" * 64)
    print(f"Engine: {report.get('engineVersion')}")
    print(f"Timeline score: {report.get('benchmarkScore')}/100")
    print(f"Timeline segments: {report.get('canonicalSegmentCount')}")
    print(f"Timeline zone accuracy: {report.get('positionZoneAccuracy', 0) * 100:.1f}%")
    print(f"Timeline large shifts: {report.get('largeUpperPositionShifts')}")
    print(f"Timeline open collapses: {report.get('unnecessaryOpenCollapses')}")
    print(f"Timeline high corrections: {report.get('highPositionOvercorrections')}")
    print(f"Timeline low corrections: {report.get('lowPositionUndercorrections')}")
    print(
        "Overlapping-window score: "
        f"{overlapping.get('benchmarkScore')} (diagnostic only)"
    )
    print(
        "Legacy progress-slice score: "
        f"{legacy_report.get('benchmarkScore')} (historical only)"
    )

    print("\nCanonical harmonic timeline")
    for item in report.get("canonicalSegments", []):
        marker = "PASS" if item.get("inPreferredZone") else "FAIL"
        print(
            f"S{item.get('segmentIndex'):02d} {marker}  "
            f"{item.get('chord')}  "
            f"{item.get('start')}-{item.get('end')}  "
            f"median={item.get('upperMedianFret')}  "
            f"target={item.get('preferredRange')}  "
            f"open={item.get('disallowedOpenUpperNotes')}  "
            f"source=W{item.get('sourceWindowIndex')}"
        )
