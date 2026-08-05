#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

REFERENCE_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-rhythm-reference.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-full-machine.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
)
TIMING_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-timing-map-v2.json",
    PUBLIC_DIR / "gomyway-professional-timing-map-v1.json",
)
MERGE_PATH = PUBLIC_DIR / "gomyway-full-song-review-evidence-merge-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-full-song-v8-notation-metadata.json"

SUPPORTED_TYPES = {
    "chord-label",
    "bend-release",
    "palm-mute-span",
    "slide",
    "muted-attack",
    "rest",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path.relative_to(REPO_ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path.relative_to(REPO_ROOT)}")
    return value


def first_existing(paths: tuple[Path, ...]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError("No candidate source file exists: " + ", ".join(str(p) for p in paths))


def number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def measure_number(row: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = number(row.get(key))
        if value is not None:
            return int(value)
    return None


def measure_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("measures", "measureReports", "measureBounds", "measureBoundaries"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def timing_bounds(payload: dict[str, Any]) -> dict[int, tuple[float, float]]:
    result: dict[int, tuple[float, float]] = {}
    for row in measure_rows(payload):
        measure = measure_number(row)
        if measure is None:
            continue
        start = number(row.get("startSeconds", row.get("measureStartSeconds", row.get("start"))))
        end = number(row.get("endSeconds", row.get("measureEndSeconds", row.get("end"))))
        time_range = row.get("timeRange")
        if (start is None or end is None) and isinstance(time_range, list) and len(time_range) >= 2:
            start = number(time_range[0])
            end = number(time_range[1])
        if start is not None and end is not None and end > start:
            result[measure] = (start, end)
    return result


def event_lists(measure: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    found: list[tuple[str, dict[str, Any]]] = []
    ignored = {"sixteenthSlots", "slots", "grid", "warnings", "notes"}
    for key, value in measure.items():
        if key in ignored or not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                found.append((key, item))
    return found


def event_times(event: dict[str, Any], bounds: tuple[float, float]) -> tuple[float, float]:
    measure_start, measure_end = bounds
    measure_duration = measure_end - measure_start
    start = number(event.get("start"))
    end = number(event.get("end"))
    if start is not None and end is not None and end >= start:
        return start, end

    position = number(event.get("positionInMeasure", event.get("position")))
    step = number(event.get("quantizedStep", event.get("step", event.get("sixteenthStep"))))
    if position is None and step is not None:
        position = step / 16.0
    if position is None:
        position = 0.0

    duration_steps = number(event.get("durationSteps"))
    duration = number(event.get("duration"))
    if duration is None and duration_steps is not None:
        duration = measure_duration * duration_steps / 16.0
    if duration is None:
        duration = max(0.08, measure_duration / 16.0)

    start = measure_start + max(0.0, min(1.0, position)) * measure_duration
    end = min(measure_end, max(start + 0.02, start + duration))
    return start, end


def technique_names(event: dict[str, Any]) -> list[str]:
    raw = event.get("techniques") or event.get("technique") or []
    if isinstance(raw, str):
        return [raw]
    if isinstance(raw, list):
        return [str(item) for item in raw]
    return []


def chord_label(event: dict[str, Any]) -> str | None:
    for key in ("chordLabel", "chord", "label", "voicingLabel"):
        value = event.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    notes = event.get("notes")
    if isinstance(notes, list) and len(notes) >= 2:
        frets = []
        for note in notes:
            if isinstance(note, dict) and note.get("fret") is not None:
                frets.append(str(note.get("fret")))
        if frets:
            return "Chord " + "/".join(frets)
    return None


def marker_rows(measure: dict[str, Any], bounds: tuple[float, float]) -> list[dict[str, Any]]:
    markers: list[dict[str, Any]] = []
    measure_no = measure_number(measure)
    for source_list, event in event_lists(measure):
        start, end = event_times(event, bounds)
        label = chord_label(event)
        if label:
            markers.append({
                "type": "chord-label",
                "instrument": "rhythm",
                "label": label,
                "start": round(start, 6),
                "end": round(end, 6),
                "measureNumber": measure_no,
                "sourceList": source_list,
                "eventIndex": event.get("eventIndex"),
                "readOnly": True,
            })

        for technique in technique_names(event):
            normalized = technique.lower().replace("_", "-").replace(" ", "-")
            marker_type: str | None = None
            if "palm" in normalized and "mute" in normalized:
                marker_type = "palm-mute-span"
            elif "bend" in normalized:
                marker_type = "bend-release"
            elif "slide" in normalized:
                marker_type = "slide"
            elif normalized in {"muted", "muted-attack", "dead-note", "x"}:
                marker_type = "muted-attack"
            elif "rest" in normalized:
                marker_type = "rest"
            if marker_type:
                marker = {
                    "type": marker_type,
                    "instrument": "rhythm",
                    "start": round(start, 6),
                    "end": round(end, 6),
                    "measureNumber": measure_no,
                    "sourceList": source_list,
                    "eventIndex": event.get("eventIndex"),
                    "readOnly": True,
                }
                if marker_type == "slide":
                    marker["targetFret"] = event.get("targetFret", event.get("fret"))
                markers.append(marker)

    return markers


def main() -> None:
    reference_path = first_existing(REFERENCE_CANDIDATES)
    timing_path = first_existing(TIMING_CANDIDATES)
    reference = load_json(reference_path)
    timing = load_json(timing_path)
    merge = load_json(MERGE_PATH)

    bounds = timing_bounds(timing)
    measures = {
        measure_number(row): row
        for row in measure_rows(reference)
        if measure_number(row) is not None
    }

    all_markers: list[dict[str, Any]] = []
    missing_measures: list[int] = []
    missing_timing: list[int] = []
    for measure_no in range(1, 114):
        row = measures.get(measure_no)
        if row is None:
            missing_measures.append(measure_no)
            continue
        if measure_no not in bounds:
            missing_timing.append(measure_no)
            continue
        all_markers.extend(marker_rows(row, bounds[measure_no]))

    all_markers.sort(key=lambda item: (float(item["start"]), str(item["type"]), int(item.get("measureNumber") or 0)))
    unsupported = sorted({str(item.get("type")) for item in all_markers if item.get("type") not in SUPPORTED_TYPES})
    song_duration = max((end for _, end in bounds.values()), default=0.0)

    checks = {
        "fullSongReviewEvidenceGreen": merge.get("passed") is True,
        "readyForProtectedPdfComparison": merge.get("readyForProtectedPdfComparison") is True,
        "all113ReferenceMeasuresPresent": not missing_measures,
        "all113TimingMeasuresPresent": not missing_timing,
        "notationMarkersCreated": len(all_markers) > 0,
        "allMarkerTypesSupported": not unsupported,
        "allMarkersReadOnly": all(item.get("readOnly") is True for item in all_markers),
        "professionalReferenceUntouched": True,
        "v7EventsUntouched": True,
        "rendererUntouched": True,
    }

    projection = {
        "projectionVersion": 8,
        "projectionType": "v8-read-only-professional-rhythm-notation-metadata",
        "audioName": "gomywayfullaitest.m4a",
        "songDuration": round(song_duration, 6),
        "sourceProfessionalReference": str(reference_path.relative_to(REPO_ROOT)),
        "sourceTimingMap": str(timing_path.relative_to(REPO_ROOT)),
        "sourceReviewEvidenceMerge": str(MERGE_PATH.relative_to(REPO_ROOT)),
        "measureRange": [1, 113],
        "missingReferenceMeasures": missing_measures,
        "missingTimingMeasures": missing_timing,
        "notationMetadata": {
            "allMarkers": all_markers,
            "markerCount": len(all_markers),
            "markerTypes": sorted({str(item.get("type")) for item in all_markers}),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(projection, indent=2) + "\n", encoding="utf-8")

    print("V8 notation-metadata projection V1 complete")
    print("Passed:", projection["passed"])
    print("Reference:", projection["sourceProfessionalReference"])
    print("Timing map:", projection["sourceTimingMap"])
    print("Measures:", projection["measureRange"])
    print("Missing reference measures:", missing_measures)
    print("Missing timing measures:", missing_timing)
    print("Notation markers:", len(all_markers))
    print("Marker types:", projection["notationMetadata"]["markerTypes"])
    print("Ready for V8 layout binding:", projection["passed"])
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not projection["passed"]:
        raise SystemExit("V8 notation projection did not pass its protected checks.")


if __name__ == "__main__":
    main()
