import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V42 = PUBLIC / "gomyway-event-row-membership-string-y-v42.json"
OUTPUT = PUBLIC / "gomyway-row-specific-string-line-calibration-v43.json"
PREVIEW_DIR = PUBLIC / "gomyway-row-specific-string-line-calibration-v43"


def flatten_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in data.get("rows", []):
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        for measure_group in row.get("measureEventSlots", []):
            fallback_measure = int(measure_group.get("measure", 0))
            for slot in measure_group.get("eventSlots", []):
                item = dict(slot)
                item["pageNumber"] = page
                item["rowIndex"] = row_index
                item["measure"] = int(item.get("measure", fallback_measure))
                result.append(item)
    return result


def darkness_integral(gray):
    import cv2
    darkness = 255.0 - cv2.GaussianBlur(gray, (3, 3), 0).astype("float32")
    return cv2.integral(darkness)


def rect_mean(integral, x0: int, y0: int, x1: int, y1: int) -> float:
    h = integral.shape[0] - 1
    w = integral.shape[1] - 1
    x0 = max(0, min(w, x0)); x1 = max(0, min(w, x1))
    y0 = max(0, min(h, y0)); y1 = max(0, min(h, y1))
    if x1 <= x0 or y1 <= y0:
        return 0.0
    total = integral[y1, x1] - integral[y0, x1] - integral[y1, x0] + integral[y0, x0]
    return float(total) / float((x1 - x0) * (y1 - y0))


def local_darkness(integral, x: float, y: float, spacing: float) -> float:
    hw = max(4, round(spacing * 0.62))
    hh = max(2, round(spacing * 0.42))
    return rect_mean(integral, round(x) - hw, round(y) - hh, round(x) + hw + 1, round(y) + hh + 1)


def line_darkness(integral, y: float, width: int, spacing: float) -> float:
    hh = max(1, round(spacing * 0.12))
    return rect_mean(integral, round(width * 0.05), round(y) - hh, round(width * 0.98), round(y) + hh + 1)


def candidate_score(integral, width: int, slots: list[dict[str, Any]], top: float, spacing: float, reversed_order: bool) -> tuple[float, float, float]:
    rows = [top + index * spacing for index in range(6)]
    target_values: list[float] = []
    rival_values: list[float] = []
    for slot in slots:
        string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
        if not 1 <= string_number <= 6:
            continue
        index = 6 - string_number if reversed_order else string_number - 1
        x = float(slot.get("expectedX") or 0)
        target = local_darkness(integral, x, rows[index], spacing)
        alternatives = [local_darkness(integral, x, y, spacing) for i, y in enumerate(rows) if i != index]
        target_values.append(target)
        rival_values.append(max(alternatives) if alternatives else 0.0)
    if not target_values:
        return -1e9, 0.0, 0.0
    target_mean = sum(target_values) / len(target_values)
    rival_mean = sum(rival_values) / len(rival_values)
    continuity = sum(line_darkness(integral, y, width, spacing) for y in rows) / 6.0
    separation = target_mean - rival_mean
    score = target_mean + continuity * 0.35 + separation * 1.25
    return score, target_mean, separation


