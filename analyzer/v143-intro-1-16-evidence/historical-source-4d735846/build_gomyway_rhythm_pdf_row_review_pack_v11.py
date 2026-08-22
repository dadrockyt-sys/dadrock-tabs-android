import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LOCALIZATION_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-localization-v10.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-row-review-pack-v11.json"
REVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-row-review-pack-v11"


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    if not LOCALIZATION_PATH.exists():
        raise RuntimeError(
            f"Missing v10 localization: {LOCALIZATION_PATH.relative_to(ROOT)}"
        )

    data = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    if not data.get("completeLocalizationScaffoldPassed", False):
        raise RuntimeError("V10 localization scaffold has not passed")

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    page_results = []
    reviewed_rows = 0
    missing_crops = []

    print("Rhythm PDF canonical row visual review pack v11 starting", flush=True)

    for page in data["pages"]:
        page_number = int(page["pageNumber"])
        panels = []
        row_results = []

        for row in page["rows"]:
            crop_path = ROOT / row["crop"]
            if not crop_path.exists():
                missing_crops.append(str(crop_path.relative_to(ROOT)))
                continue

            image = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                missing_crops.append(str(crop_path.relative_to(ROOT)))
                continue

            target_width = 1320
            scale = target_width / image.shape[1]
            resized = cv2.resize(
                image,
                (target_width, max(1, round(image.shape[0] * scale))),
                interpolation=cv2.INTER_AREA,
            )
            panel = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
            label_height = 54
            labelled = np.full(
                (panel.shape[0] + label_height, panel.shape[1], 3),
                255,
                dtype=np.uint8,
            )
            labelled[label_height:, :] = panel
            measures = ", ".join(str(value) for value in row["measures"])
            label = f"Page {page_number} row {row['rowIndex']} | measures {measures}"
            cv2.putText(
                labelled,
                label,
                (18, 36),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (0, 0, 0),
                2,
                cv2.LINE_AA,
            )
            panels.append(labelled)
            reviewed_rows += 1
            row_results.append(
                {
                    "rowIndex": row["rowIndex"],
                    "measures": row["measures"],
                    "crop": row["crop"],
                    "visualStatus": "pending-human-validation",
                    "mustContainCompleteTabStaff": True,
                    "mustContainPrintedMeasureNumbers": True,
                    "noteEventsExtracted": False,
                }
            )

        if panels:
            gap = 18
            height = sum(panel.shape[0] for panel in panels) + gap * (len(panels) - 1)
            sheet = np.full((height, 1320, 3), 245, dtype=np.uint8)
            y = 0
            for panel in panels:
                sheet[y : y + panel.shape[0], :] = panel
                y += panel.shape[0] + gap
            sheet_path = REVIEW_DIR / f"page-{page_number:02d}-row-contact-sheet.png"
            cv2.imwrite(str(sheet_path), sheet)
            sheet_rel = str(sheet_path.relative_to(ROOT))
        else:
            sheet_rel = None

        page_results.append(
            {
                "pageNumber": page_number,
                "expectedRows": page["expectedCanonicalRows"],
                "reviewRowsPrepared": len(row_results),
                "allRowsPrepared": len(row_results) == page["expectedCanonicalRows"],
                "contactSheet": sheet_rel,
                "rows": row_results,
            }
        )
        print(
            f"Page {page_number}: prepared {len(row_results)}/{page['expectedCanonicalRows']} rows",
            flush=True,
        )

    complete = (
        reviewed_rows == int(data["canonicalRowsLocalized"])
        and not missing_crops
        and all(page["allRowsPrepared"] for page in page_results)
    )

    output = {
        "diagnosticName": "Gomyway rhythm PDF canonical row visual review pack v11",
        "referenceType": "professional-rhythm-tab-visual-validation-pack",
        "canonicalRowsExpected": int(data["canonicalRowsLocalized"]),
        "canonicalRowsPreparedForReview": reviewed_rows,
        "reviewPackBuildPassed": complete,
        "missingCrops": missing_crops,
        "pages": page_results,
        "visualValidationComplete": False,
        "verifiedMeasures1To16Protected": True,
        "candidateAudioUsed": False,
        "noteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-of-v11-contact-sheets",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF canonical row visual review pack v11 complete")
    print(f"Canonical rows expected: {output['canonicalRowsExpected']}")
    print(f"Canonical rows prepared: {reviewed_rows}")
    print(f"Review pack build passed: {complete}")
    print(f"Missing crops: {missing_crops}")
    print("Visual validation complete: False")
    print("Verified measures 1-16 protected: True")
    print("Candidate audio used: False")
    print("Note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Contact sheets: {REVIEW_DIR.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V11 review pack build failed")


if __name__ == "__main__":
    main()
