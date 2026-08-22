from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median, pstdev
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONSENSUS_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-aligned-intro-rhythm-consensus.json"
REFERENCE_PATH = REPO_ROOT / "analyzer" / "fixtures" / "gomyway_professional_intro_reference_v1.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-reference-slot-support.json"

STEPS_PER_MEASURE = 16
STEPS_PER_PAIR = 32
INTRO_PAIR_COUNT = 8
MATCH_RADIUS_STEPS = 2
MIN_SUPPORTED_PAIRS = 4
STRONG_SUPPORTED_PAIRS = 6


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


def _circular_distance(left: int, right: int, period: int) -> int:
    delta = abs((left - right) % period)
    return min(delta, period - delta)


def _reference_steps(reference: dict[str, Any]) -> list[int]:
    source_measures = {
        _safe_int(value)
        for value in (reference.get("repeat") or {}).get("sourceMeasures", [1, 2])
    }
    first_measure = min(source_measures) if source_measures else 1
    return sorted(
        {
            ((_safe_int(note.get("measure")) - first_measure) * STEPS_PER_MEASURE
             + _safe_int(note.get("step")))
            % STEPS_PER_PAIR
            for note in reference.get("notes") or []
            if _safe_int(note.get("measure")) in source_measures
        }
    )


def main() -> None:
    if not CONSENSUS_PATH.exists():
        raise FileNotFoundError(
            "Missing aligned intro consensus. Run "
            "python analyzer/run_v8_aligned_intro_rhythm_consensus_benchmark.py first."
        )
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(f"Missing professional reference: {REFERENCE_PATH}")

    consensus = json.loads(CONSENSUS_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    reference_steps = _reference_steps(reference)

    all_events: list[dict[str, Any]] = []
    for slot in (consensus.get("consensusRhythmSlots") or []) + (
        consensus.get("rejectedLowSupportEvents") or []
    ):
        if not isinstance(slot, dict):
            continue
        for event in slot.get("events") or []:
            if isinstance(event, dict):
                all_events.append(event)

    events_by_pair: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in all_events:
        pair_index = _safe_int(event.get("pairIndex"), -1)
        if 0 <= pair_index < INTRO_PAIR_COUNT:
            events_by_pair[pair_index].append(event)

    slot_reports: list[dict[str, Any]] = []
    unmatched_events: list[dict[str, Any]] = []
    used_event_ids: set[tuple[int, int]] = set()

    for target_step in reference_steps:
        matches: list[dict[str, Any]] = []
        for pair_index in range(INTRO_PAIR_COUNT):
            candidates = []
            for event_index, event in enumerate(events_by_pair.get(pair_index, [])):
                event_step = _safe_int(event.get("alignedPairStep")) % STEPS_PER_PAIR
                distance = _circular_distance(event_step, target_step, STEPS_PER_PAIR)
                if distance <= MATCH_RADIUS_STEPS:
                    candidates.append((distance, -_safe_float(event.get("strength")), event_index, event))
            if not candidates:
                continue
            distance, _, event_index, event = min(candidates, key=lambda item: (item[0], item[1]))
            used_event_ids.add((pair_index, event_index))
            matches.append(
                {
                    "pairIndex": pair_index,
                    "targetStep": target_step,
                    "observedStep": _safe_int(event.get("alignedPairStep")) % STEPS_PER_PAIR,
                    "stepDistance": distance,
                    "timingDeltaSteps": _safe_float(event.get("timingDeltaSteps")),
                    "strength": _safe_float(event.get("strength")),
                    "readOnly": True,
                }
            )

        support = len({item["pairIndex"] for item in matches})
        observed_steps = [item["observedStep"] for item in matches]
        distances = [item["stepDistance"] for item in matches]
        strengths = [item["strength"] for item in matches]
        timing = [item["timingDeltaSteps"] for item in matches]
        slot_reports.append(
            {
                "referenceStep": target_step,
                "measureInPair": target_step // STEPS_PER_MEASURE + 1,
                "stepInMeasure": target_step % STEPS_PER_MEASURE,
                "pairSupport": support,
                "supportRatio": round(support / INTRO_PAIR_COUNT, 6),
                "supported": support >= MIN_SUPPORTED_PAIRS,
                "strongSupport": support >= STRONG_SUPPORTED_PAIRS,
                "medianObservedStep": round(median(observed_steps), 6) if observed_steps else None,
                "medianStepDistance": round(median(distances), 6) if distances else None,
                "medianStrength": round(median(strengths), 6) if strengths else 0.0,
                "timingSpreadSteps": round(pstdev(timing), 6) if len(timing) > 1 else 0.0,
                "matches": matches,
                "readOnly": True,
            }
        )

    for pair_index, events in events_by_pair.items():
        for event_index, event in enumerate(events):
            if (pair_index, event_index) not in used_event_ids:
                unmatched_events.append(event)

    supported = [item for item in slot_reports if item["supported"]]
    strong = [item for item in slot_reports if item["strongSupport"]]
    support_histogram = Counter(item["pairSupport"] for item in slot_reports)
    reference_coverage = len(supported) / len(reference_steps) if reference_steps else 0.0

    checks = {
        "alignedConsensusPassed": consensus.get("passed") is True,
        "orientationOffsetIsLockedTwelve": _safe_int(consensus.get("orientationOffsetSteps"), -1) == 12,
        "allEightPairsRepresented": len(events_by_pair) == INTRO_PAIR_COUNT,
        "referenceSlotsPresent": bool(reference_steps),
        "supportedReferenceSlotsPresent": bool(supported),
        "rendererUnchanged": consensus.get("rendererChanged") is False,
        "protectedBaselinesUnchanged": consensus.get("protectedBaselinesChanged") is False,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-professional-intro-reference-slot-support",
        "passed": all(checks.values()),
        "matchRadiusSteps": MATCH_RADIUS_STEPS,
        "minimumSupportedPairs": MIN_SUPPORTED_PAIRS,
        "strongSupportedPairs": STRONG_SUPPORTED_PAIRS,
        "referenceSteps": reference_steps,
        "referenceSlotCount": len(reference_steps),
        "supportedReferenceSlots": supported,
        "supportedReferenceSlotCount": len(supported),
        "strongReferenceSlots": strong,
        "strongReferenceSlotCount": len(strong),
        "referenceCoverage": round(reference_coverage, 6),
        "slotReports": slot_reports,
        "supportHistogram": dict(sorted(support_histogram.items())),
        "unmatchedDirectAudioEvents": unmatched_events,
        "unmatchedDirectAudioEventCount": len(unmatched_events),
        "checks": checks,
        "usesProfessionalReferenceAsBenchmarkOnly": True,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "The professional reference defines expected rhythm attack locations only. "
            "A slot is supported solely when direct-audio onset evidence appears near it "
            "in at least four of the eight aligned repetitions. This diagnostic must not "
            "create notes, copy the reference into production, or change the renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact = [
        (
            item["referenceStep"],
            item["pairSupport"],
            item["medianObservedStep"],
            item["medianStepDistance"],
            item["medianStrength"],
        )
        for item in slot_reports
    ]

    print("Intro reference-slot support pass:", report["passed"])
    print("Reference slot count:", report["referenceSlotCount"])
    print("Supported reference slot count:", report["supportedReferenceSlotCount"])
    print("Strong reference slot count:", report["strongReferenceSlotCount"])
    print("Reference coverage:", report["referenceCoverage"])
    print("Reference slots (step, support, observed, distance, strength):", compact)
    print("Support histogram:", report["supportHistogram"])
    print("Unmatched direct-audio event count:", report["unmatchedDirectAudioEventCount"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
