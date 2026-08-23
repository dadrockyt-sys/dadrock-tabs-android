"""Canonical scorer-only representation of V143 Rhythm render events.

This module mirrors the established `lib/v143RenderContract.js` event shape so the
frozen stream can be passed directly to the professional PDF renderer without losing
or inventing musical information. Runtime/analyzer code must not import this module.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}
ALLOWED_SUSTAIN_TIERS = {"short", "medium", "long"}


def _num(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be numeric")
    return float(value)


def _int(value: Any, name: str) -> int:
    number = _num(value, name)
    rounded = int(round(number))
    if abs(number - rounded) > 1e-9:
        raise ValueError(f"{name} must be an integer")
    return rounded


def _optional_num(event: Mapping[str, Any], key: str, *, minimum: float | None = None) -> float | None:
    value = event.get(key)
    if value is None:
        return None
    number = _num(value, key)
    if minimum is not None and number < minimum:
        raise ValueError(f"{key} must be >= {minimum}")
    return number


def _optional_int(event: Mapping[str, Any], key: str, *, minimum: int | None = None) -> int | None:
    value = event.get(key)
    if value is None:
        return None
    number = _int(value, key)
    if minimum is not None and number < minimum:
        raise ValueError(f"{key} must be >= {minimum}")
    return number


def _techniques(event: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    many = event.get("techniques")
    if isinstance(many, list):
        labels.extend(str(item).strip().lower() for item in many if str(item).strip())
    return sorted(set(labels))


def canonical_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(event, Mapping):
        raise ValueError("render event must be an object")

    event_index = _int(event.get("eventIndex"), "eventIndex")
    measure = _int(event.get("measure"), "measure")
    step = _int(event.get("step"), "step")
    string_index = _int(event.get("stringIndex"), "stringIndex")
    fret = _int(event.get("fret"), "fret")
    midi = _int(event.get("midi"), "midi")
    duration_steps = _int(event.get("durationSteps"), "durationSteps")

    if event_index < 0:
        raise ValueError(f"invalid eventIndex {event_index}")
    if measure < 1:
        raise ValueError(f"invalid measure {measure}")
    if not 0 <= step <= 15:
        raise ValueError(f"invalid 16-step placement {step}")
    if string_index not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError(f"invalid guitar stringIndex {string_index}")
    if not 0 <= fret <= 36:
        raise ValueError(f"invalid guitar fret {fret}")
    if duration_steps < 1:
        raise ValueError("durationSteps must be >= 1")

    expected_midi = OPEN_MIDI_BY_STRING_INDEX[string_index] + fret
    if midi != expected_midi:
        raise ValueError(
            "pitch-position mismatch: "
            f"stringIndex={string_index} fret={fret} midi={midi} expected={expected_midi}"
        )

    output: dict[str, Any] = {
        "eventIndex": event_index,
        "measure": measure,
        "step": step,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "durationSteps": duration_steps,
        "techniques": _techniques(event),
    }

    duration_seconds = _optional_num(event, "durationSeconds", minimum=0.0)
    if duration_seconds is not None:
        output["durationSeconds"] = duration_seconds

    sustain_tier = str(event.get("sustainTier") or "").strip().lower()
    if sustain_tier:
        if sustain_tier not in ALLOWED_SUSTAIN_TIERS:
            raise ValueError(f"invalid sustainTier {sustain_tier!r}")
        output["sustainTier"] = sustain_tier

    bend_semitones = _optional_num(event, "bendSemitones", minimum=0.0)
    if bend_semitones is not None:
        output["bendSemitones"] = bend_semitones
        bend_target_fret = _optional_int(event, "bendTargetFret")
        bend_target_midi = _optional_int(event, "bendTargetMidi")
        if bend_target_fret is not None:
            output["bendTargetFret"] = bend_target_fret
        if bend_target_midi is not None:
            output["bendTargetMidi"] = bend_target_midi
        output["bendRelease"] = event.get("bendRelease") is True

    legato_target_event_index = _optional_int(event, "legatoTargetEventIndex", minimum=0)
    if legato_target_event_index is not None:
        output["legatoTargetEventIndex"] = legato_target_event_index
        legato_target_fret = _optional_int(event, "legatoTargetFret")
        legato_target_midi = _optional_int(event, "legatoTargetMidi")
        if legato_target_fret is not None:
            output["legatoTargetFret"] = legato_target_fret
        if legato_target_midi is not None:
            output["legatoTargetMidi"] = legato_target_midi

    continuation_from = _optional_int(event, "legatoContinuationFromEventIndex", minimum=0)
    if continuation_from is not None:
        output["legatoContinuationFromEventIndex"] = continuation_from

    continuation_type = str(event.get("legatoContinuationType") or "").strip().lower()
    if continuation_type:
        output["legatoContinuationType"] = continuation_type

    return output


def canonical_events(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Validate and normalize while preserving the exact renderer input order."""
    return [canonical_event(event) for event in events]


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def group_onsets(events: Iterable[Mapping[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for event in canonical_events(events):
        grouped.setdefault((event["measure"], event["step"]), []).append(event)
    return grouped
