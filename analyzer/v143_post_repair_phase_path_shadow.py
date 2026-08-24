from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Any, Sequence

from v143_reference_free_bar_phase_consensus import (
    estimate_reference_free_bar_phase_consensus_from_samples,
)


BEATS_PER_MEASURE = 4
LOCAL_WINDOW_BEATS = 64
LOCAL_STRIDE_BEATS = 16
MIN_WINDOW_BEATS = 32


@dataclass(frozen=True)
class PhasePathWindow:
    name: str
    start_beat_index: int
    end_beat_index_exclusive: int
    winner_downbeat_index_mod4: int
    confidence: float
    consensus_signal_count: int
    stable_across_halves: bool
    signal_winners: dict[str, int]
    candidate_combined_scores: dict[int, float]

    @property
    def independent_signal_supported(self) -> bool:
        return int(self.consensus_signal_count) >= 2

    @property
    def strong(self) -> bool:
        # No fixture-tuned confidence threshold: a local window is considered
        # strong only when at least two independent signals select its winner and
        # that winner is stable between the window's two halves.
        return bool(self.independent_signal_supported and self.stable_across_halves)

    def diagnostics(self) -> dict[str, Any]:
        return {
            "name": str(self.name),
            "startBeatIndex": int(self.start_beat_index),
            "endBeatIndexExclusive": int(self.end_beat_index_exclusive),
            "beatCount": int(self.end_beat_index_exclusive - self.start_beat_index),
            "winnerDownbeatIndexMod4": int(self.winner_downbeat_index_mod4),
            "winnerFirstBeatInMeasure": int((-self.winner_downbeat_index_mod4) % BEATS_PER_MEASURE),
            "confidence": float(self.confidence),
            "consensusSignalCount": int(self.consensus_signal_count),
            "stableAcrossHalves": bool(self.stable_across_halves),
            "independentSignalSupported": bool(self.independent_signal_supported),
            "strong": bool(self.strong),
            "signalWinners": dict(self.signal_winners),
            "candidateCombinedScores": {
                str(int(phase)): float(score)
                for phase, score in sorted(self.candidate_combined_scores.items())
            },
        }


def _aligned_floor(value: int) -> int:
    return max(0, int(value) - (int(value) % BEATS_PER_MEASURE))


def local_window_specs(
    beat_count: int,
    *,
    window_beats: int = LOCAL_WINDOW_BEATS,
    stride_beats: int = LOCAL_STRIDE_BEATS,
) -> tuple[tuple[str, int, int], ...]:
    n = int(beat_count)
    window = _aligned_floor(int(window_beats))
    stride = _aligned_floor(int(stride_beats))
    if window < MIN_WINDOW_BEATS:
        raise ValueError(f"window_beats must be at least {MIN_WINDOW_BEATS}")
    if stride < BEATS_PER_MEASURE:
        raise ValueError("stride_beats must be at least one 4/4 measure")
    if n < MIN_WINDOW_BEATS:
        raise ValueError(f"At least {MIN_WINDOW_BEATS} repaired beats are required")

    specs: list[tuple[str, int, int]] = []
    if n <= window:
        return (("local-000", 0, n),)

    index = 0
    start = 0
    while start + window <= n:
        specs.append((f"local-{index:03d}", int(start), int(start + window)))
        index += 1
        start += stride

    # Include an aligned tail window so the end of the repaired pulse train is
    # represented even when its length is not an exact stride multiple.
    tail_start = _aligned_floor(n - window)
    tail = (f"local-{index:03d}-tail", int(tail_start), int(n))
    if not specs or (tail[1], tail[2]) != (specs[-1][1], specs[-1][2]):
        if tail[2] - tail[1] >= MIN_WINDOW_BEATS:
            specs.append(tail)

    seen: set[tuple[int, int]] = set()
    output: list[tuple[str, int, int]] = []
    for name, start, end in specs:
        if start % BEATS_PER_MEASURE != 0:
            raise RuntimeError("local phase window start escaped 4/4 residue alignment")
        key = (int(start), int(end))
        if key in seen:
            continue
        seen.add(key)
        output.append((name, int(start), int(end)))
    return tuple(output)


def _strong_runs(windows: Sequence[PhasePathWindow]) -> tuple[dict[str, Any], ...]:
    runs: list[dict[str, Any]] = []
    current: list[PhasePathWindow] = []

    def flush() -> None:
        nonlocal current
        if not current:
            return
        phase = int(current[0].winner_downbeat_index_mod4)
        runs.append(
            {
                "phase": phase,
                "firstBeatInMeasure": int((-phase) % BEATS_PER_MEASURE),
                "windowCount": len(current),
                "startBeatIndex": int(current[0].start_beat_index),
                "endBeatIndexExclusive": int(current[-1].end_beat_index_exclusive),
                "minimumConfidence": float(min(item.confidence for item in current)),
                "meanConfidence": float(sum(item.confidence for item in current) / len(current)),
            }
        )
        current = []

    for window in windows:
        if not window.strong:
            flush()
            continue
        if current and int(current[-1].winner_downbeat_index_mod4) != int(window.winner_downbeat_index_mod4):
            flush()
        current.append(window)
    flush()
    return tuple(runs)


