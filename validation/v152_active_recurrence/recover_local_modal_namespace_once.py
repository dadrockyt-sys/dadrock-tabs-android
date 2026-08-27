#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import runpy
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
root = str(ROOT)
while root in sys.path:
    sys.path.remove(root)
sys.path.insert(0, root)

local_modal = types.ModuleType("modal")
local_modal.__path__ = [str(ROOT / "modal")]
local_modal.__package__ = "modal"
sys.modules["modal"] = local_modal

runpy.run_path(str(ROOT / "validation/v152_active_recurrence/construct_once.py"), run_name="__main__")
