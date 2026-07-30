#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    import modal_analyzer_v7 as entrypoint
except ImportError:
    from analyzer import modal_analyzer_v7 as entrypoint


def main() -> None:
    verified_payload = {
        "referenceChords": [
            {"name": "G6", "pitchClasses": [2, 4, 7, 11]},
            {"name": "A(tp2)", "pitchClasses": [1, 4, 9]},
            {"name": "E", "pitchClasses": [4, 8, 11]},
            {"name": "D", "pitchClasses": [2, 6, 9]},
            {"name": "G", "pitchClasses": [2, 7, 11]},
            {"name": "bad", "pitchClasses": ["x"]},
        ],
        "expectedProgression": [
            "G6",
            "A(tp2)",
            "E",
            "D",
            "E",
            "G",
            "E",
            "unknown",
        ],
    }

    chords, progression = entrypoint.normalize_verified_context(
        verified_payload
    )
    chord_names = {
        str(chord.get("name") or "")
        for chord in (chords or [])
    }

    malformed_cases = [
        {},
        {"referenceChords": "bad", "expectedProgression": []},
        {"referenceChords": [], "expectedProgression": ["E"]},
        {
            "referenceChords": [
                {"name": "E", "pitchClasses": [4]}
            ],
            "expectedProgression": ["E"],
        },
        {
            "referenceChords": [
                {"name": "E", "pitchClasses": [4, 8, 11]}
            ],
            "expectedProgression": ["G"],
        },
    ]

    malformed_ignored = all(
        entrypoint.normalize_verified_context(payload)
        == (None, None)
        for payload in malformed_cases
    )

    original_analyzer = entrypoint._analyze_audio_file_v6
    original_adapter = entrypoint.attach_rhythm_chord_diagnostics
    calls: list[dict] = []

    base_result = {
        "generatedTab": "UNCHANGED TAB",
        "events": [
            {"start": 0.0, "end": 0.4, "midi": 52},
            {"start": 0.0, "end": 0.4, "midi": 56},
            {"start": 0.0, "end": 0.4, "midi": 64},
        ],
    }

    def fake_analyzer(
        audio_path: str,
        transcription_type: str,
    ) -> dict:
        return deepcopy(base_result)

    def fake_adapter(
        result: dict,
        transcription_type: str,
        reference_chords=None,
        expected_progression=None,
    ) -> dict:
        calls.append(
            {
                "transcriptionType": transcription_type,
                "referenceChords": deepcopy(reference_chords),
                "expectedProgression": deepcopy(expected_progression),
            }
        )
        return result

    entrypoint._analyze_audio_file_v6 = fake_analyzer
    entrypoint.attach_rhythm_chord_diagnostics = fake_adapter

    try:
        rhythm_result = entrypoint.analyze_audio_file(
            "/tmp/fake.wav",
            "rhythm",
            reference_chords=chords,
            expected_progression=progression,
        )
        lead_result = entrypoint.analyze_audio_file(
            "/tmp/fake.wav",
            "lead",
        )
        bass_result = entrypoint.analyze_audio_file(
            "/tmp/fake.wav",
            "bass",
        )
    finally:
        entrypoint._analyze_audio_file_v6 = original_analyzer
        entrypoint.attach_rhythm_chord_diagnostics = original_adapter

    checks = {
        "verifiedChordNamesAccepted": chord_names
        == {"G6", "A(tp2)", "E", "D", "G"},
        "unknownProgressionRemoved": progression
        == ["G6", "A(tp2)", "E", "D", "E", "G", "E"],
        "malformedContextIgnored": malformed_ignored,
        "rhythmReceivesContext": (
            calls[0]["transcriptionType"] == "rhythm"
            and calls[0]["referenceChords"] == chords
            and calls[0]["expectedProgression"] == progression
        ),
        "leadReceivesNoContext": (
            calls[1]["transcriptionType"] == "lead"
            and calls[1]["referenceChords"] is None
            and calls[1]["expectedProgression"] is None
        ),
        "bassReceivesNoContext": (
            calls[2]["transcriptionType"] == "bass"
            and calls[2]["referenceChords"] is None
            and calls[2]["expectedProgression"] is None
        ),
        "tabUnchanged": all(
            result.get("generatedTab") == "UNCHANGED TAB"
            for result in (rhythm_result, lead_result, bass_result)
        ),
        "eventsUnchanged": all(
            result.get("events") == base_result["events"]
            for result in (rhythm_result, lead_result, bass_result)
        ),
    }

    failed = False
    print("JIMMY PAIGE V7 MODAL VERIFIED-CONTEXT PAYLOAD GUARD")
    print("=" * 72)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 Modal verified-context payload regression detected."
        )

    print("\nV7 MODAL VERIFIED-CONTEXT PAYLOAD PRESERVED 💚")
    print("Malformed context is ignored; verified rhythm context is opt-in.")
    print("Lead, bass, generated tab, and events remain unchanged.")


if __name__ == "__main__":
    main()
