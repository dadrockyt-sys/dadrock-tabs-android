#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--report",
        default="/tmp/gomyway-v7-harmony-context-report.json",
    )
    args = parser.parse_args()

    report = load_json(Path(args.report))
    before = report.get("before") or {}
    after = report.get("after") or {}
    protection = report.get("protectionChecks") or {}

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
            == "reference-aware-harmony-context-tie-breaker",
            report.get("benchmarkType"),
            "reference-aware-harmony-context-tie-breaker",
        ),
        (
            "passed",
            bool(report.get("passed")),
            report.get("passed"),
            True,
        ),
        (
            "afterScoreNotLower",
            float(after.get("score") or 0.0)
            >= float(before.get("score") or 0.0),
            after.get("score"),
            f">= {before.get('score')}",
        ),
        (
            "noSyntheticNotes",
            bool(
                ((after.get("analysis") or {}).get("noSyntheticNotes"))
            ),
            (after.get("analysis") or {}).get("noSyntheticNotes"),
            True,
        ),
        (
            "protectedBaselinesChanged",
            report.get("protectedBaselinesChanged") is False,
            report.get("protectedBaselinesChanged"),
            False,
        ),
    ]

    for name, value in protection.items():
        checks.append(
            (
                f"protection.{name}",
                value is True,
                value,
                True,
            )
        )

    failed = False
    print("JIMMY PAIGE V7 HARMONY CONTEXT REGRESSION GUARD")
    print("=" * 68)
    print("Before harmony score:", before.get("score"))
    print("After harmony score:", after.get("score"))
    print("Improvement:", report.get("scoreImprovement"))

    for name, passed, actual, expected in checks:
        marker = "PASS" if passed else "FAIL"
        print(f"{marker:4}  {name}: {actual}  expected {expected}")
        failed = failed or not passed

    print("\nAfter harmony evidence:")
    for name, passed in (after.get("checks") or {}).items():
        print("PASS" if passed else "MISS", name)

    if failed:
        raise SystemExit(
            "\nV7 harmony context regression detected. "
            "Do not activate this tuning path."
        )

    print(
        "\nV7 HARMONY CONTEXT & LAYERED PROTECTIONS PRESERVED 💚"
    )
    print(
        "Progression context remains a tie-breaker; no notes were synthesized."
    )


if __name__ == "__main__":
    main()
