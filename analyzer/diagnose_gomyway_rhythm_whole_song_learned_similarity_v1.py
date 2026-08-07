from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

SOURCE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
PROJECTION_PATH = PUBLIC / "gomyway-rhythm-learned-rules-whole-song-projection-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1-manifest.json"

FIRST_MEASURE = 1
LAST_MEASURE = 113
TRAINED_LAST_MEASURE = 35

STANDARD_TUNING_MIDI = {
    1: 64,
    2: 59,
    3: 55,
    4: 50,
    5: 45,
    6: 40,
}


def load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def source_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def normalize_note(note: dict[str, Any]) -> tuple[int, int] | None:
    string = integer(note.get("string", note.get("stringIndex")))
    fret = integer(note.get("fret"))
    if string is None or fret is None or not 0 <= fret <= 24:
        return None
    if 1 <= string <= 6:
        return string, fret
    if 0 <= string <= 5:
        return string + 1, fret
    return None


def notes_for_event(event: dict[str, Any]) -> list[tuple[int, int]]:
    raw = event.get("notes")
    if not isinstance(raw, list):
        return []
    result: set[tuple[int, int]] = set()
    for note in raw:
        if not isinstance(note, dict):
            continue
        normalized = normalize_note(note)
        if normalized is not None:
            result.add(normalized)
    return sorted(result)


def pitch_class(note: tuple[int, int]) -> int:
    string, fret = note
    return (STANDARD_TUNING_MIDI[string] + fret) % 12


