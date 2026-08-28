#!/usr/bin/env python3
"""Pure deterministic V162 segmentation/subdivision helpers for song-blind tests."""
from __future__ import annotations

import math
from typing import Any, Iterable, Mapping

import numpy as np

EPS = 1e-12
SR = 22050
HOP = 256

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
REGISTER_CONTEXT_WINDOW_SECONDS = 0.75
REGISTER_MIN_RANK_GAIN = 0.15
REGISTER_MIN_CONTEXT_DISTANCE_GAIN = 3.0
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


def seconds_to_frames(seconds: float) -> int:
    return max(1, int(math.ceil(float(seconds) * SR / HOP)))


def frame_to_seconds(frame: int) -> float:
    return float(int(frame) * HOP / SR)


def seconds_to_nearest_frame(seconds: float, n_frames: int) -> int:
    if n_frames <= 0:
        raise RuntimeError("n_frames must be positive")
    return int(np.clip(round(float(seconds) * SR / HOP), 0, n_frames - 1))


def positive_quantile(values: np.ndarray, q: float) -> float | None:
    x = np.asarray(values, dtype=float)
    positive = x[np.isfinite(x) & (x > 0.0)]
    if positive.size == 0:
        return None
    return float(np.quantile(positive, float(q)))


def support_unit(value: float, population: np.ndarray) -> float:
    x = np.asarray(population, dtype=float)
    positive = x[np.isfinite(x) & (x > 0.0)]
    if positive.size == 0:
        return 0.0
    scale = float(np.quantile(positive, 0.95))
    if not math.isfinite(scale) or scale <= EPS:
        return 0.0
    return float(np.clip(float(value) / scale, 0.0, 1.0))


def local_peak(env: np.ndarray, center: int, radius: int) -> tuple[int, float]:
    x = np.asarray(env, dtype=float)
    if x.size == 0 or not np.all(np.isfinite(x)):
        raise RuntimeError("local_peak requires finite nonempty envelope")
    c = int(np.clip(int(center), 0, len(x) - 1))
    lo = max(0, c - int(radius))
    hi = min(len(x) - 1, c + int(radius))
    peak = max(float(x[i]) for i in range(lo, hi + 1))
    frames = [i for i in range(lo, hi + 1) if abs(float(x[i]) - peak) <= EPS]
    frame = min(frames, key=lambda i: (abs(i - c), i))
    return frame, peak


def supported_attack(
    env: np.ndarray,
    center_frame: int,
    *,
    radius: int,
    positive_q: float,
    minimum_support: float,
) -> tuple[bool, dict[str, Any]]:
    peak_frame, peak = local_peak(env, center_frame, radius)
    threshold = positive_quantile(env, positive_q)
    support = support_unit(peak, env)
    supported = bool(
        threshold is not None
        and peak + EPS >= threshold
        and support + EPS >= float(minimum_support)
    )
    return supported, {
        "centerFrame": int(center_frame),
        "peakFrame": int(peak_frame),
        "peakStrength": float(peak),
        "positiveThreshold": threshold,
        "normalizedSupport": float(support),
        "supported": supported,
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
        same_midi = int(row["midi"]) == int(current["midi"])
        if not same_midi:
            result.append(current)
            current = row
            continue
        gap = float(row["startSeconds"]) - float(current["endSeconds"])
        should_merge = gap <= 0.0 + EPS
        attack_meta: dict[str, Any] | None = None
        if gap > 0.0 and gap <= GUITAR_MAX_UNSUPPORTED_GAP_SECONDS + EPS:
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


def recovery_score(parent_confidence: float, template_rank: float, onset_support: float) -> float:
    values = [parent_confidence, template_rank, onset_support]
    if not all(math.isfinite(float(v)) for v in values):
        raise RuntimeError("nonfinite recovery score input")
    return float(np.clip(0.50 * parent_confidence + 0.30 * template_rank + 0.20 * onset_support, 0.0, 1.0))


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
            }
            old = by_midi.get(midi)
            if old is None or (-score, -confidence, -rank, midi) < (
                -float(old["recoveryScore"]), -float(old["parentConfidence"]), -float(old["templateRank"]), int(old["midi"])
            ):
                by_midi[midi] = candidate
        ranked = sorted(
            by_midi.values(),
            key=lambda r: (-float(r["recoveryScore"]), -float(r["parentConfidence"]), -float(r["templateRank"]), int(r["midi"])),
        )
        out.extend(ranked[:GUITAR_RECOVERY_CAP])
    return sorted(out, key=lambda r: (float(r["startSeconds"]), int(r["midi"])))


