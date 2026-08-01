from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
)
EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
]
CALIBRATION_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-professional-measures-1-16-timing-calibration.json",
    REPO_ROOT / "public" / "gomyway-professional-timing-map-v2.json",
]
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "gomyway-professional-rhythm-chords-measures-33-38-timing-v1.json"
)

TEMPO_SEARCH = [
    133.80,
    134.40,
    135.00,
    135.40,
    135.88,
    136.20,
]
OFFSET_ADJUSTMENTS = [-0.80, -0.60, -0.40, -0.20, 0.0, 0.20, 0.40, 0.60, 0.80]
TIMING_WINDOWS = [0.08, 0.12, 0.16, 0.22, 0.30]
MIN_GROUP_SIZE = 2


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError(
        "None of the required files exist: " + ", ".join(str(path) for path in paths)
    )


def _event_start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def _event_pitch(event: dict[str, Any]) -> int:
    return int(event.get("midiPitch", event.get("pitch", -999)))


def _base_timing(calibration: Any) -> tuple[float, float]:
    if isinstance(calibration, dict):
        tempo_keys = ["bestTempo", "resolvedTempo", "tempo", "tempoBpm", "bpm"]
        offset_keys = [
            "bestFirstMeasureOffsetSeconds",
            "resolvedFirstMeasureOffset",
            "firstMeasureOffsetSeconds",
            "offsetSeconds",
        ]
        tempo = next(
            (float(calibration[key]) for key in tempo_keys if key in calibration),
            135.88,
        )
        offset = next(
            (float(calibration[key]) for key in offset_keys if key in calibration),
            5.045,
        )
        return tempo, offset
    return 135.88, 5.045


def _fret_to_midi(voicing: list[int | None]) -> list[int]:
    open_strings = [64, 59, 55, 50, 45, 40]
    return [
        open_pitch + int(fret)
        for open_pitch, fret in zip(open_strings, voicing)
        if fret is not None
    ]


def _measure_bounds(measure: int, tempo: float, offset: float) -> tuple[float, float]:
    measure_duration = 4.0 * 60.0 / tempo
    start = offset + (measure - 1) * measure_duration
    return start, start + measure_duration


def _group_events(events: list[dict[str, Any]], window: float) -> list[list[dict[str, Any]]]:
    ordered = sorted(events, key=_event_start)
    groups: list[list[dict[str, Any]]] = []
    for event in ordered:
        if not groups or _event_start(event) - _event_start(groups[-1][0]) > window:
            groups.append([event])
        else:
            groups[-1].append(event)
    return [group for group in groups if len(group) >= MIN_GROUP_SIZE]


