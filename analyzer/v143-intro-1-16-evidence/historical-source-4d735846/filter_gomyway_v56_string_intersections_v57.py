"""Filter v56 fret matches to candidates that truly intersect canonical TAB strings.

The v56 visual review showed false positives on rhythm stems and technique marks.
This read-only stage keeps only accepted 0/2/3 hypotheses whose component bounding
box physically crosses its assigned canonical string row and has digit-like geometry.
No protected events or measures are modified.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-locked-fret-template-matching-v56.json"
OUTPUT_PATH = PUBLIC / "gomyway-locked-fret-string-intersection-v57.json"
PREVIEW_DIR = PUBLIC / "gomyway-locked-fret-string-intersection-v57"

MAX_CENTER_DISTANCE_PIXELS = 3.25
MAX_HEIGHT_SPACING_RATIO = 0.82
MAX_WIDTH_SPACING_RATIO = 0.90
MIN_ASPECT_RATIO = 0.18
MAX_ASPECT_RATIO = 1.35


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless") from exc

    source = load_json(INPUT_PATH)
    jobs = source.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 v56 jobs, found {len(jobs or [])}")
    if source.get("professionalFretGlyphRecognitionPerformed") is not True:
        raise RuntimeError("V56 recognition did not complete")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    output_jobs: list[dict[str, Any]] = []
    reviewed = 0
    retained = 0
    rejected_not_intersecting = 0
    rejected_geometry = 0
    covered: set[int] = set()

    print("Canonical-string intersection filtering v57 starting", flush=True)

    for job in jobs:
        crop_value = job.get("crop") or job.get("sourceCrop") or job.get("cropPath")
        if not isinstance(crop_value, str) or not crop_value:
            raise RuntimeError(
                f"Missing crop for page {job.get('pageNumber')} row {job.get('rowIndex')}"
            )
        crop_path = ROOT / crop_value
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unable to read {crop_path.relative_to(ROOT)}")

        rows = [float(value) for value in job.get("canonicalStringRowsPixels", [])]
        if len(rows) != 6:
            raise RuntimeError("Canonical string-row count changed")
        spacing = float(job.get("canonicalMedianSpacingPixels", 18.4))

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        retained_candidates: list[dict[str, Any]] = []

        for candidate in job.get("candidateComponents", []):
            if candidate.get("accepted") is not True:
                continue
            reviewed += 1

            bbox = candidate.get("boundingBox", {})
            x = int(bbox.get("x", 0))
            y = int(bbox.get("y", 0))
            width = int(bbox.get("width", 0))
            height = int(bbox.get("height", 0))
            string_index = int(candidate.get("stringHighEToLowE", 0)) - 1
            if not 0 <= string_index < 6 or width <= 0 or height <= 0:
                rejected_geometry += 1
                continue

            row_y = rows[string_index]
            center_y = y + (height / 2.0)
            intersects_row = (y - 1.0) <= row_y <= (y + height + 1.0)
            center_distance = abs(center_y - row_y)
            aspect_ratio = width / float(height)
            digit_like = (
                height <= spacing * MAX_HEIGHT_SPACING_RATIO
                and width <= spacing * MAX_WIDTH_SPACING_RATIO
                and MIN_ASPECT_RATIO <= aspect_ratio <= MAX_ASPECT_RATIO
            )

            if not intersects_row or center_distance > MAX_CENTER_DISTANCE_PIXELS:
                rejected_not_intersecting += 1
                continue
            if not digit_like:
                rejected_geometry += 1
                continue

            retained_candidate = {
                **candidate,
                "v57StringIntersectionPassed": True,
                "v57CenterDistancePixels": round(center_distance, 3),
                "v57AspectRatio": round(aspect_ratio, 3),
            }
            retained_candidates.append(retained_candidate)
            retained += 1

            cv2.rectangle(preview, (x, y), (x + width, y + height), (255, 255, 255), 1)
            cv2.putText(
                preview,
                str(candidate.get("recognizedFret")),
                (x, max(10, y - 2)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)
        preview_name = (
            f"page-{int(job.get('pageNumber', 0)):02d}-"
            f"row-{int(job.get('rowIndex', 0)):02d}.png"
        )
        preview_path = PREVIEW_DIR / preview_name
        cv2.imwrite(str(preview_path), preview)

        output_jobs.append(
            {
                **job,
                "v57RetainedFretMatches": retained_candidates,
                "v57RetainedFretMatchCount": len(retained_candidates),
                "v57Preview": str(preview_path.relative_to(ROOT)),
                "v57StringIntersectionFilterApplied": True,
            }
        )
        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, v56Accepted={job.get('acceptedFretMatchCount', 0)}, "
            f"v57Retained={len(retained_candidates)}",
            flush=True,
        )

    complete_coverage = covered == set(range(17, 114))
    retention_ratio = retained / reviewed if reviewed else 0.0

    output = {
        "diagnosticName": "Gomyway canonical-string fret intersection filter v57",
        "sourceV56": str(INPUT_PATH.relative_to(ROOT)),
        "recognitionJobsProcessed": len(output_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "v56AcceptedMatchesReviewed": reviewed,
        "v57RetainedMatches": retained,
        "v57RetentionRatio": round(retention_ratio, 6),
        "rejectedNotIntersectingCanonicalString": rejected_not_intersecting,
        "rejectedNonDigitGeometry": rejected_geometry,
        "maximumCenterDistancePixels": MAX_CENTER_DISTANCE_PIXELS,
        "recognitionJobs": output_jobs,
        "humanVisualValidationRequired": True,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "nextRequiredStage": "human-review-v57-string-intersection-previews",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Canonical-string intersection filtering v57 complete")
    print(f"Recognition jobs processed: {len(output_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"V56 accepted matches reviewed: {reviewed}")
    print(f"V57 retained matches: {retained}")
    print(f"V57 retention ratio: {retention_ratio:.6f}")
    print(f"Rejected outside canonical strings: {rejected_not_intersecting}")
    print(f"Rejected non-digit geometry: {rejected_geometry}")
    print("Human visual validation required: True")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
