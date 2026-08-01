import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
DATASET_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-training-dataset.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-primitive-benchmark.json"

PRIMITIVE_CONTRACTS = {
    "full-bend-release": {
        "primitive": "bezier-bend-release",
        "requiredCapabilities": ["curve", "arrowhead", "bend-label", "return-curve"],
    },
    "vibrato": {
        "primitive": "wavy-vibrato-line",
        "requiredCapabilities": ["repeating-wave", "sustain-span"],
    },
    "muted-note": {
        "primitive": "muted-note-glyph",
        "requiredCapabilities": ["x-glyph", "string-alignment"],
    },
    "pick-direction": {
        "primitive": "pick-direction-glyph",
        "requiredCapabilities": ["downstroke", "upstroke", "beat-alignment"],
    },
    "chord-sustain-tie": {
        "primitive": "multi-string-sustain-ties",
        "requiredCapabilities": ["parallel-curves", "note-anchor", "cross-beat-span"],
    },
    "chord-slide": {
        "primitive": "multi-string-slide-lines",
        "requiredCapabilities": ["parallel-diagonals", "source-anchor", "target-anchor"],
    },
    "time-signature-change": {
        "primitive": "stacked-time-signature",
        "requiredCapabilities": ["numerator", "denominator", "staff-centering"],
    },
    "section-label": {
        "primitive": "section-heading-text",
        "requiredCapabilities": ["italic-text", "measure-anchor", "vertical-clearance"],
    },
    "final-barline": {
        "primitive": "final-double-barline",
        "requiredCapabilities": ["thin-line", "thick-line", "staff-height-span"],
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def valid_geometry(geometry: dict) -> bool:
    required = ("xStart", "yStart", "xEnd", "yEnd", "width", "height")
    if not all(isinstance(geometry.get(key), (int, float)) for key in required):
        return False

    x_start = float(geometry["xStart"])
    y_start = float(geometry["yStart"])
    x_end = float(geometry["xEnd"])
    y_end = float(geometry["yEnd"])
    width = float(geometry["width"])
    height = float(geometry["height"])

    return (
        0.0 <= x_start <= x_end <= 1.0
        and 0.0 <= y_start <= y_end <= 1.0
        and width > 0.0
        and height > 0.0
        and abs(width - (x_end - x_start)) < 1e-6
        and abs(height - (y_end - y_start)) < 1e-6
    )


def main() -> None:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Missing protected dataset: {DATASET_PATH}")

    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))

    safety_requirements = {
        "allExamplesHumanConfirmed": True,
        "syntheticAnnotationsCreated": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedPrimitiveBenchmark": True,
    }

    failed_safety = [
        key
        for key, expected in safety_requirements.items()
        if dataset.get(key) is not expected
    ]
    if failed_safety:
        raise RuntimeError(f"Protected dataset safety contract failed: {failed_safety}")

    examples = dataset.get("examples") or []
    if len(examples) != 9:
        raise RuntimeError(f"Expected 9 protected examples, found {len(examples)}")

    benchmark_rows = []
    eligible_count = 0
    seen_families = set()

    for example in examples:
        family = example.get("techniqueFamily")
        contract = PRIMITIVE_CONTRACTS.get(family)
        permissions = example.get("trainingPermissions") or {}
        geometry = example.get("geometry") or {}

        permission_valid = (
            permissions.get("mayTrainDrawingPrimitive") is True
            and permissions.get("mayChangePitch") is False
            and permissions.get("mayChangeTiming") is False
            and permissions.get("mayCreateNotes") is False
            and permissions.get("mayAlterMeasures") is False
            and permissions.get("mayWriteProductionOutput") is False
        )
        geometry_valid = valid_geometry(geometry)
        unique_family = family not in seen_families
        contract_present = contract is not None
        source = example.get("source") or {}
        professional_source_valid = (
            source.get("type") == "human-confirmed-professional-pdf-region"
            and source.get("synthetic") is False
            and source.get("sourceEventsMutated") is False
        )

        eligible = all(
            (
                permission_valid,
                geometry_valid,
                unique_family,
                contract_present,
                professional_source_valid,
            )
        )

        if family:
            seen_families.add(family)
        if eligible:
            eligible_count += 1

        benchmark_rows.append(
            {
                "exampleId": example.get("exampleId"),
                "techniqueFamily": family,
                "page": example.get("page"),
                "measure": example.get("measure"),
                "primitiveContract": contract,
                "geometryValid": geometry_valid,
                "trainingPermissionsValid": permission_valid,
                "professionalSourceValid": professional_source_valid,
                "representativeFamilyUnique": unique_family,
                "eligibleForIsolatedPrimitivePreview": eligible,
                "geometry": geometry,
            }
        )

    all_contracts_present = set(PRIMITIVE_CONTRACTS) == seen_families
    benchmark_passed = (
        eligible_count == 9
        and len(seen_families) == 9
        and all_contracts_present
    )

    output = {
        "benchmarkName": "Jimmy Page protected professional technique primitive benchmark",
        "benchmarkVersion": 1,
        "sourceDataset": str(DATASET_PATH.relative_to(ROOT)),
        "sourceDatasetSha256": sha256_file(DATASET_PATH),
        "examplesInspected": len(examples),
        "eligibleExamples": eligible_count,
        "representativeTechniqueFamilies": len(seen_families),
        "allPrimitiveContractsPresent": all_contracts_present,
        "benchmarkPassed": benchmark_passed,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForIsolatedPrimitivePreview": benchmark_passed,
        "readyForRendererIntegration": False,
        "rows": benchmark_rows,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected technique primitive benchmark complete")
    print(f"Examples inspected: {len(examples)}")
    print(f"Eligible examples: {eligible_count}/9")
    print(f"Representative technique families: {len(seen_families)}/9")
    print(f"All primitive contracts present: {all_contracts_present}")
    print(f"Benchmark passed: {benchmark_passed}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for isolated primitive preview: {benchmark_passed}")
    print("Ready for renderer integration: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
