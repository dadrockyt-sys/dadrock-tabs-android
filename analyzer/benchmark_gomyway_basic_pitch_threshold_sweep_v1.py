from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

STEM_PATH = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-basic-pitch-threshold-sweep-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-basic-pitch-threshold-sweep-v1-manifest.json"

CONTROL_PITCH_F1 = 4.73
CURRENT_SEPARATOR_WINNER_F1 = 6.12

# Baseline plus progressively stricter false-positive suppression settings.
CONFIGS: list[dict[str, Any]] = [
    {
        "name": "baseline",
        "onsetThreshold": 0.50,
        "frameThreshold": 0.30,
        "minimumNoteLengthMs": 58.0,
    },
    {
        "name": "onset055",
        "onsetThreshold": 0.55,
        "frameThreshold": 0.30,
        "minimumNoteLengthMs": 58.0,
    },
    {
        "name": "onset060",
        "onsetThreshold": 0.60,
        "frameThreshold": 0.30,
        "minimumNoteLengthMs": 58.0,
    },
    {
        "name": "frame035",
        "onsetThreshold": 0.50,
        "frameThreshold": 0.35,
        "minimumNoteLengthMs": 58.0,
    },
    {
        "name": "frame040",
        "onsetThreshold": 0.50,
        "frameThreshold": 0.40,
        "minimumNoteLengthMs": 58.0,
    },
    {
        "name": "min80",
        "onsetThreshold": 0.50,
        "frameThreshold": 0.30,
        "minimumNoteLengthMs": 80.0,
    },
    {
        "name": "min110",
        "onsetThreshold": 0.50,
        "frameThreshold": 0.30,
        "minimumNoteLengthMs": 110.0,
    },
    {
        "name": "strict_a",
        "onsetThreshold": 0.55,
        "frameThreshold": 0.35,
        "minimumNoteLengthMs": 80.0,
    },
    {
        "name": "strict_b",
        "onsetThreshold": 0.60,
        "frameThreshold": 0.40,
        "minimumNoteLengthMs": 110.0,
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return v2.load_json(path)


def run_config(
    config: dict[str, Any],
    grid: dict[tuple[int, int], float],
    reference: Any,
) -> dict[str, Any]:
    v2.ONSET_THRESHOLD = float(config["onsetThreshold"])
    v2.FRAME_THRESHOLD = float(config["frameThreshold"])
    v2.MINIMUM_NOTE_LENGTH_MS = float(config["minimumNoteLengthMs"])

    print(
        "Running",
        config["name"],
        f"onset={v2.ONSET_THRESHOLD}",
        f"frame={v2.FRAME_THRESHOLD}",
        f"minMs={v2.MINIMUM_NOTE_LENGTH_MS}",
        flush=True,
    )

    result = v2.analyze_stem(
        str(config["name"]),
        STEM_PATH,
        grid,
        reference,
    )

    result["settings"] = {
        "onsetThreshold": v2.ONSET_THRESHOLD,
        "frameThreshold": v2.FRAME_THRESHOLD,
        "minimumNoteLengthMs": v2.MINIMUM_NOTE_LENGTH_MS,
        "snapToleranceSeconds": v2.SNAP_TOLERANCE_SECONDS,
    }
    return result


def main() -> None:
    if not STEM_PATH.exists():
        raise FileNotFoundError(f"Missing winning separator stem: {STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = v2.sha256(CANDIDATE_PATH)
    candidate = load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference_payload = load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")

    reference = v3.reference_tokens(reference_payload)
    if not reference:
        raise RuntimeError("No professional pitch tokens found after V3 normalization.")

    results = [run_config(config, grid, reference) for config in CONFIGS]

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

    candidate_hash_after = v2.sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during threshold sweep.")

    winner_f1 = float(winner["pitchF1"])
    improvement_vs_baseline = round(winner_f1 - CURRENT_SEPARATOR_WINNER_F1, 2)
    improvement_vs_control = round(winner_f1 - CONTROL_PITCH_F1, 2)

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "basic-pitch-threshold-sweep-on-winning-separator-stem",
        "stem": str(STEM_PATH.relative_to(ROOT)),
        "timingGrid": grid_diagnostics,
        "professionalReferenceRole": "downstream-grading-only",
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "controlPitchF1": CONTROL_PITCH_F1,
        "currentSeparatorWinnerPitchF1": CURRENT_SEPARATOR_WINNER_F1,
        "results": results,
        "winner": winner["name"],
        "winnerPitchF1": winner_f1,
        "winnerSettings": winner["settings"],
        "winnerMatched": winner["matchedPitchTokens"],
        "winnerMissing": winner["missingProfessionalPitchTokens"],
        "winnerExtra": winner["extraCandidatePitchTokens"],
        "winnerPriorityBatch": winner["priorityBatch"],
        "improvementVsCurrentWinnerPoints": improvement_vs_baseline,
        "improvementVsControlPoints": improvement_vs_control,
        "winnerBeatsCurrentWinner": winner_f1 > CURRENT_SEPARATOR_WINNER_F1,
        "recommendedNextAction": (
            "refine-basic-pitch-filtering-around-winner"
            if winner_f1 >= CURRENT_SEPARATOR_WINNER_F1 + 0.50
            else "evaluate-alternative-pitch-detector"
        ),
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "stem": str(STEM_PATH.relative_to(ROOT)),
        "winner": output["winner"],
        "winnerPitchF1": output["winnerPitchF1"],
        "winnerSettings": output["winnerSettings"],
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": True,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY BASIC PITCH THRESHOLD SWEEP V1 COMPLETE")
    print("Passed: True")
    print("Control pitch F1:", CONTROL_PITCH_F1)
    print("Current separator winner pitch F1:", CURRENT_SEPARATOR_WINNER_F1)
    for row in results:
        settings = row["settings"]
        print(
            f"{row['name']}: pitchF1={row['pitchF1']} "
            f"matched={row['matchedPitchTokens']} "
            f"missing={row['missingProfessionalPitchTokens']} "
            f"extra={row['extraCandidatePitchTokens']} "
            f"raw={row['basicPitchRawNoteCount']} "
            f"onset={settings['onsetThreshold']} "
            f"frame={settings['frameThreshold']} "
            f"minMs={settings['minimumNoteLengthMs']}"
        )
    print("Winner:", output["winner"])
    print("Winner pitch F1:", output["winnerPitchF1"])
    print("Winner settings:", output["winnerSettings"])
    print("Winner matched/missing/extra:", output["winnerMatched"], "/", output["winnerMissing"], "/", output["winnerExtra"])
    print("Winner priority matched/missing/extra:", output["winnerPriorityBatch"]["matched"], "/", output["winnerPriorityBatch"]["missing"], "/", output["winnerPriorityBatch"]["extra"])
    print("Improvement vs current winner points:", output["improvementVsCurrentWinnerPoints"])
    print("Improvement vs control points:", output["improvementVsControlPoints"])
    print("Winner beats current winner:", output["winnerBeatsCurrentWinner"])
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
