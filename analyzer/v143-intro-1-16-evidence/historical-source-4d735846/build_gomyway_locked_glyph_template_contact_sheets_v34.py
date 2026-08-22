import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LIBRARY_PATH = PUBLIC / "gomyway-locked-glyph-template-library-v33.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-glyph-template-contact-sheets-v34.json"
CONTACT_DIR = PUBLIC / "gomyway-locked-glyph-template-contact-sheets-v34"
REQUIRED_FRETS = ["0", "2", "3"]


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    if not LIBRARY_PATH.exists():
        raise RuntimeError(f"Missing prerequisite: {LIBRARY_PATH.relative_to(ROOT)}")

    library = json.loads(LIBRARY_PATH.read_text(encoding="utf-8"))
    if not bool(library.get("templateLibraryBuilt", False)):
        raise RuntimeError("V33 template library was not built")
    if library.get("requiredFretClasses") != REQUIRED_FRETS:
        raise RuntimeError(
            f"Unexpected required frets: {library.get('requiredFretClasses')}"
        )
    if not bool(library.get("templatesRequireHumanVisualValidation", False)):
        raise RuntimeError("V33 did not require human visual validation")

    CONTACT_DIR.mkdir(parents=True, exist_ok=True)

    contact_sheets: dict[str, dict[str, Any]] = {}
    all_sheets_built = True

    print("Locked glyph template contact sheets v34 starting", flush=True)

    for fret in REQUIRED_FRETS:
        entries = list(library.get("templates", {}).get(fret, []))
        if not entries:
            raise RuntimeError(f"No templates available for fret {fret}")

        columns = 6
        rows = (len(entries) + columns - 1) // columns
        tile_width = 150
        tile_height = 150
        header_height = 54
        sheet_width = columns * tile_width
        sheet_height = header_height + rows * tile_height
        sheet = np.full((sheet_height, sheet_width, 3), 255, dtype=np.uint8)

        title = f"Professional locked glyph templates — fret {fret}"
        cv2.putText(
            sheet,
            title,
            (14, 34),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.72,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )

        missing_images: list[str] = []
        for index, entry in enumerate(entries):
            row = index // columns
            column = index % columns
            tile_x = column * tile_width
            tile_y = header_height + row * tile_height

            cv2.rectangle(
                sheet,
                (tile_x + 4, tile_y + 4),
                (tile_x + tile_width - 5, tile_y + tile_height - 5),
                (170, 170, 170),
                1,
            )

            image_path = ROOT / entry["templateImage"]
            image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                missing_images.append(str(image_path.relative_to(ROOT)))
                continue

            display = cv2.resize(image, (80, 80), interpolation=cv2.INTER_NEAREST)
            display = cv2.cvtColor(display, cv2.COLOR_GRAY2BGR)
            image_x = tile_x + (tile_width - 80) // 2
            image_y = tile_y + 12
            sheet[image_y:image_y + 80, image_x:image_x + 80] = display

            label_1 = str(entry.get("templateId", f"template-{index + 1}"))
            label_2 = (
                f"m{entry.get('measure')} s{entry.get('stringHighEToLowE')} "
                f"d={entry.get('distancePixels')}"
            )
            cv2.putText(
                sheet,
                label_1,
                (tile_x + 10, tile_y + 111),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.39,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )
            cv2.putText(
                sheet,
                label_2,
                (tile_x + 10, tile_y + 132),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.36,
                (0, 0, 0),
                1,
                cv2.LINE_AA,
            )

        contact_path = CONTACT_DIR / f"fret-{fret}-template-contact-sheet.png"
        written = cv2.imwrite(str(contact_path), sheet)
        sheet_built = bool(written and contact_path.exists() and not missing_images)
        all_sheets_built = all_sheets_built and sheet_built

        contact_sheets[fret] = {
            "fret": int(fret),
            "templateCount": len(entries),
            "columns": columns,
            "rows": rows,
            "contactSheet": str(contact_path.relative_to(ROOT)),
            "missingTemplateImages": missing_images,
            "contactSheetBuilt": sheet_built,
            "humanValidated": False,
        }
        print(
            f"Fret {fret}: templates={len(entries)}, rows={rows}, "
            f"sheetBuilt={sheet_built}",
            flush=True,
        )

    output = {
        "diagnosticName": "Gomyway locked glyph template contact sheets v34",
        "referenceType": "locked-professional-template-human-review-pack",
        "sourceTemplateLibrary": str(LIBRARY_PATH.relative_to(ROOT)),
        "requiredFretClasses": REQUIRED_FRETS,
        "templateCountsByFret": library.get("templateCountsByFret", {}),
        "contactSheets": contact_sheets,
        "allContactSheetsBuilt": all_sheets_built,
        "humanVisualValidationComplete": False,
        "humanVisualValidationRequired": True,
        "unresolvedTechniqueConnectedEventsExcluded": 6,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesHumanApproved": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-three-v34-contact-sheets"
            if all_sheets_built
            else "repair-missing-v34-template-contact-sheets"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked glyph template contact sheets v34 complete")
    print(f"Required fret classes: {REQUIRED_FRETS}")
    print(f"Template counts by fret: {output['templateCountsByFret']}")
    print(f"All contact sheets built: {all_sheets_built}")
    print("Human visual validation complete: False")
    print("Human visual validation required: True")
    print("Unresolved technique-connected events excluded: 6")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates human approved: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Contact sheets: {CONTACT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
