#!/usr/bin/env python3
"""V166 timebase QC: exact sealed V165 behavior with version isolation only.

The inherited V164 runtime expects legacy `frozenV162SourcePins`. V166 supplies
those exact transitive predecessor identities in memory only. The sealed V166
contract file and every timebase/QC numeric remain unchanged.
"""
from __future__ import annotations

import hashlib
import sys
import types
from pathlib import Path
from typing import Any

FROZEN_V165_TIMEBASE_QC_BLOB = "3c11a490d24d06647894ee8c3700d9ff7decd993"
LEGACY_V162_PINS = {
    "numericContract": "409da313ed03a6c232d6578d48b0da6aa35b000b",
    "eventLogic": "9f9b33fd8c210ad581025b454cf69b6999aa544b",
    "timebaseBuilder": "f7e9483aea16af770bcffe01ad8cfaf689d693b9",
    "timebaseQc": "78acc9fd626039801011d039cca12686b72369c0",
    "transcriber": "fa163cafe2131aa73cdbb50df10d4e4912cff53b",
    "structuralQc": "b7d3fa92fc9f3bed00931d19097e08cd91eab62b",
}


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def runtime_contract_overlay(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("version") != "V166":
        return data
    out = dict(data)
    pins = dict(out.get("frozenV162SourcePins") or {})
    pins.update(LEGACY_V162_PINS)
    out["frozenV162SourcePins"] = pins
    return out


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
_RUNTIME = _IMPL._IMPL
_ORIGINAL_RUNTIME_LOAD_JSON = _RUNTIME.load_json


def _compat_runtime_load_json(path: Path) -> dict[str, Any]:
    data = _ORIGINAL_RUNTIME_LOAD_JSON(path)
    if Path(path).name == "implementation-contract.json":
        return runtime_contract_overlay(data)
    return data


_RUNTIME.load_json = _compat_runtime_load_json
SCHEMA = _IMPL.SCHEMA
TIMEBASE_SCHEMA = _IMPL.TIMEBASE_SCHEMA


def main() -> int:
    return int(_IMPL.main())


if __name__ == "__main__":
    raise SystemExit(main())
