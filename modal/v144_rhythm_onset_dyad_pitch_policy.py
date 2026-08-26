from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
DEFAULT_MAX_ABS_SEMITONE_SHIFT = 12


def _stable_note_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return (
        int(row.get("stringIndex", -1)),
        int(row["midi"]),
        int(row.get("fret", -1)),
        int(row.get("eventIndex", -1)),
    )


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
        raise ValueError("onset context unexpectedly contains pitch-derived data")
    return signatures


def _normalize_note_rules(
    note_rules: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if len(note_rules) != 2:
        raise ValueError("atomic onset-dyad rule requires exactly two note rules")

    normalized: list[tuple[int, int, int]] = []
    for rule in note_rules:
        string_index = int(rule["stringIndex"])
        source_pitch_class = int(rule["sourcePitchClass"])
        shift = int(rule["semitoneShift"])
        if string_index not in OPEN_MIDI_BY_STRING_INDEX:
            raise ValueError("dyad rule contains invalid stringIndex")
        if not 0 <= source_pitch_class <= 11:
            raise ValueError("dyad rule sourcePitchClass must be in [0, 11]")
        if shift == 0 or abs(shift) > maximum:
            raise ValueError("dyad rule semitoneShift must be non-zero and inside preregistered bound")
        normalized.append((string_index, source_pitch_class, shift))

    normalized.sort()
    if normalized[0][0] == normalized[1][0]:
        raise ValueError("atomic onset-dyad rule requires two distinct strings")
    return normalized[0], normalized[1]


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
        raise ValueError("dyad rule requires one reference-free structural onset context signature")
    return signature


def _group_by_onset(
    rows: Sequence[Mapping[str, Any]],
) -> dict[tuple[int, int], list[dict[str, Any]]]:
    grouped: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["measure"]), int(row["step"]))].append(dict(row))
    return grouped


