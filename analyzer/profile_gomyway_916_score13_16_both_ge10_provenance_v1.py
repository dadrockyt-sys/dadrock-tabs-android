from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-916-score13-16-both-ge10-provenance-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-916-score13-16-both-ge10-provenance-v1-manifest.json"

TEMPORAL_RULE = gate909.TEMPORAL_RULE
PRUNING_RULE = gate909.PRUNING_RULE
METRICAL_RULE = gate909.METRICAL_RULE
STEP_RULE = gate909.STEP_RULE
AGREEMENT_RULE = gate909.AGREEMENT_RULE
SAFE_CROSS_RULE = gate909.SAFE_CROSS_RULE
ZERO_PRECISION_RULE = gate909.ZERO_PRECISION_RULE
WINNER_910_RULE = gate910.WINNER_910_RULE
WINNER_916_RULE = next(rule for rule in gate910.RULES if rule["name"] == "drop_all_profiled_zero_precision_step_pitch")
DANGEROUS_RULE = {
    "name": "drop_score13_16_both_ge10",
    "dropScoreAgreement": [{"scoreBucket": "13_16", "agreementBucket": "both_ge10"}],
}

EXPECTED_BASELINE = (102, 765, 1257)
EXPECTED_BASELINE_F1 = 9.16
EXPECTED_CANDIDATE = (97, 770, 1252)
EXPECTED_CANDIDATE_F1 = 8.75


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, float | int]:
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

    print("Rebuilding validated 9.16 champion and failed score13_16/both_ge10 candidate...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, TEMPORAL_RULE)
    precision_additions = pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, PRUNING_RULE)
    metrical_additions = metrical.metrical_prune(precision_additions, winner_scores, alt_scores, METRICAL_RULE)
    step_additions = step10.prune_step_signature(metrical_additions, winner_scores, alt_scores, STEP_RULE)
    champion_additions = agreement.agreement_prune(step_additions, winner_scores, alt_scores, AGREEMENT_RULE)
    additions_1287 = crossgate.cross_signature_prune(champion_additions, winner_scores, alt_scores, adaptive_base, SAFE_CROSS_RULE)
    additions_909 = crossgate.cross_signature_prune(additions_1287, winner_scores, alt_scores, adaptive_base, ZERO_PRECISION_RULE)
    additions_910 = crossgate.cross_signature_prune(additions_909, winner_scores, alt_scores, adaptive_base, WINNER_910_RULE)
    additions_916 = crossgate.cross_signature_prune(additions_910, winner_scores, alt_scores, adaptive_base, WINNER_916_RULE)

    baseline_prediction = precond.merge_with_cap(base_champion, additions_916)
    baseline_score = grade(baseline_prediction, reference)
    baseline_tuple = (int(baseline_score["matched"]), int(baseline_score["missing"]), int(baseline_score["extra"]))
    if baseline_tuple != EXPECTED_BASELINE or abs(float(baseline_score["pitchF1"]) - EXPECTED_BASELINE_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.16 baseline {EXPECTED_BASELINE} / {EXPECTED_BASELINE_F1}, got {baseline_tuple} / {baseline_score['pitchF1']}")

    candidate_additions = crossgate.cross_signature_prune(additions_916, winner_scores, alt_scores, adaptive_base, DANGEROUS_RULE)
    candidate_prediction = precond.merge_with_cap(base_champion, candidate_additions)
    candidate_score = grade(candidate_prediction, reference)
    candidate_tuple = (int(candidate_score["matched"]), int(candidate_score["missing"]), int(candidate_score["extra"]))
    if candidate_tuple != EXPECTED_CANDIDATE or abs(float(candidate_score["pitchF1"]) - EXPECTED_CANDIDATE_F1) > 0.01:
        raise RuntimeError(f"Expected failed candidate {EXPECTED_CANDIDATE} / {EXPECTED_CANDIDATE_F1}, got {candidate_tuple} / {candidate_score['pitchF1']}")

    dropped_additions = additions_916 - candidate_additions
    dropped_prediction = baseline_prediction - candidate_prediction

    rows: list[dict[str, Any]] = []
    total_matched_loss = 0
    total_extra_reduction = 0
    for token in sorted(dropped_prediction):
        measure, step, pitch = token
        base_count = int(base_champion[token])
        addition_before = int(additions_916[token])
        addition_after = int(candidate_additions[token])
        baseline_count = int(baseline_prediction[token])
        candidate_count = int(candidate_prediction[token])
        reference_count = int(reference[token])
        baseline_matched = min(baseline_count, reference_count)
        candidate_matched = min(candidate_count, reference_count)
        baseline_extra = max(0, baseline_count - reference_count)
        candidate_extra = max(0, candidate_count - reference_count)
        matched_loss = baseline_matched - candidate_matched
        extra_reduction = baseline_extra - candidate_extra
        total_matched_loss += matched_loss
        total_extra_reduction += extra_reduction
        rows.append({
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "token": [measure, step, pitch],
            "baseChampionCount": base_count,
            "additionBefore": addition_before,
            "additionAfter": addition_after,
            "additionDropped": int(dropped_additions[token]),
            "baselinePredictionCount": baseline_count,
            "candidatePredictionCount": candidate_count,
            "referenceCount": reference_count,
            "matchedLoss": matched_loss,
            "extraReduction": extra_reduction,
            "scoreBucket": pruning.score_bucket(token, winner_scores, alt_scores),
            "agreementBucket": pruning.agreement_bucket(token, winner_scores, alt_scores),
            "winnerScore": float(winner_scores.get(token, 0.0)),
            "altScore": float(alt_scores.get(token, 0.0)),
            "safeToDropAtMergedMultiplicity": matched_loss == 0 and extra_reduction > 0,
        })

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during provenance profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.16-failed-score13-16-both-ge10-provenance-profile",
        "baselineScore": baseline_score,
        "failedCandidateScore": candidate_score,
        "rule": DANGEROUS_RULE,
        "droppedPredictionCount": sum(dropped_prediction.values()),
        "droppedAdditionCount": sum(dropped_additions.values()),
        "totalMatchedLoss": total_matched_loss,
        "totalExtraReduction": total_extra_reduction,
        "rows": rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "use-merged-multiplicity-provenance-to-split-safe-extra-removals-from-match-bearing-removals",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "baselinePitchF1": baseline_score["pitchF1"],
        "failedCandidatePitchF1": candidate_score["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.16 SCORE13_16 BOTH_GE10 PROVENANCE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Baseline matched/missing/extra:", baseline_score["matched"], "/", baseline_score["missing"], "/", baseline_score["extra"])
    print("Failed candidate matched/missing/extra:", candidate_score["matched"], "/", candidate_score["missing"], "/", candidate_score["extra"])
    print("Dropped prediction/addition counts:", sum(dropped_prediction.values()), "/", sum(dropped_additions.values()))
    print("Total matched loss / extra reduction:", total_matched_loss, "/", total_extra_reduction)
    print("Per-token provenance:")
    for row in rows:
        print(
            f"  m{row['measure']} step{row['step']} midi{row['pitch']}: "
            f"base={row['baseChampionCount']} add={row['additionBefore']}->{row['additionAfter']} "
            f"pred={row['baselinePredictionCount']}->{row['candidatePredictionCount']} ref={row['referenceCount']} "
            f"matchedLoss={row['matchedLoss']} extraReduction={row['extraReduction']} "
            f"safe={row['safeToDropAtMergedMultiplicity']}"
        )
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
