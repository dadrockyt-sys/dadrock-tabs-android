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
        default="/tmp/gomyway-v7-eg-two-tone-report.json",
    )
    args = parser.parse_args()
    report = load_json(Path(args.report))
    checks = report.get("checks") or {}
    promotions = report.get("promotions") or {}
    evidence = report.get("evidence") or {}

    expected_checks = {
        "contextAlreadyHasG6": True,
        "contextAlreadyHasATp2": True,
        "promotesEFromTwoToneEvidence": True,
        "promotesGFromTwoToneEvidence": True,
        "doesNotPromoteDWithoutTwoTones": True,
        "bassSeparationActive": True,
        "rhythmSeparationActive": True,
        "leadSeparationActive": True,
        "bassEventsPresent": True,
        "rhythmEventsPresent": True,
        "leadEventsPresent": True,
        "engineV6": True,
        "noSyntheticNotes": True,
        "eventCountsUnchanged": True,
    }

    results: list[tuple[str, bool, Any, Any]] = [
        (
            "benchmarkVersion",
            report.get("benchmarkVersion") == 7,
            report.get("benchmarkVersion"),
            7,
        ),
        (
            "benchmarkType",
            report.get("benchmarkType")
            == "E-G-two-tone-progression-aware-promotion",
            report.get("benchmarkType"),
            "E-G-two-tone-progression-aware-promotion",
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
        (
            "promotion.E",
            promotions.get("E") is True,
            promotions.get("E"),
            True,
        ),
        (
            "promotion.G",
            promotions.get("G") is True,
            promotions.get("G"),
            True,
        ),
        (
            "promotion.D",
            promotions.get("D") is False,
            promotions.get("D"),
            False,
        ),
        (
            "evidence.E.twoToneWindowCount",
            int((evidence.get("E") or {}).get("twoToneWindowCount") or 0) >= 1,
            (evidence.get("E") or {}).get("twoToneWindowCount"),
            ">= 1",
        ),
        (
            "evidence.G.twoToneWindowCount",
            int((evidence.get("G") or {}).get("twoToneWindowCount") or 0) >= 1,
            (evidence.get("G") or {}).get("twoToneWindowCount"),
            ">= 1",
        ),
        (
            "evidence.D.twoToneWindowCount",
            int((evidence.get("D") or {}).get("twoToneWindowCount") or 0) == 0,
            (evidence.get("D") or {}).get("twoToneWindowCount"),
            0,
        ),
    ]

    for name, expected in expected_checks.items():
        results.append(
            (
                f"check.{name}",
                checks.get(name) is expected,
                checks.get(name),
                expected,
            )
        )

    failed = False
    print("JIMMY PAIGE V7 E / G TWO-TONE HARMONY GUARD")
    print("=" * 72)
    for name, passed, actual, expected in results:
        print(
            f"{'PASS' if passed else 'FAIL':4}  "
            f"{name}: {actual}  expected {expected}"
        )
        failed = failed or not passed

    if failed:
        raise SystemExit(
            "\nV7 E/G harmony regression detected. Do not promote this path."
        )

    print("\nV7 E / G TWO-TONE HARMONY & PROTECTIONS PRESERVED 💚")
    print("D remains unpromoted because only one real chord tone was detected.")


if __name__ == "__main__":
    main()
