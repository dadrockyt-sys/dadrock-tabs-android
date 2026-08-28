#!/usr/bin/env python3
"""Sealed V161 CPU transcriber consuming a frozen PASS V161 timebase QC."""
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

from event_logic_v161 import (
    BASS_ONSET_RADIUS_FRAMES,
    GUITAR_ONSET_RADIUS_FRAMES,
    bass_admission_score,
    bass_transition_frames,
    cap_bass_grid,
    cap_guitar_polyphony,
    guitar_admission_score,
    median_smooth_midi,
    merge_bass_proposals,
    merge_same_pitch_rows,
    refine_onset_frame,
    support_unit,
    suppress_same_pitch_refractory,
    template_rank,
)

SR = 22050
HOP = 256
BPO = 36
HARMONICS = (1, 2, 3, 4, 5)
HWEIGHTS = (1.0, 0.5, 0.3333333333, 0.25, 0.2)
BASS_RANGE = (28, 67)
GUITAR_RANGE = (40, 88)
EPS = 1e-12
TARGET_ARTIST = "Lenny Kravitz"
TARGET_TITLE = "Are You Gonna Go My Way"

CANDIDATE_SCHEMA = "dadrock.tabs.v161.cpu-event-refined-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v161.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v161.reference-blind-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v161.reference-blind-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v161.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v161.cpu-environment-receipt.v1"


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
    x = np.asarray(librosa.onset.onset_strength(y=y, sr=SR, hop_length=HOP), dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("invalid onset envelope")
    return x


def rms_env(y: np.ndarray) -> np.ndarray:
    import librosa
    x = np.asarray(librosa.feature.rms(y=y, frame_length=2048, hop_length=HOP)[0], dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("invalid RMS envelope")
    return x


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
    cqt = np.log1p(np.abs(librosa.cqt(harmonic, sr=SR, hop_length=HOP, fmin=fmin, n_bins=n_bins, bins_per_octave=BPO)))
    freqs = librosa.cqt_frequencies(n_bins, fmin=fmin, bins_per_octave=BPO)
    if not np.all(np.isfinite(cqt)) or not np.all(np.isfinite(freqs)):
        raise RuntimeError("nonfinite harmonic CQT")
    return cqt, freqs


def frequency_bin(freqs: np.ndarray, hz: float) -> int:
    return int(np.argmin(np.abs(freqs - hz)))


def template_scores(cqt: np.ndarray, freqs: np.ndarray, frames: list[int], midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
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


def three_frame_template(cqt: np.ndarray, freqs: np.ndarray, frame: int, midi_min: int, midi_max: int) -> tuple[np.ndarray, np.ndarray]:
    frames = [int(np.clip(frame + delta, 0, cqt.shape[1] - 1)) for delta in (-1, 0, 1)]
    return template_scores(cqt, freqs, frames, midi_min, midi_max)


def collapse_onsets(frames: np.ndarray, min_ms: float) -> list[int]:
    min_frames = max(1, int(math.ceil((min_ms / 1000.0) * SR / HOP)))
    out: list[int] = []
    for frame in sorted(set(int(x) for x in frames)):
        if not out or frame - out[-1] >= min_frames:
            out.append(frame)
    return out


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa
    from basic_pitch import ICASSP_2022_MODEL_PATH
    from basic_pitch.inference import predict

    y = load_mono(path)
    env = onset_env(y)
    rms = rms_env(y)
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
    raw: list[dict[str, Any]] = []
    for note in notes:
        if len(note) < 4:
            continue
        start, end = float(note[0]), float(note[1])
        midi = int(round(float(note[2])))
        confidence = float(note[3])
        if GUITAR_RANGE[0] <= midi <= GUITAR_RANGE[1] and math.isfinite(start) and math.isfinite(end) and math.isfinite(confidence):
            raw.append({"midi": midi, "startSeconds": start, "endSeconds": end, "durationSeconds": max(0.0, end - start), "confidence": confidence})

    merged = merge_same_pitch_rows(raw)
    admitted: list[dict[str, Any]] = []
    register_repairs = 0
    rejected_score = 0
    rejected_activity = 0
    refined_count = 0
    for row in merged:
        original_start = float(row["startSeconds"])
        duration = max(0.0, float(row["endSeconds"]) - original_start)
        original_frame = int(np.clip(round(original_start * SR / HOP), 0, cqt.shape[1] - 1))
        refined_frame, refine_meta = refine_onset_frame(env, original_frame, GUITAR_ONSET_RADIUS_FRAMES)
        refined_count += int(refine_meta["moved"])
        scores, fundamentals = three_frame_template(cqt, freqs, refined_frame, GUITAR_RANGE[0], GUITAR_RANGE[1])
        raw_midi = int(row["midi"])
        candidates = [raw_midi] + [m for m in (raw_midi - 12, raw_midi + 12) if GUITAR_RANGE[0] <= m <= GUITAR_RANGE[1]]
        chosen = raw_midi
        chosen_offset = raw_midi - GUITAR_RANGE[0]
        chosen_score = float(scores[chosen_offset])
        median_fundamental = float(np.median(fundamentals))
        for midi in sorted(candidates):
            offset = midi - GUITAR_RANGE[0]
            score = float(scores[offset])
            fundamental_present = bool(fundamentals[offset] > median_fundamental)
            if midi != raw_midi and fundamental_present and score > chosen_score + EPS:
                chosen, chosen_offset, chosen_score = midi, offset, score
        register_repairs += int(chosen != raw_midi)
        rank = template_rank(scores, chosen_offset)
        onset_support = support_unit(float(env[min(refined_frame, len(env) - 1)]), env)
        activity_frame = int(np.clip(refined_frame, 0, len(rms) - 1))
        activity_support = support_unit(float(rms[activity_frame]), rms)
        persistence = float(np.clip(duration / 0.250, 0.0, 1.0))
        confidence = float(np.clip(float(row.get("confidence", 0.0)), 0.0, 1.0))
        admission = guitar_admission_score(confidence, rank, onset_support, persistence, activity_support)
        if activity_support + EPS < 0.05:
            rejected_activity += 1
            continue
        if admission + EPS < 0.50:
            rejected_score += 1
            continue
        start = float(librosa.frames_to_time(refined_frame, sr=SR, hop_length=HOP))
        admitted.append({
            "midi": int(chosen),
            "startSeconds": start,
            "endSeconds": start + duration,
            "durationSeconds": duration,
            "confidence": confidence,
            "source": "basic_pitch_consolidated",
            "basicPitchOriginalMidi": raw_midi,
            "registerRepaired": bool(chosen != raw_midi),
            "templateScore": chosen_score,
            "templateRank": rank,
            "onsetSupport": onset_support,
            "activitySupport": activity_support,
            "persistenceSupport": persistence,
            "admissionScore": admission,
            "mergedRawCount": int(row.get("mergedRawCount", 1)),
            "originalStartSeconds": original_start,
            "originalOnsetFrame": original_frame,
            "refinedOnsetFrame": refined_frame,
            "onsetRefined": bool(refine_meta["moved"]),
            "onsetRefinement": refine_meta,
        })
    return admitted, {
        "inputSha256": sha256_file(path),
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": len(raw),
        "consolidatedCandidateCount": len(merged),
        "admittedEventCountBeforeGridDedupe": len(admitted),
        "registerRepairCount": register_repairs,
        "onsetRefinedCount": refined_count,
        "rejectedByAdmissionScore": rejected_score,
        "rejectedByActivity": rejected_activity,
        "standaloneHarmonicTrackRecoveryEnabled": False,
        "standaloneHarmonicTrackAddedCount": 0,
    }


def bass_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    import librosa

    y = load_mono(path)
    env = onset_env(y)
    rms = rms_env(y)
    onset_frames = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=True, units="frames"), dtype=int)
    retained_onsets = collapse_onsets(onset_frames, 35.0)
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
    smoothed = median_smooth_midi(pyin_midi)
    transitions = bass_transition_frames(smoothed, voiced_prob)
    proposals = merge_bass_proposals(retained_onsets, transitions, env)
    cqt, freqs = harmonic_cqt(y, BASS_RANGE[0], BASS_RANGE[1])
    half_frames = max(1, int(round((0.120 / 2.0) * SR / HOP)))
    admitted: list[dict[str, Any]] = []
    refined_count = 0
    rejected_score = 0
    rejected_activity = 0
    rejected_additional = 0
    for index, proposal in enumerate(proposals):
        original_frame = int(proposal["frame"])
        refined_frame, refine_meta = refine_onset_frame(env, original_frame, BASS_ONSET_RADIUS_FRAMES)
        refined_count += int(refine_meta["moved"])
        lo = max(0, refined_frame - half_frames)
        hi = min(cqt.shape[1], refined_frame + half_frames + 1)
        frames = list(range(lo, hi)) or [refined_frame]
        hscores, fundamentals = template_scores(cqt, freqs, frames, BASS_RANGE[0], BASS_RANGE[1])
        harmonic_z = z_across_candidates(hscores)
        p_lo = max(0, lo)
        p_hi = min(len(pyin_midi), hi)
        finite = np.isfinite(pyin_midi[p_lo:p_hi])
        if np.any(finite):
            pm = float(np.median(pyin_midi[p_lo:p_hi][finite]))
            vp = float(np.nanmedian(voiced_prob[p_lo:p_hi][finite]))
            vp = 0.0 if not math.isfinite(vp) else float(np.clip(vp, 0.0, 1.0))
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
        rank = template_rank(combined, best_offset)
        fundamental_present = bool(fundamentals[best_offset] > float(np.median(fundamentals)))
        onset_support = support_unit(float(env[min(refined_frame, len(env) - 1)]), env)
        activity_frame = int(np.clip(refined_frame, 0, len(rms) - 1))
        activity_support = support_unit(float(rms[activity_frame]), rms)
        admission = bass_admission_score(vp, rank, onset_support, activity_support)
        if activity_support + EPS < 0.04:
            rejected_activity += 1
            continue
        if not (fundamental_present or vp + EPS >= 0.60):
            rejected_additional += 1
            continue
        if admission + EPS < 0.42:
            rejected_score += 1
            continue
        start = float(librosa.frames_to_time(refined_frame, sr=SR, hop_length=HOP))
        source = "onset_harmonic_pyin_refined" if proposal["kind"] == "detected_onset" else "transition_harmonic_pyin_refined"
        admitted.append({
            "midi": int(midi),
            "startSeconds": start,
            "endSeconds": start + 0.5,
            "durationSeconds": 0.5,
            "source": source,
            "proposalKind": proposal["kind"],
            "proposalIndex": index,
            "mergedProposalCount": int(proposal["mergedProposalCount"]),
            "originalOnsetFrame": original_frame,
            "refinedOnsetFrame": refined_frame,
            "onsetRefined": bool(refine_meta["moved"]),
            "onsetRefinement": refine_meta,
            "harmonicTemplateScore": float(hscores[best_offset]),
            "fundamentalMeanMagnitude": float(fundamentals[best_offset]),
            "fundamentalPresent": fundamental_present,
            "medianPyinMidi": pm,
            "medianPyinVoicedProbability": vp,
            "combinedPitchScore": best_value,
            "templateRank": rank,
            "onsetSupport": onset_support,
            "activitySupport": activity_support,
            "admissionScore": admission,
        })
    admitted = suppress_same_pitch_refractory(admitted)
    admitted.sort(key=lambda r: (float(r["startSeconds"]), int(r["midi"])))
    for i, row in enumerate(admitted):
        start = float(row["startSeconds"])
        next_start = float(admitted[i + 1]["startSeconds"]) if i + 1 < len(admitted) else start + 0.5
        end = min(next_start, start + 0.5)
        row["endSeconds"] = end
        row["durationSeconds"] = max(0.0, end - start)
    return admitted, {
        "inputSha256": sha256_file(path),
        "detectedOnsetCount": int(len(onset_frames)),
        "retainedOnsetCount": int(len(retained_onsets)),
        "pitchTransitionProposalCount": int(len(transitions)),
        "mergedProposalCount": int(len(proposals)),
        "admittedEventCountBeforeGridDedupe": len(admitted),
        "onsetRefinedCount": refined_count,
        "rejectedByAdmissionScore": rejected_score,
        "rejectedByActivity": rejected_activity,
        "rejectedByAdditionalGate": rejected_additional,
    }


@dataclass(frozen=True)
class FrozenGrid:
    times: np.ndarray
    steps: np.ndarray

    def raw_step(self, seconds: float) -> float:
        t = float(seconds)
        if len(self.times) < 2:
            raise RuntimeError("V161 frozen grid has fewer than two beats")
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
            raise RuntimeError("V161 frozen grid interpolation interval invalid")
        frac = (t - float(self.times[lo])) / dt
        return float(self.steps[lo] + frac * (self.steps[hi] - self.steps[lo]))


def frozen_grid(timebase: dict[str, Any]) -> FrozenGrid:
    times = np.asarray(timebase.get("gridBeatTimesSeconds", []), dtype=float)
    steps = np.asarray(timebase.get("gridBeatSteps", []), dtype=float)
    if len(times) < 2 or len(times) != len(steps):
        raise RuntimeError("V161 frozen timebase grid length invalid")
    if not np.all(np.isfinite(times)) or not np.all(np.isfinite(steps)) or not np.all(np.diff(times) > 0.0) or not np.all(np.diff(steps) == 4.0):
        raise RuntimeError("V161 frozen timebase grid invariant failure")
    return FrozenGrid(times=times, steps=steps)


def map_events(events: list[dict[str, Any]], grid: FrozenGrid, stream: str) -> tuple[list[dict[str, Any]], int]:
    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = 0
    for row in events:
        raw = grid.raw_step(float(row["startSeconds"]))
        snapped = int(round(raw))
        if snapped < 0:
            pregrid += 1
            continue
        item = dict(row)
        item.update({"rawGridStep": float(raw), "absoluteGridStep": snapped, "measure": snapped // 16 + 1, "step": snapped % 16, "stream": stream})
        key = (snapped, int(item["midi"]))
        old = mapped.get(key)
        if old is None:
            mapped[key] = item
        else:
            new_key = (-float(item.get("admissionScore", 0.0)), -float(item.get("confidence", item.get("medianPyinVoicedProbability", 0.0))), int(item["midi"]))
            old_key = (-float(old.get("admissionScore", 0.0)), -float(old.get("confidence", old.get("medianPyinVoicedProbability", 0.0))), int(old["midi"]))
            if new_key < old_key:
                mapped[key] = item
    rows = list(mapped.values())
    rows = cap_guitar_polyphony(rows) if stream == "combinedGuitar" else cap_bass_grid(rows)
    return rows, pregrid


def validate_runtime_boundary(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    timebase = load_json(args.timebase)
    qc = load_json(args.timebase_qc)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)
    if prereg.get("version") != "V161" or prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V161 preregistration state invalid")
    if contract.get("version") != "V161" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V161 implementation-contract state invalid")
    schemas = contract.get("canonicalSchemas", {})
    if timebase.get("schema") != TIMEBASE_SCHEMA or schemas.get("timebase") != TIMEBASE_SCHEMA:
        raise RuntimeError("V161 timebase schema invalid")
    if schemas.get("candidate") != CANDIDATE_SCHEMA or schemas.get("generationReceipt") != RECEIPT_SCHEMA:
        raise RuntimeError("V161 candidate/generation schema contract drift")
    if qc.get("schema") != TIMEBASE_QC_SCHEMA or schemas.get("timebaseQc") != TIMEBASE_QC_SCHEMA or qc.get("validation") != "PASS":
        raise RuntimeError("V161 timebase QC is not frozen PASS")
    if qc.get("timebaseSha256") != sha256_file(args.timebase):
        raise RuntimeError("V161 timebase identity differs from PASS QC receipt")
    if pre_run.get("schema") != PRE_RUN_SCHEMA or pre_run.get("validation") != "PASS":
        raise RuntimeError("V161 pre-run identity receipt invalid")
    if environment.get("schema") != ENV_SCHEMA or environment.get("validation") != "PASS" or environment.get("device") != "cpu":
        raise RuntimeError("V161 environment receipt invalid")
    if environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        raise RuntimeError("V161 environment is not sealed CPU-only")
    pins = pre_run.get("pinnedGitBlobs") or {}
    expected = {
        "preregistration": git_blob_sha(args.preregistration),
        "implementationContract": git_blob_sha(args.implementation_contract),
        "eventLogic": git_blob_sha(Path(__file__).with_name("event_logic_v161.py")),
        "transcriber": git_blob_sha(Path(__file__)),
    }
    for key, value in expected.items():
        if pins.get(key) != value:
            raise RuntimeError(f"V161 pre-run pin drift: {key}")
    for key in ("timebaseMustNotExistAtSeal", "timebaseQcReceiptMustNotExistAtSeal", "candidateMustNotExistAtSeal", "generationReceiptMustNotExistAtSeal"):
        if pre_run.get(key) is not True:
            raise RuntimeError(f"V161 pre-run absence boundary invalid: {key}")
    if pre_run.get("referenceReadAtSeal") is not False or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0 or pre_run.get("V160CandidateReadAtSeal") is not False:
        raise RuntimeError("V161 pre-run reference/predecessor boundary invalid")
    safety = timebase.get("safety") or {}
    if not (safety.get("referenceRead") is False and safety.get("professionalReferencePathsOpened") == 0 and safety.get("priorGeneratedCandidateRead") is False and safety.get("priorScoreRead") is False and safety.get("priorDiagnosticReadByRuntime") is False and safety.get("V160CandidateRead") is False and safety.get("gpu") is False):
        raise RuntimeError("V161 timebase safety boundary invalid")
    for name, path in {"guitar": args.guitar, "bass": args.bass, "drums": args.drums}.items():
        record = (timebase.get("stemIdentities") or {}).get(name) or {}
        if record.get("sha256") != sha256_file(path) or record.get("bytes") != path.stat().st_size:
            raise RuntimeError(f"V161 {name} stem differs from frozen timebase")
    mix_record = (timebase.get("audioIdentity") or {}).get("normalizedMix") or {}
    if mix_record.get("sha256") != sha256_file(args.mix) or mix_record.get("bytes") != args.mix.stat().st_size:
        raise RuntimeError("V161 normalized mix differs from frozen timebase")
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
        raise RuntimeError("V161 candidate/generation receipt is write-once")
    for path in (args.mix, args.guitar, args.bass, args.drums, args.timebase, args.timebase_qc, args.preregistration, args.implementation_contract, args.pre_run_receipt, args.environment_receipt):
        if not path.is_file():
            raise RuntimeError(f"missing V161 transcriber input: {path}")

    _prereg, _contract, timebase, environment = validate_runtime_boundary(args)
    grid = frozen_grid(timebase)
    # HARD BOUNDARY: no pitch inference occurs before the frozen independent QC PASS above.
    bass_raw, bass_meta = bass_events(args.bass)
    guitar_raw, guitar_meta = guitar_events(args.guitar)
    guitar, guitar_pre = map_events(guitar_raw, grid, "combinedGuitar")
    bass, bass_pre = map_events(bass_raw, grid, "bass")
    if not guitar or not bass:
        raise RuntimeError("V161 generated empty required stream")

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "V160CandidateRead": False,
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
        "song": {"artist": TARGET_ARTIST, "title": TARGET_TITLE},
        "classification": "single-preregistered-reference-blind-v161-cpu-event-refined-candidate",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebaseIdentity": {"path": str(args.timebase), "sha256": sha256_file(args.timebase), "schema": timebase.get("schema"), "timebaseQcPath": str(args.timebase_qc), "timebaseQcSha256": sha256_file(args.timebase_qc), "selectedPhase": timebase.get("selectedPhase")},
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "sealedInputs": {
            "preregistrationGitBlob": git_blob_sha(args.preregistration),
            "implementationContractGitBlob": git_blob_sha(args.implementation_contract),
            "eventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v161.py")),
            "canonicalEntryPointGitBlob": git_blob_sha(Path(__file__)),
            "preRunReceiptSha256": sha256_file(args.pre_run_receipt),
            "environmentReceiptSha256": sha256_file(args.environment_receipt),
            "timebaseSha256": sha256_file(args.timebase),
            "timebaseQcSha256": sha256_file(args.timebase_qc),
        },
        "safety": safety,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(candidate, indent=2, sort_keys=True, allow_nan=False) + "\n")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "version": "V161",
        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "candidatePath": str(args.output),
        "candidateSha256": sha256_file(args.output),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
        "preRunReceiptSha256": sha256_file(args.pre_run_receipt),
        "environmentReceiptSha256": sha256_file(args.environment_receipt),
        "timebaseSha256": sha256_file(args.timebase),
        "timebaseQcSha256": sha256_file(args.timebase_qc),
        "implementation": {"eventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v161.py")), "canonicalEntryPointGitBlob": git_blob_sha(Path(__file__))},
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "inputIdentities": {"mixSha256": sha256_file(args.mix), "guitarStemSha256": sha256_file(args.guitar), "bassStemSha256": sha256_file(args.bass), "drumsStemSha256": sha256_file(args.drums)},
        "environment": environment,
        "streamMetadata": {"combinedGuitar": guitar_meta, "bass": bass_meta},
        "safety": safety,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"candidateSha256": receipt["candidateSha256"], "counts": receipt["counts"], "timebaseQc": "PASS", "referenceRead": False, "scoreCalls": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
