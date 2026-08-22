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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-cross-signature-pruned-residual-zero-precision-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-cross-signature-pruned-residual-zero-precision-gate-v1-manifest.json"

TEMPORAL_RULE = {"name": "repeat_m2_step1_or_both10", "measureRadius": 2, "stepRadius": 1, "bothFloor": 10.0}
PRUNING_RULE = {"name": "drop_score_10_13", "dropScoreBuckets": ["10_13"]}
METRICAL_RULE = {"name": "even_steps_only", "mode": "even"}
STEP_RULE = {"name": "quarter_plus_step10", "keepSteps": [0, 4, 8, 10, 12]}
AGREEMENT_RULE = {"name": "step10_require_both13", "step": 10, "bothFloor": 13.0}
SAFE_CROSS_RULE = {
    "name": "drop_step10_low_score_13_16",
    "dropStepScore": [{"step": 10, "scoreBucket": "13_16"}],
}

EXPECTED_BASELINE_MATCHED = 102
EXPECTED_BASELINE_MISSING = 765
EXPECTED_BASELINE_EXTRA = 1287
EXPECTED_BASELINE_F1 = 9.04

# Detector-side rules chosen only from zero-precision residual profile buckets.
# The professional reference is not consulted by these rules during detection.
RULES: list[dict[str, Any]] = [
    {
        "name": "drop_step10_score16_20",
        "dropStepScore": [{"step": 10, "scoreBucket": "16_20"}],
    },
    {
        "name": "drop_step0_score16_20",
        "dropStepScore": [{"step": 0, "scoreBucket": "16_20"}],
    },
    {
        "name": "drop_step4_score16_20",
        "dropStepScore": [{"step": 4, "scoreBucket": "16_20"}],
    },
    {
        "name": "drop_step0_4_score16_20",
        "dropStepScore": [
            {"step": 0, "scoreBucket": "16_20"},
            {"step": 4, "scoreBucket": "16_20"},
        ],
    },
    {
        "name": "drop_step0_4_10_score16_20",
        "dropStepScore": [
            {"step": 0, "scoreBucket": "16_20"},
            {"step": 4, "scoreBucket": "16_20"},
            {"step": 10, "scoreBucket": "16_20"},
        ],
    },
]


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

    print("Rebuilding validated 1287-extra residual baseline and zero-precision candidates...", flush=True)
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

    residual_additions = crossgate.cross_signature_prune(
        champion_additions,
        winner_scores,
        alt_scores,
        adaptive_base,
        SAFE_CROSS_RULE,
    )
    residual_prediction = precond.merge_with_cap(base_champion, residual_additions)
    residual_score = grade(residual_prediction, reference)

    expected = (EXPECTED_BASELINE_MATCHED, EXPECTED_BASELINE_MISSING, EXPECTED_BASELINE_EXTRA)
    actual = (
        int(residual_score["matched"]),
        int(residual_score["missing"]),
        int(residual_score["extra"]),
    )
    if actual != expected:
        raise RuntimeError(f"Expected validated residual baseline {expected}, got {actual}")
    if abs(float(residual_score["pitchF1"]) - EXPECTED_BASELINE_F1) > 0.01:
        raise RuntimeError(
            f"Expected residual baseline F1 {EXPECTED_BASELINE_F1}, got {residual_score['pitchF1']}"
        )

    results: dict[str, Any] = {}
    for rule in RULES:
        filtered_additions = crossgate.cross_signature_prune(
            residual_additions,
            winner_scores,
            alt_scores,
            adaptive_base,
            rule,
        )
        prediction = precond.merge_with_cap(base_champion, filtered_additions)
        result = crossgate.evaluate_candidate(
            prediction,
            residual_prediction,
            reference,
            residual_score,
        )
        result["rule"] = rule
        result["additionCount"] = sum(filtered_additions.values())
        result["additionsDroppedFromResidual"] = sum(residual_additions.values()) - sum(filtered_additions.values())
        results[str(rule["name"])] = result
        print(
            f"{rule['name']}: F1={result['fullScore']['pitchF1']} "
            f"matched={result['fullScore']['matched']} missing={result['fullScore']['missing']} "
            f"extra={result['fullScore']['extra']} extraReduction={result['extraReduction']} "
            f"matchedChange={result['matchedChange']} cv={result['crossValidationPassed']} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={result['acceptedOverChampion']}",
            flush=True,
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["acceptedOverChampion"]),
            int(item[1]["fullScore"]["matched"]),
            float(item[1]["fullScore"]["pitchF1"]),
            -int(item[1]["fullScore"]["extra"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]
    validated_new_champion = bool(winner["acceptedOverChampion"])

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during residual zero-precision benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-1287-extra-residual-zero-precision-cross-signature-gate",
        "baselineScore": residual_score,
        "safeCrossSignatureRule": SAFE_CROSS_RULE,
        "rules": RULES,
        "results": results,
        "winner": winner_name,
        "winnerResult": winner,
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
        "candidateSha256": candidate_hash_after,
        "baselinePitchF1": residual_score["pitchF1"],
        "baselineExtra": residual_score["extra"],
        "winner": winner_name,
        "winnerPitchF1": winner["fullScore"]["pitchF1"],
        "winnerMatched": winner["fullScore"]["matched"],
        "winnerExtra": winner["fullScore"]["extra"],
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY CROSS-SIGNATURE PRUNED RESIDUAL ZERO-PRECISION GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", residual_score["pitchF1"])
    print(
        "Baseline matched/missing/extra:",
        residual_score["matched"], "/", residual_score["missing"], "/", residual_score["extra"],
    )
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print(
        "Winner matched/missing/extra:",
        winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"],
    )
    print("Winner extra reduction:", winner["extraReduction"])
    print("Winner matched change:", winner["matchedChange"])
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
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
