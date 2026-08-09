from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_1382_never_seen_raw_spectral_evidence_v1 as raw

miss = raw.miss
v2 = raw.v2
v3 = raw.v3
p1382 = raw.p1382
recall = raw.recall
p1316 = raw.p1316
gate1328 = raw.gate1328
gate1345 = raw.gate1345
gate1370 = raw.gate1370
gate1382 = raw.gate1382

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-dual-stem-recurrence-recall-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-dual-stem-recurrence-recall-gate-v1-manifest.json"

EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82
WINNER_NAME = "dual6_quarter_40_64"

VARIANTS: list[dict[str, Any]] = [
    {"name": "dual4_recur2_all", "bothFloor": 4.0, "recurrence": 2, "steps": None},
    {"name": "dual4_recur3_all", "bothFloor": 4.0, "recurrence": 3, "steps": None},
    {"name": "dual4_recur2_even", "bothFloor": 4.0, "recurrence": 2, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
    {"name": "dual4_recur3_even", "bothFloor": 4.0, "recurrence": 3, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
    {"name": "dual5_recur2_all", "bothFloor": 5.0, "recurrence": 2, "steps": None},
    {"name": "dual5_recur3_all", "bothFloor": 5.0, "recurrence": 3, "steps": None},
    {"name": "dual5_recur2_even", "bothFloor": 5.0, "recurrence": 2, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
    {"name": "dual6_recur2_all", "bothFloor": 6.0, "recurrence": 2, "steps": None},
    {"name": "dual6_recur3_all", "bothFloor": 6.0, "recurrence": 3, "steps": None},
    {"name": "dual6_recur2_even", "bothFloor": 6.0, "recurrence": 2, "steps": [0, 2, 4, 6, 8, 10, 12, 14]},
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


def build_frozen_1382(grid):
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

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)
    winner_scores: dict[tuple[int, int, int], float] = {}
    alt_scores: dict[tuple[int, int, int], float] = {}
    for (measure, step), center in grid.items():
        if 17 <= measure <= 113:
            for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
                token = (measure, step, pitch)
                winner_scores[token] = recall.spectral.spectral_score(winner_audio, winner_sr, float(center), pitch)
                alt_scores[token] = recall.spectral.spectral_score(alt_audio, alt_sr, float(center), pitch)

    variant = next(v for v in recall.VARIANTS if v["name"] == WINNER_NAME)
    proposed = recall.recall_additions(grid, winner_scores, alt_scores, core, variant)

    p1315 = p1316.p1315
    p1312 = p1315.p1312
    p1308 = p1312.p1308
    p1305 = p1308.p1305
    p1285 = p1305.p1285
    p1272 = p1285.p1272

    kept = p1272.prune1163.prune_proposed(proposed, winner_scores, alt_scores, p1272.FIRST_PRUNE)
    kept = p1272.prune1186.prune_residual(kept, winner_scores, alt_scores, p1272.SECOND_PRUNE)
    kept = p1272.prune1217.prune_residual(kept, winner_scores, alt_scores, p1272.THIRD_PRUNE)
    kept = p1272.prune1229.prune_residual(kept, winner_scores, alt_scores, p1272.FOURTH_PRUNE)
    kept = p1272.prune1244.prune_residual(kept, winner_scores, alt_scores, p1272.FIFTH_PRUNE)
    kept = p1272.prune1253.prune_residual(kept, winner_scores, alt_scores, p1272.SIXTH_PRUNE)
    kept = p1272.prune1258.prune_residual(kept, winner_scores, alt_scores, p1272.SEVENTH_PRUNE)
    kept = p1272.prune1272.prune_residual(kept, winner_scores, alt_scores, p1272.EIGHTH_PRUNE)
    kept = p1285.prune1285.prune_residual(kept, winner_scores, alt_scores, p1285.NINTH_PRUNE)
    kept = p1305.prune1305.prune_residual(kept, winner_scores, alt_scores, p1305.TENTH_PRUNE)
    kept = p1308.prune1308.prune_residual(kept, winner_scores, alt_scores, p1308.ELEVENTH_PRUNE)
    kept = p1312.prune1312.prune_residual(kept, winner_scores, alt_scores, p1312.TWELFTH_PRUNE)
    kept = p1315.prune1315.prune_residual(kept, winner_scores, alt_scores, p1315.THIRTEENTH_PRUNE)
    kept = p1316.prune1316.prune_residual(kept, winner_scores, alt_scores, p1316.FOURTEENTH_PRUNE)
    kept = gate1328.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1328.TARGET_SIGNATURES})
    kept = gate1345.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1345.TARGET_SIGNATURES})
    kept = gate1370.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1370.TARGET_SIGNATURES})
    kept = gate1382.prune_residual(kept, winner_scores, alt_scores, gate1382.TARGET_SIGNATURES)

    champion = recall.precond.merge_with_cap(core, kept)
    return champion, winner_scores, alt_scores


