from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

INTRO_START_MEASURE = 1
INTRO_END_MEASURE = 16
MAX_RETRIGGER_STEP_GAP = 2
MAX_BEND_RISE_STEPS = 4
MAX_RELEASE_STEPS = 7
MIN_CONTOUR_PAIR_SUPPORT = 3


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
    return max(0, (measure_number - INTRO_START_MEASURE) // 2)


def _measure_offset(measure_number: int) -> int:
    return (measure_number - INTRO_START_MEASURE) % 2


def _event_key(event: dict[str, Any]) -> tuple[int, int, int, int]:
    return (
        _safe_int(event.get("measureNumber")),
        _safe_int(event.get("quantizedStep")),
        _safe_int(event.get("stringIndex")),
        _safe_int(event.get("midiPitch")),
    )


def _quality(event: dict[str, Any]) -> tuple[float, float, int]:
    return (
        _safe_float(event.get("confidence")),
        _safe_float(event.get("duration")),
        -_safe_int(event.get("sourceEventIndex")),
    )


def _find_rise_and_return(
    events: list[dict[str, Any]],
    start_index: int,
) -> tuple[int, int, int] | None:
    start = events[start_index]
    start_pitch = _safe_int(start.get("midiPitch"))
    start_step = _safe_int(start.get("quantizedStep"))
    string_index = _safe_int(start.get("stringIndex"), -1)

    if start_pitch <= 0 or string_index < 0:
        return None

    rise_index: int | None = None
    for index in range(start_index + 1, len(events)):
        candidate = events[index]
        step = _safe_int(candidate.get("quantizedStep"))
        if step - start_step > MAX_BEND_RISE_STEPS:
            break
        if _safe_int(candidate.get("stringIndex"), -1) != string_index:
            continue
        pitch_delta = _safe_int(candidate.get("midiPitch")) - start_pitch
        if 1 <= pitch_delta <= 3:
            rise_index = index
            break

    if rise_index is None:
        return None

    for index in range(rise_index + 1, len(events)):
        candidate = events[index]
        step = _safe_int(candidate.get("quantizedStep"))
        if step - start_step > MAX_RELEASE_STEPS:
            break
        if _safe_int(candidate.get("stringIndex"), -1) != string_index:
            continue
        if abs(_safe_int(candidate.get("midiPitch")) - start_pitch) <= 1:
            rise_pitch = _safe_int(events[rise_index].get("midiPitch"))
            return rise_index, index, max(1, min(3, rise_pitch - start_pitch))

    return None


def _find_direct_release(
    events: list[dict[str, Any]],
    start_index: int,
) -> tuple[int, int] | None:
    """Recognize a bend when transcription captures only fretted start and release.

    Some source separators do not emit the temporary raised pitch of a bend. They
    instead produce the fretted attack followed by a lower same-string release.
    Repeated support across the intro is required before this display-only layer
    labels that contour as a bend.
    """

    start = events[start_index]
    start_pitch = _safe_int(start.get("midiPitch"))
    start_step = _safe_int(start.get("quantizedStep"))
    string_index = _safe_int(start.get("stringIndex"), -1)

    if start_pitch <= 0 or string_index < 0:
        return None

    for index in range(start_index + 1, len(events)):
        candidate = events[index]
        step = _safe_int(candidate.get("quantizedStep"))
        if step - start_step > MAX_RELEASE_STEPS:
            break
        if _safe_int(candidate.get("stringIndex"), -1) != string_index:
            continue

        fall = start_pitch - _safe_int(candidate.get("midiPitch"))
        if 1 <= fall <= 4:
            # A fall of two semitones is the strongest full-bend-release signal.
            bend_semitones = 2 if fall >= 2 else 1
            return index, bend_semitones

    return None


def reconstruct_intro_pitch_contours(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Create a read-only V8 display layer for repeated bend contours.

    This pass never changes the locked V7 event list. It recognizes either an
    observed rise-and-return contour or a repeated direct same-string release,
    removes only redundant display retriggers, and keeps every retained item
    traceable to its original source event.
    """

    intro = [
        dict(event)
        for event in events
        if INTRO_START_MEASURE
        <= _safe_int(event.get("measureNumber"))
        <= INTRO_END_MEASURE
    ]
    outside = [
        dict(event)
        for event in events
        if not (
            INTRO_START_MEASURE
            <= _safe_int(event.get("measureNumber"))
            <= INTRO_END_MEASURE
        )
    ]

    by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in intro:
        by_measure[_safe_int(event.get("measureNumber"))].append(event)
    for measure_events in by_measure.values():
        measure_events.sort(
            key=lambda event: (
                _safe_int(event.get("quantizedStep")),
                _safe_int(event.get("stringIndex")),
                _safe_int(event.get("midiPitch")),
            )
        )

    contour_observations: dict[tuple[int, int, int, int, str], set[int]] = defaultdict(set)
    contour_instances: list[tuple[int, int, int | None, int, int, int, str]] = []

    for measure, measure_events in by_measure.items():
        for index, event in enumerate(measure_events):
            observed = _find_rise_and_return(measure_events, index)
            if observed is not None:
                rise_index, release_index, pitch_delta = observed
                contour_kind = "rise-return"
            else:
                direct = _find_direct_release(measure_events, index)
                if direct is None:
                    continue
                release_index, pitch_delta = direct
                rise_index = None
                contour_kind = "direct-release"

            signature = (
                _measure_offset(measure),
                _safe_int(event.get("quantizedStep")),
                _safe_int(event.get("stringIndex")),
                pitch_delta,
                contour_kind,
            )
            pair_id = _pair_index(measure)
            contour_observations[signature].add(pair_id)
            contour_instances.append(
                (
                    measure,
                    index,
                    rise_index,
                    release_index,
                    pair_id,
                    pitch_delta,
                    contour_kind,
                )
            )

    accepted = {
        signature
        for signature, pair_ids in contour_observations.items()
        if len(pair_ids) >= MIN_CONTOUR_PAIR_SUPPORT
    }

    remove_keys: set[tuple[int, int, int, int]] = set()
    bend_start_keys: dict[tuple[int, int, int, int], int] = {}
    release_keys: set[tuple[int, int, int, int]] = set()
    accepted_direct_release_count = 0

    for (
        measure,
        start_index,
        rise_index,
        release_index,
        _pair_id,
        pitch_delta,
        contour_kind,
    ) in contour_instances:
        measure_events = by_measure[measure]
        start = measure_events[start_index]
        release = measure_events[release_index]
        signature = (
            _measure_offset(measure),
            _safe_int(start.get("quantizedStep")),
            _safe_int(start.get("stringIndex")),
            pitch_delta,
            contour_kind,
        )
        if signature not in accepted:
            continue

        bend_start_keys[_event_key(start)] = pitch_delta
        release_keys.add(_event_key(release))
        if rise_index is not None:
            remove_keys.add(_event_key(measure_events[rise_index]))
        else:
            accepted_direct_release_count += 1

    deduped: dict[tuple[int, int, int], dict[str, Any]] = {}
    retriggers_removed = 0
    for event in intro:
        event_key = _event_key(event)
        if event_key in remove_keys:
            continue

        slot = (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("midiPitch")),
        )
        previous = deduped.get(slot)
        if previous is not None:
            gap = abs(
                _safe_int(event.get("quantizedStep"))
                - _safe_int(previous.get("quantizedStep"))
            )
            if gap <= MAX_RETRIGGER_STEP_GAP:
                retriggers_removed += 1
                if _quality(event) > _quality(previous):
                    deduped[slot] = event
                continue
        deduped[slot] = event

    reconstructed_intro: list[dict[str, Any]] = []
    bends_marked = 0
    releases_marked = 0
    for event in deduped.values():
        item = dict(event)
        key = _event_key(item)
        if key in bend_start_keys:
            semitones = bend_start_keys[key]
            label = "full-bend" if semitones >= 2 else "half-bend"
            item["technique"] = label
            techniques = item.get("techniques") or []
            if isinstance(techniques, str):
                techniques = [techniques]
            item["techniques"] = list(dict.fromkeys([*techniques, label]))
            item["bendSemitones"] = semitones
            item["bendAmount"] = "full" if semitones >= 2 else "half"
            item["pitchContourReconstructed"] = True
            bends_marked += 1
        elif key in release_keys:
            item["technique"] = "bend-release"
            techniques = item.get("techniques") or []
            if isinstance(techniques, str):
                techniques = [techniques]
            item["techniques"] = list(dict.fromkeys([*techniques, "bend-release"]))
            item["pitchContourReconstructed"] = True
            releases_marked += 1
        reconstructed_intro.append(item)

    result = reconstructed_intro + outside
    result.sort(
        key=lambda event: (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
    )

    diagnostics = {
        "introMeasureRange": [INTRO_START_MEASURE, INTRO_END_MEASURE],
        "inputEventCount": len(events),
        "inputIntroEventCount": len(intro),
        "outputIntroEventCount": len(reconstructed_intro),
        "acceptedContourSignatureCount": len(accepted),
        "acceptedDirectReleaseInstances": accepted_direct_release_count,
        "minimumContourPairSupport": MIN_CONTOUR_PAIR_SUPPORT,
        "bendEventsMarked": bends_marked,
        "bendReleaseEventsMarked": releases_marked,
        "pitchExcursionDisplayEventsRemoved": len(remove_keys),
        "nearbySustainRetriggersRemoved": retriggers_removed,
        "contourSupportHistogram": dict(
            sorted(Counter(len(value) for value in contour_observations.values()).items())
        ),
        "sourceEventsSynthetic": False,
        "readOnly": True,
    }
    return result, diagnostics
