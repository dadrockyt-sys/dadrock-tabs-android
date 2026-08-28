#!/usr/bin/env python3
"""Sealed V159 CPU transcriber consuming a frozen PASS V159 timebase.

Pitch-recognition numerics are mechanically preserved from the sealed V158
numeric contract.  This module does not build a beat/bar timebase and cannot run
unless the independent V159 timebase-QC receipt is already frozen PASS.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

SR = 22050
HOP = 256
BPO = 36
HARMONICS = (1, 2, 3, 4, 5)
HWEIGHTS = (1.0, 0.5, 0.3333333333, 0.25, 0.2)
BASS_RANGE = (28, 67)
GUITAR_RANGE = (40, 88)
EPS = 1e-12

CANDIDATE_SCHEMA = "dadrock.tabs.v159.cpu-timebase-first-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v159.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v159.reference-blind-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v159.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v159.cpu-environment-receipt.v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise RuntimeError(f"expected JSON object: {path}")
    return value


def load_mono(path: Path) -> np.ndarray:
    import librosa

    y, sr = librosa.load(str(path), sr=SR, mono=True)
    y = np.asarray(y, dtype=np.float32)
    if sr != SR or y.size == 0 or not np.all(np.isfinite(y)):
        raise RuntimeError(f"invalid audio load: {path}")
    return y


def onset_env(y: np.ndarray) -> np.ndarray:
    import librosa

    return np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)


def z_across_candidates(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    std = float(np.std(x))
    if not math.isfinite(std) or std < 1e-9:
        return np.zeros_like(x)
    return (x - float(np.mean(x))) / std


def harmonic_cqt(y: np.ndarray, midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
    import librosa

    harmonic, _ = librosa.effects.hpss(y)
    top = midi_max + 30
    fmin = librosa.midi_to_hz(midi_min - 1)
    n_bins = int(math.ceil((top - (midi_min - 1)) * BPO / 12.0)) + 1
    cqt = np.log1p(np.abs(librosa.cqt(
        harmonic,
        sr=SR,
        hop_length=HOP,
        fmin=fmin,
        n_bins=n_bins,
        bins_per_octave=BPO,
    )))
    freqs = librosa.cqt_frequencies(n_bins, fmin=fmin, bins_per_octave=BPO)
    if not np.all(np.isfinite(cqt)) or not np.all(np.isfinite(freqs)):
        raise RuntimeError("nonfinite harmonic CQT")
    return cqt, freqs


def frequency_bin(freqs: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(freqs - hz)))


def template_scores(
    cqt: np.ndarray,
    freqs: np.ndarray,
    frames: list[int],
    midi_min: int,
    midi_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    import librosa

    safe_frames = [int(np.clip(frame, 0, cqt.shape[1] - 1)) for frame in frames]
    scores: list[float] = []
    fundamentals: list[float] = []
    for midi in range(midi_min, midi_max + 1):
        f0 = float(librosa.midi_to_hz(midi))
        fundamental = frequency_bin(freqs, f0)
        lo = max(0, fundamental - 1)
        hi = min(cqt.shape[0], fundamental + 2)
        fund_mean = float(np.mean(cqt[lo:hi, safe_frames]))
        score = 0.75 * fund_mean
        for harmonic, weight in zip(HARMONICS, HWEIGHTS):
            hz = f0 * harmonic
            if hz > freqs[-1]:
                continue
            center = frequency_bin(freqs, hz)
            hlo = max(0, center - 1)
            hhi = min(cqt.shape[0], center + 2)
            score += float(weight) * float(np.mean(cqt[hlo:hhi, safe_frames]))
        scores.append(score)
        fundamentals.append(fund_mean)
    return np.asarray(scores, dtype=float), np.asarray(fundamentals, dtype=float)


def collapse_onsets(frames: np.ndarray, min_ms: float) -> list[int]:
    min_frames = max(1, int(math.ceil((min_ms / 1000.0) * SR / HOP)))
    out: list[int] = []
    for frame in sorted(set(int(x) for x in frames)):
        if not out or frame - out[-1] >= min_frames:
            out.append(frame)
    return out


def bass_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa

    y = load_mono(path)
    env = onset_env(y)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=env,
        sr=SR,
        hop_length=HOP,
        backtrack=True,
        units="frames",
    )
    retained = collapse_onsets(np.asarray(onset_frames, dtype=int), 35.0)
    harmonic, _ = librosa.effects.hpss(y)
    f0, _voiced_flag, voiced_prob = librosa.pyin(
        harmonic,
        fmin=librosa.midi_to_hz(BASS_RANGE[0]),
        fmax=librosa.midi_to_hz(BASS_RANGE[1]),
        sr=SR,
        frame_length=2048,
        hop_length=256,
    )
    pyin_midi = librosa.hz_to_midi(np.asarray(f0, dtype=float))
    voiced_prob = np.asarray(voiced_prob, dtype=float)
    cqt, freqs = harmonic_cqt(y, BASS_RANGE[0], BASS_RANGE[1])
    half_frames = max(1, int(round((0.180 / 2.0) * SR / HOP)))
    rows: list[dict[str, Any]] = []
    for index, frame in enumerate(retained):
        lo = max(0, frame - half_frames)
        hi = min(cqt.shape[1], frame + half_frames + 1)
        frames = list(range(lo, hi)) or [frame]
        hscores, fundamentals = template_scores(cqt, freqs, frames, BASS_RANGE[0], BASS_RANGE[1])
        harmonic_z = z_across_candidates(hscores)
        p_lo = max(0, lo)
        p_hi = min(len(pyin_midi), hi)
        finite = np.isfinite(pyin_midi[p_lo:p_hi])
        if np.any(finite):
            pm = float(np.median(pyin_midi[p_lo:p_hi][finite]))
            vp = float(np.nanmedian(voiced_prob[p_lo:p_hi][finite]))
            vp = 0.0 if not math.isfinite(vp) else vp
            midi_candidates = np.arange(BASS_RANGE[0], BASS_RANGE[1] + 1, dtype=float)
            proximity = np.exp(-0.5 * ((midi_candidates - pm) / 0.75) ** 2)
            combined = harmonic_z + 0.75 * vp * proximity
        else:
            pm = None
            vp = 0.0
            combined = harmonic_z
        best_value = float(np.max(combined))
        best_offsets = np.where(np.abs(combined - best_value) <= EPS)[0]
        best_offset = int(best_offsets[0])
        midi = BASS_RANGE[0] + best_offset
        start = float(librosa.frames_to_time(frame, sr=SR, hop_length=HOP))
        if index + 1 < len(retained):
            next_start = float(librosa.frames_to_time(retained[index + 1], sr=SR, hop_length=HOP))
            end = min(next_start, start + 0.5)
        else:
            end = start + 0.5
        rows.append({
            "midi": int(midi),
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": max(0.0, end - start),
            "source": "onset_harmonic_pyin",
            "onsetProposalIndex": index,
            "onsetFrame": int(frame),
            "harmonicTemplateScore": float(hscores[best_offset]),
            "fundamentalMeanMagnitude": float(fundamentals[best_offset]),
            "fundamentalPresent": bool(fundamentals[best_offset] > float(np.median(fundamentals))),
            "medianPyinMidi": pm,
            "medianPyinVoicedProbability": vp,
            "combinedPitchScore": best_value,
        })
    return rows, {
        "detectedOnsetCount": int(len(onset_frames)),
        "retainedOnsetCount": int(len(retained)),
        "eventCountBeforeGridDedupe": len(rows),
        "inputSha256": sha256_file(path),
    }


def top_template_midi_per_frame(
    cqt: np.ndarray,
    freqs: np.ndarray,
    frame: int,
    midi_min: int,
    midi_max: int,
    topn: int,
) -> list[tuple[int, float, bool]]:
    scores, fundamentals = template_scores(cqt, freqs, [frame], midi_min, midi_max)
    med_fund = float(np.median(fundamentals))
    ranked = sorted(
        [(midi_min + i, float(scores[i]), bool(fundamentals[i] > med_fund)) for i in range(len(scores))],
        key=lambda row: (-row[1], row[0]),
    )
    return ranked[:topn]


def three_frame_template(
    cqt: np.ndarray,
    freqs: np.ndarray,
    frame: int,
    midi_min: int,
    midi_max: int,
) -> tuple[np.ndarray, np.ndarray]:
    frames = [int(np.clip(frame + delta, 0, cqt.shape[1] - 1)) for delta in (-1, 0, 1)]
    return template_scores(cqt, freqs, frames, midi_min, midi_max)


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    y = load_mono(path)
    cqt, freqs = harmonic_cqt(y, GUITAR_RANGE[0], GUITAR_RANGE[1])
    _, _, notes = predict(
        path,
        model_or_model_path=Path(ICASSP_2022_MODEL_PATH),
        onset_threshold=0.50,
        frame_threshold=0.30,
        minimum_note_length=90.0,
        minimum_frequency=librosa.midi_to_hz(GUITAR_RANGE[0]),
        maximum_frequency=librosa.midi_to_hz(GUITAR_RANGE[1]),
        multiple_pitch_bends=False,
        melodia_trick=True,
    )
    rows: list[dict[str, Any]] = []
    raw_basic_pitch_count = 0
    register_repairs = 0
    for note in notes:
        if len(note) < 4:
            continue
        start = float(note[0])
        end = float(note[1])
        raw_midi = int(round(float(note[2])))
        amplitude = float(note[3])
        if not GUITAR_RANGE[0] <= raw_midi <= GUITAR_RANGE[1]:
            continue
        raw_basic_pitch_count += 1
        frame = int(np.clip(round(start * SR / HOP), 0, cqt.shape[1] - 1))
        scores, fundamentals = three_frame_template(cqt, freqs, frame, GUITAR_RANGE[0], GUITAR_RANGE[1])
        median_fundamental = float(np.median(fundamentals))
        candidates = [raw_midi] + [
            midi for midi in (raw_midi - 12, raw_midi + 12)
            if GUITAR_RANGE[0] <= midi <= GUITAR_RANGE[1]
        ]
        chosen = raw_midi
        chosen_score = float(scores[raw_midi - GUITAR_RANGE[0]])
        for midi in sorted(candidates):
            offset = midi - GUITAR_RANGE[0]
            score = float(scores[offset])
            fundamental_present = bool(fundamentals[offset] > median_fundamental)
            if midi != raw_midi and fundamental_present and score > chosen_score + EPS:
                chosen = midi
                chosen_score = score
        if chosen != raw_midi:
            register_repairs += 1
        rows.append({
            "midi": int(chosen),
            "startSeconds": start,
            "endSeconds": end,
            "durationSeconds": max(0.0, end - start),
            "confidence": amplitude,
            "source": "basic_pitch",
            "basicPitchOriginalMidi": int(raw_midi),
            "registerRepaired": bool(chosen != raw_midi),
            "templateScore": chosen_score,
        })

    env = onset_env(y)
    onset_frames = np.asarray(librosa.onset.onset_detect(
        onset_envelope=env,
        sr=SR,
        hop_length=HOP,
        backtrack=False,
        units="frames",
    ), dtype=int)
    added = 0
    for onset_index, raw_frame in enumerate(onset_frames):
        frame = int(np.clip(raw_frame, 1, cqt.shape[1] - 2))
        frame_sets: list[set[int]] = []
        frame_scores: dict[int, list[float]] = {}
        frame_fundamental: dict[int, list[bool]] = {}
        for analysis_frame in (frame - 1, frame, frame + 1):
            ranked = top_template_midi_per_frame(
                cqt, freqs, analysis_frame, GUITAR_RANGE[0], GUITAR_RANGE[1], 6
            )
            frame_sets.append({midi for midi, _, _ in ranked})
            for midi, score, fundamental_present in ranked:
                frame_scores.setdefault(midi, []).append(score)
                frame_fundamental.setdefault(midi, []).append(fundamental_present)
        persistent = set.intersection(*frame_sets) if frame_sets else set()
        candidates: list[tuple[int, float, bool]] = []
        for midi in persistent:
            values = frame_scores.get(midi, [])
            if len(values) != 3:
                continue
            candidates.append((
                midi,
                float(np.mean(values)),
                any(frame_fundamental.get(midi, [])),
            ))
        candidates.sort(key=lambda row: (-row[1], row[0]))
        onset_seconds = float(librosa.frames_to_time(frame, sr=SR, hop_length=HOP))
        for midi, score, fundamental_present in candidates[:6]:
            if any(
                int(row["midi"]) == midi
                and abs(float(row["startSeconds"]) - onset_seconds) <= 0.060
                for row in rows
            ):
                continue
            rows.append({
                "midi": int(midi),
                "startSeconds": onset_seconds,
                "endSeconds": onset_seconds + 0.07,
                "durationSeconds": 0.07,
                "confidence": score,
                "source": "harmonic_track",
                "onsetProposalIndex": onset_index,
                "onsetFrame": frame,
                "persistentTrackFrames": 3,
                "templateScore": score,
                "fundamentalPresent": bool(fundamental_present),
            })
            added += 1
    return rows, {
        "inputSha256": sha256_file(path),
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": raw_basic_pitch_count,
        "registerRepairCount": register_repairs,
        "independentOnsetCount": int(len(onset_frames)),
        "harmonicTrackAddedCount": added,
        "eventCountBeforeGridDedupe": len(rows),
    }


@dataclass(frozen=True)
class FrozenGrid:
    times: np.ndarray
    steps: np.ndarray

    def raw_step(self, seconds: float) -> float:
        t = float(seconds)
        if len(self.times) < 2:
            raise RuntimeError("V159 frozen grid has fewer than two beats")
        if t <= self.times[0]:
            period = float(self.times[1] - self.times[0])
            return float(self.steps[0] + 4.0 * (t - self.times[0]) / period)
        if t >= self.times[-1]:
            period = float(self.times[-1] - self.times[-2])
            return float(self.steps[-1] + 4.0 * (t - self.times[-1]) / period)
        hi = int(np.searchsorted(self.times, t, side="right"))
        lo = hi - 1
        dt = float(self.times[hi] - self.times[lo])
        if not math.isfinite(dt) or dt <= 0.0:
            raise RuntimeError("V159 frozen grid interpolation interval invalid")
        frac = (t - float(self.times[lo])) / dt
        return float(self.steps[lo] + frac * (self.steps[hi] - self.steps[lo]))


def frozen_grid(timebase: dict[str, Any]) -> FrozenGrid:
    times = np.asarray(timebase.get("gridBeatTimesSeconds", []), dtype=float)
    steps = np.asarray(timebase.get("gridBeatSteps", []), dtype=float)
    if len(times) < 2 or len(times) != len(steps):
        raise RuntimeError("V159 frozen timebase grid length invalid")
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(steps)):
        raise RuntimeError("V159 frozen timebase grid nonfinite")
    if not np.all(np.diff(times) > 0.0) or not np.all(np.diff(steps) == 4.0):
        raise RuntimeError("V159 frozen timebase grid invariant failure")
    return FrozenGrid(times=times, steps=steps)


def map_and_dedupe(
    events: list[dict[str, Any]],
    grid: FrozenGrid,
    stream: str,
) -> tuple[list[dict[str, Any]], int]:
    precedence = {"basic_pitch": 0, "harmonic_track": 1, "onset_harmonic_pyin": 2}
    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = 0
    for row in events:
        raw = grid.raw_step(float(row["startSeconds"]))
        snapped = int(round(raw))
        if snapped < 0:
            pregrid += 1
            continue
        item = dict(row)
        item.update({
            "rawGridStep": float(raw),
            "absoluteGridStep": snapped,
            "measure": snapped // 16 + 1,
            "step": snapped % 16,
            "stream": stream,
        })
        key = (snapped, int(item["midi"]))
        old = mapped.get(key)
        if old is None:
            mapped[key] = item
        else:
            new_precedence = precedence.get(str(item.get("source")), 99)
            old_precedence = precedence.get(str(old.get("source")), 99)
            new_evidence = float(item.get("confidence", item.get("combinedPitchScore", 0.0)))
            old_evidence = float(old.get("confidence", old.get("combinedPitchScore", 0.0)))
            if new_precedence < old_precedence or (
                new_precedence == old_precedence and new_evidence > old_evidence
            ):
                mapped[key] = item
    return sorted(
        mapped.values(),
        key=lambda row: (int(row["absoluteGridStep"]), int(row["midi"]), str(row["source"])),
    ), pregrid


def validate_runtime_boundary(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    timebase = load_json(args.timebase)
    qc = load_json(args.timebase_qc)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)

    if prereg.get("version") != "V159" or prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V159 preregistration state invalid")
    if contract.get("version") != "V159" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V159 implementation-contract state invalid")
    schemas = contract.get("canonicalSchemas", {})
    if timebase.get("schema") != TIMEBASE_SCHEMA or schemas.get("timebase") != TIMEBASE_SCHEMA:
        raise RuntimeError("V159 timebase schema invalid")
    if qc.get("schema") != TIMEBASE_QC_SCHEMA or qc.get("validation") != "PASS":
        raise RuntimeError("V159 timebase QC is not frozen PASS")
    if qc.get("timebaseSha256") != sha256_file(args.timebase):
        raise RuntimeError("V159 timebase identity differs from PASS QC receipt")
    if pre_run.get("schema") != PRE_RUN_SCHEMA or pre_run.get("validation") != "PASS":
        raise RuntimeError("V159 pre-run identity receipt invalid")
    if environment.get("schema") != ENV_SCHEMA or environment.get("validation") != "PASS" or environment.get("device") != "cpu":
        raise RuntimeError("V159 environment receipt invalid")
    if environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        raise RuntimeError("V159 environment is not sealed CPU-only")

    pins = pre_run.get("pinnedGitBlobs") or {}
    expected_pins = {
        "preregistration": git_blob_sha(args.preregistration),
        "implementationContract": git_blob_sha(args.implementation_contract),
        "transcriber": git_blob_sha(Path(__file__)),
    }
    for key, expected in expected_pins.items():
        if pins.get(key) != expected:
            raise RuntimeError(f"V159 pre-run code/input pin drift: {key}")
    if pre_run.get("timebaseMustNotExistAtSeal") is not True:
        raise RuntimeError("V159 pre-run receipt did not seal pre-timebase state")
    if pre_run.get("candidateMustNotExistAtSeal") is not True or pre_run.get("generationReceiptMustNotExistAtSeal") is not True:
        raise RuntimeError("V159 pre-run candidate/receipt absence boundary invalid")
    if pre_run.get("referenceReadAtSeal") is not False or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0:
        raise RuntimeError("V159 pre-run reference boundary invalid")

    safety = timebase.get("safety") or {}
    if not (
        safety.get("referenceRead") is False
        and safety.get("professionalReferencePathsOpened") == 0
        and safety.get("priorGeneratedCandidateRead") is False
        and safety.get("priorScoreRead") is False
        and safety.get("priorDiagnosticReadByRuntime") is False
        and safety.get("gpu") is False
    ):
        raise RuntimeError("V159 frozen timebase safety boundary invalid")

    stem_ids = timebase.get("stemIdentities") or {}
    expected_stems = {
        "guitar": args.guitar,
        "bass": args.bass,
        "drums": args.drums,
    }
    for name, path in expected_stems.items():
        record = stem_ids.get(name) or {}
        if record.get("sha256") != sha256_file(path) or record.get("bytes") != path.stat().st_size:
            raise RuntimeError(f"V159 {name} stem differs from frozen timebase identity")
    mix_record = (timebase.get("audioIdentity") or {}).get("normalizedMix") or {}
    if mix_record.get("sha256") != sha256_file(args.mix) or mix_record.get("bytes") != args.mix.stat().st_size:
        raise RuntimeError("V159 normalized mix differs from frozen timebase identity")

    return prereg, contract, timebase, environment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mix", type=Path, required=True)
    parser.add_argument("--guitar", type=Path, required=True)
    parser.add_argument("--bass", type=Path, required=True)
    parser.add_argument("--drums", type=Path, required=True)
    parser.add_argument("--timebase", type=Path, required=True)
    parser.add_argument("--timebase-qc", type=Path, required=True)
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--implementation-contract", type=Path, required=True)
    parser.add_argument("--pre-run-receipt", type=Path, required=True)
    parser.add_argument("--environment-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()

    if args.output.exists() or args.receipt.exists():
        raise RuntimeError("V159 candidate/generation receipt is write-once")
    for path in (
        args.mix, args.guitar, args.bass, args.drums, args.timebase,
        args.timebase_qc, args.preregistration, args.implementation_contract,
        args.pre_run_receipt, args.environment_receipt,
    ):
        if not path.is_file():
            raise RuntimeError(f"missing V159 transcriber input: {path}")

    prereg, contract, timebase, environment = validate_runtime_boundary(args)
    grid = frozen_grid(timebase)

    # HARD BOUNDARY: pitch inference begins only after validate_runtime_boundary
    # has proved the independent timebase-QC receipt is frozen PASS.
    bass_raw, bass_meta = bass_events(args.bass)
    guitar_raw, guitar_meta = guitar_events(args.guitar)
    guitar, guitar_pre = map_and_dedupe(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = map_and_dedupe(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V159 generated empty required stream")

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "priorDiagnosticReadByRuntime": False,
        "referenceGuidedFiltering": False,
        "thresholdSweep": False,
        "variantSelection": False,
        "humanCorrection": False,
        "cudaGpuUsed": False,
        "modalUsed": False,
        "mainOrProductionModified": False,
    }
    song = prereg.get("song", {})
    candidate = {
        "schema": CANDIDATE_SCHEMA,
        "song": {"artist": song.get("artist"), "title": song.get("title")},
        "classification": "single-preregistered-reference-blind-v159-cpu-timebase-first-candidate",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebaseIdentity": {
            "path": str(args.timebase),
            "sha256": sha256_file(args.timebase),
            "schema": timebase.get("schema"),
            "timebaseQcPath": str(args.timebase_qc),
            "timebaseQcSha256": sha256_file(args.timebase_qc),
            "selectedPhase": timebase.get("selectedPhase"),
        },
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "sealedInputs": {
            "preregistrationGitBlob": git_blob_sha(args.preregistration),
            "implementationContractGitBlob": git_blob_sha(args.implementation_contract),
            "canonicalEntryPointGitBlob": git_blob_sha(Path(__file__)),
            "preRunReceiptSha256": sha256_file(args.pre_run_receipt),
            "environmentReceiptSha256": sha256_file(args.environment_receipt),
            "timebaseSha256": sha256_file(args.timebase),
            "timebaseQcSha256": sha256_file(args.timebase_qc),
        },
        "safety": safety,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": "V159",
        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "candidatePath": str(args.output),
        "candidateSha256": sha256_file(args.output),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
        "preRunReceiptSha256": sha256_file(args.pre_run_receipt),
        "environmentReceiptSha256": sha256_file(args.environment_receipt),
        "timebaseSha256": sha256_file(args.timebase),
        "timebaseQcSha256": sha256_file(args.timebase_qc),
        "implementation": {"canonicalEntryPointGitBlob": git_blob_sha(Path(__file__))},
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {
            "mixSha256": sha256_file(args.mix),
            "guitarStemSha256": sha256_file(args.guitar),
            "bassStemSha256": sha256_file(args.bass),
            "drumsStemSha256": sha256_file(args.drums),
        },
        "environment": environment,
        "safety": safety,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "candidateSha256": receipt["candidateSha256"],
        "counts": receipt["counts"],
        "timebaseQc": "PASS",
        "referenceRead": False,
        "scoreCalls": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
