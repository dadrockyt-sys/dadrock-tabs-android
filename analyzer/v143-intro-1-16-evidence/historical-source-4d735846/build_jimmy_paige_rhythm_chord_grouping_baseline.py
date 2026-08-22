from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import median
from typing import Any

from run_jimmy_paige_em_riff_extraction_training_loop import REPO_ROOT

EVENTS_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json"
REGRESSION_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-regression-validation.json"
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-rhythm-chord-grouping-baseline.json"

GROUPING_WINDOWS_MS = [20, 30, 40, 50, 65, 80, 100]
MINIMUM_OVERLAP_MS = 20.0

PITCH_CLASS_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def _load_json(path: Path) -> Any:
    if not path.is_file():
        raise FileNotFoundError(f"Missing required file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize_event(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    try:
        start = float(raw.get("start", raw.get("start_time", 0.0)))
        end = float(raw.get("end", raw.get("end_time", start)))
        pitch = int(raw.get("midiPitch", raw.get("midi_pitch", raw.get("pitch"))))
        confidence = float(raw.get("confidence", raw.get("amplitude", 0.0)) or 0.0)
    except (TypeError, ValueError):
        return None
    return {
        "start": start,
        "end": max(start, end),
        "duration": max(0.0, end - start),
        "midiPitch": pitch,
        "confidence": confidence,
    }


def _group_events(events: list[dict[str, Any]], window_ms: float) -> list[dict[str, Any]]:
    window = window_ms / 1000.0
    groups: list[list[dict[str, Any]]] = []

    for event in sorted(events, key=lambda item: (item["start"], item["midiPitch"])):
        if not groups:
            groups.append([event])
            continue

        anchor = min(item["start"] for item in groups[-1])
        if event["start"] - anchor <= window:
            groups[-1].append(event)
        else:
            groups.append([event])

    output: list[dict[str, Any]] = []
    for index, group in enumerate(groups, start=1):
        starts = [item["start"] for item in group]
        ends = [item["end"] for item in group]
        pitches = sorted({int(item["midiPitch"]) for item in group})
        overlap = max(0.0, min(ends) - max(starts))
        output.append(
            {
                "groupNumber": index,
                "start": min(starts),
                "end": max(ends),
                "attackSpreadMs": round((max(starts) - min(starts)) * 1000.0, 3),
                "commonOverlapMs": round(overlap * 1000.0, 3),
                "eventCount": len(group),
                "uniquePitchCount": len(pitches),
                "midiPitches": pitches,
                "pitchClasses": sorted({PITCH_CLASS_NAMES[pitch % 12] for pitch in pitches}),
                "medianDurationMs": round(median(item["duration"] for item in group) * 1000.0, 3),
                "meanConfidence": round(sum(item["confidence"] for item in group) / len(group), 5),
                "isSimultaneousCandidate": bool(
                    len(pitches) >= 2 and overlap * 1000.0 >= MINIMUM_OVERLAP_MS
                ),
                "candidateType": (
                    "single-note"
                    if len(pitches) == 1
                    else "double-stop"
                    if len(pitches) == 2
                    else "chord"
                ),
            }
        )
    return output


def _interval_signature(pitches: list[int]) -> list[int]:
    if not pitches:
        return []
    root = min(pitches)
    return [pitch - root for pitch in sorted(pitches)]


def _summarize(groups: list[dict[str, Any]], window_ms: int) -> dict[str, Any]:
    candidates = [group for group in groups if group["isSimultaneousCandidate"]]
    double_stops = [group for group in candidates if group["candidateType"] == "double-stop"]
    chords = [group for group in candidates if group["candidateType"] == "chord"]

    signatures = Counter(
        tuple(_interval_signature(group["midiPitches"]))
        for group in candidates
    )
    pitch_sets = Counter(tuple(group["midiPitches"]) for group in candidates)

    return {
        "windowMs": window_ms,
        "totalAttackGroups": len(groups),
        "simultaneousCandidates": len(candidates),
        "doubleStopCandidates": len(double_stops),
        "chordCandidates": len(chords),
        "singleNoteGroups": sum(1 for group in groups if group["candidateType"] == "single-note"),
        "medianCandidateAttackSpreadMs": (
            round(median(group["attackSpreadMs"] for group in candidates), 3)
            if candidates
            else 0.0
        ),
        "medianCandidateOverlapMs": (
            round(median(group["commonOverlapMs"] for group in candidates), 3)
            if candidates
            else 0.0
        ),
        "mostCommonIntervalSignatures": [
            {"intervals": list(signature), "count": count}
            for signature, count in signatures.most_common(12)
        ],
        "mostCommonMidiPitchSets": [
            {"midiPitches": list(pitches), "count": count}
            for pitches, count in pitch_sets.most_common(12)
        ],
        "candidateGroups": candidates,
    }


def main() -> None:
    raw_events = _load_json(EVENTS_PATH)
    regression = _load_json(REGRESSION_PATH)

    if isinstance(raw_events, dict):
        raw_events = raw_events.get("events", [])
    events = [event for raw in raw_events if (event := _normalize_event(raw)) is not None]
    if not events:
        raise RuntimeError("No normalized winning events were found.")

    if not regression.get("combinedRegressionPassed"):
        raise RuntimeError("The protected 93.06% combined regression checkpoint is not marked as passed.")

    window_reports: list[dict[str, Any]] = []
    for window_ms in GROUPING_WINDOWS_MS:
        groups = _group_events(events, window_ms)
        report = _summarize(groups, window_ms)
        window_reports.append(report)
        print(
            f"Window {window_ms:>3} ms | groups={report['totalAttackGroups']} | "
            f"simultaneous={report['simultaneousCandidates']} | "
            f"doubleStops={report['doubleStopCandidates']} | chords={report['chordCandidates']}"
        )

    selected = min(
        window_reports,
        key=lambda item: (
            abs(item["medianCandidateAttackSpreadMs"] - 30.0),
            -item["simultaneousCandidates"],
        ),
    )

    output = {
        "benchmarkVersion": 1,
        "benchmarkType": "jimmy-paige-protected-rhythm-chord-grouping-baseline",
        "sourceEvents": str(EVENTS_PATH.relative_to(REPO_ROOT)),
        "protectedRegression": str(REGRESSION_PATH.relative_to(REPO_ROOT)),
        "protectedProfessionalScore": regression.get("professionalScore", {}).get("overallRecallPercentage"),
        "protectedNineSlotScore": regression.get("nineSlotCorrect"),
        "eventCount": len(events),
        "minimumCommonOverlapMs": MINIMUM_OVERLAP_MS,
        "groupingWindowsTestedMs": GROUPING_WINDOWS_MS,
        "selectedExploratoryWindowMs": selected["windowMs"],
        "selectionStatus": "diagnostic-only-not-production",
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "windowReports": window_reports,
        "nextRequiredStep": "build-professional-chord-targets-and-score-grouping-precision-recall",
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")

    print(
        "Chord grouping baseline complete | "
        f"selected exploratory window={selected['windowMs']} ms | "
        f"simultaneous candidates={selected['simultaneousCandidates']} | "
        f"double-stops={selected['doubleStopCandidates']} | chords={selected['chordCandidates']}"
    )
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
