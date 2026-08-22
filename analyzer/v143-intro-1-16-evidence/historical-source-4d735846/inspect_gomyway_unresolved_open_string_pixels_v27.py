import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INSPECTION_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
RECOVERY_PATH = PUBLIC / "gomyway-open-string-technique-glyph-recovery-v26.json"
OUTPUT_PATH = PUBLIC / "gomyway-unresolved-open-string-pixel-inspection-v27.json"
PREVIEW_DIR = PUBLIC / "gomyway-unresolved-open-string-pixel-inspection-v27"

EXPECTED_MEASURES = [1, 2, 7, 8, 13, 14]


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    for path in (INSPECTION_PATH, LOCALIZATION_PATH, RECOVERY_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    inspection = json.loads(INSPECTION_PATH.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    recovery = json.loads(RECOVERY_PATH.read_text(encoding="utf-8"))

    if int(inspection.get("unmatchedEventSlots", -1)) != 6:
        raise RuntimeError("V25 did not isolate six unmatched slots")
    if int(recovery.get("unresolvedEventSlots", -1)) != 6:
        raise RuntimeError("V26 did not leave exactly six unresolved slots")

    row_lookup = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }

    targets: list[dict[str, Any]] = []
    for measure_text, entries in inspection.get("unmatchedByMeasure", {}).items():
        for entry in entries:
            target = dict(entry)
            target["measure"] = int(measure_text)
            targets.append(target)

    targets.sort(key=lambda item: int(item["measure"]))
    measures = [int(item["measure"]) for item in targets]
    if measures != EXPECTED_MEASURES:
        raise RuntimeError(f"Unexpected v25 target measures: {measures}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    print("Unresolved open-string raw pixel inspection v27 starting", flush=True)

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
        string_y = string_rows[5]
        spacing = sum(string_rows[i + 1] - string_rows[i] for i in range(5)) / 5.0

        half_width = max(36, round(spacing * 4.5))
        half_height = max(22, round(spacing * 2.6))
        x0 = max(0, round(expected_x) - half_width)
        x1 = min(image.shape[1], round(expected_x) + half_width + 1)
        y0 = max(0, string_y - half_height)
        y1 = min(image.shape[0], string_y + half_height + 1)
        patch = image[y0:y1, x0:x1]

        blur = cv2.GaussianBlur(patch, (3, 3), 0)
        binary = cv2.adaptiveThreshold(
            blur,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            7,
        )

        local_string_y = string_y - y0
        suppressed = binary.copy()
        thickness = max(1, round(spacing * 0.22))
        suppressed[
            max(0, local_string_y - thickness):
            min(suppressed.shape[0], local_string_y + thickness + 1),
            :,
        ] = 0
        suppressed = cv2.morphologyEx(
            suppressed,
            cv2.MORPH_CLOSE,
            cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)),
        )

        count, _, stats, centroids = cv2.connectedComponentsWithStats(suppressed, 8)
        components = []
        for label in range(1, count):
            x, y, width, height, area = [int(value) for value in stats[label]]
            if area < 3:
                continue
            cx, cy = [float(value) for value in centroids[label]]
            components.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "area": area,
                "centerX": round(cx, 2),
                "centerY": round(cy, 2),
                "distanceFromExpectedX": round(abs((x0 + cx) - expected_x), 2),
                "distanceFromStringY": round(abs((y0 + cy) - string_y), 2),
            })

        components.sort(
            key=lambda item: (
                item["distanceFromExpectedX"] + item["distanceFromStringY"],
                -item["area"],
            )
        )

        annotated = cv2.cvtColor(patch, cv2.COLOR_GRAY2BGR)
        expected_local_x = round(expected_x) - x0
        cv2.line(annotated, (expected_local_x, 0), (expected_local_x, annotated.shape[0] - 1), (0, 0, 255), 1)
        cv2.line(annotated, (0, local_string_y), (annotated.shape[1] - 1, local_string_y), (255, 0, 0), 1)
        for component in components[:12]:
            x = int(component["x"])
            y = int(component["y"])
            width = int(component["width"])
            height = int(component["height"])
            cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 255, 0), 1)

        enlarged = cv2.resize(annotated, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        preview_path = PREVIEW_DIR / f"m{measure:03d}-raw-open-string-window.png"
        cv2.imwrite(str(preview_path), enlarged)

        near_components = [
            item for item in components
            if item["distanceFromExpectedX"] <= max(18.0, spacing * 1.8)
            and item["distanceFromStringY"] <= max(14.0, spacing * 1.4)
        ]
        result = {
            "pageNumber": page,
            "rowIndex": row_index,
            "measure": measure,
            "stringHighEToLowE": 6,
            "fret": 0,
            "expectedX": round(expected_x, 2),
            "stringYPixel": string_y,
            "stringSpacingPixels": round(spacing, 2),
            "windowPixels": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
            "rawForegroundPixels": int(binary.sum() // 255),
            "foregroundPixelsAfterStringSuppression": int(suppressed.sum() // 255),
            "localComponents": components[:40],
            "nearExpectedPositionComponents": near_components,
            "nearExpectedPositionComponentCount": len(near_components),
            "preview": str(preview_path.relative_to(ROOT)),
            "humanVerificationRequired": True,
        }
        results.append(result)
        print(
            f"m{measure}: rawPixels={result['rawForegroundPixels']}, "
            f"components={len(components)}, nearExpected={len(near_components)}",
            flush=True,
        )

    all_previews_built = len(results) == 6 and all((ROOT / item["preview"]).exists() for item in results)
    output = {
        "diagnosticName": "Gomyway unresolved open-string raw pixel inspection v27",
        "referenceType": "locked-professional-raw-pixel-open-string-diagnostic",
        "sourceInspection": str(INSPECTION_PATH.relative_to(ROOT)),
        "sourceLocalization": str(LOCALIZATION_PATH.relative_to(ROOT)),
        "sourceRecovery": str(RECOVERY_PATH.relative_to(ROOT)),
        "targetEventSlots": len(results),
        "targetMeasures": measures,
        "allSixRawPixelPreviewsBuilt": all_previews_built,
        "targets": results,
        "humanValidationRequired": True,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-six-v27-raw-pixel-windows",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Unresolved open-string raw pixel inspection v27 complete")
    print(f"Target event slots: {len(results)}")
    print(f"Target measures: {measures}")
    print(f"All six raw pixel previews built: {all_previews_built}")
    print("Human validation required: True")
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
