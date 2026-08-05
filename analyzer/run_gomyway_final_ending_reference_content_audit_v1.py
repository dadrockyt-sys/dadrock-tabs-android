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
OUTPUT_PATH = PUBLIC_DIR / "gomyway-final-ending-reference-content-audit-v1.json"

ENDING_START = 111
ENDING_END = 113


def load_source() -> tuple[Path, dict[str, Any]]:
    for path in SOURCE_CANDIDATES:
        if path.exists():
            return path, json.loads(path.read_text(encoding="utf-8"))
    names = ", ".join(str(path.relative_to(REPO_ROOT)) for path in SOURCE_CANDIDATES)
    raise FileNotFoundError(f"No final-ending professional reference found. Tried: {names}")


def as_measure_number(item: dict[str, Any]) -> int | None:
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
                pass
    return None


def event_lists(measure: dict[str, Any]) -> dict[str, list[Any]]:
    result: dict[str, list[Any]] = {}
    for key, value in measure.items():
        if isinstance(value, list) and value:
            result[key] = value
    return result


def compact_event(event: Any) -> Any:
    if not isinstance(event, dict):
        return event
    keep = (
        "quantizedStep",
        "step",
        "position",
        "positionInMeasure",
        "durationSteps",
        "duration",
        "start",
        "end",
        "string",
        "stringIndex",
        "fret",
        "midiPitch",
        "midi",
        "pitch",
        "notes",
        "techniques",
        "referenceConfidence",
        "confidence",
        "sourceDerived",
        "humanValidated",
        "readOnly",
    )
    return {key: event.get(key) for key in keep if key in event}


def main() -> None:
    source_path, payload = load_source()
    measures = payload.get("measures") or payload.get("measureReports") or []
    if not isinstance(measures, list):
        raise TypeError("Professional reference does not expose a list under measures/measureReports")

    reports: list[dict[str, Any]] = []
    total_events = 0

    for item in measures:
        if not isinstance(item, dict):
            continue
        number = as_measure_number(item)
        if number is None or not ENDING_START <= number <= ENDING_END:
            continue

        lists = event_lists(item)
        summarized_lists = {
            key: {
                "count": len(value),
                "sample": [compact_event(event) for event in value[:20]],
            }
            for key, value in lists.items()
        }
        event_count = sum(len(value) for value in lists.values())
        total_events += event_count

        reports.append({
            "measureNumber": number,
            "section": item.get("section") or item.get("sectionLabel"),
            "meter": item.get("meter"),
            "measureFlags": item.get("measureFlags") or {},
            "humanReview": item.get("humanReview") or {},
            "listFields": summarized_lists,
            "eventCountAcrossLists": event_count,
            "topLevelKeys": sorted(item.keys()),
        })

    reports.sort(key=lambda item: item["measureNumber"])
    found_measures = [item["measureNumber"] for item in reports]

    report = {
        "schemaVersion": 1,
        "auditType": "final-ending-professional-reference-content",
        "source": str(source_path.relative_to(REPO_ROOT)),
        "measureRange": [ENDING_START, ENDING_END],
        "foundMeasures": found_measures,
        "missingMeasures": [
            measure
            for measure in range(ENDING_START, ENDING_END + 1)
            if measure not in found_measures
        ],
        "eventCountAcrossLists": total_events,
        "measureReports": reports,
        "interpretation": (
            "Measures 111-113 are present in the professional rhythm reference even though "
            "they are absent from the chorus-ranking source. This audit exposes their exact "
            "event-bearing list fields and review metadata before deciding whether the ending "
            "is silent, sustained, or contains explicit rhythm articulations."
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

    print("Final-ending professional-reference content audit V1 complete")
    print("Source:", report["source"])
    print("Found measures:", report["foundMeasures"])
    print("Missing measures:", report["missingMeasures"])
    print("Events across list fields:", report["eventCountAcrossLists"])
    print()

    for item in reports:
        counts = {
            key: value["count"]
            for key, value in item["listFields"].items()
        }
        print(
            f"measure {item['measureNumber']} "
            f"section={item['section']} "
            f"listCounts={counts} "
            f"flags={item['measureFlags']} "
            f"reviewStatus={item['humanReview'].get('status')}"
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
