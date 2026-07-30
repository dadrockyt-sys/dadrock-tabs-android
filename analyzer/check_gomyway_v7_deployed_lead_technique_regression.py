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
        default="/tmp/gomyway-v7-deployed-lead-technique-report.json",
    )
    args = parser.parse_args()

    report = load_json(Path(args.report))
    checks = report.get("checks") or {}

    required = {
        "benchmarkVersion": report.get("benchmarkVersion") == 7,
        "benchmarkType": (
            report.get("benchmarkType")
            == "deployed-v7-lead-technique-audio-path"
        ),
        "passed": report.get("passed") is True,
        "protectedBaselinesChanged": (
            report.get("protectedBaselinesChanged") is False
        ),
        "genericLeadUnchanged": checks.get("genericLeadUnchanged") is True,
        "contextModeEnabled": checks.get("contextModeEnabled") is True,
        "detectsBend": checks.get("detectsBend") is True,
        "detectsRelease": checks.get("detectsRelease") is True,
        "detectsPalmMute": checks.get("detectsPalmMute") is True,
        "requiresBendEvidence": checks.get("requiresBendEvidence") is True,
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
        "rhythmHarmonyAbsent": checks.get("rhythmHarmonyAbsent") is True,
    }

    failed = False
    print("JIMMY PAIGE V7 DEPLOYED LEAD-TECHNIQUE GUARD")
    print("=" * 70)
    for name, passed in required.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    analysis = report.get("leadTechniqueAnalysis") or {}
    print("Release pairs:", analysis.get("releasePairCount"))
    print("Palm-muted events:", analysis.get("palmMutedEventCount"))

    if failed:
        raise SystemExit(
            "\nV7 deployed lead-technique regression detected. Do not deploy."
        )

    print("\nV7 DEPLOYED LEAD-TECHNIQUE & TAB PROTECTIONS PRESERVED 💚")
    print(
        "Bend/release and palm-mute diagnostics are opt-in; "
        "tab and events remain protected."
    )


if __name__ == "__main__":
    main()
