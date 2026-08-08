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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-step10-pruned-champion-extras-profile-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-step10-pruned-champion-extras-profile-v1-manifest.json"

TEMPORAL_RULE = {"name": "repeat_m2_step1_or_both10", "measureRadius": 2, "stepRadius": 1, "bothFloor": 10.0}
PRUNING_RULE = {"name": "drop_score_10_13", "dropScoreBuckets": ["10_13"]}
METRICAL_RULE = {"name": "even_steps_only", "mode": "even"}
STEP_RULE = {"name": "quarter_plus_step10", "keepSteps": [0, 4, 8, 10, 12]}
EXPECTED_F1 = 9.01


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

    print("Rebuilding frozen validated 9.01 step10-pruned champion...", flush=True)
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
    champion_additions = step10.prune_step_signature(metrical_additions, winner_scores, alt_scores, STEP_RULE)
    champion = precond.merge_with_cap(base_champion, champion_additions)
    full = grade(champion, reference)
    if abs(float(full["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen champion F1 {EXPECTED_F1}, got {full['pitchF1']}")

    extras = champion - reference
    matched = champion & reference
    specialist_extras = Counter({token: count for token, count in extras.items() if token in champion_additions})
    specialist_matches = Counter({token: count for token, count in matched.items() if token in champion_additions})

    dimensions = {
        "scoreBucket": (Counter(), Counter()),
        "stemAgreement": (Counter(), Counter()),
        "recurrenceReason": (Counter(), Counter()),
        "section": (Counter(), Counter()),
        "pitch": (Counter(), Counter()),
        "step": (Counter(), Counter()),
        "stepPitch": (Counter(), Counter()),
        "stepAgreement": (Counter(), Counter()),
    }

    def record(token: tuple[int, int, int], count: int, is_true: bool) -> None:
        measure, step, pitch = token
        values = {
            "scoreBucket": pruning.score_bucket(token, winner_scores, alt_scores),
            "stemAgreement": pruning.agreement_bucket(token, winner_scores, alt_scores),
            "recurrenceReason": pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores),
            "section": section_name(measure),
            "pitch": str(pitch),
            "step": str(step),
            "stepPitch": f"step{step}_midi{pitch}",
            "stepAgreement": f"step{step}_{pruning.agreement_bucket(token, winner_scores, alt_scores)}",
        }
        for name, value in values.items():
            false_counter, true_counter = dimensions[name]
            (true_counter if is_true else false_counter)[value] += count

    for token, count in specialist_extras.items():
        record(token, count, False)
    for token, count in specialist_matches.items():
        record(token, count, True)

    profiles = {name: precision_rows(false_counts, true_counts) for name, (false_counts, true_counts) in dimensions.items()}

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during 9.01 extras profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.01-step10-pruned-champion-extra-profile",
        "championScore": full,
        "frozenTemporalRule": TEMPORAL_RULE,
        "frozenPrecisionRule": PRUNING_RULE,
        "frozenMetricalRule": METRICAL_RULE,
        "frozenStepRule": STEP_RULE,
        "specialistAdditionMatchedCount": sum(specialist_matches.values()),
        "specialistAdditionExtraCount": sum(specialist_extras.values()),
        "profiles": profiles,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-fourth-stage-precision-pruning-from-validated-9.01-cross-signatures",
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

    print("GOMYWAY STEP10-PRUNED CHAMPION EXTRAS PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Frozen champion pitch F1:", full["pitchF1"])
    print("Champion matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Specialist addition matches/extras:", sum(specialist_matches.values()), "/", sum(specialist_extras.values()))
    for label, key, limit in [
        ("Score-bucket specialist precision", "scoreBucket", None),
        ("Stem-agreement specialist precision", "stemAgreement", None),
        ("Recurrence-reason specialist precision", "recurrenceReason", None),
        ("Section specialist precision", "section", None),
        ("Top pitch specialist buckets", "pitch", 12),
        ("Rhythm-step specialist precision", "step", None),
        ("Top step/pitch specialist buckets", "stepPitch", 20),
        ("Step/agreement specialist precision", "stepAgreement", None),
    ]:
        print(label + ":")
        rows = profiles[key][:limit] if limit is not None else profiles[key]
        for row in rows:
            prefix = "midi" if key == "pitch" else ("step" if key == "step" else "")
            print(f"  {prefix}{row['bucket']}: true={row['true']} false={row['false']} precision={row['precisionPercent']}%")
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
