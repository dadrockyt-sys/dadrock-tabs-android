#!/usr/bin/env python3
"""Deterministic V164 event/subdivision helpers with sealed local onset evidence.

The frozen V162 implementation is loaded by exact Git-blob identity only for
unaffected pure helpers. V164 reimplements every helper whose decision depends
on onset/subdivision normalization. No song, scorer, or reference I/O occurs.
"""
from __future__ import annotations

import hashlib
import importlib.util
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np

EPS = 1e-12
SR = 22050
HOP = 256
LOCAL_HALF_WINDOW_FRAMES = 32
SUPPORT_SCALE_QUANTILE = 0.95

SUBDIV_SEARCH_RADIUS_FRAMES = 3
SUBDIV_POSITIVE_QUANTILE = 0.55
SUBDIV_MOVE_MIN_RATIO = 1.05
EVENT_NON_NEAREST_MARGIN = 0.05

GUITAR_MAX_UNSUPPORTED_GAP_SECONDS = 0.120
GUITAR_REATTACK_RADIUS_FRAMES = 3
GUITAR_REATTACK_POSITIVE_QUANTILE = 0.60
GUITAR_REATTACK_MIN_SUPPORT = 0.30
GUITAR_RECOVERY_MIN_SUPPORT = 0.35
GUITAR_RECOVERY_POSITIVE_QUANTILE = 0.60
GUITAR_RECOVERY_EXISTING_ATTACK_SECONDS = 0.050
GUITAR_RECOVERY_MIN_PARENT_CONFIDENCE = 0.35
GUITAR_RECOVERY_MIN_TEMPLATE_RANK = 0.80
GUITAR_RECOVERY_MIN_SCORE = 0.58
GUITAR_RECOVERY_CAP = 3
GUITAR_POLYPHONY_CAP = 6

BASS_STATE_MIN_VOICED = 0.50
BASS_MEDIAN_WINDOW = 7
BASS_STATE_MIN_FRAMES = 4
BASS_BRIDGE_GAP_FRAMES = 2
BASS_STATE_CHANGE_SEMITONES = 1
BASS_STATE_MIN_MEDIAN_VOICED = 0.55
BASS_SILENCE_NEW_STATE_FRAMES = 6
BASS_STATE_LOOKUP_RADIUS_FRAMES = 4
BASS_ONSET_MIN_SUPPORT = 0.20
BASS_REATTACK_MIN_SUPPORT = 0.30
BASS_REATTACK_POSITIVE_QUANTILE = 0.60
BASS_REATTACK_MIN_IOI_SECONDS = 0.080
BASS_PROPOSAL_MERGE_SECONDS = 0.045
BASS_GRID_CAP = 1

_V162_EVENT_LOGIC_GIT_BLOB = "9f9b33fd8c210ad581025b454cf69b6999aa544b"
_V162_PATH = Path(__file__).resolve().parents[1] / "v162_cpu_autonomous" / "event_logic_v162.py"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


if not _V162_PATH.is_file() or _git_blob_sha(_V162_PATH) != _V162_EVENT_LOGIC_GIT_BLOB:
    raise RuntimeError("V164 frozen V162 event-logic dependency identity mismatch")
_spec = importlib.util.spec_from_file_location("_dadrock_v162_event_logic", _V162_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError("V164 could not load frozen V162 event logic")
_V162 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_V162)

# Pure unaffected V162 helpers are reused exactly from the pinned blob.
recovery_score = _V162.recovery_score
register_context_center = _V162.register_context_center
choose_sequence_register = _V162.choose_sequence_register
median_smooth_midi = _V162.median_smooth_midi
stable_bass_states = _V162.stable_bass_states
state_for_frame = _V162.state_for_frame
cap_grid = _V162.cap_grid
cap_guitar_polyphony = _V162.cap_guitar_polyphony
cap_bass_grid = _V162.cap_bass_grid


def _finite_env(env: np.ndarray) -> np.ndarray:
    x = np.asarray(env, dtype=float)
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("V164 onset envelope must be finite, one-dimensional, and nonempty")
    return x


def seconds_to_frames(seconds: float) -> int:
    return max(1, int(math.ceil(float(seconds) * SR / HOP)))


