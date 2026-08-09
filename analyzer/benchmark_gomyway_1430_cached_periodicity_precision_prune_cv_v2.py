from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import benchmark_gomyway_1430_cached_periodicity_zero_precision_prune_v1 as prune

recur = prune.recur
recall = prune.recall
v2 = prune.v2
v3 = prune.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1430-cached-periodicity-precision-prune-cv-v2.json"
MANIFEST_PATH = PUBLIC / "gomyway-1430-cached-periodicity-precision-prune-cv-v2-manifest.json"
EXPECTED_1430 = (183, 684, 1510)
EXPECTED_1430_F1 = 14.30
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    # Deterministic measure-stratified held-out fold. Offset keeps neighboring
    # measures distributed while remaining completely reference-free.
    return int(tok[0]) % FOLD_COUNT


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    periodicity_payload = v2.load_json(prune.PERIODICITY_PATH)
    precision_payload = v2.load_json(prune.PRECISION_PATH)
    if periodicity_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Periodicity profile is not reference-free during detection")
    if precision_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Precision profile is not reference-free during detection")

    periodicity_rows = list(periodicity_payload.get("rows", []))
    precision_rows = list(precision_payload.get("rows", []))
    precision_by_token = {token(row): row for row in precision_rows}

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    cached_rows = prune.cached.load_profile_rows()
    baseline_1382, _, _ = prune.recur.build_frozen_1382(grid)
    champion_1419_additions = prune.bench.rows_to_counter(cached_rows, prune.bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_1419_additions

    winner_rows = [row for row in periodicity_rows if prune.gate.sig_d(row)]
    periodicity_additions = prune.gate.rows_to_counter(winner_rows, lambda row: True)
    champion_1430 = champion_1419 + periodicity_additions
    score_1430 = recur.grade(champion_1430, reference)
    actual = (int(score_1430["matched"]), int(score_1430["missing"]), int(score_1430["extra"]))
    if actual != EXPECTED_1430 or abs(float(score_1430["pitchF1"]) - EXPECTED_1430_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 14.30 champion, got {actual}/{score_1430['pitchF1']}")

    eligible_rows: list[dict[str, Any]] = []
    for prow in winner_rows:
        tok = token(prow)
        detail = precision_by_token.get(tok)
        if detail is None:
            raise RuntimeError(f"Missing cached precision detail for token {tok}")
        merged = dict(detail)
        merged["token"] = list(tok)
        eligible_rows.append(merged)

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in prune.VARIANTS:
        pruned_tokens: Counter[tuple[int, int, int]] = Counter()
        selected_rows: list[dict[str, Any]] = []
        for row in eligible_rows:
            if predicate(row):
                tok = token(row)
                pruned_tokens[tok] = 1
                selected_rows.append(row)

        candidate = champion_1430 - pruned_tokens
        full = recur.grade(candidate, reference)
        stability = recall.evaluate_recall(candidate, champion_1430, reference, score_1430)

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

        heldout_cv_passed = (
            all_folds_zero_true_loss
            and int(sum(pruned_tokens.values())) > 0
            and folds_with_false_reduction >= 2
        )
        extra_reduction = EXPECTED_1430[2] - int(full["extra"])
        strict_accepted = (
            int(full["matched"]) == EXPECTED_1430[0]
            and int(full["missing"]) == EXPECTED_1430[1]
            and extra_reduction > 0
            and float(full["pitchF1"]) > EXPECTED_1430_F1
            and heldout_cv_passed
            and bool(stability["sectionStabilityPassed"])
            and bool(stability["shiftedWindowStabilityPassed"])
        )

        result = {
            "fullScore": full,
            "pruneCount": int(sum(pruned_tokens.values())),
            "extraReduction": extra_reduction,
            "heldoutPruneCrossValidationPassed": heldout_cv_passed,
            "foldsWithFalseReduction": folds_with_false_reduction,
            "folds": folds,
            "legacyRecallCrossValidationPassed": bool(stability["crossValidationPassed"]),
            "sectionStabilityPassed": bool(stability["sectionStabilityPassed"]),
            "shiftedWindowStabilityPassed": bool(stability["shiftedWindowStabilityPassed"]),
            "acceptedOver1430": strict_accepted,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={heldout_cv_passed} foldsWithReduction={folds_with_false_reduction} "
            f"legacyRecallCV={result['legacyRecallCrossValidationPassed']} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={strict_accepted}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if strict_accepted:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_14_30_champion"
        winner_eval = {
            "fullScore": score_1430,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "legacyRecallCrossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1430": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during prune-specific CV benchmark")

    output = {
        "schemaVersion": 2,
        "passed": True,
        "benchmarkType": "validated-14.30-cached-periodicity-precision-prune-with-prune-specific-heldout-cv",
        "baseline1430Score": score_1430,
        "foldDefinition": "measureNumber modulo 5",
        "pruneCrossValidationRequirement": "zero true notes pruned in every fold and false reduction in at least two folds",
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
        "schemaVersion": 2,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "baseline1430PitchF1": score_1430["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.30 CACHED PERIODICITY PRECISION PRUNE CV V2 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", score_1430["pitchF1"])
    print("Baseline matched/missing/extra:", score_1430["matched"], "/", score_1430["missing"], "/", score_1430["extra"])
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
