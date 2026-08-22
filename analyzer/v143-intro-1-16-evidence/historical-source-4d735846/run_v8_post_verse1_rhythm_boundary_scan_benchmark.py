from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
VERSE1_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-template-lock.json"
INTRO_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-post-verse1-rhythm-boundary-scan.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
SCAN_START_MEASURE = 33
SCAN_PAIR_COUNT = 12
MATCH_RADIUS_STEPS = 1


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _pair_step(event: dict[str, Any], pair_start: int) -> int:
    measure = _safe_int(event.get("measureNumber"))
    step = _safe_int(event.get("quantizedStep"))
    return ((measure - pair_start) * STEPS_PER_MEASURE) + step


def _matches(step: int, template_steps: list[int]) -> bool:
    return any(abs(step - template_step) <= MATCH_RADIUS_STEPS for template_step in template_steps)


def main() -> None:
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(
            "Missing rhythm candidates. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )
    if not VERSE1_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing Verse 1 rhythm lock. Run "
            "python analyzer/run_v8_verse1_rhythm_template_lock_benchmark.py first."
        )
    if not INTRO_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing intro rhythm lock. Run "
            "python analyzer/run_v8_intro_rhythm_template_lock_benchmark.py first."
        )

    candidates = json.loads(CANDIDATE_PATH.read_text())
    verse1_lock = json.loads(VERSE1_LOCK_PATH.read_text())
    intro_lock = json.loads(INTRO_LOCK_PATH.read_text())

    template_steps = sorted(
        _safe_int(item.get("consensusStep"), -1)
        for item in verse1_lock.get("lockedRhythmTemplate") or []
        if isinstance(item, dict) and _safe_int(item.get("consensusStep"), -1) >= 0
    )

    events = [
        event for event in candidates.get("candidates") or []
        if isinstance(event, dict)
    ]
    maximum_measure = max(
        (_safe_int(event.get("measureNumber")) for event in events),
        default=0,
    )

    pair_reports: list[dict[str, Any]] = []
    for pair_index in range(SCAN_PAIR_COUNT):
        pair_start = SCAN_START_MEASURE + (pair_index * 2)
        if pair_start > maximum_measure:
            break

        pair_events = [
            event for event in events
            if pair_start <= _safe_int(event.get("measureNumber")) <= pair_start + 1
        ]
        observed_steps = sorted({_pair_step(event, pair_start) for event in pair_events})
        matched_steps = [step for step in observed_steps if _matches(step, template_steps)]
        unmatched_steps = [step for step in observed_steps if not _matches(step, template_steps)]
        supported_template_steps = [
            step for step in template_steps
            if any(abs(observed - step) <= MATCH_RADIUS_STEPS for observed in observed_steps)
        ]

        template_coverage = (
            len(supported_template_steps) / len(template_steps)
            if template_steps else 0.0
        )
        event_match_ratio = (
            len(matched_steps) / len(observed_steps)
            if observed_steps else 0.0
        )
        boundary_score = round(
            1.0 - ((template_coverage + event_match_ratio) / 2.0),
            6,
        )

        pair_reports.append({
            "pairStartMeasure": pair_start,
            "pairEndMeasure": pair_start + 1,
            "directAudioEventCount": len(pair_events),
            "observedSteps": observed_steps,
            "matchedObservedSteps": matched_steps,
            "unmatchedObservedSteps": unmatched_steps,
            "supportedVerse1TemplateSteps": supported_template_steps,
            "verse1TemplateCoverage": round(template_coverage, 6),
            "eventMatchRatio": round(event_match_ratio, 6),
            "boundaryScore": boundary_score,
            "readOnly": True,
        })

    strongest_boundary = max(
        pair_reports,
        key=lambda item: (item["boundaryScore"], -item["pairStartMeasure"]),
        default=None,
    )

    checks = {
        "candidateReportPassed": candidates.get("passed") is True,
        "verse1RhythmTemplateLocked": verse1_lock.get("rhythmTemplateLocked") is True,
        "introRhythmTemplateLocked": intro_lock.get("rhythmTemplateLocked") is True,
        "verse1TemplatePresent": len(template_steps) == 9,
        "postVerse1PairsPresent": bool(pair_reports),
        "scanStartsAfterVerse1": SCAN_START_MEASURE > _safe_int(verse1_lock.get("endMeasure")),
        "rendererUnchanged": candidates.get("diagnostics", {}).get("rendererChanged") is False,
        "protectedBaselinesUnchanged": candidates.get("protectedBaselinesChanged") is False,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-post-verse1-rhythm-boundary-scan",
        "passed": all(checks.values()),
        "scanStartMeasure": SCAN_START_MEASURE,
        "scanEndMeasure": pair_reports[-1]["pairEndMeasure"] if pair_reports else SCAN_START_MEASURE,
        "verse1TemplateSteps": template_steps,
        "pairReports": pair_reports,
        "strongestBoundaryCandidate": strongest_boundary,
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This diagnostic scans two-measure windows after Verse 1 and compares direct-audio "
            "rhythm attacks with the locked Verse 1 rhythm template. It may identify candidate "
            "section boundaries only. It must not label a section permanently, synthesize notes, "
            "change pitches, frets, techniques, durations, locked V7 events, locked rhythm "
            "templates, or the PDF renderer."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_pairs = [
        (
            item["pairStartMeasure"],
            item["directAudioEventCount"],
            item["verse1TemplateCoverage"],
            item["eventMatchRatio"],
            item["boundaryScore"],
        )
        for item in pair_reports
    ]

    print("Post-Verse 1 rhythm boundary scan pass:", report["passed"])
    print("Scan measures:", f"{report['scanStartMeasure']}-{report['scanEndMeasure']}")
    print("Verse 1 locked template steps:", template_steps)
    print("Pairs (start, events, template coverage, event match, boundary score):", compact_pairs)
    print("Strongest boundary candidate:", strongest_boundary)
    print("Checks:", checks)
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
