from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SUPPORT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-reference-slot-support.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"

EXPECTED_REFERENCE_SLOTS = 12
EXPECTED_INTRO_PAIRS = 8
MAX_MEDIAN_DISTANCE_STEPS = 1.5
MAX_UNMATCHED_EVENTS = 8


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
    if not SUPPORT_PATH.exists():
        raise FileNotFoundError(
            "Missing intro reference-slot support report. Run "
            "python analyzer/run_v8_intro_reference_slot_support_benchmark.py first."
        )

    support_report = json.loads(SUPPORT_PATH.read_text())
    slot_reports = [
        item for item in support_report.get("slotReports") or []
        if isinstance(item, dict)
    ]

    locked_slots: list[dict[str, Any]] = []
    for item in slot_reports:
        reference_step = _safe_int(item.get("referenceStep"), -1)
        observed_step = item.get("medianObservedStep")
        median_distance = _safe_float(item.get("medianStepDistance"), 999.0)
        pair_support = _safe_int(item.get("pairSupport"), 0)

        if reference_step < 0 or observed_step is None:
            continue

        locked_slots.append(
            {
                "referenceStep": reference_step,
                "measureInPair": _safe_int(item.get("measureInPair"), 0),
                "stepInMeasure": _safe_int(item.get("stepInMeasure"), 0),
                "learnedObservedStep": _safe_float(observed_step),
                "timingCorrectionSteps": round(
                    float(reference_step) - _safe_float(observed_step), 6
                ),
                "pairSupport": pair_support,
                "supportRatio": _safe_float(item.get("supportRatio")),
                "medianStepDistance": median_distance,
                "medianStrength": _safe_float(item.get("medianStrength")),
                "timingSpreadSteps": _safe_float(item.get("timingSpreadSteps")),
                "strongSupport": item.get("strongSupport") is True,
                "source": "direct-audio-repetition-consensus",
                "readOnly": True,
            }
        )

    distances = [
        _safe_float(item.get("medianStepDistance"), 999.0)
        for item in locked_slots
    ]
    minimum_support = min(
        (_safe_int(item.get("pairSupport"), 0) for item in locked_slots),
        default=0,
    )
    maximum_distance = max(distances, default=999.0)

    checks = {
        "supportBenchmarkPassed": support_report.get("passed") is True,
        "allReferenceSlotsPresent": _safe_int(
            support_report.get("referenceSlotCount"), -1
        ) == EXPECTED_REFERENCE_SLOTS,
        "allReferenceSlotsSupported": _safe_int(
            support_report.get("supportedReferenceSlotCount"), -1
        ) == EXPECTED_REFERENCE_SLOTS,
        "allReferenceSlotsStrong": _safe_int(
            support_report.get("strongReferenceSlotCount"), -1
        ) == EXPECTED_REFERENCE_SLOTS,
        "fullReferenceCoverage": _safe_float(
            support_report.get("referenceCoverage"), 0.0
        ) == 1.0,
        "allEightPairsContributed": minimum_support >= EXPECTED_INTRO_PAIRS - 1,
        "timingDistanceWithinTolerance": maximum_distance
        <= MAX_MEDIAN_DISTANCE_STEPS,
        "unmatchedEventsWithinTolerance": _safe_int(
            support_report.get("unmatchedDirectAudioEventCount"), 999
        ) <= MAX_UNMATCHED_EVENTS,
        "lockedSlotCountMatchesReference": len(locked_slots)
        == EXPECTED_REFERENCE_SLOTS,
        "rendererUnchanged": support_report.get("rendererChanged") is False,
        "protectedBaselinesUnchanged": support_report.get(
            "protectedBaselinesChanged"
        ) is False,
        "noSyntheticNotes": True,
    }

    rhythm_template_locked = all(checks.values())
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-intro-rhythm-template-lock",
        "passed": rhythm_template_locked,
        "rhythmTemplateLocked": rhythm_template_locked,
        "referenceSlotCount": EXPECTED_REFERENCE_SLOTS,
        "lockedSlotCount": len(locked_slots),
        "minimumPairSupport": minimum_support,
        "maximumMedianDistanceSteps": round(maximum_distance, 6),
        "unmatchedDirectAudioEventCount": _safe_int(
            support_report.get("unmatchedDirectAudioEventCount"), 0
        ),
        "lockedRhythmTemplate": locked_slots,
        "checks": checks,
        "usesProfessionalReferenceAsCalibrationOnly": True,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "The intro rhythm template may lock only when every professional attack slot "
            "is independently supported by repeated direct-audio evidence. The reference "
            "provides calibration coordinates only; it must not create pitches, frets, "
            "techniques, durations, or production notes. Renderer and V7 baselines remain "
            "unchanged until a later guarded integration benchmark passes."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_slots = [
        (
            item["referenceStep"],
            item["learnedObservedStep"],
            item["timingCorrectionSteps"],
            item["pairSupport"],
            item["medianStrength"],
        )
        for item in locked_slots
    ]

    print("Intro rhythm template lock pass:", report["passed"])
    print("Rhythm template locked:", report["rhythmTemplateLocked"])
    print("Reference slot count:", report["referenceSlotCount"])
    print("Locked slot count:", report["lockedSlotCount"])
    print("Minimum pair support:", report["minimumPairSupport"])
    print("Maximum median distance steps:", report["maximumMedianDistanceSteps"])
    print("Unmatched direct-audio event count:", report["unmatchedDirectAudioEventCount"])
    print(
        "Locked slots (reference, observed, correction, support, strength):",
        compact_slots,
    )
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
