#!/usr/bin/env python3
"""Static JSON-native fixture for V166 structural-QC receipt normalization."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

import structural_qc_v166 as qc

PREREG_BLOB = "ca45241b4ab4689c8ceb3a7107e158367814cc1d"
CONTRACT_BLOB = "9ab505ee8c7de732b6e9a8928854ae99d3ebb0c7"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def contains_numpy(value) -> bool:
    if isinstance(value, (np.ndarray, np.generic)):
        return True
    if isinstance(value, list):
        return any(contains_numpy(x) for x in value)
    if isinstance(value, dict):
        return any(contains_numpy(x) for x in value.values())
    return False


def main() -> int:
    repo = Path(__file__).resolve().parents[2]
    assert git_blob_sha(repo / "debug/v166-cpu-autonomous/preregistration.json") == PREREG_BLOB
    assert git_blob_sha(repo / "debug/v166-cpu-autonomous/implementation-contract.json") == CONTRACT_BLOB
    module = qc.build_adapted_module()
    payload = {
        "schema": "dadrock.tabs.v166.synthetic-json-native-fixture.v1",
        "offsets": np.asarray([-1, 0, 1, 2, 3, 4], dtype=np.int64),
        "frameCount": np.int64(6),
        "support": np.float64(0.75),
        "flags": {"paired": np.bool_(True)},
        "nested": [np.float32(0.25), {"index": np.int32(3)}],
    }
    normalized = module.json_native(payload)
    assert not contains_numpy(normalized)
    encoded = json.dumps(normalized, allow_nan=False, sort_keys=True)
    assert json.loads(encoded) == normalized
    assert normalized["offsets"] == [-1, 0, 1, 2, 3, 4]
    assert normalized["frameCount"] == 6
    for bad in (np.float64(np.nan), np.float64(np.inf), float("-inf")):
        try:
            module.json_native(bad)
            raise AssertionError("nonfinite value accepted")
        except RuntimeError:
            pass
    print(json.dumps({
        "schema": "dadrock.tabs.v166.json-native-static-test.v1",
        "validation": "PASS",
        "safety": {
            "songAudioRead": False,
            "pitchInferenceInvoked": False,
            "professionalReferenceRead": False,
            "scorerRead": False,
            "V165CandidateRead": False,
            "V165ScoreRead": False,
            "gpuUsed": False
        }
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
