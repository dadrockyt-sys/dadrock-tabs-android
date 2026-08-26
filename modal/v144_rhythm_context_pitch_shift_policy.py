from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature

DEFAULT_MIN_CORRECTION_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256
MAX_ABS_SEMITONE_SHIFT = 12
OPEN_MIDI_BY_STRING_INDEX = {0: 64, 1: 59, 2: 55, 3: 50, 4: 45, 5: 40}
LINKAGE_FIELDS = (
    "bendSemitones",
    "bendTargetFret",
    "bendTargetMidi",
    "legatoTargetEventIndex",
    "legatoTargetFret",
    "legatoTargetMidi",
    "legatoContinuationFromEventIndex",
    "legatoContinuationType",
)
BLOCKED_TECHNIQUE_TOKENS = ("bend", "hammer", "pull", "slide", "legato")


def signature_pairs(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    """Return deterministic two-signature runtime contexts for one generated row."""
    return tuple(tuple(values) for values in combinations(context_signature(row), 2))


def normalize_signature_pair(signatures: Sequence[str]) -> tuple[str, str]:
    if len(signatures) != 2:
        raise ValueError("a V144 context pitch-shift rule requires exactly two signatures")
    normalized = tuple(sorted(str(value) for value in signatures))
    if len(set(normalized)) != 2:
        raise ValueError("pitch-shift signatures must be distinct")
    return normalized


def normalize_delta(delta: int) -> int:
    value = int(delta)
    if value == 0:
        raise ValueError("pitch-shift delta must be non-zero")
    if abs(value) > MAX_ABS_SEMITONE_SHIFT:
        raise ValueError(
            f"pitch-shift delta must be within +/-{MAX_ABS_SEMITONE_SHIFT} semitones"
        )
    return value


def has_pitch_linkage(event: Mapping[str, Any]) -> bool:
    """Reject events whose technique/link targets would need coordinated rewriting."""
    for key in LINKAGE_FIELDS:
        value = event.get(key)
        if value is not None and value != "":
            return True
    techniques = event.get("techniques")
    if isinstance(techniques, Sequence) and not isinstance(techniques, (str, bytes)):
        for technique in techniques:
            label = str(technique).strip().lower()
            if any(token in label for token in BLOCKED_TECHNIQUE_TOKENS):
                return True
    return False


def event_is_shift_safe(event: Mapping[str, Any], delta: int) -> bool:
    """Return whether a same-string semitone shift preserves the V143 pitch-position contract."""
    shift = normalize_delta(delta)
    if has_pitch_linkage(event):
        return False
    try:
        string_index = int(event["stringIndex"])
        fret = int(event["fret"])
        midi = int(event["midi"])
    except (KeyError, TypeError, ValueError):
        return False
    if string_index not in OPEN_MIDI_BY_STRING_INDEX:
        return False
    if fret < 0 or fret > 36:
        return False
    if midi != OPEN_MIDI_BY_STRING_INDEX[string_index] + fret:
        return False
    shifted_fret = fret + shift
    return 0 <= shifted_fret <= 36


def event_matches_signature_pair(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    normalized = normalize_signature_pair(signatures)
    available = set(context_signature(event))
    return all(signature in available for signature in normalized)


def apply_context_pitch_shift(
    events: Sequence[Mapping[str, Any]],
    signatures: Sequence[str],
    delta: int,
) -> list[dict[str, Any]]:
    """Apply one reference-free same-string correction rule without deleting/moving events."""
    normalized = normalize_signature_pair(signatures)
    shift = normalize_delta(delta)
    output: list[dict[str, Any]] = []
    for source in events:
        event = dict(source)
        if event_matches_signature_pair(event, normalized) and event_is_shift_safe(event, shift):
            event["fret"] = int(event["fret"]) + shift
            event["midi"] = int(event["midi"]) + shift
        output.append(event)
    return output


def rank_fit_pitch_shift_rules(
    fit_correction_rows: Sequence[Mapping[str, Any]],
    fit_generated: Sequence[Mapping[str, Any]],
    *,
    minimum_correction_support: int = DEFAULT_MIN_CORRECTION_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Rank pair+delta rules solely from caller-supplied fit correction evidence.

    Each correction row must be the generated row augmented with ``targetDelta``.
    No validation/canary/reference object is accepted by this runtime policy helper.
    """
    minimum_support = int(minimum_correction_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1:
        raise ValueError("minimum_correction_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")

    correction_support: Counter[tuple[tuple[str, str], int]] = Counter()
    deltas: set[int] = set()
    for row in fit_correction_rows:
        if "targetDelta" not in row:
            raise ValueError("fit correction row missing targetDelta")
        delta = normalize_delta(int(row["targetDelta"]))
        if not event_is_shift_safe(row, delta):
            continue
        deltas.add(delta)
        for pair in signature_pairs(row):
            correction_support[(pair, delta)] += 1

    if not correction_support:
        return []

    total_support: Counter[tuple[tuple[str, str], int]] = Counter()
    for row in fit_generated:
        pairs = signature_pairs(row)
        for delta in sorted(deltas):
            if not event_is_shift_safe(row, delta):
                continue
            for pair in pairs:
                total_support[(pair, delta)] += 1

    candidates: list[dict[str, Any]] = []
    for (pair, delta), support in correction_support.items():
        if support < minimum_support:
            continue
        total = int(total_support[(pair, delta)])
        if total < support or total <= 0:
            raise ValueError(f"invalid fit support for pitch-shift rule {pair!r} delta={delta}")
        candidates.append(
            {
                "signatures": list(pair),
                "semitoneDelta": int(delta),
                "fitCorrectionSupport": int(support),
                "fitTotalEligibleSupport": total,
                "fitCorrectionPrecision": float(support) / float(total),
            }
        )

    candidates.sort(
        key=lambda item: (
            -float(item["fitCorrectionPrecision"]),
            -int(item["fitCorrectionSupport"]),
            int(item["fitTotalEligibleSupport"]),
            abs(int(item["semitoneDelta"])),
            int(item["semitoneDelta"]),
            tuple(item["signatures"]),
        )
    )
    return candidates[:maximum]


__all__ = [
    "BLOCKED_TECHNIQUE_TOKENS",
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_CORRECTION_SUPPORT",
    "LINKAGE_FIELDS",
    "MAX_ABS_SEMITONE_SHIFT",
    "apply_context_pitch_shift",
    "event_is_shift_safe",
    "event_matches_signature_pair",
    "has_pitch_linkage",
    "normalize_delta",
    "normalize_signature_pair",
    "rank_fit_pitch_shift_rules",
    "signature_pairs",
]
