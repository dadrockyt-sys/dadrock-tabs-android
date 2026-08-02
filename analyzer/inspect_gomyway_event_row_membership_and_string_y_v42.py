import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSIGNMENT = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V41 = PUBLIC / "gomyway-raw-row-coordinate-model-v41.json"
OUTPUT = PUBLIC / "gomyway-event-row-membership-string-y-v42.json"
PREVIEW_DIR = PUBLIC / "gomyway-event-row-membership-string-y-v42"


def flatten_slots(data: dict[str, Any]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
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
                output.append(item)
    return output


def detect_line_groups(binary, minimum_ratio: float) -> list[int]:
    width = binary.shape[1]
    x0 = round(width * 0.04)
    x1 = round(width * 0.98)
    counts = binary[:, x0:x1].sum(axis=1) / 255
    threshold = max(12, (x1 - x0) * minimum_ratio)
    raw = [index for index, value in enumerate(counts) if value >= threshold]
    groups: list[list[int]] = []
    for value in raw:
        if groups and value - groups[-1][-1] <= 3:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(median(group)) for group in groups]


def choose_six_rows(binary) -> tuple[list[int], str, list[int]]:
    best: list[int] = []
    best_score = -1e30
    best_source = "none"
    best_all: list[int] = []
    width = binary.shape[1]
    x0 = round(width * 0.04)
    x1 = round(width * 0.98)
    row_strength = binary[:, x0:x1].sum(axis=1) / 255

    for ratio in (0.52, 0.42, 0.34, 0.27, 0.20, 0.14):
        rows = detect_line_groups(binary, ratio)
        for start in range(max(0, len(rows) - 5)):
            group = rows[start:start + 6]
            if len(group) != 6:
                continue
            gaps = [group[index + 1] - group[index] for index in range(5)]
            spacing = float(median(gaps))
            if not 4 <= spacing <= 36:
                continue
            irregularity = max(abs(gap - spacing) for gap in gaps)
            if irregularity > max(4, spacing * 0.42):
                continue
            strength = sum(float(row_strength[y]) for y in group)
            score = strength - irregularity * width * 0.4
            if score > best_score:
                best_score = score
                best = group
                best_source = f"ratio-{ratio:.2f}"
                best_all = rows
    return best, best_source, best_all


def local_ink(binary, x: float, y: float, spacing: float) -> float:
    half_width = max(3, round(spacing * 0.55))
    half_height = max(2, round(spacing * 0.55))
    x0 = max(0, round(x) - half_width)
    x1 = min(binary.shape[1], round(x) + half_width + 1)
    y0 = max(0, round(y) - half_height)
    y1 = min(binary.shape[0], round(y) + half_height + 1)
    if x1 <= x0 or y1 <= y0:
        return 0.0
    return float((binary[y0:y1, x0:x1] > 0).mean())


