#!/usr/bin/env python3
"""V165 transcriber: exact V164 adapter with one preregistered count repair.

The frozen V164 transcriber adapter is verified by Git blob and adapted in memory.
All V164/V165 version/provenance names are mechanically versioned forward. The
only functional repair is the sealed event-logic provenance-path transform count:
V164 expected 2 occurrences in the pinned V162 source; V165 requires exactly 3.
No song/reference/scorer I/O occurs while constructing this module.
"""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path

FROZEN_V164_TRANSCRIBER_BLOB = "df1302216df404bc3368ff820f005d6b63ae100d"
V165_REQUIRED_OCCURRENCE_COUNT = 3
_FAILED_NEEDLE = "event_logic_v162.py"
_REPLACEMENT_NEEDLE = "event_logic_v165.py"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _adapt_v164_adapter_source() -> str:
    repo = Path(__file__).resolve().parents[2]
    path = repo / "validation/v164_cpu_autonomous/transcribe_v164.py"
    if not path.is_file() or _git_blob_sha(path) != FROZEN_V164_TRANSCRIBER_BLOB:
        raise RuntimeError("V165 frozen V164 transcriber-adapter identity mismatch")

    source = path.read_text()
    # Mechanical version isolation first. This preserves all V164 algorithmic code.
    source = source.replace("v164", "v165").replace("V164", "V165")

    # Sole preregistered functional repair: exact-count provenance transform 2 -> 3.
    old = (
        "source = replace_exact(source, 'event_logic_v162.py', 'event_logic_v165.py', "
        "2, \"event-logic provenance path\")"
    )
    new = (
        "source = replace_exact(source, 'event_logic_v162.py', 'event_logic_v165.py', "
        "3, \"event-logic provenance path\")"
    )
    if source.count(old) != 1:
        raise RuntimeError(f"V165 adapter-repair site drift: expected 1, found {source.count(old)}")
    source = source.replace(old, new)

    if source.count("'event_logic_v162.py', 'event_logic_v165.py', 3") != 1:
        raise RuntimeError("V165 repaired provenance transform is not uniquely sealed at count 3")
    return source


def _build_v165_adapter_module() -> types.ModuleType:
    source = _adapt_v164_adapter_source()
    module = types.ModuleType("_dadrock_v165_transcriber_adapter")
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


_IMPL = _build_v165_adapter_module()

# Public construction hook used by the mandatory song-blind static fixture.
def build_adapted_module() -> types.ModuleType:
    return _IMPL.build_adapted_module()


def main() -> int:
    return int(_IMPL.main())


# Expose schemas/helpers for structural/runtime pinning without shadowing wrapper hooks.
for _name, _value in vars(_IMPL).items():
    if _name.startswith("__") or _name in {"build_adapted_module", "main"}:
        continue
    globals().setdefault(_name, _value)


if __name__ == "__main__":
    raise SystemExit(main())
