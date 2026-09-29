"""Pure manifest/timing measurement helpers for Astra pre-V9 review.

No audio, model, numpy, torch, or network dependencies.
"""
from __future__ import annotations

import math
from typing import Iterable, Mapping, Sequence


class ContractError(ValueError):
    pass


def _num(value, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ContractError(f"{name} must be a real number, not {type(value).__name__}")
    value = float(value)
    if not math.isfinite(value):
        raise ContractError(f"{name} must be finite")
    return value


def corrected_duration(clip: Mapping, corrections: Mapping[str, float]) -> float:
    clip_id = str(clip.get("id", ""))
    if not clip_id:
        raise ContractError("clip id is required")
    if clip_id in corrections:
        duration = _num(corrections[clip_id], f"correction[{clip_id}]")
    else:
        start = _num(clip.get("evaluationStartSeconds"), f"{clip_id}.evaluationStartSeconds")
        end = _num(clip.get("evaluationEndSeconds"), f"{clip_id}.evaluationEndSeconds")
        duration = end - start
    if duration <= 0:
        raise ContractError(f"{clip_id} duration must be > 0")
    return duration


def validate_manifest(clips: Sequence[Mapping], corrections: Mapping[str, float] | None = None) -> dict:
    corrections = corrections or {}
    seen = set()
    positive_seconds = 0.0
    negative_seconds = 0.0
    positive = 0
    negative = 0
    for clip in clips:
        clip_id = str(clip.get("id", ""))
        if not clip_id:
            raise ContractError("every clip requires a non-empty id")
        if clip_id in seen:
            raise ContractError(f"duplicate clip id: {clip_id}")
        seen.add(clip_id)
        kind = clip.get("kind")
        if kind not in {"positive", "negative-only"}:
            raise ContractError(f"{clip_id} has invalid kind: {kind!r}")
        duration = corrected_duration(clip, corrections)
        if kind == "positive":
            positive += 1
            positive_seconds += duration
        else:
            negative += 1
            negative_seconds += duration
    unknown_corrections = set(corrections) - seen
    if unknown_corrections:
        raise ContractError(f"correction references unknown clip ids: {sorted(unknown_corrections)}")
    return {
        "total": len(clips),
        "positive": positive,
        "negativeOnly": negative,
        "positiveSeconds": positive_seconds,
        "negativeSeconds": negative_seconds,
    }


def group_acoustic_attacks(note_times: Iterable[float], tolerance_seconds: float) -> list[float]:
    tolerance = _num(tolerance_seconds, "tolerance_seconds")
    if tolerance < 0:
        raise ContractError("tolerance_seconds must be >= 0")
    times = sorted(_num(v, "attack time") for v in note_times)
    if not times:
        return []
    groups = [times[0]]
    anchor = times[0]
    for t in times[1:]:
        if t - anchor <= tolerance:
            continue
        groups.append(t)
        anchor = t
    return groups


def validate_group_times(group_times: Sequence[float], duration_seconds: float, include_endpoint: bool = False) -> None:
    duration = _num(duration_seconds, "duration_seconds")
    if duration <= 0:
        raise ContractError("duration_seconds must be > 0")
    previous = None
    for raw in group_times:
        t = _num(raw, "group time")
        if t < 0 or (t > duration if include_endpoint else t >= duration):
            bracket = "[0,duration]" if include_endpoint else "[0,duration)"
            raise ContractError(f"group time {t} outside {bracket}")
        if previous is not None and t <= previous:
            raise ContractError("group times must be strictly increasing")
        previous = t


def eligible_positive_iois(group_times: Sequence[float]) -> list[float]:
    return [b - a for a, b in zip(group_times, group_times[1:]) if b - a > 0]


def repeat_fraction(group_times: Sequence[float], threshold_seconds: float = 0.250) -> float | None:
    threshold = _num(threshold_seconds, "threshold_seconds")
    if threshold <= 0:
        raise ContractError("threshold_seconds must be > 0")
    iois = eligible_positive_iois(group_times)
    if not iois:
        return None
    return sum(i <= threshold for i in iois) / len(iois)


def pooled_density(group_counts: Sequence[int], positive_durations: Sequence[float]) -> float:
    if len(group_counts) != len(positive_durations):
        raise ContractError("group_counts and positive_durations must have equal length")
    total_seconds = 0.0
    total_groups = 0
    for idx, (count, duration) in enumerate(zip(group_counts, positive_durations)):
        if isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise ContractError(f"group_counts[{idx}] must be a nonnegative integer")
        d = _num(duration, f"positive_durations[{idx}]")
        if d <= 0:
            raise ContractError(f"positive_durations[{idx}] must be > 0")
        total_groups += count
        total_seconds += d
    if total_seconds <= 0:
        raise ContractError("positive duration denominator must be > 0")
    return total_groups / total_seconds


def check_count_rate_consistency(count: int, seconds: float, rate: float, atol: float = 1e-12) -> None:
    if isinstance(count, bool) or not isinstance(count, int) or count < 0:
        raise ContractError("count must be a nonnegative integer")
    seconds = _num(seconds, "seconds")
    rate = _num(rate, "rate")
    atol = _num(atol, "atol")
    if seconds <= 0 or rate < 0 or atol < 0:
        raise ContractError("invalid count/rate consistency inputs")
    expected = count / seconds
    if abs(expected - rate) > atol:
        raise ContractError(f"count/rate mismatch: expected {expected}, got {rate}")
