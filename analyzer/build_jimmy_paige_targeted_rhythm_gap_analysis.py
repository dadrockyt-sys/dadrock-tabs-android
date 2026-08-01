import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

REGRESSION_PATH = PUBLIC / "gomyway-jimmy-paige-protected-113-measure-rhythm-regression.json"
PROFESSIONAL_PDF_PATH = PUBLIC / "gomyway-professional-reference.pdf"
OUTPUT_PATH = PUBLIC / "gomyway-jimmy-paige-targeted-rhythm-gap-analysis.json"

EXPECTED_MEASURES = 113

SECTION_PLAN = [
    {
        "section": "Intro",
        "startMeasure": 1,
        "endMeasure": 16,
        "priority": "high",
        "checks": [
            "full-bend-release placement",
            "open-string riff timing",
            "repeated attack spacing",
            "measure-to-measure pattern consistency",
        ],
    },
    {
        "section": "Verse 1",
        "startMeasure": 17,
        "endMeasure": 32,
        "priority": "high",
        "checks": [
            "riff timing under vocals",
            "vibrato placement",
            "muted-note and pick-direction events",
            "rests and sustained note lengths",
        ],
    },
    {
        "section": "Chorus 1",
        "startMeasure": 33,
        "endMeasure": 38,
        "priority": "critical",
        "checks": [
            "G6 voicing 0-3-4-5",
            "A(tp2) voicing 2-2-2-2-0",
            "E/D/E rhythm preservation",
            "separate repeated chord attacks",
        ],
    },
    {
        "section": "Riff 1",
        "startMeasure": 39,
        "endMeasure": 46,
        "priority": "medium",
        "checks": [
            "return-riff alignment",
            "bend-release timing",
            "terminal chord attack placement",
        ],
    },
    {
        "section": "Verse 2",
        "startMeasure": 47,
        "endMeasure": 62,
        "priority": "high",
        "checks": [
            "cross-verse rhythmic consistency",
            "vibrato and muted-note placement",
            "measure-boundary stability",
        ],
    },
    {
        "section": "Chorus 2",
        "startMeasure": 63,
        "endMeasure": 69,
        "priority": "critical",
        "checks": [
            "held-out G6 voicing 0-3-4-5",
            "held-out A(tp2) voicing 2-2-2-2-0",
            "E/D/E rhythm preservation",
            "generalization from measures 33-38",
        ],
    },
    {
        "section": "Bridge",
        "startMeasure": 70,
        "endMeasure": 77,
        "priority": "high",
        "checks": [
            "muted strums",
            "syncopated chord attacks",
            "chord-slide geometry",
            "rest and accent placement",
        ],
    },
    {
        "section": "Solo Backing",
        "startMeasure": 78,
        "endMeasure": 94,
        "priority": "high",
        "checks": [
            "backing-chord timing beneath solo",
            "muted-note distribution",
            "sustain and chord-slide continuity",
            "measure 93-94 long sustain transition",
        ],
    },
    {
        "section": "Return Riff and Out-Chorus",
        "startMeasure": 95,
        "endMeasure": 113,
        "priority": "critical",
        "checks": [
            "return-riff timing consistency",
            "time-signature changes at measures 104-105",
            "long chord ties across measures 109-113",
            "final barline placement",
        ],
    },
]


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


def main() -> None:
    regression = load_json(REGRESSION_PATH)
    if not PROFESSIONAL_PDF_PATH.exists():
        raise FileNotFoundError(
            f"Missing required artifact: {PROFESSIONAL_PDF_PATH.relative_to(ROOT)}"
        )

    regression_passed = regression.get(
        "protected113MeasureRhythmRegressionPassed"
    ) is True
    full_coverage = (
        regression.get("measuresCovered") == EXPECTED_MEASURES
        and regression.get("missingMeasures") == []
        and regression.get("fullMeasureCoveragePassed") is True
    )
    structural_coverage = regression.get("structuralCoveragePassed") is True
    source_events_unchanged = regression.get("sourceEventsMutated") is False
    renderer_unchanged = regression.get("rendererChanged") is False
    production_locked = (
        regression.get("productionRendererCalled") is False
        and regression.get("productionOutputCreated") is False
        and regression.get("productionPromotionAllowed") is False
    )

    section_measure_count = sum(
        section["endMeasure"] - section["startMeasure"] + 1
        for section in SECTION_PLAN
    )
    contiguous_sections = all(
        SECTION_PLAN[index]["endMeasure"] + 1
        == SECTION_PLAN[index + 1]["startMeasure"]
        for index in range(len(SECTION_PLAN) - 1)
    )
    section_plan_complete = (
        SECTION_PLAN[0]["startMeasure"] == 1
        and SECTION_PLAN[-1]["endMeasure"] == EXPECTED_MEASURES
        and section_measure_count == EXPECTED_MEASURES
        and contiguous_sections
    )

    gap_analysis_ready = all(
        (
            regression_passed,
            full_coverage,
            structural_coverage,
            source_events_unchanged,
            renderer_unchanged,
            production_locked,
            section_plan_complete,
        )
    )

    output = {
        "analysisName": "Jimmy Page targeted 113-measure rhythm gap analysis",
        "analysisVersion": 1,
        "expectedMeasureCount": EXPECTED_MEASURES,
        "regressionPassed": regression_passed,
        "fullMeasureCoveragePassed": full_coverage,
        "structuralCoveragePassed": structural_coverage,
        "sectionPlanComplete": section_plan_complete,
        "sectionCount": len(SECTION_PLAN),
        "sectionPlan": SECTION_PLAN,
        "interpretation": {
            "confirmed": [
                "all 113 measures have protected structural evidence",
                "section, timing, rhythm, event, and attack signals are present",
                "the protected renderer workflow remained unchanged",
            ],
            "notYetConfirmed": [
                "note-for-note pitch agreement with the professional PDF",
                "attack-by-attack timing agreement within every measure",
                "technique placement agreement across all 113 measures",
            ],
        },
        "recommendedNextGate": "protected section-by-section professional comparison",
        "targetedRhythmGapAnalysisReady": gap_analysis_ready,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "professionalPdfRemainsScoringAuthority": True,
        "readyForProtectedSectionComparison": gap_analysis_ready,
        "readyForProduction": False,
        "artifactHashes": {
            str(REGRESSION_PATH.relative_to(ROOT)): sha256_file(REGRESSION_PATH),
            str(PROFESSIONAL_PDF_PATH.relative_to(ROOT)): sha256_file(
                PROFESSIONAL_PDF_PATH
            ),
        },
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Targeted Jimmy Page rhythm gap analysis complete")
    print(f"Regression passed: {regression_passed}")
    print(f"Full measure coverage passed: {full_coverage}")
    print(f"Structural coverage passed: {structural_coverage}")
    print(f"Section plan complete: {section_plan_complete}")
    print(f"Sections queued for comparison: {len(SECTION_PLAN)}")
    for section in SECTION_PLAN:
        print(
            f"{section['section']}: measures "
            f"{section['startMeasure']}-{section['endMeasure']} "
            f"priority={section['priority']}"
        )
    print(f"Targeted rhythm gap analysis ready: {gap_analysis_ready}")
    print("Source events mutated: False")
    print("Renderer changed: False")
    print("Production renderer called: False")
    print("Production output created: False")
    print("Production promotion allowed: False")
    print("Professional PDF remains scoring authority: True")
    print(f"Ready for protected section comparison: {gap_analysis_ready}")
    print("Ready for production: False")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")

    if not gap_analysis_ready:
        raise RuntimeError("Targeted rhythm gap analysis gate did not pass")


if __name__ == "__main__":
    main()
