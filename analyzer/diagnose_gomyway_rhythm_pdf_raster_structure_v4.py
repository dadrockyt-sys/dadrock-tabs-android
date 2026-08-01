import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
STRUCTURE_PATH = PUBLIC / "gomyway-professional-rhythm-reference.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v4.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages-v4"

SCALE = 3.0
EXPECTED_MEASURES = 113


def cluster(values, tolerance):
    if not values:
        return []
    values = sorted(values)
    groups = [[values[0]]]
    for value in values[1:]:
        if abs(value - median(groups[-1])) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def six_string_groups(rows):
    groups = []
    for i in range(len(rows) - 5):
        group = rows[i:i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if 10 <= spacing <= 60 and max(abs(g - spacing) for g in gaps) <= max(5, spacing * 0.24):
            if not groups or abs(group[0] - groups[-1][0]) > spacing * 3:
                groups.append(group)
    return groups


def normalized_hough_lines(lines, np):
    if lines is None:
        return []
    array = np.asarray(lines)
    if array.size == 0:
        return []
    return array.reshape(-1, 4)


def main():
    try:
        import fitz
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Run: pip install pymupdf numpy opencv-python-headless") from exc

    structure = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    expected_pages = int(structure.get("sourcePageCount", 0) or 0)

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    pages = []
    total_staves = 0
    total_boxes = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False, colorspace=fitz.csGRAY)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        h_lines = cv2.HoughLinesP(
            binary,
            1,
            np.pi / 180,
            threshold=80,
            minLineLength=max(120, int(pix.width * 0.22)),
            maxLineGap=18,
        )
        horizontal_rows = []
        for line in normalized_hough_lines(h_lines, np):
            x1, y1, x2, y2 = map(int, line.tolist())
            if abs(y2 - y1) <= 3 and abs(x2 - x1) >= pix.width * 0.22:
                horizontal_rows.append(round((y1 + y2) / 2))
        horizontal_rows = cluster(horizontal_rows, 4)
        staves = six_string_groups(horizontal_rows)

        page_rows = []
        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for stave_index, stave in enumerate(staves):
            spacing = median([stave[i + 1] - stave[i] for i in range(5)])
            top = max(0, int(stave[0] - spacing * 0.4))
            bottom = min(pix.height - 1, int(stave[-1] + spacing * 0.4))
            crop = binary[top:bottom + 1, :]

            v_lines = cv2.HoughLinesP(
                crop,
                1,
                np.pi / 180,
                threshold=max(18, int((bottom - top) * 0.45)),
                minLineLength=max(18, int((bottom - top) * 0.72)),
                maxLineGap=5,
            )
            xs = []
            for line in normalized_hough_lines(v_lines, np):
                x1, y1, x2, y2 = map(int, line.tolist())
                if abs(x2 - x1) <= 3 and abs(y2 - y1) >= (bottom - top) * 0.72:
                    xs.append(round((x1 + x2) / 2))
            xs = cluster(xs, 5)
            xs = [x for x in xs if pix.width * 0.04 <= x <= pix.width * 0.97]

            if len(xs) >= 2:
                widths = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
                normal = median([w for w in widths if w >= 25]) if any(w >= 25 for w in widths) else 0
                filtered = [xs[0]]
                for x in xs[1:]:
                    if x - filtered[-1] >= max(24, normal * 0.28 if normal else 24):
                        filtered.append(x)
                xs = filtered

            boxes = max(0, len(xs) - 1)
            total_boxes += boxes
            total_staves += 1
            page_rows.append({
                "staveIndex": stave_index,
                "stringRowsPixels": stave,
                "barlineColumnsPixels": xs,
                "measureBoxes": boxes,
            })

            for y in stave:
                cv2.line(annotated, (0, y), (pix.width - 1, y), (255, 0, 0), 1)
            for x in xs:
                cv2.line(annotated, (x, top), (x, bottom), (0, 0, 255), 2)

        preview = PREVIEW_DIR / f"page-{page_index + 1:02d}.png"
        cv2.imwrite(str(preview), annotated)
        pages.append({
            "pageNumber": page_index + 1,
            "horizontalRowsDetected": len(horizontal_rows),
            "sixStringStavesDetected": len(staves),
            "staves": page_rows,
            "preview": str(preview.relative_to(ROOT)),
        })

    page_count_matches = len(doc) == expected_pages
    exact_target = total_boxes == EXPECTED_MEASURES
    plausible = 100 <= total_boxes <= 126

    output = {
        "diagnosticName": "Gomyway rhythm PDF raster structure diagnostic v4",
        "pdfPageCount": len(doc),
        "expectedSourcePageCount": expected_pages,
        "sourcePageCountMatches": page_count_matches,
        "possibleMissingSourcePages": max(0, expected_pages - len(doc)),
        "totalSixStringStavesDetected": total_staves,
        "totalFullHeightMeasureBoxes": total_boxes,
        "exact113MeasureTargetPassed": exact_target,
        "plausible100To126MeasureRangePassed": plausible,
        "rhythmGuitarOnlyTarget": True,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF raster structure diagnostic v4 complete")
    print(f"PDF pages rendered: {len(doc)}")
    print(f"Expected source pages: {expected_pages}")
    print(f"Source page count matches: {page_count_matches}")
    print(f"Possible missing source pages: {output['possibleMissingSourcePages']}")
    print(f"Six-string TAB staves detected: {total_staves}")
    print(f"Full-height measure boxes detected: {total_boxes}")
    print(f"Exact 113-measure target passed: {exact_target}")
    print(f"Plausible 100-126 measure range passed: {plausible}")
    print("Rhythm guitar only: True")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Annotated pages: {PREVIEW_DIR.relative_to(ROOT)}")

    if not plausible:
        raise RuntimeError("Raster v4 measure detection did not reach a plausible full-song range")


if __name__ == "__main__":
    main()
