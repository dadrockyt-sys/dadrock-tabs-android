"""Recalibrate v51 TAB string rows using long-horizontal-rule evidence.

Human review showed that v51 could select six evenly spaced rhythm/text bands
instead of the six printed TAB rules. This read-only correction searches for six
long, parallel horizontal rules at the locked professional spacing and rejects
rows lacking sufficient continuity. It does not recognize frets or modify the
protected measures 1-16.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INPUT = PUBLIC / "gomyway-professional-string-row-coordinates-v51.json"
OUTPUT = PUBLIC / "gomyway-professional-string-row-coordinates-v52.json"
PREVIEWS = PUBLIC / "gomyway-professional-string-row-coordinates-v52"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def horizontal_rule_profile(gray: Any, cv2: Any, np: Any) -> Any:
    """Return per-y support for long printed horizontal rules."""
    height, width = gray.shape
    x0 = max(0, int(width * 0.03))
    x1 = min(width, int(width * 0.98))
    band = gray[:, x0:x1]

    # Local thresholding handles dark PDF backgrounds and uneven screenshots.
    binary = cv2.adaptiveThreshold(
        band,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        7,
    )

    # Preserve only strokes that remain horizontal for a meaningful fraction of
    # the row. Digits, lyrics, stems and bend marks are largely removed.
    kernel_width = max(25, int(binary.shape[1] * 0.10))
    horizontal = cv2.morphologyEx(
        binary,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, 1)),
    )

    support = (horizontal > 0).mean(axis=1).astype(np.float32)
    # A three-pixel maximum absorbs anti-aliasing and slight line thickness.
    return np.maximum.reduce(
        [support, np.roll(support, 1), np.roll(support, -1)]
    )


def choose_rows(profile: Any, spacing: float, np: Any) -> tuple[list[float], float, float]:
    height = len(profile)
    best_rows: list[float] = []
    best_objective = float("-inf")
    best_continuity = 0.0

    for trial_spacing in np.linspace(spacing * 0.82, spacing * 1.18, 37):
        span = trial_spacing * 5
        for top in range(2, max(3, int(height - span - 2))):
            rows: list[float] = []
            supports: list[float] = []
            for index in range(6):
                expected = top + index * trial_spacing
                lo = max(0, int(round(expected)) - 2)
                hi = min(height - 1, int(round(expected)) + 2)
                y = lo + int(np.argmax(profile[lo : hi + 1]))
                rows.append(float(y))
                supports.append(float(profile[y]))

            if len(set(rows)) != 6:
                continue
            ordered = sorted(rows)
            gaps = np.diff(ordered)
            gap_error = float(np.mean(np.abs(gaps - spacing)))
            continuity = float(median(supports))
            minimum_support = float(min(supports))

            # Six genuine TAB rules should each retain long horizontal support.
            objective = (
                12.0 * continuity
                + 5.0 * minimum_support
                - 0.45 * gap_error
            )
            if objective > best_objective:
                best_objective = objective
                best_rows = ordered
                best_continuity = continuity

    if len(best_rows) != 6:
        return [], 999.0, 0.0

    gaps = [best_rows[i + 1] - best_rows[i] for i in range(5)]
    deviation = float(median(abs(gap - spacing) for gap in gaps))
    return best_rows, deviation, best_continuity


def main() -> None:
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Run: pip install numpy opencv-python-headless") from exc

    source = load_json(INPUT)
    jobs = source.get("recognitionJobs", [])
    if not isinstance(jobs, list) or len(jobs) != 45:
        raise RuntimeError(f"Expected 45 v51 jobs, found {len(jobs or [])}")

    spacing = float(source.get("expectedStringSpacingPixels", 0.0))
    if spacing <= 0:
        raise RuntimeError("V51 expected string spacing is unavailable")

    PREVIEWS.mkdir(parents=True, exist_ok=True)
    corrected: list[dict[str, Any]] = []
    passed_count = 0

    print("Professional horizontal-rule string-row recalibration v52 starting")

    for job in jobs:
        crop_path = ROOT / str(job.get("crop") or "")
        gray = cv2.imread(str(crop_path), cv2.IMREAD_GRAYSCALE)
        rows: list[float] = []
        deviation = 999.0
        continuity = 0.0

        if gray is not None:
            profile = horizontal_rule_profile(gray, cv2, np)
            rows, deviation, continuity = choose_rows(profile, spacing, np)

        # Continuity is intentionally required in addition to spacing. This is
        # the safeguard v51 lacked and prevents rhythm/text bands from passing.
        passed = (
            len(rows) == 6
            and deviation <= 2.5
            and continuity >= 0.20
        )
        if passed:
            passed_count += 1

        preview_path = None
        if gray is not None:
            annotated = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            color = (0, 255, 255) if passed else (0, 0, 255)
            for index, value in enumerate(rows, start=1):
                y = int(round(value))
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
            name = (
                f"page-{int(job.get('pageNumber', 0)):02d}-"
                f"row-{int(job.get('rowIndex', 0)):02d}-strings.png"
            )
            preview = PREVIEWS / name
            cv2.imwrite(str(preview), annotated)
            preview_path = str(preview.relative_to(ROOT))

        corrected.append(
            {
                **job,
                "v51StringRowsPixels": job.get("stringRowsPixels", []),
                "stringRowsPixels": [round(value, 3) for value in rows],
                "medianSpacingDeviationPixels": round(deviation, 6),
                "medianHorizontalRuleContinuity": round(continuity, 6),
                "sixStringRowsPopulated": len(rows) == 6,
                "rowGeometryPassed": passed,
                "preview": preview_path,
                "recognitionPerformed": False,
                "recognizedGlyphs": [],
            }
        )
        print(
            f"Page {job.get('pageNumber')} row {job.get('rowIndex')}: "
            f"strings={len(rows)}, deviation={deviation:.3f}, "
            f"continuity={continuity:.3f}, passed={passed}",
            flush=True,
        )

    all_passed = passed_count == len(jobs)
    output = {
        "diagnosticName": "Gomyway professional string-row recalibration v52",
        "source": str(INPUT.relative_to(ROOT)),
        "expectedStringSpacingPixels": spacing,
        "recognitionJobsInspected": len(jobs),
        "jobsPassingHorizontalRuleGeometry": passed_count,
        "allJobsPassedHorizontalRuleGeometry": all_passed,
        "recognitionJobs": corrected,
        "professionalFretGlyphRecognitionPerformed": False,
        "semanticNoteEvents17To113Extracted": False,
        "lockedMeasures1To16Modified": False,
        "candidateAudioUsed": False,
        "readyForScoring": False,
        "productionPromotionAllowed": False,
        "humanVisualValidationRequired": True,
        "nextRequiredStage": (
            "human-review-v52-horizontal-rule-previews"
            if all_passed
            else "inspect-v52-horizontal-rule-failures-v53"
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print("Professional horizontal-rule string-row recalibration v52 complete")
    print(f"Recognition jobs inspected: {len(jobs)}")
    print(f"Jobs passing horizontal-rule geometry: {passed_count}")
    print(f"All jobs passed horizontal-rule geometry: {all_passed}")
    print("Professional fret glyph recognition performed: False")
    print("Semantic note events 17-113 extracted: False")
    print("Locked measures 1-16 modified: False")
    print("Candidate audio used: False")
    print("Ready for scoring: False")
    print("Production promotion allowed: False")
    print("Human visual validation required: True")
    print(f"Next required stage: {output['nextRequiredStage']}")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print(f"Previews: {PREVIEWS.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
