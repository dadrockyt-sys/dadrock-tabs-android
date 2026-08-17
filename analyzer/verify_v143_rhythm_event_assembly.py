from __future__ import annotations

import json

from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate
from v143_rhythm_event_assembly import assemble_rhythm_events


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def main() -> None:
    timing = ReferenceFreeTimingEstimate(
        beat_times=(0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0),
        first_beat_in_measure=0,
        downbeat_index_mod4=0,
        tempo_bpm=120.0,
        beat_confidence=0.91,
        bar_confidence=0.84,
        source_sample_rate=44_100,
    )

    candidates = (
        {
            "measure": 1,
            "step": 0,
            "timeSeconds": 0.5,
            "dominantMidi": 52,
            "pitchHypotheses": [
                {
                    "midi": 52,
                    "sourceCount": 2,
                    "maxAmplitude": 0.85,
                    "minGridError": 0.002,
                    "maxDuration": 0.28,
                    "bestOnsetTime": 0.49,
                    "bestOffsetTime": 0.77,
                }
            ],
        },
        {
            "measure": 1,
            "step": 4,
            "timeSeconds": 1.0,
            "dominantMidi": 55,
            "pitchHypotheses": [
                {
                    "midi": 55,
                    "sourceCount": 1,
                    "maxAmplitude": 0.40,
                    "minGridError": 0.008,
                    "maxDuration": 0.18,
                }
            ],
        },
        {
            "measure": 1,
            "step": 8,
            "timeSeconds": 1.5,
            "dominantMidi": 64,
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
    )

    rows = (
        {
            **candidates[0],
            "v143Score": 3.25,
            "v143Rank": 1,
            "v143Selected": True,
        },
        {
            **candidates[1],
            "v143Score": 0.50,
            "v143Rank": 3,
            "v143Selected": False,
        },
        {
            **candidates[2],
            "v143Score": 2.75,
            "v143Rank": 2,
            "v143Selected": True,
        },
    )

    source = ReferenceFreeRhythmResult(
        timing=timing,
        candidates=candidates,
        rows=rows,
    )
    source_before = canonical(source.to_dict())

    first = assemble_rhythm_events(source)
    second = assemble_rhythm_events(source)

    # Assembly is downstream-only and deterministic.
    assert canonical(source.to_dict()) == source_before
    assert canonical(first.to_dict()) == canonical(second.to_dict())

    payload = first.to_dict()
    assert payload["candidateCount"] == 3
    assert payload["selectedCount"] == 2
    assert len(payload["events"]) == 2
    assert [(event["measure"], event["step"]) for event in payload["events"]] == [
        (1, 0),
        (1, 8),
    ]

    # Frozen selection, score/rank, attack timing and pitch evidence remain exact.
    assert payload["events"][0]["v143Score"] == 3.25
    assert payload["events"][0]["v143Rank"] == 1
    assert payload["events"][0]["v143Selected"] is True
    assert payload["events"][0]["timeSeconds"] == 0.5
    assert payload["events"][0]["pitchHypotheses"] == rows[0]["pitchHypotheses"]

    assert payload["events"][1]["v143Score"] == 2.75
    assert payload["events"][1]["v143Rank"] == 2
    assert payload["events"][1]["v143Selected"] is True
    assert payload["events"][1]["timeSeconds"] == 1.5
    assert payload["events"][1]["pitchHypotheses"] == rows[2]["pitchHypotheses"]

    # Note mapping sits immediately after frozen V143 selection.
    assert (
        payload["events"][0]["midi"],
        payload["events"][0]["stringIndex"],
        payload["events"][0]["fret"],
    ) == (52, 3, 2)
    assert payload["events"][0]["noteMapping"]["jointChordVoicingResolved"] is False

    # Sustain is downstream and attack timing is unchanged.
    assert payload["events"][0]["rhythmSustain"]["durationSteps"] == 2
    assert payload["events"][0]["rhythmSustain"]["tier"] == "medium"
    assert payload["events"][1]["rhythmSustain"]["durationSteps"] == 4
    assert payload["events"][1]["rhythmSustain"]["tier"] == "long"
    assert all(
        event["rhythmSustain"]["attackTimingChanged"] is False
        for event in payload["events"]
    )

    # Techniques are explicit-evidence-only and aggregated for the final payload.
    assert payload["events"][0]["rhythmTechniques"] == []
    assert payload["events"][1]["rhythmTechniques"] == [
        {"type": "bend", "source": "bend-semitones"},
        {"type": "palm-mute", "source": "explicit-palmMuted"},
    ]
    assert payload["techniques"] == ["bend", "palm-mute"]

    assert payload["timing"]["tempoBpm"] == 120.0
    assert payload["assembly"] == {
        "version": 1,
        "mode": "v143-selection-note-map-sustain-technique",
        "selectionChanged": False,
        "attackTimingChanged": False,
        "pitchEvidenceChanged": False,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }

    print("=== V143 RHYTHM EVENT ASSEMBLY VERIFIED ===")
    print("Frozen V143 selection preserved: True")
    print("Frozen score/rank fields preserved: True")
    print("Quantized attack timing preserved exactly: True")
    print("Pitch hypotheses preserved exactly: True")
    print("Frozen note mapper consumed downstream: True")
    print("Sustain/technique enricher consumed downstream: True")
    print("Unselected attacks emitted: False")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("Source result mutated: False")
    print("Deterministic repeat exact: True")
    print("READY FOR PRODUCTION RHYTHM OUTPUT INTEGRATION: True")


if __name__ == "__main__":
    main()
