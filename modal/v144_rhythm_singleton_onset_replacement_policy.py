from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
DEFAULT_MAX_ABS_SEMITONE_SHIFT = 12


def _validate_event_position(event: Mapping[str, Any]) -> tuple[int, int, int]:
    string_index = int(event["stringIndex"])
    fret = int(event["fret"])
    midi = int(event["midi"])
    if string_index not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError(f"invalid stringIndex {string_index}")
    if not 0 <= fret <= 36:
        raise ValueError(f"invalid fret {fret}")
    expected = OPEN_MIDI_BY_STRING_INDEX[string_index] + fret
    if midi != expected:
        raise ValueError(
            f"pitch-position mismatch stringIndex={string_index} fret={fret} midi={midi} expected={expected}"
        )
    return string_index, fret, midi


def _onset_context_signatures(measure: int, step: int) -> tuple[str, ...]:
    signatures = context_signature({"measure": int(measure), "step": int(step)})
    if any(value.startswith(("pitchClass::", "register::", "registerStep::")) for value in signatures):
        raise ValueError("singleton onset context unexpectedly contains pitch-derived data")
    return signatures


def _validate_context_signature_value(value: str) -> str:
    signature = str(value)
    allowed_prefixes = (
        "measurePhase::",
        "section16::",
        "stepParity::",
        "stepQuarter::",
        "measurePhaseStep::",
    )
    if not signature.startswith(allowed_prefixes):
        raise ValueError(
            "singleton onset replacement requires one reference-free structural onset context signature"
        )
    return signature


