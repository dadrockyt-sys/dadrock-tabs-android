import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
VALIDATION_PATH = PUBLIC / "gomyway-locked-event-glyph-validation-v22.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"


def assignment_cost(slot: dict[str, Any], component: dict[str, Any], measure_width: float) -> float:
    expected_x = float(slot["expectedX"])
    distance = abs(float(component["centerX"]) - expected_x)
    width = float(component.get("width", 0))
    height = float(component.get("height", 0))
    area = float(component.get("area", 0))

    geometry_penalty = 0.0
    if width <= 0 or height <= 0 or area <= 0:
        geometry_penalty += measure_width
    if width > 28:
        geometry_penalty += (width - 28) * 2.0
    if height > 32:
        geometry_penalty += (height - 32) * 2.0
    return distance + geometry_penalty


def monotonic_assign(
    slots: list[dict[str, Any]],
    components: list[dict[str, Any]],
    measure_width: float,
) -> list[dict[str, Any]]:
    if not slots:
        return []
    slots = sorted(slots, key=lambda item: float(item["expectedX"]))
    components = sorted(components, key=lambda item: float(item["centerX"]))

    n = len(slots)
    m = len(components)
    unmatched_penalty = max(30.0, measure_width * 0.18)
    inf = float("inf")
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    choice: list[list[tuple[str, int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]

    for j in range(m + 1):
        dp[0][j] = 0.0
        if j:
            choice[0][j] = ("skip_component", 0, j - 1)
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + unmatched_penalty
        choice[i][0] = ("unmatched_slot", i - 1, 0)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            options = [
                (dp[i][j - 1], "skip_component", i, j - 1),
                (dp[i - 1][j] + unmatched_penalty, "unmatched_slot", i - 1, j),
                (
                    dp[i - 1][j - 1] + assignment_cost(slots[i - 1], components[j - 1], measure_width),
                    "match",
                    i - 1,
                    j - 1,
                ),
            ]
            value, action, pi, pj = min(options, key=lambda item: item[0])
            dp[i][j] = value
            choice[i][j] = (action, pi, pj)

    assignments: list[dict[str, Any]] = []
    i, j = n, m
    while i > 0 or j > 0:
        action_data = choice[i][j]
        if action_data is None:
            break
        action, pi, pj = action_data
        if action == "match":
            slot = slots[i - 1]
            component = components[j - 1]
            distance = abs(float(component["centerX"]) - float(slot["expectedX"]))
            assignments.append(
                {
                    **slot,
                    "assignedComponentIndex": component["componentIndex"],
                    "assignedCenterX": component["centerX"],
                    "assignedWidth": component.get("width"),
                    "assignedHeight": component.get("height"),
                    "assignedArea": component.get("area"),
                    "distancePixels": round(distance, 2),
                    "oneToOneAssignment": True,
                }
            )
        elif action == "unmatched_slot":
            slot = slots[i - 1]
            assignments.append(
                {
                    **slot,
                    "assignedComponentIndex": None,
                    "distancePixels": None,
                    "oneToOneAssignment": True,
                }
            )
        i, j = pi, pj

    assignments.reverse()
    return assignments


def main() -> None:
    for path in (INPUT_PATH, VALIDATION_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    if int(source.get("eventLocalizationSlots", 0)) != 144:
        raise RuntimeError("V21 does not contain 144 event slots")
    if int(validation.get("lockedEventSlotsObserved", 0)) != 144:
        raise RuntimeError("V22 did not observe all 144 event slots")
    if not validation.get("all144EventSlotsPresent", False):
        raise RuntimeError("V22 did not confirm all 144 event slots were present")

    rows_output = []
    total_slots = 0
    matched_slots = 0
    strict_slots = 0
    collision_slots = 0
    used_global: set[tuple[int, int, int]] = set()

    print("Locked event one-to-one glyph reassignment v23 starting", flush=True)

    for row in source["rows"]:
        components = row.get("compactStringLocalComponents", [])
        row_measures = []
        row_slot_count = 0
        row_matched = 0
        row_strict = 0

        for measure_entry in row.get("measureEventSlots", []):
            measure = int(measure_entry["measure"])
            x0, x1 = [float(value) for value in measure_entry["xRangePixels"]]
            measure_width = max(1.0, x1 - x0)
            measure_components = [
                component
                for component in components
                if x0 <= float(component["centerX"]) < x1
            ]

            slots_by_string: dict[int, list[dict[str, Any]]] = defaultdict(list)
            for slot in measure_entry.get("eventSlots", []):
                string_number = slot.get("normalizedStringHighEToLowE")
                if isinstance(string_number, int):
                    slots_by_string[string_number].append(slot)
                else:
                    slots_by_string[0].append(slot)

            reassigned_slots = []
            for string_number, slots in sorted(slots_by_string.items()):
                candidates = [
                    component
                    for component in measure_components
                    if int(component.get("stringHighEToLowE", -1)) == string_number
                ]
                reassigned_slots.extend(monotonic_assign(slots, candidates, measure_width))

            reassigned_slots.sort(
                key=lambda item: (
                    int(item.get("normalizedStringHighEToLowE") or 0),
                    float(item.get("expectedX") or 0),
                )
            )

            for slot in reassigned_slots:
                total_slots += 1
                row_slot_count += 1
                component_index = slot.get("assignedComponentIndex")
                if component_index is not None:
                    matched_slots += 1
                    row_matched += 1
                    key = (int(row["pageNumber"]), int(row["rowIndex"]), int(component_index))
                    if key in used_global:
                        collision_slots += 1
                    used_global.add(key)
                    distance = float(slot.get("distancePixels") or 9999)
                    width = float(slot.get("assignedWidth") or 9999)
                    height = float(slot.get("assignedHeight") or 9999)
                    strict = distance <= max(18.0, measure_width * 0.10) and width <= 28 and height <= 32
                    slot["strictCandidate"] = strict
                    if strict:
                        strict_slots += 1
                        row_strict += 1
                else:
                    slot["strictCandidate"] = False

            row_measures.append(
                {
                    "measure": measure,
                    "xRangePixels": [x0, x1],
                    "eventSlots": reassigned_slots,
                }
            )

        rows_output.append(
            {
                "pageNumber": row["pageNumber"],
                "rowIndex": row["rowIndex"],
                "measures": row["measures"],
                "measureEventSlots": row_measures,
                "slotCount": row_slot_count,
                "matchedSlots": row_matched,
                "strictSlots": row_strict,
            }
        )
        print(
            f"Page {row['pageNumber']} row {row['rowIndex']}: "
            f"slots={row_slot_count}, matched={row_matched}, strict={row_strict}",
            flush=True,
        )

    matched_ratio = matched_slots / total_slots if total_slots else 0.0
    strict_ratio = strict_slots / total_slots if total_slots else 0.0
    reassignment_passed = (
        total_slots == 144
        and matched_slots >= 136
        and collision_slots == 0
        and strict_slots >= 72
    )

    output = {
        "diagnosticName": "Gomyway locked event one-to-one glyph reassignment v23",
        "referenceType": "locked-professional-event-glyph-bipartite-reassignment",
        "sourceLocalization": str(INPUT_PATH.relative_to(ROOT)),
        "sourceValidation": str(VALIDATION_PATH.relative_to(ROOT)),
        "eventSlotsObserved": total_slots,
        "matchedEventSlots": matched_slots,
        "matchedRatio": round(matched_ratio, 6),
        "strictAutomaticCandidates": strict_slots,
        "strictCandidateRatio": round(strict_ratio, 6),
        "componentCollisionSlots": collision_slots,
        "oneToOneReassignmentPassed": reassignment_passed,
        "rows": rows_output,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-reviewed-locked-glyph-template-library-v24"
            if reassignment_passed
            else "improve-measure-and-time-position-model-v24"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked event one-to-one glyph reassignment v23 complete")
    print(f"Event slots observed: {total_slots}")
    print(f"Matched event slots: {matched_slots}")
    print(f"Matched ratio: {matched_ratio:.6f}")
    print(f"Strict automatic candidates: {strict_slots}")
    print(f"Strict candidate ratio: {strict_ratio:.6f}")
    print(f"Component collision slots: {collision_slots}")
    print(f"One-to-one reassignment passed: {reassignment_passed}")
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
