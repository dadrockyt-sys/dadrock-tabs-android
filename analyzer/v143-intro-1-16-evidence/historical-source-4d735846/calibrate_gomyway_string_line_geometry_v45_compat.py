"""Compatibility runner for the read-only v45 string-line geometry audit.

Some OpenCV builds return HoughLinesP results as an N x 4 array while
others return N x 1 x 4. The original v45 audit expected the latter.
This runner normalizes both forms without changing any source data,
locked events, thresholds, scoring rules, or promotion safeguards.
"""

from __future__ import annotations

from typing import Any


def main() -> None:
    try:
        import cv2
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            "Run: pip install opencv-python-headless numpy"
        ) from exc

    original_hough_lines_p = cv2.HoughLinesP

    def compatible_hough_lines_p(*args: Any, **kwargs: Any):
        lines = original_hough_lines_p(*args, **kwargs)
        if lines is None:
            return None

        array = np.asarray(lines)
        if array.size == 0:
            return array.reshape((0, 1, 4))

        if array.ndim == 2 and array.shape[1] == 4:
            return array.reshape((-1, 1, 4))

        if array.ndim == 3 and array.shape[1:] == (1, 4):
            return array

        if array.size % 4 != 0:
            raise RuntimeError(
                "Unexpected HoughLinesP result shape: "
                f"{array.shape}"
            )

        return array.reshape((-1, 1, 4))

    cv2.HoughLinesP = compatible_hough_lines_p

    from calibrate_gomyway_string_line_geometry_v45 import (
        main as run_v45,
    )

    run_v45()


if __name__ == "__main__":
    main()
