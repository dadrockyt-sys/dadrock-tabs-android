from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import median
from typing import Any, Iterable, Mapping, Protocol, Sequence


MIN_DYNAMIC_RANGE = 1.0e-9
PRE_ONSET_WINDOW_SECONDS = 0.12
PRE_ONSET_GUARD_SECONDS = 0.03
ATTACK_WINDOW_SECONDS = 0.10
SUSTAIN_START_OFFSET_SECONDS = 0.04
SUSTAIN_THRESHOLD_FRACTION = 0.18
MAX_INACTIVE_GAP_SECONDS = 0.10
MAX_SUSTAIN_SECONDS = 3.0
SAME_STRING_GUARD_SECONDS = 0.01
SUBDIVISIONS_PER_BEAT = 4


class SustainEnergyView(Protocol):
    source_name: str
    times: Any

    def energy(self, midi: int) -> Any: ...


@dataclass(frozen=True)
class SustainViewEvidence:
    source_name: str
    duration_seconds: float
    floor_energy: float
    attack_peak: float
    threshold: float
    hard_end_seconds: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source_name,
            "durationSeconds": float(self.duration_seconds),
            "floorEnergy": float(self.floor_energy),
            "attackPeak": float(self.attack_peak),
            "threshold": float(self.threshold),
            "hardEndSeconds": float(self.hard_end_seconds),
        }


@dataclass(frozen=True)
class SustainConsensus:
    duration_seconds: float
    duration_steps: int
    step_seconds: float
    view_agreement: int
    required_views: int
    views: tuple[SustainViewEvidence, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "durationSeconds": float(self.duration_seconds),
            "durationSteps": int(self.duration_steps),
            "stepSeconds": float(self.step_seconds),
            "viewAgreement": int(self.view_agreement),
            "requiredViewAgreement": int(self.required_views),
            "views": [item.to_dict() for item in self.views],
            "mode": "reference-free-two-view-harmonic-persistence-shadow",
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }


