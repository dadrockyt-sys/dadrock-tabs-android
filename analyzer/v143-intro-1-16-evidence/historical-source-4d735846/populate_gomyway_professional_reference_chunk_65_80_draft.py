from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated-audit.json"


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


def chord(notes: list[tuple[int, int]], confidence: float = 0.86, techniques: list[str] | None = None) -> list[dict[str, Any]]:
    return [event(0, 16, [note(s, f) for s, f in notes], techniques or ["sustain"], confidence)]


def repeated_chord(attacks: list[int], notes: list[tuple[int, int]], confidence: float, techniques: list[str] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, step in enumerate(attacks):
        next_step = attacks[i + 1] if i + 1 < len(attacks) else 16
        out.append(event(step, max(1, next_step - step), [note(s, f) for s, f in notes], techniques or [], confidence))
    return out


def chorus_measure_65() -> list[dict[str, Any]]:
    # Professional reference page 5: repeated E power-chord attacks followed by D then E.
    out: list[dict[str, Any]] = []
    for step in (0, 2, 4, 6, 8):
        out.append(event(step, 2, [note(3, 9), note(4, 9), note(5, 7)], [], 0.88))
    out.append(event(10, 2, [note(3, 7), note(4, 7), note(5, 5)], [], 0.86))
    out.append(event(12, 4, [note(3, 9), note(4, 9), note(5, 7)], ["sustain"], 0.88))
    return out


def chorus_measure_66() -> list[dict[str, Any]]:
    return [
        event(0, 6, [note(2, 0), note(3, 0), note(4, 3), note(5, 4), note(6, 5)], ["sustain"], 0.84),
        event(8, 6, [note(2, 0), note(3, 0), note(4, 2), note(5, 2), note(6, 0)], ["sustain"], 0.84),
    ]


def chorus_measure_67() -> list[dict[str, Any]]:
    return repeated_chord([0, 4, 8, 12], [(2, 0), (3, 0), (4, 3), (5, 4), (6, 5)], 0.83)


def chorus_measure_68() -> list[dict[str, Any]]:
    # Rest/empty continuation at end of chorus in the professional reference.
    return [event(0, 16, [], ["rest"], 0.94)]


def bridge_e() -> list[dict[str, Any]]:
    return repeated_chord([0, 4, 8, 12], [(3, 9), (4, 9), (5, 9), (6, 7)], 0.88)


def bridge_d() -> list[dict[str, Any]]:
    return [
        event(0, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.86),
        event(4, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.82),
        event(8, 4, [note(3, 7), note(4, 7), note(5, 7), note(6, 5)], [], 0.86),
        event(12, 4, [note(3, -1), note(4, -1), note(5, -1)], ["dead-note"], 0.82),
    ]


def bridge_a() -> list[dict[str, Any]]:
    return [
        event(0, 4, [note(2, 5), note(3, 6), note(4, 7), note(5, 7)], ["sustain"], 0.86),
        event(8, 4, [note(2, 7), note(3, 7), note(4, 7)], [], 0.84),
        event(12, 4, [note(2, 5), note(3, 6), note(4, 7)], [], 0.84),
    ]


def bridge_e_resolution() -> list[dict[str, Any]]:
    return chord([(2, 9), (3, 9), (4, 9), (5, 7)], 0.88, ["sustain"])


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(65, 81)):
        raise RuntimeError("Expected complete measures 65-80 chunk")

    events_by_measure: dict[int, list[dict[str, Any]]] = {
        65: chorus_measure_65(),
        66: chorus_measure_66(),
        67: chorus_measure_67(),
        68: chorus_measure_68(),
    }

    # Bridge and solo-backing progression visible on professional pages 5-6.
    progression = {
        69: bridge_e(), 70: bridge_d(), 71: bridge_a(), 72: bridge_e_resolution(),
        73: bridge_e(), 74: bridge_d(), 75: bridge_a(), 76: bridge_e_resolution(),
        77: bridge_e(), 78: bridge_d(), 79: bridge_a(), 80: bridge_e_resolution(),
    }
    events_by_measure.update(progression)

    for number in range(65, 81):
        measure = by_measure[number]
        if number <= 68:
            section = "Chorus 2"
            variant = "Chorus completion"
        elif number <= 77:
            section = "Bridge"
            variant = "E-D-A-E progression"
        else:
            section = "Solo"
            variant = "Rhythm backing E-D-A-E"
        measure["section"] = section
        measure["sectionVariant"] = variant
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        measure["events"] = deepcopy(events_by_measure[number])
        measure["measureFlags"] = {
            "pickup": False,
            "partialEnding": False,
            "containsRest": number == 68,
            "containsTieAcrossBarline": False,
            "containsChordOrDoubleStop": number != 68,
            "containsTechnique": any(evt.get("techniques") for evt in events_by_measure[number]),
        }
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 5-6. "
                "Verify chorus chord voicings, dead-note attacks, and bridge/solo-backing chord stacks."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(65, 81)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [5, 6]
    packet["professionalReferenceUsedForScoringOnly"] = True
    packet["humanValidationRequired"] = True
    packet["fullCrossChorusConsensusNowPossible"] = True
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    low_confidence = [
        {"measureNumber": item["measureNumber"], "step": evt.get("quantizedStep"), "confidence": evt.get("referenceConfidence")}
        for item in packet["measures"]
        for evt in item.get("events", [])
        if float(evt.get("referenceConfidence", 0.0)) < 0.85
    ]
    audit = {
        "chunk": [65, 80],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": sum(len(item.get("events", [])) for item in packet["measures"]),
        "sectionCounts": {
            "Chorus 2": 4,
            "Bridge": 9,
            "Solo": 3,
        },
        "lowConfidenceEvents": low_confidence,
        "priorityReviewMeasures": [65, 66, 67, 69, 70, 71, 73, 74, 75, 77, 78, 79, 80],
        "fullCrossChorusConsensusPossible": True,
        "humanApprovedMeasures": 0,
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 65-80 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", audit["totalReferenceEvents"])
    print("Low-confidence events:", len(low_confidence))
    print("Priority review measures:", audit["priorityReviewMeasures"])
    print("Full cross-chorus consensus possible: True")
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
