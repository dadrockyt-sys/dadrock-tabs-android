from __future__ import annotations

from typing import Any

try:
    from bass_technique_diagnostics_v7 import (
        detect_reference_guided_bass_techniques,
    )
except ImportError:
    from analyzer.bass_technique_diagnostics_v7 import (
        detect_reference_guided_bass_techniques,
    )


def attach_bass_technique_diagnostics(
    result: dict[str, Any],
    transcription_type: str,
    *,
    enable_reference_guided_techniques: bool = False,
) -> dict[str, Any]:
    """Attach read-only V7 bass-technique diagnostics when explicitly enabled.

    Generic bass, rhythm, and lead responses are unchanged unless the caller
    opts in for a bass transcription. The helper reads the existing event list
    and adds a separate diagnostics object; it never replaces events or changes
    generated tablature.
    """

    if (
        transcription_type != "bass"
        or not enable_reference_guided_techniques
    ):
        return result

    events = result.get("events")
    normalized_events = events if isinstance(events, list) else []

    enriched_result = dict(result)
    enriched_result["bassTechniqueAnalysis"] = (
        detect_reference_guided_bass_techniques(normalized_events)
    )
    enriched_result["bassTechniqueAnalysisMode"] = "diagnostic-only"
    enriched_result["bassTechniqueAnalysisAffectsTab"] = False
    enriched_result["bassTechniqueAnalysisAffectsEvents"] = False

    return enriched_result
