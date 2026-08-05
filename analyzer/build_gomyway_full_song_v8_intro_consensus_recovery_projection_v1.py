from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOUND_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1.json"
BOUND_MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1-manifest.json"
RECOVERY_PATH = ROOT / "public" / "gomyway-intro-unresolved-slot-consensus-recovery-v1.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v1.json"
MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v1-manifest.json"


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def measure_number(event: dict[str, Any]) -> int | None:
    value = event.get("measureNumber", event.get("measure"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def step_number(event: dict[str, Any]) -> int | None:
    value = event.get("quantizedStep", event.get("step"))
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def event_signature(event: dict[str, Any]) -> tuple[Any, ...]:
    notes = event.get("notes", [])
    normalized_notes: list[tuple[int, int]] = []
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            try:
                normalized_notes.append((int(note.get("string", note.get("stringIndex"))), int(note.get("fret"))))
            except (TypeError, ValueError):
                continue
    try:
        duration = int(event.get("durationSteps", event.get("duration", 1)))
    except (TypeError, ValueError):
        duration = 1
    techniques_raw = event.get("techniques", event.get("technique", []))
    if isinstance(techniques_raw, str):
        techniques = (techniques_raw,)
    elif isinstance(techniques_raw, list):
        techniques = tuple(sorted(str(value) for value in techniques_raw if value is not None))
    else:
        techniques = tuple()
    return (
        measure_number(event),
        step_number(event),
        tuple(sorted(set(normalized_notes))),
        duration,
        techniques,
    )


def main() -> None:
    bound = load(BOUND_PATH)
    bound_manifest = load(BOUND_MANIFEST_PATH)
    recovery = load(RECOVERY_PATH)

    if recovery.get("readyForRecoveryProjection") is not True:
        raise RuntimeError("Consensus recovery audit did not authorize recovery projection")

    source_events = bound.get("events", bound.get("candidates", []))
    if not isinstance(source_events, list):
        raise RuntimeError("Bound intro source has no event list")

    recovery_rows = recovery.get("recoveryRows", [])
    if not isinstance(recovery_rows, list):
        raise RuntimeError("Recovery audit has no recovery rows")

    output_events = [copy.deepcopy(event) for event in source_events if isinstance(event, dict)]
    source_signatures = {event_signature(event) for event in output_events}
    recovered_events: list[dict[str, Any]] = []

    for row in recovery_rows:
        if not isinstance(row, dict) or row.get("readyForRecovery") is not True:
            continue
        signature = row.get("selectedSignature")
        if not isinstance(signature, dict):
            continue
        measure = int(row["measureNumber"])
        step = int(row["expectedStep"])
        event = {
            "measureNumber": measure,
            "quantizedStep": step,
            "durationSteps": int(signature.get("durationSteps") or 1),
            "notes": copy.deepcopy(signature.get("notes") or []),
            "techniques": copy.deepcopy(signature.get("techniques") or []),
            "confidence": 1.0,
            "source": "audio-derived repeated-intro consensus",
            "introRecovery": {
                "schemaVersion": 1,
                "mode": "consensus-recovery",
                "supportingMeasures": copy.deepcopy(row.get("supportingMeasures", [])),
                "supportCount": int(row.get("supportCount") or 0),
                "professionalNotesCopied": False,
                "audioDerivedConsensusOnly": True,
            },
        }
        signature_key = event_signature(event)
        if signature_key in source_signatures:
            continue
        source_signatures.add(signature_key)
        recovered_events.append(event)
        output_events.append(event)

    output_events.sort(key=lambda item: (
        measure_number(item) if measure_number(item) is not None else 9999,
        step_number(item) if step_number(item) is not None else 9999,
    ))

    covered = sorted({m for event in output_events for m in [measure_number(event)] if m is not None})
    missing_measures = sorted(set(range(1, 114)) - set(covered))
    intro_slots = {
        (measure_number(event), step_number(event))
        for event in output_events
        if measure_number(event) in range(1, 17) and step_number(event) is not None
    }
    expected_intro_slots = {(measure, step) for measure in range(1, 17) for step in (2, 4, 6, 9, 11, 14)}
    unresolved_slots = sorted(expected_intro_slots - intro_slots)
    recovered_slot_keys = sorted((measure_number(event), step_number(event)) for event in recovered_events)

    original_17_113 = [event_signature(event) for event in source_events if measure_number(event) in range(17, 114)]
    output_17_113 = [event_signature(event) for event in output_events if measure_number(event) in range(17, 114)]
    measures_17_113_preserved = original_17_113 == output_17_113

    passed = bool(
        len(recovered_events) == int(recovery.get("consensusRecoverableSlotCount", 0))
        and not unresolved_slots
        and not missing_measures
        and len(covered) == 113
        and measures_17_113_preserved
    )

    result = copy.deepcopy(bound)
    result.update({
        "schemaVersion": 4,
        "candidateType": "full-song-rhythm-with-locked-intro-and-consensus-recovery",
        "sourceBoundPath": str(BOUND_PATH.relative_to(ROOT)),
        "recoveryAuditPath": str(RECOVERY_PATH.relative_to(ROOT)),
        "events": output_events,
        "candidates": output_events,
        "eventCount": len(output_events),
        "consensusRecoveredIntroSlots": recovered_slot_keys,
        "consensusRecoveredIntroSlotCount": len(recovered_events),
        "lockedIntroUnresolvedSlots": len(unresolved_slots),
        "lockedIntroUnresolvedSlotKeys": [
            {"measureNumber": measure, "expectedStep": step}
            for measure, step in unresolved_slots
        ],
        "measuresCovered": covered,
        "missingMeasures": missing_measures,
        "measures17To113Preserved": measures_17_113_preserved,
        "professionalNotesCopiedIntoOutput": False,
        "audioDerivedConsensusOnly": True,
        "readyForFullSongTraining": passed,
        "productionPromotionAllowed": False,
    })

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "boundSourceEvents": len(source_events),
        "consensusRecoveryRows": len(recovery_rows),
        "recoveredEventsAdded": len(recovered_events),
        "outputEvents": len(output_events),
        "recoveredSlotKeys": recovered_slot_keys,
        "unresolvedIntroSlots": len(unresolved_slots),
        "unresolvedIntroSlotKeys": [
            {"measureNumber": measure, "expectedStep": step}
            for measure, step in unresolved_slots
        ],
        "coveredMeasures": len(covered),
        "missingMeasures": missing_measures,
        "measures17To113Preserved": measures_17_113_preserved,
        "professionalNotesCopiedIntoOutput": False,
        "audioDerivedConsensusOnly": True,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Full-song V8 intro consensus-recovery projection V1 complete")
    print("Passed:", passed)
    print("Bound source events:", len(source_events))
    print("Consensus recovery rows:", len(recovery_rows))
    print("Recovered events added:", len(recovered_events))
    print("Output events:", len(output_events))
    print("Recovered slot keys:", recovered_slot_keys)
    print("Unresolved intro slots:", len(unresolved_slots))
    print("Unresolved intro slot keys:", unresolved_slots)
    print("Covered measures:", len(covered))
    print("Missing measures:", missing_measures)
    print("Measures 17-113 preserved:", measures_17_113_preserved)
    print("Professional notes copied into output: False")
    print("Audio-derived consensus only: True")
    print("Ready for full-song training:", passed)
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit("Consensus recovery projection did not pass protected checks")


if __name__ == "__main__":
    main()
