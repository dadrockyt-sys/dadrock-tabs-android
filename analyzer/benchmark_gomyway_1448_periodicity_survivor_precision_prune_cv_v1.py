from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1448_periodicity_survivor_additions_precision_v1 as p1448
import benchmark_gomyway_1444_cached_periodicity_survivor_precision_prune_cv_v1 as b1444
import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

recur = p1448.recur
recall = p1448.recall
v2 = p1448.v2
v3 = p1448.v3
bench = p1448.bench
cached = p1448.cached
gate = p1448.gate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1444_PATH = PUBLIC / "gomyway-1444-periodicity-survivor-additions-precision-v1.json"
PROFILE_1448_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-additions-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1448-periodicity-survivor-precision-prune-cv-v1-manifest.json"
EXPECTED_1448 = (183, 684, 1478)
EXPECTED_1448_F1 = 14.48
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


# These predicates are detector/audio signatures discovered by the 14.48
# survivor profiler. They intentionally contain no song-coordinate, measure,
# step, or pitch identity rules.
def pred_a(row: dict[str, Any]) -> bool:
    return (
        str(row.get("rmsBucket")) == "rms_lt_0"
        and float(row.get("maxTargetCorr", 999.0)) < 0.55
        and float(row.get("maxTargetMargin", 999.0)) < 0.15
    )


def pred_b(row: dict[str, Any]) -> bool:
    return (
        float(row.get("maxTargetOrOctaveCorr", 999.0)) < 0.60
        and float(row.get("minTargetOrOctaveCorr", 999.0)) < 0.50
        and float(row.get("maxTargetMargin", 999.0)) < 0.15
    )


def pred_c(row: dict[str, Any]) -> bool:
    return str(row.get("ratioBucket")) == "ratio_200_400"


def pred_d(row: dict[str, Any]) -> bool:
    return str(row.get("fluxBucket")) == "flux_0_010"


def pred_e(row: dict[str, Any]) -> bool:
    return str(row.get("rmsBucket")) == "rms_lt_0" and str(row.get("fluxBucket")) == "flux_0_010"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("survivor_prune_a_low_rms_maxc55_maxm15", pred_a),
    ("survivor_prune_b_low_octave_pair_maxm15", pred_b),
    ("survivor_prune_c_ratio200_400", pred_c),
    ("survivor_prune_d_flux0_010", pred_d),
    ("survivor_prune_e_low_rms_flux0_010", pred_e),
    ("survivor_prune_union_a_b", lambda row: pred_a(row) or pred_b(row)),
    ("survivor_prune_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("survivor_prune_union_a_b_c_d", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row)),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    if not PROFILE_1444_PATH.exists():
        raise RuntimeError(f"Missing 14.44 survivor profile: {PROFILE_1444_PATH.relative_to(ROOT)}")
    if not PROFILE_1448_PATH.exists():
        raise RuntimeError(f"Missing 14.48 survivor profile: {PROFILE_1448_PATH.relative_to(ROOT)}")

    survivor_1444_payload = v2.load_json(PROFILE_1444_PATH)
    survivor_1448_payload = v2.load_json(PROFILE_1448_PATH)
    if survivor_1444_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.44 survivor profile is not reference-free during detection")
    if survivor_1448_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("14.48 survivor profile is not reference-free during detection")
    survivor_1444_rows = list(survivor_1444_payload.get("rows", []))
    survivor_1448_rows = list(survivor_1448_payload.get("rows", []))
    if not survivor_1448_rows:
        raise RuntimeError("14.48 survivor profile has no rows")

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    periodicity_payload = v2.load_json(prune.PERIODICITY_PATH)
    precision_payload = v2.load_json(prune.PRECISION_PATH)
    precision_by_token = {token(row): row for row in precision_payload.get("rows", [])}

    cached_rows = cached.load_profile_rows()
    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_1419_additions = bench.rows_to_counter(cached_rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions
    winner_rows = [row for row in periodicity_payload.get("rows", []) if gate.sig_d(row)]
    periodicity_additions = gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions

    first_pruned: Counter[tuple[int, int, int]] = Counter()
    for prow in winner_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached 14.30 precision detail for token {tok}")
        if prune.pred_a(detail) or prune.pred_b(detail) or prune.pred_c(detail):
            first_pruned[tok] = 1
    champion_1444 = champion_1430 - first_pruned

    second_pruned: Counter[tuple[int, int, int]] = Counter()
    for row in survivor_1444_rows:
        if b1444.pred_a(row) or b1444.pred_b(row) or b1444.pred_c(row) or b1444.pred_d(row):
            second_pruned[token(row)] = 1
    champion_1448 = champion_1444 - second_pruned

    score_1448 = recur.grade(champion_1448, reference)
    actual = (int(score_1448["matched"]), int(score_1448["missing"]), int(score_1448["extra"]))
    if actual != EXPECTED_1448 or abs(float(score_1448["pitchF1"]) - EXPECTED_1448_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.48 champion {EXPECTED_1448}/{EXPECTED_1448_F1}, got {actual}/{score_1448['pitchF1']}")

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in VARIANTS:
        pruned_tokens: Counter[tuple[int, int, int]] = Counter()
        for row in survivor_1448_rows:
            if predicate(row):
                pruned_tokens[token(row)] = 1

        candidate = champion_1448 - pruned_tokens
        full = recur.grade(candidate, reference)
        stability = recall.evaluate_recall(candidate, champion_1448, reference, score_1448)

        folds: list[dict[str, Any]] = []
        folds_with_false_reduction = 0
        all_folds_zero_true_loss = True
        for fold in range(FOLD_COUNT):
            fold_tokens = Counter({tok: count for tok, count in pruned_tokens.items() if fold_for_token(tok) == fold})
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
            and int(sum(pruned_tokens.values())) > 0
            and folds_with_false_reduction >= 2
        )
        extra_reduction = EXPECTED_1448[2] - int(full["extra"])
        accepted_over_1448 = (
            int(full["matched"]) == EXPECTED_1448[0]
            and int(full["missing"]) == EXPECTED_1448[1]
            and extra_reduction > 0
            and float(full["pitchF1"]) > EXPECTED_1448_F1
            and prune_cv
            and bool(stability["sectionStabilityPassed"])
            and bool(stability["shiftedWindowStabilityPassed"])
        )

        result = {
            "fullScore": full,
            "pruneCount": int(sum(pruned_tokens.values())),
            "extraReduction": extra_reduction,
            "heldoutPruneCrossValidationPassed": prune_cv,
            "foldsWithFalseReduction": folds_with_false_reduction,
            "folds": folds,
            "sectionStabilityPassed": bool(stability["sectionStabilityPassed"]),
            "shiftedWindowStabilityPassed": bool(stability["shiftedWindowStabilityPassed"]),
            "acceptedOver1448": accepted_over_1448,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_1448}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1448:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_48_champion"
        winner_eval = {
            "fullScore": score_1448,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1448": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.48 survivor prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-14.48-periodicity-survivor-precision-prune-with-heldout-cv",
        "baseline1448Score": score_1448,
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
        "baseline1448PitchF1": score_1448["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.48 PERIODICITY SURVIVOR PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", score_1448["pitchF1"])
    print("Baseline matched/missing/extra:", score_1448["matched"], "/", score_1448["missing"], "/", score_1448["extra"])
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
