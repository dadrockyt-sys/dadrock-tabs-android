#!/usr/bin/env python3
"""First-run synthetic-only gate for the V7 reattack temporal/support diagnostic."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import onset_birth_corroboration_v6 as v6
import physical_template_plausibility_v3 as v3
import v6_innovation_peak_band_bridge_v2 as bridge
import v7_reattack_temporal_support_diagnostics_v1 as diagnostic

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "v6_onset_birth_synthetic_fixtures.json"
REPETITIONS = 3
EXPECTED_FIXTURE_CONTRACT = "songsterr-fresh-v6-onset-birth-synthetic-fixtures-v1"
EXPECTED_DIAGNOSTIC_CONTRACT = "songsterr-fresh-v7-reattack-temporal-support-diagnostic-v1"


class MechanicalInvariantError(RuntimeError):
    pass


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _check_finite(value: Any, path: str = "root") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise MechanicalInvariantError(f"NONFINITE:{path}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _check_finite(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            _check_finite(item, f"{path}.{key}")
        return
    raise MechanicalInvariantError(f"UNEXPECTED_TYPE:{path}:{type(value).__name__}")


def _evaluate_fixture(fixture: dict[str, Any], frequencies: np.ndarray) -> dict[str, Any]:
    selected_midi = int(fixture["selectedMidi"])
    onset_sample = int(round(float(fixture["onsetSeconds"]) * v6.SAMPLE_RATE))
    audio = v6._fixture_audio(fixture)
    row = diagnostic.evaluate_temporal_support_diagnostic(
        audio,
        onset_sample,
        selected_midi,
        frequencies,
    )
    if row.get("contract") != EXPECTED_DIAGNOSTIC_CONTRACT or row.get("version") != 1:
        raise MechanicalInvariantError(f"CONTRACT:{fixture['id']}")
    if row.get("selectedMidi") != selected_midi:
        raise MechanicalInvariantError(f"MIDI_IDENTITY:{fixture['id']}")
    if row.get("finalDecisionDefined") is not False or "finalDecision" in row:
        raise MechanicalInvariantError(f"FINAL_DECISION_DEFINED:{fixture['id']}")
    _check_finite(row, str(fixture["id"]))

    onset_available = row.get("onsetAvailable") is True
    traces = row.get("anchorTraces")
    if not isinstance(traces, list):
        raise MechanicalInvariantError(f"ANCHOR_TRACE_TYPE:{fixture['id']}")
    if onset_available:
        if len(traces) != len(v3.DETUNE_CENTS):
            raise MechanicalInvariantError(f"ANCHOR_COUNT:{fixture['id']}:{len(traces)}")
        bridge_diag = row.get("bridgeDiagnostics")
        if not isinstance(bridge_diag, dict):
            raise MechanicalInvariantError(f"BRIDGE_DIAGNOSTIC_MISSING:{fixture['id']}")
        if bridge_diag.get("amplitudeBoosted") is not False:
            raise MechanicalInvariantError(f"BRIDGE_AMPLITUDE_BOOST:{fixture['id']}")
        retained_bins = {int(value) for value in bridge_diag.get("retainedBins", [])}
        if len(retained_bins) != int(bridge_diag.get("retainedPositiveBinCount", -1)):
            raise MechanicalInvariantError(f"RETAINED_BIN_COUNT:{fixture['id']}")
        if row.get("selectedTemplate") is None:
            raise MechanicalInvariantError(f"SELECTED_TEMPLATE_MISSING:{fixture['id']}")
        if len(row.get("frameEndOffsets", [])) != len(v6.FRAME_END_OFFSETS):
            raise MechanicalInvariantError(f"FRAME_OFFSET_COUNT:{fixture['id']}")
        if len(row.get("frameRms", [])) != len(v6.FRAME_END_OFFSETS):
            raise MechanicalInvariantError(f"FRAME_RMS_COUNT:{fixture['id']}")
        if len(row.get("frameDeviationNorms", [])) != len(v6.FRAME_END_OFFSETS):
            raise MechanicalInvariantError(f"FRAME_DEVIATION_COUNT:{fixture['id']}")
    else:
        if traces:
            raise MechanicalInvariantError(f"FABRICATED_ANCHOR_TRACE:{fixture['id']}")
        if row.get("selectedTemplate") is not None:
            raise MechanicalInvariantError(f"FABRICATED_SELECTED_TEMPLATE:{fixture['id']}")
        if row.get("bridgeDiagnostics") is not None:
            raise MechanicalInvariantError(f"FABRICATED_BRIDGE_DIAGNOSTIC:{fixture['id']}")

    return {
        "fixtureId": str(fixture["id"]),
        "selectedMidi": selected_midi,
        "referenceExpectedClassification": str(fixture["expectedClassification"]),
        "referenceExpectedUsedForComputation": False,
        "diagnostic": row,
    }


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest.get("contract") != EXPECTED_FIXTURE_CONTRACT:
        raise MechanicalInvariantError("FIXTURE_CONTRACT_MISMATCH")
    fixtures = manifest.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) != 23:
        raise MechanicalInvariantError("EXPECTED_23_FIXTURES")

    if diagnostic.CONTRACT != EXPECTED_DIAGNOSTIC_CONTRACT or diagnostic.VERSION != 1:
        raise MechanicalInvariantError("DIAGNOSTIC_CONTRACT_MISMATCH")
    if bridge.LINE_SUPPRESSION_RADIUS_BINS != 8 or bridge.PEAK_BAND_RADIUS_BINS != 1:
        raise MechanicalInvariantError("BRIDGE_GEOMETRY_CHANGED")
    if v3.PEAK_BIN_RADIUS != 1 or v3.BACKGROUND_BIN_RADIUS != 6:
        raise MechanicalInvariantError("V3_LOCAL_GEOMETRY_CHANGED")
    if v3.LOCAL_SNR_MULTIPLIER != 3.0 or v3.RELATIVE_HARMONIC_SUPPORT_FLOOR != 0.10:
        raise MechanicalInvariantError("V3_SUPPORT_THRESHOLDS_CHANGED")
    if v3.MIN_SUPPORTED_HARMONICS != 3 or v3.MIN_WEIGHTED_HARMONIC_COVERAGE != 0.35:
        raise MechanicalInvariantError("V3_SUPPORT_GATES_CHANGED")

    frequencies = np.fft.rfftfreq(v6.FFT_SIZE, d=1.0 / float(v6.SAMPLE_RATE))
    if not np.allclose(frequencies, v3.expected_frequencies(), rtol=0.0, atol=1e-12):
        raise MechanicalInvariantError("FREQUENCY_GRID_MISMATCH")

    repetitions: list[list[dict[str, Any]]] = []
    for _ in range(REPETITIONS):
        repetitions.append([_evaluate_fixture(fixture, frequencies) for fixture in fixtures])

    canonical_runs = [_canonical(rows) for rows in repetitions]
    deterministic = len(set(canonical_runs)) == 1
    if not deterministic:
        raise MechanicalInvariantError("NONDETERMINISTIC_OUTPUT")

    rows = repetitions[0]
    expected_ids = [str(fixture["id"]) for fixture in fixtures]
    observed_ids = [str(row["fixtureId"]) for row in rows]
    if observed_ids != expected_ids:
        raise MechanicalInvariantError("FIXTURE_ORDER_CHANGED")

    onset_available_count = sum(
        1 for row in rows if row["diagnostic"].get("onsetAvailable") is True
    )
    selected_template_valid_count = sum(
        1
        for row in rows
        if isinstance(row["diagnostic"].get("selectedTemplate"), dict)
        and row["diagnostic"]["selectedTemplate"].get("valid") is True
    )

    output = {
        "contract": "songsterr-fresh-v7-reattack-temporal-support-diagnostic-synthetic-test-v1",
        "diagnosticContract": diagnostic.CONTRACT,
        "fixtureContract": manifest["contract"],
        "fixtureCount": len(rows),
        "repetitions": REPETITIONS,
        "deterministic": deterministic,
        "onsetAvailableCount": onset_available_count,
        "selectedTemplateValidCount": selected_template_valid_count,
        "finalDecisionDefined": False,
        "referenceExpectedUsedForComputation": False,
        "realCorpusEvaluated": False,
        "modelInferenceInvoked": False,
        "basicPitchInvoked": False,
        "networkInvoked": False,
        "customerEligibleEvents": 0,
        "mayAdvanceDelivery": False,
        "mechanicalDiagnosticStatus": "COMPLETE",
        "rows": rows,
    }
    print(json.dumps(output, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
