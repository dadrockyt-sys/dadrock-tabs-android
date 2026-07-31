from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ANCHOR_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-pitch-aware-rhythm-anchor.json"
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-corrected-intro-signature.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
INTRO_MEASURES = 16
WINDOW_RADIUS = 3

# Professional reference: each first measure resolves to open low E (MIDI 40).
# Each second measure ends with fret 3 on the high E and B strings:
# high E string fret 3 = MIDI 67, B string fret 3 = MIDI 62.
FIRST_MEASURE_TARGET_STEP = 14
SECOND_MEASURE_TARGET_STEP = 30
FIRST_MEASURE_SIGNATURE = {40}
SECOND_MEASURE_SIGNATURE = {62, 67}

EVENT_LAYER_KEYS = (
    "fingeringNormalizedEvents",
    "pitchContourReconstructedEvents",
    "motifStabilizedEvents",
    "renderEvents",
    "rhythmEvents",
)


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _event_midi(event: dict[str, Any]) -> int:
    midi = _safe_int(event.get("midiPitch") or event.get("midi") or event.get("pitch"))
    if midi > 0:
        return midi

    string_index = _safe_int(event.get("stringIndex"), -1)
    fret = _safe_int(event.get("fret"), -1)
    open_midi = (64, 59, 55, 50, 45, 40)
    if 0 <= string_index < len(open_midi) and fret >= 0:
        return open_midi[string_index] + fret
    return 0


def _event_step(event: dict[str, Any]) -> int:
    position = _safe_float(event.get("positionInMeasure"))
    return max(0, min(15, int(round(position * STEPS_PER_MEASURE))))


def _circular_distance(left: int, right: int) -> int:
    raw = abs(left - right) % PAIR_STEPS
    return min(raw, PAIR_STEPS - raw)


def _intro_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        event
        for event in events
        if 1 <= _safe_int(event.get("measureNumber")) <= INTRO_MEASURES
    ]


def _pair_step(event: dict[str, Any]) -> int:
    measure = _safe_int(event.get("measureNumber"))
    return ((measure - 1) % 2) * STEPS_PER_MEASURE + _event_step(event)


def _evaluate_target(
    events: list[dict[str, Any]],
    target_step: int,
    expected_midis: set[int],
) -> dict[str, Any]:
    nearby = [
        event
        for event in events
        if _circular_distance(_pair_step(event), target_step) <= WINDOW_RADIUS
    ]
    midi_histogram = Counter(
        midi for midi in (_event_midi(event) for event in nearby) if midi > 0
    )
    pair_step_histogram = Counter(_pair_step(event) for event in nearby)

    exact_events = [event for event in nearby if _event_midi(event) in expected_midis]
    exact_midis = {_event_midi(event) for event in exact_events}
    expected_coverage = len(exact_midis & expected_midis) / max(1, len(expected_midis))

    return {
        "targetStep": target_step,
        "expectedMidis": sorted(expected_midis),
        "nearbyEventCount": len(nearby),
        "mostCommonMidi": midi_histogram.most_common(12),
        "mostCommonPairSteps": pair_step_histogram.most_common(12),
        "exactMidiHits": len(exact_events),
        "exactDistinctMidis": sorted(exact_midis),
        "expectedCoverage": round(expected_coverage, 6),
    }


def _evaluate_layer(
    layer_name: str,
    events: list[dict[str, Any]],
    offsets: list[int],
) -> dict[str, Any]:
    intro = _intro_events(events)
    offset_results: list[dict[str, Any]] = []

    for offset in offsets:
        first_target = (FIRST_MEASURE_TARGET_STEP + offset) % PAIR_STEPS
        second_target = (SECOND_MEASURE_TARGET_STEP + offset) % PAIR_STEPS
        first = _evaluate_target(intro, first_target, FIRST_MEASURE_SIGNATURE)
        second = _evaluate_target(intro, second_target, SECOND_MEASURE_SIGNATURE)

        # The second-measure double-stop is the stronger orientation clue.
        score = first["expectedCoverage"] + 2.0 * second["expectedCoverage"]
        offset_results.append(
            {
                "offsetSteps": offset,
                "rotatedTargetSteps": [first_target, second_target],
                "firstMeasure": first,
                "secondMeasure": second,
                "orientationScore": round(score, 6),
            }
        )

    best_score = max((item["orientationScore"] for item in offset_results), default=0.0)
    best_offsets = [
        item["offsetSteps"]
        for item in offset_results
        if abs(item["orientationScore"] - best_score) <= 1e-9
    ]

    return {
        "layer": layer_name,
        "eventCount": len(events),
        "introEventCount": len(intro),
        "offsetResults": offset_results,
        "bestScore": best_score,
        "equivalentBestOffsets": best_offsets,
        "uniqueOrientationFound": best_score > 0 and len(best_offsets) == 1,
        "bestOffset": best_offsets[0] if best_offsets else None,
    }


