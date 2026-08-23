"""Canonical scorer-only representation of V143 Rhythm render events.

This module is validation infrastructure only. Runtime/analyzer code must not import it.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

OPEN_MIDI = {1: 64, 2: 59, 3: 55, 4: 50, 5: 45, 6: 40}


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


def _techniques(event: Mapping[str, Any]) -> list[str]:
    labels: list[str] = []
    single = event.get("technique")
    if isinstance(single, str) and single.strip():
        labels.append(single.strip())
    many = event.get("techniques")
    if isinstance(many, list):
        labels.extend(str(item).strip() for item in many if str(item).strip())
    return sorted(set(labels))


def canonical_event(event: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(event, Mapping):
        raise ValueError("render event must be an object")

    string = _int(event.get("string"), "string")
    fret = _int(event.get("fret"), "fret")
    midi = _int(event.get("midi"), "midi")
    measure = _int(event.get("measure"), "measure")
    step = _num(event.get("step"), "step")

    if string not in OPEN_MIDI:
        raise ValueError(f"invalid guitar string {string}")
    if not 0 <= fret <= 24:
        raise ValueError(f"invalid guitar fret {fret}")
    if measure < 1:
        raise ValueError(f"invalid measure {measure}")
    if not 0 <= step < 16:
        raise ValueError(f"invalid 16-step placement {step}")
    expected_midi = OPEN_MIDI[string] + fret
    if midi != expected_midi:
        raise ValueError(
            f"pitch-position mismatch: string={string} fret={fret} midi={midi} expected={expected_midi}"
        )

    duration = event.get("durationSteps")
    sustain = event.get("sustainSteps")
    duration_value = None if duration is None else _num(duration, "durationSteps")
    sustain_value = None if sustain is None else _num(sustain, "sustainSteps")
    if duration_value is not None and duration_value <= 0:
        raise ValueError("durationSteps must be positive")
    if sustain_value is not None and sustain_value < 0:
        raise ValueError("sustainSteps must be non-negative")

    return {
        "measure": measure,
        "step": step,
        "string": string,
        "fret": fret,
        "midi": midi,
        "durationSteps": duration_value,
        "sustainSteps": sustain_value,
        "tieIn": bool(event.get("tieIn", False)),
        "tieOut": bool(event.get("tieOut", False)),
        "rest": bool(event.get("rest", False)),
        "techniques": _techniques(event),
    }


def canonical_events(events: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized = [canonical_event(event) for event in events]
    normalized.sort(
        key=lambda e: (
            e["measure"],
            e["step"],
            e["string"],
            e["fret"],
            e["midi"],
            e["durationSteps"] if e["durationSteps"] is not None else -1.0,
            e["sustainSteps"] if e["sustainSteps"] is not None else -1.0,
            tuple(e["techniques"]),
        )
    )
    return normalized


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def group_onsets(events: Iterable[Mapping[str, Any]]) -> dict[tuple[int, float], list[dict[str, Any]]]:
    grouped: dict[tuple[int, float], list[dict[str, Any]]] = {}
    for event in canonical_events(events):
        grouped.setdefault((event["measure"], event["step"]), []).append(event)
    return grouped
