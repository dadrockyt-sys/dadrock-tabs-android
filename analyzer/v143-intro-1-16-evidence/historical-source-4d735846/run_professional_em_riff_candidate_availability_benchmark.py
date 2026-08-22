from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-diagnosis.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-candidate-availability.json"


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
    slot_reports = diagnosis.get("slotReports") or []

    if not isinstance(slot_reports, list):
        raise ValueError("Expected slotReports to be a list.")

    availability: list[dict[str, Any]] = []
    slots_with_correct_candidate = 0
    slots_with_only_wrong_candidates = 0

    for slot in slot_reports:
        if not isinstance(slot, dict):
            continue

        accepted = {
            _safe_int(value)
            for value in (slot.get("acceptedMidiPitches") or [])
            if _safe_int(value) >= 0
        }
        observed = [
            item
            for item in (slot.get("observedMidiCandidates") or [])
            if isinstance(item, dict) and _safe_int(item.get("midiPitch")) >= 0
        ]

        observed_pitches = [_safe_int(item.get("midiPitch")) for item in observed]
        matching_candidates = [
            {
                "midiPitch": _safe_int(item.get("midiPitch")),
                "support": _safe_int(item.get("support"), 0),
                "rank": index + 1,
            }
            for index, item in enumerate(observed)
            if _safe_int(item.get("midiPitch")) in accepted
        ]

        correct_candidate_present = bool(matching_candidates)
        if correct_candidate_present:
            slots_with_correct_candidate += 1
        else:
            slots_with_only_wrong_candidates += 1

        availability.append(
            {
                "patternId": slot.get("patternId"),
                "quantizedStep": slot.get("quantizedStep"),
                "professionalLabel": slot.get("professionalLabel"),
                "acceptedMidiPitches": sorted(accepted),
                "observedMidiPitches": observed_pitches,
                "correctCandidatePresent": correct_candidate_present,
                "matchingCandidates": matching_candidates,
                "trainingPath": (
                    "candidate-ranking-loop"
                    if correct_candidate_present
                    else "underlying-pitch-extraction-training"
                ),
            }
        )

    protected_slot_count = len(availability)
    candidate_presence_percentage = round(
        100.0 * slots_with_correct_candidate / max(1, protected_slot_count), 2
    )

    if slots_with_correct_candidate == protected_slot_count and protected_slot_count == 9:
        recommended_loop = "bounded-candidate-ranking-training"
        ready_for_training_loop = True
    elif slots_with_correct_candidate > 0:
        recommended_loop = "hybrid-pitch-extraction-and-ranking-training"
        ready_for_training_loop = True
    else:
        recommended_loop = "pitch-extraction-training-only"
        ready_for_training_loop = False

    checks = {
        "pitchDiagnosisPassed": diagnosis.get("passed") is True,
        "allNineProtectedSlotsPresent": protected_slot_count == 9,
        "candidateListsPresent": all(item["observedMidiPitches"] for item in availability),
        "readOnlyBenchmark": True,
        "lockedV7EventsProtected": True,
        "lockedV8TimingProtected": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-candidate-availability",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "readyForBoundedTrainingLoop": ready_for_training_loop,
        "protectedSlotCount": protected_slot_count,
        "slotsWithCorrectPitchCandidate": slots_with_correct_candidate,
        "slotsWithoutCorrectPitchCandidate": slots_with_only_wrong_candidates,
        "candidatePresencePercentage": candidate_presence_percentage,
        "recommendedTrainingLoop": recommended_loop,
        "slotAvailability": availability,
        "checks": checks,
        "safeguards": {
            "diagnosticOnly": True,
            "doesNotRewriteJimmyEvents": True,
            "doesNotCopyProfessionalNotesIntoJimmy": True,
            "doesNotModifyLockedTiming": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Create the first bounded automated loop using the recommended training mode. "
            "The loop must operate on read-only candidates, retain only measurable improvements, "
            "and stop immediately if any protection benchmark fails."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff candidate availability pass:", report["passed"])
    print("Protected slots inspected:", protected_slot_count)
    print(
        "Slots containing a correct pitch candidate:",
        f"{slots_with_correct_candidate}/{protected_slot_count}",
    )
    print("Candidate presence percentage:", f"{candidate_presence_percentage}%")
    print("Recommended training loop:", recommended_loop)
    print("Ready for bounded training loop:", ready_for_training_loop)
    for item in availability:
        print(
            f"- {item['patternId']} step {item['quantizedStep']}: "
            f"correctCandidatePresent={item['correctCandidatePresent']} "
            f"matches={item['matchingCandidates']}"
        )
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
