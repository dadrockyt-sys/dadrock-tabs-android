from __future__ import annotations

from collections import defaultdict
from typing import Any

SIXTEENTH_STEPS = 16
ATTACK_CLUSTER_STEPS = 1
NEAR_DUPLICATE_STEPS = 1
MIN_DURATION_SECONDS = 0.045
SHORT_EVENT_SECONDS = 0.075
LOW_CONFIDENCE_THRESHOLD = 0.12


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _quantized_step(position: float, steps: int = SIXTEENTH_STEPS) -> int:
    return max(0, min(steps - 1, int(round(position * steps))))


def _event_quality(event: dict[str, Any]) -> tuple[float, float, int]:
    return (
        _safe_float(event.get("confidence")),
        _safe_float(event.get("duration")),
        -_safe_int(event.get("eventIndex")),
    )


def _group_by_measure(events: list[dict[str, Any]]) -> dict[int, list[dict[str, Any]]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        grouped[_safe_int(event.get("measureNumber"), 1)].append(event)
    return dict(grouped)


def _dedupe_same_attack(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    best: dict[tuple[int, int, int], dict[str, Any]] = {}
    removed = 0

    for event in events:
        key = (
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
        previous = best.get(key)
        if previous is None or _event_quality(event) > _event_quality(previous):
            if previous is not None:
                removed += 1
            best[key] = event
        else:
            removed += 1

    return sorted(
        best.values(),
        key=lambda item: (
            _safe_int(item.get("quantizedStep")),
            _safe_int(item.get("stringIndex")),
            _safe_int(item.get("fret")),
        ),
    ), removed


def _dedupe_nearby_retriggers(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int]:
    """Collapse same-note retriggers quantized within one sixteenth step."""
    by_note: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_note[
            (
                _safe_int(event.get("stringIndex")),
                _safe_int(event.get("fret")),
            )
        ].append(event)

    kept: list[dict[str, Any]] = []
    removed = 0
    for note_events in by_note.values():
        note_events.sort(key=lambda item: _safe_int(item.get("quantizedStep")))
        cluster: list[dict[str, Any]] = []

        def flush() -> None:
            nonlocal removed
            if not cluster:
                return
            winner = max(cluster, key=_event_quality)
            kept.append(winner)
            removed += len(cluster) - 1
            cluster.clear()

        for event in note_events:
            if not cluster:
                cluster.append(event)
                continue
            previous_step = _safe_int(cluster[-1].get("quantizedStep"))
            step = _safe_int(event.get("quantizedStep"))
            if step - previous_step <= NEAR_DUPLICATE_STEPS:
                cluster.append(event)
            else:
                flush()
                cluster.append(event)
        flush()

    kept.sort(
        key=lambda item: (
            _safe_int(item.get("quantizedStep")),
            _safe_int(item.get("stringIndex")),
            _safe_int(item.get("fret")),
        )
    )
    return kept, removed


def _suppress_weak_transients(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    kept: list[dict[str, Any]] = []
    removed = 0

    for event in events:
        duration = _safe_float(event.get("duration"))
        confidence = _safe_float(event.get("confidence"))
        step = _safe_int(event.get("quantizedStep"))
        neighboring_attack = any(
            other is not event
            and abs(_safe_int(other.get("quantizedStep")) - step) <= ATTACK_CLUSTER_STEPS
            for other in events
        )
        same_string_neighbor = any(
            other is not event
            and _safe_int(other.get("stringIndex")) == _safe_int(event.get("stringIndex"))
            and abs(_safe_int(other.get("quantizedStep")) - step) <= 2
            for other in events
        )

        low_confidence_transient = (
            duration > 0
            and duration < MIN_DURATION_SECONDS
            and confidence > 0
            and confidence < LOW_CONFIDENCE_THRESHOLD
            and not neighboring_attack
        )
        unscored_micro_transient = (
            duration > 0
            and duration < SHORT_EVENT_SECONDS
            and confidence <= 0
            and not neighboring_attack
            and same_string_neighbor
        )

        if low_confidence_transient or unscored_micro_transient:
            removed += 1
            continue

        kept.append(event)

    return kept, removed


def _assign_attack_groups(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    attack_id = 0
    previous_step: int | None = None
    groups: set[int] = set()
    rendered: list[dict[str, Any]] = []

    for event in sorted(
        events,
        key=lambda item: (
            _safe_int(item.get("quantizedStep")),
            _safe_int(item.get("stringIndex")),
        ),
    ):
        step = _safe_int(event.get("quantizedStep"))
        if previous_step is None or step - previous_step > ATTACK_CLUSTER_STEPS:
            attack_id += 1
        previous_step = step
        groups.add(attack_id)

        item = dict(event)
        item["attackGroup"] = attack_id
        item["positionInMeasure"] = round(step / SIXTEENTH_STEPS, 6)
        item["renderOnly"] = True
        rendered.append(item)

    return rendered, len(groups)


def clean_render_events(
    projected_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Create read-only drawing events without modifying protected analyzer events."""
    prepared: list[dict[str, Any]] = []
    for event in projected_events:
        item = dict(event)
        item["sourceEventIndex"] = _safe_int(event.get("eventIndex"))
        item["quantizedStep"] = _quantized_step(
            _safe_float(event.get("positionInMeasure"))
        )
        prepared.append(item)

    grouped_measures = _group_by_measure(prepared)
    rendered: list[dict[str, Any]] = []
    exact_duplicate_count = 0
    nearby_duplicate_count = 0
    transient_count = 0
    attack_group_count = 0

    for measure_number in sorted(grouped_measures):
        measure_events = grouped_measures[measure_number]
        deduped, removed_exact = _dedupe_same_attack(measure_events)
        retrigger_cleaned, removed_nearby = _dedupe_nearby_retriggers(deduped)
        filtered, removed_transients = _suppress_weak_transients(retrigger_cleaned)
        grouped, groups = _assign_attack_groups(filtered)
        exact_duplicate_count += removed_exact
        nearby_duplicate_count += removed_nearby
        transient_count += removed_transients
        attack_group_count += groups
        rendered.extend(grouped)

    rendered.sort(
        key=lambda item: (
            _safe_int(item.get("measureNumber")),
            _safe_int(item.get("quantizedStep")),
            _safe_int(item.get("stringIndex")),
            _safe_int(item.get("fret")),
        )
    )

    source_indices = [_safe_int(item.get("sourceEventIndex")) for item in rendered]
    diagnostics = {
        "rawEventCount": len(projected_events),
        "renderEventCount": len(rendered),
        "duplicateEventsRemoved": exact_duplicate_count + nearby_duplicate_count,
        "exactDuplicateEventsRemoved": exact_duplicate_count,
        "nearbyRetriggerEventsRemoved": nearby_duplicate_count,
        "weakTransientEventsRemoved": transient_count,
        "attackGroupCount": attack_group_count,
        "quantizationStepsPerMeasure": SIXTEENTH_STEPS,
        "sourceIndicesUnique": len(source_indices) == len(set(source_indices)),
        "allRenderEventsTraceable": all(index >= 0 for index in source_indices),
    }
    return rendered, diagnostics
