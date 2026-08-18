from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from v143_rhythm_bend_evidence import enrich_rhythm_assembly_with_audio_bends
from v143_rhythm_event_assembly import RhythmEventAssemblyResult
from v143_rhythm_output_adapter import render_event_token


class FakeEnergyView:
    def __init__(self, name: str, scale: float = 1.0) -> None:
        self.source_name = name
        self.times = np.arange(0.80, 2.01, 0.02)
        self._energies: dict[int, np.ndarray] = {}
        for midi in (57, 58, 59, 60):
            self._energies[midi] = np.full_like(self.times, 0.003, dtype=float)

        # Synthetic but source-agnostic continuous full bend: MIDI 57 rises
        # through 58 to 59, then releases to the source pitch.
        self._energies[57] += scale * (
            0.20 * np.exp(-((self.times - 1.04) / 0.08) ** 2)
            + 0.15 * np.exp(-((self.times - 1.58) / 0.10) ** 2)
        )
        self._energies[58] += scale * (
            0.11 * np.exp(-((self.times - 1.18) / 0.07) ** 2)
        )
        self._energies[59] += scale * (
            0.22 * np.exp(-((self.times - 1.34) / 0.09) ** 2)
        )
        self._energies[60] += scale * (
            0.025 * np.exp(-((self.times - 1.42) / 0.09) ** 2)
        )

    def energy(self, midi: int) -> np.ndarray:
        return self._energies.get(
            int(midi),
            np.full_like(self.times, 0.003, dtype=float),
        )


def main() -> None:
    original_event: dict[str, Any] = {
        "measure": 1,
        "step": 4,
        "timeSeconds": 1.0,
        "midi": 57,
        "dominantMidi": 57,
        "stringIndex": 2,
        "fret": 2,
        "v143Selected": True,
        "v143Score": 0.91,
        "v143Rank": 1,
        "pitchHypotheses": [{"midi": 57}],
        "rhythmSustain": {
            "durationSeconds": 0.70,
            "durationSteps": 6,
            "tier": "long",
        },
        "rhythmTechniques": [],
    }
    untouched_copy = dict(original_event)

    assembly = RhythmEventAssemblyResult(
        source=object(),
        events=(original_event,),
    )

    created_views: list[str] = []

    def fake_view_builder(path: str | Path) -> FakeEnergyView:
        name = Path(path).name
        created_views.append(name)
        return FakeEnergyView(name, 1.0 if len(created_views) == 1 else 0.93)

    enriched = enrich_rhythm_assembly_with_audio_bends(
        assembly,
        carrier_stem_paths=("direct-guitar.wav", "cascade-guitar.wav"),
        view_builder=fake_view_builder,
    )

    event = dict(enriched.events[0])
    technique_types = {
        str(item.get("type"))
        for item in event.get("rhythmTechniques", [])
        if isinstance(item, dict)
    }

    frozen_location_preserved = (
        event.get("measure") == original_event["measure"]
        and event.get("step") == original_event["step"]
        and event.get("timeSeconds") == original_event["timeSeconds"]
    )
    frozen_pitch_preserved = (
        event.get("midi") == original_event["midi"]
        and event.get("dominantMidi") == original_event["dominantMidi"]
        and event.get("pitchHypotheses") == original_event["pitchHypotheses"]
    )
    frozen_selection_preserved = (
        event.get("v143Selected") is True
        and event.get("v143Score") == original_event["v143Score"]
        and event.get("v143Rank") == original_event["v143Rank"]
    )
    two_independent_views_consumed = created_views == [
        "direct-guitar.wav",
        "cascade-guitar.wav",
    ]
    full_bend_detected = event.get("bendSemitones") == 2
    target_pitch_preserved = event.get("bendTargetMidi") == 59
    target_fret_correct = event.get("bendTargetFret") == 4
    release_detected = event.get("bendRelease") is True
    bend_technique_present = "bend" in technique_types
    bend_release_present = "bend-release" in technique_types
    notation_exact = render_event_token(event) == "2b4r2"
    reference_free = (
        event.get("bendEvidence", {}).get("professionalReferenceUsed") is False
        and event.get("bendEvidence", {}).get("runtimeLabelsRequired") is False
    )
    cross_view_agreement = event.get("bendEvidence", {}).get("viewAgreement") == 2
    input_mutated = original_event != untouched_copy

    repeat_views: list[str] = []

    def repeat_builder(path: str | Path) -> FakeEnergyView:
        name = Path(path).name
        repeat_views.append(name)
        return FakeEnergyView(name, 1.0 if len(repeat_views) == 1 else 0.93)

    repeated = enrich_rhythm_assembly_with_audio_bends(
        assembly,
        carrier_stem_paths=("direct-guitar.wav", "cascade-guitar.wav"),
        view_builder=repeat_builder,
    )
    deterministic_repeat = repeated.events == enriched.events

    checks = {
        "Frozen attack location preserved": frozen_location_preserved,
        "Frozen pitch evidence preserved": frozen_pitch_preserved,
        "Frozen V143 selection preserved": frozen_selection_preserved,
        "Two independent carrier views consumed": two_independent_views_consumed,
        "Whole-step bend detected": full_bend_detected,
        "Bend target MIDI preserved": target_pitch_preserved,
        "Bend target fret calculated": target_fret_correct,
        "Bend release detected": release_detected,
        "Bend technique appended": bend_technique_present,
        "Bend-release technique appended": bend_release_present,
        "Professional bend notation exact": notation_exact,
        "Cross-view evidence agreement": cross_view_agreement,
        "Professional reference used": False,
        "Runtime labels required": False,
        "Reference-free evidence metadata": reference_free,
        "Input event mutated": input_mutated,
        "Deterministic repeat exact": deterministic_repeat,
    }

    ready = all(
        (
            frozen_location_preserved,
            frozen_pitch_preserved,
            frozen_selection_preserved,
            two_independent_views_consumed,
            full_bend_detected,
            target_pitch_preserved,
            target_fret_correct,
            release_detected,
            bend_technique_present,
            bend_release_present,
            notation_exact,
            cross_view_agreement,
            reference_free,
            not input_mutated,
            deterministic_repeat,
        )
    )

    print("=== V143 REFERENCE-FREE RHYTHM BEND EVIDENCE VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR REAL GOMYWAY BEND SMOKE: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
