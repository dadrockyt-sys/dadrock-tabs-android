#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass

from v143_rhythm_sustain_consensus_shadow import annotate_sustain_shadow


@dataclass
class FakeView:
    source_name: str
    times: list[float]
    energy_by_midi: dict[int, list[float]]

    def energy(self, midi: int) -> list[float]:
        return self.energy_by_midi[int(midi)]


def _curve(times: list[float], active_until: float) -> list[float]:
    values: list[float] = []
    for t in times:
        if t < -0.03:
            values.append(0.05)
        elif t <= 0.08:
            values.append(1.00)
        elif t <= active_until:
            values.append(0.52)
        else:
            values.append(0.06)
    return values


def main() -> None:
    times = [round(-0.12 + 0.02 * index, 4) for index in range(70)]
    view_a = FakeView("a", times, {57: _curve(times, 0.64), 59: _curve(times, 0.22)})
    view_b = FakeView("b", times, {57: _curve(times, 0.60), 59: _curve(times, 0.20)})

    events = [
        {
            "measure": 1,
            "step": 0,
            "timeSeconds": 0.0,
            "midi": 57,
            "stringIndex": 2,
            "fret": 2,
            "rhythmSustain": {"durationSeconds": 0.12, "durationSteps": 1},
        },
        {
            "measure": 1,
            "step": 8,
            "timeSeconds": 0.80,
            "midi": 59,
            "stringIndex": 2,
            "fret": 4,
            "rhythmSustain": {"durationSeconds": 0.10, "durationSteps": 1},
        },
    ]

    annotated, report = annotate_sustain_shadow(
        events,
        [view_a, view_b],
        tempo_bpm=120.0,
    )

    assert len(annotated) == len(events)
    for before, after in zip(events, annotated):
        for field in ("measure", "step", "timeSeconds", "midi", "stringIndex", "fret"):
            assert before[field] == after[field]
        assert before["rhythmSustain"] == after["rhythmSustain"]

    first = annotated[0]["rhythmSustainShadow"]
    assert first["viewAgreement"] == 2
    assert first["requiredViewAgreement"] == 2
    assert first["durationSeconds"] <= 0.79
    assert first["durationSeconds"] >= 0.50
    assert first["durationSteps"] >= 4
    assert first["tieOrLetRingInferred"] is False

    assert report["annotatedEventCount"] >= 1
    assert report["longerThanDetectorCount"] >= 1
    assert report["eventCountChanged"] is False
    assert report["attackTimingChanged"] is False
    assert report["pitchChanged"] is False
    assert report["tieOrLetRingInferred"] is False
    assert report["referenceFree"] is True
    assert report["runtimeLabelsRequired"] is False
    assert report["productionModified"] is False

    print("V143 rhythm sustain consensus shadow proof passed")
    print(report)


if __name__ == "__main__":
    main()
