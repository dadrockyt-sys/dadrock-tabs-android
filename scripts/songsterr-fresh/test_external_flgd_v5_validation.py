#!/usr/bin/env python3
"""Controlled contract tests for external_flgd_v5_validation.py.

No FLGD checkout, Basic Pitch model call, real V5 call or real-corpus
correctness is permitted here.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("external_flgd_v5_validation.py")
spec = importlib.util.spec_from_file_location("flgd_v5_scoring", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def expect_error(fn, text: str) -> None:
    try:
        fn()
    except m.ValidationError as exc:
        assert text in str(exc), (text, str(exc))
    else:
        raise AssertionError(f"expected ValidationError containing {text}")


class FakeV5:
    """Synthetic classifier used only to test event bookkeeping."""

    @staticmethod
    def classify_audio_event(_audio, _onset_sample: int, midi: int) -> dict:
        mapping = {
            60: m.CLASS_POSITIVE,
            61: m.CLASS_NEGATIVE,
            62: m.CLASS_INSUFFICIENT,
        }
        return {"classification": mapping[midi], "reason": f"FAKE_{midi}"}


def main() -> int:
    assert m.CONTRACT == "songsterr-fresh-flgd-v5-external-validation-v1"
    assert m.EXPECTED_PERFORMANCE_COUNT == 79
    assert m.EXPECTED_REFERENCE_EVENT_COUNT == 76392
    assert m.EXPECTED_IGNORED_RELEASE_COUNT == 24
    assert m.SAMPLE_RATE == 44100
    assert m.MIN_MIDI == 40 and m.MAX_MIDI == 88
    assert m.ONSET_TOLERANCE_SECONDS == 0.050
    assert m.PITCH_TOLERANCE_CENTS == 50.0
    assert m.INCLUSIVE_ABS_TOL == 1e-12
    assert m.MIN_TOTAL_POSITIVES == 1000
    assert m.OVERALL_WILSON_LOWER_BOUND_MIN == 0.9900
    assert m.STRATUM_MIN_POSITIVES == 100
    assert m.STRATUM_POINT_PRECISION_MIN == 0.9500

    # The mathematical boundary is inclusive even when binary64 represents
    # 1.05 - 1.0 a hair above 0.05.
    assert m.inclusive_at_limit(1.05 - 1.0, 0.050)
    assert m.inclusive_at_limit(0.050, 0.050)
    assert not m.inclusive_at_limit(0.05000000001, 0.050)

    # Duration/end fields are deliberately irrelevant to correctness.
    estimate = {
        "noteId": "e0",
        "startSeconds": 3.05,
        "midi": 60,
        "diagnosticModelEndSeconds": 99.0,
    }
    reference = {
        "referenceId": "r0",
        "onsetSeconds": 3.0,
        "midi": 60,
        "offsetSeconds": 3.001,
    }
    assert m.valid_match(estimate, reference)
    assert not m.valid_match({**estimate, "midi": 61}, reference)

    # Maximum-cardinality matching must find both same-pitch references rather
    # than greedily consuming the only compatible reference for the second note.
    refs = [
        {"referenceId": "r0", "onsetSeconds": 1.00, "midi": 60},
        {"referenceId": "r1", "onsetSeconds": 1.04, "midi": 60},
    ]
    estimates = [
        {"noteId": "e0", "startSeconds": 1.05, "midi": 60},
        {"noteId": "e1", "startSeconds": 1.00, "midi": 60},
    ]
    matches = m.maximum_cardinality_matches(estimates, refs)
    assert len(matches) == 2
    assert len(set(matches.values())) == 2

    # Event identity/classification bookkeeping is tested with a fake classifier,
    # so this controlled test never imports or executes the real V5 implementation.
    identity_events = [
        {"noteId": "n0", "startSeconds": 0.10, "midi": 60},
        {"noteId": "n1", "startSeconds": 0.20, "midi": 61},
        {"noteId": "n2", "startSeconds": 0.30, "midi": 62},
    ]
    classified, counts = m.classify_events(FakeV5(), object(), identity_events)
    assert counts == {
        m.CLASS_POSITIVE: 1,
        m.CLASS_NEGATIVE: 1,
        m.CLASS_INSUFFICIENT: 1,
    }
    assert [(x["noteId"], x["startSeconds"], x["midi"]) for x in classified] == [
        (x["noteId"], x["startSeconds"], x["midi"]) for x in identity_events
    ]

    # Wilson primary gate is deliberately stricter than point precision.
    assert m.wilson_lower_one_sided_95(1000, 1000) > 0.99
    assert m.wilson_lower_one_sided_95(990, 1000) < 0.99
    assert m.wilson_lower_one_sided_95(0, 0) is None

    rows = [
        {
            "split": "train",
            "guitarType": "nylon",
            "decodedEventCount": 800,
            "referenceEventCount": 800,
            "positiveCount": 600,
            "positiveCorrectCount": 600,
        },
        {
            "split": "validate",
            "guitarType": "acoustic",
            "decodedEventCount": 60,
            "referenceEventCount": 60,
            "positiveCount": 50,
            "positiveCorrectCount": 20,
        },
        {
            "split": "test",
            "guitarType": "electric",
            "decodedEventCount": 600,
            "referenceEventCount": 600,
            "positiveCount": 500,
            "positiveCorrectCount": 500,
        },
    ]
    aggregate = {
        "completedFileCount": 79,
        "decodedEventCount": 1460,
        "classifiedEventCount": 1460,
        "positiveEventCount": 1150,
        "positivePrecisionWilsonLowerOneSided95": m.wilson_lower_one_sided_95(1150, 1150),
        "bySplit": m.summarize_by(rows, "split"),
        "byGuitarType": m.summarize_by(rows, "guitarType"),
        "identityRuntimeGuards": True,
        "policyBoundaryGuard": True,
    }
    gates = m.evaluate_gates(aggregate)
    # validate/acoustic are deliberately poor but under the frozen 100-positive
    # minimum, so they remain diagnostic instead of becoming a size-only fail.
    assert gates["splitRobustness"]["validate"] is True
    assert gates["guitarTypeRobustness"]["acoustic"] is True
    assert gates["allMandatoryGatesPassed"] is True

    # A mandatory-sized weak stratum fails.
    bad_rows = [
        {
            "split": "train",
            "guitarType": "nylon",
            "decodedEventCount": 200,
            "referenceEventCount": 200,
            "positiveCount": 100,
            "positiveCorrectCount": 94,
        }
    ]
    aggregate["bySplit"] = m.summarize_by(bad_rows, "split")
    aggregate["byGuitarType"] = m.summarize_by(bad_rows, "guitarType")
    gates = m.evaluate_gates(aggregate)
    assert gates["splitRobustness"]["train"] is False
    assert gates["guitarTypeRobustness"]["nylon"] is False
    assert gates["allMandatoryGatesPassed"] is False

    # Runtime guard logic is exercised without installing Basic Pitch.  The
    # metadata-version source is temporarily replaced with exact synthetic
    # package identities, then one deliberate drift must fail closed.
    real_version = m.importlib.metadata.version
    expected_versions = {
        "basic-pitch": m.BASIC_PITCH_VERSION,
        "numpy": m.NUMPY_VERSION,
        "scipy": m.SCIPY_VERSION,
        "librosa": m.LIBROSA_VERSION,
        "soundfile": m.SOUNDFILE_VERSION,
    }
    try:
        m.importlib.metadata.version = lambda name: expected_versions[name]
        runtime = m.package_runtime()
        assert runtime["packages"] == expected_versions
        drifted = dict(expected_versions)
        drifted["numpy"] = "9.9.9"
        m.importlib.metadata.version = lambda name: drifted[name]
        expect_error(lambda: m.package_runtime(), "RUNTIME_PACKAGE_VERSION_CHANGED:numpy")
    finally:
        m.importlib.metadata.version = real_version

    # Synthetic Basic Pitch payload validation checks settings/provenance while
    # ignoring diagnostic model end/confidence as scoring inputs.
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "basic-pitch.json"
        payload = {
            "contract": "songsterr-fresh-basic-pitch-isolated-guitar-v1",
            "referenceBlind": True,
            "role": "guitar",
            "model": {
                "packageVersion": "0.4.0",
                "minimumMidi": 40,
                "maximumMidi": 88,
                "onsetThreshold": 0.5,
                "frameThreshold": 0.3,
                "minimumNoteLengthMs": 127.7,
            },
            "notes": [
                {
                    "noteId": "basic-pitch-note-000000",
                    "startSeconds": 0.25,
                    "diagnosticModelEndSeconds": 9.0,
                    "midi": 64,
                    "confidence": 0.01,
                }
            ],
            "diagnostics": {
                "modelNoteEndsUsedAsDuration": False,
                "predictInvocationCount": 1,
            },
            "provenance": {
                "gpuInvoked": False,
                "separationSource": m.SEPARATION_SOURCE,
            },
        }
        path.write_text(json.dumps(payload), encoding="utf-8")
        notes = m.validate_basic_pitch_payload(path)
        assert notes == [
            {
                "noteId": "basic-pitch-note-000000",
                "startSeconds": 0.25,
                "midi": 64,
            }
        ]
        payload["provenance"]["gpuInvoked"] = True
        path.write_text(json.dumps(payload), encoding="utf-8")
        expect_error(lambda: m.validate_basic_pitch_payload(path), "BASIC_PITCH_GPU_INVOKED")

        # A dummy Stage B file can never masquerade as the immutable report.
        stage_b = Path(td) / "stage-b.json"
        stage_b.write_text("{}", encoding="utf-8")
        expect_error(lambda: m.validate_stage_b_report(stage_b), "STAGE_B_REPORT_SHA256_CHANGED")

    result = m.self_test()
    assert result["selfTest"] == "PASS"
    boundary = result["policyBoundary"]
    assert boundary["realFLGDAccessed"] is False
    assert boundary["basicPitchInvoked"] is False
    assert boundary["v5ClassifierInvoked"] is False
    assert boundary["modelValidationComplete"] is False
    assert boundary["customerEligibleEvents"] == 0
    assert boundary["mayAdvanceDelivery"] is False

    print("FLGD_V5_SCORING_CONTROLLED_CONTRACT_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
