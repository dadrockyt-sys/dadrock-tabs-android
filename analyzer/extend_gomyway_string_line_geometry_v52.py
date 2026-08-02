"""Extend the proven v45 TAB string-line detector through measures 17-113.

This intentionally reuses the same evidence model that succeeded for locked
measures 1-16: CLAHE normalization, Canny edges, horizontal morphology, Hough
segments, projection peaks, weighted y clustering, and six-line sequence
selection. The approved v46 spacing is used only as a validation constraint.

This stage is read-only. It performs no fret recognition, uses no candidate
audio, and never modifies locked measures 1-16.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median, pstdev
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SCAFFOLD = PUBLIC / "gomyway-approved-string-geometry-extraction-scaffold-v48.json"
CONSENSUS = PUBLIC / "gomyway-string-line-geometry-consensus-v46.json"
OUTPUT = PUBLIC / "gomyway-full-song-string-line-geometry-v52.json"
PREVIEW_DIR = PUBLIC / "gomyway-full-song-string-line-geometry-v52"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def cluster_positions(
    values: list[tuple[float, float]], tolerance: float = 2.0
) -> list[dict[str, float]]:
    if not values:
        return []
    ordered = sorted(values)
    clusters: list[list[tuple[float, float]]] = [[ordered[0]]]
    for value, weight in ordered[1:]:
        weighted_center = sum(v * w for v, w in clusters[-1]) / max(
            1e-9, sum(w for _, w in clusters[-1])
        )
        if abs(value - weighted_center) <= tolerance:
            clusters[-1].append((value, weight))
        else:
            clusters.append([(value, weight)])

    result: list[dict[str, float]] = []
    for cluster in clusters:
        total_weight = sum(weight for _, weight in cluster)
        center = sum(value * weight for value, weight in cluster) / max(
            1e-9, total_weight
        )
        result.append(
            {
                "y": center,
                "weight": total_weight,
                "members": float(len(cluster)),
            }
        )
    return result


def projection_peaks(edge_image: Any, min_strength: float) -> list[tuple[float, float]]:
    import numpy as np

    profile = edge_image.mean(axis=1).astype("float32")
    if profile.size < 3:
        return []
    smoothed = np.convolve(
        profile,
        np.ones(3, dtype="float32") / 3.0,
        mode="same",
    )
    peaks: list[tuple[float, float]] = []
    for y in range(1, len(smoothed) - 1):
        value = float(smoothed[y])
        if (
            value >= min_strength
            and value >= float(smoothed[y - 1])
            and value >= float(smoothed[y + 1])
        ):
            peaks.append((float(y), value * 20.0))
    return peaks


def best_six_line_sequence(
    clusters: list[dict[str, float]],
    height: int,
    locked_spacing: float,
) -> dict[str, Any] | None:
    if len(clusters) < 6:
        return None

    candidates: list[dict[str, Any]] = []
    ys = [float(item["y"]) for item in clusters]
    weights = [float(item["weight"]) for item in clusters]

    # Keep the original v45 search range. Locked spacing is not used to invent
    # line positions; it only contributes a mild validation penalty.
    for top in ys:
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
                    if index not in used
                    and abs(value - target) <= max(2.25, spacing * 0.24)
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
                if index not in used
                and top - spacing <= value <= expected[-1] + spacing
            )
            spacing_delta = abs((sum(gaps) / len(gaps)) - locked_spacing)

            score = (
                continuity
                - mean_residual * 90.0
                - gap_std * 130.0
                - nearby_noise * 0.18
                - spacing_delta * 18.0
            )
            candidates.append(
                {
                    "score": score,
                    "rows": actual,
                    "spacing": sum(gaps) / len(gaps),
                    "gapStd": gap_std,
                    "meanResidual": mean_residual,
                    "continuity": continuity,
                    "nearbyNoise": nearby_noise,
                    "spacingDeltaFromLocked": spacing_delta,
                }
            )

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
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless numpy") from exc

    scaffold = load_json(SCAFFOLD)
    consensus = load_json(CONSENSUS)

    if scaffold.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V48 complete measures 17-113 coverage did not pass")
    if scaffold.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("V48 locked-measure safeguard is not intact")
    if consensus.get("geometryConsensusPassed") is not True:
        raise RuntimeError("V46 geometry consensus did not pass")

    locked_spacing = float(consensus.get("medianStringSpacingPixels", 0.0))
    if locked_spacing <= 0:
        raise RuntimeError("V46 median string spacing is unavailable")

    rows = sorted(
        scaffold.get("rows", []),
        key=lambda row: (
            int(row.get("pageNumber", 0)),
            int(row.get("rowIndex", 0)),
        ),
    )
    if len(rows) != 45:
        raise RuntimeError(f"Expected 45 canonical rows, found {len(rows)}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    passed_rows = 0
    covered: set[int] = set()

    print("Full-song v45-method string-line geometry extension v52 starting", flush=True)

    for row in rows:
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        measures = [int(value) for value in row.get("measures", [])]
        covered.update(measures)
        source_crop = row.get("crop")
        gray = cv2.imread(str(ROOT / str(source_crop)), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unreadable source crop: {source_crop}")

        height, width = gray.shape[:2]
        normalized = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(16, 8),
        ).apply(gray)
        blurred = cv2.GaussianBlur(normalized, (3, 3), 0)
        edges = cv2.Canny(blurred, 45, 135)

        horizontal_kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (max(35, width // 18), 1),
        )
        horizontal = cv2.morphologyEx(
            edges,
            cv2.MORPH_OPEN,
            horizontal_kernel,
        )
        horizontal = cv2.dilate(
            horizontal,
            cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1)),
            iterations=1,
        )

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

        projection_threshold = max(
            2.0,
            float(np.percentile(horizontal.mean(axis=1), 80)),
        )
        evidence.extend(projection_peaks(horizontal, projection_threshold))
        clusters = cluster_positions(evidence, tolerance=2.0)
        best = best_six_line_sequence(clusters, height, locked_spacing)

        if best is None:
            selected_rows: list[float] = []
            spacing = None
            gap_std = None
            continuity = 0.0
            score_margin = None
            spacing_delta = None
            passed = False
        else:
            selected_rows = [float(value) for value in best["rows"]]
            spacing = float(best["spacing"])
            gap_std = float(best["gapStd"])
            continuity = float(best["continuity"])
            score_margin = best.get("scoreMargin")
            spacing_delta = float(best["spacingDeltaFromLocked"])
            passed = (
                5.0 <= spacing <= 18.0
                and gap_std <= 1.25
                and continuity >= width * 0.20
                and spacing_delta <= 3.0
                and selected_rows[-1] < height
            )

        if passed:
            passed_rows += 1

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for cluster in clusters:
            y = round(float(cluster["y"]))
            cv2.line(preview, (0, y), (width - 1, y), (255, 0, 0), 1)
        color = (0, 255, 255) if passed else (0, 0, 255)
        for index, y_value in enumerate(selected_rows):
            y = round(y_value)
            cv2.line(preview, (0, y), (width - 1, y), color, 2)
            cv2.putText(
                preview,
                str(index + 1),
                (6, max(14, y - 3)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                color,
                1,
                cv2.LINE_AA,
            )

        preview_name = f"page-{page:02d}-row-{row_index:02d}-geometry.png"
        preview_path = PREVIEW_DIR / preview_name
        cv2.imwrite(str(preview_path), preview)

        report = {
            "pageNumber": page,
            "rowIndex": row_index,
            "measures": measures,
            "sourceCrop": source_crop,
            "imageWidth": width,
            "imageHeight": height,
            "houghHorizontalSegments": line_count,
            "clusterCount": len(clusters),
            "candidateClusterYs": [
                round(float(item["y"]), 3) for item in clusters
            ],
            "selectedStringRowsPixels": [
                round(value, 3) for value in selected_rows
            ],
            "selectedSpacingPixels": (
                round(spacing, 3) if spacing is not None else None
            ),
            "lockedSpacingPixels": round(locked_spacing, 6),
            "spacingDeltaFromLocked": (
                round(spacing_delta, 6) if spacing_delta is not None else None
            ),
            "gapStandardDeviation": (
                round(gap_std, 6) if gap_std is not None else None
            ),
            "continuityScore": round(continuity, 3),
            "scoreMargin": (
                round(float(score_margin), 6)
                if score_margin is not None
                else None
            ),
            "geometryCalibrationPassed": passed,
            "preview": str(preview_path.relative_to(ROOT)),
        }
        reports.append(report)
        print(
            f"Page {page} row {row_index}: measures={measures}, "
            f"segments={line_count}, clusters={len(clusters)}, "
            f"spacing={report['selectedSpacingPixels']}, "
            f"gapStd={report['gapStandardDeviation']}, passed={passed}",
            flush=True,
        )

    complete_coverage = covered == set(range(17, 114))
    all_rows_passed = passed_rows == 45
    output = {
        "diagnosticName": "Gomyway full-song v45-method string-line geometry v52",
        "methodSource": "analyzer/calibrate_gomyway_string_line_geometry_v45.py",
        "scaffoldSource": str(SCAFFOLD.relative_to(ROOT)),
        "consensusSource": str(CONSENSUS.relative_to(ROOT)),
        "rowsExpected": 45,
        "rowsInspected": len(reports),
        "rowsPassingGeometryCalibration": passed_rows,
        "allRowsPassedGeometryCalibration": all_rows_passed,
        "complete17To113CoveragePassed": complete_coverage,
        "lockedMedianStringSpacingPixels": round(locked_spacing, 6),
        "rows": reports,
        "humanVisualValidationComplete": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-v52-full-song-v45-method-previews"
            if all_rows_passed and complete_coverage
            else "inspect-v52-v45-method-geometry-failures-v53"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Full-song v45-method string-line geometry extension v52 complete")
    print("Rows expected: 45")
    print(f"Rows inspected: {len(reports)}")
    print(f"Rows passing geometry calibration: {passed_rows}")
    print(f"All rows passed geometry calibration: {all_rows_passed}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print("Human visual validation complete: False")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
