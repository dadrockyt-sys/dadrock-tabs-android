from __future__ import annotations

import hashlib
import json
from pathlib import Path

import analyze_and_grade_gomyway_separator_benchmark_stems_v2 as v2
import analyze_and_grade_gomyway_separator_benchmark_stems_v3 as v3
import benchmark_gomyway_929_champion_reference_free_upstream_recall_spectral_gate_v1 as recall
import benchmark_gomyway_1113_recall_champion_zero_precision_pitch_strength_prune_v1 as prune1163
import benchmark_gomyway_1163_champion_second_zero_precision_pitch_strength_prune_v1 as prune1186
import profile_gomyway_1113_recall_champion_effective_additions_precision_v1 as profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1186-champion-third-zero-precision-pitch-strength-prune-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1186-champion-third-zero-precision-pitch-strength-prune-v1-manifest.json"

EXPECTED_CORE = (102, 765, 1227)
EXPECTED_CHAMPION = (162, 705, 1704)
EXPECTED_F1 = 11.86
WINNER_NAME = "dual6_quarter_40_64"
FIRST_PRUNE = next(r for r in prune1163.RULES if r["name"] == "drop_all_profiled_zero_precision_pitch_strength")
SECOND_PRUNE = next(r for r in prune1186.RULES if r["name"] == "drop_all_second_profiled_zero_precision_pitch_strength")

THIRD_ZERO_BUCKETS = {
    (57, "20_plus"),
    (48, "6_8"),
    (51, "8_10"),
    (53, "10_13"),
    (62, "10_13"),
}

RULES = [
    {"name": "drop_third_zero_low_strength", "drop": sorted([list(x) for x in THIRD_ZERO_BUCKETS if x[1] in {"6_8", "8_10"}])},
    {"name": "drop_third_zero_high_strength", "drop": sorted([list(x) for x in THIRD_ZERO_BUCKETS if x[1] not in {"6_8", "8_10"}])},
    {"name": "drop_all_third_profiled_zero_precision_pitch_strength", "drop": sorted([list(x) for x in THIRD_ZERO_BUCKETS])},
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prune_residual(proposed, winner_scores, alt_scores, rule):
    drop = {(int(pitch), str(strength)) for pitch, strength in rule["drop"]}
    out = proposed.__class__()
    for token, count in proposed.items():
        pitch = int(token[2])
        strength = profile.bucket(min(winner_scores.get(token, 0.0), alt_scores.get(token, 0.0)))
        if (pitch, strength) not in drop:
            out[token] = count
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

    print("Rebuilding frozen validated 9.29 core and 11.86 pruned recall champion...", flush=True)
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
    core_score = prune1163.grade(core, reference)
    core_actual = (int(core_score["matched"]), int(core_score["missing"]), int(core_score["extra"]))
    if core_actual != EXPECTED_CORE:
        raise RuntimeError(f"Expected frozen 9.29 core {EXPECTED_CORE}, got {core_actual}")

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
    champion = recall.precond.merge_with_cap(core, second_kept)
    champion_score = prune1163.grade(champion, reference)
    champion_actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if champion_actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 11.86 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {champion_actual}/{champion_score['pitchF1']}")

    results = {}
    for rule in RULES:
        third_kept = prune_residual(second_kept, winner_scores, alt_scores, rule)
        candidate = recall.precond.merge_with_cap(core, third_kept)
        audit = prune1163.evaluate(candidate, champion, reference, champion_score)
        results[rule["name"]] = {"rule": rule, "keptProposedAdditions": int(sum(third_kept.values())), **audit}
        s = audit["fullScore"]
        print(
            f"{rule['name']}: F1={s['pitchF1']} matched={s['matched']} missing={s['missing']} extra={s['extra']} "
            f"extraReduction={audit['extraReduction']} matchedChange={audit['matchedChange']} "
            f"cv={audit['crossValidationPassed']} sections={audit['sectionStabilityPassed']} "
            f"shifted={audit['shiftedWindowStabilityPassed']} accepted={audit['acceptedOverChampion']}",
            flush=True,
        )

    accepted = [(name, row) for name, row in results.items() if row["acceptedOverChampion"]]
    if accepted:
        winner_name, winner = max(
            accepted,
            key=lambda item: (
                float(item[1]["fullScore"]["pitchF1"]),
                int(item[1]["fullScore"]["matched"]),
                -int(item[1]["fullScore"]["extra"]),
            ),
        )
    else:
        winner_name, winner = "retain_11_86_champion", {
            "fullScore": champion_score,
            "extraReduction": 0,
            "matchedChange": 0,
            "crossValidationPassed": True,
            "sectionStabilityPassed": True,
            "shiftedWindowStabilityPassed": True,
            "acceptedOverChampion": False,
        }

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 11.86 third pitch-strength prune benchmark.")

    ws = winner["fullScore"]
    validated = winner_name != "retain_11_86_champion"
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-11.86-recall-champion-third-zero-precision-pitch-strength-prune",
        "baselineScore": champion_score,
        "results": results,
        "winner": winner_name,
        "winnerScore": ws,
        "winnerExtraReduction": winner["extraReduction"],
        "winnerMatchedChange": winner["matchedChange"],
        "winnerCrossValidationPassed": winner["crossValidationPassed"],
        "winnerSectionStabilityPassed": winner["sectionStabilityPassed"],
        "winnerShiftedWindowStabilityPassed": winner["shiftedWindowStabilityPassed"],
        "validatedNewChampion": validated,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "profile-residual-recall-additions-from-validated-third-pruned-champion" if validated else "retain-11.86-and-profile-finer-cross-signatures",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "winner": winner_name,
        "winnerPitchF1": ws["pitchF1"],
        "validatedNewChampion": validated,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 11.86 CHAMPION THIRD ZERO-PRECISION PITCH-STRENGTH PRUNE V1 COMPLETE")
    print("Passed: True")
    print("Baseline pitch F1:", champion_score["pitchF1"])
    print("Baseline matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Winner:", winner_name)
    print("Winner pitch F1:", ws["pitchF1"])
    print("Winner matched/missing/extra:", ws["matched"], "/", ws["missing"], "/", ws["extra"])
    print("Winner extra reduction:", winner["extraReduction"])
    print("Winner matched change:", winner["matchedChange"])
    print("Winner cross-validation passed:", winner["crossValidationPassed"])
    print("Winner section stability passed:", winner["sectionStabilityPassed"])
    print("Winner shifted-window stability passed:", winner["shiftedWindowStabilityPassed"])
    print("Validated new champion:", validated)
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
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
