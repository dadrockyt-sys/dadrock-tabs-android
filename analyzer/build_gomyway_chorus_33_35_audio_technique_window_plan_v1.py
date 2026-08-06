from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
INVENTORY_PATH = PUBLIC / "gomyway-chorus-33-35-bend-vibrato-inventory-v1.json"
FOCUSED_PROOF_PATH = PUBLIC / "gomyway-chorus-33-35-focused-proof-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-window-plan-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-chorus-33-35-audio-technique-window-plan-v1-manifest.json"

CHORUS_MEASURES = {33, 34, 35}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0.0 else None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("measureNumber", row.get("measure")))


def step_of(row: dict[str, Any]) -> int | None:
    return integer(row.get("quantizedStep", row.get("step")))


def event_start(row: dict[str, Any]) -> float | None:
    for key in (
        "startTime",
        "start_time",
        "start",
        "time",
        "onsetTime",
        "onset_time",
        "onset",
    ):
        value = number(row.get(key))
        if value is not None:
            return value
    return None


def event_end(row: dict[str, Any], start: float | None) -> float | None:
    for key in ("endTime", "end_time", "end", "offsetTime", "offset_time", "offset"):
        value = number(row.get(key))
        if value is not None and (start is None or value >= start):
            return value
    for key in ("duration", "durationSeconds", "duration_seconds"):
        duration = number(row.get(key))
        if duration is not None and start is not None:
            return start + duration
    return None


def normalized_notes(row: dict[str, Any]) -> list[dict[str, int]]:
    raw = row.get("notes")
    if not isinstance(raw, list):
        return []
    notes: set[tuple[int, int]] = set()
    for note in raw:
        if not isinstance(note, dict):
            continue
        string = integer(note.get("string", note.get("stringIndex")))
        fret = integer(note.get("fret"))
        if string is None or fret is None:
            continue
        if "stringIndex" in note and "string" not in note and 0 <= string <= 5:
            string += 1
        if 1 <= string <= 6 and 0 <= fret <= 24:
            notes.add((string, fret))
    return [
        {"string": string, "fret": fret}
        for string, fret in sorted(notes)
    ]


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    inventory = load(INVENTORY_PATH)
    proof = load(FOCUSED_PROOF_PATH)

    if inventory.get("passed") is not True:
        raise RuntimeError("Bend/vibrato inventory is not green.")
    if inventory.get("readyForAudioTechniqueEvidence") is not True:
        raise RuntimeError("Inventory is not ready for audio technique evidence.")
    if proof.get("passed") is not True:
        raise RuntimeError("Focused chorus proof is not green.")
    if proof.get("readyForTechniqueCorrectionWork") is not True:
        raise RuntimeError("Focused proof is not ready for technique work.")

    events = source_rows(source)
    if len(events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(events)}.")

    proof_attacks = {
        (int(row["measureNumber"]), int(row["quantizedStep"]))
        for row in proof.get("rows", [])
        if isinstance(row, dict)
    }

    chorus_rows: list[dict[str, Any]] = []
    timed_rows = 0
    melodic_rows = 0

    for source_index, event in enumerate(events):
        measure = measure_of(event)
        if measure not in CHORUS_MEASURES:
            continue

        step = step_of(event)
        notes = normalized_notes(event)
        start = event_start(event)
        end = event_end(event, start)
        if start is not None:
            timed_rows += 1
        if len(notes) == 1:
            melodic_rows += 1

        # Use a narrow pre-roll and a longer post-roll so later evidence code can
        # measure attack-to-sustain pitch motion without assigning a technique.
        analysis_start = max(0.0, start - 0.04) if start is not None else None
        natural_end = end if end is not None else (start + 0.45 if start is not None else None)
        analysis_end = natural_end + 0.12 if natural_end is not None else None

        chorus_rows.append({
            "sourceEventIndex": source_index,
            "measureNumber": measure,
            "quantizedStep": step,
            "notes": notes,
            "noteMultiplicity": len(notes),
            "isSingleNoteTechniqueCandidate": len(notes) == 1,
            "isRecoveredChordAttack": (measure, step) in proof_attacks if step is not None else False,
            "sourceStartSeconds": start,
            "sourceEndSeconds": end,
            "analysisWindowStartSeconds": round(analysis_start, 6) if analysis_start is not None else None,
            "analysisWindowEndSeconds": round(analysis_end, 6) if analysis_end is not None else None,
            "requestedEvidenceFeatures": [
                "monophonic-pitch-contour",
                "sustained-pitch-variance",
                "directional-pitch-rise",
                "pitch-return-after-rise",
                "modulation-rate",
                "modulation-depth-semitones",
            ],
            "bendSupportClaimed": False,
            "vibratoSupportClaimed": False,
            "readOnly": True,
        })

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    chorus_event_count_matches_inventory = (
        len(chorus_rows) == int(inventory.get("chorusEventCount", -1))
    )
    ready = (
        source_unchanged
        and len(events) == 949
        and chorus_event_count_matches_inventory
        and len(chorus_rows) > 0
        and timed_rows > 0
    )

    output = {
        "schemaVersion": 1,
        "planType": "read-only-chorus-audio-technique-evidence-windows",
        "passed": source_unchanged and chorus_event_count_matches_inventory,
        "chorusEventCount": len(chorus_rows),
        "timedChorusEventCount": timed_rows,
        "singleNoteTechniqueCandidateCount": melodic_rows,
        "eventsWithoutTimingCount": len(chorus_rows) - timed_rows,
        "rows": chorus_rows,
        "audioTechniqueSupportClaimed": False,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoProtectedSource": False,
        "protectedSourceEventCount": len(events),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "chorusEventCountMatchesInventory": chorus_event_count_matches_inventory,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": output["passed"],
        "chorusEventCount": len(chorus_rows),
        "timedChorusEventCount": timed_rows,
        "singleNoteTechniqueCandidateCount": melodic_rows,
        "audioTechniqueSupportClaimed": False,
        "protectedSourceEventCount": len(events),
        "protectedSourceHashUnchanged": source_unchanged,
        "readyForAudioTechniqueFeatureExtraction": ready,
        "sourceEventsModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CHORUS 33-35 AUDIO TECHNIQUE WINDOW PLAN V1 COMPLETE")
    print("Passed:", output["passed"])
    print("Chorus events planned:", len(chorus_rows))
    print("Timed chorus events:", timed_rows)
    print("Single-note technique candidates:", melodic_rows)
    print("Events without timing:", len(chorus_rows) - timed_rows)
    print("Audio technique support claimed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Chorus event count matches inventory:", chorus_event_count_matches_inventory)
    print("Professional reference used as training label only: True")
    print("Professional notes copied into protected source: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for audio technique feature extraction:", ready)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not output["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
