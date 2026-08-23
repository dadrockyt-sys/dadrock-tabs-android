from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from v143_reference_free_rhythm_pipeline import ReferenceFreeRhythmResult
from v143_rhythm_guitar_note_mapper import map_selected_v143_rows
from v143_rhythm_sustain_technique_enricher import enrich_mapped_rhythm_events


@dataclass(frozen=True)
class RhythmEventAssemblyResult:
    """Final reference-free rhythm-guitar events after frozen V143 selection."""

    source: ReferenceFreeRhythmResult
    events: tuple[dict[str, Any], ...]

    @property
    def selected_count(self) -> int:
        """Number of frozen V143 rhythmic attack slots."""
        return int(self.source.selected_count)

    @property
    def note_count(self) -> int:
        """Number of rendered guitar notes after reference-free polyphony recovery."""
        return len(self.events)

    @property
    def techniques(self) -> tuple[str, ...]:
        values = {
            str(item["type"])
            for event in self.events
            for item in event.get("rhythmTechniques", [])
            if item.get("type")
        }
        return tuple(sorted(values))

    def to_dict(self) -> dict[str, Any]:
        source_payload = self.source.to_dict()
        return {
            "timing": deepcopy(source_payload["timing"]),
            "candidateCount": int(source_payload["candidateCount"]),
            "selectedCount": self.selected_count,
            "noteCount": self.note_count,
            "techniques": list(self.techniques),
            "events": [deepcopy(event) for event in self.events],
            "assembly": {
                "version": 2,
                "mode": "v143-selection-polyphonic-note-map-sustain-technique",
                "selectionChanged": False,
                "attackTimingChanged": False,
                "pitchEvidenceChanged": False,
                "polyphonicExpansion": self.note_count > self.selected_count,
                "selectedAttackCount": self.selected_count,
                "renderNoteCount": self.note_count,
                "professionalReferenceUsed": False,
                "runtimeLabelsRequired": False,
            },
        }


def assemble_rhythm_events(
    rhythm_result: ReferenceFreeRhythmResult,
) -> RhythmEventAssemblyResult:
    """
    Compose the frozen V143 rhythm boundary into final rhythm-guitar events.

    The assembly is strictly downstream: V143 score/rank/selection, quantized
    attack timing, and source pitch hypotheses remain untouched. A selected
    attack can now map to multiple strong reference-free chord tones, but every
    rendered note must still trace to that exact frozen attack and one of its
    original pitch hypotheses.
    """
    if not isinstance(rhythm_result, ReferenceFreeRhythmResult):
        raise TypeError("rhythm_result must be ReferenceFreeRhythmResult")

    mapped = map_selected_v143_rows(rhythm_result.rows)
    enriched = enrich_mapped_rhythm_events(
        mapped,
        tempo_bpm=float(rhythm_result.timing.tempo_bpm),
    )

    if len(enriched) != len(mapped):
        raise RuntimeError(
            "Sustain/technique enricher changed mapped note count: "
            f"{len(mapped)} -> {len(enriched)}"
        )

    frozen_by_location = {
        (int(row["measure"]), int(row["step"])): row
        for row in rhythm_result.selected_rows
    }
    if len(frozen_by_location) != rhythm_result.selected_count:
        raise RuntimeError(
            "Frozen V143 selection contains duplicate measure/step attack slots"
        )

    protected_fields = (
        "measure",
        "step",
        "timeSeconds",
        "dominantMidi",
        "pitchHypotheses",
        "v143Score",
        "v143Rank",
        "v143Selected",
    )
    emitted_locations: Counter[tuple[int, int]] = Counter()
    emitted_strings: set[tuple[int, int, int]] = set()

    for event in enriched:
        key = (int(event["measure"]), int(event["step"]))
        frozen = frozen_by_location.get(key)
        if frozen is None:
            raise RuntimeError(f"Assembly emitted non-selected V143 location: {key}")

        emitted_locations[key] += 1
        string_key = (key[0], key[1], int(event["stringIndex"]))
        if string_key in emitted_strings:
            raise RuntimeError(
                "Assembly emitted multiple notes on one guitar string at "
                f"measure {key[0]}, step {key[1]}, "
                f"string {int(event['stringIndex'])}"
            )
        emitted_strings.add(string_key)

        for field in protected_fields:
            if field in frozen and event.get(field) != frozen.get(field):
                raise RuntimeError(
                    f"Assembly changed frozen V143 field {field!r} at {key}"
                )
        if event.get("v143Selected") is not True:
            raise RuntimeError(f"Assembly emitted unselected V143 event at {key}")

        source_midis = {
            int(item["midi"])
            for item in frozen.get("pitchHypotheses") or []
            if item.get("midi") is not None
        }
        event_midi = int(event["midi"])
        if event_midi not in source_midis:
            raise RuntimeError(
                f"Assembly invented MIDI {event_midi} outside frozen "
                f"pitch hypotheses at {key}"
            )

        mapping = event.get("noteMapping") or {}
        if mapping.get("version") != 2:
            raise RuntimeError(f"Assembly received non-v2 note mapping at {key}")
        if mapping.get("jointChordVoicingResolved") is not True:
            raise RuntimeError(f"Assembly received unresolved chord voicing at {key}")
        if mapping.get("professionalReferenceUsed") is not False:
            raise RuntimeError(f"Assembly received reference-dependent mapping at {key}")
        if mapping.get("runtimeLabelsRequired") is not False:
            raise RuntimeError(f"Assembly received runtime-label mapping at {key}")

    missing_locations = sorted(
        set(frozen_by_location).difference(emitted_locations)
    )
    if missing_locations:
        raise RuntimeError(
            "Note mapper dropped frozen V143 selected attacks: "
            f"{missing_locations[:8]}"
        )

    extra_locations = sorted(
        set(emitted_locations).difference(frozen_by_location)
    )
    if extra_locations:
        raise RuntimeError(
            "Note mapper emitted non-selected attack locations: "
            f"{extra_locations[:8]}"
        )

    for key, frozen in frozen_by_location.items():
        if emitted_locations[key] < 1:
            raise RuntimeError(f"Selected V143 attack emitted no notes at {key}")
        dominant_midi = int(frozen["dominantMidi"])
        if not any(
            int(event["measure"]) == key[0]
            and int(event["step"]) == key[1]
            and int(event["midi"]) == dominant_midi
            for event in enriched
        ):
            raise RuntimeError(
                f"Selected V143 attack lost frozen dominant MIDI "
                f"{dominant_midi} at {key}"
            )

    return RhythmEventAssemblyResult(
        source=rhythm_result,
        events=tuple(deepcopy(event) for event in enriched),
    )


__all__ = [
    "RhythmEventAssemblyResult",
    "assemble_rhythm_events",
]
