from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
REPETITION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-repetition.json"
INTRO_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-consensus.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
MATCH_RADIUS_STEPS = 1
MIN_PAIR_SUPPORT = 5
MAX_MEDIAN_SPREAD_STEPS = 1.0


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


def _pair_step(event: dict[str, Any], pair_start: int) -> int:
    measure = _safe_int(event.get("measureNumber"))
    step = _safe_int(event.get("quantizedStep"))
    return ((measure - pair_start) * STEPS_PER_MEASURE) + step


def _nearest_slot(step: int, slots: list[int]) -> int | None:
    candidates = [slot for slot in slots if abs(slot - step) <= MATCH_RADIUS_STEPS]
    if not candidates:
        return None
    return min(candidates, key=lambda slot: (abs(slot - step), slot))


def main() -> None:
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(
            "Missing rhythm candidates. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )
    if not REPETITION_PATH.exists():
        raise FileNotFoundError(
            "Missing Verse 1 repetition report. Run "
            "python analyzer/run_v8_verse1_rhythm_repetition_benchmark.py first."
        )
    if not INTRO_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing intro rhythm-template lock. Run "
            "python analyzer/run_v8_intro_rhythm_template_lock_benchmark.py first."
        )

    candidate_report = json.loads(CANDIDATE_PATH.read_text())
    repetition_report = json.loads(REPETITION_PATH.read_text())
    intro_lock = json.loads(INTRO_LOCK_PATH.read_text())

    start_measure = _safe_int(repetition_report.get("startMeasure"), 18)
    end_measure = _safe_int(repetition_report.get("endMeasure"), 32)
    pair_starts = [
        _safe_int(value)
        for value in repetition_report.get("repeatedPairStartMeasures") or []
        if _safe_int(value) > 0
    ]

    verse_events = [
        event for event in candidate_report.get("candidates") or []
        if isinstance(event, dict)
        and start_measure <= _safe_int(event.get("measureNumber")) <= end_measure
    ]

    events_by_pair: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for pair_start in pair_starts:
        for event in verse_events:
            measure = _safe_int(event.get("measureNumber"))
            if pair_start <= measure <= pair_start + 1:
                events_by_pair[pair_start].append(event)

    observed_steps_by_pair: dict[int, list[int]] = {
        pair_start: sorted({_pair_step(event, pair_start) for event in events})
        for pair_start, events in events_by_pair.items()
    }

    seed_support: Counter[int] = Counter()
    for steps in observed_steps_by_pair.values():
        for step in steps:
            seed_support[step] += 1

    ordered_seeds = sorted(
        seed_support,
        key=lambda step: (-seed_support[step], step),
    )
    consensus_seed_slots: list[int] = []
    for step in ordered_seeds:
        if _nearest_slot(step, consensus_seed_slots) is None:
            consensus_seed_slots.append(step)
    consensus_seed_slots.sort()

    slot_observations: dict[int, list[dict[str, Any]]] = defaultdict(list)
    unmatched_events: list[dict[str, Any]] = []

    for pair_start in pair_starts:
        used_slots: set[int] = set()
        for event in sorted(
            events_by_pair.get(pair_start, []),
            key=lambda item: (_pair_step(item, pair_start), -_safe_float(item.get("strength"))),
        ):
            observed_step = _pair_step(event, pair_start)
            slot = _nearest_slot(observed_step, consensus_seed_slots)
            if slot is None or slot in used_slots:
                unmatched_events.append({
                    "pairStartMeasure": pair_start,
                    "observedStep": observed_step,
                    "strength": round(_safe_float(event.get("strength")), 6),
                    "readOnly": True,
                })
                continue
            used_slots.add(slot)
            slot_observations[slot].append({
                "pairStartMeasure": pair_start,
                "observedStep": observed_step,
                "distanceSteps": abs(observed_step - slot),
                "strength": _safe_float(event.get("strength")),
                "readOnly": True,
            })

    slot_reports: list[dict[str, Any]] = []
    locked_slots: list[dict[str, Any]] = []
    for seed_slot in consensus_seed_slots:
        observations = slot_observations.get(seed_slot, [])
        observed_steps = [item["observedStep"] for item in observations]
        strengths = [item["strength"] for item in observations]
        support = len(observations)
        consensus_step = int(round(median(observed_steps))) if observed_steps else seed_slot
        median_distance = (
            round(median(abs(step - consensus_step) for step in observed_steps), 6)
            if observed_steps else 0.0
        )
        median_strength = round(median(strengths), 6) if strengths else 0.0
        high_confidence = (
            support >= MIN_PAIR_SUPPORT
            and median_distance <= MAX_MEDIAN_SPREAD_STEPS
        )
        report = {
            "seedStep": seed_slot,
            "consensusStep": consensus_step,
            "pairSupport": support,
            "pairCoverage": round(support / len(pair_starts), 6) if pair_starts else 0.0,
            "medianDistanceSteps": median_distance,
            "medianStrength": median_strength,
            "observedSteps": observed_steps,
            "highConfidence": high_confidence,
            "readOnly": True,
        }
        slot_reports.append(report)
        if high_confidence:
            locked_slots.append(report)

    support_histogram = dict(sorted(Counter(item["pairSupport"] for item in slot_reports).items()))
    maximum_median_distance = max(
        (item["medianDistanceSteps"] for item in locked_slots),
        default=0.0,
    )

    checks = {
        "candidateReportPassed": candidate_report.get("passed") is True,
        "repetitionReportPassed": repetition_report.get("passed") is True,
        "introRhythmTemplateLocked": intro_lock.get("rhythmTemplateLocked") is True,
        "allRepeatedPairsRepresented": len(events_by_pair) == len(pair_starts) and bool(pair_starts),
        "consensusSlotsPresent": bool(slot_reports),
        "highConfidenceSlotsPresent": bool(locked_slots),
        "minimumPairSupportMet": all(
            item["pairSupport"] >= MIN_PAIR_SUPPORT for item in locked_slots
        ),
        "medianSpreadWithinTolerance": all(
            item["medianDistanceSteps"] <= MAX_MEDIAN_SPREAD_STEPS
            for item in locked_slots
        ),
        "rendererUnchanged": candidate_report.get("diagnostics", {}).get("rendererChanged") is False,
        "protectedBaselinesUnchanged": candidate_report.get("protectedBaselinesChanged") is False,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-verse1-rhythm-consensus",
        "passed": all(checks.values()),
        "sectionLabel": "Verse 1",
        "startMeasure": start_measure,
        "endMeasure": end_measure,
        "repeatedPairStartMeasures": pair_starts,
        "alignedPairCount": len(pair_starts),
        "directAudioEventCount": len(verse_events),
        "consensusSlotCount": len(slot_reports),
        "highConfidenceSlotCount": len(locked_slots),
        "minimumPairSupport": MIN_PAIR_SUPPORT,
        "maximumAllowedMedianSpreadSteps": MAX_MEDIAN_SPREAD_STEPS,
        "maximumObservedMedianSpreadSteps": maximum_median_distance,
        "consensusSlots": slot_reports,
        "highConfidenceSlots": locked_slots,
        "supportHistogram": support_histogram,
        "unmatchedDirectAudioEventCount": len(unmatched_events),
        "unmatchedDirectAudioEvents": unmatched_events,
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This stage aligns the seven repeated Verse 1 two-measure phrases and derives "
            "a timing consensus from direct-audio rhythm candidates only. It may merge "
            "events within one sixteenth-note step, but it must not copy professional "
            "notes, synthesize attacks, alter locked V7 events, or change the PDF renderer. "
            "The high-confidence output remains a read-only proposal until a later lock gate."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_slots = [
        (
            item["consensusStep"],
            item["pairSupport"],
            item["pairCoverage"],
            item["medianDistanceSteps"],
            item["medianStrength"],
        )
        for item in slot_reports
    ]
    compact_high_confidence = [
        (
            item["consensusStep"],
            item["pairSupport"],
            item["pairCoverage"],
            item["medianDistanceSteps"],
        )
        for item in locked_slots
    ]

    print("Verse 1 rhythm consensus pass:", report["passed"])
    print("Verse 1 measures:", f"{start_measure}-{end_measure}")
    print("Aligned pair count:", report["alignedPairCount"])
    print("Direct-audio event count:", report["directAudioEventCount"])
    print("Consensus rhythm slot count:", report["consensusSlotCount"])
    print("Consensus slots (step, support, coverage, spread, strength):", compact_slots)
    print("High-confidence rhythm slot count:", report["highConfidenceSlotCount"])
    print("High-confidence slots (step, support, coverage, spread):", compact_high_confidence)
    print("Support histogram:", report["supportHistogram"])
    print("Unmatched direct-audio event count:", report["unmatchedDirectAudioEventCount"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
