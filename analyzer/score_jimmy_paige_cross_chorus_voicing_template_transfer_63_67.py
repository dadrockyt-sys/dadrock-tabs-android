from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
)
VALIDATION_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-cross-chorus-voicing-template-transfer-63-67.json"
)

SOURCE_TO_HELD_OUT = {33: 63, 34: 64, 35: 65, 36: 66, 37: 67}
MAX_TIMING_DELTA_SECONDS = 0.30
MIN_PITCH_CLASS_RECALL = 0.50


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _fret_to_midi(voicing: list[int | None]) -> list[int]:
    open_strings = [64, 59, 55, 50, 45, 40]
    return [
        open_pitch + int(fret)
        for open_pitch, fret in zip(open_strings, voicing)
        if fret is not None
    ]


def _attack_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for measure in validation.get("measureReports", []):
        if not isinstance(measure, dict):
            continue
        for attack in measure.get("attacks", []):
            if isinstance(attack, dict):
                rows.append(attack)
    return rows


def main() -> None:
    reference = _load(REFERENCE_PATH)
    validation = _load(VALIDATION_PATH)
    observed_rows = _attack_rows(validation)

    observed_lookup = {
        (
            int(row["heldOutMeasureNumber"]),
            int(row["attackNumber"]),
        ): row
        for row in observed_rows
    }

    transfer_rows: list[dict[str, Any]] = []

    for source_measure in reference["measures"]:
        source_number = int(source_measure["measureNumber"])
        if source_number not in SOURCE_TO_HELD_OUT:
            continue

        held_out_number = SOURCE_TO_HELD_OUT[source_number]
        for attack_number, attack in enumerate(source_measure["attacks"], start=1):
            observed = observed_lookup.get((held_out_number, attack_number))
            if observed is None:
                transfer_rows.append(
                    {
                        "sourceMeasureNumber": source_number,
                        "heldOutMeasureNumber": held_out_number,
                        "attackNumber": attack_number,
                        "chordLabels": source_measure["chordLabels"],
                        "eligibleForTemplateTransfer": False,
                        "reason": "missing-held-out-attack-row",
                    }
                )
                continue

            exact_pass = bool(observed.get("exactPass", False))
            pitch_class_pass = bool(observed.get("pitchClassPass", False))
            timing_delta = observed.get("absoluteTimingDeltaSeconds")
            timing_pass = (
                timing_delta is not None
                and float(timing_delta) <= MAX_TIMING_DELTA_SECONDS
            )
            pitch_class_recall = float(observed.get("pitchClassRecall", 0.0))

            template_frets = attack["voicingFretsHighToLow"]
            template_pitches = _fret_to_midi(template_frets)

            eligible = bool(
                not exact_pass
                and pitch_class_pass
                and timing_pass
                and pitch_class_recall >= MIN_PITCH_CLASS_RECALL
            )

            transfer_rows.append(
                {
                    "sourceMeasureNumber": source_number,
                    "heldOutMeasureNumber": held_out_number,
                    "attackNumber": attack_number,
                    "chordLabels": source_measure["chordLabels"],
                    "targetPhase": attack["phase"],
                    "observedPitches": observed.get("candidatePitches", []),
                    "observedExactVoicingRecall": observed.get(
                        "exactVoicingRecall",
                        0.0,
                    ),
                    "observedPitchClassRecall": pitch_class_recall,
                    "absoluteTimingDeltaSeconds": timing_delta,
                    "exactPass": exact_pass,
                    "pitchClassPass": pitch_class_pass,
                    "templateFretsHighToLow": template_frets,
                    "templateMidiPitches": template_pitches,
                    "eligibleForTemplateTransfer": eligible,
                    "reason": (
                        "already-exact"
                        if exact_pass
                        else "guarded-repeated-section-template"
                        if eligible
                        else "insufficient-held-out-evidence"
                    ),
                }
            )

    exact_rows = [row for row in transfer_rows if row.get("exactPass")]
    eligible_rows = [
        row for row in transfer_rows if row.get("eligibleForTemplateTransfer")
    ]
    unresolved_rows = [
        row
        for row in transfer_rows
        if not row.get("exactPass")
        and not row.get("eligibleForTemplateTransfer")
    ]

    target_count = len(transfer_rows)
    resolved_equivalent = len(exact_rows) + len(eligible_rows)
    resolved_recall = (
        100.0 * resolved_equivalent / target_count if target_count else 0.0
    )

    measure_reports: list[dict[str, Any]] = []
    for measure_number in range(63, 68):
        rows = [
            row
            for row in transfer_rows
            if row.get("heldOutMeasureNumber") == measure_number
        ]
        measure_reports.append(
            {
                "measureNumber": measure_number,
                "exactAttacks": sum(1 for row in rows if row.get("exactPass")),
                "templateTransferEligibleAttacks": sum(
                    1 for row in rows if row.get("eligibleForTemplateTransfer")
                ),
                "unresolvedAttacks": sum(
                    1
                    for row in rows
                    if not row.get("exactPass")
                    and not row.get("eligibleForTemplateTransfer")
                ),
                "targetAttacks": len(rows),
            }
        )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-cross-chorus-voicing-template-transfer",
        "trainedSectionMeasures": [33, 34, 35, 36, 37],
        "heldOutSectionMeasures": [63, 64, 65, 66, 67],
        "exactMatchedAttacks": len(exact_rows),
        "templateTransferEligibleAttacks": len(eligible_rows),
        "unresolvedAttacks": len(unresolved_rows),
        "targetAttacks": target_count,
        "guardedResolvedEquivalentAttacks": resolved_equivalent,
        "guardedResolvedEquivalentRecallPercentage": round(
            resolved_recall,
            2,
        ),
        "measureReports": measure_reports,
        "transferRows": transfer_rows,
        "unresolvedRows": unresolved_rows,
        "policy": {
            "requiresRepeatedSectionMapping": True,
            "requiresHeldOutPitchClassPass": True,
            "requiresTimingWithinSeconds": MAX_TIMING_DELTA_SECONDS,
            "minimumPitchClassRecall": MIN_PITCH_CLASS_RECALL,
            "exactObservedVoicingRemainsPreferred": True,
            "templateTransferChangesEvaluationOnly": True,
            "templateTransferMayNotCreateNewChordAttacks": True,
            "templateTransferMayNotRunWithoutObservedHarmonicEvidence": True,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForCanonicalVoicingResolverPrototype": (
            len(unresolved_rows) == 0
            and resolved_recall >= 90.0
            and bool(eligible_rows)
        ),
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    print("Protected cross-chorus voicing template transfer complete")
    print(f"Exact observed attacks: {len(exact_rows)}/{target_count}")
    print(f"Template-transfer eligible attacks: {len(eligible_rows)}")
    print(f"Unresolved attacks: {len(unresolved_rows)}")
    print(
        f"Guarded resolved-equivalent attacks: {resolved_equivalent}/{target_count} "
        f"({payload['guardedResolvedEquivalentRecallPercentage']:.2f}%)"
    )
    for measure in measure_reports:
        print(
            f"Measure {measure['measureNumber']} | "
            f"exact={measure['exactAttacks']} | "
            f"template={measure['templateTransferEligibleAttacks']} | "
            f"unresolved={measure['unresolvedAttacks']} | "
            f"target={measure['targetAttacks']}"
        )
    for row in unresolved_rows:
        print(
            f"UNRESOLVED measure {row['heldOutMeasureNumber']} "
            f"attack {row['attackNumber']} | reason={row['reason']}"
        )
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
