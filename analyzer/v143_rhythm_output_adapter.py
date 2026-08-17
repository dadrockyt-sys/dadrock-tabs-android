from __future__ import annotations

from copy import deepcopy
from typing import Any

from v143_rhythm_event_assembly import RhythmEventAssemblyResult


STRING_LABELS = ("e", "B", "G", "D", "A", "E")
STEPS_PER_MEASURE = 16
CELL_WIDTH = 4


def _technique_types(event: dict[str, Any]) -> set[str]:
    return {
        str(item.get("type"))
        for item in event.get("rhythmTechniques", [])
        if item.get("type")
    }


def render_event_token(event: dict[str, Any]) -> str:
    fret = int(event["fret"])
    token = str(fret)
    techniques = _technique_types(event)

    if "bend" in techniques:
        token += "b"
    elif "natural-harmonic" in techniques:
        token = f"<{token}>"
    elif "dead-note" in techniques or "muted-strum" in techniques:
        token = "x"

    if len(token) > CELL_WIDTH - 1:
        return token[: CELL_WIDTH - 1]
    return token


def render_measure(
    measure_number: int,
    events: list[dict[str, Any]],
) -> str:
    by_step: dict[int, list[dict[str, Any]]] = {}
    for event in events:
        step = int(event["step"])
        if not 0 <= step < STEPS_PER_MEASURE:
            raise ValueError(
                f"Rhythm event step {step} is outside the 16-step 4/4 grid"
            )
        by_step.setdefault(step, []).append(event)

    lines = [f"Measure {int(measure_number)}"]
    rows = [["-" * CELL_WIDTH for _ in range(STEPS_PER_MEASURE)] for _ in STRING_LABELS]

    for step in range(STEPS_PER_MEASURE):
        step_events = sorted(
            by_step.get(step, []),
            key=lambda event: (
                int(event["stringIndex"]),
                int(event["fret"]),
                int(event.get("midi", event.get("dominantMidi", 0))),
            ),
        )
        used_strings: set[int] = set()
        for event in step_events:
            string_index = int(event["stringIndex"])
            if not 0 <= string_index < len(STRING_LABELS):
                raise ValueError(f"Invalid stringIndex: {string_index}")
            if string_index in used_strings:
                raise RuntimeError(
                    f"Multiple rhythm events occupy string {string_index} at "
                    f"measure {measure_number}, step {step}"
                )
            used_strings.add(string_index)
            token = render_event_token(event)
            rows[string_index][step] = token.ljust(CELL_WIDTH, "-")

    for string_index, label in enumerate(STRING_LABELS):
        lines.append(f"{label}|{''.join(rows[string_index])}|")
    return "\n".join(lines)


def render_rhythm_tab(events: list[dict[str, Any]]) -> str:
    if not events:
        return "No selected rhythm-guitar events were detected."

    ordered = sorted(
        (deepcopy(event) for event in events),
        key=lambda event: (
            int(event["measure"]),
            int(event["step"]),
            int(event["stringIndex"]),
            int(event["fret"]),
        ),
    )

    by_measure: dict[int, list[dict[str, Any]]] = {}
    for event in ordered:
        by_measure.setdefault(int(event["measure"]), []).append(event)

    return "\n\n".join(
        render_measure(measure_number, by_measure[measure_number])
        for measure_number in sorted(by_measure)
    )


def build_rhythm_output(
    assembly_result: RhythmEventAssemblyResult,
) -> dict[str, Any]:
    """Convert final V143 rhythm events into the existing analyzer response contract."""
    if not isinstance(assembly_result, RhythmEventAssemblyResult):
        raise TypeError("assembly_result must be RhythmEventAssemblyResult")

    payload = assembly_result.to_dict()
    events = [deepcopy(event) for event in payload["events"]]
    generated_tab = render_rhythm_tab(events)

    return {
        "generatedTab": generated_tab,
        "tuning": "E Standard",
        "tempo": float(payload["timing"]["tempoBpm"]),
        "timeSignature": str(payload["timing"]["timeSignature"]),
        "keySignature": None,
        "difficulty": None,
        "techniques": list(payload["techniques"]),
        "confidence": None,
        "events": events,
        "noteCount": len(events),
        "candidateCount": int(payload["candidateCount"]),
        "selectedCount": int(payload["selectedCount"]),
        "assembly": deepcopy(payload["assembly"]),
        "engineVersion": "v143-reference-free-rhythm-output-v1",
    }


__all__ = [
    "STRING_LABELS",
    "STEPS_PER_MEASURE",
    "CELL_WIDTH",
    "render_event_token",
    "render_measure",
    "render_rhythm_tab",
    "build_rhythm_output",
]
