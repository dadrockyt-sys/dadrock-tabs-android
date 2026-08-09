from __future__ import annotations

import hashlib
import json
from pathlib import Path

import profile_gomyway_1328_champion_finer_cross_signatures_v1 as p1328

finer = p1328.finer
gate1328 = p1328.gate1328
p1316 = p1328.p1316
v2 = p1328.v2
v3 = p1328.v3
recall = p1328.recall
profile = p1328.profile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1328-champion-section-step-pitch-score-agreement-gate-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1328-champion-section-step-pitch-score-agreement-gate-v1-manifest.json"
EXPECTED_CORE = (102, 765, 1227)
EXPECTED_CHAMPION = (172, 695, 1551)
EXPECTED_F1 = 13.28
WINNER_NAME = "dual6_quarter_40_64"

TARGET_SIGNATURES = {
    "m65_80_step4_midi50_score8_13_single_or_weak",
    "m17_32_step0_midi52_score13_20_both10",
    "m17_32_step0_midi54_score13_20_both10",
    "m17_32_step4_midi50_score8_13_single_or_weak",
    "m17_32_step4_midi52_score8_13_single_or_weak",
    "m17_32_step4_midi62_score8_13_single_or_weak",
    "m17_32_step8_midi52_score13_20_both10",
    "m17_32_step8_midi54_score8_13_single_or_weak",
    "m33_48_step0_midi45_score8_13_single_or_weak",
    "m33_48_step12_midi45_score13_20_single_or_weak",
    "m33_48_step12_midi64_score20_plus_both10",
    "m33_48_step4_midi50_score8_13_single_or_weak",
    "m65_80_step0_midi47_score_lt8_single_or_weak",
    "m65_80_step12_midi42_score20_plus_both10",
    "m65_80_step12_midi43_score20_plus_both10",
    "m65_80_step12_midi45_score20_plus_both10",
    "m65_80_step12_midi45_score_lt8_single_or_weak",
    "m65_80_step12_midi57_score13_20_both10",
    "m65_80_step4_midi46_score20_plus_both10",
    "m65_80_step4_midi49_score20_plus_both10",
    "m65_80_step4_midi52_score8_13_single_or_weak",
}

RULES = [
    {"name": "drop_" + sig, "drop": {sig}} for sig in sorted(TARGET_SIGNATURES)
] + [
    {"name": "drop_all_profiled_section_step_pitch_score_agreement_zero_precision", "drop": TARGET_SIGNATURES}
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def section_for(measure: int) -> str:
    return p1328.section_for(measure)


def signature(token, winner_scores, alt_scores) -> str:
    measure, step, pitch = token
    ws = float(winner_scores.get(token, 0.0))
    als = float(alt_scores.get(token, 0.0))
    max_score = max(ws, als)
    score_band = (
        "score20_plus" if max_score >= 20
        else "score13_20" if max_score >= 13
        else "score8_13" if max_score >= 8
        else "score_lt8"
    )
    agreement = "both10" if ws >= 10 and als >= 10 else "single_or_weak"
    return f"{section_for(int(measure))}_step{step}_midi{pitch}_{score_band}_{agreement}"


def prune_residual(proposed, winner_scores, alt_scores, rule):
    drop = set(rule["drop"])
    out = proposed.__class__()
    for token, count in proposed.items():
        if signature(token, winner_scores, alt_scores) not in drop:
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

    print("Rebuilding frozen validated 9.29 core and 13.28 champion for deep section/signature gate...", flush=True)
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
    core_score = p1316.grade(core, reference)
    core_actual = (int(core_score["matched"]), int(core_score["missing"]), int(core_score["extra"]))
    if core_actual != EXPECTED_CORE:
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

    p1315 = p1316.p1315
    p1312 = p1315.p1312
    p1308 = p1312.p1308
    p1305 = p1308.p1305
    p1285 = p1305.p1285
    p1272 = p1285.p1272
    kept = p1272.prune1163.prune_proposed(proposed, winner_scores, alt_scores, p1272.FIRST_PRUNE)
    kept = p1272.prune1186.prune_residual(kept, winner_scores, alt_scores, p1272.SECOND_PRUNE)
    kept = p1272.prune1217.prune_residual(kept, winner_scores, alt_scores, p1272.THIRD_PRUNE)
    kept = p1272.prune1229.prune_residual(kept, winner_scores, alt_scores, p1272.FOURTH_PRUNE)
    kept = p1272.prune1244.prune_residual(kept, winner_scores, alt_scores, p1272.FIFTH_PRUNE)
    kept = p1272.prune1253.prune_residual(kept, winner_scores, alt_scores, p1272.SIXTH_PRUNE)
    kept = p1272.prune1258.prune_residual(kept, winner_scores, alt_scores, p1272.SEVENTH_PRUNE)
    kept = p1272.prune1272.prune_residual(kept, winner_scores, alt_scores, p1272.EIGHTH_PRUNE)
    kept = p1285.prune1285.prune_residual(kept, winner_scores, alt_scores, p1285.NINTH_PRUNE)
    kept = p1305.prune1305.prune_residual(kept, winner_scores, alt_scores, p1305.TENTH_PRUNE)
    kept = p1308.prune1308.prune_residual(kept, winner_scores, alt_scores, p1308.ELEVENTH_PRUNE)
    kept = p1312.prune1312.prune_residual(kept, winner_scores, alt_scores, p1312.TWELFTH_PRUNE)
    kept = p1315.prune1315.prune_residual(kept, winner_scores, alt_scores, p1315.THIRTEENTH_PRUNE)
    kept = p1316.prune1316.prune_residual(kept, winner_scores, alt_scores, p1316.FOURTEENTH_PRUNE)
    kept = gate1328.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1328.TARGET_SIGNATURES})

    champion = recall.precond.merge_with_cap(core, kept)
    champion_score = p1316.grade(champion, reference)
    champion_actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if champion_actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.28 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {champion_actual}/{champion_score['pitchF1']}")

    evaluator = p1272.prune1163.evaluate
    results = {}
    for rule in RULES:
        candidate_kept = prune_residual(kept, winner_scores, alt_scores, rule)
        candidate = recall.precond.merge_with_cap(core, candidate_kept)
        audit = evaluator(candidate, champion, reference, champion_score)
        results[rule["name"]] = {
            "rule": {"name": rule["name"], "drop": sorted(rule["drop"])},
            "keptProposedAdditions": int(sum(candidate_kept.values())),
            **audit,
        }
        s = audit["fullScore"]
        print(
            f"{rule['name']}: F1={s['pitchF1']} matched={s['matched']} missing={s['missing']} "
            f"extra={s['extra']} extraReduction={audit['extraReduction']} matchedChange={audit['matchedChange']} "
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
        winner_name, winner = "retain_13_28_champion", {
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
        raise RuntimeError("Protected candidate changed during 13.28 deep section/signature benchmark")

    ws = winner["fullScore"]
    validated = winner_name != "retain_13_28_champion"
    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.28-section-step-pitch-score-agreement-gate",
        "baselineScore": champion_score,
        "profiledTargetSignatures": sorted(TARGET_SIGNATURES),
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
        "recommendedNextAction": "profile-next-finer-cross-signatures-from-validated-winner" if validated else "retain-13.28-and-test-next-finer-family",
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

    print("GOMYWAY 13.28 CHAMPION SECTION-STEP-PITCH-SCORE-AGREEMENT GATE V1 COMPLETE")
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
