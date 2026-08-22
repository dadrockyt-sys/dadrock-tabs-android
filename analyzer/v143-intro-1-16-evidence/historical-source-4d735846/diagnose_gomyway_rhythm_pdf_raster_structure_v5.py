import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
STRUCTURE_PATH = PUBLIC / "gomyway-professional-rhythm-reference.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v5.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages-v5"

SCALE = 3.0
EXPECTED_MEASURES = 113


def cluster(values: list[int], tolerance: int) -> list[int]:
    if not values:
        return []
    values = sorted(values)
    groups: list[list[int]] = [[values[0]]]
    for value in values[1:]:
        if abs(value - round(median(groups[-1]))) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def six_string_groups(rows: list[int], spacing_tolerance: float) -> list[list[int]]:
    groups: list[list[int]] = []
    for i in range(len(rows) - 5):
        group = rows[i : i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if not (8 <= spacing <= 70):
            continue
        if max(abs(gap - spacing) for gap in gaps) > max(5, spacing * spacing_tolerance):
            continue
        if groups and abs(group[0] - groups[-1][0]) <= spacing * 3:
            continue
        groups.append(group)
    return groups


def longest_vertical_run(column: Any, np: Any) -> int:
    best = 0
    current = 0
    for value in column:
        if bool(value):
            current += 1
            best = max(best, current)
        else:
            current = 0
    return best


def detect_barlines(mask: Any, stave: list[int], np: Any, continuity: float) -> list[int]:
    spacing = median([stave[i + 1] - stave[i] for i in range(5)])
    top = max(0, int(stave[0] - spacing * 0.35))
    bottom = min(mask.shape[0] - 1, int(stave[-1] + spacing * 0.35))
    crop = mask[top : bottom + 1, :].copy()

    # Remove the six horizontal string bands before measuring vertical continuity.
    for y in stave:
        local_y = y - top
        y0 = max(0, local_y - 2)
        y1 = min(crop.shape[0], local_y + 3)
        crop[y0:y1, :] = False

    required = max(10, round(crop.shape[0] * continuity))
    candidates: list[int] = []
    for x in range(crop.shape[1]):
        x0 = max(0, x - 1)
        x1 = min(crop.shape[1], x + 2)
        merged = np.any(crop[:, x0:x1], axis=1)
        if longest_vertical_run(merged, np) >= required:
            candidates.append(x)

    xs = cluster(candidates, 5)
    xs = [x for x in xs if mask.shape[1] * 0.04 <= x <= mask.shape[1] * 0.97]
    if len(xs) < 2:
        return xs

    widths = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    useful = [width for width in widths if width >= 28]
    normal = median(useful) if useful else 0
    filtered = [xs[0]]
    minimum_gap = max(26, round(normal * 0.30)) if normal else 26
    for x in xs[1:]:
        if x - filtered[-1] >= minimum_gap:
            filtered.append(x)
    return filtered


def evaluate_configuration(image: Any, np: Any, percentile: int, row_ratio: float, spacing_tolerance: float, continuity: float) -> dict[str, Any]:
    threshold = min(245, int(np.percentile(image, percentile)) + 40)
    mask = image < threshold
    row_counts = mask.sum(axis=1)
    rows = [int(i) for i, count in enumerate(row_counts) if count >= image.shape[1] * row_ratio]
    rows = cluster(rows, max(2, round(SCALE * 1.5)))
    staves = six_string_groups(rows, spacing_tolerance)

    stave_results = []
    total_boxes = 0
    for stave in staves:
        xs = detect_barlines(mask, stave, np, continuity)
        boxes = max(0, len(xs) - 1)
        total_boxes += boxes
        stave_results.append({
            "stringRowsPixels": stave,
            "barlineColumnsPixels": xs,
            "measureBoxes": boxes,
        })

    # Prefer configurations that find multiple systems and a realistic 3-8 measures per system.
    nonempty = sum(1 for row in stave_results if row["measureBoxes"] > 0)
    unrealistic_penalty = sum(max(0, row["measureBoxes"] - 12) * 4 for row in stave_results)
    score = nonempty * 100 + total_boxes * 5 + len(staves) * 20 - unrealistic_penalty
    return {
        "percentile": percentile,
        "threshold": threshold,
        "rowRatio": row_ratio,
        "spacingTolerance": spacing_tolerance,
        "barlineContinuity": continuity,
        "horizontalRowsDetected": len(rows),
        "sixStringStavesDetected": len(staves),
        "fullHeightMeasureBoxes": total_boxes,
        "score": score,
        "staves": stave_results,
    }


def main() -> None:
    try:
        import fitz  # type: ignore
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install pymupdf numpy opencv-python-headless") from exc

    structure = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    metadata_pages = int(structure.get("sourcePageCount", 0) or 0)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)

    configurations = [
        (percentile, row_ratio, spacing_tolerance, continuity)
        for percentile in (20, 30, 40, 50)
        for row_ratio in (0.16, 0.20, 0.24, 0.28)
        for spacing_tolerance in (0.20, 0.28, 0.36)
        for continuity in (0.42, 0.50, 0.58, 0.66)
    ]

    pages = []
    total_staves = 0
    total_boxes = 0
    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False, colorspace=fitz.csGRAY)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)

        candidates = [
            evaluate_configuration(image, np, percentile, row_ratio, spacing_tolerance, continuity)
            for percentile, row_ratio, spacing_tolerance, continuity in configurations
        ]
        candidates.sort(key=lambda item: (item["score"], item["fullHeightMeasureBoxes"]), reverse=True)
        best = candidates[0]

        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for stave in best["staves"]:
            rows = stave["stringRowsPixels"]
            spacing = median([rows[i + 1] - rows[i] for i in range(5)])
            top = max(0, int(rows[0] - spacing * 0.35))
            bottom = min(pix.height - 1, int(rows[-1] + spacing * 0.35))
            for y in rows:
                cv2.line(annotated, (0, y), (pix.width - 1, y), (255, 0, 0), 1)
            for x in stave["barlineColumnsPixels"]:
                cv2.line(annotated, (x, top), (x, bottom), (0, 0, 255), 2)

        preview = PREVIEW_DIR / f"page-{page_index + 1:02d}.png"
        cv2.imwrite(str(preview), annotated)
        total_staves += best["sixStringStavesDetected"]
        total_boxes += best["fullHeightMeasureBoxes"]
        pages.append({
            "pageNumber": page_index + 1,
            "selectedConfiguration": best,
            "topAlternativeConfigurations": candidates[1:4],
            "preview": str(preview.relative_to(ROOT)),
        })

    exact_target = total_boxes == EXPECTED_MEASURES
    plausible = 100 <= total_boxes <= 126
    page_metadata_disagrees = metadata_pages != len(doc)

    output = {
        "diagnosticName": "Gomyway rhythm PDF adaptive raster calibration v5",
        "pdfPageCount": len(doc),
        "metadataSourcePageCount": metadata_pages,
        "pageMetadataDisagrees": page_metadata_disagrees,
        "pdfPageCountUsedAsAuthority": True,
        "totalSixStringStavesDetected": total_staves,
        "totalFullHeightMeasureBoxes": total_boxes,
        "exact113MeasureTargetPassed": exact_target,
        "plausible100To126MeasureRangePassed": plausible,
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF adaptive raster calibration v5 complete")
    print(f"PDF pages rendered: {len(doc)}")
    print(f"Metadata source pages: {metadata_pages}")
    print(f"Page metadata disagrees: {page_metadata_disagrees}")
    print("PDF page count used as authority: True")
    print(f"Six-string TAB staves detected: {total_staves}")
    print(f"Full-height measure boxes detected: {total_boxes}")
    print(f"Exact 113-measure target passed: {exact_target}")
    print(f"Plausible 100-126 measure range passed: {plausible}")
    print("Rhythm guitar only: True")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Annotated pages: {PREVIEW_DIR.relative_to(ROOT)}")

    if total_staves == 0:
        raise RuntimeError("Adaptive v5 calibration found no six-string TAB systems")


if __name__ == "__main__":
    main()
