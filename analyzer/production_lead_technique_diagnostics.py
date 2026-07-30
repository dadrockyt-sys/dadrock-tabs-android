from __future__ import annotations

from typing import Any

try:
    from lead_technique_diagnostics_v7 import (
        detect_reference_guided_lead_techniques,
    )
except ImportError:
    from analyzer.lead_technique_diagnostics_v7 import (
        detect_reference_guided_lead_techniques,
    )


def attach_lead_technique_diagnostics(
    result: dict[str, Any],
    transcription_type: str,
    *,
    enable_reference_guided_techniques: bool = False,
    bend_evidence_present: bool = False,
) -> dict[str, Any]:
    """Attach read-only V7 lead-technique diagnostics when explicitly enabled.

    Generic lead, rhythm, and bass responses are unchanged unless the caller
    opts in for a lead transcription. The helper reads the existing event list
    and adds a separate diagnostics object; it never replaces events or changes
    generated tablature.
    """

    if (
        transcription_type != "lead"
        or not enable_reference_guided_techniques
    ):
        return result

    events = result.get("events")
    normalized_events = events if isinstance(events, list) else []

    enriched_result = dict(result)
    enriched_result["leadTechniqueAnalysis"] = (
        detect_reference_guided_lead_techniques(
            normalized_events,
            bend_evidence_present=bool(bend_evidence_present),
        )
    )
    enriched_result["leadTechniqueAnalysisMode"] = "diagnostic-only"
    enriched_result["leadTechniqueAnalysisAffectsTab"] = False
    enriched_result["leadTechniqueAnalysisAffectsEvents"] = False

    return enriched_result
