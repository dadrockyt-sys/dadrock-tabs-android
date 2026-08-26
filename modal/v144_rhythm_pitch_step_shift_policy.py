from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
DEFAULT_MAX_ABS_SEMITONE_SHIFT = 12
DEFAULT_MAX_ABS_STEP_SHIFT = 2


def _rule_signatures(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return source pitch-class + one structural context signature."""
    signatures = context_signature(row)
    pitch_classes = tuple(value for value in signatures if value.startswith("pitchClass::"))
    if len(pitch_classes) != 1:
        raise ValueError("joint pitch-step construction requires exactly one pitch-class signature")
    pitch_class = pitch_classes[0]
    return tuple(
        (pitch_class, value)
        for value in signatures
        if value != pitch_class
    )


def _stable_note_key(row: Mapping[str, Any]) -> tuple[int, int, int, int]:
    return (
        int(row["step"]),
        int(row["midi"]),
        int(row.get("stringIndex", -1)),
        int(row.get("fret", -1)),
    )


def same_measure_joint_correction_pairs(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Pair fit-only notes that require both pitch and onset correction.

    Exact pitch+step matches are removed first within each measure. Remaining
    generated/reference rows are greedily paired by smallest absolute step delta,
    then smallest absolute MIDI delta, with stable row-key tie-breaking. A pair is
    eligible only when both deltas are non-zero and inside the pre-registered bounds.

    This is construction-time calibration logic only. Runtime application never
    receives a reference row.
    """
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    if maximum_pitch < 1 or maximum_pitch > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if maximum_step < 1 or maximum_step > 2:
        raise ValueError("maximum_abs_step_shift must be in [1, 2]")

    generated_by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    reference_by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in generated_notes:
        generated_by_measure[int(row["measure"])].append(dict(row))
    for row in reference_notes:
        reference_by_measure[int(row["measure"])].append(dict(row))

    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for measure in sorted(set(generated_by_measure) | set(reference_by_measure)):
        generated = sorted(generated_by_measure[measure], key=_stable_note_key)
        reference = sorted(reference_by_measure[measure], key=_stable_note_key)

        used_reference: set[int] = set()
        unmatched_generated: list[dict[str, Any]] = []
        for generated_row in generated:
            exact_index = next(
                (
                    index
                    for index, reference_row in enumerate(reference)
                    if index not in used_reference
                    and int(reference_row["step"]) == int(generated_row["step"])
                    and int(reference_row["midi"]) == int(generated_row["midi"])
                ),
                None,
            )
            if exact_index is None:
                unmatched_generated.append(generated_row)
            else:
                used_reference.add(exact_index)

        unmatched_reference = [
            row for index, row in enumerate(reference) if index not in used_reference
        ]
        pair_candidates: list[
            tuple[int, int, tuple[int, int, int, int], tuple[int, int, int, int], int, int]
        ] = []
        for generated_index, generated_row in enumerate(unmatched_generated):
            for reference_index, reference_row in enumerate(unmatched_reference):
                semitone_shift = int(reference_row["midi"]) - int(generated_row["midi"])
                step_shift = int(reference_row["step"]) - int(generated_row["step"])
                if semitone_shift == 0 or step_shift == 0:
                    continue
                if abs(semitone_shift) > maximum_pitch or abs(step_shift) > maximum_step:
                    continue
                pair_candidates.append(
                    (
                        abs(step_shift),
                        abs(semitone_shift),
                        _stable_note_key(generated_row),
                        _stable_note_key(reference_row),
                        generated_index,
                        reference_index,
                    )
                )

        pair_candidates.sort()
        used_generated: set[int] = set()
        used_unmatched_reference: set[int] = set()
        for _, _, _, _, generated_index, reference_index in pair_candidates:
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


def _eligible_for_joint_shift(
    event: Mapping[str, Any], semitone_shift: int, step_shift: int
) -> bool:
    if has_pitch_linkage(event):
        return False
    _, fret, _ = _validate_event_position(event)
    shifted_fret = fret + int(semitone_shift)
    shifted_step = int(event["step"]) + int(step_shift)
    return 0 <= shifted_fret <= 36 and 0 <= shifted_step <= 15


def event_matches_pitch_step_rule(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    if len(signatures) != 2:
        raise ValueError("a V144 joint pitch-step rule requires exactly two signatures")
    normalized = tuple(sorted(str(value) for value in signatures))
    if len(set(normalized)) != 2:
        raise ValueError("joint pitch-step signatures must be distinct")
    if sum(value.startswith("pitchClass::") for value in normalized) != 1:
        raise ValueError("joint pitch-step rule requires exactly one source pitch-class signature")
    available = set(context_signature(event))
    return all(value in available for value in normalized)


def rank_fit_pitch_step_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
) -> list[dict[str, Any]]:
    """Construct/rank joint pitch+step rules solely from current-baseline fit labels."""
    minimum_support = int(minimum_correction_support)
    maximum = int(maximum_candidates)
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")
    if maximum_pitch < 1 or maximum_pitch > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if maximum_step < 1 or maximum_step > 2:
        raise ValueError("maximum_abs_step_shift must be in [1, 2]")

    correction_support: Counter[tuple[tuple[str, str], int, int]] = Counter()
    for generated_row, reference_row in same_measure_joint_correction_pairs(
        fit_generated,
        fit_reference,
        maximum_abs_semitone_shift=maximum_pitch,
        maximum_abs_step_shift=maximum_step,
    ):
        semitone_shift = int(reference_row["midi"]) - int(generated_row["midi"])
        step_shift = int(reference_row["step"]) - int(generated_row["step"])
        if semitone_shift == 0 or step_shift == 0:
            raise ValueError("joint correction pairing emitted a zero shift")
        if not _eligible_for_joint_shift(generated_row, semitone_shift, step_shift):
            continue
        for signatures in _rule_signatures(generated_row):
            correction_support[(signatures, semitone_shift, step_shift)] += 1

    candidates: list[dict[str, Any]] = []
    for (signatures, semitone_shift, step_shift), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = sum(
            1
            for row in fit_generated
            if event_matches_pitch_step_rule(row, signatures)
            and _eligible_for_joint_shift(row, semitone_shift, step_shift)
        )
        if eligible_support < support or eligible_support <= 0:
            raise ValueError(
                "invalid joint eligible support "
                f"signatures={signatures!r} pitch={semitone_shift} step={step_shift}"
            )
        candidates.append(
            {
                "signatures": list(signatures),
                "semitoneShift": int(semitone_shift),
                "stepShift": int(step_shift),
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
            abs(int(item["stepShift"])),
            abs(int(item["semitoneShift"])),
            int(item["stepShift"]),
            int(item["semitoneShift"]),
            tuple(item["signatures"]),
        )
    )
    return candidates[:maximum]


def apply_pitch_step_rule(
    events: Sequence[Mapping[str, Any]],
    signatures: Sequence[str],
    semitone_shift: int,
    step_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
) -> list[dict[str, Any]]:
    """Apply a reference-free same-string pitch+within-measure onset correction."""
    pitch_shift = int(semitone_shift)
    timing_shift = int(step_shift)
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    if (
        pitch_shift == 0
        or abs(pitch_shift) > maximum_pitch
        or maximum_pitch < 1
        or maximum_pitch > 12
    ):
        raise ValueError("semitone_shift must be non-zero and within [1, 12]")
    if (
        timing_shift == 0
        or abs(timing_shift) > maximum_step
        or maximum_step < 1
        or maximum_step > 2
    ):
        raise ValueError("step_shift must be non-zero and within [1, 2]")

    transformed: list[dict[str, Any]] = []
    for event in events:
        row = dict(event)
        if event_matches_pitch_step_rule(row, signatures) and _eligible_for_joint_shift(
            row, pitch_shift, timing_shift
        ):
            _, fret, midi = _validate_event_position(row)
            row["fret"] = fret + pitch_shift
            row["midi"] = midi + pitch_shift
            row["step"] = int(row["step"]) + timing_shift
        transformed.append(row)
    return transformed


__all__ = [
    "DEFAULT_MAX_ABS_SEMITONE_SHIFT",
    "DEFAULT_MAX_ABS_STEP_SHIFT",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "apply_pitch_step_rule",
    "event_matches_pitch_step_rule",
    "rank_fit_pitch_step_rules",
    "same_measure_joint_correction_pairs",
]
