from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
STEM_PATH = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-basic-pitch-chord-aware-filter-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-basic-pitch-chord-aware-filter-v1-manifest.json"

TUNED_BASIC_PITCH_F1 = 6.39
SNAP_TOLERANCE_SECONDS = 0.085
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]

# Fixed before grading. None of these settings use the professional reference during detection.
CONFIGS: list[dict[str, Any]] = [
    {"name": "tuned_raw", "dedupe": False, "minMidi": None, "maxMidi": None, "maxNotesPerSlot": None, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "dedupe", "dedupe": True, "minMidi": None, "maxMidi": None, "maxNotesPerSlot": None, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "guitar_range", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": None, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "cap6", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 6, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "cap5", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 5, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "cap4", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 4, "minAmplitude": 0.0, "harmonicSuppression": False},
    {"name": "cap6_amp015", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 6, "minAmplitude": 0.15, "harmonicSuppression": False},
    {"name": "cap5_amp015", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 5, "minAmplitude": 0.15, "harmonicSuppression": False},
    {"name": "cap5_harmonic", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 5, "minAmplitude": 0.0, "harmonicSuppression": True},
    {"name": "cap4_harmonic", "dedupe": True, "minMidi": 40, "maxMidi": 88, "maxNotesPerSlot": 4, "minAmplitude": 0.0, "harmonicSuppression": True},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snap_notes(
    notes: list[tuple[float, float, int, float]],
    grid: dict[tuple[int, int], float],
) -> tuple[dict[tuple[int, int], list[dict[str, float | int]]], int, list[float]]:
    grid_items = list(grid.items())
    grouped: dict[tuple[int, int], list[dict[str, float | int]]] = defaultdict(list)
    discarded = 0
    distances: list[float] = []
    for start, end, midi, amplitude in notes:
        slot, distance = v2.nearest_grid_slot(start, grid_items)
        if slot is None or distance > SNAP_TOLERANCE_SECONDS:
            discarded += 1
            continue
        grouped[slot].append(
            {
                "midi": int(midi),
                "amplitude": float(amplitude),
                "duration": max(0.0, float(end) - float(start)),
                "distance": float(distance),
            }
        )
        distances.append(float(distance))
    return grouped, discarded, distances


def suppress_harmonics(rows: list[dict[str, float | int]]) -> list[dict[str, float | int]]:
    # Conservative suppression only: remove a weak upper octave / twelfth / double-octave
    # when a materially stronger lower candidate is present in the same rhythmic slot.
    ordered = sorted(rows, key=lambda row: (float(row["amplitude"]), float(row["duration"])), reverse=True)
    kept: list[dict[str, float | int]] = []
    for row in ordered:
        midi = int(row["midi"])
        amp = float(row["amplitude"])
        suppress = False
        for stronger in kept:
            lower = int(stronger["midi"])
            interval = midi - lower
            if interval in (12, 19, 24) and amp < float(stronger["amplitude"]) * 0.62:
                suppress = True
                break
        if not suppress:
            kept.append(row)
    return kept


def apply_config(
    grouped: dict[tuple[int, int], list[dict[str, float | int]]],
    config: dict[str, Any],
) -> Counter[tuple[int, int, int]]:
    predicted: Counter[tuple[int, int, int]] = Counter()
    for (measure, step), original_rows in grouped.items():
        rows = list(original_rows)

        min_midi = config.get("minMidi")
        max_midi = config.get("maxMidi")
        min_amp = float(config.get("minAmplitude", 0.0))
        rows = [
            row for row in rows
            if (min_midi is None or int(row["midi"]) >= int(min_midi))
            and (max_midi is None or int(row["midi"]) <= int(max_midi))
            and float(row["amplitude"]) >= min_amp
        ]

        if config.get("dedupe"):
            best_by_pitch: dict[int, dict[str, float | int]] = {}
            for row in rows:
                pitch = int(row["midi"])
                current = best_by_pitch.get(pitch)
                if current is None or (float(row["amplitude"]), float(row["duration"])) > (
                    float(current["amplitude"]), float(current["duration"])
                ):
                    best_by_pitch[pitch] = row
            rows = list(best_by_pitch.values())

        if config.get("harmonicSuppression"):
            rows = suppress_harmonics(rows)

        cap = config.get("maxNotesPerSlot")
        if cap is not None and len(rows) > int(cap):
            # Amplitude is primary evidence; duration and proximity to the timing grid break ties.
            rows = sorted(
                rows,
                key=lambda row: (
                    float(row["amplitude"]),
                    float(row["duration"]),
                    -float(row["distance"]),
                ),
                reverse=True,
            )[: int(cap)]

        for row in rows:
            predicted[(measure, step, int(row["midi"]))] += 1
    return predicted


def score_prediction(
    name: str,
    predicted: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    config: dict[str, Any],
) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    reference_count = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    pitch_f1 = round(100.0 * v2.f1(matched, predicted_count, reference_count), 2)

    priority_reference = Counter({k: v for k, v in reference.items() if k[0] in PRIORITY_MEASURES})
    priority_predicted = Counter({k: v for k, v in predicted.items() if k[0] in PRIORITY_MEASURES})
    priority_matched = sum((priority_reference & priority_predicted).values())
    priority_missing = sum((priority_reference - priority_predicted).values())
    priority_extra = sum((priority_predicted - priority_reference).values())

    return {
        "name": name,
        "pitchF1": pitch_f1,
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "predictionCount": predicted_count,
        "priorityBatch": {
            "matched": priority_matched,
            "missing": priority_missing,
            "extra": priority_extra,
        },
        "settings": config,
    }


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winning separator stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diagnostics = v2.build_timing_grid(events)
    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)
    if sum(reference.values()) != 867:
        raise RuntimeError(f"Expected 867 normalized professional pitch tokens, found {sum(reference.values())}")

    # Lock to the only detector settings that have won so far.
    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    raw_notes = v2.basic_pitch_notes(STEM_PATH)
    grouped, discarded, distances = snap_notes(raw_notes, grid)

    results: list[dict[str, Any]] = []
    for config in CONFIGS:
        predicted = apply_config(grouped, config)
        result = score_prediction(str(config["name"]), predicted, reference, config)
        results.append(result)
        print(
            f"{result['name']}: pitchF1={result['pitchF1']} "
            f"matched={result['matchedPitchTokens']} missing={result['missingProfessionalPitchTokens']} "
            f"extra={result['extraCandidatePitchTokens']} predictions={result['predictionCount']} "
            f"priority={result['priorityBatch']['matched']}/{result['priorityBatch']['missing']}/{result['priorityBatch']['extra']}",
            flush=True,
        )

    ranked = sorted(
        results,
        key=lambda row: (
            float(row["pitchF1"]),
            int(row["matchedPitchTokens"]),
            -int(row["extraCandidatePitchTokens"]),
        ),
        reverse=True,
    )
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during chord-aware benchmark.")

    improvement = round(float(winner["pitchF1"]) - TUNED_BASIC_PITCH_F1, 2)
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "tuned-basic-pitch-chord-aware-postfilter",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "detectorSettings": {
            "onsetThreshold": 0.50,
            "frameThreshold": 0.30,
            "minimumNoteLengthMs": 110.0,
            "snapToleranceSeconds": SNAP_TOLERANCE_SECONDS,
        },
        "timingGrid": grid_diagnostics,
        "rawBasicPitchNoteCount": len(raw_notes),
        "snappedSlotCount": len(grouped),
        "discardedOutsideGrid": discarded,
        "medianSnapDistanceSeconds": round(statistics.median(distances), 6) if distances else None,
        "professionalPitchTokens": sum(reference.values()),
        "tunedBasicPitchF1": TUNED_BASIC_PITCH_F1,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsTunedBasicPitchPoints": improvement,
        "winnerBeatsTunedBasicPitch": float(winner["pitchF1"]) > TUNED_BASIC_PITCH_F1,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "refine-chord-aware-filter-around-winner"
            if float(winner["pitchF1"]) > TUNED_BASIC_PITCH_F1
            else "retain-tuned-basic-pitch-and-test-pitch-class-chord-model"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "professionalReferenceUsedDuringDetection": False,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY BASIC PITCH CHORD-AWARE FILTER V1 COMPLETE")
    print("Passed: True")
    print("Tuned Basic Pitch F1:", TUNED_BASIC_PITCH_F1)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Winner priority matched/missing/extra:", output["winnerPriorityBatch"]["matched"], "/", output["winnerPriorityBatch"]["missing"], "/", output["winnerPriorityBatch"]["extra"])
    print("Improvement vs tuned Basic Pitch points:", improvement)
    print("Winner beats tuned Basic Pitch:", output["winnerBeatsTunedBasicPitch"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
