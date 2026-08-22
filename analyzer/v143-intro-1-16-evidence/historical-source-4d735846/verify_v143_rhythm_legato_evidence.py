from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import numpy as np

from v143_rhythm_event_assembly import RhythmEventAssemblyResult
from v143_rhythm_legato_evidence import enrich_rhythm_assembly_with_legato


class FakeLegatoView:
    def __init__(self, name: str, scale: float = 1.0) -> None:
        self.source_name = name
        self.times = np.arange(0.80, 4.61, 0.02)
        self._energies: dict[int, np.ndarray] = {
            midi: np.full_like(self.times, 0.003, dtype=float)
            for midi in range(55, 70)
        }
        self._onsets = {
            1.00: 1.00,
            1.18: 0.28,
            2.00: 0.96,
            2.18: 0.26,
            3.00: 0.92,
            3.30: 0.34,
            4.00: 0.90,
            4.18: 0.95,
        }

        def peak(midi: int, centre: float, amount: float, width: float = 0.055) -> None:
            self._energies[midi] += scale * amount * np.exp(
                -((self.times - centre) / width) ** 2
            )

        # Hammer-on: 5h7, target pitch arrives with weak re-attack and no
        # continuous semitone path.
        peak(60, 1.02, 0.26)
        peak(62, 1.20, 0.20)

        # Pull-off: 7p5, again with weak target re-attack.
        peak(62, 2.02, 0.25)
        peak(60, 2.20, 0.19)

        # Slide: 5/9, with strong intermediate pitch path and weak target pick.
        peak(60, 3.02, 0.23)
        peak(61, 3.08, 0.13, 0.075)
        peak(62, 3.15, 0.14, 0.075)
        peak(63, 3.22, 0.14, 0.075)
        peak(64, 3.31, 0.21, 0.070)

        # Ordinary re-picked move: must not become legato.
        peak(65, 4.02, 0.23)
        peak(67, 4.20, 0.22)

    def energy(self, midi: int) -> np.ndarray:
        return self._energies.get(
            int(midi),
            np.full_like(self.times, 0.003, dtype=float),
        )

    def onset_strength(self, time_seconds: float, radius: float = 0.045) -> float:
        candidates = [
            strength
            for time_value, strength in self._onsets.items()
            if abs(float(time_seconds) - time_value) <= radius
        ]
        return max(candidates) if candidates else 0.0


def event(
    measure: int,
    step: int,
    time_seconds: float,
    string_index: int,
    fret: int,
    midi: int,
    rank: int,
) -> dict[str, Any]:
    return {
        "measure": measure,
        "step": step,
        "timeSeconds": time_seconds,
        "stringIndex": string_index,
        "fret": fret,
        "midi": midi,
        "dominantMidi": midi,
        "v143Selected": True,
        "v143Score": 0.95 - rank * 0.01,
        "v143Rank": rank,
        "pitchHypotheses": [{"midi": midi, "sourceCount": 2}],
        "rhythmTechniques": [],
    }


def main() -> None:
    original_events = [
        event(1, 0, 1.00, 0, 5, 60, 1),
        event(1, 2, 1.18, 0, 7, 62, 2),
        event(2, 0, 2.00, 1, 7, 62, 3),
        event(2, 2, 2.18, 1, 5, 60, 4),
        event(3, 0, 3.00, 2, 5, 60, 5),
        event(3, 3, 3.30, 2, 9, 64, 6),
        event(4, 0, 4.00, 3, 10, 65, 7),
        event(4, 2, 4.18, 3, 12, 67, 8),
    ]
    untouched = deepcopy(original_events)
    assembly = RhythmEventAssemblyResult(
        source=object(),
        events=tuple(original_events),
    )

    created_views: list[str] = []

    def fake_builder(path: str | Path) -> FakeLegatoView:
        name = Path(path).name
        created_views.append(name)
        return FakeLegatoView(name, 1.0 if len(created_views) == 1 else 0.93)

    enriched = enrich_rhythm_assembly_with_legato(
        assembly,
        carrier_stem_paths=("direct-guitar.wav", "cascade-guitar.wav"),
        view_builder=fake_builder,
    )
    events = list(enriched.events)

    technique_by_source = {}
    for index, item in enumerate(events):
        evidence = item.get("legatoEvidence")
        if isinstance(evidence, dict):
            technique_by_source[index] = str(evidence.get("type") or "")

    expected = {
        0: "hammer-on",
        2: "pull-off",
        4: "slide-up",
    }
    exact_techniques = technique_by_source == expected
    repick_rejected = 6 not in technique_by_source
    strict_two_view = all(
        (events[index].get("legatoEvidence") or {}).get("viewAgreement") == 2
        and (events[index].get("legatoEvidence") or {}).get("requiredViewAgreement") == 2
        and (events[index].get("legatoEvidence") or {}).get("consensusPassed") is True
        for index in expected
    )
    continuations_linked = (
        events[1].get("legatoContinuationFromEventIndex") == 0
        and events[3].get("legatoContinuationFromEventIndex") == 2
        and events[5].get("legatoContinuationFromEventIndex") == 4
    )
    frozen_fields = (
        "measure",
        "step",
        "timeSeconds",
        "stringIndex",
        "fret",
        "midi",
        "dominantMidi",
        "v143Selected",
        "v143Score",
        "v143Rank",
        "pitchHypotheses",
    )
    frozen_preserved = all(
        all(events[index].get(field) == untouched[index].get(field) for field in frozen_fields)
        for index in range(len(events))
    )
    input_unchanged = original_events == untouched
    two_views_consumed = created_views == ["direct-guitar.wav", "cascade-guitar.wav"]
    reference_free = all(
        (events[index].get("legatoEvidence") or {}).get("professionalReferenceUsed") is False
        and (events[index].get("legatoEvidence") or {}).get("runtimeLabelsRequired") is False
        for index in expected
    )

    repeat_views: list[str] = []

    def repeat_builder(path: str | Path) -> FakeLegatoView:
        name = Path(path).name
        repeat_views.append(name)
        return FakeLegatoView(name, 1.0 if len(repeat_views) == 1 else 0.93)

    repeated = enrich_rhythm_assembly_with_legato(
        assembly,
        carrier_stem_paths=("direct-guitar.wav", "cascade-guitar.wav"),
        view_builder=repeat_builder,
    )
    deterministic = repeated.events == enriched.events

    checks = {
        "Hammer-on detected": technique_by_source.get(0) == "hammer-on",
        "Pull-off detected": technique_by_source.get(2) == "pull-off",
        "Slide-up detected": technique_by_source.get(4) == "slide-up",
        "Ordinary re-pick rejected": repick_rejected,
        "Exact expected technique set": exact_techniques,
        "Strict two-view consensus": strict_two_view,
        "Continuation events linked": continuations_linked,
        "Frozen V143 fields preserved": frozen_preserved,
        "Two carrier views consumed": two_views_consumed,
        "Professional reference used": False,
        "Runtime labels required": False,
        "Reference-free evidence metadata": reference_free,
        "Input events unchanged": input_unchanged,
        "Deterministic repeat exact": deterministic,
    }
    ready = all(
        (
            exact_techniques,
            repick_rejected,
            strict_two_view,
            continuations_linked,
            frozen_preserved,
            two_views_consumed,
            reference_free,
            input_unchanged,
            deterministic,
        )
    )

    print("=== V143 REFERENCE-FREE RHYTHM LEGATO EVIDENCE VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR REAL-AUDIO LEGATO SMOKE: {ready}")
    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
