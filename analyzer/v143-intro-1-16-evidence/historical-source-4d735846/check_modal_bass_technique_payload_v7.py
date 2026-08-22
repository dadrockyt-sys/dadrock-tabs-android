#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    import modal_analyzer_v7 as analyzer
except ImportError:
    from analyzer import modal_analyzer_v7 as analyzer


def synthetic_result(transcription_type: str) -> dict:
    events = [
        {"start": 0.00, "end": 0.20, "midi": 40, "fret": 7},
        {"start": 0.30, "end": 0.50, "midi": 38, "fret": 5},
        {"start": 0.62, "end": 0.82, "midi": 40, "fret": 7},
        {"start": 1.75, "end": 1.95, "midi": 47, "fret": 14},
    ]
    return {
        "transcriptionType": transcription_type,
        "generatedTab": "UNCHANGED TAB",
        "events": deepcopy(events),
        "noteCount": len(events),
    }


def main() -> None:
    original_runner = analyzer._analyze_audio_file_v6

    def fake_runner(
        audio_path: str,
        transcription_type: str,
    ) -> dict:
        del audio_path
        return synthetic_result(transcription_type)

    analyzer._analyze_audio_file_v6 = fake_runner

    try:
        malformed = analyzer.normalize_bass_technique_context(
            {"enableReferenceGuidedBassTechniques": "true"}
        )
        explicit_off = analyzer.normalize_bass_technique_context({})
        explicit_on = analyzer.normalize_bass_technique_context(
            {"enableReferenceGuidedBassTechniques": True}
        )

        generic_bass = analyzer.analyze_audio_file(
            "unused.wav",
            "bass",
        )
        contextual_bass = analyzer.analyze_audio_file(
            "unused.wav",
            "bass",
            enable_reference_guided_bass_techniques=True,
        )
        rhythm = analyzer.analyze_audio_file(
            "unused.wav",
            "rhythm",
            enable_reference_guided_bass_techniques=True,
        )
        lead = analyzer.analyze_audio_file(
            "unused.wav",
            "lead",
            enable_reference_guided_bass_techniques=True,
        )
    finally:
        analyzer._analyze_audio_file_v6 = original_runner

    diagnostics = contextual_bass.get("bassTechniqueAnalysis") or {}
    checks = {
        "malformedFlagIgnored": malformed is False,
        "defaultFlagDisabled": explicit_off is False,
        "explicitBooleanFlagAccepted": explicit_on is True,
        "genericBassUnchanged": "bassTechniqueAnalysis" not in generic_bass,
        "contextualBassEnabled": diagnostics.get("mode")
        == "reference-guided-bass-technique-diagnostic-only",
        "detectsFiveSevenContour": diagnostics.get("contour5And7Detected") is True,
        "detectsSlideTarget": diagnostics.get("slideDetected") is True,
        "detectsMutedAttack": diagnostics.get("mutedAttackDetected") is True,
        "detectsRest": diagnostics.get("restDetected") is True,
        "tabUnchanged": contextual_bass.get("generatedTab")
        == generic_bass.get("generatedTab"),
        "eventsUnchanged": contextual_bass.get("events")
        == generic_bass.get("events"),
        "noteCountUnchanged": contextual_bass.get("noteCount")
        == generic_bass.get("noteCount"),
        "noSyntheticNotes": diagnostics.get("syntheticNoteCount") == 0,
        "diagnosticsDoNotAffectTab": contextual_bass.get(
            "bassTechniqueAnalysisAffectsTab"
        )
        is False,
        "diagnosticsDoNotAffectEvents": contextual_bass.get(
            "bassTechniqueAnalysisAffectsEvents"
        )
        is False,
        "rhythmReceivesNoBassDiagnostics": "bassTechniqueAnalysis" not in rhythm,
        "leadReceivesNoBassDiagnostics": "bassTechniqueAnalysis" not in lead,
    }

    failed = False
    print("JIMMY PAIGE V7 MODAL BASS-TECHNIQUE PAYLOAD GUARD")
    print("=" * 72)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 Modal bass-technique payload regression detected. Do not deploy."
        )

    print("\nV7 MODAL BASS-TECHNIQUE PAYLOAD PRESERVED 💚")
    print("Malformed flags are ignored; bass technique diagnostics are opt-in.")
    print("Rhythm, lead, generated tab, events, and note count remain unchanged.")


if __name__ == "__main__":
    main()
