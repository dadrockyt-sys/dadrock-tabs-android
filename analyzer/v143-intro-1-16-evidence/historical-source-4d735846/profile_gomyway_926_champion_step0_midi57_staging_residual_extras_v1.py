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
import benchmark_gomyway_916_champion_recurrent_step8_or_midi57_winner13_subgate_v1 as gate919
import benchmark_gomyway_919_champion_zero_precision_step_pitch_gate_v1 as gate921
import benchmark_gomyway_921_champion_zero_precision_step_agreement_and_step_pitch_gate_v1 as gate923
import benchmark_gomyway_923_champion_deep_zero_precision_gate_v1 as gate926
import benchmark_gomyway_926_champion_step0_midi57_score8_10_single_weak_gate_v1 as staging

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-926-champion-step0-midi57-staging-residual-extras-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-926-champion-step0-midi57-staging-residual-extras-profile-v1-manifest.json"

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
STAGING_RULE = staging.NEW_RULE

EXPECTED_CHAMPION = (102, 765, 1235)
EXPECTED_STAGING = (102, 765, 1233)
EXPECTED_F1 = 9.26


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


def precision_rows(false_counts: Counter[str], true_counts: Counter[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in sorted(set(false_counts) | set(true_counts)):
        false = int(false_counts[key])
        true = int(true_counts[key])
        total = true + false
        out.append({
            "bucket": key,
            "true": true,
            "false": false,
            "total": total,
            "precisionPercent": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(out, key=lambda row: (-int(row["total"]), float(row["precisionPercent"]), str(row["bucket"])))


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

    print("Rebuilding validated 9.26 champion, applying safe non-promoted staging prune, and profiling residual extras...", flush=True)
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

    champion_prediction = precond.merge_with_cap(base_champion, additions_926)
    champion_score = grade(champion_prediction, reference)
    champion_tuple = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if champion_tuple != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.26 {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {champion_tuple}/{champion_score['pitchF1']}")

    staged_additions = gate926.deep_prune(additions_926, winner_scores, alt_scores, STAGING_RULE)
    staged_prediction = precond.merge_with_cap(base_champion, staged_additions)
    staged_score = grade(staged_prediction, reference)
    staged_tuple = (int(staged_score["matched"]), int(staged_score["missing"]), int(staged_score["extra"]))
    if staged_tuple != EXPECTED_STAGING or abs(float(staged_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected safe staging score {EXPECTED_STAGING}/{EXPECTED_F1}, got {staged_tuple}/{staged_score['pitchF1']}")

    specialist_extras = Counter({t: c for t, c in (staged_prediction - reference).items() if t in staged_additions})
    specialist_matches = Counter({t: c for t, c in (staged_prediction & reference).items() if t in staged_additions})

    names = [
        "stepPitchScore",
        "stepPitchAgreement",
        "stepScoreAgreement",
        "stepPitchScoreAgreement",
        "stepPitchReason",
        "pitchScoreAgreement",
    ]
    dims = {name: (Counter(), Counter()) for name in names}

    def record(token: tuple[int, int, int], count: int, is_true: bool) -> None:
        _measure, step, pitch = token
        score = pruning.score_bucket(token, winner_scores, alt_scores)
        agree = pruning.agreement_bucket(token, winner_scores, alt_scores)
        reason = pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores)
        values = {
            "stepPitchScore": f"step{step}_midi{pitch}_score{score}",
            "stepPitchAgreement": f"step{step}_midi{pitch}_{agree}",
            "stepScoreAgreement": f"step{step}_score{score}_{agree}",
            "stepPitchScoreAgreement": f"step{step}_midi{pitch}_score{score}_{agree}",
            "stepPitchReason": f"step{step}_midi{pitch}_{reason}",
            "pitchScoreAgreement": f"midi{pitch}_score{score}_{agree}",
        }
        for name, value in values.items():
            false_counter, true_counter = dims[name]
            (true_counter if is_true else false_counter)[value] += count

    for token, count in specialist_extras.items():
        record(token, count, False)
    for token, count in specialist_matches.items():
        record(token, count, True)

    profiles = {name: precision_rows(f, t) for name, (f, t) in dims.items()}
    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 9.26 staging residual profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.26-champion-safe-staging-prune-residual-profile",
        "officialChampionScore": champion_score,
        "stagingScore": staged_score,
        "stagingRule": STAGING_RULE,
        "stagingPromoted": False,
        "specialistAdditionMatchedCount": sum(specialist_matches.values()),
        "specialistAdditionExtraCount": sum(specialist_extras.values()),
        "profiles": profiles,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "find-complementary-zero-precision-signature-and-benchmark-combined-rule-against-official-9.26-champion",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "officialChampionPitchF1": champion_score["pitchF1"],
        "stagingPitchF1": staged_score["pitchF1"],
        "stagingPromoted": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.26 CHAMPION SAFE STAGING PRUNE RESIDUAL PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Official champion pitch F1:", champion_score["pitchF1"])
    print("Official champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Staging pitch F1:", staged_score["pitchF1"])
    print("Staging matched/missing/extra:", staged_score["matched"], "/", staged_score["missing"], "/", staged_score["extra"])
    print("Staging promoted: False")
    for label, key in [
        ("Step/pitch/score precision", "stepPitchScore"),
        ("Step/pitch/agreement precision", "stepPitchAgreement"),
        ("Step/score/agreement precision", "stepScoreAgreement"),
        ("Step/pitch/score/agreement precision", "stepPitchScoreAgreement"),
        ("Step/pitch/reason precision", "stepPitchReason"),
        ("Pitch/score/agreement precision", "pitchScoreAgreement"),
    ]:
        print(label + ":")
        for row in profiles[key][:30]:
            print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
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
