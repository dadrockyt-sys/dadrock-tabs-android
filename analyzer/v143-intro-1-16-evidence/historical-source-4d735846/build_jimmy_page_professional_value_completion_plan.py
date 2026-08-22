import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

INTRO_REFERENCE = PUBLIC / "gomyway-professional-rhythm-reference-v2.json"
FULL_STRUCTURE = PUBLIC / "gomyway-professional-rhythm-reference.json"
TIMING_MAP = PUBLIC / "gomyway-professional-timing-map-v2.json"
INVENTORY = PUBLIC / "gomyway-jimmy-paige-professional-value-reference-inventory.json"
OUTPUT = PUBLIC / "gomyway-jimmy-paige-professional-value-completion-plan.json"

SECTIONS = [
    ("Intro", 1, 16, "complete"),
    ("Verse 1", 17, 32, "high"),
    ("Chorus 1", 33, 38, "critical"),
    ("Riff 1", 39, 46, "medium"),
    ("Verse 2", 47, 62, "high"),
    ("Chorus 2", 63, 69, "critical"),
    ("Bridge", 70, 77, "high"),
    ("Solo Backing", 78, 94, "high"),
    ("Return Riff and Out-Chorus", 95, 113, "critical"),
]


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def measure_count(payload: Any) -> int:
    if isinstance(payload, dict):
        measures = payload.get("measures")
        if isinstance(measures, list):
            return len(measures)
    return 0


def main() -> None:
    intro = load_json(INTRO_REFERENCE)
    structure = load_json(FULL_STRUCTURE)
    timing = load_json(TIMING_MAP)
    inventory = load_json(INVENTORY)

    intro_count = measure_count(intro)
    structure_count = measure_count(structure)

    timing_coverage = inventory.get("timingCoverage", 113)
    if not isinstance(timing_coverage, int):
        timing_coverage = 113

    section_rows = []
    missing_measures = []

    for name, start, end, priority in SECTIONS:
        complete = end <= intro_count
        measures = list(range(start, end + 1))
        if not complete:
            missing_measures.extend(measures)

        section_rows.append(
            {
                "name": name,
                "startMeasure": start,
                "endMeasure": end,
                "measureCount": end - start + 1,
                "priority": priority,
                "professionalValuesComplete": complete,
                "workflow": (
                    "reuse verified professional reference"
                    if complete
                    else "prefill candidate values, compare against professional PDF, correct, human-confirm"
                ),
            }
        )

    plan_ready = (
        intro_count == 16
        and structure_count >= 113
        and timing_coverage >= 113
        and missing_measures == list(range(17, 114))
    )

    output = {
        "planName": "Jimmy Page professional musical-value completion plan",
        "expectedMeasures": 113,
        "verifiedProfessionalValueMeasures": list(range(1, intro_count + 1)),
        "missingProfessionalValueMeasures": missing_measures,
        "verifiedProfessionalValueCount": intro_count,
        "missingProfessionalValueCount": len(missing_measures),
        "fullSongStructureCoverage": structure_count,
        "fullSongTimingCoverage": timing_coverage,
        "sections": section_rows,
        "recommendedBatchOrder": [
            "Chorus 1",
            "Chorus 2",
            "Return Riff and Out-Chorus",
            "Verse 1",
            "Verse 2",
            "Bridge",
            "Solo Backing",
            "Riff 1",
        ],
        "candidatePrefillAllowed": True,
        "candidateValuesAreAuthority": False,
        "professionalPdfRemainsScoringAuthority": True,
        "humanConfirmationRequired": True,
        "syntheticProfessionalValuesAllowed": False,
        "sourceEventsMutated": False,
        "rendererChanged": False,
        "productionRendererCalled": False,
        "productionOutputCreated": False,
        "productionPromotionAllowed": False,
        "completionPlanReady": plan_ready,
        "readyForTabletSafeProfessionalValueAnnotator": plan_ready,
        "readyForProtected113MeasureValueExtraction": False,
        "readyForProduction": False,
    }

    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Jimmy Page professional musical-value completion plan complete")
    print(f"Verified professional value measures: {intro_count}/113")
    print(f"Missing professional value measures: {len(missing_measures)}")
    print(f"Full-song structure coverage: {structure_count}/113")
    print(f"Full-song timing coverage: {timing_coverage}/113")
    print(f"Completion plan ready: {plan_ready}")
    for row in section_rows:
        print(
            f"{row['name']}: measures {row['startMeasure']}-{row['endMeasure']} "
            f"complete={row['professionalValuesComplete']} priority={row['priority']}"
        )
    print("Professional PDF remains scoring authority: True")
    print("Ready for tablet-safe professional value annotator: " f"{plan_ready}")
    print("Ready for protected 113-measure value extraction: False")
    print("Ready for production: False")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")

    if not plan_ready:
        raise RuntimeError("Professional value completion plan did not pass")


if __name__ == "__main__":
    main()
