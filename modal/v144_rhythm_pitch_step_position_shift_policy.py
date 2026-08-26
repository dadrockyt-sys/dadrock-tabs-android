from __future__ import annotations

from collections import Counter
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature
from v144_rhythm_pitch_shift_policy import OPEN_MIDI_BY_STRING_INDEX, has_pitch_linkage
from v144_rhythm_pitch_step_shift_policy import same_measure_joint_correction_pairs

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
DEFAULT_MAX_ABS_SEMITONE_SHIFT = 12
DEFAULT_MAX_ABS_STEP_SHIFT = 2
DEFAULT_MAX_ABS_STRING_SHIFT = 1


def _rule_signatures(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    signatures = context_signature(row)
    pitch_classes = tuple(value for value in signatures if value.startswith("pitchClass::"))
    if len(pitch_classes) != 1:
        raise ValueError("joint pitch-step-position construction requires exactly one pitch-class signature")
    pitch_class = pitch_classes[0]
    return tuple((pitch_class, value) for value in signatures if value != pitch_class)


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


def _target_state(
    event: Mapping[str, Any],
    semitone_shift: int,
    step_shift: int,
    string_shift: int,
) -> tuple[int, int, int, int] | None:
    if has_pitch_linkage(event):
        return None
    source_string, _, source_midi = _validate_event_position(event)
    target_step = int(event["step"]) + int(step_shift)
    target_string = source_string + int(string_shift)
    target_midi = source_midi + int(semitone_shift)
    if not 0 <= target_step <= 15:
        return None
    if target_string not in OPEN_MIDI_BY_STRING_INDEX:
        return None
    target_fret = target_midi - OPEN_MIDI_BY_STRING_INDEX[target_string]
    if not 0 <= target_fret <= 36:
        return None
    return target_step, target_string, target_fret, target_midi


def event_matches_pitch_step_position_rule(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    if len(signatures) != 2:
        raise ValueError("a V144 joint pitch-step-position rule requires exactly two signatures")
    normalized = tuple(sorted(str(value) for value in signatures))
    if len(set(normalized)) != 2:
        raise ValueError("joint pitch-step-position signatures must be distinct")
    if sum(value.startswith("pitchClass::") for value in normalized) != 1:
        raise ValueError("joint pitch-step-position rule requires exactly one source pitch-class signature")
    available = set(context_signature(event))
    return all(value in available for value in normalized)


def same_measure_pitch_step_position_pairs(
    generated_notes: Sequence[Mapping[str, Any]],
    reference_notes: Sequence[Mapping[str, Any]],
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
    maximum_abs_string_shift: int = DEFAULT_MAX_ABS_STRING_SHIFT,
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Return fit-only pairs requiring pitch, step and adjacent-string changes.

    The deterministic base pairing is the already pre-registered same-measure
    pitch+step pairing. This materially new family then retains only pairs whose
    reference target also requires a non-zero adjacent-string move and exactly
    matches the tuning-derived target fret. Runtime never receives reference rows.
    """
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    maximum_string = int(maximum_abs_string_shift)
    if maximum_pitch < 1 or maximum_pitch > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if maximum_step < 1 or maximum_step > 2:
        raise ValueError("maximum_abs_step_shift must be in [1, 2]")
    if maximum_string != 1:
        raise ValueError("maximum_abs_string_shift is preregistered at exactly 1")

    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for generated_row, reference_row in same_measure_joint_correction_pairs(
        generated_notes,
        reference_notes,
        maximum_abs_semitone_shift=maximum_pitch,
        maximum_abs_step_shift=maximum_step,
    ):
        semitone_shift = int(reference_row["midi"]) - int(generated_row["midi"])
        step_shift = int(reference_row["step"]) - int(generated_row["step"])
        string_shift = int(reference_row["stringIndex"]) - int(generated_row["stringIndex"])
        if semitone_shift == 0 or step_shift == 0 or string_shift == 0:
            continue
        if abs(string_shift) > maximum_string:
            continue
        target = _target_state(generated_row, semitone_shift, step_shift, string_shift)
        if target is None:
            continue
        target_step, target_string, target_fret, target_midi = target
        if target_step != int(reference_row["step"]):
            continue
        if target_string != int(reference_row["stringIndex"]):
            continue
        if target_fret != int(reference_row["fret"]):
            continue
        if target_midi != int(reference_row["midi"]):
            continue
        result.append((dict(generated_row), dict(reference_row)))
    return result


def rank_fit_pitch_step_position_rules(
    fit_generated: Sequence[Mapping[str, Any]],
    fit_reference: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
    maximum_abs_string_shift: int = DEFAULT_MAX_ABS_STRING_SHIFT,
) -> list[dict[str, Any]]:
    minimum_support = int(minimum_correction_support)
    maximum = int(maximum_candidates)
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    maximum_string = int(maximum_abs_string_shift)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")
    if maximum_pitch < 1 or maximum_pitch > 12:
        raise ValueError("maximum_abs_semitone_shift must be in [1, 12]")
    if maximum_step < 1 or maximum_step > 2:
        raise ValueError("maximum_abs_step_shift must be in [1, 2]")
    if maximum_string != 1:
        raise ValueError("maximum_abs_string_shift is preregistered at exactly 1")

    correction_support: Counter[tuple[tuple[str, str], int, int, int]] = Counter()
    for generated_row, reference_row in same_measure_pitch_step_position_pairs(
        fit_generated,
        fit_reference,
        maximum_abs_semitone_shift=maximum_pitch,
        maximum_abs_step_shift=maximum_step,
        maximum_abs_string_shift=maximum_string,
    ):
        semitone_shift = int(reference_row["midi"]) - int(generated_row["midi"])
        step_shift = int(reference_row["step"]) - int(generated_row["step"])
        string_shift = int(reference_row["stringIndex"]) - int(generated_row["stringIndex"])
        for signatures in _rule_signatures(generated_row):
            correction_support[(signatures, semitone_shift, step_shift, string_shift)] += 1

    candidates: list[dict[str, Any]] = []
    for (signatures, semitone_shift, step_shift, string_shift), support in correction_support.items():
        if support < minimum_support:
            continue
        eligible_support = sum(
            1
            for row in fit_generated
            if event_matches_pitch_step_position_rule(row, signatures)
            and _target_state(row, semitone_shift, step_shift, string_shift) is not None
        )
        if eligible_support < support or eligible_support <= 0:
            raise ValueError("invalid pitch-step-position eligible support")
        candidates.append(
            {
                "signatures": list(signatures),
                "semitoneShift": int(semitone_shift),
                "stepShift": int(step_shift),
                "stringShift": int(string_shift),
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
            int(item["stringShift"]),
            int(item["stepShift"]),
            int(item["semitoneShift"]),
            tuple(item["signatures"]),
        )
    )
    return candidates[:maximum]


def apply_pitch_step_position_rule(
    events: Sequence[Mapping[str, Any]],
    signatures: Sequence[str],
    semitone_shift: int,
    step_shift: int,
    string_shift: int,
    *,
    maximum_abs_semitone_shift: int = DEFAULT_MAX_ABS_SEMITONE_SHIFT,
    maximum_abs_step_shift: int = DEFAULT_MAX_ABS_STEP_SHIFT,
    maximum_abs_string_shift: int = DEFAULT_MAX_ABS_STRING_SHIFT,
) -> list[dict[str, Any]]:
    pitch_shift = int(semitone_shift)
    timing_shift = int(step_shift)
    position_shift = int(string_shift)
    maximum_pitch = int(maximum_abs_semitone_shift)
    maximum_step = int(maximum_abs_step_shift)
    maximum_string = int(maximum_abs_string_shift)
    if maximum_pitch < 1 or maximum_pitch > 12 or pitch_shift == 0 or abs(pitch_shift) > maximum_pitch:
        raise ValueError("semitone_shift must be non-zero and within [1, 12]")
    if maximum_step < 1 or maximum_step > 2 or timing_shift == 0 or abs(timing_shift) > maximum_step:
        raise ValueError("step_shift must be non-zero and within [1, 2]")
    if maximum_string != 1 or position_shift not in (-1, 1):
        raise ValueError("string_shift must be non-zero and adjacent-string only")

    transformed: list[dict[str, Any]] = []
    for event in events:
        row = dict(event)
        if event_matches_pitch_step_position_rule(row, signatures):
            target = _target_state(row, pitch_shift, timing_shift, position_shift)
            if target is not None:
                target_step, target_string, target_fret, target_midi = target
                row["step"] = target_step
                row["stringIndex"] = target_string
                row["fret"] = target_fret
                row["midi"] = target_midi
        transformed.append(row)
    return transformed


__all__ = [
    "DEFAULT_MAX_ABS_SEMITONE_SHIFT",
    "DEFAULT_MAX_ABS_STEP_SHIFT",
    "DEFAULT_MAX_ABS_STRING_SHIFT",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "apply_pitch_step_position_rule",
    "event_matches_pitch_step_position_rule",
    "rank_fit_pitch_step_position_rules",
    "same_measure_pitch_step_position_pairs",
]
