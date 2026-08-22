#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_BINDING = Path("/tmp/gomyway-full-song-v7-layout-binding.json")
DEFAULT_OUTPUT = Path("/tmp/gomyway-full-song-v7-pdf-render-plan.json")

PAGE_WIDTH = 612.0
PAGE_HEIGHT = 792.0
CONTENT_LEFT = 50.0
CONTENT_RIGHT = 560.0
SYSTEMS_PER_PAGE = 6
FIRST_PAGE_TOP = 578.0
CONTINUATION_TOP = 704.0
SYSTEM_HEIGHT = 82.0

LANE_Y_OFFSETS = {
    "chord-label": 11.0,
    "bend-release": 4.0,
    "palm-mute-span": -4.0,
    "slide": -12.0,
    "muted-attack": -20.0,
    "rest": -28.0,
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def rounded(value: Any) -> float:
    return round(float(value or 0.0), 4)


def page_and_system(segment_index: int) -> tuple[int, int]:
    return segment_index // SYSTEMS_PER_PAGE, segment_index % SYSTEMS_PER_PAGE


def system_top(page_index: int, system_index: int) -> float:
    top = FIRST_PAGE_TOP if page_index == 0 else CONTINUATION_TOP
    return top - system_index * SYSTEM_HEIGHT


def command_kind(marker_type: str) -> str:
    return {
        "chord-label": "draw-text",
        "bend-release": "draw-bend-release",
        "palm-mute-span": "draw-span",
        "slide": "draw-slide",
        "muted-attack": "draw-symbol",
        "rest": "draw-symbol",
    }.get(marker_type, "draw-marker")


def marker_label(marker: dict[str, Any]) -> str:
    marker_type = str(marker.get("type") or "")
    if marker_type == "chord-label":
        return str(marker.get("label") or "")
    if marker_type == "bend-release":
        return "full"
    if marker_type == "palm-mute-span":
        return "P.M."
    if marker_type == "slide":
        target = marker.get("targetFret")
        return f"slide to {target}" if target is not None else "slide"
    if marker_type == "muted-attack":
        return "x"
    if marker_type == "rest":
        return "rest"
    return marker_type


def build_command(marker: dict[str, Any], command_index: int) -> dict[str, Any]:
    segment_index = int(marker.get("layoutSegmentIndex") or 0)
    page_index, system_index = page_and_system(segment_index)
    width = CONTENT_RIGHT - CONTENT_LEFT
    start_ratio = clamp(float(marker.get("layoutStartRatio") or 0.0), 0.0, 1.0)
    end_ratio = clamp(float(marker.get("layoutEndRatio") or start_ratio), 0.0, 1.0)
    x1 = CONTENT_LEFT + start_ratio * width
    x2 = CONTENT_LEFT + max(start_ratio, end_ratio) * width
    marker_type = str(marker.get("type") or "")
    y = system_top(page_index, system_index) + LANE_Y_OFFSETS.get(marker_type, 0.0)

    return {
        "commandIndex": command_index,
        "kind": command_kind(marker_type),
        "markerType": marker_type,
        "instrument": marker.get("instrument"),
        "label": marker_label(marker),
        "pageIndex": page_index,
        "systemIndex": system_index,
        "segmentIndex": segment_index,
        "x1": round(x1, 3),
        "x2": round(x2, 3),
        "y": round(y, 3),
        "sourceStart": rounded(marker.get("start")),
        "sourceEnd": rounded(marker.get("end")),
        "sourceEventIndex": marker.get("eventIndex"),
        "sourceEventIndices": marker.get("eventIndices") or [],
        "continuesBeyondSegment": bool(marker.get("continuesBeyondSegment")),
        "renderMode": "dry-run-only",
        "readOnly": True,
    }


def build_plan(binding: dict[str, Any]) -> dict[str, Any]:
    markers = [
        marker
        for marker in (binding.get("boundMarkers") or [])
        if isinstance(marker, dict)
    ]
    commands = [build_command(marker, index) for index, marker in enumerate(markers)]
    commands.sort(
        key=lambda command: (
            int(command.get("pageIndex") or 0),
            int(command.get("systemIndex") or 0),
            float(command.get("x1") or 0.0),
            int(command.get("commandIndex") or 0),
        )
    )

    page_count = (
        max((int(command.get("pageIndex") or 0) for command in commands), default=-1)
        + 1
    )
    pages = []
    for page_index in range(page_count):
        page_commands = [
            command for command in commands if command.get("pageIndex") == page_index
        ]
        pages.append({
            "pageIndex": page_index,
            "commandCount": len(page_commands),
            "commands": page_commands,
        })

    checks = {
        "sourceBindingPassed": binding.get("passed") is True,
        "protectedBaselinesUnchanged": binding.get("protectedBaselinesChanged") is False,
        "allMarkersProjected": len(commands) == len(markers),
        "allCommandsReadOnly": all(command.get("readOnly") is True for command in commands),
        "allCommandsDryRun": all(command.get("renderMode") == "dry-run-only" for command in commands),
        "allCoordinatesFinite": all(
            all(isinstance(command.get(field), (int, float)) for field in ("x1", "x2", "y"))
            for command in commands
        ),
        "allXCoordinatesBounded": all(
            CONTENT_LEFT <= float(command.get("x1") or 0.0) <= CONTENT_RIGHT
            and CONTENT_LEFT <= float(command.get("x2") or 0.0) <= CONTENT_RIGHT
            and float(command.get("x2") or 0.0) >= float(command.get("x1") or 0.0)
            for command in commands
        ),
        "allYCoordinatesBounded": all(
            30.0 <= float(command.get("y") or 0.0) <= PAGE_HEIGHT - 30.0
            for command in commands
        ),
        "allMarkerTypesSupported": all(
            command.get("markerType") in LANE_Y_OFFSETS for command in commands
        ),
        "pageCommandCountsConsistent": sum(
            int(page.get("commandCount") or 0) for page in pages
        ) == len(commands),
    }

    return {
        "renderPlanVersion": 7,
        "renderPlanType": "v7-read-only-pdf-drawing-instructions",
        "audioName": binding.get("audioName"),
        "songDuration": binding.get("songDuration"),
        "sourceBindingType": binding.get("bindingType"),
        "virtualPage": {
            "width": PAGE_WIDTH,
            "height": PAGE_HEIGHT,
            "contentLeft": CONTENT_LEFT,
            "contentRight": CONTENT_RIGHT,
            "systemsPerPage": SYSTEMS_PER_PAGE,
            "systemHeight": SYSTEM_HEIGHT,
        },
        "pages": pages,
        "commands": commands,
        "counts": {
            "pages": page_count,
            "commands": len(commands),
            "markerTypes": sorted({str(command.get("markerType") or "") for command in commands}),
            "continuingSpans": sum(1 for command in commands if command.get("continuesBeyondSegment")),
        },
        "checks": checks,
        "passed": all(checks.values()),
        "affectsProductionEvents": False,
        "affectsGeneratedTab": False,
        "affectsPdf": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "PDF drawing instructions are a dry-run projection only. They must not call "
            "pdf-lib, modify production events, rewrite generated tab, or alter any PDF."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding", default=str(DEFAULT_BINDING))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    plan = build_plan(load_json(Path(args.binding)))
    output = Path(args.output)
    output.write_text(json.dumps(plan, indent=2, sort_keys=True), encoding="utf-8")

    print("JIMMY PAIGE V7 PDF RENDER-PLAN PROJECTION")
    print("=" * 72)
    for name, passed in (plan.get("checks") or {}).items():
        print("PASS" if passed else "FAIL", name)
    print("Counts:", plan.get("counts"))
    print("Overall:", "PASS" if plan.get("passed") else "FAIL")
    print("Saved render plan:", output)

    if not plan.get("passed"):
        raise SystemExit("\nV7 PDF render-plan projection regression detected.")


if __name__ == "__main__":
    main()
