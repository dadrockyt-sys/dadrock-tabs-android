#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import benchmark_pretrained_frontend as base  # noqa: E402


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "tolist"):
        return json_safe(value.tolist())
    if hasattr(value, "item"):
        return json_safe(value.item())
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    raise TypeError(f"unsupported Basic Pitch metadata type for JSON persistence: {type(value)!r}")


# A2 proved inference succeeds and fails only when nested NumPy scalar pitch-bend
# values reach json.dumps. Replace only the metadata serializer; all inference,
# thresholds, scoring, and selection logic stay in the frozen parent benchmark.
base.json_pitch_bend = json_safe


if __name__ == "__main__":
    raise SystemExit(base.main())
