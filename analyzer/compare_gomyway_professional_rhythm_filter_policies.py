from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
WINNER_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-test.json"
CALIBRATION_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-filter-policy-comparison.json"


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def find_timed_events(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            sample = value[:30]
            has_pitch = any(
                any(key in item for key in ("midiPitch", "pitch_midi", "pitchMidi", "pitch", "midi"))
                for item in sample
            )
            has_time = any(
                any(key in item for key in ("start", "start_time", "startTime", "time"))
                for item in sample
            )
            if has_pitch and has_time:
                return value
        for item in value:
            found = find_timed_events(item)
            if found:
                return found
    elif isinstance(value, dict):
        for key in ("events", "noteEvents", "notes", "result", "output", "prediction"):
            if key in value:
                found = find_timed_events(value[key])
                if found:
                    return found
        for item in value.values():
            found = find_timed_events(item)
            if found:
                return found
    return []


def event_start(event: dict[str, Any]) -> float | None:
    for key in ("start", "start_time", "startTime", "time"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def event_pitch(event: dict[str, Any]) -> int | None:
    for key in ("midiPitch", "pitch_midi", "pitchMidi", "pitch", "midi"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def accepted_pitches(event: dict[str, Any]) -> set[int]:
    result = {int(round(event["midiPitch"]))}
    sounding = event.get("soundingMidiPitch")
    if isinstance(sounding, (int, float)):
        result.add(int(round(sounding)))
    return result


def build_targets(reference: dict[str, Any]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for measure in reference.get("measures", []):
        measure_number = int(measure.get("measureNumber", 0))
        if not 1 <= measure_number <= 16:
            continue
        for event_index, event in enumerate(measure.get("events", [])):
            if not isinstance(event, dict) or "midiPitch" not in event:
                continue
            targets.append(
                {
                    "measureNumber": measure_number,
                    "eventIndex": event_index,
                    "acceptedPitches": sorted(accepted_pitches(event)),
                    "event": event,
                }
            )
    return targets


def normalize_events(raw_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for raw in raw_events:
        start = event_start(raw)
        pitch = event_pitch(raw)
        if start is None or pitch is None:
            continue
        events.append({"start": start, "midiPitch": pitch, "raw": raw})
    return sorted(events, key=lambda event: event["start"])


def timing_parameters() -> tuple[float, float, str]:
    calibration = load_json(CALIBRATION_PATH)
    best = calibration.get("best") if isinstance(calibration.get("best"), dict) else {}
    tempo = best.get("tempoBpm")
    offset = best.get("firstMeasureOffsetSeconds")
    if isinstance(tempo, (int, float)) and isinstance(offset, (int, float)):
        return float(tempo), float(offset), str(CALIBRATION_PATH.relative_to(REPO_ROOT))
    return 129.0, 5.045, "fallback-documented-tempo-and-observed-offset"


def score_measure_availability(
    targets: list[dict[str, Any]],
    events: list[dict[str, Any]],
    tempo: float,
    offset: float,
) -> dict[str, Any]:
    measure_seconds = 4.0 * 60.0 / tempo
    matched_total = 0
    measure_reports: list[dict[str, Any]] = []

    for measure_number in range(1, 17):
        measure_targets = [
            target for target in targets if target["measureNumber"] == measure_number
        ]
        start = offset + (measure_number - 1) * measure_seconds
        end = start + measure_seconds
        measure_events = [event for event in events if start <= event["start"] < end]
        unused = set(range(len(measure_events)))
        matched = 0
        missing: list[dict[str, Any]] = []

        # This intentionally ignores exact within-measure timing. It tests whether
        # the required professional pitch inventory is available at all.
        for target in measure_targets:
            accepted = set(target["acceptedPitches"])
            candidate_index = next(
                (
                    index
                    for index in sorted(unused)
                    if measure_events[index]["midiPitch"] in accepted
                ),
                None,
            )
            if candidate_index is None:
                missing.append(
                    {
                        "eventIndex": target["eventIndex"],
                        "acceptedPitches": target["acceptedPitches"],
                    }
                )
                continue
            unused.remove(candidate_index)
            matched += 1

        matched_total += matched
        total = len(measure_targets)
        measure_reports.append(
            {
                "measureNumber": measure_number,
                "matched": matched,
                "total": total,
                "score": matched / total if total else 0.0,
                "filteredEventCount": len(measure_events),
                "missing": missing,
            }
        )

    total_targets = len(targets)
    return {
        "matched": matched_total,
        "total": total_targets,
        "score": matched_total / total_targets if total_targets else 0.0,
        "measureReports": measure_reports,
    }


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    cache = load_json(EVENT_CACHE_PATH)
    winner = load_json(WINNER_PATH)
    raw_events = find_timed_events(cache) or find_timed_events(winner)
    events = normalize_events(raw_events)
    targets = build_targets(reference)

    if not events:
        raise RuntimeError("No timed Jimmy PAIge full-song events were found.")
    if not targets:
        raise RuntimeError("No professional measures 1-16 targets were found.")

    professional_pitch_set = {
        pitch for target in targets for pitch in target["acceptedPitches"]
    }
    policies: dict[str, Callable[[int], bool]] = {
        "v7-strict-rhythm-52-63": lambda pitch: 52 <= pitch <= 63,
        "expanded-guitar-40-76": lambda pitch: 40 <= pitch <= 76,
        "professional-pitch-set": lambda pitch: pitch in professional_pitch_set,
    }

    tempo, offset, timing_source = timing_parameters()
    policy_reports: list[dict[str, Any]] = []

    print("Jimmy PAIge professional rhythm filter-policy comparison")
    print(f"Timed full-song events: {len(events)}")
    print(f"Professional targets: {len(targets)}")
    print(f"Timing: {tempo:.3f} BPM | first measure offset={offset:.3f}s")
    print(f"Professional pitch set: {sorted(professional_pitch_set)}")

    for name, predicate in policies.items():
        filtered = [event for event in events if predicate(event["midiPitch"])]
        score = score_measure_availability(targets, filtered, tempo, offset)
        inventory = Counter(event["midiPitch"] for event in filtered)
        report = {
            "policy": name,
            "filteredEventCount": len(filtered),
            "midiInventory": sorted(inventory.items()),
            **score,
        }
        policy_reports.append(report)
        print(
            f"{name}: {score['matched']}/{score['total']} "
            f"({score['score'] * 100:.2f}%) | events={len(filtered)}"
        )

    policy_reports.sort(
        key=lambda report: (report["score"], -report["filteredEventCount"]),
        reverse=True,
    )
    winner_report = policy_reports[0]
    runner_up = policy_reports[1]
    improvement_over_unfiltered = winner_report["score"] - (43 / 144)

    ready_for_timing_calibration = winner_report["score"] >= 0.60
    ready_for_guarded_training = winner_report["score"] >= 0.90

    output = {
        "schemaVersion": 1,
        "benchmark": "professional-rhythm-filter-policy-comparison",
        "sourceEvents": str(
            (EVENT_CACHE_PATH if EVENT_CACHE_PATH.exists() else WINNER_PATH).relative_to(REPO_ROOT)
        ),
        "professionalReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "timingSource": timing_source,
        "tempoBpm": tempo,
        "firstMeasureOffsetSeconds": offset,
        "professionalTargetCount": len(targets),
        "unfilteredPitchAvailabilityBaseline": {
            "matched": 43,
            "total": 144,
            "score": 43 / 144,
        },
        "professionalPitchSet": sorted(professional_pitch_set),
        "policies": policy_reports,
        "winner": winner_report["policy"],
        "winnerScore": winner_report["score"],
        "runnerUp": runner_up["policy"],
        "improvementOverUnfilteredBaseline": improvement_over_unfiltered,
        "readyForFilteredTimingCalibration": ready_for_timing_calibration,
        "readyForGuardedAutomatedTraining": ready_for_guarded_training,
        "productionPromotionAllowed": False,
        "protectedBaselinesChanged": False,
        "notes": (
            "This is a measure-wide pitch-availability comparison. It does not "
            "claim exact timing, string/fret, chord, or technique accuracy. The "
            "winning policy must pass exact timing calibration before training."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print(f"Winning policy: {winner_report['policy']}")
    print(f"Winning score: {winner_report['score'] * 100:.2f}%")
    print(
        "Improvement over unfiltered baseline: "
        f"{improvement_over_unfiltered * 100:+.2f} percentage points"
    )
    print(f"Ready for filtered timing calibration: {ready_for_timing_calibration}")
    print(f"Ready for guarded automated training: {ready_for_guarded_training}")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
