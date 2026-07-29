#!/usr/bin/env python3
"""Evaluate guitar fingering against phrase-accurate position segments."""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any, Iterable

LOW_BASS_MIDI_MAX = 43
LARGE_SHIFT_FRETS = 5.0


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def flatten_events(result: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = (
        result.get("events"),
        result.get("tabEvents"),
        result.get("notes"),
        result.get("transcription", {}).get("events")
        if isinstance(result.get("transcription"), dict)
        else None,
    )
    for candidate in candidates:
        if not isinstance(candidate, list):
            continue
        flat: list[dict[str, Any]] = []
        for item in candidate:
            if isinstance(item, dict):
                flat.append(dict(item))
            elif isinstance(item, list):
                flat.extend(dict(value) for value in item if isinstance(value, dict))
        if flat:
            return flat
    return []


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_midi(event: dict[str, Any]) -> int | None:
    value = event.get("midi")
    if value is None:
        value = event.get("pitch")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def event_fret(event: dict[str, Any]) -> int | None:
    try:
        return int(event["fret"])
    except (KeyError, TypeError, ValueError):
        return None


def event_string(event: dict[str, Any]) -> int | None:
    for key in ("stringIndex", "string_index", "string"):
        if key in event:
            try:
                return int(event[key])
            except (TypeError, ValueError):
                return None
    return None


def median_upper_fret(events: Iterable[dict[str, Any]]) -> float | None:
    frets = [
        fret
        for event in events
        if (midi := event_midi(event)) is not None
        and midi > LOW_BASS_MIDI_MAX
        and (fret := event_fret(event)) is not None
    ]
    return float(statistics.median(frets)) if frets else None


def timeline_bounds(events: list[dict[str, Any]]) -> tuple[float, float]:
    starts = [event_start(event) for event in events]
    if not starts:
        return 0.0, 1.0
    minimum = min(starts)
    maximum = max(starts)
    return minimum, max(minimum + 0.001, maximum)


def events_for_segment(
    events: list[dict[str, Any]],
    minimum: float,
    maximum: float,
    segment: dict[str, Any],
) -> list[dict[str, Any]]:
    duration = maximum - minimum
    start = minimum + duration * float(segment["startProgress"])
    end = minimum + duration * float(segment["endProgress"])
    include_end = float(segment["endProgress"]) >= 1.0
    return [
        event
        for event in events
        if event_start(event) >= start
        and (event_start(event) <= end if include_end else event_start(event) < end)
    ]


def count_large_segment_shifts(segment_scores: list[dict[str, Any]]) -> int:
    centers = [
        float(item["upperMedianFret"])
        for item in segment_scores
        if item.get("upperMedianFret") is not None
    ]
    return sum(
        1
        for first, second in zip(centers, centers[1:])
        if abs(second - first) >= LARGE_SHIFT_FRETS
    )


def exact_note_metrics(
    events: list[dict[str, Any]],
    references: list[dict[str, Any]],
    tolerance: float,
) -> dict[str, Any]:
    if not references:
        return {
            "referenceNoteCount": 0,
            "pitchRecall": None,
            "exactStringFretAccuracy": None,
            "message": "No trusted timed note assignments are present yet.",
        }

    unmatched = set(range(len(events)))
    pitch_hits = 0
    exact_hits = 0
    for reference in references:
        ref_start = float(reference.get("start") or 0.0)
        ref_midi = int(reference["midi"])
        best_index = None
        best_distance = math.inf
        for index in unmatched:
            event = events[index]
            if event_midi(event) != ref_midi:
                continue
            distance = abs(event_start(event) - ref_start)
            if distance <= tolerance and distance < best_distance:
                best_index = index
                best_distance = distance
        if best_index is None:
            continue
        unmatched.remove(best_index)
        pitch_hits += 1
        event = events[best_index]
        if (
            event_string(event) == int(reference.get("stringIndex", -999))
            and event_fret(event) == int(reference.get("fret", -999))
        ):
            exact_hits += 1

    total = len(references)
    return {
        "referenceNoteCount": total,
        "pitchRecall": round(pitch_hits / total, 4),
        "exactStringFretAccuracy": round(exact_hits / total, 4),
    }


def evaluate(result: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    events = flatten_events(result)
    minimum, maximum = timeline_bounds(events)
    segments = list(fixture.get("positionSegments") or [])

    segment_scores: list[dict[str, Any]] = []
    open_failures = 0
    high_failures = 0
    low_failures = 0

    for segment in segments:
        current = events_for_segment(events, minimum, maximum, segment)
        center = median_upper_fret(current)
        lower = float(segment.get("preferredUpperFretMin", 0))
        upper = float(segment.get("preferredUpperFretMax", 24))
        allow_open = bool(segment.get("allowOpenUpperStrings", False))
        open_upper = sum(
            1
            for event in current
            if (event_midi(event) or -999) > LOW_BASS_MIDI_MAX
            and event_fret(event) == 0
        )
        if open_upper and not allow_open:
            open_failures += 1

        in_zone = center is None or lower <= center <= upper
        if center is not None and center > upper:
            high_failures += 1
        if center is not None and center < lower:
            low_failures += 1

        segment_scores.append(
            {
                "segment": segment.get("segment"),
                "measure": segment.get("measure"),
                "chord": segment.get("chord"),
                "eventCount": len(current),
                "upperMedianFret": round(center, 2) if center is not None else None,
                "preferredRange": [lower, upper],
                "inPreferredZone": in_zone,
                "allowOpenUpperStrings": allow_open,
                "disallowedOpenUpperNotes": open_upper if not allow_open else 0,
            }
        )

    scored = [item for item in segment_scores if item["upperMedianFret"] is not None]
    zone_accuracy = (
        sum(1 for item in scored if item["inPreferredZone"]) / len(scored)
        if scored
        else 0.0
    )
    large_shifts = count_large_segment_shifts(segment_scores)
    expected_shifts = int(fixture.get("globalExpectations", {}).get("expectedLargePositionShifts", 0))
    shift_error = abs(large_shifts - expected_shifts)

    exact = exact_note_metrics(
        events,
        list(fixture.get("notes") or []),
        float(fixture.get("timingToleranceSeconds") or 0.12),
    )

    score = 100.0
    score -= (1.0 - zone_accuracy) * 55.0
    score -= open_failures * 7.0
    score -= high_failures * 3.0
    score -= low_failures * 3.0
    score -= shift_error * 4.0
    if exact.get("exactStringFretAccuracy") is not None:
        score = score * 0.65 + float(exact["exactStringFretAccuracy"]) * 100.0 * 0.35

    return {
        "fixture": fixture.get("name"),
        "fixtureVersion": fixture.get("fixtureVersion"),
        "engineVersion": result.get("engineVersion"),
        "eventCount": len(events),
        "benchmarkScore": round(max(0.0, min(100.0, score)), 2),
        "positionZoneAccuracy": round(zone_accuracy, 4),
        "largeUpperPositionShifts": large_shifts,
        "expectedLargePositionShifts": expected_shifts,
        "shiftCountError": shift_error,
        "unnecessaryOpenCollapses": open_failures,
        "highPositionOvercorrections": high_failures,
        "lowPositionUndercorrections": low_failures,
        "exactNoteMetrics": exact,
        "segments": segment_scores,
    }


def print_report(report: dict[str, Any]) -> None:
    print("\nJIMMY PAIGE PHRASE BENCHMARK")
    print("=" * 60)
    print(f"Fixture version: {report.get('fixtureVersion')}")
    print(f"Engine: {report.get('engineVersion')}")
    print(f"Score: {report['benchmarkScore']}/100")
    print(f"Events evaluated: {report['eventCount']}")
    print(f"Position-zone accuracy: {report['positionZoneAccuracy'] * 100:.1f}%")
    print(
        "Large position shifts: "
        f"{report['largeUpperPositionShifts']} "
        f"(expected {report['expectedLargePositionShifts']})"
    )
    print(f"Unnecessary open collapses: {report['unnecessaryOpenCollapses']}")
    print(f"High-position overcorrections: {report['highPositionOvercorrections']}")
    print(f"Low-position undercorrections: {report['lowPositionUndercorrections']}")

    print("\nPhrase-position segments")
    for item in report["segments"]:
        marker = "PASS" if item["inPreferredZone"] else "FAIL"
        print(
            f"{item['segment']} {marker}  "
            f"M{item['measure']} {item.get('chord') or ''}  "
            f"median={item['upperMedianFret']}  "
            f"target={item['preferredRange']}  "
            f"open={item['disallowedOpenUpperNotes']}"
        )
