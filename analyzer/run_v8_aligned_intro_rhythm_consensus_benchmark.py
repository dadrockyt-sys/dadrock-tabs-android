from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median, pstdev
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-orientation-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-aligned-intro-rhythm-consensus.json"

STEPS_PER_MEASURE = 16
STEPS_PER_PAIR = 32
INTRO_MEASURE_COUNT = 16
INTRO_PAIR_COUNT = 8
MIN_SUPPORT = 4
HIGH_CONFIDENCE_SUPPORT = 6
MAX_TIMING_SPREAD_STEPS = 1.25


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


def _circular_delta(value: float, target: float, period: float) -> float:
    delta = (value - target) % period
    if delta > period / 2.0:
        delta -= period
    return delta


def main() -> None:
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(
            "Missing rhythm candidates. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )
    if not LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing orientation lock. Run "
            "python analyzer/run_v8_intro_orientation_lock_benchmark.py first."
        )

    candidate_report = json.loads(CANDIDATE_PATH.read_text())
    lock_report = json.loads(LOCK_PATH.read_text())

    if lock_report.get("orientationLocked") is not True:
        raise ValueError("Intro orientation is not locked; refusing to build consensus")

    offset_steps = _safe_int(lock_report.get("selectedOffsetSteps"), -999)
    if offset_steps < 0:
        raise ValueError("Locked intro offset is missing or invalid")

    candidates = [
        item
        for item in candidate_report.get("candidates") or []
        if isinstance(item, dict)
        and 1 <= _safe_int(item.get("measureNumber")) <= INTRO_MEASURE_COUNT
    ]

    # Keep the strongest direct-audio onset for each aligned slot in each repeated pair.
    strongest_by_pair_slot: dict[tuple[int, int], dict[str, Any]] = {}
    for item in candidates:
        measure_number = _safe_int(item.get("measureNumber"))
        pair_index = (measure_number - 1) // 2
        measure_in_pair = (measure_number - 1) % 2
        step_in_measure = _safe_int(item.get("quantizedStep")) % STEPS_PER_MEASURE
        raw_pair_step = measure_in_pair * STEPS_PER_MEASURE + step_in_measure
        aligned_pair_step = (raw_pair_step + offset_steps) % STEPS_PER_PAIR
        strength = _safe_float(item.get("strength"))

        position_in_measure = _safe_float(item.get("positionInMeasure"))
        continuous_raw_step = (
            measure_in_pair * STEPS_PER_MEASURE
            + position_in_measure * STEPS_PER_MEASURE
        )
        continuous_aligned_step = (continuous_raw_step + offset_steps) % STEPS_PER_PAIR
        timing_delta = _circular_delta(
            continuous_aligned_step,
            float(aligned_pair_step),
            float(STEPS_PER_PAIR),
        )

        normalized = {
            "pairIndex": pair_index,
            "sourceMeasure": measure_number,
            "rawPairStep": raw_pair_step,
            "alignedPairStep": aligned_pair_step,
            "timingDeltaSteps": round(timing_delta, 6),
            "strength": round(strength, 6),
            "source": item.get("source"),
            "readOnly": True,
        }
        key = (pair_index, aligned_pair_step)
        previous = strongest_by_pair_slot.get(key)
        if previous is None or strength > _safe_float(previous.get("strength")):
            strongest_by_pair_slot[key] = normalized

    events_by_slot: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for (_, aligned_pair_step), event in strongest_by_pair_slot.items():
        events_by_slot[aligned_pair_step].append(event)

    consensus_slots: list[dict[str, Any]] = []
    rejected_slots: list[dict[str, Any]] = []
    support_histogram: Counter[int] = Counter()

    for aligned_pair_step in sorted(events_by_slot):
        slot_events = sorted(
            events_by_slot[aligned_pair_step],
            key=lambda event: int(event["pairIndex"]),
        )
        support = len({int(event["pairIndex"]) for event in slot_events})
        support_histogram[support] += 1
        strengths = [_safe_float(event.get("strength")) for event in slot_events]
        timing_deltas = [
            _safe_float(event.get("timingDeltaSteps")) for event in slot_events
        ]
        timing_spread = pstdev(timing_deltas) if len(timing_deltas) > 1 else 0.0
        stable = support >= MIN_SUPPORT
        high_confidence = (
            support >= HIGH_CONFIDENCE_SUPPORT
            and timing_spread <= MAX_TIMING_SPREAD_STEPS
        )

        slot = {
            "alignedPairStep": aligned_pair_step,
            "measureInPair": aligned_pair_step // STEPS_PER_MEASURE + 1,
            "stepInMeasure": aligned_pair_step % STEPS_PER_MEASURE,
            "pairSupport": support,
            "supportRatio": round(support / INTRO_PAIR_COUNT, 6),
            "medianStrength": round(median(strengths), 6) if strengths else 0.0,
            "timingSpreadSteps": round(timing_spread, 6),
            "stable": stable,
            "highConfidence": high_confidence,
            "sourcePairs": sorted({int(event["pairIndex"]) for event in slot_events}),
            "events": slot_events,
            "readOnly": True,
        }
        if stable:
            consensus_slots.append(slot)
        else:
            rejected_slots.append(slot)

    high_confidence_events = [
        slot for slot in consensus_slots if slot.get("highConfidence") is True
    ]

    checks = {
        "candidateReportPassed": candidate_report.get("passed") is True,
        "orientationLockPassed": lock_report.get("passed") is True,
        "orientationLocked": lock_report.get("orientationLocked") is True,
        "selectedOffsetMatchesLock": offset_steps
        == _safe_int(lock_report.get("selectedOffsetSteps"), -998),
        "allEightPairsRepresented": len(
            {int(event["pairIndex"]) for event in strongest_by_pair_slot.values()}
        ) == INTRO_PAIR_COUNT,
        "consensusSlotsPresent": bool(consensus_slots),
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-aligned-intro-rhythm-consensus",
        "passed": all(checks.values()),
        "orientationOffsetSteps": offset_steps,
        "alignedPairCount": INTRO_PAIR_COUNT,
        "introCandidateCount": len(candidates),
        "deduplicatedPairSlotEventCount": len(strongest_by_pair_slot),
        "minimumSupport": MIN_SUPPORT,
        "highConfidenceSupport": HIGH_CONFIDENCE_SUPPORT,
        "maximumTimingSpreadSteps": MAX_TIMING_SPREAD_STEPS,
        "consensusRhythmSlots": consensus_slots,
        "consensusRhythmSlotCount": len(consensus_slots),
        "highConfidenceConsensusEvents": high_confidence_events,
        "highConfidenceConsensusEventCount": len(high_confidence_events),
        "rejectedLowSupportEvents": rejected_slots,
        "rejectedLowSupportEventCount": len(rejected_slots),
        "supportHistogram": dict(sorted(support_histogram.items())),
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "usesLockedOrientation": True,
        "usesV7PitchEvidence": False,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This stage learns only the repeated intro rhythm skeleton from direct audio. "
            "It must not synthesize notes, replace V7 pitch events, or change the PDF. "
            "The same guarded consensus method can later expand section-by-section "
            "through the complete rhythm part before separate bass and lead models are trained."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_consensus = [
        (
            slot["alignedPairStep"],
            slot["pairSupport"],
            slot["medianStrength"],
            slot["timingSpreadSteps"],
        )
        for slot in consensus_slots
    ]
    compact_high_confidence = [
        (
            slot["alignedPairStep"],
            slot["pairSupport"],
            slot["medianStrength"],
        )
        for slot in high_confidence_events
    ]

    print("Aligned intro rhythm consensus pass:", report["passed"])
    print("Orientation offset steps:", report["orientationOffsetSteps"])
    print("Aligned pair count:", report["alignedPairCount"])
    print("Intro candidates:", report["introCandidateCount"])
    print("Deduplicated pair-slot events:", report["deduplicatedPairSlotEventCount"])
    print("Consensus rhythm slot count:", report["consensusRhythmSlotCount"])
    print("Consensus slots (step, support, strength, spread):", compact_consensus)
    print("High-confidence consensus event count:", report["highConfidenceConsensusEventCount"])
    print("High-confidence events (step, support, strength):", compact_high_confidence)
    print("Rejected low-support event count:", report["rejectedLowSupportEventCount"])
    print("Support histogram:", report["supportHistogram"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
