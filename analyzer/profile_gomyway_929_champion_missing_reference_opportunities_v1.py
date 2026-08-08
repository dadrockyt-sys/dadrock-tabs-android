from __future__ import annotations

import hashlib
import json
from collections import Counter
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
import benchmark_gomyway_926_champion_combined_staging_plus_step8_midi52_both10_only_gate_v1 as gate927
import benchmark_gomyway_927_champion_step0_midi57_recurrent_and_both10_gate_v1 as gate929

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-929-champion-missing-reference-opportunities-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-929-champion-missing-reference-opportunities-v1-manifest.json"

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

EXPECTED = (102, 765, 1227)
EXPECTED_F1 = 9.29


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


def recoverable_units(
    missing: Counter[tuple[int, int, int]],
    final_prediction: Counter[tuple[int, int, int]],
    source: Counter[tuple[int, int, int]],
) -> Counter[tuple[int, int, int]]:
    source_residual = source - final_prediction
    return missing & source_residual


def top_counter_rows(counter: Counter[str], limit: int = 20) -> list[dict[str, int | str]]:
    return [
        {"bucket": bucket, "count": int(count)}
        for bucket, count in counter.most_common(limit)
    ]


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

    print("Rebuilding validated 9.29 champion before downstream missing-note profiling...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)

    stage_temporal = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, TEMPORAL_RULE)
    stage_pruning = pruning.prune(stage_temporal, winner_scores, alt_scores, adaptive_base, PRUNING_RULE)
    stage_metrical = metrical.metrical_prune(stage_pruning, winner_scores, alt_scores, METRICAL_RULE)
    stage_step10 = step10.prune_step_signature(stage_metrical, winner_scores, alt_scores, STEP_RULE)
    stage_agreement = agreement.agreement_prune(stage_step10, winner_scores, alt_scores, AGREEMENT_RULE)
    stage_safe_cross = crossgate.cross_signature_prune(
        stage_agreement, winner_scores, alt_scores, adaptive_base, SAFE_CROSS_RULE
    )
    stage_zero_precision = crossgate.cross_signature_prune(
        stage_safe_cross, winner_scores, alt_scores, adaptive_base, ZERO_PRECISION_RULE
    )
    stage_910 = crossgate.cross_signature_prune(
        stage_zero_precision, winner_scores, alt_scores, adaptive_base, WINNER_910_RULE
    )
    stage_916 = crossgate.cross_signature_prune(
        stage_910, winner_scores, alt_scores, adaptive_base, WINNER_916_RULE
    )
    stage_919 = gate919.refined_subgate(stage_916, winner_scores, alt_scores, adaptive_base)
    stage_921 = crossgate.cross_signature_prune(
        stage_919, winner_scores, alt_scores, adaptive_base, WINNER_921_RULE
    )
    stage_923 = crossgate.cross_signature_prune(
        stage_921, winner_scores, alt_scores, adaptive_base, WINNER_923_RULE
    )
    stage_926 = gate926.deep_prune(stage_923, winner_scores, alt_scores, WINNER_926_RULE)
    stage_927 = gate927.combined_prune(stage_926, winner_scores, alt_scores, adaptive_base)
    stage_929 = gate929.residual_prune(stage_927, winner_scores, alt_scores, adaptive_base)

    final_prediction = precond.merge_with_cap(base_champion, stage_929)
    full = grade(final_prediction, reference)
    actual = (int(full["matched"]), int(full["missing"]), int(full["extra"]))
    if actual != EXPECTED or abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.29 {EXPECTED}/{EXPECTED_F1}, got {actual}/{full['pitchF1']}")

    # The professional reference is used only below this line to label misses after detection is frozen.
    missing = reference - final_prediction

    sources: list[tuple[str, Counter[tuple[int, int, int]]]] = [
        ("winnerStem", base_winner),
        ("alternateStem", base_alt),
        ("baseMerged", base_champion),
        ("top1Spectral", top1),
        ("adaptiveAdditions", adaptive_base),
        ("afterTemporal", stage_temporal),
        ("afterPrecisionPruning", stage_pruning),
        ("afterMetrical", stage_metrical),
        ("afterStep10", stage_step10),
        ("afterAgreement", stage_agreement),
        ("afterSafeCross", stage_safe_cross),
        ("afterZeroPrecision", stage_zero_precision),
        ("after910", stage_910),
        ("after916", stage_916),
        ("after919", stage_919),
        ("after921", stage_921),
        ("after923", stage_923),
        ("after926", stage_926),
        ("after927", stage_927),
    ]

    opportunities: dict[str, dict[str, object]] = {}
    union_recoverable: Counter[tuple[int, int, int]] = Counter()
    for name, source in sources:
        recoverable = recoverable_units(missing, final_prediction, source)
        union_recoverable |= recoverable
        by_step: Counter[str] = Counter()
        by_pitch: Counter[str] = Counter()
        by_step_pitch: Counter[str] = Counter()
        for (_measure, step, pitch), count in recoverable.items():
            by_step[f"step{step}"] += count
            by_pitch[f"midi{pitch}"] += count
            by_step_pitch[f"step{step}_midi{pitch}"] += count
        opportunities[name] = {
            "recoverableMissingUnits": int(sum(recoverable.values())),
            "recoverableTokenKeys": int(len(recoverable)),
            "topSteps": top_counter_rows(by_step, 12),
            "topPitches": top_counter_rows(by_pitch, 20),
            "topStepPitch": top_counter_rows(by_step_pitch, 30),
        }

    never_seen = missing - union_recoverable
    missing_by_step: Counter[str] = Counter()
    missing_by_pitch: Counter[str] = Counter()
    missing_by_step_pitch: Counter[str] = Counter()
    never_seen_by_step_pitch: Counter[str] = Counter()
    for (_measure, step, pitch), count in missing.items():
        missing_by_step[f"step{step}"] += count
        missing_by_pitch[f"midi{pitch}"] += count
        missing_by_step_pitch[f"step{step}_midi{pitch}"] += count
    for (_measure, step, pitch), count in never_seen.items():
        never_seen_by_step_pitch[f"step{step}_midi{pitch}"] += count

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 9.29 missing-note opportunity profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.29-champion-downstream-missing-reference-opportunity-profile",
        "championScore": full,
        "missingReferenceUnits": int(sum(missing.values())),
        "recoverableFromAnyProfiledUpstreamSource": int(sum(union_recoverable.values())),
        "neverSeenInProfiledUpstreamSources": int(sum(never_seen.values())),
        "opportunities": opportunities,
        "missingProfile": {
            "topSteps": top_counter_rows(missing_by_step, 12),
            "topPitches": top_counter_rows(missing_by_pitch, 20),
            "topStepPitch": top_counter_rows(missing_by_step_pitch, 30),
            "topNeverSeenStepPitch": top_counter_rows(never_seen_by_step_pitch, 30),
        },
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-miss-profiling-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "choose-recall-axis-from-detected-then-discarded-versus-never-detected-miss-split",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": full["pitchF1"],
        "championMatched": full["matched"],
        "championMissing": full["missing"],
        "championExtra": full["extra"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.29 CHAMPION MISSING REFERENCE OPPORTUNITIES V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Missing reference units:", sum(missing.values()))
    print("Recoverable from any profiled upstream source:", sum(union_recoverable.values()))
    print("Never seen in profiled upstream sources:", sum(never_seen.values()))
    print("Recall opportunity by source:")
    for name, _source in sources:
        print(f"  {name}: recoverable={opportunities[name]['recoverableMissingUnits']}")
    print("Top missing step/pitch buckets:")
    for row in output["missingProfile"]["topStepPitch"][:20]:
        print(f"  {row['bucket']}: missing={row['count']}")
    print("Top never-seen step/pitch buckets:")
    for row in output["missingProfile"]["topNeverSeenStepPitch"][:20]:
        print(f"  {row['bucket']}: missing={row['count']}")
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
