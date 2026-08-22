"""Audit v49 recognition jobs before any fret-template matching is attempted.

This guard verifies that every measures 17-113 job has a readable crop and six
explicit string-line coordinates. It remains read-only and deliberately refuses
to perform template matching when geometry is incomplete.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT = PUBLIC / "gomyway-professional-fret-recognition-jobs-v49.json"
OUTPUT = PUBLIC / "gomyway-professional-fret-recognition-input-audit-v50.json"


def main() -> None:
    if not INPUT.exists():
        raise RuntimeError(f"Missing prerequisite: {INPUT.relative_to(ROOT)}")

    data: dict[str, Any] = json.loads(INPUT.read_text(encoding="utf-8"))
    jobs = data.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 recognition jobs, found {len(jobs or [])}")

    reports: list[dict[str, Any]] = []
    readable_crops = 0
    six_line_jobs = 0

    for job in jobs:
        crop_value = job.get("crop")
        crop_path = ROOT / str(crop_value) if crop_value else None
        crop_readable = bool(crop_path and crop_path.exists())
        rows = job.get("stringRowsPixels")
        normalized_rows: list[float] = []
        if isinstance(rows, list):
            for value in rows:
                try:
                    normalized_rows.append(float(value))
                except (TypeError, ValueError):
                    pass
        six_lines = len(normalized_rows) == 6
        readable_crops += int(crop_readable)
        six_line_jobs += int(six_lines)
        reports.append({
            "jobIndex": int(job.get("jobIndex", 0)),
            "pageNumber": int(job.get("pageNumber", 0)),
            "rowIndex": int(job.get("rowIndex", 0)),
            "measures": job.get("measures", []),
            "crop": crop_value,
            "cropReadable": crop_readable,
            "stringRowsPixels": normalized_rows,
            "sixStringRowsAvailable": six_lines,
            "readyForTemplateMatching": crop_readable and six_lines,
        })

    ready_jobs = sum(bool(report["readyForTemplateMatching"]) for report in reports)
    passed = ready_jobs == 45

    output = {
        "diagnosticName": "Gomyway professional fret recognition input audit v50",
        "source": str(INPUT.relative_to(ROOT)),
        "recognitionJobsExpected": 45,
        "recognitionJobsInspected": len(reports),
        "jobsWithReadableCrops": readable_crops,
        "jobsWithSixStringRows": six_line_jobs,
        "jobsReadyForTemplateMatching": ready_jobs,
        "recognitionInputAuditPassed": passed,
        "jobs": reports,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": (
            "run-locked-template-matching-v51"
            if passed
            else "populate-six-string-row-coordinates-for-v49-jobs-v51"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional fret recognition input audit v50 complete")
    print(f"Recognition jobs inspected: {len(reports)}")
    print(f"Jobs with readable crops: {readable_crops}")
    print(f"Jobs with six string rows: {six_line_jobs}")
    print(f"Jobs ready for template matching: {ready_jobs}")
    print(f"Recognition input audit passed: {passed}")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
