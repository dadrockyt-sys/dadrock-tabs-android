from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
OUTPUT = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
AUDIT = PUBLIC / "gomyway-professional-rhythm-reference-17-113-audit.json"

MEASURE_START = 17
MEASURE_END = 113


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_locations() -> dict[int, dict[str, Any]]:
    locations: dict[int, dict[str, Any]] = {}
    if not SOURCE.exists():
        return locations
    data = load_json(SOURCE)
    for job in data.get("recognitionJobs", []):
        for measure in job.get("measures", []):
            try:
                number = int(measure)
            except (TypeError, ValueError):
                continue
            locations[number] = {
                "pageNumber": job.get("pageNumber"),
                "rowIndex": job.get("rowIndex"),
                "sourceCrop": job.get("crop") or job.get("sourceCrop") or job.get("cropPath"),
            }
    return locations


def empty_measure(number: int, location: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "measureNumber": number,
        "section": None,
        "sectionVariant": None,
        "timeSignature": "4/4",
        "tempoBpm": None,
        "sixteenthSlotsPerMeasure": 16,
        "events": [],
        "transition": None,
        "source": location or {},
        "referenceStatus": "awaiting-semantic-transcription",
        "humanValidated": False,
    }


def main() -> None:
    locations = source_locations()
    existing: dict[str, Any] = {}
    if OUTPUT.exists():
        existing = load_json(OUTPUT)
    existing_by_measure = {
        int(item.get("measureNumber")): item
        for item in existing.get("measures", [])
        if isinstance(item, dict) and item.get("measureNumber") is not None
    }

    measures = []
    for number in range(MEASURE_START, MEASURE_END + 1):
        if number in existing_by_measure:
            item = existing_by_measure[number]
            item.setdefault("source", locations.get(number, {}))
            item.setdefault("sixteenthSlotsPerMeasure", 16)
            item.setdefault("referenceStatus", "awaiting-semantic-transcription")
            item.setdefault("humanValidated", False)
            measures.append(item)
        else:
            measures.append(empty_measure(number, locations.get(number)))

    reference = {
        "schemaVersion": 1,
        "referenceName": "Gomyway professional rhythm semantic reference measures 17-113",
        "instrument": "rhythm-guitar",
        "stringCount": 6,
        "measureStart": MEASURE_START,
        "measureEnd": MEASURE_END,
        "timingGrid": "sixteenth-note",
        "professionalReferenceReadOnly": True,
        "semanticReferenceFinalized": False,
        "measures": measures,
        "protectedBaselines": {
            "lockedMeasures1To16Modified": False,
            "v7EventsModified": False,
            "rendererModified": False,
            "candidateAudioModified": False,
        },
    }
    OUTPUT.write_text(json.dumps(reference, indent=2) + "\n", encoding="utf-8")

    pending = [m["measureNumber"] for m in measures if not m.get("humanValidated")]
    missing_sections = [m["measureNumber"] for m in measures if not m.get("section")]
    audit = {
        "measuresExpected": MEASURE_END - MEASURE_START + 1,
        "measuresPresent": len(measures),
        "measuresWithSourceLocation": sum(bool(m.get("source")) for m in measures),
        "measuresHumanValidated": sum(bool(m.get("humanValidated")) for m in measures),
        "measuresPending": pending,
        "measuresMissingSection": missing_sections,
        "semanticReferenceFinalized": False,
        "readyForTraining": False,
        "nextRequiredStage": "transcribe-professional-musical-events-in-measure-chunks",
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference bootstrap complete")
    print(f"Measures present: {len(measures)}")
    print(f"Measures with source location: {audit['measuresWithSourceLocation']}")
    print(f"Measures human validated: {audit['measuresHumanValidated']}")
    print("Ready for training: False")
    print(f"Reference: {OUTPUT.relative_to(ROOT)}")
    print(f"Audit: {AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