def main() -> None:
    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    for path in (ASSIGNMENT, LOCALIZATION, V42):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    v42 = json.loads(V42.read_text(encoding="utf-8"))
    if int(v42.get("lockedEventSlotsObserved", -1)) != 144:
        raise RuntimeError("V42 did not inspect 144 locked slots")
    if int(assignment.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 contains component collisions")

    row_lookup = {
        (int(row.get("pageNumber", 0)), int(row.get("rowIndex", 0))): row
        for row in localization.get("rows", [])
    }
    locked = [
        slot for slot in flatten_slots(assignment)
        if 1 <= int(slot["measure"]) <= 16 and str(int(slot["fret"])) in {"0", "2", "3"}
    ]
    if len(locked) != 144:
        raise RuntimeError(f"Expected 144 locked slots, found {len(locked)}")

    slots_by_row: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for slot in locked:
        slots_by_row[(int(slot["pageNumber"]), int(slot["rowIndex"]))].append(slot)

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    reports: list[dict[str, Any]] = []
    passed_rows = 0
    direct_rows = 0
    reversed_rows = 0
    separation_values: list[float] = []

    print("Row-specific supervised string-line calibration v43 starting", flush=True)
    for key in sorted(slots_by_row):
        row = row_lookup.get(key)
        if row is None:
            raise RuntimeError(f"Missing localization row {key}")
        source_crop = row.get("sourceCrop")
        gray = cv2.imread(str(ROOT / str(source_crop)), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unreadable crop: {source_crop}")
        h, w = gray.shape[:2]
        integral = darkness_integral(gray)
        row_slots = slots_by_row[key]

        best: dict[str, Any] | None = None
        spacing_min = max(5, round(h * 0.018))
        spacing_max = min(36, max(spacing_min + 1, round(h * 0.075)))
        for spacing_i in range(spacing_min * 2, spacing_max * 2 + 1):
            spacing = spacing_i / 2.0
            top_min = max(2, round(h * 0.05))
            top_max = min(h - 3, round(h * 0.88) - round(5 * spacing))
            for top_i in range(top_min * 2, top_max * 2 + 1):
                top = top_i / 2.0
                for reversed_order in (False, True):
                    score, target_mean, separation = candidate_score(
                        integral, w, row_slots, top, spacing, reversed_order
                    )
                    current = {
                        "score": score,
                        "top": top,
                        "spacing": spacing,
                        "reversed": reversed_order,
                        "targetMean": target_mean,
                        "separation": separation,
                    }
                    if best is None or current["score"] > best["score"]:
                        best = current
        if best is None:
            raise RuntimeError(f"No calibration candidate for row {key}")

        rows = [best["top"] + index * best["spacing"] for index in range(6)]
        calibration_passed = (
            best["targetMean"] >= 12.0
            and best["separation"] >= -2.5
            and rows[-1] < h
        )
        if calibration_passed:
            passed_rows += 1
        if best["reversed"]:
            reversed_rows += 1
            direction = "low-E-to-high-E"
        else:
            direct_rows += 1
            direction = "high-E-to-low-E"
        separation_values.append(float(best["separation"]))

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for index, y in enumerate(rows):
            cv2.line(preview, (0, round(y)), (w - 1, round(y)), (0, 255, 255), 1)
            label = str(6 - index if best["reversed"] else index + 1)
            cv2.putText(preview, label, (5, max(12, round(y) - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1, cv2.LINE_AA)
        for slot in row_slots:
            string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
            index = 6 - string_number if best["reversed"] else string_number - 1
            cv2.circle(preview, (round(float(slot.get("expectedX") or 0)), round(rows[index])), 3, (0, 0, 255), -1)
        preview_name = f"page-{key[0]:02d}-row-{key[1]:02d}-calibrated.png"
        cv2.imwrite(str(PREVIEW_DIR / preview_name), preview)

        reports.append({
            "pageNumber": key[0],
            "rowIndex": key[1],
            "sourceCrop": source_crop,
            "slotCount": len(row_slots),
            "imageWidth": w,
            "imageHeight": h,
            "topStringY": round(best["top"], 3),
            "stringSpacingPixels": round(best["spacing"], 3),
            "stringRowsPixels": [round(value, 3) for value in rows],
            "preferredDirection": direction,
            "score": round(best["score"], 6),
            "targetDarknessMean": round(best["targetMean"], 6),
            "targetVsRivalSeparation": round(best["separation"], 6),
            "calibrationPassed": calibration_passed,
            "preview": str((PREVIEW_DIR / preview_name).relative_to(ROOT)),
        })
        print(
            f"Page {key[0]} row {key[1]}: top={best['top']:.1f}, spacing={best['spacing']:.1f}, "
            f"direction={direction}, darkness={best['targetMean']:.2f}, separation={best['separation']:.2f}, "
            f"passed={calibration_passed}"
        )

    dominant_direction = (
        "high-E-to-low-E" if direct_rows > reversed_rows
        else "low-E-to-high-E" if reversed_rows > direct_rows
        else "ambiguous"
    )
    all_rows_calibrated = passed_rows == len(slots_by_row)
    direction_consistent = max(direct_rows, reversed_rows) >= 7
    median_separation = float(median(separation_values)) if separation_values else 0.0
    calibration_passed = all_rows_calibrated and direction_consistent

    output = {
        "diagnosticName": "Gomyway row-specific supervised string-line calibration v43",
        "lockedEventSlotsObserved": len(locked),
        "lockedRowsExpected": len(slots_by_row),
        "rowsCalibrated": len(reports),
        "rowsPassingCalibration": passed_rows,
        "allRowsCalibrated": all_rows_calibrated,
        "directDirectionRows": direct_rows,
        "reversedDirectionRows": reversed_rows,
        "dominantStringDirection": dominant_direction,
        "directionConsistent": direction_consistent,
        "medianTargetVsRivalSeparation": round(median_separation, 6),
        "rowSpecificCalibrationPassed": calibration_passed,
        "rows": reports,
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "human-review-eight-v43-calibrated-row-previews"
            if calibration_passed
            else "inspect-v43-row-specific-calibration-outliers-v44"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Row-specific supervised string-line calibration v43 complete")
    print(f"Locked event slots observed: {len(locked)}")
    print(f"Locked rows expected: {len(slots_by_row)}")
    print(f"Rows calibrated: {len(reports)}")
    print(f"Rows passing calibration: {passed_rows}")
    print(f"All rows calibrated: {all_rows_calibrated}")
    print(f"Direct direction rows: {direct_rows}")
    print(f"Reversed direction rows: {reversed_rows}")
    print(f"Dominant string direction: {dominant_direction}")
    print(f"Direction consistent: {direction_consistent}")
    print(f"Median target-vs-rival separation: {median_separation:.6f}")
    print(f"Row-specific calibration passed: {calibration_passed}")
    print("Human visual validation complete: False")
    print("Glyph templates human approved: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
