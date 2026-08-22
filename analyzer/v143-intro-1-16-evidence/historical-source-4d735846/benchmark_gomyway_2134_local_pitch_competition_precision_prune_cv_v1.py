from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_2134_dual_stem_local_pitch_competition_v1 as comp

recur = comp.recur
recall = comp.recall
v2 = comp.v2
v3 = comp.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2134-dual-stem-local-pitch-competition-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2134-local-pitch-competition-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2134-local-pitch-competition-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 665)
EXPECTED_F1 = 21.34
FOLD_COUNT = 5
TARGET_SIGNATURE = "competitionCross::ratio_075_095|ratio_115_145|margin_n015_000|agree_one"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def row_signatures(row: dict[str, Any]) -> set[str]:
    rmin = comp.ratio_bucket(float(row["minTargetVsCompetitorRatio"]))
    rmax = comp.ratio_bucket(float(row["maxTargetVsCompetitorRatio"]))
    marg = comp.margin_bucket(float(row["minTargetCompetitionMargin"]))
    wins = int(row["targetWinsAcrossStems"])
    agree = comp.disagree_bucket(2 - wins)
    return {
        f"minCompetitionRatio::{rmin}",
        f"maxCompetitionRatio::{rmax}",
        f"competitionMargin::{marg}",
        f"targetWinAgreement::{agree}",
        f"ratioAgreement::{rmin}|{agree}",
        f"marginAgreement::{marg}|{agree}",
        f"competitionCross::{rmin}|{rmax}|{marg}|{agree}",
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile = v2.load_json(PROFILE_PATH)
    if profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("21.34 local-pitch-competition profile is not reference-free during detection")

    zero_rows = list(profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    zero_signatures = {str(r["signature"]) for r in zero_rows}
    if TARGET_SIGNATURE not in zero_signatures:
        raise RuntimeError(f"Expected zero-precision signature missing: {TARGET_SIGNATURE}")

    rows = list(profile.get("rows", []))
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

    champion = comp.reconstruct_2134(grid)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 21.34 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion.items():
        row = row_by_token.get(tok)
        if row is not None and TARGET_SIGNATURE in row_signatures(row):
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
    accepted = (
        int(full["matched"]) == EXPECTED[0]
        and int(full["missing"]) == EXPECTED[1]
        and extra_reduction > 0
        and float(full["pitchF1"]) > EXPECTED_F1
        and prune_cv
        and bool(stability["sectionStabilityPassed"])
        and bool(stability["shiftedWindowStabilityPassed"])
    )

    if accepted:
        winner = "localpitch2134_exact_zero_precision"
        winner_score = full
        prune_count = int(sum(pruned.values()))
        validated = True
    else:
        winner = "retain_21_34_champion"
        winner_score = baseline
        prune_count = 0
        extra_reduction = 0
        validated = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 21.34 local-pitch-competition prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-21.34-local-pitch-competition-single-signature-precision-prune-with-heldout-cv",
        "baseline2134Score": baseline,
        "targetSignature": TARGET_SIGNATURE,
        "foldDefinition": "measureNumber modulo 5",
        "candidateScore": full,
        "candidatePruneCount": int(sum(pruned.values())),
        "candidateExtraReduction": EXPECTED[2] - int(full["extra"]),
        "heldoutPruneCrossValidationPassed": prune_cv,
        "foldsWithFalseReduction": folds_with_false_reduction,
        "folds": folds,
        "sectionStabilityPassed": bool(stability["sectionStabilityPassed"]),
        "shiftedWindowStabilityPassed": bool(stability["shiftedWindowStabilityPassed"]),
        "winner": winner,
        "winnerScore": winner_score,
        "winnerPruneCount": prune_count,
        "winnerExtraReduction": extra_reduction,
        "validatedNewChampion": validated,
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
        "baseline2134PitchF1": baseline["pitchF1"],
        "winner": winner,
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 21.34 LOCAL PITCH COMPETITION PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Target signature:", TARGET_SIGNATURE)
    print("Candidate pitch F1:", full["pitchF1"])
    print("Candidate matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Candidate prune count:", sum(pruned.values()))
    print("Candidate extra reduction:", EXPECTED[2] - int(full["extra"]))
    print("Prune-specific cross-validation passed:", prune_cv)
    print("Folds:", folds)
    print("Section stability passed:", stability["sectionStabilityPassed"])
    print("Shifted-window stability passed:", stability["shiftedWindowStabilityPassed"])
    print("Winner:", winner)
    print("Winner pitch F1:", winner_score["pitchF1"])
    print("Winner matched/missing/extra:", winner_score["matched"], "/", winner_score["missing"], "/", winner_score["extra"])
    print("Validated new champion:", validated)
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
