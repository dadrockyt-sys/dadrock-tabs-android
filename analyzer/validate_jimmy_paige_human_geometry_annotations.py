import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "public/gomyway-jimmy-paige-human-geometry-annotation-queue.json"
OUTPUT_PATH = ROOT / "public/gomyway-jimmy-paige-human-geometry-annotation-validation.json"


def is_normalized_number(value):
    return isinstance(value, (int, float)) and 0.0 <= float(value) <= 1.0


def get_geometry(row):
    geometry = row.get("normalizedGeometry") or row.get("geometry") or {}

    x_start = geometry.get("xStart")
    y_start = geometry.get("yStart")
    x_end = geometry.get("xEnd")
    y_end = geometry.get("yEnd")

    if x_start is None:
        x_start = geometry.get("xStartNormalized")
    if y_start is None:
        y_start = geometry.get("yStartNormalized")
    if x_end is None:
        x_end = geometry.get("xEndNormalized")
    if y_end is None:
        y_end = geometry.get("yEndNormalized")

    return x_start, y_start, x_end, y_end


def is_human_confirmed(row):
    if row.get("humanConfirmed") is True:
        return True

    verification = row.get("verification") or {}
    return verification.get("confirmedAgainstProfessionalPdf") is True


def main():
    if not QUEUE_PATH.exists():
        raise FileNotFoundError(f"Missing annotation queue: {QUEUE_PATH}")

    queue_payload = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    rows = queue_payload.get("queue") or queue_payload.get("annotationQueue") or []

    validated_rows = []
    complete_count = 0
    invalid_count = 0

    for row in rows:
        x_start, y_start, x_end, y_end = get_geometry(row)
        human_confirmed = is_human_confirmed(row)

        fields_valid = all(
            is_normalized_number(value)
            for value in (x_start, y_start, x_end, y_end)
        )
        box_order_valid = (
            fields_valid
            and x_end >= x_start
            and y_end >= y_start
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
        "sourceQueue": str(QUEUE_PATH.relative_to(ROOT)),
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

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Human geometry annotation validation complete")
    print(f"Annotation queue rows: {queue_count}")
    print(f"Completed annotations: {complete_count}")
    print(f"Incomplete or invalid annotations: {invalid_count}")
    print(f"All representative families human-confirmed: {all_complete}")
    print("Synthetic coordinates accepted: False")
    print(f"Ready for technique renderer training: {all_complete}")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
