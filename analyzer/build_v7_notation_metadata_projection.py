#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_TIMELINE = Path("/tmp/gomyway-full-song-v7-timeline-report.json")
DEFAULT_OUTPUT = Path("/tmp/gomyway-full-song-v7-notation-metadata.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def rounded(value: Any) -> float:
    return round(float(value or 0.0), 4)


def build_projection(timeline: dict[str, Any]) -> dict[str, Any]:
    harmony_markers = [
        {
            "type": "chord-label",
            "instrument": "rhythm",
            "label": str(item.get("chord") or ""),
            "start": rounded(item.get("start")),
            "end": rounded(item.get("end")),
            "duration": rounded(item.get("duration")),
            "source": "rhythm-chord-timeline",
            "readOnly": True,
        }
        for item in (timeline.get("harmonyRanges") or [])
        if isinstance(item, dict) and item.get("chord")
    ]

    lead_release_markers = [
        {
            "type": "bend-release",
            "instrument": "lead",
            "start": rounded(item.get("bendStart")),
            "releaseStart": rounded(item.get("releaseStart")),
            "end": rounded(item.get("releaseStart")),
            "bendFret": item.get("bendFret"),
            "releaseFret": item.get("releaseFret"),
            "bendAmount": "full",
            "source": "lead-release-timeline",
            "readOnly": True,
        }
        for item in (timeline.get("leadReleaseRanges") or [])
        if isinstance(item, dict)
    ]

    lead_palm_mute_markers = [
        {
            "type": "palm-mute-span",
            "instrument": "lead",
            "start": rounded(item.get("start")),
            "end": rounded(item.get("end")),
            "eventCount": int(item.get("eventCount") or 0),
            "eventIndices": [int(value) for value in (item.get("eventIndices") or [])],
            "source": "lead-palm-mute-cluster",
            "readOnly": True,
        }
        for item in (timeline.get("leadPalmMuteClusters") or [])
        if isinstance(item, dict)
    ]

    bass_markers: list[dict[str, Any]] = []
    bass_points = timeline.get("bassPoints") or {}
    marker_types = {
        "slide": "slide",
        "mute": "muted-attack",
        "rest": "rest",
    }
    for key, marker_type in marker_types.items():
        point = bass_points.get(key)
        if not isinstance(point, dict):
            continue
        marker = {
            "type": marker_type,
            "instrument": "bass",
            "start": rounded(point.get("start")),
            "end": rounded(point.get("end")),
            "eventIndex": int(point.get("eventIndex") or 0),
            "source": f"bass-{key}-timeline",
            "readOnly": True,
        }
        if key == "slide":
            marker["targetFret"] = point.get("targetFret")
        bass_markers.append(marker)

    all_markers = [
        *harmony_markers,
        *lead_release_markers,
        *lead_palm_mute_markers,
        *bass_markers,
    ]
    all_markers.sort(
        key=lambda marker: (
            rounded(marker.get("start")),
            str(marker.get("instrument") or ""),
            str(marker.get("type") or ""),
        )
    )

    song_duration = rounded(timeline.get("songDuration"))
    checks = {
        "timelinePassed": timeline.get("passed") is True,
        "protectedBaselinesUnchanged": timeline.get("protectedBaselinesChanged") is False,
        "chordLabelsPresent": bool(harmony_markers),
        "bendReleaseMarkersPresent": bool(lead_release_markers),
        "palmMuteSpansPresent": bool(lead_palm_mute_markers),
        "bassSlidePresent": any(item.get("type") == "slide" for item in bass_markers),
        "bassMutePresent": any(item.get("type") == "muted-attack" for item in bass_markers),
        "bassRestPresent": any(item.get("type") == "rest" for item in bass_markers),
        "allMarkersReadOnly": all(item.get("readOnly") is True for item in all_markers),
        "allMarkersWithinSong": all(
            0.0 <= rounded(item.get("start")) <= song_duration + 0.01
            and 0.0 <= rounded(item.get("end")) <= song_duration + 0.01
            for item in all_markers
        ),
    }

    return {
        "projectionVersion": 7,
        "projectionType": "v7-read-only-notation-metadata",
        "audioName": timeline.get("audioName"),
        "songDuration": song_duration,
        "sourceBenchmarkType": timeline.get("benchmarkType"),
        "rhythmVocabulary": timeline.get("rhythmVocabulary") or [],
        "rhythmPromotions": timeline.get("rhythmPromotions") or {},
        "notationMetadata": {
            "chordLabels": harmony_markers,
            "leadBendReleaseMarkers": lead_release_markers,
            "leadPalmMuteSpans": lead_palm_mute_markers,
            "bassMarkers": bass_markers,
            "allMarkers": all_markers,
        },
        "counts": {
            "chordLabels": len(harmony_markers),
            "leadBendReleaseMarkers": len(lead_release_markers),
            "leadPalmMuteSpans": len(lead_palm_mute_markers),
            "leadPalmMutedEvents": int(timeline.get("leadPalmMutedEventCount") or 0),
            "bassMarkers": len(bass_markers),
            "allMarkers": len(all_markers),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "affectsProductionEvents": False,
        "affectsGeneratedTab": False,
        "affectsPdf": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "Notation metadata is projected from the locked read-only timeline only. "
            "It must not alter production events, generated tab, pitch, fret, timing, "
            "note count, or PDF rendering."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeline", default=str(DEFAULT_TIMELINE))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    projection = build_projection(load_json(Path(args.timeline)))
    output = Path(args.output)
    output.write_text(
        json.dumps(projection, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print("JIMMY PAIGE V7 NOTATION-METADATA PROJECTION")
    print("=" * 72)
    for name, passed in (projection.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Counts:", projection.get("counts"))
    print("Overall:", "PASS" if projection.get("passed") else "FAIL")
    print("Saved projection:", output)

    if not projection.get("passed"):
        raise SystemExit("\nV7 notation-metadata projection regression detected.")


if __name__ == "__main__":
    main()
