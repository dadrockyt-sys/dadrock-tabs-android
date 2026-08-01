import json
from collections import defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
V23_PATH = PUBLIC / "gomyway-locked-event-glyph-reassignment-v23.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-measure-time-model-v24.json"


def cluster_x(values: list[float], tolerance: float) -> list[float]:
    if not values:
        return []
    groups: list[list[float]] = [[sorted(values)[0]]]
    for value in sorted(values)[1:]:
        center = float(median(groups[-1]))
        if abs(value - center) <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [round(float(median(group)), 2) for group in groups]


def time_key(slot: dict[str, Any]) -> str:
    value = slot.get("time")
    if value is None:
        return f"fallback:{round(float(slot.get('expectedX') or 0), 2)}"
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def monotonic_column_map(expected: list[float], detected: list[float], width: float) -> list[float | None]:
    n, m = len(expected), len(detected)
    if n == 0:
        return []
    unmatched = max(24.0, width * 0.12)
    inf = float("inf")
    dp = [[inf] * (m + 1) for _ in range(n + 1)]
    choice: list[list[tuple[str, int, int] | None]] = [[None] * (m + 1) for _ in range(n + 1)]
    for j in range(m + 1):
        dp[0][j] = 0.0
        if j:
            choice[0][j] = ("skip", 0, j - 1)
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + unmatched
        choice[i][0] = ("miss", i - 1, 0)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            options = [
                (dp[i][j - 1], "skip", i, j - 1),
                (dp[i - 1][j] + unmatched, "miss", i - 1, j),
                (dp[i - 1][j - 1] + abs(expected[i - 1] - detected[j - 1]), "match", i - 1, j - 1),
            ]
            value, action, pi, pj = min(options, key=lambda item: item[0])
            dp[i][j] = value
            choice[i][j] = (action, pi, pj)
    result: list[float | None] = [None] * n
    i, j = n, m
    while i > 0 or j > 0:
        action_data = choice[i][j]
        if action_data is None:
            break
        action, pi, pj = action_data
        if action == "match":
            result[i - 1] = detected[j - 1]
        i, j = pi, pj
    return result


