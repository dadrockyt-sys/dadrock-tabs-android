import json
from pathlib import Path
from statistics import median, pstdev
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V44 = PUBLIC / "gomyway-v43-row-specific-calibration-outliers-v44.json"
OUTPUT = PUBLIC / "gomyway-string-line-geometry-calibration-v45.json"
PREVIEW_DIR = PUBLIC / "gomyway-string-line-geometry-calibration-v45"


def cluster_positions(values: list[tuple[float, float]], tolerance: float = 2.0) -> list[dict[str, float]]:
    if not values:
        return []
    ordered = sorted(values)
    clusters: list[list[tuple[float, float]]] = [[ordered[0]]]
    for value, weight in ordered[1:]:
        weighted_center = sum(v * w for v, w in clusters[-1]) / max(1e-9, sum(w for _, w in clusters[-1]))
        if abs(value - weighted_center) <= tolerance:
            clusters[-1].append((value, weight))
        else:
            clusters.append([(value, weight)])
    result = []
    for cluster in clusters:
        total_weight = sum(weight for _, weight in cluster)
        center = sum(value * weight for value, weight in cluster) / max(1e-9, total_weight)
        result.append({"y": center, "weight": total_weight, "members": float(len(cluster))})
    return result


def projection_peaks(edge_image, min_strength: float) -> list[tuple[float, float]]:
    import numpy as np
    profile = edge_image.mean(axis=1).astype("float32")
    if profile.size < 3:
        return []
    smoothed = np.convolve(profile, np.ones(3, dtype="float32") / 3.0, mode="same")
    peaks: list[tuple[float, float]] = []
    for y in range(1, len(smoothed) - 1):
        value = float(smoothed[y])
        if value >= min_strength and value >= float(smoothed[y - 1]) and value >= float(smoothed[y + 1]):
            peaks.append((float(y), value * 20.0))
    return peaks


def best_six_line_sequence(clusters: list[dict[str, float]], height: int) -> dict[str, Any] | None:
    if len(clusters) < 6:
        return None
    candidates: list[dict[str, Any]] = []
    ys = [float(item["y"]) for item in clusters]
    weights = [float(item["weight"]) for item in clusters]
    for start_index, top in enumerate(ys):
        for spacing_step in range(8, 37):
            spacing = spacing_step / 2.0
            if spacing < 4.0 or spacing > 18.0:
                continue
            expected = [top + spacing * index for index in range(6)]
            if expected[-1] >= height - 2:
                continue
            matched_indices: list[int] = []
            residuals: list[float] = []
            matched_weights: list[float] = []
            used: set[int] = set()
            valid = True
            for target in expected:
                options = [
                    (abs(value - target), index)
                    for index, value in enumerate(ys)
                    if index not in used and abs(value - target) <= max(2.25, spacing * 0.24)
                ]
                if not options:
                    valid = False
                    break
                residual, index = min(options)
                used.add(index)
                matched_indices.append(index)
                residuals.append(residual)
                matched_weights.append(weights[index])
            if not valid:
                continue
            actual = [ys[index] for index in matched_indices]
            gaps = [actual[index + 1] - actual[index] for index in range(5)]
            gap_std = pstdev(gaps) if len(gaps) > 1 else 0.0
            mean_residual = sum(residuals) / 6.0
            continuity = sum(matched_weights) / 6.0
            nearby_noise = sum(
                weights[index]
                for index, value in enumerate(ys)
                if index not in used and top - spacing <= value <= expected[-1] + spacing
            )
            score = continuity - mean_residual * 90.0 - gap_std * 130.0 - nearby_noise * 0.18
            candidates.append({
                "score": score,
                "rows": actual,
                "top": actual[0],
                "spacing": sum(gaps) / len(gaps),
                "gapStd": gap_std,
                "meanResidual": mean_residual,
                "continuity": continuity,
                "nearbyNoise": nearby_noise,
                "matchedClusterIndices": matched_indices,
            })
    if not candidates:
        return None
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    best["runnerUpScore"] = candidates[1]["score"] if len(candidates) > 1 else None
    best["scoreMargin"] = (
        best["score"] - candidates[1]["score"] if len(candidates) > 1 else None
    )
    return best


