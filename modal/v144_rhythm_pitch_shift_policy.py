from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
DEFAULT_MAX_ABS_SEMITONE_SHIFT = 12
OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}


def _rule_signatures(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return pre-registered rule keys: source pitch class + one context signature."""
    signatures = context_signature(row)
    pitch_classes = tuple(sig for sig in signatures if sig.startswith("pitchClass::"))
    if len(pitch_classes) != 1:
        raise ValueError("pitch-shift construction requires exactly one source pitch-class signature")
    pitch_class = pitch_classes[0]
    return tuple(
        (pitch_class, signature)
        for signature in signatures
        if signature != pitch_class
    )


def _stable_note_key(row: Mapping[str, Any]) -> tuple[int, int, int]:
    return (
        int(row["midi"]),
        int(row.get("stringIndex", -1)),
        int(row.get("fret", -1)),
    )


def same_onset_substitution_pairs(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Pair fit-only same-onset wrong-pitch notes deterministically.

    Exact-pitch notes are removed first. Remaining notes at each onset are paired by
    smallest absolute MIDI distance with deterministic tie-breaking. Pairs outside
    the pre-registered semitone bound are ignored. This function is construction-
    time only; runtime application never receives a reference row.
    """
    maximum = int(maximum_abs_semitone_shift)
    if maximum < 1 or maximum > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    generated_by_onset: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    reference_by_onset: dict[tuple[int, int], list[dict[str, Any]]] = defaultdict(list)
    for row in generated_notes:
        generated_by_onset[(int(row["measure"]), int(row["step"]))].append(dict(row))
    for row in reference_notes:
        reference_by_onset[(int(row["measure"]), int(row["step"]))].append(dict(row))

    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for onset in sorted(set(generated_by_onset) | set(reference_by_onset)):
        generated = sorted(generated_by_onset[onset], key=_stable_note_key)
        reference = sorted(reference_by_onset[onset], key=_stable_note_key)

        used_reference: set[int] = set()
        unmatched_generated: list[dict[str, Any]] = []
        for generated_row in generated:
            exact_index = next(
                (
                    index
                    for index, reference_row in enumerate(reference)
                    if index not in used_reference
                    and int(reference_row["midi"]) == int(generated_row["midi"])
                ),
                None,
            )
            if exact_index is None:
                unmatched_generated.append(generated_row)
            else:
                used_reference.add(exact_index)

        unmatched_reference = [
            reference_row
            for index, reference_row in enumerate(reference)
            if index not in used_reference
        ]
        candidates: list[tuple[int, int, int, int, int]] = []
        for generated_index, generated_row in enumerate(unmatched_generated):
            for reference_index, reference_row in enumerate(unmatched_reference):
                delta = int(reference_row["midi"]) - int(generated_row["midi"])
                if delta == 0 or abs(delta) > maximum:
                    continue
                candidates.append(
                    (
                        abs(delta),
                        int(generated_row["midi"]),
                        int(reference_row["midi"]),
                        generated_index,
                        reference_index,
                    )
                )

        candidates.sort()
        used_generated: set[int] = set()
        used_unmatched_reference: set[int] = set()
        for _, _, _, generated_index, reference_index in candidates:
            if generated_index in used_generated or reference_index in used_unmatched_reference:
                continue
            used_generated.add(generated_index)
            used_unmatched_reference.add(reference_index)
            result.append(
                (
                    dict(unmatched_generated[generated_index]),
                    dict(unmatched_reference[reference_index]),
                )
            )
    return result


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


def _eligible_for_shift(event: Mapping[str, Any], semitone_shift: int) -> bool:
    _, fret, _ = _validate_event_position(event)
    shifted_fret = fret + int(semitone_shift)
    return 0 <= shifted_fret <= 36


def rank_fit_pitch_shift_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Construct/rank pitch-shift rules solely from accepted-baseline fit labels."""
    minimum_support = int(minimum_correction_support)
    maximum = int(maximum_candidates)
    maximum_shift = int(maximum_abs_semitone_shift)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")
    if maximum_shift < 1 or maximum_shift > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")

    correction_support: Counter[tuple[tuple[str, str], int]] = Counter()
    for generated_row, reference_row in same_onset_substitution_pairs(
        fit_generated,
        fit_reference,
        maximum_abs_semitone_shift=maximum_shift,
    ):
        delta = int(reference_row["midi"]) - int(generated_row["midi"])
        if not _eligible_for_shift(generated_row, delta):
            continue
        for signatures in _rule_signatures(generated_row):
            correction_support[(signatures, delta)] += 1

    candidates: list[dict[str, Any]] = []
    for (signatures, semitone_shift), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = sum(
            1
            for row in fit_generated
            if event_matches_pitch_shift_rule(row, signatures)
            and _eligible_for_shift(row, semitone_shift)
        )
        if eligible_support < support or eligible_support <= 0:
            raise ValueError(
                f"invalid eligible support signatures={signatures!r} shift={semitone_shift}"
            )
        candidates.append(
            {
                "signatures": list(signatures),
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
            int(item["semitoneShift"]),
            tuple(item["signatures"]),
        )
    )
    return candidates[:maximum]


def event_matches_pitch_shift_rule(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    if len(signatures) != 2:
        raise ValueError("a V144 pitch-shift rule requires exactly two signatures")
    normalized = tuple(sorted(str(value) for value in signatures))
    if len(set(normalized)) != 2:
        raise ValueError("pitch-shift signatures must be distinct")
    if sum(value.startswith("pitchClass::") for value in normalized) != 1:
        raise ValueError("pitch-shift rule requires exactly one source pitch-class signature")
    available = set(context_signature(event))
    return all(signature in available for signature in normalized)


def apply_pitch_shift_rule(
    events: Sequence[Mapping[str, Any]],
    signatures: Sequence[str],
    semitone_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
) -> list[dict[str, Any]]:
    """Apply a reference-free same-string pitch/fret correction without deleting events."""
    shift = int(semitone_shift)
    maximum = int(maximum_abs_semitone_shift)
    if shift == 0 or abs(shift) > maximum or maximum < 1 or maximum > 12:
        raise ValueError("semitone_shift must be non-zero and within the configured [1, 12] bound")

    transformed: list[dict[str, Any]] = []
    for event in events:
        row = dict(event)
        if event_matches_pitch_shift_rule(row, signatures):
            _, fret, midi = _validate_event_position(row)
            shifted_fret = fret + shift
            if 0 <= shifted_fret <= 36:
                row["fret"] = shifted_fret
                row["midi"] = midi + shift
        transformed.append(row)
    return transformed


__all__ = [
    "DEFAULT_MAX_ABS_SEMITONE_SHIFT",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "OPEN_MIDI_BY_STRING_INDEX",
    "apply_pitch_shift_rule",
    "event_matches_pitch_shift_rule",
    "rank_fit_pitch_shift_rules",
    "same_onset_substitution_pairs",
]
