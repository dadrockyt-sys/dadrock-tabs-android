from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
VALIDATION = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-validation.json"
JSON_OUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-review-packet.json"
TEXT_OUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-review-packet.txt"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    packet = load(SOURCE)
    validation = load(VALIDATION)
    measures = packet.get("measures", [])
    review_rows: list[dict[str, Any]] = []
    priority: list[dict[str, Any]] = []
    lines: list[str] = [
        "Gomyway professional rhythm reference review packet 33-48",
        "Timing grid: 16th-note slots 0-15",
        "Priority focus: Chorus 1 measures 33-38",
        "",
    ]

    for measure in measures:
        number = int(measure["measureNumber"])
        section = str(measure.get("section", "Unknown"))
        events = measure.get("events", [])
        rows = []
        lines.append(f"Measure {number} | {section} | {measure.get('timeSignature')} | {measure.get('tempoBpm')} BPM")
        for index, event in enumerate(events):
            row = {
                "eventIndex": index,
                "step": event.get("quantizedStep"),
                "durationSteps": event.get("durationSteps"),
                "notes": event.get("notes", []),
                "techniques": event.get("techniques", []),
                "confidence": event.get("referenceConfidence"),
            }
            rows.append(row)
            confidence = float(event.get("referenceConfidence", 0.0))
            if confidence < 0.85:
                priority.append({"measureNumber": number, **row})
            lines.append(
                f"  e{index:02d} step={row['step']:>2} dur={row['durationSteps']:>2} "
                f"notes={row['notes']} tech={row['techniques']} conf={confidence:.2f}"
            )
        lines.append("")
        review_rows.append({
            "measureNumber": number,
            "section": section,
            "events": rows,
            "humanDecision": "pending",
            "reviewNotes": "",
        })

    output = {
        "packetType": "professional-rhythm-human-review",
        "measureStart": 33,
        "measureEnd": 48,
        "validationPassed": validation.get("validDraft") is True,
        "errorCount": len(validation.get("errors", [])),
        "warningCount": len(validation.get("warnings", [])),
        "priorityReviewMeasures": sorted({item["measureNumber"] for item in priority}),
        "priorityReviewEvents": priority,
        "measures": review_rows,
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
    }
    JSON_OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    TEXT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Professional rhythm reference review packet 33-48 complete")
    print("Validation passed:", output["validationPassed"])
    print("Measures included:", len(review_rows))
    print("Errors:", output["errorCount"])
    print("Warnings:", output["warningCount"])
    print("Priority review measures:", output["priorityReviewMeasures"])
    print("Priority review events:", len(priority))
    print("Ready for training: False")
    print("JSON:", JSON_OUT.relative_to(ROOT))
    print("Text:", TEXT_OUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
