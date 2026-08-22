from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
)
TIMING_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-timing-v1.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-jimmy-paige-professional-chords-33-38-baseline.json"
)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    reference = _load(REFERENCE_PATH)
    timing = _load(TIMING_PATH)
    best = timing["bestCalibration"]

    measures: list[dict[str, Any]] = []
    all_attack_rows: list[dict[str, Any]] = []

    for measure in best["measureReports"]:
        number = int(measure["measureNumber"])
        reference_measure = next(
            item for item in reference["measures"]
            if int(item["measureNumber"]) == number
        )

        attack_rows: list[dict[str, Any]] = []
        for index, attack in enumerate(measure["attacks"], start=1):
            passed = bool(attack.get("passed", False))
            voicing_recall = float(attack.get("voicingRecall", 0.0))
            timing_delta = attack.get("timingDeltaSeconds")
            absolute_delta = attack.get("absoluteTimingDeltaSeconds")

            row = {
                "measureNumber": number,
                "attackNumber": index,
                "chordLabels": reference_measure["chordLabels"],
                "targetPhase": attack["targetPhase"],
                "expectedPitches": attack["expectedPitches"],
                "candidatePitches": attack.get("candidatePitches", []),
                "voicingRecall": voicing_recall,
                "timingDeltaSeconds": timing_delta,
                "absoluteTimingDeltaSeconds": absolute_delta,
                "passed": passed,
                "failureReason": None,
            }

            if not passed:
                if absolute_delta is None:
                    row["failureReason"] = "no-multi-note-candidate"
                elif float(absolute_delta) > 0.30:
                    row["failureReason"] = "timing-outside-300ms"
                elif voicing_recall < 0.50:
                    row["failureReason"] = "voicing-recall-below-50-percent"
                else:
                    row["failureReason"] = "combined-timing-and-voicing-failure"

            attack_rows.append(row)
            all_attack_rows.append(row)

        passed_count = sum(1 for row in attack_rows if row["passed"])
        target_count = len(attack_rows)
        measure_recall = 100.0 * passed_count / target_count if target_count else 0.0
        passed_voicing = [
            row["voicingRecall"] for row in attack_rows if row["passed"]
        ]
        passed_timing = [
            float(row["absoluteTimingDeltaSeconds"])
            for row in attack_rows
            if row["passed"] and row["absoluteTimingDeltaSeconds"] is not None
        ]

        measures.append(
            {
                "measureNumber": number,
                "chordLabels": reference_measure["chordLabels"],
                "matchedAttacks": passed_count,
                "targetAttacks": target_count,
                "attackRecallPercentage": round(measure_recall, 2),
                "meanPassedVoicingRecall": (
                    round(mean(passed_voicing), 4) if passed_voicing else 0.0
                ),
                "meanPassedAbsoluteTimingDeltaSeconds": (
                    round(mean(passed_timing), 6) if passed_timing else None
                ),
                "attacks": attack_rows,
            }
        )

    matched = sum(1 for row in all_attack_rows if row["passed"])
    target = len(all_attack_rows)
    misses = [row for row in all_attack_rows if not row["passed"]]
    recall = 100.0 * matched / target if target else 0.0

    failure_counts: dict[str, int] = {}
    for row in misses:
        reason = str(row["failureReason"])
        failure_counts[reason] = failure_counts.get(reason, 0) + 1

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-rhythm-chord-section-protected-baseline",
        "sourceReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "sourceTimingCalibration": str(TIMING_PATH.relative_to(REPO_ROOT)),
        "tempoBpm": best["tempoBpm"],
        "firstMeasureOffsetSeconds": best["firstMeasureOffsetSeconds"],
        "groupWindowSeconds": best["groupWindowSeconds"],
        "matchedAttacks": matched,
        "targetAttacks": target,
        "attackRecallPercentage": round(recall, 2),
        "missedAttackCount": len(misses),
        "failureReasonCounts": failure_counts,
        "missedAttacks": misses,
        "measureReports": measures,
        "protectedCheckpointRequirements": reference[
            "protectedCheckpointRequirements"
        ],
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForMissedAttackDiagnosis": len(misses) > 0,
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional chord-section protected baseline complete")
    print(
        f"Matched attacks: {matched}/{target} "
        f"({payload['attackRecallPercentage']:.2f}%)"
    )
    print(f"Missed attacks: {len(misses)}")
    print(f"Failure reasons: {failure_counts}")

    for measure in measures:
        print(
            f"Measure {measure['measureNumber']:>2} "
            f"{','.join(measure['chordLabels'])} | "
            f"{measure['matchedAttacks']}/{measure['targetAttacks']} "
            f"({measure['attackRecallPercentage']:.2f}%)"
        )

    for row in misses:
        print(
            f"MISS measure {row['measureNumber']:>2} "
            f"attack {row['attackNumber']} | "
            f"phase={row['targetPhase']} | "
            f"timing={row['absoluteTimingDeltaSeconds']} | "
            f"voicingRecall={row['voicingRecall']:.2f} | "
            f"reason={row['failureReason']}"
        )

    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