def register_context_center(rows: list[Mapping[str, Any]], index: int) -> float | None:
    row = rows[index]
    midi = int(row["midi"])
    t = float(row["startSeconds"])
    pitch_class = midi % 12
    prior: tuple[float, int] | None = None
    nxt: tuple[float, int] | None = None
    for j, other in enumerate(rows):
        if j == index or int(other["midi"]) % 12 != pitch_class:
            continue
        dt = float(other["startSeconds"]) - t
        if abs(dt) > REGISTER_CONTEXT_WINDOW_SECONDS + EPS:
            continue
        if dt < 0 and (prior is None or dt > prior[0]):
            prior = (dt, int(other["midi"]))
        if dt > 0 and (nxt is None or dt < nxt[0]):
            nxt = (dt, int(other["midi"]))
    neighbors = [m for pair in (prior, nxt) if pair is not None for m in [pair[1]]]
    if not neighbors:
        return None
    return float(np.median(np.asarray(neighbors, dtype=float)))


def choose_sequence_register(
    rows: list[Mapping[str, Any]],
    index: int,
    template_ranks: Mapping[int, float],
    fundamental_present: Mapping[int, bool],
    midi_min: int = 40,
    midi_max: int = 88,
) -> tuple[int, dict[str, Any]]:
    raw = int(rows[index]["midi"])
    raw_rank = float(template_ranks[raw])
    context = register_context_center(rows, index)
    if context is None:
        return raw, {"rawMidi": raw, "contextCenter": None, "repaired": False, "reason": "NO_CONTEXT"}
    eligible: list[tuple[int, float, float, float]] = []
    raw_distance = abs(raw - context)
    for midi in [raw] + [m for m in (raw - 12, raw + 12) if midi_min <= m <= midi_max]:
        rank = float(template_ranks[midi])
        distance = abs(midi - context)
        continuity = float(np.clip(1.0 - distance / 12.0, 0.0, 1.0))
        seq = 0.65 * rank + 0.35 * continuity
        if midi == raw:
            eligible.append((midi, rank, continuity, seq))
            continue
        if not bool(fundamental_present.get(midi, False)):
            continue
        if rank + EPS < raw_rank + REGISTER_MIN_RANK_GAIN:
            continue
        if raw_distance - distance + EPS < REGISTER_MIN_CONTEXT_DISTANCE_GAIN:
            continue
        eligible.append((midi, rank, continuity, seq))
    ranked = sorted(eligible, key=lambda x: (0 if x[0] == raw else 1, -x[3], x[0]))
    raw_entry = next(x for x in eligible if x[0] == raw)
    alternatives = [x for x in eligible if x[0] != raw]
    chosen = raw_entry if not alternatives else max(alternatives, key=lambda x: (x[3], -x[0]))
    if alternatives and chosen[3] <= raw_entry[3] + EPS:
        chosen = raw_entry
    return int(chosen[0]), {
        "rawMidi": raw,
        "contextCenter": context,
        "rawTemplateRank": raw_rank,
        "chosenTemplateRank": float(chosen[1]),
        "chosenContinuity": float(chosen[2]),
        "chosenSequenceScore": float(chosen[3]),
        "repaired": bool(chosen[0] != raw),
        "reason": "SEQUENCE_ELIGIBLE" if chosen[0] != raw else "RAW_PREFERRED",
    }


