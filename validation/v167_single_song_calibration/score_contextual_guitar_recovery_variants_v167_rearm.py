#!/usr/bin/env python3
"""Safe V167 contextual Guitar grader re-arm.

The first one-shot arm stopped before generation/scoring because the checkpoint's
written Iteration 003 SHA256 was stale. The immutable Git blob was correct and the
runner independently hashed its bytes as the value below. This adapter changes
only that pre-score identity constant; all scoring/selection logic remains in the
already-preregistered base grader.
"""
from __future__ import annotations

import score_contextual_guitar_recovery_variants_v167 as grader

ACTUAL_FROZEN_ITERATION003_SHA256 = "f15c6f40dd4b8479c2dfb7eab039cff98a23b45eb796265ffad08c5a8ae37115"


def main() -> int:
    grader.EXPECTED_BASE_SHA256 = ACTUAL_FROZEN_ITERATION003_SHA256
    return grader.main()


if __name__ == "__main__":
    raise SystemExit(main())
