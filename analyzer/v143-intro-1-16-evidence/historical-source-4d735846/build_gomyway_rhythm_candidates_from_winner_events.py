from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
REFERENCE = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
AUDIT = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-audit.json"

TEMPO_BPM = 129.0
MEASURE_SECONDS = (60.0 / TEMPO_BPM) * 4.0
SIXTEENTH_SECONDS = MEASURE_SECONDS / 16.0
AUDIO_ORIGIN_SECONDS = 0.0
STANDARD_TUNING = [
    (6, 40),
    (5, 45),
    (4, 50),
    (3, 55),
    (2, 59),
    (1, 64),
]
MAX_FRET = 24


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def choose_string_and_fret(midi_pitch: int) -> tuple[int, int] | None:
    choices: list[tuple[int, int, int]] = []
    for string_number, open_pitch in STANDARD_TUNING:
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_FRET:
            # Prefer low fret, then lower-pitched/heavier string for rhythm guitar.
            choices.append((fret, -string_number, string_number))
    if not choices:
        return None
    fret, _, string_number = min(choices)
    return string_number, fret


def main() -> None:
    source = load(SOURCE)
    reference = load(REFERENCE)
    raw_events = source.get("events", [])
    if not isinstance(raw_events, list) or not raw_events:
        raise RuntimeError("Winner event source has no events")

    measure_meta: dict[int, dict[str, Any]] = {}
    for measure in reference.get("measures", []):
        number = int(measure["measureNumber"])
        if 17 <= number <= 113:
            measure_meta[number] = {
                "section": str(measure.get("section", "Unknown")),
                "timeSignature": str(measure.get("timeSignature", "4/4")),
                "tempoBpm": float(measure.get("tempoBpm", TEMPO_BPM) or TEMPO_BPM),
            }

    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    discarded_before = discarded_after = discarded_unplayable = 0

    for event in sorted(raw_events, key=lambda item: (float(item["start"]), float(item["end"]))):
        start = float(event["start"])
        end = max(start, float(event["end"]))
        relative = start - AUDIO_ORIGIN_SECONDS
        measure_number = int(relative // MEASURE_SECONDS) + 1
        if measure_number < 17:
            discarded_before += 1
            continue
        if measure_number > 113:
            discarded_after += 1
            continue

        measure_start = AUDIO_ORIGIN_SECONDS + (measure_number - 1) * MEASURE_SECONDS
        step = round((start - measure_start) / SIXTEENTH_SECONDS)
        if step >= 16:
            measure_number += 1
            step = 0
        if not 17 <= measure_number <= 113:
            discarded_after += 1
            continue

        midi_pitch = int(event["midiPitch"])
        position = choose_string_and_fret(midi_pitch)
        if position is None:
            discarded_unplayable += 1
            continue
        string_number, fret = position

        duration_steps = max(1, round((end - start) / SIXTEENTH_SECONDS))
        duration_steps = min(16, duration_steps)
        grouped[(measure_number, int(step))].append({
            "string": string_number,
            "fret": fret,
            "midi": midi_pitch,
            "confidence": float(event.get("confidence", 0.0)),
            "sourceStart": start,
            "sourceEnd": end,
            "durationSteps": duration_steps,
        })

    candidates: list[dict[str, Any]] = []
    for (measure_number, step), notes in sorted(grouped.items()):
        unique: dict[tuple[int, int, int], dict[str, Any]] = {}
        for note in notes:
            key = (note["string"], note["fret"], note["midi"])
            if key not in unique or note["confidence"] > unique[key]["confidence"]:
                unique[key] = note
        selected = sorted(unique.values(), key=lambda item: (-item["string"], item["fret"], item["midi"]))
        confidence = sum(item["confidence"] for item in selected) / len(selected)
        duration_steps = max(item["durationSteps"] for item in selected)
        meta = measure_meta.get(measure_number, {
            "section": "Unknown",
            "timeSignature": "4/4",
            "tempoBpm": TEMPO_BPM,
        })
        candidates.append({
            "measureNumber": measure_number,
            "quantizedStep": step,
            "durationSteps": duration_steps,
            "notes": [
                {"string": item["string"], "fret": item["fret"], "midi": item["midi"]}
                for item in selected
            ],
            "techniques": [],
            "confidence": confidence,
            "strength": confidence,
            "section": meta["section"],
            "timeSignature": meta["timeSignature"],
            "tempoBpm": meta["tempoBpm"],
            "source": "gomyway-jimmy-paige-full-song-winner-events",
            "sourceStarts": [item["sourceStart"] for item in selected],
        })

    measures_covered = sorted({int(item["measureNumber"]) for item in candidates})
    result = {
        "schemaVersion": 1,
        "candidateType": "rhythm-guitar-sixteenth-grid",
        "sourceEventPath": str(SOURCE.relative_to(ROOT)),
        "professionalReferenceUsedForLabelsOnly": True,
        "professionalReferenceCopiedIntoCandidate": False,
        "tempoBpm": TEMPO_BPM,
        "audioOriginSeconds": AUDIO_ORIGIN_SECONDS,
        "measureSeconds": MEASURE_SECONDS,
        "sixteenthSeconds": SIXTEENTH_SECONDS,
        "events": candidates,
        "candidates": candidates,
        "eventCount": len(candidates),
        "rawSourceEventCount": len(raw_events),
        "measuresCovered": measures_covered,
        "measureCoverageCount": len(measures_covered),
        "discardedBeforeMeasure17": discarded_before,
        "discardedAfterMeasure113": discarded_after,
        "discardedUnplayablePitch": discarded_unplayable,
        "lockedMeasures1To16Modified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "professionalReferenceModified": False,
        "candidateAudioModified": False,
        "readyForScoredTraining": bool(candidates),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    AUDIT.write_text(json.dumps({
        key: value for key, value in result.items() if key not in {"events", "candidates"}
    }, indent=2) + "\n", encoding="utf-8")

    print("Gomyway winner-event rhythm candidate adapter complete")
    print(f"Raw source events: {len(raw_events)}")
    print(f"Sixteenth-grid candidate events: {len(candidates)}")
    print(f"Measures covered: {len(measures_covered)}")
    print(f"First covered measure: {measures_covered[0] if measures_covered else None}")
    print(f"Last covered measure: {measures_covered[-1] if measures_covered else None}")
    print(f"Discarded before measure 17: {discarded_before}")
    print(f"Discarded after measure 113: {discarded_after}")
    print(f"Discarded unplayable pitch: {discarded_unplayable}")
    print("Audio origin seconds: 0.0")
    print(f"Output: {OUTPUT.relative_to(ROOT)}")
    print("Protected baselines changed: False")


if __name__ == "__main__":
    main()