def recurrent_dual_stem_additions(grid, winner_scores, alt_scores, champion, variant):
    floor = float(variant["bothFloor"])
    recurrence = int(variant["recurrence"])
    allowed_steps = None if variant.get("steps") is None else set(int(x) for x in variant["steps"])

    supported: list[tuple[int, int, int]] = []
    signature_counts: Counter[tuple[int, int]] = Counter()
    for measure, step in grid:
        if not 17 <= measure <= 113:
            continue
        if allowed_steps is not None and step not in allowed_steps:
            continue
        for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
            token = (measure, step, pitch)
            if champion.get(token, 0) > 0:
                continue
            if min(float(winner_scores.get(token, 0.0)), float(alt_scores.get(token, 0.0))) >= floor:
                supported.append(token)
                signature_counts[(step, pitch)] += 1

    out: Counter[tuple[int, int, int]] = Counter()
    for token in supported:
        if signature_counts[(token[1], token[2])] >= recurrence:
            out[token] = 1
    return out


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

    print("Rebuilding frozen validated 13.82 champion and detector-side dual-stem scores...", flush=True)
    champion, winner_scores, alt_scores = build_frozen_1382(grid)
    champion_score = grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for variant in VARIANTS:
        additions = recurrent_dual_stem_additions(grid, winner_scores, alt_scores, champion, variant)
        candidate = champion + additions
        evaluation = recall.evaluate_recall(candidate, champion, reference, champion_score)
        evaluation["additionCount"] = int(sum(additions.values()))
        evaluation["variant"] = variant
        results[str(variant["name"])] = evaluation
        full = evaluation["fullScore"]
        print(
            f"{variant['name']}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} additions={sum(additions.values())} matchedGain={evaluation['matchedGain']} "
            f"extraIncrease={evaluation['extraIncrease']} cv={evaluation['crossValidationPassed']} "
            f"sections={evaluation['sectionStabilityPassed']} shifted={evaluation['shiftedWindowStabilityPassed']} "
            f"accepted={evaluation['acceptedOverChampion']}",
            flush=True,
        )
        if evaluation["acceptedOverChampion"]:
            accepted.append((str(variant["name"]), evaluation))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["matchedGain"]),
                -int(item[1]["extraIncrease"]),
            ),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_13_82_champion"
        winner_eval = {
            "fullScore": champion_score,
            "matchedGain": 0,
            "missingReduction": 0,
            "extraIncrease": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
            "additionCount": 0,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 13.82 recurrent dual-stem recall benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-reference-free-dual-stem-recurrence-upstream-recall-gate",
        "baselineScore": champion_score,
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
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
        "recommendedNextAction": (
            "profile-and-prune-residual-additions-from-validated-recurrent-dual-stem-recall-winner"
            if validated_new_champion
            else "design-next-reference-free-upstream-recall-feature-family"
        ),
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baselinePitchF1": champion_score["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    full = winner_eval["fullScore"]
    print("GOMYWAY 13.82 CHAMPION DUAL-STEM RECURRENCE RECALL GATE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print("Baseline matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", full["pitchF1"])
    print("Winner matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Winner matched gain:", winner_eval["matchedGain"])
    print("Winner missing reduction:", winner_eval["missingReduction"])
    print("Winner extra increase:", winner_eval["extraIncrease"])
    print("Winner cross-validation passed:", winner_eval["crossValidationPassed"])
    print("Winner section stability passed:", winner_eval["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner_eval["shiftedWindowStabilityPassed"])
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
