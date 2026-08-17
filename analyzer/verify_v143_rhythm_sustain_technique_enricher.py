from __future__ import annotations

import json
from copy import deepcopy

from v143_rhythm_sustain_technique_enricher import (
    enrich_mapped_rhythm_events,
    explicit_technique_evidence,
    quantize_duration_steps,
    raw_duration_seconds,
    step_seconds_from_tempo,
    sustain_tier,
)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main() -> None:
    assert step_seconds_from_tempo(120.0) == 0.125
    assert quantize_duration_steps(0.28, 120.0) == (2, 0.125)
    assert sustain_tier(1) == "short"
    assert sustain_tier(2) == "medium"
    assert sustain_tier(3) == "long"

    events = [
        {
            "measure": 1,
            "step": 0,
            "timeSeconds": 1.0,
            "midi": 52,
            "stringIndex": 3,
            "stringName": "D",
            "fret": 2,
            "v143Score": 3.25,
            "v143Rank": 1,
            "v143Selected": True,
            "pitchHypotheses": [
                {
                    "midi": 52,
                    "sourceCount": 2,
                    "maxAmplitude": 0.85,
                    "minGridError": 0.002,
                    "maxDuration": 0.28,
                    "bestOnsetTime": 0.99,
                    "bestOffsetTime": 1.27,
                }
            ],
            "mappedPitchHypotheses": [
                {
                    "midi": 52,
                    "preferredPosition": {
                        "stringIndex": 3,
                        "stringName": "D",
                        "fret": 2,
                    },
                }
            ],
            "noteMapping": {
                "version": 1,
                "mode": "dominant-midi-lowest-fret",
                "tuning": "standard",
                "stringOrder": "high-to-low",
                "maxFret": 24,
                "jointChordVoicingResolved": False,
            },
        },
        {
            "measure": 1,
            "step": 4,
            "timeSeconds": 1.5,
            "midi": 64,
            "stringIndex": 0,
            "stringName": "e",
            "fret": 0,
            "v143Score": 2.75,
            "v143Rank": 2,
            "v143Selected": True,
            "pitchHypotheses": [
                {
                    "midi": 64,
                    "sourceCount": 2,
                    "maxAmplitude": 0.90,
                    "minGridError": 0.0,
                    "maxDuration": 0.52,
                }
            ],
            "bendSemitones": 1.0,
            "palmMuted": True,
        },
    ]
    original = deepcopy(events)

    duration, source = raw_duration_seconds(events[0])
    assert abs(duration - 0.28) < 1e-12
    assert source == "best-onset-offset"

    duration, source = raw_duration_seconds(events[1])
    assert abs(duration - 0.52) < 1e-12
    assert source == "max-duration"

    explicit = explicit_technique_evidence(events[1])
    assert explicit == [
        {"type": "bend", "source": "bend-semitones"},
        {"type": "palm-mute", "source": "explicit-palmMuted"},
    ]

    first = enrich_mapped_rhythm_events(events, tempo_bpm=120.0)
    second = enrich_mapped_rhythm_events(events, tempo_bpm=120.0)

    # The frozen mapper output must remain untouched.
    assert events == original

    # Frozen V143 and note-mapping fields remain exact.
    for index in range(2):
        for key in (
            "measure",
            "step",
            "timeSeconds",
            "midi",
            "stringIndex",
            "stringName",
            "fret",
            "v143Score",
            "v143Rank",
            "v143Selected",
            "pitchHypotheses",
        ):
            assert first[index][key] == original[index][key]

    assert first[0]["mappedPitchHypotheses"] == original[0]["mappedPitchHypotheses"]
    assert first[0]["noteMapping"] == original[0]["noteMapping"]

    # Duration is quantized independently; attack time is never moved.
    assert first[0]["rhythmSustain"] == {
        "version": 1,
        "durationSeconds": 0.28,
        "durationSteps": 2,
        "stepSeconds": 0.125,
        "tier": "medium",
        "source": "best-onset-offset",
        "attackTimingChanged": False,
    }
    assert first[1]["rhythmSustain"]["durationSteps"] == 4
    assert first[1]["rhythmSustain"]["tier"] == "long"
    assert first[0]["timeSeconds"] == 1.0
    assert first[1]["timeSeconds"] == 1.5

    # Long duration does not fabricate a performance technique.
    assert first[0]["rhythmTechniques"] == []
    assert first[1]["rhythmTechniques"] == explicit
    assert first[0]["techniqueEnrichment"]["durationCreatesTechniqueLabels"] is False
    assert first[0]["techniqueEnrichment"]["professionalReferenceUsed"] is False
    assert first[0]["techniqueEnrichment"]["runtimeLabelsRequired"] is False

    # Repeat must serialize identically.
    assert canonical(first) == canonical(second)

    print("=== V143 RHYTHM SUSTAIN / TECHNIQUE ENRICHER VERIFIED ===")
    print("Frozen V143 fields preserved: True")
    print("Frozen note mapping preserved: True")
    print("Attack timing preserved exactly: True")
    print("Reference-free duration evidence consumed: True")
    print("Duration quantized to 16th-note grid: True")
    print("Sustain tier added downstream: True")
    print("Technique inference from duration: False")
    print("Explicit technique evidence preserved: True")
    print("Input events mutated: False")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("Deterministic repeat exact: True")
    print("READY FOR RHYTHM EVENT ASSEMBLY: True")


if __name__ == "__main__":
    main()
