#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from production_bass_technique_diagnostics import (
        attach_bass_technique_diagnostics,
    )
except ImportError:
    from analyzer.production_bass_technique_diagnostics import (
        attach_bass_technique_diagnostics,
    )


def sample_events() -> list[dict]:
    return [
        {"start": 0.00, "end": 0.20, "midi": 40, "fret": 7},
        {"start": 0.30, "end": 0.50, "midi": 38, "fret": 5},
        {"start": 0.62, "end": 0.82, "midi": 40, "fret": 7},
        {"start": 1.75, "end": 1.95, "midi": 38, "fret": 5},
    ]


def main() -> None:
    base = {
        "generatedTab": "E|---7---5---7---5---|",
        "events": sample_events(),
    }
    before = deepcopy(base)

    generic = attach_bass_technique_diagnostics(
        deepcopy(base),
        "bass",
        enable_reference_guided_techniques=False,
    )
    contextual = attach_bass_technique_diagnostics(
        deepcopy(base),
        "bass",
        enable_reference_guided_techniques=True,
    )
    rhythm = attach_bass_technique_diagnostics(
        deepcopy(base),
        "rhythm",
        enable_reference_guided_techniques=True,
    )
    lead = attach_bass_technique_diagnostics(
        deepcopy(base),
        "lead",
        enable_reference_guided_techniques=True,
    )

    analysis = contextual.get("bassTechniqueAnalysis") or {}
    checks = {
        "genericBassUnchanged": generic == before,
        "contextualBassEnabled": (
            contextual.get("bassTechniqueAnalysisMode")
            == "diagnostic-only"
        ),
        "detectsFiveSevenContour": (
            analysis.get("fiveSevenContourDetected") is True
        ),
        "detectsSlideTarget": analysis.get("slideTargetDetected") is True,
        "detectsMutedAttack": analysis.get("mutedAttackDetected") is True,
        "detectsRest": analysis.get("restDetected") is True,
        "tabUnchanged": contextual.get("generatedTab") == before["generatedTab"],
        "eventsUnchanged": contextual.get("events") == before["events"],
        "noteCountUnchanged": (
            len(contextual.get("events") or []) == len(before["events"])
        ),
        "noSyntheticNotes": int(analysis.get("syntheticNoteCount") or 0) == 0,
        "doesNotAffectTab": (
            contextual.get("bassTechniqueAnalysisAffectsTab") is False
        ),
        "doesNotAffectEvents": (
            contextual.get("bassTechniqueAnalysisAffectsEvents") is False
        ),
        "rhythmUntouched": "bassTechniqueAnalysis" not in rhythm,
        "leadUntouched": "bassTechniqueAnalysis" not in lead,
    }

    failed = False
    print("JIMMY PAIGE V7 PRODUCTION BASS-TECHNIQUE ADAPTER")
    print("=" * 68)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit("\nV7 production bass-technique adapter regression detected.")

    print("\nV7 PRODUCTION BASS-TECHNIQUE ADAPTER PRESERVED 💚")
    print("Generic bass is unchanged; reference-guided techniques are opt-in.")
    print("Rhythm, lead, tab, events, and note count remain untouched.")


if __name__ == "__main__":
    main()
