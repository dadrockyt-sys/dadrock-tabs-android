from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_basic_pitch_harmonic_refinement_v2 as harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-cross-stem-consensus-recall-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-cross-stem-consensus-recall-v1-manifest.json"

CURRENT_CHAMPION_F1 = 6.60
CURRENT_CHAMPION_MATCHED = 63
SNAP_TOLERANCE_SECONDS = 0.085
HARMONIC_CONFIG = {"name": "harmonic_r074_cap5", "ratio": 0.74, "cap": 5, "intervals": (12, 19, 24)}
PRIORITY_MEASURES = harmonic.PRIORITY_MEASURES


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def group_rows(path: Path, grid: dict[tuple[int, int], float]) -> dict[tuple[int, int], list[dict[str, float | int]]]:
    v2.ONSET_THRESHOLD = 0.50
    v2.FRAME_THRESHOLD = 0.30
    v2.MINIMUM_NOTE_LENGTH_MS = 110.0
    notes = v2.basic_pitch_notes(path)
    grouped, _discarded, _distances = harmonic.snap_notes(notes, grid)
    return grouped


def prediction(grouped: dict[tuple[int, int], list[dict[str, float | int]]]) -> Counter[tuple[int, int, int]]:
    return harmonic.predict_for_config(grouped, HARMONIC_CONFIG)


def merge_rows(
    winner_grouped: dict[tuple[int, int], list[dict[str, float | int]]],
    alt_grouped: dict[tuple[int, int], list[dict[str, float | int]]],
    mode: str,
) -> Counter[tuple[int, int, int]]:
    base = prediction(winner_grouped)
    alt = prediction(alt_grouped)

    if mode == "champion_only":
        return base

    merged = Counter(base)
    for token in alt:
        if token in merged:
            continue
        measure, step, midi = token
        slot_count = sum(count for (m, s, _p), count in merged.items() if m == measure and s == step)
        if slot_count >= 5:
            continue

        if mode == "alt_additions_all":
            merged[token] += 1
            continue

        # Cross-stem structural support: prefer additions that agree with an existing
        # pitch-class neighborhood in the winner stem or repeat in an adjacent slot.
        winner_slot = {p for (m, s, p) in base if m == measure and s == step}
        same_pc_support = any((p - midi) % 12 in {0, 3, 4, 5, 7, 8, 9} for p in winner_slot)
        neighbor_repeat = any(
            (measure, neighbor_step, midi) in base
            for neighbor_step in (step - 1, step + 1)
            if neighbor_step >= 0
        )

        if mode == "alt_additions_neighbor" and neighbor_repeat:
            merged[token] += 1
        elif mode == "alt_additions_chord_or_neighbor" and (same_pc_support or neighbor_repeat):
            merged[token] += 1
        elif mode == "alt_additions_chord_and_neighbor" and same_pc_support and neighbor_repeat:
            merged[token] += 1

    return merged


def score(name: str, predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, Any]:
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
    }


def main() -> None:
    for path in (WINNER_STEM, ALT_STEM):
        if not path.exists():
            raise FileNotFoundError(f"Missing benchmark stem: {path.relative_to(ROOT)}")

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

    print("Analyzing winner stem...", flush=True)
    winner_grouped = group_rows(WINNER_STEM, grid)
    print("Analyzing alternate direct-Demucs stem...", flush=True)
    alt_grouped = group_rows(ALT_STEM, grid)

    modes = [
        "champion_only",
        "alt_additions_all",
        "alt_additions_neighbor",
        "alt_additions_chord_or_neighbor",
        "alt_additions_chord_and_neighbor",
    ]
    results = []
    for mode in modes:
        result = score(mode, merge_rows(winner_grouped, alt_grouped, mode), reference)
        results.append(result)
        p = result["priorityBatch"]
        print(
            f"{mode}: pitchF1={result['pitchF1']} matched={result['matchedPitchTokens']} "
            f"missing={result['missingProfessionalPitchTokens']} extra={result['extraCandidatePitchTokens']} "
            f"predictions={result['predictionCount']} priority={p['matched']}/{p['missing']}/{p['extra']}",
            flush=True,
        )

    ranked = sorted(
        results,
        key=lambda row: (float(row["pitchF1"]), int(row["matchedPitchTokens"]), -int(row["extraCandidatePitchTokens"])),
        reverse=True,
    )
    winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during cross-stem benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "cross-separator-stem-consensus-recall",
        "winnerStem": str(WINNER_STEM.relative_to(ROOT)),
        "alternateStem": str(ALT_STEM.relative_to(ROOT)),
        "timingGrid": grid_diagnostics,
        "detectorSettings": {
            "onsetThreshold": 0.50,
            "frameThreshold": 0.30,
            "minimumNoteLengthMs": 110.0,
            "harmonicAmplitudeRatio": 0.74,
            "harmonicIntervals": [12, 19, 24],
            "maxNotesPerSlot": 5,
        },
        "currentChampionPitchF1": CURRENT_CHAMPION_F1,
        "currentChampionMatched": CURRENT_CHAMPION_MATCHED,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner["pitchF1"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsCurrentChampionPoints": round(float(winner["pitchF1"]) - CURRENT_CHAMPION_F1, 2),
        "winnerBeatsCurrentChampion": float(winner["pitchF1"]) > CURRENT_CHAMPION_F1,
        "winnerImprovesMatched": int(winner["matchedPitchTokens"]) > CURRENT_CHAMPION_MATCHED,
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
            "heldout-validate-cross-stem-rule"
            if float(winner["pitchF1"]) > CURRENT_CHAMPION_F1 and int(winner["matchedPitchTokens"]) > CURRENT_CHAMPION_MATCHED
            else "freeze-6.60-and-profile-missing-pitches-by-section-and-register"
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

    print("GOMYWAY CROSS-STEM CONSENSUS RECALL V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", CURRENT_CHAMPION_F1)
    print("Current champion matched:", CURRENT_CHAMPION_MATCHED)
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Improvement vs current champion points:", output["improvementVsCurrentChampionPoints"])
    print("Winner beats current champion:", output["winnerBeatsCurrentChampion"])
    print("Winner improves matched:", output["winnerImprovesMatched"])
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
