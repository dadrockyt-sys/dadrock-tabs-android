from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated-audit.json"


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


def chord(step: int, duration: int, frets_by_string: dict[int, int], techniques: list[str] | None = None, confidence: float = 0.82) -> dict[str, Any]:
    return event(
        step,
        duration,
        [note(string, fret) for string, fret in sorted(frets_by_string.items())],
        techniques or ["chord"],
        confidence,
    )


def em_riff(include_terminal_double_stop: bool) -> list[dict[str, Any]]:
    values = [
        event(0, 3, [note(3, 2)], ["full-bend", "bend-release"], 0.98),
        event(3, 2, [note(3, 0)], [], 0.98),
        event(5, 3, [note(4, 2)], [], 0.98),
        event(8, 2, [note(5, 0)], [], 0.98),
        event(10, 2, [note(4, 0)], [], 0.98),
        event(12, 3, [note(4, 2)], [], 0.98),
    ]
    if include_terminal_double_stop:
        values.append(event(15, 1, [note(2, 3), note(3, 3)], ["double-stop", "staccato"], 0.96))
    else:
        values.append(event(15, 1, [note(5, 0)], [], 0.98))
    return values


def chorus_measure(number: int) -> list[dict[str, Any]]:
    # Chord voicings are transcribed from the visible professional-reference shapes.
    # They remain below full confidence until the chord stacks are visually reviewed.
    if number == 33:
        return [
            chord(0, 4, {1: 0, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3}, ["chord", "let-ring"], 0.80),
            chord(4, 4, {1: 0, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3}, ["chord", "let-ring"], 0.80),
            chord(8, 8, {1: 0, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3}, ["chord", "let-ring", "tie"], 0.80),
        ]
    if number == 34:
        return [
            chord(0, 4, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring"], 0.82),
            chord(4, 4, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring"], 0.82),
            chord(8, 8, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring", "tie"], 0.82),
        ]
    if number == 35:
        return [
            chord(0, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(2, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(4, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(6, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(8, 2, {2: 7, 3: 7, 4: 7, 5: 7}, ["chord", "downstroke"], 0.76),
            chord(10, 6, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "let-ring"], 0.78),
        ]
    if number == 36:
        return [
            chord(0, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(2, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(4, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(6, 2, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "downstroke"], 0.78),
            chord(8, 2, {2: 12, 3: 12, 4: 12, 5: 12}, ["chord", "downstroke"], 0.76),
            chord(10, 6, {2: 9, 3: 9, 4: 9, 5: 9}, ["chord", "let-ring"], 0.78),
        ]
    if number == 37:
        return [
            chord(0, 8, {1: 0, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3}, ["chord", "let-ring"], 0.80),
            chord(8, 8, {1: 0, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3}, ["chord", "let-ring"], 0.80),
        ]
    return [
        chord(0, 4, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring"], 0.82),
        chord(4, 4, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring"], 0.82),
        chord(8, 8, {1: 0, 2: 0, 3: 2, 4: 2, 5: 2}, ["chord", "let-ring", "tie"], 0.82),
    ]


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(33, 49)):
        raise RuntimeError("Expected complete measures 33-48 chunk")

    for number in range(33, 49):
        measure = by_measure[number]
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        if 33 <= number <= 38:
            measure["section"] = "Chorus 1"
            measure["sectionVariant"] = "Chord chorus"
            measure["events"] = chorus_measure(number)
        elif 39 <= number <= 46:
            measure["section"] = "Riff"
            measure["sectionVariant"] = "Em riff with alternating double-stop ending"
            measure["events"] = deepcopy(em_riff(include_terminal_double_stop=(number % 2 == 0)))
        else:
            measure["section"] = "Verse 2"
            measure["sectionVariant"] = "Em riff"
            measure["events"] = deepcopy(em_riff(include_terminal_double_stop=False))

        flags = measure.setdefault("measureFlags", {})
        flags.update({
            "pickup": False,
            "partialEnding": False,
            "containsRest": number in (35, 36, 38),
            "containsTieAcrossBarline": False,
            "containsChordOrDoubleStop": 33 <= number <= 38 or (39 <= number <= 46 and number % 2 == 0),
            "containsTechnique": True,
        })
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 3-4. "
                "Priority review: chorus chord voicings and exact chorus attack durations."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(33, 49)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [3, 4]
    packet["professionalReferenceUsedForScoringOnly"] = True
    packet["humanValidationRequired"] = True
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    total_events = sum(len(item.get("events", [])) for item in packet["measures"])
    low_confidence = [
        {"measureNumber": item["measureNumber"], "step": evt.get("quantizedStep"), "confidence": evt.get("referenceConfidence")}
        for item in packet["measures"]
        for evt in item.get("events", [])
        if float(evt.get("referenceConfidence", 0.0)) < 0.85
    ]
    audit = {
        "chunk": [33, 48],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": total_events,
        "sectionLabels": sorted({item.get("section") for item in packet["measures"]}),
        "machineTranscribedMeasures": 16,
        "humanApprovedMeasures": 0,
        "lowConfidenceEvents": low_confidence,
        "priorityReviewMeasures": [33, 34, 35, 36, 37, 38],
        "readyForTraining": False,
        "nextRequiredStage": "validate-and-human-review-measures-33-48",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 33-48 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", total_events)
    print("Low-confidence events:", len(low_confidence))
    print("Priority review measures: 33-38")
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
