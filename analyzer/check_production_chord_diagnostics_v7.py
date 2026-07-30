from copy import deepcopy

from production_chord_diagnostics import attach_rhythm_chord_diagnostics


def event(start, end, midi):
    return {
        "start": start,
        "end": end,
        "duration": end - start,
        "midi": midi,
        "amplitude": 0.9,
        "stringIndex": 0,
        "fret": 0,
        "technique": None,
        "bendSemitones": 0.0,
    }


def main():
    events = []
    shapes = [
        (0.0, [57, 61, 64]),
        (0.8, [50, 54, 57]),
        (1.6, [52, 56, 59]),
        (2.4, [55, 59, 62, 64]),
    ]

    for start, midis in shapes:
        for midi in midis:
            events.append(event(start, start + 0.72, midi))

    original_events = deepcopy(events)
    tab = "e|---|\nB|---|\nG|---|\nD|---|\nA|---|\nE|---|"
    base = {
        "generatedTab": tab,
        "events": events,
        "noteCount": len(events),
        "techniques": [],
    }

    rhythm = attach_rhythm_chord_diagnostics(base, "rhythm")
    analysis = rhythm["chordAnalysis"]

    assert rhythm is not base
    assert rhythm["generatedTab"] == tab
    assert rhythm["events"] is events
    assert events == original_events
    assert rhythm["chordAnalysisMode"] == "diagnostic-only"
    assert rhythm["chordAnalysisAffectsTab"] is False
    assert analysis["engineVersion"] == 6
    assert analysis["noSyntheticNotes"] is True
    assert analysis["matchedChordWindowCount"] > 0
    assert analysis["sustainedChordCount"] > 0

    assert attach_rhythm_chord_diagnostics(base, "lead") is base
    assert attach_rhythm_chord_diagnostics(base, "bass") is base
    assert "chordAnalysis" not in base
    assert base["generatedTab"] == tab
    assert base["events"] == original_events

    print("V7 PRODUCTION CHORD ADAPTER PRESERVED")
    print("Rhythm gains read-only chord diagnostics.")
    print("Lead, bass, tab, and note events remain unchanged.")


if __name__ == "__main__":
    main()
