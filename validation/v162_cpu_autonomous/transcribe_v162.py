#!/usr/bin/env python3
"""Sealed V162 CPU transcriber consuming an independently validated subdivision timebase."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from event_logic_v162 import (
    active_state_reattack_candidates,
    bass_state_proposals,
    cap_bass_grid,
    cap_guitar_polyphony,
    choose_sequence_register,
    local_peak,
    median_smooth_midi,
    segment_guitar_rows,
    select_event_step,
    stable_bass_states,
    support_unit,
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

CANDIDATE_SCHEMA = "dadrock.tabs.v162.cpu-state-segmented-generated.v1"
RECEIPT_SCHEMA = "dadrock.tabs.v162.cpu-generation-receipt.v1"
TIMEBASE_SCHEMA = "dadrock.tabs.v162.reference-blind-subdivision-timebase.v1"
TIMEBASE_QC_SCHEMA = "dadrock.tabs.v162.reference-blind-subdivision-timebase-qc.v1"
PRE_RUN_SCHEMA = "dadrock.tabs.v162.pre-run-identity-receipt.v1"
ENV_SCHEMA = "dadrock.tabs.v162.cpu-environment-receipt.v1"


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


def positive_unit_scale(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    x = np.maximum(x, 0.0)
    peak = float(np.max(x)) if x.size else 0.0
    if not math.isfinite(peak) or peak <= EPS:
        raise RuntimeError("unit-scale envelope lacks positive evidence")
    return x / peak


def shared_onset_env(mix: np.ndarray, drums: np.ndarray) -> np.ndarray:
    mix_env = onset_env(mix)
    drums_env = onset_env(drums)
    n = min(len(mix_env), len(drums_env))
    if n == 0:
        raise RuntimeError("empty shared onset envelope")
    return 0.65 * positive_unit_scale(drums_env[:n]) + 0.35 * positive_unit_scale(mix_env[:n])


def z_across_candidates(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    std = float(np.std(x))
    if not math.isfinite(std) or std < 1e-9:
        return np.zeros_like(x)
    return (x - float(np.mean(x))) / std


def template_rank(scores: np.ndarray, selected_index: int) -> float:
    x = np.asarray(scores, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("template_rank requires finite scores")
    idx = int(selected_index)
    if not 0 <= idx < len(x):
        raise RuntimeError("template_rank index out of bounds")
    selected = float(x[idx])
    return float(np.count_nonzero(x <= selected + EPS) / len(x))


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


def positive_quantile(values: np.ndarray, q: float) -> float | None:
    x = np.asarray(values, dtype=float)
    positive = x[np.isfinite(x) & (x > 0.0)]
    return None if positive.size == 0 else float(np.quantile(positive, q))


def refine_onset_frame(env: np.ndarray, original_frame: int, radius: int) -> tuple[int, dict[str, Any]]:
    x = np.asarray(env, dtype=float)
    original = int(np.clip(int(original_frame), 0, len(x) - 1))
    lo = max(0, original - int(radius))
    hi = min(len(x) - 1, original + int(radius))
    threshold = positive_quantile(x, 0.60)
    current = float(x[original])
    peak = max(float(x[i]) for i in range(lo, hi + 1))
    peaks = [i for i in range(lo, hi + 1) if abs(float(x[i]) - peak) <= EPS]
    selected = min(peaks, key=lambda i: (abs(i - original), i))
    moved = bool(threshold is not None and peak + EPS >= threshold and peak + EPS >= 1.10 * current and selected != original)
    refined = selected if moved else original
    return refined, {
        "originalFrame": original,
        "selectedPeakFrame": selected,
        "refinedFrame": refined,
        "searchRadiusFrames": int(radius),
        "currentOnsetStrength": current,
        "peakOnsetStrength": peak,
        "positiveQ60": threshold,
        "moved": moved,
    }


def collapse_onsets(frames: np.ndarray, min_seconds: float) -> list[int]:
    min_frames = max(1, int(math.ceil(float(min_seconds) * SR / HOP)))
    out: list[int] = []
    for frame in sorted(set(int(x) for x in frames)):
        if not out or frame - out[-1] >= min_frames:
            out.append(frame)
    return out


def guitar_admission_score(confidence: float, rank: float, onset: float, persistence: float, activity: float) -> float:
    return float(np.clip(0.45 * confidence + 0.25 * rank + 0.15 * onset + 0.10 * persistence + 0.05 * activity, 0.0, 1.0))


def bass_admission_score(voiced: float, rank: float, onset: float, activity: float) -> float:
    return float(np.clip(0.40 * voiced + 0.35 * rank + 0.15 * onset + 0.10 * activity, 0.0, 1.0))


def guitar_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], np.ndarray]:
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

    segmented = segment_guitar_rows(raw, env)
    admitted: list[dict[str, Any]] = []
    rejected_score = 0
    rejected_activity = 0
    refined_count = 0
    register_repairs = 0
    no_context_count = 0

    for index, row in enumerate(segmented):
        original_start = float(row["startSeconds"])
        duration = max(0.0, float(row["endSeconds"]) - original_start)
        original_frame = int(np.clip(round(original_start * SR / HOP), 0, cqt.shape[1] - 1))
        refined_frame, refine_meta = refine_onset_frame(env, original_frame, 6)
        refined_count += int(refine_meta["moved"])
        scores, fundamentals = three_frame_template(cqt, freqs, refined_frame, GUITAR_RANGE[0], GUITAR_RANGE[1])
        raw_midi = int(row["midi"])
        candidate_midis = [raw_midi] + [m for m in (raw_midi - 12, raw_midi + 12) if GUITAR_RANGE[0] <= m <= GUITAR_RANGE[1]]
        rank_map = {m: template_rank(scores, m - GUITAR_RANGE[0]) for m in candidate_midis}
        med_fund = float(np.median(fundamentals))
        fund_map = {m: bool(fundamentals[m - GUITAR_RANGE[0]] > med_fund) for m in candidate_midis}
        chosen, register_meta = choose_sequence_register(segmented, index, rank_map, fund_map, GUITAR_RANGE[0], GUITAR_RANGE[1])
        register_repairs += int(register_meta["repaired"])
        no_context_count += int(register_meta["reason"] == "NO_CONTEXT")
        chosen_offset = chosen - GUITAR_RANGE[0]
        rank = template_rank(scores, chosen_offset)
        onset_support = support_unit(float(env[min(refined_frame, len(env) - 1)]), env)
        activity_support = support_unit(float(rms[int(np.clip(refined_frame, 0, len(rms) - 1))]), rms)
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
            "source": "basic_pitch_segmented",
            "basicPitchOriginalMidi": raw_midi,
            "registerRepaired": bool(register_meta["repaired"]),
            "registerContext": register_meta,
            "templateScore": float(scores[chosen_offset]),
            "templateRank": rank,
            "fundamentalPresent": bool(fundamentals[chosen_offset] > med_fund),
            "onsetSupport": onset_support,
            "activitySupport": activity_support,
            "persistenceSupport": persistence,
            "admissionScore": admission,
            "segmentedRawCount": int(row.get("segmentedRawCount", 1)),
            "reattackEvidence": row.get("reattackEvidence"),
            "originalStartSeconds": original_start,
            "originalOnsetFrame": original_frame,
            "refinedOnsetFrame": refined_frame,
            "onsetRefined": bool(refine_meta["moved"]),
            "onsetRefinement": refine_meta,
        })

    independent = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=False, units="frames"), dtype=int)
    independent = np.asarray(collapse_onsets(independent, 0.040), dtype=int)
    pitch_evidence: dict[tuple[int, int], dict[str, Any]] = {}
    peak_frames: set[int] = set()
    for frame in independent:
        peak_frame, _peak = local_peak(env, int(frame), 3)
        peak_frames.add(int(peak_frame))
    for frame in sorted(peak_frames):
        scores, fundamentals = three_frame_template(cqt, freqs, frame, GUITAR_RANGE[0], GUITAR_RANGE[1])
        med_fund = float(np.median(fundamentals))
        seconds = float(librosa.frames_to_time(frame, sr=SR, hop_length=HOP))
        active_midis = sorted({int(row["midi"]) for row in raw if float(row["startSeconds"]) - EPS <= seconds <= float(row["endSeconds"]) + EPS})
        for midi in active_midis:
            offset = midi - GUITAR_RANGE[0]
            pitch_evidence[(frame, midi)] = {
                "templateRank": template_rank(scores, offset),
                "fundamentalPresent": bool(fundamentals[offset] > med_fund),
            }
    recovered = active_state_reattack_candidates(raw, segmented, independent.tolist(), env, pitch_evidence)
    for row in recovered:
        midi = int(row["midi"])
        start = float(row["startSeconds"])
        parent_ends = [float(parent["endSeconds"]) for parent in raw if int(parent["midi"]) == midi and float(parent["startSeconds"]) - EPS <= start <= float(parent["endSeconds"]) + EPS]
        end = max(parent_ends) if parent_ends else start
        item = dict(row)
        item.update({
            "endSeconds": end,
            "durationSeconds": max(0.0, end - start),
            "confidence": float(row["parentConfidence"]),
            "activitySupport": support_unit(float(rms[int(np.clip(round(start * SR / HOP), 0, len(rms) - 1))]), rms),
            "admissionScore": float(row["recoveryScore"]),
            "registerRepaired": False,
            "registerContext": {"rawMidi": midi, "contextCenter": None, "repaired": False, "reason": "ACTIVE_PARENT_REGISTER"},
        })
        admitted.append(item)

    admitted.sort(key=lambda r: (float(r["startSeconds"]), int(r["midi"]), str(r["source"])))
    return admitted, {
        "inputSha256": sha256_file(path),
        "basicPitchVersion": importlib.metadata.version("basic-pitch"),
        "basicPitchModelSha256": sha256_file(Path(ICASSP_2022_MODEL_PATH)),
        "basicPitchRawEventCount": len(raw),
        "segmentedCandidateCount": len(segmented),
        "segmentedAdmittedCount": len(admitted) - len(recovered),
        "activeStateRecoveredCount": len(recovered),
        "eventCountBeforeGridDedupe": len(admitted),
        "registerRepairCount": register_repairs,
        "registerNoContextCount": no_context_count,
        "onsetRefinedCount": refined_count,
        "rejectedByAdmissionScore": rejected_score,
        "rejectedByActivity": rejected_activity,
        "independentOnsetCount": len(independent),
        "standaloneHarmonicPitchDiscoveryEnabled": False,
    }, env


def bass_events(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], np.ndarray]:
    import librosa
    y = load_mono(path)
    env = onset_env(y)
    rms = rms_env(y)
    raw_onsets = np.asarray(librosa.onset.onset_detect(onset_envelope=env, sr=SR, hop_length=HOP, backtrack=True, units="frames"), dtype=int)
    retained_onsets = collapse_onsets(raw_onsets, 0.035)
    harmonic, _ = librosa.effects.hpss(y)
    f0, _flag, voiced_prob = librosa.pyin(
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
    states = stable_bass_states(smoothed, voiced_prob)
    proposals = bass_state_proposals(states, retained_onsets, env)
    cqt, freqs = harmonic_cqt(y, BASS_RANGE[0], BASS_RANGE[1])
    half_frames = max(1, int(round((0.120 / 2.0) * SR / HOP)))
    admitted: list[dict[str, Any]] = []
    refined_count = rejected_score = rejected_activity = rejected_additional = 0
    proposal_counts = {"detected_onset": 0, "same_pitch_reattack": 0, "state_change": 0}
    for index, proposal in enumerate(proposals):
        proposal_counts[str(proposal["kind"])] += 1
        original_frame = int(proposal["frame"])
        refined_frame, refine_meta = refine_onset_frame(env, original_frame, 8)
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
        best_offset = int(np.where(np.abs(combined - best_value) <= EPS)[0][0])
        midi = BASS_RANGE[0] + best_offset
        rank = template_rank(combined, best_offset)
        fundamental_present = bool(fundamentals[best_offset] > float(np.median(fundamentals)))
        onset_support = support_unit(float(env[min(refined_frame, len(env) - 1)]), env)
        activity_support = support_unit(float(rms[int(np.clip(refined_frame, 0, len(rms) - 1))]), rms)
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
        source_map = {
            "detected_onset": "bass_detected_onset_state",
            "same_pitch_reattack": "bass_same_pitch_reattack_state",
            "state_change": "bass_state_change",
        }
        admitted.append({
            "midi": int(midi),
            "startSeconds": start,
            "endSeconds": start + 0.5,
            "durationSeconds": 0.5,
            "source": source_map[str(proposal["kind"])],
            "proposalKind": str(proposal["kind"]),
            "proposalIndex": index,
            "mergedProposalCount": int(proposal["mergedProposalCount"]),
            "stateMidi": int(proposal["midi"]),
            "stateVoicedProbability": float(proposal["stateVoicedProbability"]),
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
    admitted.sort(key=lambda r: (float(r["startSeconds"]), int(r["midi"])))
    for i, row in enumerate(admitted):
        start = float(row["startSeconds"])
        next_start = float(admitted[i + 1]["startSeconds"]) if i + 1 < len(admitted) else start + 0.5
        end = min(next_start, start + 0.5)
        row["endSeconds"] = end
        row["durationSeconds"] = max(0.0, end - start)
    return admitted, {
        "inputSha256": sha256_file(path),
        "detectedOnsetCount": len(raw_onsets),
        "retainedOnsetCount": len(retained_onsets),
        "stablePitchStateCount": len(states),
        "mergedProposalCount": len(proposals),
        "detectedOnsetProposalCount": proposal_counts["detected_onset"],
        "samePitchReattackProposalCount": proposal_counts["same_pitch_reattack"],
        "stateChangeProposalCount": proposal_counts["state_change"],
        "admittedEventCountBeforeGridDedupe": len(admitted),
        "onsetRefinedCount": refined_count,
        "rejectedByAdmissionScore": rejected_score,
        "rejectedByActivity": rejected_activity,
        "rejectedByAdditionalGate": rejected_additional,
    }, env


def map_events(events: list[dict[str, Any]], lattice: list[float], instrument_env: np.ndarray, shared_env: np.ndarray, stream: str) -> tuple[list[dict[str, Any]], int, int]:
    if len(lattice) < 2:
        raise RuntimeError("V162 frozen subdivision lattice too short")
    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    pregrid = corrected = 0
    first_half = 0.5 * float(lattice[1] - lattice[0])
    for row in events:
        event_time = float(row["startSeconds"])
        if event_time < float(lattice[0]) - first_half:
            pregrid += 1
            continue
        step, selection = select_event_step(event_time, lattice, instrument_env, shared_env)
        nearest = int(selection["nearestStep"])
        corrected += int(step != nearest)
        item = dict(row)
        item.update({
            "absoluteGridStep": int(step),
            "measure": int(step) // 16 + 1,
            "step": int(step) % 16,
            "stream": stream,
            "nearestLatticeStep": nearest,
            "selectedLatticeTimeSeconds": float(lattice[step]),
            "gridCorrectionSteps": int(step - nearest),
            "stepSelection": selection,
        })
        key = (int(step), int(item["midi"]))
        old = mapped.get(key)
        if old is None:
            mapped[key] = item
        else:
            new_evidence = float(item.get("admissionScore", item.get("recoveryScore", 0.0)))
            old_evidence = float(old.get("admissionScore", old.get("recoveryScore", 0.0)))
            new_conf = float(item.get("confidence", item.get("medianPyinVoicedProbability", 0.0)))
            old_conf = float(old.get("confidence", old.get("medianPyinVoicedProbability", 0.0)))
            if (-new_evidence, -new_conf, int(item["midi"])) < (-old_evidence, -old_conf, int(old["midi"])):
                mapped[key] = item
    rows = list(mapped.values())
    rows = cap_guitar_polyphony(rows) if stream == "combinedGuitar" else cap_bass_grid(rows)
    return rows, pregrid, corrected


def validate_runtime_boundary(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    prereg = load_json(args.preregistration)
    contract = load_json(args.implementation_contract)
    timebase = load_json(args.timebase)
    qc = load_json(args.timebase_qc)
    pre_run = load_json(args.pre_run_receipt)
    environment = load_json(args.environment_receipt)
    if prereg.get("version") != "V162" or prereg.get("status") != "PREREGISTERED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V162 preregistration state invalid")
    if contract.get("version") != "V162" or contract.get("status") != "SEALED_BEFORE_IMPLEMENTATION_CODE":
        raise RuntimeError("V162 implementation-contract state invalid")
    schemas = contract.get("canonicalSchemas", {})
    if timebase.get("schema") != TIMEBASE_SCHEMA or schemas.get("timebase") != TIMEBASE_SCHEMA:
        raise RuntimeError("V162 timebase schema invalid")
    if schemas.get("candidate") != CANDIDATE_SCHEMA or schemas.get("generationReceipt") != RECEIPT_SCHEMA:
        raise RuntimeError("V162 candidate/generation schema contract drift")
    if qc.get("schema") != TIMEBASE_QC_SCHEMA or schemas.get("timebaseQc") != TIMEBASE_QC_SCHEMA or qc.get("validation") != "PASS":
        raise RuntimeError("V162 timebase QC is not frozen PASS")
    if qc.get("timebaseSha256") != sha256_file(args.timebase):
        raise RuntimeError("V162 timebase differs from PASS QC receipt")
    if pre_run.get("schema") != PRE_RUN_SCHEMA or pre_run.get("validation") != "PASS":
        raise RuntimeError("V162 pre-run identity receipt invalid")
    if environment.get("schema") != ENV_SCHEMA or environment.get("validation") != "PASS" or environment.get("device") != "cpu":
        raise RuntimeError("V162 environment receipt invalid")
    if environment.get("cudaAvailable") is not False or environment.get("torchCudaVersion") is not None:
        raise RuntimeError("V162 environment is not CPU-only")
    pins = pre_run.get("pinnedGitBlobs") or {}
    expected = {
        "preregistration": git_blob_sha(args.preregistration),
        "implementationContract": git_blob_sha(args.implementation_contract),
        "eventLogic": git_blob_sha(Path(__file__).with_name("event_logic_v162.py")),
        "transcriber": git_blob_sha(Path(__file__)),
    }
    for key, value in expected.items():
        if pins.get(key) != value:
            raise RuntimeError(f"V162 pre-run pin drift: {key}")
    for key in ("timebaseMustNotExistAtSeal", "timebaseQcReceiptMustNotExistAtSeal", "candidateMustNotExistAtSeal", "generationReceiptMustNotExistAtSeal"):
        if pre_run.get(key) is not True:
            raise RuntimeError(f"V162 pre-run absence boundary invalid: {key}")
    if pre_run.get("referenceReadAtSeal") is not False or pre_run.get("professionalReferencePathsOpenedAtSeal") != 0 or pre_run.get("V161CandidateReadAtSeal") is not False:
        raise RuntimeError("V162 pre-run reference/predecessor boundary invalid")
    safety = timebase.get("safety") or {}
    if not (safety.get("referenceRead") is False and safety.get("professionalReferencePathsOpened") == 0 and safety.get("priorGeneratedCandidateRead") is False and safety.get("priorScoreRead") is False and safety.get("V161CandidateRead") is False and safety.get("gpu") is False):
        raise RuntimeError("V162 timebase safety boundary invalid")
    for name, path in {"guitar": args.guitar, "bass": args.bass, "drums": args.drums}.items():
        record = (timebase.get("stemIdentities") or {}).get(name) or {}
        if record.get("sha256") != sha256_file(path) or record.get("bytes") != path.stat().st_size:
            raise RuntimeError(f"V162 {name} stem differs from frozen timebase")
    mix_record = (timebase.get("audioIdentity") or {}).get("normalizedMix") or {}
    if mix_record.get("sha256") != sha256_file(args.mix) or mix_record.get("bytes") != args.mix.stat().st_size:
        raise RuntimeError("V162 normalized mix differs from frozen timebase")
    subdivisions = np.asarray(timebase.get("subdivisionTimesSeconds", []), dtype=float)
    steps = np.asarray(timebase.get("subdivisionAbsoluteSteps", []), dtype=int)
    if len(subdivisions) < 2 or len(subdivisions) != len(steps) or not np.all(np.isfinite(subdivisions)) or not np.all(np.diff(subdivisions) > 0.0) or not np.array_equal(steps, np.arange(len(steps), dtype=int)):
        raise RuntimeError("V162 frozen subdivision lattice invalid")
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
        raise RuntimeError("V162 candidate/generation receipt is write-once")
    for path in (args.mix, args.guitar, args.bass, args.drums, args.timebase, args.timebase_qc, args.preregistration, args.implementation_contract, args.pre_run_receipt, args.environment_receipt):
        if not path.is_file():
            raise RuntimeError(f"missing V162 transcriber input: {path}")

    _prereg, _contract, timebase, environment = validate_runtime_boundary(args)
    lattice = [float(x) for x in timebase["subdivisionTimesSeconds"]]
    mix_y = load_mono(args.mix)
    drums_y = load_mono(args.drums)
    shared_env = shared_onset_env(mix_y, drums_y)

    # HARD BOUNDARY: all pitch inference begins only after exact independent timebase-QC PASS above.
    bass_raw, bass_meta, bass_env = bass_events(args.bass)
    guitar_raw, guitar_meta, guitar_env = guitar_events(args.guitar)
    guitar, guitar_pre, guitar_corrected = map_events(guitar_raw, lattice, guitar_env, shared_env, "combinedGuitar")
    bass, bass_pre, bass_corrected = map_events(bass_raw, lattice, bass_env, shared_env, "bass")
    if not guitar or not bass:
        raise RuntimeError("V162 generated empty required stream")

    safety = {
        "referenceRead": False,
        "professionalReferencePathsOpened": 0,
        "referenceFacingScoreCalls": 0,
        "priorGeneratedCandidateRead": False,
        "priorScoreRead": False,
        "V161CandidateRead": False,
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
        "classification": "single-preregistered-reference-blind-v162-cpu-state-segmented-subdivision-candidate",
        "streams": {"combinedGuitar": guitar, "bass": bass},
        "timebaseIdentity": {
            "path": str(args.timebase),
            "sha256": sha256_file(args.timebase),
            "schema": timebase.get("schema"),
            "timebaseQcPath": str(args.timebase_qc),
            "timebaseQcSha256": sha256_file(args.timebase_qc),
            "selectedPhase": timebase.get("selectedPhase"),
            "subdivisionCount": len(lattice),
        },
        "streamMetadata": {
            "combinedGuitar": {**guitar_meta, "finalEventCount": len(guitar), "preGridExcluded": guitar_pre, "evidenceStepCorrectionCount": guitar_corrected},
            "bass": {**bass_meta, "finalEventCount": len(bass), "preGridExcluded": bass_pre, "evidenceStepCorrectionCount": bass_corrected},
        },
        "sealedInputs": {
            "preregistrationGitBlob": git_blob_sha(args.preregistration),
            "implementationContractGitBlob": git_blob_sha(args.implementation_contract),
            "eventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v162.py")),
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
        "version": "V162",
        "validation": "PENDING_INDEPENDENT_STRUCTURAL_QC",
        "candidatePath": str(args.output),
        "candidateSha256": sha256_file(args.output),
        "preregistrationSha256": sha256_file(args.preregistration),
        "implementationContractSha256": sha256_file(args.implementation_contract),
        "preRunReceiptSha256": sha256_file(args.pre_run_receipt),
        "environmentReceiptSha256": sha256_file(args.environment_receipt),
        "timebaseSha256": sha256_file(args.timebase),
        "timebaseQcSha256": sha256_file(args.timebase_qc),
        "implementation": {"canonicalEntryPointGitBlob": git_blob_sha(Path(__file__)), "eventLogicGitBlob": git_blob_sha(Path(__file__).with_name("event_logic_v162.py"))},
        "counts": {"combinedGuitar": len(guitar), "bass": len(bass)},
        "preGridExcluded": {"combinedGuitar": guitar_pre, "bass": bass_pre},
        "evidenceStepCorrections": {"combinedGuitar": guitar_corrected, "bass": bass_corrected},
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
    args.receipt.write_text(json.dumps(receipt, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"candidateSha256": receipt["candidateSha256"], "counts": receipt["counts"], "timebaseQc": "PASS", "referenceRead": False, "scoreCalls": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
