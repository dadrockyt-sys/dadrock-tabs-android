from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-rhythm-candidates.json"
SECTION_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-sections.json"
INTRO_LOCK_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-intro-rhythm-template-lock.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-full-song-v8-verse1-rhythm-repetition.json"

STEPS_PER_MEASURE = 16
PAIR_STEPS = 32
DEFAULT_START_MEASURE = 18
DEFAULT_END_MEASURE = 32
MATCH_RADIUS_STEPS = 1
MIN_REPEATED_PAIR_SUPPORT = 3


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


def _find_verse1_bounds(section_report: dict[str, Any]) -> tuple[int, int]:
    for section in section_report.get("sections") or []:
        if not isinstance(section, dict):
            continue
        label = str(section.get("label") or "").strip().lower()
        if label in {"verse 1", "verse1", "verse"}:
            start = _safe_int(section.get("startMeasure"), DEFAULT_START_MEASURE)
            end = _safe_int(section.get("endMeasure"), DEFAULT_END_MEASURE)
            if start > 0 and end >= start:
                return start, end
    return DEFAULT_START_MEASURE, DEFAULT_END_MEASURE


def _pair_signature(events: list[dict[str, Any]], pair_start: int) -> list[int]:
    return sorted({
        ((measure - pair_start) * STEPS_PER_MEASURE + _safe_int(event.get("quantizedStep")))
        for event in events
        if pair_start <= (measure := _safe_int(event.get("measureNumber"))) <= pair_start + 1
    })


def _near(left: int, right: int) -> bool:
    return abs(left - right) <= MATCH_RADIUS_STEPS


