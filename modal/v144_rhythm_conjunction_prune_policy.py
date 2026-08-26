from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature

DEFAULT_MIN_FALSE_POSITIVE_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 256


def conjunction_pairs(row: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    signatures = context_signature(row)
    return tuple((left, right) for left, right in combinations(signatures, 2))


def rank_fit_conjunctions(
    fit_unmatched_generated: Sequence[Mapping[str, Any]],
    fit_generated: Sequence[Mapping[str, Any]],
    *,
    minimum_false_positive_support: int = DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Construct candidates solely from fit rows; no validation/canary inputs exist."""
    minimum_support = int(minimum_false_positive_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1:
        raise ValueError("minimum_false_positive_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")

    false_positive_support: Counter[tuple[str, str]] = Counter()
    total_fit_support: Counter[tuple[str, str]] = Counter()

    for row in fit_unmatched_generated:
        false_positive_support.update(conjunction_pairs(row))
    for row in fit_generated:
        total_fit_support.update(conjunction_pairs(row))

    candidates: list[dict[str, Any]] = []
    for pair, fp_support in false_positive_support.items():
        if fp_support < minimum_support:
            continue
        total_support = int(total_fit_support[pair])
        if total_support < fp_support or total_support <= 0:
            raise ValueError(f"invalid fit support for conjunction {pair!r}")
        candidates.append(
            {
                "signatures": [pair[0], pair[1]],
                "fitFalsePositiveSupport": int(fp_support),
                "fitTotalGeneratedSupport": total_support,
                "fitFalsePositivePrecision": float(fp_support) / float(total_support),
            }
        )

    candidates.sort(
        key=lambda item: (
            -float(item["fitFalsePositivePrecision"]),
            -int(item["fitFalsePositiveSupport"]),
            int(item["fitTotalGeneratedSupport"]),
            tuple(item["signatures"]),
        )
    )
    return candidates[:maximum]


def event_matches_conjunction(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    if len(signatures) != 2:
        raise ValueError("a V144 conjunction rule requires exactly two signatures")
    left, right = sorted(str(value) for value in signatures)
    if left == right:
        raise ValueError("conjunction signatures must be distinct")
    available = set(context_signature(event))
    return left in available and right in available


def apply_conjunction_prune(
    events: Sequence[Mapping[str, Any]], signatures: Sequence[str]
) -> list[dict[str, Any]]:
    """Reference-free runtime transform: only event context is inspected."""
    return [
        dict(event)
        for event in events
        if not event_matches_conjunction(event, signatures)
    ]


__all__ = [
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_FALSE_POSITIVE_SUPPORT",
    "apply_conjunction_prune",
    "conjunction_pairs",
    "event_matches_conjunction",
    "rank_fit_conjunctions",
]
