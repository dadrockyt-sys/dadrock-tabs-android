from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated-audit.json"


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


def repeated_chord(attacks: list[int], notes: list[tuple[int, int]], confidence: float = 0.86, techniques: list[str] | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for index, step in enumerate(attacks):
        next_step = attacks[index + 1] if index + 1 < len(attacks) else 16
        out.append(event(step, max(1, next_step - step), [note(s, f) for s, f in notes], techniques, confidence))
    return out


def out_chorus_measure(number: int) -> list[dict[str, Any]]:
    # Professional reference pages 7-8 show the recurring chorus vocabulary.
    if number in (103, 105, 109):
        return [event(0, 16, [note(2, 0), note(3, 0), note(4, 3), note(5, 4), note(6, 5)], ["sustain"], 0.86)]
    if number in (104, 106, 110):
        return [event(0, 16, [note(2, 0), note(3, 0), note(4, 2), note(5, 2), note(6, 0)], ["sustain"], 0.86)]
    if number in (107, 108):
        return repeated_chord([0, 2, 4, 6, 8, 10, 12], [(3, 9), (4, 9), (5, 7)], 0.88)
    raise ValueError(number)


def ending_measure(number: int) -> list[dict[str, Any]]:
    if number == 111:
        return [event(0, 16, [note(2, 0), note(3, 0), note(4, 2), note(5, 2), note(6, 0)], ["sustain", "tie-forward"], 0.88)]
    if number == 112:
        return [event(0, 16, [note(2, 0), note(3, 0), note(4, 2), note(5, 2), note(6, 0)], ["sustain", "tie-forward"], 0.88)]
    return [event(0, 16, [note(2, 0), note(3, 0), note(4, 2), note(5, 2), note(6, 0)], ["final-sustain", "fermata-or-stop"], 0.82)]


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(97, 114)):
        raise RuntimeError("Expected complete measures 97-113 chunk")

    for number in range(97, 114):
        measure = by_measure[number]
        if number <= 102:
            section, variant, events = "Post-Solo", "Em riff return", em_riff()
        elif number <= 110:
            section, variant, events = "Out-Chorus", "Final chorus progression", out_chorus_measure(number)
        else:
            section, variant, events = "Ending", "Sustained final resolution", ending_measure(number)

        measure["section"] = section
        measure["sectionVariant"] = variant
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        measure["events"] = deepcopy(events)
        measure["measureFlags"] = {
            "pickup": False,
            "partialEnding": number == 113,
            "containsRest": False,
            "containsTieAcrossBarline": number in (111, 112),
            "containsChordOrDoubleStop": number >= 103,
            "containsTechnique": any(evt.get("techniques") for evt in events),
        }
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 7-8. "
                "Verify out-chorus chord voicings, exact attack counts, ties, and the final stop in measure 113."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(97, 114)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [7, 8]
    packet["professionalReferenceUsedForScoringOnly"] = True
    packet["humanValidationRequired"] = True
    packet["finalReferenceChunk"] = True
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    low_confidence = [
        {"measureNumber": item["measureNumber"], "step": evt.get("quantizedStep"), "confidence": evt.get("referenceConfidence")}
        for item in packet["measures"]
        for evt in item.get("events", [])
        if float(evt.get("referenceConfidence", 0.0)) < 0.85
    ]
    audit = {
        "chunk": [97, 113],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": sum(len(item.get("events", [])) for item in packet["measures"]),
        "sectionCounts": {"Post-Solo": 6, "Out-Chorus": 8, "Ending": 3},
        "lowConfidenceEvents": low_confidence,
        "priorityReviewMeasures": [103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113],
        "humanApprovedMeasures": 0,
        "readyForTraining": False,
        "finalReferenceChunk": True,
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 97-113 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", audit["totalReferenceEvents"])
    print("Low-confidence events:", len(low_confidence))
    print("Priority review measures:", audit["priorityReviewMeasures"])
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Final reference chunk: True")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
