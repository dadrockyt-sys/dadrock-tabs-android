from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOUND_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1.json"
RECOVERY_PATH = ROOT / "public" / "gomyway-intro-unresolved-slot-consensus-recovery-v2.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2-manifest.json"
EXPECTED_STEPS = (2, 4, 6, 9, 11, 14)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def measure_number(event: dict[str, Any]) -> int | None:
    try:
        return int(event.get("measureNumber", event.get("measure")))
    except (TypeError, ValueError):
        return None


def step_number(event: dict[str, Any]) -> int | None:
    try:
        return int(event.get("quantizedStep", event.get("step")))
    except (TypeError, ValueError):
        return None


def event_signature(event: dict[str, Any]) -> tuple[Any, ...]:
    notes = event.get("notes", [])
    normalized: list[tuple[int, int]] = []
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            try:
                normalized.append((int(note.get("string", note.get("stringIndex"))), int(note.get("fret"))))
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
    return measure_number(event), step_number(event), tuple(sorted(set(normalized))), duration, techniques


def main() -> None:
    bound = load(BOUND_PATH)
    recovery = load(RECOVERY_PATH)

    if recovery.get("readyForRecoveryProjection") is not True:
        raise RuntimeError("V2 consensus audit did not authorize recovery projection")

    exact_count = int(recovery.get("exactUnresolvedSlotCount", -1))
    manifest_count = int(recovery.get("manifestUnresolvedSlotCount", -2))
    recoverable_count = int(recovery.get("consensusRecoverableSlotCount", -3))
    if not (exact_count == manifest_count == recoverable_count == 10):
        raise RuntimeError(
            f"Expected exactly 10 authorized recovery slots, got exact={exact_count}, "
            f"manifest={manifest_count}, recoverable={recoverable_count}"
        )

    source_events = bound.get("events", bound.get("candidates", []))
    if not isinstance(source_events, list):
        raise RuntimeError("Bound intro source has no event list")

    rows = recovery.get("recoveryRows", [])
    if not isinstance(rows, list) or len(rows) != 10:
        raise RuntimeError(f"Expected 10 V2 recovery rows, got {len(rows) if isinstance(rows, list) else 'invalid'}")

    output_events = [copy.deepcopy(event) for event in source_events if isinstance(event, dict)]
    existing_signatures = {event_signature(event) for event in output_events}
    recovered_events: list[dict[str, Any]] = []

    for row in rows:
        if not isinstance(row, dict) or row.get("readyForRecovery") is not True:
            raise RuntimeError("V2 recovery row is not authorized")
        signature = row.get("selectedSignature")
        if not isinstance(signature, dict):
            raise RuntimeError("V2 recovery row has no selected signature")

        measure = int(row["measureNumber"])
        step = int(row["expectedStep"])
        event = {
            "measureNumber": measure,
            "quantizedStep": step,
            "durationSteps": int(signature.get("durationSteps") or 1),
            "notes": copy.deepcopy(signature.get("notes") or []),
            "techniques": copy.deepcopy(signature.get("techniques") or []),
            "confidence": 1.0,
            "source": "audio-derived repeated-intro consensus-v2",
            "introRecovery": {
                "schemaVersion": 2,
                "mode": "exact-unresolved-consensus-recovery",
                "supportingMeasures": copy.deepcopy(row.get("supportingMeasures", [])),
                "supportCount": int(row.get("supportCount") or 0),
                "professionalNotesCopied": False,
                "audioDerivedConsensusOnly": True,
            },
        }
        signature_key = event_signature(event)
        if signature_key in existing_signatures:
            raise RuntimeError(f"Recovery event already exists for measure {measure}, step {step}")
        existing_signatures.add(signature_key)
        recovered_events.append(event)
        output_events.append(event)

    output_events.sort(key=lambda event: (
        measure_number(event) if measure_number(event) is not None else 9999,
        step_number(event) if step_number(event) is not None else 9999,
    ))

    covered = sorted({measure_number(event) for event in output_events if measure_number(event) is not None})
    missing_measures = sorted(set(range(1, 114)) - set(covered))
    intro_slots = {
        (measure_number(event), step_number(event))
        for event in output_events
        if measure_number(event) in range(1, 17) and step_number(event) is not None
    }
    expected_slots = {(measure, step) for measure in range(1, 17) for step in EXPECTED_STEPS}
    unresolved_slots = sorted(expected_slots - intro_slots)

    source_17_113 = [event_signature(event) for event in source_events if measure_number(event) in range(17, 114)]
    output_17_113 = [event_signature(event) for event in output_events if measure_number(event) in range(17, 114)]
    preserved_17_113 = source_17_113 == output_17_113

    recovered_keys = sorted((measure_number(event), step_number(event)) for event in recovered_events)
    passed = bool(
        len(source_events) == 939
        and len(recovered_events) == 10
        and len(output_events) == 949
        and not unresolved_slots
        and len(covered) == 113
        and not missing_measures
        and preserved_17_113
    )

    result = copy.deepcopy(bound)
    result.update({
        "schemaVersion": 5,
        "candidateType": "full-song-rhythm-with-locked-intro-and-exact-consensus-recovery-v2",
        "sourceBoundPath": str(BOUND_PATH.relative_to(ROOT)),
        "recoveryAuditPath": str(RECOVERY_PATH.relative_to(ROOT)),
        "events": output_events,
        "candidates": output_events,
        "eventCount": len(output_events),
        "consensusRecoveredIntroSlots": recovered_keys,
        "consensusRecoveredIntroSlotCount": len(recovered_events),
        "lockedIntroUnresolvedSlots": len(unresolved_slots),
        "lockedIntroUnresolvedSlotKeys": [
            {"measureNumber": measure, "expectedStep": step} for measure, step in unresolved_slots
        ],
        "measuresCovered": covered,
        "missingMeasures": missing_measures,
        "measures17To113Preserved": preserved_17_113,
        "professionalNotesCopiedIntoOutput": False,
        "audioDerivedConsensusOnly": True,
        "readyForFullSongTraining": passed,
        "productionPromotionAllowed": False,
    })

    manifest = {
        "schemaVersion": 2,
        "passed": passed,
        "boundSourceEvents": len(source_events),
        "authorizedRecoveryRows": len(rows),
        "recoveredEventsAdded": len(recovered_events),
        "outputEvents": len(output_events),
        "recoveredSlotKeys": recovered_keys,
        "unresolvedIntroSlots": len(unresolved_slots),
        "unresolvedIntroSlotKeys": [
            {"measureNumber": measure, "expectedStep": step} for measure, step in unresolved_slots
        ],
        "coveredMeasures": len(covered),
        "missingMeasures": missing_measures,
        "measures17To113Preserved": preserved_17_113,
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

    print("Full-song V8 intro exact consensus-recovery projection V2 complete")
    print("Passed:", passed)
    print("Bound source events:", len(source_events))
    print("Authorized recovery rows:", len(rows))
    print("Recovered events added:", len(recovered_events))
    print("Output events:", len(output_events))
    print("Recovered slot keys:", recovered_keys)
    print("Unresolved intro slots:", len(unresolved_slots))
    print("Unresolved intro slot keys:", unresolved_slots)
    print("Covered measures:", len(covered))
    print("Missing measures:", missing_measures)
    print("Measures 17-113 preserved:", preserved_17_113)
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
        raise SystemExit("V2 consensus recovery projection did not pass protected checks")


if __name__ == "__main__":
    main()
