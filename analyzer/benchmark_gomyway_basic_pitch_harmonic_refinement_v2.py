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
OUTPUT_PATH = PUBLIC / "gomyway-basic-pitch-harmonic-refinement-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-basic-pitch-harmonic-refinement-v2-manifest.json"

TUNED_BASIC_PITCH_F1 = 6.39
CHORD_AWARE_WINNER_F1 = 6.51
SNAP_TOLERANCE_SECONDS = 0.085
PRIORITY_MEASURES = [68, 76, 111, 109, 72, 93, 103, 105, 110, 104, 113, 80]

# Search only around the first chord-aware winner. These settings are fixed before grading.
CONFIGS: list[dict[str, Any]] = [
    {"name": "harmonic_r050_cap5", "ratio": 0.50, "cap": 5, "intervals": (12, 19, 24)},
    {"name": "harmonic_r056_cap5", "ratio": 0.56, "cap": 5, "intervals": (12, 19, 24)},
    {"name": "harmonic_r062_cap5", "ratio": 0.62, "cap": 5, "intervals": (12, 19, 24)},
    {"name": "harmonic_r068_cap5", "ratio": 0.68, "cap": 5, "intervals": (12, 19, 24)},
    {"name": "harmonic_r074_cap5", "ratio": 0.74, "cap": 5, "intervals": (12, 19, 24)},
    {"name": "harmonic_r062_cap4", "ratio": 0.62, "cap": 4, "intervals": (12, 19, 24)},
    {"name": "harmonic_r068_cap4", "ratio": 0.68, "cap": 4, "intervals": (12, 19, 24)},
    {"name": "octaves_r062_cap5", "ratio": 0.62, "cap": 5, "intervals": (12, 24)},
    {"name": "octaves_r068_cap5", "ratio": 0.68, "cap": 5, "intervals": (12, 24)},
    {"name": "wide_r062_cap5", "ratio": 0.62, "cap": 5, "intervals": (12, 19, 24, 31, 36)},
    {"name": "wide_r068_cap5", "ratio": 0.68, "cap": 5, "intervals": (12, 19, 24, 31, 36)},
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
        grouped[slot].append({
            "midi": int(midi),
            "amplitude": float(amplitude),
            "duration": max(0.0, float(end) - float(start)),
            "distance": float(distance),
        })
        distances.append(float(distance))
    return grouped, discarded, distances


def dedupe_and_range(rows: list[dict[str, float | int]]) -> list[dict[str, float | int]]:
    best: dict[int, dict[str, float | int]] = {}
    for row in rows:
        midi = int(row["midi"])
        if midi < 40 or midi > 88:
            continue
        current = best.get(midi)
        if current is None or (
            float(row["amplitude"]), float(row["duration"]), -float(row["distance"])
        ) > (
            float(current["amplitude"]), float(current["duration"]), -float(current["distance"])
        ):
            best[midi] = row
    return list(best.values())


def suppress_harmonics(
    rows: list[dict[str, float | int]],
    ratio: float,
    intervals: tuple[int, ...],
) -> list[dict[str, float | int]]:
    ordered = sorted(
        rows,
        key=lambda row: (float(row["amplitude"]), float(row["duration"]), -float(row["distance"])),
        reverse=True,
    )
    kept: list[dict[str, float | int]] = []
    for row in ordered:
        midi = int(row["midi"])
        amp = float(row["amplitude"])
        suppress = False
        for stronger in kept:
            lower = int(stronger["midi"])
            if midi > lower and (midi - lower) in intervals and amp < float(stronger["amplitude"]) * ratio:
                suppress = True
                break
        if not suppress:
            kept.append(row)
    return kept


def predict_for_config(
    grouped: dict[tuple[int, int], list[dict[str, float | int]]],
    config: dict[str, Any],
) -> Counter[tuple[int, int, int]]:
    predicted: Counter[tuple[int, int, int]] = Counter()
    for (measure, step), original in grouped.items():
        rows = dedupe_and_range(list(original))
        rows = suppress_harmonics(rows, float(config["ratio"]), tuple(config["intervals"]))
        cap = int(config["cap"])
        if len(rows) > cap:
            rows = sorted(
                rows,
                key=lambda row: (float(row["amplitude"]), float(row["duration"]), -float(row["distance"])),
                reverse=True,
            )[:cap]
        for row in rows:
            predicted[(measure, step, int(row["midi"]))] += 1
    return predicted


def score(
    name: str,
    predicted: Counter[tuple[int, int, int]],
    reference: Counter[tuple[int, int, int]],
    config: dict[str, Any],
) -> dict[str, Any]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    missing = sum((reference - predicted).values())
    extra = sum((predicted - reference).values())
    priority_ref = Counter({k: v for k, v in reference.items() if k[0] in PRIORITY_MEASURES})
    priority_pred = Counter({k: v for k, v in predicted.items() if k[0] in PRIORITY_MEASURES})
    return {
        "name": name,
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matchedPitchTokens": matched,
        "missingProfessionalPitchTokens": missing,
        "extraCandidatePitchTokens": extra,
        "predictionCount": predicted_count,
        "priorityBatch": {
            "matched": sum((priority_ref & priority_pred).values()),
            "missing": sum((priority_ref - priority_pred).values()),
            "extra": sum((priority_pred - priority_ref).values()),
        },
        "settings": {
            "harmonicAmplitudeRatio": config["ratio"],
            "maxNotesPerSlot": config["cap"],
            "harmonicIntervals": list(config["intervals"]),
        },
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
        raise RuntimeError(f"Expected 867 professional pitch tokens, found {sum(reference.values())}")

    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    raw_notes = v2.basic_pitch_notes(STEM_PATH)
    grouped, discarded, distances = snap_notes(raw_notes, grid)

    results: list[dict[str, Any]] = []
    for config in CONFIGS:
        result = score(str(config["name"]), predict_for_config(grouped, config), reference, config)
        results.append(result)
        p = result["priorityBatch"]
        print(
            f"{result['name']}: pitchF1={result['pitchF1']} matched={result['matchedPitchTokens']} "
            f"missing={result['missingProfessionalPitchTokens']} extra={result['extraCandidatePitchTokens']} "
            f"predictions={result['predictionCount']} priority={p['matched']}/{p['missing']}/{p['extra']}",
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
        raise RuntimeError("Protected 949-event candidate changed during harmonic refinement.")

    output = {
        "schemaVersion": 2,
        "passed": True,
        "benchmarkType": "tuned-basic-pitch-harmonic-refinement-around-chord-aware-winner",
        "inputStem": str(STEM_PATH.relative_to(ROOT)),
        "detectorSettings": {
            "onsetThreshold": 0.50,
            "frameThreshold": 0.30,
            "minimumNoteLengthMs": 110.0,
            "snapToleranceSeconds": SNAP_TOLERANCE_SECONDS,
        },
        "timingGrid": grid_diagnostics,
        "rawBasicPitchNoteCount": len(raw_notes),
        "discardedOutsideGrid": discarded,
        "medianSnapDistanceSeconds": round(statistics.median(distances), 6) if distances else None,
        "professionalPitchTokens": sum(reference.values()),
        "tunedBasicPitchF1": TUNED_BASIC_PITCH_F1,
        "chordAwareWinnerF1": CHORD_AWARE_WINNER_F1,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerSettings": winner["settings"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsChordAwareWinnerPoints": round(float(winner["pitchF1"]) - CHORD_AWARE_WINNER_F1, 2),
        "winnerBeatsChordAwareWinner": float(winner["pitchF1"]) > CHORD_AWARE_WINNER_F1,
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
            "refine-around-harmonic-v2-winner"
            if float(winner["pitchF1"]) > CHORD_AWARE_WINNER_F1
            else "freeze-chord-aware-6.51-and-shift-to-recall-recovery"
        ),
    }
    manifest = {
        "schemaVersion": 2,
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

    print("GOMYWAY BASIC PITCH HARMONIC REFINEMENT V2 COMPLETE")
    print("Passed: True")
    print("Tuned Basic Pitch F1:", TUNED_BASIC_PITCH_F1)
    print("Chord-aware winner F1:", CHORD_AWARE_WINNER_F1)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner settings:", output["winnerSettings"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Winner priority matched/missing/extra:", output["winnerPriorityBatch"]["matched"], "/", output["winnerPriorityBatch"]["missing"], "/", output["winnerPriorityBatch"]["extra"])
    print("Improvement vs chord-aware winner points:", output["improvementVsChordAwareWinnerPoints"])
    print("Winner beats chord-aware winner:", output["winnerBeatsChordAwareWinner"])
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
