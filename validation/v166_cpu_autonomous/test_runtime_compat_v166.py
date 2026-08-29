#!/usr/bin/env python3
"""Song-blind static fixture for V166 inherited-runtime contract compatibility."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import build_timebase_v166 as tb
import structural_qc_v166 as sqc
import timebase_qc_v166 as tqc
import transcribe_v166 as tx

PREREG_BLOB = "ca45241b4ab4689c8ceb3a7107e158367814cc1d"
CONTRACT_BLOB = "9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7"
LEGACY = {
    "numericContract": "409da313ed03a6c232d6578d48b0da6aa35b000b",
    "eventLogic": "9f9b33fd8c210ad581025b454cf69b6999aa544b",
    "timebaseBuilder": "f7e9483aea16af770bcffe01ad8cfaf689d693b9",
    "timebaseQc": "78acc9fd626039801011d039cca12686b72369c0",
    "transcriber": "fa163cafe2131aa73cdbb50df10d4e4912cff53b",
    "structuralQc": "b7d3fa92fc9f3bed00931d19097e08cd91eab62b",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def assert_overlay(fn, raw: dict) -> None:
    over = fn(raw)
    assert over is not raw
    assert over["version"] == "V166"
    assert over["frozenV162SourcePins"] == LEGACY
    assert "frozenV162SourcePins" not in raw


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    prereg_path = repo / "debug/v166-cpu-autonomous/preregistration.json"
    contract_path = repo / "debug/v166-cpu-autonomous/implementation-contract.json"
    assert git_blob_sha(prereg_path) == PREREG_BLOB
    assert git_blob_sha(contract_path) == CONTRACT_BLOB
    raw = json.loads(contract_path.read_text())
    assert raw["version"] == "V166"
    assert "frozenV162SourcePins" not in raw

    assert_overlay(tb.runtime_contract_overlay, raw)
    assert_overlay(tqc.runtime_contract_overlay, raw)
    assert_overlay(tx.runtime_contract_overlay, raw)

    # Prove the exact inherited runtime loaders receive the compatibility view.
    assert tb._RUNTIME.load_json(contract_path)["frozenV162SourcePins"] == LEGACY
    assert tqc._RUNTIME.load_json(contract_path)["frozenV162SourcePins"] == LEGACY
    assert tx._RUNTIME_ADAPTER.load_json(contract_path)["frozenV162SourcePins"] == LEGACY

    # Structural QC separately adds only its inherited schema key in memory.
    qcm = sqc.build_adapted_module()
    qc_contract = qcm.load_json(contract_path)
    assert qc_contract["canonicalSchemas"]["structuralQc"] == sqc.QC_SCHEMA
    disk_again = json.loads(contract_path.read_text())
    assert "structuralQc" not in disk_again["canonicalSchemas"]
    assert "frozenV162SourcePins" not in disk_again
    assert git_blob_sha(contract_path) == CONTRACT_BLOB

    result = {
        "schema": "dadrock.tabs.v166.runtime-compat-static-test.v1",
        "validation": "PASS",
        "checks": {
            "sealedContractUnchanged": True,
            "timebaseLegacyPinsInMemory": True,
            "timebaseQcLegacyPinsInMemory": True,
            "transcriberLegacyPinsInMemory": True,
            "structuralQcSchemaInMemoryOnly": True,
            "legacyPinsExact": LEGACY,
        },
        "safety": {
            "songAudioRead": False,
            "demucsInvoked": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "scorerRead": False,
            "V165CandidateRead": False,
            "V165ScoreRead": False,
            "gpuUsed": False,
        },
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
