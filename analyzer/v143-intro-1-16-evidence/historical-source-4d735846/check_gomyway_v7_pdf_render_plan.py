#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_PLAN = Path("/tmp/gomyway-full-song-v7-pdf-render-plan.json")
EXPECTED_MARKER_TYPES = {
    "bend-release",
    "chord-label",
    "muted-attack",
    "palm-mute-span",
    "rest",
    "slide",
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    args = parser.parse_args()

    plan = load_json(Path(args.plan))
    checks = plan.get("checks") or {}
    counts = plan.get("counts") or {}
    commands = [
        command
        for command in (plan.get("commands") or [])
        if isinstance(command, dict)
    ]
    pages = [page for page in (plan.get("pages") or []) if isinstance(page, dict)]
    marker_types = {str(value) for value in (counts.get("markerTypes") or [])}

    guard = {
        "renderPlanPassed": plan.get("passed") is True,
        "sourcePlanChecksGreen": bool(checks) and all(checks.values()),
        "protectedBaselinesUnchanged": plan.get("protectedBaselinesChanged") is False,
        "productionEventsUnaffected": plan.get("affectsProductionEvents") is False,
        "generatedTabUnaffected": plan.get("affectsGeneratedTab") is False,
        "pdfStillUnaffected": plan.get("affectsPdf") is False,
        "all103MarkersProjected": len(commands) == 103,
        "allMarkerTypesPreserved": marker_types == EXPECTED_MARKER_TYPES,
        "virtualPagesPresent": bool(pages),
        "allCommandsDryRun": all(
            command.get("renderMode") == "dry-run-only" for command in commands
        ),
        "allCommandsReadOnly": all(command.get("readOnly") is True for command in commands),
        "allCoordinatesBounded": all(
            50.0 <= float(command.get("x1") or 0.0) <= 560.0
            and 50.0 <= float(command.get("x2") or 0.0) <= 560.0
            and 30.0 <= float(command.get("y") or 0.0) <= 762.0
            for command in commands
        ),
        "pageCommandCountsConsistent": sum(
            int(page.get("commandCount") or 0) for page in pages
        ) == len(commands),
    }

    print("JIMMY PAIGE V7 PDF RENDER-PLAN GUARD")
    print("=" * 72)
    for name, passed in guard.items():
        print("PASS" if passed else "FAIL", name)
    print("Virtual pages:", counts.get("pages"))
    print("Drawing commands:", counts.get("commands"))
    print("Continuing spans:", counts.get("continuingSpans"))
    print("Marker types:", sorted(marker_types))

    if not all(guard.values()):
        raise SystemExit("\nV7 PDF render-plan regression detected. Do not integrate renderer.")

    print("\nV7 PDF RENDER-PLAN PROJECTION PRESERVED 💚")
    print("All 103 notation markers have bounded dry-run drawing instructions.")
    print("Production events, generated tab, and real PDF rendering remain untouched.")


if __name__ == "__main__":
    main()
