from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-baseline.json"
)
DIAGNOSIS_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-voicing-miss-diagnosis.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-pitch-class-recovery.json"
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _pitch_class(pitch: int) -> int:
    return int(pitch) % 12


def _candidate_pitches(row: dict[str, Any]) -> list[int]:
    for key in (
        "candidatePitches",
        "candidateMidiPitches",
        "observedPitches",
        "nearbyPitches",
    ):
        value = row.get(key)
        if isinstance(value, list):
            result: list[int] = []
            for item in value:
                if isinstance(item, int):
                    result.append(item)
                elif isinstance(item, dict):
                    for pitch_key in ("pitch", "midiPitch", "midi"):
                        if pitch_key in item:
                            result.append(int(item[pitch_key]))
                            break
            if result:
                return result
    return []


def _expected_pitches(row: dict[str, Any]) -> list[int]:
    value = row.get("expectedPitches", [])
    return [int(item) for item in value if isinstance(item, (int, float))]


def _pitch_class_recall(expected: list[int], candidate: list[int]) -> float:
    expected_classes = {_pitch_class(pitch) for pitch in expected}
    candidate_classes = {_pitch_class(pitch) for pitch in candidate}
    if not expected_classes:
        return 0.0
    return len(expected_classes & candidate_classes) / len(expected_classes)


def _exact_recall(expected: list[int], candidate: list[int]) -> float:
    expected_set = set(expected)
    candidate_set = set(candidate)
    if not expected_set:
        return 0.0
    return len(expected_set & candidate_set) / len(expected_set)


def main() -> None:
    baseline = _load(BASELINE_PATH)
    diagnosis = _load(DIAGNOSIS_PATH)

    diagnosis_rows = diagnosis.get("missedAttacks", diagnosis.get("reports", []))
    if not isinstance(diagnosis_rows, list):
        raise RuntimeError("Voicing diagnosis does not contain a usable miss list")

    lookup: dict[tuple[int, int], dict[str, Any]] = {}
    for row in diagnosis_rows:
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measureNumber", row.get("measure", -1)))
        attack = int(row.get("attackNumber", row.get("attack", -1)))
        if measure > 0 and attack > 0:
            lookup[(measure, attack)] = row

    attack_rows: list[dict[str, Any]] = []
    recovered_count = 0
    exact_count = 0

    for measure in baseline["measureReports"]:
        for attack in measure["attacks"]:
            measure_number = int(attack["measureNumber"])
            attack_number = int(attack["attackNumber"])
            expected = _expected_pitches(attack)
            candidate = _candidate_pitches(attack)

            if not candidate:
                diagnosis_row = lookup.get((measure_number, attack_number), {})
                candidate = _candidate_pitches(diagnosis_row)

            exact_recall = _exact_recall(expected, candidate)
            class_recall = _pitch_class_recall(expected, candidate)
            exact_pass = bool(attack.get("passed", False))
            timing_delta = attack.get("absoluteTimingDeltaSeconds")
            timing_pass = (
                timing_delta is not None and float(timing_delta) <= 0.30
            )
            pitch_class_recovered = bool(
                not exact_pass
                and timing_pass
                and class_recall >= 0.50
                and exact_recall < 0.50
            )
            guarded_pass = exact_pass or pitch_class_recovered

            if exact_pass:
                exact_count += 1
            if pitch_class_recovered:
                recovered_count += 1

            attack_rows.append(
                {
                    "measureNumber": measure_number,
                    "attackNumber": attack_number,
                    "chordLabels": attack.get("chordLabels", []),
                    "expectedPitches": expected,
                    "candidatePitches": candidate,
                    "exactVoicingRecall": round(exact_recall, 4),
                    "pitchClassRecall": round(class_recall, 4),
                    "absoluteTimingDeltaSeconds": timing_delta,
                    "exactPass": exact_pass,
                    "pitchClassRecovered": pitch_class_recovered,
                    "guardedPass": guarded_pass,
                    "classification": (
                        "exact-voicing-match"
                        if exact_pass
                        else "octave-displaced-chord-evidence"
                        if pitch_class_recovered
                        else "unrecovered"
                    ),
                }
            )

    guarded_matches = sum(1 for row in attack_rows if row["guardedPass"])
    target_count = len(attack_rows)
    recall = 100.0 * guarded_matches / target_count if target_count else 0.0

    measure_reports: list[dict[str, Any]] = []
    for measure_number in range(33, 39):
        rows = [row for row in attack_rows if row["measureNumber"] == measure_number]
        matched = sum(1 for row in rows if row["guardedPass"])
        recovered = sum(1 for row in rows if row["pitchClassRecovered"])
        measure_reports.append(
            {
                "measureNumber": measure_number,
                "matchedAttacks": matched,
                "targetAttacks": len(rows),
                "pitchClassRecoveredAttacks": recovered,
                "attackRecallPercentage": round(
                    100.0 * matched / len(rows) if rows else 0.0,
                    2,
                ),
                "attacks": rows,
            }
        )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "protected-professional-chord-pitch-class-recovery",
        "sourceBaseline": str(BASELINE_PATH.relative_to(REPO_ROOT)),
        "sourceVoicingDiagnosis": str(DIAGNOSIS_PATH.relative_to(REPO_ROOT)),
        "exactMatchedAttacks": exact_count,
        "pitchClassRecoveredAttacks": recovered_count,
        "guardedMatchedAttacks": guarded_matches,
        "targetAttacks": target_count,
        "guardedAttackRecallPercentage": round(recall, 2),
        "unrecoveredAttacks": [
            row for row in attack_rows if not row["guardedPass"]
        ],
        "measureReports": measure_reports,
        "policy": {
            "maximumTimingDeltaSeconds": 0.30,
            "minimumPitchClassRecall": 0.50,
            "exactVoicingStillPreferred": True,
            "octaveDisplacementIsEvidenceOnly": True,
            "stringAndFretAssignmentNotChanged": True,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForCrossSectionValidation": guarded_matches > exact_count,
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Protected pitch-class chord recovery scoring complete")
    print(f"Exact attacks: {exact_count}/{target_count}")
    print(f"Recovered octave-displaced attacks: {recovered_count}")
    print(
        f"Guarded attacks: {guarded_matches}/{target_count} "
        f"({payload['guardedAttackRecallPercentage']:.2f}%)"
    )
    for measure in measure_reports:
        print(
            f"Measure {measure['measureNumber']} | "
            f"{measure['matchedAttacks']}/{measure['targetAttacks']} | "
            f"recovered={measure['pitchClassRecoveredAttacks']}"
        )
    for row in payload["unrecoveredAttacks"]:
        print(
            f"UNRECOVERED measure {row['measureNumber']} "
            f"attack {row['attackNumber']} | "
            f"exact={row['exactVoicingRecall']:.2f} | "
            f"pitchClass={row['pitchClassRecall']:.2f} | "
            f"timing={row['absoluteTimingDeltaSeconds']}"
        )
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
