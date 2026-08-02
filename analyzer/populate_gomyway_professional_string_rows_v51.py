"""Populate six professional TAB string-row coordinates for v49 jobs.

This read-only stage uses the human-approved v47 spacing consensus and each
canonical row crop to locate six nearly parallel TAB string lines. It prepares
coordinates only; it does not recognize fret values, extract semantic events,
modify measures 1-16, or use candidate audio.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
JOBS_PATH = PUBLIC / "gomyway-professional-fret-recognition-jobs-v49.json"
CONSENSUS_PATH = PUBLIC / "gomyway-string-line-geometry-consensus-v46.json"
OUTPUT_PATH = PUBLIC / "gomyway-professional-string-row-coordinates-v51.json"
PREVIEW_DIR = PUBLIC / "gomyway-professional-string-row-coordinates-v51"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def smooth(values: Any, np: Any, radius: int = 2) -> Any:
    kernel = np.ones(radius * 2 + 1, dtype=float)
    kernel /= kernel.sum()
    return np.convolve(values, kernel, mode="same")


def choose_six_rows(gray: Any, expected_spacing: float, np: Any) -> tuple[list[float], float]:
    height, width = gray.shape
    x0 = max(0, round(width * 0.04))
    x1 = min(width, round(width * 0.97))
    band = gray[:, x0:x1].astype(np.float32)

    # Dark horizontal TAB rules produce strong row-wise darkness. Mild gradient
    # support helps when the printed rule is light but has crisp upper/lower edges.
    darkness = 255.0 - band.mean(axis=1)
    gradient = np.abs(np.gradient(band, axis=0)).mean(axis=1)
    score = smooth(darkness + 0.35 * gradient, np, radius=2)

    spacing_min = max(4.0, expected_spacing * 0.72)
    spacing_max = expected_spacing * 1.28
    best_rows: list[float] = []
    best_score = float("-inf")

    # Evaluate every plausible top-line anchor and a small spacing range around
    # the locked professional consensus. Each expected line may move ±2 pixels.
    for spacing in np.linspace(spacing_min, spacing_max, 45):
        total_span = spacing * 5
        max_top = int(height - total_span - 1)
        if max_top <= 1:
            continue
        for top in range(1, max_top):
            rows: list[float] = []
            value = 0.0
            for index in range(6):
                expected = top + index * spacing
                lo = max(0, int(round(expected)) - 2)
                hi = min(height - 1, int(round(expected)) + 2)
                local_index = lo + int(np.argmax(score[lo : hi + 1]))
                rows.append(float(local_index))
                value += float(score[local_index])

            gaps = np.diff(rows)
            gap_penalty = float(np.mean(np.abs(gaps - expected_spacing)))
            duplicate_penalty = 1000.0 if len(set(rows)) != 6 else 0.0
            objective = value - 5.0 * gap_penalty - duplicate_penalty
            if objective > best_score:
                best_score = objective
                best_rows = rows

    if len(best_rows) != 6:
        return [], 999.0

    # Lines must be strictly ordered and close to the approved spacing model.
    ordered = sorted(best_rows)
    gaps = [ordered[i + 1] - ordered[i] for i in range(5)]
    deviation = float(median(abs(gap - expected_spacing) for gap in gaps))
    return ordered, deviation


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    jobs_data = load_json(JOBS_PATH)
    consensus = load_json(CONSENSUS_PATH)

    jobs = jobs_data.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 v49 jobs, found {len(jobs or [])}")
    if jobs_data.get("complete17To113CoveragePassed") is not True:
        raise RuntimeError("V49 complete measures 17-113 coverage did not pass")
    if consensus.get("geometryConsensusPassed") is not True:
        raise RuntimeError("V46 string-line geometry consensus did not pass")

    expected_spacing = float(consensus.get("medianStringSpacingPixels", 0.0))
    if expected_spacing <= 0:
        raise RuntimeError("V46 median string spacing is unavailable")

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    populated: list[dict[str, Any]] = []
    ready_count = 0
    covered: set[int] = set()

    print("Professional six-string row coordinate population v51 starting", flush=True)

    for job in jobs:
        crop_value = job.get("crop")
        crop_path = ROOT / str(crop_value or "")
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            rows: list[float] = []
            deviation = 999.0
        else:
            rows, deviation = choose_six_rows(gray, expected_spacing, np)

        passed = len(rows) == 6 and deviation <= 2.5
        if passed:
            ready_count += 1

        measures = [int(value) for value in job.get("measures", [])]
        covered.update(measures)

        preview_path = None
        if gray is not None:
            annotated = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            for index, y_value in enumerate(rows, start=1):
                y = int(round(y_value))
                color = (0, 255, 255) if passed else (0, 0, 255)
                cv2.line(annotated, (0, y), (annotated.shape[1] - 1, y), color, 2)
                cv2.putText(
                    annotated,
                    str(index),
                    (5, max(12, y - 3)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    color,
                    1,
                    cv2.LINE_AA,
                )
            preview_file = (
                f"page-{int(job.get('pageNumber', 0)):02d}-"
                f"row-{int(job.get('rowIndex', 0)):02d}-strings.png"
            )
            preview_full = PREVIEW_DIR / preview_file
            cv2.imwrite(str(preview_full), annotated)
            preview_path = str(preview_full.relative_to(ROOT))

        populated.append(
            {
                **job,
                "stringRowsPixels": [round(value, 3) for value in rows],
                "expectedStringSpacingPixels": round(expected_spacing, 6),
                "medianSpacingDeviationPixels": round(deviation, 6),
                "sixStringRowsPopulated": len(rows) == 6,
                "rowGeometryPassed": passed,
                "preview": preview_path,
                "recognitionPerformed": False,
                "recognizedGlyphs": [],
            }
        )
        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"strings={len(rows)}, deviation={deviation:.3f}, passed={passed}",
            flush=True,
        )

    expected_measures = set(range(17, 114))
    complete_coverage = covered == expected_measures
    all_ready = ready_count == len(jobs) and complete_coverage

    output = {
        "diagnosticName": "Gomyway professional six-string row coordinates v51",
        "recognitionJobsSource": str(JOBS_PATH.relative_to(ROOT)),
        "geometryConsensusSource": str(CONSENSUS_PATH.relative_to(ROOT)),
        "expectedStringSpacingPixels": round(expected_spacing, 6),
        "recognitionJobsInspected": len(jobs),
        "jobsWithSixStringRows": sum(
            1 for job in populated if job["sixStringRowsPopulated"]
        ),
        "jobsPassingRowGeometry": ready_count,
        "complete17To113CoveragePassed": complete_coverage,
        "allJobsReadyForTemplateMatching": all_ready,
        "recognitionJobs": populated,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": (
            "human-review-v51-string-row-coordinate-previews"
            if all_ready
            else "inspect-v51-string-row-coordinate-failures-v52"
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional six-string row coordinate population v51 complete")
    print(f"Recognition jobs inspected: {len(jobs)}")
    print(f"Jobs with six string rows: {output['jobsWithSixStringRows']}")
    print(f"Jobs passing row geometry: {ready_count}")
    print(f"Complete 17-113 coverage passed: {complete_coverage}")
    print(f"All jobs ready for template matching: {all_ready}")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
