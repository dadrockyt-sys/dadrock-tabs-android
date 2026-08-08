from __future__ import annotations

from collections import Counter
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2

# Professional tab reference uses conventional 1-based guitar strings:
# 1 = high E, 2 = B, 3 = G, 4 = D, 5 = A, 6 = low E.
OPEN_STRING_MIDI_1_BASED = {
    1: 64,
    2: 59,
    3: 55,
    4: 50,
    5: 45,
    6: 40,
}


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def midi_from_reference_note(note: dict[str, Any]) -> int | None:
    explicit = integer(note.get("midi"))
    if explicit is not None:
        return explicit

    string_number = integer(note.get("string"))
    fret = integer(note.get("fret"))
    if string_number not in OPEN_STRING_MIDI_1_BASED or fret is None:
        return None
    if fret < 0 or fret > 24:
        return None
    return OPEN_STRING_MIDI_1_BASED[string_number] + fret


def reference_tokens(reference: dict[str, Any]) -> Counter[tuple[int, int, int]]:
    measures = reference.get("measures")
    if not isinstance(measures, list):
        raise RuntimeError("Professional reference measures missing.")

    tokens: Counter[tuple[int, int, int]] = Counter()
    explicit_midi_count = 0
    derived_midi_count = 0
    unusable_note_count = 0

    for measure_row in measures:
        if not isinstance(measure_row, dict):
            continue
        measure = integer(measure_row.get("measureNumber"))
        if measure is None or not v2.MEASURE_START <= measure <= v2.MEASURE_END:
            continue

        events = measure_row.get("events")
        if not isinstance(events, list):
            continue

        for event in events:
            if not isinstance(event, dict):
                continue
            step = integer(event.get("quantizedStep"))
            if step is None:
                continue

            notes = event.get("notes")
            if not isinstance(notes, list):
                continue

            for note in notes:
                if not isinstance(note, dict):
                    continue

                explicit = integer(note.get("midi"))
                midi = midi_from_reference_note(note)
                if midi is None:
                    unusable_note_count += 1
                    continue

                if explicit is not None:
                    explicit_midi_count += 1
                else:
                    derived_midi_count += 1
                tokens[(measure, step, midi)] += 1

    print("Professional pitch-token normalization:")
    print("  explicit MIDI notes:", explicit_midi_count)
    print("  string/fret-derived MIDI notes:", derived_midi_count)
    print("  unusable professional notes:", unusable_note_count)
    print("  professional pitch tokens:", sum(tokens.values()))

    return tokens


def main() -> None:
    # Keep every detector, timing-grid, scoring, protection, and output rule from V2.
    # Only repair the professional-reference normalization function.
    v2.reference_tokens = reference_tokens
    v2.main()


if __name__ == "__main__":
    main()
