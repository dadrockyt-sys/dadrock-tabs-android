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
        default="/tmp/gomyway-v7-deployed-bass-technique-report.json",
    )
    args = parser.parse_args()

    report = load_json(Path(args.report))
    checks = report.get("checks") or {}

    expected = {
        "benchmarkVersion": report.get("benchmarkVersion") == 7,
        "benchmarkType": (
            report.get("benchmarkType")
            == "deployed-v7-bass-technique-audio-path"
        ),
        "passed": report.get("passed") is True,
        "protectedBaselinesChanged": (
            report.get("protectedBaselinesChanged") is False
        ),
        "genericBassUnchanged": checks.get("genericBassUnchanged") is True,
        "contextModeEnabled": checks.get("contextModeEnabled") is True,
        "detectsFiveSevenContour": (
            checks.get("detectsFiveSevenContour") is True
        ),
        "detectsSlideTarget": checks.get("detectsSlideTarget") is True,
        "detectsMutedAttack": checks.get("detectsMutedAttack") is True,
        "detectsRest": checks.get("detectsRest") is True,
        "tabPresent": checks.get("tabPresent") is True,
        "tabUnchanged": checks.get("tabUnchanged") is True,
        "eventsUnchanged": checks.get("eventsUnchanged") is True,
        "noteCountUnchanged": checks.get("noteCountUnchanged") is True,
        "noSyntheticNotes": checks.get("noSyntheticNotes") is True,
        "diagnosticsDoNotAffectTab": (
            checks.get("diagnosticsDoNotAffectTab") is True
        ),
        "diagnosticsDoNotAffectEvents": (
            checks.get("diagnosticsDoNotAffectEvents") is True
        ),
        "leadAnalysisAbsent": checks.get("leadAnalysisAbsent") is True,
        "rhythmHarmonyAbsent": checks.get("rhythmHarmonyAbsent") is True,
    }

    failed = False
    print("JIMMY PAIGE V7 DEPLOYED BASS-TECHNIQUE GUARD")
    print("=" * 72)
    for name, passed in expected.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    analysis = report.get("bassTechniqueAnalysis") or {}
    print("5/7 contour:", analysis.get("contour5And7Detected"))
    print("Slide target:", analysis.get("slideTargetFret"))
    print("Muted attack index:", analysis.get("muteEventIndex"))
    print("Rest index:", analysis.get("restEventIndex"))

    if failed:
        raise SystemExit(
            "\nV7 deployed bass-technique regression detected. Do not deploy."
        )

    print("\nV7 DEPLOYED BASS-TECHNIQUE & TAB PROTECTIONS PRESERVED 💚")
    print("5/7 contour, slide, mute, and rest diagnostics are opt-in;")
    print("lead, rhythm, tab, events, and note count remain protected.")


if __name__ == "__main__":
    main()
