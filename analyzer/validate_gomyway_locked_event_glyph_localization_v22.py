import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-locked-event-pdf-glyph-localization-v21.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-event-glyph-validation-v22.json"
REVIEW_DIR = PUBLIC / "gomyway-locked-event-glyph-validation-v22"

EXPECTED_LOCKED_EVENTS = 144


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    if not INPUT_PATH.exists():
        raise RuntimeError(f"Missing v21 localization: {INPUT_PATH.relative_to(ROOT)}")

    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if not source.get("all144EventsScaffolded", False):
        raise RuntimeError("V21 did not scaffold all 144 locked events")
    if not source.get("allLockedRowsHaveSixStrings", False):
        raise RuntimeError("V21 did not detect six strings in every locked row")

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    total_slots = 0
    matched_slots = 0
    strict_slots = 0
    collision_slots = 0
    rows_output: list[dict[str, Any]] = []
    fret_counts: Counter[str] = Counter()
    provisional_templates: list[dict[str, Any]] = []

    print("Locked event glyph localization validation v22 starting", flush=True)

    for row in source["rows"]:
        crop_path = ROOT / row["sourceCrop"]
        image = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            raise RuntimeError(f"Unable to read crop: {crop_path.relative_to(ROOT)}")

        string_rows = [int(value) for value in row["stringRowsPixelsHighEToLowE"]]
        spacing = float(median([
            string_rows[index + 1] - string_rows[index]
            for index in range(5)
        ]))
        components = {
            int(component["componentIndex"]): component
            for component in row["compactStringLocalComponents"]
        }

        slots: list[dict[str, Any]] = []
        for measure_entry in row["measureEventSlots"]:
            for slot in measure_entry["eventSlots"]:
                copied = dict(slot)
                copied["measure"] = int(copied["measure"])
                slots.append(copied)

        assignment_counts = Counter(
            int(slot["nearestComponentIndex"])
            for slot in slots
            if slot.get("nearestComponentIndex") is not None
        )

        annotated = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        row_strict = 0
        row_matched = 0
        row_collisions = 0
        validated_slots: list[dict[str, Any]] = []

        for slot_index, slot in enumerate(slots, start=1):
            total_slots += 1
            component_index = slot.get("nearestComponentIndex")
            component = components.get(int(component_index)) if component_index is not None else None
            distance = slot.get("distancePixels")
            normalized_distance = (
                float(distance) / spacing
                if distance is not None and spacing > 0
                else None
            )
            collision = bool(
                component_index is not None
                and assignment_counts[int(component_index)] > 1
            )
            string_match = bool(
                component is not None
                and int(component["stringHighEToLowE"])
                == int(slot["normalizedStringHighEToLowE"])
            )
            geometry_ok = bool(
                component is not None
                and 1 <= int(component["width"]) <= max(3, round(spacing * 1.55))
                and 1 <= int(component["height"]) <= max(3, round(spacing * 1.70))
            )
            distance_ok = bool(
                normalized_distance is not None
                and normalized_distance <= 0.72
            )
            strict = bool(
                component is not None
                and string_match
                and geometry_ok
                and distance_ok
                and not collision
            )

            if component is not None:
                matched_slots += 1
                row_matched += 1
            if collision:
                collision_slots += 1
                row_collisions += 1
            if strict:
                strict_slots += 1
                row_strict += 1
                fret_counts[str(slot.get("fret"))] += 1

                x = int(component["x"])
                y = int(component["y"])
                width = int(component["width"])
                height = int(component["height"])
                pad = max(2, round(spacing * 0.35))
                x0 = max(0, x - pad)
                y0 = max(0, y - pad)
                x1 = min(image.shape[1], x + width + pad)
                y1 = min(image.shape[0], y + height + pad)
                patch = image[y0:y1, x0:x1]
                patch_name = (
                    f"m{int(slot['measure']):03d}-s"
                    f"{int(slot['normalizedStringHighEToLowE'])}-"
                    f"f{str(slot.get('fret')).replace('/', '_')}-"
                    f"slot{slot_index:03d}.png"
                )
                patch_path = REVIEW_DIR / patch_name
                cv2.imwrite(str(patch_path), patch)
                provisional_templates.append({
                    "measure": int(slot["measure"]),
                    "stringHighEToLowE": int(slot["normalizedStringHighEToLowE"]),
                    "fret": slot.get("fret"),
                    "time": slot.get("time"),
                    "technique": slot.get("technique") or {},
                    "componentIndex": int(component_index),
                    "componentBoundsPixels": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height,
                    },
                    "normalizedDistance": round(float(normalized_distance), 4),
                    "patch": str(patch_path.relative_to(ROOT)),
                    "verifiedTemplate": False,
                    "requiresHumanReview": True,
                })

            if component is not None:
                x = int(component["x"])
                y = int(component["y"])
                width = int(component["width"])
                height = int(component["height"])
                color = (0, 255, 0) if strict else ((0, 165, 255) if collision else (0, 0, 255))
                cv2.rectangle(annotated, (x, y), (x + width, y + height), color, 1)
                cv2.putText(
                    annotated,
                    str(slot.get("fret")),
                    (x, max(10, y - 2)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.32,
                    color,
                    1,
                    cv2.LINE_AA,
                )

            validated_slots.append({
                **slot,
                "componentFound": component is not None,
                "componentAssignmentCollision": collision,
                "stringMatches": string_match,
                "geometryPlausible": geometry_ok,
                "normalizedDistance": round(float(normalized_distance), 4)
                if normalized_distance is not None else None,
                "strictAutomaticLocalizationCandidate": strict,
                "humanVerified": False,
            })

        preview_path = REVIEW_DIR / (
            f"page-{int(row['pageNumber']):02d}-"
            f"row-{int(row['rowIndex']):02d}-validation.png"
        )
        cv2.imwrite(str(preview_path), annotated)

        rows_output.append({
            "pageNumber": int(row["pageNumber"]),
            "rowIndex": int(row["rowIndex"]),
            "measures": [int(value) for value in row["measures"]],
            "stringSpacingPixels": spacing,
            "eventSlots": len(slots),
            "matchedSlots": row_matched,
            "strictAutomaticCandidates": row_strict,
            "collisionSlots": row_collisions,
            "validatedSlots": validated_slots,
            "preview": str(preview_path.relative_to(ROOT)),
            "humanReviewComplete": False,
        })

        print(
            f"Page {row['pageNumber']} row {row['rowIndex']}: "
            f"slots={len(slots)}, matched={row_matched}, "
            f"strict={row_strict}, collisions={row_collisions}",
            flush=True,
        )

    all_slots_present = total_slots == EXPECTED_LOCKED_EVENTS
    strict_ratio = strict_slots / total_slots if total_slots else 0.0
    automatic_validation_passed = bool(
        all_slots_present
        and matched_slots == EXPECTED_LOCKED_EVENTS
        and collision_slots == 0
        and strict_slots == EXPECTED_LOCKED_EVENTS
    )

    output = {
        "diagnosticName": "Gomyway locked event glyph localization validation v22",
        "referenceType": "locked-professional-pdf-glyph-localization-validation",
        "input": str(INPUT_PATH.relative_to(ROOT)),
        "lockedEventSlotsExpected": EXPECTED_LOCKED_EVENTS,
        "lockedEventSlotsObserved": total_slots,
        "all144EventSlotsPresent": all_slots_present,
        "matchedEventSlots": matched_slots,
        "strictAutomaticLocalizationCandidates": strict_slots,
        "strictAutomaticCandidateRatio": round(strict_ratio, 6),
        "componentAssignmentCollisionSlots": collision_slots,
        "automaticValidationPassed": automatic_validation_passed,
        "provisionalTemplateCandidatesBuilt": len(provisional_templates) > 0,
        "provisionalTemplateCandidateCount": len(provisional_templates),
        "provisionalTemplateFretCounts": dict(sorted(fret_counts.items())),
        "provisionalTemplates": provisional_templates,
        "rows": rows_output,
        "humanValidationRequired": True,
        "localizationHypothesesVerified": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "glyphTemplatesBuilt": False,
        "semanticNoteEvents17To113Extracted": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-v22-locked-glyph-localization-previews",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Locked event glyph localization validation v22 complete")
    print(f"Event slots observed: {total_slots}")
    print(f"Matched event slots: {matched_slots}")
    print(f"Strict automatic candidates: {strict_slots}")
    print(f"Component collision slots: {collision_slots}")
    print(f"Strict candidate ratio: {strict_ratio:.6f}")
    print(f"Automatic validation passed: {automatic_validation_passed}")
    print(f"Provisional template candidates: {len(provisional_templates)}")
    print("Human validation required: True")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Glyph templates built: False")
    print("Semantic note events 17-113 extracted: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Review previews: {REVIEW_DIR.relative_to(ROOT)}")

    if not all_slots_present:
        raise RuntimeError("V22 did not receive all 144 locked event slots")


if __name__ == "__main__":
    main()
