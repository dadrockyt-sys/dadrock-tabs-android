#!/usr/bin/env python3
"""Independent sealed V161 timebase QC; hard pre-pitch boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

SCHEMA = "dadrock.tabs.v161.reference-blind-timebase-qc.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v161.reference-blind-timebase.v1"
SR = 22050
HOP = 256


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def finite_scalar(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def exact_identity(record: Any, path: Path) -> bool:
    return isinstance(record, dict) and record.get("path") == str(path) and record.get("sha256") == sha256_file(path) and record.get("bytes") == path.stat().st_size


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--source-audio", type=Path, required=True)
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.receipt.exists():
        raise RuntimeError("V161 timebase-QC receipt is write-once")
    for path in (args.timebase, args.source_audio, args.mix, args.drums, args.bass, args.guitar, args.preregistration, args.implementation_contract):
        if not path.is_file():
            raise RuntimeError(f"missing V161 timebase-QC input: {path}")

    tb = load_json(args.timebase)
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    numerics = contract.get("globalTimebase") or {}
    source_contract = contract.get("sourceAndSeparation") or {}

    checks: dict[str, bool] = {}
    details: dict[str, Any] = {}
    checks["schema"] = tb.get("schema") == TIMEBASE_SCHEMA and contract.get("canonicalSchemas", {}).get("timebaseQc") == SCHEMA
    checks["preregistrationState"] = prereg.get("version") == "V161" and prereg.get("status") == "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE"
    checks["contractState"] = contract.get("version") == "V161" and contract.get("status") == "SEALED_BEFORE_IMPLEMENTATION_CODE"
    checks["analysisGeometry"] = tb.get("analysisSampleRate") == SR and tb.get("hopLength") == HOP

    audio = tb.get("audioIdentity") or {}
    stems = tb.get("stemIdentities") or {}
    checks["sourceAudioIdentity"] = exact_identity(audio.get("source"), args.source_audio) and sha256_file(args.source_audio) == source_contract.get("sourceAudioSha256") and args.source_audio.stat().st_size == source_contract.get("sourceAudioBytes")
    checks["normalizedMixIdentity"] = exact_identity(audio.get("normalizedMix"), args.mix) and sha256_file(args.mix) == source_contract.get("normalizedWavSha256")
    checks["drumsIdentity"] = exact_identity(stems.get("drums"), args.drums)
    checks["bassIdentity"] = exact_identity(stems.get("bass"), args.bass)
    checks["guitarIdentity"] = exact_identity(stems.get("guitar"), args.guitar)

    detected = np.asarray(tb.get("detectedBeatTimesSeconds", []), dtype=float)
    grid_times = np.asarray(tb.get("gridBeatTimesSeconds", []), dtype=float)
    grid_steps = np.asarray(tb.get("gridBeatSteps", []), dtype=float)
    ordinals = np.asarray(tb.get("detectedBeatOrdinals", []), dtype=int)
    minimum_beats = int(numerics.get("minimumDetectedBeats", 8))
    checks["minimumDetectedBeats"] = len(detected) >= minimum_beats
    checks["detectedFinite"] = bool(detected.size and np.all(np.isfinite(detected)))
    checks["detectedStrictlyIncreasing"] = bool(len(detected) >= 2 and np.all(np.diff(detected) > 0.0))
    checks["gridFinite"] = bool(grid_times.size and grid_steps.size and np.all(np.isfinite(grid_times)) and np.all(np.isfinite(grid_steps)))
    checks["gridLengthMatch"] = len(grid_times) == len(grid_steps) == len(detected) + int(tb.get("leadingBeatCount", -999))
    checks["gridStrictlyIncreasing"] = bool(len(grid_times) >= 2 and np.all(np.diff(grid_times) > 0.0))
    checks["gridStepDifferenceExactlyFour"] = bool(len(grid_steps) >= 2 and np.all(np.diff(grid_steps) == 4.0))
    checks["gridStartsAtZero"] = bool(len(grid_steps) and grid_steps[0] == 0.0)
    checks["detectedOrdinalLength"] = len(ordinals) == len(detected)
    checks["detectedOrdinalDifferenceExactlyOne"] = bool(len(ordinals) >= 2 and np.all(np.diff(ordinals) == 1))

    selected_phase = tb.get("selectedPhase")
    checks["selectedPhase"] = isinstance(selected_phase, int) and selected_phase in {0, 1, 2, 3}
    leading = tb.get("leadingBeatCount")
    checks["leadingBeatCount"] = isinstance(leading, int) and checks["selectedPhase"] and leading == ((-selected_phase) % 4)
    checks["detectedOrdinalOrigin"] = bool(len(ordinals) and isinstance(leading, int) and ordinals[0] == leading)
    phase_scores = tb.get("phaseScores") or {}
    checks["fourPhaseScores"] = set(phase_scores.keys()) == {"0", "1", "2", "3"} and all(finite_scalar(v) for v in phase_scores.values())

    tempo = tb.get("trackerTempoBpm")
    duration = tb.get("audioDurationSeconds")
    checks["trackerTempoFinitePositive"] = finite_scalar(tempo) and float(tempo) > 0.0
    checks["durationFinitePositive"] = finite_scalar(duration) and float(duration) > 0.0
    if checks["detectedStrictlyIncreasing"]:
        ibis = np.diff(detected)
        mean_ibi = float(np.mean(ibis))
        median_ibi = float(np.median(ibis))
        mean_bpm = float(60.0 / mean_ibi)
        median_bpm = float(60.0 / median_ibi)
    else:
        mean_ibi = median_ibi = mean_bpm = median_bpm = float("nan")
    count_bpm = float(60.0 * len(detected) / float(duration)) if checks["durationFinitePositive"] else float("nan")
    ratio = float(median_bpm / float(tempo)) if checks["trackerTempoFinitePositive"] and math.isfinite(median_bpm) else float("nan")
    details.update({"detectedBeatCount": len(detected), "meanInterBeatIntervalSeconds": mean_ibi, "medianInterBeatIntervalSeconds": median_ibi, "meanIbiImpliedBpm": mean_bpm, "medianIbiImpliedBpm": median_bpm, "beatCountDurationBpm": count_bpm, "tempoConsistencyRatio": ratio})
    bpm_range = numerics.get("acceptedBpmRangeInclusive", [30.0, 300.0])
    ratio_range = numerics.get("tempoConsistencyRatioInclusive", [0.5, 2.0])
    lo, hi = float(bpm_range[0]), float(bpm_range[1])
    rlo, rhi = float(ratio_range[0]), float(ratio_range[1])
    checks["meanIbiBpmRange"] = math.isfinite(mean_bpm) and lo <= mean_bpm <= hi
    checks["medianIbiBpmRange"] = math.isfinite(median_bpm) and lo <= median_bpm <= hi
    checks["beatCountDurationBpmRange"] = math.isfinite(count_bpm) and lo <= count_bpm <= hi
    checks["tempoConsistencyRatio"] = math.isfinite(ratio) and rlo <= ratio <= rhi

    early = tb.get("earlyPeriodSeconds")
    checks["earlyPeriodFinitePositive"] = finite_scalar(early) and float(early) > 0.0
    if checks["detectedStrictlyIncreasing"] and checks["earlyPeriodFinitePositive"]:
        expected_early = float(np.median(np.diff(detected)[: min(8, len(detected) - 1)]))
        checks["earlyPeriodExact"] = abs(float(early) - expected_early) <= 1e-12
    else:
        checks["earlyPeriodExact"] = False
    if checks["leadingBeatCount"] and checks["gridLengthMatch"] and checks["earlyPeriodFinitePositive"] and len(detected):
        expected_prefix = [float(detected[0] - float(early) * k) for k in range(leading, 0, -1)]
        actual_prefix = grid_times[:leading].tolist()
        checks["prefixExact"] = len(expected_prefix) == len(actual_prefix) and all(abs(a - b) <= 1e-12 for a, b in zip(expected_prefix, actual_prefix))
        checks["detectedTimesUnshifted"] = bool(np.array_equal(grid_times[leading:], detected))
    else:
        checks["prefixExact"] = False
        checks["detectedTimesUnshifted"] = False

    diagnostics = tb.get("diagnostics") or {}
    warnings_rows = tb.get("warnings")
    checks["warningCountZero"] = isinstance(warnings_rows, list) and len(warnings_rows) == 0 and diagnostics.get("warningCount") == 0
    checks["fusedEnvelopeProvenance"] = diagnostics.get("fusedEnvelopeFinite") is True and diagnostics.get("fusedEnvelopeNonnegative") is True and diagnostics.get("fusedEnvelopeHasPositive") is True
    safety = tb.get("safety") or {}
    checks["referenceBlindSafety"] = safety.get("referenceRead") is False and safety.get("professionalReferencePathsOpened") == 0 and safety.get("priorGeneratedCandidateRead") is False and safety.get("priorScoreRead") is False and safety.get("priorDiagnosticReadByRuntime") is False and safety.get("V160CandidateRead") is False and safety.get("gpu") is False

    native_checks = {key: bool(value) for key, value in checks.items()}
    if not all(type(value) is bool for value in native_checks.values()):
        raise RuntimeError("V161 timebase-QC check normalization failed")
    passed = all(native_checks.values())
    receipt = {
        "schema": SCHEMA,
        "version": "V161",
        "validation": "PASS" if passed else "FAIL",
        "terminalForV161OnFailure": True,
        "timebasePath": str(args.timebase),
        "timebaseSha256": sha256_file(args.timebase),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
        "inputIdentities": {"sourceAudioSha256": sha256_file(args.source_audio), "normalizedMixSha256": sha256_file(args.mix), "drumsSha256": sha256_file(args.drums), "bassSha256": sha256_file(args.bass), "guitarSha256": sha256_file(args.guitar)},
        "checks": native_checks,
        "diagnostics": details,
        "safety": {"referenceRead": False, "professionalReferencePathsOpened": 0, "pitchInferenceInvoked": False, "priorGeneratedCandidateRead": False, "priorScoreRead": False, "priorDiagnosticReadByRuntime": False, "V160CandidateRead": False},
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"validation": receipt["validation"], "failedChecks": [k for k, ok in native_checks.items() if not ok]}, sort_keys=True))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
