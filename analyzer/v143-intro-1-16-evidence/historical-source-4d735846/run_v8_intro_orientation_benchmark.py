from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
ANCHOR_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-pitch-aware-rhythm-anchor.json"
NOTATION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-notation.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-orientation.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
INTRO_MEASURES = 16
STEP_TOLERANCE = 1

# Professional reference orientation signatures.
# Measure 1 ends with open low E; measure 2 ends with the G-string/B-string
# third-fret double-stop visible in the supplied professional score.
FIRST_MEASURE_END_STEP = 14
SECOND_MEASURE_END_STEP = 30
FIRST_MEASURE_END_MIDIS = {40}
SECOND_MEASURE_END_MIDIS = {58, 62}


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


def _step_distance(left: int, right: int) -> int:
    return abs(left - right)


def _observed_midis(
    pair_events: list[tuple[int, dict[str, Any]]],
    target_step: int,
) -> set[int]:
    return {
        _event_midi(event)
        for event_step, event in pair_events
        if _step_distance(event_step, target_step) <= STEP_TOLERANCE
        and _event_midi(event) > 0
    }


def _signature_score(observed: set[int], expected: set[int]) -> tuple[float, bool]:
    if not expected:
        return 0.0, False
    intersection = observed & expected
    recall = len(intersection) / len(expected)
    precision = len(intersection) / len(observed) if observed else 0.0
    exact = observed == expected
    score = 0.55 * recall + 0.30 * precision + 0.15 * (1.0 if exact else 0.0)
    return score, exact


