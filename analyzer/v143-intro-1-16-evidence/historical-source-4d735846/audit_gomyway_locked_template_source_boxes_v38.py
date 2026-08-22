import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-template-source-box-audit-v38.json"
OUTPUT_DIR = PUBLIC / "gomyway-locked-template-source-box-audit-v38"
REQUIRED_FRETS = ["0", "2", "3"]


def build_sheet(cv2: Any, np: Any, fret: str, entries: list[dict[str, Any]]) -> str:
    columns = 4
    cell_w = 300
    cell_h = 210
    header_h = 62
    rows = (len(entries) + columns - 1) // columns
    sheet = np.full((header_h + rows * cell_h, columns * cell_w, 3), 255, dtype=np.uint8)
    cv2.putText(
        sheet,
        f"Original professional crop + stored source box - fret {fret}",
        (18, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (0, 0, 0),
        2,
        cv2.LINE_AA,
    )

    for index, entry in enumerate(entries):
        row = index // columns
        column = index % columns
        left = column * cell_w
        top = header_h + row * cell_h
        cv2.rectangle(sheet, (left + 4, top + 4), (left + cell_w - 4, top + cell_h - 4), (190, 190, 190), 1)

        gray = cv2.imread(str(ROOT / entry["sourceCrop"]), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue
        box = entry["sourceBoundingBox"]
        x = int(box["x"])
        y = int(box["y"])
        width = int(box["width"])
        height = int(box["height"])

        pad_x = max(28, width * 6)
        pad_y = max(22, height * 4)
        x0 = max(0, x - pad_x)
        y0 = max(0, y - pad_y)
        x1 = min(gray.shape[1], x + width + pad_x)
        y1 = min(gray.shape[0], y + height + pad_y)
        context = cv2.cvtColor(gray[y0:y1, x0:x1], cv2.COLOR_GRAY2BGR)
        if context.size == 0:
            continue
        cv2.rectangle(
            context,
            (x - x0, y - y0),
            (x + width - x0, y + height - y0),
            (0, 0, 255),
            2,
        )
        center_x = x + width // 2 - x0
        center_y = y + height // 2 - y0
        cv2.drawMarker(context, (center_x, center_y), (0, 255, 255), cv2.MARKER_CROSS, 12, 1)

        target_w = 270
        target_h = 142
        scale = min(target_w / max(1, context.shape[1]), target_h / max(1, context.shape[0]))
        display = cv2.resize(
            context,
            (max(1, round(context.shape[1] * scale)), max(1, round(context.shape[0] * scale))),
            interpolation=cv2.INTER_NEAREST if scale >= 1 else cv2.INTER_AREA,
        )
        image_left = left + (cell_w - display.shape[1]) // 2
        image_top = top + 10
        sheet[image_top:image_top + display.shape[0], image_left:image_left + display.shape[1]] = display

        aspect = width / max(1, height)
        cv2.putText(sheet, entry["templateId"], (left + 12, top + 168), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 0, 0), 1, cv2.LINE_AA)
        cv2.putText(
            sheet,
            f"m{entry['measure']} s{entry['stringHighEToLowE']} box={width}x{height} ar={aspect:.2f}",
            (left + 12, top + 190),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"fret-{fret}-source-box-contact-sheet.png"
    cv2.imwrite(str(path), sheet)
    return str(path.relative_to(ROOT))


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    if not SOURCE_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {SOURCE_PATH.relative_to(ROOT)}")
    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if not bool(source.get("templateLibraryBuilt", False)):
        raise RuntimeError("V33 template library did not pass")

    all_entries = [
        entry
        for fret in REQUIRED_FRETS
        for entry in source.get("templates", {}).get(fret, [])
    ]
    if len(all_entries) != 70:
        raise RuntimeError(f"Expected 70 source entries, found {len(all_entries)}")

    aspect_values = []
    vertical_bar_like = []
    horizontal_fragment_like = []
    tiny_boxes = []
    dimensions = Counter()
    by_fret: dict[str, dict[str, Any]] = {}

    for fret in REQUIRED_FRETS:
        entries = source.get("templates", {}).get(fret, [])
        fret_aspects = []
        for entry in entries:
            box = entry["sourceBoundingBox"]
            width = int(box["width"])
            height = int(box["height"])
            aspect = width / max(1, height)
            aspect_values.append(aspect)
            fret_aspects.append(aspect)
            dimensions[f"{width}x{height}"] += 1
            summary = {
                "templateId": entry["templateId"],
                "fret": int(fret),
                "measure": entry["measure"],
                "stringHighEToLowE": entry["stringHighEToLowE"],
                "width": width,
                "height": height,
                "aspectRatio": round(aspect, 6),
                "sourceCrop": entry["sourceCrop"],
            }
            if aspect <= 0.48:
                vertical_bar_like.append(summary)
            if aspect >= 2.2:
                horizontal_fragment_like.append(summary)
            if width <= 4 or height <= 4:
                tiny_boxes.append(summary)
        by_fret[fret] = {
            "count": len(entries),
            "medianAspectRatio": round(median(fret_aspects), 6),
            "verticalBarLikeCount": sum(1 for value in fret_aspects if value <= 0.48),
            "horizontalFragmentLikeCount": sum(1 for value in fret_aspects if value >= 2.2),
        }

    contact_sheets = {
        fret: build_sheet(cv2, np, fret, source.get("templates", {}).get(fret, []))
        for fret in REQUIRED_FRETS
    }
    vertical_ratio = len(vertical_bar_like) / len(all_entries)
    source_boxes_likely_not_digit_glyphs = vertical_ratio >= 0.65

    output = {
        "diagnosticName": "Gomyway locked template source bounding box audit v38",
        "referenceType": "locked-professional-source-box-visual-audit",
        "sourceTemplateLibrary": str(SOURCE_PATH.relative_to(ROOT)),
        "templateEntriesObserved": len(all_entries),
        "requiredFretClasses": REQUIRED_FRETS,
        "countsByFret": by_fret,
        "medianAspectRatioAll": round(median(aspect_values), 6),
        "verticalBarLikeBoxes": vertical_bar_like,
        "verticalBarLikeCount": len(vertical_bar_like),
        "verticalBarLikeRatio": round(vertical_ratio, 6),
        "horizontalFragmentLikeBoxes": horizontal_fragment_like,
        "horizontalFragmentLikeCount": len(horizontal_fragment_like),
        "tinyBoxes": tiny_boxes,
        "tinyBoxCount": len(tiny_boxes),
        "commonDimensions": dimensions.most_common(12),
        "contactSheets": contact_sheets,
        "sourceBoxesLikelyNotDigitGlyphs": source_boxes_likely_not_digit_glyphs,
        "humanVisualValidationComplete": False,
        "glyphMasksHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "relocalize-locked-fret-digits-from-original-row-pixels-v39",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked template source bounding box audit v38 complete")
    print(f"Template entries observed: {len(all_entries)}")
    for fret in REQUIRED_FRETS:
        stats = by_fret[fret]
        print(
            f"Fret {fret}: count={stats['count']}, medianAspect={stats['medianAspectRatio']}, "
            f"verticalBarLike={stats['verticalBarLikeCount']}, horizontalLike={stats['horizontalFragmentLikeCount']}"
        )
    print(f"Median aspect ratio all boxes: {output['medianAspectRatioAll']}")
    print(f"Vertical-bar-like boxes: {len(vertical_bar_like)}")
    print(f"Vertical-bar-like ratio: {vertical_ratio:.6f}")
    print(f"Horizontal-fragment-like boxes: {len(horizontal_fragment_like)}")
    print(f"Tiny boxes: {len(tiny_boxes)}")
    print(f"Source boxes likely not digit glyphs: {source_boxes_likely_not_digit_glyphs}")
    print("All three source-box contact sheets built: True")
    print("Human visual validation complete: False")
    print("Glyph masks human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Contact sheets: {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
