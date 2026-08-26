from __future__ import annotations

from typing import Any, Mapping, Sequence


def generated_measure_ids(events: Sequence[Mapping[str, Any]]) -> tuple[int, ...]:
    measures: set[int] = set()
    for event in events:
        measure = int(event["measure"])
        if measure < 1:
            raise ValueError(f"invalid generated measure {measure}")
        measures.add(measure)
    if not measures:
        raise ValueError("generated event stream must contain at least one measure")
    return tuple(sorted(measures))


def measure_set_evidence(
    baseline_events: Sequence[Mapping[str, Any]],
    candidate_events: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Compare generated measure IDs only; no professional reference is consulted."""
    baseline = generated_measure_ids(baseline_events)
    candidate = generated_measure_ids(candidate_events)
    baseline_set = set(baseline)
    candidate_set = set(candidate)
    missing = sorted(baseline_set - candidate_set)
    extra = sorted(candidate_set - baseline_set)
    preserved = not missing and not extra
    return {
        "baselineGeneratedMeasureIds": list(baseline),
        "candidateGeneratedMeasureIds": list(candidate),
        "baselineGeneratedMeasureCount": len(baseline),
        "candidateGeneratedMeasureCount": len(candidate),
        "missingBaselineGeneratedMeasures": missing,
        "extraCandidateGeneratedMeasures": extra,
        "baselineGeneratedMeasureSetPreserved": preserved,
        "professionalReferenceUsed": False,
    }


__all__ = ["generated_measure_ids", "measure_set_evidence"]
