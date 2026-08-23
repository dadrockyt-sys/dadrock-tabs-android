#!/usr/bin/env python3
from __future__ import annotations

from v143_rhythm_semantic_primary_note_guard import guard_semantic_events


def _mapping(primary: bool, index: int, count: int) -> dict:
    return {
        "version": 2,
        "chordNoteIndex": index,
        "chordNoteCount": count,
        "primaryTechniqueNote": primary,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }


def main() -> None:
    events = [
        {
            "measure": 1,
            "step": 0,
            "midi": 57,
            "stringIndex": 2,
            "fret": 2,
            "noteMapping": _mapping(True, 0, 2),
            "bendSemitones": 2,
            "bendTargetMidi": 59,
            "bendTargetFret": 4,
            "bendRelease": True,
            "bendEvidence": {"viewAgreement": 2},
            "rhythmTechniques": [
                {"type": "bend", "source": "reference-free-audio-pitch-contour"},
                {"type": "bend-release", "source": "reference-free-audio-pitch-contour"},
            ],
            # This link intentionally targets a secondary chord tone and must be removed.
            "legatoTargetEventIndex": 1,
            "legatoTargetFret": 7,
            "legatoTargetMidi": 64,
            "legatoEvidence": {"viewAgreement": 2},
        },
        {
            "measure": 1,
            "step": 0,
            "midi": 64,
            "stringIndex": 0,
            "fret": 0,
            "noteMapping": _mapping(False, 1, 2),
            "bendSemitones": 1,
            "bendTargetMidi": 65,
            "bendTargetFret": 1,
            "bendEvidence": {"viewAgreement": 2},
            "rhythmTechniques": [
                {"type": "bend", "source": "reference-free-audio-pitch-contour"},
                {"type": "slide-up", "source": "reference-free-audio-legato-evidence"},
            ],
            "legatoContinuationFromEventIndex": 0,
            "legatoContinuationType": "slide-up",
        },
        {
            "measure": 1,
            "step": 4,
            "midi": 59,
            "stringIndex": 1,
            "fret": 0,
            "noteMapping": _mapping(True, 0, 1),
            "rhythmTechniques": [
                {"type": "vibrato", "source": "upstream-technique"},
            ],
        },
    ]

    guarded, diagnostics = guard_semantic_events(events)

    # Notes, attack locations, pitch and positions are immutable.
    assert len(guarded) == len(events)
    for before, after in zip(events, guarded):
        for field in ("measure", "step", "midi", "stringIndex", "fret"):
            assert before[field] == after[field]

    # Primary bend remains, but the invalid primary->secondary legato link is removed.
    assert guarded[0]["bendSemitones"] == 2
    assert "legatoTargetEventIndex" not in guarded[0]
    assert any(item.get("type") == "bend" for item in guarded[0]["rhythmTechniques"])
    assert not any(item.get("source") == "reference-free-audio-legato-evidence" for item in guarded[0]["rhythmTechniques"])

    # Secondary chord tone cannot carry audio-derived bend/legato semantics.
    assert "bendSemitones" not in guarded[1]
    assert "bendEvidence" not in guarded[1]
    assert "legatoContinuationFromEventIndex" not in guarded[1]
    assert guarded[1]["rhythmTechniques"] == []

    # Non-audio explicit evidence on a primary monophonic event is untouched.
    assert guarded[2]["rhythmTechniques"] == [
        {"type": "vibrato", "source": "upstream-technique"}
    ]

    report = diagnostics.to_dict()
    assert report["eventCountChanged"] is False
    assert report["attackTimingChanged"] is False
    assert report["pitchChanged"] is False
    assert report["stringFretChanged"] is False
    assert report["referenceFree"] is True
    assert report["runtimeLabelsRequired"] is False
    assert report["productionModified"] is False
    assert report["strippedSecondaryBends"] == 1
    assert report["strippedInvalidPrimaryLegato"] == 1

    print("V143 rhythm semantic primary-note guard proof passed")
    print(report)


if __name__ == "__main__":
    main()
