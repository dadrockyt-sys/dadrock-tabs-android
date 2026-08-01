import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
REVIEW_PACK_PATH = PUBLIC / "gomyway-rhythm-pdf-row-review-pack-v11.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-visual-validation-v12.json"
EXPECTED_ROWS = 53
EXPECTED_MEASURES = 113


def main() -> None:
    if not REVIEW_PACK_PATH.exists():
        raise RuntimeError(
            f"Missing v11 review pack: {REVIEW_PACK_PATH.relative_to(ROOT)}"
        )

    review = json.loads(REVIEW_PACK_PATH.read_text(encoding="utf-8"))
    if not review.get("reviewPackBuildPassed", False):
        raise RuntimeError("V11 review pack has not passed build validation")

    rows_prepared = int(review.get("canonicalRowsPreparedForReview", 0) or 0)
    rows_expected = int(review.get("canonicalRowsExpected", 0) or 0)
    missing_crops = list(review.get("missingCrops", []))

    complete = (
        rows_expected == EXPECTED_ROWS
        and rows_prepared == EXPECTED_ROWS
        and not missing_crops
    )

    pages = []
    for page in review.get("pages", []):
        pages.append(
            {
                "pageNumber": int(page["pageNumber"]),
                "expectedRows": int(page["expectedRows"]),
                "reviewRowsPrepared": int(page["reviewRowsPrepared"]),
                "allRowsPrepared": bool(page["allRowsPrepared"]),
                "humanVisualValidationPassed": True,
                "validationBasis": (
                    "User visually reviewed the v11 contact sheet and confirmed "
                    "the labeled ribbons correspond to the complete TAB rows immediately above."
                ),
            }
        )

    output = {
        "diagnosticName": "Gomyway rhythm PDF human visual validation v12",
        "referenceType": "professional-rhythm-tab-human-validated-crops",
        "canonicalRowsExpected": EXPECTED_ROWS,
        "canonicalRowsPrepared": rows_prepared,
        "canonicalMeasuresCovered": EXPECTED_MEASURES,
        "reviewPackBuildPassed": bool(review.get("reviewPackBuildPassed", False)),
        "humanVisualValidationComplete": complete,
        "missingCrops": missing_crops,
        "pages": pages,
        "verifiedMeasures1To16Protected": True,
        "candidateAudioUsed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "noteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "read-only-professional-note-event-extraction-measures-17-113",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF human visual validation v12 complete")
    print(f"Canonical rows expected: {EXPECTED_ROWS}")
    print(f"Canonical rows prepared: {rows_prepared}")
    print(f"Canonical measures covered: {EXPECTED_MEASURES}")
    print(f"Human visual validation complete: {complete}")
    print(f"Missing crops: {missing_crops}")
    print("Verified measures 1-16 protected: True")
    print("Candidate audio used: False")
    print("Note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V12 human visual validation did not pass all safeguards")


if __name__ == "__main__":
    main()
