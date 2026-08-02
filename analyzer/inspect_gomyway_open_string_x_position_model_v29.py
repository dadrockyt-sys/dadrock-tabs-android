import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PIXEL_PATH = PUBLIC / "gomyway-unresolved-open-string-pixel-inspection-v27.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
OUTPUT_PATH = PUBLIC / "gomyway-open-string-x-position-model-v29.json"
PREVIEW_DIR = PUBLIC / "gomyway-open-string-x-position-model-v29"
EXPECTED_MEASURES = [1, 2, 7, 8, 13, 14]


def contiguous_runs(indices: list[int]) -> list[tuple[int, int]]:
    if not indices:
        return []
    runs: list[tuple[int, int]] = []
    start = previous = indices[0]
    for value in indices[1:]:
        if value == previous + 1:
            previous = value
            continue
        runs.append((start, previous))
        start = previous = value
    runs.append((start, previous))
    return runs


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    for path in (PIXEL_PATH, LOCALIZATION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    pixel_data = json.loads(PIXEL_PATH.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    targets = list(pixel_data.get("targets", []))
    targets.sort(key=lambda item: int(item["measure"]))
    measures = [int(item["measure"]) for item in targets]
    if measures != EXPECTED_MEASURES:
        raise RuntimeError(f"Unexpected v27 measures: {measures}")

    row_lookup = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    offsets: list[float] = []
    print("Open-string horizontal position model inspection v29 starting", flush=True)

    for target in targets:
        page = int(target["pageNumber"])
        row_index = int(target["rowIndex"])
        measure = int(target["measure"])
        expected_x = float(target["expectedX"])
        row = row_lookup.get((page, row_index))
        if row is None:
            raise RuntimeError(f"Missing localization row for page {page} row {row_index}")

        crop_path = ROOT / row["sourceCrop"]
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

        string_rows = [int(value) for value in row["stringRowsPixelsHighEToLowE"]]
        if len(string_rows) != 6:
            raise RuntimeError(f"Expected six strings for page {page} row {row_index}")
        string_y = string_rows[5]
        spacing = sum(string_rows[i + 1] - string_rows[i] for i in range(5)) / 5.0

        half_width = max(90, round(spacing * 12.0))
        x0 = max(0, round(expected_x) - half_width)
        x1 = min(gray.shape[1], round(expected_x) + half_width + 1)
        y0 = max(0, round(string_y - spacing * 1.3))
        y1 = min(gray.shape[0], round(string_y + spacing * 1.3) + 1)
        patch = gray[y0:y1, x0:x1]

        binary = cv2.adaptiveThreshold(
            cv2.GaussianBlur(patch, (3, 3), 0),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            21,
            7,
        )
        local_string_y = string_y - y0
        suppression = max(1, round(spacing * 0.18))
        binary[
            max(0, local_string_y - suppression):
            min(binary.shape[0], local_string_y + suppression + 1),
            :,
        ] = 0

        vertical_radius = max(3, round(spacing * 0.8))
        band_y0 = max(0, local_string_y - vertical_radius)
        band_y1 = min(binary.shape[0], local_string_y + vertical_radius + 1)
        band = binary[band_y0:band_y1, :]
        projection = (band > 0).sum(axis=0).astype(int)
        threshold = max(2, round(band.shape[0] * 0.14))
        active_columns = [int(index) for index, value in enumerate(projection) if value >= threshold]
        runs = contiguous_runs(active_columns)

        candidates = []
        for run_start, run_end in runs:
            run_width = run_end - run_start + 1
            run_pixels = int(projection[run_start:run_end + 1].sum())
            center_local = (run_start + run_end) / 2.0
            center_global = x0 + center_local
            distance = abs(center_global - expected_x)
            if run_width < 2 or run_pixels < 4:
                continue
            candidates.append({
                "xStart": x0 + run_start,
                "xEnd": x0 + run_end,
                "centerX": round(center_global, 2),
                "width": run_width,
                "foregroundPixels": run_pixels,
                "distanceFromExpectedX": round(distance, 2),
                "signedOffsetPixels": round(center_global - expected_x, 2),
            })

        candidates.sort(key=lambda item: (item["distanceFromExpectedX"], -item["foregroundPixels"]))
        nearest = candidates[0] if candidates else None
        if nearest is not None:
            offsets.append(float(nearest["signedOffsetPixels"]))

        annotated = cv2.cvtColor(patch, cv2.COLOR_GRAY2BGR)
        expected_local = round(expected_x) - x0
        cv2.line(annotated, (expected_local, 0), (expected_local, annotated.shape[0] - 1), (0, 0, 255), 1)
        cv2.line(annotated, (0, local_string_y), (annotated.shape[1] - 1, local_string_y), (255, 0, 0), 1)
        for candidate in candidates[:8]:
            left = int(candidate["xStart"] - x0)
            right = int(candidate["xEnd"] - x0)
            cv2.rectangle(annotated, (left, band_y0), (right, max(band_y0, band_y1 - 1)), (0, 255, 0), 1)
        if nearest is not None:
            nearest_local = round(float(nearest["centerX"])) - x0
            cv2.line(annotated, (nearest_local, 0), (nearest_local, annotated.shape[0] - 1), (0, 255, 255), 1)

        enlarged = cv2.resize(annotated, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST)
        preview_path = PREVIEW_DIR / f"m{measure:03d}-x-position-audit.png"
        cv2.imwrite(str(preview_path), enlarged)

        result = {
            "pageNumber": page,
            "rowIndex": row_index,
            "measure": measure,
            "expectedX": round(expected_x, 2),
            "string6YPixel": string_y,
            "stringSpacingPixels": round(spacing, 2),
            "candidateRuns": candidates[:20],
            "nearestEvidence": nearest,
            "preview": str(preview_path.relative_to(ROOT)),
        }
        results.append(result)
        print(
            f"m{measure}: expectedX={expected_x:.2f}, "
            f"nearestX={nearest['centerX'] if nearest else None}, "
            f"offset={nearest['signedOffsetPixels'] if nearest else None}",
            flush=True,
        )

    nonzero_offsets = [value for value in offsets if abs(value) >= 1.0]
    median_offset = round(float(median(nonzero_offsets)), 2) if nonzero_offsets else None
    same_direction = False
    if nonzero_offsets:
        positive = sum(1 for value in nonzero_offsets if value > 0)
        negative = sum(1 for value in nonzero_offsets if value < 0)
        same_direction = max(positive, negative) >= 5
    consistent_offset_supported = (
        len(nonzero_offsets) >= 5
        and same_direction
        and median_offset is not None
        and abs(median_offset) >= 8.0
    )
    previews_built = len(results) == 6 and all((ROOT / item["preview"]).exists() for item in results)

    output = {
        "diagnosticName": "Gomyway open-string horizontal position model inspection v29",
        "referenceType": "locked-professional-open-string-x-position-diagnostic",
        "sourcePixelInspection": str(PIXEL_PATH.relative_to(ROOT)),
        "sourceLocalization": str(LOCALIZATION_PATH.relative_to(ROOT)),
        "targetEventSlots": len(results),
        "targetMeasures": measures,
        "nearestEvidenceFoundCount": sum(1 for item in results if item["nearestEvidence"] is not None),
        "signedOffsetsPixels": offsets,
        "medianSignedOffsetPixels": median_offset,
        "consistentOffsetDirection": same_direction,
        "consistentHorizontalOffsetSupported": consistent_offset_supported,
        "allSixXPositionPreviewsBuilt": previews_built,
        "targets": results,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "apply-read-only-open-string-x-offset-hypothesis-v30"
            if consistent_offset_supported
            else "inspect-per-measure-technique-anchor-model-v30"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Open-string horizontal position model inspection v29 complete")
    print(f"Target event slots: {len(results)}")
    print(f"Nearest evidence found count: {output['nearestEvidenceFoundCount']}")
    print(f"Median signed offset pixels: {median_offset}")
    print(f"Consistent offset direction: {same_direction}")
    print(f"Consistent horizontal offset supported: {consistent_offset_supported}")
    print(f"All six x-position previews built: {previews_built}")
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
