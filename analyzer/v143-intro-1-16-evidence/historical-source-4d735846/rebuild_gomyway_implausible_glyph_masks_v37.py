import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-locked-glyph-mask-rebuild-v35.json"
AUDIT_PATH = PUBLIC / "gomyway-locked-glyph-mask-failure-audit-v36.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-glyph-mask-targeted-rebuild-v37.json"
OUTPUT_DIR = PUBLIC / "gomyway-locked-glyph-mask-targeted-rebuild-v37"
CONTACT_DIR = PUBLIC / "gomyway-locked-glyph-mask-contact-sheets-v37"
REQUIRED_FRETS = ["0", "2", "3"]
MIN_RATIO = 0.015
MAX_RATIO = 0.48


def ratio(cv2: Any, mask: Any) -> float:
    return float(cv2.countNonZero(mask)) / float(mask.size)


def adaptive_reduce_dense_mask(cv2: Any, mask: Any) -> tuple[Any, dict[str, Any]]:
    working = mask.copy()
    initial_ratio = ratio(cv2, working)
    iterations = 0
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    while ratio(cv2, working) > MAX_RATIO and iterations < 6:
        candidate = cv2.erode(working, kernel, iterations=1)
        if cv2.countNonZero(candidate) == 0:
            break
        working = candidate
        iterations += 1

    # If erosion alone cannot reduce density enough, remove edge-touching runs.
    if ratio(cv2, working) > MAX_RATIO:
        count, labels, stats, _ = cv2.connectedComponentsWithStats(working, 8)
        keep = working * 0
        components = []
        for index in range(1, count):
            x = int(stats[index, cv2.CC_STAT_LEFT])
            y = int(stats[index, cv2.CC_STAT_TOP])
            w = int(stats[index, cv2.CC_STAT_WIDTH])
            h = int(stats[index, cv2.CC_STAT_HEIGHT])
            area = int(stats[index, cv2.CC_STAT_AREA])
            touches = x == 0 or y == 0 or x + w >= working.shape[1] or y + h >= working.shape[0]
            components.append((touches, -area, index))
        components.sort()
        for touches, _, index in components:
            if touches and cv2.countNonZero(keep) > 0:
                continue
            keep[labels == index] = 255
            if MIN_RATIO <= ratio(cv2, keep) <= MAX_RATIO:
                working = keep
                break

    final_ratio = ratio(cv2, working)
    return working, {
        "initialForegroundRatio": round(initial_ratio, 6),
        "finalForegroundRatio": round(final_ratio, 6),
        "erosionIterations": iterations,
        "plausibleForeground": MIN_RATIO <= final_ratio <= MAX_RATIO,
    }


