import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages"

SCALE = 3.0
MIN_HORIZONTAL_RATIO = 0.28
MIN_VERTICAL_RATIO = 0.12


def import_dependencies():
    try:
        import fitz  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install pymupdf numpy") from exc
    return fitz, np


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


def detect_horizontal_rows(mask: Any, np: Any) -> list[int]:
    width = mask.shape[1]
    counts = mask.sum(axis=1)
    candidates = [int(i) for i, count in enumerate(counts) if count >= width * MIN_HORIZONTAL_RATIO]
    return cluster(candidates, max(2, round(SCALE * 1.5)))


def detect_six_string_staves(rows: list[int]) -> list[list[int]]:
    staves: list[list[int]] = []
    i = 0
    while i <= len(rows) - 6:
        group = rows[i : i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if 10 <= spacing <= 55 and max(abs(gap - spacing) for gap in gaps) <= max(4, spacing * 0.18):
            staves.append(group)
            i += 6
        else:
            i += 1
    return staves


def detect_vertical_barlines(mask: Any, stave: list[int], np: Any) -> list[int]:
    top = max(0, stave[0] - round((stave[1] - stave[0]) * 1.2))
    bottom = min(mask.shape[0], stave[-1] + round((stave[1] - stave[0]) * 1.2))
    crop = mask[top:bottom, :]
    height = crop.shape[0]
    counts = crop.sum(axis=0)
    candidates = [int(i) for i, count in enumerate(counts) if count >= height * MIN_VERTICAL_RATIO]
    return cluster(candidates, max(2, round(SCALE * 1.5)))


def main() -> None:
    fitz, np = import_dependencies()
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"Missing PDF: {PDF_PATH.relative_to(ROOT)}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)
    pages = []
    total_staves = 0
    total_measure_boxes = 0

    for page_index in range(len(doc)):
        page = doc[page_index]
        pix = page.get_pixmap(matrix=fitz.Matrix(SCALE, SCALE), alpha=False, colorspace=fitz.csGRAY)
        preview_path = PREVIEW_DIR / f"page-{page_index + 1:02d}.png"
        pix.save(preview_path)

        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
        threshold = min(235, int(np.percentile(image, 30)) + 45)
        mask = image < threshold

        horizontal_rows = detect_horizontal_rows(mask, np)
        staves = detect_six_string_staves(horizontal_rows)
        stave_rows = []
        for stave_index, stave in enumerate(staves):
            barlines = detect_vertical_barlines(mask, stave, np)
            usable_boxes = max(0, len(barlines) - 1)
            stave_rows.append(
                {
                    "staveIndex": stave_index,
                    "stringRowsPixels": stave,
                    "estimatedSpacingPixels": round(median([stave[i + 1] - stave[i] for i in range(5)]), 2),
                    "barlineColumnsPixels": barlines,
                    "estimatedMeasureBoxes": usable_boxes,
                }
            )
            total_measure_boxes += usable_boxes

        total_staves += len(staves)
        pages.append(
            {
                "pageNumber": page_index + 1,
                "widthPixels": pix.width,
                "heightPixels": pix.height,
                "threshold": threshold,
                "horizontalRowsDetected": len(horizontal_rows),
                "sixStringStavesDetected": len(staves),
                "staves": stave_rows,
                "preview": str(preview_path.relative_to(ROOT)),
            }
        )

    raster_structure_present = total_staves > 0 and total_measure_boxes > 0
    output = {
        "diagnosticName": "Gomyway rhythm PDF raster structure diagnostic",
        "pdf": str(PDF_PATH.relative_to(ROOT)),
        "pageCount": len(doc),
        "renderScale": SCALE,
        "totalSixStringStavesDetected": total_staves,
        "totalEstimatedMeasureBoxes": total_measure_boxes,
        "rasterStructurePresent": raster_structure_present,
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF raster structure diagnostic complete")
    print(f"PDF pages rendered: {len(doc)}")
    print(f"Six-string TAB staves detected: {total_staves}")
    print(f"Estimated measure boxes detected: {total_measure_boxes}")
    print(f"Raster TAB structure present: {raster_structure_present}")
    print("Rhythm guitar only: True")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Rendered pages: {PREVIEW_DIR.relative_to(ROOT)}")

    if not raster_structure_present:
        raise RuntimeError("No usable raster TAB structure was detected")


if __name__ == "__main__":
    main()