def main() -> None:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless numpy") from exc

    for path in (LOCALIZATION, V44):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    v44 = json.loads(V44.read_text(encoding="utf-8"))
    if int(v44.get("rowsInspected", -1)) != 8:
        raise RuntimeError("V44 did not inspect all eight locked rows")
    if int(v44.get("trustworthyRows", -1)) != 0:
        raise RuntimeError("V44 no longer reports zero trustworthy rows")

    rows = sorted(
        localization.get("rows", []),
        key=lambda row: (int(row.get("pageNumber", 0)), int(row.get("rowIndex", 0))),
    )
    if len(rows) != 8:
        raise RuntimeError(f"Expected eight localization rows, found {len(rows)}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    passed_rows = 0
    spacing_values: list[float] = []
    margin_values: list[float] = []

    print("String-line geometry calibration v45 starting", flush=True)
    for row in rows:
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        source_crop = row.get("sourceCrop")
        gray = cv2.imread(str(ROOT / str(source_crop)), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unreadable source crop: {source_crop}")
        height, width = gray.shape[:2]

        normalized = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(16, 8)).apply(gray)
        blurred = cv2.GaussianBlur(normalized, (3, 3), 0)
        edges = cv2.Canny(blurred, 45, 135)

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(35, width // 18), 1))
        horizontal = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal = cv2.dilate(horizontal, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1)), iterations=1)

        evidence: list[tuple[float, float]] = []
        lines = cv2.HoughLinesP(
            horizontal,
            1,
            np.pi / 180.0,
            threshold=max(25, width // 24),
            minLineLength=max(80, round(width * 0.18)),
            maxLineGap=max(20, round(width * 0.035)),
        )
        line_count = 0
        if lines is not None:
            for entry in lines[:, 0, :]:
                x1, y1, x2, y2 = map(int, entry)
                length = float(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
                if length <= 0:
                    continue
                slope = abs(y2 - y1) / max(1.0, abs(x2 - x1))
                if slope > 0.025:
                    continue
                evidence.append(((y1 + y2) / 2.0, length))
                line_count += 1

        projection_threshold = max(2.0, float(np.percentile(horizontal.mean(axis=1), 80)))
        evidence.extend(projection_peaks(horizontal, projection_threshold))
        clusters = cluster_positions(evidence, tolerance=2.0)
        best = best_six_line_sequence(clusters, height)

        if best is None:
            passed = False
            rows_pixels: list[float] = []
            spacing = None
            gap_std = None
            score_margin = None
            continuity = 0.0
        else:
            rows_pixels = [float(value) for value in best["rows"]]
            spacing = float(best["spacing"])
            gap_std = float(best["gapStd"])
            score_margin = best.get("scoreMargin")
            continuity = float(best["continuity"])
            passed = (
                5.0 <= spacing <= 16.0
                and gap_std <= 1.25
                and continuity >= width * 0.20
                and rows_pixels[-1] < height
            )

        if passed:
            passed_rows += 1
            spacing_values.append(float(spacing))
            if score_margin is not None:
                margin_values.append(float(score_margin))

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for cluster in clusters:
            y = round(float(cluster["y"]))
            cv2.line(preview, (0, y), (width - 1, y), (255, 0, 0), 1)
        for index, y_value in enumerate(rows_pixels):
            y = round(y_value)
            cv2.line(preview, (0, y), (width - 1, y), (0, 255, 255), 2)
            cv2.putText(preview, str(index + 1), (6, max(14, y - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1, cv2.LINE_AA)
        preview_name = f"page-{page:02d}-row-{row_index:02d}-geometry.png"
        cv2.imwrite(str(PREVIEW_DIR / preview_name), preview)

        report = {
            "pageNumber": page,
            "rowIndex": row_index,
            "sourceCrop": source_crop,
            "imageWidth": width,
            "imageHeight": height,
            "houghHorizontalSegments": line_count,
            "clusterCount": len(clusters),
            "candidateClusterYs": [round(float(item["y"]), 3) for item in clusters],
            "selectedStringRowsPixels": [round(value, 3) for value in rows_pixels],
            "selectedSpacingPixels": round(spacing, 3) if spacing is not None else None,
            "gapStandardDeviation": round(gap_std, 6) if gap_std is not None else None,
            "continuityScore": round(continuity, 3),
            "scoreMargin": round(float(score_margin), 6) if score_margin is not None else None,
            "geometryCalibrationPassed": passed,
            "preview": str((PREVIEW_DIR / preview_name).relative_to(ROOT)),
        }
        reports.append(report)
        print(
            f"Page {page} row {row_index}: segments={line_count}, clusters={len(clusters)}, "
            f"rows={report['selectedStringRowsPixels']}, spacing={report['selectedSpacingPixels']}, "
            f"gapStd={report['gapStandardDeviation']}, passed={passed}"
        )

    median_spacing = float(median(spacing_values)) if spacing_values else 0.0
    spacing_consistent_rows = sum(
        1
        for report in reports
        if report["geometryCalibrationPassed"]
        and abs(float(report["selectedSpacingPixels"]) - median_spacing) <= 2.0
    ) if spacing_values else 0
    all_rows_passed = passed_rows == 8
    spacing_consistent = spacing_consistent_rows >= 7
    calibration_passed = all_rows_passed and spacing_consistent

    output = {
        "diagnosticName": "Gomyway locked-row string-line geometry calibration v45",
        "rowsExpected": 8,
        "rowsInspected": len(reports),
        "rowsPassingGeometryCalibration": passed_rows,
        "allRowsPassedGeometryCalibration": all_rows_passed,
        "medianStringSpacingPixels": round(median_spacing, 6),
        "spacingConsistentRows": spacing_consistent_rows,
        "spacingConsistent": spacing_consistent,
        "geometryCalibrationPassed": calibration_passed,
        "rows": reports,
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-eight-v45-string-line-geometry-previews"
            if calibration_passed
            else "inspect-v45-geometry-calibration-failures-v46"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("String-line geometry calibration v45 complete")
    print(f"Rows expected: 8")
    print(f"Rows inspected: {len(reports)}")
    print(f"Rows passing geometry calibration: {passed_rows}")
    print(f"All rows passed geometry calibration: {all_rows_passed}")
    print(f"Median string spacing pixels: {median_spacing:.6f}")
    print(f"Spacing-consistent rows: {spacing_consistent_rows}")
    print(f"Spacing consistent: {spacing_consistent}")
    print(f"Geometry calibration passed: {calibration_passed}")
    print("Human visual validation complete: False")
    print("Glyph templates human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
