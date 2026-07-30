#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_PROJECTION = Path("/tmp/gomyway-full-song-v7-notation-metadata.json")
DEFAULT_OUTPUT = Path("/tmp/gomyway-full-song-v7-measure-grid.json")
DEFAULT_BPM = 129.0
DEFAULT_BEATS_PER_MEASURE = 4
DEFAULT_MEASURES_PER_ROW = 6


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def number(value: Any) -> float:
    return float(value or 0.0)


def rounded(value: Any, digits: int = 6) -> float:
    return round(number(value), digits)


def musical_position(
    seconds: float,
    *,
    beat_seconds: float,
    measure_seconds: float,
    measures_per_row: int,
) -> dict[str, Any]:
    safe_seconds = max(0.0, seconds)
    zero_measure = int(math.floor(safe_seconds / measure_seconds))
    within_measure = safe_seconds - zero_measure * measure_seconds
    beat_zero = min(3, int(math.floor(within_measure / beat_seconds)))
    within_beat = within_measure - beat_zero * beat_seconds
    row_zero = zero_measure // measures_per_row
    measure_in_row_zero = zero_measure % measures_per_row
    measure_ratio = min(1.0, max(0.0, within_measure / measure_seconds))
    row_ratio = (measure_in_row_zero + measure_ratio) / measures_per_row

    return {
        "measureNumber": zero_measure + 1,
        "beatNumber": beat_zero + 1,
        "beatFraction": round(min(0.999999, max(0.0, within_beat / beat_seconds)), 6),
        "measureRatio": round(measure_ratio, 6),
        "rowNumber": row_zero + 1,
        "measureInRow": measure_in_row_zero + 1,
        "rowRatio": round(min(1.0, max(0.0, row_ratio)), 6),
    }


def split_marker(
    marker: dict[str, Any],
    *,
    song_duration: float,
    beat_seconds: float,
    measure_seconds: float,
    measures_per_row: int,
) -> list[dict[str, Any]]:
    start = max(0.0, min(song_duration, number(marker.get("start"))))
    end = max(start, min(song_duration, number(marker.get("end"))))
    is_span = end > start + 0.000001

    start_measure_zero = int(math.floor(start / measure_seconds))
    end_probe = max(start, end - 0.000001) if is_span else start
    end_measure_zero = int(math.floor(end_probe / measure_seconds))

    fragments: list[dict[str, Any]] = []
    for measure_zero in range(start_measure_zero, end_measure_zero + 1):
        measure_start = measure_zero * measure_seconds
        measure_end = min(song_duration, measure_start + measure_seconds)
        fragment_start = max(start, measure_start)
        fragment_end = min(end, measure_end) if is_span else fragment_start
        start_position = musical_position(
            fragment_start,
            beat_seconds=beat_seconds,
            measure_seconds=measure_seconds,
            measures_per_row=measures_per_row,
        )
        end_position = musical_position(
            fragment_end,
            beat_seconds=beat_seconds,
            measure_seconds=measure_seconds,
            measures_per_row=measures_per_row,
        )
        measure_in_row_zero = measure_zero % measures_per_row
        local_start_ratio = max(0.0, min(1.0, (fragment_start - measure_start) / measure_seconds))
        local_end_ratio = (
            max(local_start_ratio, min(1.0, (fragment_end - measure_start) / measure_seconds))
            if is_span
            else local_start_ratio
        )
        row_start_ratio = (measure_in_row_zero + local_start_ratio) / measures_per_row
        row_end_ratio = (measure_in_row_zero + local_end_ratio) / measures_per_row

        fragments.append({
            "fragmentIndex": len(fragments),
            "measureNumber": measure_zero + 1,
            "rowNumber": measure_zero // measures_per_row + 1,
            "measureInRow": measure_in_row_zero + 1,
            "start": round(fragment_start, 6),
            "end": round(fragment_end, 6),
            "startBeat": start_position["beatNumber"],
            "startBeatFraction": start_position["beatFraction"],
            "endBeat": end_position["beatNumber"],
            "endBeatFraction": end_position["beatFraction"],
            "measureStartRatio": round(local_start_ratio, 6),
            "measureEndRatio": round(local_end_ratio, 6),
            "rowStartRatio": round(row_start_ratio, 6),
            "rowEndRatio": round(row_end_ratio, 6),
            "continuesFromPreviousMeasure": measure_zero > start_measure_zero,
            "continuesIntoNextMeasure": measure_zero < end_measure_zero,
            "readOnly": True,
        })

    return fragments


