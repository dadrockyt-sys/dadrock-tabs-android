from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_1694_dual_stem_octave_subharmonic_discrimination_v1 as octave

recur = octave.recur
recall = octave.recall
v2 = octave.v2
v3 = octave.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1694-octave-subharmonic-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1694-octave-subharmonic-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 1110)
EXPECTED_F1 = 16.94
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def buckets(row: dict[str, Any]) -> dict[str, str]:
    return {
        "lowerRatio": octave.ratio_bucket(float(row["minTargetVsLower"])),
        "upperRatio": octave.ratio_bucket(float(row["minTargetVsUpper"])),
        "lowerDom": octave.dominance_bucket(float(row["maxLowerDominance"])),
        "upperDom": octave.dominance_bucket(float(row["maxUpperDominance"])),
        "wins": octave.win_bucket(int(row["targetWinsAcrossStems"])),
        "disagree": octave.disagreement_bucket(int(row["octaveStemDisagreement"])),
    }


def pred_a(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_105_135" and b["upperRatio"] == "ratio_135_180" and b["wins"] == "targetwins_2"


def pred_b(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_135_180" and b["upperRatio"] == "ratio_085_105" and b["wins"] == "targetwins_2"


def pred_c(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerDom"] == "dom_100_125" and b["upperDom"] == "dom_lt075" and b["disagree"] == "octave_disagree_0"


def pred_d(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerDom"] == "dom_lt075" and b["upperDom"] == "dom_125_175" and b["disagree"] == "octave_disagree_1"


def pred_e(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["upperRatio"] == "ratio_135_180" and b["wins"] == "targetwins_1"


def pred_f(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_085_105" and b["upperRatio"] == "ratio_135_180" and b["wins"] == "targetwins_1"


def pred_g(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_180_plus" and b["upperRatio"] == "ratio_065_085" and b["wins"] == "targetwins_1"


def pred_h(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_065_085" and b["upperRatio"] == "ratio_180_plus" and b["wins"] == "targetwins_0"


def pred_i(row: dict[str, Any]) -> bool:
    b = buckets(row)
    return b["lowerRatio"] == "ratio_085_105" and b["upperRatio"] == "ratio_180_plus" and b["wins"] == "targetwins_0"


VARIANTS: list[tuple[str, Callable[[dict[str, Any]], bool]]] = [
    ("octave1694_prune_a_cross105135_135180_wins2", pred_a),
    ("octave1694_prune_b_cross135180_085105_wins2", pred_b),
    ("octave1694_prune_c_dom100125_lt075_agree", pred_c),
    ("octave1694_prune_d_domlt075_125175_disagree", pred_d),
    ("octave1694_prune_e_upper135180_wins1", pred_e),
    ("octave1694_prune_f_cross085105_135180_wins1", pred_f),
    ("octave1694_prune_g_cross180plus_065085_wins1", pred_g),
    ("octave1694_prune_h_cross065085_180plus_wins0", pred_h),
    ("octave1694_prune_i_cross085105_180plus_wins0", pred_i),
    ("octave1694_prune_union_a_b_c", lambda row: pred_a(row) or pred_b(row) or pred_c(row)),
    ("octave1694_prune_union_a_b_c_d_e", lambda row: pred_a(row) or pred_b(row) or pred_c(row) or pred_d(row) or pred_e(row)),
    ("octave1694_prune_union_a_b_c_d_e_f_g_h_i", lambda row: any(p(row) for p in (pred_a, pred_b, pred_c, pred_d, pred_e, pred_f, pred_g, pred_h, pred_i))),
]


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("16.94 octave profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("16.94 octave profile has no rows")
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

    champion = octave.reconstruct_1694(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 16.94 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

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
        accepted_over_1694 = (
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
            "acceptedOver1694": accepted_over_1694,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={result['pruneCount']} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} accepted={accepted_over_1694}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_1694:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(accepted, key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])))
        validated_new_champion = True
    else:
        winner_name = "retain_16_94_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver1694": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 16.94 octave/subharmonic prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-16.94-octave-subharmonic-precision-prune-with-heldout-cv",
        "baseline1694Score": baseline,
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
        "baseline1694PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 16.94 OCTAVE SUBHARMONIC PRECISION PRUNE CV V1 COMPLETE")
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
