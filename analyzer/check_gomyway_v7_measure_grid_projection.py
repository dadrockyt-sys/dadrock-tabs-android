#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_GRID = Path("/tmp/gomyway-full-song-v7-measure-grid.json")
EXPECTED_BPM = 129.0
EXPECTED_BEATS_PER_MEASURE = 4
EXPECTED_MEASURES_PER_ROW = 6
EXPECTED_MARKERS = 103
EXPECTED_MEASURES = 113
EXPECTED_ROWS = 19


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--grid", default=str(DEFAULT_GRID))
    args = parser.parse_args()

    grid = load_json(Path(args.grid))
    checks = grid.get("checks") or {}
    counts = grid.get("counts") or {}
    markers = grid.get("markers") or []
    rows = grid.get("rows") or []

    required_marker_types = {
        "bend-release",
        "chord-label",
        "muted-attack",
        "palm-mute-span",
        "rest",
        "slide",
    }
    marker_types = {
        str(marker.get("type") or "")
        for marker in markers
        if isinstance(marker, dict)
    }

    assertions = {
        "measureGridPassed": grid.get("passed") is True,
        "allSourceChecksGreen": bool(checks) and all(checks.values()),
        "protectedBaselinesUnchanged": grid.get("protectedBaselinesChanged") is False,
        "productionEventsUnaffected": grid.get("affectsProductionEvents") is False,
        "generatedTabUnaffected": grid.get("affectsGeneratedTab") is False,
        "pdfStillUnaffected": grid.get("affectsPdf") is False,
        "tempoLockedToReference": abs(float(grid.get("tempoBpm") or 0.0) - EXPECTED_BPM) < 0.0001,
        "timeSignatureLocked": int(grid.get("beatsPerMeasure") or 0) == EXPECTED_BEATS_PER_MEASURE,
        "sixMeasuresPerRowLocked": int(grid.get("measuresPerRow") or 0) == EXPECTED_MEASURES_PER_ROW,
        "all103MarkersProjected": int(counts.get("markers") or 0) == EXPECTED_MARKERS,
        "measureCountLocked": int(counts.get("measures") or 0) == EXPECTED_MEASURES,
        "rowCountLocked": int(counts.get("rows") or 0) == EXPECTED_ROWS,
        "allMarkerTypesPreserved": required_marker_types.issubset(marker_types),
        "measureFragmentsPresent": int(counts.get("fragments") or 0) >= EXPECTED_MARKERS,
        "crossMeasureSpansPresent": int(counts.get("measureCrossingMarkers") or 0) > 0,
        "rowsPresent": len(rows) == EXPECTED_ROWS,
        "allRowsBoundedToSixMeasures": all(
            1 <= int(row.get("measureCount") or 0) <= EXPECTED_MEASURES_PER_ROW
            for row in rows
            if isinstance(row, dict)
        ),
        "allMarkersReadOnly": all(
            marker.get("measureGridReadOnly") is True
            for marker in markers
            if isinstance(marker, dict)
        ),
    }

    print("JIMMY PAIGE V7 MEASURE-GRID PROJECTION GUARD")
    print("=" * 72)
    for name, passed in assertions.items():
        print("PASS" if passed else "FAIL", name)

    print("Tempo:", grid.get("tempoBpm"), "BPM")
    print("Time signature:", f"{grid.get('beatsPerMeasure')}/{grid.get('beatUnit')}")
    print("Measures:", counts.get("measures"))
    print("Rows:", counts.get("rows"))
    print("Measures per row:", grid.get("measuresPerRow"))
    print("Markers:", counts.get("markers"))
    print("Fragments:", counts.get("fragments"))
    print("Measure-crossing markers:", counts.get("measureCrossingMarkers"))
    print("Row-crossing markers:", counts.get("rowCrossingMarkers"))
    print("Marker types:", sorted(marker_types))

    passed = all(assertions.values())
    if passed:
        print("\nV7 MEASURE-AWARE NOTATION GRID PRESERVED 💚")
        print("All 103 markers are mapped into 4/4 measures at 129 BPM.")
        print("Six measures per row are preserved; barline continuations are read-only.")
        print("Production events, generated tab, and real PDF rendering remain untouched.")
    else:
        raise SystemExit("\nV7 measure-grid regression detected. Do not render.")


if __name__ == "__main__":
    main()
