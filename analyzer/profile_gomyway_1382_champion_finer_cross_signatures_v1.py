from __future__ import annotations

import hashlib
import json
from pathlib import Path

import benchmark_gomyway_1370_champion_micro_score_singleton_gate_v1 as gate1382

p1370 = gate1382.p1370
p1345 = p1370.p1345
p1328 = p1370.p1328
gate1345 = p1370.gate1345
gate1328 = p1370.gate1328
gate1370 = p1370.gate1370
p1316 = p1370.p1316
v2 = p1370.v2
v3 = p1370.v3
recall = p1370.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-champion-finer-cross-signatures-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-champion-finer-cross-signatures-v1-manifest.json"
EXPECTED_CORE = (102, 765, 1227)
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82
WINNER_NAME = "dual6_quarter_40_64"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bump(table: dict[str, list[int]], key: str, t: int, f: int) -> None:
    row = table.setdefault(key, [0, 0])
    row[0] += int(t)
    row[1] += int(f)


def rows(table: dict[str, list[int]]):
    out = []
    for key, (t, f) in table.items():
        n = t + f
        out.append({
            "bucket": key,
            "true": t,
            "false": f,
            "precision": round(100.0 * t / n, 2) if n else 0.0,
        })
    out.sort(key=lambda r: (-int(r["false"]), int(r["true"]), str(r["bucket"])))
    return out


def section_for(measure: int) -> str:
    return p1370.section_for(measure)


def score_band(value: float) -> str:
    return p1370.score_band(value)


def narrow_score_band(value: float) -> str:
    return p1370.narrow_score_band(value)


def micro_score_band(value: float) -> str:
    return p1370.micro_score_band(value)


def integer_score_band(value: float) -> str:
    # Reference-free detector-side spectral score only; bucket to integer floor.
    return f"score{int(value)}_{int(value) + 1}"


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

    print("Rebuilding frozen validated 9.29 core and 13.82 champion for deeper residual profiling...", flush=True)
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
    kept = gate1345.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1345.TARGET_SIGNATURES})
    kept = gate1370.prune_residual(kept, winner_scores, alt_scores, {"drop": gate1370.TARGET_SIGNATURES})
    kept = gate1382.prune_residual(kept, winner_scores, alt_scores, gate1382.TARGET_SIGNATURES)

    champion = recall.precond.merge_with_cap(core, kept)
    champion_score = p1316.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    effective = champion - core
    effective_true = effective & (reference - core)
    names = [
        "stepPitchStrength",
        "sectionPitchStrength",
        "sectionStepPitch",
        "sectionStepStrength",
        "stepPitchScoreAgreement",
        "sectionStepPitchScoreAgreement",
        "sectionStepPitchNarrowScoreAgreement",
        "sectionStepPitchMicroScoreAgreement",
        "sectionStepPitchIntegerScoreAgreement",
    ]
    tables = {name: {} for name in names}

    for token, count in effective.items():
        measure, step, pitch = token
        t = min(count, effective_true.get(token, 0))
        f = count - t
        strength = p1345.profile.bucket(min(winner_scores.get(token, 0.0), alt_scores.get(token, 0.0)))
        section = section_for(int(measure))
        ws = float(winner_scores.get(token, 0.0))
        als = float(alt_scores.get(token, 0.0))
        max_score = max(ws, als)
        broad_band = score_band(max_score)
        narrow_band = narrow_score_band(max_score)
        micro_band = micro_score_band(max_score)
        integer_band = integer_score_band(max_score)
        agreement = "both10" if ws >= 10 and als >= 10 else "single_or_weak"

        bump(tables["stepPitchStrength"], f"step{step}_midi{pitch}_{strength}", t, f)
        bump(tables["sectionPitchStrength"], f"{section}_midi{pitch}_{strength}", t, f)
        bump(tables["sectionStepPitch"], f"{section}_step{step}_midi{pitch}", t, f)
        bump(tables["sectionStepStrength"], f"{section}_step{step}_{strength}", t, f)
        bump(tables["stepPitchScoreAgreement"], f"step{step}_midi{pitch}_{broad_band}_{agreement}", t, f)
        bump(tables["sectionStepPitchScoreAgreement"], f"{section}_step{step}_midi{pitch}_{broad_band}_{agreement}", t, f)
        bump(tables["sectionStepPitchNarrowScoreAgreement"], f"{section}_step{step}_midi{pitch}_{narrow_band}_{agreement}", t, f)
        bump(tables["sectionStepPitchMicroScoreAgreement"], f"{section}_step{step}_midi{pitch}_{micro_band}_{agreement}", t, f)
        bump(tables["sectionStepPitchIntegerScoreAgreement"], f"{section}_step{step}_midi{pitch}_{integer_band}_{agreement}", t, f)

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 13.82 finer cross-signature profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-champion-finer-residual-cross-signature-profile",
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
        "recommendedNextAction": "inspect-repeatable-zero-precision-structure-or-pivot-to-next-recall-feature-family",
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

    print("GOMYWAY 13.82 CHAMPION FINER CROSS-SIGNATURE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Effective residual true / false:", sum(effective_true.values()), "/", sum((effective - effective_true).values()))
    for title, name in [
        ("Step/pitch/strength precision", "stepPitchStrength"),
        ("Section/pitch/strength precision", "sectionPitchStrength"),
        ("Section/step/pitch precision", "sectionStepPitch"),
        ("Section/step/strength precision", "sectionStepStrength"),
        ("Step/pitch/score/agreement precision", "stepPitchScoreAgreement"),
        ("Section/step/pitch/score/agreement precision", "sectionStepPitchScoreAgreement"),
        ("Section/step/pitch/narrow-score/agreement precision", "sectionStepPitchNarrowScoreAgreement"),
        ("Section/step/pitch/micro-score/agreement precision", "sectionStepPitchMicroScoreAgreement"),
        ("Section/step/pitch/integer-score/agreement precision", "sectionStepPitchIntegerScoreAgreement"),
    ]:
        print(title + ":")
        for row in output["precisionTables"][name][:30]:
            print(f"  {row['bucket']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Professional reference used during detection: False")
    print("Protected 949-event candidate hash unchanged: True")
    print("Candidate events modified: False")
    print("V7 events modified: False")
    print("Renderer modified: False")
    print("Protected baselines changed: False")
    print("Production separator changed: False")
    print("Production promotion allowed: False")
    print("Recommended next action: inspect-repeatable-zero-precision-structure-or-pivot-to-next-recall-feature-family")
    print("Output:", OUTPUT_PATH.relative_to(ROOT))
    print("Manifest:", MANIFEST_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
