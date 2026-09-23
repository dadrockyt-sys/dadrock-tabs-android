from __future__ import annotations

import math
from collections import Counter

import numpy as np
import torch
import torch.nn.functional as F

MASK = -100
NUM_STRINGS = 6
NUM_FRETS = 20
NUM_CLASSES = 21
SILENCE_CLASS = 20
OPEN_MIDI = (40, 45, 50, 55, 59, 64)
PRIMARY_CONTENT = ("chords", "scales", "singlenotes", "PalmMute")

ACTIVE_WEIGHT = 1.20
CONTINUITY_LAMBDA = 0.10
IDENTITY_LAMBDA = 0.25
IDENTITY_MARGIN = 0.15
CONTENT_WEIGHT_MIN = 0.75
CONTENT_WEIGHT_MAX = 1.50

DECODER_START_CONFIDENCE = 0.55
DECODER_CONTINUE_CONFIDENCE = 0.35
DECODER_GAP_FRAMES = 2
DECODER_MIN_RUN_FRAMES = 2


def _validate_logits_labels(logits: torch.Tensor, labels: torch.Tensor):
    if labels.ndim != 3 or labels.shape[1] != NUM_STRINGS:
        raise ValueError("labels must be B x 6 x T")
    batch, _, frames = labels.shape
    if logits.shape != (batch, frames, NUM_STRINGS * NUM_CLASSES):
        raise ValueError("unexpected TabCNN output shape")
    return batch, frames


def normalized_targets(labels: torch.Tensor) -> torch.Tensor:
    target = labels.transpose(1, 2).contiguous().clone()
    target[target == -1] = SILENCE_CLASS
    invalid = (target != MASK) & ((target < 0) | (target >= NUM_CLASSES))
    if torch.any(invalid):
        raise ValueError("labels contain an invalid class")
    return target


def bounded_content_weights(category_counts: dict[str, int]) -> dict[str, float]:
    if set(category_counts) != set(PRIMARY_CONTENT):
        raise ValueError("all four primary content classes are required")
    if any((not isinstance(v, int)) or v <= 0 for v in category_counts.values()):
        raise ValueError("content counts must be positive integers")

    mean_count = sum(category_counts.values()) / len(PRIMARY_CONTENT)
    raw = {
        name: math.sqrt(mean_count / category_counts[name])
        for name in PRIMARY_CONTENT
    }
    clipped = {
        name: min(CONTENT_WEIGHT_MAX, max(CONTENT_WEIGHT_MIN, raw[name]))
        for name in PRIMARY_CONTENT
    }
    weighted_mean = (
        sum(clipped[name] * category_counts[name] for name in PRIMARY_CONTENT)
        / sum(category_counts.values())
    )
    normalized = {
        name: min(
            CONTENT_WEIGHT_MAX,
            max(CONTENT_WEIGHT_MIN, clipped[name] / weighted_mean),
        )
        for name in PRIMARY_CONTENT
    }
    return normalized


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
                if not 0 <= fret < NUM_FRETS:
                    raise ValueError("active fret outside supported range")
                target_pitch = OPEN_MIDI[string] + fret
                correct = probs[b, t, string, fret]
                for alt_string in range(NUM_STRINGS):
                    if alt_string == string:
                        continue
                    alt_fret = target_pitch - OPEN_MIDI[alt_string]
                    if 0 <= alt_fret < NUM_FRETS:
                        alt = probs[b, t, alt_string, alt_fret]
                        losses.append(F.relu(IDENTITY_MARGIN + alt - correct))
    if not losses:
        return probs.new_tensor(0.0)
    return torch.stack(losses).mean()


