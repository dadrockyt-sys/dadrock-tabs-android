from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-phase-alignment.json"

INTRO_MEASURE_COUNT = 16
INTRO_PAIR_COUNT = 8
STEPS_PER_MEASURE = 16
STEPS_PER_PAIR = 32
MIN_PAIR_SUPPORT = 4
PHASE_OFFSETS = tuple(range(-8, 9))


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _evaluate_offset(
    intro_candidates: list[dict[str, Any]],
    offset_steps: int,
) -> dict[str, Any]:
    slot_pairs: dict[int, set[int]] = defaultdict(set)
    slot_strengths: dict[int, list[float]] = defaultdict(list)

    for item in intro_candidates:
        measure_number = int(item.get("measureNumber") or 0)
        if measure_number < 1 or measure_number > INTRO_MEASURE_COUNT:
            continue

        position = _safe_float(item.get("positionInMeasure"))
        absolute_step = ((measure_number - 1) * STEPS_PER_MEASURE) + int(
            round(position * STEPS_PER_MEASURE)
        )
        shifted_step = absolute_step + offset_steps

        shifted_measure_index, step_in_measure = divmod(
            shifted_step,
            STEPS_PER_MEASURE,
        )
        shifted_measure_number = shifted_measure_index + 1
        if shifted_measure_number < 1 or shifted_measure_number > INTRO_MEASURE_COUNT:
            continue

        pair_index = shifted_measure_index // 2
        measure_in_pair = shifted_measure_index % 2
        pair_step = measure_in_pair * STEPS_PER_MEASURE + step_in_measure

        slot_pairs[pair_step].add(pair_index)
        slot_strengths[pair_step].append(_safe_float(item.get("strength")))

    support_histogram: Counter[int] = Counter()
    stable_slots: list[dict[str, Any]] = []
    weighted_support = 0.0

    for pair_step in sorted(slot_pairs):
        support = len(slot_pairs[pair_step])
        support_histogram[support] += 1
        strengths = slot_strengths[pair_step]
        median_strength = median(strengths) if strengths else 0.0

        if support >= MIN_PAIR_SUPPORT:
            weighted_support += support * median_strength
            stable_slots.append(
                {
                    "pairStep": pair_step,
                    "pairSupport": support,
                    "supportRatio": round(support / INTRO_PAIR_COUNT, 6),
                    "medianStrength": round(median_strength, 6),
                }
            )

    stable_support_total = sum(
        int(item["pairSupport"])
        for item in stable_slots
    )
    score = (
        len(stable_slots) * 10.0
        + stable_support_total
        + weighted_support
    )

    return {
        "offsetSteps": offset_steps,
        "offsetMeasureFraction": round(offset_steps / STEPS_PER_MEASURE, 6),
        "stableSlotCount": len(stable_slots),
        "stableSupportTotal": stable_support_total,
        "weightedSupport": round(weighted_support, 6),
        "score": round(score, 6),
        "supportHistogram": dict(sorted(support_histogram.items())),
        "stableSlots": stable_slots,
        "readOnly": True,
    }


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            "Missing direct rhythm candidate report. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )

    source = json.loads(INPUT_PATH.read_text())
    candidates = source.get("candidates") or []
    intro_candidates = [
        item
        for item in candidates
        if 1 <= int(item.get("measureNumber") or 0) <= INTRO_MEASURE_COUNT
    ]

    evaluations = [
        _evaluate_offset(intro_candidates, offset_steps)
        for offset_steps in PHASE_OFFSETS
    ]
    ranked = sorted(
        evaluations,
        key=lambda item: (
            float(item["score"]),
            int(item["stableSupportTotal"]),
            int(item["stableSlotCount"]),
            -abs(int(item["offsetSteps"])),
        ),
        reverse=True,
    )
    best = ranked[0] if ranked else None
    zero = next(
        (item for item in evaluations if int(item["offsetSteps"]) == 0),
        None,
    )

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-direct-audio-intro-phase-alignment",
        "input": INPUT_PATH.name,
        "introCandidateCount": len(intro_candidates),
        "minimumPairSupport": MIN_PAIR_SUPPORT,
        "testedOffsets": list(PHASE_OFFSETS),
        "bestAlignment": best,
        "zeroOffsetAlignment": zero,
        "rankedAlignments": ranked,
        "independentOfV7Events": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "passed": bool(best),
        "trainingRule": (
            "This benchmark may identify a stronger measure-grid phase, but it is "
            "read-only. No V7 note, measure assignment, technique, or PDF position "
            "may change until a later professional-reference benchmark improves."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2))

    print("V8 rhythm phase alignment pass:", report["passed"])
    print("Independent of V7 events:", report["independentOfV7Events"])
    print("Renderer changed:", report["rendererChanged"])
    print("Intro candidates evaluated:", len(intro_candidates))
    print("Tested phase offsets:", list(PHASE_OFFSETS))
    print("Zero-offset score:", zero.get("score") if zero else None)
    print("Best phase offset steps:", best.get("offsetSteps") if best else None)
    print(
        "Best phase offset measure fraction:",
        best.get("offsetMeasureFraction") if best else None,
    )
    print("Best alignment score:", best.get("score") if best else None)
    print("Best stable slot count:", best.get("stableSlotCount") if best else None)
    print(
        "Best stable slots (step, support, strength):",
        [
            (
                item.get("pairStep"),
                item.get("pairSupport"),
                item.get("medianStrength"),
            )
            for item in (best.get("stableSlots") if best else [])
        ],
    )
    print("Top phase candidates (offset, score, stable slots):")
    for item in ranked[:5]:
        print(
            " ",
            item.get("offsetSteps"),
            item.get("score"),
            item.get("stableSlotCount"),
        )
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
