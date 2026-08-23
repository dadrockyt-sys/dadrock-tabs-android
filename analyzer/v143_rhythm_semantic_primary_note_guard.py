from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


AUDIO_BEND_SOURCE = "reference-free-audio-pitch-contour"
AUDIO_LEGATO_SOURCE = "reference-free-audio-legato-evidence"
AUDIO_SEMANTIC_SOURCES = frozenset({AUDIO_BEND_SOURCE, AUDIO_LEGATO_SOURCE})

BEND_FIELDS = (
    "bendSemitones",
    "bendTargetMidi",
    "bendTargetFret",
    "bendRelease",
    "bendEvidence",
)
LEGATO_SOURCE_FIELDS = (
    "legatoTargetEventIndex",
    "legatoTargetFret",
    "legatoTargetMidi",
    "legatoEvidence",
)
LEGATO_TARGET_FIELDS = (
    "legatoContinuationFromEventIndex",
    "legatoContinuationType",
)


@dataclass(frozen=True)
class SemanticGuardDiagnostics:
    event_count: int
    primary_event_count: int
    secondary_event_count: int
    stripped_secondary_bends: int
    stripped_secondary_legato: int
    stripped_invalid_primary_legato: int
    stripped_audio_technique_labels: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "eventCount": int(self.event_count),
            "primaryEventCount": int(self.primary_event_count),
            "secondaryEventCount": int(self.secondary_event_count),
            "strippedSecondaryBends": int(self.stripped_secondary_bends),
            "strippedSecondaryLegato": int(self.stripped_secondary_legato),
            "strippedInvalidPrimaryLegato": int(self.stripped_invalid_primary_legato),
            "strippedAudioTechniqueLabels": int(self.stripped_audio_technique_labels),
            "eventCountChanged": False,
            "attackTimingChanged": False,
            "pitchChanged": False,
            "stringFretChanged": False,
            "referenceFree": True,
            "runtimeLabelsRequired": False,
            "productionModified": False,
        }


def _mapping(event: Mapping[str, Any]) -> Mapping[str, Any]:
    value = event.get("noteMapping")
    return value if isinstance(value, Mapping) else {}


def _is_primary(event: Mapping[str, Any]) -> bool:
    mapping = _mapping(event)
    marker = mapping.get("primaryTechniqueNote")
    if marker is not None:
        return marker is True

    # Backward-compatible isolated verification: monophonic events have no
    # secondary chord tone to inherit an attack-level technique from.
    try:
        chord_count = int(mapping.get("chordNoteCount", 1))
    except (TypeError, ValueError):
        chord_count = 1
    return chord_count <= 1


def _strip_fields(event: dict[str, Any], fields: Sequence[str]) -> bool:
    changed = False
    for field in fields:
        if field in event:
            event.pop(field, None)
            changed = True
    return changed


def _strip_audio_techniques(event: dict[str, Any]) -> int:
    techniques = event.get("rhythmTechniques")
    if not isinstance(techniques, list):
        return 0

    kept: list[Any] = []
    removed = 0
    for item in techniques:
        if not isinstance(item, Mapping):
            kept.append(deepcopy(item))
            continue
        source = str(item.get("source") or "")
        if source in AUDIO_SEMANTIC_SOURCES:
            removed += 1
            continue
        kept.append(deepcopy(item))
    event["rhythmTechniques"] = kept
    return removed


