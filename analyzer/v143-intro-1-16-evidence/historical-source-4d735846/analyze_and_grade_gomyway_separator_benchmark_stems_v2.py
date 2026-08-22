from __future__ import annotations

import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

BENCHMARK_PATH = PUBLIC / "gomyway-separator-upgrade-benchmark-v2-codespace.json"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-separator-benchmark-stem-grade-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-separator-benchmark-stem-grade-v2-manifest.json"

MEASURE_START = 17
MEASURE_END = 113
STEPS_PER_MEASURE = 16
CONTROL_PITCH_F1 = 4.73
CONTROL_PRIORITY_MATCHED = 0
CONTROL_PRIORITY_MISSING = 51
CONTROL_PRIORITY_EXTRA = 187
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]

# Use the same detector settings for both stems. The benchmark is intended to compare
# separation quality, not tune Basic Pitch independently per candidate.
ONSET_THRESHOLD = 0.50
FRAME_THRESHOLD = 0.30
MINIMUM_NOTE_LENGTH_MS = 58.0
SNAP_TOLERANCE_SECONDS = 0.085


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing prerequisite: {path.relative_to(ROOT)}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected JSON object: {path.relative_to(ROOT)}")
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integer(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def floating(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def candidate_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("events", "candidates", "rhythmEvents", "renderEvents"):
        rows = payload.get(key)
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def measure_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("measureNumber", event.get("measure")))


def step_of(event: dict[str, Any]) -> int | None:
    return integer(event.get("quantizedStep", event.get("step")))


def first_source_start(event: dict[str, Any]) -> float | None:
    for key in ("sourceStart", "startTime", "start_time", "start"):
        value = floating(event.get(key))
        if value is not None:
            return value
    starts = event.get("sourceStarts")
    if isinstance(starts, list):
        values = [floating(item) for item in starts]
        values = [item for item in values if item is not None]
        if values:
            return min(values)
    return None


def infer_tempo(events: list[dict[str, Any]]) -> float:
    tempos = [floating(row.get("tempoBpm")) for row in events]
    tempos = [value for value in tempos if value and 40.0 <= value <= 240.0]
    if not tempos:
        return 129.0
    return float(statistics.median(tempos))


def build_timing_grid(events: list[dict[str, Any]]) -> tuple[dict[tuple[int, int], float], dict[str, Any]]:
    tempo = infer_tempo(events)
    beat_seconds = 60.0 / tempo
    step_seconds = beat_seconds / 4.0
    measure_seconds = beat_seconds * 4.0

    measure_start_samples: dict[int, list[float]] = defaultdict(list)
    for event in events:
        measure = measure_of(event)
        step = step_of(event)
        start = first_source_start(event)
        if measure is None or step is None or start is None:
            continue
        if not 1 <= measure <= MEASURE_END or not 0 <= step < STEPS_PER_MEASURE:
            continue
        measure_start_samples[measure].append(start - step * step_seconds)

    measured_starts = {
        measure: float(statistics.median(samples))
        for measure, samples in measure_start_samples.items()
        if samples
    }
    if not measured_starts:
        raise RuntimeError("Could not derive song timing grid from protected candidate events.")

    # Estimate a global measure-1 start by removing the expected measure displacement.
    base_samples = [
        start - (measure - 1) * measure_seconds
        for measure, start in measured_starts.items()
    ]
    global_measure1_start = float(statistics.median(base_samples))

    grid: dict[tuple[int, int], float] = {}
    residuals: list[float] = []
    for measure in range(MEASURE_START, MEASURE_END + 1):
        predicted_measure_start = global_measure1_start + (measure - 1) * measure_seconds
        if measure in measured_starts:
            residuals.append(measured_starts[measure] - predicted_measure_start)
        for step in range(STEPS_PER_MEASURE):
            grid[(measure, step)] = predicted_measure_start + step * step_seconds

    diagnostics = {
        "tempoBpm": round(tempo, 6),
        "stepSeconds": round(step_seconds, 9),
        "measureSeconds": round(measure_seconds, 9),
        "globalMeasure1Start": round(global_measure1_start, 9),
        "measuresWithDirectTimingEvidence": len(measured_starts),
        "medianAbsoluteMeasureStartResidualSeconds": round(
            statistics.median(abs(value) for value in residuals) if residuals else 0.0,
            9,
        ),
    }
    return grid, diagnostics


def reference_tokens(reference: dict[str, Any]) -> Counter[tuple[int, int, int]]:
    measures = reference.get("measures")
    if not isinstance(measures, list):
        raise RuntimeError("Professional reference measures missing.")
    tokens: Counter[tuple[int, int, int]] = Counter()
    for measure_row in measures:
        if not isinstance(measure_row, dict):
            continue
        measure = integer(measure_row.get("measureNumber"))
        if measure is None or not MEASURE_START <= measure <= MEASURE_END:
            continue
        events = measure_row.get("events")
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            step = integer(event.get("quantizedStep"))
            if step is None:
                continue
            notes = event.get("notes")
            if not isinstance(notes, list):
                continue
            for note in notes:
                if not isinstance(note, dict):
                    continue
                midi = integer(note.get("midi"))
                if midi is not None:
                    tokens[(measure, step, midi)] += 1
    return tokens


def f1(tp: int, predicted: int, expected: int) -> float:
    if predicted == 0 and expected == 0:
        return 1.0
    if tp == 0 or predicted == 0 or expected == 0:
        return 0.0
    precision = tp / predicted
    recall = tp / expected
    return 2.0 * precision * recall / (precision + recall)


def nearest_grid_slot(start_time: float, grid_items: list[tuple[tuple[int, int], float]]) -> tuple[tuple[int, int] | None, float]:
    best_slot: tuple[int, int] | None = None
    best_distance = float("inf")
    for slot, slot_time in grid_items:
        distance = abs(start_time - slot_time)
        if distance < best_distance:
            best_distance = distance
            best_slot = slot
    return best_slot, best_distance


def basic_pitch_notes(audio_path: Path) -> list[tuple[float, float, int, float]]:
    try:
        from basic_pitch.inference import predict
    except Exception as exc:  # pragma: no cover - environment-dependent
        raise RuntimeError(
            "basic-pitch is required in the active environment. Install with: "
            "python -m pip install basic-pitch"
        ) from exc

    _model_output, _midi_data, note_events = predict(
        str(audio_path),
        onset_threshold=ONSET_THRESHOLD,
        frame_threshold=FRAME_THRESHOLD,
        minimum_note_length=MINIMUM_NOTE_LENGTH_MS,
    )

    normalized: list[tuple[float, float, int, float]] = []
    for row in note_events:
        if len(row) < 4:
            continue
        start = floating(row[0])
        end = floating(row[1])
        pitch = integer(row[2])
        amplitude = floating(row[3])
        if start is None or end is None or pitch is None or amplitude is None:
            continue
        normalized.append((start, end, pitch, amplitude))
    return normalized


def analyze_stem(
    name: str,
    path: Path,
    grid: dict[tuple[int, int], float],
    reference: Counter[tuple[int, int, int]],
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Benchmark stem missing: {path.relative_to(ROOT)}")

    notes = basic_pitch_notes(path)
    grid_items = list(grid.items())
    predicted: Counter[tuple[int, int, int]] = Counter()
    discarded_outside_grid = 0
    snap_distances: list[float] = []

    for start, _end, midi, _amplitude in notes:
        slot, distance = nearest_grid_slot(start, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            discarded_outside_grid += 1
            continue
        measure, step = slot
        predicted[(measure, step, midi)] += 1
        snap_distances.append(distance)

    intersection = predicted & reference
    matched = sum(intersection.values())
    predicted_count = sum(predicted.values())
    reference_count = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    score = f1(matched, predicted_count, reference_count)

    priority_reference = Counter({
        token: count
        for token, count in reference.items()
        if token[0] in PRIORITY_MEASURES
    })
    priority_predicted = Counter({
        token: count
        for token, count in predicted.items()
        if token[0] in PRIORITY_MEASURES
    })
    priority_matched = sum((priority_reference & priority_predicted).values())
    priority_missing = sum((priority_reference - priority_predicted).values())
    priority_extra = sum((priority_predicted - priority_reference).values())

    by_measure: list[dict[str, Any]] = []
    for measure in range(MEASURE_START, MEASURE_END + 1):
        ref_measure = Counter({token: count for token, count in reference.items() if token[0] == measure})
        pred_measure = Counter({token: count for token, count in predicted.items() if token[0] == measure})
        measure_matched = sum((ref_measure & pred_measure).values())
        measure_predicted = sum(pred_measure.values())
        measure_reference = sum(ref_measure.values())
        by_measure.append({
            "measureNumber": measure,
            "pitchF1": round(100.0 * f1(measure_matched, measure_predicted, measure_reference), 2),
            "matched": measure_matched,
            "missing": sum((ref_measure - pred_measure).values()),
            "extra": sum((pred_measure - ref_measure).values()),
        })

    strongest = sorted(by_measure, key=lambda row: (row["pitchF1"], row["matched"]), reverse=True)[:12]
    weakest = sorted(by_measure, key=lambda row: (row["pitchF1"], -row["extra"]))[:12]

    return {
        "name": name,
        "audioPath": str(path.relative_to(ROOT)),
        "basicPitchRawNoteCount": len(notes),
        "snappedPredictionCount": predicted_count,
        "discardedOutsideGrid": discarded_outside_grid,
        "medianSnapDistanceSeconds": round(statistics.median(snap_distances), 6) if snap_distances else None,
        "pitchF1": round(100.0 * score, 2),
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "priorityBatch": {
            "matched": priority_matched,
            "missing": priority_missing,
            "extra": priority_extra,
        },
        "strongestMeasures": strongest,
        "weakestMeasures": weakest,
        "measureScores": by_measure,
    }


def main() -> None:
    benchmark = load_json(BENCHMARK_PATH)
    if benchmark.get("passed") is not True:
        raise RuntimeError("Separator benchmark V2 is not green.")
    if benchmark.get("professionalReferenceUsedForSeparation") is not False:
        raise RuntimeError("Professional reference was unexpectedly used during separation.")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = load_json(CANDIDATE_PATH)
    events = candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diagnostics = build_timing_grid(events)

    reference = load_json(REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference_counter = reference_tokens(reference)
    if not reference_counter:
        raise RuntimeError("No professional MIDI pitch tokens found.")

    stem_paths = benchmark.get("benchmarkStems")
    if not isinstance(stem_paths, list) or len(stem_paths) != 2:
        raise RuntimeError("Expected exactly two separator benchmark stems.")

    results = []
    for index, relative in enumerate(stem_paths):
        if not isinstance(relative, str):
            raise RuntimeError("Invalid benchmark stem path.")
        stem_path = ROOT / relative
        name = "demucs6s-direct" if index == 0 else "bsroformer-then-demucs6s"
        print(f"Analyzing {name}: {relative}")
        results.append(analyze_stem(name, stem_path, grid, reference_counter))

    ranked = sorted(
        results,
        key=lambda row: (
            float(row["pitchF1"]),
            int(row["priorityBatch"]["matched"]),
            -int(row["priorityBatch"]["extra"]),
        ),
        reverse=True,
    )
    winner = ranked[0]
    winner_improvement = round(float(winner["pitchF1"]) - CONTROL_PITCH_F1, 2)
    beats_control = float(winner["pitchF1"]) > CONTROL_PITCH_F1

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during stem grading.")

    output = {
        "schemaVersion": 2,
        "passed": True,
        "comparisonType": "identical-basic-pitch-analyzer-on-separator-benchmark-stems",
        "detectorSettings": {
            "onsetThreshold": ONSET_THRESHOLD,
            "frameThreshold": FRAME_THRESHOLD,
            "minimumNoteLengthMs": MINIMUM_NOTE_LENGTH_MS,
            "snapToleranceSeconds": SNAP_TOLERANCE_SECONDS,
        },
        "timingGrid": grid_diagnostics,
        "professionalReferenceRole": "downstream-grading-only",
        "professionalReferenceUsedDuringDetection": False,
        "control": {
            "pitchF1": CONTROL_PITCH_F1,
            "priorityBatch": {
                "matched": CONTROL_PRIORITY_MATCHED,
                "missing": CONTROL_PRIORITY_MISSING,
                "extra": CONTROL_PRIORITY_EXTRA,
            },
        },
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerImprovementVsControlPoints": winner_improvement,
        "winnerBeatsControl": beats_control,
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "readyForSeparatorDecisionReview": True,
        "recommendedNextAction": "review-gomyway-separator-analyzer-comparison-v2",
    }

    manifest = {
        "schemaVersion": 2,
        "passed": True,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerImprovementVsControlPoints": winner_improvement,
        "winnerBeatsControl": beats_control,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY SEPARATOR STEM ANALYZER COMPARISON V2 COMPLETE")
    print("Passed: True")
    print("Timing grid:", grid_diagnostics)
    print("Control pitch F1:", CONTROL_PITCH_F1)
    print("Control priority matched/missing/extra: 0 / 51 / 187")
    for result in results:
        batch = result["priorityBatch"]
        print(
            f"{result['name']}: pitchF1={result['pitchF1']} "
            f"rawNotes={result['basicPitchRawNoteCount']} snapped={result['snappedPredictionCount']} "
            f"matched={result['matchedPitchTokens']} missing={result['missingProfessionalPitchTokens']} "
            f"extra={result['extraCandidatePitchTokens']} "
            f"priority={batch['matched']}/{batch['missing']}/{batch['extra']}"
        )
    print("Winner:", winner["name"])
    print("Winner pitch F1:", winner["pitchF1"])
    print("Improvement vs control points:", winner_improvement)
    print("Winner beats control:", beats_control)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Ready for separator decision review: True")
    print("Recommended next action: review-gomyway-separator-analyzer-comparison-v2")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
