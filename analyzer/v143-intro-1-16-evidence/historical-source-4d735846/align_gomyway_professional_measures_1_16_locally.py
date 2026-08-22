from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
EVENT_CACHE_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json"
GLOBAL_CALIBRATION_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-measures-1-16-local-alignment.json"

DEFAULT_TEMPO = 129.0
SEARCH_RADIUS_SECONDS = 0.90
SEARCH_STEP_SECONDS = 0.01
MATCH_WINDOW_SECONDS = 0.22


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def event_midi(event: dict[str, Any]) -> int | None:
    for key in ("midiPitch", "pitch_midi", "midi", "pitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return int(round(value))
    return None


def event_start(event: dict[str, Any]) -> float | None:
    for key in ("startTime", "start_time", "start", "onset"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def professional_midis(event: dict[str, Any]) -> list[int]:
    values: list[int] = []
    for key in ("midiPitch", "soundingMidiPitch"):
        value = event.get(key)
        if isinstance(value, (int, float)):
            midi = int(round(value))
            if midi not in values:
                values.append(midi)
    return values


def score_measure(
    professional_events: list[dict[str, Any]],
    extracted_events: list[dict[str, Any]],
    measure_start: float,
    measure_duration: float,
) -> dict[str, Any]:
    candidates: list[tuple[int, float]] = []
    lower = measure_start - MATCH_WINDOW_SECONDS
    upper = measure_start + measure_duration + MATCH_WINDOW_SECONDS
    for index, event in enumerate(extracted_events):
        midi = event_midi(event)
        start = event_start(event)
        if midi is None or start is None or start < lower or start > upper:
            continue
        candidates.append((index, start))

    used: set[int] = set()
    matches: list[dict[str, Any]] = []
    misses: list[dict[str, Any]] = []

    for target in professional_events:
        position = float(target.get("positionInMeasure") or 0.0)
        target_time = measure_start + position * measure_duration
        allowed_midis = professional_midis(target)
        best: tuple[float, int, float, int] | None = None

        for index, start in candidates:
            if index in used:
                continue
            midi = event_midi(extracted_events[index])
            if midi not in allowed_midis:
                continue
            delta = abs(start - target_time)
            if delta > MATCH_WINDOW_SECONDS:
                continue
            candidate = (delta, index, start, int(midi))
            if best is None or candidate < best:
                best = candidate

        if best is None:
            misses.append(
                {
                    "step": target.get("step"),
                    "allowedMidis": allowed_midis,
                    "targetTime": round(target_time, 6),
                }
            )
            continue

        delta, index, start, midi = best
        used.add(index)
        matches.append(
            {
                "step": target.get("step"),
                "midi": midi,
                "targetTime": round(target_time, 6),
                "observedTime": round(start, 6),
                "absoluteDelta": round(delta, 6),
            }
        )

    total = len(professional_events)
    matched = len(matches)
    return {
        "matched": matched,
        "total": total,
        "scorePercent": round(100.0 * matched / total, 2) if total else 0.0,
        "matches": matches,
        "misses": misses,
    }


def main() -> None:
    reference = load_json(REFERENCE_PATH)
    cache = load_json(EVENT_CACHE_PATH)
    calibration = load_json(GLOBAL_CALIBRATION_PATH)

    extracted_events = [
        event for event in (cache.get("events") or []) if isinstance(event, dict)
    ]
    if not extracted_events:
        raise RuntimeError("No extracted events found in the full-song event cache.")

    best_global = calibration.get("best") or {}
    global_tempo = float(best_global.get("tempo") or DEFAULT_TEMPO)
    global_offset = float(best_global.get("offsetSeconds") or 0.0)
    measure_duration = 240.0 / global_tempo

    detailed_measures = [
        measure
        for measure in (reference.get("measures") or [])
        if isinstance(measure, dict) and 1 <= int(measure.get("measureNumber") or 0) <= 16
    ]
    detailed_measures.sort(key=lambda item: int(item["measureNumber"]))

    local_results: list[dict[str, Any]] = []
    total_matched = 0
    total_targets = 0
    previous_start: float | None = None

    for measure in detailed_measures:
        number = int(measure["measureNumber"])
        expected_start = global_offset + (number - 1) * measure_duration
        if previous_start is not None:
            expected_start = max(expected_start, previous_start + measure_duration * 0.70)

        best_result: dict[str, Any] | None = None
        best_start = expected_start
        steps = int(round((2.0 * SEARCH_RADIUS_SECONDS) / SEARCH_STEP_SECONDS))
        for step_index in range(steps + 1):
            candidate_start = expected_start - SEARCH_RADIUS_SECONDS + step_index * SEARCH_STEP_SECONDS
            result = score_measure(
                [event for event in (measure.get("events") or []) if isinstance(event, dict)],
                extracted_events,
                candidate_start,
                measure_duration,
            )
            ranking = (
                int(result["matched"]),
                -abs(candidate_start - expected_start),
            )
            if best_result is None or ranking > (
                int(best_result["matched"]),
                -abs(best_start - expected_start),
            ):
                best_result = result
                best_start = candidate_start

        assert best_result is not None
        previous_start = best_start
        total_matched += int(best_result["matched"])
        total_targets += int(best_result["total"])
        local_results.append(
            {
                "measureNumber": number,
                "expectedStart": round(expected_start, 6),
                "bestStart": round(best_start, 6),
                "localShiftSeconds": round(best_start - expected_start, 6),
                **best_result,
            }
        )

    score = round(100.0 * total_matched / total_targets, 2) if total_targets else 0.0
    shifts = [abs(float(item["localShiftSeconds"])) for item in local_results]
    report = {
        "diagnosticVersion": 1,
        "diagnosticType": "locally-aligned-professional-measure-score",
        "globalTempoBpm": global_tempo,
        "globalFirstMeasureOffsetSeconds": global_offset,
        "measureDurationSeconds": round(measure_duration, 6),
        "searchRadiusSeconds": SEARCH_RADIUS_SECONDS,
        "matchWindowSeconds": MATCH_WINDOW_SECONDS,
        "professionalTargets": total_targets,
        "matchedTargets": total_matched,
        "locallyAlignedScorePercent": score,
        "maximumAbsoluteLocalShiftSeconds": round(max(shifts), 6) if shifts else 0.0,
        "averageAbsoluteLocalShiftSeconds": round(sum(shifts) / len(shifts), 6) if shifts else 0.0,
        "measures": local_results,
        "classification": (
            "global-timing-map-problem"
            if score >= 75.0
            else "mixed-reference-timing-and-extraction-problem"
            if score >= 55.0
            else "pitch-extraction-or-reference-detail-problem"
        ),
        "readyForAutomatedTraining": False,
        "protectedBaselinesChanged": False,
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Jimmy PAIge local professional-measure alignment")
    print(f"Professional targets: {total_targets}")
    print(f"Matched after local alignment: {total_matched}")
    print(f"Locally aligned score: {score:.2f}%")
    print(f"Maximum local shift: {report['maximumAbsoluteLocalShiftSeconds']:.3f}s")
    print(f"Classification: {report['classification']}")
    for item in local_results:
        print(
            f"- measure {item['measureNumber']}: "
            f"{item['matched']}/{item['total']} ({item['scorePercent']:.1f}%) "
            f"shift={item['localShiftSeconds']:+.3f}s"
        )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")
    print("Ready for automated training: False")


if __name__ == "__main__":
    main()
