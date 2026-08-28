#!/usr/bin/env python3
"""Song-blind V164 JSON-native receipt + local-provenance static fixture."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from structural_qc_v164 import build_adapted_module

V162_JSON_FIXTURE_BLOB = "654557363745f580f425252395542e9fb91adaad"
SCHEMA = "dadrock.tabs.v164.json-native-local-provenance-static-test.v1"


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def contains_numpy(value: Any) -> bool:
    if isinstance(value, (np.generic, np.ndarray)):
        return True
    if isinstance(value, dict):
        return any(contains_numpy(key) or contains_numpy(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_numpy(item) for item in value)
    return False


def main() -> int:
    frozen = Path(__file__).resolve().parents[1] / "v162_cpu_autonomous" / "test_json_native_v162.py"
    if not frozen.is_file() or git_blob_sha(frozen) != V162_JSON_FIXTURE_BLOB:
        raise RuntimeError("V164 frozen V162 JSON-native fixture dependency drift")

    json_native = build_adapted_module().json_native

    control_failed = False
    try:
        json.dumps({"x": np.bool_(True)})
    except TypeError:
        control_failed = True
    if not control_failed:
        raise RuntimeError("control fixture did not reproduce raw numpy.bool_ JSON failure")

    native_checks = {"boolTrue": bool(np.bool_(True)), "boolFalse": bool(np.bool_(False))}
    if not all(type(value) is bool for value in native_checks.values()):
        raise RuntimeError("V164 synthetic structural checks did not normalize to native bool")

    fixture = {
        "boolScalar": np.bool_(True),
        "integerScalar": np.int64(7),
        "floatingScalar": np.float64(1.25),
        "array": np.asarray([[1, 2], [3, 4]], dtype=np.int64),
        "nested": {
            "list": [np.bool_(False), np.int32(9)],
            "tuple": (np.float32(2.5), np.asarray([5, 6], dtype=np.int16)),
        },
        "checks": native_checks,
        "localEvidence": {
            "onsetNormalization": {
                "centerFrame": np.int64(64),
                "loFrame": np.int64(32),
                "hiFrame": np.int64(96),
                "positiveCount": np.int64(13),
                "supportScale": np.float64(0.875),
            },
            "proposalNormalization": {"loFrame": np.int32(0), "hiFrame": np.int32(47)},
            "normalizedSupport": np.float64(0.625),
            "remoteDependency": np.bool_(False),
        },
    }
    normalized = json_native(fixture)
    if contains_numpy(normalized):
        raise RuntimeError("NumPy type remained after V164 JSON-native normalization")
    expected = {
        "boolScalar": True,
        "integerScalar": 7,
        "floatingScalar": 1.25,
        "array": [[1, 2], [3, 4]],
        "nested": {"list": [False, 9], "tuple": [2.5, [5, 6]]},
        "checks": {"boolTrue": True, "boolFalse": False},
        "localEvidence": {
            "onsetNormalization": {
                "centerFrame": 64,
                "loFrame": 32,
                "hiFrame": 96,
                "positiveCount": 13,
                "supportScale": 0.875,
            },
            "proposalNormalization": {"loFrame": 0, "hiFrame": 47},
            "normalizedSupport": 0.625,
            "remoteDependency": False,
        },
    }
    if normalized != expected:
        raise RuntimeError(f"unexpected normalized V164 fixture: {normalized!r}")
    local = normalized["localEvidence"]
    onset = local["onsetNormalization"]
    if not (0 <= onset["loFrame"] <= onset["centerFrame"] <= onset["hiFrame"] and onset["hiFrame"] - onset["loFrame"] == 64):
        raise RuntimeError("V164 local normalization provenance lost integer/range semantics")
    if not 0.0 <= float(local["normalizedSupport"]) <= 1.0 or not math.isfinite(float(onset["supportScale"])):
        raise RuntimeError("V164 local support metadata lost finite [0,1] semantics")

    encoded = json.dumps(normalized, allow_nan=False, sort_keys=True)
    if json.loads(encoded) != normalized:
        raise RuntimeError("V164 JSON-native fixture did not round-trip exactly")

    for nonfinite in (float("nan"), float("inf"), float("-inf")):
        try:
            json_native(nonfinite)
        except RuntimeError:
            pass
        else:
            raise RuntimeError("V164 json_native accepted nonfinite native float")
        try:
            json.dumps({"x": nonfinite}, allow_nan=False)
        except ValueError:
            pass
        else:
            raise RuntimeError("allow_nan=False failed to reject nonfinite float")

    print(json.dumps({
        "schema": SCHEMA,
        "validation": "PASS",
        "frozenV162JsonFixtureGitBlob": V162_JSON_FIXTURE_BLOB,
        "controlRawNumpyFailureReproduced": True,
        "numpyTypesRemainAfterNormalization": False,
        "nativeCheckValuesAreBool": True,
        "localNormalizationMetadataNative": True,
        "localNormalizationBoundsPreserved": True,
        "normalizedSupportFiniteWithinZeroOne": True,
        "roundTripExact": True,
        "nonfiniteRejected": True,
        "songAudioRead": False,
        "demucsInvoked": False,
        "pitchInferenceInvoked": False,
        "professionalReferenceRead": False,
        "frozenScorerRead": False,
        "V163CandidateRead": False,
        "V163ScoreRead": False,
        "priorScoreRead": False,
        "gpuUsed": False
    }, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
