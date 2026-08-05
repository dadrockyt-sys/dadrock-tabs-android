from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"

SOURCE_PATH = PUBLIC_DIR / "gomyway-full-song-v8-notation.json"
CONSENSUS_PATH = PUBLIC_DIR / "gomyway-missing-render-measures-consensus-selection-v1.json"
OUTPUT_PATH = PUBLIC_DIR / "gomyway-full-song-v8-render-events-overlay-v1.json"

TARGETS = (106, 113)


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path.relative_to(REPO_ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path.relative_to(REPO_ROOT)}")
    return value


def get_measure(event: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = event.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                pass
    return None


def normalize_overlay(measure: int, selection: dict[str, Any]) -> dict[str, Any]:
    notes = selection.get("notes")
    if not isinstance(notes, list) or not notes:
        raise ValueError(f"Measure {measure} selection has no notes")

    normalized_notes: list[dict[str, int]] = []
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError(f"Measure {measure} contains a non-object note")
        string = note.get("string", note.get("stringIndex"))
        fret = note.get("fret")
        if not isinstance(string, (int, float)) or not isinstance(fret, (int, float)):
            raise ValueError(f"Measure {measure} note is missing numeric string/fret")
        normalized_notes.append({"string": int(string), "fret": int(fret)})

    step = selection.get("quantizedStep")
    duration = selection.get("durationSteps")
    techniques = selection.get("techniques")
    if not isinstance(step, (int, float)):
        raise ValueError(f"Measure {measure} selection is missing quantizedStep")
    if not isinstance(duration, (int, float)):
        raise ValueError(f"Measure {measure} selection is missing durationSteps")
    if not isinstance(techniques, list):
        techniques = []

    return {
        "measureNumber": measure,
        "quantizedStep": int(step),
        "durationSteps": int(duration),
        "notes": normalized_notes,
        "techniques": [str(value) for value in techniques],
        "source": "read-only-consensus-overlay",
        "overlayVersion": 1,
        "humanPromotionAllowed": False,
    }


def event_signature(event: dict[str, Any]) -> tuple[Any, ...]:
    notes = event.get("notes")
    normalized_notes: list[tuple[int, int]] = []
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            string = note.get("string", note.get("stringIndex"))
            fret = note.get("fret")
            if isinstance(string, (int, float)) and isinstance(fret, (int, float)):
                normalized_notes.append((int(string), int(fret)))

    if not normalized_notes:
        string = event.get("string", event.get("stringIndex"))
        fret = event.get("fret")
        if isinstance(string, (int, float)) and isinstance(fret, (int, float)):
            normalized_notes.append((int(string), int(fret)))

    return (
        get_measure(event),
        int(event.get("quantizedStep")) if isinstance(event.get("quantizedStep"), (int, float)) else None,
        int(event.get("durationSteps")) if isinstance(event.get("durationSteps"), (int, float)) else None,
        tuple(sorted(normalized_notes)),
        tuple(sorted(str(value) for value in event.get("techniques", []) if value is not None))
        if isinstance(event.get("techniques"), list)
        else (),
    )


def main() -> None:
    source = load_json(SOURCE_PATH)
    consensus = load_json(CONSENSUS_PATH)

    source_events = source.get("rhythmEvents")
    if not isinstance(source_events, list):
        raise TypeError("Source rhythmEvents is missing or not a list")
    if len(source_events) != 572:
        raise ValueError(f"Expected 572 source rhythmEvents, found {len(source_events)}")

    measures = consensus.get("measures")
    if not isinstance(measures, dict):
        raise TypeError("Consensus measures block is missing")
    if consensus.get("readyForReadOnlyOverlayProjection") is not True:
        raise ValueError("Consensus selection is not green")

    overlays: list[dict[str, Any]] = []
    overlay_support: dict[str, Any] = {}
    for measure in TARGETS:
        item = measures.get(str(measure))
        if not isinstance(item, dict):
            raise ValueError(f"Missing consensus item for measure {measure}")
        if item.get("readyForReadOnlyOverlay") is not True:
            raise ValueError(f"Measure {measure} is not ready for overlay")
        selection = item.get("selectedSignature")
        if not isinstance(selection, dict):
            raise ValueError(f"Measure {measure} has no selected signature")
        overlays.append(normalize_overlay(measure, selection))
        overlay_support[str(measure)] = {
            "supportCount": item.get("supportCount"),
            "distinctSourceCount": item.get("distinctSourceCount"),
            "distinctSourceFamilyCount": item.get("distinctSourceFamilyCount"),
            "sources": item.get("sources", []),
        }

    output_events = [copy.deepcopy(event) for event in source_events if isinstance(event, dict)]
    output_events.extend(overlays)
    output_events.sort(
        key=lambda event: (
            get_measure(event) or 0,
            int(event.get("quantizedStep")) if isinstance(event.get("quantizedStep"), (int, float)) else -1,
            event_signature(event),
        )
    )

    signatures = [event_signature(event) for event in output_events]
    duplicate_count = len(signatures) - len(set(signatures))
    covered_measures = sorted({measure for event in output_events for measure in [get_measure(event)] if measure is not None})
    missing_measures = sorted(set(range(1, 114)) - set(covered_measures))

    report = {
        "schemaVersion": 1,
        "projectionType": "full-song-v8-render-events-read-only-overlay",
        "source": str(SOURCE_PATH.relative_to(REPO_ROOT)),
        "consensus": str(CONSENSUS_PATH.relative_to(REPO_ROOT)),
        "sourceEventCount": len(source_events),
        "overlayEventCount": len(overlays),
        "renderEventCount": len(output_events),
        "overlayMeasures": list(TARGETS),
        "overlaySupport": overlay_support,
        "coveredMeasures": covered_measures,
        "missingMeasures": missing_measures,
        "duplicateEventSignatures": duplicate_count,
        "renderEvents": output_events,
        "passed": (
            len(source_events) == 572
            and len(overlays) == 2
            and len(output_events) == 574
            and covered_measures == list(range(1, 114))
            and missing_measures == []
            and duplicate_count == 0
        ),
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Full-song V8 render-event overlay V1 complete")
    print("Passed:", report["passed"])
    print("Source events:", report["sourceEventCount"])
    print("Overlay events:", report["overlayEventCount"])
    print("Render events:", report["renderEventCount"])
    print("Covered measures:", len(report["coveredMeasures"]))
    print("Missing measures:", report["missingMeasures"])
    print("Duplicate event signatures:", report["duplicateEventSignatures"])
    print("Overlay measures:", report["overlayMeasures"])
    print("Ready for genuine tablature renderer:", report["passed"])
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit("V8 render-event overlay did not pass protected checks")


if __name__ == "__main__":
    main()
