#!/usr/bin/env python3
"""Run the static V143 equivalence verifier with the zero-step parse correction.

The first verifier revision used ``value or -1`` for a grid step, which maps the
valid integer step 0 to -1. Keep the original evidence script immutable for audit
history and apply the one-character-class correction before executing it.
"""
from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent
VERIFIER = HERE / "verify_source_artifact_equivalence.py"

source = VERIFIER.read_text(encoding="utf-8")
old = 'int(row.get("step") or -1)'
new = 'int(row.get("step")) if row.get("step") is not None else -1'
if source.count(old) != 1:
    raise RuntimeError(f"Expected exactly one zero-step parser to patch, found {source.count(old)}")
source = source.replace(old, new)

namespace = {
    "__file__": str(VERIFIER),
    "__name__": "__main__",
}
exec(compile(source, str(VERIFIER), "exec"), namespace, namespace)
