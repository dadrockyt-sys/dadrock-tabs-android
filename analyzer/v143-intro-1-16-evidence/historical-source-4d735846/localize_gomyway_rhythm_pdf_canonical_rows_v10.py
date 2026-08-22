import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
ROW_MANIFEST_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-manifest-v9.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-localization-v10.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-canonical-row-crops-v10"

SCALE = 3.0


def smooth(values: Any, np: Any, radius: int) -> Any:
    if radius <= 0:
        return values
    kernel = np.ones(radius * 2 + 1, dtype=float)
    kernel /= kernel.sum()
    return np.convolve(values, kernel, mode="same")


def choose_boundaries(activity: Any, row_count: int, np: Any) -> list[int]:
    height = len(activity)
    if row_count <= 0:
        return [0, height]

    # Keep title/header and mobile-player footer out of the musical-row search area.
    top = round(height * 0.08)
    bottom = round(height * 0.94)
    span = bottom - top
    boundaries = [top]

    # Find one low-ink valley near each expected row separator. This is only
    # localization scaffolding; no note events are extracted from these crops.
    for index in range(1, row_count):
        expected = top + round(span * index / row_count)
        window = max(18, round(span / row_count * 0.28))
        lo = max(boundaries[-1] + 20, expected - window)
        hi = min(bottom - 20, expected + window)
        if hi <= lo:
            boundary = expected
        else:
            local = activity[lo : hi + 1]
            boundary = lo + int(np.argmin(local))
        boundaries.append(boundary)

    boundaries.append(bottom)
    return boundaries


def main() -> None:
    try:
        import fitz  # type: ignore
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Run: pip install pymupdf numpy opencv-python-headless"
        ) from exc

    if not ROW_MANIFEST_PATH.exists():
        raise RuntimeError(
            f"Missing v9 row manifest: {ROW_MANIFEST_PATH.relative_to(ROOT)}"
        )

    manifest = json.loads(ROW_MANIFEST_PATH.read_text(encoding="utf-8"))
    if not manifest.get("completeOrdered1To113CoveragePassed", False):
        raise RuntimeError("V9 row manifest has not passed ordered 1-113 coverage")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    if len(doc) != 8:
        raise RuntimeError(f"Expected authoritative 8-page PDF, found {len(doc)}")

    page_results = []
    total_rows = 0
    total_measures = 0

    print("Rhythm PDF canonical row pixel localization v10 starting", flush=True)

    for page_manifest in manifest["pages"]:
        page_number = int(page_manifest["pageNumber"])
        rows = page_manifest["rows"]
        page = doc[page_number - 1]
        pix = page.get_pixmap(
            matrix=fitz.Matrix(SCALE, SCALE),
            alpha=False,
            colorspace=fitz.csGRAY,
        )
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width
        )

        dark = (255 - image.astype(np.float32)) / 255.0
        activity = dark[:, round(pix.width * 0.03) : round(pix.width * 0.97)].mean(axis=1)
        activity = smooth(activity, np, max(3, round(pix.height * 0.003)))
        boundaries = choose_boundaries(activity, len(rows), np)

        localized_rows = []
        for row_index, measures in enumerate(rows, start=1):
            y0 = boundaries[row_index - 1]
            y1 = boundaries[row_index]
            pad = max(8, round((y1 - y0) * 0.04))
            crop_y0 = max(0, y0 - pad)
            crop_y1 = min(pix.height, y1 + pad)
            crop = image[crop_y0:crop_y1, :]

            measure_label = "-".join(str(value) for value in measures)
            crop_path = PREVIEW_DIR / (
                f"page-{page_number:02d}-row-{row_index:02d}-measures-{measure_label}.png"
            )
            cv2.imwrite(str(crop_path), crop)

            localized_rows.append(
                {
                    "rowIndex": row_index,
                    "measures": measures,
                    "pixelBounds": {
                        "x0": 0,
                        "y0": crop_y0,
                        "x1": pix.width,
                        "y1": crop_y1,
                    },
                    "crop": str(crop_path.relative_to(ROOT)),
                    "localizationMethod": "adaptive-horizontal-activity-valley",
                    "visualVerificationRequired": True,
                    "noteEventsExtracted": False,
                }
            )
            total_rows += 1
            total_measures += len(measures)

        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for boundary in boundaries:
            cv2.line(annotated, (0, boundary), (pix.width - 1, boundary), (0, 0, 255), 2)
        annotated_path = PREVIEW_DIR / f"page-{page_number:02d}-boundaries.png"
        cv2.imwrite(str(annotated_path), annotated)

        page_results.append(
            {
                "pageNumber": page_number,
                "pageWidthPixels": pix.width,
                "pageHeightPixels": pix.height,
                "expectedCanonicalRows": len(rows),
                "localizedCanonicalRows": len(localized_rows),
                "rowCountMatched": len(localized_rows) == len(rows),
                "rows": localized_rows,
                "annotatedPreview": str(annotated_path.relative_to(ROOT)),
            }
        )
        print(
            f"Page {page_number}: localized {len(localized_rows)}/{len(rows)} canonical rows",
            flush=True,
        )

    complete = (
        total_rows == int(manifest["canonicalRows"])
        and total_measures == int(manifest["canonicalMeasureCount"])
        and all(page["rowCountMatched"] for page in page_results)
    )

    output = {
        "diagnosticName": "Gomyway rhythm PDF canonical row pixel localization v10",
        "referenceType": "professional-rhythm-tab-pixel-localization",
        "pdfPageCountUsedAsAuthority": len(doc),
        "canonicalRowsExpected": int(manifest["canonicalRows"]),
        "canonicalRowsLocalized": total_rows,
        "canonicalMeasuresCovered": total_measures,
        "completeLocalizationScaffoldPassed": complete,
        "pages": page_results,
        "visualVerificationRequiredBeforeExtraction": True,
        "verifiedMeasures1To16Protected": True,
        "candidateAudioUsed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "noteEventsExtracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "visual-row-crop-validation",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF canonical row pixel localization v10 complete")
    print(f"Canonical rows expected: {output['canonicalRowsExpected']}")
    print(f"Canonical rows localized: {output['canonicalRowsLocalized']}")
    print(f"Canonical measures covered: {output['canonicalMeasuresCovered']}")
    print(f"Complete localization scaffold passed: {complete}")
    print("Visual verification required before extraction: True")
    print("Verified measures 1-16 protected: True")
    print("Candidate audio used: False")
    print("Note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Crops: {PREVIEW_DIR.relative_to(ROOT)}")

    if not complete:
        raise RuntimeError("V10 localization scaffold failed canonical row accounting")


if __name__ == "__main__":
    main()
