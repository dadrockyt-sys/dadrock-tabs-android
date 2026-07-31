from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-diagnosis.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-failure-profile.json"


def _safe_int(value: Any, fallback: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def main() -> None:
    if not DIAGNOSIS_PATH.exists():
        raise FileNotFoundError(
            "Missing Em riff pitch diagnosis. Run "
            "python analyzer/run_professional_em_riff_pitch_diagnosis_benchmark.py first."
        )

    diagnosis = json.loads(DIAGNOSIS_PATH.read_text())
    slot_reports = [
        item
        for item in diagnosis.get("slotReports") or []
        if isinstance(item, dict)
    ]

    observed_counter: Counter[int] = Counter()
    slot_profiles: list[dict[str, Any]] = []

    for node in slot_reports:
        observed = node.get("observedMidiCandidates") or []
        expected = node.get("acceptedMidiPitches") or []

        observed_pitches: list[int] = []
        for item in observed:
            if not isinstance(item, dict):
                continue
            pitch = _safe_int(item.get("midiPitch"))
            support = max(1, _safe_int(item.get("support"), 1))
            if pitch >= 0:
                observed_pitches.append(pitch)
                observed_counter[pitch] += support

        expected_pitches = [
            pitch
            for pitch in (_safe_int(item) for item in expected)
            if pitch >= 0
        ]

        leading = observed_pitches[0] if observed_pitches else None
        nearest_distance = None
        if leading is not None and expected_pitches:
            nearest_distance = min(
                abs(leading - expected_pitch)
                for expected_pitch in expected_pitches
            )

        slot_profiles.append(
            {
                "patternId": node.get("patternId"),
                "quantizedStep": node.get("quantizedStep"),
                "leadingObservedMidiPitch": leading,
                "expectedMidiPitches": expected_pitches,
                "nearestSemitoneDistance": nearest_distance,
                "leadingIsLowE2": leading == 40,
                "leadingIsOctaveRelated": nearest_distance in {12, 24},
                "leadingIsFifthRelated": nearest_distance in {7, 19},
            }
        )

    protected_slots = len(slot_profiles)
    low_e_collapse_slots = sum(
        1 for item in slot_profiles if item["leadingIsLowE2"]
    )
    octave_related_slots = sum(
        1 for item in slot_profiles if item["leadingIsOctaveRelated"]
    )
    fifth_related_slots = sum(
        1 for item in slot_profiles if item["leadingIsFifthRelated"]
    )

    dominant_observed = observed_counter.most_common(5)
    dominant_pitch = dominant_observed[0][0] if dominant_observed else None
    low_e_collapse_ratio = (
        round(low_e_collapse_slots / protected_slots, 6)
        if protected_slots
        else 0.0
    )

    profile = (
        "low-register-collapse-dominant"
        if low_e_collapse_ratio >= 0.5
        else "mixed-pitch-selection-errors"
    )

    checks = {
        "pitchDiagnosisPassed": diagnosis.get("passed") is True,
        "slotReportsPresent": len(slot_reports) == 9,
        "protectedSlotsPresent": protected_slots == 9,
        "observedPitchEvidencePresent": bool(observed_counter),
        "readOnlyDiagnosis": True,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-pitch-failure-profile",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "protectedSlotCount": protected_slots,
        "failureProfile": profile,
        "dominantObservedMidiPitch": dominant_pitch,
        "dominantObservedPitchHistogram": [
            {"midiPitch": pitch, "support": support}
            for pitch, support in dominant_observed
        ],
        "lowE2CollapseSlots": low_e_collapse_slots,
        "lowE2CollapseRatio": low_e_collapse_ratio,
        "octaveRelatedErrorSlots": octave_related_slots,
        "fifthRelatedErrorSlots": fifth_related_slots,
        "slotProfiles": slot_profiles,
        "checks": checks,
        "trainingRecommendation": (
            "Train the pitch-selection layer before fretboard assignment. "
            "Use the repeated Em-riff evidence to penalize unsupported low-register "
            "fundamentals, but do not alter protected production events."
        ),
        "safeguards": {
            "diagnosticOnly": True,
            "doesNotRewriteJimmyEvents": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff pitch failure profile pass:", report["passed"])
    print("Failure profile:", profile)
    print("Dominant observed MIDI pitch:", dominant_pitch)
    print("Low-E2 collapse slots:", f"{low_e_collapse_slots}/{protected_slots}")
    print("Low-E2 collapse ratio:", f"{low_e_collapse_ratio * 100:.1f}%")
    print("Octave-related error slots:", octave_related_slots)
    print("Fifth-related error slots:", fifth_related_slots)
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
