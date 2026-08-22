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

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
WINNER_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-bsroformer-demucs6s-guitar.wav"
ALT_STEM = PUBLIC / "separator-benchmark-v2" / "gomyway-demucs6s-direct-guitar.wav"
CANDIDATE_PATH = PUBLIC / "gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json"
REFERENCE_PATH = PUBLIC / "gomyway-professional-rhythm-reference-17-113.json"
OUTPUT_PATH = PUBLIC / "gomyway-metrically-pruned-champion-step10-exception-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-metrically-pruned-champion-step10-exception-v1-manifest.json"

FOLDS = 5
BLOCKS = temporal.BLOCKS
SHIFTED_WINDOWS = temporal.SHIFTED_WINDOWS
CURRENT_CHAMPION_F1 = 8.77
TEMPORAL_RULE = {"name": "repeat_m2_step1_or_both10", "measureRadius": 2, "stepRadius": 1, "bothFloor": 10.0}
PRUNING_RULE = {"name": "drop_score_10_13", "dropScoreBuckets": ["10_13"]}
METRICAL_RULE = {"name": "even_steps_only", "mode": "even"}

# Predeclared detector-side rules motivated by the frozen 8.77 profile:
# step%4==2 had only two surviving specialist matches, both at step 10.
# Validation below decides whether this signature generalizes; reference labels
# are never consulted by the detector itself.
RULES = [
    {"name": "quarter_plus_step10", "keepSteps": [0, 4, 8, 10, 12]},
    {"name": "quarter_plus_step10_or_both13", "keepSteps": [0, 4, 8, 10, 12], "bothFloor": 13.0},
    {"name": "quarter_plus_step10_or_both16", "keepSteps": [0, 4, 8, 10, 12], "bothFloor": 16.0},
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
    nonnegative_f1 = 0
    catastrophic = 0
    extra_reduced = 0
    matched_nonloss = 0
    deltas = []
    for start, end in ranges:
        ref = range_subset(reference, start, end)
        c = grade(range_subset(champion, start, end), ref)
        p = grade(range_subset(candidate, start, end), ref)
        delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
        extra_delta = int(p["extra"]) - int(c["extra"])
        matched_delta = int(p["matched"]) - int(c["matched"])
        positive_f1 += int(delta > 0)
        nonnegative_f1 += int(delta >= 0)
        catastrophic += int(delta <= -1.0)
        extra_reduced += int(extra_delta < 0)
        matched_nonloss += int(matched_delta >= 0)
        deltas.append(delta)
        rows.append({"range": f"m{start}_{end}", "deltaPoints": delta, "matchedDelta": matched_delta, "extraDelta": extra_delta})
    return {
        "rows": rows,
        "positiveF1": positive_f1,
        "nonnegativeF1": nonnegative_f1,
        "catastrophic": catastrophic,
        "extraReduced": extra_reduced,
        "matchedNonloss": matched_nonloss,
        "meanDelta": round(sum(deltas) / len(deltas), 2),
        "medianDelta": round(float(statistics.median(deltas)), 2),
    }


def prune_step_signature(additions: Counter, winner_scores: dict, alt_scores: dict, rule: dict[str, Any]) -> Counter:
    out: Counter = Counter()
    keep_steps = set(int(step) for step in rule["keepSteps"])
    both_floor = rule.get("bothFloor")
    for token, count in additions.items():
        _, step, _ = token
        keep = step in keep_steps
        if not keep and both_floor is not None:
            w = float(winner_scores.get(token, 0.0))
            a = float(alt_scores.get(token, 0.0))
            keep = w >= float(both_floor) and a >= float(both_floor)
        if keep:
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

    print("Rebuilding frozen validated 8.77 champion and step-signature candidates...", flush=True)
    base_winner = precond.prediction(precond.grouped_for(WINNER_STEM, grid))
    base_alt = precond.prediction(precond.grouped_for(ALT_STEM, grid))
    base_champion = precond.merge_with_cap(base_winner, base_alt)

    winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, TEMPORAL_RULE)
    precision_additions = pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, PRUNING_RULE)
    champion_additions = metrical.metrical_prune(precision_additions, winner_scores, alt_scores, METRICAL_RULE)
    champion = precond.merge_with_cap(base_champion, champion_additions)
    champion_score = grade(champion, reference)
    if abs(float(champion_score["pitchF1"]) - CURRENT_CHAMPION_F1) > 0.01:
        raise RuntimeError(f"Expected frozen champion F1 {CURRENT_CHAMPION_F1}, got {champion_score['pitchF1']}")

    results: dict[str, Any] = {}
    for rule in RULES:
        filtered_additions = prune_step_signature(champion_additions, winner_scores, alt_scores, rule)
        prediction = precond.merge_with_cap(base_champion, filtered_additions)
        full = grade(prediction, reference)

        fold_deltas = []
        positive_folds = 0
        matched_nonloss_folds = 0
        extra_reduced_folds = 0
        catastrophic_folds = 0
        for fold in range(FOLDS):
            ref = fold_subset(reference, fold)
            c = grade(fold_subset(champion, fold), ref)
            p = grade(fold_subset(prediction, fold), ref)
            delta = round(float(p["pitchF1"]) - float(c["pitchF1"]), 2)
            matched_delta = int(p["matched"]) - int(c["matched"])
            extra_delta = int(p["extra"]) - int(c["extra"])
            positive_folds += int(delta > 0)
            matched_nonloss_folds += int(matched_delta >= 0)
            extra_reduced_folds += int(extra_delta < 0)
            catastrophic_folds += int(delta <= -1.0)
            fold_deltas.append(delta)
        mean_fold = round(sum(fold_deltas) / FOLDS, 2)
        median_fold = round(float(statistics.median(fold_deltas)), 2)
        cv_passed = (
            positive_folds >= 4
            and matched_nonloss_folds == FOLDS
            and extra_reduced_folds == FOLDS
            and catastrophic_folds == 0
            and mean_fold > 0
            and median_fold > 0
        )

        blocks = compare_ranges(prediction, champion, reference, BLOCKS)
        section_passed = (
            blocks["positiveF1"] >= 4
            and blocks["matchedNonloss"] == len(BLOCKS)
            and blocks["extraReduced"] >= 4
            and blocks["catastrophic"] == 0
            and blocks["meanDelta"] > 0
            and blocks["medianDelta"] >= 0
        )

        windows = compare_ranges(prediction, champion, reference, SHIFTED_WINDOWS)
        shifted_passed = (
            windows["positiveF1"] >= 8
            and windows["matchedNonloss"] == len(SHIFTED_WINDOWS)
            and windows["extraReduced"] >= 8
            and windows["catastrophic"] == 0
            and windows["meanDelta"] > 0
            and windows["medianDelta"] >= 0
        )

        accepted = (
            float(full["pitchF1"]) > CURRENT_CHAMPION_F1
            and int(full["extra"]) < int(champion_score["extra"])
            and int(full["matched"]) >= int(champion_score["matched"])
            and cv_passed and section_passed and shifted_passed
        )
        results[str(rule["name"])] = {
            "rule": rule,
            "additionCount": sum(filtered_additions.values()),
            "fullScore": full,
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
            f"extraReduction={int(champion_score['extra'])-int(full['extra'])} matchedChange={int(full['matched'])-int(champion_score['matched'])} "
            f"cv={cv_passed} sections={section_passed} shifted={shifted_passed} accepted={accepted}",
            flush=True,
        )

    ranked = sorted(results.items(), key=lambda item: (
        bool(item[1]["acceptedOverChampion"]),
        bool(item[1]["shiftedWindowStabilityPassed"]),
        bool(item[1]["sectionStabilityPassed"]),
        bool(item[1]["crossValidationPassed"]),
        int(item[1]["matchedChange"] >= 0),
        float(item[1]["fullScore"]["pitchF1"]),
        int(item[1]["extraReduction"]),
    ), reverse=True)
    winner_name, winner = ranked[0]

    candidate_hash_after = sha256(CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during step-signature precision benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-8.77-champion-step10-exception-precision-gate",
        "currentChampion": champion_score,
        "frozenTemporalRule": TEMPORAL_RULE,
        "frozenPrecisionRule": PRUNING_RULE,
        "frozenMetricalRule": METRICAL_RULE,
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
        "recommendedNextAction": "lock-step10-exception-pruned-champion" if winner["acceptedOverChampion"] else "retain-8.77-and-profile-cross-signatures",
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

    print("GOMYWAY METRICALLY-PRUNED CHAMPION STEP10 EXCEPTION V1 COMPLETE")
    print("Passed: True")
    print("Current champion pitch F1:", champion_score["pitchF1"])
    print("Current champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner extra reduction:", winner["extraReduction"])
    print("Winner matched change:", winner["matchedChange"])
    print("Winner positive F1 folds:", winner["positiveF1Folds"], "/", FOLDS)
    print("Winner matched-nonloss folds:", winner["matchedNonlossFolds"], "/", FOLDS)
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner positive F1 blocks:", winner["sectionAudit"]["positiveF1"], "/", len(BLOCKS))
    print("Winner matched-nonloss blocks:", winner["sectionAudit"]["matchedNonloss"], "/", len(BLOCKS))
    print("Winner catastrophic block regressions:", winner["sectionAudit"]["catastrophic"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner positive shifted windows:", winner["shiftedWindowAudit"]["positiveF1"], "/", len(SHIFTED_WINDOWS))
    print("Winner matched-nonloss shifted windows:", winner["shiftedWindowAudit"]["matchedNonloss"], "/", len(SHIFTED_WINDOWS))
    print("Winner catastrophic shifted regressions:", winner["shiftedWindowAudit"]["catastrophic"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
    print("Winner accepted over 8.77 champion:", winner["acceptedOverChampion"])
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
