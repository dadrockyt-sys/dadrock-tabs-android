#!/usr/bin/env python3
"""Validate portable preprocessing invariants against the frozen reference receipt.

Raw CQT float-byte SHA256 values are intentionally diagnostic only because GitHub-hosted
CPU/FFT implementations can differ in least-significant bits across runners even with the
same frozen package versions. The authoritative numerical check is Astra-vs-pinned-source
parity within the same runtime.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def require_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label} mismatch: {actual!r} != {expected!r}")


def require_close(actual: float, expected: float, tolerance: float, label: str) -> None:
    if not math.isfinite(actual) or abs(actual - expected) > tolerance:
        raise AssertionError(
            f"{label} mismatch: {actual!r} vs {expected!r}, tolerance={tolerance}"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frozen", required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    frozen = json.loads(Path(args.frozen).read_text(encoding="utf-8"))
    candidate = json.loads(Path(args.candidate).read_text(encoding="utf-8"))

    for key in (
        "schema",
        "checkpointLoaded",
        "modelInvoked",
        "syntheticAudioOnly",
        "contract",
        "runtime",
        "sourceBlobs",
        "sourceRevision",
    ):
        require_equal(candidate[key], frozen[key], key)

    for key in ("syntheticAudio", "normalizedAudio"):
        require_equal(candidate[key]["shape"], frozen[key]["shape"], f"{key}.shape")
        require_equal(candidate[key]["dtype"], frozen[key]["dtype"], f"{key}.dtype")
        require_equal(candidate[key]["sha256"], frozen[key]["sha256"], f"{key}.sha256")

    for key in ("features", "modelWindows"):
        require_equal(candidate[key]["shape"], frozen[key]["shape"], f"{key}.shape")
        require_equal(candidate[key]["dtype"], frozen[key]["dtype"], f"{key}.dtype")
        require_close(candidate[key]["min"], frozen[key]["min"], 1e-6, f"{key}.min")
        require_close(candidate[key]["max"], frozen[key]["max"], 1e-6, f"{key}.max")

    tolerance = 1e-7
    for key, value in candidate["maxAbsoluteDifference"].items():
        if not math.isfinite(value) or value > tolerance:
            raise AssertionError(
                f"source parity failed for {key}: {value} > {tolerance}"
            )

    print("TABCNN_PREPROCESSING_PORTABLE_CONTRACT=PASS")
    print(f"TABCNN_PREPROCESSING_SOURCE_PARITY_TOLERANCE={tolerance}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