def summarize_phase_path(windows: Sequence[PhasePathWindow]) -> dict[str, Any]:
    values = tuple(windows)
    if not values:
        raise ValueError("phase path requires at least one local window")
    phase_counts = Counter(int(item.winner_downbeat_index_mod4) for item in values)
    strong_values = tuple(item for item in values if item.strong)
    strong_phase_counts = Counter(int(item.winner_downbeat_index_mod4) for item in strong_values)
    runs = _strong_runs(values)
    transitions = []
    for left, right in zip(runs[:-1], runs[1:]):
        if int(left["phase"]) == int(right["phase"]):
            continue
        transitions.append(
            {
                "fromPhase": int(left["phase"]),
                "toPhase": int(right["phase"]),
                "leftEndBeatIndexExclusive": int(left["endBeatIndexExclusive"]),
                "rightStartBeatIndex": int(right["startBeatIndex"]),
            }
        )
    return {
        "windowCount": len(values),
        "strongWindowCount": len(strong_values),
        "phaseWindowCounts": {str(key): int(value) for key, value in sorted(phase_counts.items())},
        "strongPhaseWindowCounts": {str(key): int(value) for key, value in sorted(strong_phase_counts.items())},
        "strongRuns": [dict(item) for item in runs],
        "strongTransitionCount": len(transitions),
        "strongTransitions": transitions,
        "multipleStrongPhasesObserved": len(strong_phase_counts) > 1,
        "referenceFree": True,
        "runtimeLabelsRequired": False,
        "productionModified": False,
    }


def assess_post_repair_phase_path_from_samples(
    samples: Any,
    sample_rate: int,
    repaired_beat_times: Sequence[float],
    *,
    window_beats: int = LOCAL_WINDOW_BEATS,
    stride_beats: int = LOCAL_STRIDE_BEATS,
) -> dict[str, Any]:
    """Trace local 4/4 phase preference along a repaired beat grid using audio only.

    This is diagnostic-only. It deliberately does not choose a runtime phase or
    mutate beat times. Local windows start on the same repaired modulo-4 residue,
    so winner changes reflect changing audio evidence against a fixed pulse-index
    convention rather than an accidental window-index offset.
    """
    beats = tuple(float(value) for value in repaired_beat_times)
    if any(not math.isfinite(value) for value in beats):
        raise ValueError("repaired beat times must be finite")
    if any(right <= left for left, right in zip(beats[:-1], beats[1:])):
        raise ValueError("repaired beat times must be strictly increasing")

    windows: list[PhasePathWindow] = []
    for name, start, end in local_window_specs(
        len(beats),
        window_beats=int(window_beats),
        stride_beats=int(stride_beats),
    ):
        consensus = estimate_reference_free_bar_phase_consensus_from_samples(
            samples,
            int(sample_rate),
            beats[start:end],
        )
        candidate_scores = {
            int(item["downbeatIndexMod4"]): float(item["combinedScore"])
            for item in consensus.candidates
        }
        windows.append(
            PhasePathWindow(
                name=str(name),
                start_beat_index=int(start),
                end_beat_index_exclusive=int(end),
                winner_downbeat_index_mod4=int(consensus.winner_downbeat_index_mod4),
                confidence=float(consensus.confidence),
                consensus_signal_count=int(consensus.consensus_signal_count),
                stable_across_halves=bool(consensus.stable_across_halves),
                signal_winners=dict(consensus.signal_winners),
                candidate_combined_scores=candidate_scores,
            )
        )

    summary = summarize_phase_path(windows)
    return {
        "schemaVersion": 1,
        "mode": "v143-post-repair-local-phase-path-shadow",
        "windowBeats": int(_aligned_floor(window_beats)),
        "strideBeats": int(_aligned_floor(stride_beats)),
        "beatCount": len(beats),
        "windows": [item.diagnostics() for item in windows],
        "summary": summary,
        "referenceFree": True,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
        "runtimePhaseChanged": False,
        "liveRhythmOutputChanged": False,
        "productionModified": False,
    }


__all__ = [
    "BEATS_PER_MEASURE",
    "LOCAL_WINDOW_BEATS",
    "LOCAL_STRIDE_BEATS",
    "MIN_WINDOW_BEATS",
    "PhasePathWindow",
    "local_window_specs",
    "summarize_phase_path",
    "assess_post_repair_phase_path_from_samples",
]
