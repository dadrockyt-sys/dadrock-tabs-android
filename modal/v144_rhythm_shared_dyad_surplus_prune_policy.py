from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
_ALLOWED_CONTEXT_PREFIXES = (
    "measurePhase::",
    "section16::",
    "stepParity::",
    "stepQuarter::",
    "measurePhaseStep::",
)

NoteIdentity = tuple[int, int]
DyadIdentity = tuple[NoteIdentity, NoteIdentity]
RuleIdentity = tuple[str, DyadIdentity, NoteIdentity]


def _group_by_onset(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(dict(row))
    return grouped


def _structural_onset_signatures(measure: int, step: int) -> tuple[str, ...]:
    signatures = context_signature({"measure": int(measure), "step": int(step)})
    result = tuple(value for value in signatures if value.startswith(_ALLOWED_CONTEXT_PREFIXES))
    if not result:
        raise ValueError("shared dyad surplus prune requires structural onset signatures")
    if any(value.startswith(("pitchClass::", "register::", "registerStep::")) for value in result):
        raise ValueError("shared dyad surplus structural context unexpectedly contains pitch-derived data")
    return result


def _validate_note_identity(string_index: int, pitch_class: int) -> NoteIdentity:
    string_value = int(string_index)
    pitch_value = int(pitch_class)
    if string_value not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("shared dyad surplus source string is invalid")
    if not 0 <= pitch_value <= 11:
        raise ValueError("shared dyad surplus source pitch class must be in [0,11]")
    return string_value, pitch_value


def _normalize_dyad_identities(
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
) -> DyadIdentity:
    identities = tuple(
        sorted(
            (
                _validate_note_identity(first_string_index, first_pitch_class),
                _validate_note_identity(second_string_index, second_pitch_class),
            )
        )
    )
    if identities[0] == identities[1]:
        raise ValueError("shared dyad surplus rule requires two distinguishable source identities")
    return identities  # type: ignore[return-value]


def _validate_rule(
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    prune_string_index: int,
    prune_pitch_class: int,
) -> RuleIdentity:
    context_value = str(context_signature_value)
    if not context_value.startswith(_ALLOWED_CONTEXT_PREFIXES):
        raise ValueError("shared dyad surplus prune requires one structural onset context signature")
    identities = _normalize_dyad_identities(
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
    )
    prune_identity = _validate_note_identity(prune_string_index, prune_pitch_class)
    if sum(1 for identity in identities if identity == prune_identity) != 1:
        raise ValueError("shared dyad surplus prune identity must uniquely name one dyad member")
    return context_value, identities, prune_identity


def _source_position_is_valid(event: Mapping[str, Any]) -> bool:
    try:
        string_index = int(event["stringIndex"])
        fret = int(event["fret"])
        midi = int(event["midi"])
    except (KeyError, TypeError, ValueError):
        return False
    if string_index not in OPEN_MIDI_BY_STRING_INDEX or not 0 <= fret <= 36:
        return False
    return OPEN_MIDI_BY_STRING_INDEX[string_index] + fret == midi


def _event_referenced_by_other_event(
    events: Sequence[Mapping[str, Any]], target_event: Mapping[str, Any]
) -> bool:
    if "eventIndex" not in target_event:
        return True
    target_index = int(target_event["eventIndex"])
    for row in events:
        if row is target_event:
            continue
        for key, value in row.items():
            if key == "eventIndex" or not key.endswith("EventIndex"):
                continue
            if value is None:
                continue
            try:
                if int(value) == target_index:
                    return True
            except (TypeError, ValueError):
                continue
    return False


def _event_identity(event: Mapping[str, Any]) -> NoteIdentity | None:
    try:
        return int(event["stringIndex"]), int(event["midi"]) % 12
    except (KeyError, TypeError, ValueError):
        return None


def _onset_dyad_identities(onset_events: Sequence[Mapping[str, Any]]) -> DyadIdentity | None:
    if len(onset_events) != 2:
        return None
    identities = [_event_identity(event) for event in onset_events]
    if any(identity is None for identity in identities):
        return None
    normalized = tuple(sorted(identity for identity in identities if identity is not None))
    if len(normalized) != 2 or normalized[0] == normalized[1]:
        return None
    return normalized  # type: ignore[return-value]


def _matching_prune_local_index(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    identities: DyadIdentity,
    prune_identity: NoteIdentity,
) -> int | None:
    if len(onset_events) != 2:
        return None
    try:
        measure = int(onset_events[0]["measure"])
        step = int(onset_events[0]["step"])
    except (KeyError, TypeError, ValueError):
        return None
    if any(
        int(event["measure"]) != measure or int(event["step"]) != step
        for event in onset_events
    ):
        return None
    if context_signature_value not in _structural_onset_signatures(measure, step):
        return None
    if _onset_dyad_identities(onset_events) != identities:
        return None
    matches = [
        index for index, event in enumerate(onset_events) if _event_identity(event) == prune_identity
    ]
    if len(matches) != 1:
        return None
    return matches[0]


def _runtime_prune_eligible(
    events: Sequence[Mapping[str, Any]],
    onset_events: Sequence[Mapping[str, Any]],
    prune_event: Mapping[str, Any],
) -> bool:
    if len(onset_events) != 2:
        return False
    if any(not _source_position_is_valid(event) for event in onset_events):
        return False
    if any(has_pitch_linkage(event) for event in onset_events):
        return False
    if _event_referenced_by_other_event(events, prune_event):
        return False
    try:
        measure = int(prune_event["measure"])
    except (KeyError, TypeError, ValueError):
        return False
    if sum(1 for row in events if int(row["measure"]) == measure) <= 1:
        return False
    return True


def shared_dyad_surplus_corrections(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return unambiguous FIT dyad-to-singleton surplus-note corrections.

    FIT labels are used only during construction: exactly two generated notes share
    an onset with exactly one reference note, and exactly one generated note has
    exact MIDI equality with that reference note. The exact-MIDI match is retained;
    the other generated note is the correction target. Runtime application never
    receives reference rows.
    """
    generated_by_onset = _group_by_onset(fit_generated)
    reference_by_onset = _group_by_onset(fit_reference)
    result: list[dict[str, Any]] = []
    for onset in sorted(generated_by_onset):
        generated = generated_by_onset[onset]
        reference = reference_by_onset.get(onset, [])
        if len(generated) != 2 or len(reference) != 1:
            continue
        if _onset_dyad_identities(generated) is None:
            continue
        if any(not _source_position_is_valid(event) or has_pitch_linkage(event) for event in generated):
            continue
        try:
            reference_midi = int(reference[0]["midi"])
        except (KeyError, TypeError, ValueError):
            continue
        exact_matches = [index for index, event in enumerate(generated) if int(event["midi"]) == reference_midi]
        if len(exact_matches) != 1:
            continue
        survivor_index = exact_matches[0]
        prune_index = 1 - survivor_index
        prune_event = generated[prune_index]
        if _event_referenced_by_other_event(fit_generated, prune_event):
            continue
        result.append(
            {
                "onsetEvents": [dict(event) for event in generated],
                "pruneEvent": dict(prune_event),
                "survivorEvent": dict(generated[survivor_index]),
            }
        )
    return result


def onset_matches_shared_dyad_surplus_prune_rule(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    prune_string_index: int,
    prune_pitch_class: int,
) -> bool:
    context_value, identities, prune_identity = _validate_rule(
        context_signature_value,
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
        prune_string_index,
        prune_pitch_class,
    )
    return (
        _matching_prune_local_index(
            onset_events,
            context_value,
            identities,
            prune_identity,
        )
        is not None
    )


def rank_fit_shared_dyad_surplus_prune_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Construct/rank family #14 rules from FIT labels only."""
    minimum_support = int(minimum_correction_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")

    correction_support: Counter[RuleIdentity] = Counter()
    for correction in shared_dyad_surplus_corrections(fit_generated, fit_reference):
        onset_events = correction["onsetEvents"]
        identities = _onset_dyad_identities(onset_events)
        prune_identity = _event_identity(correction["pruneEvent"])
        if identities is None or prune_identity is None:
            raise ValueError("shared dyad surplus correction lost frozen source identity")
        measure = int(onset_events[0]["measure"])
        step = int(onset_events[0]["step"])
        for context_value in _structural_onset_signatures(measure, step):
            correction_support[(context_value, identities, prune_identity)] += 1

    generated_by_onset = _group_by_onset(fit_generated)
    candidates: list[dict[str, Any]] = []
    for (context_value, identities, prune_identity), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = 0
        for onset in sorted(generated_by_onset):
            onset_events = generated_by_onset[onset]
            prune_local_index = _matching_prune_local_index(
                onset_events,
                context_value,
                identities,
                prune_identity,
            )
            if prune_local_index is None:
                continue
            if not _runtime_prune_eligible(
                fit_generated,
                onset_events,
                onset_events[prune_local_index],
            ):
                continue
            eligible_support += 1
        if eligible_support < support or eligible_support <= 0:
            raise ValueError("shared dyad surplus eligible support is inconsistent")
        candidates.append(
            {
                "contextSignature": context_value,
                "firstSourceStringIndex": identities[0][0],
                "firstSourcePitchClass": identities[0][1],
                "secondSourceStringIndex": identities[1][0],
                "secondSourcePitchClass": identities[1][1],
                "pruneSourceStringIndex": prune_identity[0],
                "pruneSourcePitchClass": prune_identity[1],
                "fitCorrectionSupport": int(support),
                "fitEligibleGeneratedSupport": int(eligible_support),
                "fitCorrectionPrecision": float(support) / float(eligible_support),
            }
        )

    candidates.sort(
        key=lambda item: (
            -float(item["fitCorrectionPrecision"]),
            -int(item["fitCorrectionSupport"]),
            int(item["fitEligibleGeneratedSupport"]),
            str(item["contextSignature"]),
            int(item["firstSourceStringIndex"]),
            int(item["firstSourcePitchClass"]),
            int(item["secondSourceStringIndex"]),
            int(item["secondSourcePitchClass"]),
            int(item["pruneSourceStringIndex"]),
            int(item["pruneSourcePitchClass"]),
        )
    )
    return candidates[:maximum]


def apply_shared_dyad_surplus_prune_rule(
    events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    prune_string_index: int,
    prune_pitch_class: int,
) -> list[dict[str, Any]]:
    """Reference-free atomic removal of one uniquely identified dyad member."""
    context_value, identities, prune_identity = _validate_rule(
        context_signature_value,
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
        prune_string_index,
        prune_pitch_class,
    )
    source = [dict(row) for row in events]
    grouped_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(source):
        grouped_indices[(int(row["measure"]), int(row["step"]))].append(index)

    prune_indices: set[int] = set()
    for onset in sorted(grouped_indices):
        indices = grouped_indices[onset]
        onset_events = [source[index] for index in indices]
        prune_local_index = _matching_prune_local_index(
            onset_events,
            context_value,
            identities,
            prune_identity,
        )
        if prune_local_index is None:
            continue
        prune_event = onset_events[prune_local_index]
        if not _runtime_prune_eligible(source, onset_events, prune_event):
            continue
        prune_indices.add(indices[prune_local_index])

    return [row for index, row in enumerate(source) if index not in prune_indices]


__all__ = [
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "apply_shared_dyad_surplus_prune_rule",
    "onset_matches_shared_dyad_surplus_prune_rule",
    "rank_fit_shared_dyad_surplus_prune_rules",
    "shared_dyad_surplus_corrections",
]
