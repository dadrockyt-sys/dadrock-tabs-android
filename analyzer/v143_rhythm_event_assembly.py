from __future__ import annotations

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
            "techniques": list(self.techniques),
            "events": [deepcopy(event) for event in self.events],
            "assembly": {
                "version": 1,
                "mode": "v143-selection-note-map-sustain-technique",
                "selectionChanged": False,
                "attackTimingChanged": False,
                "pitchEvidenceChanged": False,
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
    attack timing, and pitch hypotheses remain untouched. String/fret mapping is
    added first, then reference-free sustain duration and explicit-only technique
    evidence are appended.
    """
    if not isinstance(rhythm_result, ReferenceFreeRhythmResult):
        raise TypeError("rhythm_result must be ReferenceFreeRhythmResult")

    mapped = map_selected_v143_rows(rhythm_result.rows)
    enriched = enrich_mapped_rhythm_events(
        mapped,
        tempo_bpm=float(rhythm_result.timing.tempo_bpm),
    )

    if len(mapped) != rhythm_result.selected_count:
        raise RuntimeError(
            "Note mapper changed frozen V143 selection count: "
            f"{rhythm_result.selected_count} -> {len(mapped)}"
        )
    if len(enriched) != len(mapped):
        raise RuntimeError(
            "Sustain/technique enricher changed mapped event count: "
            f"{len(mapped)} -> {len(enriched)}"
        )

    frozen_by_location = {
        (int(row["measure"]), int(row["step"])): row
        for row in rhythm_result.selected_rows
    }
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

    for event in enriched:
        key = (int(event["measure"]), int(event["step"]))
        frozen = frozen_by_location.get(key)
        if frozen is None:
            raise RuntimeError(f"Assembly emitted non-selected V143 location: {key}")
        for field in protected_fields:
            if field in frozen and event.get(field) != frozen.get(field):
                raise RuntimeError(
                    f"Assembly changed frozen V143 field {field!r} at {key}"
                )
        if event.get("v143Selected") is not True:
            raise RuntimeError(f"Assembly emitted unselected V143 event at {key}")

    return RhythmEventAssemblyResult(
        source=rhythm_result,
        events=tuple(deepcopy(event) for event in enriched),
    )


__all__ = [
    "RhythmEventAssemblyResult",
    "assemble_rhythm_events",
]
