from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import profile_gomyway_1382_champion_finer_cross_signatures_v1 as p1382

v2 = p1382.v2
v3 = p1382.v3
recall = p1382.recall
p1316 = p1382.p1316
gate1328 = p1382.gate1328
gate1345 = p1382.gate1345
gate1370 = p1382.gate1370
gate1382 = p1382.gate1382

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-missing-reference-opportunities-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-missing-reference-opportunities-v1-manifest.json"
EXPECTED_CORE = (102, 765, 1227)
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82
WINNER_NAME = "dual6_quarter_40_64"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted: Counter[tuple[int, int, int]], reference: Counter[tuple[int, int, int]]) -> dict[str, float | int]:
    matched = sum((predicted & reference).values())
    predicted_count = sum(predicted.values())
    expected = sum(reference.values())
    return {
        "pitchF1": round(100.0 * v2.f1(matched, predicted_count, expected), 2),
        "matched": matched,
        "missing": sum((reference - predicted).values()),
        "extra": sum((predicted - reference).values()),
        "predictions": predicted_count,
    }


def recoverable_units(
    missing: Counter[tuple[int, int, int]],
    final_prediction: Counter[tuple[int, int, int]],
    source: Counter[tuple[int, int, int]],
) -> Counter[tuple[int, int, int]]:
    return missing & (source - final_prediction)


def top_rows(counter: Counter[str], limit: int = 30) -> list[dict[str, int | str]]:
    return [{"bucket": key, "count": int(value)} for key, value in counter.most_common(limit)]


