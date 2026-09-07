from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from v143_rhythm_guitar_note_mapper import MAX_FRET, OPEN_MIDI_HIGH_TO_LOW


@dataclass(frozen=True)
class PreExportValidationDiagnostics:
    event_count: int
    attack_count: int
    multi_note_attack_count: int
    maximum_chord_size: int
    recovered_secondary_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "eventCount": int(self.event_count),
            "attackCount": int(self.attack_count),
            "multiNoteAttackCount": int(self.multi_note_attack_count),
            "maximumChordSize": int(self.maximum_chord_size),
            "recoveredSecondaryCount": int(self.recovered_secondary_count),
            "uniqueSimultaneousStrings": True,
            "legalStandardTuningStringFretMidi": True,
            "primaryPreserved": True,
            "noUnobservedRecoveredMidi": True,
            "duplicateNoteIdentityCount": 0,
            "stableEventOrder": True,
            "referenceFree": True,
            "professionalReferenceUsed": False,
            "runtimeLabelsRequired": False,
        }


def _integer(event: Mapping[str, Any], key: str) -> int:
    try:
        return int(event[key])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Missing or invalid integer field {key}") from exc


def _mapping(event: Mapping[str, Any]) -> Mapping[str, Any]:
    value = event.get("noteMapping")
    return value if isinstance(value, Mapping) else {}


def _observed_midis(event: Mapping[str, Any]) -> set[int]:
    values: set[int] = set()
    raw = event.get("pitchHypotheses")
    if not isinstance(raw, list):
        return values
    for item in raw:
        if not isinstance(item, Mapping) or item.get("midi") is None:
            continue
        try:
            values.add(int(item["midi"]))
        except (TypeError, ValueError):
            continue
    return values


def _recovery_hypothesis(
    event: Mapping[str, Any],
    midi: int,
) -> Mapping[str, Any] | None:
    raw = event.get("pitchHypotheses")
    if not isinstance(raw, list):
        return None
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        try:
            item_midi = int(item.get("midi"))
        except (TypeError, ValueError):
            continue
        if item_midi == int(midi):
            return item
    return None


