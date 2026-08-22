import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-open-string-x-position-model-v29.json"
OUTPUT_PATH = PUBLIC / "gomyway-open-string-x-offset-hypothesis-v30.json"
EXPECTED_MEASURES = [1, 2, 7, 8, 13, 14]


def main() -> None:
    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {INPUT_PATH.relative_to(ROOT)}")

    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if not source.get("consistentHorizontalOffsetSupported", False):
        raise RuntimeError("V29 did not support a horizontal-offset hypothesis")

    targets = list(source.get("targets", []))
    targets.sort(key=lambda item: int(item["measure"]))
    measures = [int(item["measure"]) for item in targets]
    if measures != EXPECTED_MEASURES:
        raise RuntimeError(f"Unexpected v29 target measures: {measures}")

    model_offset = float(source.get("medianSignedOffsetPixels"))
    evaluations: list[dict[str, Any]] = []
    corrected_residuals: list[float] = []
    individually_supported = 0

    print("Read-only open-string x-offset hypothesis v30 starting", flush=True)
    print(f"Global median offset: {model_offset:.2f}px", flush=True)

    for target in targets:
        measure = int(target["measure"])
        expected_x = float(target["expectedX"])
        nearest = target.get("nearestEvidence") or {}
        nearest_x_value = nearest.get("centerX")
        if nearest_x_value is None:
            evaluation = {
                "measure": measure,
                "expectedX": round(expected_x, 2),
                "nearestEvidenceX": None,
                "globalCorrectedExpectedX": round(expected_x + model_offset, 2),
                "globalCorrectedResidualPixels": None,
                "individualEvidenceOffsetPixels": None,
                "globalCorrectionSupported": False,
            }
            evaluations.append(evaluation)
            print(f"m{measure}: no evidence", flush=True)
            continue

        nearest_x = float(nearest_x_value)
        corrected_x = expected_x + model_offset
        original_residual = abs(nearest_x - expected_x)
        corrected_residual = abs(nearest_x - corrected_x)
        corrected_residuals.append(corrected_residual)
        supported = corrected_residual <= 14.0 and corrected_residual < original_residual
        if supported:
            individually_supported += 1

        evaluation = {
            "measure": measure,
            "expectedX": round(expected_x, 2),
            "nearestEvidenceX": round(nearest_x, 2),
            "originalResidualPixels": round(original_residual, 2),
            "globalOffsetPixels": round(model_offset, 2),
            "globalCorrectedExpectedX": round(corrected_x, 2),
            "globalCorrectedResidualPixels": round(corrected_residual, 2),
            "individualEvidenceOffsetPixels": round(nearest_x - expected_x, 2),
            "globalCorrectionSupported": supported,
        }
        evaluations.append(evaluation)
        print(
            f"m{measure}: originalResidual={original_residual:.2f}px, "
            f"correctedResidual={corrected_residual:.2f}px, supported={supported}",
            flush=True,
        )

    median_corrected_residual = (
        round(float(median(corrected_residuals)), 2)
        if corrected_residuals
        else None
    )
    global_offset_passed = (
        len(evaluations) == 6
        and individually_supported >= 5
        and median_corrected_residual is not None
        and median_corrected_residual <= 10.0
    )

    outliers = [
        item["measure"]
        for item in evaluations
        if not item.get("globalCorrectionSupported", False)
    ]

    output = {
        "diagnosticName": "Gomyway read-only open-string x-offset hypothesis v30",
        "referenceType": "locked-professional-open-string-x-offset-validation",
        "sourcePositionModel": str(INPUT_PATH.relative_to(ROOT)),
        "targetEventSlots": len(evaluations),
        "targetMeasures": measures,
        "globalMedianOffsetPixels": round(model_offset, 2),
        "globallySupportedEventSlots": individually_supported,
        "globalOffsetOutlierMeasures": outliers,
        "medianCorrectedResidualPixels": median_corrected_residual,
        "globalOffsetHypothesisPassed": global_offset_passed,
        "evaluations": evaluations,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-locked-glyph-template-review-pack-v31"
            if global_offset_passed
            else "fit-per-measure-open-string-technique-anchor-model-v31"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Read-only open-string x-offset hypothesis v30 complete")
    print(f"Target event slots: {len(evaluations)}")
    print(f"Global median offset pixels: {model_offset:.2f}")
    print(f"Globally supported event slots: {individually_supported}")
    print(f"Global offset outlier measures: {outliers}")
    print(f"Median corrected residual pixels: {median_corrected_residual}")
    print(f"Global offset hypothesis passed: {global_offset_passed}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
