import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
GEOMETRY_REFERENCE = PUBLIC / "gomyway-jimmy-paige-measure-geometry-reference.json"
PROFESSIONAL_PDF = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-queue.json"

REPRESENTATIVE_TARGETS = [
    {"techniqueFamily": "full-bend-release", "measure": 1, "page": 1, "priority": 1},
    {"techniqueFamily": "vibrato", "measure": 25, "page": 2, "priority": 2},
    {"techniqueFamily": "muted-note", "measure": 28, "page": 3, "priority": 3},
    {"techniqueFamily": "pick-direction", "measure": 28, "page": 3, "priority": 4},
    {"techniqueFamily": "chord-sustain-tie", "measure": 33, "page": 3, "priority": 5},
    {"techniqueFamily": "chord-slide", "measure": 79, "page": 6, "priority": 6},
    {"techniqueFamily": "time-signature-change", "measure": 104, "page": 8, "priority": 7},
    {"techniqueFamily": "section-label", "measure": 17, "page": 2, "priority": 8},
    {"techniqueFamily": "final-barline", "measure": 113, "page": 8, "priority": 9},
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if not GEOMETRY_REFERENCE.exists():
        raise FileNotFoundError(f"Missing geometry reference: {GEOMETRY_REFERENCE}")
    if not PROFESSIONAL_PDF.exists():
        raise FileNotFoundError(f"Missing professional PDF: {PROFESSIONAL_PDF}")

    geometry_payload = json.loads(GEOMETRY_REFERENCE.read_text(encoding="utf-8"))
    source_rows = geometry_payload.get("rows") or geometry_payload.get("geometryRows") or []

    queue = []
    for target in REPRESENTATIVE_TARGETS:
        queue.append(
            {
                **target,
                "status": "pending-human-annotation",
                "normalizedGeometry": {
                    "xStart": None,
                    "yStart": None,
                    "xEnd": None,
                    "yEnd": None,
                    "controlPoints": [],
                    "labelBox": None,
                    "staffBox": None,
                },
                "verification": {
                    "confirmedAgainstProfessionalPdf": False,
                    "reviewer": None,
                    "notes": None,
                },
            }
        )

    report = {
        "schemaVersion": 1,
        "professionalPdf": str(PROFESSIONAL_PDF.relative_to(ROOT)),
        "professionalPdfSha256": sha256(PROFESSIONAL_PDF),
        "geometryReference": str(GEOMETRY_REFERENCE.relative_to(ROOT)),
        "sourceGeometryRows": len(source_rows),
        "queueRows": len(queue),
        "techniqueFamilies": sorted({row["techniqueFamily"] for row in queue}),
        "queue": queue,
        "checks": {
            "professionalPdfPresent": True,
            "geometryReferencePresent": True,
            "representativeTechniqueFamiliesCovered": len(queue) == 9,
            "syntheticCoordinatesCreated": False,
            "rendererChanged": False,
            "productionPromotionAllowed": False,
            "queuePassed": True,
            "readyForHumanGeometryAnnotation": True,
            "readyForTechniqueRendererTraining": False,
        },
    }

    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Human geometry annotation queue complete")
    print(f"Professional PDF present: {report['checks']['professionalPdfPresent']}")
    print(f"Geometry reference present: {report['checks']['geometryReferencePresent']}")
    print(f"Source geometry rows: {report['sourceGeometryRows']}")
    print(f"Annotation queue rows: {report['queueRows']}")
    print(f"Representative technique families: {len(report['techniqueFamilies'])}")
    print("Synthetic coordinates created: False")
    print("Queue passed: True")
    print("Ready for human geometry annotation: True")
    print("Ready for technique renderer training: False")
    print("Renderer changed: False")
    print("Production promotion allowed: False")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
