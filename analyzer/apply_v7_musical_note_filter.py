#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIMELINE = ROOT / "analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py"
GRID = ROOT / "analyzer/build_v7_measure_grid_projection.py"
OVERLAY = ROOT / "lib/v7MeasureGridOverlay.js"


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"SKIP {label} already installed")
        return
    if old not in text:
        raise RuntimeError(f"Expected anchor not found for {label}: {path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"PATCH {label}")


def main() -> None:
    # Preserve useful analyzer evidence in the read-only projection. Missing values
    # safely become zero and never alter the protected production events.
    replace_once(
        TIMELINE,
        '''        "midiPitch": int(event.get("midiPitch") or event.get("pitch") or 0),
        "readOnly": True,
''',
        '''        "midiPitch": int(event.get("midiPitch") or event.get("pitch") or 0),
        "confidence": round(float(
            event.get("confidence")
            or event.get("noteConfidence")
            or event.get("probability")
            or event.get("amplitude")
            or event.get("velocity")
            or 0.0
        ), 6),
        "readOnly": True,
''',
        "timeline confidence projection",
    )

    helpers_anchor = '''def split_marker(
'''
    helpers = '''def note_confidence(note: dict[str, Any]) -> float:
    value = number(note.get("confidence"))
    if value > 1.0:
        value /= 127.0
    return max(0.0, min(1.0, value))


def filter_note_events(
    source_events: list[dict[str, Any]],
    *,
    song_duration: float,
    beat_seconds: float,
    measure_seconds: float,
    measures_per_row: int,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    # A conservative first-pass musical filter. It changes only projected copies.
    # Production events, generated TAB, pitches, frets and source timing stay untouched.
    sixteenth = beat_seconds / 4.0
    minimum_duration = max(0.055, sixteenth * 0.32)
    candidates: list[dict[str, Any]] = []

    for source_order, event in enumerate(source_events):
        if not isinstance(event, dict):
            continue
        start = max(0.0, min(song_duration, number(event.get("start"))))
        end = max(start, min(song_duration, number(event.get("end"))))
        duration = end - start
        confidence = note_confidence(event)

        if duration < minimum_duration:
            continue
        # Only apply confidence gating when the analyzer actually supplied a score.
        if confidence > 0.0 and confidence < 0.34:
            continue

        string_index = max(0, min(5, int(event.get("stringIndex") or 0)))
        fret = max(0, min(24, int(event.get("fret") or 0)))
        midi_pitch = int(event.get("midiPitch") or 0)
        slot = max(0, int(round(start / sixteenth)))
        quantized_start = min(song_duration, slot * sixteenth)
        position = musical_position(
            quantized_start,
            beat_seconds=beat_seconds,
            measure_seconds=measure_seconds,
            measures_per_row=measures_per_row,
        )
        candidates.append({
            **event,
            "sourceOrder": source_order,
            "sourceStart": round(start, 6),
            "sourceEnd": round(end, 6),
            "start": round(quantized_start, 6),
            "end": round(max(quantized_start + minimum_duration, end), 6),
            "duration": round(duration, 6),
            "confidence": round(confidence, 6),
            "stringIndex": string_index,
            "fret": fret,
            "midiPitch": midi_pitch,
            "quantizedSlot": slot,
            **position,
            "measureGridReadOnly": True,
            "musicallyFiltered": True,
        })

    # Exact duplicate collapse: one projected note per pitch/fret/string in a slot.
    exact: dict[tuple[int, int, int, int], dict[str, Any]] = {}
    for note in candidates:
        key = (
            int(note["quantizedSlot"]),
            int(note["stringIndex"]),
            int(note["fret"]),
            int(note["midiPitch"]),
        )
        previous = exact.get(key)
        score = (number(note.get("confidence")), number(note.get("duration")))
        previous_score = (
            number(previous.get("confidence")),
            number(previous.get("duration")),
        ) if previous else (-1.0, -1.0)
        if previous is None or score > previous_score:
            exact[key] = note

    # Lead TAB should not contain a stack of unrelated simultaneous detections.
    # Keep one musically strongest note per 1/16 slot, favouring confidence,
    # duration and continuity with the previous selected fret/string.
    by_slot: dict[int, list[dict[str, Any]]] = {}
    for note in exact.values():
        by_slot.setdefault(int(note["quantizedSlot"]), []).append(note)

    selected: list[dict[str, Any]] = []
    previous: dict[str, Any] | None = None
    for slot in sorted(by_slot):
        options = by_slot[slot]

        def musical_score(note: dict[str, Any]) -> tuple[float, float, float, float]:
            confidence = number(note.get("confidence"))
            duration = number(note.get("duration"))
            if previous is None:
                continuity = 0.0
            else:
                fret_jump = abs(int(note["fret"]) - int(previous["fret"]))
                string_jump = abs(int(note["stringIndex"]) - int(previous["stringIndex"]))
                continuity = -(fret_jump * 0.10 + string_jump * 0.22)
            # Open strings are valid, but should not beat an equally strong fretted note.
            fretted_bonus = 0.08 if int(note["fret"]) > 0 else 0.0
            return (confidence + fretted_bonus + continuity, duration, -int(note["stringIndex"]), -int(note["fret"]))

        winner = max(options, key=musical_score)

        # Suppress repeated open-string machine-gun noise on the same string while
        # preserving real repeated notes separated by at least an eighth note.
        if (
            previous is not None
            and int(winner["fret"]) == 0
            and int(previous["fret"]) == 0
            and int(winner["stringIndex"]) == int(previous["stringIndex"])
            and int(winner["quantizedSlot"]) - int(previous["quantizedSlot"]) < 2
        ):
            continue

        selected.append(winner)
        previous = winner

    counts = {
        "source": len(source_events),
        "durationAndConfidencePassed": len(candidates),
        "exactDuplicatesRemoved": len(candidates) - len(exact),
        "slotCollisionsRemoved": len(exact) - len(selected),
        "filtered": len(selected),
    }
    return selected, counts


def split_marker(
'''
    replace_once(GRID, helpers_anchor, helpers, "musical filter helpers")

    old_note_block = '''    note_events: list[dict[str, Any]] = []
    for event in (projection.get("noteEvents") or []):
        if not isinstance(event, dict):
            continue
        start = max(0.0, min(song_duration, number(event.get("start"))))
        end = max(start, min(song_duration, number(event.get("end"))))
        position = musical_position(
            start,
            beat_seconds=beat_seconds,
            measure_seconds=measure_seconds,
            measures_per_row=measures_per_row,
        )
        note_events.append({
            **event,
            "start": round(start, 6),
            "end": round(end, 6),
            "measureNumber": position["measureNumber"],
            "rowNumber": position["rowNumber"],
            "measureInRow": position["measureInRow"],
            "beatNumber": position["beatNumber"],
            "beatFraction": position["beatFraction"],
            "rowRatio": position["rowRatio"],
            "measureRatio": position["measureRatio"],
            "measureGridReadOnly": True,
        })

'''
    new_note_block = '''    source_note_events = [
        event for event in (projection.get("noteEvents") or [])
        if isinstance(event, dict)
    ]
    note_events, note_filter_counts = filter_note_events(
        source_note_events,
        song_duration=song_duration,
        beat_seconds=beat_seconds,
        measure_seconds=measure_seconds,
        measures_per_row=measures_per_row,
    )

'''
    replace_once(GRID, old_note_block, new_note_block, "filtered note projection")

    replace_once(
        GRID,
        '''            "notes": len(note_events),
            "fragments": len(all_fragments),
''',
        '''            "notes": len(note_events),
            "noteFilter": note_filter_counts,
            "fragments": len(all_fragments),
''',
        "filter diagnostics",
    )

    replace_once(
        OVERLAY,
        '''    // Raw analyzer note events are intentionally not rendered directly.
    // They require musical filtering, deduplication, confidence gating,
    // rhythmic quantization, and density control before entering the PDF.
    const renderableNotes = [];
    for (const note of renderableNotes) {
      drawProjectedNote(page, note, layout, transcriptionType, boldFont);
    }
''',
        '''    // Only read-only notes that passed the V7 musical filter may render.
    const renderableNotes = notes.filter(
      (note) => note?.musicallyFiltered === true && note?.measureGridReadOnly === true
    );
    for (const note of renderableNotes) {
      drawProjectedNote(page, note, layout, transcriptionType, boldFont);
    }
''',
        "filtered-note renderer",
    )

    print("\nV7 MUSICAL NOTE FILTER INSTALLED 💚")
    print("Raw analyzer events remain protected and read-only.")
    print("The PDF now receives quantized, deduplicated, density-controlled projected notes only.")


if __name__ == "__main__":
    main()
