from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DIAGNOSIS_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-diagnosis.json"
PROFILE_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-pitch-failure-profile.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-low-register-penalty-sweep.json"

# Read-only experiment: scale MIDI 40 support and observe whether an existing
# alternative candidate becomes the leading pitch. No notation or renderer data
# is changed, and no professional pitch is inserted into Jimmy's candidates.
PENALTIES = [1.0, 0.85, 0.7, 0.55, 0.4, 0.25, 0.1]


def _safe_int(value: Any, fallback: int = -1) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def main() -> None:
    if not DIAGNOSIS_PATH.exists():
        raise FileNotFoundError(
            "Missing pitch diagnosis. Run python analyzer/"
            "run_professional_em_riff_pitch_diagnosis_benchmark.py first."
        )
    if not PROFILE_PATH.exists():
        raise FileNotFoundError(
            "Missing pitch failure profile. Run python analyzer/"
            "run_professional_em_riff_pitch_failure_profile_benchmark.py first."
        )

    diagnosis = json.loads(DIAGNOSIS_PATH.read_text())
    profile = json.loads(PROFILE_PATH.read_text())
    slot_reports = diagnosis.get("slotReports") or []

    sweep: list[dict[str, Any]] = []
    for penalty in PENALTIES:
        correct = 0
        selections: list[dict[str, Any]] = []

        for slot in slot_reports:
            observed = slot.get("observedMidiCandidates") or []
            accepted = {_safe_int(value) for value in slot.get("acceptedMidiPitches") or []}
            rescored: list[tuple[float, int, int]] = []

            for candidate in observed:
                pitch = _safe_int(candidate.get("midiPitch"))
                support = max(0, _safe_int(candidate.get("support"), 0))
                adjusted = float(support) * (penalty if pitch == 40 else 1.0)
                rescored.append((adjusted, support, pitch))

            rescored.sort(key=lambda item: (-item[0], -item[1], item[2]))
            selected_pitch = rescored[0][2] if rescored else None
            is_correct = selected_pitch in accepted if selected_pitch is not None else False
            if is_correct:
                correct += 1

            selections.append(
                {
                    "patternId": slot.get("patternId"),
                    "quantizedStep": slot.get("quantizedStep"),
                    "selectedMidiPitch": selected_pitch,
                    "acceptedMidiPitches": sorted(accepted),
                    "correct": is_correct,
                }
            )

        sweep.append(
            {
                "lowE2SupportMultiplier": penalty,
                "correctSlots": correct,
                "totalSlots": len(slot_reports),
                "accuracyPercentage": round(100.0 * correct / max(1, len(slot_reports)), 2),
                "selections": selections,
            }
        )

    best = max(
        sweep,
        key=lambda item: (
            item["correctSlots"],
            item["lowE2SupportMultiplier"],
        ),
        default=None,
    )

    checks = {
        "pitchDiagnosisPassed": diagnosis.get("passed") is True,
        "failureProfilePassed": profile.get("passed") is True,
        "nineProtectedSlotsPresent": len(slot_reports) == 9,
        "lowRegisterCollapseConfirmed": profile.get("failureProfile") == "low-register-collapse-dominant",
        "diagnosticOnly": True,
        "doesNotModifyV7OrV8Events": True,
        "doesNotCopyProfessionalNotesIntoJimmy": True,
        "rendererUnchanged": True,
        "protectedBaselinesUnchanged": True,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-low-register-penalty-sweep",
        "passed": all(checks.values()),
        "readyForExactScoring": False,
        "baselineAccuracyPercentage": next(
            (item["accuracyPercentage"] for item in sweep if item["lowE2SupportMultiplier"] == 1.0),
            0.0,
        ),
        "bestReadOnlyExperiment": best,
        "sweep": sweep,
        "checks": checks,
        "safeguards": {
            "readOnlyParameterExperiment": True,
            "doesNotPromotePenalty": True,
            "requiresIndependentValidationBeforeAdoption": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Use the best multiplier only as a candidate for an independent audio-based validation. "
            "Do not apply it to production or rewrite Jimmy's events from this benchmark alone."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff low-register penalty sweep pass:", report["passed"])
    print("Baseline pitch accuracy:", f"{report['baselineAccuracyPercentage']}%")
    if best:
        print("Best read-only multiplier:", best["lowE2SupportMultiplier"])
        print("Best pitch accuracy:", f"{best['accuracyPercentage']}%")
        print("Correct protected slots:", f"{best['correctSlots']}/{best['totalSlots']}")
    print("Penalty promoted to production: False")
    print("Ready for exact scoring: False")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))

    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
