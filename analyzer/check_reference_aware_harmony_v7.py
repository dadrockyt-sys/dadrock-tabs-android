#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from reference_aware_harmony import (
        promote_reference_aware_two_tone_chords,
    )
except ImportError:
    from analyzer.reference_aware_harmony import (
        promote_reference_aware_two_tone_chords,
    )


def synthetic_events() -> list[dict]:
    # Repeated E and G evidence. D intentionally has only one represented tone.
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
    before_events = deepcopy(events)
    base_analysis = {
        "engineVersion": 6,
        "chordVocabulary": ["A(tp2)", "G6"],
        "noSyntheticNotes": True,
    }
    chords = [
        {"name": "E", "pitchClasses": [4, 8, 11]},
        {"name": "G", "pitchClasses": [2, 7, 11]},
        {"name": "D", "pitchClasses": [2, 6, 9]},
    ]
    result = promote_reference_aware_two_tone_chords(
        events,
        base_analysis,
        chords,
        ["G6", "A(tp2)", "E", "D", "E", "G", "E"],
    )

    vocabulary = set(result.get("chordVocabulary") or [])
    promotions = result.get("referenceAwarePromotions") or {}
    checks = {
        "preservesExistingVocabulary": {"A(tp2)", "G6"}.issubset(vocabulary),
        "promotesE": "E" in vocabulary and promotions.get("E") is True,
        "promotesG": "G" in vocabulary and promotions.get("G") is True,
        "doesNotPromoteD": "D" not in vocabulary,
        "eventsReadOnly": events == before_events,
        "noSyntheticNotes": result.get("noSyntheticNotes") is True,
        "doesNotAffectTab": result.get("referenceAwareAffectsTab") is False,
        "doesNotAffectEvents": result.get("referenceAwareAffectsEvents") is False,
    }

    failed = False
    print("JIMMY PAIGE V7 REFERENCE-AWARE HARMONY HELPER")
    print("=" * 66)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit("\nV7 reference-aware harmony helper regression detected.")

    print("\nV7 REFERENCE-AWARE HARMONY HELPER PRESERVED 💚")
    print("E and G require two real chord tones; D remains unpromoted.")


if __name__ == "__main__":
    main()
