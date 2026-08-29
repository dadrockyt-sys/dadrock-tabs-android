#!/usr/bin/env python3
"""V165 JSON-native/local-provenance fixture: exact sealed V164 behavior."""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

FROZEN_V164_JSON_TEST_BLOB = "a0b525485bbea933004045622bbf8c63527f123b"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _build_impl() -> types.ModuleType:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v164_cpu_autonomous/test_json_native_v164.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V164_JSON_TEST_BLOB:
        raise RuntimeError("V165 frozen V164 JSON fixture identity mismatch")
    source = path.read_text().replace("v164", "v165").replace("V164", "V165")
    module = types.ModuleType("_dadrock_v165_json_fixture")
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
