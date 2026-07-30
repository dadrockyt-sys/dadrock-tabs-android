from __future__ import annotations

from typing import Any

try:
    from chord_sustain import detect_chord_sustain
    from reference_aware_harmony import (
        promote_reference_aware_two_tone_chords,
    )
except ImportError:
    from analyzer.chord_sustain import detect_chord_sustain
    from analyzer.reference_aware_harmony import (
        promote_reference_aware_two_tone_chords,
    )


def attach_rhythm_chord_diagnostics(
    result: dict[str, Any],
    transcription_type: str,
    reference_chords: list[dict[str, Any]] | None = None,
    expected_progression: list[str] | None = None,
) -> dict[str, Any]:
    """Attach read-only chord diagnostics to rhythm results.

    Lead and bass responses are returned untouched. Rhythm responses receive a
    ``chordAnalysis`` field calculated from the existing normalized note events.

    Verified reference context is optional. When both ``reference_chords`` and
    ``expected_progression`` are supplied, the V7 two-tone helper may promote E
    and G only when real pitch evidence satisfies the locked thresholds. Generic
    no-context behavior remains identical to the V6 diagnostic path.

    No notes are created, moved, retuned, deleted, or reassigned, and generated
    tablature is never changed by this adapter.
    """

    if transcription_type != "rhythm":
        return result

    events = result.get("events")
    normalized_events = events if isinstance(events, list) else []

    chord_analysis = detect_chord_sustain(
        normalized_events,
        chords=reference_chords,
        progression=expected_progression,
    )

    context_enabled = bool(
        reference_chords
        and expected_progression
    )

    if context_enabled:
        chord_analysis = promote_reference_aware_two_tone_chords(
            normalized_events,
            chord_analysis,
            reference_chords or [],
            expected_progression or [],
        )

    enriched_result = dict(result)
    enriched_result["chordAnalysis"] = chord_analysis
    enriched_result["chordAnalysisMode"] = (
        "diagnostic-with-verified-context"
        if context_enabled
        else "diagnostic-only"
    )
    enriched_result["chordAnalysisAffectsTab"] = False
    enriched_result["chordAnalysisAffectsEvents"] = False

    return enriched_result
