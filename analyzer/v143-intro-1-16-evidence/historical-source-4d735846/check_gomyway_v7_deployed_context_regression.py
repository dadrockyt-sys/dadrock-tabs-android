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
        default="/tmp/gomyway-v7-deployed-context-report.json",
    )
    args = parser.parse_args()

    report = load_json(Path(args.report))
    checks = report.get("checks") or {}

    required = {
        "benchmarkVersion": report.get("benchmarkVersion") == 7,
        "benchmarkType": report.get("benchmarkType") == "deployed-v7-verified-context-audio-path",
        "passed": report.get("passed") is True,
        "protectedBaselinesChanged": report.get("protectedBaselinesChanged") is False,
        "genericModeUnchanged": checks.get("genericModeUnchanged") is True,
        "contextModeEnabled": checks.get("contextModeEnabled") is True,
        "contextPromotesE": checks.get("contextPromotesE") is True,
        "contextPromotesG": checks.get("contextPromotesG") is True,
        "contextDoesNotPromoteD": checks.get("contextDoesNotPromoteD") is True,
        "preservesG6": checks.get("preservesG6") is True,
        "preservesATp2": checks.get("preservesATp2") is True,
        "contextTabUnchanged": checks.get("contextTabUnchanged") is True,
        "contextEventsUnchanged": checks.get("contextEventsUnchanged") is True,
        "leadReceivesNoChordAnalysis": checks.get("leadReceivesNoChordAnalysis") is True,
        "bassReceivesNoChordAnalysis": checks.get("bassReceivesNoChordAnalysis") is True,
        "noSyntheticNotes": checks.get("noSyntheticNotes") is True,
        "diagnosticsDoNotAffectTab": checks.get("diagnosticsDoNotAffectTab") is True,
    }

    failed = False
    print("JIMMY PAIGE V7 DEPLOYED VERIFIED-CONTEXT GUARD")
    print("=" * 70)
    for name, passed in required.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    print("Generic vocabulary:", report.get("genericVocabulary"))
    print("Contextual vocabulary:", report.get("contextualVocabulary"))
    print("Promotions:", report.get("referenceAwarePromotions"))

    if failed:
        raise SystemExit(
            "\nV7 deployed verified-context regression detected. Do not deploy."
        )

    print("\nV7 DEPLOYED VERIFIED-CONTEXT & TAB PROTECTIONS PRESERVED 💚")
    print("E/G are opt-in diagnostics; D, lead, bass, tab, and events remain protected.")


if __name__ == "__main__":
    main()