def frame_to_seconds(frame: int) -> float:
    return float(int(frame) * HOP / SR)


def seconds_to_nearest_frame(seconds: float, n_frames: int) -> int:
    if n_frames <= 0 or not math.isfinite(float(seconds)):
        raise RuntimeError("invalid frame conversion input")
    return int(np.clip(round(float(seconds) * SR / HOP), 0, n_frames - 1))


def local_window_bounds(center_frame: int, n_frames: int, half_window_frames: int = LOCAL_HALF_WINDOW_FRAMES) -> tuple[int, int]:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    if half_window_frames != LOCAL_HALF_WINDOW_FRAMES:
        raise RuntimeError("V164 local half-window is sealed at 32 frames")
    center = int(np.clip(int(center_frame), 0, n_frames - 1))
    return max(0, center - half_window_frames), min(n_frames - 1, center + half_window_frames)


def local_positive_population(
    env: np.ndarray,
    center_frame: int,
    half_window_frames: int = LOCAL_HALF_WINDOW_FRAMES,
) -> tuple[np.ndarray, dict[str, int]]:
    x = _finite_env(env)
    lo, hi = local_window_bounds(center_frame, len(x), half_window_frames)
    positive = x[lo : hi + 1]
    positive = positive[positive > 0.0]
    return positive, {"loFrame": lo, "hiFrame": hi, "positiveCount": int(positive.size)}


def local_positive_quantile(env: np.ndarray, center_frame: int, q: float) -> tuple[float | None, dict[str, int]]:
    if not 0.0 <= float(q) <= 1.0:
        raise RuntimeError("quantile must be in [0,1]")
    positive, provenance = local_positive_population(env, center_frame)
    return (None if positive.size == 0 else float(np.quantile(positive, float(q)))), provenance


def local_support_unit(value: float, env: np.ndarray, center_frame: int) -> tuple[float, dict[str, Any]]:
    if not math.isfinite(float(value)):
        raise RuntimeError("support value must be finite")
    positive, provenance = local_positive_population(env, center_frame)
    if positive.size == 0:
        return 0.0, {**provenance, "supportScale": None}
    scale = float(np.quantile(positive, SUPPORT_SCALE_QUANTILE))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0, {**provenance, "supportScale": scale}
    return float(np.clip(float(value) / scale, 0.0, 1.0)), {**provenance, "supportScale": scale}


def local_peak(env: np.ndarray, center: int, radius: int) -> tuple[int, float]:
    x = _finite_env(env)
    c = int(np.clip(int(center), 0, len(x) - 1))
    lo, hi = max(0, c - int(radius)), min(len(x) - 1, c + int(radius))
    peak = max(float(x[i]) for i in range(lo, hi + 1))
    frames = [i for i in range(lo, hi + 1) if abs(float(x[i]) - peak) <= EPS]
    return min(frames, key=lambda i: (abs(i - c), i)), peak


def onset_evidence(env: np.ndarray, center_frame: int, *, radius: int, positive_q: float) -> dict[str, Any]:
    x = _finite_env(env)
    peak_frame, peak = local_peak(x, center_frame, radius)
    threshold, threshold_prov = local_positive_quantile(x, center_frame, positive_q)
    support, support_prov = local_support_unit(peak, x, center_frame)
    for key in ("loFrame", "hiFrame", "positiveCount"):
        if threshold_prov[key] != support_prov[key]:
            raise RuntimeError("local normalization provenance mismatch")
    return {
        "centerFrame": int(np.clip(int(center_frame), 0, len(x) - 1)),
        "peakFrame": int(peak_frame),
        "peakStrength": float(peak),
        "positiveThreshold": threshold,
        "normalizedSupport": float(support),
        "normalizationLoFrame": int(support_prov["loFrame"]),
        "normalizationHiFrame": int(support_prov["hiFrame"]),
        "normalizationPositiveCount": int(support_prov["positiveCount"]),
        "normalizationSupportScale": support_prov["supportScale"],
    }