def exact_two_note_onset_dyad_corrections(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Return fit-only exact-two-note same-string dyad rewrites.

    Construction is deliberately narrow and pre-registered: generated and reference
    onsets must each contain exactly two notes on the same two distinct strings. Both
    notes must require non-zero pitch changes inside the fixed semitone bound, and
    the target fret must be the tuning-derived same-string fret. Runtime application
    never receives reference rows.
    """
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    generated_by_onset = _group_by_onset(generated_notes)
    reference_by_onset = _group_by_onset(reference_notes)
    result: list[dict[str, Any]] = []

    for onset in sorted(set(generated_by_onset) & set(reference_by_onset)):
        generated = sorted(generated_by_onset[onset], key=_stable_note_key)
        reference = sorted(reference_by_onset[onset], key=_stable_note_key)
        if len(generated) != 2 or len(reference) != 2:
            continue

        generated_by_string = {int(row["stringIndex"]): row for row in generated}
        reference_by_string = {int(row["stringIndex"]): row for row in reference}
        if len(generated_by_string) != 2 or len(reference_by_string) != 2:
            continue
        if tuple(sorted(generated_by_string)) != tuple(sorted(reference_by_string)):
            continue

        note_rules: list[dict[str, int]] = []
        valid = True
        for string_index in sorted(generated_by_string):
            generated_row = generated_by_string[string_index]
            reference_row = reference_by_string[string_index]
            try:
                _, generated_fret, generated_midi = _validate_event_position(generated_row)
            except ValueError:
                valid = False
                break
            if has_pitch_linkage(generated_row):
                valid = False
                break
            reference_midi = int(reference_row["midi"])
            reference_fret = int(reference_row["fret"])
            shift = reference_midi - generated_midi
            if shift == 0 or abs(shift) > maximum:
                valid = False
                break
            target_fret = generated_fret + shift
            if not 0 <= target_fret <= 36:
                valid = False
                break
            if target_fret != reference_fret:
                valid = False
                break
            if OPEN_MIDI_BY_STRING_INDEX[string_index] + target_fret != reference_midi:
                valid = False
                break
            note_rules.append(
                {
                    "stringIndex": string_index,
                    "sourcePitchClass": generated_midi % 12,
                    "semitoneShift": shift,
                }
            )
        if not valid:
            continue

        normalized = _normalize_note_rules(
            note_rules,
            maximum_abs_semitone_shift=maximum,
        )
        result.append(
            {
                "measure": onset[0],
                "step": onset[1],
                "noteRules": [
                    {
                        "stringIndex": string_index,
                        "sourcePitchClass": source_pitch_class,
                        "semitoneShift": shift,
                    }
                    for string_index, source_pitch_class, shift in normalized
                ],
            }
        )
    return result


def onset_matches_dyad_rule(
    onset_events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    note_rules: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> bool:
    context_value = _validate_context_signature_value(context_signature_value)
    normalized = _normalize_note_rules(
        note_rules,
        maximum_abs_semitone_shift=maximum_abs_semitone_shift,
    )
    if len(onset_events) != 2:
        return False

    events = [dict(row) for row in onset_events]
    locations = {(int(row["measure"]), int(row["step"])) for row in events}
    if len(locations) != 1:
        raise ValueError("atomic onset-dyad runtime group spans multiple onsets")
    measure, step = next(iter(locations))
    if context_value not in _onset_context_signatures(measure, step):
        return False

    events_by_string = {int(row["stringIndex"]): row for row in events}
    if len(events_by_string) != 2:
        return False
    if tuple(sorted(events_by_string)) != tuple(rule[0] for rule in normalized):
        return False
    for string_index, source_pitch_class, _ in normalized:
        row = events_by_string[string_index]
        if int(row["midi"]) % 12 != source_pitch_class:
            return False
    return True


def _eligible_atomic_rewrite(
    onset_events: Sequence[Mapping[str, Any]],
    note_rules: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> bool:
    normalized = _normalize_note_rules(
        note_rules,
        maximum_abs_semitone_shift=maximum_abs_semitone_shift,
    )
    events_by_string = {int(row["stringIndex"]): row for row in onset_events}
    if len(events_by_string) != 2:
        return False
    for string_index, _, shift in normalized:
        row = events_by_string.get(string_index)
        if row is None or has_pitch_linkage(row):
            return False
        try:
            _, fret, _ = _validate_event_position(row)
        except ValueError:
            return False
        target_fret = fret + shift
        if not 0 <= target_fret <= 36:
            return False
    return True


def rank_fit_onset_dyad_pitch_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Construct/rank atomic dyad rewrite rules solely from current-baseline fit labels."""
    minimum_support = int(minimum_correction_support)
    maximum_candidates_value = int(maximum_candidates)
    maximum_shift = int(maximum_abs_semitone_shift)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum_candidates_value < 1:
        raise ValueError("maximum_candidates must be >= 1")
    if maximum_shift < 1 or maximum_shift > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    corrections = exact_two_note_onset_dyad_corrections(
        fit_generated,
        fit_reference,
        maximum_abs_semitone_shift=maximum_shift,
    )
    correction_support: Counter[tuple[str, tuple[tuple[int, int, int], ...]]] = Counter()
    for correction in corrections:
        normalized = _normalize_note_rules(
            correction["noteRules"],
            maximum_abs_semitone_shift=maximum_shift,
        )
        for context_value in _onset_context_signatures(
            int(correction["measure"]), int(correction["step"])
        ):
            correction_support[(context_value, tuple(normalized))] += 1

    generated_by_onset = _group_by_onset(fit_generated)
    candidates: list[dict[str, Any]] = []
    for (context_value, normalized), support in correction_support.items():
        if support < minimum_support:
            continue
        note_rules = [
            {
                "stringIndex": string_index,
                "sourcePitchClass": source_pitch_class,
                "semitoneShift": shift,
            }
            for string_index, source_pitch_class, shift in normalized
        ]
        eligible_support = 0
        for onset in sorted(generated_by_onset):
            events = generated_by_onset[onset]
            if onset_matches_dyad_rule(
                events,
                context_value,
                note_rules,
                maximum_abs_semitone_shift=maximum_shift,
            ) and _eligible_atomic_rewrite(
                events,
                note_rules,
                maximum_abs_semitone_shift=maximum_shift,
            ):
                eligible_support += 1
        if eligible_support < support or eligible_support <= 0:
            raise ValueError("atomic dyad eligible support is inconsistent with fit correction support")
        candidates.append(
            {
                "contextSignature": context_value,
                "noteRules": note_rules,
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
            sum(abs(int(rule["semitoneShift"])) for rule in item["noteRules"]),
            tuple(
                (int(rule["stringIndex"]), int(rule["sourcePitchClass"]), int(rule["semitoneShift"]))
                for rule in item["noteRules"]
            ),
            str(item["contextSignature"]),
        )
    )
    return candidates[:maximum_candidates_value]


def apply_onset_dyad_pitch_rule(
    events: Sequence[Mapping[str, Any]],
    context_signature_value: str,
    note_rules: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Apply a reference-free atomic two-note same-onset pitch/fret rewrite."""
    context_value = _validate_context_signature_value(context_signature_value)
    normalized = _normalize_note_rules(
        note_rules,
        maximum_abs_semitone_shift=maximum_abs_semitone_shift,
    )
    normalized_rules = [
        {
            "stringIndex": string_index,
            "sourcePitchClass": source_pitch_class,
            "semitoneShift": shift,
        }
        for string_index, source_pitch_class, shift in normalized
    ]

    result = [dict(row) for row in events]
    indices_by_onset: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, row in enumerate(result):
        indices_by_onset[(int(row["measure"]), int(row["step"]))].append(index)

    for onset in sorted(indices_by_onset):
        indices = indices_by_onset[onset]
        onset_events = [result[index] for index in indices]
        if not onset_matches_dyad_rule(
            onset_events,
            context_value,
            normalized_rules,
            maximum_abs_semitone_shift=maximum_abs_semitone_shift,
        ):
            continue
        if not _eligible_atomic_rewrite(
            onset_events,
            normalized_rules,
            maximum_abs_semitone_shift=maximum_abs_semitone_shift,
        ):
            continue

        index_by_string = {int(result[index]["stringIndex"]): index for index in indices}
        updates: list[tuple[int, int]] = []
        for string_index, _, shift in normalized:
            index = index_by_string[string_index]
            updates.append((index, shift))
        for index, shift in updates:
            result[index]["midi"] = int(result[index]["midi"]) + shift
            result[index]["fret"] = int(result[index]["fret"]) + shift
    return result
