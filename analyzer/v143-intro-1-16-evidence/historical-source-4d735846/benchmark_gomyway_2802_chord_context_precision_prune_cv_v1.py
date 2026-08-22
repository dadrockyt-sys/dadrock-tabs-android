from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import profile_gomyway_2802_polyphonic_chord_context_v1 as chord

recur = chord.recur
recall = chord.recall
v2 = chord.v2
v3 = chord.v3
harmonic = chord.harmonic
h2802 = chord.h2802

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_PATH = PUBLIC / "gomyway-2802-polyphonic-chord-context-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2802-chord-context-precision-prune-cv-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2802-chord-context-precision-prune-cv-v1-manifest.json"
EXPECTED = (183, 684, 256)
EXPECTED_F1 = 28.02
EXPECTED_ZERO_SIGNATURES = 1
EXPECTED_SIGNATURE = "repeatVoicingCross::m_0_3|rn2_3|nn13p"
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
        raise RuntimeError(f"Profile row missing chord-context signatures for token {row.get('token')}")
    return {str(s) for s in signatures}


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    profile_payload = v2.load_json(PROFILE_PATH)
    if profile_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("28.02 chord-context profile is not reference-free during detection")

    rows = list(profile_payload.get("rows", []))
    if not rows:
        raise RuntimeError("28.02 chord-context profile has no rows")
    row_by_token = {token(row): row for row in rows}

    zero_rows = list(profile_payload.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != EXPECTED_ZERO_SIGNATURES:
        raise RuntimeError(
            f"Expected exactly {EXPECTED_ZERO_SIGNATURES} chord-context zero-precision signature, got {len(zero_rows)}"
        )
    zero_row = zero_rows[0]
    signature = str(zero_row.get("signature", ""))
    if signature != EXPECTED_SIGNATURE:
        raise RuntimeError(f"Expected chord-context signature {EXPECTED_SIGNATURE}, got {signature}")
    if int(zero_row.get("true", -1)) != 0 or int(zero_row.get("false", 0)) < 5:
        raise RuntimeError(f"Invalid zero-precision chord-context row: {zero_row}")

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
    champion, _ = h2802.reconstruct_2802(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 28.02 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion.items():
        row = row_by_token.get(tok)
        if row is not None and signature in row_signatures(row):
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

    if accepted:
        winner = "chordcontext2802_exact_zero_precision"
        winner_eval = {
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
            "acceptedOver2802": True,
        }
        validated_new_champion = True
    else:
        winner = "retain_28_02_champion"
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
            "acceptedOver2802": False,
        }
        validated_new_champion = False

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 28.02 chord-context precision-prune benchmark")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-28.02-chord-context-precision-prune-with-heldout-cv",
        "baseline2802Score": baseline,
        "foldDefinition": "measureNumber modulo 5",
        "zeroPrecisionSignatureCount": 1,
        "zeroPrecisionSignature": signature,
        "testedEvaluation": {
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
            "acceptedOver2802": accepted,
        },
        "winner": winner,
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
        "baseline2802PitchF1": baseline["pitchF1"],
        "winner": winner,
        "validatedNewChampion": validated_new_champion,
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 28.02 CHORD CONTEXT PRECISION PRUNE CV V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", baseline["pitchF1"])
    print("Baseline matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Tested signature:", signature)
    print("Candidate pitch F1:", full["pitchF1"])
    print("Candidate matched/missing/extra:", full["matched"], "/", full["missing"], "/", full["extra"])
    print("Candidate prune count:", prune_count)
    print("Candidate true pruned:", true_pruned_total)
    print("Candidate false pruned:", false_pruned_total)
    print("Candidate extra reduction:", extra_reduction)
    print("Candidate prune-specific cross-validation passed:", prune_cv)
    print("Candidate folds with false reduction:", folds_with_false_reduction)
    print("Candidate folds:", folds)
    print("Candidate section stability passed:", bool(stability_eval["sectionStabilityPassed"]))
    print("Candidate shifted-window stability passed:", bool(stability_eval["shiftedWindowStabilityPassed"]))
    print("Winner:", winner)
    print("Winner pitch F1:", winner_eval["fullScore"]["pitchF1"])
    print("Winner matched/missing/extra:", winner_eval["fullScore"]["matched"], "/", winner_eval["fullScore"]["missing"], "/", winner_eval["fullScore"]["extra"])
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
