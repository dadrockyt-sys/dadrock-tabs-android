import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V40 = PUBLIC / "gomyway-raw-digit-line-suppression-calibration-v40.json"
OUTPUT = PUBLIC / "gomyway-raw-row-coordinate-model-v41.json"


def flatten_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in data.get("rows", []):
        page_number = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        for measure_group in row.get("measureEventSlots", []):
            fallback_measure = int(measure_group.get("measure", 0))
            for slot in measure_group.get("eventSlots", []):
                item = dict(slot)
                item["pageNumber"] = page_number
                item["rowIndex"] = row_index
                item["measure"] = int(item.get("measure", fallback_measure))
                result.append(item)
    return result


def numeric(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_numeric(mapping: dict[str, Any], names: tuple[str, ...]) -> tuple[str | None, float | None]:
    for name in names:
        value = numeric(mapping.get(name))
        if value is not None:
            return name, value
    return None, None


def find_offset(mapping: dict[str, Any], axis: str) -> tuple[str | None, float | None]:
    if axis == "x":
        names = (
            "cropX", "cropLeft", "sourceX", "sourceLeft", "pageX", "left",
            "xOffset", "cropOffsetX", "sourceOffsetX", "pageOffsetX",
        )
    else:
        names = (
            "cropY", "cropTop", "sourceY", "sourceTop", "pageY", "top",
            "yOffset", "cropOffsetY", "sourceOffsetY", "pageOffsetY",
        )
    name, value = first_numeric(mapping, names)
    if value is not None:
        return name, value
    for container_name in ("cropBox", "sourceBox", "pageBox", "bounds", "bbox"):
        nested = mapping.get(container_name)
        if not isinstance(nested, dict):
            continue
        nested_names = ("x", "left", "x0") if axis == "x" else ("y", "top", "y0")
        nested_name, nested_value = first_numeric(nested, nested_names)
        if nested_value is not None:
            return f"{container_name}.{nested_name}", nested_value
    return None, None


def main() -> None:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (ASSIGNMENT, LOCALIZATION, V40):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    v40 = json.loads(V40.read_text(encoding="utf-8"))

    if int(v40.get("bestCandidateTotal", -1)) != 0:
        raise RuntimeError("V40 no longer reports zero candidates")
    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 contains component collisions")

    row_lookup = {
        (int(row.get("pageNumber", 0)), int(row.get("rowIndex", 0))): row
        for row in localization.get("rows", [])
    }
    locked = [
        slot for slot in flatten_slots(assignment)
        if 1 <= int(slot["measure"]) <= 16
        and str(int(slot["fret"])) in {"0", "2", "3"}
    ]
    if len(locked) != 144:
        raise RuntimeError(f"Expected 144 locked slots, found {len(locked)}")

    rows_report: list[dict[str, Any]] = []
    slot_report: list[dict[str, Any]] = []
    rows_missing = 0
    rows_unreadable = 0
    page_space_likely = 0
    crop_space_likely = 0
    offset_correctable = 0
    unresolved = 0
    offset_field_counts: Counter[str] = Counter()
    row_slot_counts: Counter[tuple[int, int]] = Counter()
    expected_ratios: list[float] = []
    corrected_ratios: list[float] = []

    for slot in locked:
        row_slot_counts[(int(slot["pageNumber"]), int(slot["rowIndex"]))] += 1

    print("Raw professional row coordinate model inspection v41 starting", flush=True)

    for key in sorted(row_slot_counts):
        row = row_lookup.get(key)
        if row is None:
            rows_missing += 1
            continue

        crop_path = row.get("sourceCrop")
        if not crop_path:
            rows_unreadable += 1
            continue
        image = cv2.imread(str(ROOT / str(crop_path)), cv2.IMREAD_GRAYSCALE)
        if image is None:
            rows_unreadable += 1
            continue

        height, width = image.shape[:2]
        x_name, x_offset = find_offset(row, "x")
        y_name, y_offset = find_offset(row, "y")
        if x_name:
            offset_field_counts[x_name] += 1
        if y_name:
            offset_field_counts[y_name] += 1

        row_slots = [
            slot for slot in locked
            if (int(slot["pageNumber"]), int(slot["rowIndex"])) == key
        ]
        expected_values = [float(slot.get("expectedX") or 0) for slot in row_slots]
        inside_raw = sum(0 <= value < width for value in expected_values)
        corrected_values = [
            value - x_offset if x_offset is not None else value
            for value in expected_values
        ]
        inside_corrected = sum(0 <= value < width for value in corrected_values)

        raw_ratio = inside_raw / len(row_slots) if row_slots else 0.0
        corrected_ratio = inside_corrected / len(row_slots) if row_slots else raw_ratio
        expected_ratios.append(raw_ratio)
        corrected_ratios.append(corrected_ratio)

        if raw_ratio >= 0.8:
            coordinate_class = "crop-space-likely"
            crop_space_likely += 1
        elif x_offset is not None and corrected_ratio >= 0.8 and corrected_ratio > raw_ratio:
            coordinate_class = "page-space-with-recorded-crop-offset"
            page_space_likely += 1
            offset_correctable += 1
        elif expected_values and median(expected_values) > width * 1.15:
            coordinate_class = "page-space-or-scaled-space-likely"
            page_space_likely += 1
        else:
            coordinate_class = "unresolved-coordinate-space"
            unresolved += 1

        rows_report.append({
            "pageNumber": key[0],
            "rowIndex": key[1],
            "sourceCrop": crop_path,
            "imageWidth": width,
            "imageHeight": height,
            "slotCount": len(row_slots),
            "expectedXMin": round(min(expected_values), 3) if expected_values else None,
            "expectedXMedian": round(float(median(expected_values)), 3) if expected_values else None,
            "expectedXMax": round(max(expected_values), 3) if expected_values else None,
            "rawExpectedXInsideCropCount": inside_raw,
            "rawExpectedXInsideCropRatio": round(raw_ratio, 6),
            "xOffsetField": x_name,
            "xOffsetValue": x_offset,
            "yOffsetField": y_name,
            "yOffsetValue": y_offset,
            "offsetCorrectedInsideCropCount": inside_corrected,
            "offsetCorrectedInsideCropRatio": round(corrected_ratio, 6),
            "coordinateClass": coordinate_class,
            "availableRowKeys": sorted(row.keys()),
        })

        print(
            f"Page {key[0]} row {key[1]}: width={width}, slots={len(row_slots)}, "
            f"expectedX={min(expected_values):.1f}-{max(expected_values):.1f}, "
            f"rawInside={inside_raw}/{len(row_slots)}, "
            f"xOffset={x_name}:{x_offset}, correctedInside={inside_corrected}/{len(row_slots)}, "
            f"class={coordinate_class}"
        )

        for slot, corrected_x in zip(row_slots, corrected_values):
            slot_report.append({
                "pageNumber": key[0],
                "rowIndex": key[1],
                "measure": int(slot["measure"]),
                "stringHighEToLowE": int(slot.get("normalizedStringHighEToLowE") or 0),
                "fret": int(slot["fret"]),
                "expectedX": round(float(slot.get("expectedX") or 0), 3),
                "rawExpectedXInsideCrop": 0 <= float(slot.get("expectedX") or 0) < width,
                "offsetCorrectedX": round(float(corrected_x), 3),
                "offsetCorrectedXInsideCrop": 0 <= corrected_x < width,
            })

    median_raw_inside = float(median(expected_ratios)) if expected_ratios else 0.0
    median_corrected_inside = float(median(corrected_ratios)) if corrected_ratios else 0.0
    coordinate_mismatch_confirmed = (
        len(rows_report) > 0
        and median_raw_inside < 0.25
        and (
            page_space_likely >= max(1, round(len(rows_report) * 0.6))
            or median_corrected_inside >= 0.75
        )
    )

    output = {
        "diagnosticName": "Gomyway raw professional row coordinate model inspection v41",
        "lockedEventSlotsObserved": len(locked),
        "localizedRowsInspected": len(rows_report),
        "rowsMissingFromLocalization": rows_missing,
        "rowsWithUnreadableCrops": rows_unreadable,
        "cropSpaceLikelyRows": crop_space_likely,
        "pageSpaceLikelyRows": page_space_likely,
        "offsetCorrectableRows": offset_correctable,
        "unresolvedCoordinateRows": unresolved,
        "medianRawExpectedXInsideCropRatio": round(median_raw_inside, 6),
        "medianOffsetCorrectedInsideCropRatio": round(median_corrected_inside, 6),
        "offsetFieldCounts": dict(offset_field_counts),
        "coordinateMismatchConfirmed": coordinate_mismatch_confirmed,
        "rows": rows_report,
        "slots": slot_report,
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "transform-locked-event-page-coordinates-to-row-crop-space-v42"
            if coordinate_mismatch_confirmed
            else "inspect-event-to-row-membership-and-string-y-model-v42"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Raw professional row coordinate model inspection v41 complete")
    print(f"Locked event slots observed: {len(locked)}")
    print(f"Localized rows inspected: {len(rows_report)}")
    print(f"Rows missing from localization: {rows_missing}")
    print(f"Rows with unreadable crops: {rows_unreadable}")
    print(f"Crop-space-likely rows: {crop_space_likely}")
    print(f"Page-space-likely rows: {page_space_likely}")
    print(f"Offset-correctable rows: {offset_correctable}")
    print(f"Unresolved coordinate rows: {unresolved}")
    print(f"Median raw expected-X inside-crop ratio: {median_raw_inside:.6f}")
    print(f"Median offset-corrected inside-crop ratio: {median_corrected_inside:.6f}")
    print(f"Coordinate mismatch confirmed: {coordinate_mismatch_confirmed}")
    print("Human visual validation complete: False")
    print("Glyph templates human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
