from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

REFERENCE_PATH = Path("analyzer/fixtures/gomyway_professional_intro_reference_v1.json")
NOTATION_PATH = Path("public/gomyway-full-song-v8-notation.json")
REPORT_PATH = Path("public/gomyway-full-song-v8-professional-intro-score.json")

STEP_TOLERANCE = 1
PASSING_SCORE = 0.90


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _expand_reference(reference: dict[str, Any]) -> list[dict[str, Any]]:
    base = [dict(note) for note in reference.get("notes", [])]
    repeat = reference.get("repeat", {})
    source_start = min(repeat.get("sourceMeasures", [1]))
    expanded = list(base)

    source_notes = [
        note for note in base
        if _safe_int(note.get("measure")) in set(repeat.get("sourceMeasures", [1, 2]))
    ]

    for target_start in repeat.get("targetMeasureStarts", []):
        for note in source_notes:
            item = dict(note)
            item["measure"] = target_start + (_safe_int(note.get("measure")) - source_start)
            expanded.append(item)

    return sorted(
        expanded,
        key=lambda item: (
            _safe_int(item.get("measure")),
            _safe_int(item.get("step")),
            _safe_int(item.get("stringIndex")),
            _safe_int(item.get("fret")),
        ),
    )


def _event_key(item: dict[str, Any]) -> tuple[int, int, int]:
    return (
        _safe_int(item.get("measure", item.get("measureNumber"))),
        _safe_int(item.get("stringIndex")),
        _safe_int(item.get("fret")),
    )


def score_intro(
    reference_notes: list[dict[str, Any]],
    detected_events: list[dict[str, Any]],
) -> dict[str, Any]:
    detected_by_identity: dict[tuple[int, int, int], list[dict[str, Any]]] = defaultdict(list)
    for event in detected_events:
        measure = _safe_int(event.get("measureNumber"))
        if 1 <= measure <= 16:
            detected_by_identity[_event_key(event)].append(event)

    matched_detected_ids: set[int] = set()
    comparisons: list[dict[str, Any]] = []
    exact_identity_matches = 0
    timing_matches = 0
    technique_matches = 0
    technique_targets = 0

    for reference_index, reference in enumerate(reference_notes):
        key = _event_key(reference)
        candidates = detected_by_identity.get(key, [])
        target_step = _safe_int(reference.get("step"))
        available = [
            event for event in candidates
            if _safe_int(event.get("sourceEventIndex"), id(event)) not in matched_detected_ids
        ]
        best = min(
            available,
            key=lambda event: abs(_safe_int(event.get("quantizedStep")) - target_step),
            default=None,
        )

        identity_match = best is not None
        timing_delta = None
        timing_match = False
        technique_target = reference.get("technique")
        technique_match = False

        if identity_match:
            exact_identity_matches += 1
            detected_id = _safe_int(best.get("sourceEventIndex"), id(best))
            matched_detected_ids.add(detected_id)
            timing_delta = abs(_safe_int(best.get("quantizedStep")) - target_step)
            timing_match = timing_delta <= STEP_TOLERANCE
            if timing_match:
                timing_matches += 1

            if technique_target:
                technique_targets += 1
                detected_techniques = best.get("techniques") or []
                if isinstance(detected_techniques, str):
                    detected_techniques = [detected_techniques]
                technique_match = technique_target in detected_techniques
                if technique_match:
                    technique_matches += 1
        elif technique_target:
            technique_targets += 1

        comparisons.append({
            "referenceIndex": reference_index,
            "measure": _safe_int(reference.get("measure")),
            "step": target_step,
            "stringIndex": _safe_int(reference.get("stringIndex")),
            "fret": _safe_int(reference.get("fret")),
            "technique": technique_target,
            "identityMatch": identity_match,
            "timingMatch": timing_match,
            "timingDelta": timing_delta,
            "techniqueMatch": technique_match,
            "detected": best,
        })

    intro_detected = [
        event for event in detected_events
        if 1 <= _safe_int(event.get("measureNumber")) <= 16
    ]
    false_positive_count = max(0, len(intro_detected) - len(matched_detected_ids))

    reference_count = len(reference_notes)
    detected_count = len(intro_detected)
    identity_recall = exact_identity_matches / reference_count if reference_count else 0.0
    identity_precision = exact_identity_matches / detected_count if detected_count else 0.0
    timing_accuracy = timing_matches / reference_count if reference_count else 0.0
    technique_accuracy = (
        technique_matches / technique_targets if technique_targets else 1.0
    )

    overall_score = (
        0.45 * identity_recall
        + 0.25 * identity_precision
        + 0.25 * timing_accuracy
        + 0.05 * technique_accuracy
    )

    return {
        "passed": overall_score >= PASSING_SCORE,
        "targetScore": PASSING_SCORE,
        "overallScore": round(overall_score, 4),
        "identityRecall": round(identity_recall, 4),
        "identityPrecision": round(identity_precision, 4),
        "timingAccuracy": round(timing_accuracy, 4),
        "techniqueAccuracy": round(technique_accuracy, 4),
        "referenceEventCount": reference_count,
        "detectedIntroEventCount": detected_count,
        "matchedIdentityCount": exact_identity_matches,
        "timingMatchCount": timing_matches,
        "falsePositiveCount": false_positive_count,
        "techniqueTargetCount": technique_targets,
        "techniqueMatchCount": technique_matches,
        "stepTolerance": STEP_TOLERANCE,
        "comparisons": comparisons,
    }


def main() -> None:
    reference = json.loads(REFERENCE_PATH.read_text())
    notation = json.loads(NOTATION_PATH.read_text())
    reference_notes = _expand_reference(reference)
    detected_events = (
        notation.get("fingeringNormalizedEvents")
        or notation.get("motifStabilizedEvents")
        or notation.get("renderEvents")
        or notation.get("rhythmEvents")
        or []
    )

    score = score_intro(reference_notes, detected_events)
    report = {
        "benchmark": "Jimmy PAIge V8 professional intro note accuracy",
        "reference": str(REFERENCE_PATH),
        "notation": str(NOTATION_PATH),
        "selectedEventLayer": (
            "fingeringNormalizedEvents"
            if notation.get("fingeringNormalizedEvents")
            else "motifStabilizedEvents"
        ),
        "protectedBaselinesChanged": notation.get("protectedBaselinesChanged"),
        "notationPassed": notation.get("passed"),
        "score": score,
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional intro benchmark passed:", score["passed"])
    print("Protected V7 unchanged:", notation.get("protectedBaselinesChanged") is False)
    print("Selected event layer:", report["selectedEventLayer"])
    print("Overall score:", score["overallScore"])
    print("Target score:", score["targetScore"])
    print("Identity recall:", score["identityRecall"])
    print("Identity precision:", score["identityPrecision"])
    print("Timing accuracy:", score["timingAccuracy"])
    print("Technique accuracy:", score["techniqueAccuracy"])
    print("Reference events:", score["referenceEventCount"])
    print("Detected intro events:", score["detectedIntroEventCount"])
    print("False positives:", score["falsePositiveCount"])
    print("Wrote:", REPORT_PATH)


if __name__ == "__main__":
    main()
