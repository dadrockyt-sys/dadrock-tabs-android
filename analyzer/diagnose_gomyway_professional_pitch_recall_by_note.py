from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-timing-map-v2.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-pitch-recall-by-note.json"

MEASURE_PADDING_SECONDS = 0.12


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midiPitch", "midi", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def event_start(event: dict[str, Any]) -> float | None:
    for key in ("startTime", "start_time", "start", "time"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def normalize_event_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("events", "noteEvents", "extractedEvents", "result"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    timing = load_json(TIMING_PATH)
    extracted_payload = load_json(EVENT_CACHE_PATH)
    extracted_events = normalize_event_list(extracted_payload)

    timed_events = [
        event
        for event in extracted_events
        if event_midi(event) is not None and event_start(event) is not None
    ]
    if not timed_events:
        raise RuntimeError("No timed extracted events were found in the full-song event cache.")

    boundaries = {
        int(item["measureNumber"]): item
        for item in timing.get("measureBoundaries", [])
        if isinstance(item, dict) and "measureNumber" in item
    }

    per_pitch: dict[int, dict[str, Any]] = defaultdict(
        lambda: {
            "expected": 0,
            "matched": 0,
            "measureHits": [],
            "measureMisses": [],
            "nearbyObservedPitches": Counter(),
        }
    )
    per_measure: list[dict[str, Any]] = []

    total_expected = 0
    total_matched = 0

    for measure in reference.get("measures", []):
        if not isinstance(measure, dict):
            continue
        measure_number = int(measure.get("measureNumber", 0))
        if not 1 <= measure_number <= 16:
            continue
        boundary = boundaries.get(measure_number)
        if not boundary:
            continue

        start = float(boundary["startSeconds"]) - MEASURE_PADDING_SECONDS
        end = float(boundary["endSeconds"]) + MEASURE_PADDING_SECONDS
        observed = [
            event
            for event in timed_events
            if start <= float(event_start(event)) <= end
        ]
        observed_midis = Counter(
            midi
            for event in observed
            if (midi := event_midi(event)) is not None
        )

        measure_expected = 0
        measure_matched = 0
        pitch_rows: list[dict[str, Any]] = []

        for professional_event in measure.get("events", []):
            if not isinstance(professional_event, dict):
                continue
            written = event_midi(professional_event)
            if written is None:
                continue
            accepted = {written}
            sounding = professional_event.get("soundingMidiPitch")
            if isinstance(sounding, (int, float)):
                accepted.add(int(round(sounding)))

            measure_expected += 1
            total_expected += 1
            matched_pitch = next((pitch for pitch in accepted if observed_midis[pitch] > 0), None)
            matched = matched_pitch is not None
            if matched:
                measure_matched += 1
                total_matched += 1

            stat = per_pitch[written]
            stat["expected"] += 1
            if matched:
                stat["matched"] += 1
                stat["measureHits"].append(measure_number)
            else:
                stat["measureMisses"].append(measure_number)
                for nearby_pitch, count in observed_midis.items():
                    if abs(nearby_pitch - written) <= 3:
                        stat["nearbyObservedPitches"][nearby_pitch] += count

            pitch_rows.append(
                {
                    "writtenMidi": written,
                    "acceptedMidis": sorted(accepted),
                    "matched": matched,
                    "matchedMidi": matched_pitch,
                    "stringIndex": professional_event.get("stringIndex"),
                    "fret": professional_event.get("fret"),
                    "technique": professional_event.get("technique"),
                }
            )

        per_measure.append(
            {
                "measureNumber": measure_number,
                "expected": measure_expected,
                "matched": measure_matched,
                "scorePercent": round(100.0 * measure_matched / measure_expected, 2) if measure_expected else 0.0,
                "observedPitchInventory": sorted(observed_midis.items()),
                "professionalEvents": pitch_rows,
            }
        )

    pitch_summary: list[dict[str, Any]] = []
    for midi, raw in sorted(per_pitch.items()):
        expected = int(raw["expected"])
        matched = int(raw["matched"])
        pitch_summary.append(
            {
                "midiPitch": midi,
                "expected": expected,
                "matched": matched,
                "recallPercent": round(100.0 * matched / expected, 2) if expected else 0.0,
                "measureHits": sorted(set(raw["measureHits"])),
                "measureMisses": sorted(set(raw["measureMisses"])),
                "nearbyObservedPitches": sorted(raw["nearbyObservedPitches"].items()),
            }
        )

    weakest = sorted(pitch_summary, key=lambda item: (item["recallPercent"], -item["expected"]))
    report = {
        "diagnostic": "professional-pitch-recall-by-note",
        "measureRange": [1, 16],
        "measurePaddingSeconds": MEASURE_PADDING_SECONDS,
        "professionalTargets": total_expected,
        "matchedTargets": total_matched,
        "overallRecallPercent": round(100.0 * total_matched / total_expected, 2) if total_expected else 0.0,
        "pitchSummary": pitch_summary,
        "weakestPitches": weakest,
        "measures": per_measure,
        "readyForAutomatedTraining": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print("Jimmy PAIge professional pitch recall by note")
    print(f"Professional targets: {total_expected}")
    print(f"Matched targets: {total_matched}")
    print(f"Overall recall: {report['overallRecallPercent']:.2f}%")
    print("\nPer-pitch recall")
    for item in pitch_summary:
        nearby = item["nearbyObservedPitches"][:6]
        print(
            f"- MIDI {item['midiPitch']}: {item['matched']}/{item['expected']} "
            f"({item['recallPercent']:.1f}%) | misses={item['measureMisses']} | nearby={nearby}"
        )
    print(f"\nOutput: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print("Ready for automated training: False")


if __name__ == "__main__":
    main()
