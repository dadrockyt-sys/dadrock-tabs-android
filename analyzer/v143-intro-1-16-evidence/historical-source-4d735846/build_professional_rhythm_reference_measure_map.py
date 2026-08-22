from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference.json"

SECTIONS = [
    (1, 16, "Intro"),
    (17, 32, "Verse 1"),
    (33, 38, "Chorus 1"),
    (39, 46, "Riff"),
    (47, 62, "Verse 2"),
    (63, 69, "Chorus 2"),
    (70, 77, "Bridge"),
    (78, 94, "Solo rhythm backing / transition"),
    (95, 102, "Riff"),
    (103, 113, "Out-Chorus / ending"),
]

CHORDS = {
    33: ["G6"], 34: ["A(tp2)"], 35: ["E", "D", "E"], 36: ["G", "E"],
    37: ["G6"], 38: ["A(tp2)"],
    63: ["G6"], 64: ["A(tp2)"], 65: ["E", "D", "E"], 66: ["G", "E"],
    67: ["G6"],
    70: ["E", "D"], 71: ["A", "E"], 72: ["E", "D"], 73: ["A", "E"],
    74: ["E", "D"], 75: ["A", "E"], 76: ["E", "D"], 77: ["A", "E"],
    78: ["E", "D"], 79: ["A", "D6", "A"], 80: ["E", "D"], 81: ["A", "D6", "A"],
    82: ["E", "D"], 83: ["A", "D6", "A"], 84: ["E", "D"], 85: ["A", "D6", "A"],
    86: ["E", "D"], 87: ["A", "D6", "A"], 88: ["E", "D"], 89: ["A", "D6", "A"],
    90: ["E", "D"], 91: ["A", "D6", "A"], 92: ["E", "D"], 93: ["D"],
    103: ["G6"], 104: ["A(tp2)"], 105: ["G6"], 106: ["A(tp2)"],
    107: ["E", "D", "E"], 108: ["G", "E"], 109: ["G(tp2)", "A(tp2)"],
    110: ["A(tp2)"], 111: ["A(tp2)"], 112: ["A(tp2)"], 113: ["A(tp2)"],
}


def section_for(measure: int) -> str:
    for start, end, label in SECTIONS:
        if start <= measure <= end:
            return label
    raise ValueError(f"No section for measure {measure}")


def pattern_for(measure: int) -> str:
    em_ranges = ((1, 24), (29, 32), (39, 54), (59, 62), (95, 102))
    if any(start <= measure <= end for start, end in em_ranges):
        return "em-riff-a" if measure % 2 else "em-riff-b"
    if measure in (25, 27, 55, 57): return "g-position-riff-a"
    if measure in (26, 56): return "g-position-riff-b"
    if measure in (28, 58): return "picked-muted-turnaround"
    if measure in (33, 37, 63, 67, 103, 105): return "chorus-g6"
    if measure in (34, 38, 64, 104, 106): return "chorus-atp2"
    if measure in (35, 65, 107): return "chorus-e-d-e"
    if measure in (36, 66, 108): return "chorus-g-e"
    if measure in (68, 69): return "full-measure-rest"
    if 70 <= measure <= 77: return "bridge-e-d" if measure % 2 == 0 else "bridge-a-e"
    if 78 <= measure <= 91:
        return "solo-backing-e-d" if measure % 2 == 0 else "solo-backing-a-d6-a"
    if measure == 92: return "solo-transition-e-d"
    if measure == 93: return "solo-transition-held-d"
    if measure == 94: return "solo-transition-pickup-4-5-6"
    if measure == 109: return "outro-g-atp2"
    if 110 <= measure <= 112: return "outro-held-atp2"
    if measure == 113: return "outro-final-held-atp2-dead-note-rest"
    return "unclassified"


def chord_symbols_for(measure: int) -> list[str]:
    if measure in CHORDS:
        return CHORDS[measure]
    if 1 <= measure <= 32 or 39 <= measure <= 62 or 95 <= measure <= 102:
        return ["G"] if measure in (25, 26, 27, 28, 55, 56, 57, 58) else ["Em"]
    return []


def source_pages_for(measure: int) -> list[int]:
    pages: list[int] = []
    ranges = {
        1: (1, 14), 2: (13, 27), 3: (27, 43), 4: (43, 57), 5: (57, 75),
        6: (74, 90), 7: (90, 108), 8: (97, 113), 9: (97, 113),
    }
    for page, (start, end) in ranges.items():
        if start <= measure <= end:
            pages.append(page)
    return pages


def main() -> None:
    reference = json.loads(REFERENCE_PATH.read_text())
    reference["measures"] = [
        {
            "measureNumber": measure,
            "timeSignature": "2/4" if measure == 104 else "4/4",
            "sectionLabel": section_for(measure),
            "chordSymbols": [
                {"symbol": symbol, "verifiedFromSource": True}
                for symbol in chord_symbols_for(measure)
            ],
            "patternId": pattern_for(measure),
            "events": [],
            "eventTranscriptionStatus": "pending-manual-event-entry",
            "sourcePages": source_pages_for(measure),
            "measureIdentityVerified": True,
            "confidence": 1.0,
        }
        for measure in range(1, 114)
    ]
    reference["measureCount"] = len(reference["measures"])
    reference["status"] = "measure-map-complete-event-transcription-pending"
    reference["readyForScoring"] = False
    REFERENCE_PATH.write_text(json.dumps(reference, indent=2) + "\n")

    print("Professional rhythm measure map built:", len(reference["measures"]))
    print("First measure:", reference["measures"][0]["measureNumber"])
    print("Last measure:", reference["measures"][-1]["measureNumber"])
    print("Ready for scoring:", reference["readyForScoring"])
    print("Output:", REFERENCE_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
