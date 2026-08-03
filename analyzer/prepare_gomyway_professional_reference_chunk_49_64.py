from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-audit.json"

START_MEASURE = 49
END_MEASURE = 64
EXPECTED = set(range(START_MEASURE, END_MEASURE + 1))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def section_for_measure(number: int) -> tuple[str, str]:
    if 49 <= number <= 62:
        return "Verse 2", "Verse 2 continuation"
    return "Chorus 2", "Chorus 2 opening"


def main() -> None:
    source = load_json(REFERENCE)
    measures = [
        item for item in source.get("measures", [])
        if START_MEASURE <= int(item.get("measureNumber", -1)) <= END_MEASURE
    ]
    found = {int(item.get("measureNumber", -1)) for item in measures}
    if found != EXPECTED:
        raise RuntimeError(
            f"Chunk coverage mismatch missing={sorted(EXPECTED-found)} extra={sorted(found-EXPECTED)}"
        )

    prepared: list[dict[str, Any]] = []
    for measure in sorted(measures, key=lambda item: int(item["measureNumber"])):
        number = int(measure["measureNumber"])
        section, variant = section_for_measure(number)
        prepared.append({
            "measureNumber": number,
            "section": section,
            "sectionVariant": variant,
            "timeSignature": "4/4",
            "tempoBpm": 129,
            "sixteenthSlots": list(range(16)),
            "source": measure.get("source", {}),
            "events": measure.get("events", []),
            "measureFlags": {
                "pickup": False,
                "partialEnding": False,
                "containsRest": False,
                "containsTieAcrossBarline": False,
                "containsChordOrDoubleStop": section == "Chorus 2",
                "containsTechnique": True,
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
        "sections": {
            "Verse 2": [49, 62],
            "Chorus 2 opening": [63, 64],
        },
        "humanValidatedMeasures": 0,
        "measuresWithEvents": sum(1 for item in prepared if item.get("events")),
        "readyForTraining": False,
        "nextRequiredStage": "populate-and-human-validate-measures-49-64",
        "chorusCrossCheckPlan": "Use measures 63-68 to resolve Chorus 1 measures 33-38 by repeated-section consensus.",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 49-64 prepared")
    print("Measures present:", len(prepared))
    print("Measures with source location:", sum(1 for item in prepared if item.get("source")))
    print("Sections: Verse 2=49-62, Chorus 2 opening=63-64")
    print("Measures human validated: 0")
    print("Ready for training: False")
    print("Cross-check plan: Chorus 2 will resolve Chorus 1 warnings")
    print("Chunk:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))


if __name__ == "__main__":
    main()
