#!/usr/bin/env python3
"""V165 event logic: exact sealed V164 behavior, version-isolated by pinned source adaptation.

No musical/numeric behavior changes are permitted in V165. This module verifies
the exact V164 event-logic blob, changes only V164/V165 diagnostic text in memory,
then exports the resulting pure helpers. No song, scorer, reference, or runtime
artifact I/O occurs.
"""
from __future__ import annotations

import hashlib
import types
from pathlib import Path

FROZEN_V164_EVENT_LOGIC_BLOB = "62303877a1971f75cacda002c5ad921680161674"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_frozen_v164_behavior() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v164_cpu_autonomous/event_logic_v164.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V164_EVENT_LOGIC_BLOB:
        raise RuntimeError("V165 frozen V164 event-logic dependency identity mismatch")
    source = path.read_text()
    source = source.replace("V164", "V165")
    module = types.ModuleType("_dadrock_v165_frozen_event_logic")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


_IMPL = _build_frozen_v164_behavior()

for _name, _value in vars(_IMPL).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

# Reassert the V165 wrapper identity constant after exporting the adapted source.
FROZEN_V164_EVENT_LOGIC_BLOB = "62303877a1971f75cacda002c5ad921680161674"
