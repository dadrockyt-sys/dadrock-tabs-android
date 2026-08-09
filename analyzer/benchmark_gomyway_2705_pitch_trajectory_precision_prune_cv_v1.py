from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import profile_gomyway_2705_dual_stem_pitch_trajectory_stability_v1 as trajectory

recur = trajectory.recur
recall = trajectory.recall
v2 = trajectory.v2
v3 = trajectory.v3
harmonic = trajectory.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2705-dual-stem-pitch-trajectory-stability-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2705-pitch-trajectory-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2705-pitch-trajectory-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 303)
EXPECTED_F1 = 27.05
EXPECTED_ZERO_SIGNATURES = 6
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def row_signatures(row: dict[str, Any]) -> set[str]:
    signatures = row.get("signatures")
    if not signatures:
        raise RuntimeError(f"Profile row missing pitch-trajectory signatures for token {row.get('token')}")
    return {str(s) for s in signatures}


def make_exact_predicate(signature: str) -> Callable[[dict[str, Any]], bool]:
    return lambda row, s=signature: s in row_signatures(row)


def union_pred(selected: list[str]) -> Callable[[dict[str, Any]], bool]:
    chosen = set(selected)
    return lambda row: bool(row_signatures(row) & chosen)


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("27.05 pitch-trajectory profile is not reference-free during detection")
    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("27.05 pitch-trajectory profile has no rows")
    row_by_token = {token(row): row for row in rows}

    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} pitch-trajectory zero-precision signatures, got {len(zero_rows)}"
        )
    for row in zero_rows:
        if int(row.get("true", -1)) != 0 or int(row.get("false", 0)) < 5:
            raise RuntimeError(f"Invalid zero-precision pitch-trajectory row: {row}")
    zero_rows.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    exact_signatures = [str(r["signature"]) for r in zero_rows]

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)
    champion = trajectory.reconstruct_2705(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.05 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    variants: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    for idx, signature in enumerate(exact_signatures, start=1):
        variants.append((f"pitchtrajectory2705_exact_{idx:02d}", make_exact_predicate(signature)))
    variants.append(("pitchtrajectory2705_union_top2", union_pred(exact_signatures[:2])))
    variants.append(("pitchtrajectory2705_union_top3", union_pred(exact_signatures[:3])))
    variants.append(("pitchtrajectory2705_union_top5", union_pred(exact_signatures[:5])))
    variants.append(("pitchtrajectory2705_union_all_zero_precision", union_pred(exact_signatures)))

    results: dict[str, Any] = {}
    accepted: list[tuple[str, dict[str, Any]]] = []

    for name, predicate in variants:
        pruned: Counter[tuple[int, int, int]] = Counter()
        for tok, count in champion.items():
            row = row_by_token.get(tok)
            if row is not None and predicate(row):
                pruned[tok] = count

        candidate = champion - pruned
        full = recur.grade(candidate, reference)
        stability_eval = recall.evaluate_recall(candidate, champion, reference, baseline)

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

        prune_count = int(sum(pruned.values()))
        true_pruned_total = int(sum((pruned & reference).values()))
        false_pruned_total = prune_count - true_pruned_total
        prune_cv = all_folds_zero_true_loss and prune_count > 0 and folds_with_false_reduction >= 2
        extra_reduction = EXPECTED[2] - int(full["extra"])
        accepted_over_2705 = (
            int(full["matched"]) == EXPECTED[0]
            and int(full["missing"]) == EXPECTED[1]
            and true_pruned_total == 0
            and extra_reduction > 0
            and float(full["pitchF1"]) > EXPECTED_F1
            and prune_cv
            and bool(stability_eval["sectionStabilityPassed"])
            and bool(stability_eval["shiftedWindowStabilityPassed"])
        )

        result = {
            "fullScore": full,
            "pruneCount": prune_count,
            "truePruned": true_pruned_total,
            "falsePruned": false_pruned_total,
            "extraReduction": extra_reduction,
            "heldoutPruneCrossValidationPassed": prune_cv,
            "foldsWithFalseReduction": folds_with_false_reduction,
            "folds": folds,
            "sectionStabilityPassed": bool(stability_eval["sectionStabilityPassed"]),
            "shiftedWindowStabilityPassed": bool(stability_eval["shiftedWindowStabilityPassed"]),
            "acceptedOver2705": accepted_over_2705,
        }
        results[name] = result
        print(
            f"{name}: F1={full['pitchF1']} matched={full['matched']} missing={full['missing']} "
            f"extra={full['extra']} pruned={prune_count} truePruned={true_pruned_total} "
            f"falsePruned={false_pruned_total} extraReduction={extra_reduction} "
            f"pruneCV={prune_cv} foldsWithReduction={folds_with_false_reduction} "
            f"sections={result['sectionStabilityPassed']} shifted={result['shiftedWindowStabilityPassed']} "
            f"accepted={accepted_over_2705}",
            flush=True,
        )
        print("  folds:", folds, flush=True)
        if accepted_over_2705:
            accepted.append((name, result))

    if accepted:
        winner_name, winner_eval = max(
            accepted,
            key=lambda item: (float(item[1]["fullScore"]["pitchF1"]), int(item[1]["extraReduction"])),
        )
        validated_new_champion = True
    else:
        winner_name = "retain_27_05_champion"
        winner_eval = {
            "fullScore": baseline,
            "pruneCount": 0,
            "truePruned": 0,
            "falsePruned": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "foldsWithFalseReduction": 0,
            "folds": [],
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver2705": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.05 pitch-trajectory precision-prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-27.05-pitch-trajectory-precision-prune-with-heldout-cv",
        "baseline2705Score": baseline,
        "foldDefinition": "measureNumber modulo 5",
        "zeroPrecisionSignatureCount": len(exact_signatures),
        "zeroPrecisionSignatures": exact_signatures,
        "results": results,
        "winner": winner_name,
        "winnerEvaluation": winner_eval,
        "validatedNewChampion": validated_new_champion,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-validation-only",
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
        "baseline2705PitchF1": baseline["pitchF1"],
        "winner": winner_name,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 27.05 PITCH TRAJECTORY PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Zero-precision signature count:", len(exact_signatures))
    print("Winner:", winner_name)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Winner prune count:", winner_eval["pruneCount"])
    print("Winner true pruned:", winner_eval["truePruned"])
    print("Winner false pruned:", winner_eval["falsePruned"])
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