def guard_semantic_events(
    events: Iterable[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], SemanticGuardDiagnostics]:
    """Keep audio-derived technique semantics on the mapped primary note only.

    The polyphonic mapper already records which rendered note owns attack-level
    technique semantics through noteMapping.primaryTechniqueNote. Downstream bend
    and legato detectors operate on individual rendered notes, so without this
    guard a harmonic/secondary chord tone can inherit a false bend or become a
    false legato endpoint. This guard changes annotation only: it never adds,
    removes, retimes, repitches, or remaps a rendered note.
    """
    guarded = [deepcopy(dict(event)) for event in events]
    primary = [_is_primary(event) for event in guarded]

    stripped_secondary_bends = 0
    stripped_secondary_legato = 0
    stripped_invalid_primary_legato = 0
    stripped_labels = 0

    # First remove audio semantics from every mapped secondary chord tone.
    for index, event in enumerate(guarded):
        if primary[index]:
            continue
        if _strip_fields(event, BEND_FIELDS):
            stripped_secondary_bends += 1
        if _strip_fields(event, LEGATO_SOURCE_FIELDS + LEGATO_TARGET_FIELDS):
            stripped_secondary_legato += 1
        stripped_labels += _strip_audio_techniques(event)
        event["semanticPrimaryNoteGuard"] = {
            "version": 1,
            "primaryTechniqueNote": False,
            "audioDerivedSemanticsAllowed": False,
            "referenceFree": True,
        }

    # A primary source event may have been linked by the legacy legato evidence
    # pass to a secondary chord tone. Remove that relationship rather than
    # silently redirecting it to another note.
    for index, event in enumerate(guarded):
        if not primary[index]:
            continue
        raw_target = event.get("legatoTargetEventIndex")
        if raw_target is None:
            event["semanticPrimaryNoteGuard"] = {
                "version": 1,
                "primaryTechniqueNote": True,
                "audioDerivedSemanticsAllowed": True,
                "referenceFree": True,
            }
            continue
        try:
            target_index = int(raw_target)
        except (TypeError, ValueError):
            target_index = -1
        target_is_primary = (
            0 <= target_index < len(guarded)
            and primary[target_index]
        )
        if not target_is_primary:
            if _strip_fields(event, LEGATO_SOURCE_FIELDS):
                stripped_invalid_primary_legato += 1
            stripped_labels += _strip_audio_techniques(event)
        event["semanticPrimaryNoteGuard"] = {
            "version": 1,
            "primaryTechniqueNote": True,
            "audioDerivedSemanticsAllowed": True,
            "referenceFree": True,
        }

    # Remove orphan continuation markers whose source link no longer exists.
    valid_links: set[tuple[int, int]] = set()
    for source_index, event in enumerate(guarded):
        raw_target = event.get("legatoTargetEventIndex")
        try:
            target_index = int(raw_target)
        except (TypeError, ValueError):
            continue
        if 0 <= target_index < len(guarded):
            valid_links.add((source_index, target_index))

    for target_index, event in enumerate(guarded):
        raw_source = event.get("legatoContinuationFromEventIndex")
        if raw_source is None:
            continue
        try:
            source_index = int(raw_source)
        except (TypeError, ValueError):
            source_index = -1
        if (source_index, target_index) not in valid_links:
            _strip_fields(event, LEGATO_TARGET_FIELDS)

    diagnostics = SemanticGuardDiagnostics(
        event_count=len(guarded),
        primary_event_count=sum(1 for value in primary if value),
        secondary_event_count=sum(1 for value in primary if not value),
        stripped_secondary_bends=stripped_secondary_bends,
        stripped_secondary_legato=stripped_secondary_legato,
        stripped_invalid_primary_legato=stripped_invalid_primary_legato,
        stripped_audio_technique_labels=stripped_labels,
    )
    return guarded, diagnostics


def guard_rhythm_assembly(assembly: Any) -> Any:
    """Assembly adapter kept isolated until a new approved-audio freeze is authorized."""
    from v143_rhythm_event_assembly import RhythmEventAssemblyResult

    if not isinstance(assembly, RhythmEventAssemblyResult):
        raise TypeError("assembly must be RhythmEventAssemblyResult")
    guarded, diagnostics = guard_semantic_events(assembly.events)
    result = RhythmEventAssemblyResult(
        source=assembly.source,
        events=tuple(guarded),
    )
    # Attribute assignment is intentionally avoided on the frozen dataclass;
    # diagnostics are returned by the pure event-level API used by shadow gates.
    _ = diagnostics
    return result


__all__ = [
    "AUDIO_BEND_SOURCE",
    "AUDIO_LEGATO_SOURCE",
    "AUDIO_SEMANTIC_SOURCES",
    "SemanticGuardDiagnostics",
    "guard_semantic_events",
    "guard_rhythm_assembly",
]
