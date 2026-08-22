from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
AUDIT_PATH = PUBLIC / "gomyway-full-rhythm-technique-evidence-audit-v1.json"
TRAINING_GATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-training-gate-v1.json"
NOTATION_LOCK_PATH = PUBLIC / "professional-tablature-notation-standard-lock-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-full-rhythm-sustain-projection-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-full-rhythm-sustain-projection-v1-manifest.json"

STEPS_PER_MEASURE = 16
MIN_DURATION_STEPS = 2
MAX_DURATION_STEPS = 16


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def events_from(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    raise RuntimeError("No recognized event list")


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def duration_steps(event: dict[str, Any]) -> int:
    value = integer(event.get("durationSteps", event.get("duration", 1)))
    return max(1, value or 1)


def notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    return [row for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def normalized_notes(event: dict[str, Any]) -> list[dict[str, int]]:
    result: list[dict[str, int]] = []
    for note in notes(event):
        string_value = integer(note.get("string", note.get("stringIndex")))
        fret_value = integer(note.get("fret"))
        if string_value is None or fret_value is None:
            continue
        result.append({"string": string_value, "fret": fret_value})
    result.sort(key=lambda row: (row["string"], row["fret"]))
    return result


def signature(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    return tuple((row["string"], row["fret"]) for row in normalized_notes(event))


def clamp_end(start_step: int, duration: int) -> int:
    return min(STEPS_PER_MEASURE, start_step + max(MIN_DURATION_STEPS, min(duration, MAX_DURATION_STEPS)))


def main() -> None:
    source = load(SOURCE_PATH)
    audit = load(AUDIT_PATH)
    training_gate = load(TRAINING_GATE_PATH)
    notation_lock = load(NOTATION_LOCK_PATH)

    if training_gate.get("passed") is not True:
        raise RuntimeError("Full rhythm training gate is not green.")
    if notation_lock.get("passed") is not True:
        raise RuntimeError("Professional notation lock is not green.")
    if audit.get("passed") is not True:
        raise RuntimeError("Technique evidence audit is not green.")
    if ((audit.get("readiness") or {}).get("readyForDurationSustainLines")) is not True:
        raise RuntimeError("Technique audit did not authorize duration sustain lines.")

    source_events = events_from(source)
    if len(source_events) != 949:
        raise RuntimeError(f"Expected 949 source events, got {len(source_events)}.")

    by_measure: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for index, event in enumerate(source_events):
        measure_value = measure(event)
        step_value = step(event)
        if measure_value is None or step_value is None:
            continue
        by_measure[measure_value].append((index, event))

    sustain_rows: list[dict[str, Any]] = []
    duration_rows = 0
    continuation_rows = 0
    rejected_overlap = 0
    rejected_empty_notes = 0

    for measure_value in sorted(by_measure):
        ordered = sorted(by_measure[measure_value], key=lambda item: (step(item[1]) or 0, item[0]))

        for position, (event_index, event) in enumerate(ordered):
            start_step = step(event)
            if start_step is None:
                continue
            event_notes = normalized_notes(event)
            if not event_notes:
                rejected_empty_notes += 1
                continue

            duration = duration_steps(event)
            next_step = None
            if position + 1 < len(ordered):
                next_step = step(ordered[position + 1][1])

            if duration >= MIN_DURATION_STEPS:
                end_step = clamp_end(start_step, duration)
                if next_step is not None:
                    end_step = min(end_step, next_step)
                if end_step > start_step:
                    sustain_rows.append({
                        "measureNumber": measure_value,
                        "startStep": start_step,
                        "endStep": end_step,
                        "notes": event_notes,
                        "sourceEventIndex": event_index,
                        "evidenceType": "duration-steps",
                        "durationSteps": duration,
                        "confidence": event.get("confidence"),
                        "readOnly": True,
                    })
                    duration_rows += 1
                else:
                    rejected_overlap += 1

        for position in range(len(ordered) - 1):
            current_index, current = ordered[position]
            following_index, following = ordered[position + 1]
            current_step = step(current)
            following_step = step(following)
            if current_step is None or following_step is None or following_step <= current_step:
                continue
            if not signature(current) or signature(current) != signature(following):
                continue

            duplicate = any(
                row["measureNumber"] == measure_value
                and row["startStep"] == current_step
                and row["endStep"] >= following_step
                and tuple((note["string"], note["fret"]) for note in row["notes"]) == signature(current)
                for row in sustain_rows
            )
            if duplicate:
                continue

            sustain_rows.append({
                "measureNumber": measure_value,
                "startStep": current_step,
                "endStep": following_step,
                "notes": normalized_notes(current),
                "sourceEventIndex": current_index,
                "followingSourceEventIndex": following_index,
                "evidenceType": "same-note-continuation",
                "durationSteps": following_step - current_step,
                "confidence": min(
                    float(current.get("confidence") or 0.0),
                    float(following.get("confidence") or 0.0),
                ),
                "readOnly": True,
            })
            continuation_rows += 1

    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in sustain_rows:
        key = (
            row["measureNumber"],
            row["startStep"],
            row["endStep"],
            tuple((note["string"], note["fret"]) for note in row["notes"]),
        )
        existing = unique.get(key)
        if existing is None or existing["evidenceType"] == "same-note-continuation":
            unique[key] = row

    projected = sorted(
        unique.values(),
        key=lambda row: (
            row["measureNumber"],
            row["startStep"],
            row["endStep"],
            tuple((note["string"], note["fret"]) for note in row["notes"]),
        ),
    )

    covered_measures = sorted({row["measureNumber"] for row in projected})
    invalid_rows = [
        row
        for row in projected
        if not (
            1 <= row["measureNumber"] <= 113
            and 0 <= row["startStep"] < row["endStep"] <= STEPS_PER_MEASURE
            and row["notes"]
        )
    ]

    projection = {
        "schemaVersion": 1,
        "projectionType": "full-rhythm-read-only-sustain-lines",
        "sourcePath": str(SOURCE_PATH.relative_to(ROOT)),
        "auditPath": str(AUDIT_PATH.relative_to(ROOT)),
        "measureRange": [1, 113],
        "rows": projected,
        "rowCount": len(projected),
        "coveredMeasureCount": len(covered_measures),
        "coveredMeasures": covered_measures,
        "rules": {
            "minimumDurationSteps": MIN_DURATION_STEPS,
            "durationLinesClampedToNextAttack": True,
            "durationLinesClampedToMeasureEnd": True,
            "sameNoteContinuationAllowed": True,
            "crossMeasureSustainAllowed": False,
            "bendOrVibratoInferred": False,
        },
        "readOnly": True,
        "trainingOnly": True,
        "productionEligible": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "protectedRendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": not invalid_rows and len(projected) > 0,
        "sourceEventCount": len(source_events),
        "durationEvidenceRowsBuilt": duration_rows,
        "sameNoteContinuationRowsBuilt": continuation_rows,
        "uniqueProjectedRows": len(projected),
        "coveredMeasureCount": len(covered_measures),
        "invalidRows": invalid_rows[:50],
        "rejectedOverlapRows": rejected_overlap,
        "rejectedEmptyNoteRows": rejected_empty_notes,
        "readyForReadOnlySustainRenderer": not invalid_rows and len(projected) > 0,
        "bendOrVibratoInferred": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "protectedRendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(projection, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY FULL RHYTHM SUSTAIN PROJECTION V1 COMPLETE")
    print("Passed:", manifest["passed"])
    print("Source events:", manifest["sourceEventCount"])
    print("Duration evidence rows built:", duration_rows)
    print("Same-note continuation rows built:", continuation_rows)
    print("Unique projected sustain rows:", len(projected))
    print("Covered measures:", len(covered_measures))
    print("Rejected overlaps:", rejected_overlap)
    print("Ready for read-only sustain renderer:", manifest["readyForReadOnlySustainRenderer"])
    print("Bend or vibrato inferred: False")
    print("Source events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Protected renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not manifest["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
