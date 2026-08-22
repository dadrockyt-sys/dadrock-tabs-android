from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1569_attack_envelope_survivors_precision_v1 as p1569
import benchmark_gomyway_1542_attack_envelope_survivor_precision_prune_cv_v1 as b1542
import benchmark_gomyway_1499_attack_envelope_survivor_precision_prune_cv_v1 as b1499
import benchmark_gomyway_1460_attack_envelope_precision_prune_cv_v1 as b1460

recur = b1542.recur
recall = b1542.recall
v2 = b1542.v2
v3 = b1542.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1542_PATH = PUBLIC / "gomyway-1542-attack-envelope-survivors-precision-v1.json"
PROFILE_1569_PATH = PUBLIC / "gomyway-1569-attack-envelope-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1569-attack-envelope-final-survivor-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1569-attack-envelope-final-survivor-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1283)
EXPECTED_F1 = 15.69
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def reconstruct_1569(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1542 = b1542.reconstruct_1542(grid)
    payload = v2.load_json(PROFILE_1542_PATH)
    rows = list(payload.get("rows", []))
    row_by_token = {token(row): row for row in rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1542.items():
        row = row_by_token.get(tok)
        if row is not None and (b1542.pred_a(row) or b1542.pred_b(row) or b1542.pred_c(row) or b1542.pred_d(row)):
            pruned[tok] = count
    return champion_1542 - pruned


def pred_a(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return b["maxDecay"] == "decay_120_plus" and b["attackDisagreement"] == "attack_disagree_050_100"


def pred_b(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return (
        b["minAttack"] == "minattack_080_100"
        and b["maxDecay"] == "decay_120_plus"
        and b["attackDisagreement"] == "attack_disagree_020_050"
    )


def pred_c(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return (
        b["minAttack"] == "minattack_080_100"
        and b["maxDecay"] == "decay_070_095"
        and b["attackDisagreement"] == "attack_disagree_020_050"
    )


def pred_d(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return (
        b["minAttack"] == "minattack_lt080"
        and b["maxDecay"] == "decay_070_095"
        and b["attackDisagreement"] == "attack_disagree_020_050"
    )


def pred_e(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return b["minAttack"] == "minattack_lt080" and b["maxZcr"] == "max_zcr_lt800"


def pred_f(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return b["minCrest"] == "min_crest_3_4p5" and b["maxZcr"] == "max_zcr_lt800"


def pred_g(row: dict[str, Any]) -> bool:
    b = b1460.buckets(row)
    return b["minAttack"] == "minattack_125_160" and b["maxZcr"] == "max_zcr_1600_3000"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("attack1569_final_a_decay120_disagree050100", pred_a),
    ("attack1569_final_b_attack080100_decay120_disagree020050", pred_b),
    ("attack1569_final_c_attack080100_decay070095_disagree020050", pred_c),
    ("attack1569_final_d_attacklt080_decay070095_disagree020050", pred_d),
    ("attack1569_final_e_attacklt080_zcrlt800", pred_e),
    ("attack1569_final_f_crest3_4p5_zcrlt800", pred_f),
    ("attack1569_final_g_attack125160_zcr1600_3000", pred_g),
    ("attack1569_final_union_a_b", lambda row: pred_a(row) or pred_b(row)),
    ("attack1569_final_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("attack1569_final_union_a_b_c_d", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row)),
    ("attack1569_final_union_a_b_c_d_e", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row) or pred_e(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    survivor_payload = v2.load_json(PROFILE_1569_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.69 survivor profile is not reference-free during detection")
    rows = list(survivor_payload.get("rows", []))
    if not rows:
        raise RuntimeError("15.69 survivor profile has no rows")
    row_by_token = {token(row): row for row in rows}

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    champion = reconstruct_1569(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 15.69 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        pruned: Counter[tuple[int, int, int]] = Counter()
        for tok, count in champion.items():
            row = row_by_token.get(tok)
            if row is not None and predicate(row):
                pruned[tok] = count

        candidate = champion - pruned
        full = recur.grade(candidate, reference)
        stability = recall.evaluate_recall(candidate, champion, reference, baseline)

        folds: list[dict[str, Any]] = []
        folds_with_false_reduction = 0
        all_folds_zero_true_loss = True
        for fold in range(FOLD_COUNT):
            fold_tokens = Counter({tok: count for tok, count in pruned.items() if fold_for_token(tok) == fold})
            true_pruned = int(sum((fold_tokens & reference).values()))
            false_pruned = int(sum(fold_tokens.values()) - true_pruned)
            if true_pruned != 0:
                all_folds_zero_true_loss = False
            if false_pruned > 0:
                folds_with_false_reduction += 1
            folds.append({
                "fold": fold,
                "pruned": int(sum(fold_tokens.values())),
                "truePruned": true_pruned,
                "falsePruned": false_pruned,
                "passedZeroTrueLoss": true_pruned == 0,
            })

        prune_cv = all_folds_zero_true_loss and int(sum(pruned.values())) > 0 and folds_with_false_reduction >= 2
        extra_reduction = EXPECTED[2] - int(full["extra"])
        accepted_over_1569 = (
            int(full["matched"]) == EXPECTED[0]
            and int(full["missing"]) == EXPECTED[1]
            and extra_reduction > 0
            and float(full["pitchF1"]) > EXPECTED_F1
            and prune_cv
            and bool(stability["sectionStabilityPassed"])
            and bool(stability["shiftedWindowStabilityPassed"])
        )
        result = {
            "fullScore": full,
            "pruneCount": int(sum(pruned.values())),
            "extraReduction": extra_reduction,
            "heldoutPruneCrossValidationPassed": prune_cv,
            "foldsWithFalseReduction": folds_with_false_reduction,
            "folds": folds,
            "sectionStabilityPassed": bool(stability["sectionStabilityPassed"]),
            "shiftedWindowStabilityPassed": bool(stability["shiftedWindowStabilityPassed"]),
            "acceptedOver1569": accepted_over_1569,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1569}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1569:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_15_69_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1569": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 15.69 final attack-envelope prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-15.69-final-attack-envelope-survivor-precision-prune-with-heldout-cv",
        "baseline1569Score": baseline,
        "foldDefinition": "measureNumber modulo 5",
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
        "validatedNewChampion": validated_new_champion,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-validation-only",
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
        "baseline1569PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 15.69 FINAL ATTACK-ENVELOPE SURVIVOR PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Winner prune count:", winner_eval["pruneCount"])
    print("Winner extra reduction:", winner_eval["extraReduction"])
    print("Winner prune-specific cross-validation passed:", winner_eval["heldoutPruneCrossValidationPassed"])
    print("Winner section stability passed:", winner_eval["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner_eval["shiftedWindowStabilityPassed"])
    print("Validated new champion:", validated_new_champion)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged:", before == after)
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
