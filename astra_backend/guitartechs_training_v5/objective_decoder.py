from __future__ import annotations

import math
from collections import Counter

import numpy as np
import torch
import torch.nn.functional as F

from guitartechs_training_v5.model import (
    MAX_MIDI,
    MIN_MIDI,
    NUM_CLASSES,
    NUM_FRETS,
    NUM_PITCHES,
    NUM_STRINGS,
    OPEN_MIDI,
    SILENCE_CLASS,
)

MASK = -100
PRIMARY_CONTENT = ("chords", "scales", "singlenotes", "PalmMute")

STATE_ACTIVE_WEIGHT = 1.15
ONSET_POS_WEIGHT = 2.0
ACTIVITY_POS_WEIGHT = 1.20
PITCH_POS_WEIGHT = 3.0
CONTINUITY_LAMBDA = 0.05
IDENTITY_LAMBDA = 0.25
IDENTITY_MARGIN = 0.15
CONTENT_WEIGHT_MIN = 0.75
CONTENT_WEIGHT_MAX = 1.50
TASK_LOG_VAR_MIN = -2.0
TASK_LOG_VAR_MAX = 2.0

ONSET_START_CONFIDENCE = 0.50
ACTIVITY_START_CONFIDENCE = 0.50
STATE_START_CONFIDENCE = 0.30
STATE_START_VS_SILENCE_RATIO = 0.70
ACTIVITY_CONTINUE_CONFIDENCE = 0.45
STATE_CONTINUE_CONFIDENCE = 0.20
STATE_CONTINUE_VS_SILENCE_RATIO = 0.60
GAP_FRAMES = 2
MIN_RUN_FRAMES = 2


def bounded_content_weights(category_counts: dict[str, int]) -> dict[str, float]:
    if set(category_counts) != set(PRIMARY_CONTENT):
        raise ValueError("all four primary content classes are required")
    if any((not isinstance(v, int)) or v <= 0 for v in category_counts.values()):
        raise ValueError("content counts must be positive integers")
    mean_count = sum(category_counts.values()) / len(PRIMARY_CONTENT)
    raw = {name: math.sqrt(mean_count / category_counts[name]) for name in PRIMARY_CONTENT}
    clipped = {
        name: min(CONTENT_WEIGHT_MAX, max(CONTENT_WEIGHT_MIN, raw[name]))
        for name in PRIMARY_CONTENT
    }
    weighted_mean = (
        sum(clipped[name] * category_counts[name] for name in PRIMARY_CONTENT)
        / sum(category_counts.values())
    )
    return {
        name: min(
            CONTENT_WEIGHT_MAX,
            max(CONTENT_WEIGHT_MIN, clipped[name] / weighted_mean),
        )
        for name in PRIMARY_CONTENT
    }


def normalized_targets(labels: torch.Tensor) -> torch.Tensor:
    if labels.ndim != 3 or labels.shape[1] != NUM_STRINGS:
        raise ValueError("labels must be B x 6 x T")
    target = labels.transpose(1, 2).contiguous().clone()
    target[target == -1] = SILENCE_CLASS
    invalid = (target != MASK) & ((target < 0) | (target >= NUM_CLASSES))
    if torch.any(invalid):
        raise ValueError("labels contain an invalid class")
    return target


def auxiliary_targets(labels: torch.Tensor):
    target = normalized_targets(labels)
    valid = target != MASK
    active = valid & (target != SILENCE_CLASS)

    activity_target = active.to(torch.float32)
    activity_valid = valid

    onset_target = torch.zeros_like(activity_target)
    onset_valid = torch.zeros_like(valid)
    if target.shape[1] > 1:
        prev_valid = valid[:, :-1, :]
        now_valid = valid[:, 1:, :]
        onset_valid[:, 1:, :] = prev_valid & now_valid
        prev_active = active[:, :-1, :]
        now_active = active[:, 1:, :]
        changed = target[:, 1:, :] != target[:, :-1, :]
        onset_target[:, 1:, :] = (now_active & (~prev_active | changed)).to(torch.float32)

    pitch_target = torch.zeros(
        (target.shape[0], target.shape[1], NUM_PITCHES),
        dtype=torch.float32,
        device=target.device,
    )
    pitch_valid = valid.all(dim=-1)
    for string in range(NUM_STRINGS):
        fret = target[:, :, string]
        active_string = (fret >= 0) & (fret < NUM_FRETS) & pitch_valid
        if torch.any(active_string):
            midi = OPEN_MIDI[string] + fret[active_string]
            pitch_index = midi - MIN_MIDI
            rows = active_string.nonzero(as_tuple=False)
            pitch_target[rows[:, 0], rows[:, 1], pitch_index.long()] = 1.0

    return {
        "state": target,
        "valid": valid,
        "active": active,
        "onsetTarget": onset_target,
        "onsetValid": onset_valid,
        "activityTarget": activity_target,
        "activityValid": activity_valid,
        "pitchTarget": pitch_target,
        "pitchValid": pitch_valid,
    }


