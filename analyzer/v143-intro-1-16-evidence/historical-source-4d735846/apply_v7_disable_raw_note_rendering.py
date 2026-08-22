#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "lib/v7MeasureGridOverlay.js"

RAW_LOOP = '''    for (const note of notes) {
      drawProjectedNote(page, note, layout, transcriptionType, boldFont);
    }

'''
GUARDED_LOOP = '''    // Raw analyzer note events are intentionally not rendered directly.
    // They require musical filtering, deduplication, confidence gating,
    // rhythmic quantization, and density control before entering the PDF.
    const renderableNotes = [];
    for (const note of renderableNotes) {
      drawProjectedNote(page, note, layout, transcriptionType, boldFont);
    }

'''


def main() -> None:
    text = OVERLAY.read_text(encoding="utf-8")

    if GUARDED_LOOP in text:
        print("SKIP lib/v7MeasureGridOverlay.js already guarded")
        return

    if RAW_LOOP not in text:
        raise RuntimeError(
            "Expected raw V7 note-rendering loop was not found. "
            "Confirm apply_v7_populate_measure_notes.py was run first."
        )

    OVERLAY.write_text(text.replace(RAW_LOOP, GUARDED_LOOP, 1), encoding="utf-8")
    print("V7 raw note rendering disabled successfully 💚")
    print("Projected note data remains available, but the polished PDF is clean again.")


if __name__ == "__main__":
    main()