def _score_candidate(
    reference: dict[str, Any],
    events: list[dict[str, Any]],
    tempo: float,
    offset: float,
    window: float,
) -> dict[str, Any]:
    target_count = 0
    matched = 0
    timing_deltas: list[float] = []
    measure_rows: list[dict[str, Any]] = []

    for measure in reference["measures"]:
        number = int(measure["measureNumber"])
        start, end = _measure_bounds(number, tempo, offset)
        local_events = [event for event in events if start - 0.30 <= _event_start(event) <= end + 0.30]
        groups = _group_events(local_events, window)

        matched_attacks = 0
        attack_rows: list[dict[str, Any]] = []
        for attack in measure["attacks"]:
            target_count += 1
            target_time = start + (end - start) * float(attack["phase"])
            expected_pitches = set(_fret_to_midi(attack["voicingFretsHighToLow"]))

            best: tuple[float, float, list[dict[str, Any]]] | None = None
            for group in groups:
                center = median([_event_start(item) for item in group])
                delta = abs(center - target_time)
                group_pitches = {_event_pitch(item) for item in group}
                overlap = len(expected_pitches & group_pitches) / max(1, len(expected_pitches))
                candidate = (delta, -overlap, group)
                if best is None or candidate[:2] < best[:2]:
                    best = candidate

            passed = False
            row: dict[str, Any] = {
                "targetPhase": attack["phase"],
                "targetTimeSeconds": round(target_time, 6),
                "expectedPitches": sorted(expected_pitches),
            }
            if best is not None:
                delta, negative_overlap, group = best
                overlap = -negative_overlap
                center = median([_event_start(item) for item in group])
                passed = delta <= 0.30 and overlap >= 0.50
                row.update(
                    {
                        "candidateCenterSeconds": round(center, 6),
                        "timingDeltaSeconds": round(center - target_time, 6),
                        "absoluteTimingDeltaSeconds": round(delta, 6),
                        "candidatePitches": sorted({_event_pitch(item) for item in group}),
                        "voicingRecall": round(overlap, 4),
                        "passed": passed,
                    }
                )
                if passed:
                    matched += 1
                    matched_attacks += 1
                    timing_deltas.append(center - target_time)
            else:
                row["passed"] = False
            attack_rows.append(row)

        measure_rows.append(
            {
                "measureNumber": number,
                "matchedAttacks": matched_attacks,
                "targetAttacks": len(measure["attacks"]),
                "attacks": attack_rows,
            }
        )

    recall = 100.0 * matched / target_count if target_count else 0.0
    median_abs = median([abs(value) for value in timing_deltas]) if timing_deltas else 999.0
    score = recall - median_abs * 10.0
    return {
        "tempoBpm": tempo,
        "firstMeasureOffsetSeconds": offset,
        "groupWindowSeconds": window,
        "matchedAttacks": matched,
        "targetAttacks": target_count,
        "attackRecallPercentage": round(recall, 2),
        "medianSignedTimingDeltaSeconds": round(median(timing_deltas), 6) if timing_deltas else None,
        "medianAbsoluteTimingDeltaSeconds": round(median_abs, 6) if timing_deltas else None,
        "selectionScore": round(score, 6),
        "measureReports": measure_rows,
    }


def main() -> None:
    reference = _load(REFERENCE_PATH)
    events_path = _first_existing(EVENT_CANDIDATES)
    calibration_path = _first_existing(CALIBRATION_CANDIDATES)
    events = _load(events_path)
    calibration = _load(calibration_path)
    base_tempo, base_offset = _base_timing(calibration)

    tempos = sorted(set(TEMPO_SEARCH + [round(base_tempo, 3)]))
    candidates: list[dict[str, Any]] = []
    for tempo in tempos:
        for adjustment in OFFSET_ADJUSTMENTS:
            offset = base_offset + adjustment
            for window in TIMING_WINDOWS:
                candidates.append(
                    _score_candidate(reference, events, tempo, offset, window)
                )

    best = max(
        candidates,
        key=lambda row: (
            row["selectionScore"],
            row["attackRecallPercentage"],
            -row["groupWindowSeconds"],
        ),
    )

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "professional-rhythm-chord-section-timing-calibration",
        "sourceReference": str(REFERENCE_PATH.relative_to(REPO_ROOT)),
        "sourceEvents": str(events_path.relative_to(REPO_ROOT)),
        "sourceTimingCalibration": str(calibration_path.relative_to(REPO_ROOT)),
        "baseTempoBpm": base_tempo,
        "baseFirstMeasureOffsetSeconds": base_offset,
        "candidateCount": len(candidates),
        "bestCalibration": best,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "rendererChanged": False,
        "protectedPitchCheckpointChanged": False,
        "readyForChordBaselineScoring": best["matchedAttacks"] > 0,
        "readyForAutomatedTraining": False,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Professional chord-section timing calibration complete")
    print(f"Candidates tested: {len(candidates)}")
    print(
        "Best calibration | "
        f"tempo={best['tempoBpm']:.3f} BPM | "
        f"offset={best['firstMeasureOffsetSeconds']:.3f}s | "
        f"groupWindow={best['groupWindowSeconds'] * 1000:.0f} ms"
    )
    print(
        f"Matched chord attacks: {best['matchedAttacks']}/{best['targetAttacks']} "
        f"({best['attackRecallPercentage']:.2f}%)"
    )
    print(
        "Median absolute timing delta: "
        f"{best['medianAbsoluteTimingDeltaSeconds']} seconds"
    )
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