def v3_sequence_loss(
    logits: torch.Tensor,
    labels: torch.Tensor,
    *,
    content_weight: float = 1.0,
    active_weight: float = ACTIVE_WEIGHT,
    continuity_lambda: float = CONTINUITY_LAMBDA,
    identity_lambda: float = IDENTITY_LAMBDA,
):
    _validate_logits_labels(logits, labels)
    if not (CONTENT_WEIGHT_MIN <= content_weight <= CONTENT_WEIGHT_MAX):
        raise ValueError("content_weight outside frozen V3 bounds")
    if active_weight < 1.0:
        raise ValueError("active_weight must not downweight active supervision")
    if continuity_lambda < 0 or identity_lambda < 0:
        raise ValueError("auxiliary loss weights must be nonnegative")

    batch, frames, _ = labels.shape
    x = logits.reshape(batch, frames, NUM_STRINGS, NUM_CLASSES)
    target = normalized_targets(labels)
    flat = F.cross_entropy(
        x.reshape(-1, NUM_CLASSES),
        target.reshape(-1),
        ignore_index=MASK,
        reduction="none",
    ).reshape(batch, frames, NUM_STRINGS)

    valid = target != MASK
    active = valid & (target != SILENCE_CLASS)
    token_weight = torch.ones_like(flat)
    token_weight[active] = active_weight
    token_weight = token_weight * valid
    denom = token_weight.sum().clamp(min=1.0)
    base_ce = (flat * token_weight).sum() / denom

    probs = F.softmax(x, dim=-1)
    continuity = _continuity_loss(probs, target)
    identity = _identity_margin_loss(probs, target)
    total = content_weight * (
        base_ce
        + continuity_lambda * continuity
        + identity_lambda * identity
    )
    return total, {
        "baseCrossEntropy": base_ce,
        "continuity": continuity,
        "identityMargin": identity,
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
    if max_gap <= 0:
        return states
    out = states.copy()
    changed = True
    while changed:
        changed = False
        runs = _runs(out)
        for i in range(1, len(runs) - 1):
            start, end, value = runs[i]
            left = runs[i - 1]
            right = runs[i + 1]
            if (
                value == -1
                and end - start <= max_gap
                and left[2] >= 0
                and left[2] == right[2]
            ):
                out[start:end] = left[2]
                changed = True
                break
    return out


def _prune_short_active_runs(states: np.ndarray, min_run: int):
    if min_run <= 1:
        return states
    out = states.copy()
    for start, end, value in _runs(out):
        if value >= 0 and end - start < min_run:
            out[start:end] = -1
    return out


def decode_with_hysteresis(
    probabilities,
    *,
    start_confidence: float = DECODER_START_CONFIDENCE,
    continue_confidence: float = DECODER_CONTINUE_CONFIDENCE,
    gap_frames: int = DECODER_GAP_FRAMES,
    min_run_frames: int = DECODER_MIN_RUN_FRAMES,
):
    probs = np.asarray(probabilities, dtype=np.float64)
    if probs.ndim != 3 or probs.shape[1:] != (NUM_STRINGS, NUM_CLASSES):
        raise ValueError("probabilities must be T x 6 x 21")
    if not (0.0 <= continue_confidence <= start_confidence <= 1.0):
        raise ValueError("invalid confidence thresholds")
    if gap_frames < 0 or min_run_frames <= 0:
        raise ValueError("invalid temporal decoder bounds")
    sums = probs.sum(axis=-1)
    if np.any(~np.isfinite(probs)) or np.any(probs < 0) or not np.allclose(sums, 1.0, atol=1e-5):
        raise ValueError("probabilities must be finite normalized distributions")

    frames = probs.shape[0]
    decoded = np.full((frames, NUM_STRINGS), -1, dtype=np.int16)

    for string in range(NUM_STRINGS):
        current = -1
        for frame in range(frames):
            row = probs[frame, string]
            silence = float(row[SILENCE_CLASS])
            best_fret = int(np.argmax(row[:NUM_FRETS]))
            best_active = float(row[best_fret])

            if current >= 0:
                keep = float(row[current])
                if keep >= continue_confidence and keep >= silence * 0.80:
                    decoded[frame, string] = current
                    continue

            if best_active >= start_confidence and best_active > silence:
                current = best_fret
                decoded[frame, string] = current
            else:
                current = -1

        merged = _merge_short_gaps(decoded[:, string], gap_frames)
        decoded[:, string] = _prune_short_active_runs(merged, min_run_frames)

    return decoded


def count_active_runs(states) -> int:
    arr = np.asarray(states)
    if arr.ndim != 2 or arr.shape[1] != NUM_STRINGS:
        raise ValueError("states must be T x 6")
    count = 0
    for string in range(NUM_STRINGS):
        count += sum(1 for _, _, value in _runs(arr[:, string]) if value >= 0)
    return count


def content_counts_from_categories(categories) -> dict[str, int]:
    normalized = ["PalmMute" if c == "techniques" else c for c in categories]
    counts = Counter(normalized)
    if set(counts) != set(PRIMARY_CONTENT):
        raise ValueError("categories must cover all primary content classes")
    return {name: int(counts[name]) for name in PRIMARY_CONTENT}