def supported_attack(
    env: np.ndarray,
    center_frame: int,
    *,
    radius: int,
    positive_q: float,
    minimum_support: float,
) -> tuple[bool, dict[str, Any]]:
    evidence = onset_evidence(env, center_frame, radius=radius, positive_q=positive_q)
    threshold = evidence["positiveThreshold"]
    supported = bool(
        threshold is not None
        and float(evidence["peakStrength"]) + EPS >= float(threshold)
        and float(evidence["normalizedSupport"]) + EPS >= float(minimum_support)
    )
    evidence["supported"] = supported
    return supported, evidence


def refine_onset_frame(env: np.ndarray, original_frame: int, radius: int) -> tuple[int, dict[str, Any]]:
    """V162 refinement rule with only the q60 population localized."""
    x = _finite_env(env)
    original = int(np.clip(int(original_frame), 0, len(x) - 1))
    peak_frame, peak = local_peak(x, original, radius)
    threshold, provenance = local_positive_quantile(x, original, 0.60)
    current = float(x[original])
    moved = bool(
        threshold is not None
        and peak + EPS >= float(threshold)
        and peak + EPS >= 1.10 * current
        and peak_frame != original
    )
    refined = int(peak_frame if moved else original)
    return refined, {
        "originalFrame": original,
        "selectedPeakFrame": int(peak_frame),
        "refinedFrame": refined,
        "searchRadiusFrames": int(radius),
        "currentOnsetStrength": current,
        "peakOnsetStrength": float(peak),
        "positiveQ60": threshold,
        "moved": moved,
        "normalizationLoFrame": provenance["loFrame"],
        "normalizationHiFrame": provenance["hiFrame"],
        "normalizationPositiveCount": provenance["positiveCount"],
    }


def segment_guitar_rows(rows: Iterable[Mapping[str, Any]], onset_env: np.ndarray) -> list[dict[str, Any]]:
    ordered = sorted(
        (dict(row) for row in rows),
        key=lambda r: (int(r["midi"]), float(r["startSeconds"]), float(r["endSeconds"])),
    )
    result: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for row in ordered:
        row.setdefault("segmentedRawCount", 1)
        if current is None:
            current = row
            continue
        if int(row["midi"]) != int(current["midi"]):
            result.append(current)
            current = row
            continue
        gap = float(row["startSeconds"]) - float(current["endSeconds"])
        should_merge = gap <= EPS
        attack_meta: dict[str, Any] | None = None
        if 0.0 < gap <= GUITAR_MAX_UNSUPPORTED_GAP_SECONDS + EPS:
            center = seconds_to_nearest_frame(float(row["startSeconds"]), len(onset_env))
            attack, attack_meta = supported_attack(
                onset_env,
                center,
                radius=GUITAR_REATTACK_RADIUS_FRAMES,
                positive_q=GUITAR_REATTACK_POSITIVE_QUANTILE,
                minimum_support=GUITAR_REATTACK_MIN_SUPPORT,
            )
            should_merge = not attack
        if should_merge:
            current["startSeconds"] = min(float(current["startSeconds"]), float(row["startSeconds"]))
            current["endSeconds"] = max(float(current["endSeconds"]), float(row["endSeconds"]))
            current["durationSeconds"] = max(0.0, float(current["endSeconds"]) - float(current["startSeconds"]))
            current["confidence"] = max(float(current.get("confidence", 0.0)), float(row.get("confidence", 0.0)))
            current["segmentedRawCount"] = int(current.get("segmentedRawCount", 1)) + int(row.get("segmentedRawCount", 1))
            current.setdefault("suppressedReattackChecks", []).append(attack_meta)
        else:
            if attack_meta is not None:
                row["reattackEvidence"] = attack_meta
            result.append(current)
            current = row
    if current is not None:
        result.append(current)
    for row in result:
        row.setdefault("durationSeconds", max(0.0, float(row["endSeconds"]) - float(row["startSeconds"])))
        row.setdefault("segmentedRawCount", 1)
    return sorted(result, key=lambda r: (float(r["startSeconds"]), int(r["midi"]), float(r["endSeconds"])))


