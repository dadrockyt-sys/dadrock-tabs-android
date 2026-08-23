from __future__ import annotations

from dataclasses import dataclass

A4_HZ = 440.0
A4_MIDI = 69
MAX_FRET = 24

# High string to low string, matching DadRock TAB stringIndex ordering.
STANDARD_BASS_STRINGS = (
    ("G", 43),
    ("D", 38),
    ("A", 33),
    ("E", 28),
)


def midi_to_hz(midi: int) -> float:
    """Convert a MIDI note number to equal-tempered frequency in Hz."""
    value = int(midi)
    if not 0 <= value <= 127:
        raise ValueError("MIDI note must be between 0 and 127")
    return A4_HZ * (2.0 ** ((value - A4_MIDI) / 12.0))


def playable_midi_bounds() -> tuple[int, int]:
    lowest = min(open_midi for _, open_midi in STANDARD_BASS_STRINGS)
    highest = max(open_midi + MAX_FRET for _, open_midi in STANDARD_BASS_STRINGS)
    return lowest, highest


def playable_fundamental_hz_bounds() -> tuple[float, float]:
    low_midi, high_midi = playable_midi_bounds()
    return midi_to_hz(low_midi), midi_to_hz(high_midi)


@dataclass(frozen=True)
class BassPosition:
    string_index: int
    string_label: str
    fret: int
    midi: int
    hz: float


def position(string_index: int, fret: int) -> BassPosition:
    if not 0 <= int(string_index) < len(STANDARD_BASS_STRINGS):
        raise ValueError("Bass stringIndex must be 0..3")
    if not 0 <= int(fret) <= MAX_FRET:
        raise ValueError(f"Bass fret must be 0..{MAX_FRET}")

    label, open_midi = STANDARD_BASS_STRINGS[int(string_index)]
    midi = open_midi + int(fret)
    return BassPosition(
        string_index=int(string_index),
        string_label=label,
        fret=int(fret),
        midi=midi,
        hz=midi_to_hz(midi),
    )


def pitch_matches_position(midi: int, string_index: int, fret: int) -> bool:
    try:
        return position(string_index, fret).midi == int(midi)
    except (TypeError, ValueError):
        return False


def describe() -> dict:
    low_midi, high_midi = playable_midi_bounds()
    low_hz, high_hz = playable_fundamental_hz_bounds()
    return {
        "instrument": "bass",
        "tuning": "Standard Bass",
        "stringLabels": [label for label, _ in STANDARD_BASS_STRINGS],
        "openMidi": [midi for _, midi in STANDARD_BASS_STRINGS],
        "maximumFret": MAX_FRET,
        "playableMidiMinimum": low_midi,
        "playableMidiMaximum": high_midi,
        "playableFundamentalHzMinimum": round(low_hz, 6),
        "playableFundamentalHzMaximum": round(high_hz, 6),
        "equalTemperamentA4Hz": A4_HZ,
        "referenceFree": True,
        "diagnosticOnly": True,
        "analyzerRoutingEnabled": False,
        "professionalStructuredIdentityEnabled": False,
    }


__all__ = [
    "A4_HZ",
    "MAX_FRET",
    "STANDARD_BASS_STRINGS",
    "BassPosition",
    "midi_to_hz",
    "playable_midi_bounds",
    "playable_fundamental_hz_bounds",
    "position",
    "pitch_matches_position",
    "describe",
]
