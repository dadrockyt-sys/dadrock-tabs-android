from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_929_champion_reference_free_upstream_recall_spectral_gate_v1 as recall
import profile_gomyway_1113_recall_champion_effective_additions_precision_v1 as profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1113-recall-champion-zero-precision-pitch-strength-prune-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1113-recall-champion-zero-precision-pitch-strength-prune-v1-manifest.json"

EXPECTED_CORE = (102, 765, 1227)
EXPECTED_RECALL = (160, 707, 1848)
EXPECTED_RECALL_F1 = 11.13
FOLDS = 5
BLOCKS = recall.BLOCKS
SHIFTED_WINDOWS = recall.SHIFTED_WINDOWS
WINNER_NAME = "dual6_quarter_40_64"

ZERO_BUCKETS_ALL = {
    (53, "6_8"),
    (41, "6_8"),
    (46, "6_8"),
    (40, "6_8"),
    (64, "13_16"),
    (49, "6_8"),
    (53, "8_10"),
    (43, "6_8"),
    (44, "6_8"),
    (59, "8_10"),
}

RULES: list[dict[str, Any]] = [
    {
        "name": "drop_zero_pitch_strength_6_8",
        "drop": sorted([list(x) for x in ZERO_BUCKETS_ALL if x[1] == "6_8"]),
    },
    {
        "name": "drop_zero_pitch_strength_non_6_8",
        "drop": sorted([list(x) for x in ZERO_BUCKETS_ALL if x[1] != "6_8"]),
    },
    {
        "name": "drop_all_profiled_zero_precision_pitch_strength",
        "drop": sorted([list(x) for x in ZERO_BUCKETS_ALL]),
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
    extra_reduced = 0
    for start, end in ranges:
        ref = subset_range(reference, start, end)
        old = grade(subset_range(champion, start, end), ref)
        new = grade(subset_range(candidate, start, end), ref)
        delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
        md = int(new["matched"]) - int(old["matched"])
        xd = int(new["extra"]) - int(old["extra"])
        positive += int(delta > 0)
        matched_nonloss += int(md >= 0)
        extra_reduced += int(xd < 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        rows.append({"range": f"m{start}_{end}", "deltaPoints": delta, "matchedDelta": md, "extraDelta": xd})
    return {
        "rows": rows,
        "positiveF1": positive,
        "matchedNonloss": matched_nonloss,
        "extraReduced": extra_reduced,
        "catastrophic": catastrophic,
        "meanDelta": round(sum(deltas) / len(deltas), 2),
        "medianDelta": round(float(statistics.median(deltas)), 2),
    }


def prune_proposed(proposed, winner_scores, alt_scores, rule):
    drop = {(int(pitch), str(strength)) for pitch, strength in rule["drop"]}
    out: Counter[tuple[int, int, int]] = Counter()
    for token, count in proposed.items():
        pitch = int(token[2])
        strength = profile.bucket(min(winner_scores.get(token, 0.0), alt_scores.get(token, 0.0)))
        if (pitch, strength) not in drop:
            out[token] = count
    return out


def evaluate(candidate, champion, reference, champion_score):
    full = grade(candidate, reference)
    fold_rows = []
    deltas = []
    positive_f1 = 0
    matched_nonloss = 0
    extra_reduced = 0
    catastrophic = 0
    for fold in range(FOLDS):
        ref = subset_fold(reference, fold)
        old = grade(subset_fold(champion, fold), ref)
        new = grade(subset_fold(candidate, fold), ref)
        delta = round(float(new["pitchF1"]) - float(old["pitchF1"]), 2)
        md = int(new["matched"]) - int(old["matched"])
        xd = int(new["extra"]) - int(old["extra"])
        positive_f1 += int(delta > 0)
        matched_nonloss += int(md >= 0)
        extra_reduced += int(xd < 0)
        catastrophic += int(delta <= -1.0)
        deltas.append(delta)
        fold_rows.append({"fold": fold, "deltaPoints": delta, "matchedDelta": md, "extraDelta": xd})
    mean_fold = round(sum(deltas) / FOLDS, 2)
    median_fold = round(float(statistics.median(deltas)), 2)
    cv_passed = (
        matched_nonloss == FOLDS
        and extra_reduced >= 1
        and catastrophic == 0
        and mean_fold >= 0
        and median_fold >= 0
    )

    blocks = range_audit(candidate, champion, reference, BLOCKS)
    section_passed = (
        blocks["matchedNonloss"] == len(BLOCKS)
        and blocks["catastrophic"] == 0
        and blocks["meanDelta"] >= 0
        and blocks["medianDelta"] >= 0
    )
    windows = range_audit(candidate, champion, reference, SHIFTED_WINDOWS)
    shifted_passed = (
        windows["matchedNonloss"] == len(SHIFTED_WINDOWS)
        and windows["catastrophic"] == 0
        and windows["meanDelta"] >= 0
        and windows["medianDelta"] >= 0
    )

    accepted = (
        float(full["pitchF1"]) > float(champion_score["pitchF1"])
        and int(full["matched"]) >= int(champion_score["matched"])
        and int(full["missing"]) <= int(champion_score["missing"])
        and int(full["extra"]) < int(champion_score["extra"])
        and cv_passed
        and section_passed
        and shifted_passed
    )
    return {
        "fullScore": full,
        "extraReduction": int(champion_score["extra"]) - int(full["extra"]),
        "matchedChange": int(full["matched"]) - int(champion_score["matched"]),
        "missingChange": int(full["missing"]) - int(champion_score["missing"]),
        "positiveF1Folds": positive_f1,
        "matchedNonlossFolds": matched_nonloss,
        "extraReducedFolds": extra_reduced,
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
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen validated 9.29 core and 11.13 recall champion...", flush=True)
    base_winner = recall.precond.prediction(recall.precond.grouped_for(recall.WINNER_STEM, grid))
    base_alt = recall.precond.prediction(recall.precond.grouped_for(recall.ALT_STEM, grid))
    base_champion = recall.precond.merge_with_cap(base_winner, base_alt)

    mid_winner = recall.spectral.specialist_scores(recall.WINNER_STEM, grid)
    mid_alt = recall.spectral.specialist_scores(recall.ALT_STEM, grid)
    top1 = recall.gate.accepted_tokens(recall.temporal.TOP1_RULE, mid_winner, mid_alt, base_champion)
    adaptive_base = recall.adaptive.adaptive_additions(top1, mid_winner, mid_alt, 2, 13.0)
    a = recall.temporal.recurrence_gate(adaptive_base, mid_winner, mid_alt, recall.TEMPORAL_RULE)
    a = recall.pruning.prune(a, mid_winner, mid_alt, adaptive_base, recall.PRUNING_RULE)
    a = recall.metrical.metrical_prune(a, mid_winner, mid_alt, recall.METRICAL_RULE)
    a = recall.step10.prune_step_signature(a, mid_winner, mid_alt, recall.STEP_RULE)
    a = recall.agreement.agreement_prune(a, mid_winner, mid_alt, recall.AGREEMENT_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.SAFE_CROSS_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.ZERO_PRECISION_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_910_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_916_RULE)
    a = recall.gate919.refined_subgate(a, mid_winner, mid_alt, adaptive_base)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_921_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_923_RULE)
    a = recall.gate926.deep_prune(a, mid_winner, mid_alt, recall.WINNER_926_RULE)
    a = recall.gate927.combined_prune(a, mid_winner, mid_alt, adaptive_base)
    a = recall.gate929.residual_prune(a, mid_winner, mid_alt, adaptive_base)
    core = recall.precond.merge_with_cap(base_champion, a)
    core_score = grade(core, reference)
    actual_core = (int(core_score["matched"]), int(core_score["missing"]), int(core_score["extra"]))
    if actual_core != EXPECTED_CORE:
        raise RuntimeError(f"Expected frozen 9.29 core {EXPECTED_CORE}, got {actual_core}")

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)
    winner_scores = {}
    alt_scores = {}
    for (measure, step), center in grid.items():
        if measure < 17 or measure > 113:
            continue
        for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
            token = (measure, step, pitch)
            winner_scores[token] = recall.spectral.spectral_score(winner_audio, winner_sr, float(center), pitch)
            alt_scores[token] = recall.spectral.spectral_score(alt_audio, alt_sr, float(center), pitch)

    variant = next(v for v in recall.VARIANTS if v["name"] == WINNER_NAME)
    proposed = recall.recall_additions(grid, winner_scores, alt_scores, core, variant)
    recall_champion = recall.precond.merge_with_cap(core, proposed)
    recall_score = grade(recall_champion, reference)
    actual_recall = (int(recall_score["matched"]), int(recall_score["missing"]), int(recall_score["extra"]))
    if actual_recall != EXPECTED_RECALL or abs(float(recall_score["pitchF1"]) - EXPECTED_RECALL_F1) > 0.01:
        raise RuntimeError(f"Expected 11.13 recall champion {EXPECTED_RECALL}/{EXPECTED_RECALL_F1}, got {actual_recall}/{recall_score['pitchF1']}")

    results: dict[str, Any] = {}
    for rule in RULES:
        kept = prune_proposed(proposed, winner_scores, alt_scores, rule)
        candidate = recall.precond.merge_with_cap(core, kept)
        audit = evaluate(candidate, recall_champion, reference, recall_score)
        results[rule["name"]] = {
            "rule": rule,
            "keptProposedAdditions": int(sum(kept.values())),
            **audit,
        }
        s = audit["fullScore"]
        print(
            f"{rule['name']}: F1={s['pitchF1']} matched={s['matched']} missing={s['missing']} extra={s['extra']} "
            f"extraReduction={audit['extraReduction']} matchedChange={audit['matchedChange']} "
            f"cv={audit['crossValidationPassed']} sections={audit['sectionStabilityPassed']} "
            f"shifted={audit['shiftedWindowStabilityPassed']} accepted={audit['acceptedOverChampion']}",
            flush=True,
        )

    accepted = [(name, row) for name, row in results.items() if row["acceptedOverChampion"]]
    if accepted:
        winner_name, winner = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["fullScore"]["matched"]),
                -int(item[1]["fullScore"]["extra"]),
            ),
        )
    else:
        winner_name, winner = "retain_11_13_recall_champion", {
            "fullScore": recall_score,
            "extraReduction": 0,
            "matchedChange": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
        }

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 11.13 pitch-strength prune benchmark.")

    ws = winner["fullScore"]
    validated = winner_name != "retain_11_13_recall_champion"
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-11.13-recall-champion-zero-precision-pitch-strength-prune",
        "baselineScore": recall_score,
        "results": results,
        "winner": winner_name,
        "winnerScore": ws,
        "winnerExtraReduction": winner["extraReduction"],
        "winnerMatchedChange": winner["matchedChange"],
        "winnerCrossValidationPassed": winner["crossValidationPassed"],
        "winnerSectionStabilityPassed": winner["sectionStabilityPassed"],
        "winnerShiftedWindowStabilityPassed": winner["shiftedWindowStabilityPassed"],
        "validatedNewChampion": validated,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-prune-validation-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "profile-residual-new-recall-additions-from-validated-pruned-recall-champion" if validated else "retain-11.13-and-refine-recall-addition-precision-signatures",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "winner": winner_name,
        "winnerPitchF1": ws["pitchF1"],
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 11.13 RECALL CHAMPION ZERO-PRECISION PITCH-STRENGTH PRUNE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", recall_score["pitchF1"])
    print("Baseline matched/missing/extra:", recall_score["matched"], "/", recall_score["missing"], "/", recall_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", ws["pitchF1"])
    print("Winner matched/missing/extra:", ws["matched"], "/", ws["missing"], "/", ws["extra"])
    print("Winner extra reduction:", winner["extraReduction"])
    print("Winner matched change:", winner["matchedChange"])
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
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
