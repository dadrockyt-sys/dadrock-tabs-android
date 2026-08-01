from __future__ import annotations

import bisect
import json
from collections import Counter
from pathlib import Path
from typing import Any

import modal

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-timing-map-v2.json"
FULL_SONG_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-professional-score-measures-1-16.json"

DEFAULT_TOLERANCE_SECONDS = 0.22


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start") or event.get("start_time") or 0.0)


def event_pitch(event: dict[str, Any]) -> int:
    try:
        return int(event.get("midiPitch"))
    except (TypeError, ValueError):
        return -1


def expected_pitches(reference_event: dict[str, Any]) -> set[int]:
    pitches = {int(reference_event["midiPitch"])}
    sounding = reference_event.get("soundingMidiPitch")
    if sounding is not None:
        pitches.add(int(sounding))
    return pitches


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    timing = load_json(TIMING_PATH)
    full_song = load_json(FULL_SONG_PATH)

    measures = reference.get("measures") or []
    if not measures or reference.get("detailedMeasureRange") != [1, 16]:
        raise RuntimeError("Professional reference v2 is not ready for measures 1-16 scoring.")

    boundaries = {
        int(item["measureNumber"]): item
        for item in timing.get("measureBoundaries", [])
    }
    if any(number not in boundaries for number in range(1, 17)):
        raise RuntimeError("Timing map does not contain all measure boundaries 1-16.")

    call_id = full_song.get("callId") or full_song.get("sourceCallId")
    if not call_id:
        raise RuntimeError("Full-song winner report does not contain a Modal call ID.")

    result_bytes = modal.FunctionCall.from_id(str(call_id)).get(timeout=0)
    remote = json.loads(result_bytes.decode("utf-8"))
    extracted = sorted(
        [event for event in remote.get("events", []) if event_pitch(event) >= 0],
        key=event_start,
    )
    starts = [event_start(event) for event in extracted]

    tolerance = DEFAULT_TOLERANCE_SECONDS
    used_event_indices: set[int] = set()
    reports: list[dict[str, Any]] = []
    section_counts: Counter[str] = Counter()
    section_matches: Counter[str] = Counter()
    technique_counts: Counter[str] = Counter()
    technique_matches: Counter[str] = Counter()

    for measure in measures:
        measure_number = int(measure["measureNumber"])
        boundary = boundaries[measure_number]
        start_seconds = float(boundary["startSeconds"])
        duration_seconds = float(boundary["durationSeconds"])
        section = str(measure.get("section") or "Unknown")

        for reference_event in measure.get("events", []):
            position = float(reference_event["positionInMeasure"])
            target_time = start_seconds + position * duration_seconds
            accepted_pitches = expected_pitches(reference_event)
            technique = str(reference_event.get("technique") or "unknown")

            left = bisect.bisect_left(starts, target_time - tolerance)
            right = bisect.bisect_right(starts, target_time + tolerance)

            candidates: list[tuple[float, int, dict[str, Any]]] = []
            nearby_pitch_counts: Counter[int] = Counter()
            for index in range(left, right):
                extracted_event = extracted[index]
                pitch = event_pitch(extracted_event)
                nearby_pitch_counts[pitch] += 1
                if index in used_event_indices or pitch not in accepted_pitches:
                    continue
                candidates.append(
                    (abs(event_start(extracted_event) - target_time), index, extracted_event)
                )

            candidates.sort(key=lambda item: item[0])
            matched_event = None
            delta_seconds = None
            if candidates:
                delta_seconds, matched_index, matched_event = candidates[0]
                used_event_indices.add(matched_index)

            matched = matched_event is not None
            section_counts[section] += 1
            technique_counts[technique] += 1
            if matched:
                section_matches[section] += 1
                technique_matches[technique] += 1

            reports.append(
                {
                    "measureNumber": measure_number,
                    "section": section,
                    "patternId": measure.get("patternId"),
                    "step": int(reference_event["step"]),
                    "targetSeconds": round(target_time, 6),
                    "stringIndex": int(reference_event["stringIndex"]),
                    "fret": int(reference_event["fret"]),
                    "expectedMidiPitches": sorted(accepted_pitches),
                    "technique": technique,
                    "matched": matched,
                    "matchedMidiPitch": event_pitch(matched_event) if matched_event else None,
                    "matchedStartSeconds": (
                        round(event_start(matched_event), 6) if matched_event else None
                    ),
                    "absoluteDeltaSeconds": (
                        round(float(delta_seconds), 6) if delta_seconds is not None else None
                    ),
                    "nearbyPitchCounts": [
                        {"midiPitch": pitch, "count": count}
                        for pitch, count in nearby_pitch_counts.most_common(8)
                    ],
                }
            )

    total = len(reports)
    matched_total = sum(1 for report in reports if report["matched"])
    score = matched_total / total if total else 0.0

    section_scores = []
    for section, count in sorted(section_counts.items()):
        matches = section_matches[section]
        section_scores.append(
            {
                "section": section,
                "matched": matches,
                "total": count,
                "score": round(matches / count, 6) if count else 0.0,
            }
        )

    technique_scores = []
    for technique, count in sorted(technique_counts.items()):
        matches = technique_matches[technique]
        technique_scores.append(
            {
                "technique": technique,
                "matched": matches,
                "total": count,
                "pitchTimingCandidateScore": round(matches / count, 6) if count else 0.0,
                "note": "This confirms a pitch candidate near the professional event; it does not yet prove technique recognition.",
            }
        )

    output = {
        "schemaVersion": 1,
        "benchmarkType": "professional-rhythm-tab-partial-event-score",
        "measureRange": [1, 16],
        "professionalEventCount": total,
        "matchedProfessionalEvents": matched_total,
        "pitchTimingCandidateScore": round(score, 6),
        "pitchTimingCandidatePercentage": round(score * 100.0, 2),
        "targetPercentage": 90.0,
        "targetReached": score >= 0.90,
        "timingToleranceSeconds": tolerance,
        "sourceCallId": call_id,
        "extractedFullSongEventCount": len(extracted),
        "scoringRules": {
            "pitch": "Exact MIDI match; bent notes accept written and sounding pitch.",
            "timing": "Nearest unused extracted event within the configured tolerance.",
            "stringAndFret": "Preserved from professional reference but not independently scored yet.",
            "technique": "Grouped diagnostically; technique recognition is not yet scored.",
            "doubleStops": "Each professional note is scored independently using one-to-one extracted-event matching.",
        },
        "sectionScores": section_scores,
        "techniqueCandidateScores": technique_scores,
        "eventReports": reports,
        "readyForAutomatedTrainingOnMeasures1To16": True,
        "readyForFullSongAutomatedTraining": False,
        "productionPromotionAllowed": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")

    print("Jimmy PAIge professional measures 1-16 scoring complete")
    print(f"Professional events: {total}")
    print(f"Matched events: {matched_total}")
    print(f"Pitch + timing candidate score: {score * 100.0:.2f}%")
    print(f"90% partial target reached: {score >= 0.90}")
    for section_score in section_scores:
        print(
            f"- {section_score['section']}: "
            f"{section_score['matched']}/{section_score['total']} "
            f"({section_score['score'] * 100.0:.2f}%)"
        )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print("Ready for full-song >=90% automated training: False")


if __name__ == "__main__":
    main()
