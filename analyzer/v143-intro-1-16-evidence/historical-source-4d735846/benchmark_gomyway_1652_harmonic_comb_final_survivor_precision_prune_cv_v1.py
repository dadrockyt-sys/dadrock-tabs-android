from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1652_harmonic_comb_survivors_precision_v1 as p1652
import benchmark_gomyway_1590_harmonic_comb_precision_prune_cv_v1 as b1590

harmonic = b1590.harmonic
recur = b1590.recur
recall = b1590.recall
v2 = b1590.v2
v3 = b1590.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1590_PATH = PUBLIC / "gomyway-1590-dual-stem-harmonic-comb-coherence-v1.json"
PROFILE_1652_PATH = PUBLIC / "gomyway-1652-harmonic-comb-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1652-harmonic-comb-final-survivor-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1652-harmonic-comb-final-survivor-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1166)
EXPECTED_F1 = 16.52
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def reconstruct_1652(grid: Any) -> Counter[tuple[int, int, int]]:
    survivor_payload = v2.load_json(harmonic.b1569.PROFILE_1569_PATH)
    attack_rows = list(survivor_payload.get("rows", []))
    attack_row_by_token = {tuple(int(v) for v in row["token"]): row for row in attack_rows}
    champion_1590 = harmonic.reconstruct_1590(grid, attack_row_by_token)

    profile_payload = v2.load_json(PROFILE_1590_PATH)
    rows = list(profile_payload.get("rows", []))
    row_by_token = {token(row): row for row in rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1590.items():
        row = row_by_token.get(tok)
        if row is not None and (
            b1590.pred_a(row)
            or b1590.pred_b(row)
            or b1590.pred_c(row)
            or b1590.pred_d(row)
            or b1590.pred_e(row)
        ):
            pruned[tok] = count
    return champion_1590 - pruned


def pred_a(row: dict[str, Any]) -> bool:
    b = b1590.harmonic_buckets(row)
    return b["minMargin"] == "margin_080_095" and b["minF0Share"] == "f0share_035_050"


def pred_b(row: dict[str, Any]) -> bool:
    b = b1590.harmonic_buckets(row)
    return b["minComb"] == "comb_003_006" and b["minMargin"] == "margin_080_095"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("harmonic1652_final_a_margin080095_f0share035050", pred_a),
    ("harmonic1652_final_b_comb003006_margin080095", pred_b),
    ("harmonic1652_final_union_a_b", lambda row: pred_a(row) or pred_b(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    survivor_payload = v2.load_json(PROFILE_1652_PATH)
    if survivor_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("16.52 harmonic-comb survivor profile is not reference-free during detection")
    rows = list(survivor_payload.get("rows", []))
    if not rows:
        raise RuntimeError("16.52 harmonic-comb survivor profile has no rows")
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

    champion = reconstruct_1652(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 16.52 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

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
        accepted_over_1652 = (
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
            "acceptedOver1652": accepted_over_1652,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1652}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1652:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_16_52_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1652": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during final 16.52 harmonic-comb survivor prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-16.52-final-harmonic-comb-survivor-precision-prune-with-heldout-cv",
        "baseline1652Score": baseline,
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
        "baseline1652PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 16.52 FINAL HARMONIC-COMB SURVIVOR PRECISION PRUNE CV V1 COMPLETE")
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
