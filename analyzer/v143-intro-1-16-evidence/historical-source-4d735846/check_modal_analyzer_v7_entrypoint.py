from __future__ import annotations

from copy import deepcopy

try:
    import modal_analyzer_v7 as entrypoint
except ImportError:
    from analyzer import modal_analyzer_v7 as entrypoint


SAMPLE_EVENTS = [
    {
        "start": 0.0,
        "end": 0.9,
        "duration": 0.9,
        "midi": 57,
        "amplitude": 0.8,
        "stringIndex": 4,
        "fret": 12,
        "technique": None,
        "bendSemitones": 0.0,
    },
    {
        "start": 0.0,
        "end": 0.9,
        "duration": 0.9,
        "midi": 61,
        "amplitude": 0.8,
        "stringIndex": 3,
        "fret": 11,
        "technique": None,
        "bendSemitones": 0.0,
    },
    {
        "start": 0.0,
        "end": 0.9,
        "duration": 0.9,
        "midi": 64,
        "amplitude": 0.8,
        "stringIndex": 2,
        "fret": 9,
        "technique": None,
        "bendSemitones": 0.0,
    },
]

BASE_RESULT = {
    "generatedTab": "LOCKED TAB",
    "events": SAMPLE_EVENTS,
    "noteCount": len(SAMPLE_EVENTS),
    "techniques": [],
}


def fake_v6_analyzer(
    audio_path: str,
    transcription_type: str,
) -> dict:
    del audio_path, transcription_type
    return deepcopy(BASE_RESULT)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    original_analyzer = entrypoint._analyze_audio_file_v6
    entrypoint._analyze_audio_file_v6 = fake_v6_analyzer

    try:
        rhythm = entrypoint.analyze_audio_file(
            "fixture.wav",
            "rhythm",
        )
        lead = entrypoint.analyze_audio_file(
            "fixture.wav",
            "lead",
        )
        bass = entrypoint.analyze_audio_file(
            "fixture.wav",
            "bass",
        )
    finally:
        entrypoint._analyze_audio_file_v6 = original_analyzer

    require(
        rhythm["generatedTab"] == BASE_RESULT["generatedTab"],
        "Rhythm generatedTab changed.",
    )
    require(
        rhythm["events"] == BASE_RESULT["events"],
        "Rhythm note events changed.",
    )
    require(
        "chordAnalysis" in rhythm,
        "Rhythm chordAnalysis was not attached.",
    )
    require(
        rhythm.get("chordAnalysisMode") == "diagnostic-only",
        "Rhythm diagnostics are not marked diagnostic-only.",
    )
    require(
        rhythm.get("chordAnalysisAffectsTab") is False,
        "Rhythm diagnostics incorrectly claim to affect tab.",
    )
    require(
        lead == BASE_RESULT,
        "Lead response changed.",
    )
    require(
        bass == BASE_RESULT,
        "Bass response changed.",
    )

    print("JIMMY PAIGE V7 MODAL ENTRY POINT PRESERVED 💚")
    print("Rhythm returns read-only chordAnalysis diagnostics.")
    print("Lead, bass, generatedTab, and events remain unchanged.")


if __name__ == "__main__":
    main()