def _masked_bce(logits, target, valid, pos_weight: float):
    if not torch.any(valid):
        return logits.new_tensor(0.0)
    weight = torch.tensor(pos_weight, device=logits.device, dtype=logits.dtype)
    raw = F.binary_cross_entropy_with_logits(
        logits,
        target.to(logits.dtype),
        pos_weight=weight,
        reduction="none",
    )
    return raw[valid].mean()


def _pitch_bce(logits, target, valid):
    if not torch.any(valid):
        return logits.new_tensor(0.0)
    weight = torch.full(
        (NUM_PITCHES,),
        PITCH_POS_WEIGHT,
        device=logits.device,
        dtype=logits.dtype,
    )
    raw = F.binary_cross_entropy_with_logits(
        logits,
        target.to(logits.dtype),
        pos_weight=weight,
        reduction="none",
    )
    return raw[valid].mean()


def _continuity_loss(probs: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    valid_now = target[:, 1:, :] != MASK
    valid_prev = target[:, :-1, :] != MASK
    stable = valid_now & valid_prev & (target[:, 1:, :] == target[:, :-1, :])
    if not torch.any(stable):
        return probs.new_tensor(0.0)
    delta = (probs[:, 1:, :, :] - probs[:, :-1, :, :]).pow(2).mean(dim=-1)
    return delta[stable].mean()


def _identity_margin_loss(probs: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    losses = []
    batch, frames, strings = target.shape
    for b in range(batch):
        for t in range(frames):
            for string in range(strings):
                fret = int(target[b, t, string].item())
                if fret == MASK or fret == SILENCE_CLASS:
                    continue
                target_pitch = OPEN_MIDI[string] + fret
                correct = probs[b, t, string, fret]
                for alt_string in range(NUM_STRINGS):
                    if alt_string == string:
                        continue
                    alt_fret = target_pitch - OPEN_MIDI[alt_string]
                    if 0 <= alt_fret < NUM_FRETS:
                        alt_target = int(target[b, t, alt_string].item())
                        if alt_target == MASK or alt_target == alt_fret:
                            continue
                        alt = probs[b, t, alt_string, alt_fret]
                        losses.append(F.relu(IDENTITY_MARGIN + alt - correct))
    if not losses:
        return probs.new_tensor(0.0)
    return torch.stack(losses).mean()


def v5_sequence_loss(outputs: dict[str, torch.Tensor], labels: torch.Tensor, *, content_weight: float = 1.0):
    required = {"tablature", "onset", "activity", "pitch", "taskLogVars"}
    if not required.issubset(outputs):
        raise ValueError("V5 outputs missing required heads")
    if not (CONTENT_WEIGHT_MIN <= content_weight <= CONTENT_WEIGHT_MAX):
        raise ValueError("content_weight outside frozen bounds")

    target_info = auxiliary_targets(labels)
    target = target_info["state"]
    batch, frames, strings = target.shape

    state_logits = outputs["tablature"]
    if state_logits.shape != (batch, frames, NUM_STRINGS * NUM_CLASSES):
        raise ValueError("unexpected V5 tablature output shape")
    if outputs["onset"].shape != (batch, frames, NUM_STRINGS):
        raise ValueError("unexpected V5 onset output shape")
    if outputs["activity"].shape != (batch, frames, NUM_STRINGS):
        raise ValueError("unexpected V5 activity output shape")
    if outputs["pitch"].shape != (batch, frames, NUM_PITCHES):
        raise ValueError("unexpected V5 pitch output shape")

    x = state_logits.reshape(batch, frames, NUM_STRINGS, NUM_CLASSES)
    flat = F.cross_entropy(
        x.reshape(-1, NUM_CLASSES),
        target.reshape(-1),
        ignore_index=MASK,
        reduction="none",
    ).reshape(batch, frames, NUM_STRINGS)
    valid = target_info["valid"]
    active = target_info["active"]
    token_weight = torch.ones_like(flat)
    token_weight[active] = STATE_ACTIVE_WEIGHT
    token_weight = token_weight * valid
    state_loss = (flat * token_weight).sum() / token_weight.sum().clamp(min=1.0)

    onset_loss = _masked_bce(
        outputs["onset"],
        target_info["onsetTarget"],
        target_info["onsetValid"],
        ONSET_POS_WEIGHT,
    )
    activity_loss = _masked_bce(
        outputs["activity"],
        target_info["activityTarget"],
        target_info["activityValid"],
        ACTIVITY_POS_WEIGHT,
    )
    pitch_loss = _pitch_bce(
        outputs["pitch"],
        target_info["pitchTarget"],
        target_info["pitchValid"],
    )

    log_vars = outputs["taskLogVars"]
    if log_vars.shape != (4,):
        raise ValueError("taskLogVars must contain four task weights")
    bounded_log_vars = torch.clamp(log_vars, TASK_LOG_VAR_MIN, TASK_LOG_VAR_MAX)
    task_losses = torch.stack((state_loss, onset_loss, activity_loss, pitch_loss))
    multitask = torch.mean(torch.exp(-bounded_log_vars) * task_losses + bounded_log_vars)

    probs = F.softmax(x, dim=-1)
    continuity = _continuity_loss(probs, target)
    identity = _identity_margin_loss(probs, target)
    total = content_weight * (
        multitask
        + CONTINUITY_LAMBDA * continuity
        + IDENTITY_LAMBDA * identity
    )
    return total, {
        "state": state_loss,
        "onset": onset_loss,
        "activity": activity_loss,
        "pitch": pitch_loss,
        "continuity": continuity,
        "identityMargin": identity,
        "taskLogVars": bounded_log_vars,
        "contentWeight": float(content_weight),
    }


def _runs(states: np.ndarray):
    runs = []
    start = 0
    while start < len(states):
        value = int(states[start])
        end = start + 1
        while end < len(states) and int(states[end]) == value:
            end += 1
        runs.append((start, end, value))
        start = end
    return runs


def _merge_short_gaps(states: np.ndarray, max_gap: int):
    out = states.copy()
    if max_gap <= 0:
        return out
    changed = True
    while changed:
        changed = False
        runs = _runs(out)
        for i in range(1, len(runs) - 1):
            start, end, value = runs[i]
            left = runs[i - 1]
            right = runs[i + 1]
            if value == -1 and end - start <= max_gap and left[2] >= 0 and left[2] == right[2]:
                out[start:end] = left[2]
                changed = True
                break
    return out


def _prune_short_active_runs(states: np.ndarray, min_run: int):
    out = states.copy()
    for start, end, value in _runs(out):
        if value >= 0 and end - start < min_run:
            out[start:end] = -1
    return out


def decode_multitask(
    state_probabilities,
    onset_probabilities,
    activity_probabilities,
    *,
    onset_start_confidence: float = ONSET_START_CONFIDENCE,
    activity_start_confidence: float = ACTIVITY_START_CONFIDENCE,
    state_start_confidence: float = STATE_START_CONFIDENCE,
    activity_continue_confidence: float = ACTIVITY_CONTINUE_CONFIDENCE,
    state_continue_confidence: float = STATE_CONTINUE_CONFIDENCE,
    gap_frames: int = GAP_FRAMES,
    min_run_frames: int = MIN_RUN_FRAMES,
):
    state = np.asarray(state_probabilities, dtype=np.float64)
    onset = np.asarray(onset_probabilities, dtype=np.float64)
    activity = np.asarray(activity_probabilities, dtype=np.float64)
    if state.ndim != 3 or state.shape[1:] != (NUM_STRINGS, NUM_CLASSES):
        raise ValueError("state probabilities must be T x 6 x 21")
    if onset.shape != state.shape[:2] or activity.shape != state.shape[:2]:
        raise ValueError("auxiliary probabilities must be T x 6")
    if np.any(~np.isfinite(state)) or np.any(~np.isfinite(onset)) or np.any(~np.isfinite(activity)):
        raise ValueError("probabilities must be finite")
    if np.any(onset < 0) or np.any(onset > 1) or np.any(activity < 0) or np.any(activity > 1):
        raise ValueError("auxiliary probabilities must be within [0,1]")
    if np.any(state < 0) or not np.allclose(state.sum(axis=-1), 1.0, atol=1e-5):
        raise ValueError("state probabilities must be normalized")

    frames = state.shape[0]
    decoded = np.full((frames, NUM_STRINGS), -1, dtype=np.int16)
    for string in range(NUM_STRINGS):
        current = -1
        for frame in range(frames):
            row = state[frame, string]
            silence = float(row[SILENCE_CLASS])
            best_fret = int(np.argmax(row[:NUM_FRETS]))
            best_active = float(row[best_fret])
            onset_ok = float(onset[frame, string]) >= onset_start_confidence
            activity_start_ok = float(activity[frame, string]) >= activity_start_confidence

            can_start = (
                onset_ok
                and activity_start_ok
                and best_active >= state_start_confidence
                and best_active >= silence * STATE_START_VS_SILENCE_RATIO
            )

            if current >= 0:
                if can_start and best_fret != current:
                    current = best_fret
                    decoded[frame, string] = current
                    continue
                keep = float(row[current])
                if (
                    float(activity[frame, string]) >= activity_continue_confidence
                    and keep >= state_continue_confidence
                    and keep >= silence * STATE_CONTINUE_VS_SILENCE_RATIO
                ):
                    decoded[frame, string] = current
                    continue
                current = -1

            if can_start:
                current = best_fret
                decoded[frame, string] = current

        merged = _merge_short_gaps(decoded[:, string], gap_frames)
        decoded[:, string] = _prune_short_active_runs(merged, min_run_frames)

    return decoded


def count_active_runs(states) -> int:
    arr = np.asarray(states)
    if arr.ndim != 2 or arr.shape[1] != NUM_STRINGS:
        raise ValueError("states must be T x 6")
    return sum(
        1
        for string in range(NUM_STRINGS)
        for _, _, value in _runs(arr[:, string])
        if value >= 0
    )


def content_counts_from_categories(categories) -> dict[str, int]:
    normalized = ["PalmMute" if c == "techniques" else c for c in categories]
    counts = Counter(normalized)
    if set(counts) != set(PRIMARY_CONTENT):
        raise ValueError("categories must cover all primary content classes")
    return {name: int(counts[name]) for name in PRIMARY_CONTENT}
