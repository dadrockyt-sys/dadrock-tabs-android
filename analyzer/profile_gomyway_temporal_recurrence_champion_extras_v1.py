from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_mid_register_audio_preconditioning_v1 as precond
import benchmark_gomyway_mid_register_spectral_specialist_v1 as spectral
import benchmark_gomyway_spectral_specialist_precision_gate_v1 as gate
import benchmark_gomyway_spectral_top1_adaptive_local_gate_v1 as adaptive
import benchmark_gomyway_adaptive_spectral_temporal_recurrence_gate_v1 as temporal

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-temporal-recurrence-champion-extras-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-temporal-recurrence-champion-extras-profile-v1-manifest.json"

WINNER_RULE = {
    "name": "repeat_m2_step1_or_both10",
    "measureRadius": 2,
    "stepRadius": 1,
    "bothFloor": 10.0,
}
EXPECTED_F1 = 8.04


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


def pitch_band(pitch: int) -> str:
    if pitch < 52:
        return "below_mid"
    if pitch <= 63:
        return "mid_52_63"
    return "above_mid"


def main() -> None:
    candidate_hash_before = sha256(CANDIDATE_PATH)
    candidate = v2.load_json(CANDIDATE_PATH)
    events = v2.candidate_rows(candidate)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen 8.04 temporal-recurrence champion...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    recurrence_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, WINNER_RULE)
    champion = precond.merge_with_cap(base_champion, recurrence_additions)
    full = grade(champion, reference)

    if abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen champion F1 {EXPECTED_F1}, got {full['pitchF1']}")

    extras = champion - reference
    matched = champion & reference
    base_extras = base_champion - reference
    addition_extras = Counter({t: c for t, c in extras.items() if t in recurrence_additions})
    addition_matches = Counter({t: c for t, c in matched.items() if t in recurrence_additions})

    section_extra = Counter()
    section_add_extra = Counter()
    pitch_extra = Counter()
    pitch_add_extra = Counter()
    band_extra = Counter()
    step_extra = Counter()
    score_bucket_extra = Counter()
    score_bucket_true = Counter()
    agreement_extra = Counter()
    agreement_true = Counter()
    recurrence_reason_extra = Counter()
    recurrence_reason_true = Counter()

    def score_bucket(token: tuple[int, int, int]) -> str:
        best = max(float(winner_scores.get(token, 0.0)), float(alt_scores.get(token, 0.0)))
        if best < 10:
            return "8_10"
        if best < 13:
            return "10_13"
        if best < 16:
            return "13_16"
        if best < 20:
            return "16_20"
        return "20_plus"

    def agreement_bucket(token: tuple[int, int, int]) -> str:
        w = float(winner_scores.get(token, 0.0))
        a = float(alt_scores.get(token, 0.0))
        if w >= 10.0 and a >= 10.0:
            return "both_ge10"
        if w >= 8.0 and a >= 8.0:
            return "both_ge8"
        return "single_stem_or_weak_second"

    def reason_bucket(token: tuple[int, int, int]) -> str:
        recurrent = temporal.recurrent(token, set(adaptive_base), 2, 1)
        w = float(winner_scores.get(token, 0.0))
        a = float(alt_scores.get(token, 0.0))
        both10 = w >= 10.0 and a >= 10.0
        if recurrent and both10:
            return "recurrent_and_both10"
        if recurrent:
            return "recurrent_only"
        if both10:
            return "both10_only"
        return "other"

    for token, count in extras.items():
        measure, step, pitch = token
        section_extra[section_name(measure)] += count
        pitch_extra[pitch] += count
        band_extra[pitch_band(pitch)] += count
        step_extra[step] += count
        if token in recurrence_additions:
            section_add_extra[section_name(measure)] += count
            pitch_add_extra[pitch] += count
            score_bucket_extra[score_bucket(token)] += count
            agreement_extra[agreement_bucket(token)] += count
            recurrence_reason_extra[reason_bucket(token)] += count

    for token, count in addition_matches.items():
        score_bucket_true[score_bucket(token)] += count
        agreement_true[agreement_bucket(token)] += count
        recurrence_reason_true[reason_bucket(token)] += count

    def precision_rows(false_counts: Counter[str], true_counts: Counter[str]) -> list[dict[str, Any]]:
        keys = sorted(set(false_counts) | set(true_counts))
        rows: list[dict[str, Any]] = []
        for key in keys:
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
        return sorted(rows, key=lambda r: (-float(r["precisionPercent"]), -int(r["total"]), str(r["bucket"])))

    score_precision = precision_rows(score_bucket_extra, score_bucket_true)
    agreement_precision = precision_rows(agreement_extra, agreement_true)
    reason_precision = precision_rows(recurrence_reason_extra, recurrence_reason_true)

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected 949-event candidate changed during extras profiling.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-temporal-recurrence-champion-extra-profile",
        "frozenChampionRule": WINNER_RULE,
        "championScore": full,
        "baseExtraCount": sum(base_extras.values()),
        "totalExtraCount": sum(extras.values()),
        "specialistAdditionExtraCount": sum(addition_extras.values()),
        "specialistAdditionMatchedCount": sum(addition_matches.values()),
        "sectionExtraCounts": dict(section_extra),
        "sectionSpecialistExtraCounts": dict(section_add_extra),
        "topExtraPitches": pitch_extra.most_common(15),
        "topSpecialistExtraPitches": pitch_add_extra.most_common(15),
        "pitchBandExtraCounts": dict(band_extra),
        "rhythmStepExtraCounts": dict(step_extra),
        "scoreBucketPrecision": score_precision,
        "stemAgreementPrecision": agreement_precision,
        "recurrenceReasonPrecision": reason_precision,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-precision-filter-for-validated-8.04-champion-using-detector-side-extra-signature",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "frozenChampionPitchF1": full["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY TEMPORAL RECURRENCE CHAMPION EXTRAS PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion: repeat_m2_step1_or_both10")
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Champion pitch F1:", full["pitchF1"])
    print("Base extras:", sum(base_extras.values()))
    print("Specialist addition extras:", sum(addition_extras.values()))
    print("Specialist addition matches:", sum(addition_matches.values()))
    print("Section specialist extras:")
    for key, value in section_add_extra.most_common():
        print(" ", key, value)
    print("Score-bucket specialist precision:")
    for row in score_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Stem-agreement specialist precision:")
    for row in agreement_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Recurrence-reason specialist precision:")
    for row in reason_precision:
        print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
    print("Top specialist extra pitches:")
    for pitch, count in pitch_add_extra.most_common(12):
        print(" ", pitch, count)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
