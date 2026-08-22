from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-protected-chord-resolver-gate.json"
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
TRANSFER_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-cross-chorus-voicing-template-transfer-63-67.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-canonical-chord-resolver-prototype.json"

SOURCE_TO_HELD_OUT = {33: 63, 34: 64, 35: 65, 36: 66, 37: 67}


def load(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    gate = load(GATE_PATH)
    reference = load(REFERENCE_PATH)
    transfer = load(TRANSFER_PATH)

    if not bool(gate.get("gatePassed", False)):
        raise RuntimeError("Protected chord resolver gate has not passed")

    transfer_rows = transfer.get("transferRows", [])
    transfer_lookup = {
        (int(row["heldOutMeasureNumber"]), int(row["attackNumber"])): row
        for row in transfer_rows
        if isinstance(row, dict)
    }

    source_lookup = {
        int(measure["measureNumber"]): measure
        for measure in reference.get("measures", [])
        if isinstance(measure, dict)
    }

    resolved_attacks: list[dict[str, Any]] = []
    exact_count = 0
    template_count = 0

    for source_measure, heldout_measure in SOURCE_TO_HELD_OUT.items():
        source = source_lookup[source_measure]
        for attack_number, attack in enumerate(source["attacks"], start=1):
            observed = transfer_lookup[(heldout_measure, attack_number)]
            exact_pass = bool(observed.get("exactPass", False))
            template_eligible = bool(observed.get("eligibleForTemplateTransfer", False))

            if not exact_pass and not template_eligible:
                raise RuntimeError(
                    f"Unresolved held-out attack {heldout_measure}:{attack_number}"
                )

            resolution_mode = "observed-exact" if exact_pass else "guarded-template-transfer"
            if exact_pass:
                exact_count += 1
            else:
                template_count += 1

            resolved_attacks.append(
                {
                    "heldOutMeasureNumber": heldout_measure,
                    "attackNumber": attack_number,
                    "sourceTemplateMeasureNumber": source_measure,
                    "chordLabels": source.get("chordLabels", []),
                    "targetPhase": attack["phase"],
                    "resolutionMode": resolution_mode,
                    "resolvedFretsHighToLow": attack["voicingFretsHighToLow"],
                    "resolvedMidiPitches": observed.get("templateMidiPitches", []),
                    "observedMidiPitches": observed.get("observedPitches", []),
                    "observedPitchClassRecall": observed.get("observedPitchClassRecall", 0.0),
                    "absoluteTimingDeltaSeconds": observed.get("absoluteTimingDeltaSeconds"),
                    "guardRequirements": {
                        "repeatedSectionMappingPresent": True,
                        "observedChordAttackPresent": True,
                        "pitchClassRecognitionPassed": bool(observed.get("pitchClassPass", False)),
                        "timingWithin300ms": (
                            observed.get("absoluteTimingDeltaSeconds") is not None
                            and float(observed["absoluteTimingDeltaSeconds"]) <= 0.30
                        ),
                        "protectedResolverGatePassed": True,
                    },
                    "sourceEventMutationAllowed": False,
                    "syntheticAttackCreationAllowed": False,
                }
            )

    payload = {
        "prototypeVersion": 1,
        "prototypeType": "guarded-canonical-chord-voicing-resolver",
        "status": "evaluation-only",
        "sourceSectionMeasures": sorted(SOURCE_TO_HELD_OUT.keys()),
        "targetSectionMeasures": sorted(SOURCE_TO_HELD_OUT.values()),
        "exactObservedAttacks": exact_count,
        "guardedTemplateTransferredAttacks": template_count,
        "resolvedAttacks": len(resolved_attacks),
        "targetAttacks": len(resolved_attacks),
        "resolvedAttackPercentage": 100.0,
        "attackRows": resolved_attacks,
        "policy": {
            "professionalPdfRemainsScoringAuthority": True,
            "requiresProtectedGatePass": True,
            "requiresRepeatedSectionIdentity": True,
            "requiresObservedHarmonicEvidence": True,
            "requiresTimingWithinSeconds": 0.30,
            "exactObservedVoicingPreferred": True,
            "templateTransferMayNotCreateNewAttack": True,
            "templateTransferMayNotAlterSourcePitchEvidence": True,
            "templateTransferMayNotAlterSourceTimingEvidence": True,
            "templateTransferMayNotMutateProtectedEvents": True,
            "rendererChanged": False,
            "syntheticNotesAllowed": False,
            "productionPromotionAllowed": False,
        },
        "protectedCheckpoints": gate.get("scores", {}),
        "protectedPitchCheckpointChanged": False,
        "readyForReadOnlyIntegrationBenchmark": True,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Guarded canonical chord resolver prototype built")
    print(f"Exact observed attacks: {exact_count}")
    print(f"Guarded template-transferred attacks: {template_count}")
    print(f"Resolved attacks: {len(resolved_attacks)}/{len(resolved_attacks)} (100.00%)")
    print("Protected gate passed: True")
    print("Source events mutated: False")
    print("Synthetic attacks created: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for read-only integration benchmark: True")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
