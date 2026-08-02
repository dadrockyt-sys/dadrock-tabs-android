import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
REASSIGNMENT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
INSPECTION_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
OUTPUT_PATH = PUBLIC / "gomyway-open-string-technique-glyph-recovery-v26.json"

EXPECTED_TARGET_MEASURES = [1, 2, 7, 8, 13, 14]
EXPECTED_TARGET_COUNT = 6


def component_key(page: int, row: int, component_index: int) -> tuple[int, int, int]:
    return page, row, component_index


def main() -> None:
    for path in (REASSIGNMENT_PATH, LOCALIZATION_PATH, INSPECTION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    reassignment = json.loads(REASSIGNMENT_PATH.read_text(encoding="utf-8"))
    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    inspection = json.loads(INSPECTION_PATH.read_text(encoding="utf-8"))

    if int(reassignment.get("eventSlotsObserved", 0)) != 144:
        raise RuntimeError("V23 does not contain 144 locked event slots")
    if int(inspection.get("unmatchedEventSlots", -1)) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("V25 did not isolate exactly six unmatched locked events")

    localization_rows = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }

    used_components: set[tuple[int, int, int]] = set()
    targets: list[dict[str, Any]] = []

    for row in reassignment.get("rows", []):
        page = int(row["pageNumber"])
        row_index = int(row["rowIndex"])
        for measure_entry in row.get("measureEventSlots", []):
            x0, x1 = [float(value) for value in measure_entry.get("xRangePixels", [0, 0])]
            for slot in measure_entry.get("eventSlots", []):
                assigned = slot.get("assignedComponentIndex")
                if assigned is not None:
                    used_components.add(component_key(page, row_index, int(assigned)))
                    continue
                targets.append({
                    "pageNumber": page,
                    "rowIndex": row_index,
                    "measure": int(slot["measure"]),
                    "xRangePixels": [x0, x1],
                    "slot": slot,
                })

    target_measures = sorted(int(item["measure"]) for item in targets)
    if len(targets) != EXPECTED_TARGET_COUNT:
        raise RuntimeError(f"Expected six unmatched v23 slots, found {len(targets)}")
    if target_measures != EXPECTED_TARGET_MEASURES:
        raise RuntimeError(f"Unexpected unmatched measures: {target_measures}")

    recovered = []
    unresolved = []
    newly_used: set[tuple[int, int, int]] = set()

    print("Targeted open-string technique glyph recovery v26 starting", flush=True)

    for target in targets:
        page = target["pageNumber"]
        row_index = target["rowIndex"]
        measure = target["measure"]
        slot = target["slot"]
        string_number = int(slot.get("normalizedStringHighEToLowE") or -1)
        fret = str(slot.get("fret"))
        expected_x = float(slot.get("expectedX") or 0)
        x0, x1 = target["xRangePixels"]
        measure_width = max(1.0, x1 - x0)

        if fret != "0" or string_number != 6 or not (slot.get("technique") or {}):
            raise RuntimeError(
                f"Target m{measure} is not the expected fret-0/string-6 technique event"
            )

        source_row = localization_rows.get((page, row_index))
        if source_row is None:
            raise RuntimeError(f"Missing v21 row for page {page} row {row_index}")

        candidates = []
        for component in source_row.get("compactStringLocalComponents", []):
            component_index = int(component["componentIndex"])
            key = component_key(page, row_index, component_index)
            if key in used_components or key in newly_used:
                continue
            if int(component.get("stringHighEToLowE", -1)) != string_number:
                continue
            center_x = float(component.get("centerX", -9999))
            # Permit a small spill outside the nominal measure because bend curves and
            # open-string zeros can be segmented near the barline.
            spill = measure_width * 0.12
            if not x0 - spill <= center_x <= x1 + spill:
                continue
            distance = abs(center_x - expected_x)
            width = float(component.get("width", 0))
            height = float(component.get("height", 0))
            area = float(component.get("area", 0))
            if width <= 0 or height <= 0 or area <= 0:
                continue
            # Relax geometry only for these six known technique-connected zeros.
            geometry_penalty = 0.0
            if width > 42:
                geometry_penalty += (width - 42) * 1.5
            if height > 46:
                geometry_penalty += (height - 46) * 1.5
            score = distance + geometry_penalty
            candidates.append((score, distance, component))

        candidates.sort(key=lambda item: (item[0], item[1], int(item[2]["componentIndex"])))
        best = candidates[0] if candidates else None
        maximum_distance = max(24.0, measure_width * 0.16)

        if best is not None and best[1] <= maximum_distance:
            _, distance, component = best
            component_index = int(component["componentIndex"])
            key = component_key(page, row_index, component_index)
            newly_used.add(key)
            recovered.append({
                "pageNumber": page,
                "rowIndex": row_index,
                "measure": measure,
                "stringHighEToLowE": string_number,
                "fret": slot.get("fret"),
                "time": slot.get("time"),
                "technique": slot.get("technique") or {},
                "expectedX": round(expected_x, 2),
                "recoveredComponentIndex": component_index,
                "componentCenterX": component.get("centerX"),
                "componentBoundsPixels": {
                    "x": component.get("x"),
                    "y": component.get("y"),
                    "width": component.get("width"),
                    "height": component.get("height"),
                    "area": component.get("area"),
                },
                "distancePixels": round(float(distance), 2),
                "maximumAllowedDistancePixels": round(maximum_distance, 2),
                "recoveryReason": "unused same-string component near technique-connected open-string event",
                "automaticRecoveryHypothesis": True,
                "humanVerified": False,
            })
            print(
                f"Recovered m{measure}: component={component_index}, distance={distance:.2f}px",
                flush=True,
            )
        else:
            unresolved.append({
                "pageNumber": page,
                "rowIndex": row_index,
                "measure": measure,
                "stringHighEToLowE": string_number,
                "fret": slot.get("fret"),
                "time": slot.get("time"),
                "technique": slot.get("technique") or {},
                "expectedX": round(expected_x, 2),
                "nearestUnusedCandidateDistancePixels": round(float(best[1]), 2) if best else None,
                "maximumAllowedDistancePixels": round(maximum_distance, 2),
            })
            print(f"Unresolved m{measure}", flush=True)

    collision_count = len(newly_used) - len(set(newly_used))
    recovered_measures = sorted(int(item["measure"]) for item in recovered)
    targeted_recovery_passed = (
        len(recovered) == EXPECTED_TARGET_COUNT
        and not unresolved
        and recovered_measures == EXPECTED_TARGET_MEASURES
        and collision_count == 0
    )

    output = {
        "diagnosticName": "Gomyway targeted open-string technique glyph recovery v26",
        "referenceType": "locked-professional-open-string-technique-glyph-recovery-hypotheses",
        "sourceReassignment": str(REASSIGNMENT_PATH.relative_to(ROOT)),
        "sourceLocalization": str(LOCALIZATION_PATH.relative_to(ROOT)),
        "sourceInspection": str(INSPECTION_PATH.relative_to(ROOT)),
        "targetEventSlots": len(targets),
        "targetMeasures": target_measures,
        "targetFretCounts": dict(Counter(str(item["slot"].get("fret")) for item in targets)),
        "targetStringCounts": dict(Counter(str(item["slot"].get("normalizedStringHighEToLowE")) for item in targets)),
        "recoveredEventSlots": len(recovered),
        "unresolvedEventSlots": len(unresolved),
        "componentCollisionSlots": collision_count,
        "recovered": recovered,
        "unresolved": unresolved,
        "targetedRecoveryPassed": targeted_recovery_passed,
        "humanValidationRequired": True,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "visual-validate-six-recovered-open-string-glyphs-v27"
            if targeted_recovery_passed
            else "inspect-unresolved-open-string-glyphs-v27"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Targeted open-string technique glyph recovery v26 complete")
    print(f"Target event slots: {len(targets)}")
    print(f"Recovered event slots: {len(recovered)}")
    print(f"Unresolved event slots: {len(unresolved)}")
    print(f"Component collision slots: {collision_count}")
    print(f"Targeted recovery passed: {targeted_recovery_passed}")
    print("Human validation required: True")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
