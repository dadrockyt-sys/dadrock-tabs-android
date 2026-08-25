#!/usr/bin/env python3
"""Materialize the exact successful v143 paid capture from Git history.

This helper is intentionally CPU-only. It never imports Modal, performs inference,
or contacts the professional scorer. Future precision experiments should use this
fixture before considering any new paid L4 capture.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

PINNED_COMMIT = "c1451df43cc1162ed2b38aa3f3300b7af4d9b527"
RUN_ID = 32805316807
FILES = {
    "repaired-timing-precision-candidate-product.json": (
        "debug/v143-contextual-prune/repaired-timing-precision-candidate-product.json",
        "a2d451a39391b797e55623bb3c616735a3f1b39648103cb630a9bb1035430951",
    ),
    "precision-v2-replay-artifact-validation.json": (
        "debug/v143-contextual-prune/precision-v2-replay-artifact-validation.json",
        "182247f2beda257a49cfb454b1e7fc920594ffe5ecce39f7b9517ed15b21b95a",
    ),
    "precision-v2-replay-policy-compare.json": (
        "debug/v143-contextual-prune/precision-v2-replay-policy-compare.json",
        "c77f923db45099f79df563e2c2d2487e46dceaef6f9469db8bd790f78f8cfcda",
    ),
    "precision-v2-capture-lock.json": (
        "debug/v143-contextual-prune/precision-v2-capture-lock.json",
        "49898a441aed8519d96a71bc46c3e85d5d6c64c4be6da5398e9749ab1d6287be",
    ),
}


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{PINNED_COMMIT}:{path}"])


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=f"debug/v143-contextual-prune/pinned-modal-capture-{RUN_ID}",
        help="Directory to receive the immutable fixture files.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for output_name, (repo_path, expected_sha) in FILES.items():
        payload = git_show(repo_path)
        actual_sha = sha256(payload)
        if actual_sha != expected_sha:
            raise SystemExit(
                f"Pinned fixture hash mismatch for {repo_path}: "
                f"expected {expected_sha}, got {actual_sha}"
            )
        (output_dir / output_name).write_bytes(payload)

    product = json.loads(
        (output_dir / "repaired-timing-precision-candidate-product.json").read_text()
    )
    replay = product.get("precisionReplayEvidence")
    if not isinstance(replay, dict):
        raise SystemExit("Pinned candidate is missing precisionReplayEvidence")

    required_true = (
        "fixedRetainedAttackPitchReplayReady",
        "attackPolicyReplayReady",
        "sourceViewEvidenceReady",
        "precisionStrengthRecomputeReady",
        "zeroValuePreservationReady",
    )
    missing = [key for key in required_true if replay.get(key) is not True]
    if missing:
        raise SystemExit(f"Pinned replay readiness mismatch: {missing}")

    print(f"Materialized immutable CPU replay fixture from {PINNED_COMMIT}")
    print(f"Run: {RUN_ID}")
    print(f"Output: {output_dir}")
    print("Modal/L4 invoked: false")
    print("Professional reference invoked: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