def profile_counter(counter: Counter[tuple[int, int, int]]) -> dict[str, list[dict[str, int | str]]]:
    by_section: Counter[str] = Counter()
    by_step: Counter[str] = Counter()
    by_pitch: Counter[str] = Counter()
    by_step_pitch: Counter[str] = Counter()
    by_section_step_pitch: Counter[str] = Counter()
    for (measure, step, pitch), count in counter.items():
        section = p1382.section_for(int(measure))
        by_section[section] += count
        by_step[f"step{step}"] += count
        by_pitch[f"midi{pitch}"] += count
        by_step_pitch[f"step{step}_midi{pitch}"] += count
        by_section_step_pitch[f"{section}_step{step}_midi{pitch}"] += count
    return {
        "topSections": top_rows(by_section, 12),
        "topSteps": top_rows(by_step, 16),
        "topPitches": top_rows(by_pitch, 24),
        "topStepPitch": top_rows(by_step_pitch, 30),
        "topSectionStepPitch": top_rows(by_section_step_pitch, 40),
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    print("Rebuilding frozen validated 9.29 core and 13.82 champion before downstream miss profiling...", flush=True)

    base_winner = recall.precond.prediction(recall.precond.grouped_for(recall.WINNER_STEM, grid))
    base_alt = recall.precond.prediction(recall.precond.grouped_for(recall.ALT_STEM, grid))
    base_champion = recall.precond.merge_with_cap(base_winner, base_alt)

    mid_winner = recall.spectral.specialist_scores(recall.WINNER_STEM, grid)
    mid_alt = recall.spectral.specialist_scores(recall.ALT_STEM, grid)
    top1 = recall.gate.accepted_tokens(recall.temporal.TOP1_RULE, mid_winner, mid_alt, base_champion)
    adaptive_base = recall.adaptive.adaptive_additions(top1, mid_winner, mid_alt, 2, 13.0)

    a = recall.temporal.recurrence_gate(adaptive_base, mid_winner, mid_alt, recall.TEMPORAL_RULE)
    a = recall.pruning.prune(a, mid_winner, mid_alt, adaptive_base, recall.PRUNING_RULE)
    a = recall.metrical.metrical_prune(a, mid_winner, mid_alt, recall.METRICAL_RULE)
    a = recall.step10.prune_step_signature(a, mid_winner, mid_alt, recall.STEP_RULE)
    a = recall.agreement.agreement_prune(a, mid_winner, mid_alt, recall.AGREEMENT_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.SAFE_CROSS_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.ZERO_PRECISION_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_910_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_916_RULE)
    a = recall.gate919.refined_subgate(a, mid_winner, mid_alt, adaptive_base)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_921_RULE)
    a = recall.crossgate.cross_signature_prune(a, mid_winner, mid_alt, adaptive_base, recall.WINNER_923_RULE)
    a = recall.gate926.deep_prune(a, mid_winner, mid_alt, recall.WINNER_926_RULE)
    a = recall.gate927.combined_prune(a, mid_winner, mid_alt, adaptive_base)
    a = recall.gate929.residual_prune(a, mid_winner, mid_alt, adaptive_base)

    core = recall.precond.merge_with_cap(base_champion, a)
    core_score = grade(core, reference)
    core_actual = (int(core_score["matched"]), int(core_score["missing"]), int(core_score["extra"]))
    if core_actual != EXPECTED_CORE:
        raise RuntimeError(f"Frozen 9.29 core mismatch: {core_score}")

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)
    winner_scores: dict[tuple[int, int, int], float] = {}
    alt_scores: dict[tuple[int, int, int], float] = {}
    for (measure, step), center in grid.items():
        if 17 <= measure <= 113:
            for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
                token = (measure, step, pitch)
                winner_scores[token] = recall.spectral.spectral_score(winner_audio, winner_sr, float(center), pitch)
                alt_scores[token] = recall.spectral.spectral_score(alt_audio, alt_sr, float(center), pitch)

    variant = next(v for v in recall.VARIANTS if v["name"] == WINNER_NAME)
    proposed = recall.recall_additions(grid, winner_scores, alt_scores, core, variant)

    p1315 = p1316.p1315
    p1312 = p1315.p1312
    p1308 = p1312.p1308
    p1305 = p1308.p1305
    p1285 = p1305.p1285
    p1272 = p1285.p1272

    stages: list[tuple[str, Counter[tuple[int, int, int]]]] = []
    kept = p1272.prune1163.prune_proposed(proposed, winner_scores, alt_scores, p1272.FIRST_PRUNE)
    stages.append(("after1163", kept.copy()))
    kept = p1272.prune1186.prune_residual(kept, winner_scores, alt_scores, p1272.SECOND_PRUNE)
    stages.append(("after1186", kept.copy()))
    kept = p1272.prune1217.prune_residual(kept, winner_scores, alt_scores, p1272.THIRD_PRUNE)
    stages.append(("after1217", kept.copy()))
    kept = p1272.prune1229.prune_residual(kept, winner_scores, alt_scores, p1272.FOURTH_PRUNE)
    stages.append(("after1229", kept.copy()))
    kept = p1272.prune1244.prune_residual(kept, winner_scores, alt_scores, p1272.FIFTH_PRUNE)
    stages.append(("after1244", kept.copy()))
    kept = p1272.prune1253.prune_residual(kept, winner_scores, alt_scores, p1272.SIXTH_PRUNE)
    stages.append(("after1253", kept.copy()))
    kept = p1272.prune1258.prune_residual(kept, winner_scores, alt_scores, p1272.SEVENTH_PRUNE)
    stages.append(("after1258", kept.copy()))
    kept = p1272.prune1272.prune_residual(kept, winner_scores, alt_scores, p1272.EIGHTH_PRUNE)
    stages.append(("after1272", kept.copy()))
    kept = p1285.prune1285.prune_residual(kept, winner_scores, alt_scores, p1285.NINTH_PRUNE)
    stages.append(("after1285", kept.copy()))
    kept = p1305.prune1305.prune_residual(kept, winner_scores, alt_scores, p1305.TENTH_PRUNE)
    stages.append(("after1305", kept.copy()))
    kept = p1308.prune1308.prune_residual(kept, winner_scores, alt_scores, p1308.ELEVENTH_PRUNE)
    stages.append(("after1308", kept.copy()))
    kept = p1312.prune1312.prune_residual(kept, winner_scores, alt_scores, p1312.TWELFTH_PRUNE)
    stages.append(("after1312", kept.copy()))
    kept = p1315.prune1315.prune_residual(kept, winner_scores, alt_scores, p1315.THIRTEENTH_PRUNE)
    stages.append(("after1315", kept.copy()))
    kept = p1316.prune1316.prune_residual(kept, winner_scores, alt_scores, p1316.FOURTEENTH_PRUNE)
    stages.append(("after1316", kept.copy()))
    kept = gate1328.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1328.TARGET_SIGNATURES})
    stages.append(("after1328", kept.copy()))
    kept = gate1345.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1345.TARGET_SIGNATURES})
    stages.append(("after1345", kept.copy()))
    kept = gate1370.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1370.TARGET_SIGNATURES})
    stages.append(("after1370", kept.copy()))
    kept = gate1382.prune_residual(kept, winner_scores, alt_scores, gate1382.TARGET_SIGNATURES)
    stages.append(("after1382", kept.copy()))

    champion = recall.precond.merge_with_cap(core, kept)
    champion_score = grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    # Reference use begins only after the detector and complete 13.82 champion are frozen.
    missing = reference - champion

    sources: list[tuple[str, Counter[tuple[int, int, int]]]] = [
        ("winnerStem", base_winner),
        ("alternateStem", base_alt),
        ("baseMerged", base_champion),
        ("top1Spectral", top1),
        ("adaptiveAdditions", adaptive_base),
        ("rawRecallProposed", proposed),
    ] + stages

    opportunities: dict[str, dict[str, object]] = {}
    union_recoverable: Counter[tuple[int, int, int]] = Counter()
    for name, source in sources:
        recoverable = recoverable_units(missing, champion, source)
        union_recoverable |= recoverable
        opportunities[name] = {
            "recoverableMissingUnits": int(sum(recoverable.values())),
            "recoverableTokenKeys": int(len(recoverable)),
            **profile_counter(recoverable),
        }

    raw_recoverable = recoverable_units(missing, champion, proposed)
    kept_recoverable = recoverable_units(missing, champion, kept)
    pruned_recall_recoverable = raw_recoverable - kept_recoverable
    never_seen = missing - union_recoverable

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 13.82 missing-reference opportunity profile")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-champion-downstream-missing-reference-opportunity-profile",
        "championScore": champion_score,
        "missingReferenceUnits": int(sum(missing.values())),
        "recoverableFromAnyProfiledUpstreamSource": int(sum(union_recoverable.values())),
        "neverSeenInProfiledUpstreamSources": int(sum(never_seen.values())),
        "rawRecallProposedRecoverableMissingUnits": int(sum(raw_recoverable.values())),
        "prunedRecallRecoverableMissingUnits": int(sum(pruned_recall_recoverable.values())),
        "opportunities": opportunities,
        "missingProfile": profile_counter(missing),
        "prunedRecallRecoverableProfile": profile_counter(pruned_recall_recoverable),
        "neverSeenProfile": profile_counter(never_seen),
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-miss-profiling-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "choose-between-reopening-existing-recall-gate-and-new-upstream-detector-from-1382-miss-split",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "championMatched": champion_score["matched"],
        "championMissing": champion_score["missing"],
        "championExtra": champion_score["extra"],
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 CHAMPION MISSING REFERENCE OPPORTUNITIES V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Missing reference units:", sum(missing.values()))
    print("Recoverable from any profiled upstream source:", sum(union_recoverable.values()))
    print("Never seen in profiled upstream sources:", sum(never_seen.values()))
    print("Raw recall proposed recoverable misses:", sum(raw_recoverable.values()))
    print("Pruned recall recoverable misses:", sum(pruned_recall_recoverable.values()))
    print("Recall opportunity by source:")
    for name, _source in sources:
        print(f"  {name}: recoverable={opportunities[name]['recoverableMissingUnits']}")
    print("Top pruned-recall recoverable section/step/pitch buckets:")
    for row in output["prunedRecallRecoverableProfile"]["topSectionStepPitch"][:20]:
        print(f"  {row['bucket']}: missing={row['count']}")
    print("Top never-seen section/step/pitch buckets:")
    for row in output["neverSeenProfile"]["topSectionStepPitch"][:20]:
        print(f"  {row['bucket']}: missing={row['count']}")
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
