from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = ROOT / "analyzer" / "fixtures" / "gomyway_professional_intro_reference_v1.json"
TRAINING_GATE_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-training-gate-v1.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-intro-pitch-technique-training-pack-v1.json"

MEASURES = range(1, 7)
EXPECTED_STEPS = (2, 4, 6, 9, 11, 14)


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def measure_number(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_number(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def normalize_string(value: Any) -> int | None:
    number = integer(value)
    if number is None:
        return None
    # The professional fixture uses 0-based stringIndex. Most current events use 1-based string.
    if 1 <= number <= 6:
        return number - 1
    if 0 <= number <= 5:
        return number
    return None


def normalized_notes(event: dict[str, Any]) -> list[dict[str, int]]:
    raw_notes = event.get("notes")
    rows: list[dict[str, int]] = []
    if isinstance(raw_notes, list):
        candidates = raw_notes
    else:
        candidates = [event]
    for note in candidates:
        if not isinstance(note, dict):
            continue
        string_index = normalize_string(note.get("string", note.get("stringIndex")))
        fret = integer(note.get("fret"))
        if string_index is None or fret is None:
            continue
        rows.append({"stringIndex": string_index, "fret": fret})
    unique = {(row["stringIndex"], row["fret"]): row for row in rows}
    return [unique[key] for key in sorted(unique)]


def normalized_techniques(event: dict[str, Any]) -> list[str]:
    raw = event.get("techniques", event.get("technique", []))
    if isinstance(raw, str):
        values = [raw]
    elif isinstance(raw, list):
        values = [str(value) for value in raw if value is not None]
    else:
        values = []
    aliases = {
        "bend": "full-bend",
        "fullbend": "full-bend",
        "full bend": "full-bend",
        "full-step-bend": "full-bend",
        "full_step_bend": "full-bend",
    }
    return sorted({aliases.get(value.strip().lower(), value.strip().lower()) for value in values if value.strip()})


def expand_reference(reference: dict[str, Any]) -> dict[tuple[int, int], dict[str, Any]]:
    base_notes = reference.get("notes", [])
    if not isinstance(base_notes, list):
        raise RuntimeError("Professional intro fixture has no notes list")

    by_slot: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in base_notes:
        if not isinstance(row, dict):
            continue
        measure = integer(row.get("measure"))
        step = integer(row.get("step"))
        string_index = integer(row.get("stringIndex"))
        fret = integer(row.get("fret"))
        if None in (measure, step, string_index, fret):
            continue
        by_slot[(measure, step)].append(row)

    repeat = reference.get("repeat", {})
    targets = repeat.get("targetMeasureStarts", []) if isinstance(repeat, dict) else []
    for start in targets:
        start_measure = integer(start)
        if start_measure is None:
            continue
        for source_measure in (1, 2):
            target_measure = start_measure + source_measure - 1
            for (measure, step), rows in list(by_slot.items()):
                if measure != source_measure:
                    continue
                for row in rows:
                    copied = dict(row)
                    copied["measure"] = target_measure
                    by_slot[(target_measure, step)].append(copied)

    result: dict[tuple[int, int], dict[str, Any]] = {}
    for key, rows in by_slot.items():
        notes = sorted(
            [
                {"stringIndex": int(row["stringIndex"]), "fret": int(row["fret"])}
                for row in rows
            ],
            key=lambda note: (note["stringIndex"], note["fret"]),
        )
        techniques = sorted({str(row["technique"]) for row in rows if row.get("technique")})
        chord_ids = sorted({str(row["chordId"]) for row in rows if row.get("chordId")})
        result[key] = {
            "notes": notes,
            "techniques": techniques,
            "chordIds": chord_ids,
        }
    return result


def note_distance(candidate: list[dict[str, int]], target: list[dict[str, int]]) -> int:
    candidate_pairs = {(row["stringIndex"], row["fret"]) for row in candidate}
    target_pairs = {(row["stringIndex"], row["fret"]) for row in target}
    return len(candidate_pairs.symmetric_difference(target_pairs))


def main() -> None:
    source = load(SOURCE_PATH)
    reference = load(REFERENCE_PATH)
    training_gate = load(TRAINING_GATE_PATH)
    if training_gate.get("passed") is not True:
        raise RuntimeError("Full-song rhythm training gate is not green")

    events = source.get("events", source.get("candidates", []))
    if not isinstance(events, list):
        raise RuntimeError("Recovered rhythm source has no event list")

    reference_slots = expand_reference(reference)
    candidate_slots: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = measure_number(event)
        step = step_number(event)
        if measure in MEASURES and step in EXPECTED_STEPS:
            candidate_slots[(measure, step)].append(event)

    rows: list[dict[str, Any]] = []
    exact_note_matches = 0
    exact_technique_matches = 0
    bends_expected = 0
    bends_present = 0
    missing_candidate_slots: list[dict[str, int]] = []

    for measure in MEASURES:
        for step in EXPECTED_STEPS:
            key = (measure, step)
            target = reference_slots.get(key)
            if target is None:
                raise RuntimeError(f"Missing professional target for measure {measure}, step {step}")
            candidates = candidate_slots.get(key, [])
            if not candidates:
                missing_candidate_slots.append({"measureNumber": measure, "step": step})
                rows.append({
                    "measureNumber": measure,
                    "step": step,
                    "target": target,
                    "candidate": None,
                    "noteMatch": False,
                    "techniqueMatch": False,
                    "trainingAction": "recover-audio-candidate",
                })
                continue

            ranked = sorted(
                candidates,
                key=lambda event: (
                    note_distance(normalized_notes(event), target["notes"]),
                    -float(event.get("confidence", 0) or 0),
                ),
            )
            selected = ranked[0]
            candidate_notes = normalized_notes(selected)
            candidate_techniques = normalized_techniques(selected)
            note_match = candidate_notes == target["notes"]
            technique_match = candidate_techniques == target["techniques"]
            bend_expected = "full-bend" in target["techniques"]
            bend_present = "full-bend" in candidate_techniques

            exact_note_matches += int(note_match)
            exact_technique_matches += int(technique_match)
            bends_expected += int(bend_expected)
            bends_present += int(bend_expected and bend_present)

            if not note_match and not technique_match:
                action = "retrain-pitch-and-technique"
            elif not note_match:
                action = "retrain-pitch-fingering"
            elif not technique_match:
                action = "retrain-technique"
            else:
                action = "retain"

            rows.append({
                "measureNumber": measure,
                "step": step,
                "target": target,
                "candidate": {
                    "notes": candidate_notes,
                    "techniques": candidate_techniques,
                    "confidence": selected.get("confidence"),
                    "source": selected.get("source"),
                    "sourceEventIndex": selected.get("sourceEventIndex"),
                },
                "candidateCountAtSlot": len(candidates),
                "noteDistance": note_distance(candidate_notes, target["notes"]),
                "noteMatch": note_match,
                "techniqueMatch": technique_match,
                "bendExpected": bend_expected,
                "bendPresent": bend_present,
                "trainingAction": action,
            })

    total_slots = len(rows)
    mismatches = [row for row in rows if row["trainingAction"] != "retain"]
    bend_slots = [row for row in rows if row.get("bendExpected")]
    ready_for_supervised_intro_training = bool(
        total_slots == 36
        and not missing_candidate_slots
        and len(reference_slots) >= 36
        and training_gate.get("readyForRhythmTraining") is True
    )

    report = {
        "schemaVersion": 1,
        "packType": "focused-intro-pitch-technique-supervised-training-pack",
        "sourcePath": str(SOURCE_PATH.relative_to(ROOT)),
        "referencePath": str(REFERENCE_PATH.relative_to(ROOT)),
        "trainingGatePath": str(TRAINING_GATE_PATH.relative_to(ROOT)),
        "measureRange": [1, 6],
        "expectedSteps": list(EXPECTED_STEPS),
        "slotCount": total_slots,
        "exactNoteMatches": exact_note_matches,
        "exactNoteMatchRate": exact_note_matches / total_slots if total_slots else 0,
        "exactTechniqueMatches": exact_technique_matches,
        "exactTechniqueMatchRate": exact_technique_matches / total_slots if total_slots else 0,
        "bendsExpected": bends_expected,
        "bendsPresent": bends_present,
        "bendRecall": bends_present / bends_expected if bends_expected else 1,
        "mismatchCount": len(mismatches),
        "missingCandidateSlots": missing_candidate_slots,
        "rows": rows,
        "readyForSupervisedIntroTraining": ready_for_supervised_intro_training,
        "professionalReferenceUsedAsTrainingLabelOnly": True,
        "professionalNotesCopiedIntoOutput": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Gomyway focused intro pitch-technique training pack V1 complete")
    print("Measures: 1-6")
    print("Slots evaluated:", total_slots)
    print("Exact note matches:", f"{exact_note_matches} / {total_slots}")
    print("Exact technique matches:", f"{exact_technique_matches} / {total_slots}")
    print("Bends expected:", bends_expected)
    print("Bends present:", bends_present)
    print("Mismatch slots:", len(mismatches))
    print("Missing candidate slots:", missing_candidate_slots)
    print("Ready for supervised intro training:", ready_for_supervised_intro_training)
    print()
    for row in mismatches:
        print(
            f"measure={row['measureNumber']} step={row['step']} "
            f"action={row['trainingAction']} candidate={row['candidate']} target={row['target']}"
        )
    print()
    print("Professional reference used as training label only: True")
    print("Professional notes copied into output: False")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))

    if not ready_for_supervised_intro_training:
        raise SystemExit("Focused intro training pack did not pass protected prerequisites")


if __name__ == "__main__":
    main()
