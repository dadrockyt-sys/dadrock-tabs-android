from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-populated.json"
OUTPUT = ROOT / "public" / "gomyway-professional-rhythm-reference-chunk-49-64-validation.json"

EXPECTED = set(range(49, 65))
EXPECTED_SECTIONS = {
    **{number: "Verse 2" for number in range(49, 63)},
    63: "Chorus 2",
    64: "Chorus 2",
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
    by_number = {as_int(item.get("measureNumber")): item for item in measures if isinstance(item, dict)}

    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    found = set(by_number)
    if found != EXPECTED:
        errors.append({"type": "coverage-mismatch", "missing": sorted(EXPECTED - found), "extra": sorted(found - EXPECTED)})

    total_events = 0
    for number in sorted(EXPECTED & found):
        measure = by_number[number]
        section = measure.get("section")
        if section != EXPECTED_SECTIONS[number]:
            errors.append({"measure": number, "type": "section-mismatch", "expected": EXPECTED_SECTIONS[number], "actual": section})
        if measure.get("timeSignature") != "4/4":
            errors.append({"measure": number, "type": "time-signature-mismatch", "actual": measure.get("timeSignature")})
        if as_int(measure.get("tempoBpm")) != 129:
            errors.append({"measure": number, "type": "tempo-mismatch", "actual": measure.get("tempoBpm")})

        events = measure.get("events") or []
        if not events:
            errors.append({"measure": number, "type": "empty-measure-events"})
        total_events += len(events)

        for index, event in enumerate(events):
            step = as_int(event.get("quantizedStep"))
            duration = as_int(event.get("durationSteps"), 0)
            if not 0 <= step <= 15:
                errors.append({"measure": number, "event": index, "type": "invalid-step", "step": step})
            if duration < 1 or step + duration > 16:
                errors.append({"measure": number, "event": index, "type": "invalid-duration", "step": step, "duration": duration})

            notes = event.get("notes") or []
            if not notes:
                errors.append({"measure": number, "event": index, "type": "missing-notes"})
            for note in notes:
                string = as_int(note.get("string"))
                fret = as_int(note.get("fret"))
                if not 1 <= string <= 6:
                    errors.append({"measure": number, "event": index, "type": "invalid-string", "string": string})
                if not -1 <= fret <= 24:
                    errors.append({"measure": number, "event": index, "type": "invalid-fret", "fret": fret})

            confidence = float(event.get("referenceConfidence", 0.0) or 0.0)
            if confidence < 0.85:
                warnings.append({"measure": number, "event": index, "type": "low-confidence-event", "step": step, "confidence": confidence})

    chorus_consensus_available = bool(packet.get("crossChorusConsensusAvailable", packet.get("crossChorusConsensus", True)))
    if not chorus_consensus_available:
        errors.append({"type": "cross-chorus-consensus-missing"})

    sections = Counter(str(item.get("section")) for item in measures)
    valid = not errors
    report = {
        "chunk": [49, 64],
        "validDraft": valid,
        "measuresChecked": len(measures),
        "totalEvents": total_events,
        "sectionCounts": dict(sections),
        "errors": errors,
        "warnings": warnings,
        "priorityReviewMeasures": sorted({item["measure"] for item in warnings}),
        "crossChorusConsensusAvailable": chorus_consensus_available,
        "readyForTraining": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm reference chunk 49-64 validation complete")
    print("Valid draft:", valid)
    print("Measures checked:", len(measures))
    print("Total events:", total_events)
    print("Section counts:", dict(sections))
    print("Errors:", len(errors))
    print("Warnings:", len(warnings))
    print("Priority review measures:", report["priorityReviewMeasures"])
    print("Cross-chorus consensus available:", chorus_consensus_available)
    print("Ready for training: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
