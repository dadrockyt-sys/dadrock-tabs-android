from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CONSENSUS_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-consensus.json"
INTRO_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-template-lock.json"

EXPECTED_START_MEASURE = 18
EXPECTED_END_MEASURE = 32
EXPECTED_PAIR_COUNT = 7
EXPECTED_HIGH_CONFIDENCE_SLOT_COUNT = 9
EXPECTED_HIGH_CONFIDENCE_STEPS = [2, 6, 10, 14, 18, 20, 22, 26, 30]
EXPECTED_VARIATION_STEPS = [4, 9]
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


def main() -> None:
    if not CONSENSUS_PATH.exists():
        raise FileNotFoundError(
            "Missing Verse 1 rhythm consensus report. Run "
            "python analyzer/run_v8_verse1_rhythm_consensus_benchmark.py first."
        )
    if not INTRO_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing intro rhythm-template lock. Run "
            "python analyzer/run_v8_intro_rhythm_template_lock_benchmark.py first."
        )

    consensus = json.loads(CONSENSUS_PATH.read_text())
    intro_lock = json.loads(INTRO_LOCK_PATH.read_text())

    consensus_slots = [
        item for item in consensus.get("consensusSlots") or []
        if isinstance(item, dict)
    ]
    high_confidence_slots = [
        item for item in consensus.get("highConfidenceSlots") or []
        if isinstance(item, dict)
    ]

    locked_slots: list[dict[str, Any]] = []
    for item in high_confidence_slots:
        support = _safe_int(item.get("pairSupport"))
        spread = _safe_float(item.get("medianDistanceSteps"), 999.0)
        if support < MIN_PAIR_SUPPORT or spread > MAX_MEDIAN_SPREAD_STEPS:
            continue
        locked_slots.append(
            {
                "consensusStep": _safe_int(item.get("consensusStep"), -1),
                "measureInPair": _safe_int(item.get("consensusStep")) // 16,
                "stepInMeasure": _safe_int(item.get("consensusStep")) % 16,
                "pairSupport": support,
                "pairCoverage": _safe_float(item.get("pairCoverage")),
                "medianDistanceSteps": spread,
                "medianStrength": _safe_float(item.get("medianStrength")),
                "source": "verse1-direct-audio-repetition-consensus",
                "readOnly": True,
            }
        )

    variation_slots: list[dict[str, Any]] = []
    for item in consensus_slots:
        step = _safe_int(item.get("consensusStep"), -1)
        if item.get("highConfidence") is True:
            continue
        variation_slots.append(
            {
                "consensusStep": step,
                "measureInPair": step // 16,
                "stepInMeasure": step % 16,
                "pairSupport": _safe_int(item.get("pairSupport")),
                "pairCoverage": _safe_float(item.get("pairCoverage")),
                "medianDistanceSteps": _safe_float(item.get("medianDistanceSteps")),
                "medianStrength": _safe_float(item.get("medianStrength")),
                "classification": "documented-optional-variation",
                "readOnly": True,
            }
        )

    locked_steps = sorted(item["consensusStep"] for item in locked_slots)
    variation_steps = sorted(item["consensusStep"] for item in variation_slots)

    checks = {
        "consensusBenchmarkPassed": consensus.get("passed") is True,
        "introRhythmTemplateLocked": intro_lock.get("rhythmTemplateLocked") is True,
        "verseMeasureRangeUnchanged": (
            _safe_int(consensus.get("startMeasure")) == EXPECTED_START_MEASURE
            and _safe_int(consensus.get("endMeasure")) == EXPECTED_END_MEASURE
        ),
        "allSevenRepeatedPairsRetained": _safe_int(
            consensus.get("alignedPairCount")
        ) == EXPECTED_PAIR_COUNT,
        "expectedLockedSlotCount": len(locked_slots)
        == EXPECTED_HIGH_CONFIDENCE_SLOT_COUNT,
        "expectedLockedSteps": locked_steps == EXPECTED_HIGH_CONFIDENCE_STEPS,
        "optionalVariationsPreserved": variation_steps == EXPECTED_VARIATION_STEPS,
        "minimumPairSupportMet": all(
            item["pairSupport"] >= MIN_PAIR_SUPPORT for item in locked_slots
        ),
        "medianSpreadWithinTolerance": all(
            item["medianDistanceSteps"] <= MAX_MEDIAN_SPREAD_STEPS
            for item in locked_slots
        ),
        "rendererUnchanged": consensus.get("rendererChanged") is False,
        "protectedBaselinesUnchanged": consensus.get(
            "protectedBaselinesChanged"
        ) is False,
        "noSyntheticNotes": consensus.get("checks", {}).get(
            "noSyntheticNotes"
        ) is True,
    }

    template_locked = all(checks.values())
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-verse1-rhythm-template-lock",
        "passed": template_locked,
        "rhythmTemplateLocked": template_locked,
        "sectionLabel": "Verse 1",
        "startMeasure": EXPECTED_START_MEASURE,
        "endMeasure": EXPECTED_END_MEASURE,
        "alignedPairCount": EXPECTED_PAIR_COUNT,
        "lockedSlotCount": len(locked_slots),
        "variationSlotCount": len(variation_slots),
        "lockedRhythmTemplate": locked_slots,
        "documentedOptionalVariations": variation_slots,
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This gate locks only the nine Verse 1 rhythm attacks independently supported "
            "by at least five of the seven repeated two-measure phrases. Lower-support "
            "steps remain documented optional variations and must not be promoted into "
            "the core template. The lock is read-only: it must not synthesize notes, "
            "change pitches, frets, techniques, durations, locked V7 events, the intro "
            "rhythm template, or the PDF renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_locked = [
        (
            item["consensusStep"],
            item["pairSupport"],
            item["pairCoverage"],
            item["medianDistanceSteps"],
        )
        for item in locked_slots
    ]
    compact_variations = [
        (
            item["consensusStep"],
            item["pairSupport"],
            item["pairCoverage"],
        )
        for item in variation_slots
    ]

    print("Verse 1 rhythm template lock pass:", report["passed"])
    print("Rhythm template locked:", report["rhythmTemplateLocked"])
    print("Verse 1 measures:", f"{EXPECTED_START_MEASURE}-{EXPECTED_END_MEASURE}")
    print("Aligned pair count:", report["alignedPairCount"])
    print("Locked rhythm slot count:", report["lockedSlotCount"])
    print("Locked slots (step, support, coverage, spread):", compact_locked)
    print("Optional variation slot count:", report["variationSlotCount"])
    print("Optional variations (step, support, coverage):", compact_variations)
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
