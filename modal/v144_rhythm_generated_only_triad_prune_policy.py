from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage

DEFAULT_MIN_FALSE_POSITIVE_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
_ALLOWED_CONTEXT_PREFIXES = (
    "measurePhase::",
    "section16::",
    "stepParity::",
    "stepQuarter::",
    "measurePhaseStep::",
)


def _group_by_onset(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(dict(row))
    return grouped


def _structural_onset_signatures(measure: int, step: int) -> tuple[str, ...]:
    signatures = context_signature({"measure": int(measure), "step": int(step)})
    result = tuple(value for value in signatures if value.startswith(_ALLOWED_CONTEXT_PREFIXES))
    if not result:
        raise ValueError("generated-only triad prune requires structural onset signatures")
    return result


def _validate_note_identity(string_index: int, pitch_class: int) -> tuple[int, int]:
    string_value = int(string_index)
    pitch_value = int(pitch_class)
    if string_value not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("generated-only triad source string is invalid")
    if not 0 <= pitch_value <= 11:
        raise ValueError("generated-only triad source pitch class must be in [0,11]")
    return string_value, pitch_value


def _normalize_identities(values: Sequence[tuple[int, int]]) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]]:
    if len(values) != 3:
        raise ValueError("generated-only triad rule requires exactly three source identities")
    normalized = tuple(sorted(_validate_note_identity(string_index, pitch_class) for string_index, pitch_class in values))
    return normalized  # type: ignore[return-value]


def _validate_rule(
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    third_string_index: int,
    third_pitch_class: int,
) -> tuple[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]:
    context_value = str(context_signature_value)
    if not context_value.startswith(_ALLOWED_CONTEXT_PREFIXES):
        raise ValueError("generated-only triad prune requires one structural onset context signature")
    return context_value, _normalize_identities(
        (
            (first_string_index, first_pitch_class),
            (second_string_index, second_pitch_class),
            (third_string_index, third_pitch_class),
        )
    )


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


def _event_referenced_by_other_event(events: Sequence[Mapping[str, Any]], target_event: Mapping[str, Any]) -> bool:
    if "eventIndex" not in target_event:
        return True
    target_index = int(target_event["eventIndex"])
    for row in events:
        if row is target_event:
            continue
        for key, value in row.items():
            if key == "eventIndex" or not key.endswith("EventIndex") or value is None:
                continue
            try:
                if int(value) == target_index:
                    return True
            except (TypeError, ValueError):
                continue
    return False


def _onset_identities(onset_events: Sequence[Mapping[str, Any]]) -> tuple[tuple[int, int], tuple[int, int], tuple[int, int]] | None:
    if len(onset_events) != 3:
        return None
    try:
        return tuple(sorted((int(event["stringIndex"]), int(event["midi"]) % 12) for event in onset_events))  # type: ignore[return-value]
    except (KeyError, TypeError, ValueError):
        return None


def _triad_is_runtime_prune_eligible(events: Sequence[Mapping[str, Any]], onset_events: Sequence[Mapping[str, Any]]) -> bool:
    if len(onset_events) != 3:
        return False
    if any(not _source_position_is_valid(event) or has_pitch_linkage(event) for event in onset_events):
        return False
    if any(_event_referenced_by_other_event(events, event) for event in onset_events):
        return False
    measure = int(onset_events[0]["measure"])
    if any(int(event["measure"]) != measure for event in onset_events):
        return False
    if sum(1 for row in events if int(row["measure"]) == measure) <= 3:
        return False
    return True


def generated_only_triad_corrections(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
) -> list[list[dict[str, Any]]]:
    generated_by_onset = _group_by_onset(fit_generated)
    reference_by_onset = _group_by_onset(fit_reference)
    result: list[list[dict[str, Any]]] = []
    for onset in sorted(generated_by_onset):
        generated = generated_by_onset[onset]
        if len(generated) != 3 or len(reference_by_onset.get(onset, [])) != 0:
            continue
        if any(not _source_position_is_valid(event) or has_pitch_linkage(event) for event in generated):
            continue
        result.append([dict(event) for event in generated])
    return result


