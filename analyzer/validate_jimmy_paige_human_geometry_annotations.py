import json
from pathlib import Path

QUEUE_PATH = Path("public/gomyway-jimmy-paige-human-geometry-annotation-queue.json")
OUTPUT_PATH = Path("public/gomyway-jimmy-paige-human-geometry-annotation-validation.json")

REQUIRED_GEOMETRY_FIELDS = (
    "xStartNormalized",
    "yStartNormalized",
    "xEndNormalized",
    "yEndNormalized",
)


def is_normalized_number(value):
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def main():
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Missing annotation queue: {QUEUE_PATH}")

    queue_payload = json.loads(QUEUE_PATH.read_text())
    rows = queue_payload.get("annotationQueue", [])

    validated_rows = []
    complete_count = 0
    invalid_count = 0

    for row in rows:
        geometry = row.get("geometry", {})
        human_confirmed = row.get("humanConfirmed") is True
        fields_valid = all(
            is_normalized_number(geometry.get(field))
            for field in REQUIRED_GEOMETRY_FIELDS
        )
        box_order_valid = (
            fields_valid
            and geometry["xEndNormalized"] >= geometry["xStartNormalized"]
            and geometry["yEndNormalized"] >= geometry["yStartNormalized"]
        )
        row_complete = human_confirmed and fields_valid and box_order_valid

        if row_complete:
            complete_count += 1
        else:
            invalid_count += 1

        validated_rows.append(
            {
                "techniqueFamily": row.get("techniqueFamily"),
                "page": row.get("page"),
                "measure": row.get("measure"),
                "humanConfirmed": human_confirmed,
                "normalizedGeometryValid": fields_valid,
                "boxOrderValid": box_order_valid,
                "annotationComplete": row_complete,
            }
        )

    queue_count = len(rows)
    all_complete = queue_count > 0 and complete_count == queue_count

    output = {
        "validationName": "Jimmy Page human geometry annotation gate",
        "sourceQueue": str(QUEUE_PATH),
        "annotationQueueRows": queue_count,
        "completedAnnotations": complete_count,
        "incompleteOrInvalidAnnotations": invalid_count,
        "allRepresentativeFamiliesHumanConfirmed": all_complete,
        "syntheticCoordinatesAccepted": False,
        "rendererChanged": False,
        "productionPromotionAllowed": False,
        "readyForTechniqueRendererTraining": all_complete,
        "rows": validated_rows,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")

    print("Human geometry annotation validation complete")
    print(f"Annotation queue rows: {queue_count}")
    print(f"Completed annotations: {complete_count}")
    print(f"Incomplete or invalid annotations: {invalid_count}")
    print(f"All representative families human-confirmed: {all_complete}")
    print("Synthetic coordinates accepted: False")
    print(f"Ready for technique renderer training: {all_complete}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