def refine_beat_subdivisions(beat_start: float, beat_end: float, shared_env: np.ndarray) -> list[dict[str, Any]]:
    if not math.isfinite(beat_start) or not math.isfinite(beat_end) or beat_end <= beat_start:
        raise RuntimeError("invalid beat interval")
    env = np.asarray(shared_env, dtype=float)
    if env.size == 0 or not np.all(np.isfinite(env)):
        raise RuntimeError("invalid shared onset envelope")
    period = beat_end - beat_start
    nominal = [beat_start + j * period / 4.0 for j in range(5)]
    threshold = positive_quantile(env, SUBDIV_POSITIVE_QUANTILE)
    out: list[dict[str, Any]] = [{"subdivision": 0, "nominalSeconds": nominal[0], "seconds": nominal[0], "moved": False}]
    for j in (1, 2, 3):
        nominal_frame = seconds_to_nearest_frame(nominal[j], len(env))
        lo = max(0, nominal_frame - SUBDIV_SEARCH_RADIUS_FRAMES)
        hi = min(len(env) - 1, nominal_frame + SUBDIV_SEARCH_RADIUS_FRAMES)
        left_mid = 0.5 * (nominal[j - 1] + nominal[j])
        right_mid = 0.5 * (nominal[j] + nominal[j + 1])
        candidates: list[int] = []
        for frame in range(lo, hi + 1):
            sec = frame_to_seconds(frame)
            if left_mid - EPS <= sec <= right_mid + EPS:
                candidates.append(frame)
        if not candidates:
            out.append({"subdivision": j, "nominalSeconds": nominal[j], "seconds": nominal[j], "moved": False})
            continue
        peak = max(float(env[f]) for f in candidates)
        peak_frames = [f for f in candidates if abs(float(env[f]) - peak) <= EPS]
        selected = min(peak_frames, key=lambda f: (abs(f - nominal_frame), f))
        nominal_strength = float(env[nominal_frame])
        moved = bool(
            threshold is not None
            and peak + EPS >= threshold
            and peak + EPS >= SUBDIV_MOVE_MIN_RATIO * nominal_strength
            and selected != nominal_frame
        )
        seconds = frame_to_seconds(selected) if moved else nominal[j]
        out.append({
            "subdivision": j,
            "nominalSeconds": nominal[j],
            "seconds": seconds,
            "moved": moved,
            "nominalFrame": nominal_frame,
            "selectedFrame": selected,
            "peakStrength": peak,
            "nominalStrength": nominal_strength,
        })
    out.append({"subdivision": 4, "nominalSeconds": nominal[4], "seconds": nominal[4], "moved": False})
    times = [float(row["seconds"]) for row in out]
    if not all(times[i + 1] > times[i] + EPS for i in range(len(times) - 1)):
        raise RuntimeError("refined subdivision interval is not strictly increasing")
    return out


def build_subdivision_lattice(beat_times: Iterable[float], shared_env: np.ndarray) -> list[float]:
    beats = [float(x) for x in beat_times]
    if len(beats) < 2 or not all(math.isfinite(x) for x in beats) or not all(beats[i + 1] > beats[i] for i in range(len(beats) - 1)):
        raise RuntimeError("invalid beat times")
    lattice: list[float] = []
    for i in range(len(beats) - 1):
        interval = refine_beat_subdivisions(beats[i], beats[i + 1], shared_env)
        lattice.extend(float(row["seconds"]) for row in interval[:4])
    lattice.append(beats[-1])
    if not all(lattice[i + 1] > lattice[i] + EPS for i in range(len(lattice) - 1)):
        raise RuntimeError("subdivision lattice not strictly increasing")
    return lattice


def event_step_score(event_time: float, step_time: float, nominal_substep: float, instrument_support: float, shared_support: float) -> float:
    temporal = float(np.clip(1.0 - abs(float(event_time) - float(step_time)) / (0.75 * float(nominal_substep)), 0.0, 1.0))
    return float(np.clip(0.70 * temporal + 0.20 * instrument_support + 0.10 * shared_support, 0.0, 1.0))


