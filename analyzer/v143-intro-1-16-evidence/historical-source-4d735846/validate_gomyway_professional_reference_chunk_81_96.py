from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-81-96-validation.json"

START_MEASURE = 81
END_MEASURE = 96
EXPECTED_MEASURES = set(range(START_MEASURE, END_MEASURE + 1))
EXPECTED_SECTIONS = {
    **{number: "Solo" for number in range(81, 95)},
    95: "Post-Solo",
    96: "Post-Solo",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_event(measure_number: int, event_index: int, event: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    step = event.get("quantizedStep")
    duration = event.get("durationSteps")

    if not isinstance(step, int) or not 0 <= step <= 15:
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "invalid-quantized-step",
            "value": step,
        })

    if not isinstance(duration, int) or duration < 1:
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "invalid-duration",
            "value": duration,
        })
    elif isinstance(step, int) and step + duration > 16:
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "event-crosses-measure-boundary",
            "step": step,
            "duration": duration,
        })

    notes = event.get("notes", [])
    if not isinstance(notes, list):
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "notes-not-list",
        })
        return errors

    for note_index, note in enumerate(notes):
        if not isinstance(note, dict):
            errors.append({
                "measure": measure_number,
                "event": event_index,
                "note": note_index,
                "type": "note-not-object",
            })
            continue
        string = note.get("string")
        fret = note.get("fret")
        if not isinstance(string, int) or not 1 <= string <= 6:
            errors.append({
                "measure": measure_number,
                "event": event_index,
                "note": note_index,
                "type": "invalid-string",
                "value": string,
            })
        if not isinstance(fret, int) or not -1 <= fret <= 24:
            errors.append({
                "measure": measure_number,
                "event": event_index,
                "note": note_index,
                "type": "invalid-fret",
                "value": fret,
            })

    techniques = event.get("techniques", [])
    if not isinstance(techniques, list):
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "techniques-not-list",
        })

    confidence = event.get("referenceConfidence")
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        errors.append({
            "measure": measure_number,
            "event": event_index,
            "type": "invalid-reference-confidence",
            "value": confidence,
        })

    return errors


def main() -> None:
    packet = load_json(INPUT)
    measures = packet.get("measures", [])
    by_measure = {int(item.get("measureNumber", -1)): item for item in measures}

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []

    found = set(by_measure)
    if found != EXPECTED_MEASURES:
        errors.append({
            "type": "measure-coverage-mismatch",
            "missing": sorted(EXPECTED_MEASURES - found),
            "extra": sorted(found - EXPECTED_MEASURES),
        })

    section_counts: Counter[str] = Counter()
    total_events = 0
    low_confidence_measures: set[int] = set()

    for number in sorted(EXPECTED_MEASURES & found):
        measure = by_measure[number]
        section = measure.get("section")
        section_counts[str(section)] += 1

        expected_section = EXPECTED_SECTIONS[number]
        if section != expected_section:
            errors.append({
                "measure": number,
                "type": "unexpected-section",
                "expected": expected_section,
                "actual": section,
            })

        if measure.get("timeSignature") != "4/4":
            errors.append({
                "measure": number,
                "type": "unexpected-time-signature",
                "expected": "4/4",
                "actual": measure.get("timeSignature"),
            })

        if measure.get("tempoBpm") != 129:
            errors.append({
                "measure": number,
                "type": "unexpected-tempo",
                "expected": 129,
                "actual": measure.get("tempoBpm"),
            })

        events = measure.get("events", [])
        if not isinstance(events, list) or not events:
            errors.append({
                "measure": number,
                "type": "missing-events",
            })
            continue

        total_events += len(events)
        previous_step = -1
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                errors.append({
                    "measure": number,
                    "event": index,
                    "type": "event-not-object",
                })
                continue

            errors.extend(validate_event(number, index, event))
            step = event.get("quantizedStep")
            if isinstance(step, int):
                if step < previous_step:
                    errors.append({
                        "measure": number,
                        "event": index,
                        "type": "events-not-sorted",
                        "step": step,
                        "previousStep": previous_step,
                    })
                previous_step = step

            confidence = float(event.get("referenceConfidence", 0.0))
            if confidence < 0.85:
                low_confidence_measures.add(number)
                warnings.append({
                    "measure": number,
                    "event": index,
                    "type": "low-confidence-event",
                    "step": event.get("quantizedStep"),
                    "confidence": confidence,
                })

    expected_counts = {"Solo": 14, "Post-Solo": 2}
    if dict(section_counts) != expected_counts:
        errors.append({
            "type": "section-count-mismatch",
            "expected": expected_counts,
            "actual": dict(section_counts),
        })

    valid = len(errors) == 0
    validation = {
        "chunk": [START_MEASURE, END_MEASURE],
        "validDraft": valid,
        "measuresChecked": len(EXPECTED_MEASURES & found),
        "totalEvents": total_events,
        "sectionCounts": dict(section_counts),
        "errors": errors,
        "warnings": warnings,
        "priorityReviewMeasures": sorted(low_confidence_measures),
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
        "nextRequiredStage": "build-human-review-packet-measures-81-96",
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 81-96 validation complete")
    print("Valid draft:", valid)
    print("Measures checked:", validation["measuresChecked"])
    print("Total events:", total_events)
    print("Section counts:", dict(section_counts))
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", sorted(low_confidence_measures))
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
