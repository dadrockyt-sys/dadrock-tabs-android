from __future__ import annotations

import json
from copy import deepcopy

from v143_rhythm_guitar_note_mapper import (
    MAX_FRET,
    OPEN_MIDI_HIGH_TO_LOW,
    STRING_NAMES_HIGH_TO_LOW,
    legal_positions_for_midi,
    map_selected_v143_rows,
)


def canonical(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    )


def main() -> None:
    assert STRING_NAMES_HIGH_TO_LOW == ("e", "B", "G", "D", "A", "E")
    assert OPEN_MIDI_HIGH_TO_LOW == (64, 59, 55, 50, 45, 40)
    assert MAX_FRET == 24

    assert legal_positions_for_midi(40)[0] == {
        "stringIndex": 5,
        "stringName": "E",
        "fret": 0,
    }

    assert legal_positions_for_midi(52)[0] == {
        "stringIndex": 3,
        "stringName": "D",
        "fret": 2,
    }

    assert legal_positions_for_midi(64)[0] == {
        "stringIndex": 0,
        "stringName": "e",
        "fret": 0,
    }

    assert legal_positions_for_midi(88) == [
        {
            "stringIndex": 0,
            "stringName": "e",
            "fret": 24,
        }
    ]

    try:
        legal_positions_for_midi(39)
    except ValueError:
        pass
    else:
        raise AssertionError("MIDI below guitar range was accepted")

    rows = [
        {
            "measure": 1,
            "step": 0,
            "timeSeconds": 1.000,
            "dominantMidi": 52,
            "pitchHypotheses": [
                {
                    "midi": 52,
                    "sourceCount": 2,
                    "maxAmplitude": 0.85,
                    "minGridError": 0.002,
                    "maxDuration": 0.28,
                }
            ],
            "v143Score": 3.25,
            "v143Rank": 1,
            "v143Selected": True,
        },
        {
            "measure": 1,
            "step": 1,
            "timeSeconds": 1.125,
            "dominantMidi": 55,
            "pitchHypotheses": [
                {
                    "midi": 55,
                    "sourceCount": 2,
                    "maxAmplitude": 0.75,
                    "minGridError": 0.001,
                    "maxDuration": 0.21,
                },
                {
                    "midi": 57,
                    "sourceCount": 1,
                    "maxAmplitude": 0.60,
                    "minGridError": 0.004,
                    "maxDuration": 0.23,
                },
            ],
            "v143Score": 1.50,
            "v143Rank": 3,
            "v143Selected": False,
        },
        {
            "measure": 2,
            "step": 0,
            "timeSeconds": 3.000,
            "dominantMidi": 64,
            "pitchHypotheses": [
                {
                    "midi": 64,
                    "sourceCount": 2,
                    "maxAmplitude": 0.90,
                    "minGridError": 0.000,
                    "maxDuration": 0.30,
                }
            ],
            "v143Score": 2.75,
            "v143Rank": 2,
            "v143Selected": True,
        },
    ]

    original = deepcopy(rows)

    first = map_selected_v143_rows(rows)
    second = map_selected_v143_rows(rows)

    # Mapper must never mutate the frozen V143 rows.
    assert rows == original

    # Only the frozen selection is allowed through.
    assert len(first) == 2
    assert [(row["measure"], row["step"]) for row in first] == [
        (1, 0),
        (2, 0),
    ]

    # Frozen timing and V143 outputs remain exact.
    assert first[0]["timeSeconds"] == 1.000
    assert first[0]["v143Score"] == 3.25
    assert first[0]["v143Rank"] == 1
    assert first[0]["v143Selected"] is True

    assert first[1]["timeSeconds"] == 3.000
    assert first[1]["v143Score"] == 2.75
    assert first[1]["v143Rank"] == 2
    assert first[1]["v143Selected"] is True

    # Primary note mapping.
    assert (
        first[0]["midi"],
        first[0]["stringIndex"],
        first[0]["fret"],
    ) == (52, 3, 2)

    assert (
        first[1]["midi"],
        first[1]["stringIndex"],
        first[1]["fret"],
    ) == (64, 0, 0)

    # Original pitch evidence remains byte-equivalent as data.
    assert first[0]["pitchHypotheses"] == original[0]["pitchHypotheses"]
    assert first[1]["pitchHypotheses"] == original[2]["pitchHypotheses"]

    # Additional mapped hypotheses are downstream metadata only.
    assert first[0]["mappedPitchHypotheses"][0]["midi"] == 52
    assert first[0]["mappedPitchHypotheses"][0]["preferredPosition"] == {
        "stringIndex": 3,
        "stringName": "D",
        "fret": 2,
    }

    assert all(
        row["noteMapping"]["jointChordVoicingResolved"] is False
        for row in first
    )

    # Repeat must serialize identically.
    assert canonical(first) == canonical(second)

    forbidden = (
        "professionalReference",
        "referenceLabel",
        "runtimeLabel",
    )
    for row in first:
        assert all(key not in row for key in forbidden)

    print("=== V143 RHYTHM GUITAR NOTE MAPPER VERIFIED ===")
    print("Frozen V143 selection consumed downstream: True")
    print("Frozen score/rank/selection fields preserved: True")
    print("Quantized timing preserved exactly: True")
    print("Original pitch hypotheses preserved: True")
    print("Standard tuning high-e -> low-E convention: True")
    print("24-fret repository range enforced: True")
    print("Deterministic primary string/fret mapping: True")
    print("Chord pitch evidence retained for later voicing: True")
    print("Input rows mutated: False")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("Deterministic repeat exact: True")
    print("READY FOR SUSTAIN/TECHNIQUE INTEGRATION: True")


if __name__ == "__main__":
    main()
