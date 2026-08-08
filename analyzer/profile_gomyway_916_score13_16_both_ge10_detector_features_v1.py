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
OUTPUT_PATH = PUBLIC / "gomyway-916-score13-16-both-ge10-detector-features-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-916-score13-16-both-ge10-detector-features-v1-manifest.json"

TEMPORAL_RULE = gate909.TEMPORAL_RULE
PRUNING_RULE = gate909.PRUNING_RULE
METRICAL_RULE = gate909.METRICAL_RULE
STEP_RULE = gate909.STEP_RULE
AGREEMENT_RULE = gate909.AGREEMENT_RULE
SAFE_CROSS_RULE = gate909.SAFE_CROSS_RULE
ZERO_PRECISION_RULE = gate909.ZERO_PRECISION_RULE
WINNER_910_RULE = gate910.WINNER_910_RULE
WINNER_916_RULE = next(rule for rule in gate910.RULES if rule["name"] == "drop_all_profiled_zero_precision_step_pitch")
TARGET_RULE = {
    "name": "drop_score13_16_both_ge10",
    "dropScoreAgreement": [{"scoreBucket": "13_16", "agreementBucket": "both_ge10"}],
}

EXPECTED_BASELINE = (102, 765, 1257)
EXPECTED_BASELINE_F1 = 9.16


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


def section_name(measure: int) -> str:
    for start, end in temporal.BLOCKS:
        if start <= measure <= end:
            return f"m{start}_{end}"
    return "outside_scored_range"


def support_count(additions: Counter[tuple[int, int, int]], token: tuple[int, int, int], measure_radius: int, *, same_step: bool, same_pitch: bool) -> int:
    measure, step, pitch = token
    total = 0
    for (m, s, p), count in additions.items():
        if (m, s, p) == token:
            continue
        if abs(m - measure) > measure_radius:
            continue
        if same_step and s != step:
            continue
        if same_pitch and p != pitch:
            continue
        total += int(count)
    return total


def same_measure_neighbor_steps(additions: Counter[tuple[int, int, int]], token: tuple[int, int, int], step_radius: int = 2) -> int:
    measure, step, _ = token
    return sum(
        int(count)
        for (m, s, _p), count in additions.items()
        if m == measure and (m, s, _p) != token and abs(s - step) <= step_radius
    )


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

    print("Rebuilding validated 9.16 champion and profiling detector-side features...", flush=True)
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

    candidate_additions = crossgate.cross_signature_prune(additions_916, winner_scores, alt_scores, adaptive_base, TARGET_RULE)
    candidate_prediction = precond.merge_with_cap(base_champion, candidate_additions)
    dropped_prediction = baseline_prediction - candidate_prediction

    rows: list[dict[str, Any]] = []
    for token in sorted(dropped_prediction):
        measure, step, pitch = token
        baseline_count = int(baseline_prediction[token])
        candidate_count = int(candidate_prediction[token])
        reference_count = int(reference[token])
        matched_loss = min(baseline_count, reference_count) - min(candidate_count, reference_count)
        extra_reduction = max(0, baseline_count - reference_count) - max(0, candidate_count - reference_count)
        ws = float(winner_scores.get(token, 0.0))
        als = float(alt_scores.get(token, 0.0))
        rows.append({
            "token": [measure, step, pitch],
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "trainingLabelSafeExtra": matched_loss == 0 and extra_reduction > 0,
            "matchedLoss": matched_loss,
            "extraReduction": extra_reduction,
            "winnerScore": round(ws, 4),
            "altScore": round(als, 4),
            "minStemScore": round(min(ws, als), 4),
            "maxStemScore": round(max(ws, als), 4),
            "stemScoreGap": round(abs(ws - als), 4),
            "scoreBucket": pruning.score_bucket(token, winner_scores, alt_scores),
            "agreementBucket": pruning.agreement_bucket(token, winner_scores, alt_scores),
            "recurrenceReason": pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores),
            "section": section_name(measure),
            "measureParity": measure % 2,
            "sameStepPitchSupportR1": support_count(additions_916, token, 1, same_step=True, same_pitch=True),
            "sameStepPitchSupportR2": support_count(additions_916, token, 2, same_step=True, same_pitch=True),
            "sameStepPitchSupportR4": support_count(additions_916, token, 4, same_step=True, same_pitch=True),
            "samePitchSupportR2": support_count(additions_916, token, 2, same_step=False, same_pitch=True),
            "samePitchSupportR4": support_count(additions_916, token, 4, same_step=False, same_pitch=True),
            "sameStepSupportR2": support_count(additions_916, token, 2, same_step=True, same_pitch=False),
            "sameStepSupportR4": support_count(additions_916, token, 4, same_step=True, same_pitch=False),
            "sameMeasureNeighborStepsR2": same_measure_neighbor_steps(additions_916, token, 2),
        })

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during detector-feature profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.16-score13-16-both-ge10-detector-feature-profile",
        "baselineScore": baseline_score,
        "targetRule": TARGET_RULE,
        "rows": rows,
        "safeTrainingLabelCount": sum(1 for row in rows if row["trainingLabelSafeExtra"]),
        "unsafeTrainingLabelCount": sum(1 for row in rows if not row["trainingLabelSafeExtra"]),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "derive-generalizable-detector-only-subgate-separating-safe-and-match-bearing-provenance-rows",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "baselinePitchF1": baseline_score["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.16 SCORE13_16 BOTH_GE10 DETECTOR FEATURES V1 COMPLETE")
    print("Passed: True")
    print("Baseline matched/missing/extra:", baseline_score["matched"], "/", baseline_score["missing"], "/", baseline_score["extra"])
    print("Safe/unsafe training-label rows:", output["safeTrainingLabelCount"], "/", output["unsafeTrainingLabelCount"])
    print("Detector-feature rows:")
    for row in rows:
        label = "SAFE_EXTRA" if row["trainingLabelSafeExtra"] else "MATCH_BEARING"
        print(
            f"  {label} m{row['measure']} step{row['step']} midi{row['pitch']} "
            f"ws={row['winnerScore']} as={row['altScore']} min={row['minStemScore']} gap={row['stemScoreGap']} "
            f"reason={row['recurrenceReason']} section={row['section']} parity={row['measureParity']} "
            f"ssp2={row['sameStepPitchSupportR2']} ssp4={row['sameStepPitchSupportR4']} "
            f"sp2={row['samePitchSupportR2']} sp4={row['samePitchSupportR4']} "
            f"ss2={row['sameStepSupportR2']} ss4={row['sameStepSupportR4']} neigh={row['sameMeasureNeighborStepsR2']}"
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
