from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIBRARY_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-pattern-library.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-professional-em-riff-event-scaffold.json"


def main() -> None:
    if not LIBRARY_PATH.exists():
        raise FileNotFoundError(
            "Missing professional rhythm pattern library. Run "
            "python analyzer/build_professional_rhythm_pattern_library.py first."
        )

    library = json.loads(LIBRARY_PATH.read_text())
    pattern_ids = {
        item.get("patternId")
        for item in library.get("patterns") or []
        if isinstance(item, dict)
    }

    required = {"em-riff-a", "em-riff-b"}
    if not required.issubset(pattern_ids):
        raise ValueError("Pattern library is missing em-riff-a or em-riff-b.")

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "professional-em-riff-event-scaffold",
        "status": "source-identity-verified-timing-entry-pending",
        "readyForExactScoring": False,
        "patterns": [
            {
                "patternId": "em-riff-a",
                "sourcePages": [1, 2, 3, 4, 5, 7, 8, 9],
                "verifiedVisibleFeatures": {
                    "tonalCenter": "Em",
                    "containsFullStepBend": True,
                    "containsBendRelease": True,
                    "containsOpenStrings": True,
                    "containsFret2Notes": True,
                    "containsSingleNoteRiff": True,
                    "containsPalmMute": False,
                    "containsDeadNotes": False,
                },
                "events": [],
                "eventEntryStatus": "pending-quantized-step-string-fret-entry",
            },
            {
                "patternId": "em-riff-b",
                "sourcePages": [1, 2, 3, 4, 5, 7, 8, 9],
                "verifiedVisibleFeatures": {
                    "tonalCenter": "Em",
                    "containsFullStepBend": True,
                    "containsBendRelease": True,
                    "containsOpenStrings": True,
                    "containsFret2Notes": True,
                    "containsEndingDoubleStop": True,
                    "endingDoubleStopFrets": [3, 3],
                    "containsPalmMute": False,
                    "containsDeadNotes": False,
                },
                "events": [],
                "eventEntryStatus": "pending-quantized-step-string-fret-entry",
            },
        ],
        "safeguards": {
            "professionalReferenceMayScoreButNotGenerate": True,
            "directAudioRemainsSourceOfTruth": True,
            "noSyntheticNotes": True,
            "lockedV7EventsProtected": True,
            "lockedIntroTemplateProtected": True,
            "lockedVerse1TemplateProtected": True,
            "rendererChanged": False,
            "protectedBaselinesChanged": False,
        },
        "nextStep": (
            "Align the locked direct-audio timing slots with the visible Em riff note identities, "
            "then manually verify string/fret and technique fields before enabling exact scoring."
        ),
    }

    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Professional Em riff scaffold pass: True")
    print("Patterns scaffolded: 2")
    print("Ready for exact scoring: False")
    print("Next target: align direct-audio timing slots with em-riff-a")
    print("Renderer changed: False")
    print("Protected baselines changed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
