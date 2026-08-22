import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LOCALIZATION_PATH = PUBLIC / "gomyway-rhythm-pdf-canonical-row-localization-v10.json"
VALIDATION_PATH = PUBLIC / "gomyway-rhythm-pdf-visual-validation-v12.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-professional-symbol-candidates-v13.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-professional-symbol-candidates-v13"

LOCKED_MEASURE_END = 16
TARGET_MEASURE_START = 17
TARGET_MEASURE_END = 113


def cluster(values: list[int], tolerance: int) -> list[int]:
    if not values:
        return []
    values = sorted(values)
    groups: list[list[int]] = [[values[0]]]
    for value in values[1:]:
        center = round(median(groups[-1]))
        if abs(value - center) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def choose_six_string_rows(binary: Any, np: Any) -> list[int]:
    height, width = binary.shape
    x0 = round(width * 0.06)
    x1 = round(width * 0.98)
    counts = binary[:, x0:x1].sum(axis=1)
    threshold = max(20, round((x1 - x0) * 0.42))
    rows = cluster([int(i) for i, value in enumerate(counts) if value >= threshold], 3)

    best: list[int] = []
    best_score = float("-inf")
    for index in range(max(0, len(rows) - 5)):
        group = rows[index : index + 6]
        if len(group) < 6:
            continue
        gaps = [group[i + 1] - group[i] for i in range(5)]
        spacing = float(median(gaps))
        if not 5 <= spacing <= 30:
            continue
        irregularity = max(abs(gap - spacing) for gap in gaps)
        if irregularity > max(3.0, spacing * 0.28):
            continue
        coverage = sum(int(counts[y]) for y in group)
        score = coverage - irregularity * width
        if score > best_score:
            best_score = score
            best = group
    return best