def select_event_step(event_time: float, lattice: list[float], instrument_env: np.ndarray, shared_env: np.ndarray) -> tuple[int, dict[str, Any]]:
    if len(lattice) < 2:
        raise RuntimeError("lattice too short")
    times = np.asarray(lattice, dtype=float)
    if not np.all(np.isfinite(times)) or not np.all(np.diff(times) > 0.0):
        raise RuntimeError("invalid lattice")
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
        frame = seconds_to_nearest_frame(float(times[k]), min(len(instrument_env), len(shared_env)))
        inst = support_unit(float(instrument_env[frame]), instrument_env)
        shared = support_unit(float(shared_env[frame]), shared_env)
        score = event_step_score(event_time, float(times[k]), nominal_sub, inst, shared)
        rows.append({"step": k, "score": score, "instrumentSupport": inst, "sharedSupport": shared, "time": float(times[k])})
    nearest_row = next(row for row in rows if int(row["step"]) == nearest)
    winner = sorted(rows, key=lambda r: (-float(r["score"]), abs(int(r["step"]) - nearest), int(r["step"])))[0]
    if int(winner["step"]) != nearest and float(winner["score"]) + EPS < float(nearest_row["score"]) + EVENT_NON_NEAREST_MARGIN:
        winner = nearest_row
    return int(winner["step"]), {"nearestStep": nearest, "winner": dict(winner), "candidates": rows}


def median_smooth_midi(midi: np.ndarray, window: int = BASS_MEDIAN_WINDOW) -> np.ndarray:
    x = np.asarray(midi, dtype=float)
    if window != BASS_MEDIAN_WINDOW:
        raise RuntimeError("V162 Bass median window is sealed at 7")
    out = np.full_like(x, np.nan, dtype=float)
    radius = window // 2
    for i in range(len(x)):
        lo = max(0, i - radius)
        hi = min(len(x), i + radius + 1)
        finite = x[lo:hi][np.isfinite(x[lo:hi])]
        if finite.size:
            out[i] = float(np.median(finite))
    return out


def stable_bass_states(smoothed_midi: np.ndarray, voiced_prob: np.ndarray) -> list[dict[str, Any]]:
    midi = np.asarray(smoothed_midi, dtype=float)
    vp = np.asarray(voiced_prob, dtype=float)
    if midi.shape != vp.shape:
        raise RuntimeError("Bass MIDI/voiced arrays must align")
    labels: list[int | None] = []
    for m, v in zip(midi, vp):
        if math.isfinite(float(m)) and math.isfinite(float(v)) and float(v) + EPS >= BASS_STATE_MIN_VOICED:
            labels.append(int(round(float(m))))
        else:
            labels.append(None)
    # Bridge only short gaps surrounded by the same finite MIDI state.
    i = 0
    while i < len(labels):
        if labels[i] is not None:
            i += 1
            continue
        start = i
        while i < len(labels) and labels[i] is None:
            i += 1
        end = i
        gap = end - start
        left = labels[start - 1] if start > 0 else None
        right = labels[end] if end < len(labels) else None
        if gap <= BASS_BRIDGE_GAP_FRAMES and left is not None and left == right:
            for j in range(start, end):
                labels[j] = left
    raw_runs: list[dict[str, Any]] = []
    i = 0
    while i < len(labels):
        if labels[i] is None:
            i += 1
            continue
        start = i
        state = int(labels[i])
        while i < len(labels) and labels[i] == state:
            i += 1
        end = i
        if end - start < BASS_STATE_MIN_FRAMES:
            continue
        finite_vp = vp[start:end][np.isfinite(vp[start:end])]
        median_vp = float(np.median(finite_vp)) if finite_vp.size else 0.0
        if median_vp + EPS < BASS_STATE_MIN_MEDIAN_VOICED:
            continue
        raw_runs.append({"midi": state, "startFrame": start, "endFrameExclusive": end, "frameCount": end - start, "medianVoicedProbability": median_vp})
    return raw_runs


