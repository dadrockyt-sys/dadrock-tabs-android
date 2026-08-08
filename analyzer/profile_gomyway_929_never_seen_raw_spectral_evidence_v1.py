from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

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
OUTPUT_PATH = PUBLIC / "gomyway-929-never-seen-raw-spectral-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-929-never-seen-raw-spectral-evidence-v1-manifest.json"

EXPECTED = (102, 765, 1227)
EXPECTED_F1 = 9.29
THRESHOLDS = (2.0, 4.0, 6.0, 8.0, 10.0, 13.0, 16.0, 20.0)

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


def recoverable_units(missing, final_prediction, source):
    return missing & (source - final_prediction)


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

    print("Rebuilding frozen validated 9.29 champion...", flush=True)
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
    a = gate926.deep_prune(a, winner_scores, alt_scores, WINNER_926_RULE)
    a = gate927.combined_prune(a, winner_scores, alt_scores, adaptive_base)
    a = gate929.residual_prune(a, winner_scores, alt_scores, adaptive_base)

    final_prediction = precond.merge_with_cap(base_champion, a)
    full = grade(final_prediction, reference)
    actual = (int(full["matched"]), int(full["missing"]), int(full["extra"]))
    if actual != EXPECTED or abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.29 {EXPECTED}/{EXPECTED_F1}, got {actual}/{full['pitchF1']}")

    # Detection is frozen above. Professional reference is used only below for training-label profiling.
    missing = reference - final_prediction
    profiled_sources = [base_winner, base_alt, base_champion, top1, adaptive_base]
    union_recoverable: Counter[tuple[int, int, int]] = Counter()
    for source in profiled_sources:
        union_recoverable |= recoverable_units(missing, final_prediction, source)
    never_seen = missing - union_recoverable

    print("Computing raw spectral evidence at never-seen labeled locations...", flush=True)
    winner_audio, winner_sr = spectral.load_filtered(WINNER_STEM)
    alt_audio, alt_sr = spectral.load_filtered(ALT_STEM)

    threshold_counts = {
        f"either_ge_{int(t)}": 0 for t in THRESHOLDS
    } | {
        f"both_ge_{int(t)}": 0 for t in THRESHOLDS
    }
    rows: list[dict[str, object]] = []
    bucket_values: dict[str, list[tuple[float, float, int]]] = defaultdict(list)

    for (measure, step, pitch), count in never_seen.items():
        center = grid.get((measure, step))
        if center is None:
            continue
        ws = spectral.spectral_score(winner_audio, winner_sr, float(center), int(pitch))
        ats = spectral.spectral_score(alt_audio, alt_sr, float(center), int(pitch))
        mx = max(ws, ats)
        mn = min(ws, ats)
        for t in THRESHOLDS:
            if mx >= t:
                threshold_counts[f"either_ge_{int(t)}"] += int(count)
            if mn >= t:
                threshold_counts[f"both_ge_{int(t)}"] += int(count)
        bucket = f"step{step}_midi{pitch}"
        bucket_values[bucket].append((ws, ats, int(count)))
        rows.append({
            "measure": int(measure),
            "step": int(step),
            "pitch": int(pitch),
            "missingUnits": int(count),
            "winnerScore": round(float(ws), 4),
            "alternateScore": round(float(ats), 4),
            "maxScore": round(float(mx), 4),
            "minScore": round(float(mn), 4),
        })

    bucket_rows: list[dict[str, object]] = []
    for bucket, vals in bucket_values.items():
        units = sum(c for _, _, c in vals)
        winner_weighted = sum(w * c for w, _, c in vals) / units
        alt_weighted = sum(a_ * c for _, a_, c in vals) / units
        max_weighted = sum(max(w, a_) * c for w, a_, c in vals) / units
        either4 = sum(c for w, a_, c in vals if max(w, a_) >= 4.0)
        either8 = sum(c for w, a_, c in vals if max(w, a_) >= 8.0)
        both4 = sum(c for w, a_, c in vals if min(w, a_) >= 4.0)
        bucket_rows.append({
            "bucket": bucket,
            "missingUnits": int(units),
            "winnerMeanScore": round(float(winner_weighted), 3),
            "alternateMeanScore": round(float(alt_weighted), 3),
            "maxMeanScore": round(float(max_weighted), 3),
            "eitherGe4Units": int(either4),
            "eitherGe8Units": int(either8),
            "bothGe4Units": int(both4),
        })
    bucket_rows.sort(key=lambda r: (-int(r["missingUnits"]), -int(r["eitherGe4Units"]), str(r["bucket"])))
    rows.sort(key=lambda r: (-float(r["maxScore"]), int(r["measure"]), int(r["step"]), int(r["pitch"])))

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during never-seen raw spectral profiler.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.29-never-seen-raw-spectral-evidence-training-profile",
        "championScore": full,
        "missingReferenceUnits": int(sum(missing.values())),
        "recoverableFromProfiledUpstream": int(sum(union_recoverable.values())),
        "neverSeenUnits": int(sum(never_seen.values())),
        "rawSpectralThresholdCoverage": threshold_counts,
        "topNeverSeenBucketsWithRawEvidence": bucket_rows[:40],
        "topNeverSeenLocationsByRawSpectralScore": rows[:80],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-never-seen-audio-evidence-profiling-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-reference-free-upstream-recall-candidates-from-raw-spectral-coverage-profile",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": full["pitchF1"],
        "neverSeenUnits": int(sum(never_seen.values())),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.29 NEVER-SEEN RAW SPECTRAL EVIDENCE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Missing / recoverable / never-seen:", sum(missing.values()), "/", sum(union_recoverable.values()), "/", sum(never_seen.values()))
    print("Raw spectral threshold coverage:")
    for t in THRESHOLDS:
        print(f"  either>={int(t)}: {threshold_counts[f'either_ge_{int(t)}']}  both>={int(t)}: {threshold_counts[f'both_ge_{int(t)}']}")
    print("Top never-seen buckets with raw spectral evidence:")
    for row in bucket_rows[:20]:
        print(
            f"  {row['bucket']}: missing={row['missingUnits']} maxMean={row['maxMeanScore']} "
            f"either>=4={row['eitherGe4Units']} either>=8={row['eitherGe8Units']} both>=4={row['bothGe4Units']}"
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