def build_measure_grid(
    projection: dict[str, Any],
    *,
    bpm: float,
    beats_per_measure: int,
    measures_per_row: int,
) -> dict[str, Any]:
    if bpm <= 0:
        raise ValueError("bpm must be positive")
    if beats_per_measure <= 0:
        raise ValueError("beats_per_measure must be positive")
    if measures_per_row <= 0:
        raise ValueError("measures_per_row must be positive")

    song_duration = number(projection.get("songDuration"))
    beat_seconds = 60.0 / bpm
    measure_seconds = beat_seconds * beats_per_measure
    measure_count = int(math.ceil(song_duration / measure_seconds)) if song_duration else 0
    row_count = int(math.ceil(measure_count / measures_per_row)) if measure_count else 0

    source_markers = [
        marker
        for marker in ((projection.get("notationMetadata") or {}).get("allMarkers") or [])
        if isinstance(marker, dict)
    ]

    markers: list[dict[str, Any]] = []
    all_fragments: list[dict[str, Any]] = []
    for marker_index, marker in enumerate(source_markers):
        start = max(0.0, min(song_duration, number(marker.get("start"))))
        end = max(start, min(song_duration, number(marker.get("end"))))
        fragments = split_marker(
            marker,
            song_duration=song_duration,
            beat_seconds=beat_seconds,
            measure_seconds=measure_seconds,
            measures_per_row=measures_per_row,
        )
        projected = dict(marker)
        projected.update({
            "measureGridMarkerIndex": marker_index,
            "measureGridStart": musical_position(
                start,
                beat_seconds=beat_seconds,
                measure_seconds=measure_seconds,
                measures_per_row=measures_per_row,
            ),
            "measureGridEnd": musical_position(
                end,
                beat_seconds=beat_seconds,
                measure_seconds=measure_seconds,
                measures_per_row=measures_per_row,
            ),
            "measureFragments": fragments,
            "crossesMeasureBoundary": len(fragments) > 1,
            "crossesRowBoundary": len({fragment["rowNumber"] for fragment in fragments}) > 1,
            "measureGridReadOnly": True,
        })
        markers.append(projected)
        for fragment in fragments:
            all_fragments.append({
                **fragment,
                "markerIndex": marker_index,
                "markerType": marker.get("type"),
                "instrument": marker.get("instrument"),
                "label": marker.get("label"),
            })

    rows: list[dict[str, Any]] = []
    for row_zero in range(row_count):
        first_measure = row_zero * measures_per_row + 1
        last_measure = min(measure_count, first_measure + measures_per_row - 1)
        row_fragments = [
            fragment for fragment in all_fragments
            if int(fragment.get("rowNumber") or 0) == row_zero + 1
        ]
        rows.append({
            "rowNumber": row_zero + 1,
            "firstMeasure": first_measure,
            "lastMeasure": last_measure,
            "measureCount": max(0, last_measure - first_measure + 1),
            "fragmentCount": len(row_fragments),
            "markerTypes": sorted({str(fragment.get("markerType") or "") for fragment in row_fragments}),
            "fragments": row_fragments,
        })

    checks = {
        "sourceProjectionPassed": projection.get("passed") is True,
        "protectedBaselinesUnchanged": projection.get("protectedBaselinesChanged") is False,
        "timeSignatureFourFour": beats_per_measure == 4,
        "sixMeasuresPerRow": measures_per_row == 6,
        "allMarkersProjected": len(markers) == len(source_markers),
        "allMarkersReadOnly": all(marker.get("measureGridReadOnly") is True for marker in markers),
        "allFragmentsReadOnly": all(fragment.get("readOnly") is True for fragment in all_fragments),
        "allMeasuresValid": all(
            1 <= int(fragment.get("measureNumber") or 0) <= max(1, measure_count)
            for fragment in all_fragments
        ),
        "allRowsValid": all(
            1 <= int(fragment.get("rowNumber") or 0) <= max(1, row_count)
            for fragment in all_fragments
        ),
        "allRatiosNormalized": all(
            0.0 <= number(fragment.get("measureStartRatio")) <= 1.0
            and 0.0 <= number(fragment.get("measureEndRatio")) <= 1.0
            and 0.0 <= number(fragment.get("rowStartRatio")) <= 1.0
            and 0.0 <= number(fragment.get("rowEndRatio")) <= 1.0
            for fragment in all_fragments
        ),
        "timestampsPreserved": all(
            abs(number(marker.get("start")) - number(source_markers[index].get("start"))) < 0.000001
            and abs(number(marker.get("end")) - number(source_markers[index].get("end"))) < 0.000001
            for index, marker in enumerate(markers)
        ),
    }

    return {
        "measureGridVersion": 7,
        "measureGridType": "v7-read-only-four-four-six-measures-per-row",
        "audioName": projection.get("audioName"),
        "songDuration": round(song_duration, 6),
        "tempoBpm": round(bpm, 4),
        "beatsPerMeasure": beats_per_measure,
        "beatUnit": 4,
        "beatSeconds": round(beat_seconds, 8),
        "measureSeconds": round(measure_seconds, 8),
        "measuresPerRow": measures_per_row,
        "measureCount": measure_count,
        "rowCount": row_count,
        "sourceProjectionType": projection.get("projectionType"),
        "markers": markers,
        "rows": rows,
        "counts": {
            "markers": len(markers),
            "fragments": len(all_fragments),
            "measureCrossingMarkers": sum(1 for marker in markers if marker.get("crossesMeasureBoundary")),
            "rowCrossingMarkers": sum(1 for marker in markers if marker.get("crossesRowBoundary")),
            "measures": measure_count,
            "rows": row_count,
        },
        "checks": checks,
        "passed": all(checks.values()),
        "affectsProductionEvents": False,
        "affectsGeneratedTab": False,
        "affectsPdf": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Convert read-only notation timestamps into 4/4 measure and beat coordinates at the configured tempo. "
            "Use six measures per printable row and split spans at measure and row boundaries without altering "
            "production events, generated tab, pitches, frets, timing, note count, or PDF rendering."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projection", default=str(DEFAULT_PROJECTION))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--bpm", type=float, default=DEFAULT_BPM)
    parser.add_argument("--beats-per-measure", type=int, default=DEFAULT_BEATS_PER_MEASURE)
    parser.add_argument("--measures-per-row", type=int, default=DEFAULT_MEASURES_PER_ROW)
    args = parser.parse_args()

    result = build_measure_grid(
        load_json(Path(args.projection)),
        bpm=args.bpm,
        beats_per_measure=args.beats_per_measure,
        measures_per_row=args.measures_per_row,
    )
    output = Path(args.output)
    output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V7 MEASURE-GRID PROJECTION")
    print("=" * 72)
    for name, passed in (result.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Tempo:", result.get("tempoBpm"), "BPM")
    print("Time signature: 4/4")
    print("Measures per row:", result.get("measuresPerRow"))
    print("Counts:", result.get("counts"))
    print("Overall:", "PASS" if result.get("passed") else "FAIL")
    print("Saved measure grid:", output)

    if not result.get("passed"):
        raise SystemExit("\nV7 measure-grid projection regression detected.")


if __name__ == "__main__":
    main()
