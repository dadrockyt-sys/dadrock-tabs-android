from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2.json"
BINDING_MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1-manifest.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-intro-unresolved-slot-consensus-recovery-v1.json"

INTRO_MEASURES = range(1, 17)
EXPECTED_STEPS = [2, 4, 6, 9, 11, 14]
MIN_SUPPORTING_MEASURES = 2


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


def normalized_notes(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    notes = event.get("notes")
    pairs: list[tuple[int, int]] = []

    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            string_value = note.get("string", note.get("stringIndex"))
            fret_value = note.get("fret")
            try:
                pairs.append((int(string_value), int(fret_value)))
            except (TypeError, ValueError):
                continue
    else:
        string_value = event.get("string", event.get("stringIndex"))
        fret_value = event.get("fret")
        try:
            pairs.append((int(string_value), int(fret_value)))
        except (TypeError, ValueError):
            pass

    return tuple(sorted(set(pairs)))


def technique_signature(event: dict[str, Any]) -> tuple[str, ...]:
    raw = event.get("techniques", event.get("technique", []))
    if isinstance(raw, str):
        return (raw,)
    if isinstance(raw, list):
        return tuple(sorted(str(value) for value in raw if value is not None))
    return tuple()


def event_signature(event: dict[str, Any]) -> tuple[Any, ...] | None:
    notes = normalized_notes(event)
    if not notes:
        return None
    duration = event.get("durationSteps", event.get("duration", 1))
    try:
        duration_value = int(duration)
    except (TypeError, ValueError):
        duration_value = 1
    return notes, duration_value, technique_signature(event)


def unresolved_slots_from_manifest(manifest: dict[str, Any]) -> list[dict[str, int]]:
    rows = manifest.get("unresolvedSlots")
    if isinstance(rows, list):
        cleaned: list[dict[str, int]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            try:
                cleaned.append({
                    "measureNumber": int(row.get("measureNumber", row.get("measure"))),
                    "expectedStep": int(row.get("expectedStep", row.get("step"))),
                })
            except (TypeError, ValueError):
                continue
        if cleaned:
            return cleaned

    unresolved_measures = manifest.get("unresolvedIntroMeasures", [])
    if not isinstance(unresolved_measures, list):
        return []

    return [
        {"measureNumber": int(measure), "expectedStep": step}
        for measure in unresolved_measures
        for step in EXPECTED_STEPS
    ]


def main() -> None:
    candidates = load(CANDIDATES_PATH)
    manifest = load(BINDING_MANIFEST_PATH)

    events = candidates.get("events", candidates.get("candidates", []))
    if not isinstance(events, list):
        raise RuntimeError("Candidate source has no event list")

    unresolved_slots = unresolved_slots_from_manifest(manifest)
    if not unresolved_slots:
        raise RuntimeError("Binding manifest has no unresolved slots")

    by_measure_step: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if not isinstance(event, dict):
            continue
        measure = measure_number(event)
        step = step_number(event)
        if measure in INTRO_MEASURES and step is not None:
            by_measure_step[(measure, step)].append(event)

    recovery_rows: list[dict[str, Any]] = []

    for unresolved in unresolved_slots:
        measure = unresolved["measureNumber"]
        expected_step = unresolved["expectedStep"]

        signature_support: dict[tuple[Any, ...], set[int]] = defaultdict(set)
        signature_examples: dict[tuple[Any, ...], dict[str, Any]] = {}

        for donor_measure in INTRO_MEASURES:
            if donor_measure == measure:
                continue
            for donor_step in (expected_step - 1, expected_step, expected_step + 1):
                if donor_step < 0 or donor_step > 15:
                    continue
                for event in by_measure_step.get((donor_measure, donor_step), []):
                    signature = event_signature(event)
                    if signature is None:
                        continue
                    signature_support[signature].add(donor_measure)
                    signature_examples.setdefault(signature, event)

        ranked = sorted(
            signature_support.items(),
            key=lambda item: (len(item[1]), item[0]),
            reverse=True,
        )
        selected_signature = ranked[0][0] if ranked else None
        supporting_measures = sorted(signature_support[selected_signature]) if selected_signature else []
        selected_example = signature_examples.get(selected_signature) if selected_signature else None
        ready = len(supporting_measures) >= MIN_SUPPORTING_MEASURES and selected_example is not None

        recovery_rows.append({
            "measureNumber": measure,
            "expectedStep": expected_step,
            "selectedSignature": {
                "notes": [
                    {"string": string_value, "fret": fret_value}
                    for string_value, fret_value in (selected_signature[0] if selected_signature else [])
                ],
                "durationSteps": selected_signature[1] if selected_signature else None,
                "techniques": list(selected_signature[2]) if selected_signature else [],
            } if selected_signature else None,
            "supportingMeasures": supporting_measures,
            "supportCount": len(supporting_measures),
            "candidateSignatureCount": len(ranked),
            "readyForRecovery": ready,
            "source": "audio-derived repeated-intro consensus",
        })

    ready_rows = [row for row in recovery_rows if row["readyForRecovery"]]
    unresolved_after_consensus = [
        {"measureNumber": row["measureNumber"], "expectedStep": row["expectedStep"]}
        for row in recovery_rows
        if not row["readyForRecovery"]
    ]
    ready_for_recovery_projection = len(ready_rows) == len(recovery_rows)

    report = {
        "schemaVersion": 1,
        "auditType": "intro-unresolved-slot-consensus-recovery",
        "candidatePath": str(CANDIDATES_PATH.relative_to(ROOT)),
        "bindingManifestPath": str(BINDING_MANIFEST_PATH.relative_to(ROOT)),
        "unresolvedSlotCount": len(unresolved_slots),
        "consensusRecoverableSlotCount": len(ready_rows),
        "unresolvedAfterConsensus": unresolved_after_consensus,
        "recoveryRows": recovery_rows,
        "readyForRecoveryProjection": ready_for_recovery_projection,
        "professionalNotesCopied": False,
        "audioDerivedConsensusOnly": True,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Intro unresolved-slot consensus recovery V1 complete")
    print("Unresolved slots from binding:", len(unresolved_slots))
    print("Consensus-recoverable slots:", len(ready_rows))
    print("Still unresolved after consensus:", unresolved_after_consensus)
    print("Ready for recovery projection:", ready_for_recovery_projection)
    print()

    for row in recovery_rows:
        print(
            f"measure={row['measureNumber']} "
            f"step={row['expectedStep']} "
            f"support={row['supportCount']} "
            f"supportingMeasures={row['supportingMeasures']} "
            f"ready={row['readyForRecovery']} "
            f"signature={row['selectedSignature']}"
        )

    print()
    print("Professional notes copied: False")
    print("Audio-derived consensus only: True")
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
