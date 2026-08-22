"""Run V63 with corrected horizontal-run detection.

NumPy.diff on uint8 wraps -1 transitions to 255, so the original V63 run
counter could produce starts without matching ends. This wrapper replaces only
that feature builder, then runs the unchanged read-only V63 diagnostic.
"""

from __future__ import annotations

from typing import Any

import recover_gomyway_vertical_string_offsets_v63 as v63


def build_row_features_fixed(gray: Any, np: Any) -> dict[str, Any]:
    height, width = gray.shape
    x0 = max(0, int(round(width * 0.035)))
    x1 = min(width, int(round(width * 0.975)))
    band = gray[:, x0:x1].astype(np.float32)

    darkness = 255.0 - band.mean(axis=1)
    gradient = np.abs(np.gradient(band, axis=0)).mean(axis=1)

    dark_threshold = np.percentile(band, 34)
    dark_pixels = band <= dark_threshold
    continuity = dark_pixels.mean(axis=1)

    run_continuity = np.zeros(height, dtype=float)
    for y in range(height):
        # Signed integers are required so falling edges remain -1 instead of
        # wrapping to 255 as they do with uint8.
        row = dark_pixels[y].astype(np.int16)
        padded = np.pad(row, (1, 1), constant_values=0)
        changes = np.diff(padded)
        starts = np.flatnonzero(changes == 1)
        ends = np.flatnonzero(changes == -1)

        pair_count = min(len(starts), len(ends))
        if pair_count:
            run_lengths = ends[:pair_count] - starts[:pair_count]
            longest = int(run_lengths.max())
        else:
            longest = 0
        run_continuity[y] = longest / max(1, band.shape[1])

    vertical_gradient = np.abs(np.gradient(band, axis=1)).mean(axis=1)

    row_score = (
        45.0 * continuity
        + 120.0 * run_continuity
        + 0.18 * darkness
        + 0.20 * gradient
        - 0.10 * vertical_gradient
    )
    return {
        "score": v63.smooth(row_score, np, radius=1),
        "continuity": continuity,
        "runContinuity": run_continuity,
        "darkness": darkness,
        "verticalGradient": vertical_gradient,
    }


v63.build_row_features = build_row_features_fixed


if __name__ == "__main__":
    v63.main()
