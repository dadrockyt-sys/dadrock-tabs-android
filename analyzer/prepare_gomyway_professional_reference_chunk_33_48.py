from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-audit.json"

START_MEASURE = 33
END_MEASURE = 48
EXPECTED = set(range(START_MEASURE, END_MEASURE + 1))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    source = load_json(REFERENCE)
    measures = [
        item for item in source.get("measures", [])
        if START_MEASURE <= int(item.get("measureNumber", -1)) <= END_MEASURE
    ]
    found = {int(item.get("measureNumber", -1)) for item in measures}
    if found != EXPECTED:
        missing = sorted(EXPECTED - found)
        extra = sorted(found - EXPECTED)
        raise RuntimeError(f"Chunk coverage mismatch missing={missing} extra={extra}")

    prepared: list[dict[str, Any]] = []
    for measure in sorted(measures, key=lambda item: int(item["measureNumber"])):
        number = int(measure["measureNumber"])
        if 33 <= number <= 38:
            section = "Chorus 1"
        elif 39 <= number <= 46:
            section = "Riff"
        else:
            section = "Verse 2"
        prepared.append({
            "measureNumber": number,
            "section": section,
            "sectionVariant": None,
            "timeSignature": measure.get("timeSignature", "4/4"),
            "tempoBpm": measure.get("tempoBpm", 129),
            "sixteenthSlots": list(range(16)),
            "source": measure.get("source", {}),
            "events": measure.get("events", []),
            "measureFlags": {
                "pickup": False,
                "partialEnding": False,
                "containsRest": False,
                "containsTieAcrossBarline": False,
                "containsChordOrDoubleStop": False,
                "containsTechnique": False,
            },
            "humanReview": {
                "status": "pending",
                "reviewedBy": None,
                "reviewedAt": None,
                "notes": "",
            },
        })

    packet = {
        "schemaVersion": 1,
        "referenceType": "professional-rhythm-semantic-reference-chunk",
        "instrument": "rhythm-guitar",
        "measureStart": START_MEASURE,
        "measureEnd": END_MEASURE,
        "timingGrid": "sixteenth-note",
        "timingSlotsPerFourFourMeasure": 16,
        "sourceReference": str(REFERENCE.relative_to(ROOT)),
        "readyForTraining": False,
        "humanValidationRequired": True,
        "trainingMayStartFromThisChunk": False,
        "measures": prepared,
        "protectedRules": {
            "lockedMeasures1To16Modified": False,
            "v7EventsModified": False,
            "rendererModified": False,
            "professionalReferenceSourceModified": False,
            "candidateAudioModified": False,
        },
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    audit = {
        "chunk": [START_MEASURE, END_MEASURE],
        "measuresPresent": len(prepared),
        "allMeasuresHaveSourceLocation": all(bool(item.get("source")) for item in prepared),
        "sectionCoverage": {
            "Chorus 1": [33, 38],
            "Riff": [39, 46],
            "Verse 2 start": [47, 48],
        },
        "humanValidatedMeasures": 0,
        "measuresWithEvents": sum(1 for item in prepared if item.get("events")),
        "readyForTraining": False,
        "nextRequiredStage": "populate-and-human-validate-measures-33-48",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 33-48 prepared")
    print(f"Measures present: {len(prepared)}")
    print(f"Measures with source location: {sum(1 for item in prepared if item.get('source'))}")
    print("Sections: Chorus 1=33-38, Riff=39-46, Verse 2 start=47-48")
    print("Measures human validated: 0")
    print("Ready for training: False")
    print(f"Chunk: {OUTPUT.relative_to(ROOT)}")
    print(f"Audit: {AUDIT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
