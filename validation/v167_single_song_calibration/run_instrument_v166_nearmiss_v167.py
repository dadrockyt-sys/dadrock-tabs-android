#!/usr/bin/env python3
"""Runner binding exact V166 event-logic exports into the V167 observer module."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import instrument_v166_nearmiss_v167 as observer

EXPECTED_V166_EVENT_LOGIC_BLOB = "6561194742093d76bab452ef0bbb0b889724dc4e"
_ORIGINAL_LOAD = observer.load_v166_module


def _load_event_logic(path: Path):
    if observer.git_blob_sha(path) != EXPECTED_V166_EVENT_LOGIC_BLOB:
        raise RuntimeError("V166 event-logic blob identity mismatch")
    parent = str(path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        spec = importlib.util.spec_from_file_location("_v167_pinned_v166_event_logic", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("cannot load V166 event logic")
        event = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(event)
    finally:
        if inserted:
            sys.path.remove(parent)
    return event


def load_v166_module_with_event_logic(path: Path):
    module = _ORIGINAL_LOAD(path)
    event = _load_event_logic(path.with_name("event_logic_v166.py"))
    for name, value in vars(event).items():
        if name.startswith("__"):
            continue
        if not hasattr(module, name):
            setattr(module, name, value)
    module.V167_OBSERVER_EVENT_LOGIC_GIT_BLOB = EXPECTED_V166_EVENT_LOGIC_BLOB
    return module


observer.load_v166_module = load_v166_module_with_event_logic

if __name__ == "__main__":
    raise SystemExit(observer.main())
