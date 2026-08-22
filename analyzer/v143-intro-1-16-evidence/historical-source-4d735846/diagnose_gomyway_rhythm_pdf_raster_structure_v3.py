import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v3.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages-v3"

SCALE = 3.0
EXPECTED_MEASURES = 113


def cluster(values, tolerance):
    if not values:
        return []
    values = sorted(int(v) for v in values)
    groups = [[values[0]]]
    for value in values[1:]:
        if abs(value - round(median(groups[-1]))) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def detect_horizontal_rows(mask, np):
    width = mask.shape[1]
    counts = mask.sum(axis=1)
    rows = [int(i) for i, count in enumerate(counts) if count >= width * 0.28]
    return cluster(rows, max(2, round(SCALE * 1.5)))


def detect_six_string_staves(rows):
    staves = []
    i = 0
    while i <= len(rows) - 6:
        group = rows[i:i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if 10 <= spacing <= 55 and max(abs(gap - spacing) for gap in gaps) <= max(4, spacing * 0.18):
            staves.append(group)
            i += 6
        else:
            i += 1
    return staves


def vertical_continuity_score(mask, x, top, bottom, string_rows):
    x0 = max(0, x - 2)
    x1 = min(mask.shape[1], x + 3)
    crop = mask[top:bottom, x0:x1]
    if crop.size == 0:
        return 0.0

    row_hits = crop.any(axis=1)
    ignored = set()
    for y in string_rows:
        for yy in range(max(top, y - 2), min(bottom, y + 3)):
            ignored.add(yy - top)

    usable = [bool(hit) for idx, hit in enumerate(row_hits) if idx not in ignored]
    if not usable:
        return 0.0

    coverage = sum(usable) / len(usable)
    longest = 0
    current = 0
    for hit in usable:
        if hit:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    continuity = longest / len(usable)
    return 0.65 * coverage + 0.35 * continuity


def detect_barlines(mask, stave):
    spacing = median([stave[i + 1] - stave[i] for i in range(5)])
    top = max(0, round(stave[0] - spacing * 0.35))
    bottom = min(mask.shape[0], round(stave[-1] + spacing * 0.35))

    candidates = []
    for x in range(mask.shape[1]):
        score = vertical_continuity_score(mask, x, top, bottom, stave)
        if score >= 0.72:
            candidates.append(x)

    xs = cluster(candidates, max(3, round(SCALE * 2.0)))
    if len(xs) < 2:
        return []

    filtered = [xs[0]]
    for x in xs[1:]:
        if x - filtered[-1] >= 35:
            filtered.append(x)
    return filtered


def main():
    try:
        import fitz
        import numpy as np
        import cv2
    except ImportError as exc:
        raise RuntimeError("Run: pip install pymupdf numpy opencv-python-headless") from exc

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    pages = []
    total_staves = 0
    total_boxes = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False, colorspace=fitz.csGRAY)
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        threshold = min(235, int(np.percentile(image, 30)) + 45)
        mask = image < threshold

        rows = detect_horizontal_rows(mask, np)
        staves = detect_six_string_staves(rows)
        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        stave_rows = []

        for stave_index, stave in enumerate(staves):
            barlines = detect_barlines(mask, stave)
            boxes = max(0, len(barlines) - 1)
            total_boxes += boxes
            total_staves += 1

            for y in stave:
                cv2.line(annotated, (0, y), (pix.width - 1, y), (0, 180, 0), 1)
            for x in barlines:
                cv2.line(annotated, (x, stave[0] - 10), (x, stave[-1] + 10), (0, 0, 255), 2)

            stave_rows.append({
                "staveIndex": stave_index,
                "stringRowsPixels": stave,
                "barlineColumnsPixels": barlines,
                "estimatedMeasureBoxes": boxes,
            })

        preview = PREVIEW_DIR / f"page-{page_index + 1:02d}.png"
        cv2.imwrite(str(preview), annotated)
        pages.append({
            "pageNumber": page_index + 1,
            "sixStringStavesDetected": len(staves),
            "estimatedMeasureBoxes": sum(row["estimatedMeasureBoxes"] for row in stave_rows),
            "staves": stave_rows,
            "preview": str(preview.relative_to(ROOT)),
        })

    exact = total_boxes == EXPECTED_MEASURES
    plausible = 100 <= total_boxes <= 126
    output = {
        "diagnosticName": "Gomyway hybrid rhythm PDF raster structure diagnostic v3",
        "pageCount": len(doc),
        "totalSixStringStavesDetected": total_staves,
        "totalFullHeightMeasureBoxes": total_boxes,
        "exact113MeasureTargetPassed": exact,
        "plausible100To126MeasureRangePassed": plausible,
        "hybridMethod": "v1 staff rows plus strict full-height barline continuity",
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF raster structure diagnostic v3 complete")
    print(f"PDF pages rendered: {len(doc)}")
    print(f"Six-string TAB staves detected: {total_staves}")
    print(f"Full-height measure boxes detected: {total_boxes}")
    print(f"Exact 113-measure target passed: {exact}")
    print(f"Plausible 100-126 measure range passed: {plausible}")
    print("Rhythm guitar only: True")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Annotated pages: {PREVIEW_DIR.relative_to(ROOT)}")

    if not plausible:
        raise RuntimeError("Hybrid raster measure detection did not reach a plausible full-song range")


if __name__ == "__main__":
    main()
