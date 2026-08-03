from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated-audit.json"


def note(string: int, fret: int) -> dict[str, int]:
    return {"string": string, "fret": fret}


def event(step: int, duration: int, notes: list[dict[str, int]], techniques: list[str] | None = None, confidence: float = 0.95) -> dict[str, Any]:
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
        event(3, 2, [note(3, 0)], confidence=0.98),
        event(5, 3, [note(4, 2)], confidence=0.98),
        event(8, 2, [note(5, 0)], confidence=0.98),
        event(10, 2, [note(4, 0)], confidence=0.98),
        event(12, 3, [note(4, 2)], confidence=0.98),
        event(15, 1, [note(5, 0)], confidence=0.98),
    ]


def g_riff() -> list[dict[str, Any]]:
    return [
        event(0, 3, [note(3, 5)], ["full-bend", "bend-release"], 0.97),
        event(3, 2, [note(3, 3)], confidence=0.97),
        event(5, 3, [note(4, 5)], confidence=0.97),
        event(8, 2, [note(5, 3)], confidence=0.97),
        event(10, 2, [note(4, 3)], confidence=0.97),
        event(12, 3, [note(4, 5)], ["vibrato"], 0.92),
        event(15, 1, [note(5, 3)], confidence=0.97),
    ]


def muted_turnaround() -> list[dict[str, Any]]:
    pattern = [
        (0, None, ["dead-note", "downstroke"], 0.94),
        (1, 5, ["upstroke"], 0.94),
        (3, None, ["dead-note", "downstroke"], 0.94),
        (4, 4, ["upstroke"], 0.94),
        (6, 3, ["muted-grace-rake", "downstroke"], 0.90),
        (8, None, ["dead-note", "upstroke"], 0.94),
        (9, 2, ["downstroke"], 0.94),
        (11, None, ["dead-note", "downstroke"], 0.94),
        (12, 4, ["upstroke"], 0.94),
        (14, None, ["dead-note", "upstroke"], 0.94),
    ]
    out: list[dict[str, Any]] = []
    for index, (step, fret, tech, conf) in enumerate(pattern):
        next_step = pattern[index + 1][0] if index + 1 < len(pattern) else 16
        out.append(event(step, max(1, next_step - step), [note(3, fret if fret is not None else -1)], tech, conf))
    return out


def chord(strings_and_frets: list[tuple[int, int]], step: int, duration: int, confidence: float = 0.78, techniques: list[str] | None = None) -> dict[str, Any]:
    return event(step, duration, [note(s, f) for s, f in strings_and_frets], techniques or ["strum"], confidence)


def chorus_measure_63() -> list[dict[str, Any]]:
    # G6 figure from the professional reference, matched to Chorus 1 measure 33.
    shape = [(6, 3), (5, 5), (4, 4), (3, 3)]
    return [
        chord(shape, 0, 2, 0.80),
        chord(shape, 2, 2, 0.80),
        chord(shape, 4, 4, 0.80, ["strum", "let-ring"]),
        chord(shape, 8, 4, 0.76, ["strum", "tie-or-sustain"]),
        event(12, 4, [note(6, -1)], ["rest"], 0.82),
    ]


def chorus_measure_64() -> list[dict[str, Any]]:
    # A(add2) figure from the professional reference, matched to Chorus 1 measure 34.
    shape = [(6, 0), (5, 0), (4, 2), (3, 2), (2, 2)]
    return [
        chord(shape, 0, 3, 0.80),
        chord(shape, 3, 3, 0.80),
        chord(shape, 6, 4, 0.78, ["strum", "let-ring"]),
        chord(shape, 10, 6, 0.76, ["strum", "tie-or-sustain"]),
    ]


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(49, 65)):
        raise RuntimeError("Expected complete measures 49-64 chunk")

    for number in range(49, 65):
        measure = by_measure[number]
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        if 49 <= number <= 54 or 59 <= number <= 62:
            measure["section"] = "Verse 2"
            measure["sectionVariant"] = "Em riff"
            measure["events"] = deepcopy(em_riff())
        elif 55 <= number <= 57:
            measure["section"] = "Verse 2"
            measure["sectionVariant"] = "G riff"
            measure["events"] = deepcopy(g_riff())
        elif number == 58:
            measure["section"] = "Verse 2"
            measure["sectionVariant"] = "Muted turnaround"
            measure["events"] = muted_turnaround()
        elif number == 63:
            measure["section"] = "Chorus 2"
            measure["sectionVariant"] = "G6 opening"
            measure["events"] = chorus_measure_63()
        else:
            measure["section"] = "Chorus 2"
            measure["sectionVariant"] = "A(add2) opening"
            measure["events"] = chorus_measure_64()

        flags = measure.setdefault("measureFlags", {})
        flags.update({
            "pickup": False,
            "partialEnding": False,
            "containsRest": number in (58, 63),
            "containsTieAcrossBarline": False,
            "containsChordOrDoubleStop": number in (63, 64),
            "containsTechnique": True,
        })
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 4-5. "
                "Measures 63-64 are retained at lower confidence for cross-chorus consensus."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(49, 65)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [4, 5]
    packet["crossChorusConsensusMeasures"] = {"chorus1": [33, 34], "chorus2": [63, 64]}
    packet["professionalReferenceUsedForScoringOnly"] = True
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    low_confidence = [
        {"measureNumber": item["measureNumber"], "step": evt.get("quantizedStep"), "confidence": evt.get("referenceConfidence")}
        for item in packet["measures"]
        for evt in item.get("events", [])
        if float(evt.get("referenceConfidence", 0.0)) < 0.85
    ]
    total_events = sum(len(item.get("events", [])) for item in packet["measures"])
    audit = {
        "chunk": [49, 64],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": total_events,
        "lowConfidenceEvents": low_confidence,
        "priorityReviewMeasures": [63, 64],
        "crossChorusConsensusAvailable": True,
        "humanApprovedMeasures": 0,
        "readyForTraining": False,
        "nextRequiredStage": "validate-and-cross-check-measures-49-64",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 49-64 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", total_events)
    print("Low-confidence events:", len(low_confidence))
    print("Priority review measures: 63-64")
    print("Cross-chorus consensus available: True")
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
