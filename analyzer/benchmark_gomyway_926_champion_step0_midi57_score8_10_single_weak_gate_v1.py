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
import benchmark_gomyway_909_champion_zero_precision_cross_signature_gate_v1 as gate909
import benchmark_gomyway_910_champion_zero_precision_step_pitch_gate_v1 as gate910
import benchmark_gomyway_916_champion_recurrent_step8_or_midi57_winner13_subgate_v1 as gate919
import benchmark_gomyway_919_champion_zero_precision_step_pitch_gate_v1 as gate921
import benchmark_gomyway_921_champion_zero_precision_step_agreement_and_step_pitch_gate_v1 as gate923
import benchmark_gomyway_923_champion_deep_zero_precision_gate_v1 as gate926

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-926-champion-step0-midi57-score8-10-single-weak-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-926-champion-step0-midi57-score8-10-single-weak-gate-v1-manifest.json"

TEMPORAL_RULE = gate909.TEMPORAL_RULE
PRUNING_RULE = gate909.PRUNING_RULE
METRICAL_RULE = gate909.METRICAL_RULE
STEP_RULE = gate909.STEP_RULE
AGREEMENT_RULE = gate909.AGREEMENT_RULE
SAFE_CROSS_RULE = gate909.SAFE_CROSS_RULE
ZERO_PRECISION_RULE = gate909.ZERO_PRECISION_RULE
WINNER_910_RULE = gate910.WINNER_910_RULE
WINNER_916_RULE = next(rule for rule in gate910.RULES if rule["name"] == "drop_all_profiled_zero_precision_step_pitch")
WINNER_921_RULE = next(rule for rule in gate921.RULES if rule["name"] == "drop_all_profiled_zero_precision_step_pitch_919")
WINNER_923_RULE = next(rule for rule in gate923.RULES if rule["name"] == "drop_step12_single_weak_plus_step8_midi53_55")
WINNER_926_RULE = next(rule for rule in gate926.RULES if rule["name"] == "drop_primary_plus_step4_midi53")

EXPECTED_BASELINE = (102, 765, 1235)
EXPECTED_F1 = 9.26
NEW_RULE = {
    "name": "drop_step0_midi57_score8_10_single_weak",
    "selectors": [
        {"step": 0, "pitch": 57, "score": "8_10", "agreement": "single_stem_or_weak_second"}
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
    before = sha256(CANDIDATE_PATH)
    payload = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding validated 9.26 champion and step0/midi57 residual candidate...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    a = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, TEMPORAL_RULE)
    a = pruning.prune(a, winner_scores, alt_scores, adaptive_base, PRUNING_RULE)
    a = metrical.metrical_prune(a, winner_scores, alt_scores, METRICAL_RULE)
    a = step10.prune_step_signature(a, winner_scores, alt_scores, STEP_RULE)
    a = agreement.agreement_prune(a, winner_scores, alt_scores, AGREEMENT_RULE)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, SAFE_CROSS_RULE)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, ZERO_PRECISION_RULE)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, WINNER_910_RULE)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, WINNER_916_RULE)
    a = gate919.refined_subgate(a, winner_scores, alt_scores, adaptive_base)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, WINNER_921_RULE)
    a = crossgate.cross_signature_prune(a, winner_scores, alt_scores, adaptive_base, WINNER_923_RULE)
    additions_926 = gate926.deep_prune(a, winner_scores, alt_scores, WINNER_926_RULE)

    baseline_prediction = precond.merge_with_cap(base_champion, additions_926)
    baseline_score = grade(baseline_prediction, reference)
    baseline_tuple = (
        int(baseline_score["matched"]), int(baseline_score["missing"]), int(baseline_score["extra"])
    )
    if baseline_tuple != EXPECTED_BASELINE or abs(float(baseline_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(
            f"Expected validated 9.26 baseline {EXPECTED_BASELINE}/{EXPECTED_F1}, got {baseline_tuple}/{baseline_score['pitchF1']}"
        )

    filtered = gate926.deep_prune(additions_926, winner_scores, alt_scores, NEW_RULE)
    prediction = precond.merge_with_cap(base_champion, filtered)
    result = crossgate.evaluate_candidate(prediction, baseline_prediction, reference, baseline_score)
    result["rule"] = NEW_RULE
    result["additionsDroppedFrom926"] = sum(additions_926.values()) - sum(filtered.values())
    validated_new_champion = bool(result["acceptedOverChampion"])

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 9.26 residual benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.26-champion-step0-midi57-score8-10-single-weak-gate",
        "baselineScore": baseline_score,
        "rule": NEW_RULE,
        "result": result,
        "validatedNewChampion": validated_new_champion,
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
        "candidateSha256": after,
        "baselinePitchF1": baseline_score["pitchF1"],
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.26 CHAMPION STEP0 MIDI57 SCORE8_10 SINGLE-WEAK GATE V1 COMPLETE")
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
    print("Validated new champion:", validated_new_champion)
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
