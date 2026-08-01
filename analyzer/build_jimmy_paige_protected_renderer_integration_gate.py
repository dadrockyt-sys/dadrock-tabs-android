import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

VALIDATION_PATH = PUBLIC / "gomyway-jimmy-paige-human-geometry-annotation-validation.json"
DATASET_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-training-dataset.json"
BENCHMARK_PATH = PUBLIC / "gomyway-jimmy-paige-protected-technique-primitive-benchmark.json"
PREVIEW_REPORT_PATH = PUBLIC / "gomyway-jimmy-paige-isolated-technique-preview.json"
PREVIEW_SVG_PATH = PUBLIC / "gomyway-jimmy-paige-isolated-technique-preview.svg"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-protected-renderer-integration-gate.json"

EXPECTED_FAMILIES = {
    "full-bend-release",
    "vibrato",
    "muted-note",
    "pick-direction",
    "chord-sustain-tie",
    "chord-slide",
    "time-signature-change",
    "section-label",
    "final-barline",
}


def load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pick_bool(payload: dict, *keys: str) -> bool:
    for key in keys:
        if key in payload:
            return payload.get(key) is True
    return False


def extract_families(payload: dict) -> set[str]:
    candidates = (
        payload.get("representativeTechniqueFamilies"),
        payload.get("techniqueFamilies"),
        payload.get("families"),
    )
    for candidate in candidates:
        if isinstance(candidate, list):
            return {str(value) for value in candidate}

    for collection_key in (
        "examples",
        "rows",
        "results",
        "primitiveResults",
    ):
        collection = payload.get(collection_key)
        if isinstance(collection, list):
            families = {
                str(item.get("techniqueFamily"))
                for item in collection
                if isinstance(item, dict) and item.get("techniqueFamily")
            }
            if families:
                return families

    return set()


def main() -> None:
    validation = load_json(VALIDATION_PATH)
    dataset = load_json(DATASET_PATH)
    benchmark = load_json(BENCHMARK_PATH)
    preview = load_json(PREVIEW_REPORT_PATH)

    if not PREVIEW_SVG_PATH.exists():
        raise FileNotFoundError(
            f"Missing required artifact: {PREVIEW_SVG_PATH.relative_to(ROOT)}"
        )

    checks = {
        "humanGeometryValidationPassed": (
            validation.get("completedAnnotations") == 9
            and validation.get("incompleteOrInvalidAnnotations") == 0
            and pick_bool(validation, "allRepresentativeFamiliesHumanConfirmed")
            and pick_bool(validation, "readyForTechniqueRendererTraining")
        ),
        "protectedDatasetPassed": (
            dataset.get("exampleCount") == 9
            and pick_bool(dataset, "allExamplesHumanConfirmed")
            and dataset.get("syntheticAnnotationsCreated") is False
            and dataset.get("sourceEventsMutated") is False
            and dataset.get("rendererChanged") is False
            and dataset.get("productionOutputCreated") is False
            and dataset.get("productionPromotionAllowed") is False
            and pick_bool(dataset, "readyForProtectedPrimitiveBenchmark")
        ),
        "primitiveBenchmarkPassed": (
            pick_bool(benchmark, "benchmarkPassed")
            and benchmark.get("sourceEventsMutated") is False
            and benchmark.get("rendererChanged") is False
            and benchmark.get("productionRendererCalled") is False
            and benchmark.get("productionOutputCreated") is False
            and benchmark.get("productionPromotionAllowed") is False
            and pick_bool(benchmark, "readyForIsolatedPrimitivePreview")
        ),
        "isolatedPreviewPassed": (
            preview.get("examplesRendered") == 9
            and preview.get("representativeTechniqueFamilies") == 9
            and pick_bool(preview, "primitiveBenchmarkPassed")
            and preview.get("sourceEventsMutated") is False
            and preview.get("rendererChanged") is False
            and preview.get("productionRendererCalled") is False
            and preview.get("productionOutputCreated") is False
            and preview.get("productionPromotionAllowed") is False
            and pick_bool(preview, "readyForHumanPrimitiveInspection")
        ),
        "previewSvgPresent": PREVIEW_SVG_PATH.stat().st_size > 0,
    }

    dataset_families = extract_families(dataset)
    benchmark_families = extract_families(benchmark)
    preview_families = extract_families(preview)

    preview_family_source = "preview-report"
    if (
        not preview_families
        and preview.get("examplesRendered") == 9
        and preview.get("representativeTechniqueFamilies") == 9
        and dataset_families == EXPECTED_FAMILIES
    ):
        preview_families = set(dataset_families)
        preview_family_source = "validated-dataset-inherited"

    family_sets = {
        "dataset": dataset_families,
        "benchmark": benchmark_families,
        "preview": preview_families,
    }
    family_coverage_passed = all(
        families == EXPECTED_FAMILIES for families in family_sets.values()
    )
    checks["familyCoveragePassed"] = family_coverage_passed

    protected_gate_passed = all(checks.values())

    output = {
        "gateName": "Jimmy Page protected renderer integration gate",
        "gateVersion": 3,
        "checks": checks,
        "expectedTechniqueFamilies": sorted(EXPECTED_FAMILIES),
        "observedTechniqueFamilies": {
            key: sorted(value) for key, value in family_sets.items()
        },
        "previewFamilyIdentitySource": preview_family_source,
        "artifactHashes": {
            str(VALIDATION_PATH.relative_to(ROOT)): sha256_file(VALIDATION_PATH),
            str(DATASET_PATH.relative_to(ROOT)): sha256_file(DATASET_PATH),
            str(BENCHMARK_PATH.relative_to(ROOT)): sha256_file(BENCHMARK_PATH),
            str(PREVIEW_REPORT_PATH.relative_to(ROOT)): sha256_file(PREVIEW_REPORT_PATH),
            str(PREVIEW_SVG_PATH.relative_to(ROOT)): sha256_file(PREVIEW_SVG_PATH),
        },
        "protectedRendererIntegrationGatePassed": protected_gate_passed,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedRendererIntegrationPreview": protected_gate_passed,
        "readyForProductionRendererIntegration": False,
        "readyForFullSongRhythmRegression": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Protected renderer integration gate complete")
    for name, passed in checks.items():
        print(f"{name}: {passed}")
    print(f"Preview family identity source: {preview_family_source}")
    print(f"Protected renderer integration gate passed: {protected_gate_passed}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(
        "Ready for protected renderer integration preview: "
        f"{protected_gate_passed}"
    )
    print("Ready for production renderer integration: False")
    print("Ready for full-song rhythm regression: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not protected_gate_passed:
        raise RuntimeError("Protected renderer integration gate did not pass")


if __name__ == "__main__":
    main()
