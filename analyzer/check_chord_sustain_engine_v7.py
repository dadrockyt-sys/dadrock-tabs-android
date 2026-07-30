from __future__ import annotations

import copy
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from chord_sustain import (  # noqa: E402
    DEFAULT_CHORD_VOCABULARY,
    detect_chord_sustain,
    register_weight,
)


MIDI_BY_PITCH_CLASS = {
    1: 61,
    2: 62,
    4: 64,
    6: 66,
    7: 67,
    8: 68,
    9: 69,
    11: 71,
}


def make_chord_events(
    pitch_classes: list[int],
    start: float = 0.0,
    duration: float = 1.1,
) -> list[dict]:
    return [
        {
            "start": start,
            "end": start + duration,
            "duration": duration,
            "midi": MIDI_BY_PITCH_CLASS[pitch_class],
            "amplitude": 0.8,
            "stringIndex": index,
            "fret": index + 2,
            "technique": None,
            "bendSemitones": 0.0,
        }
        for index, pitch_class in enumerate(pitch_classes)
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    require(register_weight(45) == 1.0, "MIDI 45 lost full register weight")
    require(register_weight(76) == 1.0, "MIDI 76 lost full register weight")
    require(register_weight(40) == 0.65, "MIDI 40 lost edge register weight")
    require(register_weight(84) == 0.65, "MIDI 84 lost edge register weight")
    require(register_weight(39) == 0.30, "Low outside-register weight changed")
    require(register_weight(85) == 0.30, "High outside-register weight changed")

    expected_names = {
        "A",
        "A(tp2)",
        "D",
        "E",
        "G",
        "G6",
    }
    actual_names = {
        str(chord["name"])
        for chord in DEFAULT_CHORD_VOCABULARY
    }
    require(actual_names == expected_names, "V6 chord vocabulary changed")

    detected_names: set[str] = set()

    for chord in DEFAULT_CHORD_VOCABULARY:
        name = str(chord["name"])
        events = make_chord_events(
            [int(value) for value in chord["pitchClasses"]]
        )
        original_events = copy.deepcopy(events)
        result = detect_chord_sustain(
            events,
            chords=[chord],
            minimum_sustain_seconds=0.35,
        )

        require(events == original_events, f"{name}: detector mutated note events")
        require(result["engineVersion"] == 6, f"{name}: engine version changed")
        require(result["noSyntheticNotes"] is True, f"{name}: synthetic-note guard failed")
        require(result["matchedChordWindowCount"] >= 1, f"{name}: no matched windows")
        require(result["sustainedChordCount"] >= 1, f"{name}: sustain was not preserved")
        require(name in result["chordVocabulary"], f"{name}: chord was not identified")
        detected_names.update(result["chordVocabulary"])

    require(
        expected_names <= detected_names,
        "Not every protected V6 chord was detected",
    )

    empty_result = detect_chord_sustain([])
    require(empty_result["chords"] == [], "Empty input created chord events")
    require(empty_result["noSyntheticNotes"] is True, "Empty-input safety guard failed")

    print("JIMMY PAIGE V7 CHORD-SUSTAIN ENGINE PRESERVED 💚")
    print(f"Protected vocabulary: {', '.join(sorted(detected_names))}")
    print("Production note events remain read-only.")


if __name__ == "__main__":
    main()
