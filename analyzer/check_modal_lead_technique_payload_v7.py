#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    import modal_analyzer_v7 as analyzer
except ImportError:
    from analyzer import modal_analyzer_v7 as analyzer


def synthetic_result(transcription_type: str) -> dict:
    events = [
        {
            "start": 0.00,
            "end": 0.30,
            "midi": 76,
            "fret": 14,
            "stringIndex": 1,
        },
        {
            "start": 0.35,
            "end": 0.60,
            "midi": 74,
            "fret": 12,
            "stringIndex": 1,
        },
        {
            "start": 0.90,
            "end": 1.10,
            "midi": 74,
            "fret": 12,
            "stringIndex": 1,
        },
        {
            "start": 1.15,
            "end": 1.35,
            "midi": 76,
            "fret": 14,
            "stringIndex": 1,
        },
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
        malformed = analyzer.normalize_lead_technique_context(
            {
                "enableReferenceGuidedLeadTechniques": "true",
                "bendEvidencePresent": 1,
            }
        )
        explicit_off = analyzer.normalize_lead_technique_context({})
        explicit_on = analyzer.normalize_lead_technique_context(
            {
                "enableReferenceGuidedLeadTechniques": True,
                "bendEvidencePresent": True,
            }
        )

        generic_lead = analyzer.analyze_audio_file(
            "unused.wav",
            "lead",
        )
        contextual_lead = analyzer.analyze_audio_file(
            "unused.wav",
            "lead",
            enable_reference_guided_lead_techniques=True,
            bend_evidence_present=True,
        )
        rhythm = analyzer.analyze_audio_file(
            "unused.wav",
            "rhythm",
            enable_reference_guided_lead_techniques=True,
            bend_evidence_present=True,
        )
        bass = analyzer.analyze_audio_file(
            "unused.wav",
            "bass",
            enable_reference_guided_lead_techniques=True,
            bend_evidence_present=True,
        )
    finally:
        analyzer._analyze_audio_file_v6 = original_runner

    diagnostics = contextual_lead.get("leadTechniqueAnalysis") or {}
    checks = {
        "malformedFlagsIgnored": malformed == (False, False),
        "defaultFlagsDisabled": explicit_off == (False, False),
        "explicitBooleanFlagsAccepted": explicit_on == (True, True),
        "genericLeadUnchanged": "leadTechniqueAnalysis" not in generic_lead,
        "contextualLeadEnabled": diagnostics.get("mode")
        == "reference-guided-lead-technique-diagnostic-only",
        "detectsBend": diagnostics.get("bendDetected") is True,
        "detectsRelease": diagnostics.get("releaseDetected") is True,
        "detectsPalmMute": diagnostics.get("palmMuteDetected") is True,
        "requiresBendEvidence": diagnostics.get("bendEvidencePresent") is True,
        "tabUnchanged": contextual_lead.get("generatedTab")
        == generic_lead.get("generatedTab"),
        "eventsUnchanged": contextual_lead.get("events")
        == generic_lead.get("events"),
        "noteCountUnchanged": contextual_lead.get("noteCount")
        == generic_lead.get("noteCount"),
        "noSyntheticNotes": diagnostics.get("syntheticNoteCount") == 0,
        "diagnosticsDoNotAffectTab": contextual_lead.get(
            "leadTechniqueAnalysisAffectsTab"
        )
        is False,
        "diagnosticsDoNotAffectEvents": contextual_lead.get(
            "leadTechniqueAnalysisAffectsEvents"
        )
        is False,
        "rhythmReceivesNoLeadDiagnostics": "leadTechniqueAnalysis" not in rhythm,
        "bassReceivesNoLeadDiagnostics": "leadTechniqueAnalysis" not in bass,
    }

    failed = False
    print("JIMMY PAIGE V7 MODAL LEAD-TECHNIQUE PAYLOAD GUARD")
    print("=" * 72)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 Modal lead-technique payload regression detected. Do not deploy."
        )

    print("\nV7 MODAL LEAD-TECHNIQUE PAYLOAD PRESERVED 💚")
    print("Malformed flags are ignored; lead technique diagnostics are opt-in.")
    print("Rhythm, bass, generated tab, events, and note count remain unchanged.")


if __name__ == "__main__":
    main()
