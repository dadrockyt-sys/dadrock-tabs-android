"""Promote the proven v51 six-string coordinates into the canonical fret-recognition input.

This stage intentionally does not rediscover TAB staff geometry. It trusts the
45 v51 jobs that already passed human-reviewed six-string row population and
copies their ``stringRowsPixels`` coordinates into a clean, read-only input for
professional fret glyph matching over measures 17-113.

Measures 1-16, V7 events, candidate audio, and production outputs are untouched.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
SOURCE_PATH = PUBLIC / "gomyway-professional-string-row-coordinates-v51.json"
OUTPUT_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    source = load_json(SOURCE_PATH)
    jobs = source.get("recognitionJobs", [])

    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 v51 recognition jobs, found {len(jobs or [])}")
    if source.get("allJobsReadyForTemplateMatching") is not True:
        raise RuntimeError("V51 did not approve all jobs for template matching")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V51 complete measures 17-113 coverage did not pass")

    canonical_jobs: list[dict[str, Any]] = []
    covered: set[int] = set()
    spacing_deviations: list[float] = []

    print("V51 canonical string-row promotion v55 starting", flush=True)

    for job in jobs:
        rows = job.get("stringRowsPixels", [])
        if not isinstance(rows, list) or len(rows) != 6:
            raise RuntimeError(
                f"Page {job.get('pageNumber')} row {job.get('rowIndex')} "
                f"does not contain six canonical string rows"
            )

        normalized_rows = [float(value) for value in rows]
        if normalized_rows != sorted(normalized_rows):
            raise RuntimeError(
                f"Page {job.get('pageNumber')} row {job.get('rowIndex')} "
                "string rows are not top-to-bottom ordered"
            )
        if len(set(normalized_rows)) != 6:
            raise RuntimeError(
                f"Page {job.get('pageNumber')} row {job.get('rowIndex')} "
                "contains duplicate string rows"
            )

        gaps = [normalized_rows[index + 1] - normalized_rows[index] for index in range(5)]
        local_spacing = float(median(gaps))
        expected_spacing = float(job.get("expectedStringSpacingPixels", 0.0))
        deviation = float(job.get("medianSpacingDeviationPixels", 999.0))

        if expected_spacing <= 0:
            raise RuntimeError("V51 expected string spacing is missing")
        if job.get("rowGeometryPassed") is not True:
            raise RuntimeError(
                f"Page {job.get('pageNumber')} row {job.get('rowIndex')} "
                "was not approved by v51"
            )

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)
        spacing_deviations.append(deviation)

        canonical_jobs.append(
            {
                **job,
                "canonicalStringRowsPixels": [round(value, 3) for value in normalized_rows],
                "canonicalStringOrder": ["highE", "B", "G", "D", "A", "lowE"],
                "canonicalMedianSpacingPixels": round(local_spacing, 6),
                "geometrySource": str(SOURCE_PATH.relative_to(ROOT)),
                "geometryRediscoveryPerformed": False,
                "readyForLockedTemplateMatching": True,
                "recognizedGlyphs": [],
                "recognitionPerformed": False,
            }
        )

        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, rows=6, spacing={local_spacing:.3f}, "
            f"v51Deviation={deviation:.3f}, promoted=True",
            flush=True,
        )

    expected_measures = set(range(17, 114))
    complete_coverage = covered == expected_measures
    all_promoted = len(canonical_jobs) == 45 and complete_coverage

    output = {
        "diagnosticName": "Gomyway v51 canonical fret-recognition input v55",
        "source": str(SOURCE_PATH.relative_to(ROOT)),
        "canonicalJobsPrepared": len(canonical_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "allCanonicalRowsPromoted": all_promoted,
        "medianV51SpacingDeviationPixels": round(median(spacing_deviations), 6),
        "geometryRediscoveryPerformed": False,
        "v52ToV54GeometryFailuresIgnored": True,
        "recognitionJobs": canonical_jobs,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "run-locked-fret-template-matching-over-v55-canonical-rows-v56",
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("V51 canonical string-row promotion v55 complete")
    print(f"Canonical jobs prepared: {len(canonical_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"All canonical rows promoted: {all_promoted}")
    print("Geometry rediscovery performed: False")
    print("V52-v54 geometry failures ignored: True")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