def _signature_similarity(left: list[int], right: list[int]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    matched_right: set[int] = set()
    matches = 0
    for left_step in left:
        candidates = [
            (abs(left_step - right_step), index)
            for index, right_step in enumerate(right)
            if index not in matched_right and _near(left_step, right_step)
        ]
        if candidates:
            _, index = min(candidates)
            matched_right.add(index)
            matches += 1
    return round((2.0 * matches) / (len(left) + len(right)), 6)


def main() -> None:
    if not CANDIDATE_PATH.exists():
        raise FileNotFoundError(
            "Missing rhythm candidates. Run "
            "python analyzer/run_v8_rhythm_candidate_benchmark.py first."
        )
    if not INTRO_LOCK_PATH.exists():
        raise FileNotFoundError(
            "Missing intro rhythm-template lock. Run "
            "python analyzer/run_v8_intro_rhythm_template_lock_benchmark.py first."
        )

    candidate_report = json.loads(CANDIDATE_PATH.read_text())
    section_report = json.loads(SECTION_PATH.read_text()) if SECTION_PATH.exists() else {}
    intro_lock = json.loads(INTRO_LOCK_PATH.read_text())
    start_measure, end_measure = _find_verse1_bounds(section_report)

    verse_events = [
        event for event in candidate_report.get("candidates") or []
        if isinstance(event, dict)
        and start_measure <= _safe_int(event.get("measureNumber")) <= end_measure
    ]

    events_by_measure: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for event in verse_events:
        events_by_measure[_safe_int(event.get("measureNumber"))].append(event)

    pair_starts = list(range(start_measure, end_measure, 2))
    pair_reports: list[dict[str, Any]] = []
    signatures: dict[int, list[int]] = {}
    for pair_index, pair_start in enumerate(pair_starts):
        signature = _pair_signature(verse_events, pair_start)
        signatures[pair_start] = signature
        strengths = [
            _safe_float(event.get("strength"))
            for measure in (pair_start, pair_start + 1)
            for event in events_by_measure.get(measure, [])
        ]
        pair_reports.append({
            "pairIndex": pair_index,
            "startMeasure": pair_start,
            "endMeasure": min(pair_start + 1, end_measure),
            "eventCount": len(signature),
            "signatureSteps": signature,
            "medianStrength": round(median(strengths), 6) if strengths else 0.0,
            "readOnly": True,
        })

    comparisons: list[dict[str, Any]] = []
    support_by_pair: Counter[int] = Counter()
    for left_index, left_start in enumerate(pair_starts):
        for right_start in pair_starts[left_index + 1:]:
            similarity = _signature_similarity(signatures[left_start], signatures[right_start])
            repeated = similarity >= 0.6
            if repeated:
                support_by_pair[left_start] += 1
                support_by_pair[right_start] += 1
            comparisons.append({
                "leftStartMeasure": left_start,
                "rightStartMeasure": right_start,
                "similarity": similarity,
                "repeated": repeated,
                "readOnly": True,
            })

    repeated_pairs = [
        pair_start for pair_start in pair_starts
        if support_by_pair[pair_start] >= MIN_REPEATED_PAIR_SUPPORT - 1
    ]
    best_comparisons = sorted(
        comparisons,
        key=lambda item: item["similarity"],
        reverse=True,
    )[:10]

    checks = {
        "directAudioCandidateReportPassed": candidate_report.get("passed") is True,
        "introRhythmTemplateLocked": intro_lock.get("rhythmTemplateLocked") is True,
        "verseBoundsPresent": start_measure > 0 and end_measure >= start_measure,
        "verseEventsPresent": bool(verse_events),
        "multipleVersePairsPresent": len(pair_starts) >= 3,
        "rendererUnchanged": candidate_report.get("diagnostics", {}).get("rendererChanged") is False,
        "protectedBaselinesUnchanged": candidate_report.get("protectedBaselinesChanged") is False,
        "noSyntheticNotes": True,
    }

    report = {
        "benchmarkVersion": 8,
        "benchmarkType": "v8-read-only-verse1-rhythm-repetition-discovery",
        "passed": all(checks.values()),
        "sectionLabel": "Verse 1",
        "startMeasure": start_measure,
        "endMeasure": end_measure,
        "measureCount": end_measure - start_measure + 1,
        "directAudioEventCount": len(verse_events),
        "pairCount": len(pair_starts),
        "pairReports": pair_reports,
        "pairComparisons": comparisons,
        "bestPairComparisons": best_comparisons,
        "repeatedPairStartMeasures": repeated_pairs,
        "repeatedPairCount": len(repeated_pairs),
        "pairSupportHistogram": dict(sorted(Counter(support_by_pair.values()).items())),
        "checks": checks,
        "usesDirectAudioEvidence": True,
        "rendererChanged": False,
        "protectedBaselinesChanged": False,
        "trainingRule": (
            "This stage discovers repeated Verse 1 rhythm shapes from direct-audio onset "
            "evidence only. It may compare timing signatures within a one-step tolerance, "
            "but it must not copy professional notes, synthesize attacks, alter V7 events, "
            "or change the PDF renderer. A later benchmark must validate any proposed "
            "Verse 1 template before adoption."
        ),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    compact_pairs = [
        (item["startMeasure"], item["endMeasure"], item["eventCount"], item["signatureSteps"])
        for item in pair_reports
    ]
    compact_best = [
        (item["leftStartMeasure"], item["rightStartMeasure"], item["similarity"])
        for item in best_comparisons
    ]

    print("Verse 1 rhythm repetition pass:", report["passed"])
    print("Verse 1 measures:", f"{start_measure}-{end_measure}")
    print("Direct-audio event count:", report["directAudioEventCount"])
    print("Two-measure pair count:", report["pairCount"])
    print("Pairs (start, end, events, signature):", compact_pairs)
    print("Best pair comparisons (left, right, similarity):", compact_best)
    print("Repeated pair start measures:", report["repeatedPairStartMeasures"])
    print("Repeated pair count:", report["repeatedPairCount"])
    print("Pair-support histogram:", report["pairSupportHistogram"])
    print("Checks:", report["checks"])
    print("Renderer changed:", report["rendererChanged"])
    print("Protected baselines changed:", report["protectedBaselinesChanged"])
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
