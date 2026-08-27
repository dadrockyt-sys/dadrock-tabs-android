#!/usr/bin/env python3
"""Reference-free contract tests for the frozen V154 CPU frontend.

These tests use only synthetic notes. They do not open audio or professional
references and do not invoke Basic Pitch or Demucs.
"""
from __future__ import annotations

import math

from score_frontend_reference import (
    GROSS_STEP_TOLERANCE,
    STEP_TOLERANCE,
    load_generated,
    load_reference,
    score_stream,
)
from transcribe_broad_other import STEP_SECONDS, grid_location, json_safe


def generated_payload() -> dict:
    return {
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "safety": {
            "referenceRead": False,
            "humanCorrection": False,
            "referenceGuidedFiltering": False,
            "modalUsed": False,
            "cudaGpuUsed": False,
        },
        "streams": {
            "combinedGuitar": [
                {"measure": 1, "step": 4.0, "midi": 64},
                {"measure": 1, "step": 8.0, "midi": 67},
            ],
            "bass": [
                {"measure": 1, "step": 0.0, "midi": 40},
            ],
        },
    }


def reference_payload() -> dict:
    return {
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "referenceAuthorization": {
            "userProvidedOrAuthorized": True,
            "privateScoringOnly": True,
        },
        "parts": {
            "rhythm": [
                {"measure": 1, "step": 4.25, "midi": 64},
            ],
            "lead": [
                {"measure": 1, "step": 8.40, "midi": 67},
                {"measure": 1, "step": 12.0, "midi": 72, "excludeFromScoring": True},
            ],
            "bass": [
                {"measure": 1, "step": 0.49, "midi": 40},
            ],
        },
    }


def main() -> int:
    # Serializer repair: nested NumPy-like scalar/list objects are handled via
    # tolist/item without importing NumPy in this synthetic test.
    class Scalar:
        def item(self):
            return 7

    class Vector:
        def tolist(self):
            return [Scalar(), 2]

    assert json_safe({"bend": Vector()}) == {"bend": [7, 2]}

    # Grid boundary checks are deterministic and use the frozen tempo.
    measure, step, nearest = grid_location(0.0)
    assert (measure, step, nearest) == (1, 0.0, 0)
    measure2, step2, nearest2 = grid_location(16 * STEP_SECONDS)
    assert measure2 == 2
    assert math.isclose(step2, 0.0, abs_tol=1e-9)
    assert nearest2 == 16

    generated_guitar, generated_bass = load_generated(generated_payload())
    reference_guitar, reference_bass, counts = load_reference(reference_payload())
    assert counts == {
        "rhythmIncluded": 1,
        "leadIncluded": 1,
        "bassIncluded": 1,
        "rhythmExcluded": 0,
        "leadExcluded": 1,
        "bassExcluded": 0,
    }

    guitar_score = score_stream(generated_guitar, reference_guitar)
    bass_score = score_stream(generated_bass, reference_bass)
    assert STEP_TOLERANCE == 0.50
    assert GROSS_STEP_TOLERANCE == 2.00
    assert guitar_score["primaryTimingAwarePitch"]["matched"] == 2
    assert guitar_score["primaryTimingAwarePitch"]["f1"] == 1.0
    assert bass_score["primaryTimingAwarePitch"]["matched"] == 1
    assert bass_score["primaryTimingAwarePitch"]["f1"] == 1.0

    # A same-pitch note outside ±0.5 but inside ±2 must be gross-only.
    gross_only = score_stream(
        [{"measure": 2, "step": 5.75, "midi": 60}],
        [{"measure": 2, "step": 4.0, "midi": 60}],
    )
    assert gross_only["primaryTimingAwarePitch"]["matched"] == 0
    assert gross_only["grossTimingAwarePitch"]["matched"] == 1

    # Anti-leakage proof is mandatory.
    bad_generated = generated_payload()
    bad_generated["safety"]["referenceRead"] = True
    try:
        load_generated(bad_generated)
    except ValueError as exc:
        assert "referenceRead=false" in str(exc)
    else:
        raise AssertionError("generated payload with referenceRead=true was accepted")

    # Private-reference authorization is mandatory.
    bad_reference = reference_payload()
    bad_reference["referenceAuthorization"]["privateScoringOnly"] = False
    try:
        load_reference(bad_reference)
    except ValueError as exc:
        assert "authorization" in str(exc)
    else:
        raise AssertionError("unauthorized private reference was accepted")

    print("V154 reference-free contract tests: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
