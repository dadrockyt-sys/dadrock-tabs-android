#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
root = str(ROOT)
while root in sys.path:
    sys.path.remove(root)
sys.path.insert(0, root)
runpy.run_path(str(ROOT / "validation/v152_active_recurrence/construct_once.py"), run_name="__main__")
