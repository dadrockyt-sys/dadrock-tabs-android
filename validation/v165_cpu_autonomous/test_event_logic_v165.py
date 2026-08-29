#!/usr/bin/env python3
"""V165 song-blind invariance/regression suite: exact sealed V164 fixture behavior."""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

FROZEN_V164_EVENT_TEST_BLOB = "13d29ef19a297d19469196cb2a23a4c0d6e040de"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_impl() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v164_cpu_autonomous/test_event_logic_v164.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V164_EVENT_TEST_BLOB:
        raise RuntimeError("V165 frozen V164 event-fixture identity mismatch")
    source = path.read_text().replace("v164", "v165").replace("V164", "V165")
    module = types.ModuleType("_dadrock_v165_event_fixture")
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


def main() -> int:
    return int(_IMPL.main())


if __name__ == "__main__":
    raise SystemExit(main())
