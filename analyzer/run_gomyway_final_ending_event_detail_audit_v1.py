from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PUBLIC_DIR = REPO_ROOT / "public"
SOURCE_CANDIDATES = (
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference-chunk-97-113.json",
    PUBLIC_DIR / "gomyway-professional-rhythm-reference.json",
)
OUTPUT_PATH = PUBLIC_DIR / "gomyway-final-ending-event-detail-audit-v1.json"

ENDING_START = 111
ENDING_END = 113


def load_source() -> tuple[Path, dict[str, Any]]:
    for path in SOURCE_CANDIDATES:
        if path.exists():
            return path, json.loads(path.read_text(encoding="utf-8"))
    tried = ", ".join(str(path.relative_to(REPO_ROOT)) for path in SOURCE_CANDIDATES)
    raise FileNotFoundError(f"No final-ending professional reference found. Tried: {tried}")


def measure_number(item: dict[str, Any]) -> int | None:
    for key in ("measureNumber", "measure", "barNumber", "bar"):
        value = item.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, str):
            try:
                return int(float(value))
            except ValueError:
                continue
    return None


def event_step(event: dict[str, Any]) -> int | None:
    for key in ("quantizedStep", "step", "sixteenthStep"):
        value = event.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, (int, float)):
            return int(value)
    position = event.get("positionInMeasure", event.get("position"))
    if isinstance(position, (int, float)):
        return int(round(float(position) * 16.0)) % 16
    return None


def compact_event(event: dict[str, Any], source_list: str) -> dict[str, Any]:
    notes = event.get("notes")
    compact_notes: list[dict[str, Any]] = []
    if isinstance(notes, list):
        for note in notes:
            if isinstance(note, dict):
                compact_notes.append({
                    key: note.get(key)
                    for key in (
                        "string",
                        "stringIndex",
                        "fret",
                        "midiPitch",
                        "midi",
                        "pitch",
                    )
                    if key in note
                })

    return {
        "sourceList": source_list,
        "step": event_step(event),
        "quantizedStep": event.get("quantizedStep"),
        "positionInMeasure": event.get("positionInMeasure", event.get("position")),
        "durationSteps": event.get("durationSteps"),
        "start": event.get("start"),
        "end": event.get("end"),
        "duration": event.get("duration"),
        "string": event.get("string"),
        "stringIndex": event.get("stringIndex"),
        "fret": event.get("fret"),
        "midiPitch": event.get("midiPitch", event.get("midi", event.get("pitch"))),
        "notes": compact_notes,
        "techniques": event.get("techniques") or [],
        "referenceConfidence": event.get("referenceConfidence", event.get("confidence")),
        "sourceDerived": event.get("sourceDerived"),
        "humanValidated": event.get("humanValidated"),
        "readOnly": event.get("readOnly"),
    }


def main() -> None:
    source_path, payload = load_source()
    measures = payload.get("measures") or payload.get("measureReports") or []
    if not isinstance(measures, list):
        raise TypeError("Professional reference does not expose measures/measureReports as a list")

    reports: list[dict[str, Any]] = []
    pending_measures: list[int] = []
    approved_measures: list[int] = []
    total_explicit_events = 0

    for measure in measures:
        if not isinstance(measure, dict):
            continue
        number = measure_number(measure)
        if number is None or not ENDING_START <= number <= ENDING_END:
            continue

        human_review = measure.get("humanReview") or {}
        status = human_review.get("status")
        if status == "approved":
            approved_measures.append(number)
        else:
            pending_measures.append(number)

        explicit_events: list[dict[str, Any]] = []
        structural_lists: dict[str, int] = {}
        for key, value in measure.items():
            if not isinstance(value, list) or not value:
                continue
            if key in {"sixteenthSlots", "slots", "grid"}:
                structural_lists[key] = len(value)
                continue
            for item in value:
                if isinstance(item, dict):
                    explicit_events.append(compact_event(item, key))

        explicit_events.sort(
            key=lambda item: (
                item["step"] is None,
                item["step"] if item["step"] is not None else 999,
                item["sourceList"],
            )
        )
        total_explicit_events += len(explicit_events)

        reports.append({
            "measureNumber": number,
            "section": measure.get("section") or measure.get("sectionLabel"),
            "meter": measure.get("meter"),
            "measureFlags": measure.get("measureFlags") or {},
            "humanReview": human_review,
            "structuralLists": structural_lists,
            "explicitEventCount": len(explicit_events),
            "explicitEvents": explicit_events,
            "requiresListeningReview": status != "approved",
        })

    reports.sort(key=lambda item: item["measureNumber"])

    report = {
        "schemaVersion": 1,
        "auditType": "final-ending-event-detail",
        "source": str(source_path.relative_to(REPO_ROOT)),
        "measureRange": [ENDING_START, ENDING_END],
        "pendingHumanReviewMeasures": sorted(pending_measures),
        "approvedMeasures": sorted(approved_measures),
        "totalExplicitEvents": total_explicit_events,
        "measureReports": reports,
        "interpretation": (
            "Measures 111 and 112 contain explicit machine-transcribed ending events but remain "
            "pending human review. Measure 113 is already human approved and source resolved. "
            "This audit exposes exact steps, pitches, frets, durations, techniques, and timing before "
            "creating synchronized listening windows for only the pending measures."
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

    print("Final-ending event-detail audit V1 complete")
    print("Source:", report["source"])
    print("Pending human-review measures:", report["pendingHumanReviewMeasures"])
    print("Approved measures:", report["approvedMeasures"])
    print("Total explicit events:", report["totalExplicitEvents"])
    print()

    for item in reports:
        print(
            f"measure {item['measureNumber']} "
            f"status={item['humanReview'].get('status')} "
            f"events={item['explicitEventCount']} "
            f"flags={item['measureFlags']}"
        )
        for event in item["explicitEvents"]:
            print(
                "  ",
                f"list={event['sourceList']}",
                f"step={event['step']}",
                f"position={event['positionInMeasure']}",
                f"durationSteps={event['durationSteps']}",
                f"pitch={event['midiPitch']}",
                f"string={event['stringIndex'] if event['stringIndex'] is not None else event['string']}",
                f"fret={event['fret']}",
                f"techniques={event['techniques']}",
                f"confidence={event['referenceConfidence']}",
            )

    print()
    print("Automatic promotion allowed: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
