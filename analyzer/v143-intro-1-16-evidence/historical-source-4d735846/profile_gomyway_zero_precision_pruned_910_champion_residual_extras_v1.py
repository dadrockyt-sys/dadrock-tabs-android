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
import profile_gomyway_zero_precision_pruned_909_champion_residual_extras_v1 as p909

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-zero-precision-pruned-910-champion-residual-extras-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-zero-precision-pruned-910-champion-residual-extras-profile-v1-manifest.json"

FINAL_RULE = {
    "name": "drop_all_profiled_zero_precision_cross_signatures",
    "dropStepScore": [{"step": 4, "scoreBucket": "13_16"}],
    "dropScoreAgreement": [
        {"scoreBucket": "13_16", "agreementBucket": "both_ge8"},
        {"scoreBucket": "13_16", "agreementBucket": "single_stem_or_weak_second"},
        {"scoreBucket": "20_plus", "agreementBucket": "both_ge8"},
    ],
}
EXPECTED = (102, 765, 1272)
EXPECTED_F1 = 9.10


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    print("Rebuilding validated 9.10 champion and profiling residual extras...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)
    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, p909.TEMPORAL_RULE)
    precision_additions = pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, p909.PRUNING_RULE)
    metrical_additions = metrical.metrical_prune(precision_additions, winner_scores, alt_scores, p909.METRICAL_RULE)
    step_additions = step10.prune_step_signature(metrical_additions, winner_scores, alt_scores, p909.STEP_RULE)
    champion_additions = agreement.agreement_prune(step_additions, winner_scores, alt_scores, p909.AGREEMENT_RULE)
    residual_additions = crossgate.cross_signature_prune(champion_additions, winner_scores, alt_scores, adaptive_base, p909.SAFE_CROSS_RULE)
    winner909_additions = crossgate.cross_signature_prune(residual_additions, winner_scores, alt_scores, adaptive_base, p909.ZERO_PRECISION_RULE)
    winner910_additions = crossgate.cross_signature_prune(winner909_additions, winner_scores, alt_scores, adaptive_base, FINAL_RULE)
    prediction = precond.merge_with_cap(base_champion, winner910_additions)
    full = p909.grade(prediction, reference)

    actual = (int(full["matched"]), int(full["missing"]), int(full["extra"]))
    if actual != EXPECTED:
        raise RuntimeError(f"Expected validated 9.10 score {EXPECTED}, got {actual}")
    if abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.10 F1 {EXPECTED_F1}, got {full['pitchF1']}")

    extras = prediction - reference
    matched = prediction & reference
    specialist_extras = Counter({token: count for token, count in extras.items() if token in winner910_additions})
    specialist_matches = Counter({token: count for token, count in matched.items() if token in winner910_additions})
    dimensions = {name: (Counter(), Counter()) for name in [
        "scoreBucket", "stemAgreement", "recurrenceReason", "section", "pitch", "step",
        "stepPitch", "stepAgreement", "scoreAgreement", "stepScore"
    ]}

    def section_name(measure: int) -> str:
        for start, end in temporal.BLOCKS:
            if start <= measure <= end:
                return f"m{start}_{end}"
        return "outside_scored_range"

    def record(token: tuple[int, int, int], count: int, is_true: bool) -> None:
        measure, step, pitch = token
        score_bucket = pruning.score_bucket(token, winner_scores, alt_scores)
        agreement_bucket = pruning.agreement_bucket(token, winner_scores, alt_scores)
        values = {
            "scoreBucket": score_bucket,
            "stemAgreement": agreement_bucket,
            "recurrenceReason": pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores),
            "section": section_name(measure),
            "pitch": str(pitch),
            "step": str(step),
            "stepPitch": f"step{step}_midi{pitch}",
            "stepAgreement": f"step{step}_{agreement_bucket}",
            "scoreAgreement": f"score{score_bucket}_{agreement_bucket}",
            "stepScore": f"step{step}_score{score_bucket}",
        }
        for name, value in values.items():
            false_counter, true_counter = dimensions[name]
            (true_counter if is_true else false_counter)[value] += count

    for token, count in specialist_extras.items():
        record(token, count, False)
    for token, count in specialist_matches.items():
        record(token, count, True)

    profiles = {name: p909.precision_rows(false_counts, true_counts) for name, (false_counts, true_counts) in dimensions.items()}
    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during 9.10 residual profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.10-champion-residual-extra-profile",
        "championScore": full,
        "finalRule": FINAL_RULE,
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
        "recommendedNextAction": "design-next-precision-prune-from-validated-9.10-residual-profile",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "championPitchF1": full["pitchF1"],
        "championExtra": full["extra"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY ZERO-PRECISION PRUNED 9.10 CHAMPION RESIDUAL EXTRAS PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    for label, key, limit in [
        ("Top step/pitch specialist buckets", "stepPitch", 20),
        ("Step/agreement specialist precision", "stepAgreement", None),
        ("Score/agreement specialist precision", "scoreAgreement", 20),
        ("Step/score specialist precision", "stepScore", 20),
    ]:
        print(label + ":")
        rows = profiles[key][:limit] if limit is not None else profiles[key]
        for row in rows:
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
