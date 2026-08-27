#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]

EXPECTED_BLOBS = {
    "validation/v148_singleton_only/score_once.py": "8137734218a722bb12f364ecfea3d1b8e526cc2c",
    "validation/v147_phase_d/score_once.py": "74b31168b629812acde874b89dfcdf022acf987d",
    "debug/v147-phase-d-scoring/phase-d-score-result.json": "971359f7dc645169f0f2ef5f084d0610af8e5cc3",
    "debug/v148-singleton-only/phase-c-score-constant-diagnosis.json": "aaf74ffe149ec0c5943d3f665611c5dad70cba80",
    "debug/v148-singleton-only/phase-c-score-recovery-preregistration.json": None,
}


def git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", path], cwd=ROOT, text=True).strip()


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    for path, expected in EXPECTED_BLOBS.items():
        if expected is None:
            continue
        actual = git_blob(path)
        if actual != expected:
            raise RuntimeError(f"frozen recovery identity mismatch for {path}: {actual} != {expected}")

    diagnosis = json.loads((ROOT / "debug/v148-singleton-only/phase-c-score-constant-diagnosis.json").read_text())
    if diagnosis.get("goldRead") is not False or diagnosis.get("referenceParsed") is not False or diagnosis.get("scoreCallCount") != 0:
        raise RuntimeError("reference-free diagnosis safety state mismatch")
    if diagnosis.get("v148ExpectedGoldShaLength") != 65 or diagnosis.get("v147ExpectedGoldShaLength") != 64:
        raise RuntimeError("frozen hash-length diagnosis mismatch")

    v148 = load_module(ROOT / "validation/v148_singleton_only/score_once.py", "v148_frozen_score_once_recovery")
    v147 = load_module(ROOT / "validation/v147_phase_d/score_once.py", "v147_historical_score_once_recovery")

    malformed = v148.EXPECTED["goldSha256"]
    historical = v147.EXPECTED["goldSha256"]
    if len(malformed) != 65 or len(historical) != 64 or malformed == historical:
        raise RuntimeError("runtime expected-Gold diagnosis mismatch")
    if not all(c in "0123456789abcdef" for c in historical):
        raise RuntimeError("historical expected Gold SHA is not lowercase hexadecimal")

    historical_result = json.loads((ROOT / "debug/v147-phase-d-scoring/phase-d-score-result.json").read_text())
    historical_result_sha = ((historical_result.get("reference") or {}).get("sha256"))
    if historical_result_sha != historical:
        raise RuntimeError("historical V147 successful result does not confirm historical expected Gold SHA")
    historical_chain = historical_result.get("scoringChain") or {}
    if historical_chain.get("scoreCallCount") != 1:
        raise RuntimeError("historical V147 score result identity mismatch")

    # Infrastructure-only recovery: patch exactly one malformed expected identity in memory.
    # The frozen V148 scorer's candidate, baseline, metrics, reference parser, and scoring call remain unchanged.
    v148.EXPECTED["goldSha256"] = historical

    # Delegate to the unchanged frozen V148 main path. Its own gates execute again and it may call
    # the historical scorer exactly once only after Gold verification and reference parsing.
    return int(v148.main())


if __name__ == "__main__":
    raise SystemExit(main())
