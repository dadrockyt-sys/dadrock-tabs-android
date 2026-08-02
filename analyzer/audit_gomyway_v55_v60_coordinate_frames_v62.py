"""Audit the coordinate-frame mismatch between approved V55 rows and V60 crops.

The V61 contact sheets show that many V60 expected six-string lattices are drawn
on lyrics, rhythm stems, chord labels, or neighbouring systems while the actual
TAB staff is visible elsewhere in the same image. This stage is deliberately
read-only. It does not rediscover geometry, recognize frets, extract semantic
note events, modify locked measures 1-16 or V7 events, use candidate audio, or
promote anything to production.

The audit records every usable image-path field carried by each V55 job, compares
image dimensions, reports where the approved V55 rows land as normalized Y
coordinates, and builds contact sheets that make crop/origin mismatches visible.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
V55_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
V60_PATH = PUBLIC / "gomyway-row-local-string-lattices-v60.json"
OUTPUT_PATH = PUBLIC / "gomyway-v55-v60-coordinate-frame-audit-v62.json"
PREVIEW_DIR = PUBLIC / "gomyway-v55-v60-coordinate-frame-audit-v62"

EXPECTED_JOB_COUNT = 45
EXPECTED_MEASURES = set(range(17, 114))
PATH_KEYS = (
    "crop",
    "sourceCrop",
    "cropPath",
    "rowCrop",
    "imagePath",
    "previewPath",
)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def readable_paths(job: dict[str, Any]) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    seen: set[Path] = set()
    for key in PATH_KEYS:
        value = job.get(key)
        if not isinstance(value, str) or not value:
            continue
        path = ROOT / value
        if path.exists() and path not in seen:
            found.append((key, path))
            seen.add(path)
    return found


def job_key(job: dict[str, Any]) -> tuple[int, int]:
    return int(job.get("pageNumber", 0)), int(job.get("rowIndex", 0))


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install opencv-python-headless numpy") from exc

    v55 = load_json(V55_PATH)
    v60 = load_json(V60_PATH)

    if v55.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("V55 locked-measure safeguard is not intact")
    if v60.get("lockedMeasures1To16Modified") is not False:
        raise RuntimeError("V60 locked-measure safeguard is not intact")
    if v55.get("v7EventsModified") is not False:
        raise RuntimeError("V55 V7-event safeguard is not intact")
    if v60.get("v7EventsModified") is not False:
        raise RuntimeError("V60 V7-event safeguard is not intact")

    v55_jobs = v55.get("recognitionJobs", [])
    v60_jobs = v60.get("recognitionJobs", [])
    if not isinstance(v55_jobs, list) or len(v55_jobs) != EXPECTED_JOB_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_JOB_COUNT} V55 jobs")
    if not isinstance(v60_jobs, list) or len(v60_jobs) != EXPECTED_JOB_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_JOB_COUNT} V60 jobs")

    v60_by_key = {job_key(job): job for job in v60_jobs}
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

    cards: list[Any] = []
    reports: list[dict[str, Any]] = []
    covered: set[int] = set()
    failed_count = 0
    expected_rows_outside_image = 0
    multiple_readable_paths = 0
    dimension_disagreement_jobs = 0

    for v55_job in v55_jobs:
        key = job_key(v55_job)
        v60_job = v60_by_key.get(key)
        if v60_job is None:
            raise RuntimeError(f"Missing V60 job for page {key[0]} row {key[1]}")

        measures = [int(value) for value in v55_job.get("measures", [])]
        covered.update(measures)
        expected_rows = [float(value) for value in v55_job.get("canonicalStringRowsPixels", [])]
        if len(expected_rows) != 6:
            raise RuntimeError(f"Expected six V55 rows for page {key[0]} row {key[1]}")

        paths = readable_paths(v55_job)
        if not paths:
            raise RuntimeError(f"No readable V55 image path for page {key[0]} row {key[1]}")
        if len(paths) > 1:
            multiple_readable_paths += 1

        image_infos: list[dict[str, Any]] = []
        dimensions: set[tuple[int, int]] = set()
        for field, path in paths:
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
            height, width = image.shape
            dimensions.add((width, height))
            normalized = [round(value / max(1, height), 6) for value in expected_rows]
            rows_inside = all(0 <= value < height for value in expected_rows)
            image_infos.append(
                {
                    "field": field,
                    "path": str(path.relative_to(ROOT)),
                    "width": width,
                    "height": height,
                    "expectedRowsInsideImage": rows_inside,
                    "expectedRowsNormalizedY": normalized,
                }
            )

        if not image_infos:
            raise RuntimeError(f"No readable images for page {key[0]} row {key[1]}")
        if len(dimensions) > 1:
            dimension_disagreement_jobs += 1

        primary_info = image_infos[0]
        primary_path = ROOT / primary_info["path"]
        gray = cv2.imread(str(primary_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unreadable primary image: {primary_path.relative_to(ROOT)}")
        height, width = gray.shape

        rows_inside = all(0 <= value < height for value in expected_rows)
        if not rows_inside:
            expected_rows_outside_image += 1

        passed = v60_job.get("v60RowLocalRegistrationPassed") is True
        if not passed:
            failed_count += 1

        preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        for index, value in enumerate(expected_rows, start=1):
            y = int(round(value))
            if 0 <= y < height:
                cv2.line(preview, (0, y), (width - 1, y), (255, 0, 0), 1)
                cv2.putText(
                    preview,
                    f"V55-{index}",
                    (5, max(13, y - 3)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 0, 0),
                    1,
                    cv2.LINE_AA,
                )

        registered_rows = [
            float(value)
            for value in v60_job.get("v60RegisteredStringRowsPixels", [])
        ]
        for index, value in enumerate(registered_rows, start=1):
            y = int(round(value))
            if 0 <= y < height:
                cv2.line(preview, (0, y), (width - 1, y), (0, 255, 0), 2)
                cv2.putText(
                    preview,
                    f"V60-{index}",
                    (68, max(13, y - 3)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 255, 0),
                    1,
                    cv2.LINE_AA,
                )

        target_width = 1200
        scale = target_width / max(1, width)
        resized = cv2.resize(
            preview,
            (target_width, max(1, round(height * scale))),
            interpolation=cv2.INTER_AREA,
        )

        reason = str(v60_job.get("v60Registration", {}).get("reason") or "unknown")
        label = (
            f"p{key[0]} r{key[1]} m{','.join(str(v) for v in measures)} | "
            f"field={primary_info['field']} size={width}x{height} | "
            f"paths={len(image_infos)} dims={len(dimensions)} | "
            f"v60Passed={passed} reason={reason}"
        )
        header = np.full((62, target_width, 3), 245, dtype=np.uint8)
        cv2.putText(
            header,
            label[:185],
            (12, 39),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.58,
            (20, 20, 20),
            1,
            cv2.LINE_AA,
        )
        cards.append(np.vstack([header, resized]))

        reports.append(
            {
                "pageNumber": key[0],
                "rowIndex": key[1],
                "measures": measures,
                "canonicalStringRowsPixels": expected_rows,
                "primaryImageField": primary_info["field"],
                "primaryImagePath": primary_info["path"],
                "primaryImageWidth": width,
                "primaryImageHeight": height,
                "expectedRowsInsidePrimaryImage": rows_inside,
                "expectedRowsNormalizedY": [
                    round(value / max(1, height), 6) for value in expected_rows
                ],
                "readableImageCandidates": image_infos,
                "readableImageCandidateCount": len(image_infos),
                "distinctImageDimensionCount": len(dimensions),
                "v60RowLocalRegistrationPassed": passed,
                "v60FailureReason": reason,
                "v60RegisteredStringRowsPixels": registered_rows,
            }
        )

    sheets: list[str] = []
    per_sheet = 4
    for start in range(0, len(cards), per_sheet):
        batch = cards[start : start + per_sheet]
        width = max(card.shape[1] for card in batch)
        padded: list[Any] = []
        for card in batch:
            if card.shape[1] < width:
                pad = np.full(
                    (card.shape[0], width - card.shape[1], 3),
                    245,
                    dtype=np.uint8,
                )
                card = np.hstack([card, pad])
            padded.append(card)
        sheet = np.vstack(padded)
        path = PREVIEW_DIR / f"coordinate-frame-contact-sheet-{start // per_sheet + 1:02d}.png"
        cv2.imwrite(str(path), sheet)
        sheets.append(str(path.relative_to(ROOT)))

    complete_coverage = covered == EXPECTED_MEASURES
    output = {
        "diagnosticName": "Gomyway V55-to-V60 coordinate-frame audit V62",
        "sourceV55": str(V55_PATH.relative_to(ROOT)),
        "sourceV60": str(V60_PATH.relative_to(ROOT)),
        "jobsInspected": len(reports),
        "failedV60Jobs": failed_count,
        "jobsWithMultipleReadableImagePaths": multiple_readable_paths,
        "jobsWithDistinctImageDimensions": dimension_disagreement_jobs,
        "jobsWithExpectedRowsOutsidePrimaryImage": expected_rows_outside_image,
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "contactSheets": sheets,
        "jobs": reports,
        "coordinateFrameRepairApplied": False,
        "geometryRediscoveryPerformed": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": "inspect-v62-coordinate-frame-contact-sheets",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("V55-to-V60 coordinate-frame audit V62 complete")
    print(f"Jobs inspected: {len(reports)}")
    print(f"Failed V60 jobs: {failed_count}")
    print(f"Jobs with multiple readable image paths: {multiple_readable_paths}")
    print(f"Jobs with distinct image dimensions: {dimension_disagreement_jobs}")
    print(f"Expected rows outside primary image: {expected_rows_outside_image}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"Contact sheets built: {len(sheets)}")
    print("Coordinate-frame repair applied: False")
    print("Geometry rediscovery performed: False")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print("Next required stage: inspect-v62-coordinate-frame-contact-sheets")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Contact sheets: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
