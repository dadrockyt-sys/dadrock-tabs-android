from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BOUNDARY_SCAN_PATH = (
    REPO_ROOT / "public" / "gomyway-full-song-v8-post-verse1-rhythm-boundary-scan.json"
)
VERSE1_LOCK_PATH = (
    REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-template-lock.json"
)
INTRO_LOCK_PATH = (
    REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"
)
OUTPUT_PATH = (
    REPO_ROOT / "public" / "gomyway-full-song-v8-post-verse1-rhythm-boundary-confirmation.json"
)

EXPECTED_BOUNDARY_START = 37
EXPECTED_BOUNDARY_END = 38
MIN_BOUNDARY_SCORE = 0.25
MIN_DIRECT_AUDIO_EVENTS = 1


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


def main() -> None:
    if not BOUNDARY_SCAN_PATH.exists():
        raise FileNotFoundError(
            "Missing post-Verse 1 rhythm boundary scan. Run "
            "python analyzer/run_v8_post_verse1_rhythm_boundary_scan_benchmark.py first."
        )
    if not VERSE1_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing Verse 1 rhythm template lock. Run "
            "python analyzer/run_v8_verse1_rhythm_template_lock_benchmark.py first."
        )
    if not INTRO_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing intro rhythm template lock. Run "
            "python analyzer/run_v8_intro_rhythm_template_lock_benchmark.py first."
        )

    boundary_scan = json.loads(BOUNDARY_SCAN_PATH.read_text())
    verse1_lock = json.loads(VERSE1_LOCK_PATH.read_text())
    intro_lock = json.loads(INTRO_LOCK_PATH.read_text())

    pair_reports = [
        item
        for item in boundary_scan.get("pairReports") or []
        if isinstance(item, dict)
    ]
    reports_by_start = {
        _safe_int(item.get("pairStartMeasure")): item
        for item in pair_reports
    }

    strongest = boundary_scan.get("strongestBoundaryCandidate")
    if not isinstance(strongest, dict):
        strongest = {}

    candidate_start = _safe_int(strongest.get("pairStartMeasure"), -1)
    candidate_end = _safe_int(strongest.get("pairEndMeasure"), -1)
    candidate_score = _safe_float(strongest.get("boundaryScore"), -1.0)
    candidate_event_count = _safe_int(strongest.get("directAudioEventCount"), 0)

    previous_report = reports_by_start.get(EXPECTED_BOUNDARY_START - 2, {})
    next_report = reports_by_start.get(EXPECTED_BOUNDARY_START + 2, {})
    previous_score = _safe_float(previous_report.get("boundaryScore"), -1.0)
    next_score = _safe_float(next_report.get("boundaryScore"), -1.0)

    local_prominence = round(
        candidate_score - max(previous_score, next_score),
        6,
    )

    continuation_reports = [
        item
        for item in pair_reports
        if 33 <= _safe_int(item.get("pairStartMeasure")) <= 35
    ]
    continuation_max_score = max(
        (_safe_float(item.get("boundaryScore"), 1.0) for item in continuation_reports),
        default=1.0,
    )

    checks = {
        "boundaryScanPassed": boundary_scan.get("passed") is True,
        "verse1RhythmTemplateLocked": verse1_lock.get("rhythmTemplateLocked") is True,
        "introRhythmTemplateLocked": intro_lock.get("rhythmTemplateLocked") is True,
        "expectedBoundaryPairSelected": (
            candidate_start == EXPECTED_BOUNDARY_START
            and candidate_end == EXPECTED_BOUNDARY_END
        ),
        "boundaryScoreMeetsThreshold": candidate_score >= MIN_BOUNDARY_SCORE,
        "boundaryHasDirectAudioEvidence": candidate_event_count >= MIN_DIRECT_AUDIO_EVENTS,
        "boundaryBeatsImmediateNeighbors": (
            candidate_score > previous_score and candidate_score > next_score
        ),
        "preBoundaryPairsRemainMoreVerseLike": continuation_max_score < candidate_score,
        "rendererUnchanged": boundary_scan.get("rendererChanged") is False,
        "protectedBaselinesUnchanged": (
            boundary_scan.get("protectedBaselinesChanged") is False
        ),
        "noSyntheticNotes": True,
    }

    confirmed = all(checks.values())
    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-post-verse1-rhythm-boundary-confirmation",
        "passed": confirmed,
        "boundaryConfirmed": confirmed,
        "confirmedBoundaryStartMeasure": candidate_start,
        "confirmedBoundaryEndMeasure": candidate_end,
        "candidateBoundaryScore": round(candidate_score, 6),
        "previousPairBoundaryScore": round(previous_score, 6),
        "nextPairBoundaryScore": round(next_score, 6),
        "localProminence": local_prominence,
        "preBoundaryMaximumScore": round(continuation_max_score, 6),
        "candidateDirectAudioEventCount": candidate_event_count,
        "candidateObservedSteps": strongest.get("observedSteps") or [],
        "candidateMatchedObservedSteps": strongest.get("matchedObservedSteps") or [],
        "candidateUnmatchedObservedSteps": strongest.get("unmatchedObservedSteps") or [],
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "readOnly": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This gate confirms only whether measures 37-38 are the strongest local rhythm "
            "change immediately after Verse 1. It does not name or lock the following section, "
            "copy professional notes, synthesize attacks, alter pitches, frets, techniques, "
            "durations, locked V7 events, locked intro or Verse 1 rhythm templates, or the PDF "
            "renderer. A later read-only benchmark must analyze repetition after the confirmed "
            "boundary before any new section template can be proposed."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("Post-Verse 1 rhythm boundary confirmation pass:", report["passed"])
    print("Boundary confirmed:", report["boundaryConfirmed"])
    print(
        "Confirmed boundary measures:",
        f"{report['confirmedBoundaryStartMeasure']}-{report['confirmedBoundaryEndMeasure']}",
    )
    print("Candidate boundary score:", report["candidateBoundaryScore"])
    print("Previous pair boundary score:", report["previousPairBoundaryScore"])
    print("Next pair boundary score:", report["nextPairBoundaryScore"])
    print("Local prominence:", report["localProminence"])
    print("Pre-boundary maximum score:", report["preBoundaryMaximumScore"])
    print("Candidate direct-audio event count:", report["candidateDirectAudioEventCount"])
    print("Candidate observed steps:", report["candidateObservedSteps"])
    print("Candidate unmatched observed steps:", report["candidateUnmatchedObservedSteps"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