def _finite(value: Any, fallback: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(fallback)
    return number if math.isfinite(number) else float(fallback)


def _as_finite_pairs(times: Any, energies: Any) -> list[tuple[float, float]]:
    try:
        time_values = list(times)
        energy_values = list(energies)
    except TypeError:
        return []
    pairs: list[tuple[float, float]] = []
    for raw_time, raw_energy in zip(time_values, energy_values):
        time_value = _finite(raw_time, float("nan"))
        energy_value = _finite(raw_energy, float("nan"))
        if math.isfinite(time_value) and math.isfinite(energy_value):
            pairs.append((time_value, max(0.0, energy_value)))
    pairs.sort(key=lambda item: item[0])
    return pairs


def step_seconds(tempo_bpm: float) -> float:
    tempo = _finite(tempo_bpm)
    if tempo <= 0.0:
        raise ValueError("tempo_bpm must be positive")
    return 60.0 / tempo / float(SUBDIVISIONS_PER_BEAT)


def quantize_duration(duration_seconds: float, tempo_bpm: float) -> tuple[int, float]:
    duration = max(0.0, _finite(duration_seconds))
    one_step = step_seconds(tempo_bpm)
    steps = max(1, int(math.floor(duration / one_step + 0.5)))
    return steps, one_step


def evaluate_sustain_view(
    view: SustainEnergyView,
    *,
    onset_seconds: float,
    source_midi: int,
    hard_end_seconds: float,
) -> SustainViewEvidence | None:
    onset = _finite(onset_seconds)
    hard_end = _finite(hard_end_seconds)
    if hard_end <= onset + SUSTAIN_START_OFFSET_SECONDS:
        return None

    pairs = _as_finite_pairs(view.times, view.energy(int(source_midi)))
    if not pairs:
        return None

    before = [
        energy
        for time_value, energy in pairs
        if onset - PRE_ONSET_WINDOW_SECONDS
        <= time_value
        <= onset - PRE_ONSET_GUARD_SECONDS
    ]
    attack = [
        energy
        for time_value, energy in pairs
        if onset - 0.02 <= time_value <= onset + ATTACK_WINDOW_SECONDS
    ]
    after = [
        (time_value, energy)
        for time_value, energy in pairs
        if onset + SUSTAIN_START_OFFSET_SECONDS <= time_value <= hard_end
    ]
    if not attack or not after:
        return None

    floor = float(median(before)) if before else float(min(attack))
    peak = float(max(attack))
    dynamic = peak - floor
    if dynamic <= MIN_DYNAMIC_RANGE:
        return None
    threshold = floor + SUSTAIN_THRESHOLD_FRACTION * dynamic

    last_active_time = onset
    inactive_since: float | None = None
    saw_active = False
    for time_value, energy in after:
        if energy >= threshold:
            saw_active = True
            last_active_time = float(time_value)
            inactive_since = None
            continue
        if not saw_active:
            continue
        if inactive_since is None:
            inactive_since = float(time_value)
        if time_value - inactive_since > MAX_INACTIVE_GAP_SECONDS:
            break

    if not saw_active:
        return None
    duration = max(0.0, min(last_active_time, hard_end) - onset)
    if duration <= 0.0:
        return None
    return SustainViewEvidence(
        source_name=str(getattr(view, "source_name", "view")),
        duration_seconds=float(duration),
        floor_energy=floor,
        attack_peak=peak,
        threshold=float(threshold),
        hard_end_seconds=float(hard_end),
    )


def consensus_sustain(
    views: Sequence[SustainEnergyView],
    *,
    onset_seconds: float,
    source_midi: int,
    hard_end_seconds: float,
    tempo_bpm: float,
) -> SustainConsensus | None:
    if not views:
        return None
    required = min(2, len(views))
    evidence = [
        item
        for item in (
            evaluate_sustain_view(
                view,
                onset_seconds=onset_seconds,
                source_midi=source_midi,
                hard_end_seconds=hard_end_seconds,
            )
            for view in views[:2]
        )
        if item is not None
    ]
    if len(evidence) < required:
        return None

    # Conservative agreement: a note is considered sustained only as long as
    # every required independent guitar view continues to support it.
    duration = min(item.duration_seconds for item in evidence)
    steps, one_step = quantize_duration(duration, tempo_bpm)
    return SustainConsensus(
        duration_seconds=float(duration),
        duration_steps=int(steps),
        step_seconds=float(one_step),
        view_agreement=len(evidence),
        required_views=required,
        views=tuple(evidence),
    )


def _event_time(event: Mapping[str, Any]) -> float:
    return _finite(event.get("timeSeconds"), 0.0)


def _event_midi(event: Mapping[str, Any]) -> int | None:
    value = event.get("midi", event.get("dominantMidi"))
    try:
        midi = int(round(float(value)))
    except (TypeError, ValueError):
        return None
    return midi if 24 <= midi <= 96 else None


def _event_string(event: Mapping[str, Any]) -> int | None:
    try:
        value = int(event.get("stringIndex"))
    except (TypeError, ValueError):
        return None
    return value if 0 <= value <= 5 else None


def _hard_end_by_event(
    events: Sequence[Mapping[str, Any]],
) -> dict[int, float]:
    ordered = sorted(
        range(len(events)),
        key=lambda index: (_event_time(events[index]), index),
    )
    next_by_string: dict[int, float] = {}
    hard_end: dict[int, float] = {}
    for index in reversed(ordered):
        event = events[index]
        onset = _event_time(event)
        string_index = _event_string(event)
        limit = onset + MAX_SUSTAIN_SECONDS
        if string_index is not None and string_index in next_by_string:
            limit = min(
                limit,
                max(onset, next_by_string[string_index] - SAME_STRING_GUARD_SECONDS),
            )
        hard_end[index] = float(limit)
        if string_index is not None:
            next_by_string[string_index] = onset
    return hard_end


def annotate_sustain_shadow(
    events: Sequence[Mapping[str, Any]],
    views: Sequence[SustainEnergyView],
    *,
    tempo_bpm: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Attach label-free sustain diagnostics without changing production sustain.

    The new field is deliberately `rhythmSustainShadow`; the existing
    `rhythmSustain` contract remains untouched until an approved-audio shadow has
    independently validated the physical persistence evidence.
    """
    copied = [dict(event) for event in events]
    hard_end = _hard_end_by_event(copied)
    annotated = 0
    longer_than_detector = 0
    shorter_than_detector = 0

    for index, event in enumerate(copied):
        midi = _event_midi(event)
        if midi is None:
            continue
        consensus = consensus_sustain(
            views,
            onset_seconds=_event_time(event),
            source_midi=midi,
            hard_end_seconds=hard_end[index],
            tempo_bpm=tempo_bpm,
        )
        if consensus is None:
            continue
        existing = event.get("rhythmSustain") if isinstance(event.get("rhythmSustain"), Mapping) else {}
        detector_duration = _finite(existing.get("durationSeconds"), 0.0)
        if consensus.duration_seconds > detector_duration + 1.0e-6:
            longer_than_detector += 1
        elif detector_duration > consensus.duration_seconds + 1.0e-6:
            shorter_than_detector += 1
        event["rhythmSustainShadow"] = {
            **consensus.to_dict(),
            "detectorDurationSeconds": float(detector_duration),
            "attackTimingChanged": False,
            "pitchChanged": False,
            "tieOrLetRingInferred": False,
        }
        annotated += 1

    return copied, {
        "eventCount": len(copied),
        "annotatedEventCount": annotated,
        "longerThanDetectorCount": longer_than_detector,
        "shorterThanDetectorCount": shorter_than_detector,
        "eventCountChanged": False,
        "attackTimingChanged": False,
        "pitchChanged": False,
        "tieOrLetRingInferred": False,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


__all__ = [
    "SustainEnergyView",
    "SustainViewEvidence",
    "SustainConsensus",
    "evaluate_sustain_view",
    "consensus_sustain",
    "annotate_sustain_shadow",
]
