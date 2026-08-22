import json
import time
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
STRUCTURE_PATH = PUBLIC / "gomyway-professional-rhythm-reference.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-pdf-raster-structure-diagnostic-v6.json"
PREVIEW_DIR = PUBLIC / "gomyway-rhythm-pdf-raster-pages-v6"

SCALE = 3.0
EXPECTED_MEASURES = 113
MAX_SYSTEMS_PER_PAGE = 12


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


def stave_spacing(stave: list[int]) -> float:
    return float(median([stave[i + 1] - stave[i] for i in range(5)]))


def stave_overlap_ratio(a: list[int], b: list[int]) -> float:
    spacing = max(stave_spacing(a), stave_spacing(b))
    a0, a1 = a[0] - spacing, a[-1] + spacing
    b0, b1 = b[0] - spacing, b[-1] + spacing
    overlap = max(0.0, min(a1, b1) - max(a0, b0))
    span = max(1.0, min(a1 - a0, b1 - b0))
    return overlap / span


def six_string_groups(rows: list[int], spacing_tolerance: float) -> list[list[int]]:
    candidates: list[list[int]] = []
    for i in range(len(rows) - 5):
        group = rows[i : i + 6]
        gaps = [group[j + 1] - group[j] for j in range(5)]
        spacing = median(gaps)
        if not (10 <= spacing <= 34):
            continue
        if max(abs(gap - spacing) for gap in gaps) > max(3, spacing * spacing_tolerance):
            continue
        candidates.append(group)

    # Sliding windows create many near-identical candidates. Keep only one per real system.
    candidates.sort(key=lambda group: (group[0], max(group[i + 1] - group[i] for i in range(5))))
    selected: list[list[int]] = []
    for group in candidates:
        if any(stave_overlap_ratio(group, prior) >= 0.55 for prior in selected):
            continue
        selected.append(group)
    return selected


def longest_vertical_run(column: Any) -> int:
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
    spacing = stave_spacing(stave)
    top = max(0, int(stave[0] - spacing * 0.45))
    bottom = min(mask.shape[0] - 1, int(stave[-1] + spacing * 0.45))
    crop = mask[top : bottom + 1, :]

    # Keep the original crop. A true barline intersects or nearly intersects all strings;
    # deleting the string bands removed the strongest evidence in v5.
    required = max(10, round((stave[-1] - stave[0]) * continuity))
    candidates: list[int] = []
    for x in range(crop.shape[1]):
        x0 = max(0, x - 1)
        x1 = min(crop.shape[1], x + 2)
        merged = np.any(crop[:, x0:x1], axis=1)
        if longest_vertical_run(merged) >= required:
            candidates.append(x)

    xs = cluster(candidates, 5)
    left = round(mask.shape[1] * 0.04)
    right = round(mask.shape[1] * 0.97)
    xs = [x for x in xs if left <= x <= right]
    if len(xs) < 2:
        return xs

    # Merge duplicate thick barlines and reject implausibly tight note stems.
    widths = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    useful = [width for width in widths if width >= 32]
    normal = median(useful) if useful else 0
    minimum_gap = max(30, round(normal * 0.28)) if normal else 30
    filtered = [xs[0]]
    for x in xs[1:]:
        if x - filtered[-1] >= minimum_gap:
            filtered.append(x)
    return filtered


def evaluate_configuration(
    image: Any,
    np: Any,
    percentile: int,
    row_ratio: float,
    spacing_tolerance: float,
    continuity: float,
) -> dict[str, Any]:
    threshold = min(245, int(np.percentile(image, percentile)) + 40)
    mask = image < threshold
    row_counts = mask.sum(axis=1)
    rows = [
        int(i)
        for i, count in enumerate(row_counts)
        if count >= image.shape[1] * row_ratio
    ]
    rows = cluster(rows, max(2, round(SCALE * 1.5)))
    candidate_staves = six_string_groups(rows, spacing_tolerance)

    stave_results = []
    for stave in candidate_staves:
        xs = detect_barlines(mask, stave, np, continuity)
        boxes = max(0, len(xs) - 1)
        plausible = 1 <= boxes <= 12
        stave_results.append({
            "stringRowsPixels": stave,
            "barlineColumnsPixels": xs,
            "measureBoxes": boxes,
            "plausibleSystem": plausible,
        })

    valid_staves = [row for row in stave_results if row["plausibleSystem"]]
    valid_boxes = sum(row["measureBoxes"] for row in valid_staves)
    zero_box_count = sum(1 for row in stave_results if row["measureBoxes"] == 0)
    too_many_systems = max(0, len(valid_staves) - MAX_SYSTEMS_PER_PAGE)

    # A zero-box candidate must never help a configuration win.
    score = (
        len(valid_staves) * 300
        + valid_boxes * 20
        - zero_box_count * 180
        - too_many_systems * 500
        - max(0, len(candidate_staves) - 20) * 80
    )

    return {
        "percentile": percentile,
        "threshold": threshold,
        "rowRatio": row_ratio,
        "spacingTolerance": spacing_tolerance,
        "barlineContinuity": continuity,
        "horizontalRowsDetected": len(rows),
        "candidateSixStringStavesDetected": len(candidate_staves),
        "validSixStringStavesDetected": len(valid_staves),
        "validFullHeightMeasureBoxes": valid_boxes,
        "zeroBoxCandidateCount": zero_box_count,
        "score": score,
        "staves": stave_results,
    }


