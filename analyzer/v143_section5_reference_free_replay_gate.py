from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from v143_fresh_section5_reference_free_capture import (
    app,
    capture_fresh_section5_reference_free,
)


ROOT = Path(__file__).resolve().parents[1]
AUDIO_PATH = ROOT / "public" / "gomywayfullaitest.m4a"
CACHE_PATH = (
    ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "fresh-section5-reference-free-cache.json"
)


def _first_mismatch(expected: Any, actual: Any, path: str = "$") -> dict[str, Any] | None:
    if type(expected) is not type(actual):
        return {
            "path": path,
            "expectedType": type(expected).__name__,
            "actualType": type(actual).__name__,
            "expected": expected,
            "actual": actual,
        }
    if isinstance(expected, dict):
        if set(expected) != set(actual):
            return {
                "path": path,
                "missingKeys": sorted(set(expected) - set(actual)),
                "extraKeys": sorted(set(actual) - set(expected)),
            }
        for key in expected:
            mismatch = _first_mismatch(expected[key], actual[key], f"{path}.{key}")
            if mismatch is not None:
                return mismatch
        return None
    if isinstance(expected, list):
        if len(expected) != len(actual):
            return {
                "path": path,
                "expectedLength": len(expected),
                "actualLength": len(actual),
            }
        for index, (left, right) in enumerate(zip(expected, actual)):
            mismatch = _first_mismatch(left, right, f"{path}[{index}]")
            if mismatch is not None:
                return mismatch
        return None
    if expected != actual:
        return {"path": path, "expected": expected, "actual": actual}
    return None


@app.local_entrypoint(name="section5_replay_gate")
def section5_replay_gate(audio_path: str = str(AUDIO_PATH)) -> None:
    source = Path(audio_path)
    if not source.exists() or source.stat().st_size <= 0:
        raise RuntimeError(f"Calibration audio missing or empty: {source}")
    if not CACHE_PATH.exists() or CACHE_PATH.stat().st_size <= 0:
        raise RuntimeError(f"Frozen Section-5 cache missing or empty: {CACHE_PATH}")

    expected = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    if expected.get("referenceFree") is not True:
        raise RuntimeError("Frozen Section-5 cache is not reference-free")
    if expected.get("professionalReferenceUsedByAnalyzer") is not False:
        raise RuntimeError("Frozen Section-5 cache unexpectedly used professional reference")

    payload = source.read_bytes()
    if len(payload) / (1024 * 1024) >= 95:
        raise RuntimeError("Audio is too close to Modal's 100 MB payload limit")

    print("=== V143 SECTION 5 REFERENCE-FREE REPLAY GATE ===")
    print("Measures: 81-96")
    print("Professional reference available to remote analyzer: False")
    print("Production modified: False")
    print("Regenerating frozen reference-free carrier on Modal L4...")

    actual = capture_fresh_section5_reference_free.remote(payload, source.suffix)
    mismatch = _first_mismatch(expected, actual)

    print()
    print("EXPECTED rawEventCount:", expected.get("rawEventCount"))
    print("ACTUAL rawEventCount:", actual.get("rawEventCount"))
    print("EXPECTED candidateClusterCount:", expected.get("candidateClusterCount"))
    print("ACTUAL candidateClusterCount:", actual.get("candidateClusterCount"))
    print("EXPECTED onsetGroupCount:", expected.get("onsetGroupCount"))
    print("ACTUAL onsetGroupCount:", actual.get("onsetGroupCount"))
    print("REFERENCE_FREE:", actual.get("referenceFree") is True)
    print("PROFESSIONAL_REFERENCE_USED:", actual.get("professionalReferenceUsedByAnalyzer") is True)
    print("PRODUCTION_MODIFIED:", actual.get("productionModified") is True)
    print("EXACT_REPLAY:", mismatch is None)

    if mismatch is not None:
        print("FIRST_MISMATCH:", json.dumps(mismatch, ensure_ascii=False, sort_keys=True))
        raise RuntimeError("Section-5 reference-free carrier exact replay failed")

    print("SECTION5_REFERENCE_FREE_AUDIO_CARRIER_GATE_PASSED:", True)


if __name__ == "__main__":
    pass
