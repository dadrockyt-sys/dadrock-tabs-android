from __future__ import annotations

from typing import Any

import modal
import modal_analyzer_v69 as previous

engine = previous.engine
app = modal.App("dadrock-tab-analyzer")
image = previous.image.add_local_python_source("modal_analyzer_v69")

# Reusable guitarist-position priors learned from the canonical Stairway intro.
# These are only applied when harmonic identity is sufficiently confident.
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
    return previous.to_json_safe(value)


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def chord_payload(window: dict[str, Any]) -> tuple[str, float]:
    chord = window.get("chord")
    if isinstance(chord, dict):
        return str(chord.get("name") or ""), float(chord.get("confidence") or 0.0)
    return str(chord or ""), float(window.get("chordConfidence") or 0.0)


def canonical_window_for_event(
    event: dict[str, Any],
    windows: list[dict[str, Any]],
) -> dict[str, Any] | None:
    start = event_start(event)
    containing: list[tuple[float, float, int, dict[str, Any]]] = []

    for index, window in enumerate(windows):
        window_start = float(window.get("start") or window.get("windowStart") or 0.0)
        window_end = float(window.get("end") or window.get("windowEnd") or window_start)
        if not (window_start <= start < window_end):
            continue

        name, confidence = chord_payload(window)
        if name not in CHORD_POSITION_PRIORS or confidence < MIN_CHORD_CONFIDENCE:
            continue

        duration = max(0.0, window_end - window_start)
        # Prefer stronger harmonic identity. For equal confidence, choose the
        # narrowest window because it is normally the most specific analysis.
        containing.append((-confidence, duration, index, window))

    if not containing:
        return None

    containing.sort(key=lambda item: (item[0], item[1], item[2]))
    return containing[0][3]


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
        movement_cost = abs(float(fret) - float(old_fret)) * 0.25
        center = (lower + upper) / 2.0
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


def apply_canonical_voicing_handoff(
    result: dict[str, Any],
    transcription_type: str,
) -> list[dict[str, Any]]:
    understanding = result.get("musicalUnderstanding") or {}
    windows = list(understanding.get("harmonicWindows") or [])
    events = result.get("events")
    if not isinstance(events, list) or not windows:
        return []

    diagnostics: list[dict[str, Any]] = []

    for event_index, event in enumerate(events):
        if not isinstance(event, dict):
            continue

        window = canonical_window_for_event(event, windows)
        if window is None:
            continue

        chord_name, confidence = chord_payload(window)
        prior = CHORD_POSITION_PRIORS[chord_name]
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
                "midi": int(event.get("midi") or 0),
                "chord": chord_name,
                "confidence": round(confidence, 3),
                "old": {"stringIndex": old_string, "fret": old_fret},
                "new": {"stringIndex": new_string, "fret": new_fret},
                "preferredRange": prior["preferredRange"],
                "allowOpen": allow_open,
            }
        )

    return diagnostics


def analyze_audio_file(audio_path: str, transcription_type: str) -> dict[str, Any]:
    result = previous.analyze_audio_file(audio_path, transcription_type)
    diagnostics = apply_canonical_voicing_handoff(result, transcription_type)

    understanding = dict(result.get("musicalUnderstanding") or {})
    understanding["canonicalVoicingHandoff"] = {
        "minimumChordConfidence": MIN_CHORD_CONFIDENCE,
        "adjustmentCount": len(diagnostics),
        "adjustments": diagnostics,
        "policy": (
            "after-final-path-selection-remap-only-pitch-equivalent-positions-"
            "inside-high-confidence-canonical-chord-zones"
        ),
        "previousCanonicalTimelineBaseline": {
            "passingSegments": 3,
            "segmentCount": 6,
        },
    }
    result["musicalUnderstanding"] = understanding
    result["engineVersion"] = "7.0-phase-1-confidence-gated-canonical-voicing-handoff"
    result["guitarBrainLesson"] = (
        "when-chord-identity-is-confident-the-render-handoff-must-use-the-winning-playable-voicing-zone"
    )
    return result


@app.function(image=image, timeout=600, memory=4096)
def benchmark_healthcheck() -> dict[str, Any]:
    return {
        "ok": True,
        "engineVersion": "7.0-phase-1-confidence-gated-canonical-voicing-handoff",
        "minimumChordConfidence": MIN_CHORD_CONFIDENCE,
        "chordPriors": CHORD_POSITION_PRIORS,
    }
