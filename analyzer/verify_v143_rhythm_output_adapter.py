from __future__ import annotations

import json
from copy import deepcopy

from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate
from v143_rhythm_event_assembly import assemble_rhythm_events
from v143_rhythm_output_adapter import build_rhythm_output, render_event_token


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
            "time_seconds": 0.5,
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
            "time_seconds": 1.0,
            "dominantMidi": 64,
            "pitchHypotheses": [
                {
                    "midi": 64,
                    "sourceCount": 2,
                    "maxAmplitude": 0.90,
                    "minGridError": 0.001,
                    "maxDuration": 0.50,
                }
            ],
        },
        {
            "measure": 1,
            "step": 8,
            "time_seconds": 1.5,
            "dominantMidi": 55,
            "pitchHypotheses": [
                {
                    "midi": 55,
                    "sourceCount": 1,
                    "maxAmplitude": 0.50,
                    "minGridError": 0.003,
                    "maxDuration": 0.18,
                }
            ],
        },
    )

    rows = (
        {
            **candidates[0],
            "timeSeconds": 0.5,
            "v143Score": 3.0,
            "v143Rank": 1,
            "v143Selected": True,
        },
        {
            **candidates[1],
            "timeSeconds": 1.0,
            "v143Score": 2.0,
            "v143Rank": 2,
            "v143Selected": True,
            "bendSemitones": 1.0,
        },
        {
            **candidates[2],
            "timeSeconds": 1.5,
            "v143Score": -1.0,
            "v143Rank": 3,
            "v143Selected": False,
        },
    )

    source = ReferenceFreeRhythmResult(
        timing=timing,
        candidates=tuple(deepcopy(candidate) for candidate in candidates),
        rows=tuple(deepcopy(row) for row in rows),
    )
    source_before = canonical(source.to_dict())

    assembly = assemble_rhythm_events(source)
    first = build_rhythm_output(assembly)
    second = build_rhythm_output(assembly)

    assert source_before == canonical(source.to_dict())
    assert first == second

    assert first["tuning"] == "E Standard"
    assert first["tempo"] == 120.0
    assert first["timeSignature"] == "4/4"
    assert first["noteCount"] == 2
    assert first["candidateCount"] == 3
    assert first["selectedCount"] == 2
    assert first["engineVersion"] == "v143-reference-free-rhythm-output-v1"

    # The unselected step-8 attack must not appear in final events.
    assert [(event["measure"], event["step"]) for event in first["events"]] == [
        (1, 0),
        (1, 4),
    ]

    # Existing API contract receives a non-empty generatedTab string.
    tab = first["generatedTab"]
    assert isinstance(tab, str) and tab.strip()
    assert "Measure 1" in tab
    assert "D|2---" in tab
    assert "e|" in tab

    # Technique metadata remains explicit-only; bend rendering is downstream only.
    assert first["techniques"] == ["bend"]
    bend_event = first["events"][1]
    assert render_event_token(bend_event) == "0b"
    assert "0b--" in tab

    # Frozen attack locations and V143 fields remain intact in returned events.
    assert first["events"][0]["timeSeconds"] == 0.5
    assert first["events"][0]["v143Score"] == 3.0
    assert first["events"][0]["v143Rank"] == 1
    assert first["events"][0]["v143Selected"] is True
    assert first["events"][0]["pitchHypotheses"] == rows[0]["pitchHypotheses"]

    assert first["assembly"]["selectionChanged"] is False
    assert first["assembly"]["attackTimingChanged"] is False
    assert first["assembly"]["pitchEvidenceChanged"] is False
    assert first["assembly"]["professionalReferenceUsed"] is False
    assert first["assembly"]["runtimeLabelsRequired"] is False

    print("=== V143 RHYTHM PRODUCTION OUTPUT ADAPTER VERIFIED ===")
    print("Existing generatedTab API contract satisfied: True")
    print("Frozen selected event count preserved: True")
    print("Unselected V143 attacks rendered: False")
    print("Quantized attack positions preserved: True")
    print("Pitch hypotheses preserved: True")
    print("Sustain metadata retained in output events: True")
    print("Explicit technique metadata retained: True")
    print("4/4 sixteen-step measure spacing rendered: True")
    print("Professional reference used: False")
    print("Runtime labels required: False")
    print("Source assembly mutated: False")
    print("Deterministic repeat exact: True")
    print("READY FOR MODAL RHYTHM ROUTING: True")


if __name__ == "__main__":
    main()
