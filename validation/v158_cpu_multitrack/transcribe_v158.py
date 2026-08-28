#!/usr/bin/env python3
"""Canonical V158 reference-blind CPU transcriber entry point.

The original V158 setup draft is preserved byte-for-byte as transcribe_v158_base.py.
This entry point reuses only its reference-blind DSP helpers, implements the separately
sealed sparse-pursuit resolution, and emits exactly one candidate + generation receipt.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

import transcribe_v158_base as base

CANDIDATE_SCHEMA = "dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v158.cpu-generation-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v158.cpu-environment-receipt.v1"
PREREG_BLOB = "728cf28646db225f3c266a4bb73a6112b1f60330"
CONTRACT_BLOB = "68f01df155cd27077cea3de5a0cd048ddcb7bd76"
RESOLUTION_BLOB = "b4b6a5c1f8a88d359a981eb1238907805f2fc2a9"
BASE_HELPER_BLOB = "5617ff1a6ea301ecaeb898b123b05d2a8c915388"
EPS = 1e-12


def helper_path() -> Path:
    return Path(__file__).resolve().with_name("transcribe_v158_base.py")


def template_bins(freqs: np.ndarray, midi: int) -> tuple[int, ...]:
    import librosa

    f0 = float(librosa.midi_to_hz(midi))
    out: set[int] = set()
    for harmonic in base.HARMONICS:
        hz = f0 * harmonic
        if hz > float(freqs[-1]):
            continue
        center = base.frequency_bin(freqs, hz)
        lo = max(0, center - 1)
        hi = min(len(freqs), center + 2)
        out.update(range(lo, hi))
    return tuple(sorted(out))


def residual_template_gain(residual: np.ndarray, freqs: np.ndarray, midi: int) -> float:
    """Sealed sparse-pursuit gain on a private three-frame residual copy."""
    import librosa

    f0 = float(librosa.midi_to_hz(midi))
    fundamental = base.frequency_bin(freqs, f0)
    flo = max(0, fundamental - 1)
    fhi = min(residual.shape[0], fundamental + 2)
    fund_mean = float(np.mean(residual[flo:fhi, :]))
    score = 0.75 * fund_mean
    for harmonic, weight in zip(base.HARMONICS, base.HWEIGHTS):
        hz = f0 * harmonic
        if hz > float(freqs[-1]):
            continue
        center = base.frequency_bin(freqs, hz)
        lo = max(0, center - 1)
        hi = min(residual.shape[0], center + 2)
        score += float(weight) * float(np.mean(residual[lo:hi, :]))
    return float(score)


def sparse_pursuit_select(
    cqt: np.ndarray,
    freqs: np.ndarray,
    frame: int,
    persistent: set[int],
) -> list[tuple[int, float, bool]]:
    """Apply the sealed non-overlapping residual sparse-pursuit selection."""
    frame_ids = [frame - 1, frame, frame + 1]
    residual = np.asarray(cqt[:, frame_ids], dtype=float).copy()
    remaining = set(int(m) for m in persistent)
    occupied: set[int] = set()
    selected: list[tuple[int, float, bool]] = []

    full_scores, full_fundamentals = base.three_frame_template(
        cqt, freqs, frame, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1]
    )
    median_fundamental = float(np.median(full_fundamentals))

    while remaining and len(selected) < 6:
        best_midi: int | None = None
        best_gain = -math.inf
        best_bins: tuple[int, ...] = ()
        for midi in sorted(remaining):
            bins = template_bins(freqs, midi)
            if any(b in occupied for b in bins):
                continue
            gain = residual_template_gain(residual, freqs, midi)
            if (
                best_midi is None
                or gain > best_gain + EPS
                or (abs(gain - best_gain) <= EPS and midi < best_midi)
            ):
                best_midi = midi
                best_gain = gain
                best_bins = bins
        if best_midi is None or best_gain <= 0.0:
            break

        offset = best_midi - base.GUITAR_RANGE[0]
        fund_present = bool(full_fundamentals[offset] > median_fundamental)
        selected.append((best_midi, float(best_gain), fund_present))
        occupied.update(best_bins)
        if best_bins:
            residual[np.asarray(best_bins, dtype=int), :] = 0.0
        remaining.remove(best_midi)

    return selected


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    y, _ = base.load_mono(path)
    cqt, freqs = base.harmonic_cqt(y, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1])
    _, _, notes = predict(
        path,
        model_or_model_path=Path(ICASSP_2022_MODEL_PATH),
        onset_threshold=0.50,
        frame_threshold=0.30,
        minimum_note_length=90.0,
        minimum_frequency=librosa.midi_to_hz(base.GUITAR_RANGE[0]),
        maximum_frequency=librosa.midi_to_hz(base.GUITAR_RANGE[1]),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )

    rows: list[dict[str, Any]] = []
    raw_bp = 0
    repairs = 0
    for note in notes:
        if len(note) < 4:
            continue
        start = float(note[0])
        end = float(note[1])
        raw_midi = int(round(float(note[2])))
        amp = float(note[3])
        if not base.GUITAR_RANGE[0] <= raw_midi <= base.GUITAR_RANGE[1]:
            continue
        raw_bp += 1
        frame = int(np.clip(round(start * base.SR / base.HOP), 0, cqt.shape[1] - 1))
        scores, fundamentals = base.three_frame_template(
            cqt, freqs, frame, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1]
        )
        med_fund = float(np.median(fundamentals))
        register_candidates = [raw_midi] + [
            m
            for m in (raw_midi - 12, raw_midi + 12)
            if base.GUITAR_RANGE[0] <= m <= base.GUITAR_RANGE[1]
        ]
        chosen = raw_midi
        chosen_score = float(scores[raw_midi - base.GUITAR_RANGE[0]])
        for midi in sorted(register_candidates):
            offset = midi - base.GUITAR_RANGE[0]
            score = float(scores[offset])
            fund_present = bool(fundamentals[offset] > med_fund)
            if midi != raw_midi and fund_present and score > chosen_score + EPS:
                chosen = midi
                chosen_score = score
        if chosen != raw_midi:
            repairs += 1
        rows.append(
            {
                "midi": int(chosen),
                "startSeconds": start,
                "endSeconds": end,
                "durationSeconds": max(0.0, end - start),
                "confidence": amp,
                "source": "basic_pitch",
                "basicPitchOriginalMidi": int(raw_midi),
                "registerRepaired": bool(chosen != raw_midi),
                "templateScore": chosen_score,
            }
        )

    env = base.onset_env(y)
    onset_frames = np.asarray(
        librosa.onset.onset_detect(
            onset_envelope=env,
            sr=base.SR,
            hop_length=base.HOP,
            backtrack=False,
            units="frames",
        ),
        dtype=int,
    )
    selected_count = 0
    added_count = 0
    for onset_index, raw_frame in enumerate(onset_frames):
        frame = int(np.clip(raw_frame, 1, cqt.shape[1] - 2))
        frame_sets: list[set[int]] = []
        for f in (frame - 1, frame, frame + 1):
            ranked = base.top_template_midi_per_frame(
                cqt, freqs, f, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1], 6
            )
            frame_sets.append({m for m, _, _ in ranked})
        persistent = set.intersection(*frame_sets) if frame_sets else set()
        selected = sparse_pursuit_select(cqt, freqs, frame, persistent)
        selected_count += len(selected)
        t = float(librosa.frames_to_time(frame, sr=base.SR, hop_length=base.HOP))
        for midi, gain, fund_present in selected:
            if any(
                int(row["midi"]) == midi
                and abs(float(row["startSeconds"]) - t) <= 0.060
                for row in rows
            ):
                continue
            rows.append(
                {
                    "midi": int(midi),
                    "startSeconds": t,
                    "endSeconds": t + 0.07,
                    "durationSeconds": 0.07,
                    "confidence": float(gain),
                    "source": "harmonic_track",
                    "onsetProposalIndex": onset_index,
                    "onsetFrame": frame,
                    "persistentTrackFrames": 3,
                    "sparsePursuitGain": float(gain),
                    "fundamentalPresent": bool(fund_present),
                }
            )
            added_count += 1

    return rows, {
        "inputSha256": base.sha256_file(path),
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": base.sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": raw_bp,
        "registerRepairCount": repairs,
        "independentOnsetCount": int(len(onset_frames)),
        "sparsePursuitSelectedCount": selected_count,
        "harmonicTrackAddedCount": added_count,
        "eventCountBeforeGridDedupe": len(rows),
        "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
    }


def validate_sealed_setup(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    if base.git_blob_sha(helper_path()) != BASE_HELPER_BLOB:
        raise RuntimeError("V158 base helper identity drift")
    if base.git_blob_sha(args.preregistration) != PREREG_BLOB:
        raise RuntimeError("V158 preregistration Git blob drift")
    if base.git_blob_sha(args.implementation_contract) != CONTRACT_BLOB:
        raise RuntimeError("V158 implementation-contract Git blob drift")
    if base.git_blob_sha(args.sparse_pursuit_resolution) != RESOLUTION_BLOB:
        raise RuntimeError("V158 sparse-pursuit resolution Git blob drift")

    prereg = json.loads(args.preregistration.read_text())
    contract = json.loads(args.implementation_contract.read_text())
    resolution = json.loads(args.sparse_pursuit_resolution.read_text())
    env = json.loads(args.environment_receipt.read_text())

    if prereg.get("status") != "PREREGISTERED_BEFORE_GENERATION":
        raise RuntimeError("V158 preregistration status invalid")
    if contract.get("status") != "SEALED_BEFORE_GENERATION_CODE":
        raise RuntimeError("V158 implementation-contract status invalid")
    if resolution.get("status") != "SEALED_BEFORE_CANONICAL_EXECUTION_CODE":
        raise RuntimeError("V158 sparse-pursuit resolution status invalid")
    sealed = resolution.get("sealedInputs") or {}
    if sealed.get("preregistrationGitBlob") != PREREG_BLOB or sealed.get("implementationContractGitBlob") != CONTRACT_BLOB:
        raise RuntimeError("V158 sparse-pursuit sealed-input identity drift")
    boundary = resolution.get("boundaryAtSeal") or {}
    if boundary.get("candidateExists") is not False or boundary.get("generationWorkflowExists") is not False:
        raise RuntimeError("V158 sparse-pursuit resolution was not sealed pre-generation")
    if boundary.get("professionalReferenceRead") is not False or boundary.get("professionalReferencePathsOpened") != 0 or boundary.get("referenceFacingScoreCalls") != 0:
        raise RuntimeError("V158 sparse-pursuit resolution reference boundary invalid")
    if resolution.get("sparsePursuitNumerics", {}).get("newTunedThresholds") != []:
        raise RuntimeError("V158 sparse-pursuit resolution introduced tuned thresholds")

    if env.get("schema") != ENV_SCHEMA or env.get("validation") != "PASS" or env.get("device") != "cpu":
        raise RuntimeError("V158 environment receipt invalid")
    if env.get("cudaAvailable") is not False or env.get("torchCudaVersion") is not None:
        raise RuntimeError("V158 environment is not confirmed CPU-only")
    return prereg, contract, resolution, env


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", type=Path, required=True)
    ap.add_argument("--guitar", type=Path, required=True)
    ap.add_argument("--bass", type=Path, required=True)
    ap.add_argument("--drums", type=Path, required=True)
    ap.add_argument("--preregistration", type=Path, required=True)
    ap.add_argument("--implementation-contract", type=Path, required=True)
    ap.add_argument("--sparse-pursuit-resolution", type=Path, required=True)
    ap.add_argument("--environment-receipt", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, required=True)
    args = ap.parse_args()

    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V158 candidate/receipt is write-once")
    _, _, _, env = validate_sealed_setup(args)

    grid = base.build_timebase(args.mix, args.drums, args.bass, args.guitar)
    bass_raw, bass_meta = base.bass_events(args.bass)
    guitar_raw, guitar_meta = guitar_events(args.guitar)
    guitar, guitar_pre = base.map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = base.map_and_dedupe(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V158 generated empty stream")

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreOrDiagnosticRead": False,
        "referenceGuidedFiltering": False,
        "thresholdSweep": False,
        "variantSelection": False,
        "humanCorrection": False,
        "cudaGpuUsed": False,
        "modalUsed": False,
        "mainOrProductionModified": False,
    }
    candidate = {
        "schema": CANDIDATE_SCHEMA,
        "song": {"artist": "Lenny Kravitz", "title": "Are You Gonna Go My Way"},
        "classification": "single-preregistered-reference-blind-v158-cpu-candidate",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebase": {
            "method": "dynamic-beat-grid-four-state-viterbi-bar-position",
            "trackerTempoBpm": grid.tempo_bpm,
            "beatTimesSeconds": [float(x) for x in grid.beat_times],
            "beatGridSteps": [float(x) for x in grid.beat_steps],
            "viterbiBarStates": [int(x) for x in grid.states],
            "earliestActivitySeconds": grid.earliest_activity,
            "leadingExtensionBars": grid.leading_bars,
            "featureSummary": grid.feature_summary,
            "qc": {
                "beatCount": len(grid.beat_times),
                "strictlyIncreasingBeatTimes": True,
                "statePathLength": len(grid.states),
            },
        },
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "sealedInputs": {
            "preregistrationGitBlob": PREREG_BLOB,
            "implementationContractGitBlob": CONTRACT_BLOB,
            "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
            "baseHelperGitBlob": BASE_HELPER_BLOB,
        },
        "safety": safety,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "candidatePath": str(args.output),
        "candidateSha256": base.sha256_file(args.output),
        "preregistrationSha256": base.sha256_file(args.preregistration),
        "implementationContractSha256": base.sha256_file(args.implementation_contract),
        "sparsePursuitResolutionSha256": base.sha256_file(args.sparse_pursuit_resolution),
        "environmentReceiptSha256": base.sha256_file(args.environment_receipt),
        "implementation": {
            "canonicalEntryPointGitBlob": "PIN_AT_PRE_RUN",
            "baseHelperGitBlob": BASE_HELPER_BLOB,
            "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
        },
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {
            "mixSha256": base.sha256_file(args.mix),
            "guitarStemSha256": base.sha256_file(args.guitar),
            "bassStemSha256": base.sha256_file(args.bass),
            "drumsStemSha256": base.sha256_file(args.drums),
        },
        "environment": env,
        "safety": safety,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "candidateSha256": receipt["candidateSha256"],
                "counts": receipt["counts"],
                "referenceRead": False,
                "scoreCalls": 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