def classify_geometry(width: int, height: int, area: int, spacing: float) -> str:
    if height >= spacing * 2.2 and width <= spacing * 0.8:
        return "vertical-stem-or-barline"
    if width >= spacing * 1.8 and height <= spacing * 0.8:
        return "horizontal-articulation-or-tie"
    if height <= spacing * 1.6 and width <= spacing * 1.6:
        return "compact-glyph-candidate"
    if area >= spacing * spacing * 1.5:
        return "compound-symbol-candidate"
    return "unclassified-symbol-candidate"


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    if not LOCALIZATION_PATH.exists():
        raise RuntimeError(f"Missing v10 localization: {LOCALIZATION_PATH.relative_to(ROOT)}")
    if not VALIDATION_PATH.exists():
        raise RuntimeError(f"Missing v12 validation: {VALIDATION_PATH.relative_to(ROOT)}")

    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    if not validation.get("humanVisualValidationComplete", False):
        raise RuntimeError("V12 human visual validation has not passed")
    if not localization.get("completeLocalizationScaffoldPassed", False):
        raise RuntimeError("V10 localization scaffold has not passed")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    rows_output = []
    measures_seen: list[int] = []
    rows_attempted = 0
    rows_with_six_strings = 0
    total_candidates = 0

    print("Professional rhythm symbol candidate extraction v13 starting", flush=True)

    for page in localization["pages"]:
        page_number = int(page["pageNumber"])
        for row in page["rows"]:
            measures = [int(value) for value in row["measures"]]
            target_measures = [
                measure for measure in measures
                if TARGET_MEASURE_START <= measure <= TARGET_MEASURE_END
            ]
            if not target_measures:
                continue

            crop_path = ROOT / row["crop"]
            image = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

            rows_attempted += 1
            blur = cv2.GaussianBlur(image, (3, 3), 0)
            binary = cv2.adaptiveThreshold(
                blur,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                31,
                9,
            )
            string_rows = choose_six_string_rows(binary, np)
            candidates = []

            annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            if len(string_rows) == 6:
                rows_with_six_strings += 1
                spacing = float(median([
                    string_rows[i + 1] - string_rows[i] for i in range(5)
                ]))
                line_mask = np.zeros_like(binary)
                thickness = max(1, round(spacing * 0.18))
                for y in string_rows:
                    y0 = max(0, y - thickness)
                    y1 = min(binary.shape[0], y + thickness + 1)
                    line_mask[y0:y1, :] = binary[y0:y1, :]
                    cv2.line(annotated, (0, y), (image.shape[1] - 1, y), (255, 0, 0), 1)

                symbols = cv2.subtract(binary, line_mask)
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                symbols = cv2.morphologyEx(symbols, cv2.MORPH_CLOSE, kernel)
                count, _, stats, centroids = cv2.connectedComponentsWithStats(symbols, 8)

                min_area = max(5, round(spacing * spacing * 0.05))
                max_area = round(image.shape[0] * image.shape[1] * 0.025)
                for label in range(1, count):
                    x, y, width, height, area = [int(value) for value in stats[label]]
                    if area < min_area or area > max_area:
                        continue
                    if width >= image.shape[1] * 0.35:
                        continue
                    center_x, center_y = [float(value) for value in centroids[label]]
                    nearest_index = min(
                        range(6), key=lambda index: abs(center_y - string_rows[index])
                    )
                    distance = abs(center_y - string_rows[nearest_index])
                    assigned_string = nearest_index + 1 if distance <= spacing * 1.15 else None
                    geometry = classify_geometry(width, height, area, spacing)
                    candidate = {
                        "candidateIndex": len(candidates) + 1,
                        "boundsPixels": {"x": x, "y": y, "width": width, "height": height},
                        "centerPixels": {"x": round(center_x, 2), "y": round(center_y, 2)},
                        "areaPixels": area,
                        "nearestStringIndexHighEToLowE": assigned_string,
                        "distanceToNearestStringPixels": round(distance, 2),
                        "geometryClass": geometry,
                        "semanticValue": None,
                        "requiresRecognitionAndVerification": True,
                    }
                    candidates.append(candidate)
                    cv2.rectangle(annotated, (x, y), (x + width, y + height), (0, 0, 255), 1)

            preview_path = PREVIEW_DIR / (
                f"page-{page_number:02d}-row-{int(row['rowIndex']):02d}-"
                f"measures-{'-'.join(str(value) for value in target_measures)}.png"
            )
            cv2.imwrite(str(preview_path), annotated)

            total_candidates += len(candidates)
            measures_seen.extend(target_measures)
            rows_output.append({
                "pageNumber": page_number,
                "rowIndex": int(row["rowIndex"]),
                "measures": target_measures,
                "sourceCrop": row["crop"],
                "sixStringRowsDetected": len(string_rows) == 6,
                "stringRowsPixelsHighEToLowE": string_rows,
                "symbolCandidateCount": len(candidates),
                "symbolCandidates": candidates,
                "preview": str(preview_path.relative_to(ROOT)),
                "semanticNoteEventsExtracted": False,
            })
            print(
                f"Page {page_number} row {row['rowIndex']}: "
                f"measures {target_measures[0]}-{target_measures[-1]}, "
                f"sixStrings={len(string_rows) == 6}, candidates={len(candidates)}",
                flush=True,
            )

    unique_measures = sorted(set(measures_seen))
    expected = list(range(TARGET_MEASURE_START, TARGET_MEASURE_END + 1))
    complete_measure_coverage = unique_measures == expected
    locked_measures_touched = any(measure <= LOCKED_MEASURE_END for measure in measures_seen)

    output = {
        "diagnosticName": "Gomyway professional rhythm symbol candidate extraction v13",
        "referenceType": "professional-rhythm-tab-geometric-symbol-candidates",
        "targetMeasureStart": TARGET_MEASURE_START,
        "targetMeasureEnd": TARGET_MEASURE_END,
        "targetMeasureCount": len(expected),
        "uniqueTargetMeasuresCovered": len(unique_measures),
        "complete17To113MeasureCoveragePassed": complete_measure_coverage,
        "lockedMeasures1To16Touched": locked_measures_touched,
        "rowsAttempted": rows_attempted,
        "rowsWithSixStringsDetected": rows_with_six_strings,
        "totalGeometricSymbolCandidates": total_candidates,
        "rows": rows_output,
        "candidateAudioUsed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "semanticNoteEventsExtracted": False,
        "semanticRecognitionRequired": True,
        "manualVerificationRequiredBeforeScoring": True,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "recognize-and-verify-professional-tab-glyphs",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm symbol candidate extraction v13 complete")
    print(f"Rows attempted: {rows_attempted}")
    print(f"Rows with six strings detected: {rows_with_six_strings}")
    print(f"Unique measures 17-113 covered: {len(unique_measures)}")
    print(f"Complete 17-113 coverage passed: {complete_measure_coverage}")
    print(f"Locked measures 1-16 touched: {locked_measures_touched}")
    print(f"Geometric symbol candidates: {total_candidates}")
    print("Semantic note events extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")

    if not complete_measure_coverage:
        raise RuntimeError("V13 did not cover every target measure 17-113")
    if locked_measures_touched:
        raise RuntimeError("V13 touched protected measures 1-16")


if __name__ == "__main__":
    main()
