import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

PLAN_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-completion-plan.json"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-professional-value-annotation-queue.json"

EXPECTED_MEASURES = 113
VERIFIED_MEASURES = set(range(1, 17))
MISSING_MEASURES = set(range(17, 114))

SECTION_BATCHES = [
    {"name": "Verse 1", "start": 17, "end": 32, "priority": "high"},
    {"name": "Chorus 1", "start": 33, "end": 38, "priority": "critical"},
    {"name": "Riff 1", "start": 39, "end": 46, "priority": "medium"},
    {"name": "Verse 2", "start": 47, "end": 62, "priority": "high"},
    {"name": "Chorus 2", "start": 63, "end": 69, "priority": "critical"},
    {"name": "Bridge", "start": 70, "end": 77, "priority": "high"},
    {"name": "Solo Backing", "start": 78, "end": 94, "priority": "high"},
    {
        "name": "Return Riff and Out-Chorus",
        "start": 95,
        "end": 113,
        "priority": "critical",
    },
]

PDF_NAME_HINTS = ("professional", "reference", "gomyway", "jimmy")
CANDIDATE_NAME_HINTS = (
    "candidate",
    "winner",
    "events",
    "timing",
    "rhythm",
    "section",
    "measure",
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def discover_professional_pdf() -> Path | None:
    candidates: list[Path] = []
    for path in PUBLIC.glob("*.pdf"):
        name = path.name.lower()
        score = sum(hint in name for hint in PDF_NAME_HINTS)
        if score:
            candidates.append(path)
    if not candidates:
        return None
    candidates.sort(
        key=lambda path: (
            -sum(hint in path.name.lower() for hint in PDF_NAME_HINTS),
            -path.stat().st_size,
            path.name,
        )
    )
    return candidates[0]


def discover_candidate_jsons() -> list[Path]:
    candidates: list[Path] = []
    for path in PUBLIC.glob("*.json"):
        if path in {PLAN_PATH, OUTPUT_PATH}:
            continue
        name = path.name.lower()
        if "gomyway" not in name and "jimmy" not in name:
            continue
        if any(hint in name for hint in CANDIDATE_NAME_HINTS):
            candidates.append(path)
    candidates.sort(key=lambda path: path.name)
    return candidates


def split_into_tablet_pages(start: int, end: int, page_size: int = 4) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    page_number = 1
    cursor = start
    while cursor <= end:
        page_end = min(end, cursor + page_size - 1)
        pages.append(
            {
                "pageNumber": page_number,
                "measureStart": cursor,
                "measureEnd": page_end,
                "measureCount": page_end - cursor + 1,
                "status": "pending-human-review",
                "candidatePrefillAllowed": True,
                "professionalPdfIsAuthority": True,
                "autoSaveEveryConfirmation": True,
            }
        )
        cursor = page_end + 1
        page_number += 1
    return pages


def main() -> None:
    plan = load_json(PLAN_PATH)

    plan_ready = plan.get("completionPlanReady") is True
    verified_count = plan.get("verifiedProfessionalValueCount")
    missing_count = plan.get("missingProfessionalValueCount")
    structure_coverage = plan.get("fullSongStructureCoverage")
    timing_coverage = plan.get("fullSongTimingCoverage")

    professional_pdf = discover_professional_pdf()
    candidate_jsons = discover_candidate_jsons()

    batches: list[dict[str, Any]] = []
    queued_measures: set[int] = set()

    for batch_index, section in enumerate(SECTION_BATCHES, start=1):
        measures = list(range(section["start"], section["end"] + 1))
        queued_measures.update(measures)
        tablet_pages = split_into_tablet_pages(section["start"], section["end"])
        batches.append(
            {
                "batchIndex": batch_index,
                "sectionName": section["name"],
                "measureStart": section["start"],
                "measureEnd": section["end"],
                "measureCount": len(measures),
                "priority": section["priority"],
                "status": "pending-human-review",
                "tabletPages": tablet_pages,
                "reviewFields": [
                    "stringIndex",
                    "fret",
                    "midiPitch",
                    "positionInMeasure",
                    "durationSteps",
                    "technique",
                ],
            }
        )

    queue_measure_coverage_passed = queued_measures == MISSING_MEASURES
    dependencies_present = (
        professional_pdf is not None
        and len(candidate_jsons) > 0
        and plan_ready
        and verified_count == 16
        and missing_count == 97
        and structure_coverage == EXPECTED_MEASURES
        and timing_coverage == EXPECTED_MEASURES
    )
    queue_ready = dependencies_present and queue_measure_coverage_passed

    output = {
        "queueName": "Jimmy Page tablet-safe professional value annotation queue",
        "queueVersion": 1,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "verifiedProfessionalMeasures": sorted(VERIFIED_MEASURES),
        "queuedProfessionalMeasures": sorted(MISSING_MEASURES),
        "verifiedMeasureCount": len(VERIFIED_MEASURES),
        "queuedMeasureCount": len(MISSING_MEASURES),
        "professionalPdf": (
            str(professional_pdf.relative_to(ROOT)) if professional_pdf else None
        ),
        "candidateSourceArtifacts": [
            str(path.relative_to(ROOT)) for path in candidate_jsons
        ],
        "candidateSourceArtifactCount": len(candidate_jsons),
        "batches": batches,
        "batchCount": len(batches),
        "tabletPageCount": sum(len(batch["tabletPages"]) for batch in batches),
        "queueMeasureCoveragePassed": queue_measure_coverage_passed,
        "dependenciesPresent": dependencies_present,
        "annotationQueueReady": queue_ready,
        "professionalPdfRemainsScoringAuthority": True,
        "candidateValuesAreUnverifiedPrefillOnly": True,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "readyForTabletSafeProfessionalValueAnnotator": queue_ready,
        "readyForProtected113MeasureValueExtraction": False,
        "readyForProduction": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Jimmy Page tablet-safe professional value annotation queue complete")
    print(f"Verified professional measures: {len(VERIFIED_MEASURES)}/113")
    print(f"Queued professional measures: {len(MISSING_MEASURES)}")
    print(f"Annotation batches: {len(batches)}")
    print(f"Tablet review pages: {output['tabletPageCount']}")
    print("Professional PDF present: " f"{professional_pdf is not None}")
    if professional_pdf is not None:
        print(f"Professional PDF: {professional_pdf.relative_to(ROOT)}")
    print(f"Candidate source artifacts: {len(candidate_jsons)}")
    print(f"Queue measure coverage passed: {queue_measure_coverage_passed}")
    print(f"Dependencies present: {dependencies_present}")
    print(f"Annotation queue ready: {queue_ready}")
    print("Professional PDF remains scoring authority: True")
    print("Candidate values are unverified prefill only: True")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print(f"Ready for tablet-safe professional value annotator: {queue_ready}")
    print("Ready for protected 113-measure value extraction: False")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not queue_ready:
        raise RuntimeError("Tablet-safe professional value annotation queue did not pass")


if __name__ == "__main__":
    main()
