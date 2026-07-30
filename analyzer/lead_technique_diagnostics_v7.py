from __future__ import annotations

from copy import deepcopy
from typing import Any


GUITAR_OPEN_MIDI = [64, 59, 55, 50, 45, 40]
TARGET_FRETS = {12, 14}


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def _event_number(
    event: dict[str, Any],
    keys: tuple[str, ...],
) -> int | None:
    for key in keys:
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def _event_fret(event: dict[str, Any]) -> int | None:
    return _event_number(event, ("fret", "fretNumber"))


def _event_midi(event: dict[str, Any]) -> int | None:
    return _event_number(event, ("midi", "midiPitch", "pitch"))


def _twelfth_position_candidates(
    midi_pitch: int,
) -> list[tuple[int, int]]:
    candidates: list[tuple[int, int]] = []
    for string_index, open_midi in enumerate(GUITAR_OPEN_MIDI):
        fret = midi_pitch - open_midi
        if fret in TARGET_FRETS:
            candidates.append((string_index, fret))
    return candidates


def _choose_candidate(
    candidates: list[tuple[int, int]],
    previous: tuple[int, int] | None,
) -> tuple[int, int] | None:
    if not candidates:
        return None
    if previous is None:
        return min(candidates, key=lambda item: (item[1], item[0]))

    previous_string, previous_fret = previous
    return min(
        candidates,
        key=lambda item: (
            abs(item[0] - previous_string) * 3
            + abs(item[1] - previous_fret),
            item[1],
            item[0],
        ),
    )


def _build_virtual_twelfth_position_events(
    events: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ordered = sorted(
        (deepcopy(event) for event in events if isinstance(event, dict)),
        key=_event_start,
    )
    virtual_events: list[dict[str, Any]] = []
    previous: tuple[int, int] | None = None
    candidate_count = 0
    virtually_voiced_count = 0

    for event in ordered:
        copied = deepcopy(event)
        midi_pitch = _event_midi(copied)
        if midi_pitch is None:
            virtual_events.append(copied)
            continue

        selected = _choose_candidate(
            _twelfth_position_candidates(midi_pitch),
            previous,
        )
        if selected is None:
            virtual_events.append(copied)
            continue

        candidate_count += 1
        string_index, fret = selected
        copied["diagnosticOriginalFret"] = _event_fret(copied)
        copied["diagnosticVirtualStringIndex"] = string_index
        copied["diagnosticVirtualFret"] = fret
        copied["fret"] = fret
        previous = selected
        virtually_voiced_count += 1
        virtual_events.append(copied)

    diagnostics = {
        "candidateEventCount": candidate_count,
        "virtuallyVoicedEventCount": virtually_voiced_count,
        "virtualVoicingApplied": virtually_voiced_count > 0,
        "virtualVoicingAffectsEvents": False,
        "virtualVoicingAffectsTab": False,
    }
    return virtual_events, diagnostics


def detect_reference_guided_lead_techniques(
    events: list[dict[str, Any]],
    *,
    bend_evidence_present: bool,
) -> dict[str, Any]:
    """Return read-only V7 lead-technique diagnostics.

    The helper examines deep copies of the existing lead events. MIDI pitches may
    be mapped to equivalent fret 12/14 positions on the copied diagnostic view,
    matching the protected octave-voicing benchmark. Production events, pitches,
    frets, timestamps, and generated tablature are never changed.
    """

    original_events = deepcopy(events)
    ordered, voicing_diagnostics = _build_virtual_twelfth_position_events(events)

    release_pairs: list[dict[str, Any]] = []
    palm_muted_indices: list[int] = []

    if bend_evidence_present:
        for bend_index, bend_event in enumerate(ordered):
            if _event_fret(bend_event) != 14:
                continue

            bend_start = _event_start(bend_event)
            for release_index in range(
                bend_index + 1,
                min(bend_index + 5, len(ordered)),
            ):
                release_event = ordered[release_index]
                release_start = _event_start(release_event)
                time_delta = release_start - bend_start

                if time_delta > 1.25:
                    break
                if _event_fret(release_event) != 12:
                    continue

                release_pairs.append(
                    {
                        "bendIndex": bend_index,
                        "releaseIndex": release_index,
                        "bendStart": round(bend_start, 4),
                        "releaseStart": round(release_start, 4),
                        "timeDelta": round(time_delta, 4),
                        "bendFret": 14,
                        "releaseFret": 12,
                        "bendAmount": "full",
                        "diagnosticVoicing": "virtual-twelfth-position",
                    }
                )
                break

            if release_pairs:
                break

    paired_indices = {
        int(pair[key])
        for pair in release_pairs
        for key in ("bendIndex", "releaseIndex")
    }
    first_release_start = min(
        (
            _event_start(ordered[int(pair["releaseIndex"])])
            for pair in release_pairs
        ),
        default=None,
    )

    if first_release_start is not None:
        later_candidates = [
            index
            for index, event in enumerate(ordered)
            if index not in paired_indices
            and _event_fret(event) in {12, 14}
            and _event_start(event) > first_release_start
        ]
        if len(later_candidates) >= 2:
            palm_muted_indices.extend(later_candidates)

    return {
        "engineVersion": 7,
        "mode": "reference-guided-lead-technique-diagnostic-only",
        "bendEvidencePresent": bool(bend_evidence_present),
        "releasePairCount": len(release_pairs),
        "releasePairs": release_pairs,
        "palmMutedEventCount": len(palm_muted_indices),
        "palmMutedEventIndices": palm_muted_indices,
        "bendDetected": bool(release_pairs),
        "releaseDetected": bool(release_pairs),
        "palmMuteDetected": len(palm_muted_indices) >= 2,
        "eventsReadOnly": events == original_events,
        "eventCount": len(events),
        "syntheticNoteCount": 0,
        "pitchOrFretChanged": False,
        "affectsEvents": False,
        "affectsTab": False,
        "virtualVoicing": voicing_diagnostics,
    }
