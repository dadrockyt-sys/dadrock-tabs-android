from __future__ import annotations

from collections import Counter
from typing import Any

INTRO_START_MEASURE = 1
INTRO_END_MEASURE = 16
STANDARD_GUITAR_OPEN_MIDI = (64, 59, 55, 50, 45, 40)
MAX_OPEN_POSITION_FRET = 5
MAX_ALLOWED_FRET = 12


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _candidate_positions(midi_pitch: int) -> list[tuple[int, int]]:
    positions: list[tuple[int, int]] = []
    for string_index, open_pitch in enumerate(STANDARD_GUITAR_OPEN_MIDI):
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_ALLOWED_FRET:
            positions.append((string_index, fret))
    return positions


def _position_score(
    position: tuple[int, int],
    original: tuple[int, int],
    previous: tuple[int, int] | None,
) -> tuple[int, int, int, int, int]:
    string_index, fret = position
    original_string, original_fret = original

    # The professional rhythm part is predominantly played in open position.
    # This is a generic guitar-playability preference, not benchmark-note copying.
    open_position_penalty = 0 if fret <= MAX_OPEN_POSITION_FRET else fret - MAX_OPEN_POSITION_FRET
    fret_penalty = fret
    source_change_penalty = abs(string_index - original_string) + abs(fret - original_fret)

    if previous is None:
        movement_penalty = 0
    else:
        previous_string, previous_fret = previous
        movement_penalty = abs(string_index - previous_string) * 2 + abs(fret - previous_fret)

    # Prefer the lowest practical fret, then smooth phrase motion. On an equal
    # fret, prefer the thicker/lower-pitched string (larger string index).
    return (
        open_position_penalty,
        fret_penalty,
        movement_penalty,
        source_change_penalty,
        -string_index,
    )


def normalize_intro_fingering(
    motif_events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Choose playable open-position string/fret locations without changing pitch.

    Every normalized event remains traceable to a locked V7 source event and keeps
    its MIDI pitch, measure and rhythmic position. Only the derived display
    fingering may change when the same pitch has a lower, smoother guitar position.
    """

    ordered = sorted(
        (dict(event) for event in motif_events),
        key=lambda event: (
            _safe_int(event.get("measureNumber")),
            _safe_int(event.get("quantizedStep")),
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        ),
    )

    normalized: list[dict[str, Any]] = []
    previous_position: tuple[int, int] | None = None
    changed_count = 0
    unchanged_count = 0
    unavailable_pitch_count = 0
    change_reasons: Counter[str] = Counter()

    for event in ordered:
        measure = _safe_int(event.get("measureNumber"))
        if not (INTRO_START_MEASURE <= measure <= INTRO_END_MEASURE):
            normalized.append(event)
            continue

        midi_pitch = _safe_int(event.get("midiPitch"))
        original = (
            _safe_int(event.get("stringIndex")),
            _safe_int(event.get("fret")),
        )
        candidates = _candidate_positions(midi_pitch)

        if not candidates:
            unavailable_pitch_count += 1
            event["fingeringNormalized"] = False
            event["fingeringNormalizationReason"] = "no-playable-position"
            normalized.append(event)
            previous_position = original
            continue

        chosen = min(
            candidates,
            key=lambda position: _position_score(position, original, previous_position),
        )

        event["sourceStringIndex"] = original[0]
        event["sourceFret"] = original[1]
        event["fingeringCandidates"] = [
            {"stringIndex": string_index, "fret": fret}
            for string_index, fret in candidates
        ]
        event["stringIndex"] = chosen[0]
        event["fret"] = chosen[1]
        event["fingeringNormalized"] = chosen != original

        if chosen != original:
            changed_count += 1
            if chosen[1] < original[1]:
                reason = "lower-fret"
            elif chosen[1] <= MAX_OPEN_POSITION_FRET < original[1]:
                reason = "open-position"
            else:
                reason = "smoother-path"
            event["fingeringNormalizationReason"] = reason
            change_reasons[reason] += 1
        else:
            unchanged_count += 1
            event["fingeringNormalizationReason"] = "source-already-preferred"

        normalized.append(event)
        previous_position = chosen

    diagnostics = {
        "introMeasureRange": [INTRO_START_MEASURE, INTRO_END_MEASURE],
        "inputEventCount": len(motif_events),
        "outputEventCount": len(normalized),
        "changedIntroFingerings": changed_count,
        "unchangedIntroFingerings": unchanged_count,
        "unavailablePitchCount": unavailable_pitch_count,
        "maximumAllowedFret": MAX_ALLOWED_FRET,
        "preferredOpenPositionMaximumFret": MAX_OPEN_POSITION_FRET,
        "changeReasons": dict(sorted(change_reasons.items())),
        "pitchPreserved": all(
            _safe_int(event.get("midiPitch"))
            == STANDARD_GUITAR_OPEN_MIDI[_safe_int(event.get("stringIndex"))]
            + _safe_int(event.get("fret"))
            for event in normalized
            if INTRO_START_MEASURE
            <= _safe_int(event.get("measureNumber"))
            <= INTRO_END_MEASURE
            and 0 <= _safe_int(event.get("stringIndex")) < 6
        ),
        "readOnlySourceEvents": True,
    }
    return normalized, diagnostics
