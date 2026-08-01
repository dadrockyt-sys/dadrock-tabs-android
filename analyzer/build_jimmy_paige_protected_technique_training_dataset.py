import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
QUEUE_PATH = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-queue.json"
VALIDATION_PATH = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-validation.json"
PROFESSIONAL_PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-training-dataset.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def populated_geometry(row: dict) -> dict:
    candidates = [
        row.get("normalizedGeometry") or {},
        row.get("geometry") or {},
    ]

    key_sets = (
        ("xStart", "yStart", "xEnd", "yEnd"),
        (
            "xStartNormalized",
            "yStartNormalized",
            "xEndNormalized",
            "yEndNormalized",
        ),
    )

    for geometry in candidates:
        for keys in key_sets:
            values = [geometry.get(key) for key in keys]
            if all(isinstance(value, (int, float)) for value in values):
                x_start, y_start, x_end, y_end = map(float, values)
                if (
                    0.0 <= x_start <= 1.0
                    and 0.0 <= y_start <= 1.0
                    and 0.0 <= x_end <= 1.0
                    and 0.0 <= y_end <= 1.0
                    and x_end >= x_start
                    and y_end >= y_start
                ):
                    return {
                        "xStart": x_start,
                        "yStart": y_start,
                        "xEnd": x_end,
                        "yEnd": y_end,
                        "width": x_end - x_start,
                        "height": y_end - y_start,
                    }

    raise ValueError(
        f"No populated normalized geometry for {row.get('techniqueFamily')}"
    )


def human_confirmed(row: dict) -> bool:
    if row.get("humanConfirmed") is True:
        return True
    verification = row.get("verification") or {}
    return verification.get("confirmedAgainstProfessionalPdf") is True


def main() -> None:
    required_paths = [QUEUE_PATH, VALIDATION_PATH, PROFESSIONAL_PDF_PATH]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing required protected inputs: {missing}")

    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    if validation.get("readyForTechniqueRendererTraining") is not True:
        raise RuntimeError("Human geometry validation gate has not passed")
    if validation.get("completedAnnotations") != 9:
        raise RuntimeError("Expected exactly 9 completed professional annotations")
    if validation.get("incompleteOrInvalidAnnotations") != 0:
        raise RuntimeError("Validation still contains incomplete annotations")

    queue_payload = json.loads(QUEUE_PATH.read_text(encoding="utf-8"))
    rows = queue_payload.get("queue") or queue_payload.get("annotationQueue") or []
    if len(rows) != 9:
        raise RuntimeError(f"Expected 9 queue rows, found {len(rows)}")

    examples = []
    seen_families = set()

    for index, row in enumerate(rows, start=1):
        family = row.get("techniqueFamily")
        if not family:
            raise ValueError(f"Queue row {index} has no technique family")
        if family in seen_families:
            raise ValueError(f"Duplicate representative technique family: {family}")
        if not human_confirmed(row):
            raise ValueError(f"Technique family is not human-confirmed: {family}")

        seen_families.add(family)
        examples.append(
            {
                "exampleId": f"jimmy-page-professional-{index:02d}-{family}",
                "techniqueFamily": family,
                "page": row.get("page"),
                "measure": row.get("measure"),
                "label": row.get("label") or row.get("targetLabel") or family,
                "geometry": populated_geometry(row),
                "source": {
                    "type": "human-confirmed-professional-pdf-region",
                    "professionalPdf": str(PROFESSIONAL_PDF_PATH.relative_to(ROOT)),
                    "synthetic": False,
                    "sourceEventsMutated": False,
                },
                "trainingPermissions": {
                    "mayTrainDrawingPrimitive": True,
                    "mayChangePitch": False,
                    "mayChangeTiming": False,
                    "mayCreateNotes": False,
                    "mayAlterMeasures": False,
                    "mayWriteProductionOutput": False,
                },
            }
        )

    dataset = {
        "datasetName": "Jimmy Page protected professional technique renderer training dataset",
        "datasetVersion": 1,
        "professionalPdf": str(PROFESSIONAL_PDF_PATH.relative_to(ROOT)),
        "professionalPdfSha256": sha256_file(PROFESSIONAL_PDF_PATH),
        "annotationQueueSha256": sha256_file(QUEUE_PATH),
        "validationSha256": sha256_file(VALIDATION_PATH),
        "exampleCount": len(examples),
        "representativeTechniqueFamilies": sorted(seen_families),
        "allExamplesHumanConfirmed": True,
        "syntheticAnnotationsCreated": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedPrimitiveBenchmark": True,
        "readyForProductionRendererTraining": False,
        "examples": examples,
    }

    OUTPUT_PATH.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")

    print("Protected technique renderer training dataset complete")
    print("Human geometry validation passed: True")
    print(f"Training examples: {len(examples)}")
    print(f"Representative technique families: {len(seen_families)}")
    print("All examples human-confirmed: True")
    print("Synthetic annotations created: False")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print("Ready for protected primitive benchmark: True")
    print("Ready for production renderer training: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
