#!/usr/bin/env python3
from __future__ import annotations

from copy import deepcopy

try:
    from lead_technique_diagnostics_v7 import (
        detect_reference_guided_lead_techniques,
    )
except ImportError:
    from analyzer.lead_technique_diagnostics_v7 import (
        detect_reference_guided_lead_techniques,
    )


def synthetic_lead_events() -> list[dict]:
    return [
        {"start": 0.00, "end": 0.22, "midi": 78, "fret": 14},
        {"start": 0.28, "end": 0.50, "midi": 76, "fret": 12},
        {"start": 0.75, "end": 0.92, "midi": 76, "fret": 12},
        {"start": 1.00, "end": 1.18, "midi": 78, "fret": 14},
        {"start": 1.30, "end": 1.46, "midi": 76, "fret": 12},
    ]


def main() -> None:
    events = synthetic_lead_events()
    before = deepcopy(events)
    diagnostics = detect_reference_guided_lead_techniques(
        events,
        bend_evidence_present=True,
    )

    without_bend = detect_reference_guided_lead_techniques(
        events,
        bend_evidence_present=False,
    )

    checks = {
        "detectsFullBendRelease": diagnostics.get("bendDetected") is True
        and diagnostics.get("releaseDetected") is True,
        "findsOneReleasePair": diagnostics.get("releasePairCount") == 1,
        "detectsPalmMutedCell": diagnostics.get("palmMuteDetected") is True
        and int(diagnostics.get("palmMutedEventCount") or 0) >= 2,
        "requiresBendEvidence": without_bend.get("releasePairCount") == 0,
        "eventsReadOnly": events == before
        and diagnostics.get("eventsReadOnly") is True,
        "eventCountUnchanged": diagnostics.get("eventCount") == len(events),
        "noSyntheticNotes": diagnostics.get("syntheticNoteCount") == 0,
        "pitchOrFretUnchanged": diagnostics.get("pitchOrFretChanged") is False,
        "doesNotAffectEvents": diagnostics.get("affectsEvents") is False,
        "doesNotAffectTab": diagnostics.get("affectsTab") is False,
    }

    failed = False
    print("JIMMY PAIGE V7 LEAD TECHNIQUE DIAGNOSTICS HELPER")
    print("=" * 68)
    for name, passed in checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if failed:
        raise SystemExit("\nV7 lead technique diagnostics regression detected.")

    print("\nV7 LEAD TECHNIQUE DIAGNOSTICS HELPER PRESERVED 💚")
    print("14→12 bend/release and later 12/14 palm muting are diagnostic-only.")
    print("Events, frets, pitches, timing, and generated tab remain untouched.")


if __name__ == "__main__":
    main()
