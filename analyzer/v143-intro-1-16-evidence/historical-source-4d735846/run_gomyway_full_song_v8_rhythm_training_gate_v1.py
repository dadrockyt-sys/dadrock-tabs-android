from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
SOURCE_MANIFEST_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2-manifest.json"
BOUND_SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1.json"
UNIVERSAL_GATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2-rhythm-training-gate-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-training-gate-v1.json"

EXPECTED_MEASURES = set(range(1, 114))
EXPECTED_INTRO_SLOTS = {(measure, step) for measure in range(1, 17) for step in (2, 4, 6, 9, 11, 14)}
EXPECTED_EVENT_COUNT = 949
EXPECTED_NOTE_COUNT = 1457

PROTECTED_ARTIFACTS = (
    PUBLIC / "gomyway-out-chorus-retention-conclusion-v1.json",
    PUBLIC / "gomyway-final-ending-validation-benchmark-v1.json",
)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def notes(event: dict[str, Any]) -> list[dict[str, Any]]:
    value = event.get("notes")
    if isinstance(value, list):
        return [note for note in value if isinstance(note, dict)]
    return []


def normalized_signature(event: dict[str, Any]) -> tuple[Any, ...]:
    normalized_notes: list[tuple[int | None, int | None, int | None]] = []
    for note in notes(event):
        normalized_notes.append((
            integer(note.get("string", note.get("stringIndex"))),
            integer(note.get("fret")),
            integer(note.get("midi", note.get("pitch"))),
        ))
    return (
        measure(event),
        step(event),
        tuple(sorted(normalized_notes)),
        integer(event.get("durationSteps", event.get("duration", 1))),
    )


def section_artifact_status(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path.relative_to(ROOT)), "exists": False, "passed": False}
    try:
        payload = load(path)
    except Exception as exc:  # audit must report malformed artifacts rather than mutate them
        return {
            "path": str(path.relative_to(ROOT)),
            "exists": True,
            "passed": False,
            "error": str(exc),
        }
    passed = payload.get("passed") is True
    return {
        "path": str(path.relative_to(ROOT)),
        "exists": True,
        "passed": passed,
        "sha256": sha256(path),
    }


