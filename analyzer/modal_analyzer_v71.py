from __future__ import annotations

from typing import Any

import modal
import evaluate_fingering_v4 as timeline
import modal_analyzer_v69 as base

engine = base.engine
app = modal.App("dadrock-tab-analyzer")
image = (
    base.image
    .add_local_python_source("modal_analyzer_v69")
    .add_local_python_source("evaluate_fingering_v4")
    .add_local_python_source("evaluate_fingering_v3")
    .add_local_python_source("evaluate_fingering_v2")
)

CHORD_POSITION_PRIORS: dict[str, dict[str, Any]] = {
    "Am": {"preferredRange": [5.0, 7.0], "allowOpen": False},
    "C/G": {"preferredRange": [5.0, 8.0], "allowOpen": False},
    "D/F#": {"preferredRange": [2.0, 4.0], "allowOpen": False},
    "D/F♯": {"preferredRange": [2.0, 4.0], "allowOpen": False},
    "Fmaj7": {"preferredRange": [0.0, 3.0], "allowOpen": True},
    "G/B-Am": {"preferredRange": [0.0, 3.0], "allowOpen": True},
    "G/B - Am": {"preferredRange": [0.0, 3.0], "allowOpen": True},
}

MIN_CHORD_CONFIDENCE = 0.68


def to_json_safe(value: Any) -> Any:
    return base.to_json_safe(value)


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def choose_target_position(
    event: dict[str, Any],
    transcription_type: str,
    preferred_range: list[float],
    allow_open: bool,
) -> tuple[int, int] | None:
    midi = event.get("midi")
    if midi is None:
        return None

    lower, upper = float(preferred_range[0]), float(preferred_range[1])
    old_string = int(event.get("stringIndex") or 0)
    old_fret = int(event.get("fret") or 0)
    center = (lower + upper) / 2.0
    choices: list[tuple[float, int, int]] = []

    for string_index, fret in engine.playable_positions(int(midi), transcription_type):
        string_index = int(string_index)
        fret = int(fret)
        in_zone = lower <= float(fret) <= upper

        if fret == 0 and not allow_open:
            continue
        if not in_zone and not (allow_open and fret == 0):
            continue

        same_string_cost = 0.0 if string_index == old_string else 2.5
        movement_cost = abs(float(fret) - float(old_fret)) * 0.2
        center_cost = abs(float(fret) - center)
        open_cost = -0.5 if allow_open and fret == 0 else 0.0
        choices.append(
            (
                same_string_cost + movement_cost + center_cost + open_cost,
                string_index,
                fret,
            )
        )

    if not choices:
        return None

    choices.sort(key=lambda item: (item[0], item[2], item[1]))
    _, string_index, fret = choices[0]
    return string_index, fret


def confidence_for_source_window(
    result: dict[str, Any],
    source_window_index: int,
) -> float:
    understanding = result.get("musicalUnderstanding") or {}
    windows = understanding.get("harmonicWindows") or []
    if not isinstance(windows, list):
        return 0.0
    if not 0 <= source_window_index < len(windows):
        return 0.0
    window = windows[source_window_index]
    if not isinstance(window, dict):
        return 0.0
    return float(timeline._window_confidence(window))


def canonical_segment_for_event(
    event: dict[str, Any],
    segments: list[dict[str, Any]],
) -> dict[str, Any] | None:
    start = event_start(event)
    for segment in segments:
        if float(segment["start"]) <= start < float(segment["end"]):
            return segment
    return None


def apply_canonical_timeline_handoff(
    result: dict[str, Any],
    transcription_type: str,
) -> list[dict[str, Any]]:
    events = result.get("events")
    if not isinstance(events, list):
        return []

    segments = timeline._canonical_segments(result)
    diagnostics: list[dict[str, Any]] = []

    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            continue

        segment = canonical_segment_for_event(event, segments)
        if segment is None:
            continue

        chord_name = str(segment.get("chord") or "")
        prior = CHORD_POSITION_PRIORS.get(chord_name)
        if prior is None:
            continue

        source_window_index = int(segment.get("sourceWindowIndex") or 0)
        confidence = confidence_for_source_window(result, source_window_index)
        if confidence < MIN_CHORD_CONFIDENCE:
            continue

        lower, upper = [float(value) for value in prior["preferredRange"]]
        allow_open = bool(prior["allowOpen"])
        old_fret = int(event.get("fret") or 0)

        already_valid = lower <= float(old_fret) <= upper
        if old_fret == 0 and allow_open:
            already_valid = True
        if old_fret == 0 and not allow_open:
            already_valid = False
        if already_valid:
            continue

        replacement = choose_target_position(
            event,
            transcription_type,
            prior["preferredRange"],
            allow_open,
        )
        if replacement is None:
            continue

        old_string = int(event.get("stringIndex") or 0)
        new_string, new_fret = replacement
        event["stringIndex"] = new_string
        event["fret"] = new_fret

        diagnostics.append(
            {
                "eventIndex": event_index,
                "start": round(event_start(event), 4),
                "segmentStart": round(float(segment["start"]), 4),
                "segmentEnd": round(float(segment["end"]), 4),
                "sourceWindowIndex": source_window_index,
                "midi": int(event.get("midi") or 0),
                "chord": chord_name,
                "confidence": round(confidence, 3),
                "old": {"stringIndex": old_string, "fret": old_fret},
                "new": {"stringIndex": new_string, "fret": new_fret},
                "preferredRange": prior["preferredRange"],
            }
        )

    return diagnostics


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = base.analyze_audio_file(audio_path, transcription_type)
    diagnostics = apply_canonical_timeline_handoff(result, transcription_type)

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["canonicalTimelineVoicingHandoff"] = {
        "minimumChordConfidence": MIN_CHORD_CONFIDENCE,
        "adjustmentCount": len(diagnostics),
        "adjustments": diagnostics,
        "policy": (
            "derive-one-non-overlapping-harmonic-timeline-first-then-remap-only-"
            "pitch-equivalent-events-inside-each-segments-confident-chord-zone"
        ),
        "previousTimelineBaseline": {
            "passingSegments": 5,
            "segmentCount": 6,
        },
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "7.1-phase-1-canonical-timeline-voicing-handoff"
    result["guitarBrainLesson"] = (
        "never-use-overlapping-parent-chords-to-remap-events-after-a-canonical-timeline-exists"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "7.1-phase-1-canonical-timeline-voicing-handoff",
        "minimumChordConfidence": MIN_CHORD_CONFIDENCE,
        "chordPriors": CHORD_POSITION_PRIORS,
    }