def _normalize_rule(
    source_string_index: int,
    source_pitch_class: int,
    target_string_index: int,
    semitone_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> tuple[int, int, int, int]:
    source_string = int(source_string_index)
    source_pitch = int(source_pitch_class)
    target_string = int(target_string_index)
    shift = int(semitone_shift)
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if source_string not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("sourceStringIndex is invalid")
    if target_string not in OPEN_MIDI_BY_STRING_INDEX:
        raise ValueError("targetStringIndex is invalid")
    if source_string == target_string:
        raise ValueError("atomic singleton replacement requires a string change")
    if not 0 <= source_pitch <= 11:
        raise ValueError("sourcePitchClass must be in [0, 11]")
    if shift == 0 or abs(shift) > maximum:
        raise ValueError("semitoneShift must be non-zero and inside preregistered bound")
    return source_string, source_pitch, target_string, shift


def _group_by_onset(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(dict(row))
    return grouped


def _target_position(
    event: Mapping[str, Any],
    target_string_index: int,
    semitone_shift: int,
) -> tuple[int, int, int] | None:
    if has_pitch_linkage(event):
        return None
    try:
        source_string, _, source_midi = _validate_event_position(event)
    except ValueError:
        return None
    target_string = int(target_string_index)
    if target_string not in OPEN_MIDI_BY_STRING_INDEX or target_string == source_string:
        return None
    target_midi = source_midi + int(semitone_shift)
    target_fret = target_midi - OPEN_MIDI_BY_STRING_INDEX[target_string]
    if not 0 <= target_fret <= 36:
        return None
    return target_string, target_fret, target_midi


def exact_singleton_onset_replacements(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Return FIT-only one-note→one-note pitch+explicit-string replacements.

    Construction is deliberately onset-scoped and narrow. Generated and reference
    must each contain exactly one note at the same onset. Both pitch and string must
    change. The generated note must be safe to rewrite, the reference target must be
    a valid tuning-derived guitar position, and the pitch delta must stay inside the
    fixed semitone bound. Runtime application never receives reference rows.
    """
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    generated_by_onset = _group_by_onset(generated_notes)
    reference_by_onset = _group_by_onset(reference_notes)
    result: list[dict[str, Any]] = []

    for onset in sorted(set(generated_by_onset) & set(reference_by_onset)):
        generated = generated_by_onset[onset]
        reference = reference_by_onset[onset]
        if len(generated) != 1 or len(reference) != 1:
            continue
        generated_row = generated[0]
        reference_row = reference[0]
        if has_pitch_linkage(generated_row):
            continue
        try:
            source_string, _, source_midi = _validate_event_position(generated_row)
            target_string, target_fret, target_midi = _validate_event_position(reference_row)
        except ValueError:
            continue
        semitone_shift = target_midi - source_midi
        if semitone_shift == 0 or abs(semitone_shift) > maximum:
            continue
        if source_string == target_string:
            continue
        target = _target_position(generated_row, target_string, semitone_shift)
        if target is None:
            continue
        derived_string, derived_fret, derived_midi = target
        if (
            derived_string != target_string
            or derived_fret != target_fret
            or derived_midi != target_midi
        ):
            continue
        result.append(
            {
                "measure": int(onset[0]),
                "step": int(onset[1]),
                "sourceStringIndex": int(source_string),
                "sourcePitchClass": int(source_midi % 12),
                "targetStringIndex": int(target_string),
                "semitoneShift": int(semitone_shift),
            }
        )
    return result


def onset_matches_singleton_replacement_rule(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    source_string_index: int,
    source_pitch_class: int,
    target_string_index: int,
    semitone_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> bool:
    context_value = _validate_context_signature_value(context_signature_value)
    source_string, source_pitch, target_string, shift = _normalize_rule(
        source_string_index,
        source_pitch_class,
        target_string_index,
        semitone_shift,
        maximum_abs_semitone_shift=maximum_abs_semitone_shift,
    )
    if len(onset_events) != 1:
        return False
    row = dict(onset_events[0])
    if int(row["stringIndex"]) != source_string:
        return False
    if int(row["midi"]) % 12 != source_pitch:
        return False
    measure = int(row["measure"])
    step = int(row["step"])
    if context_value not in _onset_context_signatures(measure, step):
        return False
    return _target_position(row, target_string, shift) is not None


def rank_fit_singleton_onset_replacement_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Construct/rank singleton replacement rules solely from current-baseline FIT labels."""
    minimum_support = int(minimum_correction_support)
    maximum_candidate_count = int(maximum_candidates)
    maximum_shift = int(maximum_abs_semitone_shift)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum_candidate_count < 1:
        raise ValueError("maximum_candidates must be >= 1")
    if maximum_shift < 1 or maximum_shift > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    corrections = exact_singleton_onset_replacements(
        fit_generated,
        fit_reference,
        maximum_abs_semitone_shift=maximum_shift,
    )
    correction_support: Counter[tuple[str, int, int, int, int]] = Counter()
    for correction in corrections:
        for context_value in _onset_context_signatures(
            int(correction["measure"]), int(correction["step"])
        ):
            correction_support[
                (
                    context_value,
                    int(correction["sourceStringIndex"]),
                    int(correction["sourcePitchClass"]),
                    int(correction["targetStringIndex"]),
                    int(correction["semitoneShift"]),
                )
            ] += 1

    generated_by_onset = _group_by_onset(fit_generated)
    candidates: list[dict[str, Any]] = []
    for (
        context_value,
        source_string,
        source_pitch,
        target_string,
        semitone_shift,
    ), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = 0
        for onset in sorted(generated_by_onset):
            if onset_matches_singleton_replacement_rule(
                generated_by_onset[onset],
                context_value,
                source_string,
                source_pitch,
                target_string,
                semitone_shift,
                maximum_abs_semitone_shift=maximum_shift,
            ):
                eligible_support += 1
        if eligible_support < support or eligible_support <= 0:
            raise ValueError(
                "singleton replacement eligible support is inconsistent with FIT correction support"
            )
        candidates.append(
            {
                "contextSignature": str(context_value),
                "sourceStringIndex": int(source_string),
                "sourcePitchClass": int(source_pitch),
                "targetStringIndex": int(target_string),
                "semitoneShift": int(semitone_shift),
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
            abs(int(item["semitoneShift"])),
            int(item["sourceStringIndex"]),
            int(item["targetStringIndex"]),
            int(item["sourcePitchClass"]),
            int(item["semitoneShift"]),
            str(item["contextSignature"]),
        )
    )
    return candidates[:maximum_candidate_count]


def apply_singleton_onset_replacement_rule(
    events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    source_string_index: int,
    source_pitch_class: int,
    target_string_index: int,
    semitone_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Apply a reference-free atomic singleton pitch+explicit-string replacement."""
    context_value = _validate_context_signature_value(context_signature_value)
    source_string, source_pitch, target_string, shift = _normalize_rule(
        source_string_index,
        source_pitch_class,
        target_string_index,
        semitone_shift,
        maximum_abs_semitone_shift=maximum_abs_semitone_shift,
    )

    result = [dict(row) for row in events]
    indices_by_onset: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(result):
        indices_by_onset[(int(row["measure"]), int(row["step"]))].append(index)

    for onset in sorted(indices_by_onset):
        indices = indices_by_onset[onset]
        onset_events = [result[index] for index in indices]
        if not onset_matches_singleton_replacement_rule(
            onset_events,
            context_value,
            source_string,
            source_pitch,
            target_string,
            shift,
            maximum_abs_semitone_shift=maximum_abs_semitone_shift,
        ):
            continue
        target = _target_position(result[indices[0]], target_string, shift)
        if target is None:
            continue
        target_string_value, target_fret, target_midi = target
        index = indices[0]
        result[index]["stringIndex"] = int(target_string_value)
        result[index]["fret"] = int(target_fret)
        result[index]["midi"] = int(target_midi)
    return result


__all__ = [
    "DEFAULT_MAX_ABS_SEMITONE_SHIFT",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "apply_singleton_onset_replacement_rule",
    "exact_singleton_onset_replacements",
    "onset_matches_singleton_replacement_rule",
    "rank_fit_singleton_onset_replacement_rules",
]
