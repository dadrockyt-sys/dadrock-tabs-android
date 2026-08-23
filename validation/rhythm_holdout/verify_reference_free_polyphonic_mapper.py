#!/usr/bin/env python3
from __future__ import annotations

import sys
import types
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
ANALYZER = ROOT / "analyzer"
if str(ANALYZER) not in sys.path:
    sys.path.insert(0, str(ANALYZER))

from v143_rhythm_guitar_note_mapper import (  # noqa: E402
    MAX_CHORD_NOTES,
    map_selected_v143_rows,
    resolve_joint_chord_voicing,
)


def hypothesis(midi: int, amplitude: float, *, duration: float = 0.12) -> dict:
    return {
        "midi": int(midi),
        "sourceCount": 2,
        "eventCount": 2,
        "maxAmplitude": float(amplitude),
        "meanAmplitude": float(amplitude),
        "maxDuration": float(duration),
        "bestOnsetTime": 1.0,
        "bestOffsetTime": 1.0 + float(duration),
        "minGridError": 0.01,
    }


def row(
    measure: int,
    step: int,
    dominant_midi: int,
    hypotheses: list[dict],
    **extra,
) -> dict:
    payload = {
        "measure": int(measure),
        "step": int(step),
        "timeSeconds": float(measure) + float(step) / 16.0,
        "dominantMidi": int(dominant_midi),
        "pitchHypotheses": hypotheses,
        "v143Score": 0.91,
        "v143Rank": 1,
        "v143Selected": True,
    }
    payload.update(extra)
    return payload


def assert_true(value: bool, message: str) -> None:
    if not value:
        raise AssertionError(message)


def verify_mapper() -> None:
    single = row(1, 0, 52, [hypothesis(52, 0.80)])
    single_events = map_selected_v143_rows([single])
    assert_true(len(single_events) == 1, "single-note attack must stay single")
    assert_true(single_events[0]["midi"] == 52, "single-note MIDI changed")
    assert_true(
        single_events[0]["noteMapping"]["jointChordVoicingResolved"] is True,
        "single note must still have a resolved guitar position",
    )

    chord = row(
        2,
        4,
        40,
        [
            hypothesis(40, 0.80),
            hypothesis(47, 0.62),
            hypothesis(52, 0.56),
        ],
        palmMuted=True,
        bendSemitones=1.0,
    )
    chord_events = map_selected_v143_rows([chord])
    assert_true(
        {event["midi"] for event in chord_events} == {40, 47, 52},
        "strong simultaneous hypotheses were not retained",
    )
    assert_true(
        len({event["stringIndex"] for event in chord_events}) == 3,
        "polyphonic attack must occupy unique strings",
    )
    assert_true(
        all(event["measure"] == 2 and event["step"] == 4 for event in chord_events),
        "polyphonic expansion changed attack timing",
    )
    primary = next(event for event in chord_events if event["midi"] == 40)
    secondary = [event for event in chord_events if event["midi"] != 40]
    assert_true(primary.get("palmMuted") is True, "primary technique evidence was lost")
    assert_true(
        all("palmMuted" not in event and "bendSemitones" not in event for event in secondary),
        "attack-level techniques were multiplied across chord tones",
    )

    near_unison = row(
        3,
        8,
        57,
        [
            hypothesis(57, 0.70),
            hypothesis(58, 0.30),
            hypothesis(64, 0.50),
        ],
    )
    near_events = map_selected_v143_rows([near_unison])
    near_midis = {event["midi"] for event in near_events}
    assert_true(57 in near_midis and 64 in near_midis, "strong notes were dropped")
    assert_true(58 not in near_midis, "weak near-unison ambiguity was not suppressed")

    six_string = row(
        4,
        12,
        40,
        [
            hypothesis(40, 0.90),
            hypothesis(45, 0.85),
            hypothesis(50, 0.80),
            hypothesis(55, 0.75),
            hypothesis(59, 0.70),
            hypothesis(64, 0.65),
            hypothesis(67, 0.60),
        ],
    )
    six_events = map_selected_v143_rows([six_string])
    assert_true(len(six_events) <= MAX_CHORD_NOTES, "more than six notes were emitted")
    assert_true(any(event["midi"] == 40 for event in six_events), "dominant note was lost")
    assert_true(
        len({event["stringIndex"] for event in six_events}) == len(six_events),
        "overfull attack created duplicate strings",
    )

    voicing = resolve_joint_chord_voicing([40, 47, 52, 64])
    assert_true(voicing is not None, "known playable chord did not resolve")
    assert_true(
        len({position["stringIndex"] for position in voicing.values()}) == 4,
        "joint voicing did not use unique strings",
    )

    for event in chord_events + near_events + six_events:
        mapping = event["noteMapping"]
        assert_true(mapping["professionalReferenceUsed"] is False, "reference flag unsafe")
        assert_true(mapping["runtimeLabelsRequired"] is False, "runtime labels became required")


