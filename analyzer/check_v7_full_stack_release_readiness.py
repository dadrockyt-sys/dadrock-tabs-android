#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

DEFAULT_REPORT = Path("/tmp/gomyway-v7-combined-full-stack-report.json")
DEFAULT_BASELINE = Path("analyzer/v7_full_stack_baseline.json")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required JSON file not found: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}")
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))
    args = parser.parse_args()

    report = load_json(Path(args.report))
    baseline = load_json(Path(args.baseline))
    checks = report.get("checks") or {}

    rhythm = report.get("rhythm") or {}
    lead_analysis = report.get("lead") or {}
    bass_analysis = report.get("bass") or {}

    rhythm_vocabulary = set(
        rhythm.get("vocabulary")
        or report.get("rhythmVocabulary")
        or []
    )
    rhythm_promotions = (
        rhythm.get("promotions")
        or report.get("rhythmPromotions")
        or {}
    )

    required_checks = baseline.get("requiredChecks") or []
    missing_checks = [
        name for name in required_checks
        if checks.get(name) is not True
    ]

    required_vocabulary = set(
        baseline.get("requiredRhythmVocabulary") or []
    )
    missing_vocabulary = sorted(
        required_vocabulary - rhythm_vocabulary
    )

    required_promotions = (
        baseline.get("requiredRhythmPromotions") or []
    )
    missing_promotions = [
        name for name in required_promotions
        if rhythm_promotions.get(name) is not True
    ]

    release_pairs = int(
        lead_analysis.get("releasePairCount")
        or report.get("leadReleasePairs")
        or 0
    )
    palm_muted = int(
        lead_analysis.get("palmMutedEventCount")
        or report.get("leadPalmMutedEvents")
        or 0
    )
    bass_contour = bool(
        bass_analysis.get("contour5And7Detected")
        if "contour5And7Detected" in bass_analysis
        else report.get("bassFiveSevenContour")
    )
    bass_slide_target = bass_analysis.get("slideTargetFret")
    if bass_slide_target is None:
        bass_slide_target = report.get("bassSlideTarget")

    guard_checks = {
        "combinedBenchmarkPassed": report.get("passed") is True,
        "protectedBaselinesUnchanged": (
            report.get("protectedBaselinesChanged") is False
        ),
        "allRequiredChecksGreen": not missing_checks,
        "rhythmVocabularyLocked": not missing_vocabulary,
        "rhythmPromotionsLocked": not missing_promotions,
        "leadReleasePairsLocked": release_pairs >= int(
            baseline.get("minimumLeadReleasePairs") or 1
        ),
        "leadPalmMuteLocked": palm_muted >= int(
            baseline.get("minimumLeadPalmMutedEvents") or 1
        ),
        "bassContourLocked": bass_contour is bool(
            baseline.get("requiredBassContour", True)
        ),
        "bassSlideTargetLocked": (
            bass_slide_target
            == baseline.get("requiredBassSlideTarget")
        ),
    }

    failed = False
    print("JIMMY PAIGE V7 FULL-STACK RELEASE READINESS GUARD")
    print("=" * 72)
    for name, passed in guard_checks.items():
        print("PASS" if passed else "FAIL", name)
        failed = failed or not passed

    if missing_checks:
        print("Missing checks:", missing_checks)
    if missing_vocabulary:
        print("Missing rhythm vocabulary:", missing_vocabulary)
    if missing_promotions:
        print("Missing rhythm promotions:", missing_promotions)

    print("Rhythm vocabulary:", sorted(rhythm_vocabulary))
    print("Rhythm promotions:", rhythm_promotions)
    print("Lead release pairs:", release_pairs)
    print("Lead palm-muted events:", palm_muted)
    print("Bass 5/7 contour:", bass_contour)
    print("Bass slide target:", bass_slide_target)

    if failed:
        raise SystemExit(
            "\nV7 full-stack release readiness regression detected. "
            "Do not advance."
        )

    print("\nV7 FULL-STACK RELEASE BASELINE PRESERVED 💚")
    print("Rhythm, lead, and bass diagnostics remain isolated and read-only.")
    print("Tabs, events, note counts, pitches, frets, and timing remain protected.")


if __name__ == "__main__":
    main()
