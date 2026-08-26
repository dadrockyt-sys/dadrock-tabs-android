from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from v144_rhythm_context_split_policy import context_signature

DEFAULT_MIN_FALSE_POSITIVE_SUPPORT = 3
DEFAULT_MAX_CANDIDATES = 384


def triple_signatures(row: Mapping[str, Any]) -> tuple[tuple[str, str, str], ...]:
    signatures = context_signature(row)
    return tuple(
        (first, second, third)
        for first, second, third in combinations(signatures, 3)
    )


def rank_fit_triples(
    fit_unmatched_generated: Sequence[Mapping[str, Any]],
    fit_generated: Sequence[Mapping[str, Any]],
    *,
    minimum_false_positive_support: int = DEFAULT_MIN_FALSE_POSITIVE_SUPPORT,
    maximum_candidates: int = DEFAULT_MAX_CANDIDATES,
) -> list[dict[str, Any]]:
    """Construct/rank triple rules solely from fit rows."""
    minimum_support = int(minimum_false_positive_support)
    maximum = int(maximum_candidates)
    if minimum_support < 1:
        raise ValueError("minimum_false_positive_support must be >= 1")
    if maximum < 1:
        raise ValueError("maximum_candidates must be >= 1")

    false_positive_support: Counter[tuple[str, str, str]] = Counter()
    total_fit_support: Counter[tuple[str, str, str]] = Counter()
    for row in fit_unmatched_generated:
        false_positive_support.update(triple_signatures(row))
    for row in fit_generated:
        total_fit_support.update(triple_signatures(row))

    candidates: list[dict[str, Any]] = []
    for triple, fp_support in false_positive_support.items():
        if fp_support < minimum_support:
            continue
        total_support = int(total_fit_support[triple])
        if total_support < fp_support or total_support <= 0:
            raise ValueError(f"invalid fit support for triple {triple!r}")
        candidates.append(
            {
                "signatures": list(triple),
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


def event_matches_triple(
    event: Mapping[str, Any], signatures: Sequence[str]
) -> bool:
    if len(signatures) != 3:
        raise ValueError("a V144 triple rule requires exactly three signatures")
    normalized = sorted(str(value) for value in signatures)
    if len(set(normalized)) != 3:
        raise ValueError("triple signatures must be distinct")
    available = set(context_signature(event))
    return all(signature in available for signature in normalized)


def apply_triple_prune(
    events: Sequence[Mapping[str, Any]], signatures: Sequence[str]
) -> list[dict[str, Any]]:
    """Reference-free runtime transform using event structural context only."""
    return [
        dict(event)
        for event in events
        if not event_matches_triple(event, signatures)
    ]


__all__ = [
    "DEFAULT_MAX_CANDIDATES",
    "DEFAULT_MIN_FALSE_POSITIVE_SUPPORT",
    "apply_triple_prune",
    "event_matches_triple",
    "rank_fit_triples",
    "triple_signatures",
]
