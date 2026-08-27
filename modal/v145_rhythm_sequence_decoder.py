"""CPU-only V145 Stage 2 timing-grid inference and global Rhythm decoding.

Implements the frozen contract in
``docs/v145-rhythm-decoder-stage2-preregistration.md``.  Stage 2 imports the
frozen Stage 1 CPU core and adds runtime-only grid inference, simultaneity
clustering, cluster timing/state options, and bounded global sequence search.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Mapping, Sequence

import v145_rhythm_decoder as stage1


MIN_QUANTUM_SECONDS = 0.050
MAX_QUANTUM_SECONDS = 0.500
MAX_DELTA_DIVISOR = 4
MIN_EVIDENCE_EVENTS = 4
MIN_GRID_SUPPORT = 0.80
SUPPORTED_NORMALIZED_RESIDUAL = 0.18
MAX_MEDIAN_NORMALIZED_RESIDUAL = 0.12
SIMULTANEITY_WINDOW_RATIO = 0.30
MAX_SHIFT_STEPS = 1
MAX_FRET = 24
MAX_FRET_SPAN = 7
BEAM_WIDTH = 64
LOCAL_STATE_WEIGHT = 0.25
TRANSITION_WEIGHT = 1.0


@dataclass(frozen=True)
class InferredTimingGrid:
    quantum: float
    phase: float
    support: float
    median_normalized_residual: float
    mean_normalized_residual: float
    evidence_count: int
    candidate_count: int


@dataclass(frozen=True)
class EvidenceCluster:
    cluster_index: int
    events: tuple[stage1.EvidenceEvent, ...]


@dataclass(frozen=True)
class ClusterOption:
    cluster_index: int
    onset: float
    timing_candidates: tuple[stage1.TimingCandidate, ...]
    guitar_state: stage1.GuitarState
    local_cost: float


@dataclass(frozen=True)
class GlobalDecodeResult:
    grid: InferredTimingGrid | None
    decoded_notes: tuple[stage1.DecodedNote, ...]
    undecoded_source_indices: tuple[int, ...]
    cluster_count: int
    decoded_cluster_count: int


@dataclass(frozen=True)
class _BeamPath:
    total_cost: float
    options: tuple[ClusterOption, ...]


def _round6(value: float) -> float:
    return round(float(value), 6)


def _candidate_quantums(evidence: Sequence[stage1.EvidenceEvent]) -> tuple[float, ...]:
    onsets = sorted(event.onset for event in evidence)
    deltas = [later - earlier for earlier, later in zip(onsets, onsets[1:]) if later > earlier]
    if not deltas:
        return tuple()

    bases = list(deltas)
    bases.append(float(median(deltas)))
    candidates: set[float] = set()
    for delta in bases:
        for divisor in range(1, MAX_DELTA_DIVISOR + 1):
            quantum = delta / divisor
            if MIN_QUANTUM_SECONDS <= quantum <= MAX_QUANTUM_SECONDS:
                candidates.add(_round6(quantum))
    return tuple(sorted(candidates))


def _phase_candidates(evidence: Sequence[stage1.EvidenceEvent], quantum: float) -> tuple[float, ...]:
    phases = {0.0}
    for event in evidence:
        phase = event.onset % quantum
        if math.isclose(phase, quantum, abs_tol=1e-9):
            phase = 0.0
        phases.add(_round6(phase))
    return tuple(sorted(phases))


def _nearest_grid_residual(onset: float, quantum: float, phase: float) -> float:
    relative = (onset - phase) / quantum
    lower = math.floor(relative)
    upper = math.ceil(relative)
    lower_point = phase + lower * quantum
    upper_point = phase + upper * quantum
    return min(abs(onset - lower_point), abs(onset - upper_point))


def _grid_metrics(
    evidence: Sequence[stage1.EvidenceEvent],
    quantum: float,
    phase: float,
) -> tuple[float, float, float]:
    residuals = [
        _nearest_grid_residual(event.onset, quantum, phase) / quantum
        for event in evidence
    ]
    support = sum(value <= SUPPORTED_NORMALIZED_RESIDUAL for value in residuals) / len(residuals)
    return (
        float(support),
        float(median(residuals)),
        float(sum(residuals) / len(residuals)),
    )


def infer_timing_grid_from_evidence(
    evidence: Sequence[stage1.EvidenceEvent],
) -> InferredTimingGrid | None:
    """Infer a supported timing grid from generated evidence only."""

    if len(evidence) < MIN_EVIDENCE_EVENTS:
        return None

    quantums = _candidate_quantums(evidence)
    eligible: list[InferredTimingGrid] = []
    candidate_count = 0
    for quantum in quantums:
        for phase in _phase_candidates(evidence, quantum):
            candidate_count += 1
            support, median_residual, mean_residual = _grid_metrics(evidence, quantum, phase)
            if support < MIN_GRID_SUPPORT:
                continue
            if median_residual > MAX_MEDIAN_NORMALIZED_RESIDUAL:
                continue
            eligible.append(
                InferredTimingGrid(
                    quantum=quantum,
                    phase=phase,
                    support=support,
                    median_normalized_residual=median_residual,
                    mean_normalized_residual=mean_residual,
                    evidence_count=len(evidence),
                    candidate_count=candidate_count,
                )
            )

    if not eligible:
        return None

    winner = min(
        eligible,
        key=lambda grid: (
            -grid.support,
            grid.median_normalized_residual,
            grid.mean_normalized_residual,
            -grid.quantum,
            grid.phase,
        ),
    )
    return InferredTimingGrid(
        quantum=winner.quantum,
        phase=winner.phase,
        support=winner.support,
        median_normalized_residual=winner.median_normalized_residual,
        mean_normalized_residual=winner.mean_normalized_residual,
        evidence_count=winner.evidence_count,
        candidate_count=candidate_count,
    )


def infer_timing_grid(events: Sequence[Mapping[str, object]]) -> InferredTimingGrid | None:
    return infer_timing_grid_from_evidence(stage1.normalize_rhythm_events(events))


def cluster_evidence(
    evidence: Sequence[stage1.EvidenceEvent],
    quantum: float,
) -> tuple[EvidenceCluster, ...]:
    """Group generated events that belong to the same raw attack window."""

    if not math.isfinite(quantum) or quantum <= 0:
        raise ValueError("quantum must be finite and positive")

    ordered = sorted(evidence, key=lambda event: (event.onset, event.midi, event.source_index))
    if not ordered:
        return tuple()

    window = SIMULTANEITY_WINDOW_RATIO * quantum
    clusters: list[EvidenceCluster] = []
    current: list[stage1.EvidenceEvent] = []
    anchor = 0.0

    for event in ordered:
        if not current:
            current = [event]
            anchor = event.onset
            continue
        if event.onset - anchor <= window + 1e-12:
            current.append(event)
            continue
        clusters.append(EvidenceCluster(cluster_index=len(clusters), events=tuple(current)))
        current = [event]
        anchor = event.onset

    clusters.append(EvidenceCluster(cluster_index=len(clusters), events=tuple(current)))
    return tuple(clusters)


def _timing_candidates_for_grid(
    event: stage1.EvidenceEvent,
    grid: InferredTimingGrid,
) -> tuple[stage1.TimingCandidate, ...]:
    """Reuse Stage 1 candidate generation on a phase-shifted coordinate system."""

    relative_onset = event.onset - grid.phase
    if relative_onset < 0:
        relative_onset = 0.0
    shifted = stage1.EvidenceEvent(
        source_index=event.source_index,
        midi=event.midi,
        onset=relative_onset,
        duration=event.duration,
        confidence=event.confidence,
    )
    base_candidates = stage1.timing_candidates_for_event(
        shifted,
        grid.quantum,
        max_shift_steps=MAX_SHIFT_STEPS,
    )

    candidates: list[stage1.TimingCandidate] = []
    for base in base_candidates:
        candidate_onset = _round6(base.candidate_onset + grid.phase)
        if candidate_onset < 0:
            continue
        timing_cost = abs(candidate_onset - event.onset) / grid.quantum
        candidates.append(
            stage1.TimingCandidate(
                source_index=event.source_index,
                midi=event.midi,
                raw_onset=event.onset,
                candidate_onset=candidate_onset,
                duration=event.duration,
                confidence=event.confidence,
                shift_steps=base.shift_steps,
                timing_cost=float(timing_cost),
            )
        )

    return tuple(
        sorted(
            candidates,
            key=lambda row: (
                row.timing_cost,
                abs(row.shift_steps),
                row.candidate_onset,
                row.source_index,
            ),
        )
    )


def cluster_options(
    cluster: EvidenceCluster,
    grid: InferredTimingGrid,
) -> tuple[ClusterOption, ...]:
    """Build common-onset, physically valid options for one simultaneity cluster."""

    if not cluster.events or len(cluster.events) > 6:
        return tuple()

    per_event: list[dict[float, stage1.TimingCandidate]] = []
    for event in cluster.events:
        candidates = _timing_candidates_for_grid(event, grid)
        per_event.append({row.candidate_onset: row for row in candidates})
    if any(not mapping for mapping in per_event):
        return tuple()

    common_onsets = set(per_event[0])
    for mapping in per_event[1:]:
        common_onsets.intersection_update(mapping)
    if not common_onsets:
        return tuple()

    midis = [event.midi for event in cluster.events]
    states = stage1.enumerate_guitar_states(
        midis,
        max_fret=MAX_FRET,
        max_fret_span=MAX_FRET_SPAN,
    )
    if not states:
        return tuple()

    options: list[ClusterOption] = []
    for onset in sorted(common_onsets):
        timing_rows = tuple(
            sorted(
                (mapping[onset] for mapping in per_event),
                key=lambda row: (row.midi, row.source_index),
            )
        )
        timing_cost = sum(row.timing_cost for row in timing_rows)
        for state in states:
            options.append(
                ClusterOption(
                    cluster_index=cluster.cluster_index,
                    onset=onset,
                    timing_candidates=timing_rows,
                    guitar_state=state,
                    local_cost=float(timing_cost + LOCAL_STATE_WEIGHT * state.local_cost),
                )
            )

    return tuple(sorted(options, key=_option_sort_key))


def _state_inventory(state: stage1.GuitarState) -> tuple[tuple[int, int, int], ...]:
    return tuple((row.midi, row.string, row.fret) for row in state.positions)


def _option_sort_key(option: ClusterOption) -> tuple[object, ...]:
    return (
        option.local_cost,
        option.onset,
        _state_inventory(option.guitar_state),
    )


def _path_sort_key(path: _BeamPath) -> tuple[object, ...]:
    return (
        path.total_cost,
        tuple(option.onset for option in path.options),
        tuple(_state_inventory(option.guitar_state) for option in path.options),
    )


def select_global_sequence(
    clusters: Sequence[EvidenceCluster],
    grid: InferredTimingGrid,
) -> tuple[tuple[ClusterOption, ...], tuple[int, ...]]:
    """Choose a deterministic bounded global path across decodable clusters."""

    beam: list[_BeamPath] = [_BeamPath(total_cost=0.0, options=tuple())]
    undecoded_sources: list[int] = []

    for cluster in clusters:
        options = cluster_options(cluster, grid)
        if not options:
            undecoded_sources.extend(event.source_index for event in cluster.events)
            continue

        extended: list[_BeamPath] = []
        for path in beam:
            previous_option = path.options[-1] if path.options else None
            for option in options:
                if previous_option is not None and option.onset <= previous_option.onset:
                    continue
                transition = stage1.state_transition_cost(
                    previous_option.guitar_state if previous_option else None,
                    option.guitar_state,
                )
                extended.append(
                    _BeamPath(
                        total_cost=float(
                            path.total_cost
                            + option.local_cost
                            + TRANSITION_WEIGHT * transition
                        ),
                        options=path.options + (option,),
                    )
                )

        if not extended:
            undecoded_sources.extend(event.source_index for event in cluster.events)
            continue

        extended.sort(key=_path_sort_key)
        beam = extended[:BEAM_WIDTH]

    if not beam:
        return tuple(), tuple(sorted(set(undecoded_sources)))
    winner = min(beam, key=_path_sort_key)
    return winner.options, tuple(sorted(set(undecoded_sources)))


def _map_option_positions(
    option: ClusterOption,
) -> tuple[tuple[stage1.TimingCandidate, stage1.GuitarPosition], ...]:
    candidates = sorted(option.timing_candidates, key=lambda row: (row.midi, row.source_index))
    positions = sorted(option.guitar_state.positions, key=lambda row: (row.midi, row.string, row.fret))
    if [row.midi for row in candidates] != [row.midi for row in positions]:
        raise ValueError("cluster option pitch inventory mismatch")
    return tuple(zip(candidates, positions))


def decode_global_rhythm_sequence(
    events: Sequence[Mapping[str, object]],
) -> GlobalDecodeResult:
    """Infer a grid and globally decode generated Rhythm evidence on CPU."""

    evidence = stage1.normalize_rhythm_events(events)
    grid = infer_timing_grid_from_evidence(evidence)
    if grid is None:
        return GlobalDecodeResult(
            grid=None,
            decoded_notes=tuple(),
            undecoded_source_indices=tuple(sorted(event.source_index for event in evidence)),
            cluster_count=0,
            decoded_cluster_count=0,
        )

    clusters = cluster_evidence(evidence, grid.quantum)
    selected, undecoded = select_global_sequence(clusters, grid)
    decoded: list[stage1.DecodedNote] = []
    seen_sources: set[int] = set()

    for option in selected:
        for timing, position in _map_option_positions(option):
            if timing.source_index in seen_sources:
                raise RuntimeError("source event reused by global sequence")
            seen_sources.add(timing.source_index)
            decoded.append(
                stage1.DecodedNote(
                    source_index=timing.source_index,
                    midi=timing.midi,
                    raw_onset=timing.raw_onset,
                    onset=timing.candidate_onset,
                    duration=timing.duration,
                    confidence=timing.confidence,
                    timing_cost=timing.timing_cost,
                    string=position.string,
                    fret=position.fret,
                )
            )

    all_evidence_sources = {event.source_index for event in evidence}
    undecoded_sources = sorted((all_evidence_sources - seen_sources) | set(undecoded))
    decoded.sort(key=lambda row: (row.onset, row.midi, row.source_index))
    return GlobalDecodeResult(
        grid=grid,
        decoded_notes=tuple(decoded),
        undecoded_source_indices=tuple(undecoded_sources),
        cluster_count=len(clusters),
        decoded_cluster_count=len(selected),
    )
