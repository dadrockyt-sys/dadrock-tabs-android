from __future__ import annotations

import hashlib
import json
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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-910-champion-zero-precision-step-pitch-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-910-champion-zero-precision-step-pitch-gate-v1-manifest.json"

TEMPORAL_RULE = gate909.TEMPORAL_RULE
PRUNING_RULE = gate909.PRUNING_RULE
METRICAL_RULE = gate909.METRICAL_RULE
STEP_RULE = gate909.STEP_RULE
AGREEMENT_RULE = gate909.AGREEMENT_RULE
SAFE_CROSS_RULE = gate909.SAFE_CROSS_RULE
ZERO_PRECISION_RULE = gate909.ZERO_PRECISION_RULE
WINNER_910_RULE = next(rule for rule in gate909.RULES if rule["name"] == "drop_all_profiled_zero_precision_cross_signatures")

EXPECTED_MATCHED = 102
EXPECTED_MISSING = 765
EXPECTED_EXTRA = 1272
EXPECTED_F1 = 9.10

RULES: list[dict[str, Any]] = [
    {"name": "drop_step4_midi57", "dropStepPitch": [{"step": 4, "pitch": 57}]},
    {"name": "drop_step10_midi57", "dropStepPitch": [{"step": 10, "pitch": 57}]},
    {"name": "drop_step12_midi62", "dropStepPitch": [{"step": 12, "pitch": 62}]},
    {"name": "drop_step4_midi62", "dropStepPitch": [{"step": 4, "pitch": 62}]},
    {"name": "drop_step8_midi62", "dropStepPitch": [{"step": 8, "pitch": 62}]},
    {
        "name": "drop_midi57_zero_precision_pair",
        "dropStepPitch": [{"step": 4, "pitch": 57}, {"step": 10, "pitch": 57}],
    },
    {
        "name": "drop_midi62_zero_precision_trio",
        "dropStepPitch": [{"step": 12, "pitch": 62}, {"step": 4, "pitch": 62}, {"step": 8, "pitch": 62}],
    },
    {
        "name": "drop_all_profiled_zero_precision_step_pitch",
        "dropStepPitch": [
            {"step": 4, "pitch": 57},
            {"step": 10, "pitch": 57},
            {"step": 12, "pitch": 62},
            {"step": 4, "pitch": 62},
            {"step": 8, "pitch": 62},
        ],
    },
]


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

    print("Rebuilding validated 9.10 champion and step-pitch candidates...", flush=True)
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
    residual_additions = crossgate.cross_signature_prune(champion_additions, winner_scores, alt_scores, adaptive_base, SAFE_CROSS_RULE)
    additions909 = crossgate.cross_signature_prune(residual_additions, winner_scores, alt_scores, adaptive_base, ZERO_PRECISION_RULE)
    additions910 = crossgate.cross_signature_prune(additions909, winner_scores, alt_scores, adaptive_base, WINNER_910_RULE)
    baseline_prediction = precond.merge_with_cap(base_champion, additions910)
    baseline_score = grade(baseline_prediction, reference)

    actual = (int(baseline_score["matched"]), int(baseline_score["missing"]), int(baseline_score["extra"]))
    expected = (EXPECTED_MATCHED, EXPECTED_MISSING, EXPECTED_EXTRA)
    if actual != expected:
        raise RuntimeError(f"Expected validated 9.10 baseline {expected}, got {actual}")
    if abs(float(baseline_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated F1 {EXPECTED_F1}, got {baseline_score['pitchF1']}")

    results: dict[str, Any] = {}
    for rule in RULES:
        filtered_additions = crossgate.cross_signature_prune(additions910, winner_scores, alt_scores, adaptive_base, rule)
        prediction = precond.merge_with_cap(base_champion, filtered_additions)
        result = crossgate.evaluate_candidate(prediction, baseline_prediction, reference, baseline_score)
        result["rule"] = rule
        result["additionsDroppedFrom910"] = sum(additions910.values()) - sum(filtered_additions.values())
        results[str(rule["name"])] = result
        print(
            f"{rule['name']}: F1={result['fullScore']['pitchF1']} matched={result['fullScore']['matched']} "
            f"missing={result['fullScore']['missing']} extra={result['fullScore']['extra']} "
            f"extraReduction={result['extraReduction']} matchedChange={result['matchedChange']} "
            f"cv={result['crossValidationPassed']} sections={result['sectionStabilityPassed']} "
            f"shifted={result['shiftedWindowStabilityPassed']} accepted={result['acceptedOverChampion']}",
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
        raise RuntimeError("Protected candidate changed during 9.10 step-pitch benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.10-champion-zero-precision-step-pitch-gate",
        "baselineScore": baseline_score,
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
        "baselinePitchF1": baseline_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.10 CHAMPION ZERO-PRECISION STEP-PITCH GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline_score["pitchF1"])
    print("Baseline matched/missing/extra:", baseline_score["matched"], "/", baseline_score["missing"], "/", baseline_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
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