def verify_assembly() -> None:
    fake_pipeline = types.ModuleType("v143_reference_free_rhythm_pipeline")

    class ReferenceFreeRhythmResult:
        def __init__(self, rows: list[dict]):
            self.rows = tuple(rows)
            self.candidates = tuple(dict(item) for item in rows)
            self.timing = SimpleNamespace(tempo_bpm=120.0)

        @property
        def selected_rows(self):
            return tuple(item for item in self.rows if item.get("v143Selected") is True)

        @property
        def selected_count(self):
            return len(self.selected_rows)

        def to_dict(self):
            return {
                "timing": {
                    "tempoBpm": 120.0,
                    "timeSignature": "4/4",
                    "firstBeatInMeasure": 0,
                    "downbeatIndexMod4": 0,
                    "beatConfidence": 1.0,
                    "barConfidence": 1.0,
                    "beatTimes": [],
                },
                "candidateCount": len(self.candidates),
                "selectedCount": self.selected_count,
                "candidates": [dict(item) for item in self.candidates],
                "rows": [dict(item) for item in self.rows],
            }

    fake_pipeline.ReferenceFreeRhythmResult = ReferenceFreeRhythmResult
    sys.modules["v143_reference_free_rhythm_pipeline"] = fake_pipeline

    sys.modules.pop("v143_rhythm_event_assembly", None)
    from v143_rhythm_event_assembly import assemble_rhythm_events  # noqa: E402

    rows = [
        row(
            10,
            0,
            40,
            [hypothesis(40, 0.80), hypothesis(47, 0.60), hypothesis(52, 0.55)],
        ),
        row(10, 4, 55, [hypothesis(55, 0.75)]),
    ]
    result = assemble_rhythm_events(ReferenceFreeRhythmResult(rows))
    payload = result.to_dict()

    assert_true(result.selected_count == 2, "selected attack count changed")
    assert_true(result.note_count == 4, "polyphonic note count is wrong")
    assert_true(payload["selectedCount"] == 2, "payload selectedCount must count attacks")
    assert_true(payload["noteCount"] == 4, "payload noteCount must count rendered notes")
    assert_true(payload["assembly"]["polyphonicExpansion"] is True, "expansion not declared")
    assert_true(payload["assembly"]["selectionChanged"] is False, "selection changed")
    assert_true(payload["assembly"]["attackTimingChanged"] is False, "timing changed")
    assert_true(payload["assembly"]["pitchEvidenceChanged"] is False, "pitch evidence changed")
    assert_true(
        len({(event["measure"], event["step"]) for event in result.events}) == 2,
        "assembly changed frozen attack locations",
    )
    assert_true(
        len({(event["measure"], event["step"], event["stringIndex"]) for event in result.events})
        == len(result.events),
        "assembly emitted duplicate string occupancy",
    )


if __name__ == "__main__":
    verify_mapper()
    verify_assembly()
    print("reference-free polyphonic Rhythm mapper: PASS")
