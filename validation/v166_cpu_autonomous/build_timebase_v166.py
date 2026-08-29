#!/usr/bin/env python3
"""V166 timebase builder: exact sealed V165 behavior with version isolation only."""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

FROZEN_V165_TIMEBASE_BUILDER_BLOB = "62d67becb768e1e5e3e8de1cd3b121eb863b2a18"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_impl() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v165_cpu_autonomous/build_timebase_v165.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V165_TIMEBASE_BUILDER_BLOB:
        raise RuntimeError("V166 frozen V165 timebase-builder identity mismatch")
    source = path.read_text().replace("v165", "v166").replace("V165", "V166")
    module = types.ModuleType("_dadrock_v166_timebase_builder")
    module.__file__ = str(Path(__file__).resolve())
    module.__dict__["__builtins__"] = __builtins__
    parent = str(Path(__file__).resolve().parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        exec(compile(source, str(Path(__file__).resolve()), "exec"), module.__dict__)
    finally:
        if inserted:
            sys.path.remove(parent)
    return module


_IMPL = _build_impl()
SCHEMA = _IMPL.SCHEMA


def main() -> int:
    return int(_IMPL.main())


if __name__ == "__main__":
    raise SystemExit(main())
