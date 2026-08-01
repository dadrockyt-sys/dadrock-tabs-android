from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
CALIBRATION_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-pitch-availability.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def accepted_pitches(event: dict[str, Any]) -> set[int]:
    pitches = {int(event["midiPitch"])}
    sounding = event.get("soundingMidiPitch")
    if isinstance(sounding, (int, float)):
        pitches.add(int(round(sounding)))
    return pitches


def event_start(event: dict[str, Any]) -> float | None:
    for key in ("start", "start_time", "startTime", "time"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def event_pitch(event: dict[str, Any]) -> int | None:
    for key in ("midiPitch", "pitch_midi", "pitchMidi", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    cache = load_json(EVENTS_PATH)
    calibration = load_json(CALIBRATION_PATH)

    raw_events = cache.get("events", [])
    extracted: list[dict[str, Any]] = []
    for raw in raw_events:
        start = event_start(raw)
        pitch = event_pitch(raw)
        if start is None or pitch is None:
            continue
        extracted.append({"start": start, "midiPitch": pitch})
    extracted.sort(key=lambda item: item["start"])

    best = calibration.get("best") or {}
    tempo = float(best.get("tempoBpm") or 129.0)
    offset = float(best.get("firstMeasureOffsetSeconds") or 0.0)
    measure_seconds = 4.0 * 60.0 / tempo

    measure_reports: list[dict[str, Any]] = []
    total_targets = 0
    pitch_available = 0

    for measure in reference.get("measures", []):
        number = int(measure.get("measureNumber", 0))
        if not 1 <= number <= 16:
            continue

        start = offset + (number - 1) * measure_seconds
        end = start + measure_seconds
        observed = [
            event for event in extracted if start - 0.15 <= event["start"] <= end + 0.15
        ]
        observed_counts = Counter(event["midiPitch"] for event in observed)
        remaining = Counter(observed_counts)

        matched = 0
        misses: list[dict[str, Any]] = []
        for index, target in enumerate(measure.get("events", [])):
            total_targets += 1
            accepted = accepted_pitches(target)
            chosen: int | None = None
            for pitch in sorted(accepted):
                if remaining[pitch] > 0:
                    chosen = pitch
                    break
            if chosen is not None:
                remaining[chosen] -= 1
                matched += 1
                pitch_available += 1
            else:
                misses.append(
                    {
                        "eventIndex": index,
                        "step": target.get("step"),
                        "acceptedPitches": sorted(accepted),
                        "stringIndex": target.get("stringIndex"),
                        "fret": target.get("fret"),
                        "technique": target.get("technique"),
                    }
                )

        target_count = len(measure.get("events", []))
        score = matched / target_count if target_count else 0.0
        measure_reports.append(
            {
                "measureNumber": number,
                "patternId": measure.get("patternId"),
                "windowStartSeconds": round(start, 4),
                "windowEndSeconds": round(end, 4),
                "professionalTargets": target_count,
                "observedEvents": len(observed),
                "pitchAvailableMatches": matched,
                "pitchAvailabilityScore": score,
                "observedPitchCounts": dict(sorted(observed_counts.items())),
                "misses": misses,
            }
        )

    overall = pitch_available / total_targets if total_targets else 0.0
    if overall >= 0.75:
        classification = "timing-grid-or-step-position-problem"
        next_action = "rebuild-professional-step-timing-from-rhythm-notation"
    elif overall >= 0.45:
        classification = "mixed-timing-and-pitch-extraction-problem"
        next_action = "inspect-professional-pitch-encoding-and-basic-pitch-candidates"
    else:
        classification = "reference-pitch-encoding-or-source-part-mismatch"
        next_action = "verify-string-fret-to-midi-map-and-rhythm-guitar-source"

    report = {
        "schemaVersion": 1,
        "benchmark": "professional-measures-1-16-pitch-availability",
        "tempoBpm": tempo,
        "firstMeasureOffsetSeconds": offset,
        "professionalTargets": total_targets,
        "pitchAvailableMatches": pitch_available,
        "pitchAvailabilityScore": overall,
        "classification": classification,
        "recommendedNextAction": next_action,
        "measureReports": measure_reports,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "notes": (
            "This diagnostic ignores exact within-measure timing and asks whether the expected "
            "professional pitches exist anywhere inside each calibrated measure window."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge professional pitch-availability diagnosis")
    print(f"Professional targets: {total_targets}")
    print(f"Pitch-available matches: {pitch_available}")
    print(f"Pitch availability score: {overall * 100:.2f}%")
    print(f"Classification: {classification}")
    print(f"Recommended next action: {next_action}")
    for item in measure_reports:
        print(
            f"- measure {item['measureNumber']}: "
            f"{item['pitchAvailableMatches']}/{item['professionalTargets']} "
            f"({item['pitchAvailabilityScore'] * 100:.1f}%)"
        )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