def main() -> None:
    source = load(SOURCE_PATH)
    source_manifest = load(SOURCE_MANIFEST_PATH)
    bound = load(BOUND_SOURCE_PATH)
    universal = load(UNIVERSAL_GATE_PATH)

    source_events = events_from(source)
    bound_events = events_from(bound)

    covered_measures = {m for event in source_events for m in [measure(event)] if m is not None}
    missing_measures = sorted(EXPECTED_MEASURES - covered_measures)
    extra_measures = sorted(covered_measures - EXPECTED_MEASURES)

    intro_slots = {
        (measure(event), step(event))
        for event in source_events
        if measure(event) in range(1, 17) and step(event) is not None
    }
    missing_intro_slots = sorted(EXPECTED_INTRO_SLOTS - intro_slots)
    intro_nonzero_steps = {
        measure(event)
        for event in source_events
        if measure(event) in range(1, 17) and step(event) not in (None, 0)
    }

    source_17_113 = [
        normalized_signature(event)
        for event in source_events
        if measure(event) in range(17, 114)
    ]
    bound_17_113 = [
        normalized_signature(event)
        for event in bound_events
        if measure(event) in range(17, 114)
    ]
    measures_17_113_preserved = source_17_113 == bound_17_113

    invalid_timing: list[int] = []
    invalid_notes: list[dict[str, Any]] = []
    empty_notes: list[int] = []
    note_count = 0
    traceable_events = 0

    for index, event in enumerate(source_events):
        if measure(event) is None or step(event) is None:
            invalid_timing.append(index)
        event_notes = notes(event)
        if not event_notes:
            empty_notes.append(index)
        note_count += len(event_notes)
        if any(key in event for key in ("source", "sourceEventIndex", "trace", "origin", "confidence")):
            traceable_events += 1
        for note in event_notes:
            string_value = integer(note.get("string", note.get("stringIndex")))
            fret_value = integer(note.get("fret"))
            midi_value = integer(note.get("midi", note.get("pitch")))
            if not (
                string_value is not None
                and 1 <= string_value <= 6
                and fret_value is not None
                and 0 <= fret_value <= 24
                and (midi_value is None or 40 <= midi_value <= 88)
            ):
                invalid_notes.append({
                    "eventIndex": index,
                    "string": string_value,
                    "fret": fret_value,
                    "midi": midi_value,
                })

    signature_counts = Counter(normalized_signature(event) for event in source_events)
    duplicate_instances = sum(count - 1 for count in signature_counts.values() if count > 1)

    universal_event_sha = ((universal.get("eventSource") or {}).get("sha256"))
    source_sha = sha256(SOURCE_PATH)
    universal_stem = universal.get("stem") or {}

    protected_artifacts = [section_artifact_status(path) for path in PROTECTED_ARTIFACTS]
    protected_artifacts_passed = all(row["exists"] and row["passed"] for row in protected_artifacts)

    checks = {
        "universalStemGatePassed": universal.get("passed") is True,
        "universalGatePartIsRhythm": universal.get("part") == "rhythm",
        "universalGateEventSourceMatches": universal_event_sha == source_sha,
        "separatedStemRecorded": bool(universal_stem.get("sha256")) and universal_stem.get("durationSeconds", 0) > 0,
        "sourceManifestPassed": source_manifest.get("passed") is True,
        "eventCountExact": len(source_events) == EXPECTED_EVENT_COUNT,
        "noteCountExact": note_count == EXPECTED_NOTE_COUNT,
        "measureCoverageComplete": not missing_measures and not extra_measures and len(covered_measures) == 113,
        "allLockedIntroSlotsPresent": not missing_intro_slots and EXPECTED_INTRO_SLOTS.issubset(intro_slots),
        "allIntroMeasuresHaveNonzeroAttacks": intro_nonzero_steps == set(range(1, 17)),
        "measures17To113Preserved": measures_17_113_preserved,
        "allEventsTimed": not invalid_timing,
        "allEventsContainNotes": not empty_notes,
        "allNotesPlayable": not invalid_notes,
        "noDuplicateAttacks": duplicate_instances == 0,
        "allEventsTraceable": traceable_events == len(source_events),
        "protectedSectionArtifactsPassed": protected_artifacts_passed,
        "professionalNotesNotCopied": source.get("professionalNotesCopiedIntoOutput") is False,
        "audioDerivedConsensusOnly": source.get("audioDerivedConsensusOnly") is True,
        "productionPromotionDisabled": True,
    }
    passed = all(checks.values())

    report = {
        "schemaVersion": 1,
        "gateType": "gomyway-full-song-v8-rhythm-training",
        "passed": passed,
        "source": {
            "path": str(SOURCE_PATH.relative_to(ROOT)),
            "sha256": source_sha,
            "events": len(source_events),
            "notes": note_count,
            "traceableEvents": traceable_events,
        },
        "separatedStem": {
            "path": universal_stem.get("path"),
            "sha256": universal_stem.get("sha256"),
            "durationSeconds": universal_stem.get("durationSeconds"),
            "sampleRate": universal_stem.get("sampleRate"),
            "channels": universal_stem.get("channels"),
        },
        "measureCoverage": {
            "coveredCount": len(covered_measures),
            "missingMeasures": missing_measures,
            "extraMeasures": extra_measures,
        },
        "intro": {
            "expectedLockedSlots": len(EXPECTED_INTRO_SLOTS),
            "presentLockedSlots": len(EXPECTED_INTRO_SLOTS & intro_slots),
            "missingLockedSlots": [
                {"measureNumber": measure_value, "quantizedStep": step_value}
                for measure_value, step_value in missing_intro_slots
            ],
            "measuresWithNonzeroAttacks": sorted(intro_nonzero_steps),
            "stepZeroCollapseDetected": intro_nonzero_steps != set(range(1, 17)),
        },
        "preservation": {
            "measures17To113Preserved": measures_17_113_preserved,
            "boundSourcePath": str(BOUND_SOURCE_PATH.relative_to(ROOT)),
        },
        "quality": {
            "invalidTimingEventIndexes": invalid_timing[:100],
            "emptyNoteEventIndexes": empty_notes[:100],
            "invalidNotes": invalid_notes[:100],
            "duplicateAttackInstances": duplicate_instances,
        },
        "protectedSectionArtifacts": protected_artifacts,
        "checks": checks,
        "readyForRhythmTraining": passed,
        "readyForRhythmTablatureProof": passed,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Gomyway full-song V8 rhythm training gate V1 complete")
    print("Passed:", passed)
    print("Events:", len(source_events))
    print("Notes:", note_count)
    print("Covered measures:", len(covered_measures))
    print("Missing measures:", missing_measures)
    print("Locked intro slots present:", len(EXPECTED_INTRO_SLOTS & intro_slots), "/", len(EXPECTED_INTRO_SLOTS))
    print("Missing intro slots:", len(missing_intro_slots))
    print("Intro measures with nonzero attacks:", sorted(intro_nonzero_steps))
    print("Step-zero collapse detected:", checks["allIntroMeasuresHaveNonzeroAttacks"] is False)
    print("Measures 17-113 preserved:", measures_17_113_preserved)
    print("Invalid timing events:", len(invalid_timing))
    print("Empty-note events:", len(empty_notes))
    print("Invalid notes:", len(invalid_notes))
    print("Duplicate attack instances:", duplicate_instances)
    print("Traceable events:", traceable_events)
    print("Protected section artifacts passed:", protected_artifacts_passed)
    print("Ready for rhythm training:", passed)
    print("Ready for rhythm tablature proof:", passed)
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))

    if not passed:
        failed = [name for name, value in checks.items() if not value]
        print("Failed checks:", failed)
        raise SystemExit("Full-song rhythm training gate did not pass")


if __name__ == "__main__":
    main()
