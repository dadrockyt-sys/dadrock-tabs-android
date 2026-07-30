#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_BINDING = Path("/tmp/gomyway-full-song-v7-layout-binding.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding", default=str(DEFAULT_BINDING))
    args = parser.parse_args()

    binding = load_json(Path(args.binding))
    source_checks = binding.get("checks") or {}
    counts = binding.get("counts") or {}
    markers = binding.get("boundMarkers") or []
    segments = binding.get("segments") or []

    marker_types = {
        str(marker.get("type") or "")
        for marker in markers
        if isinstance(marker, dict)
    }
    required_types = {
        "chord-label",
        "bend-release",
        "palm-mute-span",
        "slide",
        "muted-attack",
        "rest",
    }

    checks = {
        "bindingPassed": binding.get("passed") is True,
        "sourceBindingChecksGreen": all(value is True for value in source_checks.values()),
        "protectedBaselinesUnchanged": binding.get("protectedBaselinesChanged") is False,
        "productionEventsUnaffected": binding.get("affectsProductionEvents") is False,
        "generatedTabUnaffected": binding.get("affectsGeneratedTab") is False,
        "pdfStillUnaffected": binding.get("affectsPdf") is False,
        "all103MarkersBound": int(counts.get("markers") or 0) == 103,
        "allMarkerTypesPreserved": required_types <= marker_types,
        "printSegmentsPresent": int(counts.get("segments") or 0) > 0 and bool(segments),
        "occupiedSegmentsPresent": int(counts.get("occupiedSegments") or 0) > 0,
        "allMarkersReadOnly": all(
            isinstance(marker, dict)
            and marker.get("readOnly") is True
            and marker.get("layoutBindingReadOnly") is True
            for marker in markers
        ),
        "segmentMarkerCountsConsistent": sum(
            int(segment.get("markerCount") or 0)
            for segment in segments
            if isinstance(segment, dict)
        ) == len(markers),
    }

    print("JIMMY PAIGE V7 NOTATION LAYOUT BINDING GUARD")
    print("=" * 72)
    failed = False
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    print("Segments:", counts.get("segments"))
    print("Occupied segments:", counts.get("occupiedSegments"))
    print("Bound markers:", counts.get("markers"))
    print("Event-linked markers:", counts.get("eventLinkedMarkers"))
    print("Marker types:", sorted(marker_types))

    if failed:
        raise SystemExit("\nV7 notation layout binding regression detected. Do not render.")

    print("\nV7 NOTATION LAYOUT BINDING PRESERVED 💚")
    print("All 103 notation markers are bound to read-only printable time segments.")
    print("Production events, generated tab, and PDF rendering remain untouched.")


if __name__ == "__main__":
    main()
