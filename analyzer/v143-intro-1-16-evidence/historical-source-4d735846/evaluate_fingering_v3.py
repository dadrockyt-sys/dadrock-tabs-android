#!/usr/bin/env python3
"""Evaluate fingering against analyzer harmonic windows and retain the legacy score."""

from __future__ import annotations

import statistics
from typing import Any

import evaluate_fingering_v2 as legacy

LOW_BASS_MIDI_MAX = legacy.LOW_BASS_MIDI_MAX
LARGE_SHIFT_FRETS = legacy.LARGE_SHIFT_FRETS

CHORD_ZONES: dict[str, tuple[float, float, bool]] = {
    "Am": (5.0, 7.0, False),
    "C/G": (5.0, 8.0, False),
    "D/F#": (2.0, 4.0, False),
    "D/F♯": (2.0, 4.0, False),
    "Fmaj7": (0.0, 3.0, True),
    "G/B-Am": (0.0, 3.0, True),
    "G/B - Am": (0.0, 3.0, True),
}


def load_json(path: str) -> dict[str, Any]:
    return legacy.load_json(path)


def _events_in_window(
    events: list[dict[str, Any]],
    start: float,
    end: float,
) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if start <= legacy.event_start(event) < end
    ]


def _window_chord(window: dict[str, Any]) -> str:
    chord = window.get("chord")
    if isinstance(chord, dict):
        return str(chord.get("name") or "")
    return str(chord or "")


def _aligned_report(result: dict[str, Any]) -> dict[str, Any]:
    events = legacy.flatten_events(result)
    understanding = result.get("musicalUnderstanding")
    windows = (
        understanding.get("harmonicWindows", [])
        if isinstance(understanding, dict)
        else []
    )

    scored_windows: list[dict[str, Any]] = []
    high_failures = 0
    low_failures = 0
    open_failures = 0

    for index, window in enumerate(windows):
        if not isinstance(window, dict):
            continue
        chord = _window_chord(window)
        zone = CHORD_ZONES.get(chord)
        if zone is None:
            continue
        start = float(window.get("start") or 0.0)
        end = float(window.get("end") or start + 0.001)
        current = _events_in_window(events, start, end)
        center = legacy.median_upper_fret(current)
        lower, upper, allow_open = zone
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

        scored_windows.append(
            {
                "windowIndex": index,
                "start": round(start, 4),
                "end": round(end, 4),
                "chord": chord,
                "eventCount": len(current),
                "upperMedianFret": round(center, 2) if center is not None else None,
                "preferredRange": [lower, upper],
                "inPreferredZone": in_zone,
                "disallowedOpenUpperNotes": open_upper if not allow_open else 0,
            }
        )

    usable = [item for item in scored_windows if item["upperMedianFret"] is not None]
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
        "windowCount": len(usable),
        "windows": scored_windows,
    }


def evaluate(result: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    legacy_report = legacy.evaluate(result, fixture)
    aligned = _aligned_report(result)

    return {
        **legacy_report,
        "legacyProgressBenchmark": legacy_report,
        "benchmarkScore": aligned["benchmarkScore"],
        "positionZoneAccuracy": aligned["positionZoneAccuracy"],
        "largeUpperPositionShifts": aligned["largeUpperPositionShifts"],
        "unnecessaryOpenCollapses": aligned["unnecessaryOpenCollapses"],
        "highPositionOvercorrections": aligned["highPositionOvercorrections"],
        "lowPositionUndercorrections": aligned["lowPositionUndercorrections"],
        "alignedWindowCount": aligned["windowCount"],
        "alignedWindows": aligned["windows"],
        "benchmarkMethod": "harmonic-window-aligned-v3",
    }


def print_report(report: dict[str, Any]) -> None:
    legacy_report = report.get("legacyProgressBenchmark", {})
    print("\nJIMMY PAIGE HARMONIC-WINDOW BENCHMARK")
    print("=" * 60)
    print(f"Engine: {report.get('engineVersion')}")
    print(f"Aligned score: {report.get('benchmarkScore')}/100")
    print(f"Aligned windows: {report.get('alignedWindowCount')}")
    print(f"Aligned zone accuracy: {report.get('positionZoneAccuracy', 0) * 100:.1f}%")
    print(f"Aligned large shifts: {report.get('largeUpperPositionShifts')}")
    print(f"Aligned open collapses: {report.get('unnecessaryOpenCollapses')}")
    print(f"Aligned high corrections: {report.get('highPositionOvercorrections')}")
    print(f"Aligned low corrections: {report.get('lowPositionUndercorrections')}")
    print(
        "Legacy progress-slice score: "
        f"{legacy_report.get('benchmarkScore')} "
        "(retained only for historical comparison)"
    )

    print("\nHarmonic windows")
    for item in report.get("alignedWindows", []):
        marker = "PASS" if item.get("inPreferredZone") else "FAIL"
        print(
            f"W{item.get('windowIndex'):02d} {marker}  "
            f"{item.get('chord')}  "
            f"{item.get('start')}-{item.get('end')}  "
            f"median={item.get('upperMedianFret')}  "
            f"target={item.get('preferredRange')}  "
            f"open={item.get('disallowedOpenUpperNotes')}"
        )
