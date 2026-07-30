from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median
from typing import Any

INTRO_START_MEASURE = 1
INTRO_END_MEASURE = 16
PAIR_LENGTH = 2
MIN_PAIR_SUPPORT = 3
STEP_TOLERANCE = 1


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


def stabilize_intro_motif(
    render_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Stabilize repeated intro drawing events without changing source notes.

    Only measures 1-16 are considered. Events outside the intro pass through unchanged.
    Inside the intro, note identities must repeat across at least three two-measure pairs.
    Surviving attacks are snapped to the median sixteenth-note step for that identity.
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

    median_steps = {
        signature: int(
            round(
                median(
                    _safe_int(event.get("quantizedStep"))
                    for event in observations[signature]
                )
            )
        )
        for signature in accepted_signatures
    }

    stabilized_intro: list[dict[str, Any]] = []
    rejected_intro: list[dict[str, Any]] = []
    moved_count = 0

    for event in intro_events:
        signature = _signature(event)
        if signature not in accepted_signatures:
            rejected_intro.append(event)
            continue

        target_step = median_steps[signature]
        original_step = _safe_int(event.get("quantizedStep"))
        if abs(original_step - target_step) <= STEP_TOLERANCE:
            resolved_step = target_step
        else:
            # Keep evidence-backed outliers rather than forcing a large timing change.
            resolved_step = original_step

        item = dict(event)
        item["motifOriginalStep"] = original_step
        item["motifConsensusStep"] = target_step
        item["motifSupportPairs"] = support_counts[signature]
        item["motifStabilized"] = True
        item["quantizedStep"] = resolved_step
        item["positionInMeasure"] = round(resolved_step / 16.0, 6)
        if resolved_step != original_step:
            moved_count += 1
        stabilized_intro.append(item)

    # Remove exact duplicates introduced by median snapping while keeping best source evidence.
    deduped: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    for event in stabilized_intro:
        key = (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
        previous = deduped.get(key)
        quality = (
            _safe_float(event.get("confidence")),
            _safe_float(event.get("duration")),
            -_safe_int(event.get("sourceEventIndex")),
        )
        previous_quality = (
            _safe_float(previous.get("confidence")),
            _safe_float(previous.get("duration")),
            -_safe_int(previous.get("sourceEventIndex")),
        ) if previous else None
        if previous is None or quality > previous_quality:
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
        "pairCount": 8,
        "minimumPairSupport": MIN_PAIR_SUPPORT,
        "inputIntroEventCount": len(intro_events),
        "outputIntroEventCount": len(deduped),
        "rejectedLowSupportIntroEvents": len(rejected_intro),
        "medianSnappedIntroEvents": moved_count,
        "acceptedMotifSignatureCount": len(accepted_signatures),
        "motifEventCount": len(motif_events),
        "supportHistogram": dict(sorted(Counter(support_counts.values()).items())),
        "readOnly": True,
    }
    return motif_events, diagnostics
