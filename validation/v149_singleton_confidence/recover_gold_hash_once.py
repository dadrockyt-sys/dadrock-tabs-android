#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    v147 = load_module("v147_frozen_score_once", ROOT / "validation/v147_phase_d/score_once.py")
    v149 = load_module("v149_frozen_score_once", ROOT / "validation/v149_singleton_confidence/score_once.py")

    good = str(v147.EXPECTED["goldSha256"])
    frozen_bad = str(v149.EXPECTED["goldSha256"])
    if len(good) != 64 or any(ch not in "0123456789abcdef" for ch in good):
        raise RuntimeError("frozen V147 authoritative Gold SHA is not valid 64-char lowercase hex")
    if len(frozen_bad) != 65:
        raise RuntimeError(f"expected frozen V149 transcription bug length 65, got {len(frozen_bad)}")
    if good == frozen_bad:
        raise RuntimeError("recovery source unexpectedly equals malformed V149 literal")

    # Infrastructure-only repair: patch only the expected Gold identity in memory.
    v149.EXPECTED["goldSha256"] = good
    return int(v149.main())


if __name__ == "__main__":
    raise SystemExit(main())
