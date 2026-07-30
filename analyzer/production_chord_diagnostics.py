from __future__ import annotations

from typing import Any

try:
    from chord_sustain import detect_chord_sustain
except ImportError:
    from analyzer.chord_sustain import detect_chord_sustain


def attach_rhythm_chord_diagnostics(
    result: dict[str, Any],
    transcription_type: str,
) -> dict[str, Any]:
    """Attach V6 chord diagnostics without changing production tab data.

    Lead and bass responses are returned untouched. Rhythm responses receive
    a new ``chordAnalysis`` field calculated from the existing normalized note
    events. The detector is read-only and never creates or rewrites notes.
    """

    if transcription_type != "rhythm":
        return result

    events = result.get("events")
    normalized_events = events if isinstance(events, list) else []

    enriched_result = dict(result)
    enriched_result["chordAnalysis"] = detect_chord_sustain(
        normalized_events,
    )
    enriched_result["chordAnalysisMode"] = "diagnostic-only"
    enriched_result["chordAnalysisAffectsTab"] = False

    return enriched_result
