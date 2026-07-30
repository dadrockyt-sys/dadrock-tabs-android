#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from bass_technique_diagnostics_v7 import detect_reference_guided_bass_techniques
except ImportError:
    from analyzer.bass_technique_diagnostics_v7 import detect_reference_guided_bass_techniques


def synthetic_bass_events() -> list[dict]:
    return [
        {"start": 0.00, "midi": 40, "stringIndex": 3, "fret": 12},
        {"start": 0.30, "midi": 38, "stringIndex": 3, "fret": 10},
        {"start": 0.60, "midi": 40, "stringIndex": 3, "fret": 12},
        {"start": 1.20, "midi": 45, "stringIndex": 2, "fret": 12},
        {"start": 2.10, "midi": 47, "stringIndex": 2, "fret": 14},
    ]


def main() -> None:
    events = synthetic_bass_events()
    before = deepcopy(events)
    diagnostics = detect_reference_guided_bass_techniques(events)

    checks = {
        "detectsFiveSevenContour": diagnostics.get("contour5And7Detected") is True,
        "detectsSlideTarget": diagnostics.get("slideDetected") is True
        and diagnostics.get("slideTargetFret") == 14,
        "detectsMutedAttack": diagnostics.get("mutedAttackDetected") is True,
        "detectsRest": diagnostics.get("restDetected") is True,
        "virtualVoicingReadOnly": diagnostics.get("virtualVoicingReadOnly") is True,
        "eventsReadOnly": events == before and diagnostics.get("eventsReadOnly") is True,
        "eventCountUnchanged": diagnostics.get("eventCount") == len(events),
        "noSyntheticNotes": diagnostics.get("syntheticNoteCount") == 0,
        "pitchOrFretUnchanged": diagnostics.get("pitchOrFretChanged") is False,
        "doesNotAffectEvents": diagnostics.get("affectsEvents") is False,
        "doesNotAffectTab": diagnostics.get("affectsTab") is False,
    }

    failed = False
    print("JIMMY PAIGE V7 BASS TECHNIQUE DIAGNOSTICS HELPER")
    print("=" * 68)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit("\nV7 bass technique diagnostics regression detected.")

    print("\nV7 BASS TECHNIQUE DIAGNOSTICS HELPER PRESERVED 💚")
    print("5/7 contour, slide-to-14, mute, and rest evidence are diagnostic-only.")
    print("Events, frets, pitches, timing, and generated tab remain untouched.")


if __name__ == "__main__":
    main()