def jaccard(a: set[Any], b: set[Any]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 1.0
    return len(a & b) / len(union)


def ratio_similarity(a: int, b: int) -> float:
    if a == 0 and b == 0:
        return 1.0
    if a <= 0 or b <= 0:
        return 0.0
    return min(a, b) / max(a, b)


def build_profiles(events: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    grouped: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        if measure is None or step is None or not FIRST_MEASURE <= measure <= LAST_MEASURE:
            continue
        grouped[measure][step].append(event)

    profiles: dict[int, dict[str, Any]] = {}
    for measure in range(FIRST_MEASURE, LAST_MEASURE + 1):
        step_map = grouped.get(measure, {})
        occupied_steps: set[int] = set()
        multiplicity_by_step: dict[int, int] = {}
        pitch_classes_by_step: dict[int, set[int]] = {}
        row_count = 0
        note_count = 0

        for step, rows in step_map.items():
            occupied_steps.add(step)
            row_count += len(rows)
            notes: set[tuple[int, int]] = set()
            for row in rows:
                row_notes = notes_for_event(row)
                note_count += len(row_notes)
                notes.update(row_notes)
            multiplicity_by_step[step] = len(notes)
            pitch_classes_by_step[step] = {pitch_class(note) for note in notes}

        profiles[measure] = {
            "measureNumber": measure,
            "occupiedSteps": occupied_steps,
            "multiplicityByStep": multiplicity_by_step,
            "pitchClassesByStep": pitch_classes_by_step,
            "sourceEventRows": row_count,
            "noteEventCount": note_count,
        }
    return profiles


def compare_profiles(a: dict[str, Any], b: dict[str, Any]) -> dict[str, float]:
    steps_a: set[int] = a["occupiedSteps"]
    steps_b: set[int] = b["occupiedSteps"]
    step_similarity = jaccard(steps_a, steps_b)

    shared_steps = steps_a & steps_b
    if shared_steps:
        multiplicity_scores = []
        pitch_scores = []
        for step in shared_steps:
            ma = int(a["multiplicityByStep"].get(step, 0))
            mb = int(b["multiplicityByStep"].get(step, 0))
            multiplicity_scores.append(1.0 - min(1.0, abs(ma - mb) / max(1, ma, mb)))
            pitch_scores.append(
                jaccard(
                    set(a["pitchClassesByStep"].get(step, set())),
                    set(b["pitchClassesByStep"].get(step, set())),
                )
            )
        multiplicity_similarity = sum(multiplicity_scores) / len(multiplicity_scores)
        pitch_class_similarity = sum(pitch_scores) / len(pitch_scores)
    else:
        multiplicity_similarity = 0.0
        pitch_class_similarity = 0.0

    row_density_similarity = ratio_similarity(a["sourceEventRows"], b["sourceEventRows"])
    note_density_similarity = ratio_similarity(a["noteEventCount"], b["noteEventCount"])

    structural_score = (
        step_similarity * 0.36
        + multiplicity_similarity * 0.28
        + row_density_similarity * 0.18
        + note_density_similarity * 0.18
    )
    musical_score = structural_score * 0.82 + pitch_class_similarity * 0.18

    return {
        "occupiedStepJaccard": round(step_similarity, 6),
        "sharedStepMultiplicitySimilarity": round(multiplicity_similarity, 6),
        "rowDensitySimilarity": round(row_density_similarity, 6),
        "noteDensitySimilarity": round(note_density_similarity, 6),
        "sharedStepPitchClassSimilarity": round(pitch_class_similarity, 6),
        "structuralSimilarityScore": round(structural_score, 6),
        "musicalSimilarityScore": round(musical_score, 6),
    }


def main() -> None:
    source_hash_before = sha256(SOURCE_PATH)
    source = load(SOURCE_PATH)
    projection = load(PROJECTION_PATH)
    events = source_rows(source)

    if len(events) != 949:
        raise RuntimeError(f"Expected 949 protected source events, found {len(events)}.")
    if projection.get("passed") is not True:
        raise RuntimeError("Whole-song learned-rules projection V1 is not green.")
    if projection.get("measureCount") != 113:
        raise RuntimeError("Projection V1 did not scan all 113 measures.")

    profiles = build_profiles(events)
    rows: list[dict[str, Any]] = []
    top_scores: list[float] = []

    for measure in range(TRAINED_LAST_MEASURE + 1, LAST_MEASURE + 1):
        comparisons: list[dict[str, Any]] = []
        for anchor in range(FIRST_MEASURE, TRAINED_LAST_MEASURE + 1):
            scores = compare_profiles(profiles[measure], profiles[anchor])
            comparisons.append({"anchorMeasure": anchor, **scores})

        comparisons.sort(
            key=lambda row: (
                float(row["structuralSimilarityScore"]),
                float(row["musicalSimilarityScore"]),
            ),
            reverse=True,
        )
        best = comparisons[0]
        runner_up = comparisons[1]
        margin = float(best["structuralSimilarityScore"]) - float(
            runner_up["structuralSimilarityScore"]
        )
        top_scores.append(float(best["structuralSimilarityScore"]))

        rows.append({
            "measureNumber": measure,
            "bestAnchorMeasure": best["anchorMeasure"],
            "bestStructuralSimilarityScore": best["structuralSimilarityScore"],
            "bestMusicalSimilarityScore": best["musicalSimilarityScore"],
            "runnerUpAnchorMeasure": runner_up["anchorMeasure"],
            "runnerUpStructuralSimilarityScore": runner_up["structuralSimilarityScore"],
            "bestVsRunnerUpMargin": round(margin, 6),
            "bestComparison": best,
            "topThreeComparisons": comparisons[:3],
            "classificationClaimed": False,
            "automaticApplyAllowed": False,
            "readOnlyDiagnostic": True,
        })

    score_ge_090 = sum(score >= 0.90 for score in top_scores)
    score_ge_080 = sum(score >= 0.80 for score in top_scores)
    score_ge_070 = sum(score >= 0.70 for score in top_scores)
    score_ge_060 = sum(score >= 0.60 for score in top_scores)

    source_hash_after = sha256(SOURCE_PATH)
    source_unchanged = source_hash_before == source_hash_after
    passed = bool(source_unchanged and len(rows) == 78)

    recommended = (
        "calibrate-gomyway-rhythm-whole-song-similarity-thresholds-v1"
        if passed
        else "diagnose-gomyway-rhythm-whole-song-learned-similarity-v1"
    )

    output = {
        "schemaVersion": 1,
        "diagnosticType": "read-only-whole-song-trained-measure-similarity",
        "passed": passed,
        "trainedMeasureRange": [1, 35],
        "untrainedMeasureRange": [36, 113],
        "untrainedMeasureCount": len(rows),
        "bestStructuralScoreAtLeast090Count": score_ge_090,
        "bestStructuralScoreAtLeast080Count": score_ge_080,
        "bestStructuralScoreAtLeast070Count": score_ge_070,
        "bestStructuralScoreAtLeast060Count": score_ge_060,
        "classificationClaimed": False,
        "rows": rows,
        "readyForSimilarityThresholdCalibration": passed,
        "recommendedNextAction": recommended,
        "automaticApplyAllowed": False,
        "protectedSourceEventCount": len(events),
        "protectedSourceHashBefore": source_hash_before,
        "protectedSourceHashAfter": source_hash_after,
        "protectedSourceHashUnchanged": source_unchanged,
        "sourceEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
    }

    manifest = {
        "schemaVersion": 1,
        "passed": passed,
        "untrainedMeasureCount": len(rows),
        "bestStructuralScoreAtLeast090Count": score_ge_090,
        "bestStructuralScoreAtLeast080Count": score_ge_080,
        "bestStructuralScoreAtLeast070Count": score_ge_070,
        "bestStructuralScoreAtLeast060Count": score_ge_060,
        "readyForSimilarityThresholdCalibration": passed,
        "recommendedNextAction": recommended,
        "automaticApplyAllowed": False,
        "protectedSourceHashUnchanged": source_unchanged,
        "protectedBaselinesChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY RHYTHM WHOLE SONG LEARNED SIMILARITY DIAGNOSTIC V1 COMPLETE")
    print("Passed:", passed)
    print("Untrained measures scanned:", len(rows))
    print("Best structural similarity >= 0.90:", score_ge_090)
    print("Best structural similarity >= 0.80:", score_ge_080)
    print("Best structural similarity >= 0.70:", score_ge_070)
    print("Best structural similarity >= 0.60:", score_ge_060)
    for row in rows:
        if float(row["bestStructuralSimilarityScore"]) >= 0.70:
            print(
                f"measure={row['measureNumber']} "
                f"anchor={row['bestAnchorMeasure']} "
                f"structural={row['bestStructuralSimilarityScore']} "
                f"musical={row['bestMusicalSimilarityScore']} "
                f"margin={row['bestVsRunnerUpMargin']}"
            )
    print("Classification claimed: False")
    print("Automatic apply allowed: False")
    print("Protected source event count:", len(events))
    print("Protected source hash unchanged:", source_unchanged)
    print("Source events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production promotion allowed: False")
    print("Ready for similarity threshold calibration:", passed)
    print("Recommended next action:", recommended)
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