def main() -> None:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    for path in (ASSIGNMENT, LOCALIZATION, V41):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION.read_text(encoding="utf-8"))
    v41 = json.loads(V41.read_text(encoding="utf-8"))

    if bool(v41.get("coordinateMismatchConfirmed")):
        raise RuntimeError("V41 unexpectedly reports an X-coordinate mismatch")
    if float(v41.get("medianRawExpectedXInsideCropRatio", 0)) < 0.99:
        raise RuntimeError("V41 does not confirm crop-space expected X coordinates")
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

    slots_by_row: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for slot in locked:
        slots_by_row[(int(slot["pageNumber"]), int(slot["rowIndex"]))].append(slot)

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    row_reports: list[dict[str, Any]] = []
    slot_reports: list[dict[str, Any]] = []
    rows_with_six = 0
    rows_without_six = 0
    direct_wins = 0
    reversed_wins = 0
    ties = 0
    best_row_matches_expected = 0
    best_row_total = 0
    direction_margin_values: list[float] = []
    detected_spacing_values: list[float] = []
    source_counts: Counter[str] = Counter()

    print("Locked event row membership and string-Y inspection v42 starting", flush=True)

    for key in sorted(slots_by_row):
        row = row_lookup.get(key)
        if row is None:
            rows_without_six += 1
            continue
        source_crop = row.get("sourceCrop")
        gray = cv2.imread(str(ROOT / str(source_crop)), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            rows_without_six += 1
            continue

        binary = cv2.adaptiveThreshold(
            cv2.GaussianBlur(gray, (3, 3), 0),
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            8,
        )
        string_rows, detection_source, all_rows = choose_six_rows(binary)
        source_counts[detection_source] += 1
        row_slots = slots_by_row[key]

        if len(string_rows) != 6:
            rows_without_six += 1
            row_reports.append({
                "pageNumber": key[0],
                "rowIndex": key[1],
                "sourceCrop": source_crop,
                "slotCount": len(row_slots),
                "sixRowsDetected": False,
                "candidateHorizontalRows": all_rows,
                "detectionSource": detection_source,
            })
            print(
                f"Page {key[0]} row {key[1]}: sixRows=False, "
                f"candidates={len(all_rows)}, slots={len(row_slots)}"
            )
            continue

        rows_with_six += 1
        gaps = [string_rows[index + 1] - string_rows[index] for index in range(5)]
        spacing = float(median(gaps))
        detected_spacing_values.append(spacing)
        direct_score = 0.0
        reversed_score = 0.0
        row_preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        colors = [
            (0, 0, 255), (0, 128, 255), (0, 220, 220),
            (0, 200, 0), (255, 160, 0), (255, 0, 180),
        ]
        for index, y in enumerate(string_rows):
            cv2.line(row_preview, (0, y), (row_preview.shape[1] - 1, y), colors[index], 1)
            cv2.putText(
                row_preview,
                str(index + 1),
                (5, max(12, y - 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                colors[index],
                1,
                cv2.LINE_AA,
            )

        for slot in row_slots:
            string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
            expected_x = float(slot.get("expectedX") or 0)
            if not 1 <= string_number <= 6:
                continue
            direct_y = string_rows[string_number - 1]
            reversed_y = string_rows[6 - string_number]
            direct_ink = local_ink(binary, expected_x, direct_y, spacing)
            reversed_ink = local_ink(binary, expected_x, reversed_y, spacing)
            row_inks = [local_ink(binary, expected_x, y, spacing) for y in string_rows]
            best_index = max(range(6), key=lambda index: row_inks[index])
            expected_direct_index = string_number - 1
            expected_reversed_index = 6 - string_number
            direct_score += direct_ink
            reversed_score += reversed_ink
            best_row_total += 1
            if best_index == expected_direct_index:
                best_row_matches_expected += 1

            slot_reports.append({
                "pageNumber": key[0],
                "rowIndex": key[1],
                "measure": int(slot["measure"]),
                "stringHighEToLowE": string_number,
                "fret": int(slot["fret"]),
                "expectedX": round(expected_x, 3),
                "directY": direct_y,
                "reversedY": reversed_y,
                "directInkRatio": round(direct_ink, 6),
                "reversedInkRatio": round(reversed_ink, 6),
                "inkByDetectedRow": [round(value, 6) for value in row_inks],
                "bestDetectedRowHighEToLowE": best_index + 1,
                "bestDetectedRowMatchesDirectString": best_index == expected_direct_index,
                "bestDetectedRowMatchesReversedString": best_index == expected_reversed_index,
            })

            cv2.circle(row_preview, (round(expected_x), direct_y), 3, (255, 255, 255), -1)

        margin = direct_score - reversed_score
        direction_margin_values.append(margin)
        if margin > 0.01:
            preferred_direction = "high-E-to-low-E"
            direct_wins += 1
        elif margin < -0.01:
            preferred_direction = "low-E-to-high-E"
            reversed_wins += 1
        else:
            preferred_direction = "tie"
            ties += 1

        preview_name = f"page-{key[0]:02d}-row-{key[1]:02d}-string-y.png"
        cv2.imwrite(str(PREVIEW_DIR / preview_name), row_preview)
        row_reports.append({
            "pageNumber": key[0],
            "rowIndex": key[1],
            "sourceCrop": source_crop,
            "slotCount": len(row_slots),
            "sixRowsDetected": True,
            "stringRowsPixels": string_rows,
            "stringSpacingPixels": round(spacing, 3),
            "candidateHorizontalRows": all_rows,
            "detectionSource": detection_source,
            "directDirectionInkScore": round(direct_score, 6),
            "reversedDirectionInkScore": round(reversed_score, 6),
            "directionMargin": round(margin, 6),
            "preferredDirection": preferred_direction,
            "preview": str((PREVIEW_DIR / preview_name).relative_to(ROOT)),
        })
        print(
            f"Page {key[0]} row {key[1]}: sixRows=True, rows={string_rows}, "
            f"spacing={spacing:.1f}, direct={direct_score:.4f}, "
            f"reversed={reversed_score:.4f}, preferred={preferred_direction}"
        )

    direct_row_match_ratio = (
        best_row_matches_expected / best_row_total if best_row_total else 0.0
    )
    dominant_direction = (
        "high-E-to-low-E" if direct_wins > reversed_wins
        else "low-E-to-high-E" if reversed_wins > direct_wins
        else "ambiguous"
    )
    six_row_detection_passed = rows_with_six == len(slots_by_row)
    string_direction_supported = (
        dominant_direction != "ambiguous"
        and max(direct_wins, reversed_wins) >= max(1, round(len(slots_by_row) * 0.75))
    )
    direct_string_model_supported = (
        dominant_direction == "high-E-to-low-E"
        and direct_row_match_ratio >= 0.45
    )

    output = {
        "diagnosticName": "Gomyway locked event row membership and string-Y inspection v42",
        "lockedEventSlotsObserved": len(locked),
        "lockedRowsExpected": len(slots_by_row),
        "rowsWithSixStringsDetected": rows_with_six,
        "rowsWithoutSixStringsDetected": rows_without_six,
        "sixRowDetectionPassed": six_row_detection_passed,
        "directDirectionWins": direct_wins,
        "reversedDirectionWins": reversed_wins,
        "directionTies": ties,
        "dominantStringDirection": dominant_direction,
        "stringDirectionSupported": string_direction_supported,
        "bestInkRowMatchesDirectStringCount": best_row_matches_expected,
        "bestInkRowComparedSlots": best_row_total,
        "bestInkRowMatchesDirectStringRatio": round(direct_row_match_ratio, 6),
        "directStringModelSupported": direct_string_model_supported,
        "medianDetectedStringSpacingPixels": (
            round(float(median(detected_spacing_values)), 3)
            if detected_spacing_values else None
        ),
        "detectionSourceCounts": dict(source_counts),
        "rows": row_reports,
        "slots": slot_reports,
        "humanVisualValidationComplete": False,
        "glyphTemplatesHumanApproved": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "relocalize-locked-digits-with-validated-string-y-v43"
            if six_row_detection_passed and string_direction_supported
            else "build-row-specific-string-line-calibration-v43"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked event row membership and string-Y inspection v42 complete")
    print(f"Locked event slots observed: {len(locked)}")
    print(f"Locked rows expected: {len(slots_by_row)}")
    print(f"Rows with six strings detected: {rows_with_six}")
    print(f"Rows without six strings detected: {rows_without_six}")
    print(f"Six-row detection passed: {six_row_detection_passed}")
    print(f"Direct direction wins: {direct_wins}")
    print(f"Reversed direction wins: {reversed_wins}")
    print(f"Direction ties: {ties}")
    print(f"Dominant string direction: {dominant_direction}")
    print(f"String direction supported: {string_direction_supported}")
    print(f"Best-ink row matches direct string ratio: {direct_row_match_ratio:.6f}")
    print(f"Direct string model supported: {direct_string_model_supported}")
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