def main() -> None:
    try:
        import fitz  # type: ignore
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "Run: pip install pymupdf numpy opencv-python-headless"
        ) from exc

    structure = json.loads(STRUCTURE_PATH.read_text(encoding="utf-8"))
    metadata_pages = int(structure.get("sourcePageCount", 0) or 0)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(PDF_PATH)

    # Narrow, structural sweep. v5 proved that a wider permissive sweep rewards noise.
    configurations = [
        (percentile, row_ratio, spacing_tolerance, continuity)
        for percentile in (20, 30, 40)
        for row_ratio in (0.18, 0.22, 0.26)
        for spacing_tolerance in (0.12, 0.18, 0.24)
        for continuity in (0.55, 0.65, 0.75)
    ]

    print("Rhythm PDF structural raster detector v6 starting", flush=True)
    print(f"Pages: {len(doc)}; configurations per page: {len(configurations)}", flush=True)

    pages = []
    total_staves = 0
    total_boxes = 0
    started = time.monotonic()

    for page_index in range(len(doc)):
        page_started = time.monotonic()
        print(f"Page {page_index + 1}/{len(doc)}: rendering", flush=True)
        page = doc[page_index]
        pix = page.get_pixmap(
            matrix=fitz.Matrix(SCALE, SCALE),
            alpha=False,
            colorspace=fitz.csGRAY,
        )
        image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)

        candidates = []
        for config_index, (percentile, row_ratio, spacing_tolerance, continuity) in enumerate(configurations, start=1):
            candidates.append(
                evaluate_configuration(
                    image,
                    np,
                    percentile,
                    row_ratio,
                    spacing_tolerance,
                    continuity,
                )
            )
            if config_index % 27 == 0 or config_index == len(configurations):
                print(
                    f"  page {page_index + 1}: {config_index}/{len(configurations)} configurations",
                    flush=True,
                )

        candidates.sort(
            key=lambda item: (
                item["score"],
                item["validFullHeightMeasureBoxes"],
                item["validSixStringStavesDetected"],
            ),
            reverse=True,
        )
        best = candidates[0]
        valid_staves = [row for row in best["staves"] if row["plausibleSystem"]]

        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        for stave in valid_staves:
            rows = stave["stringRowsPixels"]
            spacing = stave_spacing(rows)
            top = max(0, int(rows[0] - spacing * 0.45))
            bottom = min(pix.height - 1, int(rows[-1] + spacing * 0.45))
            for y in rows:
                cv2.line(annotated, (0, y), (pix.width - 1, y), (255, 0, 0), 1)
            for x in stave["barlineColumnsPixels"]:
                cv2.line(annotated, (x, top), (x, bottom), (0, 0, 255), 2)

        preview = PREVIEW_DIR / f"page-{page_index + 1:02d}.png"
        cv2.imwrite(str(preview), annotated)
        total_staves += best["validSixStringStavesDetected"]
        total_boxes += best["validFullHeightMeasureBoxes"]
        pages.append({
            "pageNumber": page_index + 1,
            "selectedConfiguration": best,
            "topAlternativeConfigurations": candidates[1:4],
            "preview": str(preview.relative_to(ROOT)),
        })
        print(
            f"Page {page_index + 1} complete: "
            f'{best["validSixStringStavesDetected"]} valid staves, '
            f'{best["validFullHeightMeasureBoxes"]} boxes, '
            f"{time.monotonic() - page_started:.1f}s",
            flush=True,
        )

    exact_target = total_boxes == EXPECTED_MEASURES
    plausible = 100 <= total_boxes <= 126
    page_metadata_disagrees = metadata_pages != len(doc)

    output = {
        "diagnosticName": "Gomyway rhythm PDF structural raster detector v6",
        "pdfPageCount": len(doc),
        "metadataSourcePageCount": metadata_pages,
        "pageMetadataDisagrees": page_metadata_disagrees,
        "pdfPageCountUsedAsAuthority": True,
        "totalValidSixStringStavesDetected": total_staves,
        "totalValidFullHeightMeasureBoxes": total_boxes,
        "exact113MeasureTargetPassed": exact_target,
        "plausible100To126MeasureRangePassed": plausible,
        "rhythmGuitarOnlyTarget": True,
        "leadGuitarIncluded": False,
        "bassIncluded": False,
        "vocalsIncluded": False,
        "verifiedMeasures1To16Protected": True,
        "pages": pages,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rhythm PDF structural raster detector v6 complete", flush=True)
    print(f"Elapsed seconds: {time.monotonic() - started:.1f}", flush=True)
    print(f"PDF pages rendered: {len(doc)}", flush=True)
    print(f"Metadata source pages: {metadata_pages}", flush=True)
    print(f"Page metadata disagrees: {page_metadata_disagrees}", flush=True)
    print("PDF page count used as authority: True", flush=True)
    print(f"Valid six-string TAB staves detected: {total_staves}", flush=True)
    print(f"Valid full-height measure boxes detected: {total_boxes}", flush=True)
    print(f"Exact 113-measure target passed: {exact_target}", flush=True)
    print(f"Plausible 100-126 measure range passed: {plausible}", flush=True)
    print("Verified measures 1-16 protected: True", flush=True)
    print("Rhythm guitar only: True", flush=True)
    print("Production promotion allowed: False", flush=True)
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}", flush=True)
    print(f"Annotated pages: {PREVIEW_DIR.relative_to(ROOT)}", flush=True)

    if total_staves == 0:
        raise RuntimeError("Structural v6 detector found no valid six-string TAB systems")


if __name__ == "__main__":
    main()
