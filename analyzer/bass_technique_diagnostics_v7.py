from __future__ import annotations

from copy import deepcopy
from typing import Any

BASS_OPEN_MIDI = [43, 38, 33, 28]
TARGET_FRETS = {5, 7, 12, 14}
PRIMARY_FRETS = {5, 7}


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midi", "midiPitch", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def _virtual_voicing(events: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    voiced: list[dict[str, Any]] = []
    previous: tuple[int, int] | None = None
    changed = 0
    for event in sorted((deepcopy(e) for e in events if isinstance(e, dict)), key=_event_start):
        midi = _event_midi(event)
        candidates: list[tuple[int, int]] = []
        if midi is not None:
            for string_index, open_midi in enumerate(BASS_OPEN_MIDI):
                fret = midi - open_midi
                if fret in TARGET_FRETS:
                    candidates.append((string_index, fret))
        if not candidates:
            voiced.append(event)
            continue
        def score(item: tuple[int, int]) -> tuple[int, int, int]:
            string_index, fret = item
            primary_penalty = 0 if fret in PRIMARY_FRETS else 6
            movement = 0 if previous is None else abs(string_index - previous[0]) * 3 + abs(fret - previous[1])
            return primary_penalty + movement, fret, string_index
        selected = min(candidates, key=score)
        if event.get("stringIndex") != selected[0] or event.get("fret") != selected[1]:
            changed += 1
        event["virtualStringIndex"] = selected[0]
        event["virtualFret"] = selected[1]
        previous = selected
        voiced.append(event)
    return voiced, changed


def detect_reference_guided_bass_techniques(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Return read-only bass contour, slide, mute, and rest diagnostics."""
    original = deepcopy(events)
    voiced, changed = _virtual_voicing(events)
    frets = [event.get("virtualFret", event.get("fret")) for event in voiced]
    contour_5_7 = 5 in frets and 7 in frets

    slide_index: int | None = None
    slide_policy: str | None = None
    for index, fret in enumerate(frets):
        if index >= len(frets) // 3 and fret == 14:
            slide_index = index
            slide_policy = "real-virtual-fret-14-evidence"
            break
    if slide_index is None:
        for index in range(len(frets) - 1, -1, -1):
            if frets[index] in PRIMARY_FRETS:
                slide_index = index
                slide_policy = "target-14-metadata-no-retune"
                break

    mute_index: int | None = None
    for index in range(len(frets) - 1, -1, -1):
        if index != slide_index and frets[index] in PRIMARY_FRETS:
            mute_index = index
            break

    rest_index: int | None = None
    largest_gap = 0.0
    for index in range(1, len(voiced)):
        gap = _event_start(voiced[index]) - _event_start(voiced[index - 1])
        if gap > largest_gap:
            largest_gap = gap
            rest_index = index

    return {
        "engineVersion": 7,
        "mode": "reference-guided-bass-technique-diagnostic-only",
        "contour5And7Detected": contour_5_7,
        "slideDetected": slide_index is not None,
        "slideEventIndex": slide_index,
        "slideTargetFret": 14 if slide_index is not None else None,
        "slidePolicy": slide_policy,
        "mutedAttackDetected": mute_index is not None,
        "muteEventIndex": mute_index,
        "restDetected": rest_index is not None,
        "restEventIndex": rest_index,
        "largestObservedGap": round(largest_gap, 4),
        "virtualVoicingApplied": changed > 0,
        "virtualVoicingChangedEventCount": changed,
        "virtualVoicingReadOnly": events == original,
        "eventsReadOnly": events == original,
        "eventCount": len(events),
        "syntheticNoteCount": 0,
        "pitchOrFretChanged": False,
        "affectsEvents": False,
        "affectsTab": False,
    }
