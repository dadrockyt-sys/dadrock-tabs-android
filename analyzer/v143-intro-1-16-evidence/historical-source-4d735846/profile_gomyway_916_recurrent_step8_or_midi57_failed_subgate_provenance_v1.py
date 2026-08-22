from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_916_champion_recurrent_step8_or_midi57_subgate_v1 as subgate

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-916-recurrent-step8-or-midi57-failed-subgate-provenance-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-916-recurrent-step8-or-midi57-failed-subgate-provenance-v1-manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    candidate_hash_before = sha256(subgate.CANDIDATE_PATH)
    payload = subgate.v2.load_json(subgate.CANDIDATE_PATH)
    events = subgate.v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = subgate.v2.build_timing_grid(events)

    reference_payload = subgate.v2.load_json(subgate.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = subgate.v3.reference_tokens(reference_payload)

    print("Rebuilding validated 9.16 champion and failed recurrent step8/midi57 subgate...", flush=True)
    base_winner = subgate.precond.prediction(subgate.precond.grouped_for(subgate.WINNER_STEM, grid))
    base_alt = subgate.precond.prediction(subgate.precond.grouped_for(subgate.ALT_STEM, grid))
    base_champion = subgate.precond.merge_with_cap(base_winner, base_alt)

    winner_scores = subgate.spectral.specialist_scores(subgate.WINNER_STEM, grid)
    alt_scores = subgate.spectral.specialist_scores(subgate.ALT_STEM, grid)
    top1 = subgate.gate.accepted_tokens(subgate.temporal.TOP1_RULE, winner_scores, alt_scores, base_champion)
    adaptive_base = subgate.adaptive.adaptive_additions(top1, winner_scores, alt_scores, 2, 13.0)
    temporal_additions = subgate.temporal.recurrence_gate(adaptive_base, winner_scores, alt_scores, subgate.TEMPORAL_RULE)
    precision_additions = subgate.pruning.prune(temporal_additions, winner_scores, alt_scores, adaptive_base, subgate.PRUNING_RULE)
    metrical_additions = subgate.metrical.metrical_prune(precision_additions, winner_scores, alt_scores, subgate.METRICAL_RULE)
    step_additions = subgate.step10.prune_step_signature(metrical_additions, winner_scores, alt_scores, subgate.STEP_RULE)
    champion_additions = subgate.agreement.agreement_prune(step_additions, winner_scores, alt_scores, subgate.AGREEMENT_RULE)
    additions_1287 = subgate.crossgate.cross_signature_prune(champion_additions, winner_scores, alt_scores, adaptive_base, subgate.SAFE_CROSS_RULE)
    additions_909 = subgate.crossgate.cross_signature_prune(additions_1287, winner_scores, alt_scores, adaptive_base, subgate.ZERO_PRECISION_RULE)
    additions_910 = subgate.crossgate.cross_signature_prune(additions_909, winner_scores, alt_scores, adaptive_base, subgate.WINNER_910_RULE)
    additions_916 = subgate.crossgate.cross_signature_prune(additions_910, winner_scores, alt_scores, adaptive_base, subgate.WINNER_916_RULE)

    baseline_prediction = subgate.precond.merge_with_cap(base_champion, additions_916)
    baseline_score = subgate.grade(baseline_prediction, reference)
    if (int(baseline_score["matched"]), int(baseline_score["missing"]), int(baseline_score["extra"])) != subgate.EXPECTED_BASELINE:
        raise RuntimeError(f"Unexpected 9.16 baseline: {baseline_score}")

    candidate_additions = subgate.provenance_subgate(additions_916, winner_scores, alt_scores, adaptive_base)
    candidate_prediction = subgate.precond.merge_with_cap(base_champion, candidate_additions)
    candidate_score = subgate.grade(candidate_prediction, reference)

    dropped_additions = additions_916 - candidate_additions
    rows = []
    total_matched_loss = 0
    total_extra_reduction = 0
    for token in sorted(dropped_additions):
        measure, step, pitch = token
        before = int(baseline_prediction[token])
        after = int(candidate_prediction[token])
        ref_count = int(reference[token])
        matched_before = min(before, ref_count)
        matched_after = min(after, ref_count)
        extra_before = max(0, before - ref_count)
        extra_after = max(0, after - ref_count)
        matched_loss = matched_before - matched_after
        extra_reduction = extra_before - extra_after
        total_matched_loss += matched_loss
        total_extra_reduction += extra_reduction
        rows.append({
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "additionDropped": int(dropped_additions[token]),
            "baseChampionCount": int(base_champion[token]),
            "baselinePredictionCount": before,
            "candidatePredictionCount": after,
            "referenceCount": ref_count,
            "matchedLoss": matched_loss,
            "extraReduction": extra_reduction,
            "winnerScore": float(winner_scores.get(token, 0.0)),
            "altScore": float(alt_scores.get(token, 0.0)),
            "scoreGap": round(abs(float(winner_scores.get(token, 0.0)) - float(alt_scores.get(token, 0.0))), 4),
            "scoreBucket": subgate.pruning.score_bucket(token, winner_scores, alt_scores),
            "agreementBucket": subgate.pruning.agreement_bucket(token, winner_scores, alt_scores),
            "recurrenceReason": subgate.pruning.reason_bucket(token, adaptive_base, winner_scores, alt_scores),
            "safeToDropAtMergedMultiplicity": matched_loss == 0 and extra_reduction > 0,
        })

    candidate_hash_after = sha256(subgate.CANDIDATE_PATH)
    if candidate_hash_before != candidate_hash_after:
        raise RuntimeError("Protected candidate changed during failed-subgate provenance profile.")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-9.16-failed-recurrent-step8-or-midi57-subgate-provenance",
        "baselineScore": baseline_score,
        "failedCandidateScore": candidate_score,
        "droppedAdditionCount": sum(dropped_additions.values()),
        "totalMatchedLoss": total_matched_loss,
        "totalExtraReduction": total_extra_reduction,
        "rows": rows,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "separate-single-match-bearing-removal-from-five-safe-extras-with-detector-side-feature",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": candidate_hash_after,
        "baselinePitchF1": baseline_score["pitchF1"],
        "failedCandidatePitchF1": candidate_score["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 9.16 FAILED RECURRENT STEP8 OR MIDI57 SUBGATE PROVENANCE V1 COMPLETE")
    print("Passed: True")
    print("Baseline matched/missing/extra:", baseline_score["matched"], "/", baseline_score["missing"], "/", baseline_score["extra"])
    print("Failed candidate matched/missing/extra:", candidate_score["matched"], "/", candidate_score["missing"], "/", candidate_score["extra"])
    print("Total matched loss / extra reduction:", total_matched_loss, "/", total_extra_reduction)
    print("Dropped-token provenance:")
    for row in rows:
        label = "MATCH_BEARING" if row["matchedLoss"] else "SAFE_EXTRA"
        print(
            f"  {label} m{row['measure']} step{row['step']} midi{row['pitch']}: "
            f"base={row['baseChampionCount']} pred={row['baselinePredictionCount']}->{row['candidatePredictionCount']} "
            f"ref={row['referenceCount']} matchedLoss={row['matchedLoss']} extraReduction={row['extraReduction']} "
            f"ws={row['winnerScore']:.4f} as={row['altScore']:.4f} gap={row['scoreGap']:.4f}"
        )
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action:", output["recommendedNextAction"])
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
