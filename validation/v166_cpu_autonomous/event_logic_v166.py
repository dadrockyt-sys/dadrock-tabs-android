#!/usr/bin/env python3
"""V166 event logic: exact sealed V165 behavior, version-isolated only.

V166 changes Guitar temporal template evidence in the transcriber wrapper. Event
segmentation, local evidence, register thresholds, Bass logic, and grid logic are
frozen to V165. No song/reference/scorer/runtime-artifact I/O occurs here.
"""
from __future__ import annotations

import hashlib
import types
from pathlib import Path

FROZEN_V165_EVENT_LOGIC_BLOB = "b296b3c322c13f8963f253f9b0666db66766a178"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_frozen_v165_behavior() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v165_cpu_autonomous/event_logic_v165.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V165_EVENT_LOGIC_BLOB:
        raise RuntimeError("V166 frozen V165 event-logic dependency identity mismatch")
    source = path.read_text().replace("v165", "v166").replace("V165", "V166")
    module = types.ModuleType("_dadrock_v166_frozen_event_logic")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module


_IMPL = _build_frozen_v165_behavior()

for _name, _value in vars(_IMPL).items():
    if not _name.startswith("__"):
        globals()[_name] = _value

FROZEN_V165_EVENT_LOGIC_BLOB = "b296b3c322c13f8963f253f9b0666db66766a178"
