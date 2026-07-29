#!/usr/bin/env python3
"""Evaluate analyzer JSON against a human-readable guitar fixture.

Usage:
    python analyzer/evaluate_fingering.py \
        --result /tmp/jimmy-result.json \
        --fixture analyzer/fixtures/stairway_intro_reference.json

The evaluator deliberately separates pitch detection from guitar fingering. Exact
note matches are scored only when the fixture contains trusted reference notes.
Position-zone, shift, open-collapse and playability metrics work immediately.
"""

from __future__ import annotations

import argparse
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
        if isinstance(candidate, list):
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


def assign_measure_numbers(
    events: list[dict[str, Any]],
    measure_count: int,
) -> list[dict[str, Any]]:
    if not events:
        return []

    starts = [event_start(event) for event in events]
    minimum = min(starts)
    maximum = max(starts)
    duration = max(0.001, maximum - minimum)

    assigned: list[dict[str, Any]] = []
    for event in events:
        item = dict(event)
        explicit = item.get("measure") or item.get("measureNumber")
        if explicit is not None:
            try:
                measure = int(explicit)
            except (TypeError, ValueError):
                measure = 1
        else:
            progress = (event_start(item) - minimum) / duration
            measure = min(measure_count, max(1, int(progress * measure_count) + 1))
        item["_benchmarkMeasure"] = measure
        assigned.append(item)
    return assigned


def median_upper_fret(events: Iterable[dict[str, Any]]) -> float | None:
    frets = [
        fret
        for event in events
        if (midi := event_midi(event)) is not None
        and midi > LOW_BASS_MIDI_MAX
        and (fret := event_fret(event)) is not None
        and fret > 0
    ]
    return float(statistics.median(frets)) if frets else None


def count_large_upper_shifts(events: list[dict[str, Any]]) -> int:
    ordered = sorted(events, key=event_start)
    centers: list[float] = []
    for measure in sorted({int(item["_benchmarkMeasure"]) for item in ordered}):
        center = median_upper_fret(
            item for item in ordered if int(item["_benchmarkMeasure"]) == measure
        )
        if center is not None:
            centers.append(center)
    return sum(
        1 for first, second in zip(centers, centers[1:])
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
            "message": "No trusted exact note assignments are present in the fixture yet.",
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


def evaluate(
    result: dict[str, Any],
    fixture: dict[str, Any],
) -> dict[str, Any]:
    events = flatten_events(result)
    measure_expectations = list(fixture.get("measureExpectations") or [])
    measure_count = max(1, len(measure_expectations))
    events = assign_measure_numbers(events, measure_count)

    measure_scores: list[dict[str, Any]] = []
    unnecessary_open_collapses = 0
    high_position_overcorrections = 0

    for expectation in measure_expectations:
        measure = int(expectation["measure"])
        current = [
            event for event in events
            if int(event.get("_benchmarkMeasure") or 0) == measure
        ]
        center = median_upper_fret(current)
        lower = float(expectation.get("preferredUpperFretMin", 0))
        upper = float(expectation.get("preferredUpperFretMax", 24))
        open_upper = sum(
            1 for event in current
            if (event_midi(event) or -999) > LOW_BASS_MIDI_MAX
            and event_fret(event) == 0
        )
        allow_open = bool(expectation.get("allowOpenUpperStrings", False))
        if open_upper and not allow_open:
            unnecessary_open_collapses += 1

        in_zone = center is None or lower <= center <= upper
        if center is not None and center > upper:
            high_position_overcorrections += 1

        measure_scores.append(
            {
                "measure": measure,
                "eventCount": len(current),
                "upperMedianFret": round(center, 2) if center is not None else None,
                "preferredRange": [lower, upper],
                "inPreferredZone": in_zone,
                "disallowedOpenUpperNotes": open_upper if not allow_open else 0,
            }
        )

    zone_measures = [item for item in measure_scores if item["upperMedianFret"] is not None]
    zone_accuracy = (
        sum(1 for item in zone_measures if item["inPreferredZone"]) / len(zone_measures)
        if zone_measures
        else 0.0
    )
    large_shifts = count_large_upper_shifts(events)

    global_expectations = dict(fixture.get("globalExpectations") or {})
    max_shifts = int(global_expectations.get("maxLargeUpperPositionShifts", 999))
    max_collapses = int(global_expectations.get("maxUnnecessaryOpenCollapses", 999))

    exact = exact_note_metrics(
        events,
        list(fixture.get("notes") or []),
        float(fixture.get("timingToleranceSeconds") or 0.12),
    )

    score = 100.0
    score -= (1.0 - zone_accuracy) * 45.0
    score -= max(0, large_shifts - max_shifts) * 8.0
    score -= max(0, unnecessary_open_collapses - max_collapses) * 10.0
    score -= high_position_overcorrections * 4.0
    if exact.get("exactStringFretAccuracy") is not None:
        score = score * 0.6 + float(exact["exactStringFretAccuracy"]) * 100.0 * 0.4

    return {
        "fixture": fixture.get("name"),
        "engineVersion": result.get("engineVersion"),
        "eventCount": len(events),
        "benchmarkScore": round(max(0.0, min(100.0, score)), 2),
        "positionZoneAccuracy": round(zone_accuracy, 4),
        "largeUpperPositionShifts": large_shifts,
        "unnecessaryOpenCollapses": unnecessary_open_collapses,
        "highPositionOvercorrections": high_position_overcorrections,
        "exactNoteMetrics": exact,
        "measures": measure_scores,
    }


def print_report(report: dict[str, Any]) -> None:
    print("\nJIMMY PAIGE BENCHMARK")
    print("=" * 56)
    print(f"Engine: {report.get('engineVersion')}")
    print(f"Score: {report['benchmarkScore']}/100")
    print(f"Events evaluated: {report['eventCount']}")
    print(f"Position-zone accuracy: {report['positionZoneAccuracy'] * 100:.1f}%")
    print(f"Large upper-position shifts: {report['largeUpperPositionShifts']}")
    print(f"Unnecessary open collapses: {report['unnecessaryOpenCollapses']}")
    print(f"High-position overcorrections: {report['highPositionOvercorrections']}")

    exact = report["exactNoteMetrics"]
    if exact.get("exactStringFretAccuracy") is None:
        print("Exact string/fret accuracy: waiting for trusted fixture notes")
    else:
        print(
            "Exact string/fret accuracy: "
            f"{float(exact['exactStringFretAccuracy']) * 100:.1f}%"
        )

    print("\nPer-measure upper-hand position")
    for item in report["measures"]:
        marker = "PASS" if item["inPreferredZone"] else "FAIL"
        print(
            f"M{item['measure']:02d} {marker}  "
            f"median={item['upperMedianFret']}  "
            f"target={item['preferredRange']}  "
            f"events={item['eventCount']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--result", required=True, help="Analyzer result JSON file")
    parser.add_argument("--fixture", required=True, help="Benchmark fixture JSON file")
    parser.add_argument("--output", help="Optional path for the report JSON")
    args = parser.parse_args()

    report = evaluate(load_json(args.result), load_json(args.fixture))
    print_report(report)
    if args.output:
        Path(args.output).write_text(
            json.dumps(report, indent=2, sort_keys=True),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
