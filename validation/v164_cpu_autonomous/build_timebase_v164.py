#!/usr/bin/env python3
"""V164 timebase adapter: frozen V162 beat backbone + V164 local subdivision lattice."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

from event_logic_v164 import build_subdivision_lattice

SCHEMA = "dadrock.tabs.v164.local-evidence-timebase.v1"
TARGET_ARTIST = "Lenny Kravitz"
TARGET_TITLE = "Are You Gonna Go My Way"
V162_BUILDER_BLOB = "f7e9483aea16af770bcffe01ad8cfaf689d693b9"
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
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-audio", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists():
        raise RuntimeError("V164 timebase is write-once")
    for path in (args.source_audio, args.mix, args.drums, args.bass, args.guitar, args.preregistration, args.implementation_contract):
        if not path.is_file():
            raise RuntimeError(f"missing V164 timebase input: {path}")

    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    if prereg.get("version") != "V164" or prereg.get("status") != "PREREGISTERED_BEFORE_NUMERIC_CONTRACT_OR_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V164 preregistration state")
    if contract.get("version") != "V164" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("invalid V164 implementation-contract state")
    if (contract.get("canonicalSchemas") or {}).get("timebase") != SCHEMA:
        raise RuntimeError("V164 timebase schema contract drift")

    repo = Path(__file__).resolve().parents[2]
    v162_builder_path = repo / "validation/v162_cpu_autonomous/build_timebase_v162.py"
    v162_contract_path = repo / "debug/v162-cpu-autonomous/implementation-contract.json"
    if git_blob_sha(v162_contract_path) != V162_CONTRACT_BLOB:
        raise RuntimeError("V164 frozen V162 numeric-contract dependency drift")
    pinned = contract.get("frozenV162SourcePins") or {}
    if pinned.get("numericContract") != V162_CONTRACT_BLOB or pinned.get("timebaseBuilder") != V162_BUILDER_BLOB:
        raise RuntimeError("V164 contract V162 timebase pins drift")

    base = load_pinned_module(v162_builder_path, V162_BUILDER_BLOB, "_dadrock_v162_timebase_builder")
    base.SCHEMA = SCHEMA
    base.build_subdivision_lattice = build_subdivision_lattice

    v162_contract = load_json(v162_contract_path)
    adapted_contract = dict(v162_contract)
    adapted_contract["version"] = "V162"
    adapted_contract["status"] = "SEALED_BEFORE_IMPLEMENTATION_CODE"
    adapted_schemas = dict(v162_contract.get("canonicalSchemas") or {})
    adapted_schemas["timebase"] = SCHEMA
    adapted_contract["canonicalSchemas"] = adapted_schemas
    adapted_prereg = {"version": "V162", "status": "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE"}

    with tempfile.TemporaryDirectory(prefix="v164-timebase-") as tmp:
        tmpdir = Path(tmp)
        compat_prereg = tmpdir / "v162-prereg-compat.json"
        compat_contract = tmpdir / "v162-contract-compat.json"
        compat_output = tmpdir / "v164-timebase-base.json"
        compat_prereg.write_text(json.dumps(adapted_prereg, sort_keys=True) + "\n")
        compat_contract.write_text(json.dumps(adapted_contract, sort_keys=True) + "\n")

        old_argv = sys.argv
        sys.argv = [
            str(v162_builder_path),
            "--source-audio", str(args.source_audio),
            "--mix", str(args.mix),
            "--drums", str(args.drums),
            "--bass", str(args.bass),
            "--guitar", str(args.guitar),
            "--preregistration", str(compat_prereg),
            "--implementation-contract", str(compat_contract),
            "--output", str(compat_output),
        ]
        try:
            rc = int(base.main())
        finally:
            sys.argv = old_argv
        if rc != 0 or not compat_output.is_file():
            raise RuntimeError(f"frozen V162 beat-backbone adapter failed: {rc}")
        artifact = load_json(compat_output)

    if artifact.get("schema") != SCHEMA:
        raise RuntimeError("V164 adapted timebase schema mismatch")
    if artifact.get("song") != {"artist": TARGET_ARTIST, "title": TARGET_TITLE}:
        raise RuntimeError("V164 song identity drift")

    artifact["version"] = "V164"
    artifact["classification"] = "v164-frozen-v162-beat-backbone-with-local-subdivision-evidence"
    artifact["implementation"] = {
        "frozenV162TimebaseBuilderGitBlob": V162_BUILDER_BLOB,
        "frozenV162NumericContractGitBlob": V162_CONTRACT_BLOB,
        "v164EventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v164.py")),
        "v164TimebaseBuilderGitBlob": git_blob_sha(Path(__file__)),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
    }
    artifact["safety"] = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "priorDiagnosticReadByRuntime": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
        "gpu": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({
        "schema": SCHEMA,
        "timebase": str(args.output),
        "subdivisionCount": len(artifact.get("subdivisionTimesSeconds") or []),
        "referenceRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
