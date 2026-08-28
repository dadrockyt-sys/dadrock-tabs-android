#!/usr/bin/env python3
"""Independent V164 timebase QC via pinned V162 QC + V164 subdivision recomputation."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from event_logic_v164 import build_subdivision_lattice, extrapolated_final_beat

SCHEMA = "dadrock.tabs.v164.local-evidence-timebase-qc.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v164.local-evidence-timebase.v1"
V162_QC_BLOB = "78acc9fd626039801011d039cca12686b72369c0"
V162_CONTRACT_BLOB = "409da313ed03a6c232d6578d48b0da6aa35b000b"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def load_pinned_module(path: Path, expected_blob: str, name: str):
    if not path.is_file() or git_blob_sha(path) != expected_blob:
        raise RuntimeError(f"V164 pinned dependency mismatch: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load pinned module: {path}")
    module = importlib.util.module_from_spec(spec)
    parent = str(path.parent)
    inserted = parent not in sys.path
    if inserted:
        sys.path.insert(0, parent)
    try:
        spec.loader.exec_module(module)
    finally:
        if inserted:
            sys.path.remove(parent)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--source-audio", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError("V164 timebase-QC receipt is write-once")
    for path in (args.timebase, args.source_audio, args.mix, args.drums, args.bass, args.guitar, args.preregistration, args.implementation_contract):
        if not path.is_file():
            raise RuntimeError(f"missing V164 timebase-QC input: {path}")

    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    timebase = load_json(args.timebase)
    schemas = contract.get("canonicalSchemas") or {}
    if prereg.get("version") != "V164" or prereg.get("status") != "PREREGISTERED_BEFORE_NUMERIC_CONTRACT_OR_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V164 preregistration state")
    if contract.get("version") != "V164" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V164 implementation-contract state")
    if schemas.get("timebase") != TIMEBASE_SCHEMA or schemas.get("timebaseQc") != SCHEMA:
        raise RuntimeError("V164 timebase/QC schema contract drift")
    if timebase.get("schema") != TIMEBASE_SCHEMA or timebase.get("version") != "V164":
        raise RuntimeError("invalid V164 timebase")

    repo = Path(__file__).resolve().parents[2]
    v162_qc_path = repo / "validation/v162_cpu_autonomous/timebase_qc_v162.py"
    v162_contract_path = repo / "debug/v162-cpu-autonomous/implementation-contract.json"
    if git_blob_sha(v162_contract_path) != V162_CONTRACT_BLOB:
        raise RuntimeError("V164 frozen V162 numeric-contract dependency drift")
    pins = contract.get("frozenV162SourcePins") or {}
    if pins.get("numericContract") != V162_CONTRACT_BLOB or pins.get("timebaseQc") != V162_QC_BLOB:
        raise RuntimeError("V164 contract V162 timebase-QC pins drift")

    base = load_pinned_module(v162_qc_path, V162_QC_BLOB, "_dadrock_v162_timebase_qc")
    base.SCHEMA = SCHEMA
    base.TIMEBASE_SCHEMA = TIMEBASE_SCHEMA
    base.build_subdivision_lattice = build_subdivision_lattice
    base.extrapolated_final_beat = extrapolated_final_beat

    v162_contract = load_json(v162_contract_path)
    adapted_contract = dict(v162_contract)
    adapted_contract["version"] = "V162"
    adapted_contract["status"] = "SEALED_BEFORE_IMPLEMENTATION_CODE"
    adapted_schemas = dict(v162_contract.get("canonicalSchemas") or {})
    adapted_schemas["timebase"] = TIMEBASE_SCHEMA
    adapted_schemas["timebaseQc"] = SCHEMA
    adapted_contract["canonicalSchemas"] = adapted_schemas
    adapted_prereg = {"version": "V162", "status": "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE"}

    compat_timebase = dict(timebase)
    compat_safety = dict(timebase.get("safety") or {})
    compat_safety["V161CandidateRead"] = False
    compat_timebase["safety"] = compat_safety

    with tempfile.TemporaryDirectory(prefix="v164-timebase-qc-") as tmp:
        tmpdir = Path(tmp)
        compat_prereg_path = tmpdir / "v162-prereg-compat.json"
        compat_contract_path = tmpdir / "v162-contract-compat.json"
        compat_timebase_path = tmpdir / "v164-timebase-compat.json"
        compat_receipt = tmpdir / "v164-timebase-qc-base.json"
        compat_prereg_path.write_text(json.dumps(adapted_prereg, sort_keys=True) + "\n")
        compat_contract_path.write_text(json.dumps(adapted_contract, sort_keys=True) + "\n")
        compat_timebase_path.write_text(json.dumps(compat_timebase, indent=2, sort_keys=True, allow_nan=False) + "\n")

        old_argv = sys.argv
        sys.argv = [
            str(v162_qc_path),
            "--timebase", str(compat_timebase_path),
            "--source-audio", str(args.source_audio),
            "--mix", str(args.mix),
            "--drums", str(args.drums),
            "--bass", str(args.bass),
            "--guitar", str(args.guitar),
            "--preregistration", str(compat_prereg_path),
            "--implementation-contract", str(compat_contract_path),
            "--receipt", str(compat_receipt),
        ]
        try:
            rc = int(base.main())
        finally:
            sys.argv = old_argv
        if not compat_receipt.is_file():
            raise RuntimeError("V164 frozen V162 QC adapter produced no receipt")
        receipt = load_json(compat_receipt)
        if rc != 0 or receipt.get("validation") != "PASS":
            raise RuntimeError(f"V164 independent timebase QC failed: {receipt.get('checks')}")

    receipt["schema"] = SCHEMA
    receipt["version"] = "V164"
    receipt.pop("terminalForV162OnFailure", None)
    receipt["terminalForV164OnFailure"] = True
    receipt["timebasePath"] = str(args.timebase)
    receipt["timebaseSha256"] = sha256_file(args.timebase)
    receipt["preregistrationSha256"] = sha256_file(args.preregistration)
    receipt["implementationContractSha256"] = sha256_file(args.implementation_contract)
    receipt["implementation"] = {
        "frozenV162TimebaseQcGitBlob": V162_QC_BLOB,
        "frozenV162NumericContractGitBlob": V162_CONTRACT_BLOB,
        "v164EventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v164.py")),
        "v164TimebaseQcGitBlob": git_blob_sha(Path(__file__)),
    }
    receipt["safety"] = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "pitchInferenceInvoked": False,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
        "gpuUsed": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "validation": "PASS",
        "timebaseSha256": receipt["timebaseSha256"],
        "pitchInferenceInvoked": False,
        "referenceRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
