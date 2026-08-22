from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-audit.json"
START_MEASURE = 97
END_MEASURE = 113
EXPECTED = set(range(START_MEASURE, END_MEASURE + 1))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def section_for_measure(number: int) -> tuple[str, str]:
    if 97 <= number <= 102:
        return "Post-Solo", "Em riff return"
    if 103 <= number <= 106:
        return "Out-Chorus", "Opening chord sequence"
    if 107 <= number <= 110:
        return "Out-Chorus", "E-D-E / G-E / G6-A sequence"
    return "Ending", "Final sustained Alt(p2) resolution"


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
                "partialEnding": number == 113,
                "containsRest": False,
                "containsTieAcrossBarline": 110 <= number <= 113,
                "containsChordOrDoubleStop": number >= 103,
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
        "sourcePages": [7, 8],
        "readyForTraining": False,
        "humanValidationRequired": True,
        "trainingMayStartFromThisChunk": False,
        "finalChunk": True,
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

    section_counts: dict[str, int] = {}
    for item in prepared:
        section_counts[item["section"]] = section_counts.get(item["section"], 0) + 1
    audit = {
        "chunk": [START_MEASURE, END_MEASURE],
        "measuresPresent": len(prepared),
        "allMeasuresHaveSourceLocation": all(bool(item.get("source")) for item in prepared),
        "sectionCounts": section_counts,
        "humanValidatedMeasures": 0,
        "readyForTraining": False,
        "finalChunk": True,
        "nextRequiredStage": "populate-and-validate-measures-97-113",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 97-113 prepared")
    print(f"Measures present: {len(prepared)}")
    print(f"Measures with source location: {sum(1 for item in prepared if item.get('source'))}")
    print("Sections: Post-Solo=97-102, Out-Chorus=103-110, Ending=111-113")
    print("Measures human validated: 0")
    print("Ready for training: False")
    print("Final reference chunk: True")
    print(f"Chunk: {OUTPUT.relative_to(ROOT)}")
    print(f"Audit: {AUDIT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
