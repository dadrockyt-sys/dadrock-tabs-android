from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference.json"
EXPECTED_MEASURES = list(range(1, 114))
EXPECTED_SECTION_MAP = [
    (1, 16, "Intro"),
    (17, 32, "Verse 1"),
    (33, 38, "Chorus 1"),
    (39, 46, "Riff"),
    (47, 62, "Verse 2"),
    (63, 69, "Chorus 2"),
    (70, 77, "Bridge"),
    (78, 94, "Solo rhythm backing / transition"),
    (95, 102, "Riff"),
    (103, 113, "Out-Chorus / ending"),
]


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def main() -> None:
    if not REFERENCE_PATH.exists():
        raise FileNotFoundError(
            "Missing professional rhythm reference. Run "
            "python analyzer/build_professional_rhythm_reference_measure_map.py first."
        )

    reference = json.loads(REFERENCE_PATH.read_text())
    measures = [item for item in reference.get("measures") or [] if isinstance(item, dict)]
    measure_numbers = [_safe_int(item.get("measureNumber"), -1) for item in measures]

    section_map = [
        (
            _safe_int(item.get("startMeasure"), -1),
            _safe_int(item.get("endMeasure"), -1),
            str(item.get("label") or ""),
        )
        for item in reference.get("sectionMap") or []
        if isinstance(item, dict)
    ]

    time_signatures = {
        _safe_int(item.get("measureNumber"), -1): str(item.get("timeSignature") or "")
        for item in reference.get("timeSignatureChanges") or []
        if isinstance(item, dict)
    }

    all_events_verified = bool(measures) and all(
        item.get("eventTranscriptionStatus") == "verified"
        and bool(item.get("events"))
        for item in measures
        if item.get("patternId") != "full-measure-rest"
    )

    checks = {
        "referenceTypeCorrect": reference.get("referenceType") == "professional-rhythm-tab-benchmark",
        "instrumentPartIsRhythm": reference.get("instrumentPart") == "rhythm",
        "measureCountDeclared113": _safe_int(reference.get("measureCount"), -1) == 113,
        "all113MeasuresPresent": len(measures) == 113,
        "measureNumbersConsecutive": measure_numbers == EXPECTED_MEASURES,
        "sectionMapMatchesVerifiedPages": section_map == EXPECTED_SECTION_MAP,
        "measure104IsTwoFour": time_signatures.get(104) == "2/4"
        and measures[103].get("timeSignature") == "2/4",
        "measure105ReturnsToFourFour": time_signatures.get(105) == "4/4"
        and measures[104].get("timeSignature") == "4/4",
        "measure113Present": bool(measures) and measures[-1].get("measureNumber") == 113,
        "allMeasureIdentitiesVerified": bool(measures)
        and all(item.get("measureIdentityVerified") is True for item in measures),
        "professionalReferenceCannotGenerate": reference.get("safeguards", {}).get(
            "professionalReferenceMayScoreButNotGenerate"
        ) is True,
        "directAudioRemainsSourceOfTruth": reference.get("safeguards", {}).get(
            "directAudioRemainsSourceOfTruth"
        ) is True,
        "lockedV7EventsProtected": reference.get("safeguards", {}).get(
            "lockedV7EventsMustRemainUnchanged"
        ) is True,
        "lockedIntroTemplateProtected": reference.get("safeguards", {}).get(
            "lockedIntroTemplateMustRemainUnchanged"
        ) is True,
        "lockedVerse1TemplateProtected": reference.get("safeguards", {}).get(
            "lockedVerse1TemplateMustRemainUnchanged"
        ) is True,
        "rendererUnchanged": reference.get("safeguards", {}).get("rendererChanged") is False,
        "protectedBaselinesUnchanged": reference.get("safeguards", {}).get(
            "protectedBaselinesChanged"
        ) is False,
        "noSyntheticNotes": reference.get("safeguards", {}).get("noSyntheticNotes") is True,
    }

    structural_pass = all(checks.values())
    scoring_gate_pass = structural_pass and all_events_verified and reference.get("readyForScoring") is True

    print("Professional rhythm reference structural pass:", structural_pass)
    print("Measures present:", len(measures))
    print("Measure range:", f"{measure_numbers[0]}-{measure_numbers[-1]}" if measures else "none")
    print("Section count:", len(section_map))
    print("Measure 104 time signature:", measures[103].get("timeSignature") if len(measures) >= 104 else None)
    print("Measure 105 time signature:", measures[104].get("timeSignature") if len(measures) >= 105 else None)
    print("All event transcriptions verified:", all_events_verified)
    print("Ready for scoring flag:", reference.get("readyForScoring"))
    print("Scoring gate pass:", scoring_gate_pass)
    print("Checks:", checks)
    print("Renderer changed:", reference.get("safeguards", {}).get("rendererChanged"))
    print("Protected baselines changed:", reference.get("safeguards", {}).get("protectedBaselinesChanged"))

    if not structural_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
