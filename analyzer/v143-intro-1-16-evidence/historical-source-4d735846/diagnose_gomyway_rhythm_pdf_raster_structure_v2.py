import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v2.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages-v2"

SCALE = 3.0
EXPECTED_MEASURES = 113


def import_dependencies():
    try:
        import fitz  # type: ignore
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install pymupdf numpy opencv-python-headless") from exc
    return fitz, cv2, np


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


def horizontal_line_rows(binary: Any, cv2: Any, np: Any) -> list[int]:
    width = binary.shape[1]
    kernel_width = max(80, width // 7)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1))
    lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    counts = (lines > 0).sum(axis=1)
    candidates = [int(i) for i, count in enumerate(counts) if count >= width * 0.22]
    return cluster(candidates, max(3, round(SCALE * 2)))


def six_string_staves(rows: list[int]) -> list[list[int]]:
    candidates: list[list[int]] = []
    for i in range(0, max(0, len(rows) - 5)):
        group = rows[i : i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if not 10 <= spacing <= 60:
            continue
        if max(abs(gap - spacing) for gap in gaps) > max(5, spacing * 0.22):
            continue
        candidates.append(group)

    result: list[list[int]] = []
    for group in candidates:
        center = median(group)
        if any(abs(center - median(existing)) < median(existing[1:]) - existing[0] for existing in result):
            continue
        result.append(group)
    return result


def barline_columns(binary: Any, stave: list[int], cv2: Any, np: Any) -> list[int]:
    spacing = median([stave[i + 1] - stave[i] for i in range(5)])
    top = max(0, round(stave[0] - spacing * 0.45))
    bottom = min(binary.shape[0], round(stave[-1] + spacing * 0.45))
    crop = binary[top:bottom, :]
    staff_height = crop.shape[0]

    kernel_height = max(15, round(staff_height * 0.72))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, kernel_height))
    vertical = cv2.morphologyEx(crop, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    xs: list[int] = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if h < staff_height * 0.72:
            continue
        if w > max(12, spacing * 0.45):
            continue
        xs.append(round(x + w / 2))

    xs = cluster(xs, max(4, round(SCALE * 2)))
    xs.sort()

    filtered: list[int] = []
    for x in xs:
        if not filtered or x - filtered[-1] >= max(18, round(spacing * 1.8)):
            filtered.append(x)
    return filtered


def measure_boxes_from_barlines(barlines: list[int], page_width: int) -> list[list[int]]:
    if len(barlines) < 2:
        return []
    gaps = [barlines[i + 1] - barlines[i] for i in range(len(barlines) - 1)]
    usable = [gap for gap in gaps if gap >= 30]
    if not usable:
        return []
    typical = median(usable)
    boxes: list[list[int]] = []
    for i, gap in enumerate(gaps):
        if gap < max(28, typical * 0.35):
            continue
        if gap > typical * 2.6:
            estimated = max(2, round(gap / typical))
            step = gap / estimated
            for part in range(estimated):
                boxes.append([round(barlines[i] + part * step), round(barlines[i] + (part + 1) * step)])
        else:
            boxes.append([barlines[i], barlines[i + 1]])
    return [box for box in boxes if 0 <= box[0] < box[1] <= page_width]


def main() -> None:
    fitz, cv2, np = import_dependencies()
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing PDF: {PDF_PATH.relative_to(ROOT)}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    pages: list[dict[str, Any]] = []
    total_staves = 0
    total_boxes = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False, colorspace=fitz.csGRAY)
        gray = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            41,
            12,
        )

        rows = horizontal_line_rows(binary, cv2, np)
        staves = six_string_staves(rows)
        annotated = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        stave_rows: list[dict[str, Any]] = []

        for stave_index, stave in enumerate(staves):
            barlines = barline_columns(binary, stave, cv2, np)
            boxes = measure_boxes_from_barlines(barlines, pix.width)
            total_boxes += len(boxes)
            total_staves += 1

            for y in stave:
                cv2.line(annotated, (0, y), (pix.width - 1, y), (0, 180, 0), 1)
            for x in barlines:
                cv2.line(annotated, (x, stave[0]), (x, stave[-1]), (0, 0, 220), 2)
            for box_index, (x0, x1) in enumerate(boxes):
                cv2.rectangle(annotated, (x0, stave[0]), (x1, stave[-1]), (220, 120, 0), 1)
                cv2.putText(
                    annotated,
                    str(box_index + 1),
                    (x0 + 4, max(14, stave[0] - 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (0, 0, 180),
                    1,
                    cv2.LINE_AA,
                )

            stave_rows.append(
                {
                    "staveIndex": stave_index,
                    "stringRowsPixels": stave,
                    "estimatedSpacingPixels": round(median([stave[i + 1] - stave[i] for i in range(5)]), 2),
                    "barlineColumnsPixels": barlines,
                    "measureBoxesPixels": boxes,
                    "measureBoxCount": len(boxes),
                }
            )

        preview_path = PREVIEW_DIR / f"page-{page_index + 1:02d}-annotated.png"
        cv2.imwrite(str(preview_path), annotated)
        pages.append(
            {
                "pageNumber": page_index + 1,
                "widthPixels": pix.width,
                "heightPixels": pix.height,
                "horizontalRowsDetected": len(rows),
                "sixStringStavesDetected": len(staves),
                "measureBoxCount": sum(row["measureBoxCount"] for row in stave_rows),
                "staves": stave_rows,
                "preview": str(preview_path.relative_to(ROOT)),
            }
        )

    exact_measure_target = total_boxes == EXPECTED_MEASURES
    plausible_measure_target = 100 <= total_boxes <= 126
    output = {
        "diagnosticName": "Gomyway rhythm PDF raster structure diagnostic v2",
        "pdf": str(PDF_PATH.relative_to(ROOT)),
        "pageCount": len(doc),
        "renderScale": SCALE,
        "totalSixStringStavesDetected": total_staves,
        "totalMeasureBoxesDetected": total_boxes,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "exact113MeasureTargetPassed": exact_measure_target,
        "plausibleMeasureTargetPassed": plausible_measure_target,
        "rasterStructurePresent": total_staves > 0 and total_boxes > 0,
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF raster structure diagnostic v2 complete")
    print(f"PDF pages rendered: {len(doc)}")
    print(f"Six-string TAB staves detected: {total_staves}")
    print(f"Full-height measure boxes detected: {total_boxes}")
    print(f"Exact 113-measure target passed: {exact_measure_target}")
    print(f"Plausible 100-126 measure range passed: {plausible_measure_target}")
    print("Rhythm guitar only: True")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Annotated pages: {PREVIEW_DIR.relative_to(ROOT)}")

    if not plausible_measure_target:
        raise RuntimeError("Raster v2 measure detection did not reach a plausible full-song range")


if __name__ == "__main__":
    main()
