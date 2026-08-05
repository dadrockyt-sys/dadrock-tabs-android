from __future__ import annotations

import copy
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "public" / "gomyway-v8-supervised-intro-overlay-v2.json"
OUTPUT_PATH = ROOT / "public" / "gomyway-v8-supervised-intro-overlay-v3.json"
MANIFEST_PATH = ROOT / "public" / "gomyway-v8-supervised-intro-overlay-v3-manifest.json"

# Measures 2, 4 and 6 are repeated instances of the same two-measure intro phrase ending.
REPEAT_CLASS = [2, 4, 6]
ENDING_REGION_STEPS = {14, 15}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Expected overlay JSON object")
    return value


def note_signature(event: dict[str, Any]) -> tuple[tuple[int, int], ...]:
    notes = event.get("notes", [])
    rows: list[tuple[int, int]] = []
    if isinstance(notes, list):
        for note in notes:
            if not isinstance(note, dict):
                continue
            try:
                rows.append((int(note["stringIndex"]), int(note["fret"])))
            except (KeyError, TypeError, ValueError):
                continue
    return tuple(sorted(rows))


def main() -> None:
    overlay = load(INPUT_PATH)
    events = overlay.get("events", [])
    if not isinstance(events, list):
        raise RuntimeError("Overlay has no events list")

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        if not isinstance(event, dict):
            continue
        try:
            measure = int(event.get("measureNumber"))
        except (TypeError, ValueError):
            continue
        by_measure[measure].append(event)

    observations: dict[int, dict[str, Any]] = {}
    multiplicities: list[int] = []
    signatures: list[tuple[tuple[int, int], ...]] = []

    for measure in REPEAT_CLASS:
        ending_events = [
            event
            for event in by_measure.get(measure, [])
            if int(event.get("quantizedStep", -1)) in ENDING_REGION_STEPS
            and len(note_signature(event)) > 1
        ]
        multiplicity = len(ending_events)
        multiplicities.append(multiplicity)
        for event in ending_events:
            signatures.append(note_signature(event))
        observations[measure] = {
            "endingDoubleStopMultiplicity": multiplicity,
            "steps": sorted(int(event.get("quantizedStep")) for event in ending_events),
            "signatures": [list(map(list, note_signature(event))) for event in ending_events],
        }

    donor_multiplicities = [observations[measure]["endingDoubleStopMultiplicity"] for measure in REPEAT_CLASS[:-1]]
    if not donor_multiplicities or len(set(donor_multiplicities)) != 1:
        raise RuntimeError(f"Repeat-class donors disagree: {donor_multiplicities}")
    target_multiplicity = donor_multiplicities[0]
    if target_multiplicity < 1:
        raise RuntimeError("No approved ending double-stop multiplicity found")

    signature_counts = Counter(signatures)
    if not signature_counts:
        raise RuntimeError("No repeated ending double-stop signature found")
    selected_signature, signature_support = signature_counts.most_common(1)[0]

    output_events = [copy.deepcopy(event) for event in events]
    target_measure = REPEAT_CLASS[-1]
    target_ending = [
        event
        for event in output_events
        if int(event.get("measureNumber", -1)) == target_measure
        and int(event.get("quantizedStep", -1)) in ENDING_REGION_STEPS
        and note_signature(event) == selected_signature
    ]

    added: list[dict[str, Any]] = []
    while len(target_ending) < target_multiplicity:
        if not target_ending:
            source = next(
                (
                    event for event in output_events
                    if int(event.get("measureNumber", -1)) in REPEAT_CLASS[:-1]
                    and note_signature(event) == selected_signature
                    and int(event.get("quantizedStep", -1)) in ENDING_REGION_STEPS
                ),
                None,
            )
            if source is None:
                raise RuntimeError("Unable to find donor ending double-stop event")
            cloned = copy.deepcopy(source)
            cloned["measureNumber"] = target_measure
            cloned["quantizedStep"] = 14
        else:
            cloned = copy.deepcopy(target_ending[-1])
            cloned["quantizedStep"] = 15

        cloned["source"] = "repeat-class-consensus-training-only"
        cloned["supervisedTraining"] = {
            "schemaVersion": 3,
            "repeatClass": REPEAT_CLASS,
            "consensusMultiplicity": target_multiplicity,
            "donorMeasures": REPEAT_CLASS[:-1],
            "signatureSupport": signature_support,
            "humanVisualInspectionRequired": False,
            "productionEligible": False,
        }
        output_events.append(cloned)
        target_ending.append(cloned)
        added.append(cloned)

    output_events.sort(key=lambda event: (
        int(event.get("measureNumber", 9999)),
        int(event.get("quantizedStep", 9999)),
    ))

    final_observations: dict[int, int] = {}
    for measure in REPEAT_CLASS:
        final_observations[measure] = sum(
            1
            for event in output_events
            if int(event.get("measureNumber", -1)) == measure
            and int(event.get("quantizedStep", -1)) in ENDING_REGION_STEPS
            and note_signature(event) == selected_signature
        )

    passed = all(value == target_multiplicity for value in final_observations.values())
    result = copy.deepcopy(overlay)
    result.update({
        "schemaVersion": 3,
        "overlayType": "supervised-intro-training-target-with-repeat-consensus",
        "events": output_events,
        "eventCount": len(output_events),
        "repeatConsensus": {
            "measureClass": REPEAT_CLASS,
            "endingRegionSteps": sorted(ENDING_REGION_STEPS),
            "consensusMultiplicity": target_multiplicity,
            "selectedNoteSignature": [list(pair) for pair in selected_signature],
            "signatureSupport": signature_support,
            "before": observations,
            "afterMultiplicities": final_observations,
            "eventsAdded": len(added),
            "humanVisualInspectionRequired": False,
        },
        "trainingOnly": True,
        "productionEligible": False,
        "protected949EventSourceModified": False,
        "v7EventsModified": False,
        "protectedRendererModified": False,
        "productionPromotionAllowed": False,
    })

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "repeatClass": REPEAT_CLASS,
        "consensusMultiplicity": target_multiplicity,
        "beforeMultiplicities": {str(key): value["endingDoubleStopMultiplicity"] for key, value in observations.items()},
        "afterMultiplicities": {str(key): value for key, value in final_observations.items()},
        "eventsAdded": len(added),
        "addedMeasures": sorted({int(event["measureNumber"]) for event in added}),
        "humanVisualInspectionRequired": False,
        "trainingOnly": True,
        "productionEligible": False,
        "protected949EventSourceModified": False,
        "v7EventsModified": False,
        "protectedRendererModified": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("Gomyway intro repeat-consensus overlay V1 complete")
    print("Passed:", passed)
    print("Repeat class:", REPEAT_CLASS)
    print("Consensus ending multiplicity:", target_multiplicity)
    print("Before multiplicities:", {key: value["endingDoubleStopMultiplicity"] for key, value in observations.items()})
    print("After multiplicities:", final_observations)
    print("Events added:", len(added))
    print("Added measures:", sorted({int(event["measureNumber"]) for event in added}))
    print("Human visual inspection required: False")
    print("Training only: True")
    print("Production eligible: False")
    print("Protected 949-event source modified: False")
    print("V7 events modified: False")
    print("Protected renderer modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit("Repeat-consensus overlay did not pass")


if __name__ == "__main__":
    main()
