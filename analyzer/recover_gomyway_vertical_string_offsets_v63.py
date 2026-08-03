"""Recover displaced V55 six-string lattices as rigid vertical groups.

The V62 coordinate-frame contact sheets show that many approved V55 lattices use
correct string spacing but are vertically displaced onto lyrics, rhythm stems,
chord labels, or neighbouring notation. V63 therefore keeps the six-row spacing
and relative geometry locked and searches a broad vertical range for one shared
offset. It does not rediscover six independent lines.

This stage is read-only and diagnostic. It does not recognize fret values,
extract semantic note events, modify measures 1-16 or V7 events, use candidate
audio, or promote anything to production.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT_PATH = PUBLIC / "gomyway-v51-canonical-fret-recognition-input-v55.json"
AUDIT_PATH = PUBLIC / "gomyway-v55-v60-coordinate-frame-audit-v62.json"
OUTPUT_PATH = PUBLIC / "gomyway-vertical-string-offset-recovery-v63.json"
PREVIEW_DIR = PUBLIC / "gomyway-vertical-string-offset-recovery-v63"

EXPECTED_JOB_COUNT = 45
EXPECTED_MEASURES = set(range(17, 114))
SEARCH_MARGIN_RATIO = 0.35
MIN_SEARCH_PIXELS = 72
MAX_SEARCH_PIXELS = 220
MIN_LINE_CONTINUITY = 0.22
MIN_GROUP_CONTINUITY = 0.30
MIN_SCORE_MARGIN = 5.0


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


def smooth(values: Any, np: Any, radius: int = 1) -> Any:
    kernel = np.ones(radius * 2 + 1, dtype=float)
    kernel /= kernel.sum()
    return np.convolve(values, kernel, mode="same")


def build_row_features(gray: Any, np: Any) -> dict[str, Any]:
    height, width = gray.shape
    x0 = max(0, int(round(width * 0.035)))
    x1 = min(width, int(round(width * 0.975)))
    band = gray[:, x0:x1].astype(np.float32)

    darkness = 255.0 - band.mean(axis=1)
    gradient = np.abs(np.gradient(band, axis=0)).mean(axis=1)

    dark_threshold = np.percentile(band, 34)
    dark_pixels = band <= dark_threshold
    continuity = dark_pixels.mean(axis=1)

    # Long horizontal runs are the strongest staff-line evidence. Lyrics and
    # symbols may be dark, but usually do not remain dark across much of a row.
    run_continuity = np.zeros(height, dtype=float)
    for y in range(height):
        row = dark_pixels[y].astype(np.uint8)
        padded = np.pad(row, (1, 1))
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)
        longest = int((ends - starts).max()) if len(starts) else 0
        run_continuity[y] = longest / max(1, band.shape[1])

    # Vertical-stroke density penalizes lyrics, stems, and chord-name regions.
    vertical_gradient = np.abs(np.gradient(band, axis=1)).mean(axis=1)

    row_score = (
        45.0 * continuity
        + 120.0 * run_continuity
        + 0.18 * darkness
        + 0.20 * gradient
        - 0.10 * vertical_gradient
    )
    return {
        "score": smooth(row_score, np, radius=1),
        "continuity": continuity,
        "runContinuity": run_continuity,
        "darkness": darkness,
        "verticalGradient": vertical_gradient,
    }


def score_offset(
    offset: int,
    expected_rows: list[float],
    features: dict[str, Any],
    height: int,
) -> dict[str, Any] | None:
    rows = [int(round(value + offset)) for value in expected_rows]
    if min(rows) < 0 or max(rows) >= height:
        return None

    score = features["score"]
    continuity = features["continuity"]
    run_continuity = features["runContinuity"]
    darkness = features["darkness"]
    vertical_gradient = features["verticalGradient"]

    line_scores = [float(score[y]) for y in rows]
    line_continuities = [float(continuity[y]) for y in rows]
    line_runs = [float(run_continuity[y]) for y in rows]
    line_darkness = [float(darkness[y]) for y in rows]
    line_vertical = [float(vertical_gradient[y]) for y in rows]

    minimum_continuity = min(line_continuities)
    mean_continuity = sum(line_continuities) / 6.0
    mean_run = sum(line_runs) / 6.0

    # Reward all six rows contributing. A single excellent lyric baseline must
    # not outweigh five weak rows.
    weak_line_penalty = sum(max(0.0, MIN_LINE_CONTINUITY - value) for value in line_continuities)
    balance_penalty = max(line_scores) - min(line_scores)
    anchor_penalty = 0.018 * abs(offset)

    objective = (
        sum(line_scores)
        + 180.0 * mean_continuity
        + 260.0 * mean_run
        - 210.0 * weak_line_penalty
        - 0.16 * balance_penalty
        - anchor_penalty
    )

    return {
        "offsetPixels": offset,
        "rows": [float(y) for y in rows],
        "objective": float(objective),
        "minimumContinuity": minimum_continuity,
        "meanContinuity": mean_continuity,
        "meanRunContinuity": mean_run,
        "rowContinuity": line_continuities,
        "rowRunContinuity": line_runs,
        "rowDarkness": line_darkness,
        "rowVerticalGradient": line_vertical,
    }


def recover_rigid_offset(
    gray: Any,
    expected_rows: list[float],
    expected_spacing: float,
    np: Any,
) -> dict[str, Any]:
    height, _ = gray.shape
    features = build_row_features(gray, np)

    broad_radius = int(round(height * SEARCH_MARGIN_RATIO))
    broad_radius = max(MIN_SEARCH_PIXELS, broad_radius)
    broad_radius = min(MAX_SEARCH_PIXELS, broad_radius)

    valid_lo = int(max(-broad_radius, -min(expected_rows)))
    valid_hi = int(min(broad_radius, (height - 1) - max(expected_rows)))

    candidates: list[dict[str, Any]] = []
    for offset in range(valid_lo, valid_hi + 1):
        candidate = score_offset(offset, expected_rows, features, height)
        if candidate is not None:
            candidates.append(candidate)

    if not candidates:
        return {
            "recoveredRows": [],
            "passed": False,
            "reason": "no-valid-rigid-offset",
            "searchOffsetRangePixels": [valid_lo, valid_hi],
        }

    candidates.sort(key=lambda item: item["objective"], reverse=True)
    best = candidates[0]
    runner_up = candidates[1] if len(candidates) > 1 else None
    score_margin = (
        best["objective"] - runner_up["objective"] if runner_up is not None else best["objective"]
    )

    gaps = [best["rows"][i + 1] - best["rows"][i] for i in range(5)]
    median_gap = float(median(gaps))
    spacing_deviation = abs(median_gap - expected_spacing)

    passed = (
        best["meanContinuity"] >= MIN_GROUP_CONTINUITY
        and best["minimumContinuity"] >= MIN_LINE_CONTINUITY
        and score_margin >= MIN_SCORE_MARGIN
        and spacing_deviation <= 0.75
    )

    reason = "recovered" if passed else "weak-or-ambiguous-rigid-offset"
    return {
        "recoveredRows": best.pop("rows"),
        "passed": passed,
        "reason": reason,
        "searchOffsetRangePixels": [valid_lo, valid_hi],
        "scoreMargin": round(float(score_margin), 3),
        "expectedSpacingPixels": round(float(expected_spacing), 3),
        "recoveredMedianSpacingPixels": round(median_gap, 3),
        "spacingDeviationPixels": round(spacing_deviation, 3),
        "bestCandidate": {
            key: ([round(float(v), 6) for v in value] if isinstance(value, list) else round(float(value), 6))
            for key, value in best.items()
        },
        "runnerUpOffsetPixels": (
            int(runner_up["offsetPixels"]) if runner_up is not None else None
        ),
        "runnerUpObjective": (
            round(float(runner_up["objective"]), 3) if runner_up is not None else None
        ),
    }


def draw_preview(
    cv2: Any,
    gray: Any,
    expected_rows: list[float],
    recovered_rows: list[float],
    passed: bool,
) -> Any:
    preview = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    width = preview.shape[1]

    for index, value in enumerate(expected_rows, start=1):
        y = int(round(value))
        if 0 <= y < preview.shape[0]:
            cv2.line(preview, (0, y), (width - 1, y), (255, 0, 0), 1)
            cv2.putText(
                preview, f"V55-{index}", (4, max(13, y - 3)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 0), 1, cv2.LINE_AA,
            )

    color = (0, 255, 0) if passed else (0, 0, 255)
    for index, value in enumerate(recovered_rows, start=1):
        y = int(round(value))
        if 0 <= y < preview.shape[0]:
            cv2.line(preview, (0, y), (width - 1, y), color, 2)
            cv2.putText(
                preview, f"V63-{index}", (70, max(13, y - 3)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA,
            )
    return preview


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    source = load_json(INPUT_PATH)
    audit = load_json(AUDIT_PATH)
    jobs = source.get("recognitionJobs", [])

    if source.get("allCanonicalRowsPromoted") is not True:
        raise RuntimeError("V55 did not promote all canonical rows")
    if source.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V55 complete measures 17-113 coverage did not pass")
    if audit.get("coordinateFrameRepairApplied") is not False:
        raise RuntimeError("V62 must remain read-only")
    if not isinstance(jobs, list) or len(jobs) != EXPECTED_JOB_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_JOB_COUNT} V55 jobs, found {len(jobs or [])}")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    output_jobs: list[dict[str, Any]] = []
    covered: set[int] = set()
    recovered_count = 0
    nonzero_offsets = 0

    print("Rigid vertical six-string offset recovery V63 starting", flush=True)

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
        result = recover_rigid_offset(gray, expected_rows, expected_spacing, np)
        recovered_rows = result.pop("recoveredRows")
        passed = bool(result["passed"])
        if passed:
            recovered_count += 1
        offset = result.get("bestCandidate", {}).get("offsetPixels")
        if offset not in (None, 0, 0.0):
            nonzero_offsets += 1

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)

        preview_name = (
            f"page-{int(job.get('pageNumber', 0)):02d}-"
            f"row-{int(job.get('rowIndex', 0)):02d}-vertical-offset.png"
        )
        preview_path = PREVIEW_DIR / preview_name
        preview = draw_preview(cv2, gray, expected_rows, recovered_rows, passed)
        cv2.imwrite(str(preview_path), preview)

        output_jobs.append(
            {
                **job,
                "v63ExpectedCanonicalStringRowsPixels": [round(v, 3) for v in expected_rows],
                "v63RecoveredStringRowsPixels": [round(v, 3) for v in recovered_rows],
                "v63RigidVerticalOffsetRecoveryPassed": passed,
                "v63VerticalOffsetPreview": str(preview_path.relative_to(ROOT)),
                "v63VerticalOffsetRecovery": result,
                "professionalFretGlyphRecognitionPerformed": False,
                "semanticNoteEventsExtracted": False,
            }
        )

        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"measures={measures}, offset={offset}, rows={len(recovered_rows)}, passed={passed}",
            flush=True,
        )

    complete_coverage = covered == EXPECTED_MEASURES
    all_recovered = recovered_count == len(output_jobs) and complete_coverage
    output = {
        "diagnosticName": "Gomyway rigid vertical six-string offset recovery V63",
        "sourceCanonicalRows": str(INPUT_PATH.relative_to(ROOT)),
        "sourceCoordinateFrameAudit": str(AUDIT_PATH.relative_to(ROOT)),
        "recognitionJobsProcessed": len(output_jobs),
        "uniqueMeasures17To113Covered": len(covered),
        "complete17To113CoveragePassed": complete_coverage,
        "jobsPassingRigidVerticalOffsetRecovery": recovered_count,
        "jobsUsingNonzeroVerticalOffset": nonzero_offsets,
        "allJobsRecovered": all_recovered,
        "recognitionJobs": output_jobs,
        "approvedV55SpacingPreserved": True,
        "rigidGroupOffsetSearchPerformed": True,
        "independentLineRediscoveryPerformed": False,
        "coordinateFrameRepairApplied": False,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": "human-review-v63-vertical-offset-previews",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Rigid vertical six-string offset recovery V63 complete")
    print(f"Recognition jobs processed: {len(output_jobs)}")
    print(f"Unique measures 17-113 covered: {len(covered)}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"Jobs passing rigid vertical offset recovery: {recovered_count}")
    print(f"Jobs using nonzero vertical offset: {nonzero_offsets}")
    print(f"All jobs recovered: {all_recovered}")
    print("Approved V55 spacing preserved: True")
    print("Rigid group offset search performed: True")
    print("Independent line rediscovery performed: False")
    print("Coordinate-frame repair applied: False")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("V7 events modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print("Next required stage: human-review-v63-vertical-offset-previews")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