def onset_matches_generated_only_triad_prune_rule(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    third_string_index: int,
    third_pitch_class: int,
) -> bool:
    context_value, expected_identities = _validate_rule(
        context_signature_value,
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
        third_string_index,
        third_pitch_class,
    )
    if len(onset_events) != 3:
        return False
    measure = int(onset_events[0]["measure"])
    step = int(onset_events[0]["step"])
    if any(int(event["measure"]) != measure or int(event["step"]) != step for event in onset_events):
        return False
    if context_value not in _structural_onset_signatures(measure, step):
        return False
    return _onset_identities(onset_events) == expected_identities


def rank_fit_generated_only_triad_prune_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_false_positive_support: int = DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    minimum_support = int(minimum_false_positive_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1 or maximum < 1:
        raise ValueError("support and candidate cap must be positive")

    support: Counter[tuple[str, tuple[tuple[int, int], tuple[int, int], tuple[int, int]]]] = Counter()
    for triad in generated_only_triad_corrections(fit_generated, fit_reference):
        identities = _onset_identities(triad)
        if identities is None:
            raise ValueError("triad correction lost source identity")
        measure = int(triad[0]["measure"]); step = int(triad[0]["step"])
        for context_value in _structural_onset_signatures(measure, step):
            support[(context_value, identities)] += 1

    generated_by_onset = _group_by_onset(fit_generated)
    candidates: list[dict[str, Any]] = []
    for (context_value, identities), correction_support in support.items():
        if correction_support < minimum_support:
            continue
        eligible_support = 0
        for onset in sorted(generated_by_onset):
            events = generated_by_onset[onset]
            if onset_matches_generated_only_triad_prune_rule(
                events, context_value,
                identities[0][0], identities[0][1],
                identities[1][0], identities[1][1],
                identities[2][0], identities[2][1],
            ) and not any(not _source_position_is_valid(event) or has_pitch_linkage(event) for event in events):
                eligible_support += 1
        if eligible_support < correction_support or eligible_support <= 0:
            raise ValueError("generated-only triad eligible support is inconsistent")
        candidates.append({
            "contextSignature": context_value,
            "firstSourceStringIndex": identities[0][0],
            "firstSourcePitchClass": identities[0][1],
            "secondSourceStringIndex": identities[1][0],
            "secondSourcePitchClass": identities[1][1],
            "thirdSourceStringIndex": identities[2][0],
            "thirdSourcePitchClass": identities[2][1],
            "fitFalsePositiveSupport": int(correction_support),
            "fitEligibleGeneratedSupport": int(eligible_support),
            "fitFalsePositivePrecision": float(correction_support) / float(eligible_support),
        })

    candidates.sort(key=lambda item: (
        -float(item["fitFalsePositivePrecision"]),
        -int(item["fitFalsePositiveSupport"]),
        int(item["fitEligibleGeneratedSupport"]),
        str(item["contextSignature"]),
        int(item["firstSourceStringIndex"]), int(item["firstSourcePitchClass"]),
        int(item["secondSourceStringIndex"]), int(item["secondSourcePitchClass"]),
        int(item["thirdSourceStringIndex"]), int(item["thirdSourcePitchClass"]),
    ))
    return candidates[:maximum]


def apply_generated_only_triad_prune_rule(
    events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    first_string_index: int,
    first_pitch_class: int,
    second_string_index: int,
    second_pitch_class: int,
    third_string_index: int,
    third_pitch_class: int,
) -> list[dict[str, Any]]:
    context_value, identities = _validate_rule(
        context_signature_value,
        first_string_index,
        first_pitch_class,
        second_string_index,
        second_pitch_class,
        third_string_index,
        third_pitch_class,
    )
    source = [dict(row) for row in events]
    grouped_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(source):
        grouped_indices[(int(row["measure"]), int(row["step"]))].append(index)

    prune_indices: set[int] = set()
    for onset in sorted(grouped_indices):
        indices = grouped_indices[onset]
        onset_events = [source[index] for index in indices]
        if not onset_matches_generated_only_triad_prune_rule(
            onset_events, context_value,
            identities[0][0], identities[0][1],
            identities[1][0], identities[1][1],
            identities[2][0], identities[2][1],
        ):
            continue
        if not _triad_is_runtime_prune_eligible(source, onset_events):
            continue
        prune_indices.update(indices)
    return [row for index, row in enumerate(source) if index not in prune_indices]


__all__ = [
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_FALSE_POSITIVE_SUPPORT",
    "apply_generated_only_triad_prune_rule",
    "generated_only_triad_corrections",
    "onset_matches_generated_only_triad_prune_rule",
    "rank_fit_generated_only_triad_prune_rules",
]
