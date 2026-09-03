from __future__ import annotations

import math
import statistics
from typing import Any, Iterable

ESTIMATOR_VERSION = 1
WINDOW_SECONDS = 0.020
HOP_SECONDS = 0.010
NOVELTY_HISTORY_FRAMES = 8
ONSET_THRESHOLD = 0.18
ONSET_LOCAL_RADIUS = 2
ONSET_REFRACTORY_SECONDS = 0.070
TEMPO_MIN_BPM = 50.0
TEMPO_MAX_BPM = 220.0
TEMPO_STEP_BPM = 0.5
TEMPO_MIN_SCORE = 0.42
TEMPO_GAP_TOLERANCE = 0.10
METER_MAP_TOLERANCE = 0.18
METER_MIN_SCORE = 0.18
METER_MIN_MARGIN = 0.04
FEEL_BEAT_EXCLUSION = 0.15
FEEL_TARGET_WINDOW = 0.12
FEEL_MIN_OFFBEAT_COUNT = 4
FEEL_MIN_EVIDENCE = 0.45
FEEL_MIN_RATIO = 1.25
EPSILON = 1e-12


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, float(value)))


def _finite_sample(value: Any) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return 0.0
    return parsed if math.isfinite(parsed) else 0.0


def _normalize_samples(samples: Iterable[Any]) -> list[float]:
    return [_finite_sample(value) for value in samples]


def _extract_onsets(samples: list[float], sample_rate: int) -> dict[str, Any]:
    window = max(1, int(round(sample_rate * WINDOW_SECONDS)))
    hop = max(1, int(round(sample_rate * HOP_SECONDS)))

    if len(samples) < window:
        return {
            "onsets": [],
            "frameCount": 0,
            "noveltyMaximum": 0.0,
        }

    energies: list[float] = []
    frame_times: list[float] = []

    for start in range(0, len(samples) - window + 1, hop):
        frame = samples[start : start + window]
        energies.append(sum(abs(value) for value in frame) / window)
        # Frame-center timing avoids the systematic early-onset bias that occurs
        # when a transient first appears near the end of an analysis window.
        frame_times.append((start + window / 2.0) / sample_rate)

    novelty: list[float] = []
    for index, energy in enumerate(energies):
        history = energies[max(0, index - NOVELTY_HISTORY_FRAMES) : index]
        baseline = statistics.median(history) if history else 0.0
        novelty.append(max(0.0, energy - baseline))

    novelty_maximum = max(novelty) if novelty else 0.0
    normalized = [
        value / novelty_maximum if novelty_maximum > 0.0 else 0.0
        for value in novelty
    ]

    candidates: list[tuple[float, float]] = []
    for index, strength in enumerate(normalized):
        if strength < ONSET_THRESHOLD:
            continue
        left = max(0, index - ONSET_LOCAL_RADIUS)
        right = min(len(normalized), index + ONSET_LOCAL_RADIUS + 1)
        if strength >= max(normalized[left:right]):
            candidates.append((frame_times[index], strength))

    accepted: list[tuple[float, float]] = []
    for time_seconds, strength in candidates:
        if (
            not accepted
            or time_seconds - accepted[-1][0] >= ONSET_REFRACTORY_SECONDS
        ):
            accepted.append((time_seconds, strength))
            continue

        if strength > accepted[-1][1]:
            accepted[-1] = (time_seconds, strength)

    return {
        "onsets": accepted,
        "frameCount": len(energies),
        "noveltyMaximum": novelty_maximum,
    }


def _folded_median_target_bpm(onsets: list[tuple[float, float]]) -> float | None:
    gaps = [
        later[0] - earlier[0]
        for earlier, later in zip(onsets, onsets[1:])
        if later[0] > earlier[0]
    ]
    if not gaps:
        return None

    beat_seconds = float(statistics.median(gaps))
    while beat_seconds < 0.32:
        beat_seconds *= 2.0
    while beat_seconds > 0.95:
        beat_seconds /= 2.0

    return 60.0 / beat_seconds if beat_seconds > 0.0 else None


