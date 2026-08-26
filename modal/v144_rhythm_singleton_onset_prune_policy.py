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
        raise ValueError("singleton onset prune requires structural onset signatures")
    if any(value.startswith(("pitchClass::", "register::", "registerStep::")) for value in result):
        raise ValueError("singleton onset prune structural context unexpectedly contains pitch-derived data")
    return result


def _validate_rule(
    context_signature_value: str,
    source_string_index: int,
    source_pitch_class: int,
) -> tuple[str, int, int]:
    context_value = str(context_signature_value)
    if not context_value.startswith(_ALLOWED_CONTEXT_PREFIXES):
        raise ValueError("singleton onset prune requires one structural onset context signature")
    source_string = int(source_string_index)
    source_pitch = int(source_pitch_class)
    if source_string not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("singleton onset prune source string is invalid")
    if not 0 <= source_pitch <= 11:
        raise ValueError("singleton onset prune source pitch class must be in [0,11]")
    return context_value, source_string, source_pitch


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


def _runtime_prune_eligible(
    events: Sequence[Mapping[str, Any]], event: Mapping[str, Any]
) -> bool:
    if not _source_position_is_valid(event):
        return False
    if has_pitch_linkage(event):
        return False
    if _event_referenced_by_other_event(events, event):
        return False
    measure = int(event["measure"])
    if sum(1 for row in events if int(row["measure"]) == measure) <= 1:
        return False
    return True


def singleton_generated_only_corrections(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Return FIT generated-only exact-singleton onset false positives.

    Construction uses FIT labels only to identify onsets with exactly one generated
    event and zero reference notes. Runtime application never receives reference
    rows. Source events with linked pitch semantics or invalid tuning positions are
    excluded before rule support is counted.
    """
    generated_by_onset = _group_by_onset(fit_generated)
    reference_by_onset = _group_by_onset(fit_reference)
    result: list[dict[str, Any]] = []
    for onset in sorted(generated_by_onset):
        generated = generated_by_onset[onset]
        reference = reference_by_onset.get(onset, [])
        if len(generated) != 1 or len(reference) != 0:
            continue
        event = generated[0]
        if not _source_position_is_valid(event) or has_pitch_linkage(event):
            continue
        result.append(dict(event))
    return result


def onset_matches_singleton_prune_rule(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    source_string_index: int,
    source_pitch_class: int,
) -> bool:
    context_value, source_string, source_pitch = _validate_rule(
        context_signature_value,
        source_string_index,
        source_pitch_class,
    )
    if len(onset_events) != 1:
        return False
    event = onset_events[0]
    measure = int(event["measure"])
    step = int(event["step"])
    if context_value not in _structural_onset_signatures(measure, step):
        return False
    if int(event["stringIndex"]) != source_string:
        return False
    if int(event["midi"]) % 12 != source_pitch:
        return False
    return True


def rank_fit_singleton_onset_prune_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_false_positive_support: int = DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Construct/rank atomic singleton-onset prune rules from FIT labels only."""
    minimum_support = int(minimum_false_positive_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1:
        raise ValueError("minimum_false_positive_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")

    correction_support: Counter[tuple[str, int, int]] = Counter()
    for event in singleton_generated_only_corrections(fit_generated, fit_reference):
        source_string = int(event["stringIndex"])
        source_pitch = int(event["midi"]) % 12
        for context_value in _structural_onset_signatures(int(event["measure"]), int(event["step"])):
            correction_support[(context_value, source_string, source_pitch)] += 1

    generated_by_onset = _group_by_onset(fit_generated)
    candidates: list[dict[str, Any]] = []
    for (context_value, source_string, source_pitch), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = 0
        for onset in sorted(generated_by_onset):
            events = generated_by_onset[onset]
            if not onset_matches_singleton_prune_rule(
                events, context_value, source_string, source_pitch
            ):
                continue
            event = events[0]
            if not _source_position_is_valid(event) or has_pitch_linkage(event):
                continue
            eligible_support += 1
        if eligible_support < support or eligible_support <= 0:
            raise ValueError("singleton onset prune eligible support is inconsistent")
        candidates.append(
            {
                "contextSignature": context_value,
                "sourceStringIndex": source_string,
                "sourcePitchClass": source_pitch,
                "fitFalsePositiveSupport": int(support),
                "fitEligibleGeneratedSupport": int(eligible_support),
                "fitFalsePositivePrecision": float(support) / float(eligible_support),
            }
        )

    candidates.sort(
        key=lambda item: (
            -float(item["fitFalsePositivePrecision"]),
            -int(item["fitFalsePositiveSupport"]),
            int(item["fitEligibleGeneratedSupport"]),
            str(item["contextSignature"]),
            int(item["sourceStringIndex"]),
            int(item["sourcePitchClass"]),
        )
    )
    return candidates[:maximum]


def apply_singleton_onset_prune_rule(
    events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    source_string_index: int,
    source_pitch_class: int,
) -> list[dict[str, Any]]:
    """Reference-free atomic prune of eligible exact-singleton generated onsets."""
    context_value, source_string, source_pitch = _validate_rule(
        context_signature_value,
        source_string_index,
        source_pitch_class,
    )
    source = [dict(row) for row in events]
    grouped_indices: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(source):
        grouped_indices[(int(row["measure"]), int(row["step"]))].append(index)

    prune_indices: set[int] = set()
    for onset in sorted(grouped_indices):
        indices = grouped_indices[onset]
        onset_events = [source[index] for index in indices]
        if not onset_matches_singleton_prune_rule(
            onset_events, context_value, source_string, source_pitch
        ):
            continue
        index = indices[0]
        event = source[index]
        if not _runtime_prune_eligible(source, event):
            continue
        prune_indices.add(index)

    return [row for index, row in enumerate(source) if index not in prune_indices]


__all__ = [
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_FALSE_POSITIVE_SUPPORT",
    "apply_singleton_onset_prune_rule",
    "onset_matches_singleton_prune_rule",
    "rank_fit_singleton_onset_prune_rules",
    "singleton_generated_only_corrections",
]
