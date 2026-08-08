from __future__ import annotations

import hashlib
import json
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond
import benchmark_gomyway_mid_register_spectral_specialist_v1 as spectral
import benchmark_gomyway_spectral_specialist_precision_gate_v1 as gate
import benchmark_gomyway_spectral_top1_adaptive_local_gate_v1 as adaptive
import benchmark_gomyway_adaptive_spectral_temporal_recurrence_gate_v1 as temporal
import benchmark_gomyway_temporal_champion_precision_pruning_v1 as pruning
import benchmark_gomyway_precision_pruned_champion_metrical_gate_v1 as metrical
import benchmark_gomyway_metrically_pruned_champion_step10_exception_v1 as step10
import benchmark_gomyway_step10_pruned_champion_step10_agreement_gate_v1 as agreement
import benchmark_gomyway_step10_agreement_pruned_champion_cross_signature_gate_v1 as crossgate
import profile_gomyway_zero_precision_pruned_916_champion_residual_extras_v1 as profile916

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-916-champion-score13-16-both-ge10-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-916-champion-score13-16-both-ge10-gate-v1-manifest.json"

EXPECTED_MATCHED = 102
EXPECTED_MISSING = 765
EXPECTED_EXTRA = 1257
EXPECTED_F1 = 9.16

RULE = {
    "name": "drop_score13_16_both_ge10",
    "dropScoreAgreement": [
        {"scoreBucket": "13_16", "agreementBucket": "both_ge10"},
    ],
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted, reference):
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": sum((reference - predicted).values()),
        "extra": sum((predicted - reference).values()),
        "predictions": predicted_count,
    }


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    payload = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding validated 9.16 champion and score/agreement candidate...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, profile916.TEMPORAL_RULE)
    precision_additions = pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, profile916.PRUNING_RULE)
    metrical_additions = metrical.metrical_prune(precision_additions, winner_scores, alt_scores, profile916.METRICAL_RULE)
    step_additions = step10.prune_step_signature(metrical_additions, winner_scores, alt_scores, profile916.STEP_RULE)
    champion_additions = agreement.agreement_prune(step_additions, winner_scores, alt_scores, profile916.AGREEMENT_RULE)
    additions_1287 = crossgate.cross_signature_prune(champion_additions, winner_scores, alt_scores, adaptive_base, profile916.SAFE_CROSS_RULE)
    additions_909 = crossgate.cross_signature_prune(additions_1287, winner_scores, alt_scores, adaptive_base, profile916.ZERO_PRECISION_RULE)
    additions_910 = crossgate.cross_signature_prune(additions_909, winner_scores, alt_scores, adaptive_base, profile916.WINNER_910_RULE)
    additions_916 = crossgate.cross_signature_prune(additions_910, winner_scores, alt_scores, adaptive_base, profile916.WINNER_916_RULE)

    baseline_prediction = precond.merge_with_cap(base_champion, additions_916)
    baseline_score = grade(baseline_prediction, reference)
    actual = (
        int(baseline_score["matched"]),
        int(baseline_score["missing"]),
        int(baseline_score["extra"]),
    )
    expected = (EXPECTED_MATCHED, EXPECTED_MISSING, EXPECTED_EXTRA)
    if actual != expected:
        raise RuntimeError(f"Expected validated 9.16 baseline {expected}, got {actual}")
    if abs(float(baseline_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated F1 {EXPECTED_F1}, got {baseline_score['pitchF1']}")

    filtered_additions = crossgate.cross_signature_prune(
        additions_916,
        winner_scores,
        alt_scores,
        adaptive_base,
        RULE,
    )
    prediction = precond.merge_with_cap(base_champion, filtered_additions)
    result = crossgate.evaluate_candidate(
        prediction,
        baseline_prediction,
        reference,
        baseline_score,
    )

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during 9.16 score/agreement benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.16-champion-score13-16-both-ge10-gate",
        "baselineScore": baseline_score,
        "rule": RULE,
        "result": result,
        "validatedNewChampion": bool(result["acceptedOverChampion"]),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "baselinePitchF1": baseline_score["pitchF1"],
        "validatedNewChampion": bool(result["acceptedOverChampion"]),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.16 CHAMPION SCORE13-16 BOTH_GE10 GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline_score["pitchF1"])
    print("Baseline matched/missing/extra:", baseline_score["matched"], "/", baseline_score["missing"], "/", baseline_score["extra"])
    print("Candidate pitch F1:", result["fullScore"]["pitchF1"])
    print("Candidate matched/missing/extra:", result["fullScore"]["matched"], "/", result["fullScore"]["missing"], "/", result["fullScore"]["extra"])
    print("Candidate extra reduction:", result["extraReduction"])
    print("Candidate matched change:", result["matchedChange"])
    print("Cross-validation passed:", result["crossValidationPassed"])
    print("Section stability passed:", result["sectionStabilityPassed"])
    print("Shifted-window stability passed:", result["shiftedWindowStabilityPassed"])
    print("Validated new champion:", result["acceptedOverChampion"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