def _gap_compatible(ratio: float) -> float:
    allowed = (0.25, 1.0 / 3.0, 0.5, 1.0, 2.0, 3.0, 4.0)
    relative_error = min(abs(ratio - target) / target for target in allowed)
    return 1.0 if relative_error <= TEMPO_GAP_TOLERANCE else 0.0


def _tempo_score(onsets: list[tuple[float, float]], bpm: float) -> dict[str, float]:
    period = 60.0 / bpm
    total_weight = sum(strength for _, strength in onsets)
    if total_weight <= 0.0:
        return {"combined": 0.0, "phaseCoherence": 0.0, "gapCompatibility": 0.0}

    cosine = sum(
        strength * math.cos(2.0 * math.pi * time_seconds / period)
        for time_seconds, strength in onsets
    )
    sine = sum(
        strength * math.sin(2.0 * math.pi * time_seconds / period)
        for time_seconds, strength in onsets
    )
    phase_coherence = math.hypot(cosine, sine) / total_weight

    weighted_gaps: list[tuple[float, float]] = []
    for earlier, later in zip(onsets, onsets[1:]):
        gap = later[0] - earlier[0]
        if gap <= 0.0:
            continue
        pair_weight = (earlier[1] + later[1]) / 2.0
        weighted_gaps.append((_gap_compatible(gap / period), pair_weight))

    gap_weight = sum(weight for _, weight in weighted_gaps)
    gap_compatibility = (
        sum(value * weight for value, weight in weighted_gaps) / gap_weight
        if gap_weight > 0.0
        else 0.0
    )

    return {
        "combined": 0.70 * phase_coherence + 0.30 * gap_compatibility,
        "phaseCoherence": phase_coherence,
        "gapCompatibility": gap_compatibility,
    }


def _estimate_tempo(onsets: list[tuple[float, float]]) -> dict[str, Any]:
    if len(onsets) < 4:
        return {
            "bpm": None,
            "confidence": None,
            "periodSeconds": None,
            "phaseSeconds": None,
            "score": None,
            "foldedMedianTargetBpm": _folded_median_target_bpm(onsets),
        }

    folded_target = _folded_median_target_bpm(onsets)
    best: dict[str, Any] | None = None
    step_count = int(round((TEMPO_MAX_BPM - TEMPO_MIN_BPM) / TEMPO_STEP_BPM))

    for step in range(step_count + 1):
        bpm = TEMPO_MIN_BPM + step * TEMPO_STEP_BPM
        score = _tempo_score(onsets, bpm)
        tie_distance = abs(bpm - folded_target) if folded_target is not None else 0.0
        ranking = (score["combined"], -tie_distance, -bpm)

        if best is None or ranking > best["ranking"]:
            best = {
                "ranking": ranking,
                "bpm": bpm,
                "score": score,
            }

    if best is None or best["score"]["combined"] < TEMPO_MIN_SCORE:
        return {
            "bpm": None,
            "confidence": None,
            "periodSeconds": None,
            "phaseSeconds": None,
            "score": best["score"] if best else None,
            "foldedMedianTargetBpm": folded_target,
        }

    bpm = float(best["bpm"])
    period = 60.0 / bpm
    total_weight = sum(strength for _, strength in onsets)
    cosine = sum(
        strength * math.cos(2.0 * math.pi * ((time_seconds % period) / period))
        for time_seconds, strength in onsets
    )
    sine = sum(
        strength * math.sin(2.0 * math.pi * ((time_seconds % period) / period))
        for time_seconds, strength in onsets
    )
    angle = math.atan2(sine, cosine)
    if angle < 0.0:
        angle += 2.0 * math.pi
    phase = (angle / (2.0 * math.pi)) * period if total_weight > 0.0 else 0.0

    return {
        "bpm": bpm,
        "confidence": _clamp(best["score"]["combined"]),
        "periodSeconds": period,
        "phaseSeconds": phase,
        "score": best["score"],
        "foldedMedianTargetBpm": folded_target,
    }


