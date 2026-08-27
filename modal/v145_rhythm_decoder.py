"""CPU-only V145 Rhythm evidence lattice and constrained guitar decoder.

This module implements only the frozen first-stage architecture contract from
``docs/v145-rhythm-decoder-preregistration.md``.  It consumes generated Rhythm
events, carries their MIDI evidence through nearby timing-grid candidates, and
maps selected pitches to physically valid standard-guitar positions.

It intentionally has no Modal dependency and no human-reference input.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math
from typing import Iterable, Mapping, Sequence


PITCH_KEYS = ("midi", "midiPitch", "pitch")
ONSET_KEYS = ("onset", "time", "start", "startTime")
DURATION_KEYS = ("duration", "durationSeconds", "length")
CONFIDENCE_KEYS = ("confidence", "score", "probability")
STANDARD_TUNING = (40, 45, 50, 55, 59, 64)  # strings 6 -> 1
DEFAULT_MAX_FRET = 24
DEFAULT_MAX_SHIFT_STEPS = 1
DEFAULT_MAX_FRET_SPAN = 7
DEFAULT_MAX_STATES = 512


@dataclass(frozen=True)
class EvidenceEvent:
    source_index: int
    midi: int
    onset: float
    duration: float
    confidence: float


@dataclass(frozen=True)
class TimingCandidate:
    source_index: int
    midi: int
    raw_onset: float
    candidate_onset: float
    duration: float
    confidence: float
    shift_steps: int
    timing_cost: float


@dataclass(frozen=True)
class GuitarPosition:
    midi: int
    string: int
    fret: int


@dataclass(frozen=True)
class GuitarState:
    positions: tuple[GuitarPosition, ...]
    fret_span: int
    anchor_fret: float
    local_cost: float


@dataclass(frozen=True)
class DecodedNote:
    source_index: int
    midi: int
    raw_onset: float
    onset: float
    duration: float
    confidence: float
    timing_cost: float
    string: int
    fret: int


@dataclass(frozen=True)
class DecodeResult:
    decoded_notes: tuple[DecodedNote, ...]
    undecoded_onsets: tuple[float, ...]
    evidence_count: int
    decoded_evidence_count: int


def _finite_number(value: object) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _first_number(event: Mapping[str, object], keys: Sequence[str]) -> float | None:
    for key in keys:
        number = _finite_number(event.get(key))
        if number is not None:
            return number
    return None


def normalize_rhythm_events(events: Sequence[Mapping[str, object]]) -> tuple[EvidenceEvent, ...]:
    """Normalize generated Rhythm events without mutating caller-owned objects."""

    normalized: list[EvidenceEvent] = []
    for source_index, event in enumerate(events):
        pitch = _first_number(event, PITCH_KEYS)
        onset = _first_number(event, ONSET_KEYS)
        if pitch is None or onset is None or onset < 0:
            continue

        duration = _first_number(event, DURATION_KEYS)
        if duration is None:
            duration = 0.0
        duration = max(0.0, duration)

        confidence = _first_number(event, CONFIDENCE_KEYS)
        if confidence is None:
            confidence = 1.0
        confidence = min(1.0, max(0.0, confidence))

        normalized.append(
            EvidenceEvent(
                source_index=source_index,
                midi=int(round(pitch)),
                onset=float(onset),
                duration=float(duration),
                confidence=float(confidence),
            )
        )

    return tuple(sorted(normalized, key=lambda item: (item.onset, item.midi, item.source_index)))


def _round_half_up(value: float) -> int:
    return int(math.floor(value + 0.5))


def timing_candidates_for_event(
    event: EvidenceEvent,
    grid_quantum_seconds: float,
    *,
    max_shift_steps: int = DEFAULT_MAX_SHIFT_STEPS,
) -> tuple[TimingCandidate, ...]:
    """Return nearest-grid and neighboring timing candidates for one event."""

    quantum = _finite_number(grid_quantum_seconds)
    if quantum is None or quantum <= 0:
        raise ValueError("grid_quantum_seconds must be a finite positive number")
    if not isinstance(max_shift_steps, int) or isinstance(max_shift_steps, bool) or max_shift_steps < 0:
        raise ValueError("max_shift_steps must be a non-negative integer")

    nearest_index = _round_half_up(event.onset / quantum)
    seen: set[float] = set()
    candidates: list[TimingCandidate] = []

    for grid_index in range(nearest_index - max_shift_steps, nearest_index + max_shift_steps + 1):
        if grid_index < 0:
            continue
        candidate_onset = round(grid_index * quantum, 12)
        if candidate_onset in seen:
            continue
        seen.add(candidate_onset)
        timing_cost = abs(candidate_onset - event.onset) / quantum
        candidates.append(
            TimingCandidate(
                source_index=event.source_index,
                midi=event.midi,
                raw_onset=event.onset,
                candidate_onset=candidate_onset,
                duration=event.duration,
                confidence=event.confidence,
                shift_steps=grid_index - nearest_index,
                timing_cost=float(timing_cost),
            )
        )

    return tuple(
        sorted(
            candidates,
            key=lambda item: (
                item.timing_cost,
                abs(item.shift_steps),
                item.candidate_onset,
                item.source_index,
            ),
        )
    )


def build_timing_lattice(
    evidence: Sequence[EvidenceEvent],
    grid_quantum_seconds: float,
    *,
    max_shift_steps: int = DEFAULT_MAX_SHIFT_STEPS,
) -> dict[float, tuple[TimingCandidate, ...]]:
    """Index all timing candidates by proposed onset."""

    grouped: dict[float, list[TimingCandidate]] = {}
    for event in evidence:
        for candidate in timing_candidates_for_event(
            event,
            grid_quantum_seconds,
            max_shift_steps=max_shift_steps,
        ):
            grouped.setdefault(candidate.candidate_onset, []).append(candidate)

    return {
        onset: tuple(sorted(rows, key=lambda row: (row.midi, row.source_index, row.timing_cost)))
        for onset, rows in sorted(grouped.items())
    }


def choose_nearest_timing_candidates(
    evidence: Sequence[EvidenceEvent],
    grid_quantum_seconds: float,
    *,
    max_shift_steps: int = DEFAULT_MAX_SHIFT_STEPS,
) -> tuple[TimingCandidate, ...]:
    """Choose exactly one deterministic timing proposal per evidence event."""

    chosen: list[TimingCandidate] = []
    for event in evidence:
        candidates = timing_candidates_for_event(
            event,
            grid_quantum_seconds,
            max_shift_steps=max_shift_steps,
        )
        if candidates:
            chosen.append(candidates[0])
    return tuple(sorted(chosen, key=lambda row: (row.candidate_onset, row.midi, row.source_index)))


def enumerate_guitar_positions(
    midi: int,
    *,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
) -> tuple[GuitarPosition, ...]:
    """Enumerate physically valid standard-guitar positions for one MIDI pitch."""

    if not isinstance(midi, int) or isinstance(midi, bool):
        raise ValueError("midi must be an integer")
    if len(tuning) != 6 or any(not isinstance(value, int) or isinstance(value, bool) for value in tuning):
        raise ValueError("tuning must contain six integer open-string MIDI values")
    if not isinstance(max_fret, int) or isinstance(max_fret, bool) or max_fret < 0:
        raise ValueError("max_fret must be a non-negative integer")

    positions: list[GuitarPosition] = []
    for tuning_index, open_midi in enumerate(tuning):
        fret = midi - open_midi
        if 0 <= fret <= max_fret:
            string_number = 6 - tuning_index
            positions.append(GuitarPosition(midi=midi, string=string_number, fret=fret))

    return tuple(sorted(positions, key=lambda pos: (pos.fret, pos.string)))


def _state_from_positions(positions: Sequence[GuitarPosition]) -> GuitarState:
    frets = [position.fret for position in positions]
    fret_span = max(frets) - min(frets) if frets else 0
    anchor = sum(frets) / len(frets) if frets else 0.0
    local_cost = fret_span * 0.25 + anchor * 0.01
    return GuitarState(
        positions=tuple(positions),
        fret_span=fret_span,
        anchor_fret=float(anchor),
        local_cost=float(local_cost),
    )


def enumerate_guitar_states(
    midis: Sequence[int],
    *,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
    max_fret_span: int = DEFAULT_MAX_FRET_SPAN,
    max_states: int = DEFAULT_MAX_STATES,
) -> tuple[GuitarState, ...]:
    """Enumerate unique-string simultaneous fingerings preserving every MIDI pitch."""

    if not midis:
        return tuple()
    if len(midis) > 6:
        return tuple()
    if not isinstance(max_fret_span, int) or isinstance(max_fret_span, bool) or max_fret_span < 0:
        raise ValueError("max_fret_span must be a non-negative integer")
    if not isinstance(max_states, int) or isinstance(max_states, bool) or max_states <= 0:
        raise ValueError("max_states must be a positive integer")

    ordered_midis = tuple(sorted(int(midi) for midi in midis))
    position_options = [
        enumerate_guitar_positions(midi, tuning=tuning, max_fret=max_fret)
        for midi in ordered_midis
    ]
    if any(not options for options in position_options):
        return tuple()

    states: list[GuitarState] = []
    for choice in product(*position_options):
        strings = [position.string for position in choice]
        if len(strings) != len(set(strings)):
            continue
        state = _state_from_positions(choice)
        if state.fret_span > max_fret_span:
            continue
        states.append(state)
        if len(states) >= max_states:
            break

    states.sort(
        key=lambda state: (
            state.local_cost,
            state.fret_span,
            state.anchor_fret,
            tuple((position.midi, position.string, position.fret) for position in state.positions),
        )
    )
    return tuple(states)


def state_transition_cost(previous: GuitarState | None, current: GuitarState) -> float:
    """Penalize large hand-position jumps while preserving pitch identity."""

    if previous is None:
        return 0.0
    return abs(current.anchor_fret - previous.anchor_fret)


def choose_guitar_state(
    midis: Sequence[int],
    *,
    previous: GuitarState | None = None,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
    max_fret_span: int = DEFAULT_MAX_FRET_SPAN,
    max_states: int = DEFAULT_MAX_STATES,
) -> GuitarState | None:
    """Choose the deterministic lowest-cost physically valid state."""

    states = enumerate_guitar_states(
        midis,
        tuning=tuning,
        max_fret=max_fret,
        max_fret_span=max_fret_span,
        max_states=max_states,
    )
    if not states:
        return None

    return min(
        states,
        key=lambda state: (
            state.local_cost + state_transition_cost(previous, state),
            state.local_cost,
            state.fret_span,
            state.anchor_fret,
            tuple((position.midi, position.string, position.fret) for position in state.positions),
        ),
    )


def _map_positions_to_candidates(
    candidates: Sequence[TimingCandidate],
    state: GuitarState,
) -> tuple[tuple[TimingCandidate, GuitarPosition], ...]:
    ordered_candidates = sorted(candidates, key=lambda row: (row.midi, row.source_index))
    ordered_positions = sorted(state.positions, key=lambda row: (row.midi, row.string, row.fret))
    if [row.midi for row in ordered_candidates] != [row.midi for row in ordered_positions]:
        raise ValueError("guitar state pitch inventory does not match timing candidates")
    return tuple(zip(ordered_candidates, ordered_positions))


def decode_nearest_timing_path(
    events: Sequence[Mapping[str, object]],
    grid_quantum_seconds: float,
    *,
    max_shift_steps: int = DEFAULT_MAX_SHIFT_STEPS,
    tuning: Sequence[int] = STANDARD_TUNING,
    max_fret: int = DEFAULT_MAX_FRET,
    max_fret_span: int = DEFAULT_MAX_FRET_SPAN,
    max_states: int = DEFAULT_MAX_STATES,
) -> DecodeResult:
    """CPU proof decoder: nearest timing candidate, then continuity-aware fingering."""

    evidence = normalize_rhythm_events(events)
    chosen = choose_nearest_timing_candidates(
        evidence,
        grid_quantum_seconds,
        max_shift_steps=max_shift_steps,
    )

    grouped: dict[float, list[TimingCandidate]] = {}
    for candidate in chosen:
        grouped.setdefault(candidate.candidate_onset, []).append(candidate)

    previous_state: GuitarState | None = None
    decoded: list[DecodedNote] = []
    undecoded: list[float] = []

    for onset, candidates in sorted(grouped.items()):
        ordered_candidates = sorted(candidates, key=lambda row: (row.midi, row.source_index))
        state = choose_guitar_state(
            [row.midi for row in ordered_candidates],
            previous=previous_state,
            tuning=tuning,
            max_fret=max_fret,
            max_fret_span=max_fret_span,
            max_states=max_states,
        )
        if state is None:
            undecoded.append(onset)
            continue

        for candidate, position in _map_positions_to_candidates(ordered_candidates, state):
            decoded.append(
                DecodedNote(
                    source_index=candidate.source_index,
                    midi=candidate.midi,
                    raw_onset=candidate.raw_onset,
                    onset=candidate.candidate_onset,
                    duration=candidate.duration,
                    confidence=candidate.confidence,
                    timing_cost=candidate.timing_cost,
                    string=position.string,
                    fret=position.fret,
                )
            )
        previous_state = state

    decoded.sort(key=lambda row: (row.onset, row.midi, row.source_index))
    return DecodeResult(
        decoded_notes=tuple(decoded),
        undecoded_onsets=tuple(undecoded),
        evidence_count=len(evidence),
        decoded_evidence_count=len(decoded),
    )


def decoded_pitch_inventory(result: DecodeResult) -> tuple[tuple[float, int], ...]:
    """Small deterministic helper for CPU assertions and later benchmark adapters."""

    return tuple((note.onset, note.midi) for note in result.decoded_notes)
