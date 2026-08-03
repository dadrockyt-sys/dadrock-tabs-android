from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "public" / "gomyway-percussive-rhythm-classifier-experiment.json"
OUTPUT = ROOT / "public" / "gomyway-percussive-rhythm-classifier-v2-experiment.json"

MARGIN_THRESHOLD = 0.80
MAX_POSITIVE_DISTANCE = 1.60
VALIDATION_MEASURES = {27, 42}


def main() -> None:
    data = json.loads(INPUT.read_text(encoding="utf-8"))

    revised = []
    validation_predictions = []
    for item in data["predictions"]:
        margin = float(item["negativeDistance"]) - float(item["positiveDistance"])
        predicted = (
            float(item["positiveDistance"]) <= MAX_POSITIVE_DISTANCE
            and margin >= MARGIN_THRESHOLD
        )
        revised_item = dict(item)
        revised_item["distanceMargin"] = round(margin, 6)
        revised_item["predictedPercussiveV2"] = predicted
        revised.append(revised_item)
        if int(item["measureNumber"]) in VALIDATION_MEASURES:
            validation_predictions.append(revised_item)

    predicted_validation = [
        item for item in validation_predictions if item["predictedPercussiveV2"]
    ]

    output = {
        "schemaVersion": 1,
        "title": "Gomyway conservative percussive rhythm classifier v2 experiment",
        "sourceExperiment": str(INPUT.relative_to(ROOT)),
        "marginThreshold": MARGIN_THRESHOLD,
        "maxPositiveDistance": MAX_POSITIVE_DISTANCE,
        "validationMeasures": sorted(VALIDATION_MEASURES),
        "validationPredictedPercussiveCount": len(predicted_validation),
        "validationPredictedPercussive": predicted_validation,
        "automaticPromotionAllowed": False,
        "professionalReferenceReadOnly": True,
        "protectedBaselinesChanged": False,
        "predictions": revised,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Conservative percussive rhythm classifier v2 complete")
    print("Margin threshold:", MARGIN_THRESHOLD)
    print("Max positive distance:", MAX_POSITIVE_DISTANCE)
    print("Validation predicted percussive count:", len(predicted_validation))
    print("Validation predicted percussive events:", predicted_validation)
    print("Automatic promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
