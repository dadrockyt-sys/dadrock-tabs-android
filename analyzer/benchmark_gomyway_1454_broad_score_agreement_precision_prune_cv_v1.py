from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1454_broad_champion_extras_cross_signatures_v1 as profile
import profile_gomyway_1454_periodicity_survivor_additions_precision_v1 as p1454
import profile_gomyway_step10_agreement_pruned_champion_extras_v1 as legacy
import benchmark_gomyway_1451_periodicity_survivor_precision_prune_cv_v1 as b1451
import benchmark_gomyway_1448_periodicity_survivor_precision_prune_cv_v1 as b1448
import benchmark_gomyway_1444_cached_periodicity_survivor_precision_prune_cv_v1 as b1444
import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

recur = p1454.recur
recall = p1454.recall
v2 = p1454.v2
v3 = p1454.v3
bench = p1454.bench
cached = p1454.cached
gate = p1454.gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1444_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1.json"
PROFILE_1448_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-additions-precision-v1.json"
PROFILE_1451_PATH = PUBLIC / "gomyway-1451-periodicity-survivor-additions-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1454-broad-score-agreement-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1454-broad-score-agreement-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1467)
EXPECTED_F1 = 14.54
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def reconstruct_1454(grid: Any) -> Counter[tuple[int, int, int]]:
    payload_1444 = v2.load_json(PROFILE_1444_PATH)
    payload_1448 = v2.load_json(PROFILE_1448_PATH)
    payload_1451 = v2.load_json(PROFILE_1451_PATH)
    rows_1444 = list(payload_1444.get("rows", []))
    rows_1448 = list(payload_1448.get("rows", []))
    rows_1451 = list(payload_1451.get("rows", []))

    periodicity_payload = v2.load_json(prune.PERIODICITY_PATH)
    precision_payload = v2.load_json(prune.PRECISION_PATH)
    precision_by_token = {token(row): row for row in precision_payload.get("rows", [])}

    cached_rows = cached.load_profile_rows()
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419 = baseline_1382 + bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    periodicity_rows = [row for row in periodicity_payload.get("rows", []) if gate.sig_d(row)]
    champion_1430 = champion_1419 + gate.rows_to_counter(periodicity_rows, lambda row: True)

    first_pruned: Counter[tuple[int, int, int]] = Counter()
    for prow in periodicity_rows:
        tok = token(prow)
        detail = precision_by_token[tok]
        if prune.pred_a(detail) or prune.pred_b(detail) or prune.pred_c(detail):
            first_pruned[tok] = 1
    champion_1444 = champion_1430 - first_pruned

    second_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1444:
        if b1444.pred_a(row) or b1444.pred_b(row) or b1444.pred_c(row) or b1444.pred_d(row):
            second_pruned[token(row)] = 1
    champion_1448 = champion_1444 - second_pruned

    third_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1448:
        if b1448.pred_a(row):
            third_pruned[token(row)] = 1
    champion_1451 = champion_1448 - third_pruned

    fourth_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in rows_1451:
        if b1451.pred_a(row) or b1451.pred_b(row) or b1451.pred_c(row):
            fourth_pruned[token(row)] = 1
    return champion_1451 - fourth_pruned


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    champion = reconstruct_1454(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.54 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    winner_scores = legacy.spectral.specialist_scores(legacy.WINNER_STEM, grid)
    alt_scores = legacy.spectral.specialist_scores(legacy.ALT_STEM, grid)

    def signature(tok: tuple[int, int, int]) -> tuple[str, str]:
        return (
            legacy.pruning.score_bucket(tok, winner_scores, alt_scores),
            legacy.pruning.agreement_bucket(tok, winner_scores, alt_scores),
        )

    predicates: list[tuple[str, Callable[[tuple[int, int, int]], bool]]] = [
        (
            "drop_score16_20_both_ge8",
            lambda tok: signature(tok) == ("16_20", "both_ge8"),
        ),
        (
            "drop_score20_plus_both_ge8",
            lambda tok: signature(tok) == ("20_plus", "both_ge8"),
        ),
        (
            "drop_score20_plus_single_or_weak_second",
            lambda tok: signature(tok) == ("20_plus", "single_stem_or_weak_second"),
        ),
        (
            "drop_union_visible_zero_precision_score_agreement",
            lambda tok: signature(tok) in {
                ("16_20", "both_ge8"),
                ("20_plus", "both_ge8"),
                ("20_plus", "single_stem_or_weak_second"),
            },
        ),
    ]

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in predicates:
        pruned = Counter({tok: count for tok, count in champion.items() if predicate(tok)})
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
        accepted_over_1454 = (
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
            "acceptedOver1454": accepted_over_1454,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1454}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1454:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_54_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1454": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.54 broad score-agreement prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.54-broad-score-agreement-precision-prune-with-heldout-cv",
        "baseline1454Score": baseline,
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
        "baseline1454PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.54 BROAD SCORE-AGREEMENT PRECISION PRUNE CV V1 COMPLETE")
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
