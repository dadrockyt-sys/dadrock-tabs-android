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
        default="/tmp/gomyway-v7-deg-harmony-diagnostics.json",
    )
    args = parser.parse_args()

    report = load_json(Path(args.report))
    protections = report.get("protectionChecks") or {}
    diagnostics = report.get("targetDiagnostics") or {}

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
            == "D-E-G-window-evidence-diagnostics",
            report.get("benchmarkType"),
            "D-E-G-window-evidence-diagnostics",
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
            "targetsPresent",
            set(diagnostics) == {"D", "E", "G"},
            sorted(diagnostics),
            ["D", "E", "G"],
        ),
    ]

    for name, value in protections.items():
        checks.append(
            (
                f"protection.{name}",
                value is True,
                value,
                True,
            )
        )

    failed = False
    print("JIMMY PAIGE V7 D / E / G DIAGNOSTICS GUARD")
    print("=" * 68)

    for name, passed, actual, expected in checks:
        print(
            f"{'PASS' if passed else 'FAIL':4}  "
            f"{name}: {actual}  expected {expected}"
        )
        failed = failed or not passed

    print("\nEvidence summary")
    for name in ("D", "E", "G"):
        item = diagnostics.get(name) or {}
        print(
            name,
            "maxCoverage=",
            item.get("maximumCoverage"),
            "maxSupport=",
            item.get("maximumWeightedSupport"),
            "fullWindows=",
            item.get("fullCoverageWindowCount"),
            "twoToneWindows=",
            item.get("twoToneWindowCount"),
        )

    if failed:
        raise SystemExit(
            "\nV7 D/E/G diagnostics protection regression detected."
        )

    print("\nV7 D / E / G DIAGNOSTICS & PROTECTIONS PRESERVED 💚")
    print("No matching thresholds were changed and no notes were synthesized.")


if __name__ == "__main__":
    main()
