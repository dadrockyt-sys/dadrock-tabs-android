from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-audit.json"

START_MEASURE = 81
END_MEASURE = 96
EXPECTED = set(range(START_MEASURE, END_MEASURE + 1))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def section_for_measure(number: int) -> tuple[str, str]:
    if 81 <= number <= 91:
        return "Solo", "Solo rhythm backing continuation"
    if 92 <= number <= 94:
        return "Solo", "Solo ending transition"
    return "Post-Solo Riff", "Em riff return"


def main() -> None:
    source = load_json(REFERENCE)
    measures = [
        item for item in source.get("measures", [])
        if START_MEASURE <= int(item.get("measureNumber", -1)) <= END_MEASURE
    ]
    found = {int(item.get("measureNumber", -1)) for item in measures}
    if found != EXPECTED:
        raise RuntimeError(
            f"Chunk coverage mismatch missing={sorted(EXPECTED - found)} extra={sorted(found - EXPECTED)}"
        )

    prepared: list[dict[str, Any]] = []
    for measure in sorted(measures, key=lambda item: int(item["measureNumber"])):
        number = int(measure["measureNumber"])
        section, variant = section_for_measure(number)
        prepared.append({
            "measureNumber": number,
            "section": section,
            "sectionVariant": variant,
            "timeSignature": measure.get("timeSignature", "4/4"),
            "tempoBpm": measure.get("tempoBpm", 129),
            "sixteenthSlots": list(range(16)),
            "source": measure.get("source", {}),
            "events": measure.get("events", []),
            "measureFlags": {
                "pickup": False,
                "partialEnding": False,
                "containsRest": number in (93, 94),
                "containsTieAcrossBarline": number in (93, 94),
                "containsChordOrDoubleStop": 81 <= number <= 94,
                "containsTechnique": number in (93, 94, 95, 96),
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
        "sourcePages": [6, 7],
        "readyForTraining": False,
        "humanValidationRequired": True,
        "trainingMayStartFromThisChunk": False,
        "soloBackingRange": [81, 91],
        "soloEndingTransitionRange": [92, 94],
        "postSoloEmReturnRange": [95, 96],
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
        "sectionCounts": {
            "Solo": sum(1 for item in prepared if item["section"] == "Solo"),
            "Post-Solo Riff": sum(1 for item in prepared if item["section"] == "Post-Solo Riff"),
        },
        "humanValidatedMeasures": 0,
        "readyForTraining": False,
        "nextRequiredStage": "populate-and-validate-measures-81-96",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 81-96 prepared")
    print(f"Measures present: {len(prepared)}")
    print(f"Measures with source location: {sum(1 for item in prepared if item.get('source'))}")
    print("Sections: Solo backing=81-91, Solo ending transition=92-94, Post-Solo Em return=95-96")
    print("Measures human validated: 0")
    print("Ready for training: False")
    print(f"Chunk: {OUTPUT.relative_to(ROOT)}")
    print(f"Audit: {AUDIT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