def main() -> None:
    for path in (SOURCE_PATH, V23_PATH):
        if not path.exists():
            raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")

    source = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    v23 = json.loads(V23_PATH.read_text(encoding="utf-8"))
    if int(source.get("eventLocalizationSlots", 0)) != 144:
        raise RuntimeError("V21 does not contain 144 event slots")
    if int(v23.get("eventSlotsObserved", 0)) != 144:
        raise RuntimeError("V23 does not contain 144 event slots")
    if int(v23.get("componentCollisionSlots", -1)) != 0:
        raise RuntimeError("V23 did not eliminate component collisions")

    total_slots = 0
    matched_slots = 0
    strict_slots = 0
    collision_slots = 0
    used_components: set[tuple[int, int, int]] = set()
    rows_output: list[dict[str, Any]] = []

    print("Locked shared time-column glyph model v24 starting", flush=True)

    for row in source["rows"]:
        components = row.get("compactStringLocalComponents", [])
        row_measures = []
        row_slots = row_matched = row_strict = 0

        for measure_entry in row.get("measureEventSlots", []):
            measure = int(measure_entry["measure"])
            x0, x1 = [float(value) for value in measure_entry["xRangePixels"]]
            width = max(1.0, x1 - x0)
            measure_components = [
                component for component in components
                if x0 <= float(component["centerX"]) < x1
            ]
            tolerance = max(4.0, width * 0.025)
            detected_columns = cluster_x(
                [float(component["centerX"]) for component in measure_components],
                tolerance,
            )

            grouped_slots: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for slot in measure_entry.get("eventSlots", []):
                grouped_slots[time_key(slot)].append(dict(slot))
            groups = sorted(
                grouped_slots.values(),
                key=lambda group: float(median([float(slot.get("expectedX") or 0) for slot in group])),
            )
            expected_columns = [
                float(median([float(slot.get("expectedX") or 0) for slot in group]))
                for group in groups
            ]
            mapped_columns = monotonic_column_map(expected_columns, detected_columns, width)

            assigned_slots: list[dict[str, Any]] = []
            used_in_measure: set[int] = set()
            for group, expected_column, mapped_column in zip(groups, expected_columns, mapped_columns):
                target_x = mapped_column if mapped_column is not None else expected_column
                for slot in sorted(group, key=lambda item: int(item.get("normalizedStringHighEToLowE") or 0)):
                    string_number = int(slot.get("normalizedStringHighEToLowE") or 0)
                    candidates = [
                        component for component in measure_components
                        if int(component.get("stringHighEToLowE", -1)) == string_number
                        and int(component["componentIndex"]) not in used_in_measure
                    ]
                    nearest = min(
                        candidates,
                        key=lambda component: abs(float(component["centerX"]) - target_x),
                    ) if candidates else None
                    max_distance = max(26.0, width * 0.16)
                    if nearest is not None and abs(float(nearest["centerX"]) - target_x) > max_distance:
                        nearest = None

                    copied = dict(slot)
                    copied["sharedExpectedColumnX"] = round(expected_column, 2)
                    copied["detectedTimeColumnX"] = round(mapped_column, 2) if mapped_column is not None else None
                    copied["assignedComponentIndex"] = int(nearest["componentIndex"]) if nearest else None
                    copied["oneToOneAssignment"] = True
                    copied["sharedTimeColumnModel"] = True
                    if nearest:
                        used_in_measure.add(int(nearest["componentIndex"]))
                        distance = abs(float(nearest["centerX"]) - target_x)
                        copied["distancePixels"] = round(distance, 2)
                        copied["assignedCenterX"] = nearest["centerX"]
                        copied["assignedWidth"] = nearest.get("width")
                        copied["assignedHeight"] = nearest.get("height")
                        strict = (
                            distance <= max(20.0, width * 0.11)
                            and float(nearest.get("width") or 999) <= 30
                            and float(nearest.get("height") or 999) <= 34
                        )
                        copied["strictCandidate"] = strict
                    else:
                        copied["distancePixels"] = None
                        copied["strictCandidate"] = False
                    assigned_slots.append(copied)

            assigned_slots.sort(key=lambda item: (
                float(item.get("detectedTimeColumnX") or item.get("sharedExpectedColumnX") or 0),
                int(item.get("normalizedStringHighEToLowE") or 0),
            ))

            for slot in assigned_slots:
                total_slots += 1
                row_slots += 1
                component_index = slot.get("assignedComponentIndex")
                if component_index is not None:
                    matched_slots += 1
                    row_matched += 1
                    key = (int(row["pageNumber"]), int(row["rowIndex"]), int(component_index))
                    if key in used_components:
                        collision_slots += 1
                    used_components.add(key)
                    if slot.get("strictCandidate"):
                        strict_slots += 1
                        row_strict += 1

            row_measures.append({
                "measure": measure,
                "xRangePixels": [x0, x1],
                "detectedTimeColumns": detected_columns,
                "eventTimeGroups": len(groups),
                "eventSlots": assigned_slots,
            })

        rows_output.append({
            "pageNumber": row["pageNumber"],
            "rowIndex": row["rowIndex"],
            "measures": row["measures"],
            "measureEventSlots": row_measures,
            "slotCount": row_slots,
            "matchedSlots": row_matched,
            "strictSlots": row_strict,
        })
        print(
            f"Page {row['pageNumber']} row {row['rowIndex']}: "
            f"slots={row_slots}, matched={row_matched}, strict={row_strict}",
            flush=True,
        )

    matched_ratio = matched_slots / total_slots if total_slots else 0.0
    strict_ratio = strict_slots / total_slots if total_slots else 0.0
    model_passed = (
        total_slots == 144
        and matched_slots >= 136
        and strict_slots >= 120
        and collision_slots == 0
    )

    output = {
        "diagnosticName": "Gomyway locked shared time-column glyph model v24",
        "referenceType": "locked-professional-shared-time-column-glyph-assignment",
        "sourceLocalization": str(SOURCE_PATH.relative_to(ROOT)),
        "sourceReassignment": str(V23_PATH.relative_to(ROOT)),
        "eventSlotsObserved": total_slots,
        "matchedEventSlots": matched_slots,
        "matchedRatio": round(matched_ratio, 6),
        "strictAutomaticCandidates": strict_slots,
        "strictCandidateRatio": round(strict_ratio, 6),
        "componentCollisionSlots": collision_slots,
        "sharedTimeColumnModelPassed": model_passed,
        "rows": rows_output,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "build-reviewed-locked-glyph-template-library-v25"
            if model_passed
            else "inspect-unmatched-locked-glyph-slots-v25"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked shared time-column glyph model v24 complete")
    print(f"Event slots observed: {total_slots}")
    print(f"Matched event slots: {matched_slots}")
    print(f"Matched ratio: {matched_ratio:.6f}")
    print(f"Strict automatic candidates: {strict_slots}")
    print(f"Strict candidate ratio: {strict_ratio:.6f}")
    print(f"Component collision slots: {collision_slots}")
    print(f"Shared time-column model passed: {model_passed}")
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
