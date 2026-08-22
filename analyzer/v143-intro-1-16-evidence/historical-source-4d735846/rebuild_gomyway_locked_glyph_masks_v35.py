import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-glyph-mask-rebuild-v35.json"
OUTPUT_DIR = PUBLIC / "gomyway-locked-glyph-mask-rebuild-v35"
CONTACT_DIR = PUBLIC / "gomyway-locked-glyph-mask-contact-sheets-v35"
REQUIRED_FRETS = ["0", "2", "3"]
CANVAS_SIZE = 48


def tight_mask(cv2: Any, gray: Any, box: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    x = int(box["x"])
    y = int(box["y"])
    width = int(box["width"])
    height = int(box["height"])
    pad_x = max(2, round(width * 0.25))
    pad_y = max(2, round(height * 0.25))
    x0 = max(0, x - pad_x)
    y0 = max(0, y - pad_y)
    x1 = min(gray.shape[1], x + width + pad_x)
    y1 = min(gray.shape[0], y + height + pad_y)
    patch = gray[y0:y1, x0:x1]
    if patch.size == 0:
        raise RuntimeError("Empty source patch")

    blurred = cv2.GaussianBlur(patch, (3, 3), 0)
    _, bright = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, dark = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    def score(mask: Any) -> float:
        ratio = float(cv2.countNonZero(mask)) / float(mask.size)
        if ratio <= 0.01 or ratio >= 0.55:
            return 999.0
        return abs(ratio - 0.16)

    mask = bright if score(bright) <= score(dark) else dark

    # Remove only long, nearly full-width horizontal remnants. Preserve digit strokes.
    row_counts = (mask > 0).sum(axis=1)
    for row_index, count in enumerate(row_counts):
        if count >= max(8, int(mask.shape[1] * 0.78)):
            mask[max(0, row_index - 1):min(mask.shape[0], row_index + 2), :] = 0

    # Keep components near the original component centre, while allowing split digit strokes.
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    target_x = (x + width / 2.0) - x0
    target_y = (y + height / 2.0) - y0
    selected = []
    for index in range(1, count):
        area = int(stats[index, cv2.CC_STAT_AREA])
        if area < 2:
            continue
        cx, cy = centroids[index]
        dx = abs(float(cx) - target_x)
        dy = abs(float(cy) - target_y)
        if dx <= max(width * 1.2, 10) and dy <= max(height * 1.2, 10):
            selected.append(index)

    cleaned = mask * 0
    for index in selected:
        cleaned[labels == index] = 255

    ys, xs = (cleaned > 0).nonzero()
    if len(xs) == 0:
        cleaned = mask
        ys, xs = (cleaned > 0).nonzero()
    if len(xs) == 0:
        raise RuntimeError("No foreground after cleanup")

    tx0, tx1 = int(xs.min()), int(xs.max()) + 1
    ty0, ty1 = int(ys.min()), int(ys.max()) + 1
    glyph = cleaned[ty0:ty1, tx0:tx1]

    target_extent = CANVAS_SIZE - 10
    scale = min(target_extent / max(1, glyph.shape[1]), target_extent / max(1, glyph.shape[0]))
    resized_w = max(1, round(glyph.shape[1] * scale))
    resized_h = max(1, round(glyph.shape[0] * scale))
    interpolation = cv2.INTER_NEAREST if scale >= 1 else cv2.INTER_AREA
    resized = cv2.resize(glyph, (resized_w, resized_h), interpolation=interpolation)
    canvas = resized * 0
    canvas = cv2.copyMakeBorder(
        resized,
        (CANVAS_SIZE - resized_h) // 2,
        CANVAS_SIZE - resized_h - (CANVAS_SIZE - resized_h) // 2,
        (CANVAS_SIZE - resized_w) // 2,
        CANVAS_SIZE - resized_w - (CANVAS_SIZE - resized_w) // 2,
        cv2.BORDER_CONSTANT,
        value=0,
    )

    metadata = {
        "sourcePatch": [x0, y0, x1, y1],
        "tightForegroundBox": [tx0, ty0, tx1, ty1],
        "foregroundPixels": int(cv2.countNonZero(cleaned)),
        "foregroundRatio": round(float(cv2.countNonZero(canvas)) / float(canvas.size), 6),
        "selectedComponentCount": len(selected),
    }
    return canvas, metadata


def build_contact_sheet(cv2: Any, fret: str, entries: list[dict[str, Any]]) -> Path:
    import numpy as np

    columns = 6
    cell_w = 150
    cell_h = 115
    header_h = 58
    rows = (len(entries) + columns - 1) // columns
    sheet = np.full((header_h + rows * cell_h, columns * cell_w), 255, dtype=np.uint8)
    cv2.putText(sheet, f"Clean locked glyph masks - fret {fret}", (18, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 2, cv2.LINE_AA)
    for index, entry in enumerate(entries):
        row = index // columns
        column = index % columns
        left = column * cell_w
        top = header_h + row * cell_h
        cv2.rectangle(sheet, (left + 4, top + 4), (left + cell_w - 4, top + cell_h - 4), 190, 1)
        mask = cv2.imread(str(ROOT / entry["cleanMaskImage"]), cv2.IMREAD_GRAYSCALE)
        display = 255 - mask
        sheet[top + 10:top + 58, left + 51:left + 99] = display
        cv2.putText(sheet, entry["templateId"], (left + 10, top + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 0, 1, cv2.LINE_AA)
        cv2.putText(sheet, f"m{entry['measure']} s{entry['stringHighEToLowE']}", (left + 10, top + 98), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 0, 1, cv2.LINE_AA)
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    path = CONTACT_DIR / f"fret-{fret}-clean-mask-contact-sheet.png"
    cv2.imwrite(str(path), sheet)
    return path


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    if not SOURCE_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {SOURCE_PATH.relative_to(ROOT)}")
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if not bool(source.get("templateLibraryBuilt", False)):
        raise RuntimeError("V33 template library did not pass")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rebuilt: dict[str, list[dict[str, Any]]] = {}
    failures: list[dict[str, Any]] = []

    print("Locked glyph tight binary mask rebuild v35 starting", flush=True)
    for fret in REQUIRED_FRETS:
        entries = []
        for source_entry in source.get("templates", {}).get(fret, []):
            try:
                gray = cv2.imread(str(ROOT / source_entry["sourceCrop"]), cv2.IMREAD_GRAYSCALE)
                if gray is None:
                    raise RuntimeError("Unable to read source crop")
                mask, metadata = tight_mask(cv2, gray, source_entry["sourceBoundingBox"])
                output_name = f"{source_entry['templateId']}-clean-mask.png"
                output_image = OUTPUT_DIR / output_name
                cv2.imwrite(str(output_image), mask)
                entries.append({
                    **source_entry,
                    "cleanMaskImage": str(output_image.relative_to(ROOT)),
                    "cleanMaskSize": [CANVAS_SIZE, CANVAS_SIZE],
                    "maskMetadata": metadata,
                    "humanValidated": False,
                })
            except Exception as exc:
                failures.append({
                    "templateId": source_entry.get("templateId"),
                    "fret": fret,
                    "error": str(exc),
                })
        rebuilt[fret] = entries
        print(f"Fret {fret}: rebuilt={len(entries)}, failed={sum(1 for item in failures if item['fret'] == fret)}", flush=True)

    contact_sheets = {
        fret: str(build_contact_sheet(cv2, fret, rebuilt[fret]).relative_to(ROOT))
        for fret in REQUIRED_FRETS
    }
    expected_counts = source.get("templateCountsByFret", {})
    all_masks_built = all(len(rebuilt[fret]) == int(expected_counts.get(fret, -1)) for fret in REQUIRED_FRETS)
    plausible_foreground = all(
        0.015 <= float(entry["maskMetadata"]["foregroundRatio"]) <= 0.48
        for fret in REQUIRED_FRETS
        for entry in rebuilt[fret]
    )

    output = {
        "diagnosticName": "Gomyway locked glyph tight binary mask rebuild v35",
        "referenceType": "locked-professional-glyph-mask-rebuild",
        "sourceTemplateLibrary": str(SOURCE_PATH.relative_to(ROOT)),
        "requiredFretClasses": REQUIRED_FRETS,
        "rebuiltCountsByFret": {fret: len(rebuilt[fret]) for fret in REQUIRED_FRETS},
        "failedTemplates": failures,
        "allMasksBuilt": all_masks_built,
        "allMasksHavePlausibleForeground": plausible_foreground,
        "contactSheets": contact_sheets,
        "cleanMasks": rebuilt,
        "humanVisualValidationComplete": False,
        "glyphMasksHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-three-v35-clean-mask-contact-sheets",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked glyph tight binary mask rebuild v35 complete")
    print(f"Rebuilt counts by fret: {output['rebuiltCountsByFret']}")
    print(f"Failed templates: {len(failures)}")
    print(f"All masks built: {all_masks_built}")
    print(f"All masks have plausible foreground: {plausible_foreground}")
    print("Human visual validation complete: False")
    print("Glyph masks human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Clean masks: {OUTPUT_DIR.relative_to(ROOT)}")
    print(f"Contact sheets: {CONTACT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
