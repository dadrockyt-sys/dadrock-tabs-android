#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )
except ImportError:
    from analyzer.production_chord_diagnostics import (
        attach_rhythm_chord_diagnostics,
    )


def synthetic_events() -> list[dict]:
    # Real E and G evidence. D intentionally contains only one pitch class.
    return [
        {"start": 0.00, "end": 0.45, "midi": 52, "amplitude": 0.9},
        {"start": 0.00, "end": 0.45, "midi": 56, "amplitude": 0.9},
        {"start": 0.00, "end": 0.45, "midi": 64, "amplitude": 0.8},
        {"start": 0.60, "end": 1.05, "midi": 55, "amplitude": 0.9},
        {"start": 0.60, "end": 1.05, "midi": 59, "amplitude": 0.9},
        {"start": 0.60, "end": 1.05, "midi": 67, "amplitude": 0.8},
        {"start": 1.20, "end": 1.55, "midi": 50, "amplitude": 0.7},
        {"start": 1.20, "end": 1.55, "midi": 62, "amplitude": 0.7},
        {"start": 1.20, "end": 1.55, "midi": 74, "amplitude": 0.6},
    ]


def main() -> None:
    events = synthetic_events()
    base_result = {
        "generatedTab": "protected-tab",
        "events": events,
        "noteCount": len(events),
    }
    before = deepcopy(base_result)
    chords = [
        {"name": "G6", "pitchClasses": [2, 4, 7, 11]},
        {"name": "A(tp2)", "pitchClasses": [1, 4, 9]},
        {"name": "E", "pitchClasses": [4, 8, 11]},
        {"name": "D", "pitchClasses": [2, 6, 9]},
        {"name": "G", "pitchClasses": [2, 7, 11]},
    ]
    progression = ["G6", "A(tp2)", "E", "D", "E", "G", "E"]

    generic = attach_rhythm_chord_diagnostics(
        deepcopy(base_result),
        "rhythm",
    )
    contextual = attach_rhythm_chord_diagnostics(
        deepcopy(base_result),
        "rhythm",
        reference_chords=chords,
        expected_progression=progression,
    )
    lead = attach_rhythm_chord_diagnostics(
        deepcopy(base_result),
        "lead",
        reference_chords=chords,
        expected_progression=progression,
    )
    bass = attach_rhythm_chord_diagnostics(
        deepcopy(base_result),
        "bass",
        reference_chords=chords,
        expected_progression=progression,
    )

    generic_analysis = generic.get("chordAnalysis") or {}
    contextual_analysis = contextual.get("chordAnalysis") or {}
    contextual_vocabulary = set(
        contextual_analysis.get("chordVocabulary") or []
    )
    promotions = contextual_analysis.get(
        "referenceAwarePromotions"
    ) or {}

    checks = {
        "genericModeUnchanged": (
            generic.get("chordAnalysisMode") == "diagnostic-only"
            and "referenceAwareMode" not in generic_analysis
        ),
        "contextModeEnabled": (
            contextual.get("chordAnalysisMode")
            == "diagnostic-with-verified-context"
        ),
        "promotesE": (
            "E" in contextual_vocabulary
            and promotions.get("E") is True
        ),
        "promotesG": (
            "G" in contextual_vocabulary
            and promotions.get("G") is True
        ),
        "doesNotPromoteD": (
            promotions.get("D") in {None, False}
            and "D" not in contextual_vocabulary
        ),
        "tabUnchanged": (
            generic.get("generatedTab") == before["generatedTab"]
            and contextual.get("generatedTab") == before["generatedTab"]
        ),
        "eventsUnchanged": (
            generic.get("events") == before["events"]
            and contextual.get("events") == before["events"]
        ),
        "noteCountUnchanged": (
            generic.get("noteCount") == before["noteCount"]
            and contextual.get("noteCount") == before["noteCount"]
        ),
        "noSyntheticNotes": (
            contextual_analysis.get("noSyntheticNotes") is True
        ),
        "diagnosticsDoNotAffectTab": (
            contextual.get("chordAnalysisAffectsTab") is False
        ),
        "diagnosticsDoNotAffectEvents": (
            contextual.get("chordAnalysisAffectsEvents") is False
        ),
        "leadUntouched": lead == before,
        "bassUntouched": bass == before,
    }

    failed = False
    print("JIMMY PAIGE V7 PRODUCTION VERIFIED-CONTEXT ADAPTER")
    print("=" * 72)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 production verified-context adapter regression detected."
        )

    print("\nV7 PRODUCTION VERIFIED-CONTEXT ADAPTER PRESERVED 💚")
    print("Generic rhythm behavior is unchanged; E/G context is opt-in.")
    print("D remains unpromoted, and lead/bass/tab/events remain untouched.")


if __name__ == "__main__":
    main()
