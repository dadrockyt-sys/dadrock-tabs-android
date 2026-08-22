from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated-audit.json"


def note(string: int, fret: int) -> dict[str, int]:
    return {"string": string, "fret": fret}


def event(step: int, duration: int, notes: list[dict[str, int]], techniques: list[str] | None = None, confidence: float = 0.9) -> dict[str, Any]:
    return {
        "quantizedStep": step,
        "durationSteps": duration,
        "notes": notes,
        "techniques": techniques or [],
        "referenceConfidence": confidence,
        "sourceDerived": True,
        "humanValidated": False,
    }


def repeated_chord(attacks: list[int], notes: list[tuple[int, int]], confidence: float, techniques: list[str] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, step in enumerate(attacks):
        next_step = attacks[i + 1] if i + 1 < len(attacks) else 16
        out.append(event(step, max(1, next_step - step), [note(s, f) for s, f in notes], techniques or [], confidence))
    return out


def solo_e() -> list[dict[str, Any]]:
    return [
        event(0, 4, [note(3, 9), note(4, 9), note(5, 9), note(6, 7)], [], 0.89),
        event(4, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.84),
        event(8, 4, [note(3, 9), note(4, 9), note(5, 9), note(6, 7)], [], 0.89),
        event(12, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.84),
    ]


def solo_d() -> list[dict[str, Any]]:
    return [
        event(0, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.87),
        event(4, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.83),
        event(8, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.87),
        event(12, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.87),
    ]


def solo_a_d6_a() -> list[dict[str, Any]]:
    return [
        event(0, 6, [note(2, 5), note(3, 6), note(4, 7), note(5, 7)], ["sustain"], 0.86),
        event(8, 4, [note(2, 7), note(3, 7), note(4, 7)], [], 0.84),
        event(12, 4, [note(2, 5), note(3, 6), note(4, 7)], [], 0.84),
    ]


def solo_transition_92() -> list[dict[str, Any]]:
    return [
        event(0, 4, [note(3, 9), note(4, 9), note(5, 9), note(6, 7)], [], 0.88),
        event(4, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.82),
        event(8, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.86),
        event(12, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.82),
    ]


def solo_transition_93() -> list[dict[str, Any]]:
    return [event(0, 16, [note(2, 7), note(3, 7), note(4, 7), note(5, 7)], ["tie", "sustain"], 0.78)]


def solo_transition_94() -> list[dict[str, Any]]:
    return [
        event(0, 8, [note(2, 7), note(3, 7), note(4, 7), note(5, 7)], ["tie", "sustain"], 0.78),
        event(8, 2, [note(3, -1)], ["dead-note"], 0.78),
        event(10, 2, [note(4, 4)], [], 0.83),
        event(12, 1, [note(4, 5)], [], 0.83),
        event(13, 1, [note(4, 6)], ["slide"], 0.79),
    ]


def em_riff() -> list[dict[str, Any]]:
    return [
        event(0, 3, [note(3, 2)], ["full-bend", "bend-release"], 0.98),
        event(3, 2, [note(3, 0)], [], 0.98),
        event(5, 3, [note(4, 2)], [], 0.98),
        event(8, 2, [note(5, 0)], [], 0.98),
        event(10, 2, [note(4, 0)], [], 0.98),
        event(12, 3, [note(4, 2)], [], 0.98),
        event(15, 1, [note(5, 0)], [], 0.98),
    ]


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(81, 97)):
        raise RuntimeError("Expected complete measures 81-96 chunk")

    events_by_measure: dict[int, list[dict[str, Any]]] = {}
    for start in (81, 84, 87, 90):
        events_by_measure[start] = solo_e()
        if start + 1 <= 91:
            events_by_measure[start + 1] = solo_d()
        if start + 2 <= 91:
            events_by_measure[start + 2] = solo_a_d6_a()

    events_by_measure[92] = solo_transition_92()
    events_by_measure[93] = solo_transition_93()
    events_by_measure[94] = solo_transition_94()
    events_by_measure[95] = em_riff()
    events_by_measure[96] = em_riff()

    for number in range(81, 97):
        measure = by_measure[number]
        if number <= 91:
            section = "Solo"
            variant = "Rhythm backing E-D-A/D6-A"
        elif number <= 94:
            section = "Solo"
            variant = "Solo ending transition"
        else:
            section = "Post-Solo"
            variant = "Em riff return"
        measure["section"] = section
        measure["sectionVariant"] = variant
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        measure["events"] = deepcopy(events_by_measure[number])
        measure["measureFlags"] = {
            "pickup": False,
            "partialEnding": False,
            "containsRest": False,
            "containsTieAcrossBarline": number in (93, 94),
            "containsChordOrDoubleStop": number <= 94,
            "containsTechnique": any(evt.get("techniques") for evt in events_by_measure[number]),
        }
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 6-7. "
                "Verify repeated solo-backing dead notes, measure 93-94 tied voicing, and transition run before Em return."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(81, 97)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [6, 7]
    packet["professionalReferenceUsedForScoringOnly"] = True
    packet["humanValidationRequired"] = True
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    low_confidence = [
        {"measureNumber": item["measureNumber"], "step": evt.get("quantizedStep"), "confidence": evt.get("referenceConfidence")}
        for item in packet["measures"]
        for evt in item.get("events", [])
        if float(evt.get("referenceConfidence", 0.0)) < 0.85
    ]
    audit = {
        "chunk": [81, 96],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": sum(len(item.get("events", [])) for item in packet["measures"]),
        "sectionCounts": {"Solo": 14, "Post-Solo": 2},
        "lowConfidenceEvents": low_confidence,
        "priorityReviewMeasures": sorted({item["measureNumber"] for item in low_confidence}),
        "humanApprovedMeasures": 0,
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 81-96 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", audit["totalReferenceEvents"])
    print("Low-confidence events:", len(low_confidence))
    print("Priority review measures:", audit["priorityReviewMeasures"])
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
