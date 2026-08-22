#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"SKIP {path.relative_to(ROOT)} already patched")
        return
    if old not in text:
        raise RuntimeError(f"Expected anchor not found in {path.relative_to(ROOT)}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"PATCH {path.relative_to(ROOT)}")


def main() -> None:
    timeline = ROOT / "analyzer/modal_analyzer_v7_full_song_timeline_benchmark.py"
    projection = ROOT / "analyzer/build_v7_notation_metadata_projection.py"
    grid = ROOT / "analyzer/build_v7_measure_grid_projection.py"
    overlay = ROOT / "lib/v7MeasureGridOverlay.js"

    replace_once(
        timeline,
        '''def event_end(event: dict[str, Any]) -> float:\n    start = event_start(event)\n    return max(start, float(event.get("end") or event.get("end_time") or start))\n\n\n''',
        '''def event_end(event: dict[str, Any]) -> float:\n    start = event_start(event)\n    return max(start, float(event.get("end") or event.get("end_time") or start))\n\n\ndef project_note_event(event: dict[str, Any], event_index: int) -> dict[str, Any]:\n    return {\n        "eventIndex": event_index,\n        "start": round(event_start(event), 6),\n        "end": round(event_end(event), 6),\n        "stringIndex": int(event.get("stringIndex") or event.get("string_index") or 0),\n        "fret": int(event.get("fret") or 0),\n        "midiPitch": int(event.get("midiPitch") or event.get("pitch") or 0),\n        "readOnly": True,\n    }\n\n\n''',
    )

    replace_once(
        timeline,
        '''        "leadPalmMutedEventCount": len(palm_indices),\n        "bassPoints": bass_points,\n''',
        '''        "leadPalmMutedEventCount": len(palm_indices),\n        "leadEvents": [\n            project_note_event(event, index)\n            for index, event in enumerate(lead_events)\n        ],\n        "bassPoints": bass_points,\n''',
    )

    replace_once(
        projection,
        '''        "rhythmPromotions": timeline.get("rhythmPromotions") or {},\n        "notationMetadata": {\n''',
        '''        "rhythmPromotions": timeline.get("rhythmPromotions") or {},\n        "noteEvents": [\n            dict(item)\n            for item in (timeline.get("leadEvents") or [])\n            if isinstance(item, dict)\n        ],\n        "notationMetadata": {\n''',
    )

    replace_once(
        projection,
        '''            "allMarkers": len(all_markers),\n        },\n''',
        '''            "allMarkers": len(all_markers),\n            "noteEvents": len(timeline.get("leadEvents") or []),\n        },\n''',
    )

    replace_once(
        grid,
        '''    rows: list[dict[str, Any]] = []\n    for row_zero in range(row_count):\n''',
        '''    note_events: list[dict[str, Any]] = []\n    for event in (projection.get("noteEvents") or []):\n        if not isinstance(event, dict):\n            continue\n        start = max(0.0, min(song_duration, number(event.get("start"))))\n        end = max(start, min(song_duration, number(event.get("end"))))\n        position = musical_position(\n            start,\n            beat_seconds=beat_seconds,\n            measure_seconds=measure_seconds,\n            measures_per_row=measures_per_row,\n        )\n        note_events.append({\n            **event,\n            "start": round(start, 6),\n            "end": round(end, 6),\n            "measureNumber": position["measureNumber"],\n            "rowNumber": position["rowNumber"],\n            "measureInRow": position["measureInRow"],\n            "beatNumber": position["beatNumber"],\n            "beatFraction": position["beatFraction"],\n            "rowRatio": position["rowRatio"],\n            "measureRatio": position["measureRatio"],\n            "measureGridReadOnly": True,\n        })\n\n    rows: list[dict[str, Any]] = []\n    for row_zero in range(row_count):\n''',
    )

    replace_once(
        grid,
        '''        rows.append({\n            "rowNumber": row_zero + 1,\n''',
        '''        row_notes = [\n            note for note in note_events\n            if int(note.get("rowNumber") or 0) == row_zero + 1\n        ]\n        rows.append({\n            "rowNumber": row_zero + 1,\n''',
    )

    replace_once(
        grid,
        '''            "markerTypes": sorted({str(fragment.get("markerType") or "") for fragment in row_fragments}),\n            "fragments": row_fragments,\n        })\n''',
        '''            "markerTypes": sorted({str(fragment.get("markerType") or "") for fragment in row_fragments}),\n            "fragments": row_fragments,\n            "noteCount": len(row_notes),\n            "notes": row_notes,\n        })\n''',
    )

    replace_once(
        grid,
        '''        "markers": markers,\n        "rows": rows,\n''',
        '''        "markers": markers,\n        "noteEvents": note_events,\n        "rows": rows,\n''',
    )

    replace_once(
        grid,
        '''            "markers": len(markers),\n            "fragments": len(all_fragments),\n''',
        '''            "markers": len(markers),\n            "notes": len(note_events),\n            "fragments": len(all_fragments),\n''',
    )

    replace_once(
        overlay,
        '''function drawFretNumber(page, value, x, y, boldFont) {\n''',
        '''function drawProjectedNote(page, note, layout, transcriptionType, boldFont) {\n  const stringSpacing = transcriptionType === 'bass' ? 9 : 7;\n  const stringCount = transcriptionType === 'bass' ? 4 : 6;\n  const stringIndex = clamp(\n    Math.round(finiteNumber(note?.stringIndex, 0)),\n    0,\n    stringCount - 1\n  );\n  const x = markerX(note?.rowRatio);\n  const y = layout.staffTop - stringIndex * stringSpacing - 2.8;\n  drawFretNumber(page, note?.fret, x, y, boldFont);\n}\n\nfunction drawFretNumber(page, value, x, y, boldFont) {\n''',
    )

    replace_once(
        overlay,
        '''    const fragments = Array.isArray(row?.fragments) ? row.fragments : [];\n    if (!layout || !fragments.length) continue;\n''',
        '''    const fragments = Array.isArray(row?.fragments) ? row.fragments : [];\n    const notes = Array.isArray(row?.notes) ? row.notes : [];\n    if (!layout || (!fragments.length && !notes.length)) continue;\n''',
    )

    replace_once(
        overlay,
        '''    const chordLanes = assignChordLanes(fragments);\n    rowsRendered += 1;\n\n    for (const fragment of fragments) {\n''',
        '''    const chordLanes = assignChordLanes(fragments);\n    rowsRendered += 1;\n\n    for (const note of notes) {\n      drawProjectedNote(page, note, layout, transcriptionType, boldFont);\n    }\n\n    for (const fragment of fragments) {\n''',
    )

    print("\nV7 production-note measure population patch applied successfully 💚")
    print("Protected analyzer events remain read-only; only the PDF overlay consumes projected copies.")


if __name__ == "__main__":
    main()
