from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-33-48-validation.json"

EXPECTED = set(range(33, 49))
EXPECTED_SECTIONS = {
    **{measure: "Chorus 1" for measure in range(33, 39)},
    **{measure: "Riff" for measure in range(39, 47)},
    **{measure: "Verse 2" for measure in range(47, 49)},
}


def as_int(value: Any, default: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing prerequisite: {INPUT.relative_to(ROOT)}")

    packet = json.loads(INPUT.read_text(encoding="utf-8"))
    measures = packet.get("measures") or []
    by_measure = {as_int(item.get("measureNumber")): item for item in measures if isinstance(item, dict)}

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    found = set(by_measure)
    if found != EXPECTED:
        errors.append({
            "type": "coverage-mismatch",
            "missing": sorted(EXPECTED - found),
            "extra": sorted(found - EXPECTED),
        })

    total_events = 0
    low_confidence = 0
    section_counts: Counter[str] = Counter()

    for measure_number in sorted(EXPECTED & found):
        measure = by_measure[measure_number]
        section = str(measure.get("section"))
        section_counts[section] += 1
        if section != EXPECTED_SECTIONS[measure_number]:
            errors.append({
                "measure": measure_number,
                "type": "section-mismatch",
                "expected": EXPECTED_SECTIONS[measure_number],
                "actual": section,
            })
        if str(measure.get("timeSignature")) != "4/4":
            errors.append({"measure": measure_number, "type": "time-signature", "actual": measure.get("timeSignature")})
        if as_int(measure.get("tempoBpm")) != 129:
            errors.append({"measure": measure_number, "type": "tempo", "actual": measure.get("tempoBpm")})

        events = measure.get("events") or []
        if not events:
            errors.append({"measure": measure_number, "type": "no-events"})
            continue

        for index, event in enumerate(events):
            total_events += 1
            step = as_int(event.get("quantizedStep"))
            duration = as_int(event.get("durationSteps"), 1)
            if not 0 <= step <= 15:
                errors.append({"measure": measure_number, "event": index, "type": "invalid-step", "step": step})
            if duration < 1 or step + duration > 16:
                errors.append({
                    "measure": measure_number,
                    "event": index,
                    "type": "duration-outside-measure",
                    "step": step,
                    "duration": duration,
                })

            notes = event.get("notes") or []
            if not notes:
                errors.append({"measure": measure_number, "event": index, "type": "missing-notes"})
            for note in notes:
                string = as_int(note.get("string"))
                fret = as_int(note.get("fret"))
                if not 1 <= string <= 6:
                    errors.append({"measure": measure_number, "event": index, "type": "invalid-string", "string": string})
                if not -1 <= fret <= 24:
                    errors.append({"measure": measure_number, "event": index, "type": "invalid-fret", "fret": fret})

            confidence = float(event.get("referenceConfidence", 0.0))
            if confidence < 0.85:
                low_confidence += 1
                warnings.append({
                    "measure": measure_number,
                    "event": index,
                    "type": "low-confidence-event",
                    "step": step,
                    "confidence": confidence,
                })

    chorus_priority = [warning for warning in warnings if 33 <= warning["measure"] <= 38]
    valid = not errors
    report = {
        "chunk": [33, 48],
        "validDraft": valid,
        "measuresChecked": len(EXPECTED & found),
        "totalEvents": total_events,
        "sectionCounts": dict(section_counts),
        "errors": errors,
        "warnings": warnings,
        "lowConfidenceEventCount": low_confidence,
        "priorityReviewMeasures": sorted({item["measure"] for item in chorus_priority}),
        "readyForTraining": False,
        "nextRequiredStage": "human-review-chorus-measures-33-38-and-approve-chunk",
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 33-48 validation complete")
    print("Valid draft:", valid)
    print("Measures checked:", report["measuresChecked"])
    print("Total events:", total_events)
    print("Section counts:", report["sectionCounts"])
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", report["priorityReviewMeasures"])
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
