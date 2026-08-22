#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        default="/tmp/gomyway-v7-combined-full-stack-report.json",
    )
    args = parser.parse_args()
    report = load_json(Path(args.report))
    checks = report.get("checks") or {}

    expected_checks = [
        "rhythmGenericHasNoReferenceMode",
        "rhythmContextEnabled",
        "rhythmPromotesE",
        "rhythmPromotesG",
        "rhythmPreservesG6",
        "rhythmPreservesATp2",
        "rhythmProductionUnchanged",
        "leadGenericUnchanged",
        "leadContextEnabled",
        "leadDetectsBend",
        "leadDetectsRelease",
        "leadDetectsPalmMute",
        "leadProductionUnchanged",
        "bassGenericUnchanged",
        "bassContextEnabled",
        "bassDetectsFiveSevenContour",
        "bassDetectsSlide",
        "bassDetectsMute",
        "bassDetectsRest",
        "bassProductionUnchanged",
        "rhythmReceivesNoLeadAnalysis",
        "rhythmReceivesNoBassAnalysis",
        "leadReceivesNoChordAnalysis",
        "leadReceivesNoBassAnalysis",
        "bassReceivesNoChordAnalysis",
        "bassReceivesNoLeadAnalysis",
        "rhythmNoSyntheticNotes",
        "leadNoSyntheticNotes",
        "bassNoSyntheticNotes",
        "allTabsPresent",
    ]

    validations = {
        "benchmarkVersion": report.get("benchmarkVersion") == 7,
        "benchmarkType": report.get("benchmarkType")
        == "combined-v7-rhythm-lead-bass-full-stack-audio-path",
        "passed": report.get("passed") is True,
        "protectedBaselinesChanged": report.get("protectedBaselinesChanged") is False,
        "allExpectedChecksPresent": all(name in checks for name in expected_checks),
        "allExpectedChecksPass": all(checks.get(name) is True for name in expected_checks),
        "threeEventCountsPresent": set((report.get("eventCounts") or {}).keys())
        == {"rhythm", "lead", "bass"},
        "allEventCountsPositive": all(
            int(value or 0) > 0
            for value in (report.get("eventCounts") or {}).values()
        ),
    }

    failed = False
    print("JIMMY PAIGE V7 COMBINED FULL-STACK REGRESSION GUARD")
    print("=" * 72)
    for name, passed in validations.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    print("\nCombined benchmark checks")
    for name in expected_checks:
        passed = checks.get(name) is True
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    rhythm = report.get("rhythm") or {}
    lead = report.get("lead") or {}
    bass = report.get("bass") or {}
    print("\nRhythm vocabulary:", rhythm.get("vocabulary"))
    print("Rhythm promotions:", rhythm.get("promotions"))
    print("Lead release pairs:", lead.get("releasePairCount"))
    print("Lead palm-muted events:", lead.get("palmMutedEventCount"))
    print("Bass 5/7 contour:", bass.get("contour5And7Detected"))
    print("Bass slide target:", bass.get("slideTargetFret"))

    if failed:
        raise SystemExit(
            "\nV7 combined full-stack regression detected. Do not deploy."
        )

    print("\nV7 COMBINED FULL-STACK & TAB PROTECTIONS PRESERVED 💚")
    print("Rhythm harmony, lead techniques, and bass techniques remain isolated.")
    print("All tabs, events, note counts, pitches, frets, and timing remain protected.")


if __name__ == "__main__":
    main()
