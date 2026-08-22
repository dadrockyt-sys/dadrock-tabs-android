from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-97-113-validation.json"
EXPECTED = set(range(97, 114))


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    packet = load_json(INPUT)
    measures = packet.get("measures", [])
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    found = {int(m.get("measureNumber", -1)) for m in measures}

    if found != EXPECTED:
        errors.append({
            "type": "coverage-mismatch",
            "missing": sorted(EXPECTED - found),
            "extra": sorted(found - EXPECTED),
        })

    section_counts: dict[str, int] = {}
    total_events = 0
    priority_review: set[int] = set()

    for measure in sorted(measures, key=lambda x: int(x.get("measureNumber", -1))):
        number = int(measure.get("measureNumber", -1))
        section = str(measure.get("section", ""))
        section_counts[section] = section_counts.get(section, 0) + 1
        if measure.get("timeSignature") != "4/4":
            errors.append({"measure": number, "type": "time-signature", "value": measure.get("timeSignature")})
        if int(measure.get("tempoBpm", 0)) != 129:
            errors.append({"measure": number, "type": "tempo", "value": measure.get("tempoBpm")})

        previous_step = -1
        for index, evt in enumerate(measure.get("events", [])):
            total_events += 1
            step = int(evt.get("quantizedStep", -1))
            duration = int(evt.get("durationSteps", 0))
            if not 0 <= step <= 15:
                errors.append({"measure": number, "event": index, "type": "invalid-step", "step": step})
            if duration < 1 or step + duration > 16:
                errors.append({"measure": number, "event": index, "type": "invalid-duration", "step": step, "duration": duration})
            if step < previous_step:
                errors.append({"measure": number, "event": index, "type": "unsorted-events"})
            previous_step = step

            for note in evt.get("notes", []):
                string = int(note.get("string", 0))
                fret = int(note.get("fret", -999))
                if not 1 <= string <= 6:
                    errors.append({"measure": number, "event": index, "type": "invalid-string", "string": string})
                if fret < -1 or fret > 24:
                    errors.append({"measure": number, "event": index, "type": "invalid-fret", "fret": fret})

            confidence = float(evt.get("referenceConfidence", 0.0))
            if confidence < 0.85:
                warnings.append({
                    "measure": number,
                    "event": index,
                    "type": "low-confidence-event",
                    "step": step,
                    "confidence": confidence,
                })
                priority_review.add(number)

    expected_sections = {"Post-Solo": 6, "Out-Chorus": 8, "Ending": 3}
    if section_counts != expected_sections:
        errors.append({"type": "section-counts", "expected": expected_sections, "actual": section_counts})

    valid = not errors
    result = {
        "chunk": [97, 113],
        "validDraft": valid,
        "measuresChecked": len(measures),
        "totalEvents": total_events,
        "sectionCounts": section_counts,
        "errors": errors,
        "warnings": warnings,
        "priorityReviewMeasures": sorted(priority_review),
        "readyForTraining": False,
        "finalReferenceChunk": True,
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 97-113 validation complete")
    print("Valid draft:", valid)
    print("Measures checked:", len(measures))
    print("Total events:", total_events)
    print("Section counts:", section_counts)
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", sorted(priority_review))
    print("Ready for training: False")
    print("Final reference chunk: True")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
