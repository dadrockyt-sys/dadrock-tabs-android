from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2.json"
BINDING_MANIFEST_PATH = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1-manifest.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-intro-unresolved-slot-consensus-recovery-v2.json"
INTRO_MEASURES = range(1, 17)
MIN_SUPPORTING_MEASURES = 2


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


def normalized_notes(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    notes = event.get("notes")
    pairs: list[tuple[int, int]] = []
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            try:
                pairs.append((int(note.get("string", note.get("stringIndex"))), int(note.get("fret"))))
            except (TypeError, ValueError):
                continue
    else:
        try:
            pairs.append((int(event.get("string", event.get("stringIndex"))), int(event.get("fret"))))
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
    try:
        duration = int(event.get("durationSteps", event.get("duration", 1)))
    except (TypeError, ValueError):
        duration = 1
    return notes, duration, technique_signature(event)


def exact_unresolved_slots(manifest: dict[str, Any]) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    reports = manifest.get("measureReports", [])
    if not isinstance(reports, list):
        return rows
    for report in reports:
        if not isinstance(report, dict):
            continue
        try:
            measure = int(report.get("measureNumber"))
        except (TypeError, ValueError):
            continue
        bindings = report.get("bindings", [])
        if not isinstance(bindings, list):
            continue
        for binding in bindings:
            if not isinstance(binding, dict) or binding.get("sourceStep") is not None:
                continue
            try:
                rows.append({"measureNumber": measure, "expectedStep": int(binding.get("expectedStep"))})
            except (TypeError, ValueError):
                continue
    return rows


def main() -> None:
    candidates = load(CANDIDATES_PATH)
    manifest = load(BINDING_MANIFEST_PATH)
    events = candidates.get("events", candidates.get("candidates", []))
    if not isinstance(events, list):
        raise RuntimeError("Candidate source has no event list")

    unresolved_slots = exact_unresolved_slots(manifest)
    expected_count = int(manifest.get("unresolvedIntroSlots", -1))
    if not unresolved_slots:
        raise RuntimeError("Binding manifest has no exact unresolved bindings")
    if len(unresolved_slots) != expected_count:
        raise RuntimeError(
            f"Exact unresolved-slot count {len(unresolved_slots)} does not match manifest count {expected_count}"
        )

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

        for donor_measure in INTRO_MEASURES:
            if donor_measure == measure:
                continue
            for donor_step in (expected_step - 1, expected_step, expected_step + 1):
                if donor_step < 0 or donor_step > 15:
                    continue
                for event in by_measure_step.get((donor_measure, donor_step), []):
                    signature = event_signature(event)
                    if signature is not None:
                        signature_support[signature].add(donor_measure)

        ranked = sorted(signature_support.items(), key=lambda item: (len(item[1]), item[0]), reverse=True)
        selected = ranked[0][0] if ranked else None
        supporting_measures = sorted(signature_support[selected]) if selected else []
        ready = selected is not None and len(supporting_measures) >= MIN_SUPPORTING_MEASURES
        recovery_rows.append({
            "measureNumber": measure,
            "expectedStep": expected_step,
            "selectedSignature": {
                "notes": [{"string": string_value, "fret": fret_value} for string_value, fret_value in selected[0]],
                "durationSteps": selected[1],
                "techniques": list(selected[2]),
            } if selected else None,
            "supportingMeasures": supporting_measures,
            "supportCount": len(supporting_measures),
            "candidateSignatureCount": len(ranked),
            "readyForRecovery": ready,
            "source": "audio-derived repeated-intro consensus",
        })

    unresolved_after = [
        {"measureNumber": row["measureNumber"], "expectedStep": row["expectedStep"]}
        for row in recovery_rows if not row["readyForRecovery"]
    ]
    ready = len(recovery_rows) == expected_count and not unresolved_after
    report = {
        "schemaVersion": 2,
        "auditType": "intro-exact-unresolved-slot-consensus-recovery",
        "candidatePath": str(CANDIDATES_PATH.relative_to(ROOT)),
        "bindingManifestPath": str(BINDING_MANIFEST_PATH.relative_to(ROOT)),
        "manifestUnresolvedSlotCount": expected_count,
        "exactUnresolvedSlotCount": len(unresolved_slots),
        "consensusRecoverableSlotCount": sum(1 for row in recovery_rows if row["readyForRecovery"]),
        "unresolvedAfterConsensus": unresolved_after,
        "recoveryRows": recovery_rows,
        "readyForRecoveryProjection": ready,
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

    print("Intro exact unresolved-slot consensus recovery V2 complete")
    print("Manifest unresolved slots:", expected_count)
    print("Exact unresolved slots selected:", len(unresolved_slots))
    print("Consensus-recoverable slots:", report["consensusRecoverableSlotCount"])
    print("Still unresolved after consensus:", unresolved_after)
    print("Ready for recovery projection:", ready)
    print()
    for row in recovery_rows:
        print(
            f"measure={row['measureNumber']} step={row['expectedStep']} "
            f"support={row['supportCount']} supportingMeasures={row['supportingMeasures']} "
            f"ready={row['readyForRecovery']} signature={row['selectedSignature']}"
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
