import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INSPECTION_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
OUTPUT_PATH = PUBLIC / "gomyway-unresolved-open-string-adjacent-string-audit-v28.json"
PREVIEW_DIR = PUBLIC / "gomyway-unresolved-open-string-adjacent-string-audit-v28"
EXPECTED_MEASURES = [1, 2, 7, 8, 13, 14]


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (INSPECTION_PATH, LOCALIZATION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    inspection = json.loads(INSPECTION_PATH.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))

    row_lookup = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }

    targets: list[dict[str, Any]] = []
    for measure_text, entries in inspection.get("unmatchedByMeasure", {}).items():
        for entry in entries:
            copied = dict(entry)
            copied["measure"] = int(measure_text)
            targets.append(copied)
    targets.sort(key=lambda item: int(item["measure"]))

    measures = [int(item["measure"]) for item in targets]
    if measures != EXPECTED_MEASURES:
        raise RuntimeError(f"Unexpected target measures: {measures}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    adjacent_preferred_count = 0

    print("Unresolved open-string adjacent-string audit v28 starting", flush=True)

    for target in targets:
        page = int(target["pageNumber"])
        row_index = int(target["rowIndex"])
        measure = int(target["measure"])
        expected_x = float(target.get("expectedX") or 0)
        row = row_lookup.get((page, row_index))
        if row is None:
            raise RuntimeError(f"Missing localization row for page {page} row {row_index}")

        crop_path = ROOT / row["sourceCrop"]
        image = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

        string_rows = [int(value) for value in row["stringRowsPixelsHighEToLowE"]]
        if len(string_rows) != 6:
            raise RuntimeError(f"Expected six string rows for page {page} row {row_index}")
        spacing = sum(string_rows[i + 1] - string_rows[i] for i in range(5)) / 5.0
        half_width = max(28, round(spacing * 3.5))
        x0 = max(0, round(expected_x) - half_width)
        x1 = min(image.shape[1], round(expected_x) + half_width + 1)
        y0 = max(0, string_rows[4] - round(spacing * 2.0))
        y1 = min(image.shape[0], string_rows[5] + round(spacing * 2.0) + 1)
        patch = image[y0:y1, x0:x1]

        blur = cv2.GaussianBlur(patch, (3, 3), 0)
        binary = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 7,
        )

        scores = {}
        for string_number in (5, 6):
            string_y = string_rows[string_number - 1] - y0
            band_half = max(3, round(spacing * 0.55))
            band_y0 = max(0, string_y - band_half)
            band_y1 = min(binary.shape[0], string_y + band_half + 1)
            band = binary[band_y0:band_y1, :]
            scores[str(string_number)] = {
                "foregroundPixels": int(band.sum() // 255),
                "stringYPixel": int(string_rows[string_number - 1]),
            }

        preferred = 5 if scores["5"]["foregroundPixels"] > scores["6"]["foregroundPixels"] else 6
        if preferred == 5:
            adjacent_preferred_count += 1

        annotated = cv2.cvtColor(patch, cv2.COLOR_GRAY2BGR)
        local_x = round(expected_x) - x0
        cv2.line(annotated, (local_x, 0), (local_x, annotated.shape[0] - 1), (0, 0, 255), 1)
        for string_number, color in ((5, (0, 255, 255)), (6, (255, 0, 0))):
            local_y = string_rows[string_number - 1] - y0
            cv2.line(annotated, (0, local_y), (annotated.shape[1] - 1, local_y), color, 1)
        enlarged = cv2.resize(annotated, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        preview_path = PREVIEW_DIR / f"m{measure:03d}-string5-vs-string6.png"
        cv2.imwrite(str(preview_path), enlarged)

        result = {
            "pageNumber": page,
            "rowIndex": row_index,
            "measure": measure,
            "expectedX": round(expected_x, 2),
            "string5ForegroundPixels": scores["5"]["foregroundPixels"],
            "string6ForegroundPixels": scores["6"]["foregroundPixels"],
            "preferredStringByRawForeground": preferred,
            "preview": str(preview_path.relative_to(ROOT)),
            "humanVerificationRequired": True,
        }
        results.append(result)
        print(
            f"m{measure}: string5={result['string5ForegroundPixels']}, "
            f"string6={result['string6ForegroundPixels']}, preferred={preferred}",
            flush=True,
        )

    adjacent_string_hypothesis_supported = adjacent_preferred_count >= 5
    all_previews_built = len(results) == 6 and all((ROOT / item["preview"]).exists() for item in results)

    output = {
        "diagnosticName": "Gomyway unresolved open-string adjacent-string audit v28",
        "referenceType": "locked-professional-adjacent-string-localization-diagnostic",
        "targetEventSlots": len(results),
        "targetMeasures": measures,
        "adjacentStringPreferredCount": adjacent_preferred_count,
        "adjacentStringHypothesisSupported": adjacent_string_hypothesis_supported,
        "allSixAdjacentStringPreviewsBuilt": all_previews_built,
        "targets": results,
        "humanValidationRequired": True,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "correct-localization-string-index-without-changing-locked-events-v29"
            if adjacent_string_hypothesis_supported
            else "inspect-open-string-x-position-model-v29"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Unresolved open-string adjacent-string audit v28 complete")
    print(f"Target event slots: {len(results)}")
    print(f"Adjacent string preferred count: {adjacent_preferred_count}")
    print(f"Adjacent string hypothesis supported: {adjacent_string_hypothesis_supported}")
    print(f"All six adjacent-string previews built: {all_previews_built}")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
