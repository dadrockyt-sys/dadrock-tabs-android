#!/usr/bin/env python3
"""V166 timebase QC: exact sealed V165 behavior with version isolation only."""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

FROZEN_V165_TIMEBASE_QC_BLOB = "3c11a490d24d06647894ee8c3700d9ff7decd993"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_impl() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v165_cpu_autonomous/timebase_qc_v165.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V165_TIMEBASE_QC_BLOB:
        raise RuntimeError("V166 frozen V165 timebase-QC identity mismatch")
    source = path.read_text().replace("v165", "v166").replace("V165", "V166")
    module = types.ModuleType("_dadrock_v166_timebase_qc")
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
TIMEBASE_SCHEMA = _IMPL.TIMEBASE_SCHEMA


def main() -> int:
    return int(_IMPL.main())


if __name__ == "__main__":
    raise SystemExit(main())
