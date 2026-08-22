"""Recover V55 six-string lattices only inside real tablature-system bands.

V63 proved that broad vertical scoring can be distracted by lyrics, rhythm stems,
empty space, adjacent systems, and the player footer. V64 keeps the approved V55
six-string spacing locked, but first searches for six regularly spaced bright
horizontal staff lines. It then evaluates rigid offsets only where a complete
staff band is present.

This is read-only diagnostic work. It does not recognize fret values, extract
semantic events, modify measures 1-16 or V7 events, use candidate audio, or
promote anything to production.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

import recover_gomyway_vertical_string_offsets_v63_fixed as v63_fixed  # patches uint8 run bug
import recover_gomyway_vertical_string_offsets_v63 as v63

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-tab-system-band-recovery-v64.json"
PREVIEW_DIR = PUBLIC / "gomyway-tab-system-band-recovery-v64"

MIN_ROW_RUN = 0.30
MIN_MEAN_RUN = 0.40
MIN_ROWS_WITH_RUN = 5
MAX_LOCAL_ADJUST = 2
PROXIMITY_WEIGHT = 0.025
MIN_OBJECTIVE_MARGIN = 1.5


def longest_true_run(row: Any, np: Any) -> int:
    signed = row.astype(np.int16)
    padded = np.pad(signed, (1, 1), constant_values=0)
    changes = np.diff(padded)
    starts = np.flatnonzero(changes == 1)
    ends = np.flatnonzero(changes == -1)
    count = min(len(starts), len(ends))
    if not count:
        return 0
    return int((ends[:count] - starts[:count]).max())


def build_staff_features(gray: Any, cv2: Any, np: Any) -> dict[str, Any]:
    height, width = gray.shape
    x0 = max(0, int(round(width * 0.035)))
    x1 = min(width, int(round(width * 0.975)))
    band = gray[:, x0:x1]

    # Staff lines are light on the dark professional reference. A percentile
    # threshold adapts to screenshots while the fixed floor rejects background.
    threshold = max(135.0, float(np.percentile(band, 78)))
    bright = (band >= threshold).astype(np.uint8)

    # Bridge fret digits and small notation interruptions without turning words
    # or isolated player icons into page-wide horizontal staff evidence.
    close_width = max(11, int(round(band.shape[1] * 0.018)))
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_width, 1))
    closed = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, kernel)

    run = np.zeros(height, dtype=float)
    occupancy = np.zeros(height, dtype=float)
    for y in range(height):
        run[y] = longest_true_run(closed[y], np) / max(1, closed.shape[1])
        occupancy[y] = float(bright[y].mean())

    # Small vertical smoothing tolerates anti-aliased one- or two-pixel lines.
    run = v63.smooth(run, np, radius=1)
    occupancy = v63.smooth(occupancy, np, radius=1)
    return {
        "run": run,
        "occupancy": occupancy,
        "threshold": threshold,
        "xRange": [x0, x1],
    }


def best_local_row(target: float, run: Any, occupancy: Any, height: int) -> tuple[int, float, float]:
    center = int(round(target))
    candidates: list[tuple[float, int, float, float]] = []
    for delta in range(-MAX_LOCAL_ADJUST, MAX_LOCAL_ADJUST + 1):
        y = center + delta
        if 0 <= y < height:
            objective = 100.0 * float(run[y]) + 15.0 * float(occupancy[y]) - 0.4 * abs(delta)
            candidates.append((objective, y, float(run[y]), float(occupancy[y])))
    if not candidates:
        return center, 0.0, 0.0
    candidates.sort(reverse=True)
    _, y, row_run, row_occupancy = candidates[0]
    return y, row_run, row_occupancy


def recover_tab_system_band(
    gray: Any,
    expected_rows: list[float],
    expected_spacing: float,
    np: Any,
) -> dict[str, Any]:
    import cv2  # type: ignore

    height, _ = gray.shape
    features = build_staff_features(gray, cv2, np)
    run = features["run"]
    occupancy = features["occupancy"]

    broad_radius = min(v63.MAX_SEARCH_PIXELS, max(v63.MIN_SEARCH_PIXELS, int(round(height * 0.42))))
    valid_lo = int(max(-broad_radius, -min(expected_rows)))
    valid_hi = int(min(broad_radius, (height - 1) - max(expected_rows)))

    candidates: list[dict[str, Any]] = []
    expected_center = float(sum(expected_rows) / 6.0)

    for offset in range(valid_lo, valid_hi + 1):
        rows: list[float] = []
        row_runs: list[float] = []
        row_occupancies: list[float] = []
        for value in expected_rows:
            y, row_run, row_occupancy = best_local_row(value + offset, run, occupancy, height)
            rows.append(float(y))
            row_runs.append(row_run)
            row_occupancies.append(row_occupancy)

        gaps = [rows[i + 1] - rows[i] for i in range(5)]
        gap_median = float(median(gaps))
        gap_deviation = max(abs(gap - expected_spacing) for gap in gaps)
        rows_with_run = sum(value >= MIN_ROW_RUN for value in row_runs)
        mean_run = float(sum(row_runs) / 6.0)
        minimum_run = float(min(row_runs))
        mean_occupancy = float(sum(row_occupancies) / 6.0)
        recovered_center = float(sum(rows) / 6.0)

        # Complete six-line staff evidence dominates. Distance from V55 is only
        # a tie-breaker so genuinely displaced systems can still be recovered.
        objective = (
            220.0 * mean_run
            + 35.0 * minimum_run
            + 35.0 * mean_occupancy
            + 8.0 * rows_with_run
            - 18.0 * gap_deviation
            - PROXIMITY_WEIGHT * abs(recovered_center - expected_center)
        )
        candidates.append(
            {
                "offsetPixels": offset,
                "rows": rows,
                "objective": objective,
                "rowRunContinuity": row_runs,
                "rowOccupancy": row_occupancies,
                "rowsWithStrongHorizontalEvidence": rows_with_run,
                "meanRunContinuity": mean_run,
                "minimumRunContinuity": minimum_run,
                "meanBrightOccupancy": mean_occupancy,
                "medianSpacingPixels": gap_median,
                "maximumSpacingDeviationPixels": gap_deviation,
            }
        )

    candidates.sort(key=lambda item: item["objective"], reverse=True)
    if not candidates:
        return {
            "recoveredRows": [],
            "passed": False,
            "reason": "no-tab-system-band-candidate",
            "searchOffsetRangePixels": [valid_lo, valid_hi],
        }

    best = candidates[0]
    runner = candidates[1] if len(candidates) > 1 else None
    margin = best["objective"] - runner["objective"] if runner else best["objective"]
    spacing_ok = best["maximumSpacingDeviationPixels"] <= 2.25
    evidence_ok = (
        best["rowsWithStrongHorizontalEvidence"] >= MIN_ROWS_WITH_RUN
        and best["meanRunContinuity"] >= MIN_MEAN_RUN
    )
    passed = bool(spacing_ok and evidence_ok and margin >= MIN_OBJECTIVE_MARGIN)

    return {
        "recoveredRows": best.pop("rows"),
        "passed": passed,
        "reason": "tab-system-band-recovered" if passed else "no-complete-confident-tab-system-band",
        "searchOffsetRangePixels": [valid_lo, valid_hi],
        "scoreMargin": round(float(margin), 3),
        "expectedSpacingPixels": round(float(expected_spacing), 3),
        "brightThreshold": round(float(features["threshold"]), 3),
        "horizontalSearchRangePixels": features["xRange"],
        "bestCandidate": {
            key: ([round(float(v), 6) for v in value] if isinstance(value, list) else round(float(value), 6))
            for key, value in best.items()
        },
        "runnerUpOffsetPixels": int(runner["offsetPixels"]) if runner else None,
        "runnerUpObjective": round(float(runner["objective"]), 3) if runner else None,
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
            cv2.putText(preview, f"V55-{index}", (4, max(13, y - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 0, 0), 1, cv2.LINE_AA)
    color = (0, 255, 0) if passed else (0, 0, 255)
    for index, value in enumerate(recovered_rows, start=1):
        y = int(round(value))
        if 0 <= y < preview.shape[0]:
            cv2.line(preview, (0, y), (width - 1, y), color, 2)
            cv2.putText(preview, f"V64-{index}", (72, max(13, y - 3)), cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1, cv2.LINE_AA)
    return preview


def main() -> None:
    # Reuse V63's protected read-only job traversal and safety assertions, while
    # replacing only the recovery method, preview renderer, and output location.
    v63.OUTPUT_PATH = OUTPUT_PATH
    v63.PREVIEW_DIR = PREVIEW_DIR
    v63.recover_rigid_offset = recover_tab_system_band
    v63.draw_preview = draw_preview
    v63.main()

    data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    data["diagnosticName"] = "Gomyway tab-system-constrained six-string recovery V64"
    data["tabSystemBandDetectionPerformed"] = True
    data["broadUnconstrainedVerticalScoringPerformed"] = False
    data["lyricsRhythmAndFooterExclusionRequired"] = True
    data["nextRequiredStage"] = "human-review-v64-tab-system-band-previews"
    for job in data.get("recognitionJobs", []):
        job["v64ExpectedCanonicalStringRowsPixels"] = job.get("v63ExpectedCanonicalStringRowsPixels", [])
        job["v64RecoveredStringRowsPixels"] = job.get("v63RecoveredStringRowsPixels", [])
        job["v64TabSystemBandRecoveryPassed"] = job.get("v63RigidVerticalOffsetRecoveryPassed", False)
        job["v64TabSystemBandPreview"] = job.get("v63VerticalOffsetPreview")
        job["v64TabSystemBandRecovery"] = job.get("v63VerticalOffsetRecovery", {})
    OUTPUT_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    print("V64 tab-system-constrained recovery metadata finalized")
    print(f"Output: {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Previews: {PREVIEW_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
