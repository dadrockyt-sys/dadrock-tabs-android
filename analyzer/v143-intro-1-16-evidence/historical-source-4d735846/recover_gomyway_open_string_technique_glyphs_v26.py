import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
LOCALIZATION_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
INSPECTION_PATH = PUBLIC / "gomyway-unmatched-locked-glyph-slots-v25.json"
OUTPUT_PATH = PUBLIC / "gomyway-open-string-technique-glyph-recovery-v26.json"

EXPECTED_TARGET_MEASURES = [1, 2, 7, 8, 13, 14]
EXPECTED_TARGET_COUNT = 6


def component_key(page: int, row: int, component_index: int) -> tuple[int, int, int]:
    return page, row, component_index


def assigned_component(slot: dict[str, Any]) -> Any:
    for key in (
        "assignedComponentIndex",
        "sharedColumnAssignedComponentIndex",
        "nearestComponentIndex",
        "componentIndex",
    ):
        value = slot.get(key)
        if value is not None:
            return value
    return None


def normalized_string(slot: dict[str, Any]) -> Any:
    return slot.get("normalizedStringHighEToLowE", slot.get("stringHighEToLowE", slot.get("string")))


def source_measure_entries(row: dict[str, Any]) -> list[dict[str, Any]]:
    return row.get("measureEventSlots") or row.get("measuresOutput") or []


def source_event_slots(measure_entry: dict[str, Any]) -> list[dict[str, Any]]:
    return measure_entry.get("eventSlots") or measure_entry.get("slots") or []


def slot_matches_target(
    slot: dict[str, Any],
    target: dict[str, Any],
    page: int,
    row_index: int,
    measure: int,
) -> bool:
    if page != int(target.get("pageNumber", -1)):
        return False
    if row_index != int(target.get("rowIndex", -1)):
        return False
    if measure != int(target.get("measure", -1)):
        return False
    if str(normalized_string(slot)) != str(target.get("stringHighEToLowE")):
        return False
    if str(slot.get("fret")) != str(target.get("fret")):
        return False

    source_x = slot.get("expectedX")
    target_x = target.get("expectedX")
    if source_x is not None and target_x is not None:
        if abs(float(source_x) - float(target_x)) > 1.0:
            return False
    return True


def main() -> None:
    for path in (LOCALIZATION_PATH, INSPECTION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    localization = json.loads(LOCALIZATION_PATH.read_text(encoding="utf-8"))
    inspection = json.loads(INSPECTION_PATH.read_text(encoding="utf-8"))

    if int(inspection.get("eventSlotsObserved", 0)) != 144:
        raise RuntimeError("V25 does not describe 144 locked event slots")
    if int(inspection.get("unmatchedEventSlots", -1)) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("V25 did not isolate exactly six unmatched locked events")

    assignment_relative = inspection.get("input")
    if not isinstance(assignment_relative, str) or not assignment_relative:
        raise RuntimeError("V25 did not record its assignment input")
    assignment_path = ROOT / assignment_relative
    if not assignment_path.exists():
        raise RuntimeError(f"Missing V25 assignment source: {assignment_path.relative_to(ROOT)}")
    assignment = json.loads(assignment_path.read_text(encoding="utf-8"))

    target_specs: list[dict[str, Any]] = []
    unmatched_by_measure = inspection.get("unmatchedByMeasure", {})
    for measure_key, items in unmatched_by_measure.items():
        if not isinstance(items, list):
            continue
        for item in items:
            copied = dict(item)
            copied["measure"] = int(copied.get("measure", measure_key))
            target_specs.append(copied)

    target_measures = sorted(int(item["measure"]) for item in target_specs)
    if len(target_specs) != EXPECTED_TARGET_COUNT:
        raise RuntimeError(f"Expected six V25 target specs, found {len(target_specs)}")
    if target_measures != EXPECTED_TARGET_MEASURES:
        raise RuntimeError(f"Unexpected V25 target measures: {target_measures}")

    localization_rows = {
        (int(row["pageNumber"]), int(row["rowIndex"])): row
        for row in localization.get("rows", [])
    }

    used_components: set[tuple[int, int, int]] = set()
    targets: list[dict[str, Any]] = []
    matched_target_indexes: set[int] = set()

    for row in assignment.get("rows", []):
        page = int(row.get("pageNumber", 0))
        row_index = int(row.get("rowIndex", 0))
        for measure_entry in source_measure_entries(row):
            measure = int(measure_entry.get("measure", 0))
            x0, x1 = [float(value) for value in measure_entry.get("xRangePixels", [0, 0])]
            for slot in source_event_slots(measure_entry):
                assigned = assigned_component(slot)
                if assigned is not None:
                    used_components.add(component_key(page, row_index, int(assigned)))

                for target_index, target in enumerate(target_specs):
                    if target_index in matched_target_indexes:
                        continue
                    if slot_matches_target(slot, target, page, row_index, measure):
                        targets.append({
                            "pageNumber": page,
                            "rowIndex": row_index,
                            "measure": measure,
                            "xRangePixels": [x0, x1],
                            "slot": {
                                **slot,
                                "normalizedStringHighEToLowE": normalized_string(slot),
                                "fret": target.get("fret", slot.get("fret")),
                                "time": target.get("time", slot.get("time")),
                                "technique": target.get("technique") or slot.get("technique") or {},
                                "expectedX": target.get("expectedX", slot.get("expectedX")),
                            },
                        })
                        matched_target_indexes.add(target_index)
                        break

    if len(targets) != EXPECTED_TARGET_COUNT:
        raise RuntimeError(
            f"Expected six V25-filtered assignment slots, found {len(targets)}"
        )

    # The six targets are unmatched in the V25 assignment source. Be defensive if a
    # source schema exposes an obsolete component key on one of them.
    for target in targets:
        slot = target["slot"]
        assigned = assigned_component(slot)
        if assigned is not None:
            used_components.discard(
                component_key(target["pageNumber"], target["rowIndex"], int(assigned))
            )

    recovered = []
    unresolved = []
    newly_used: set[tuple[int, int, int]] = set()

    print("Targeted open-string technique glyph recovery v26 starting", flush=True)
    print(f"Assignment source: {assignment_path.relative_to(ROOT)}", flush=True)

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
            spill = measure_width * 0.12
            if not x0 - spill <= center_x <= x1 + spill:
                continue
            distance = abs(center_x - expected_x)
            width = float(component.get("width", 0))
            height = float(component.get("height", 0))
            area = float(component.get("area", 0))
            if width <= 0 or height <= 0 or area <= 0:
                continue
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

    collision_count = 0
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
        "sourceAssignment": str(assignment_path.relative_to(ROOT)),
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
