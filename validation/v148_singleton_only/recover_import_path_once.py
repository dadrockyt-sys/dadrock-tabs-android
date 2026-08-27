#!/usr/bin/env python3
"""Infrastructure-only launcher for the frozen V148 constructor.

The first authorized V148 job failed before construction because executing the
constructor by filesystem path omitted the repository root from sys.path. This
wrapper changes only Python module discovery, then delegates to the unchanged
frozen constructor. It contains no candidate logic and no musical policy.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

runpy.run_path(
    str(ROOT / "validation/v148_singleton_only/construct_once.py"),
    run_name="__main__",
)