def validate_v143_preexport_events(
    events: Iterable[Mapping[str, Any]],
    *,
    require_event_index: bool = True,
    require_stable_order: bool = True,
) -> PreExportValidationDiagnostics:
    """Fail closed on deterministic score-structure invariants before export.

    This validator is deliberately model-free. It checks only already-constructed
    score events, standard-tuning playability, attack-group identity and serialized
    provenance. It never consults a scorer, reference transcription, song metadata,
    model output probabilities, or external labels.
    """
    copied = [dict(event) for event in events]
    if not copied:
        raise ValueError("Pre-export validation requires at least one event")

    seen_identities: set[tuple[int, int, int, int, int]] = set()
    ordered_keys: list[tuple[int, int, int, int, int]] = []
    by_attack: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    recovered_count = 0

    for index, event in enumerate(copied):
        measure = _integer(event, "measure")
        step = _integer(event, "step")
        string_index = _integer(event, "stringIndex")
        fret = _integer(event, "fret")
        midi = _integer(event, "midi")

        if measure < 1:
            raise ValueError(f"Invalid measure at event {index}: {measure}")
        if not 0 <= step < 16:
            raise ValueError(
                f"Invalid 16th-note step at event {index}: {step}"
            )
        if not 0 <= string_index < len(OPEN_MIDI_HIGH_TO_LOW):
            raise ValueError(
                f"Invalid string index at event {index}: {string_index}"
            )
        if not 0 <= fret <= MAX_FRET:
            raise ValueError(f"Invalid fret at event {index}: {fret}")

        expected_midi = int(OPEN_MIDI_HIGH_TO_LOW[string_index]) + fret
        if midi != expected_midi:
            raise ValueError(
                f"Illegal standard-tuning mapping at event {index}: "
                f"string={string_index} fret={fret} midi={midi} "
                f"expected={expected_midi}"
            )

        identity = (measure, step, string_index, fret, midi)
        if identity in seen_identities:
            raise ValueError(
                f"Duplicate note identity before export: {identity}"
            )
        seen_identities.add(identity)
        ordered_keys.append(identity)
        by_attack[(measure, step)].append(event)

        if require_event_index:
            event_index = _integer(event, "eventIndex")
            if event_index != index:
                raise ValueError(
                    "Unstable eventIndex before export: "
                    f"listIndex={index} eventIndex={event_index}"
                )

        observed = _observed_midis(event)
        if observed and midi not in observed:
            raise ValueError(
                f"Rendered MIDI {midi} is absent from serialized observed "
                f"hypotheses at {(measure, step)}"
            )

        mapping = _mapping(event)
        recovered = mapping.get("feasibilityRecoveredSecondary") is True
        if recovered:
            recovered_count += 1
            if not observed or midi not in observed:
                raise ValueError(
                    f"Recovered MIDI {midi} lacks observed provenance "
                    f"at {(measure, step)}"
                )
            hypothesis = _recovery_hypothesis(event, midi)
            if not isinstance(hypothesis, Mapping):
                raise ValueError(
                    f"Recovered MIDI {midi} lacks a matching pitch hypothesis"
                )
            if hypothesis.get("feasibilityRecovered") is not True:
                raise ValueError(
                    f"Recovered MIDI {midi} lacks feasibilityRecovered provenance"
                )
            if hypothesis.get("precisionRetained") is True:
                raise ValueError(
                    f"Recovered MIDI {midi} is simultaneously marked "
                    "precision-retained"
                )

    if require_stable_order and ordered_keys != sorted(ordered_keys):
        raise ValueError(
            "Pre-export event order is not stable "
            "measure/step/string/fret/MIDI order"
        )

    multi_note_attacks = 0
    maximum_chord_size = 0

    for key, group in sorted(by_attack.items()):
        maximum_chord_size = max(maximum_chord_size, len(group))
        if len(group) > 1:
            multi_note_attacks += 1

        strings = [_integer(event, "stringIndex") for event in group]
        if len(strings) != len(set(strings)):
            raise ValueError(
                f"Duplicate simultaneous string before export at {key}"
            )

        dominant_values = {
            int(event["dominantMidi"])
            for event in group
            if event.get("dominantMidi") is not None
        }
        if len(dominant_values) > 1:
            raise ValueError(
                f"Inconsistent dominant MIDI within attack {key}"
            )

        source_values = {
            int(_mapping(event)["sourceAttackMidi"])
            for event in group
            if _mapping(event).get("sourceAttackMidi") is not None
        }
        if len(source_values) > 1:
            raise ValueError(
                f"Inconsistent sourceAttackMidi within attack {key}"
            )

        primary_midi: int | None = None
        if source_values:
            primary_midi = next(iter(source_values))
        elif dominant_values:
            primary_midi = next(iter(dominant_values))

        primary_markers = [
            event
            for event in group
            if _mapping(event).get("primaryTechniqueNote") is True
        ]
        has_primary_metadata = any(
            "primaryTechniqueNote" in _mapping(event)
            for event in group
        )
        if has_primary_metadata:
            if len(primary_markers) != 1:
                raise ValueError(
                    f"Attack {key} must contain exactly one primary technique note"
                )
            if (
                primary_midi is not None
                and _integer(primary_markers[0], "midi") != int(primary_midi)
            ):
                raise ValueError(
                    f"Attack {key} primary MIDI does not match immutable "
                    "source primary"
                )

        chord_counts = {
            int(_mapping(event)["chordNoteCount"])
            for event in group
            if _mapping(event).get("chordNoteCount") is not None
        }
        if chord_counts and chord_counts != {len(group)}:
            raise ValueError(
                f"Attack {key} chordNoteCount does not match rendered group size"
            )

        chord_indices = [
            int(_mapping(event)["chordNoteIndex"])
            for event in group
            if _mapping(event).get("chordNoteIndex") is not None
        ]
        if chord_indices and sorted(chord_indices) != list(range(len(group))):
            raise ValueError(
                f"Attack {key} chordNoteIndex sequence is not complete"
            )

        hypothesis_sets = [
            frozenset(_observed_midis(event))
            for event in group
            if _observed_midis(event)
        ]
        if hypothesis_sets and len(set(hypothesis_sets)) != 1:
            raise ValueError(
                f"Attack {key} serialized observed pitch sets differ "
                "across chord notes"
            )

    return PreExportValidationDiagnostics(
        event_count=len(copied),
        attack_count=len(by_attack),
        multi_note_attack_count=multi_note_attacks,
        maximum_chord_size=maximum_chord_size,
        recovered_secondary_count=recovered_count,
    )


__all__ = [
    "PreExportValidationDiagnostics",
    "validate_v143_preexport_events",
]
