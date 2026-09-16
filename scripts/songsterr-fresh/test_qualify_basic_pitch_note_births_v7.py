#!/usr/bin/env python3
"""Prospectively frozen synthetic prerequisite for V7 boundary real evaluation.

Fixture synthesis and temporary WAV/model helpers are reused from the frozen V2
boundary test. This file re-expresses the eight frozen behavioral expectations
against the new V7 qualifier and adds V7 contract/diagnostic invariants.
No real corpus or model inference is used.
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np

import onset_birth_corroboration_v7 as v7
import qualify_basic_pitch_note_births_v7 as qualifier_v7
import test_qualify_basic_pitch_note_births_v2 as frozen_suite
from onset_birth_corroboration_v6 import SAMPLE_RATE, _synth_events

ROOT = Path(__file__).resolve().parents[2]
QUALIFIER = ROOT / "scripts" / "songsterr-fresh" / "qualify_basic_pitch_note_births_v7.py"


def statuses(payload: dict) -> list[str]:
    return [str(row["status"]) for row in payload["proposals"]]


def run_qualifier(root: Path, label: str, audio: np.ndarray, notes: list[dict]) -> dict:
    old = frozen_suite.QUALIFIER
    frozen_suite.QUALIFIER = QUALIFIER
    try:
        return frozen_suite.run_qualifier(root, label, audio, notes)
    finally:
        frozen_suite.QUALIFIER = old


def assert_v7_payload(payload: dict) -> None:
    assert payload.get("contract") == qualifier_v7.CONTRACT, json.dumps(payload, indent=2)
    assert payload.get("version") == qualifier_v7.VERSION
    assert payload.get("candidateConfidenceUsedForDecision") is False
    assert payload.get("independentOfBasicPitchCandidateConfidence") is True
    assert payload.get("provenance", {}).get("modelInvokedByQualifier") is False
    assert payload.get("provenance", {}).get("gpuInvoked") is False
    assert payload.get("provenance", {}).get("networkInvoked") is False
    assert payload.get("provenance", {}).get("syntheticPreContextUsed") is False
    assert payload.get("diagnostics", {}).get("v7DependencyContractIntegrity") is True

    for row in payload.get("proposals", []):
        provenance = row.get("provenance", {})
        assert provenance.get("candidateConfidenceReadForDecision") is False
        assert provenance.get("syntheticPreContextUsed") is False
        assert provenance.get("leftBoundaryZeroPaddingSamples") == 0
        if row.get("status") == "corroborated":
            necessity = provenance.get("necessityFraction")
            evidence = provenance.get("candidateEvidenceFraction")
            assert isinstance(necessity, (int, float)) and math.isfinite(float(necessity)), json.dumps(row, indent=2)
            assert float(necessity) >= v7.EXPECTED_NECESSITY_FRACTION_MIN, json.dumps(row, indent=2)
            assert isinstance(evidence, (int, float)) and math.isfinite(float(evidence)), json.dumps(row, indent=2)
            assert float(evidence) >= v7.EXPECTED_CANDIDATE_EVIDENCE_FRACTION_MIN, json.dumps(row, indent=2)
            assert provenance.get("vetoingOwners") == [], json.dumps(row, indent=2)


def main() -> int:
    assert v7._dependency_contract_ok()
    observed_payloads: list[dict] = []

    with tempfile.TemporaryDirectory(prefix="songsterr-dsp-qualifier-v7-") as tmp:
        root = Path(tmp)

        # 1. Frozen normal in-clip behavior: true E2 birth corroborates and
        # later fifth-harmonic-area proposal rejects.
        normal_audio, _rng = _synth_events(
            1.6,
            [{
                "onsetSeconds": 0.25,
                "stopSeconds": 1.5,
                "midi": 40,
                "amplitude": 0.8,
                "decayPerSecond": 0.35,
            }],
            seed=17,
        )
        normal_notes = [
            frozen_suite.note("normal-e2", 0.25, 40, 0.79),
            frozen_suite.note("normal-harmonic", 0.65, 68, 0.35),
        ]
        normal = run_qualifier(root, "normal", normal_audio, normal_notes)
        observed_payloads.append(normal)
        assert statuses(normal) == ["corroborated", "rejected"], json.dumps(normal, indent=2)
        assert all(
            row["provenance"]["qualificationMode"] == "normal-in-clip-onset-birth-v7"
            for row in normal["proposals"]
        )

        # 2. Candidate confidence remains diagnostic-only.
        flipped = run_qualifier(
            root,
            "confidence-flipped",
            normal_audio,
            [
                frozen_suite.note("normal-e2", 0.25, 40, 0.01),
                frozen_suite.note("normal-harmonic", 0.65, 68, 0.99),
            ],
        )
        observed_payloads.append(flipped)
        assert statuses(flipped) == statuses(normal)

        # 3. Frozen clip-start single-note recovery across several MIDI values.
        boundary_true_midis = [40, 45, 52, 68]
        boundary_true_statuses: dict[str, str] = {}
        for midi in boundary_true_midis:
            audio, _rng = _synth_events(
                1.0,
                [{
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": midi,
                    "amplitude": 0.8,
                    "decayPerSecond": 0.45,
                }],
                seed=100 + midi,
            )
            result = run_qualifier(
                root,
                f"boundary-true-{midi}",
                audio,
                [frozen_suite.note(f"boundary-true-{midi}", 0.011, midi, 0.4)],
            )
            observed_payloads.append(result)
            assert statuses(result) == ["corroborated"], json.dumps(result, indent=2)
            row = result["proposals"][0]
            assert row["provenance"]["qualificationMode"] == "clip-start-one-sided-pitch-presence-v7"
            assert row["provenance"]["evidenceKind"] == "clip-start-post-spectrum-evidence"
            boundary_true_statuses[str(midi)] = row["status"]

        # 4. Frozen clip-start alias behavior on E2-only audio.
        boundary_e2, _rng = _synth_events(
            1.0,
            [{
                "onsetSeconds": 0.011,
                "stopSeconds": 0.9,
                "midi": 40,
                "amplitude": 0.8,
                "decayPerSecond": 0.45,
            }],
            seed=211,
        )
        alias_result = run_qualifier(
            root,
            "boundary-aliases",
            boundary_e2,
            [
                frozen_suite.note("boundary-e2", 0.011, 40, 0.2),
                frozen_suite.note("boundary-octave-alias", 0.011, 52, 0.9),
                frozen_suite.note("boundary-fifth-alias", 0.011, 68, 0.99),
            ],
        )
        observed_payloads.append(alias_result)
        assert statuses(alias_result) == ["corroborated", "rejected", "rejected"], json.dumps(alias_result, indent=2)

        # 5. Frozen genuine harmonic-related polyphony behavior.
        poly_audio, _rng = _synth_events(
            1.0,
            [
                {
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": 40,
                    "amplitude": 0.4,
                    "decayPerSecond": 0.45,
                    "phase": 0.17,
                },
                {
                    "onsetSeconds": 0.011,
                    "stopSeconds": 0.9,
                    "midi": 68,
                    "amplitude": 0.8,
                    "decayPerSecond": 0.45,
                    "phase": 0.39,
                },
            ],
            seed=313,
        )
        poly = run_qualifier(
            root,
            "boundary-real-polyphony",
            poly_audio,
            [
                frozen_suite.note("poly-e2", 0.011, 40, 0.1),
                frozen_suite.note("poly-gsharp4", 0.011, 68, 0.9),
            ],
        )
        observed_payloads.append(poly)
        assert statuses(poly) == ["corroborated", "corroborated"], json.dumps(poly, indent=2)

        # 6. Noise-only clip-start evidence must not corroborate.
        rng = np.random.default_rng(404)
        noise_audio = 0.02 * rng.standard_normal(int(round(1.0 * SAMPLE_RATE)))
        noise = run_qualifier(
            root,
            "boundary-noise",
            noise_audio,
            [frozen_suite.note("noise", 0.011, 52, 0.5)],
        )
        observed_payloads.append(noise)
        assert statuses(noise)[0] != "corroborated", json.dumps(noise, indent=2)

        # 7. Missing genuine future context remains insufficient.
        short_audio, _rng = _synth_events(
            0.15,
            [{
                "onsetSeconds": 0.011,
                "stopSeconds": 0.14,
                "midi": 45,
                "amplitude": 0.8,
                "decayPerSecond": 0.45,
            }],
            seed=515,
        )
        short = run_qualifier(
            root,
            "boundary-short",
            short_audio,
            [frozen_suite.note("short", 0.011, 45, 0.4)],
        )
        observed_payloads.append(short)
        assert statuses(short) == ["insufficient"], json.dumps(short, indent=2)

        # 8. Normal right-edge missing context remains insufficient.
        right_edge = run_qualifier(
            root,
            "normal-right-edge",
            normal_audio,
            [frozen_suite.note("right-edge", 1.59, 40, 0.99)],
        )
        observed_payloads.append(right_edge)
        assert statuses(right_edge) == ["insufficient"], json.dumps(right_edge, indent=2)

        for payload in observed_payloads:
            assert_v7_payload(payload)

        summary = {
            "contract": "songsterr-fresh-independent-note-qualification-v7-boundary-test-v1",
            "status": "PASS",
            "cases": 8,
            "normalStatuses": statuses(normal),
            "confidenceInvariant": statuses(flipped) == statuses(normal),
            "boundaryTrueStatuses": boundary_true_statuses,
            "boundaryAliasStatuses": statuses(alias_result),
            "boundaryPolyphonyStatuses": statuses(poly),
            "noiseDidNotCorroborate": statuses(noise)[0] != "corroborated",
            "missingPostContextInsufficient": statuses(short) == ["insufficient"],
            "rightEdgeContextInsufficient": statuses(right_edge) == ["insufficient"],
            "allCorroboratedRowsCarryFrozenV7ThresholdDiagnostics": True,
            "syntheticPreContextUsed": False,
            "modelInferenceInvoked": False,
            "realCorpusEvaluated": False,
            "networkInvoked": False,
            "customerEligibleEvents": 0,
            "mayAdvanceDelivery": False,
        }
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
