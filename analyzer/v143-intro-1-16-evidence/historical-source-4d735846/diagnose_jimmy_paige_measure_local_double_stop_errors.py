from __future__ import annotations

import json

from run_jimmy_paige_low_register_recovery_training_loop import REPO_ROOT

SCORE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-measure-local-double-stop-score.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-measure-local-double-stop-error-diagnosis.json"


def main() -> None:
    if not SCORE_PATH.is_file():
        raise FileNotFoundError(f"Missing score file: {SCORE_PATH}")

    report = json.loads(SCORE_PATH.read_text(encoding="utf-8"))
    best = report.get("bestWindow") or {}
    positives = best.get("positiveMeasureReports", [])
    negatives = best.get("negativeMeasureReports", [])

    true_positives = [item for item in positives if item.get("predictedDoubleStopEnding")]
    false_negatives = [item for item in positives if not item.get("predictedDoubleStopEnding")]
    false_positives = [item for item in negatives if item.get("predictedDoubleStopEnding")]
    true_negatives = [item for item in negatives if not item.get("predictedDoubleStopEnding")]

    diagnosis = {
        "benchmarkVersion": 1,
        "benchmarkType": "measure-local-double-stop-error-diagnosis",
        "sourceScore": str(SCORE_PATH.relative_to(REPO_ROOT)),
        "bestWindowMilliseconds": best.get("pairWindowMilliseconds"),
        "summary": {
            "truePositiveMeasures": [item["measureNumber"] for item in true_positives],
            "falseNegativeMeasures": [item["measureNumber"] for item in false_negatives],
            "falsePositiveMeasures": [item["measureNumber"] for item in false_positives],
            "trueNegativeMeasures": [item["measureNumber"] for item in true_negatives],
        },
        "truePositives": true_positives,
        "falseNegatives": false_negatives,
        "falsePositives": false_positives,
        "trueNegatives": true_negatives,
        "recommendedNextAction": (
            "derive measure-specific ending-zone alignment and distinguish repeated riff carry-over "
            "from true professional double-stop endings"
        ),
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
    }

    OUTPUT_PATH.write_text(json.dumps(diagnosis, indent=2) + "\n", encoding="utf-8")

    print("Measure-local double-stop error diagnosis")
    print(f"Best window: {best.get('pairWindowMilliseconds')} ms")
    print(
        "True-positive measures: "
        + ", ".join(str(item["measureNumber"]) for item in true_positives)
    )
    print(
        "Missed professional measures: "
        + ", ".join(str(item["measureNumber"]) for item in false_negatives)
    )
    print(
        "False-positive odd measures: "
        + ", ".join(str(item["measureNumber"]) for item in false_positives)
    )

    for item in false_negatives:
        print(
            f"MISS measure {item['measureNumber']:>2} | "
            f"MIDI58={item['midi58Count']} | MIDI62={item['midi62Count']} | "
            f"pairs={item['qualifyingPairCount']} | bestPair={item['bestPair']}"
        )

    for item in false_positives:
        print(
            f"FALSE POSITIVE measure {item['measureNumber']:>2} | "
            f"MIDI58={item['midi58Count']} | MIDI62={item['midi62Count']} | "
            f"pairs={item['qualifyingPairCount']} | bestPair={item['bestPair']}"
        )

    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