def active_state_reattack_candidates(
    raw_rows: Iterable[Mapping[str, Any]],
    existing_attacks: Iterable[Mapping[str, Any]],
    onset_frames: Iterable[int],
    onset_env: np.ndarray,
    pitch_evidence: Mapping[tuple[int, int], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    raw = [dict(row) for row in raw_rows]
    attacks = [dict(row) for row in existing_attacks]
    out: list[dict[str, Any]] = []
    for frame in sorted(set(int(x) for x in onset_frames)):
        supported, attack_meta = supported_attack(
            onset_env,
            frame,
            radius=GUITAR_REATTACK_RADIUS_FRAMES,
            positive_q=GUITAR_RECOVERY_POSITIVE_QUANTILE,
            minimum_support=GUITAR_RECOVERY_MIN_SUPPORT,
        )
        if not supported:
            continue
        attack_seconds = frame_to_seconds(attack_meta["peakFrame"])
        if any(abs(float(row["startSeconds"]) - attack_seconds) <= GUITAR_RECOVERY_EXISTING_ATTACK_SECONDS + EPS for row in attacks):
            continue
        by_midi: dict[int, dict[str, Any]] = {}
        for row in raw:
            if not (float(row["startSeconds"]) - EPS <= attack_seconds <= float(row["endSeconds"]) + EPS):
                continue
            confidence = float(row.get("confidence", 0.0))
            if confidence + EPS < GUITAR_RECOVERY_MIN_PARENT_CONFIDENCE:
                continue
            midi = int(row["midi"])
            evidence = pitch_evidence.get((int(attack_meta["peakFrame"]), midi))
            if not isinstance(evidence, Mapping):
                continue
            rank = float(evidence.get("templateRank", 0.0))
            fundamental = bool(evidence.get("fundamentalPresent", False))
            if rank + EPS < GUITAR_RECOVERY_MIN_TEMPLATE_RANK or not fundamental:
                continue
            score = recovery_score(confidence, rank, float(attack_meta["normalizedSupport"]))
            if score + EPS < GUITAR_RECOVERY_MIN_SCORE:
                continue
            candidate = {
                "midi": midi,
                "startSeconds": attack_seconds,
                "parentConfidence": confidence,
                "templateRank": rank,
                "onsetSupport": float(attack_meta["normalizedSupport"]),
                "recoveryScore": score,
                "fundamentalPresent": True,
                "source": "basic_pitch_active_state_reattack",
                "recoveryOnsetFrame": int(attack_meta["peakFrame"]),
                "localNormalization": {
                    "loFrame": int(attack_meta["normalizationLoFrame"]),
                    "hiFrame": int(attack_meta["normalizationHiFrame"]),
                },
            }
            old = by_midi.get(midi)
            if old is None or (-score, -confidence, -rank, midi) < (
                -float(old["recoveryScore"]),
                -float(old["parentConfidence"]),
                -float(old["templateRank"]),
                int(old["midi"]),
            ):
                by_midi[midi] = candidate
        ranked = sorted(
            by_midi.values(),
            key=lambda r: (-float(r["recoveryScore"]), -float(r["parentConfidence"]), -float(r["templateRank"]), int(r["midi"])),
        )
        out.extend(ranked[:GUITAR_RECOVERY_CAP])
    return sorted(out, key=lambda r: (float(r["startSeconds"]), int(r["midi"])))


def bass_state_proposals(states: list[Mapping[str, Any]], onset_frames: Iterable[int], onset_env: np.ndarray) -> list[dict[str, Any]]:
    env = _finite_env(onset_env)
    proposals: list[dict[str, Any]] = []
    prior: Mapping[str, Any] | None = None
    for state in states:
        if prior is not None:
            gap = int(state["startFrame"]) - int(prior["endFrameExclusive"])
            changed = abs(int(state["midi"]) - int(prior["midi"])) >= BASS_STATE_CHANGE_SEMITONES
            new_after_silence = gap >= BASS_SILENCE_NEW_STATE_FRAMES
            if changed or new_after_silence:
                frame = int(state["startFrame"])
                support, prov = local_support_unit(float(env[min(frame, len(env) - 1)]), env, frame)
                proposals.append({
                    "frame": frame,
                    "kind": "state_change",
                    "midi": int(state["midi"]),
                    "onsetSupport": support,
                    "stateVoicedProbability": float(state["medianVoicedProbability"]),
                    "priority": 2,
                    "normalizationLoFrame": prov["loFrame"],
                    "normalizationHiFrame": prov["hiFrame"],
                })
        prior = state

    last_event_by_state: dict[tuple[int, int], int] = {}
    for frame in sorted(set(int(x) for x in onset_frames)):
        state = state_for_frame(states, frame)
        if state is None:
            continue
        peak_frame, peak = local_peak(env, frame, 3)
        support, prov = local_support_unit(peak, env, frame)
        if support + EPS < BASS_ONSET_MIN_SUPPORT:
            continue
        key = (int(state["startFrame"]), int(state["midi"]))
        kind, priority = "detected_onset", 0
        prior_frame = last_event_by_state.get(key)
        if prior_frame is not None:
            if frame_to_seconds(peak_frame - prior_frame) + EPS < BASS_REATTACK_MIN_IOI_SECONDS:
                continue
            threshold, _ = local_positive_quantile(env, frame, BASS_REATTACK_POSITIVE_QUANTILE)
            if threshold is None or peak + EPS < threshold or support + EPS < BASS_REATTACK_MIN_SUPPORT:
                continue
            kind, priority = "same_pitch_reattack", 1
        proposals.append({
            "frame": int(peak_frame),
            "kind": kind,
            "midi": int(state["midi"]),
            "onsetSupport": float(support),
            "stateVoicedProbability": float(state["medianVoicedProbability"]),
            "priority": priority,
            "normalizationLoFrame": prov["loFrame"],
            "normalizationHiFrame": prov["hiFrame"],
        })
        last_event_by_state[key] = int(peak_frame)

    merge_frames = seconds_to_frames(BASS_PROPOSAL_MERGE_SECONDS)
    ordered = sorted(proposals, key=lambda r: (int(r["frame"]), int(r["priority"]), -float(r["onsetSupport"])))
    groups: list[list[dict[str, Any]]] = []
    for row in ordered:
        if not groups or int(row["frame"]) - max(int(x["frame"]) for x in groups[-1]) > merge_frames:
            groups.append([row])
        else:
            groups[-1].append(row)
    out: list[dict[str, Any]] = []
    for group in groups:
        winner = min(
            group,
            key=lambda r: (int(r["priority"]), -float(r["onsetSupport"]), -float(r["stateVoicedProbability"]), int(r["frame"])),
        )
        item = dict(winner)
        item["mergedProposalCount"] = len(group)
        out.append(item)
    return sorted(out, key=lambda r: (int(r["frame"]), int(r["midi"])))


def beat_frame_bounds(beat_start: float, beat_end: float, n_frames: int) -> tuple[int, int]:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    if not math.isfinite(float(beat_start)) or not math.isfinite(float(beat_end)) or float(beat_end) <= float(beat_start):
        raise RuntimeError("invalid beat interval")
    lo = seconds_to_nearest_frame(float(beat_start), n_frames)
    hi = seconds_to_nearest_frame(float(beat_end), n_frames)
    if hi < lo:
        raise RuntimeError("beat frame bounds reversed")
    return lo, hi


def beat_positive_population(env: np.ndarray, beat_start: float, beat_end: float) -> tuple[np.ndarray, dict[str, int]]:
    x = _finite_env(env)
    lo, hi = beat_frame_bounds(beat_start, beat_end, len(x))
    positive = x[lo : hi + 1]
    positive = positive[positive > 0.0]
    return positive, {"loFrame": lo, "hiFrame": hi, "positiveCount": int(positive.size)}


def beat_positive_quantile(env: np.ndarray, beat_start: float, beat_end: float, q: float) -> tuple[float | None, dict[str, int]]:
    if not 0.0 <= float(q) <= 1.0:
        raise RuntimeError("quantile must be in [0,1]")
    positive, provenance = beat_positive_population(env, beat_start, beat_end)
    return (None if positive.size == 0 else float(np.quantile(positive, float(q)))), provenance


def beat_support_unit(value: float, env: np.ndarray, beat_start: float, beat_end: float) -> tuple[float, dict[str, Any]]:
    if not math.isfinite(float(value)):
        raise RuntimeError("support value must be finite")
    positive, provenance = beat_positive_population(env, beat_start, beat_end)
    if positive.size == 0:
        return 0.0, {**provenance, "supportScale": None}
    scale = float(np.quantile(positive, SUPPORT_SCALE_QUANTILE))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0, {**provenance, "supportScale": scale}
    return float(np.clip(float(value) / scale, 0.0, 1.0)), {**provenance, "supportScale": scale}


def refine_beat_subdivisions(beat_start: float, beat_end: float, shared_env: np.ndarray) -> list[dict[str, Any]]:
    x = _finite_env(shared_env)
    if beat_end <= beat_start:
        raise RuntimeError("invalid beat interval")
    period = float(beat_end - beat_start)
    nominal = [float(beat_start + j * period / 4.0) for j in range(5)]
    threshold, provenance = beat_positive_quantile(x, beat_start, beat_end, SUBDIV_POSITIVE_QUANTILE)
    out: list[dict[str, Any]] = [{
        "subdivision": 0, "nominalSeconds": nominal[0], "seconds": nominal[0], "moved": False,
        "normalizationLoFrame": provenance["loFrame"], "normalizationHiFrame": provenance["hiFrame"],
        "normalizationPositiveCount": provenance["positiveCount"],
    }]
    for j in (1, 2, 3):
        nominal_frame = seconds_to_nearest_frame(nominal[j], len(x))
        lo, hi = max(0, nominal_frame - SUBDIV_SEARCH_RADIUS_FRAMES), min(len(x) - 1, nominal_frame + SUBDIV_SEARCH_RADIUS_FRAMES)
        left_mid, right_mid = 0.5 * (nominal[j - 1] + nominal[j]), 0.5 * (nominal[j] + nominal[j + 1])
        candidates = [f for f in range(lo, hi + 1) if left_mid - EPS <= frame_to_seconds(f) <= right_mid + EPS]
        if not candidates:
            out.append({
                "subdivision": j, "nominalSeconds": nominal[j], "seconds": nominal[j], "moved": False,
                "normalizationLoFrame": provenance["loFrame"], "normalizationHiFrame": provenance["hiFrame"],
                "normalizationPositiveCount": provenance["positiveCount"],
            })
            continue
        peak = max(float(x[f]) for f in candidates)
        peak_frames = [f for f in candidates if abs(float(x[f]) - peak) <= EPS]
        selected = min(peak_frames, key=lambda f: (abs(f - nominal_frame), f))
        nominal_strength = float(x[nominal_frame])
        moved = bool(
            threshold is not None
            and peak + EPS >= float(threshold)
            and peak + EPS >= SUBDIV_MOVE_MIN_RATIO * nominal_strength
            and selected != nominal_frame
        )
        out.append({
            "subdivision": j,
            "nominalSeconds": nominal[j],
            "seconds": frame_to_seconds(selected) if moved else nominal[j],
            "moved": moved,
            "nominalFrame": nominal_frame,
            "selectedFrame": selected,
            "peakStrength": peak,
            "nominalStrength": nominal_strength,
            "positiveThreshold": threshold,
            "normalizationLoFrame": provenance["loFrame"],
            "normalizationHiFrame": provenance["hiFrame"],
            "normalizationPositiveCount": provenance["positiveCount"],
        })
    out.append({
        "subdivision": 4, "nominalSeconds": nominal[4], "seconds": nominal[4], "moved": False,
        "normalizationLoFrame": provenance["loFrame"], "normalizationHiFrame": provenance["hiFrame"],
        "normalizationPositiveCount": provenance["positiveCount"],
    })
    times = [float(row["seconds"]) for row in out]
    if not all(times[i + 1] > times[i] + EPS for i in range(len(times) - 1)):
        raise RuntimeError("refined subdivision interval is not strictly increasing")
    return out


def extrapolated_final_beat(beat_times: Iterable[float]) -> float:
    beats = np.asarray([float(x) for x in beat_times], dtype=float)
    if len(beats) < 2 or not np.all(np.isfinite(beats)) or not np.all(np.diff(beats) > 0.0):
        raise RuntimeError("invalid beat times for final extrapolation")
    period = float(np.median(np.diff(beats)[-min(8, len(beats) - 1) :]))
    if not math.isfinite(period) or period <= 0.0:
        raise RuntimeError("invalid final beat extrapolation period")
    return float(beats[-1] + period)


def build_subdivision_lattice(beat_times: Iterable[float], shared_env: np.ndarray) -> list[float]:
    beats = [float(x) for x in beat_times]
    if len(beats) < 2 or not all(math.isfinite(x) for x in beats) or not all(beats[i + 1] > beats[i] for i in range(len(beats) - 1)):
        raise RuntimeError("invalid beat times")
    extended = beats + [extrapolated_final_beat(beats)]
    lattice: list[float] = []
    for i in range(len(extended) - 1):
        interval = refine_beat_subdivisions(extended[i], extended[i + 1], shared_env)
        lattice.extend(float(row["seconds"]) for row in interval[:4])
    lattice.append(float(extended[-1]))
    if not all(lattice[i + 1] > lattice[i] + EPS for i in range(len(lattice) - 1)):
        raise RuntimeError("subdivision lattice not strictly increasing")
    return lattice


def event_step_score(event_time: float, step_time: float, nominal_substep: float, instrument_support: float, shared_support: float) -> float:
    temporal = float(np.clip(1.0 - abs(float(event_time) - float(step_time)) / (0.75 * float(nominal_substep)), 0.0, 1.0))
    return float(np.clip(0.70 * temporal + 0.20 * float(instrument_support) + 0.10 * float(shared_support), 0.0, 1.0))


def _candidate_beat_bounds(lattice: list[float], step: int) -> tuple[int, float, float]:
    if len(lattice) < 5 or (len(lattice) - 1) % 4 != 0:
        raise RuntimeError("V164 lattice must contain complete four-subdivision beats plus terminal endpoint")
    beat_count = (len(lattice) - 1) // 4
    beat = min(int(step) // 4, beat_count - 1)
    return beat, float(lattice[4 * beat]), float(lattice[4 * (beat + 1)])


def select_event_step(event_time: float, lattice: list[float], instrument_env: np.ndarray, shared_env: np.ndarray) -> tuple[int, dict[str, Any]]:
    inst_env, shr_env = _finite_env(instrument_env), _finite_env(shared_env)
    times = np.asarray(lattice, dtype=float)
    if len(times) < 5 or (len(times) - 1) % 4 != 0 or not np.all(np.isfinite(times)) or not np.all(np.diff(times) > 0.0):
        raise RuntimeError("invalid V164 lattice")
    nearest = int(np.argmin(np.abs(times - float(event_time))))
    candidates = [k for k in (nearest - 1, nearest, nearest + 1) if 0 <= k < len(times)]
    rows: list[dict[str, Any]] = []
    for k in candidates:
        if k == 0:
            nominal_sub = float(times[1] - times[0])
        elif k == len(times) - 1:
            nominal_sub = float(times[-1] - times[-2])
        else:
            nominal_sub = 0.5 * float(times[k + 1] - times[k - 1])
        beat_index, beat_start, beat_end = _candidate_beat_bounds(list(times), k)
        inst_frame = seconds_to_nearest_frame(float(times[k]), len(inst_env))
        shared_frame = seconds_to_nearest_frame(float(times[k]), len(shr_env))
        inst_support, inst_prov = beat_support_unit(float(inst_env[inst_frame]), inst_env, beat_start, beat_end)
        shared_support, shared_prov = beat_support_unit(float(shr_env[shared_frame]), shr_env, beat_start, beat_end)
        rows.append({
            "step": k,
            "score": event_step_score(event_time, float(times[k]), nominal_sub, inst_support, shared_support),
            "instrumentSupport": inst_support,
            "sharedSupport": shared_support,
            "time": float(times[k]),
            "normalizationBeatIndex": beat_index,
            "instrumentNormalizationLoFrame": inst_prov["loFrame"],
            "instrumentNormalizationHiFrame": inst_prov["hiFrame"],
            "sharedNormalizationLoFrame": shared_prov["loFrame"],
            "sharedNormalizationHiFrame": shared_prov["hiFrame"],
        })
    nearest_row = next(row for row in rows if int(row["step"]) == nearest)
    winner = sorted(rows, key=lambda r: (-float(r["score"]), abs(int(r["step"]) - nearest), int(r["step"])))[0]
    if int(winner["step"]) != nearest and float(winner["score"]) + EPS < float(nearest_row["score"]) + EVENT_NON_NEAREST_MARGIN:
        winner = nearest_row
    return int(winner["step"]), {"nearestStep": nearest, "winner": dict(winner), "candidates": rows}
