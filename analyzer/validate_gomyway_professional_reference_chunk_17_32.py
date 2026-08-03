from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-17-32-validation.json"


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"Missing prerequisite: {INPUT.relative_to(ROOT)}")

    packet = json.loads(INPUT.read_text(encoding="utf-8"))
    measures = packet.get("measures", [])
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    event_counts: dict[int, int] = {}
    section_counts: Counter[str] = Counter()
    technique_counts: Counter[str] = Counter()

    found = {int(item.get("measureNumber", -1)) for item in measures}
    expected = set(range(17, 33))
    if found != expected:
        errors.append({"type": "coverage-mismatch", "missing": sorted(expected - found), "extra": sorted(found - expected)})

    for measure in sorted(measures, key=lambda item: int(item.get("measureNumber", -1))):
        number = int(measure.get("measureNumber", -1))
        section = str(measure.get("section", ""))
        section_counts[section] += 1
        events = measure.get("events", [])
        event_counts[number] = len(events)

        if section != "Verse 1":
            errors.append({"measure": number, "type": "unexpected-section", "value": section})
        if measure.get("timeSignature") != "4/4":
            errors.append({"measure": number, "type": "unexpected-time-signature", "value": measure.get("timeSignature")})
        if int(measure.get("tempoBpm", 0) or 0) != 129:
            errors.append({"measure": number, "type": "unexpected-tempo", "value": measure.get("tempoBpm")})
        if not events:
            errors.append({"measure": number, "type": "empty-measure"})
            continue

        seen_steps: set[int] = set()
        for index, event in enumerate(events):
            step = int(event.get("quantizedStep", -1))
            duration = int(event.get("durationSteps", 0))
            if not 0 <= step <= 15:
                errors.append({"measure": number, "event": index, "type": "invalid-step", "value": step})
            if duration < 1 or step + duration > 16:
                errors.append({"measure": number, "event": index, "type": "invalid-duration", "step": step, "duration": duration})
            if step in seen_steps:
                warnings.append({"measure": number, "event": index, "type": "duplicate-onset-step", "step": step})
            seen_steps.add(step)

            notes = event.get("notes", [])
            if not notes:
                errors.append({"measure": number, "event": index, "type": "missing-notes"})
            for note in notes:
                string = int(note.get("string", 0))
                fret = int(note.get("fret", -99))
                if not 1 <= string <= 6:
                    errors.append({"measure": number, "event": index, "type": "invalid-string", "value": string})
                if fret < -1 or fret > 24:
                    errors.append({"measure": number, "event": index, "type": "invalid-fret", "value": fret})

            confidence = float(event.get("referenceConfidence", 0.0))
            if confidence < 0.85:
                warnings.append({"measure": number, "event": index, "type": "low-confidence-event", "step": step, "confidence": confidence})
            for technique in event.get("techniques", []):
                technique_counts[str(technique)] += 1

    repeated_groups = {
        "em": list(range(17, 25)) + list(range(29, 33)),
        "g": [25, 26, 27],
    }
    repeated_consistency: dict[str, bool] = {}
    by_number = {int(item["measureNumber"]): item for item in measures}
    for label, group in repeated_groups.items():
        signatures = []
        for number in group:
            events = by_number[number].get("events", [])
            signatures.append([
                (
                    int(event.get("quantizedStep", -1)),
                    int(event.get("durationSteps", 0)),
                    tuple((int(note.get("string", 0)), int(note.get("fret", -99))) for note in event.get("notes", [])),
                    tuple(event.get("techniques", [])),
                )
                for event in events
            ])
        repeated_consistency[label] = all(signature == signatures[0] for signature in signatures[1:])
        if not repeated_consistency[label]:
            errors.append({"type": "repeated-pattern-inconsistent", "group": label, "measures": group})

    human_statuses = Counter(
        str(item.get("humanReview", {}).get("status", "missing"))
        for item in measures
    )

    valid = not errors
    report = {
        "validationType": "professional-rhythm-reference-chunk-17-32",
        "validDraft": valid,
        "readyForTraining": False,
        "humanApprovalRequired": True,
        "measuresChecked": len(measures),
        "eventCountsByMeasure": event_counts,
        "totalEvents": sum(event_counts.values()),
        "sectionCounts": dict(section_counts),
        "techniqueCounts": dict(technique_counts),
        "repeatedPatternConsistency": repeated_consistency,
        "humanReviewStatuses": dict(human_statuses),
        "errors": errors,
        "warnings": warnings,
        "protectedBaselinesChanged": False,
        "nextRequiredStage": "human-review-professional-reference-chunk-17-32",
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 17-32 validation complete")
    print("Valid draft:", valid)
    print("Measures checked:", len(measures))
    print("Total events:", report["totalEvents"])
    print("Repeated Em pattern consistent:", repeated_consistency.get("em"))
    print("Repeated G pattern consistent:", repeated_consistency.get("g"))
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    for warning in warnings:
        print("WARNING", warning)
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
