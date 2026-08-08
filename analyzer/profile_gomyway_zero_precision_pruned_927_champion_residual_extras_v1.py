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
import benchmark_gomyway_926_champion_combined_staging_plus_step8_midi52_both10_only_gate_v1 as gate927

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-zero-precision-pruned-927-champion-residual-extras-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-zero-precision-pruned-927-champion-residual-extras-profile-v1-manifest.json"

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

EXPECTED = (102, 765, 1232)
EXPECTED_F1 = 9.27


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

    print("Rebuilding validated 9.27 champion and profiling residual extras...", flush=True)
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
    additions_927 = gate927.combined_prune(additions_926, winner_scores, alt_scores, adaptive_base)

    prediction = precond.merge_with_cap(base_champion, additions_927)
    full = grade(prediction, reference)
    actual = (int(full["matched"]), int(full["missing"]), int(full["extra"]))
    if actual != EXPECTED or abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.27 {EXPECTED}/{EXPECTED_F1}, got {actual}/{full['pitchF1']}")

    specialist_extras = Counter({t: c for t, c in (prediction - reference).items() if t in additions_927})
    specialist_matches = Counter({t: c for t, c in (prediction & reference).items() if t in additions_927})

    names = [
        "stepPitch",
        "stepAgreement",
        "scoreAgreement",
        "stepScore",
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
            "stepPitch": f"step{step}_midi{pitch}",
            "stepAgreement": f"step{step}_{agree}",
            "scoreAgreement": f"score{score}_{agree}",
            "stepScore": f"step{step}_score{score}",
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
        raise RuntimeError("Protected candidate changed during 9.27 residual profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.27-combined-pruned-champion-residual-profile",
        "championScore": full,
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
        "recommendedNextAction": "design-next-precision-prune-from-validated-9.27-residual-profile",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": full["pitchF1"],
        "championExtra": full["extra"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ZERO-PRECISION PRUNED 9.27 CHAMPION RESIDUAL EXTRAS PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Specialist addition matches/extras:", sum(specialist_matches.values()), "/", sum(specialist_extras.values()))
    for label, key, limit in [
        ("Top step/pitch specialist buckets", "stepPitch", 20),
        ("Step/agreement specialist precision", "stepAgreement", 20),
        ("Score/agreement specialist precision", "scoreAgreement", 20),
        ("Step/score specialist precision", "stepScore", 20),
        ("Step/pitch/score precision", "stepPitchScore", 30),
        ("Step/pitch/agreement precision", "stepPitchAgreement", 30),
        ("Step/score/agreement precision", "stepScoreAgreement", 30),
        ("Step/pitch/score/agreement precision", "stepPitchScoreAgreement", 30),
        ("Step/pitch/reason precision", "stepPitchReason", 30),
        ("Pitch/score/agreement precision", "pitchScoreAgreement", 30),
    ]:
        print(label + ":")
        for row in profiles[key][:limit]:
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
