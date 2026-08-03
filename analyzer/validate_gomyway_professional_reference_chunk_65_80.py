from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-65-80-validation.json"
EXPECTED = set(range(65, 81))
EXPECTED_SECTIONS = {65: "Chorus 2", 66: "Chorus 2", 67: "Chorus 2", 68: "Chorus 2"}
for number in range(69, 78):
    EXPECTED_SECTIONS[number] = "Bridge"
for number in range(78, 81):
    EXPECTED_SECTIONS[number] = "Solo"


def as_int(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing prerequisite: {INPUT.relative_to(ROOT)}")

    packet = json.loads(INPUT.read_text(encoding="utf-8"))
    measures = packet.get("measures", [])
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()

    numbers = {as_int(item.get("measureNumber")) for item in measures if isinstance(item, dict)}
    if numbers != EXPECTED:
        errors.append({
            "type": "measure-coverage-mismatch",
            "missing": sorted(EXPECTED - numbers),
            "extra": sorted(numbers - EXPECTED),
        })

    total_events = 0
    priority_measures: set[int] = set()
    for measure in measures:
        if not isinstance(measure, dict):
            errors.append({"type": "invalid-measure-object"})
            continue
        number = as_int(measure.get("measureNumber"))
        section = str(measure.get("section", ""))
        section_counts[section] += 1
        if EXPECTED_SECTIONS.get(number) != section:
            errors.append({
                "type": "section-mismatch",
                "measure": number,
                "expected": EXPECTED_SECTIONS.get(number),
                "actual": section,
            })
        if str(measure.get("timeSignature", "")) != "4/4":
            errors.append({"type": "time-signature-mismatch", "measure": number})
        if as_int(measure.get("tempoBpm")) != 129:
            errors.append({"type": "tempo-mismatch", "measure": number})

        events = measure.get("events", [])
        if not isinstance(events, list) or not events:
            errors.append({"type": "missing-events", "measure": number})
            continue
        total_events += len(events)

        for index, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append({"type": "invalid-event", "measure": number, "event": index})
                continue
            step = as_int(event.get("quantizedStep"))
            duration = as_int(event.get("durationSteps"), 1)
            if step < 0 or step > 15:
                errors.append({"type": "invalid-step", "measure": number, "event": index, "step": step})
            if duration < 1 or step + duration > 16:
                errors.append({
                    "type": "invalid-duration",
                    "measure": number,
                    "event": index,
                    "step": step,
                    "duration": duration,
                })
            for note in event.get("notes", []) or []:
                string = as_int(note.get("string"))
                fret = as_int(note.get("fret"))
                if string < 1 or string > 6:
                    errors.append({"type": "invalid-string", "measure": number, "event": index, "string": string})
                if fret < -1 or fret > 24:
                    errors.append({"type": "invalid-fret", "measure": number, "event": index, "fret": fret})
            confidence = float(event.get("referenceConfidence", 1.0) or 0.0)
            if confidence < 0.85:
                warnings.append({
                    "type": "low-confidence-event",
                    "measure": number,
                    "event": index,
                    "step": step,
                    "confidence": confidence,
                })
                priority_measures.add(number)

    result = {
        "chunk": [65, 80],
        "validDraft": not errors,
        "measuresChecked": len(measures),
        "totalEvents": total_events,
        "sectionCounts": dict(section_counts),
        "errors": errors,
        "warnings": warnings,
        "priorityReviewMeasures": sorted(priority_measures),
        "fullCrossChorusConsensusPossible": bool(packet.get("fullCrossChorusConsensusPossible", True)),
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 65-80 validation complete")
    print("Valid draft:", result["validDraft"])
    print("Measures checked:", result["measuresChecked"])
    print("Total events:", result["totalEvents"])
    print("Section counts:", result["sectionCounts"])
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", result["priorityReviewMeasures"])
    print("Full cross-chorus consensus possible:", result["fullCrossChorusConsensusPossible"])
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