def _evaluate_offset(offset: int, events: list[dict[str, Any]]) -> dict[str, Any]:
    # The two candidate offsets differ by exactly one measure. Convert that
    # rotation into the expected locations of the first- and second-measure
    # ending signatures.
    rotation = offset % PAIR_STEPS
    first_target = (FIRST_MEASURE_END_STEP + rotation) % PAIR_STEPS
    second_target = (SECOND_MEASURE_END_STEP + rotation) % PAIR_STEPS

    intro_events = [
        event for event in events
        if 1 <= _safe_int(event.get("measureNumber")) <= INTRO_MEASURES
    ]

    pair_results: list[dict[str, Any]] = []
    total_score = 0.0
    exact_first = 0
    exact_second = 0
    reversed_first = 0
    reversed_second = 0

    for pair_index in range(INTRO_MEASURES // 2):
        pair_events: list[tuple[int, dict[str, Any]]] = []
        for event in intro_events:
            measure = _safe_int(event.get("measureNumber"))
            if (measure - 1) // 2 != pair_index:
                continue
            pair_step = ((measure - 1) % 2) * STEPS_PER_MEASURE + _event_step(event)
            pair_events.append((pair_step, event))

        first_observed = _observed_midis(pair_events, first_target)
        second_observed = _observed_midis(pair_events, second_target)
        first_score, first_exact = _signature_score(first_observed, FIRST_MEASURE_END_MIDIS)
        second_score, second_exact = _signature_score(second_observed, SECOND_MEASURE_END_MIDIS)

        # Penalize the exact professional signatures appearing in reversed
        # order. This is the information the previous pitch-aware aggregate
        # benchmark intentionally discarded.
        first_reversed = SECOND_MEASURE_END_MIDIS.issubset(first_observed)
        second_reversed = FIRST_MEASURE_END_MIDIS.issubset(second_observed)
        reversal_penalty = 0.20 * int(first_reversed) + 0.10 * int(second_reversed)
        pair_score = max(0.0, 0.45 * first_score + 0.55 * second_score - reversal_penalty)
        total_score += pair_score

        exact_first += int(first_exact)
        exact_second += int(second_exact)
        reversed_first += int(first_reversed)
        reversed_second += int(second_reversed)
        pair_results.append(
            {
                "pairIndex": pair_index,
                "firstMeasureTargetStep": first_target,
                "secondMeasureTargetStep": second_target,
                "firstMeasureObservedMidi": sorted(first_observed),
                "secondMeasureObservedMidi": sorted(second_observed),
                "firstMeasureExact": first_exact,
                "secondMeasureExact": second_exact,
                "firstMeasureReversed": first_reversed,
                "secondMeasureReversed": second_reversed,
                "pairOrientationScore": round(pair_score, 6),
            }
        )

    pair_count = INTRO_MEASURES // 2
    normalized_score = total_score / pair_count if pair_count else 0.0
    return {
        "offsetSteps": offset,
        "firstMeasureTargetStep": first_target,
        "secondMeasureTargetStep": second_target,
        "orientationScore": round(normalized_score, 6),
        "exactFirstMeasureSignatureCount": exact_first,
        "exactSecondMeasureSignatureCount": exact_second,
        "reversedFirstMeasureSignatureCount": reversed_first,
        "reversedSecondMeasureSignatureCount": reversed_second,
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

    offsets = [
        _safe_int(value)
        for value in anchor_report.get("equivalentBestOffsets") or []
    ]
    if not offsets:
        raise ValueError("Pitch-aware anchor report has no equivalent offsets to disambiguate")

    evaluations = [_evaluate_offset(offset, events) for offset in offsets]
    ranked = sorted(
        evaluations,
        key=lambda item: (
            float(item["orientationScore"]),
            int(item["exactSecondMeasureSignatureCount"]),
            int(item["exactFirstMeasureSignatureCount"]),
            -int(item["reversedFirstMeasureSignatureCount"]),
            -int(item["reversedSecondMeasureSignatureCount"]),
        ),
        reverse=True,
    )
    best = ranked[0]
    equivalent = [
        item for item in ranked
        if abs(float(item["orientationScore"]) - float(best["orientationScore"])) <= 1e-9
        and int(item["exactSecondMeasureSignatureCount"]) == int(best["exactSecondMeasureSignatureCount"])
        and int(item["exactFirstMeasureSignatureCount"]) == int(best["exactFirstMeasureSignatureCount"])
        and int(item["reversedFirstMeasureSignatureCount"]) == int(best["reversedFirstMeasureSignatureCount"])
        and int(item["reversedSecondMeasureSignatureCount"]) == int(best["reversedSecondMeasureSignatureCount"])
    ]
    unique = len(equivalent) == 1

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-intro-measure-orientation",
        "anchorInput": ANCHOR_PATH.name,
        "notationInput": NOTATION_PATH.name,
        "selectedEventLayer": selected_layer,
        "candidateOffsets": offsets,
        "professionalFirstMeasureEndingMidi": sorted(FIRST_MEASURE_END_MIDIS),
        "professionalSecondMeasureEndingMidi": sorted(SECOND_MEASURE_END_MIDIS),
        "uniqueOrientationFound": unique,
        "equivalentBestOffsetCount": len(equivalent),
        "equivalentBestOffsets": [int(item["offsetSteps"]) for item in equivalent],
        "bestCandidate": best,
        "adoptedOrientation": best if unique else None,
        "rankedCandidates": ranked,
        "usesV7PitchEvidenceReadOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(events and evaluations),
        "trainingRule": (
            "Resolve a one-measure anchor ambiguity only when the professional "
            "measure-ending pitch signatures identify one orientation uniquely. "
            "Never synthesize notes or alter V7 output or the renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Intro orientation pass:", report["passed"])
    print("Selected event layer:", selected_layer)
    print("V7 pitch evidence used read-only:", report["usesV7PitchEvidenceReadOnly"])
    print("Renderer changed:", report["rendererChanged"])
    print("Candidate offsets:", offsets)
    print("Unique orientation found:", report["uniqueOrientationFound"])
    print("Equivalent best offset count:", report["equivalentBestOffsetCount"])
    print("Equivalent best offsets:", report["equivalentBestOffsets"])
    print("Best oriented offset:", best.get("offsetSteps"))
    print("Orientation score:", best.get("orientationScore"))
    print("Exact first-measure signatures:", best.get("exactFirstMeasureSignatureCount"))
    print("Exact second-measure signatures:", best.get("exactSecondMeasureSignatureCount"))
    print("Reversed first-measure signatures:", best.get("reversedFirstMeasureSignatureCount"))
    print("Reversed second-measure signatures:", best.get("reversedSecondMeasureSignatureCount"))
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
