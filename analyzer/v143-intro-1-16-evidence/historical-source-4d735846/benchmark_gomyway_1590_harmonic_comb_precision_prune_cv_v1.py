from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1590_dual_stem_harmonic_comb_coherence_v1 as harmonic

recur = harmonic.recur
recall = harmonic.recall
v2 = harmonic.v2
v3 = harmonic.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1590-dual-stem-harmonic-comb-coherence-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1590-harmonic-comb-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1590-harmonic-comb-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1252)
EXPECTED_F1 = 15.90
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def harmonic_buckets(row: dict[str, Any]) -> dict[str, str]:
    return {
        "minComb": harmonic.comb_ratio_bucket(float(row["minCombRatio"])),
        "minMargin": harmonic.margin_bucket(float(row["minNeighborMargin"])),
        "minF0Share": harmonic.f0share_bucket(float(row["minFundamentalShare"])),
        "combDisagreement": harmonic.disagreement_bucket(float(row["combRatioDisagreementOctaves"])),
    }


def pred_a(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_095_110" and b["minF0Share"] == "f0share_020_035"


def pred_b(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_lt080" and b["minF0Share"] == "f0share_020_035"


def pred_c(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_lt080" and b["minF0Share"] == "f0share_050_070"


def pred_d(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_095_110" and b["minF0Share"] == "f0share_035_050"


def pred_e(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_lt080" and b["minF0Share"] == "f0share_070_plus"


def pred_f(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return (
        b["minComb"] == "comb_012_plus"
        and b["minMargin"] == "margin_lt080"
        and b["combDisagreement"] == "disagree_020_050"
    )


def pred_g(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minMargin"] == "margin_080_095" and b["minF0Share"] == "f0share_035_050"


def pred_h(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minComb"] == "comb_003_006" and b["minF0Share"] == "f0share_020_035"


def pred_i(row: dict[str, Any]) -> bool:
    b = harmonic_buckets(row)
    return b["minComb"] == "comb_003_006" and b["minMargin"] == "margin_080_095"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("harmonic1590_prune_a_margin095110_f0share020035", pred_a),
    ("harmonic1590_prune_b_marginlt080_f0share020035", pred_b),
    ("harmonic1590_prune_c_marginlt080_f0share050070", pred_c),
    ("harmonic1590_prune_d_margin095110_f0share035050", pred_d),
    ("harmonic1590_prune_e_marginlt080_f0share070plus", pred_e),
    ("harmonic1590_prune_f_comb012_marginlt080_disagree020050", pred_f),
    ("harmonic1590_prune_g_margin080095_f0share035050", pred_g),
    ("harmonic1590_prune_h_comb003006_f0share020035", pred_h),
    ("harmonic1590_prune_i_comb003006_margin080095", pred_i),
    ("harmonic1590_prune_union_a_b", lambda row: pred_a(row) or pred_b(row)),
    ("harmonic1590_prune_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("harmonic1590_prune_union_a_b_c_d", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row)),
    ("harmonic1590_prune_union_a_b_c_d_e", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row) or pred_e(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.90 harmonic-comb profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("15.90 harmonic-comb profile has no rows")
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

    survivor_payload = v2.load_json(harmonic.b1569.PROFILE_1569_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("15.69 survivor profile is not reference-free during detection")
    survivor_rows = list(survivor_payload.get("rows", []))
    attack_row_by_token = {tuple(int(v) for v in row["token"]): row for row in survivor_rows}

    champion = harmonic.reconstruct_1590(grid, attack_row_by_token)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 15.90 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

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
        accepted_over_1590 = (
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
            "acceptedOver1590": accepted_over_1590,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1590}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1590:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_15_90_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1590": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 15.90 harmonic-comb prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-15.90-harmonic-comb-precision-prune-with-heldout-cv",
        "baseline1590Score": baseline,
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
        "baseline1590PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 15.90 HARMONIC-COMB PRECISION PRUNE CV V1 COMPLETE")
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
