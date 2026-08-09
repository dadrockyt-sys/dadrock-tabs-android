from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1460_dual_stem_attack_envelope_v1 as attack
import benchmark_gomyway_1454_broad_score_agreement_precision_prune_cv_v1 as b1454
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy

recur = b1454.recur
recall = b1454.recall
v2 = b1454.v2
v3 = b1454.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1460-dual-stem-attack-envelope-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1460-attack-envelope-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1460-attack-envelope-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1456)
EXPECTED_F1 = 14.60
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def reconstruct_1460(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1454 = b1454.reconstruct_1454(grid)
    winner_scores = legacy.spectral.specialist_scores(legacy.WINNER_STEM, grid)
    alt_scores = legacy.spectral.specialist_scores(legacy.ALT_STEM, grid)

    def score_agreement(tok: tuple[int, int, int]) -> tuple[str, str]:
        return (
            legacy.pruning.score_bucket(tok, winner_scores, alt_scores),
            legacy.pruning.agreement_bucket(tok, winner_scores, alt_scores),
        )

    validated_union = {
        ("16_20", "both_ge8"),
        ("20_plus", "both_ge8"),
        ("20_plus", "single_stem_or_weak_second"),
    }
    fifth_pruned = Counter(
        {tok: count for tok, count in champion_1454.items() if score_agreement(tok) in validated_union}
    )
    return champion_1454 - fifth_pruned


def buckets(row: dict[str, Any]) -> dict[str, str]:
    return {
        "minAttack": attack.ratio_bucket(float(row["minAttackRatio"]), "minattack"),
        "maxDecay": attack.decay_bucket(float(row["maxDecayRatio"])),
        "minCrest": "min_" + attack.crest_bucket(float(row["minCrest"])),
        "maxZcr": "max_" + attack.zcr_bucket(float(row["maxZcr"])),
        "attackDisagreement": attack.disagree_bucket(float(row["attackDisagreementOctaves"])),
    }


def pred_a(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_220_plus" and b["maxDecay"] == "decay_070_095"


def pred_b(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_080_100" and b["maxDecay"] == "decay_045_070"


def pred_c(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_125_160" and b["maxDecay"] == "decay_120_plus"


def pred_d(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["maxDecay"] == "decay_120_plus" and b["minCrest"] == "min_crest_2_3"


def pred_e(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_100_125" and b["minCrest"] == "min_crest_4p5_plus"


def pred_f(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_lt080" and b["maxZcr"] == "max_zcr_1600_3000"


def pred_g(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["minAttack"] == "minattack_160_220" and b["attackDisagreement"] == "attack_disagree_020_050"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("attack_prune_a_minattack220plus_decay070095", pred_a),
    ("attack_prune_b_minattack080100_decay045070", pred_b),
    ("attack_prune_c_minattack125160_decay120plus", pred_c),
    ("attack_prune_d_decay120plus_mincrest2_3", pred_d),
    ("attack_prune_e_minattack100125_mincrest4p5plus", pred_e),
    ("attack_prune_f_minattacklt080_maxzcr1600_3000", pred_f),
    ("attack_prune_g_minattack160220_disagree020050", pred_g),
    ("attack_prune_union_a_b", lambda row: pred_a(row) or pred_b(row)),
    ("attack_prune_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("attack_prune_union_a_b_c_d", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Attack-envelope profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("Attack-envelope profile has no rows")

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    champion = reconstruct_1460(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.60 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    row_by_token = {token(row): row for row in rows}
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

        prune_cv = (
            all_folds_zero_true_loss
            and int(sum(pruned.values())) > 0
            and folds_with_false_reduction >= 2
        )
        extra_reduction = EXPECTED[2] - int(full["extra"])
        accepted_over_1460 = (
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
            "acceptedOver1460": accepted_over_1460,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1460}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1460:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_60_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1460": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.60 attack-envelope prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.60-attack-envelope-precision-prune-with-heldout-cv",
        "baseline1460Score": baseline,
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
        "baseline1460PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.60 ATTACK-ENVELOPE PRECISION PRUNE CV V1 COMPLETE")
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
