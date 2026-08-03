"""Recover tab-system rows with multi-scale horizontal staff evidence.

V65 showed that every V64 job failed the two horizontal-run gates, while only
12/45 also failed spacing. The V64 longest-single-run metric is therefore the
wrong evidence model for these anti-aliased, notation-interrupted staff lines.

V66 keeps the approved V55 spacing, rigid six-row lattice, read-only traversal,
and human-review requirement. It changes only horizontal evidence: short gaps
from fret digits, bends, ties, bar lines, and notation are bridged at multiple
scales before measuring row coverage. Lyrics and controls still cannot pass
unless six rows appear at the approved spacing.
"""

from __future__ import annotations

from typing import Any

import recover_gomyway_tab_system_bands_v64 as v64


# Duplicate neighbouring offsets may resolve to the same six-row lattice.
v64.MIN_OBJECTIVE_MARGIN = 0.0

# Multi-scale coverage is less numerically extreme than one uninterrupted run.
v64.MIN_ROW_RUN = 0.18
v64.MIN_MEAN_RUN = 0.26
v64.MIN_ROWS_WITH_RUN = 5


def build_staff_features_multiscale(gray: Any, cv2: Any, np: Any) -> dict[str, Any]:
    height, width = gray.shape
    x0 = max(0, int(round(width * 0.035)))
    x1 = min(width, int(round(width * 0.975)))
    band = gray[:, x0:x1]

    threshold = max(125.0, float(np.percentile(band, 72)))
    bright = (band >= threshold).astype(np.uint8)

    # A small vertical close consolidates anti-aliased one/two-pixel staff lines.
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 3))
    consolidated = cv2.morphologyEx(bright, cv2.MORPH_CLOSE, vertical_kernel)

    # Bridge notation interruptions at two scales. The larger scale remains far
    # below the width of lyrical phrases and cannot by itself invent six lines.
    widths = [
        max(9, int(round(band.shape[1] * 0.012))),
        max(17, int(round(band.shape[1] * 0.035))),
    ]
    closed_masks = []
    for close_width in widths:
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (close_width, 1))
        closed_masks.append(cv2.morphologyEx(consolidated, cv2.MORPH_CLOSE, kernel))

    run = np.zeros(height, dtype=float)
    occupancy = np.zeros(height, dtype=float)
    for y in range(height):
        row_scores = []
        for mask in closed_masks:
            longest = v64.longest_true_run(mask[y], np) / max(1, mask.shape[1])
            coverage = float(mask[y].mean())
            row_scores.append(0.65 * longest + 0.35 * coverage)
        run[y] = max(row_scores)
        occupancy[y] = float(consolidated[y].mean())

    run = v64.v63.smooth(run, np, radius=1)
    occupancy = v64.v63.smooth(occupancy, np, radius=1)
    return {
        "run": run,
        "occupancy": occupancy,
        "threshold": threshold,
        "xRange": [x0, x1],
    }


v64.build_staff_features = build_staff_features_multiscale
v64.OUTPUT_PATH = v64.PUBLIC / "gomyway-tab-system-band-recovery-v66.json"
v64.PREVIEW_DIR = v64.PUBLIC / "gomyway-tab-system-band-recovery-v66"


if __name__ == "__main__":
    v64.main()
