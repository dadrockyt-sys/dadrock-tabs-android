#!/usr/bin/env python3
"""Canonical V158 reference-blind CPU transcriber entry point.

The original setup implementation is preserved byte-for-byte as
``transcribe_v158_base.py``. This entry point adds the separately sealed Guitar
sparse-pursuit resolution and cryptographically binds execution to the V158
pre-run receipt. It has no professional-reference, scorer, prior-candidate, or
prior-diagnostic input.
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
PRE_RUN_SCHEMA = "dadrock.tabs.v158.pre-run-identity-receipt.v1"
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
    bins: set[int] = set()
    for harmonic in base.HARMONICS:
        hz = f0 * harmonic
        if hz > float(freqs[-1]):
            continue
        center = base.frequency_bin(freqs, hz)
        bins.update(range(max(0, center - 1), min(len(freqs), center + 2)))
    return tuple(sorted(bins))


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
    remaining = set(int(midi) for midi in persistent)
    occupied: set[int] = set()
    selected: list[tuple[int, float, bool]] = []

    _, fundamentals = base.three_frame_template(
        cqt, freqs, frame, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1]
    )
    median_fundamental = float(np.median(fundamentals))

    while remaining and len(selected) < 6:
        best_midi: int | None = None
        best_gain = -math.inf
        best_bins: tuple[int, ...] = ()
        for midi in sorted(remaining):
            bins = template_bins(freqs, midi)
            if any(bin_index in occupied for bin_index in bins):
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
        fundamental_present = bool(fundamentals[offset] > median_fundamental)
        selected.append((best_midi, float(best_gain), fundamental_present))
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
    raw_basic_pitch_count = 0
    register_repair_count = 0
    for note in notes:
        if len(note) < 4:
            continue
        start = float(note[0])
        end = float(note[1])
        raw_midi = int(round(float(note[2])))
        amplitude = float(note[3])
        if not base.GUITAR_RANGE[0] <= raw_midi <= base.GUITAR_RANGE[1]:
            continue
        raw_basic_pitch_count += 1
        frame = int(np.clip(round(start * base.SR / base.HOP), 0, cqt.shape[1] - 1))
        scores, fundamentals = base.three_frame_template(
            cqt, freqs, frame, base.GUITAR_RANGE[0], base.GUITAR_RANGE[1]
        )
        median_fundamental = float(np.median(fundamentals))
        register_candidates = [raw_midi] + [
            midi
            for midi in (raw_midi - 12, raw_midi + 12)
            if base.GUITAR_RANGE[0] <= midi <= base.GUITAR_RANGE[1]
        ]
        chosen_midi = raw_midi
        chosen_score = float(scores[raw_midi - base.GUITAR_RANGE[0]])
        for midi in sorted(register_candidates):
            offset = midi - base.GUITAR_RANGE[0]
            score = float(scores[offset])
            fundamental_present = bool(fundamentals[offset] > median_fundamental)
            if midi != raw_midi and fundamental_present and score > chosen_score + EPS:
                chosen_midi = midi
                chosen_score = score
        if chosen_midi != raw_midi:
            register_repair_count += 1
        rows.append(
            {
                "midi": int(chosen_midi),
                "startSeconds": start,
                "endSeconds": end,
                "durationSeconds": max(0.0, end - start),
                "confidence": amplitude,
                "source": "basic_pitch",
                "basicPitchOriginalMidi": int(raw_midi),
                "registerRepaired": bool(chosen_midi != raw_midi),
                "templateScore": chosen_score,
            }
        )

    onset_envelope = base.onset_env(y)
    onset_frames = np.asarray(
        librosa.onset.onset_detect(
            onset_envelope=onset_envelope,
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
        for analysis_frame in (frame - 1, frame, frame + 1):
            ranked = base.top_template_midi_per_frame(
                cqt,
                freqs,
                analysis_frame,
                base.GUITAR_RANGE[0],
                base.GUITAR_RANGE[1],
                6,
            )
            frame_sets.append({midi for midi, _, _ in ranked})
        persistent = set.intersection(*frame_sets) if frame_sets else set()
        selected = sparse_pursuit_select(cqt, freqs, frame, persistent)
        selected_count += len(selected)
        onset_seconds = float(librosa.frames_to_time(frame, sr=base.SR, hop_length=base.HOP))
        for midi, gain, fundamental_present in selected:
            if any(
                int(row["midi"]) == midi
                and abs(float(row["startSeconds"]) - onset_seconds) <= 0.060
                for row in rows
            ):
                continue
            rows.append(
                {
                    "midi": int(midi),
                    "startSeconds": onset_seconds,
                    "endSeconds": onset_seconds + 0.07,
                    "durationSeconds": 0.07,
                    "confidence": float(gain),
                    "source": "harmonic_track",
                    "onsetProposalIndex": onset_index,
                    "onsetFrame": frame,
                    "persistentTrackFrames": 3,
                    "sparsePursuitGain": float(gain),
                    "fundamentalPresent": bool(fundamental_present),
                }
            )
            added_count += 1

    return rows, {
        "inputSha256": base.sha256_file(path),
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": base.sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": raw_basic_pitch_count,
        "registerRepairCount": register_repair_count,
        "independentOnsetCount": int(len(onset_frames)),
        "sparsePursuitSelectedCount": selected_count,
        "harmonicTrackAddedCount": added_count,
        "eventCountBeforeGridDedupe": len(rows),
        "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
    }


def validate_sealed_setup(
    args: argparse.Namespace,
) -> tuple[dict[str, Any], dict[str, Any]]:
    entrypoint_blob = base.git_blob_sha(Path(__file__))
    structural_qc_blob = base.git_blob_sha(args.structural_qc)
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
    pre_run = json.loads(args.pre_run_receipt.read_text())
    environment = json.loads(args.environment_receipt.read_text())

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

    if pre_run.get("schema") != PRE_RUN_SCHEMA or pre_run.get("version") != "V158":
        raise RuntimeError("V158 pre-run receipt schema/version invalid")
    if pre_run.get("validation") != "PASS" or pre_run.get("status") != "SEALED_BEFORE_GENERATION":
        raise RuntimeError("V158 pre-run receipt state invalid")
    pins = pre_run.get("pinnedGitBlobs") or {}
    expected_pins = {
        "preregistration": PREREG_BLOB,
        "implementationContract": CONTRACT_BLOB,
        "sparsePursuitResolution": RESOLUTION_BLOB,
        "transcriber": entrypoint_blob,
        "baseHelper": BASE_HELPER_BLOB,
        "structuralQc": structural_qc_blob,
    }
    for key, expected in expected_pins.items():
        if pins.get(key) != expected:
            raise RuntimeError(f"V158 pre-run pin drift: {key}")
    if pre_run.get("candidateExistsAtSeal") is not False:
        raise RuntimeError("V158 candidate existed at pre-run seal")
    if pre_run.get("generationReceiptAbsentAtSeal") is not True or pre_run.get("environmentReceiptAbsentAtSeal") is not True or pre_run.get("generationWorkflowAbsentAtSeal") is not True:
        raise RuntimeError("V158 pre-run absence boundary invalid")
    if pre_run.get("referenceReadAtSeal") is not False or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0 or pre_run.get("referenceFacingScoreCallsAtSeal") != 0:
        raise RuntimeError("V158 pre-run reference boundary invalid")
    trigger = pre_run.get("triggerSafety") or {}
    if trigger.get("generationWorkflowCreationIsSingleTrigger") is not True or trigger.get("secondArmEditForbidden") is not True:
        raise RuntimeError("V158 pre-run trigger-safety contract invalid")
    if trigger.get("expectedGenerationWorkflowRunCount") != 1 or trigger.get("workflowMustSelfSealAfterSuccessfulFreeze") is not True:
        raise RuntimeError("V158 pre-run workflow-count/freeze contract invalid")
    if trigger.get("duplicateRunAction") != "ABORT_V158_WITHOUT_SCORING":
        raise RuntimeError("V158 duplicate-run policy invalid")

    if environment.get("schema") != ENV_SCHEMA or environment.get("validation") != "PASS" or environment.get("device") != "cpu":
        raise RuntimeError("V158 environment receipt invalid")
    if environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        raise RuntimeError("V158 environment is not confirmed CPU-only")

    return environment, {
        "entrypointGitBlob": entrypoint_blob,
        "structuralQcGitBlob": structural_qc_blob,
        "preRunReceiptSha256": base.sha256_file(args.pre_run_receipt),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--sparse-pursuit-resolution", type=Path, required=True)
    parser.add_argument("--pre-run-receipt", type=Path, required=True)
    parser.add_argument("--structural-qc", type=Path, required=True)
    parser.add_argument("--environment-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V158 candidate/receipt is write-once")
    for path in (
        args.mix,
        args.guitar,
        args.bass,
        args.drums,
        args.preregistration,
        args.implementation_contract,
        args.sparse_pursuit_resolution,
        args.pre_run_receipt,
        args.structural_qc,
        args.environment_receipt,
    ):
        if not path.is_file():
            raise RuntimeError(f"V158 missing required input: {path}")

    environment, identities = validate_sealed_setup(args)

    grid = base.build_timebase(args.mix, args.drums, args.bass, args.guitar)
    bass_raw, bass_metadata = base.bass_events(args.bass)
    guitar_raw, guitar_metadata = guitar_events(args.guitar)
    guitar, guitar_pre_grid = base.map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre_grid = base.map_and_dedupe(bass_raw, grid, "bass")
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
            "beatTimesSeconds": [float(value) for value in grid.beat_times],
            "beatGridSteps": [float(value) for value in grid.beat_steps],
            "viterbiBarStates": [int(value) for value in grid.states],
            "earliestActivitySeconds": grid.earliest_activity,
            "leadingExtensionBars": grid.leading_bars,
            "featureSummary": grid.feature_summary,
            "qc": {
                "beatCount": len(grid.beat_times),
                "strictlyIncreasingBeatTimes": True,
                "statePathLength": len(grid.states),
            },
        },
        "streamMetadata": {"combinedGuitar": guitar_metadata, "bass": bass_metadata},
        "sealedInputs": {
            "preregistrationGitBlob": PREREG_BLOB,
            "implementationContractGitBlob": CONTRACT_BLOB,
            "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
            "canonicalEntryPointGitBlob": identities["entrypointGitBlob"],
            "baseHelperGitBlob": BASE_HELPER_BLOB,
            "structuralQcGitBlob": identities["structuralQcGitBlob"],
            "preRunReceiptSha256": identities["preRunReceiptSha256"],
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
        "preRunReceiptSha256": identities["preRunReceiptSha256"],
        "environmentReceiptSha256": base.sha256_file(args.environment_receipt),
        "implementation": {
            "canonicalEntryPointGitBlob": identities["entrypointGitBlob"],
            "baseHelperGitBlob": BASE_HELPER_BLOB,
            "structuralQcGitBlob": identities["structuralQcGitBlob"],
            "sparsePursuitResolutionGitBlob": RESOLUTION_BLOB,
        },
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre_grid, "bass": bass_pre_grid},
        "inputIdentities": {
            "mixSha256": base.sha256_file(args.mix),
            "guitarStemSha256": base.sha256_file(args.guitar),
            "bassStemSha256": base.sha256_file(args.bass),
            "drumsStemSha256": base.sha256_file(args.drums),
        },
        "environment": environment,
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