def state_for_frame(states: list[Mapping[str, Any]], frame: int, radius: int = BASS_STATE_LOOKUP_RADIUS_FRAMES) -> Mapping[str, Any] | None:
    f = int(frame)
    containing = [state for state in states if int(state["startFrame"]) <= f < int(state["endFrameExclusive"])]
    if containing:
        return containing[0]
    candidates: list[tuple[int, Mapping[str, Any]]] = []
    for state in states:
        distance = min(abs(f - int(state["startFrame"])), abs(f - (int(state["endFrameExclusive"]) - 1)))
        if distance <= radius:
            candidates.append((distance, state))
    if not candidates:
        return None
    return min(candidates, key=lambda x: (x[0], int(x[1]["startFrame"]), int(x[1]["midi"])))[1]


def bass_state_proposals(states: list[Mapping[str, Any]], onset_frames: Iterable[int], onset_env: np.ndarray) -> list[dict[str, Any]]:
    env = np.asarray(onset_env, dtype=float)
    threshold = positive_quantile(env, BASS_REATTACK_POSITIVE_QUANTILE)
    proposals: list[dict[str, Any]] = []
    # State-change starts are independent of detected onset.
    prior: Mapping[str, Any] | None = None
    for state in states:
        if prior is None:
            prior = state
            continue
        gap = int(state["startFrame"]) - int(prior["endFrameExclusive"])
        changed = abs(int(state["midi"]) - int(prior["midi"])) >= BASS_STATE_CHANGE_SEMITONES
        new_after_silence = gap >= BASS_SILENCE_NEW_STATE_FRAMES
        if changed or new_after_silence:
            frame = int(state["startFrame"])
            proposals.append({
                "frame": frame,
                "kind": "state_change",
                "midi": int(state["midi"]),
                "onsetSupport": support_unit(float(env[min(frame, len(env) - 1)]), env),
                "stateVoicedProbability": float(state["medianVoicedProbability"]),
                "priority": 2,
            })
        prior = state
    last_event_by_state: dict[tuple[int, int], int] = {}
    for frame in sorted(set(int(x) for x in onset_frames)):
        state = state_for_frame(states, frame)
        if state is None:
            continue
        peak_frame, peak = local_peak(env, frame, 3)
        support = support_unit(peak, env)
        if support + EPS < BASS_ONSET_MIN_SUPPORT:
            continue
        key = (int(state["startFrame"]), int(state["midi"]))
        kind = "detected_onset"
        priority = 0
        prior_frame = last_event_by_state.get(key)
        if prior_frame is not None:
            if frame_to_seconds(peak_frame - prior_frame) + EPS < BASS_REATTACK_MIN_IOI_SECONDS:
                continue
            if threshold is None or peak + EPS < threshold or support + EPS < BASS_REATTACK_MIN_SUPPORT:
                continue
            kind = "same_pitch_reattack"
            priority = 1
        proposals.append({
            "frame": int(peak_frame),
            "kind": kind,
            "midi": int(state["midi"]),
            "onsetSupport": float(support),
            "stateVoicedProbability": float(state["medianVoicedProbability"]),
            "priority": priority,
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


def cap_grid(rows: Iterable[Mapping[str, Any]], *, cap: int, bass: bool = False) -> list[dict[str, Any]]:
    by_step: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_step.setdefault(int(row["absoluteGridStep"]), []).append(dict(row))
    out: list[dict[str, Any]] = []
    for step in sorted(by_step):
        if bass:
            ranked = sorted(by_step[step], key=lambda r: (-float(r.get("admissionScore", 0.0)), -float(r.get("medianPyinVoicedProbability", 0.0)), int(r["midi"])))
        else:
            ranked = sorted(by_step[step], key=lambda r: (-float(r.get("admissionScore", r.get("recoveryScore", 0.0))), -float(r.get("confidence", r.get("parentConfidence", 0.0))), int(r["midi"])))
        out.extend(ranked[:cap])
    return sorted(out, key=lambda r: (int(r["absoluteGridStep"]), int(r["midi"])))


def cap_guitar_polyphony(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return cap_grid(rows, cap=GUITAR_POLYPHONY_CAP, bass=False)


def cap_bass_grid(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return cap_grid(rows, cap=BASS_GRID_CAP, bass=True)
