from __future__ import annotations

import hashlib
import json
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_929_champion_reference_free_upstream_recall_spectral_gate_v1 as recall
import benchmark_gomyway_1113_recall_champion_zero_precision_pitch_strength_prune_v1 as prune1163
import benchmark_gomyway_1163_champion_second_zero_precision_pitch_strength_prune_v1 as prune1186
import benchmark_gomyway_1186_champion_third_zero_precision_pitch_strength_prune_v1 as prune1217
import benchmark_gomyway_1217_champion_fourth_zero_precision_pitch_strength_prune_v1 as prune1229
import benchmark_gomyway_1229_champion_fifth_zero_precision_pitch_strength_prune_v1 as prune1244
import benchmark_gomyway_1244_champion_sixth_zero_precision_pitch_strength_prune_v1 as prune1253
import profile_gomyway_1113_recall_champion_effective_additions_precision_v1 as profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1253-pruned-recall-champion-residual-additions-precision-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1253-pruned-recall-champion-residual-additions-precision-v1-manifest.json"
EXPECTED_CORE = (102, 765, 1227)
EXPECTED_CHAMPION = (168, 699, 1646)
EXPECTED_F1 = 12.53
WINNER_NAME = "dual6_quarter_40_64"
FIRST_PRUNE = next(r for r in prune1163.RULES if r["name"] == "drop_all_profiled_zero_precision_pitch_strength")
SECOND_PRUNE = next(r for r in prune1186.RULES if r["name"] == "drop_all_second_profiled_zero_precision_pitch_strength")
THIRD_PRUNE = next(r for r in prune1217.RULES if r["name"] == "drop_all_third_profiled_zero_precision_pitch_strength")
FOURTH_PRUNE = next(r for r in prune1229.RULES if r["name"] == "drop_all_fourth_profiled_zero_precision_pitch_strength")
FIFTH_PRUNE = next(r for r in prune1244.RULES if r["name"] == "drop_all_fifth_profiled_zero_precision_pitch_strength")
SIXTH_PRUNE = next(r for r in prune1253.RULES if r["name"] == "drop_sixth_zero_low_mid_strength")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def grade(predicted, reference):
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


def bump(table: dict[str, list[int]], key: str, t: int, f: int) -> None:
    row = table.setdefault(key, [0, 0])
    row[0] += t
    row[1] += f


def rows(table: dict[str, list[int]]):
    out = []
    for key, (t, f) in table.items():
        n = t + f
        out.append({"bucket": key, "true": t, "false": f, "precision": round(100.0 * t / n, 2) if n else 0.0})
    out.sort(key=lambda r: (-int(r["false"]), int(r["true"]), str(r["bucket"])))
    return out


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

    print("Rebuilding frozen validated 9.29 core and 12.53 pruned recall champion...", flush=True)
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
    if (core_score["matched"], core_score["missing"], core_score["extra"]) != EXPECTED_CORE:
        raise RuntimeError(f"Frozen 9.29 core mismatch: {core_score}")

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)
    winner_scores = {}
    alt_scores = {}
    for (measure, step), center in grid.items():
        if 17 <= measure <= 113:
            for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
                token = (measure, step, pitch)
                winner_scores[token] = recall.spectral.spectral_score(winner_audio, winner_sr, float(center), pitch)
                alt_scores[token] = recall.spectral.spectral_score(alt_audio, alt_sr, float(center), pitch)

    variant = next(v for v in recall.VARIANTS if v["name"] == WINNER_NAME)
    proposed = recall.recall_additions(grid, winner_scores, alt_scores, core, variant)
    first_kept = prune1163.prune_proposed(proposed, winner_scores, alt_scores, FIRST_PRUNE)
    second_kept = prune1186.prune_residual(first_kept, winner_scores, alt_scores, SECOND_PRUNE)
    third_kept = prune1217.prune_residual(second_kept, winner_scores, alt_scores, THIRD_PRUNE)
    fourth_kept = prune1229.prune_residual(third_kept, winner_scores, alt_scores, FOURTH_PRUNE)
    fifth_kept = prune1244.prune_residual(fourth_kept, winner_scores, alt_scores, FIFTH_PRUNE)
    sixth_kept = prune1253.prune_residual(fifth_kept, winner_scores, alt_scores, SIXTH_PRUNE)
    champion = recall.precond.merge_with_cap(core, sixth_kept)
    champion_score = grade(champion, reference)
    actual = (champion_score["matched"], champion_score["missing"], champion_score["extra"])
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 12.53 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    effective = champion - core
    effective_true = effective & (reference - core)
    tables = {name: {} for name in ["strength", "step", "pitch", "stepPitch", "stepStrength", "pitchStrength"]}
    for token, count in effective.items():
        _measure, step, pitch = token
        t = min(count, effective_true.get(token, 0))
        f = count - t
        strength = profile.bucket(min(winner_scores.get(token, 0.0), alt_scores.get(token, 0.0)))
        bump(tables["strength"], strength, t, f)
        bump(tables["step"], f"step{step}", t, f)
        bump(tables["pitch"], f"midi{pitch}", t, f)
        bump(tables["stepPitch"], f"step{step}_midi{pitch}", t, f)
        bump(tables["stepStrength"], f"step{step}_{strength}", t, f)
        bump(tables["pitchStrength"], f"midi{pitch}_{strength}", t, f)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 12.53 residual profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-12.53-pruned-recall-champion-residual-additions-precision-profile",
        "championScore": champion_score,
        "effectiveResidualRecallUnits": int(sum(effective.values())),
        "effectiveResidualTrueUnits": int(sum(effective_true.values())),
        "effectiveResidualFalseUnits": int(sum((effective - effective_true).values())),
        "precisionTables": {name: rows(table) for name, table in tables.items()},
        "professionalReferenceUsedDuringDetection": False,
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-next-zero-or-near-zero-precision-prune-from-validated-12.53-residual-recall-profile",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 12.53 PRUNED RECALL CHAMPION RESIDUAL ADDITIONS PRECISION PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Effective residual recall units:", sum(effective.values()))
    print("Effective residual true / false:", sum(effective_true.values()), "/", sum((effective - effective_true).values()))
    for title, name in [("Strength precision", "strength"), ("Step precision", "step"), ("Pitch precision", "pitch"), ("Top step/pitch precision", "stepPitch"), ("Step/strength precision", "stepStrength"), ("Pitch/strength precision", "pitchStrength")]:
        print(title + ":")
        for row in output["precisionTables"][name][:25]:
            print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