def _map_onsets_to_beats(
    onsets: list[tuple[float, float]], period: float, phase: float
) -> list[tuple[int, float, float]]:
    mapped: list[tuple[int, float, float]] = []
    for time_seconds, strength in onsets:
        beat_index = int(round((time_seconds - phase) / period))
        beat_time = phase + beat_index * period
        if abs(time_seconds - beat_time) <= METER_MAP_TOLERANCE * period:
            mapped.append((beat_index, strength, time_seconds))
    return mapped


def _meter_candidate(
    mapped: list[tuple[int, float, float]], meter_length: int
) -> dict[str, Any]:
    best: dict[str, Any] | None = None

    for offset in range(meter_length):
        buckets: list[list[float]] = [[] for _ in range(meter_length)]
        for beat_index, strength, _ in mapped:
            metric_position = (beat_index - offset) % meter_length
            buckets[metric_position].append(strength)

        means = [
            sum(bucket) / len(bucket) if bucket else 0.0
            for bucket in buckets
        ]
        downbeat_mean = means[0]
        other_means = means[1:]
        other_mean = sum(other_means) / len(other_means) if other_means else 0.0
        accent_contrast = (
            (downbeat_mean - other_mean) / max(downbeat_mean, EPSILON)
        )
        coverage = sum(1 for bucket in buckets if bucket) / meter_length
        score = 0.75 * accent_contrast + 0.25 * coverage
        ranking = (score, -offset)

        if best is None or ranking > best["ranking"]:
            best = {
                "ranking": ranking,
                "score": score,
                "offset": offset,
                "accentContrast": accent_contrast,
                "coverage": coverage,
                "positionMeans": means,
            }

    assert best is not None
    return best


def _estimate_meter_and_pickup(
    onsets: list[tuple[float, float]], tempo: dict[str, Any]
) -> dict[str, Any]:
    if tempo["bpm"] is None:
        return {
            "timeSignature": None,
            "confidence": None,
            "downbeatOffset": None,
            "pickupBeats": None,
            "meterCandidates": None,
        }

    period = float(tempo["periodSeconds"])
    phase = float(tempo["phaseSeconds"])
    mapped = _map_onsets_to_beats(onsets, period, phase)
    candidates = {
        3: _meter_candidate(mapped, 3),
        4: _meter_candidate(mapped, 4),
    }

    ordered = sorted(
        candidates.items(),
        key=lambda item: (item[1]["score"], -item[0]),
        reverse=True,
    )
    winning_meter, winner = ordered[0]
    runner_score = ordered[1][1]["score"]

    if (
        winner["score"] < METER_MIN_SCORE
        or winner["score"] - runner_score < METER_MIN_MARGIN
    ):
        return {
            "timeSignature": None,
            "confidence": None,
            "downbeatOffset": None,
            "pickupBeats": None,
            "meterCandidates": candidates,
        }

    offset = int(winner["offset"])
    first_downbeat = phase + offset * period
    while first_downbeat < 0.0:
        first_downbeat += winning_meter * period

    pickup_beats = first_downbeat / period
    if abs(pickup_beats) <= 0.20:
        pickup_beats = 0.0
    else:
        pickup_beats = round(pickup_beats, 3)
        if pickup_beats < 0.0 or pickup_beats > 32.0:
            pickup_beats = None

    return {
        "timeSignature": {
            "numerator": winning_meter,
            "denominator": 4,
        },
        "confidence": _clamp(winner["score"]),
        "downbeatOffset": offset,
        "pickupBeats": pickup_beats,
        "meterCandidates": candidates,
    }


def _circular_fraction_distance(value: float, target: float) -> float:
    difference = abs(value - target)
    return min(difference, 1.0 - difference)


def _feel_family_evidence(
    offbeats: list[tuple[float, float]], targets: tuple[float, ...]
) -> float:
    total_weight = sum(strength for _, strength in offbeats)
    if total_weight <= 0.0:
        return 0.0

    evidence = 0.0
    for fraction, strength in offbeats:
        distance = min(
            _circular_fraction_distance(fraction, target)
            for target in targets
        )
        if distance <= FEEL_TARGET_WINDOW:
            evidence += strength * (1.0 - distance / FEEL_TARGET_WINDOW)

    return evidence / total_weight


