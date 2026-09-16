#!/usr/bin/env python3
"""First-run synthetic seam test for V6 innovation peak-band bridge iteration 2.

Frozen by:
  docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE_ITERATION2.md

No real media, model inference, network access or repository mutation is used.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3_iteration3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"


def _expect_bridge_error(value) -> None:
    try:
        bridge.collapse_hann_lobes_to_peak_bands(value)
    except bridge.InnovationPeakBandBridgeError:
        return
    raise AssertionError("expected InnovationPeakBandBridgeError")


def _structural_checks() -> dict:
    length = bridge.EXPECTED_VECTOR_LENGTH

    zero = np.zeros(length, dtype=np.float64)
    assert np.array_equal(bridge.collapse_hann_lobes_to_peak_bands(zero), zero)

    triplet = np.zeros(length, dtype=np.float64)
    triplet[99] = 1.1
    triplet[100] = 3.25
    triplet[101] = 0.9
    triplet_out = bridge.collapse_hann_lobes_to_peak_bands(triplet)
    assert np.flatnonzero(triplet_out).tolist() == [99, 100, 101]
    assert np.array_equal(triplet_out[99:102], triplet[99:102])

    native_bin = 37
    samples = np.arange(v6.FRAME_SAMPLES, dtype=np.float64)
    tone = np.sin(2.0 * math.pi * native_bin * samples / float(v6.FRAME_SAMPLES))
    hann_spectrum = np.abs(np.fft.rfft(tone * np.hanning(v6.FRAME_SAMPLES), n=v6.FFT_SIZE))
    hann_out = bridge.collapse_hann_lobes_to_peak_bands(hann_spectrum)
    center = native_bin * bridge.ZERO_PADDING_FACTOR
    local_survivors = [
        int(index)
        for index in np.flatnonzero(hann_out > 0.0)
        if center - bridge.LINE_SUPPRESSION_RADIUS_BINS
        <= int(index)
        <= center + bridge.LINE_SUPPRESSION_RADIUS_BINS
    ]
    assert local_survivors == [center - 1, center, center + 1], local_survivors
    assert np.array_equal(hann_out[center - 1:center + 2], hann_spectrum[center - 1:center + 2])

    separated = np.zeros(length, dtype=np.float64)
    separated[199:202] = [0.5, 2.0, 0.4]
    separated[208:211] = [0.3, 1.5, 0.2]
    separated_out = bridge.collapse_hann_lobes_to_peak_bands(separated)
    assert np.flatnonzero(separated_out).tolist() == [199, 200, 201, 208, 209, 210]

    stronger = np.zeros(length, dtype=np.float64)
    stronger[299:302] = [0.4, 2.0, 0.3]
    stronger[306:309] = [0.2, 1.0, 0.2]
    stronger_out = bridge.collapse_hann_lobes_to_peak_bands(stronger)
    assert np.flatnonzero(stronger_out).tolist() == [299, 300, 301]

    tied = np.zeros(length, dtype=np.float64)
    tied[399:402] = [0.2, 2.0, 0.1]
    tied[407:410] = [0.1, 2.0, 0.2]
    tied_out = bridge.collapse_hann_lobes_to_peak_bands(tied)
    assert np.flatnonzero(tied_out).tolist() == [399, 400, 401]

    mixed = np.zeros(length, dtype=np.float64)
    mixed[49:52] = [0.2, 0.5, 0.15]
    mixed[149:152] = [0.3, 1.0, 0.25]
    mixed[169:172] = [0.2, 0.75, 0.1]
    mixed_out = bridge.collapse_hann_lobes_to_peak_bands(mixed)
    retained = np.flatnonzero(mixed_out > 0.0)
    assert all(mixed_out[index] == mixed[index] for index in retained)
    assert np.all(mixed_out <= mixed)

    scale = 7.25
    scaled_out = bridge.collapse_hann_lobes_to_peak_bands(scale * mixed)
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
        "peakBandRadiusBins": bridge.PEAK_BAND_RADIUS_BINS,
        "zeroPaddingFactor": bridge.ZERO_PADDING_FACTOR,
        "expectedVectorLength": bridge.EXPECTED_VECTOR_LENGTH,
        "hannCenterBin": center,
        "hannMainLobeLocalSurvivors": local_survivors,
        "tripletRetained": [99, 100, 101],
        "separatedRetained": [199, 200, 201, 208, 209, 210],
        "strongerRetained": [299, 300, 301],
        "tieRetained": [399, 400, 401],
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
        return {
            "id": fixture["id"],
            "expected": fixture["expectedClassification"],
            "actual": v6.CLASS_INSUFFICIENT,
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
    bridged = bridge.collapse_hann_lobes_to_peak_bands(raw)
    result = v3.evaluate_evidence_significance_composite(selected_midi, bridged, frequencies)
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

    diagnostics = bridge.bridge_diagnostics(raw)
    return {
        "id": fixture["id"],
        "expected": fixture["expectedClassification"],
        "actual": actual,
        "selectedMidi": selected_midi,
        "onsetStatus": onset.get("status"),
        "analysisRms": onset.get("analysisRms"),
        "rawInnovationEnergy": onset.get("innovationEnergy"),
        "rawPositiveBinCount": int(np.count_nonzero(raw > 0.0)),
        "retainedCenterCount": int(diagnostics["centerCount"]),
        "retainedPositiveBinCount": int(np.count_nonzero(bridged > 0.0)),
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

    assert bridge.CONTRACT == "songsterr-fresh-v6-innovation-peak-band-bridge-synthetic-research-v2"
    assert bridge.VERSION == 2
    assert bridge.FRAME_SAMPLES == 2048
    assert bridge.FFT_SIZE == 8192
    assert bridge.ZERO_PADDING_FACTOR == 4
    assert bridge.LINE_SUPPRESSION_RADIUS_BINS == 8
    assert bridge.PEAK_BAND_RADIUS_BINS == 1

    structural = _structural_checks()
    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))

    repetitions: list[list[dict]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise AssertionError("peak-band bridge fixture results were not deterministic")

    rows = repetitions[0]
    mismatches = [row for row in rows if row["actual"] != row["expected"]]

    summary = {
        "contract": "songsterr-fresh-v7-representation-bridge-synthetic-test-v2",
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
