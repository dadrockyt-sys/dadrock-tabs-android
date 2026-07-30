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
        default="/tmp/gomyway-v7-human-reference-report.json",
    )
    args = parser.parse_args()
    report = load_json(Path(args.report))
    protections = report.get("protectionChecks") or {}

    checks: list[tuple[str, bool, Any, Any]] = [
        (
            "benchmarkVersion",
            report.get("benchmarkVersion") == 7,
            report.get("benchmarkVersion"),
            7,
        ),
        (
            "benchmarkType",
            report.get("benchmarkType")
            == "human-verified-lead-bass-rhythm-harmony-reference",
            report.get("benchmarkType"),
            "human-verified-lead-bass-rhythm-harmony-reference",
        ),
        (
            "passed",
            bool(report.get("passed")),
            report.get("passed"),
            True,
        ),
        (
            "protectedBaselinesChanged",
            report.get("protectedBaselinesChanged") is False,
            report.get("protectedBaselinesChanged"),
            False,
        ),
    ]

    required_protections = [
        "bassSeparationActive",
        "rhythmSeparationActive",
        "leadSeparationActive",
        "bassEventsPresent",
        "rhythmEventsPresent",
        "leadEventsPresent",
        "chordEngineV6",
        "noSyntheticNotes",
    ]
    for name in required_protections:
        checks.append(
            (
                f"protection.{name}",
                protections.get(name) is True,
                protections.get(name),
                True,
            )
        )

    failed = False
    print("JIMMY PAIGE V7 HUMAN-REFERENCE PROTECTION GUARD")
    print("=" * 68)
    for name, passed, actual, expected in checks:
        print(f"{'PASS' if passed else 'FAIL':4}  {name}: {actual}  expected {expected}")
        failed = failed or not passed

    print("\nCurrent human-reference category scores:")
    for category, score in (report.get("categoryScores") or {}).items():
        print(f"  {category}: {score}")

    misses = [
        name
        for name, passed in (report.get("humanReferenceChecks") or {}).items()
        if not passed
    ]
    print("Current reference misses:", misses or "none")

    if failed:
        raise SystemExit(
            "\nV7 protection regression detected. Do not tune human-reference scoring until the protected analyzer is green."
        )

    print("\nV7 LAYERED SEPARATION & CHORD PROTECTIONS PRESERVED 💚")
    print("Human-reference misses are diagnostic targets for the next tuning pass.")


if __name__ == "__main__":
    main()