def _estimate_feel(
    onsets: list[tuple[float, float]], tempo: dict[str, Any]
) -> dict[str, Any]:
    if tempo["bpm"] is None:
        return {
            "feel": None,
            "confidence": None,
            "straightEvidence": 0.0,
            "tripletEvidence": 0.0,
            "offbeatCount": 0,
        }

    period = float(tempo["periodSeconds"])
    phase = float(tempo["phaseSeconds"])
    offbeats: list[tuple[float, float]] = []

    for time_seconds, strength in onsets:
        fraction = ((time_seconds - phase) / period) % 1.0
        distance_to_beat = min(fraction, 1.0 - fraction)
        if distance_to_beat <= FEEL_BEAT_EXCLUSION:
            continue
        offbeats.append((fraction, strength))

    straight = _feel_family_evidence(offbeats, (0.5,))
    triplet = _feel_family_evidence(offbeats, (1.0 / 3.0, 2.0 / 3.0))

    feel: str | None = None
    confidence: float | None = None
    if len(offbeats) >= FEEL_MIN_OFFBEAT_COUNT:
        if straight >= FEEL_MIN_EVIDENCE and straight >= triplet * FEEL_MIN_RATIO:
            feel = "straight"
            confidence = _clamp(straight)
        elif triplet >= FEEL_MIN_EVIDENCE and triplet >= straight * FEEL_MIN_RATIO:
            feel = "triplet"
            confidence = _clamp(triplet)

    return {
        "feel": feel,
        "confidence": confidence,
        "straightEvidence": straight,
        "tripletEvidence": triplet,
        "offbeatCount": len(offbeats),
    }


def _observation_field(value: Any, confidence: float | None, method: str) -> dict[str, Any] | None:
    if value is None or confidence is None:
        return None
    return {
        "value": value,
        "confidence": round(_clamp(confidence), 6),
        "method": method,
    }


def estimate_full_mixture_structure_v1(
    samples: Iterable[Any], sample_rate: int
) -> dict[str, Any]:
    if not isinstance(sample_rate, int) or sample_rate <= 0:
        raise ValueError("sample_rate must be a positive integer")

    normalized_samples = _normalize_samples(samples)
    onset_result = _extract_onsets(normalized_samples, sample_rate)
    onsets = onset_result["onsets"]
    tempo = _estimate_tempo(onsets)
    meter = _estimate_meter_and_pickup(onsets, tempo)
    feel = _estimate_feel(onsets, tempo)

    tempo_field = _observation_field(
        round(float(tempo["bpm"]), 3) if tempo["bpm"] is not None else None,
        tempo["confidence"],
        "waveform-onset-periodicity-v1",
    )
    meter_field = _observation_field(
        meter["timeSignature"],
        meter["confidence"],
        "waveform-accent-meter-v1",
    )
    pickup_field = _observation_field(
        meter["pickupBeats"],
        meter["confidence"] if meter["pickupBeats"] is not None else None,
        "waveform-downbeat-phase-v1",
    )
    feel_field = _observation_field(
        feel["feel"],
        feel["confidence"],
        "waveform-subdivision-evidence-v1",
    )

    return {
        "version": ESTIMATOR_VERSION,
        "provenance": {
            "sourceKind": "full-mixture",
            "sourceIdentity": "request-audio",
            "referenceBlind": True,
            "referenceRuntimeInputUsed": False,
        },
        "tempoBpm": tempo_field,
        "timeSignature": meter_field,
        "pickupBeats": pickup_field,
        "feel": feel_field,
        "diagnostics": {
            "inputSampleCount": len(normalized_samples),
            "sampleRate": sample_rate,
            "frameCount": onset_result["frameCount"],
            "onsetCount": len(onsets),
            "onsets": [
                {"time": round(time_seconds, 6), "strength": round(strength, 6)}
                for time_seconds, strength in onsets
            ],
            "tempo": tempo,
            "meter": meter,
            "feel": feel,
            "referenceBlind": True,
            "carrierInputUsed": False,
            "transcribedEventInputUsed": False,
        },
    }
