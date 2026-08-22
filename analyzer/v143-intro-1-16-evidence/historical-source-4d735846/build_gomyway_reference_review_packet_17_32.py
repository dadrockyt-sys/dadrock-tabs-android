from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-populated.json"
VALIDATION = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-validation.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-review-packet.json"
TEXT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-review-packet.txt"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def note_label(note: dict[str, Any]) -> str:
    string = note.get("string", "?")
    fret = note.get("fret", "?")
    return f"s{string}:x" if fret == -1 else f"s{string}:{fret}"


def event_label(event: dict[str, Any]) -> str:
    step = int(event.get("quantizedStep", 0))
    duration = int(event.get("durationSteps", 1))
    notes = "+".join(note_label(note) for note in event.get("notes", [])) or "rest"
    techniques = ",".join(event.get("techniques", [])) or "none"
    confidence = float(event.get("referenceConfidence", 0.0))
    return f"step={step:02d} dur={duration:02d} {notes} tech=[{techniques}] conf={confidence:.2f}"


def main() -> None:
    source = load(SOURCE)
    validation = load(VALIDATION)
    measures = source.get("measures", [])

    review_measures: list[dict[str, Any]] = []
    lines = [
        "GOMYWAY PROFESSIONAL RHYTHM REFERENCE REVIEW — MEASURES 17-32",
        "Sixteenth-note grid: 0..15 | strings: 1=high e, 6=low E",
        "Source reference pages: 2-3",
        "",
    ]

    for measure in measures:
        number = int(measure["measureNumber"])
        events = measure.get("events", [])
        warnings = [
            warning for warning in validation.get("warnings", [])
            if int(warning.get("measure", -1)) == number
        ]
        review_measures.append({
            "measureNumber": number,
            "section": measure.get("section"),
            "sectionVariant": measure.get("sectionVariant"),
            "timeSignature": measure.get("timeSignature"),
            "tempoBpm": measure.get("tempoBpm"),
            "events": events,
            "warnings": warnings,
            "humanDecision": "pending",
            "reviewNotes": "",
        })
        lines.append(
            f"MEASURE {number} | {measure.get('section')} | {measure.get('sectionVariant')} | "
            f"{measure.get('timeSignature')} | {measure.get('tempoBpm')} BPM"
        )
        for index, event in enumerate(events):
            marker = "  !" if any(int(w.get("event", -1)) == index for w in warnings) else "   "
            lines.append(f"{marker} event {index:02d}: {event_label(event)}")
        if warnings:
            lines.append(f"  REVIEW REQUIRED: {warnings}")
        lines.append("")

    packet = {
        "reviewPacketVersion": 1,
        "measureStart": 17,
        "measureEnd": 32,
        "sourceReferencePages": [2, 3],
        "validationPassed": validation.get("validDraft") is True,
        "errors": validation.get("errors", []),
        "warnings": validation.get("warnings", []),
        "humanApprovalRequired": True,
        "readyForTraining": False,
        "priorityReview": {
            "measureNumber": 28,
            "eventIndex": 4,
            "quantizedStep": 6,
            "reason": "low-confidence grace-or-rake-like attack",
        },
        "measures": review_measures,
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    TEXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Professional rhythm reference review packet 17-32 complete")
    print("Validation passed:", packet["validationPassed"])
    print("Measures included:", len(review_measures))
    print("Errors:", len(packet["errors"]))
    print("Warnings:", len(packet["warnings"]))
    print("Priority review: measure 28 event 4 step 6")
    print("Ready for training: False")
    print("JSON:", OUTPUT.relative_to(ROOT))
    print("Text:", TEXT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
