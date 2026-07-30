#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from production_lead_technique_diagnostics import (
        attach_lead_technique_diagnostics,
    )
except ImportError:
    from analyzer.production_lead_technique_diagnostics import (
        attach_lead_technique_diagnostics,
    )


def sample_events() -> list[dict]:
    return [
        {"start": 0.00, "end": 0.30, "midi": 69, "fret": 14},
        {"start": 0.42, "end": 0.70, "midi": 67, "fret": 12},
        {"start": 1.00, "end": 1.20, "midi": 67, "fret": 12},
        {"start": 1.24, "end": 1.44, "midi": 69, "fret": 14},
        {"start": 1.48, "end": 1.68, "midi": 67, "fret": 12},
    ]


def main() -> None:
    base = {
        "generatedTab": "protected-tab",
        "events": sample_events(),
        "noteCount": 5,
    }
    original = deepcopy(base)

    generic_lead = attach_lead_technique_diagnostics(
        deepcopy(base),
        "lead",
    )
    contextual_lead = attach_lead_technique_diagnostics(
        deepcopy(base),
        "lead",
        enable_reference_guided_techniques=True,
        bend_evidence_present=True,
    )
    rhythm = attach_lead_technique_diagnostics(
        deepcopy(base),
        "rhythm",
        enable_reference_guided_techniques=True,
        bend_evidence_present=True,
    )
    bass = attach_lead_technique_diagnostics(
        deepcopy(base),
        "bass",
        enable_reference_guided_techniques=True,
        bend_evidence_present=True,
    )

    analysis = contextual_lead.get("leadTechniqueAnalysis") or {}
    checks = {
        "genericLeadUnchanged": generic_lead == base,
        "contextualLeadEnabled": contextual_lead.get(
            "leadTechniqueAnalysisMode"
        ) == "diagnostic-only",
        "detectsBend": analysis.get("bendDetected") is True,
        "detectsRelease": analysis.get("releaseDetected") is True,
        "detectsPalmMute": analysis.get("palmMuteDetected") is True,
        "requiresExistingBendEvidence": analysis.get(
            "bendEvidencePresent"
        ) is True,
        "tabUnchanged": contextual_lead.get("generatedTab") == base["generatedTab"],
        "eventsUnchanged": contextual_lead.get("events") == base["events"],
        "noteCountUnchanged": contextual_lead.get("noteCount") == base["noteCount"],
        "noSyntheticNotes": analysis.get("syntheticNoteCount") == 0,
        "doesNotAffectTab": analysis.get("affectsTab") is False,
        "doesNotAffectEvents": analysis.get("affectsEvents") is False,
        "rhythmUntouched": rhythm == base,
        "bassUntouched": bass == base,
        "inputUnchanged": base == original,
    }

    failed = False
    print("JIMMY PAIGE V7 PRODUCTION LEAD-TECHNIQUE ADAPTER")
    print("=" * 68)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 production lead-technique adapter regression detected."
        )

    print("\nV7 PRODUCTION LEAD-TECHNIQUE ADAPTER PRESERVED 💚")
    print("Generic lead is unchanged; reference-guided techniques are opt-in.")
    print("Rhythm, bass, tab, events, and note count remain untouched.")


if __name__ == "__main__":
    main()
