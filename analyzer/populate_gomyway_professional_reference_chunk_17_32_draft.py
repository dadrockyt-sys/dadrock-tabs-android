from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHUNK = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-populated.json"
AUDIT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-populated-audit.json"

# Guitar strings are numbered 1=high e through 6=low E.
# This is a source-derived draft from professional-reference pages 2-3.
# It is deliberately not human-approved and cannot unlock training by itself.

STANDARD_RIFF_STEPS = [0, 3, 5, 8, 10, 12, 15]


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


def g_riff() -> list[dict[str, Any]]:
    return [
        event(0, 3, [note(3, 5)], ["full-bend", "bend-release"], 0.97),
        event(3, 2, [note(3, 3)], [], 0.97),
        event(5, 3, [note(4, 5)], [], 0.97),
        event(8, 2, [note(5, 3)], [], 0.97),
        event(10, 2, [note(4, 3)], [], 0.97),
        event(12, 3, [note(4, 5)], ["vibrato"], 0.92),
        event(15, 1, [note(5, 3)], [], 0.97),
    ]


def muted_measure_28() -> list[dict[str, Any]]:
    # Page 3 shows a single-string muted/strummed figure. Exact attack positions
    # follow the visible sixteenth-note grouping; the grace/rest-like mark before
    # fret 3 remains lower confidence pending human review.
    values: list[tuple[int, int | None, list[str], float]] = [
        (0, None, ["dead-note", "downstroke"], 0.94),
        (1, 5, ["upstroke"], 0.94),
        (3, None, ["dead-note", "downstroke"], 0.94),
        (4, 4, ["upstroke"], 0.94),
        (6, 3, ["downstroke", "grace-or-rake"], 0.72),
        (8, None, ["dead-note", "upstroke"], 0.94),
        (9, 2, ["downstroke"], 0.94),
        (11, None, ["dead-note", "downstroke"], 0.94),
        (12, 4, ["upstroke"], 0.94),
        (14, None, ["dead-note", "upstroke"], 0.94),
    ]
    output: list[dict[str, Any]] = []
    for index, (step, fret, techniques, confidence) in enumerate(values):
        next_step = values[index + 1][0] if index + 1 < len(values) else 16
        notes = [note(3, fret)] if fret is not None else [note(3, -1)]
        output.append(event(step, max(1, next_step - step), notes, techniques, confidence))
    return output


def main() -> None:
    if not CHUNK.exists():
        raise FileNotFoundError(f"Missing prerequisite: {CHUNK.relative_to(ROOT)}")
    packet = json.loads(CHUNK.read_text(encoding="utf-8"))
    by_measure = {int(item["measureNumber"]): item for item in packet.get("measures", [])}
    if set(by_measure) != set(range(17, 33)):
        raise RuntimeError("Expected complete measures 17-32 chunk")

    for number in range(17, 33):
        measure = by_measure[number]
        measure["section"] = "Verse 1"
        measure["sectionVariant"] = (
            "Em riff" if number in list(range(17, 25)) + list(range(29, 33))
            else ("G riff" if number in (25, 26, 27) else "Muted turnaround")
        )
        measure["timeSignature"] = "4/4"
        measure["tempoBpm"] = 129
        if number in list(range(17, 25)) + list(range(29, 33)):
            measure["events"] = deepcopy(em_riff())
        elif number in (25, 26, 27):
            measure["events"] = deepcopy(g_riff())
        else:
            measure["events"] = muted_measure_28()

        flags = measure.setdefault("measureFlags", {})
        flags.update({
            "pickup": False,
            "partialEnding": False,
            "containsRest": number == 28,
            "containsTieAcrossBarline": False,
            "containsChordOrDoubleStop": False,
            "containsTechnique": True,
        })
        measure["humanReview"] = {
            "status": "machine-transcribed-pending-human-review",
            "reviewedBy": None,
            "reviewedAt": None,
            "notes": (
                "Source-derived draft from professional PDF pages 2-3. "
                "Verify sixteenth slots, durations, string choice, bend semantics, and measure 28 strokes."
            ),
        }

    packet["measures"] = [by_measure[number] for number in range(17, 33)]
    packet["readyForTraining"] = False
    packet["trainingMayStartFromThisChunk"] = False
    packet["draftPopulationComplete"] = True
    packet["draftSourcePages"] = [2, 3]
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
        "chunk": [17, 32],
        "measuresPresent": len(packet["measures"]),
        "measuresWithEvents": sum(1 for item in packet["measures"] if item.get("events")),
        "totalReferenceEvents": total_events,
        "sectionLabels": sorted({item.get("section") for item in packet["measures"]}),
        "timeSignatures": sorted({item.get("timeSignature") for item in packet["measures"]}),
        "tempoValues": sorted({item.get("tempoBpm") for item in packet["measures"]}),
        "machineTranscribedMeasures": 16,
        "humanApprovedMeasures": 0,
        "lowConfidenceEvents": low_confidence,
        "readyForTraining": False,
        "nextRequiredStage": "render-semantic-audit-and-human-review-measures-17-32",
        "protectedBaselinesChanged": False,
    }
    AUDIT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference draft 17-32 populated")
    print("Measures populated:", len(packet["measures"]))
    print("Reference events:", total_events)
    print("Low-confidence events:", len(low_confidence))
    print("Human approved measures: 0")
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
