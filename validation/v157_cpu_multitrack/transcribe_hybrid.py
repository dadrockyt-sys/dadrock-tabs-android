#!/usr/bin/env python3
"""Canonical V157 reference-blind CPU hybrid front-end.

V157 preserves the frozen V156/V155 musical architecture without quality tuning.
It imports only the frozen reference-blind musical engine. V154/V155/V156 generated
musical outputs and professional references are never inputs.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from validation.v155_cpu_multitrack import transcribe_hybrid as engine

ENGINE_GIT_BLOB = "3357582dd8311b28f4b85f2ebfbc7acb8c9e4fb8"
CANDIDATE_SCHEMA = "dadrock.tabs.v157.cpu-hybrid-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v157.cpu-hybrid-generation-receipt.v1"
PREREG_STATUS = "PREREGISTERED_BEFORE_GENERATION"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V157 candidate/receipt is write-once")
    for path in (args.mix, args.guitar, args.bass, args.drums, args.preregistration, args.environment_receipt):
        if not path.is_file():
            raise FileNotFoundError(path)

    prereg = json.loads(args.preregistration.read_text())
    if prereg.get("version") != "V157" or prereg.get("status") != PREREG_STATUS:
        raise RuntimeError("invalid V157 preregistration")
    contract = prereg.get("canonicalContract") or {}
    if contract.get("candidateSchema") != CANDIDATE_SCHEMA:
        raise RuntimeError("V157 candidate schema contract drift")
    if contract.get("generationReceiptSchema") != RECEIPT_SCHEMA:
        raise RuntimeError("V157 receipt schema contract drift")

    env_receipt = json.loads(args.environment_receipt.read_text())
    if env_receipt.get("validation") != "PASS":
        raise RuntimeError("environment receipt not PASS")
    if env_receipt.get("v157EngineGitBlob") != ENGINE_GIT_BLOB:
        raise RuntimeError("inherited reference-blind engine identity drift")

    grid = engine.build_timebase(args.mix, args.drums, args.bass, args.guitar)
    bass_raw, bass_meta = engine.bass_events(args.bass)
    guitar_raw, guitar_meta = engine.guitar_events(args.guitar)
    guitar, guitar_pre = engine.map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = engine.map_and_dedupe(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V157 generated an empty stream")

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0,
        "humanCorrection": False,
        "referenceGuidedFiltering": False,
        "thresholdSweep": False,
        "variantSelection": False,
        "modalUsed": False,
        "cudaGpuUsed": False,
        "mainOrProductionModified": False,
    }
    candidate = {
        "schema": CANDIDATE_SCHEMA,
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "reference-blind-single-candidate-cpu-hybrid-transcription",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebase": {
            "method": "audio-derived-piecewise-linear-beat-grid",
            "trackerTempoBpm": grid.tempo_bpm,
            "selectedDownbeatPhase": grid.selected_phase,
            "phaseScores": grid.phase_scores,
            "earliestActivitySeconds": grid.earliest_activity_seconds,
            "leadingExtensionBars": grid.extension_bars,
            "beatTimesSeconds": [float(x) for x in grid.beat_times],
            "beatGridSteps": [float(x) for x in grid.beat_steps],
            "qc": grid.qc,
        },
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "implementation": {
            "canonicalVersion": "V157",
            "inheritedReferenceBlindEngineGitBlob": ENGINE_GIT_BLOB,
        },
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "preregistrationSha256": engine.sha256_file(args.preregistration),
        "environmentReceiptSha256": engine.sha256_file(args.environment_receipt),
        "candidatePath": str(args.output),
        "candidateSha256": engine.sha256_file(args.output),
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {
            "mixSha256": engine.sha256_file(args.mix),
            "guitarStemSha256": engine.sha256_file(args.guitar),
            "bassStemSha256": engine.sha256_file(args.bass),
            "drumsStemSha256": engine.sha256_file(args.drums),
        },
        "implementation": {
            "canonicalVersion": "V157",
            "inheritedReferenceBlindEngineGitBlob": ENGINE_GIT_BLOB,
        },
        "environment": env_receipt,
        "safety": safety,
    }
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "candidateSha256": receipt["candidateSha256"],
        "counts": receipt["counts"],
        "preGridExcluded": receipt["preGridExcluded"],
        "timebaseQc": grid.qc,
        "referenceRead": False,
        "scoreCalls": 0,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
