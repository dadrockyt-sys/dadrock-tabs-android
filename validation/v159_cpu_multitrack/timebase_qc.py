#!/usr/bin/env python3
"""Independent reference-blind QC for the sealed V159 timebase artifact."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

PREREG_BLOB = "2eca55dc344908a791ba7946f42d77fbd7b8926d"
CONTRACT_BLOB = "83dfee2d537d00dbced367bdbc467d167a96db2f"
BUILDER_BLOB = "cac78de6c6561a4bf5208e644f19878bf8e75193"
NORMALIZED_WAV_SHA256 = "3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e"
TIMEBASE_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase.v1"
QC_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase-qc.v1"
EPS = 1e-9


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(f"V159 timebase QC failure: {message}")


def finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def close(actual: float, expected: float, label: str, tolerance: float = EPS) -> None:
    if abs(float(actual) - float(expected)) > tolerance:
        fail(f"{label}: {actual!r} != {expected!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timebase", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--implementation-contract", type=Path, required=True)
    ap.add_argument("--builder", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists():
        fail("QC output is write-once")
    for path in (args.timebase, args.preregistration, args.implementation_contract, args.builder):
        if not path.is_file():
            fail(f"missing input {path}")
    if git_blob_sha(args.preregistration) != PREREG_BLOB:
        fail("preregistration Git blob drift")
    if git_blob_sha(args.implementation_contract) != CONTRACT_BLOB:
        fail("implementation-contract Git blob drift")
    if git_blob_sha(args.builder) != BUILDER_BLOB:
        fail("timebase-builder Git blob drift")

    prereg = json.loads(args.preregistration.read_text(encoding="utf-8"))
    contract = json.loads(args.implementation_contract.read_text(encoding="utf-8"))
    tb = json.loads(args.timebase.read_text(encoding="utf-8"))
    if prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        fail("preregistration state")
    if contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        fail("implementation-contract state")
    if tb.get("schema") != TIMEBASE_SCHEMA:
        fail("timebase schema")
    song = tb.get("song") or {}
    if str(song.get("artist", "")).lower() != "lenny kravitz" or str(song.get("title", "")).lower() != "are you gonna go my way":
        fail("song identity")
    if (tb.get("audioIdentity") or {}).get("normalizedMixSha256") != NORMALIZED_WAV_SHA256:
        fail("normalized mix identity")

    sealed = tb.get("sealedInputs") or {}
    if sealed.get("preregistrationGitBlob") != PREREG_BLOB or sealed.get("implementationContractGitBlob") != CONTRACT_BLOB:
        fail("timebase sealed-input drift")

    safety = tb.get("safety") or {}
    for key in (
        "referenceRead",
        "priorGeneratedCandidateRead",
        "priorScoreRead",
        "priorDiagnosticReadByRuntime",
        "referenceDerivedTimingConstantsUsed",
        "gpu",
        "modal",
        "mainOrProductionModified",
    ):
        if safety.get(key) is not False:
            fail(f"safety {key}")
    if safety.get("professionalReferencePathsOpened") != 0 or safety.get("referenceFacingScoreCalls") != 0:
        fail("reference boundary")

    duration = tb.get("audioDurationSeconds")
    tempo = tb.get("trackerTempoBpm")
    if not finite(duration) or float(duration) <= 0.0:
        fail("audio duration")
    if not finite(tempo) or float(tempo) <= 0.0:
        fail("tracker tempo")

    detected = tb.get("detectedBeatTimesSeconds")
    grid_times = tb.get("gridBeatTimesSeconds")
    grid_steps = tb.get("gridBeatSteps")
    if not isinstance(detected, list) or len(detected) < 8:
        fail("minimum detected beats")
    if not isinstance(grid_times, list) or not isinstance(grid_steps, list) or len(grid_times) != len(grid_steps):
        fail("grid arrays")
    if any(not finite(value) for value in detected + grid_times + grid_steps):
        fail("nonfinite beat/grid value")
    detected_f = [float(value) for value in detected]
    grid_f = [float(value) for value in grid_times]
    steps_f = [float(value) for value in grid_steps]
    if any(b <= a for a, b in zip(detected_f, detected_f[1:])):
        fail("detected beats not strictly increasing")
    if any(b <= a for a, b in zip(grid_f, grid_f[1:])):
        fail("grid beats not strictly increasing")
    for index, value in enumerate(steps_f):
        close(value, 4.0 * index, f"grid step {index}")
    if any(abs((b - a) - 4.0) > EPS for a, b in zip(steps_f, steps_f[1:])):
        fail("grid step difference is not exactly four")

    phase = tb.get("selectedPhase")
    leading = tb.get("leadingBeatCount")
    if not isinstance(phase, int) or phase not in {0, 1, 2, 3}:
        fail("selected phase")
    if leading != (-phase) % 4:
        fail("leading beat count/phase relation")
    if len(grid_f) != len(detected_f) + int(leading):
        fail("grid/detected length relation")
    for actual, expected in zip(grid_f[int(leading):], detected_f):
        close(actual, expected, "detected grid suffix")

    early = tb.get("earlyPeriodSeconds")
    if not finite(early) or float(early) <= 0.0:
        fail("early period")
    if leading:
        for i in range(int(leading)):
            expected = detected_f[0] - float(leading - i) * float(early)
            close(grid_f[i], expected, f"prefix beat {i}")

    phase_scores = tb.get("phaseScores")
    if not isinstance(phase_scores, dict) or set(phase_scores) != {"0", "1", "2", "3"}:
        fail("phase-score set")
    scores = {int(key): float(value) for key, value in phase_scores.items() if finite(value)}
    if len(scores) != 4:
        fail("nonfinite phase score")
    deterministic_phase = 0
    best = scores[0]
    for candidate in range(1, 4):
        if scores[candidate] > best + 1e-12:
            deterministic_phase = candidate
            best = scores[candidate]
    if phase != deterministic_phase:
        fail("phase tie-break/selection drift")

    ibis = [b - a for a, b in zip(detected_f, detected_f[1:])]
    if not ibis or any(not math.isfinite(value) or value <= 0.0 for value in ibis):
        fail("inter-beat intervals")
    mean_ibi = sum(ibis) / len(ibis)
    sorted_ibis = sorted(ibis)
    mid = len(sorted_ibis) // 2
    median_ibi = sorted_ibis[mid] if len(sorted_ibis) % 2 else 0.5 * (sorted_ibis[mid - 1] + sorted_ibis[mid])
    mean_bpm = 60.0 / mean_ibi
    median_bpm = 60.0 / median_ibi
    count_duration_bpm = 60.0 * len(detected_f) / float(duration)
    ratio = median_bpm / float(tempo)

    for label, bpm in (
        ("meanIbiImpliedBpm", mean_bpm),
        ("medianIbiImpliedBpm", median_bpm),
        ("beatCountDurationBpm", count_duration_bpm),
    ):
        if not 30.0 <= bpm <= 300.0:
            fail(f"{label} outside generic 30..300 BPM: {bpm}")
    if not 0.5 <= ratio <= 2.0:
        fail(f"tempo consistency ratio outside 0.5..2.0: {ratio}")

    diagnostics = tb.get("diagnostics") or {}
    expected_diag = {
        "detectedBeatCount": len(detected_f),
        "gridBeatCount": len(grid_f),
    }
    for key, expected in expected_diag.items():
        if diagnostics.get(key) != expected:
            fail(f"diagnostic {key}")
    for key, expected in (
        ("meanInterBeatIntervalSeconds", mean_ibi),
        ("medianInterBeatIntervalSeconds", median_ibi),
        ("meanIbiImpliedBpm", mean_bpm),
        ("medianIbiImpliedBpm", median_bpm),
        ("beatCountDurationBpm", count_duration_bpm),
        ("tempoConsistencyRatio", ratio),
    ):
        if not finite(diagnostics.get(key)):
            fail(f"missing/nonfinite diagnostic {key}")
        close(float(diagnostics[key]), expected, f"diagnostic {key}")
    if not finite(diagnostics.get("fusedEnvelopeMinimum")) or float(diagnostics["fusedEnvelopeMinimum"]) < 0.0:
        fail("fused envelope minimum")
    if not finite(diagnostics.get("fusedEnvelopeMaximum")) or float(diagnostics["fusedEnvelopeMaximum"]) <= 0.0:
        fail("fused envelope maximum")
    warnings_rows = tb.get("warnings")
    if not isinstance(warnings_rows, list) or warnings_rows:
        fail("warning count must be zero")
    if diagnostics.get("warningCount") != 0:
        fail("diagnostic warning count")

    report = {
        "schema": QC_SCHEMA,
        "version": "V159",
        "status": "PASS",
        "timebasePath": str(args.timebase),
        "timebaseSha256": sha256(args.timebase),
        "timebaseGitBlob": git_blob_sha(args.timebase),
        "pinnedCode": {
            "builderGitBlob": BUILDER_BLOB,
            "preregistrationGitBlob": PREREG_BLOB,
            "implementationContractGitBlob": CONTRACT_BLOB,
        },
        "metrics": {
            "audioDurationSeconds": float(duration),
            "detectedBeatCount": len(detected_f),
            "gridBeatCount": len(grid_f),
            "trackerTempoBpm": float(tempo),
            "meanInterBeatIntervalSeconds": mean_ibi,
            "medianInterBeatIntervalSeconds": median_ibi,
            "meanIbiImpliedBpm": mean_bpm,
            "medianIbiImpliedBpm": median_bpm,
            "beatCountDurationBpm": count_duration_bpm,
            "tempoConsistencyRatio": ratio,
            "selectedPhase": phase,
            "leadingBeatCount": leading,
            "earlyPeriodSeconds": float(early),
            "firstGridBeatSeconds": grid_f[0],
            "lastGridBeatSeconds": grid_f[-1],
            "maximumGridStep": steps_f[-1],
            "warningCount": 0,
        },
        "checks": {
            "finiteNonnegativeBeatEnvelopeProvenance": True,
            "runtimeWarningsZero": True,
            "genericBpmBoundsPass": True,
            "tempoConsistencyPass": True,
            "strictBeatOrderPass": True,
            "absoluteOrdinalIncrementExactlyOne": True,
            "barPhaseDoesNotAlterOrdinal": True,
            "referenceBlind": True,
        },
        "safety": {
            "referenceRead": False,
            "professionalReferencePathsOpened": 0,
            "referenceFacingScoreCalls": 0,
            "priorGeneratedCandidateRead": False,
            "priorScoreRead": False,
            "priorDiagnosticReadByRuntime": False,
            "gpu": False,
            "mainOrProductionModified": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
