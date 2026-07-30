from __future__ import annotations

from collections import defaultdict
from typing import Any

SIXTEENTH_STEPS = 16
ATTACK_CLUSTER_STEPS = 1
MIN_DURATION_SECONDS = 0.035
LOW_CONFIDENCE_THRESHOLD = 0.08


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


def _suppress_weak_transients(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    kept: list[dict[str, Any]] = []
    removed = 0

    for event in events:
        duration = _safe_float(event.get("duration"))
        confidence = _safe_float(event.get("confidence"))
        isolated = not any(
            other is not event
            and abs(_safe_int(other.get("quantizedStep")) - _safe_int(event.get("quantizedStep")))
            <= ATTACK_CLUSTER_STEPS
            for other in events
        )

        if (
            duration > 0
            and duration < MIN_DURATION_SECONDS
            and confidence > 0
            and confidence < LOW_CONFIDENCE_THRESHOLD
            and isolated
        ):
            removed += 1
            continue

        kept.append(event)

    return kept, removed


def _assign_attack_groups(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    attack_id = 0
    previous_step: int | None = None
    groups: set[int] = set()
    rendered: list[dict[str, Any]] = []

    for event in events:
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

    rendered: list[dict[str, Any]] = []
    duplicate_count = 0
    transient_count = 0
    attack_group_count = 0

    for measure_number in sorted(_group_by_measure(prepared)):
        measure_events = _group_by_measure(prepared)[measure_number]
        deduped, removed_duplicates = _dedupe_same_attack(measure_events)
        filtered, removed_transients = _suppress_weak_transients(deduped)
        grouped, groups = _assign_attack_groups(filtered)
        duplicate_count += removed_duplicates
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

    source_indices = [
        _safe_int(item.get("sourceEventIndex"))
        for item in rendered
    ]
    diagnostics = {
        "rawEventCount": len(projected_events),
        "renderEventCount": len(rendered),
        "duplicateEventsRemoved": duplicate_count,
        "weakTransientEventsRemoved": transient_count,
        "attackGroupCount": attack_group_count,
        "quantizationStepsPerMeasure": SIXTEENTH_STEPS,
        "sourceIndicesUnique": len(source_indices) == len(set(source_indices)),
        "allRenderEventsTraceable": all(index >= 0 for index in source_indices),
    }
    return rendered, diagnostics
