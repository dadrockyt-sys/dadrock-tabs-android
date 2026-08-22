from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
REFERENCE_17_113 = ROOT / "public" / "gomyway-professional-rhythm-reference-17-113.json"
INTRO_REFERENCE = ROOT / "analyzer" / "fixtures" / "gomyway_professional_intro_reference_v1.json"
OUTPUT = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2.json"
AUDIT = ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates-1-113-v2-audit.json"

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
INTRO_MEASURES = set(range(1, 17))
ALL_MEASURES = set(range(1, 114))


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def choose_string_and_fret(midi_pitch: int) -> tuple[int, int] | None:
    choices: list[tuple[int, int, int]] = []
    for string_number, open_pitch in STANDARD_TUNING:
        fret = midi_pitch - open_pitch
        if 0 <= fret <= MAX_FRET:
            choices.append((fret, -string_number, string_number))
    if not choices:
        return None
    fret, _, string_number = min(choices)
    return string_number, fret


def intro_reference_steps(reference: dict[str, Any]) -> dict[int, set[int]]:
    result: dict[int, set[int]] = defaultdict(set)
    for row in reference.get("notes", []):
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure", 0) or 0)
        step = int(row.get("step", -1) or -1)
        if 1 <= measure <= 16 and 0 <= step <= 15:
            result[measure].add(step)

    repeat = reference.get("repeat")
    if isinstance(repeat, dict):
        source_measures = [int(value) for value in repeat.get("sourceMeasures", [])]
        target_starts = [int(value) for value in repeat.get("targetMeasureStarts", [])]
        if source_measures == [1, 2]:
            first = set(result.get(1, set()))
            second = set(result.get(2, set()))
            for start in target_starts:
                if 1 <= start <= 15:
                    result[start] = set(first)
                    result[start + 1] = set(second)
    return result


def main() -> None:
    source = load(SOURCE)
    reference = load(REFERENCE_17_113)
    intro_reference = load(INTRO_REFERENCE)

    raw_events = source.get("events", [])
    if not isinstance(raw_events, list) or not raw_events:
        raise RuntimeError("Winner event source has no events")

    measure_meta: dict[int, dict[str, Any]] = {
        number: {
            "section": "Intro" if number <= 16 else "Unknown",
            "timeSignature": "4/4",
            "tempoBpm": TEMPO_BPM,
        }
        for number in range(1, 114)
    }
    for measure in reference.get("measures", []):
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber", 0) or 0)
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
        if measure_number < 1:
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
        if not 1 <= measure_number <= 113:
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
        meta = measure_meta[measure_number]
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
    missing_measures = sorted(ALL_MEASURES - set(measures_covered))

    intro_steps: dict[int, set[int]] = defaultdict(set)
    for item in candidates:
        measure = int(item["measureNumber"])
        if measure in INTRO_MEASURES:
            intro_steps[measure].add(int(item["quantizedStep"]))

    intro_reference_by_measure = intro_reference_steps(intro_reference)
    intro_step_agreement: dict[int, dict[str, Any]] = {}
    for measure in range(1, 17):
        detected = set(intro_steps.get(measure, set()))
        expected = set(intro_reference_by_measure.get(measure, set()))
        matched = detected & expected
        precision = len(matched) / len(detected) if detected else 0.0
        recall = len(matched) / len(expected) if expected else 0.0
        intro_step_agreement[measure] = {
            "detectedSteps": sorted(detected),
            "expectedSteps": sorted(expected),
            "matchedSteps": sorted(matched),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
        }

    intro_multi_step_measures = sorted(
        measure for measure in range(1, 17) if len(intro_steps.get(measure, set())) > 1
    )
    intro_average_recall = sum(
        item["recall"] for item in intro_step_agreement.values()
    ) / 16.0

    passed = bool(
        candidates
        and measures_covered
        and measures_covered[0] == 1
        and measures_covered[-1] == 113
        and len(intro_multi_step_measures) > 0
    )

    result = {
        "schemaVersion": 2,
        "candidateType": "rhythm-guitar-sixteenth-grid-full-song-1-113",
        "sourceEventPath": str(SOURCE.relative_to(ROOT)),
        "professionalReference17To113UsedForLabelsOnly": True,
        "introProfessionalReferenceUsedForValidationOnly": True,
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
        "missingMeasures": missing_measures,
        "introMeasuresWithMultipleAttackSteps": intro_multi_step_measures,
        "introMultipleAttackMeasureCount": len(intro_multi_step_measures),
        "introReferenceAgreement": intro_step_agreement,
        "introAverageReferenceRecall": round(intro_average_recall, 6),
        "discardedBeforeMeasure1": discarded_before,
        "discardedAfterMeasure113": discarded_after,
        "discardedUnplayablePitch": discarded_unplayable,
        "passed": passed,
        "readyForFullSongTraining": passed,
        "automaticPromotionAllowed": False,
        "candidateEventsModified": False,
        "professionalReferenceModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
    }

    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    AUDIT.write_text(json.dumps({
        key: value for key, value in result.items() if key not in {"events", "candidates"}
    }, indent=2) + "\n", encoding="utf-8")

    print("Gomyway full-song V8 rhythm candidates 1-113 V2 complete")
    print("Passed:", passed)
    print("Raw source events:", len(raw_events))
    print("Sixteenth-grid candidate events:", len(candidates))
    print("Measures covered:", len(measures_covered))
    print("First covered measure:", measures_covered[0] if measures_covered else None)
    print("Last covered measure:", measures_covered[-1] if measures_covered else None)
    print("Missing measures:", missing_measures)
    print("Intro measures with multiple attack steps:", intro_multi_step_measures)
    print("Intro average professional-step recall:", round(intro_average_recall, 6))
    print("Ready for full-song training:", passed)
    print()
    print("Candidate events modified: False")
    print("Professional reference modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Production promotion allowed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT.relative_to(ROOT))
    print("Audit:", AUDIT.relative_to(ROOT))

    if not passed:
        raise SystemExit("Full-song 1-113 candidate build did not pass its protected gate.")


if __name__ == "__main__":
    main()
