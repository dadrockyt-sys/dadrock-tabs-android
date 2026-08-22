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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-precision-pruned-champion-extras-profile-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-precision-pruned-champion-extras-profile-v2-manifest.json"

TEMPORAL_RULE = {
    "name": "repeat_m2_step1_or_both10",
    "measureRadius": 2,
    "stepRadius": 1,
    "bothFloor": 10.0,
}
PRUNING_RULE = {"name": "drop_score_10_13", "dropScoreBuckets": ["10_13"]}
EXPECTED_F1 = 8.22


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
    rows: list[dict[str, Any]] = []
    for key in sorted(set(false_counts) | set(true_counts)):
        false = int(false_counts[key])
        true = int(true_counts[key])
        total = false + true
        rows.append({
            "bucket": key,
            "true": true,
            "false": false,
            "total": total,
            "precisionPercent": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda row: (-int(row["total"]), -float(row["precisionPercent"]), str(row["bucket"])))


def score_bucket(token: tuple[int, int, int], winner_scores: dict, alt_scores: dict) -> str:
    return pruning.score_bucket(token, winner_scores, alt_scores)


def agreement_bucket(token: tuple[int, int, int], winner_scores: dict, alt_scores: dict) -> str:
    return pruning.agreement_bucket(token, winner_scores, alt_scores)


def reason_bucket(token: tuple[int, int, int], adaptive_base: Counter, winner_scores: dict, alt_scores: dict) -> str:
    return pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores)


def section_name(measure: int) -> str:
    for start, end in temporal.BLOCKS:
        if start <= measure <= end:
            return f"m{start}_{end}"
    return "outside_scored_range"


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

    print("Rebuilding frozen validated 8.22 precision-pruned champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, TEMPORAL_RULE)
    pruned_additions = pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, PRUNING_RULE)
    champion = precond.merge_with_cap(base_champion, pruned_additions)
    full = grade(champion, reference)

    if abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen champion F1 {EXPECTED_F1}, got {full['pitchF1']}")

    extras = champion - reference
    matched = champion & reference
    specialist_extras = Counter({token: count for token, count in extras.items() if token in pruned_additions})
    specialist_matches = Counter({token: count for token, count in matched.items() if token in pruned_additions})

    score_false: Counter[str] = Counter()
    score_true: Counter[str] = Counter()
    agreement_false: Counter[str] = Counter()
    agreement_true: Counter[str] = Counter()
    reason_false: Counter[str] = Counter()
    reason_true: Counter[str] = Counter()
    section_false: Counter[str] = Counter()
    section_true: Counter[str] = Counter()
    pitch_false: Counter[int] = Counter()
    pitch_true: Counter[int] = Counter()
    step_false: Counter[int] = Counter()
    step_true: Counter[int] = Counter()

    for token, count in specialist_extras.items():
        measure, step, pitch = token
        score_false[score_bucket(token, winner_scores, alt_scores)] += count
        agreement_false[agreement_bucket(token, winner_scores, alt_scores)] += count
        reason_false[reason_bucket(token, adaptive_base, winner_scores, alt_scores)] += count
        section_false[section_name(measure)] += count
        pitch_false[pitch] += count
        step_false[step] += count

    for token, count in specialist_matches.items():
        measure, step, pitch = token
        score_true[score_bucket(token, winner_scores, alt_scores)] += count
        agreement_true[agreement_bucket(token, winner_scores, alt_scores)] += count
        reason_true[reason_bucket(token, adaptive_base, winner_scores, alt_scores)] += count
        section_true[section_name(measure)] += count
        pitch_true[pitch] += count
        step_true[step] += count

    score_precision = precision_rows(score_false, score_true)
    agreement_precision = precision_rows(agreement_false, agreement_true)
    reason_precision = precision_rows(reason_false, reason_true)
    section_precision = precision_rows(section_false, section_true)
    pitch_precision = precision_rows(Counter({str(k): v for k, v in pitch_false.items()}), Counter({str(k): v for k, v in pitch_true.items()}))
    step_precision = precision_rows(Counter({str(k): v for k, v in step_false.items()}), Counter({str(k): v for k, v in step_true.items()}))

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during 8.22 extras profile.")

    output = {
        "schemaVersion": 2,
        "passed": True,
        "benchmarkType": "validated-8.22-precision-pruned-champion-extra-profile",
        "frozenTemporalRule": TEMPORAL_RULE,
        "frozenPruningRule": PRUNING_RULE,
        "championScore": full,
        "specialistAdditionExtraCount": sum(specialist_extras.values()),
        "specialistAdditionMatchedCount": sum(specialist_matches.values()),
        "scoreBucketPrecision": score_precision,
        "stemAgreementPrecision": agreement_precision,
        "recurrenceReasonPrecision": reason_precision,
        "sectionPrecision": section_precision,
        "pitchPrecision": pitch_precision,
        "stepPrecision": step_precision,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-second-stage-precision-pruning-from-validated-8.22-detector-side-signatures",
    }
    manifest = {
        "schemaVersion": 2,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "frozenChampionPitchF1": full["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY PRECISION-PRUNED CHAMPION EXTRAS PROFILE V2 COMPLETE")
    print("Passed: True")
    print("Frozen champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Specialist addition matches/extras:", sum(specialist_matches.values()), "/", sum(specialist_extras.values()))
    print("Score-bucket specialist precision:")
    for row in score_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Stem-agreement specialist precision:")
    for row in agreement_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Recurrence-reason specialist precision:")
    for row in reason_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Section specialist precision:")
    for row in section_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Top pitch specialist buckets:")
    for row in pitch_precision[:12]:
        print(f"  midi{row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Rhythm-step specialist precision:")
    for row in step_precision:
        print(f"  step{row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
