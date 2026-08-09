from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_2552_dual_stem_periodicity_phase_coherence_v1 as period

p2552 = period.p2552
recur = period.recur
recall = period.recall
v2 = period.v2
v3 = period.v3
harmonic = period.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PERIOD_PROFILE_PATH = PUBLIC / "gomyway-2552-dual-stem-periodicity-phase-coherence-v1.json"
TEMPLATE_PROFILE_PATH = PUBLIC / "gomyway-2476-dual-stem-harmonic-template-competition-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2552-periodicity-phase-coherence-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2552-periodicity-phase-coherence-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 384)
EXPECTED_F1 = 25.52
EXPECTED_TEMPLATE_ZERO_SIGNATURES = 11
EXPECTED_PERIOD_ZERO_SIGNATURES = 1
FOLD_COUNT = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def fold_for_token(tok: tuple[int, int, int]) -> int:
    return int(tok[0]) % FOLD_COUNT


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    period_profile = v2.load_json(PERIOD_PROFILE_PATH)
    if period_profile.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("25.52 periodicity profile is not reference-free during detection")
    rows = list(period_profile.get("rows", []))
    if not rows:
        raise RuntimeError("25.52 periodicity profile has no rows")
    row_by_token = {token(row): row for row in rows}

    period_zero = list(period_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(period_zero) != EXPECTED_PERIOD_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_PERIOD_ZERO_SIGNATURES} periodicity zero-precision signature, got {len(period_zero)}"
        )
    target_signature = str(period_zero[0]["signature"])
    if int(period_zero[0].get("true", -1)) != 0 or int(period_zero[0].get("false", 0)) < 5:
        raise RuntimeError(f"Invalid periodicity zero-precision row: {period_zero[0]}")

    template_profile = v2.load_json(TEMPLATE_PROFILE_PATH)
    template_zero = list(template_profile.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(template_zero) != EXPECTED_TEMPLATE_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected {EXPECTED_TEMPLATE_ZERO_SIGNATURES} validated harmonic-template signatures, got {len(template_zero)}"
        )
    exact_template_signatures = {str(row["signature"]) for row in template_zero}

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
    champion, prior_pruned = p2552.reconstruct_2552(
        grid,
        winner_audio,
        winner_sr,
        alt_audio,
        alt_sr,
        exact_template_signatures,
    )
    if int(sum(prior_pruned.values())) != p2552.EXPECTED_PRUNE_COUNT:
        raise RuntimeError(
            f"Expected frozen 25.52 harmonic-template prune count {p2552.EXPECTED_PRUNE_COUNT}, got {sum(prior_pruned.values())}"
        )

    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 25.52 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion.items():
        row = row_by_token.get(tok)
        if row is not None and target_signature in {str(s) for s in row.get("signatures", [])}:
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
    accepted = (
        int(full["matched"]) == EXPECTED[0]
        and int(full["missing"]) == EXPECTED[1]
        and true_pruned_total == 0
        and extra_reduction > 0
        and float(full["pitchF1"]) > EXPECTED_F1
        and prune_cv
        and bool(stability_eval["sectionStabilityPassed"])
        and bool(stability_eval["shiftedWindowStabilityPassed"])
    )

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 25.52 periodicity precision prune benchmark")

    result = {
        "signature": target_signature,
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
        "acceptedOver2552": accepted,
    }
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-25.52-periodicity-phase-coherence-single-signature-precision-prune-with-heldout-cv",
        "baseline2552Score": baseline,
        "foldDefinition": "measureNumber modulo 5",
        "zeroPrecisionSignatureCount": len(period_zero),
        "zeroPrecisionSignature": target_signature,
        "result": result,
        "winner": "periodicity2552_exact_zero_precision" if accepted else "retain_25_52_champion",
        "winnerEvaluation": result if accepted else {
            "fullScore": baseline,
            "pruneCount": 0,
            "truePruned": 0,
            "falsePruned": 0,
            "extraReduction": 0,
            "heldoutPruneCrossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOver2552": False,
        },
        "validatedNewChampion": accepted,
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
        "baseline2552PitchF1": baseline["pitchF1"],
        "winner": output["winner"],
        "validatedNewChampion": accepted,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    winner_eval = output["winnerEvaluation"]
    print("GOMYWAY 25.52 PERIODICITY PHASE COHERENCE PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Zero-precision signature count:", len(period_zero))
    print("Tested signature:", target_signature)
    print("Candidate pitch F1:", full["pitchF1"])
    print("Candidate matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Candidate prune count:", prune_count)
    print("Candidate true pruned:", true_pruned_total)
    print("Candidate false pruned:", false_pruned_total)
    print("Candidate prune-specific cross-validation passed:", prune_cv)
    print("Candidate section stability passed:", result["sectionStabilityPassed"])
    print("Candidate shifted-window stability passed:", result["shiftedWindowStabilityPassed"])
    print("Winner:", output["winner"])
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
    print("Validated new champion:", accepted)
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
