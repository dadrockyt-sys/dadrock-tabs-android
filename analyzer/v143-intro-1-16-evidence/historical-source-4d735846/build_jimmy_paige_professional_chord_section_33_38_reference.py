from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
)

# The professional rhythm-tab PDF remains the sole musical authority.
# String order is high E, B, G, D, A, low E. None means the string is not played.
# These targets deliberately preserve voicing, attack group, sustain, and rests rather
# than reducing the passage to chord names alone.
MEASURES: list[dict[str, Any]] = [
    {
        "measureNumber": 33,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["G6"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.22,
            },
            {
                "phase": 0.20,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.38,
            },
            {
                "phase": 0.36,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.92,
            },
        ],
        "restAfterLastAttack": True,
    },
    {
        "measureNumber": 34,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["A(tp2)"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [2, 2, 2, 2, 0, None],
                "attackKind": "five-string-chord",
                "sustainToPhase": 0.22,
            },
            {
                "phase": 0.20,
                "voicingFretsHighToLow": [2, 2, 2, 2, 0, None],
                "attackKind": "five-string-chord",
                "sustainToPhase": 0.38,
            },
            {
                "phase": 0.36,
                "voicingFretsHighToLow": [2, 2, 2, 2, 0, None],
                "attackKind": "five-string-chord",
                "sustainToPhase": 0.92,
            },
        ],
        "restAfterLastAttack": False,
    },
    {
        "measureNumber": 35,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["E", "D", "E"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [None, 9, 9, 9, 9, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.18,
            },
            {
                "phase": 0.18,
                "voicingFretsHighToLow": [None, 9, 9, 9, 9, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.34,
            },
            {
                "phase": 0.34,
                "voicingFretsHighToLow": [None, 9, 9, 9, 9, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.50,
            },
            {
                "phase": 0.50,
                "voicingFretsHighToLow": [None, 9, 9, 9, 9, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.66,
            },
            {
                "phase": 0.66,
                "voicingFretsHighToLow": [None, 7, 7, 7, 7, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.80,
            },
            {
                "phase": 0.80,
                "voicingFretsHighToLow": [None, 9, 9, 9, 9, None],
                "attackKind": "four-string-power-voicing",
                "sustainToPhase": 0.95,
            },
        ],
        "restAfterLastAttack": True,
    },
    {
        "measureNumber": 36,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["G", "E"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [None, 9, 9, 9, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.14,
            },
            {
                "phase": 0.14,
                "voicingFretsHighToLow": [None, 9, 9, 9, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.27,
            },
            {
                "phase": 0.27,
                "voicingFretsHighToLow": [None, 9, 9, 9, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.40,
            },
            {
                "phase": 0.40,
                "voicingFretsHighToLow": [None, 9, 9, 9, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.53,
            },
            {
                "phase": 0.53,
                "voicingFretsHighToLow": [None, 12, 12, 12, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.67,
            },
            {
                "phase": 0.67,
                "voicingFretsHighToLow": [None, 9, 9, 9, None, None],
                "attackKind": "three-string-power-voicing",
                "sustainToPhase": 0.92,
            },
        ],
        "restAfterLastAttack": True,
    },
    {
        "measureNumber": 37,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["G6"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.22,
            },
            {
                "phase": 0.20,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.38,
            },
            {
                "phase": 0.36,
                "voicingFretsHighToLow": [0, 3, 4, 5, None, None],
                "attackKind": "four-string-chord",
                "sustainToPhase": 0.60,
            },
        ],
        "restAfterLastAttack": True,
    },
    {
        "measureNumber": 38,
        "section": "Chorus",
        "meter": [4, 4],
        "chordLabels": ["A(tp2)"],
        "attacks": [
            {
                "phase": 0.00,
                "voicingFretsHighToLow": [2, 2, 2, 2, 0, None],
                "attackKind": "five-string-chord",
                "sustainToPhase": 0.24,
            },
            {
                "phase": 0.23,
                "voicingFretsHighToLow": [2, 2, 2, 2, 0, None],
                "attackKind": "five-string-chord",
                "sustainToPhase": 0.92,
            },
        ],
        "restAfterLastAttack": False,
    },
]


def _validate() -> None:
    numbers = [int(item["measureNumber"]) for item in MEASURES]
    if numbers != [33, 34, 35, 36, 37, 38]:
        raise RuntimeError(f"Unexpected measure sequence: {numbers}")

    for measure in MEASURES:
        previous_phase = -1.0
        for attack in measure["attacks"]:
            phase = float(attack["phase"])
            sustain = float(attack["sustainToPhase"])
            voicing = attack["voicingFretsHighToLow"]
            if len(voicing) != 6:
                raise RuntimeError(
                    f"Measure {measure['measureNumber']} has a non-six-string voicing"
                )
            if phase < previous_phase:
                raise RuntimeError(
                    f"Measure {measure['measureNumber']} attacks are out of order"
                )
            if not 0.0 <= phase <= 1.0:
                raise RuntimeError(
                    f"Measure {measure['measureNumber']} attack phase is invalid"
                )
            if sustain < phase:
                raise RuntimeError(
                    f"Measure {measure['measureNumber']} sustain ends before attack"
                )
            previous_phase = phase


def main() -> None:
    _validate()

    attack_count = sum(len(item["attacks"]) for item in MEASURES)
    distinct_voicings = {
        tuple(attack["voicingFretsHighToLow"])
        for measure in MEASURES
        for attack in measure["attacks"]
    }

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-rhythm-chord-section-reference",
        "song": "Are You Gonna Go My Way",
        "artist": "Lenny Kravitz",
        "instrument": "rhythm-guitar",
        "sourceAuthority": "professional-rhythm-tab-pdf",
        "sourceMeasures": [33, 34, 35, 36, 37, 38],
        "stringOrder": ["high-e", "B", "G", "D", "A", "low-E"],
        "measures": MEASURES,
        "summary": {
            "measureCount": len(MEASURES),
            "attackTargetCount": attack_count,
            "distinctVoicingCount": len(distinct_voicings),
            "containsChordChangesWithinMeasure": True,
            "containsRestTargets": True,
            "containsSustainTargets": True,
        },
        "protectedCheckpointRequirements": {
            "professionalScoreMinimumPercentage": 93.06,
            "lowRegisterScoreMinimumPercentage": 84.38,
            "midi52MinimumMatches": 32,
            "midi62MinimumMatches": 16,
            "fullSongBenchmarkMinimumPassedSlots": 8,
            "fullSongBenchmarkTotalSlots": 9,
        },
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForTimingCalibration": True,
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional rhythm chord reference built")
    print("Measures: 33-38")
    print(f"Attack targets: {attack_count}")
    print(f"Distinct voicings: {len(distinct_voicings)}")
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print("Ready for timing calibration: True")
    print("Ready for automated training: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
