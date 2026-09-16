#!/usr/bin/env python3
"""First-run synthetic seam test for V6 innovation line bridge iteration 1.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE.md

No real media, model inference, network access or repository mutation is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3_iteration3 as v3
import v6_innovation_line_bridge_v1 as bridge

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3

EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


def _expect_bridge_error(value) -> None:
    try:
        bridge.collapse_hann_main_lobes(value)
    except bridge.InnovationLineBridgeError:
        return
    raise AssertionError("expected InnovationLineBridgeError")


def _structural_checks() -> dict:
    length = bridge.EXPECTED_VECTOR_LENGTH

    zero = np.zeros(length, dtype=np.float64)
    zero_out = bridge.collapse_hann_main_lobes(zero)
    assert np.array_equal(zero_out, zero)

    isolated = np.zeros(length, dtype=np.float64)
    isolated[100] = 3.25
    isolated_out = bridge.collapse_hann_main_lobes(isolated)
    assert np.flatnonzero(isolated_out).tolist() == [100]
    assert isolated_out[100] == isolated[100]

    # Geometry-derived Hann main-lobe check: a frame-bin-centered sinusoid in
    # the frozen 2048-sample Hann frame is zero-padded to the frozen 8192 FFT.
    # The bridge must reduce the +/-8-bin main-lobe neighborhood to its peak.
    native_bin = 37
    samples = np.arange(v6.FRAME_SAMPLES, dtype=np.float64)
    tone = np.sin(2.0 * math.pi * native_bin * samples / float(v6.FRAME_SAMPLES))
    hann_spectrum = np.abs(
        np.fft.rfft(tone * np.hanning(v6.FRAME_SAMPLES), n=v6.FFT_SIZE)
    )
    hann_out = bridge.collapse_hann_main_lobes(hann_spectrum)
    center = native_bin * bridge.ZERO_PADDING_FACTOR
    local_survivors = [
        int(index)
        for index in np.flatnonzero(hann_out > 0.0)
        if center - bridge.LINE_SUPPRESSION_RADIUS_BINS
        <= int(index)
        <= center + bridge.LINE_SUPPRESSION_RADIUS_BINS
    ]
    assert local_survivors == [center], local_survivors
    assert hann_out[center] == hann_spectrum[center]

    separated = np.zeros(length, dtype=np.float64)
    separated[200] = 2.0
    separated[209] = 1.5
    separated_out = bridge.collapse_hann_main_lobes(separated)
    assert np.flatnonzero(separated_out).tolist() == [200, 209]

    stronger = np.zeros(length, dtype=np.float64)
    stronger[300] = 2.0
    stronger[307] = 1.0
    stronger_out = bridge.collapse_hann_main_lobes(stronger)
    assert np.flatnonzero(stronger_out).tolist() == [300]

    tied = np.zeros(length, dtype=np.float64)
    tied[400] = 2.0
    tied[408] = 2.0
    tied_out = bridge.collapse_hann_main_lobes(tied)
    assert np.flatnonzero(tied_out).tolist() == [400]

    mixed = np.zeros(length, dtype=np.float64)
    mixed[50] = 0.5
    mixed[55] = 0.25
    mixed[150] = 1.0
    mixed[170] = 0.75
    mixed_out = bridge.collapse_hann_main_lobes(mixed)
    retained = np.flatnonzero(mixed_out > 0.0)
    assert all(mixed_out[index] == mixed[index] for index in retained)
    assert np.all(mixed_out <= mixed)

    scale = 7.25
    scaled_out = bridge.collapse_hann_main_lobes(scale * mixed)
    assert np.array_equal(np.flatnonzero(scaled_out), retained)
    assert np.array_equal(scaled_out[retained], scale * mixed_out[retained])

    _expect_bridge_error(np.zeros((1, length), dtype=np.float64))
    _expect_bridge_error(np.zeros(length - 1, dtype=np.float64))
    negative = np.zeros(length, dtype=np.float64)
    negative[5] = -1.0
    _expect_bridge_error(negative)
    nonfinite = np.zeros(length, dtype=np.float64)
    nonfinite[5] = np.nan
    _expect_bridge_error(nonfinite)
    infinite = np.zeros(length, dtype=np.float64)
    infinite[5] = np.inf
    _expect_bridge_error(infinite)

    return {
        "lineSuppressionRadiusBins": bridge.LINE_SUPPRESSION_RADIUS_BINS,
        "zeroPaddingFactor": bridge.ZERO_PADDING_FACTOR,
        "expectedVectorLength": bridge.EXPECTED_VECTOR_LENGTH,
        "hannCenterBin": center,
        "hannMainLobeLocalSurvivors": local_survivors,
        "isolatedRetained": [100],
        "separatedRetained": [200, 209],
        "strongerRetained": [300],
        "tieRetained": [400],
        "scaleInvariant": True,
        "malformedFailClosed": True,
    }


def _pass_necessity(result: dict) -> float:
    iteration2 = result.get("iteration2Composite")
    if not isinstance(iteration2, dict):
        raise AssertionError("missing iteration2 composite on PASS")
    base = iteration2.get("baseComposite")
    if not isinstance(base, dict):
        raise AssertionError("missing base composite on PASS")
    value = base.get("necessityFraction")
    if not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise AssertionError("nonfinite necessity on PASS")
    return float(value)


def _evaluate_fixture(fixture: dict, frequencies: np.ndarray) -> dict:
    audio = v6._fixture_audio(fixture)
    selected_midi = int(fixture["selectedMidi"])
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))

    try:
        onset = v6._onset_innovation_spectrum(audio, onset_sample)
    except v6.CorroborationError as exc:
        actual = v6.CLASS_INSUFFICIENT
        return {
            "id": fixture["id"],
            "expected": fixture["expectedClassification"],
            "actual": actual,
            "selectedMidi": selected_midi,
            "onsetStatus": "CONTEXT_ERROR",
            "reason": str(exc),
            "bridgeApplied": False,
            "v3Status": None,
            "necessityFraction": None,
            "candidateEvidenceFraction": None,
            "retainedPositiveBinCount": 0,
        }

    if onset.get("status") != "OK":
        return {
            "id": fixture["id"],
            "expected": fixture["expectedClassification"],
            "actual": v6.CLASS_INSUFFICIENT,
            "selectedMidi": selected_midi,
            "onsetStatus": onset.get("status"),
            "reason": onset.get("status"),
            "bridgeApplied": False,
            "v3Status": None,
            "necessityFraction": None,
            "candidateEvidenceFraction": None,
            "retainedPositiveBinCount": 0,
        }

    raw = np.asarray(onset["innovation"], dtype=np.float64)
    line = bridge.collapse_hann_main_lobes(raw)
    result = v3.evaluate_evidence_significance_composite(selected_midi, line, frequencies)
    actual = v6.CLASS_CORROBORATED if result.get("passed") is True else v6.CLASS_NOT_CORROBORATED

    necessity = None
    candidate_fraction = result.get("candidateEvidenceFraction")
    if result.get("passed") is True:
        necessity = _pass_necessity(result)
        if necessity < 0.01:
            raise AssertionError(f"{fixture['id']} PASS necessity below frozen minimum: {necessity}")
        if not isinstance(candidate_fraction, (int, float)) or not math.isfinite(float(candidate_fraction)):
            raise AssertionError(f"{fixture['id']} PASS candidate evidence is nonfinite")
        if float(candidate_fraction) < 0.10:
            raise AssertionError(
                f"{fixture['id']} PASS candidate evidence below frozen minimum: {candidate_fraction}"
            )

    return {
        "id": fixture["id"],
        "expected": fixture["expectedClassification"],
        "actual": actual,
        "selectedMidi": selected_midi,
        "onsetStatus": onset.get("status"),
        "analysisRms": onset.get("analysisRms"),
        "rawInnovationEnergy": onset.get("innovationEnergy"),
        "rawPositiveBinCount": int(np.count_nonzero(raw > 0.0)),
        "retainedPositiveBinCount": int(np.count_nonzero(line > 0.0)),
        "bridgeApplied": True,
        "v3Status": result.get("status"),
        "necessityFraction": necessity,
        "candidateEvidenceFraction": (
            float(candidate_fraction)
            if isinstance(candidate_fraction, (int, float)) and math.isfinite(float(candidate_fraction))
            else None
        ),
        "vetoingOwnerMidis": [
            int(row.get("ownerMidi"))
            for row in result.get("vetoingOwners", [])
            if isinstance(row, dict) and isinstance(row.get("ownerMidi"), int)
        ],
    }


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest.get("contract") == EXPECTED_FIXTURE_CONTRACT
    fixtures = manifest.get("fixtures")
    assert isinstance(fixtures, list) and len(fixtures) == 23

    assert bridge.CONTRACT == "songsterr-fresh-v6-innovation-line-bridge-synthetic-research-v1"
    assert bridge.VERSION == 1
    assert bridge.FRAME_SAMPLES == 2048
    assert bridge.FFT_SIZE == 8192
    assert bridge.ZERO_PADDING_FACTOR == 4
    assert bridge.LINE_SUPPRESSION_RADIUS_BINS == 8

    structural = _structural_checks()
    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))

    repetitions: list[list[dict]] = []
    for _ in range(REPETITIONS):
        rows = [_evaluate_fixture(fixture, frequencies) for fixture in fixtures]
        repetitions.append(rows)

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise AssertionError("bridge fixture results were not deterministic")

    rows = repetitions[0]
    mismatches = [row for row in rows if row["actual"] != row["expected"]]

    summary = {
        "contract": "songsterr-fresh-v7-representation-bridge-synthetic-test-v1",
        "bridgeContract": bridge.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "mismatchCount": len(mismatches),
        "mismatches": mismatches,
        "structuralChecks": structural,
        "rows": rows,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "result": "PASS" if not mismatches else "FAIL",
    }
    print(json.dumps(summary, indent=2, allow_nan=False))

    if mismatches:
        raise SystemExit(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
