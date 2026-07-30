#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

DEFAULT_PROJECTION = Path("/tmp/gomyway-full-song-v7-notation-metadata.json")
DEFAULT_OUTPUT = Path("/tmp/gomyway-full-song-v7-layout-binding.json")
DEFAULT_SEGMENT_SECONDS = 4.0


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def rounded(value: Any) -> float:
    return round(float(value or 0.0), 4)


def bind_marker(
    marker: dict[str, Any],
    *,
    song_duration: float,
    segment_seconds: float,
) -> dict[str, Any]:
    start = max(0.0, min(song_duration, rounded(marker.get("start"))))
    end = max(start, min(song_duration, rounded(marker.get("end"))))
    segment_index = int(math.floor(start / segment_seconds))
    segment_start = segment_index * segment_seconds
    segment_end = min(song_duration, segment_start + segment_seconds)
    segment_duration = max(0.0001, segment_end - segment_start)

    bound = dict(marker)
    bound.update({
        "layoutSegmentIndex": segment_index,
        "layoutSegmentStart": round(segment_start, 4),
        "layoutSegmentEnd": round(segment_end, 4),
        "layoutStartRatio": round((start - segment_start) / segment_duration, 6),
        "layoutEndRatio": round((end - segment_start) / segment_duration, 6),
        "layoutBindingMode": "read-only-time-segment",
        "layoutBindingReadOnly": True,
    })
    return bound


def build_binding(
    projection: dict[str, Any],
    *,
    segment_seconds: float,
) -> dict[str, Any]:
    if segment_seconds <= 0:
        raise ValueError("segment_seconds must be positive")

    song_duration = rounded(projection.get("songDuration"))
    markers = [
        marker
        for marker in ((projection.get("notationMetadata") or {}).get("allMarkers") or [])
        if isinstance(marker, dict)
    ]
    bound_markers = [
        bind_marker(
            marker,
            song_duration=song_duration,
            segment_seconds=segment_seconds,
        )
        for marker in markers
    ]
    bound_markers.sort(
        key=lambda marker: (
            int(marker.get("layoutSegmentIndex") or 0),
            rounded(marker.get("start")),
            str(marker.get("instrument") or ""),
            str(marker.get("type") or ""),
        )
    )

    segment_count = int(math.ceil(song_duration / segment_seconds)) if song_duration else 0
    segments: list[dict[str, Any]] = []
    for index in range(segment_count):
        segment_markers = [
            marker
            for marker in bound_markers
            if int(marker.get("layoutSegmentIndex") or 0) == index
        ]
        segments.append({
            "segmentIndex": index,
            "start": round(index * segment_seconds, 4),
            "end": round(min(song_duration, (index + 1) * segment_seconds), 4),
            "markerCount": len(segment_markers),
            "markerTypes": sorted({str(marker.get("type") or "") for marker in segment_markers}),
            "markers": segment_markers,
        })

    event_linked = [
        marker
        for marker in bound_markers
        if "eventIndex" in marker or bool(marker.get("eventIndices"))
    ]
    checks = {
        "sourceProjectionPassed": projection.get("passed") is True,
        "protectedBaselinesUnchanged": projection.get("protectedBaselinesChanged") is False,
        "allMarkersBound": len(bound_markers) == len(markers),
        "allBindingsReadOnly": all(marker.get("layoutBindingReadOnly") is True for marker in bound_markers),
        "allSegmentIndicesValid": all(
            0 <= int(marker.get("layoutSegmentIndex") or 0) < max(1, segment_count)
            for marker in bound_markers
        ),
        "allRatiosNormalized": all(
            0.0 <= float(marker.get("layoutStartRatio") or 0.0) <= 1.0
            and 0.0 <= float(marker.get("layoutEndRatio") or 0.0) <= 1.0
            for marker in bound_markers
        ),
        "chronologicalOrderPreserved": bound_markers == sorted(
            bound_markers,
            key=lambda marker: (
                int(marker.get("layoutSegmentIndex") or 0),
                rounded(marker.get("start")),
                str(marker.get("instrument") or ""),
                str(marker.get("type") or ""),
            ),
        ),
        "eventLinksPreserved": all(
            "eventIndex" in marker or bool(marker.get("eventIndices"))
            for marker in event_linked
        ),
    }

    return {
        "bindingVersion": 7,
        "bindingType": "v7-read-only-notation-layout-segments",
        "audioName": projection.get("audioName"),
        "songDuration": song_duration,
        "segmentSeconds": segment_seconds,
        "segmentCount": segment_count,
        "sourceProjectionType": projection.get("projectionType"),
        "segments": segments,
        "boundMarkers": bound_markers,
        "counts": {
            "segments": segment_count,
            "markers": len(bound_markers),
            "eventLinkedMarkers": len(event_linked),
            "occupiedSegments": sum(1 for segment in segments if segment.get("markerCount")),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "affectsProductionEvents": False,
        "affectsGeneratedTab": False,
        "affectsPdf": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Notation markers may be bound to deterministic printable time segments only. "
            "The binding must not alter production events, generated tab, pitches, frets, "
            "timing, note count, or PDF rendering."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projection", default=str(DEFAULT_PROJECTION))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--segment-seconds", type=float, default=DEFAULT_SEGMENT_SECONDS)
    args = parser.parse_args()

    binding = build_binding(
        load_json(Path(args.projection)),
        segment_seconds=args.segment_seconds,
    )
    output = Path(args.output)
    output.write_text(json.dumps(binding, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V7 NOTATION LAYOUT BINDING")
    print("=" * 72)
    for name, passed in (binding.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Counts:", binding.get("counts"))
    print("Overall:", "PASS" if binding.get("passed") else "FAIL")
    print("Saved binding:", output)

    if not binding.get("passed"):
        raise SystemExit("\nV7 notation layout binding regression detected.")


if __name__ == "__main__":
    main()
