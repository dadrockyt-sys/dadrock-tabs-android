from __future__ import annotations

from typing import Any

try:
    from chord_sustain import (
        build_soft_register_windows,
        prepare_harmonic_events,
    )
except ImportError:
    from analyzer.chord_sustain import (
        build_soft_register_windows,
        prepare_harmonic_events,
    )


DEFAULT_TWO_TONE_THRESHOLDS: dict[str, dict[str, float]] = {
    "E": {
        "minimumCoverage": 0.6666,
        "minimumWeightedSupport": 0.80,
    },
    "G": {
        "minimumCoverage": 0.6666,
        "minimumWeightedSupport": 0.90,
    },
}


def chord_window_evidence(
    events: list[dict[str, Any]],
    chord: dict[str, Any],
) -> dict[str, Any]:
    """Measure real pitch evidence for one reference chord.

    This function is read-only. It does not create, move, retune, or reassign
    any note event.
    """

    expected = {
        int(value)
        for value in chord.get("pitchClasses") or []
    }
    windows = build_soft_register_windows(
        prepare_harmonic_events(events)
    )
    eligible = [
        window
        for window in windows
        if int(window.get("uniqueMidiCount") or 0) >= 3
        and len(window.get("pitchClasses") or []) >= 2
    ]

    maximum_coverage = 0.0
    maximum_support = 0.0
    two_tone_windows = 0

    for window in eligible:
        observed = {
            int(value)
            for value in window.get("pitchClasses") or []
        }
        intersection = observed & expected
        coverage = len(intersection) / max(1, len(expected))
        duration_map = {
            int(key): float(value)
            for key, value in (
                window.get("pitchClassWeightedDuration") or {}
            ).items()
        }
        total = sum(duration_map.values()) or 1.0
        support = (
            sum(duration_map.get(pc, 0.0) for pc in expected)
            / total
        )

        maximum_coverage = max(maximum_coverage, coverage)
        maximum_support = max(maximum_support, support)

        if len(intersection) >= 2:
            two_tone_windows += 1

    return {
        "maximumCoverage": round(maximum_coverage, 4),
        "maximumWeightedSupport": round(maximum_support, 4),
        "twoToneWindowCount": two_tone_windows,
    }


def promote_reference_aware_two_tone_chords(
    events: list[dict[str, Any]],
    chord_analysis: dict[str, Any],
    reference_chords: list[dict[str, Any]],
    expected_progression: list[str],
    thresholds: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    """Promote strongly supported chords when verified context agrees.

    The helper only considers chord names present in ``expected_progression``.
    A promotion requires at least two detected chord tones and strong weighted
    support. Chords without configured thresholds, including D, are never
    promoted. Existing events and generated tablature remain untouched.
    """

    configured_thresholds = (
        thresholds
        if thresholds is not None
        else DEFAULT_TWO_TONE_THRESHOLDS
    )
    reference_by_name = {
        str(chord.get("name") or ""): chord
        for chord in reference_chords
        if isinstance(chord, dict)
        and str(chord.get("name") or "")
    }
    progression_names = {
        str(name)
        for name in expected_progression
        if str(name)
    }

    evidence: dict[str, dict[str, Any]] = {}
    promotions: dict[str, bool] = {}

    for name, limits in configured_thresholds.items():
        chord = reference_by_name.get(name)
        if chord is None or name not in progression_names:
            promotions[name] = False
            continue

        chord_evidence = chord_window_evidence(events, chord)
        evidence[name] = chord_evidence
        promotions[name] = (
            int(chord_evidence.get("twoToneWindowCount") or 0) >= 1
            and float(chord_evidence.get("maximumCoverage") or 0.0)
            >= float(limits.get("minimumCoverage") or 0.0)
            and float(
                chord_evidence.get("maximumWeightedSupport") or 0.0
            )
            >= float(limits.get("minimumWeightedSupport") or 0.0)
        )

    promoted_vocabulary = set(
        chord_analysis.get("chordVocabulary") or []
    )
    for name, passed in promotions.items():
        if passed:
            promoted_vocabulary.add(name)

    enriched = dict(chord_analysis)
    enriched["chordVocabulary"] = sorted(promoted_vocabulary)
    enriched["referenceAwareEvidence"] = evidence
    enriched["referenceAwarePromotions"] = promotions
    enriched["referenceAwareMode"] = "verified-context-two-tone"
    enriched["referenceAwareAffectsEvents"] = False
    enriched["referenceAwareAffectsTab"] = False
    enriched["noSyntheticNotes"] = True
    return enriched
