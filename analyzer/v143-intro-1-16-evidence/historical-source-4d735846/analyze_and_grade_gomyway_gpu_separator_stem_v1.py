from __future__ import annotations

import json
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"

GPU_REPORT_PATH = PUBLIC / "gomyway-separator-gpu-benchmark-v1.json"
GPU_STEM_PATH = (
    PUBLIC
    / "separator-benchmark-gpu-v1"
    / "gomyway-bsroformer-demucs6s-gpu-hq-guitar.wav"
)
OUTPUT_PATH = PUBLIC / "gomyway-gpu-separator-stem-grade-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-gpu-separator-stem-grade-v1-manifest.json"

CURRENT_CPU_WINNER_PITCH_F1 = 6.12


def main() -> None:
    gpu_report = v2.load_json(GPU_REPORT_PATH)
    if gpu_report.get("passed") is not True:
        raise RuntimeError("GPU separator benchmark is not green.")
    if gpu_report.get("professionalReferenceUsedForSeparation") is not False:
        raise RuntimeError("Professional reference was unexpectedly used during GPU separation.")
    if gpu_report.get("productionSeparatorChanged") is not False:
        raise RuntimeError("Production separator changed during GPU benchmark.")
    if gpu_report.get("productionPromotionAllowed") is not False:
        raise RuntimeError("Production promotion unexpectedly enabled.")

    if not GPU_STEM_PATH.exists():
        raise FileNotFoundError(f"GPU benchmark stem missing: {GPU_STEM_PATH.relative_to(ROOT)}")

    candidate_hash_before = v2.sha256(v2.CANDIDATE_PATH)
    candidate = v2.load_json(v2.CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")

    grid, grid_diagnostics = v2.build_timing_grid(events)

    reference = v2.load_json(v2.REFERENCE_PATH)
    if reference.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")

    reference_counter = v3.reference_tokens(reference)
    if not reference_counter:
        raise RuntimeError("No professional pitch tokens found after V3 normalization.")

    print("Analyzing gpu-hq-bsroformer-then-demucs6s:", GPU_STEM_PATH.relative_to(ROOT))
    result = v2.analyze_stem(
        "gpu-hq-bsroformer-then-demucs6s",
        GPU_STEM_PATH,
        grid,
        reference_counter,
    )

    gpu_pitch_f1 = float(result["pitchF1"])
    improvement_vs_control = round(gpu_pitch_f1 - v2.CONTROL_PITCH_F1, 2)
    improvement_vs_cpu_winner = round(gpu_pitch_f1 - CURRENT_CPU_WINNER_PITCH_F1, 2)

    candidate_hash_after = v2.sha256(v2.CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during GPU stem grading.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "comparisonType": "identical-basic-pitch-grading-on-gpu-hq-separator-winner",
        "gpuSeparatorArchitecture": "bsroformer-then-demucs6s",
        "gpuSeparatorReport": str(GPU_REPORT_PATH.relative_to(ROOT)),
        "gpuStem": str(GPU_STEM_PATH.relative_to(ROOT)),
        "detectorSettings": {
            "onsetThreshold": v2.ONSET_THRESHOLD,
            "frameThreshold": v2.FRAME_THRESHOLD,
            "minimumNoteLengthMs": v2.MINIMUM_NOTE_LENGTH_MS,
            "snapToleranceSeconds": v2.SNAP_TOLERANCE_SECONDS,
        },
        "timingGrid": grid_diagnostics,
        "professionalReferenceRole": "downstream-grading-only",
        "professionalReferenceUsedDuringDetection": False,
        "controlPitchF1": v2.CONTROL_PITCH_F1,
        "currentCpuWinnerPitchF1": CURRENT_CPU_WINNER_PITCH_F1,
        "result": result,
        "gpuPitchF1": gpu_pitch_f1,
        "improvementVsControlPoints": improvement_vs_control,
        "improvementVsCpuWinnerPoints": improvement_vs_cpu_winner,
        "gpuBeatsControl": gpu_pitch_f1 > v2.CONTROL_PITCH_F1,
        "gpuBeatsCpuWinner": gpu_pitch_f1 > CURRENT_CPU_WINNER_PITCH_F1,
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": (
            "review-gpu-separator-gain-before-production-wiring"
            if gpu_pitch_f1 > CURRENT_CPU_WINNER_PITCH_F1
            else "pivot-to-pitch-detector-improvement"
        ),
    }

    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "gpuStem": output["gpuStem"],
        "gpuPitchF1": gpu_pitch_f1,
        "currentCpuWinnerPitchF1": CURRENT_CPU_WINNER_PITCH_F1,
        "gpuBeatsCpuWinner": output["gpuBeatsCpuWinner"],
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY GPU SEPARATOR STEM GRADING V1 COMPLETE")
    print("Passed: True")
    print("Control pitch F1:", v2.CONTROL_PITCH_F1)
    print("Current CPU winner pitch F1:", CURRENT_CPU_WINNER_PITCH_F1)
    print("GPU HQ pitch F1:", gpu_pitch_f1)
    print("Matched:", result["matchedPitchTokens"])
    print("Missing:", result["missingProfessionalPitchTokens"])
    print("Extra:", result["extraCandidatePitchTokens"])
    print("Priority matched/missing/extra:", result["priorityBatch"]["matched"], "/", result["priorityBatch"]["missing"], "/", result["priorityBatch"]["extra"])
    print("Improvement vs control points:", improvement_vs_control)
    print("Improvement vs CPU winner points:", improvement_vs_cpu_winner)
    print("GPU beats control:", output["gpuBeatsControl"])
    print("GPU beats CPU winner:", output["gpuBeatsCpuWinner"])
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
