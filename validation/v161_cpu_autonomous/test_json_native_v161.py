#!/usr/bin/env python3
"""Song-blind static coverage for the V161 JSON-native structural-QC boundary."""
from __future__ import annotations

import json
import math
from typing import Any

import numpy as np

from structural_qc_v161 import json_native


def contains_numpy(value: Any) -> bool:
    if isinstance(value, (np.generic, np.ndarray)):
        return True
    if isinstance(value, dict):
        return any(contains_numpy(key) or contains_numpy(item) for key, item in value.items())
    if isinstance(value, (list, tuple)):
        return any(contains_numpy(item) for item in value)
    return False


def main() -> int:
    control_failed = False
    try:
        json.dumps({"x": np.bool_(True)})
    except TypeError:
        control_failed = True
    if not control_failed:
        raise RuntimeError("control fixture did not reproduce historical numpy.bool_ JSON failure")

    raw_checks = {"boolTrue": np.bool_(True), "boolFalse": np.bool_(False)}
    native_checks = {key: bool(value) for key, value in raw_checks.items()}
    if not all(type(value) is bool for value in native_checks.values()):
        raise RuntimeError("synthetic structural checks did not normalize to native bool")

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
    }
    normalized = json_native(fixture)
    if contains_numpy(normalized):
        raise RuntimeError("NumPy type remained after V161 JSON-native normalization")
    expected = {
        "boolScalar": True,
        "integerScalar": 7,
        "floatingScalar": 1.25,
        "array": [[1, 2], [3, 4]],
        "nested": {"list": [False, 9], "tuple": [2.5, [5, 6]]},
        "checks": {"boolTrue": True, "boolFalse": False},
    }
    if normalized != expected:
        raise RuntimeError(f"unexpected normalized fixture: {normalized!r}")

    encoded = json.dumps(normalized, allow_nan=False, sort_keys=True)
    decoded = json.loads(encoded)
    if decoded != normalized:
        raise RuntimeError("V161 JSON-native fixture did not round-trip exactly")

    for nonfinite in (float("nan"), float("inf"), float("-inf")):
        rejected = False
        try:
            json_native(nonfinite)
        except RuntimeError:
            rejected = True
        if not rejected:
            raise RuntimeError("json_native accepted a nonfinite native float")
        try:
            json.dumps({"x": nonfinite}, allow_nan=False)
        except ValueError:
            pass
        else:
            raise RuntimeError("allow_nan=False failed to reject nonfinite float")

    if not math.isfinite(float(normalized["floatingScalar"])):
        raise RuntimeError("normalized finite float unexpectedly became nonfinite")

    print(json.dumps({
        "schema": "dadrock.tabs.v161.json-native-static-test.v1",
        "validation": "PASS",
        "controlReproducedHistoricalNumpyBoolFailure": True,
        "numpyTypesRemainAfterNormalization": False,
        "nativeCheckValuesAreBool": True,
        "roundTripExact": True,
        "nonfiniteRejected": True,
        "songAudioRead": False,
        "demucsInvoked": False,
        "pitchInferenceInvoked": False,
        "professionalReferenceRead": False,
        "frozenScorerRead": False,
        "V160CandidateRead": False,
        "priorScoreRead": False,
    }, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
