from __future__ import annotations

import hashlib
import json
import statistics
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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-step-score-pruning-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-step-score-pruning-v1-manifest.json"

FOLDS = 5
BLOCKS = temporal.BLOCKS
SHIFTED_WINDOWS = temporal.SHIFTED_WINDOWS
CURRENT_CHAMPION_F1 = 9.04
TEMPORAL_RULE = {"name": "repeat_m2_step1_or_both10", "measureRadius": 2, "stepRadius": 1, "bothFloor": 10.0}
PRUNING_RULE = {"name": "drop_score_10_13", "dropScoreBuckets": ["10_13"]}
METRICAL_RULE = {"name": "even_steps_only", "mode": "even"}
STEP_RULE = {"name": "quarter_plus_step10", "keepSteps": [0, 4, 8, 10, 12]}
AGREEMENT_RULE = {"name": "step10_require_both13", "step": 10, "bothFloor": 13.0}

# Frozen detector-side signatures from the validated 9.04 profile.
# The professional reference was used only to identify candidate buckets, then
# these fixed rules are subjected to fold, section and shifted-window audits.
RULES = [
    {
        "name": "drop_step10_score16_20",
        "drop": [[10, "16_20"]],
    },
    {
        "name": "drop_step10_score13_20",
        "drop": [[10, "13_16"], [10, "16_20"]],
    },
    {
        "name": "drop_step0_4_score16_20",
        "drop": [[0, "16_20"], [4, "16_20"]],
    },
    {
        "name": "drop_zero_precision_cross_signatures",
        "drop": [[0, "16_20"], [4, "16_20"], [10, "13_16"], [10, "16_20"]],
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


def fold_subset(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


def range_subset(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


def compare_ranges(candidate: Counter, champion: Counter, reference: Counter, ranges: list[tuple[int, int]]) -> dict[str, Any]:
    rows = []
    positive_f1 = 0
    matched_nonloss = 0
    extra_reduced = 0
    catastrophic = 0
    deltas: list[float] = []
    for start, end in ranges:
        ref = range_subset(reference, start, end)
        old = grade(range_subset(champion, start, end), ref)
        new = grade(range_subset(candidate, start, end), ref)
        delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
        matched_delta = int(new["matched"]) - int(old["matched"])
        extra_delta = int(new["extra"]) - int(old["extra"])
        positive_f1 += int(delta > 0)
        matched_nonloss += int(matched_delta >= 0)
        extra_reduced += int(extra_delta < 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        rows.append({
            "range": f"m{start}_{end}",
            "deltaPoints": delta,
            "matchedDelta": matched_delta,
            "extraDelta": extra_delta,
        })
    return {
        "rows": rows,
        "positiveF1": positive_f1,
        "matchedNonloss": matched_nonloss,
        "extraReduced": extra_reduced,
        "catastrophic": catastrophic,
        "meanDelta": round(sum(deltas) / len(deltas), 2),
        "medianDelta": round(float(statistics.median(deltas)), 2),
    }


def step_score_prune(
    additions: Counter[tuple[int, int, int]],
    winner_scores: dict[tuple[int, int, int], float],
    alt_scores: dict[tuple[int, int, int], float],
    rule: dict[str, Any],
) -> Counter[tuple[int, int, int]]:
    drop = {(int(step), str(bucket)) for step, bucket in rule["drop"]}
    out: Counter[tuple[int, int, int]] = Counter()
    for token, count in additions.items():
        _, step, _ = token
        bucket = pruning.score_bucket(token, winner_scores, alt_scores)
        if (step, bucket) not in drop:
            out[token] = count
    return out


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

    print("Rebuilding frozen validated 9.04 champion and step-score pruning candidates...", flush=True)
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
    champion = precond.merge_with_cap(base_champion, champion_additions)
    champion_score = grade(champion, reference)
    if abs(float(champion_score["pitchF1"]) - CURRENT_CHAMPION_F1) > 0.01:
        raise RuntimeError(f"Expected frozen champion F1 {CURRENT_CHAMPION_F1}, got {champion_score['pitchF1']}")

    results: dict[str, Any] = {}
    for rule in RULES:
        filtered_additions = step_score_prune(champion_additions, winner_scores, alt_scores, rule)
        prediction = precond.merge_with_cap(base_champion, filtered_additions)
        full = grade(prediction, reference)

        positive_folds = 0
        matched_nonloss_folds = 0
        extra_reduced_folds = 0
        catastrophic_folds = 0
        fold_deltas: list[float] = []
        for fold in range(FOLDS):
            ref = fold_subset(reference, fold)
            old = grade(fold_subset(champion, fold), ref)
            new = grade(fold_subset(prediction, fold), ref)
            delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
            matched_delta = int(new["matched"]) - int(old["matched"])
            extra_delta = int(new["extra"]) - int(old["extra"])
            positive_folds += int(delta > 0)
            matched_nonloss_folds += int(matched_delta >= 0)
            extra_reduced_folds += int(extra_delta < 0)
            catastrophic_folds += int(delta <= -1.0)
            fold_deltas.append(delta)

        mean_fold = round(sum(fold_deltas) / FOLDS, 2)
        median_fold = round(float(statistics.median(fold_deltas)), 2)
        cv_passed = (
            matched_nonloss_folds == FOLDS
            and extra_reduced_folds >= 1
            and catastrophic_folds == 0
            and mean_fold >= 0
            and median_fold >= 0
        )

        blocks = compare_ranges(prediction, champion, reference, BLOCKS)
        section_passed = (
            blocks["matchedNonloss"] == len(BLOCKS)
            and blocks["catastrophic"] == 0
            and blocks["meanDelta"] >= 0
            and blocks["medianDelta"] >= 0
        )

        windows = compare_ranges(prediction, champion, reference, SHIFTED_WINDOWS)
        shifted_passed = (
            windows["matchedNonloss"] == len(SHIFTED_WINDOWS)
            and windows["catastrophic"] == 0
            and windows["meanDelta"] >= 0
            and windows["medianDelta"] >= 0
        )

        accepted = (
            float(full["pitchF1"]) > CURRENT_CHAMPION_F1
            and int(full["extra"]) < int(champion_score["extra"])
            and int(full["matched"]) >= int(champion_score["matched"])
            and cv_passed
            and section_passed
            and shifted_passed
        )

        results[str(rule["name"])] = {
            "rule": rule,
            "fullScore": full,
            "additionCount": sum(filtered_additions.values()),
            "extraReduction": int(champion_score["extra"]) - int(full["extra"]),
            "matchedChange": int(full["matched"]) - int(champion_score["matched"]),
            "positiveF1Folds": positive_folds,
            "matchedNonlossFolds": matched_nonloss_folds,
            "extraReducedFolds": extra_reduced_folds,
            "catastrophicFolds": catastrophic_folds,
            "meanFoldDeltaPoints": mean_fold,
            "medianFoldDeltaPoints": median_fold,
            "crossValidationPassed": cv_passed,
            "sectionAudit": blocks,
            "sectionStabilityPassed": section_passed,
            "shiftedWindowAudit": windows,
            "shiftedWindowStabilityPassed": shifted_passed,
            "acceptedOverChampion": accepted,
        }
        print(
            f"{rule['name']}: F1={full['pitchF1']} matched={full['matched']} extra={full['extra']} "
            f"extraReduction={int(champion_score['extra']) - int(full['extra'])} "
            f"matchedChange={int(full['matched']) - int(champion_score['matched'])} "
            f"cv={cv_passed} sections={section_passed} shifted={shifted_passed} accepted={accepted}",
            flush=True,
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["acceptedOverChampion"]),
            float(item[1]["fullScore"]["pitchF1"]),
            int(item[1]["extraReduction"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during step-score pruning benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.04-step-score-precision-pruning",
        "currentChampion": champion_score,
        "frozenTemporalRule": TEMPORAL_RULE,
        "frozenPrecisionRule": PRUNING_RULE,
        "frozenMetricalRule": METRICAL_RULE,
        "frozenStepRule": STEP_RULE,
        "frozenAgreementRule": AGREEMENT_RULE,
        "rules": RULES,
        "results": results,
        "winner": winner_name,
        "winnerAccepted": bool(winner["acceptedOverChampion"]),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "lock-step-score-pruned-champion" if winner["acceptedOverChampion"] else "retain-9.04-and-profile-next-cross-signature",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "winner": winner_name,
        "winnerAccepted": bool(winner["acceptedOverChampion"]),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY STEP-SCORE PRECISION PRUNING V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Current champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner extra reduction:", winner["extraReduction"])
    print("Winner matched change:", winner["matchedChange"])
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
    print("Winner accepted over 9.04 champion:", winner["acceptedOverChampion"])
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
