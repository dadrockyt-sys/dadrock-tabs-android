#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_PROJECTION = Path("/tmp/gomyway-full-song-v7-notation-metadata.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Notation projection not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--projection", default=str(DEFAULT_PROJECTION))
    args = parser.parse_args()

    report = load_json(Path(args.projection))
    metadata = report.get("notationMetadata") or {}
    counts = report.get("counts") or {}
    source_checks = report.get("checks") or {}

    chord_labels = metadata.get("chordLabels") or []
    release_markers = metadata.get("leadBendReleaseMarkers") or []
    palm_spans = metadata.get("leadPalmMuteSpans") or []
    bass_markers = metadata.get("bassMarkers") or []
    all_markers = metadata.get("allMarkers") or []

    bass_types = {
        str(item.get("type") or "")
        for item in bass_markers
        if isinstance(item, dict)
    }
    ordered_starts = [
        float(item.get("start") or 0.0)
        for item in all_markers
        if isinstance(item, dict)
    ]

    checks = {
        "projectionPassed": report.get("passed") is True,
        "sourceProjectionChecksGreen": all(value is True for value in source_checks.values()),
        "protectedBaselinesUnchanged": report.get("protectedBaselinesChanged") is False,
        "productionEventsUnaffected": report.get("affectsProductionEvents") is False,
        "generatedTabUnaffected": report.get("affectsGeneratedTab") is False,
        "pdfStillUnaffected": report.get("affectsPdf") is False,
        "harmonyLabelsPreserved": len(chord_labels) >= 38,
        "leadReleaseMarkerPreserved": len(release_markers) >= 1,
        "leadPalmMuteSpansPreserved": len(palm_spans) >= 1,
        "leadPalmMutedEventCountPreserved": int(counts.get("leadPalmMutedEvents") or 0) >= 157,
        "bassSlideMarkerPreserved": "slide" in bass_types,
        "bassMuteMarkerPreserved": "muted-attack" in bass_types,
        "bassRestMarkerPreserved": "rest" in bass_types,
        "allMarkersReadOnly": all(
            isinstance(item, dict) and item.get("readOnly") is True
            for item in all_markers
        ),
        "markersChronologicallySorted": ordered_starts == sorted(ordered_starts),
        "markerCountConsistent": int(counts.get("allMarkers") or 0) == len(all_markers),
    }

    failed = False
    print("JIMMY PAIGE V7 NOTATION-METADATA PROJECTION GUARD")
    print("=" * 72)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    print("Chord labels:", len(chord_labels))
    print("Lead bend/release markers:", len(release_markers))
    print("Lead palm-mute spans:", len(palm_spans))
    print("Lead palm-muted events:", counts.get("leadPalmMutedEvents"))
    print("Bass marker types:", sorted(bass_types))
    print("Total notation markers:", len(all_markers))

    if failed:
        raise SystemExit(
            "\nV7 notation-metadata projection regression detected. Do not render."
        )

    print("\nV7 NOTATION-METADATA PROJECTION PRESERVED 💚")
    print("Chord, bend/release, palm-mute, slide, mute, and rest markers are read-only.")
    print("Production events, generated tab, and PDF rendering remain untouched.")


if __name__ == "__main__":
    main()
