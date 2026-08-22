from __future__ import annotations

import json
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-chords-measures-33-38-v1.json"
TIMING_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-chords-measures-33-38-timing-v1.json"
EVENT_CANDIDATES = [
    REPO_ROOT / "public" / "gomyway-jimmy-paige-93-06-events.json",
    REPO_ROOT / "public" / "gomyway-jimmy-paige-full-song-winner-events.json",
]
OUTPUT_PATH = REPO_ROOT / "public" / "gomyway-jimmy-paige-chord-pitch-class-validation-63-67.json"

SOURCE_TO_HELD_OUT = {33: 63, 34: 64, 35: 65, 36: 66, 37: 67}
MAX_TIMING_DELTA = 0.30
MIN_EXACT_RECALL = 0.50
MIN_PITCH_CLASS_RECALL = 0.50


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def first_existing(paths: list[Path]) -> Path:
    for path in paths:
        if path.is_file():
            return path
    raise FileNotFoundError("No protected event cache found")


def event_start(event: dict[str, Any]) -> float:
    return float(event.get("start", event.get("start_time", 0.0)))


def event_pitch(event: dict[str, Any]) -> int:
    return int(event.get("midiPitch", event.get("pitch", -999)))


def fret_to_midi(voicing: list[int | None]) -> list[int]:
    open_strings = [64, 59, 55, 50, 45, 40]
    return [open_pitch + int(fret) for open_pitch, fret in zip(open_strings, voicing) if fret is not None]


def measure_bounds(measure: int, tempo: float, offset: float) -> tuple[float, float]:
    duration = 4.0 * 60.0 / tempo
    start = offset + (measure - 1) * duration
    return start, start + duration


def group_events(events: list[dict[str, Any]], window: float) -> list[list[dict[str, Any]]]:
    groups: list[list[dict[str, Any]]] = []
    for event in sorted(events, key=event_start):
        if not groups or event_start(event) - event_start(groups[-1][0]) > window:
            groups.append([event])
        else:
            groups[-1].append(event)
    return [group for group in groups if len(group) >= 2]


def recall(expected: set[int], observed: set[int]) -> float:
    return len(expected & observed) / len(expected) if expected else 0.0


