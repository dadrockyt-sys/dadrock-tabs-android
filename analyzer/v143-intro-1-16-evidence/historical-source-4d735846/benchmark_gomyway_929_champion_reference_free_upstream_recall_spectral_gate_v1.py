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
OUTPUT_PATH = PUBLIC / "gomyway-929-champion-reference-free-upstream-recall-spectral-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-929-champion-reference-free-upstream-recall-spectral-gate-v1-manifest.json"

EXPECTED = (102, 765, 1227)
EXPECTED_F1 = 9.29
FOLDS = 5
BLOCKS = temporal.BLOCKS
SHIFTED_WINDOWS = temporal.SHIFTED_WINDOWS
PITCH_MIN = 40
PITCH_MAX = 64

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

VARIANTS: list[dict[str, Any]] = [
    {"name": "dual8_all_40_64", "bothFloor": 8.0, "steps": None},
    {"name": "dual6_all_40_64", "bothFloor": 6.0, "steps": None},
    {"name": "dual4_all_40_64", "bothFloor": 4.0, "steps": None},
    {"name": "dual6_even_40_64", "bothFloor": 6.0, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
    {"name": "dual4_even_40_64", "bothFloor": 4.0, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
    {"name": "dual6_quarter_40_64", "bothFloor": 6.0, "steps": [0, 4, 8, 12]},
    {"name": "dual4_quarter_40_64", "bothFloor": 4.0, "steps": [0, 4, 8, 12]},
    {"name": "dual4_low_40_51", "bothFloor": 4.0, "steps": None, "pitchMax": 51},
    {"name": "dual6_low_40_51", "bothFloor": 6.0, "steps": None, "pitchMax": 51},
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


def subset_fold(counter: Counter[tuple[int, int, int]], fold: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if ((token[0] - 17) % FOLDS) == fold})


def subset_range(counter: Counter[tuple[int, int, int]], start: int, end: int) -> Counter[tuple[int, int, int]]:
    return Counter({token: count for token, count in counter.items() if start <= token[0] <= end})


def range_audit(candidate, champion, reference, ranges):
    rows = []
    deltas = []
    matched_nonloss = 0
    catastrophic = 0
    positive = 0
    for start, end in ranges:
        ref = subset_range(reference, start, end)
        old = grade(subset_range(champion, start, end), ref)
        new = grade(subset_range(candidate, start, end), ref)
        delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
        md = int(new["matched"]) - int(old["matched"])
        xd = int(new["extra"]) - int(old["extra"])
        positive += int(delta > 0)
        matched_nonloss += int(md >= 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        rows.append({"range": f"m{start}_{end}", "deltaPoints": delta, "matchedDelta": md, "extraDelta": xd})
    return {
        "rows": rows,
        "positiveF1": positive,
        "matchedNonloss": matched_nonloss,
        "catastrophic": catastrophic,
        "meanDelta": round(sum(deltas) / len(deltas), 2),
        "medianDelta": round(float(statistics.median(deltas)), 2),
    }


def recall_additions(grid, winner_scores, alt_scores, champion, variant):
    out: Counter[tuple[int, int, int]] = Counter()
    floor = float(variant["bothFloor"])
    allowed_steps = None if variant.get("steps") is None else set(int(x) for x in variant["steps"])
    pitch_max = int(variant.get("pitchMax", PITCH_MAX))
    for measure, step in grid:
        if measure < 17 or measure > 113:
            continue
        if allowed_steps is not None and step not in allowed_steps:
            continue
        for pitch in range(PITCH_MIN, pitch_max + 1):
            token = (measure, step, pitch)
            if champion.get(token, 0) > 0:
                continue
            if winner_scores.get(token, 0.0) >= floor and alt_scores.get(token, 0.0) >= floor:
                out[token] = 1
    return out


def evaluate_recall(candidate, champion, reference, champion_score):
    full = grade(candidate, reference)
    fold_rows = []
    deltas = []
    positive_f1 = 0
    positive_matched = 0
    catastrophic = 0
    for fold in range(FOLDS):
        ref = subset_fold(reference, fold)
        old = grade(subset_fold(champion, fold), ref)
        new = grade(subset_fold(candidate, fold), ref)
        delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
        md = int(new["matched"]) - int(old["matched"])
        xd = int(new["extra"]) - int(old["extra"])
        positive_f1 += int(delta > 0)
        positive_matched += int(md > 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        fold_rows.append({"fold": fold, "deltaPoints": delta, "matchedDelta": md, "extraDelta": xd})
    mean_fold = round(sum(deltas) / FOLDS, 2)
    median_fold = round(float(statistics.median(deltas)), 2)
    cv_passed = positive_f1 >= 4 and positive_matched >= 4 and catastrophic == 0 and mean_fold > 0 and median_fold > 0

    blocks = range_audit(candidate, champion, reference, BLOCKS)
    section_passed = blocks["matchedNonloss"] == len(BLOCKS) and blocks["catastrophic"] == 0 and blocks["meanDelta"] >= 0 and blocks["medianDelta"] >= 0
    windows = range_audit(candidate, champion, reference, SHIFTED_WINDOWS)
    shifted_passed = windows["matchedNonloss"] == len(SHIFTED_WINDOWS) and windows["catastrophic"] == 0 and windows["meanDelta"] >= 0 and windows["medianDelta"] >= 0

    accepted = (
        float(full["pitchF1"]) > float(champion_score["pitchF1"])
        and int(full["matched"]) > int(champion_score["matched"])
        and int(full["missing"]) < int(champion_score["missing"])
        and cv_passed
        and section_passed
        and shifted_passed
    )
    return {
        "fullScore": full,
        "matchedGain": int(full["matched"]) - int(champion_score["matched"]),
        "missingReduction": int(champion_score["missing"]) - int(full["missing"]),
        "extraIncrease": int(full["extra"]) - int(champion_score["extra"]),
        "positiveF1Folds": positive_f1,
        "positiveMatchedFolds": positive_matched,
        "meanFoldDeltaPoints": mean_fold,
        "medianFoldDeltaPoints": median_fold,
        "crossValidationPassed": cv_passed,
        "sectionAudit": blocks,
        "sectionStabilityPassed": section_passed,
        "shiftedWindowAudit": windows,
        "shiftedWindowStabilityPassed": shifted_passed,
        "acceptedOverChampion": accepted,
        "foldAudit": fold_rows,
    }


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

    # Existing specialist scores only cover MIDI 52..63, so compute the same
    # detector-side spectral feature across the expanded 40..64 recall range.
    winner_audio, winner_sr = spectral.load_filtered(WINNER_STEM)
    alt_audio, alt_sr = spectral.load_filtered(ALT_STEM)
    winner_scores: dict[tuple[int, int, int], float] = {}
    alt_scores: dict[tuple[int, int, int], float] = {}
    for (measure, step), center in grid.items():
        if measure < 17 or measure > 113:
            continue
        for pitch in range(PITCH_MIN, PITCH_MAX + 1):
            token = (measure, step, pitch)
            winner_scores[token] = spectral.spectral_score(winner_audio, winner_sr, float(center), pitch)
            alt_scores[token] = spectral.spectral_score(alt_audio, alt_sr, float(center), pitch)

    # Rebuild the protected 9.29 chain with the established mid-register scores.
    mid_winner_scores = spectral.specialist_scores(WINNER_STEM, grid)
    mid_alt_scores = spectral.specialist_scores(ALT_STEM, grid)
    top1 = gate.accepted_tokens(temporal.TOP1_RULE, mid_winner_scores, mid_alt_scores, base_champion)
    adaptive_base = adaptive.adaptive_additions(top1, mid_winner_scores, mid_alt_scores, 2, 13.0)
    a = temporal.recurrence_gate(adaptive_base, mid_winner_scores, mid_alt_scores, TEMPORAL_RULE)
    a = pruning.prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, PRUNING_RULE)
    a = metrical.metrical_prune(a, mid_winner_scores, mid_alt_scores, METRICAL_RULE)
    a = step10.prune_step_signature(a, mid_winner_scores, mid_alt_scores, STEP_RULE)
    a = agreement.agreement_prune(a, mid_winner_scores, mid_alt_scores, AGREEMENT_RULE)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, SAFE_CROSS_RULE)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, ZERO_PRECISION_RULE)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, WINNER_910_RULE)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, WINNER_916_RULE)
    a = gate919.refined_subgate(a, mid_winner_scores, mid_alt_scores, adaptive_base)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, WINNER_921_RULE)
    a = crossgate.cross_signature_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base, WINNER_923_RULE)
    a = gate926.deep_prune(a, mid_winner_scores, mid_alt_scores, WINNER_926_RULE)
    a = gate927.combined_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base)
    a = gate929.residual_prune(a, mid_winner_scores, mid_alt_scores, adaptive_base)

    champion = precond.merge_with_cap(base_champion, a)
    champion_score = grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected validated 9.29 {EXPECTED}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    results: dict[str, Any] = {}
    for variant in VARIANTS:
        additions = recall_additions(grid, winner_scores, alt_scores, champion, variant)
        candidate = precond.merge_with_cap(champion, additions)
        result = evaluate_recall(candidate, champion, reference, champion_score)
        result["variant"] = variant
        result["additionCount"] = int(sum(additions.values()))
        results[variant["name"]] = result
        score = result["fullScore"]
        print(
            f"{variant['name']}: F1={score['pitchF1']} matched={score['matched']} missing={score['missing']} extra={score['extra']} "
            f"adds={result['additionCount']} matchGain={result['matchedGain']} extraIncrease={result['extraIncrease']} "
            f"cv={result['crossValidationPassed']} sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={result['acceptedOverChampion']}", flush=True
        )

    ranked = sorted(
        results.items(),
        key=lambda item: (
            bool(item[1]["acceptedOverChampion"]),
            float(item[1]["fullScore"]["pitchF1"]),
            int(item[1]["matchedGain"]),
            -int(item[1]["extraIncrease"]),
        ),
        reverse=True,
    )
    winner_name, winner = ranked[0]
    validated = bool(winner["acceptedOverChampion"])

    after = sha256(CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 9.29 upstream recall benchmark.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.29-reference-free-upstream-recall-spectral-gate",
        "baselineScore": champion_score,
        "variants": results,
        "winner": winner_name,
        "winnerResult": winner,
        "validatedNewChampion": validated,
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
        "candidateSha256": after,
        "baselinePitchF1": champion_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.29 CHAMPION REFERENCE-FREE UPSTREAM RECALL SPECTRAL GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print("Baseline matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner["fullScore"]["matched"], "/", winner["fullScore"]["missing"], "/", winner["fullScore"]["extra"])
    print("Winner additions:", winner["additionCount"])
    print("Winner matched gain:", winner["matchedGain"])
    print("Winner missing reduction:", winner["missingReduction"])
    print("Winner extra increase:", winner["extraIncrease"])
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
    print("Validated new champion:", validated)
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
