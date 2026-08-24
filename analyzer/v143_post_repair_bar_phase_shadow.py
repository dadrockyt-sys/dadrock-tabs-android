from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from statistics import mean, median
from typing import Any, Sequence

from v143_reference_free_bar_phase_consensus import (
    BarPhaseConsensus,
    estimate_reference_free_bar_phase_consensus_from_samples,
)


BEATS_PER_MEASURE = 4
MIN_WINDOW_BEATS = 32


@dataclass(frozen=True)
class PostRepairBarPhaseAssessment:
    inherited_downbeat_index_mod4: int
    inherited_first_beat_in_measure: int
    preferred_downbeat_index_mod4: int
    preferred_first_beat_in_measure: int
    window_count: int
    preferred_window_vote_count: int
    preferred_window_vote_fraction: float
    preferred_weighted_vote_fraction: float
    full_consensus_signal_count: int
    full_consensus_confidence: float
    full_winner_matches_preferred: bool
    robust_preference: bool
    phase_change_recommended: bool
    windows: tuple[dict[str, Any], ...]
    aggregate_candidates: tuple[dict[str, Any], ...]

    def diagnostics(self) -> dict[str, Any]:
        return {
            "inheritedDownbeatIndexMod4": int(self.inherited_downbeat_index_mod4),
            "inheritedFirstBeatInMeasure": int(self.inherited_first_beat_in_measure),
            "preferredDownbeatIndexMod4": int(self.preferred_downbeat_index_mod4),
            "preferredFirstBeatInMeasure": int(self.preferred_first_beat_in_measure),
            "windowCount": int(self.window_count),
            "preferredWindowVoteCount": int(self.preferred_window_vote_count),
            "preferredWindowVoteFraction": float(self.preferred_window_vote_fraction),
            "preferredWeightedVoteFraction": float(self.preferred_weighted_vote_fraction),
            "fullConsensusSignalCount": int(self.full_consensus_signal_count),
            "fullConsensusConfidence": float(self.full_consensus_confidence),
            "fullWinnerMatchesPreferred": bool(self.full_winner_matches_preferred),
            "robustPreference": bool(self.robust_preference),
            "phaseChangeRecommended": bool(self.phase_change_recommended),
            "windows": [dict(value) for value in self.windows],
            "aggregateCandidates": [dict(value) for value in self.aggregate_candidates],
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _aligned_floor(value: int) -> int:
    return max(0, int(value) - (int(value) % BEATS_PER_MEASURE))


def _window_specs(beat_count: int) -> tuple[tuple[str, int, int], ...]:
    n = int(beat_count)
    if n < MIN_WINDOW_BEATS:
        raise ValueError(f"At least {MIN_WINDOW_BEATS} repaired beats are required")

    half = _aligned_floor(n // 2)
    quarter = _aligned_floor(n // 4)
    three_quarter = _aligned_floor(3 * n // 4)
    trim = BEATS_PER_MEASURE

    raw = [
        ("full", 0, n),
        ("trim-one-bar", trim, n - trim),
        ("first-half", 0, half),
        ("second-half", half, n),
        ("middle-half", quarter, three_quarter),
        ("first-three-quarters", 0, three_quarter),
        ("last-three-quarters", quarter, n),
    ]
    specs: list[tuple[str, int, int]] = []
    seen: set[tuple[int, int]] = set()
    for name, start, end in raw:
        start = _aligned_floor(start)
        end = min(n, int(end))
        if end - start < MIN_WINDOW_BEATS:
            continue
        key = (start, end)
        if key in seen:
            continue
        seen.add(key)
        specs.append((name, start, end))
    return tuple(specs)


def _window_weight(consensus: BarPhaseConsensus) -> float:
    # Confidence is intentionally not used as a hard fixture-tuned threshold.
    # Every sufficiently long audio window gets a small base vote, while stronger
    # multi-signal consensus contributes proportionally more weight.
    return float(
        0.25
        + 0.50 * max(0.0, min(1.0, float(consensus.confidence)))
        + 0.25 * (int(consensus.consensus_signal_count) / 4.0)
    )


def assess_post_repair_bar_phase_from_samples(
    samples: Any,
    sample_rate: int,
    repaired_beat_times: Sequence[float],
    *,
    inherited_downbeat_index_mod4: int,
) -> PostRepairBarPhaseAssessment:
    """Assess bar phase again after beat-grid repair using audio only.

    A repaired pulse train is a new index sequence. If the raw tracker contained
    inserted/dropped/sub-beat pulses, a bar phase originally defined by raw
    ``sequence_index % 4`` cannot safely be treated as invariant. This shadow
    therefore re-scores 4/4 phase on several long, bar-aligned windows of the
    repaired pulse train. It does not accept labels, target measures, song
    identity, or professional-reference data and does not mutate runtime output.
    """
    beats = tuple(float(value) for value in repaired_beat_times)
    if any(not math.isfinite(value) for value in beats):
        raise ValueError("repaired beat times must be finite")
    if any(right <= left for left, right in zip(beats[:-1], beats[1:])):
        raise ValueError("repaired beat times must be strictly increasing")

    inherited = int(inherited_downbeat_index_mod4) % BEATS_PER_MEASURE
    inherited_first = int((-inherited) % BEATS_PER_MEASURE)
    specs = _window_specs(len(beats))

    windows: list[dict[str, Any]] = []
    vote_counts: Counter[int] = Counter()
    weighted_votes = {phase: 0.0 for phase in range(BEATS_PER_MEASURE)}
    candidate_scores: dict[int, list[float]] = {
        phase: [] for phase in range(BEATS_PER_MEASURE)
    }
    full_consensus: BarPhaseConsensus | None = None

    for name, start, end in specs:
        # Window starts are aligned to a multiple of four repaired beats, so the
        # local phase residue is identical to the full repaired sequence residue.
        if start % BEATS_PER_MEASURE != 0:
            raise RuntimeError("phase shadow window start is not bar-residue aligned")
        consensus = estimate_reference_free_bar_phase_consensus_from_samples(
            samples,
            int(sample_rate),
            beats[start:end],
        )
        if name == "full":
            full_consensus = consensus
        winner = int(consensus.winner_downbeat_index_mod4)
        weight = _window_weight(consensus)
        vote_counts[winner] += 1
        weighted_votes[winner] += weight
        by_phase = {
            int(candidate["downbeatIndexMod4"]): float(candidate["combinedScore"])
            for candidate in consensus.candidates
        }
        for phase in range(BEATS_PER_MEASURE):
            candidate_scores[phase].append(float(by_phase[phase]))
        windows.append(
            {
                "name": name,
                "startBeatIndex": int(start),
                "endBeatIndexExclusive": int(end),
                "beatCount": int(end - start),
                "winnerDownbeatIndexMod4": winner,
                "winnerFirstBeatInMeasure": int((-winner) % BEATS_PER_MEASURE),
                "confidence": float(consensus.confidence),
                "consensusSignalCount": int(consensus.consensus_signal_count),
                "stableAcrossHalves": bool(consensus.stable_across_halves),
                "signalWinners": dict(consensus.signal_winners),
                "voteWeight": float(weight),
                "candidateCombinedScores": {
                    str(phase): float(by_phase[phase])
                    for phase in range(BEATS_PER_MEASURE)
                },
            }
        )

    if full_consensus is None or not windows:
        raise RuntimeError("full post-repair phase window missing")

    aggregate_candidates: list[dict[str, Any]] = []
    for phase in range(BEATS_PER_MEASURE):
        scores = candidate_scores[phase]
        aggregate_candidates.append(
            {
                "downbeatIndexMod4": int(phase),
                "firstBeatInMeasure": int((-phase) % BEATS_PER_MEASURE),
                "windowVoteCount": int(vote_counts[phase]),
                "weightedVote": float(weighted_votes[phase]),
                "meanCombinedScore": float(mean(scores)),
                "medianCombinedScore": float(median(scores)),
                "minimumCombinedScore": float(min(scores)),
            }
        )

    preferred = max(
        range(BEATS_PER_MEASURE),
        key=lambda phase: (
            int(vote_counts[phase]),
            float(weighted_votes[phase]),
            float(median(candidate_scores[phase])),
            -phase,
        ),
    )
    total_weight = max(sum(weighted_votes.values()), 1.0e-12)
    preferred_vote_count = int(vote_counts[preferred])
    preferred_vote_fraction = preferred_vote_count / float(len(windows))
    preferred_weighted_fraction = float(weighted_votes[preferred] / total_weight)
    full_matches = int(full_consensus.winner_downbeat_index_mod4) == int(preferred)

    # This is a deliberately generic robustness gate, not an acceptance of the
    # fixture's winning phase. A super-majority of long windows, agreement with
    # the full-file winner, and at least two independent full-file signal votes
    # are required before the shadow can recommend replacing inherited phase.
    required_votes = max(3, int(math.ceil(0.60 * len(windows))))
    robust = bool(
        full_matches
        and preferred_vote_count >= required_votes
        and preferred_weighted_fraction >= 0.55
        and int(full_consensus.consensus_signal_count) >= 2
    )
    change = bool(robust and int(preferred) != inherited)

    return PostRepairBarPhaseAssessment(
        inherited_downbeat_index_mod4=inherited,
        inherited_first_beat_in_measure=inherited_first,
        preferred_downbeat_index_mod4=int(preferred),
        preferred_first_beat_in_measure=int((-preferred) % BEATS_PER_MEASURE),
        window_count=len(windows),
        preferred_window_vote_count=preferred_vote_count,
        preferred_window_vote_fraction=float(preferred_vote_fraction),
        preferred_weighted_vote_fraction=float(preferred_weighted_fraction),
        full_consensus_signal_count=int(full_consensus.consensus_signal_count),
        full_consensus_confidence=float(full_consensus.confidence),
        full_winner_matches_preferred=bool(full_matches),
        robust_preference=bool(robust),
        phase_change_recommended=bool(change),
        windows=tuple(windows),
        aggregate_candidates=tuple(aggregate_candidates),
    )


__all__ = [
    "PostRepairBarPhaseAssessment",
    "assess_post_repair_bar_phase_from_samples",
]