def main() -> None:
    reference = load(REFERENCE_PATH)
    timing = load(TIMING_PATH)["bestCalibration"]
    events_path = first_existing(EVENT_CANDIDATES)
    events = load(events_path)

    tempo = float(timing["tempoBpm"])
    offset = float(timing["firstMeasureOffsetSeconds"])
    window = float(timing["groupWindowSeconds"])

    attack_rows: list[dict[str, Any]] = []

    for source_measure in reference["measures"]:
        source_number = int(source_measure["measureNumber"])
        if source_number not in SOURCE_TO_HELD_OUT:
            continue
        held_out_number = SOURCE_TO_HELD_OUT[source_number]
        start, end = measure_bounds(held_out_number, tempo, offset)
        local_events = [event for event in events if start - MAX_TIMING_DELTA <= event_start(event) <= end + MAX_TIMING_DELTA]
        groups = group_events(local_events, window)

        for attack_number, attack in enumerate(source_measure["attacks"], start=1):
            target_time = start + (end - start) * float(attack["phase"])
            expected_pitches = set(fret_to_midi(attack["voicingFretsHighToLow"]))
            expected_classes = {pitch % 12 for pitch in expected_pitches}

            best: dict[str, Any] | None = None
            for group in groups:
                center = median([event_start(item) for item in group])
                delta = abs(center - target_time)
                observed = {event_pitch(item) for item in group}
                exact = recall(expected_pitches, observed)
                pitch_class = recall(expected_classes, {pitch % 12 for pitch in observed})
                candidate = {
                    "center": center,
                    "delta": delta,
                    "observed": sorted(observed),
                    "exact": exact,
                    "pitchClass": pitch_class,
                }
                rank = (delta > MAX_TIMING_DELTA, -pitch_class, -exact, delta)
                if best is None or rank < best["rank"]:
                    candidate["rank"] = rank
                    best = candidate

            if best is None:
                best = {"center": None, "delta": None, "observed": [], "exact": 0.0, "pitchClass": 0.0}

            timing_pass = best["delta"] is not None and float(best["delta"]) <= MAX_TIMING_DELTA
            exact_pass = timing_pass and float(best["exact"]) >= MIN_EXACT_RECALL
            pitch_class_pass = timing_pass and float(best["pitchClass"]) >= MIN_PITCH_CLASS_RECALL
            guarded_pass = exact_pass or pitch_class_pass

            attack_rows.append({
                "sourceMeasureNumber": source_number,
                "heldOutMeasureNumber": held_out_number,
                "attackNumber": attack_number,
                "chordLabels": source_measure["chordLabels"],
                "targetPhase": attack["phase"],
                "targetTimeSeconds": round(target_time, 6),
                "expectedPitches": sorted(expected_pitches),
                "candidatePitches": best["observed"],
                "absoluteTimingDeltaSeconds": round(float(best["delta"]), 6) if best["delta"] is not None else None,
                "exactVoicingRecall": round(float(best["exact"]), 4),
                "pitchClassRecall": round(float(best["pitchClass"]), 4),
                "exactPass": exact_pass,
                "pitchClassPass": pitch_class_pass,
                "guardedPass": guarded_pass,
            })

    exact_matches = sum(1 for row in attack_rows if row["exactPass"])
    pitch_class_matches = sum(1 for row in attack_rows if row["pitchClassPass"])
    guarded_matches = sum(1 for row in attack_rows if row["guardedPass"])
    total = len(attack_rows)

    measure_reports = []
    for measure in range(63, 68):
        rows = [row for row in attack_rows if row["heldOutMeasureNumber"] == measure]
        measure_reports.append({
            "measureNumber": measure,
            "exactMatchedAttacks": sum(1 for row in rows if row["exactPass"]),
            "pitchClassMatchedAttacks": sum(1 for row in rows if row["pitchClassPass"]),
            "guardedMatchedAttacks": sum(1 for row in rows if row["guardedPass"]),
            "targetAttacks": len(rows),
            "attacks": rows,
        })

    payload = {
        "benchmarkVersion": 1,
        "benchmarkType": "held-out-professional-chorus-pitch-class-validation",
        "trainedSectionMeasures": [33, 34, 35, 36, 37],
        "heldOutSectionMeasures": [63, 64, 65, 66, 67],
        "sourceEvents": str(events_path.relative_to(REPO_ROOT)),
        "tempoBpm": tempo,
        "firstMeasureOffsetSeconds": offset,
        "groupWindowSeconds": window,
        "exactMatchedAttacks": exact_matches,
        "pitchClassMatchedAttacks": pitch_class_matches,
        "guardedMatchedAttacks": guarded_matches,
        "targetAttacks": total,
        "exactRecallPercentage": round(100.0 * exact_matches / total if total else 0.0, 2),
        "pitchClassRecallPercentage": round(100.0 * pitch_class_matches / total if total else 0.0, 2),
        "guardedRecallPercentage": round(100.0 * guarded_matches / total if total else 0.0, 2),
        "measureReports": measure_reports,
        "professionalPdfRemainsScoringAuthority": True,
        "productionPromotionAllowed": False,
        "syntheticNotesAllowed": False,
        "protectedPitchCheckpointChanged": False,
        "generalizationPassed": total > 0 and guarded_matches / total >= 0.80,
    }

    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print("Held-out chorus chord validation complete")
    print(f"Exact voicing: {exact_matches}/{total} ({payload['exactRecallPercentage']:.2f}%)")
    print(f"Pitch class: {pitch_class_matches}/{total} ({payload['pitchClassRecallPercentage']:.2f}%)")
    print(f"Guarded: {guarded_matches}/{total} ({payload['guardedRecallPercentage']:.2f}%)")
    for row in measure_reports:
        print(
            f"Measure {row['measureNumber']} | exact={row['exactMatchedAttacks']}/{row['targetAttacks']} | "
            f"pitchClass={row['pitchClassMatchedAttacks']}/{row['targetAttacks']} | "
            f"guarded={row['guardedMatchedAttacks']}/{row['targetAttacks']}"
        )
    print(f"Generalization passed: {payload['generalizationPassed']}")
    print("Professional PDF remains scoring authority: True")
    print("Protected 93.06% pitch checkpoint changed: False")
    print(f"Output: {OUTPUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