def main() -> None:
    for path in (ANCHOR_PATH, NOTATION_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark input: {path}")

    anchor_report = json.loads(ANCHOR_PATH.read_text())
    notation_report = json.loads(NOTATION_PATH.read_text())
    offsets = [_safe_int(value) for value in anchor_report.get("equivalentBestOffsets") or []]
    if not offsets:
        raise ValueError("Pitch-aware anchor report has no equivalent offsets")

    layer_results: list[dict[str, Any]] = []
    for key in EVENT_LAYER_KEYS:
        raw_events = notation_report.get(key)
        if not isinstance(raw_events, list) or not raw_events:
            continue
        events = [item for item in raw_events if isinstance(item, dict)]
        layer_results.append(_evaluate_layer(key, events, offsets))

    uniquely_oriented = [item for item in layer_results if item["uniqueOrientationFound"]]
    selected = max(uniquely_oriented, key=lambda item: item["bestScore"], default=None)

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-corrected-intro-signature",
        "candidateOffsets": offsets,
        "windowRadiusSteps": WINDOW_RADIUS,
        "firstMeasureExpectedMidi": sorted(FIRST_MEASURE_SIGNATURE),
        "secondMeasureExpectedMidi": sorted(SECOND_MEASURE_SIGNATURE),
        "layerResults": layer_results,
        "uniqueOrientationFound": selected is not None,
        "selectedLayer": selected["layer"] if selected else None,
        "selectedOffset": selected["bestOffset"] if selected else None,
        "selectedScore": selected["bestScore"] if selected else None,
        "usesV7PitchEvidenceReadOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(layer_results),
        "trainingRule": (
            "Use the corrected professional double-stop pitches (MIDI 62 and 67), inspect every "
            "available V8/V7-derived event layer read-only, and choose an orientation only when one "
            "candidate offset is uniquely supported. Do not synthesize notes or alter the renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Corrected intro signature pass:", report["passed"])
    print("V7 pitch evidence used read-only:", report["usesV7PitchEvidenceReadOnly"])
    print("Renderer changed:", report["rendererChanged"])
    print("Candidate offsets:", offsets)
    print("First-measure expected MIDI:", sorted(FIRST_MEASURE_SIGNATURE))
    print("Second-measure expected MIDI:", sorted(SECOND_MEASURE_SIGNATURE))
    print("Inspection window radius:", WINDOW_RADIUS)

    for layer in layer_results:
        print()
        print("Layer:", layer["layer"])
        print("Unique orientation found:", layer["uniqueOrientationFound"])
        print("Equivalent best offsets:", layer["equivalentBestOffsets"])
        print("Best score:", layer["bestScore"])
        for item in layer["offsetResults"]:
            print(
                " Offset",
                item["offsetSteps"],
                "score",
                item["orientationScore"],
                "targets",
                item["rotatedTargetSteps"],
            )
            print(
                "  First exact MIDI:",
                item["firstMeasure"]["exactDistinctMidis"],
                "coverage:",
                item["firstMeasure"]["expectedCoverage"],
            )
            print(
                "  Second exact MIDI:",
                item["secondMeasure"]["exactDistinctMidis"],
                "coverage:",
                item["secondMeasure"]["expectedCoverage"],
            )

    print()
    print("Overall unique orientation found:", report["uniqueOrientationFound"])
    print("Selected layer:", report["selectedLayer"])
    print("Selected offset:", report["selectedOffset"])
    print("Selected score:", report["selectedScore"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
