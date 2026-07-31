from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ANCHOR_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-pitch-aware-rhythm-anchor.json"
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-signature-evidence.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
INTRO_MEASURES = 16
TARGET_STEPS = (14, 30)
WINDOW_RADIUS = 3


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


def _notation_events(report: dict[str, Any]) -> tuple[str | None, list[dict[str, Any]]]:
    for key in (
        "fingeringNormalizedEvents",
        "pitchContourReconstructedEvents",
        "motifStabilizedEvents",
        "renderEvents",
        "rhythmEvents",
    ):
        events = report.get(key)
        if isinstance(events, list) and events:
            return key, [item for item in events if isinstance(item, dict)]
    return None, []


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


def _event_summary(event: dict[str, Any], pair_step: int) -> dict[str, Any]:
    return {
        "pairStep": pair_step,
        "measureNumber": _safe_int(event.get("measureNumber")),
        "positionInMeasure": round(_safe_float(event.get("positionInMeasure")), 6),
        "midi": _event_midi(event),
        "stringIndex": _safe_int(event.get("stringIndex"), -1),
        "fret": _safe_int(event.get("fret"), -1),
    }


def _evaluate_offset(offset: int, events: list[dict[str, Any]]) -> dict[str, Any]:
    rotated_targets = [((step + offset) % PAIR_STEPS) for step in TARGET_STEPS]
    intro_events = [
        event
        for event in events
        if 1 <= _safe_int(event.get("measureNumber")) <= INTRO_MEASURES
    ]

    aggregate_midi: dict[int, Counter[int]] = {
        target: Counter() for target in rotated_targets
    }
    aggregate_pair_steps: dict[int, Counter[int]] = {
        target: Counter() for target in rotated_targets
    }
    pair_results: list[dict[str, Any]] = []

    for pair_index in range(INTRO_MEASURES // 2):
        pair_events: list[tuple[int, dict[str, Any]]] = []
        for event in intro_events:
            measure = _safe_int(event.get("measureNumber"))
            if (measure - 1) // 2 != pair_index:
                continue
            pair_step = ((measure - 1) % 2) * STEPS_PER_MEASURE + _event_step(event)
            pair_events.append((pair_step, event))

        target_results: list[dict[str, Any]] = []
        for target in rotated_targets:
            nearby = [
                (pair_step, event)
                for pair_step, event in pair_events
                if _circular_distance(pair_step, target) <= WINDOW_RADIUS
            ]
            nearby.sort(key=lambda item: (_circular_distance(item[0], target), item[0], _event_midi(item[1])))

            for pair_step, event in nearby:
                midi = _event_midi(event)
                if midi > 0:
                    aggregate_midi[target][midi] += 1
                aggregate_pair_steps[target][pair_step] += 1

            target_results.append(
                {
                    "targetStep": target,
                    "events": [_event_summary(event, pair_step) for pair_step, event in nearby],
                }
            )

        pair_results.append({"pairIndex": pair_index, "targets": target_results})

    target_summaries = []
    for target in rotated_targets:
        target_summaries.append(
            {
                "targetStep": target,
                "midiHistogram": dict(sorted(aggregate_midi[target].items())),
                "pairStepHistogram": dict(sorted(aggregate_pair_steps[target].items())),
                "mostCommonMidi": aggregate_midi[target].most_common(12),
                "mostCommonPairSteps": aggregate_pair_steps[target].most_common(12),
            }
        )

    return {
        "offsetSteps": offset,
        "rotatedTargetSteps": rotated_targets,
        "windowRadiusSteps": WINDOW_RADIUS,
        "targetSummaries": target_summaries,
        "pairResults": pair_results,
        "readOnly": True,
    }


def main() -> None:
    for path in (ANCHOR_PATH, NOTATION_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark input: {path}")

    anchor_report = json.loads(ANCHOR_PATH.read_text())
    notation_report = json.loads(NOTATION_PATH.read_text())
    selected_layer, events = _notation_events(notation_report)

    offsets = [_safe_int(value) for value in anchor_report.get("equivalentBestOffsets") or []]
    if not offsets:
        raise ValueError("Pitch-aware anchor report has no equivalent offsets to inspect")

    evaluations = [_evaluate_offset(offset, events) for offset in offsets]
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-intro-signature-evidence",
        "selectedEventLayer": selected_layer,
        "candidateOffsets": offsets,
        "targetStepsBeforeRotation": list(TARGET_STEPS),
        "windowRadiusSteps": WINDOW_RADIUS,
        "evaluations": evaluations,
        "usesV7PitchEvidenceReadOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(events and evaluations),
        "trainingRule": (
            "Inspect the actual pitch and timing evidence near both possible measure endings. "
            "Do not synthesize notes, choose an orientation, alter V7 output, or change the renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Intro signature evidence pass:", report["passed"])
    print("Selected event layer:", selected_layer)
    print("V7 pitch evidence used read-only:", report["usesV7PitchEvidenceReadOnly"])
    print("Renderer changed:", report["rendererChanged"])
    print("Candidate offsets:", offsets)
    print("Inspection window radius:", WINDOW_RADIUS)

    for evaluation in evaluations:
        print()
        print("Offset:", evaluation["offsetSteps"])
        print("Rotated target steps:", evaluation["rotatedTargetSteps"])
        for summary in evaluation["targetSummaries"]:
            print(
                " Target",
                summary["targetStep"],
                "most common MIDI:",
                summary["mostCommonMidi"],
            )
            print(
                " Target",
                summary["targetStep"],
                "most common pair steps:",
                summary["mostCommonPairSteps"],
            )

    print()
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