def build_contact_sheet(cv2: Any, fret: str, entries: list[dict[str, Any]]) -> Path:
    import numpy as np

    columns = 6
    cell_w = 150
    cell_h = 115
    header_h = 58
    rows = (len(entries) + columns - 1) // columns
    sheet = np.full((header_h + rows * cell_h, columns * cell_w), 255, dtype=np.uint8)
    cv2.putText(sheet, f"Targeted rebuilt glyph masks - fret {fret}", (18, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.86, 0, 2, cv2.LINE_AA)
    for index, entry in enumerate(entries):
        row = index // columns
        column = index % columns
        left = column * cell_w
        top = header_h + row * cell_h
        cv2.rectangle(sheet, (left + 4, top + 4), (left + cell_w - 4, top + cell_h - 4), 190, 1)
        mask = cv2.imread(str(ROOT / entry["v37MaskImage"]), cv2.IMREAD_GRAYSCALE)
        if mask is None:
            raise RuntimeError(f"Unable to read mask: {entry['v37MaskImage']}")
        display = 255 - mask
        sheet[top + 10:top + 58, left + 51:left + 99] = display
        cv2.putText(sheet, entry["templateId"], (left + 10, top + 78), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 0, 1, cv2.LINE_AA)
        cv2.putText(sheet, f"m{entry['measure']} s{entry['stringHighEToLowE']}", (left + 10, top + 98), cv2.FONT_HERSHEY_SIMPLEX, 0.42, 0, 1, cv2.LINE_AA)
    CONTACT_DIR.mkdir(parents=True, exist_ok=True)
    path = CONTACT_DIR / f"fret-{fret}-targeted-mask-contact-sheet.png"
    cv2.imwrite(str(path), sheet)
    return path


def failure_ids(audit: dict[str, Any]) -> set[str]:
    failures = audit.get("implausibleMasks") or audit.get("failures") or []
    ids = {
        str(item.get("templateId"))
        for item in failures
        if isinstance(item, dict) and item.get("templateId")
    }
    if not ids:
        # Locked fallback matching the v36 terminal report.
        ids = {"fret-0-13", "fret-0-15", "fret-3-16"}
    return ids


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (SOURCE_PATH, AUDIT_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    targets = failure_ids(audit)
    if targets != {"fret-0-13", "fret-0-15", "fret-3-16"}:
        raise RuntimeError(f"Unexpected v36 target set: {sorted(targets)}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rebuilt: dict[str, list[dict[str, Any]]] = {}
    targeted_results: list[dict[str, Any]] = []

    print("Targeted implausible locked glyph mask rebuild v37 starting", flush=True)
    for fret in REQUIRED_FRETS:
        entries: list[dict[str, Any]] = []
        for entry in source.get("cleanMasks", {}).get(fret, []):
            template_id = str(entry["templateId"])
            source_image = ROOT / entry["cleanMaskImage"]
            mask = cv2.imread(str(source_image), cv2.IMREAD_GRAYSCALE)
            if mask is None:
                raise RuntimeError(f"Unable to read mask: {source_image.relative_to(ROOT)}")

            metadata = {
                "initialForegroundRatio": round(ratio(cv2, mask), 6),
                "finalForegroundRatio": round(ratio(cv2, mask), 6),
                "erosionIterations": 0,
                "plausibleForeground": MIN_RATIO <= ratio(cv2, mask) <= MAX_RATIO,
            }
            targeted = template_id in targets
            if targeted:
                mask, metadata = adaptive_reduce_dense_mask(cv2, mask)
                targeted_results.append({
                    "templateId": template_id,
                    "fret": fret,
                    "measure": entry.get("measure"),
                    "stringHighEToLowE": entry.get("stringHighEToLowE"),
                    **metadata,
                })
                print(
                    f"{template_id}: initial={metadata['initialForegroundRatio']:.6f}, "
                    f"final={metadata['finalForegroundRatio']:.6f}, "
                    f"erosions={metadata['erosionIterations']}, "
                    f"passed={metadata['plausibleForeground']}",
                    flush=True,
                )

            output_image = OUTPUT_DIR / f"{template_id}-v37-mask.png"
            cv2.imwrite(str(output_image), mask)
            entries.append({
                **entry,
                "v37MaskImage": str(output_image.relative_to(ROOT)),
                "v37TargetedRebuild": targeted,
                "v37MaskMetadata": metadata,
                "humanValidated": False,
            })
        rebuilt[fret] = entries

    all_entries = [entry for fret in REQUIRED_FRETS for entry in rebuilt[fret]]
    all_masks_built = len(all_entries) == 70 and all((ROOT / entry["v37MaskImage"]).exists() for entry in all_entries)
    all_plausible = all(bool(entry["v37MaskMetadata"]["plausibleForeground"]) for entry in all_entries)
    targeted_passed = len(targeted_results) == 3 and all(bool(item["plausibleForeground"]) for item in targeted_results)
    contact_sheets = {
        fret: str(build_contact_sheet(cv2, fret, rebuilt[fret]).relative_to(ROOT))
        for fret in REQUIRED_FRETS
    }

    output = {
        "diagnosticName": "Gomyway targeted implausible locked glyph mask rebuild v37",
        "referenceType": "locked-professional-targeted-glyph-mask-rebuild",
        "sourceMaskRebuild": str(SOURCE_PATH.relative_to(ROOT)),
        "sourceFailureAudit": str(AUDIT_PATH.relative_to(ROOT)),
        "targetTemplateIds": sorted(targets),
        "targetedResults": targeted_results,
        "rebuiltCountsByFret": {fret: len(rebuilt[fret]) for fret in REQUIRED_FRETS},
        "targetedMasksRebuilt": len(targeted_results),
        "targetedRebuildPassed": targeted_passed,
        "allMasksBuilt": all_masks_built,
        "allMasksHavePlausibleForeground": all_plausible,
        "contactSheets": contact_sheets,
        "masks": rebuilt,
        "humanVisualValidationComplete": False,
        "glyphMasksHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-three-v37-targeted-mask-contact-sheets"
            if targeted_passed and all_plausible
            else "inspect-v37-targeted-mask-residual-failures-v38"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Targeted implausible locked glyph mask rebuild v37 complete")
    print(f"Target template IDs: {sorted(targets)}")
    print(f"Targeted masks rebuilt: {len(targeted_results)}")
    print(f"Targeted rebuild passed: {targeted_passed}")
    print(f"All masks built: {all_masks_built}")
    print(f"All masks have plausible foreground: {all_plausible}")
    print("Human visual validation complete: False")
    print("Glyph masks human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Masks: {OUTPUT_DIR.relative_to(ROOT)}")
    print(f"Contact sheets: {CONTACT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
