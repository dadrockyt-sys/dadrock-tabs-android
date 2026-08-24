from __future__ import annotations

from typing import Any, Mapping, Sequence

from v143_contextual_prune_candidate_events import CorrectedCandidateAssembly, build_corrected_candidate_assembly
from v143_contextual_prune_precision_shadow import PrecisionShadowResult
from v143_contextual_prune_shadow_correction import ShadowCorrectionResult
from v143_reference_free_timing import ReferenceFreeTimingEstimate


EventKey = tuple[int, int]


def build_precision_candidate_assembly(
    carrier_rows: Sequence[Mapping[str, Any]],
    grid: Mapping[EventKey, float],
    precision: PrecisionShadowResult,
    timing: ReferenceFreeTimingEstimate,
) -> CorrectedCandidateAssembly:
    """Render only retained precision attacks/pitches through the proven adapter.

    The conversion intentionally carries no scorer/reference fields. It presents
    the precision result as a closed, already-observed attack/pitch set to the
    existing legal-guitar voicing adapter. No attack or pitch can be added here.
    """
    if not isinstance(precision, PrecisionShadowResult):
        raise TypeError("precision must be PrecisionShadowResult")
    proxy = ShadowCorrectionResult(
        base_events=frozenset(precision.retained_events),
        corrected_events=frozenset(precision.retained_events),
        rescued_events=frozenset(),
        original_pitch_sets=dict(precision.original_pitch_sets),
        pitch_sets=dict(precision.pitch_sets),
        suppressed_pitch_count=int(precision.suppressed_pitch_count),
        observed_slot_count=len(precision.input_events),
        strict_slot_count=len(precision.retained_events),
    )
    candidate = build_corrected_candidate_assembly(carrier_rows, grid, proxy, timing)
    emitted = {
        (int(event["measure"]), int(event["step"]))
        for event in candidate.assembly.events
    }
    if emitted != set(precision.retained_events):
        raise RuntimeError("Precision candidate adapter changed attack identity")
    for event in candidate.assembly.events:
        key = (int(event["measure"]), int(event["step"]))
        if int(event["midi"]) not in set(precision.pitch_sets[key]):
            raise RuntimeError(f"Precision candidate adapter invented pitch at {key}")
    return candidate


__all__ = ["build_precision_candidate_assembly"]
