from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
TRAINING_GATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-training-gate-v1.json"
NOTATION_LOCK_PATH = PUBLIC / "professional-tablature-notation-standard-lock-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-audit-v1.json"
PLAN_PATH = PUBLIC / "gomyway-chorus-33-35-chord-recovery-plan-v1.json"

TARGET_MEASURES = (33, 34, 35)
STANDARD_TUNING_MIDI = {
    1: 64,  # high e
    2: 59,
    3: 55,
    4: 50,
    5: 45,
    6: 40,  # low E
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        value = payload.get(key)
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    return []


def measures(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("measures")
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    return []


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure_number(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def duration(event: dict[str, Any]) -> int:
    return max(1, integer(event.get("durationSteps", event.get("duration", 1))) or 1)


def raw_notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    return [note for note in value if isinstance(note, dict)] if isinstance(value, list) else []


def source_note(note: dict[str, Any]) -> tuple[int, int] | None:
    raw_string = integer(note.get("string", note.get("stringIndex")))
    fret = integer(note.get("fret"))
    if raw_string is None or fret is None:
        return None
    # The full-song source primarily uses 1-based strings. Preserve explicit string= values.
    if "string" in note and 1 <= raw_string <= 6:
        string = raw_string
    elif 1 <= raw_string <= 6:
        string = raw_string
    elif 0 <= raw_string <= 5:
        string = raw_string + 1
    else:
        return None
    if not 0 <= fret <= 24:
        return None
    return string, fret


def normalized_notes(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    result: set[tuple[int, int]] = set()
    for note in raw_notes(event):
        normalized = source_note(note)
        if normalized is not None:
            result.add(normalized)
    return tuple(sorted(result))


def midi_signature(notes: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    return tuple(sorted(STANDARD_TUNING_MIDI[string] + fret for string, fret in notes))


def pitch_class_signature(notes: tuple[tuple[int, int], ...]) -> tuple[int, ...]:
    return tuple(sorted(set(midi % 12 for midi in midi_signature(notes))))


def event_summary(event: dict[str, Any]) -> dict[str, Any]:
    notes = normalized_notes(event)
    return {
        "quantizedStep": step(event),
        "durationSteps": duration(event),
        "notes": [{"string": string, "fret": fret} for string, fret in notes],
        "noteCount": len(notes),
        "midiSignature": list(midi_signature(notes)),
        "pitchClassSignature": list(pitch_class_signature(notes)),
        "techniques": event.get("techniques", []),
    }


def source_events_for_measure(source_rows: list[dict[str, Any]], number: int) -> list[dict[str, Any]]:
    result = [row for row in source_rows if measure_number(row) == number]
    return sorted(result, key=lambda row: (step(row) if step(row) is not None else 999, -len(normalized_notes(row))))


def reference_events_for_measure(reference_measures: list[dict[str, Any]], number: int) -> list[dict[str, Any]]:
    for measure in reference_measures:
        if integer(measure.get("measureNumber")) == number:
            value = measure.get("events")
            if isinstance(value, list):
                return sorted(
                    [row for row in value if isinstance(row, dict)],
                    key=lambda row: step(row) if step(row) is not None else 999,
                )
    return []


def index_by_step(events: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    result: dict[int, list[dict[str, Any]]] = {}
    for event in events:
        event_step = step(event)
        if event_step is None:
            continue
        result.setdefault(event_step, []).append(event)
    return result


def combined_step_notes(events: list[dict[str, Any]]) -> tuple[tuple[int, int], ...]:
    notes: set[tuple[int, int]] = set()
    for event in events:
        notes.update(normalized_notes(event))
    return tuple(sorted(notes))


def audit_measure(source_events: list[dict[str, Any]], reference_events: list[dict[str, Any]], number: int) -> dict[str, Any]:
    source_steps = index_by_step(source_events)
    reference_steps = index_by_step(reference_events)
    all_steps = sorted(set(source_steps) | set(reference_steps))

    comparisons: list[dict[str, Any]] = []
    multiplicity_deficit_steps: list[int] = []
    exact_match_steps: list[int] = []
    pitch_class_match_steps: list[int] = []
    missing_reference_steps: list[int] = []
    extra_source_steps: list[int] = []

    for event_step in all_steps:
        source_group = source_steps.get(event_step, [])
        reference_group = reference_steps.get(event_step, [])
        source_notes = combined_step_notes(source_group)
        reference_notes = combined_step_notes(reference_group)
        source_midi = midi_signature(source_notes)
        reference_midi = midi_signature(reference_notes)
        source_pc = pitch_class_signature(source_notes)
        reference_pc = pitch_class_signature(reference_notes)

        exact = bool(source_notes) and source_notes == reference_notes
        pitch_class_match = bool(source_pc) and source_pc == reference_pc
        multiplicity_deficit = len(source_notes) < len(reference_notes)

        if exact:
            exact_match_steps.append(event_step)
        if pitch_class_match:
            pitch_class_match_steps.append(event_step)
        if multiplicity_deficit:
            multiplicity_deficit_steps.append(event_step)
        if reference_notes and not source_notes:
            missing_reference_steps.append(event_step)
        if source_notes and not reference_notes:
            extra_source_steps.append(event_step)

        comparisons.append({
            "quantizedStep": event_step,
            "sourceNotes": [{"string": string, "fret": fret} for string, fret in source_notes],
            "referenceNotes": [{"string": string, "fret": fret} for string, fret in reference_notes],
            "sourceNoteCount": len(source_notes),
            "referenceNoteCount": len(reference_notes),
            "sourceMidiSignature": list(source_midi),
            "referenceMidiSignature": list(reference_midi),
            "sourcePitchClasses": list(source_pc),
            "referencePitchClasses": list(reference_pc),
            "exactStringFretMatch": exact,
            "pitchClassMatch": pitch_class_match,
            "multiplicityDeficit": multiplicity_deficit,
            "requiresAudioChordRecovery": bool(reference_notes) and not exact,
        })

    reference_attack_steps = sorted(reference_steps)
    source_attack_steps = sorted(source_steps)
    reference_chord_steps = [event_step for event_step, group in reference_steps.items() if len(combined_step_notes(group)) >= 2]
    source_chord_steps = [event_step for event_step, group in source_steps.items() if len(combined_step_notes(group)) >= 2]

    return {
        "measureNumber": number,
        "sourceEventCount": len(source_events),
        "referenceEventCount": len(reference_events),
        "sourceAttackSteps": source_attack_steps,
        "referenceAttackSteps": reference_attack_steps,
        "sourceChordAttackSteps": sorted(source_chord_steps),
        "referenceChordAttackSteps": sorted(reference_chord_steps),
        "exactMatchStepCount": len(exact_match_steps),
        "pitchClassMatchStepCount": len(pitch_class_match_steps),
        "multiplicityDeficitSteps": multiplicity_deficit_steps,
        "missingReferenceAttackSteps": missing_reference_steps,
        "extraSourceAttackSteps": extra_source_steps,
        "readyWithoutRecovery": len(exact_match_steps) == len(reference_attack_steps) and not extra_source_steps,
        "comparisons": comparisons,
    }


def main() -> None:
    source = load(SOURCE_PATH)
    reference = load(REFERENCE_PATH)
    training_gate = load(TRAINING_GATE_PATH)
    notation_lock = load(NOTATION_LOCK_PATH)

    source_rows = rows(source)
    reference_measures = measures(reference)

    if training_gate.get("passed") is not True:
        raise RuntimeError("Full-song rhythm training gate is not green.")
    if notation_lock.get("passed") is not True:
        raise RuntimeError("Professional notation lock is not green.")
    if len(source_rows) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(source_rows)}.")

    audits = []
    recovery_targets = []
    for number in TARGET_MEASURES:
        source_events = source_events_for_measure(source_rows, number)
        reference_events = reference_events_for_measure(reference_measures, number)
        audit = audit_measure(source_events, reference_events, number)
        audits.append(audit)

        for comparison in audit["comparisons"]:
            if not comparison["requiresAudioChordRecovery"]:
                continue
            recovery_targets.append({
                "measureNumber": number,
                "quantizedStep": comparison["quantizedStep"],
                "targetAttackMultiplicity": comparison["referenceNoteCount"],
                "currentAttackMultiplicity": comparison["sourceNoteCount"],
                "referencePitchClassesForScoringOnly": comparison["referencePitchClasses"],
                "referenceStringFretShapeForScoringOnly": comparison["referenceNotes"],
                "requiredEvidence": [
                    "separated-rhythm-audio attack cluster",
                    "near-simultaneous multi-pitch support",
                    "playable guitar voicing",
                    "repeat-section consistency",
                ],
                "copyProfessionalNotesIntoOutput": False,
                "productionEligible": False,
            })

    exact_total = sum(audit["exactMatchStepCount"] for audit in audits)
    reference_attack_total = sum(len(audit["referenceAttackSteps"]) for audit in audits)
    deficit_total = sum(len(audit["multiplicityDeficitSteps"]) for audit in audits)

    report = {
        "schemaVersion": 1,
        "auditType": "protected-chorus-chord-recovery-audit",
        "passed": True,
        "targetMeasures": list(TARGET_MEASURES),
        "sourceEventCount": len(source_rows),
        "referenceUsedForScoringOnly": True,
        "exactStepMatches": exact_total,
        "referenceAttackSteps": reference_attack_total,
        "attackMultiplicityDeficitCount": deficit_total,
        "recoveryTargetCount": len(recovery_targets),
        "readyForAudioChordRecovery": len(recovery_targets) > 0,
        "readyForPromotion": False,
        "sourceEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "measures": audits,
    }

    plan = {
        "schemaVersion": 1,
        "planType": "chorus-33-35-audio-derived-chord-recovery",
        "status": "read-only-target-plan",
        "targetMeasures": list(TARGET_MEASURES),
        "targets": recovery_targets,
        "scoringAuthority": str(REFERENCE_PATH.relative_to(ROOT)),
        "candidateAudio": "public/gomywayfullaitest.m4a",
        "trainingRule": "professional-reference -> audio cluster candidate -> playable voicing -> repeat consistency -> held-out validation -> zero-regression gate",
        "promotionRequirements": {
            "truePositivesMustImprove": True,
            "falsePositivesMustRemainZero": True,
            "measures1Through16Protected": True,
            "v7EventsProtected": True,
            "rendererProtected": True,
            "professionalReferenceProtected": True,
            "bestJsonProtected": True,
        },
        "professionalNotesCopiedIntoOutput": False,
        "sourceEventsModified": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    PLAN_PATH.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 CHORD RECOVERY AUDIT V1 COMPLETE")
    print("Passed: True")
    print("Protected source events:", len(source_rows))
    print("Reference attack steps:", reference_attack_total)
    print("Exact string/fret step matches:", exact_total)
    print("Attack multiplicity deficits:", deficit_total)
    print("Audio chord recovery targets:", len(recovery_targets))
    for audit in audits:
        print(
            f"Measure {audit['measureNumber']}: "
            f"source attacks={len(audit['sourceAttackSteps'])} "
            f"reference attacks={len(audit['referenceAttackSteps'])} "
            f"source chord attacks={len(audit['sourceChordAttackSteps'])} "
            f"reference chord attacks={len(audit['referenceChordAttackSteps'])} "
            f"exact matches={audit['exactMatchStepCount']} "
            f"multiplicity deficits={len(audit['multiplicityDeficitSteps'])}"
        )
    print("Ready for audio chord recovery:", report["readyForAudioChordRecovery"])
    print("Professional reference used for scoring only: True")
    print("Source events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Audit:", OUTPUT_PATH.relative_to(ROOT))
    print("Plan:", PLAN_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
