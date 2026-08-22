from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
POPULATED = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
VALIDATION = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-validation.json"
OUTPUT_JSON = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-review-packet.json"
OUTPUT_TXT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-review-packet.txt"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    populated = load_json(POPULATED)
    validation = load_json(VALIDATION)
    measures = populated.get("measures", [])
    errors = validation.get("errors", [])
    warnings = validation.get("warnings", [])
    priority = validation.get("priorityReviewMeasures", [])

    packet_measures: list[dict[str, Any]] = []
    lines = [
        "GOMYWAY PROFESSIONAL RHYTHM REFERENCE REVIEW — MEASURES 65-80",
        "",
        "Grid: 16th-note slots 0-15 | Strings: 1=high e through 6=low E",
        "Reference use: scoring only; no renderer or audio modification",
        "",
    ]

    for measure in measures:
        number = int(measure.get("measureNumber", -1))
        events = measure.get("events", [])
        review_events: list[dict[str, Any]] = []
        lines.append(
            f"MEASURE {number} | {measure.get('section')} | {measure.get('timeSignature')} | {measure.get('tempoBpm')} BPM"
        )
        for index, event in enumerate(events):
            confidence = float(event.get("referenceConfidence", 0.0))
            needs_review = confidence < 0.85 or number in priority
            item = {
                "eventIndex": index,
                "step": event.get("quantizedStep"),
                "durationSteps": event.get("durationSteps"),
                "notes": event.get("notes", []),
                "techniques": event.get("techniques", []),
                "referenceConfidence": confidence,
                "needsPriorityReview": needs_review,
            }
            review_events.append(item)
            marker = "REVIEW" if needs_review else "OK"
            lines.append(
                f"  [{marker}] event {index}: step={item['step']} duration={item['durationSteps']} "
                f"notes={item['notes']} techniques={item['techniques']} confidence={confidence:.2f}"
            )
        lines.append("")
        packet_measures.append({
            "measureNumber": number,
            "section": measure.get("section"),
            "timeSignature": measure.get("timeSignature"),
            "tempoBpm": measure.get("tempoBpm"),
            "priorityReview": number in priority,
            "events": review_events,
        })

    packet = {
        "schemaVersion": 1,
        "referenceType": "professional-rhythm-human-review-packet",
        "measureStart": 65,
        "measureEnd": 80,
        "validationPassed": bool(validation.get("validDraft", False)) and not errors,
        "measuresIncluded": len(packet_measures),
        "errors": errors,
        "warnings": warnings,
        "priorityReviewMeasures": priority,
        "fullCrossChorusConsensusPossible": bool(
            validation.get("fullCrossChorusConsensusPossible", False)
            or validation.get("crossChorusConsensusAvailable", False)
        ),
        "readyForTraining": False,
        "humanValidationRequired": True,
        "measures": packet_measures,
        "protectedRules": populated.get("protectedRules", {}),
    }
    OUTPUT_JSON.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("Professional rhythm reference review packet 65-80 complete")
    print("Validation passed:", packet["validationPassed"])
    print("Measures included:", packet["measuresIncluded"])
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", priority)
    print("Full cross-chorus consensus possible:", packet["fullCrossChorusConsensusPossible"])
    print("Ready for training: False")
    print("JSON:", OUTPUT_JSON.relative_to(ROOT))
    print("Text:", OUTPUT_TXT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
