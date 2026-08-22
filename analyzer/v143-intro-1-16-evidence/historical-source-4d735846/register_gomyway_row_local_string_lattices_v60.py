"""Register each full-song row crop to its local six-string TAB lattice.

V59 searched narrow bands centred on the promoted V55 coordinates. The previews
showed that those coordinates can still be displaced onto rhythm notation,
lyrics, bend labels, or neighbouring systems. V60 keeps V55 as the approved
anchor, but performs a tightly bounded row-local search for six horizontal TAB
rules before any further fret recognition.

This stage is read-only and diagnostic. It does not recognize fret values,
extract semantic events, modify measures 1-16 or V7 events, use candidate audio,
or promote anything to production.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
OUTPUT_PATH = PUBLIC / "gomyway-row-local-string-lattices-v60.json"
PREVIEW_DIR = PUBLIC / "gomyway-row-local-string-lattices-v60"

EXPECTED_JOB_COUNT = 45
EXPECTED_MEASURES = set(range(17, 114))
SEARCH_RADIUS_RATIO = 0.62
MAX_ANCHOR_SHIFT_RATIO = 0.75
MAX_LINE_SHIFT_RATIO = 0.42
MIN_SPACING_RATIO = 0.78
MAX_SPACING_RATIO = 1.22
MAX_MEDIAN_GAP_DEVIATION = 1.8
MAX_SINGLE_GAP_DEVIATION = 3.0
MIN_HORIZONTAL_CONTINUITY = 0.34


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_crop(job: dict[str, Any]) -> Path:
    for key in ("crop", "sourceCrop", "cropPath", "rowCrop", "imagePath", "previewPath"):
        value = job.get(key)
        if isinstance(value, str) and value:
            path = ROOT / value
            if path.exists():
                return path
    raise RuntimeError(
        f"No readable crop for page {job.get('pageNumber')} row {job.get('rowIndex')}"
    )


def smooth(values: Any, np: Any, radius: int = 2) -> Any:
    kernel = np.ones(radius * 2 + 1, dtype=float)
    kernel /= kernel.sum()
    return np.convolve(values, kernel, mode="same")


def row_features(gray: Any, np: Any) -> tuple[Any, Any, Any]:
    height, width = gray.shape
    x0 = max(0, int(round(width * 0.035)))
    x1 = min(width, int(round(width * 0.975)))
    band = gray[:, x0:x1].astype(np.float32)

    darkness = 255.0 - band.mean(axis=1)
    gradient = np.abs(np.gradient(band, axis=0)).mean(axis=1)

    dark_threshold = np.percentile(band, 38)
    dark_pixels = band <= dark_threshold
    continuity = dark_pixels.mean(axis=1)

    score = smooth(darkness + 0.45 * gradient + 45.0 * continuity, np, radius=2)
    return score, continuity, darkness


def candidate_rows_near_anchor(
    expected_y: float,
    search_radius: int,
    score: Any,
    continuity: Any,
    np: Any,
) -> list[tuple[int, float]]:
    height = len(score)
    lo = max(0, int(round(expected_y)) - search_radius)
    hi = min(height - 1, int(round(expected_y)) + search_radius)
    candidates: list[tuple[int, float]] = []

    for y in range(lo, hi + 1):
        left = score[y - 1] if y > 0 else score[y]
        right = score[y + 1] if y + 1 < height else score[y]
        if score[y] < left or score[y] < right:
            continue
        anchor_distance = abs(y - expected_y)
        continuity_bonus = 80.0 * float(continuity[y])
        value = float(score[y]) + continuity_bonus - 4.0 * anchor_distance
        candidates.append((y, value))

    if not candidates:
        best_y = lo + int(np.argmax(score[lo : hi + 1]))
        candidates.append((best_y, float(score[best_y])))

    candidates.sort(key=lambda item: item[1], reverse=True)
    return candidates[:12]


def choose_local_lattice(
    gray: Any,
    expected_rows: list[float],
    expected_spacing: float,
    np: Any,
) -> dict[str, Any]:
    score, continuity, darkness = row_features(gray, np)
    search_radius = max(4, int(round(expected_spacing * SEARCH_RADIUS_RATIO)))
    max_line_shift = max(3.0, expected_spacing * MAX_LINE_SHIFT_RATIO)

    per_line = [
        candidate_rows_near_anchor(row, search_radius, score, continuity, np)
        for row in expected_rows
    ]

    best_rows: list[int] = []
    best_objective = float("-inf")

    def visit(index: int, chosen: list[int], objective: float) -> None:
        nonlocal best_rows, best_objective
        if index == 6:
            gaps = [chosen[i + 1] - chosen[i] for i in range(5)]
            if min(gaps) < expected_spacing * MIN_SPACING_RATIO:
                return
            if max(gaps) > expected_spacing * MAX_SPACING_RATIO:
                return
            median_gap_deviation = median(abs(gap - expected_spacing) for gap in gaps)
            max_gap_deviation = max(abs(gap - expected_spacing) for gap in gaps)
            if median_gap_deviation > MAX_MEDIAN_GAP_DEVIATION:
                return
            if max_gap_deviation > MAX_SINGLE_GAP_DEVIATION:
                return

            anchor_shift = median(chosen[i] - expected_rows[i] for i in range(6))
            residuals = [
                abs((chosen[i] - expected_rows[i]) - anchor_shift)
                for i in range(6)
            ]
            if abs(anchor_shift) > expected_spacing * MAX_ANCHOR_SHIFT_RATIO:
                return
            if max(residuals) > max_line_shift:
                return

            geometry_penalty = 18.0 * median_gap_deviation + 8.0 * max(residuals)
            final_objective = objective - geometry_penalty
            if final_objective > best_objective:
                best_objective = final_objective
                best_rows = chosen.copy()
            return

        for y, value in per_line[index]:
            if chosen and y <= chosen[-1]:
                continue
            if chosen:
                gap = y - chosen[-1]
                if gap < expected_spacing * MIN_SPACING_RATIO:
                    continue
                if gap > expected_spacing * MAX_SPACING_RATIO:
                    continue
            visit(index + 1, [*chosen, y], objective + value)

    visit(0, [], 0.0)

    if len(best_rows) != 6:
        return {
            "rows": [],
            "passed": False,
            "reason": "no-valid-six-line-lattice",
            "anchorShiftPixels": None,
            "medianGapPixels": None,
            "medianGapDeviationPixels": None,
            "maxGapDeviationPixels": None,
            "minimumContinuity": None,
            "objective": None,
        }

    gaps = [best_rows[i + 1] - best_rows[i] for i in range(5)]
    anchor_shift = median(best_rows[i] - expected_rows[i] for i in range(6))
    median_gap_deviation = median(abs(gap - expected_spacing) for gap in gaps)
    max_gap_deviation = max(abs(gap - expected_spacing) for gap in gaps)
    minimum_continuity = min(float(continuity[y]) for y in best_rows)

    passed = (
        median_gap_deviation <= MAX_MEDIAN_GAP_DEVIATION
        and max_gap_deviation <= MAX_SINGLE_GAP_DEVIATION
        and abs(anchor_shift) <= expected_spacing * MAX_ANCHOR_SHIFT_RATIO
        and minimum_continuity >= MIN_HORIZONTAL_CONTINUITY
    )

    return {
        "rows": [float(y) for y in best_rows],
        "passed": passed,
        "reason": "registered" if passed else "weak-horizontal-continuity",
        "anchorShiftPixels": round(float(anchor_shift), 3),
        "medianGapPixels": round(float(median(gaps)), 3),
        "medianGapDeviationPixels": round(float(median_gap_deviation), 3),
        "maxGapDeviationPixels": round(float(max_gap_deviation), 3),
        "minimumContinuity": round(float(minimum_continuity), 6),
        "objective": round(float(best_objective), 3),
        "rowDarkness": [round(float(darkness[y]), 3) for y in best_rows],
    }


def draw_preview(
    cv2: Any,
    gray: Any,
    expected_rows: list[float],
    registered_rows: list[float],
    passed: bool,
) -> Any:
    preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    for index, value in enumerate(expected_rows, start=1):
        y = int(round(value))
        cv2.line(preview, (0, y), (preview.shape[1] - 1, y), (255, 0, 0), 1)
        cv2.putText(
            preview,
            f"E{index}",
            (4, max(12, y - 3)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            (255, 0, 0),
            1,
            cv2.LINE_AA,
        )

    color = (0, 255, 0) if passed else (0, 0, 255)
    for index, value in enumerate(registered_rows, start=1):
        y = int(round(value))
        cv2.line(preview, (0, y), (preview.shape[1] - 1, y), color, 2)
        cv2.putText(
            preview,
            f"R{index}",
            (42, max(12, y - 3)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.38,
            color,
            1,
            cv2.LINE_AA,
        )
    return preview


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    source = load_json(INPUT_PATH)
    jobs = source.get("recognitionJobs", [])
    if source.get("allCanonicalRowsPromoted") is not True:
        raise RuntimeError("V55 did not promote all canonical rows")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V55 complete measures 17-113 coverage did not pass")
    if not isinstance(jobs, list) or len(jobs) != EXPECTED_JOB_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_JOB_COUNT} v55 jobs, found {len(jobs or [])}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_jobs: list[dict[str, Any]] = []
    covered: set[int] = set()
    passed_count = 0

    print("Row-local six-string lattice registration v60 starting", flush=True)

    for job in jobs:
        crop_path = resolve_crop(job)
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            raise RuntimeError(f"Unable to read {crop_path.relative_to(ROOT)}")

        expected_rows = [float(value) for value in job.get("canonicalStringRowsPixels", [])]
        if len(expected_rows) != 6:
            raise RuntimeError(
                f"V55 canonical row count changed for page {job.get('pageNumber')} "
                f"row {job.get('rowIndex')}"
            )
        expected_spacing = float(job.get("canonicalMedianSpacingPixels", 18.4))
        result = choose_local_lattice(gray, expected_rows, expected_spacing, np)
        registered_rows = result.pop("rows")
        passed = bool(result["passed"])
        if passed:
            passed_count += 1

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)

        preview_name = (
            f"page-{int(job.get('pageNumber', 0)):02d}-"
            f"row-{int(job.get('rowIndex', 0)):02d}-registration.png"
        )
        preview_path = PREVIEW_DIR / preview_name
        preview = draw_preview(cv2, gray, expected_rows, registered_rows, passed)
        cv2.imwrite(str(preview_path), preview)

        output_jobs.append(
            {
                **job,
                "v60ExpectedCanonicalStringRowsPixels": [round(v, 3) for v in expected_rows],
                "v60RegisteredStringRowsPixels": [round(v, 3) for v in registered_rows],
                "v60RowLocalRegistrationPassed": passed,
                "v60RegistrationPreview": str(preview_path.relative_to(ROOT)),
                "v60Registration": result,
                "professionalFretGlyphRecognitionPerformed": False,
                "semanticNoteEventsExtracted": False,
            }
        )

        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, rows={len(registered_rows)}, "
            f"shift={result.get('anchorShiftPixels')}, passed={passed}",
            flush=True,
        )

    complete_coverage = covered == EXPECTED_MEASURES
    all_registered = passed_count == len(output_jobs) and complete_coverage
    output = {
        "diagnosticName": "Gomyway row-local six-string lattice registration v60",
        "sourceCanonicalRows": str(INPUT_PATH.relative_to(ROOT)),
        "recognitionJobsProcessed": len(output_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "jobsPassingRowLocalRegistration": passed_count,
        "allJobsRegistered": all_registered,
        "recognitionJobs": output_jobs,
        "approvedV55GeometryUsedAsAnchor": True,
        "rowLocalLatticeSearchPerformed": True,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": (
            "human-review-v60-row-local-string-lattice-previews"
            if all_registered
            else "inspect-v60-row-local-string-lattice-failures"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Row-local six-string lattice registration v60 complete")
    print(f"Recognition jobs processed: {len(output_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"Jobs passing row-local registration: {passed_count}")
    print(f"All jobs registered: {all_registered}")
    print("Approved V55 geometry used as anchor: True")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
