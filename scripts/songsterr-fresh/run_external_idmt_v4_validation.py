#!/usr/bin/env python3
"""Official pre-result adapter for the frozen IDMT V4 validation harness.

This adapter changes only inclusive floating-point boundary comparison semantics
as preregistered in SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md.
"""

from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

ADAPTER_PATH = "scripts/songsterr-fresh/run_external_idmt_v4_validation.py"
CORE_PATH = "scripts/songsterr-fresh/external_idmt_v4_validation.py"
NUMERICAL_INCLUSIVE_EPSILON = 1e-12


def load_core(repo_root: Path):
    path = repo_root / CORE_PATH
    spec = importlib.util.spec_from_file_location("songsterr_idmt_v4_validation_core", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("IDMT_V4_CORE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def inclusive_leq(delta: float, limit: float) -> bool:
    value = float(delta)
    boundary = float(limit)
    return value < boundary or math.isclose(
        value,
        boundary,
        rel_tol=0.0,
        abs_tol=NUMERICAL_INCLUSIVE_EPSILON,
    )


def install_amendment(core, repo_root: Path) -> None:
    def valid_match(estimate: dict, reference: dict) -> bool:
        onset_delta = abs(
            float(estimate["startSeconds"]) - float(reference["onsetSeconds"])
        )
        pitch_delta = core.pitch_delta_cents(
            float(estimate["midi"]), float(reference["midi"])
        )
        return inclusive_leq(onset_delta, core.ONSET_TOLERANCE_SECONDS) and inclusive_leq(
            pitch_delta, core.PITCH_TOLERANCE_CENTS
        )

    original_hashes = core.implementation_hashes

    def implementation_hashes(root: Path) -> dict:
        result = original_hashes(root)
        result[ADAPTER_PATH] = core.hash_file(root / ADAPTER_PATH)
        result[
            "docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md"
        ] = core.hash_file(
            root
            / "docs/checkpoints/SONGSTERR_FRESH_IDMT_V4_STAGE_B_SCORING_NUMERICAL_AMENDMENT.md"
        )
        return result

    core.valid_match = valid_match
    core.implementation_hashes = implementation_hashes


def main() -> int:
    repo_root = Path(".").absolute()
    core = load_core(repo_root)
    install_amendment(core, repo_root)

    args = core.parse_args()
    if args.self_test:
        result = core.run_self_test()
        result["numericalComparison"] = {
            "inclusiveBoundaryEpsilon": NUMERICAL_INCLUSIVE_EPSILON,
            "onsetToleranceSeconds": core.ONSET_TOLERANCE_SECONDS,
            "pitchToleranceCents": core.PITCH_TOLERANCE_CENTS,
        }
        print(core.canonical_json(result))
        return 0

    if not all((args.archive, args.stage_b_manifest, args.work_dir, args.output)):
        raise core.ValidationError(
            "OFFICIAL_MODE_REQUIRES_ARCHIVE_MANIFEST_WORKDIR_OUTPUT"
        )

    core.run_official(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Preserve the core's fail-closed exit behavior while keeping adapter failures explicit.
        if exc.__class__.__name__ == "ValidationError":
            print(f"IDMT_V4_EXTERNAL_VALIDATION_ERROR:{exc}", file=sys.stderr)
            raise SystemExit(2)
        raise
