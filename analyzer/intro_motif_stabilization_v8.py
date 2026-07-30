from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median
from typing import Any

INTRO_START_MEASURE = 1
INTRO_END_MEASURE = 16
PAIR_LENGTH = 2
PAIR_COUNT = 8
MIN_PAIR_SUPPORT = 3
MAX_PAIR_PHASE_SHIFT = 4


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _pair_index(measure_number: int) -> int:
    return max(0, (measure_number - INTRO_START_MEASURE) // PAIR_LENGTH)


def _measure_offset(measure_number: int) -> int:
    return (measure_number - INTRO_START_MEASURE) % PAIR_LENGTH


def _signature(event: dict[str, Any]) -> tuple[int, int, int]:
    return (
        _measure_offset(_safe_int(event.get("measureNumber"), 1)),
        _safe_int(event.get("stringIndex")),
        _safe_int(event.get("fret")),
    )


def _event_quality(event: dict[str, Any], target_step: int) -> tuple[float, float, float, int]:
    return (
        -abs(_safe_int(event.get("quantizedStep")) - target_step),
        _safe_float(event.get("confidence")),
        _safe_float(event.get("duration")),
        -_safe_int(event.get("sourceEventIndex")),
    )


def _best_event_per_pair_signature(
    intro_events: list[dict[str, Any]],
) -> dict[tuple[int, tuple[int, int, int]], dict[str, Any]]:
    best: dict[tuple[int, tuple[int, int, int]], dict[str, Any]] = {}
    for event in intro_events:
        pair_id = _pair_index(_safe_int(event.get("measureNumber"), INTRO_START_MEASURE))
        signature = _signature(event)
        key = (pair_id, signature)
        previous = best.get(key)
        step = _safe_int(event.get("quantizedStep"))
        if previous is None or _event_quality(event, step) > _event_quality(previous, step):
            best[key] = event
    return best


def _choose_canonical_pair(
    best_by_pair_signature: dict[tuple[int, tuple[int, int, int]], dict[str, Any]],
    accepted_signatures: set[tuple[int, int, int]],
) -> int:
    pair_scores: dict[int, tuple[int, float, float]] = {}
    for pair_id in range(PAIR_COUNT):
        events = [
            event
            for (candidate_pair, signature), event in best_by_pair_signature.items()
            if candidate_pair == pair_id and signature in accepted_signatures
        ]
        pair_scores[pair_id] = (
            len(events),
            sum(_safe_float(event.get("confidence")) for event in events),
            sum(_safe_float(event.get("duration")) for event in events),
        )
    return max(pair_scores, key=pair_scores.get)


def _estimate_pair_phase_offsets(
    best_by_pair_signature: dict[tuple[int, tuple[int, int, int]], dict[str, Any]],
    accepted_signatures: set[tuple[int, int, int]],
    canonical_pair: int,
) -> dict[int, int]:
    canonical_steps = {
        signature: _safe_int(event.get("quantizedStep"))
        for (pair_id, signature), event in best_by_pair_signature.items()
        if pair_id == canonical_pair and signature in accepted_signatures
    }

    offsets: dict[int, int] = {canonical_pair: 0}
    for pair_id in range(PAIR_COUNT):
        if pair_id == canonical_pair:
            continue

        deltas: list[int] = []
        for (candidate_pair, signature), event in best_by_pair_signature.items():
            if candidate_pair != pair_id or signature not in canonical_steps:
                continue
            delta = canonical_steps[signature] - _safe_int(event.get("quantizedStep"))
            if abs(delta) <= MAX_PAIR_PHASE_SHIFT:
                deltas.append(delta)

        offsets[pair_id] = int(round(median(deltas))) if deltas else 0

    return offsets


def stabilize_intro_motif(
    render_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Stabilize the repeated measures 1-16 intro without synthesizing notes.

    V8 first aligns each repeated two-measure pair to the strongest observed pair,
    then computes rhythmic consensus. This corrects whole-pair onset drift before
    median snapping while preserving every retained source note, string and fret.
    """

    intro_events = [
        dict(event)
        for event in render_events
        if INTRO_START_MEASURE
        <= _safe_int(event.get("measureNumber"), 0)
        <= INTRO_END_MEASURE
    ]
    outside_events = [
        dict(event)
        for event in render_events
        if not (
            INTRO_START_MEASURE
            <= _safe_int(event.get("measureNumber"), 0)
            <= INTRO_END_MEASURE
        )
    ]

    observations: dict[tuple[int, int, int], list[dict[str, Any]]] = defaultdict(list)
    pair_presence: dict[tuple[int, int, int], set[int]] = defaultdict(set)

    for event in intro_events:
        signature = _signature(event)
        observations[signature].append(event)
        pair_presence[signature].add(
            _pair_index(_safe_int(event.get("measureNumber"), INTRO_START_MEASURE))
        )

    support_counts = {
        signature: len(pair_ids)
        for signature, pair_ids in pair_presence.items()
    }
    accepted_signatures = {
        signature
        for signature, count in support_counts.items()
        if count >= MIN_PAIR_SUPPORT
    }

    best_initial = _best_event_per_pair_signature(intro_events)
    canonical_pair = _choose_canonical_pair(best_initial, accepted_signatures)
    pair_phase_offsets = _estimate_pair_phase_offsets(
        best_initial,
        accepted_signatures,
        canonical_pair,
    )

    adjusted_steps: dict[tuple[int, tuple[int, int, int]], int] = {}
    for (pair_id, signature), event in best_initial.items():
        adjusted_steps[(pair_id, signature)] = max(
            0,
            min(
                15,
                _safe_int(event.get("quantizedStep")) + pair_phase_offsets.get(pair_id, 0),
            ),
        )

    median_steps = {
        signature: int(round(median(
            adjusted_steps[(pair_id, candidate_signature)]
            for (pair_id, candidate_signature) in adjusted_steps
            if candidate_signature == signature
        )))
        for signature in accepted_signatures
    }

    slot_candidates: dict[tuple[int, int, int], list[tuple[int, int, int]]] = defaultdict(list)
    for signature in accepted_signatures:
        offset, string_index, _fret = signature
        slot_candidates[(offset, median_steps[signature], string_index)].append(signature)

    dominant_signatures: set[tuple[int, int, int]] = set()
    conflicting_signatures_removed = 0
    for candidates in slot_candidates.values():
        winner = max(
            candidates,
            key=lambda signature: (
                support_counts[signature],
                len(observations[signature]),
                -signature[2],
            ),
        )
        dominant_signatures.add(winner)
        conflicting_signatures_removed += max(0, len(candidates) - 1)

    best_by_pair_and_signature: dict[
        tuple[int, tuple[int, int, int]],
        dict[str, Any],
    ] = {}
    repeated_retriggers_removed = 0

    for event in intro_events:
        signature = _signature(event)
        if signature not in dominant_signatures:
            continue

        pair_id = _pair_index(_safe_int(event.get("measureNumber"), INTRO_START_MEASURE))
        key = (pair_id, signature)
        target_step = median_steps[signature] - pair_phase_offsets.get(pair_id, 0)
        previous = best_by_pair_and_signature.get(key)

        if previous is None or _event_quality(event, target_step) > _event_quality(previous, target_step):
            if previous is not None:
                repeated_retriggers_removed += 1
            best_by_pair_and_signature[key] = event
        else:
            repeated_retriggers_removed += 1

    stabilized_intro: list[dict[str, Any]] = []
    moved_count = 0
    phase_aligned_count = 0

    for (pair_id, signature), event in best_by_pair_and_signature.items():
        target_step = median_steps[signature]
        original_step = _safe_int(event.get("quantizedStep"))
        phase_offset = pair_phase_offsets.get(pair_id, 0)
        item = dict(event)
        item["motifOriginalStep"] = original_step
        item["motifPairPhaseOffset"] = phase_offset
        item["motifConsensusStep"] = target_step
        item["motifSupportPairs"] = support_counts[signature]
        item["motifCanonicalPair"] = canonical_pair
        item["motifStabilized"] = True
        item["quantizedStep"] = target_step
        item["positionInMeasure"] = round(target_step / 16.0, 6)
        if phase_offset:
            phase_aligned_count += 1
        if target_step != original_step:
            moved_count += 1
        stabilized_intro.append(item)

    deduped: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    snap_duplicates_removed = 0
    for event in stabilized_intro:
        key = (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
        previous = deduped.get(key)
        if previous is None:
            deduped[key] = event
            continue

        snap_duplicates_removed += 1
        if _event_quality(event, _safe_int(event.get("quantizedStep"))) > _event_quality(
            previous,
            _safe_int(previous.get("quantizedStep")),
        ):
            deduped[key] = event

    motif_events = list(deduped.values()) + outside_events
    motif_events.sort(
        key=lambda event: (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
    )

    diagnostics = {
        "introMeasureRange": [INTRO_START_MEASURE, INTRO_END_MEASURE],
        "pairLengthMeasures": PAIR_LENGTH,
        "pairCount": PAIR_COUNT,
        "minimumPairSupport": MIN_PAIR_SUPPORT,
        "canonicalPairIndex": canonical_pair,
        "pairPhaseOffsets": {str(key): value for key, value in sorted(pair_phase_offsets.items())},
        "maximumPairPhaseShift": MAX_PAIR_PHASE_SHIFT,
        "phaseAlignedIntroEvents": phase_aligned_count,
        "inputIntroEventCount": len(intro_events),
        "outputIntroEventCount": len(deduped),
        "rejectedLowSupportIntroEvents": sum(
            1 for event in intro_events if _signature(event) not in accepted_signatures
        ),
        "conflictingMotifSignaturesRemoved": conflicting_signatures_removed,
        "repeatedPairRetriggersRemoved": repeated_retriggers_removed,
        "medianSnapDuplicatesRemoved": snap_duplicates_removed,
        "medianSnappedIntroEvents": moved_count,
        "acceptedMotifSignatureCount": len(dominant_signatures),
        "motifEventCount": len(motif_events),
        "supportHistogram": dict(sorted(Counter(support_counts.values()).items())),
        "readOnly": True,
    }
    return motif_events, diagnostics
