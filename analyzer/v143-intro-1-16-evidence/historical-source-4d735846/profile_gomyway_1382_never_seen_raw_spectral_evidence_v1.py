from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import profile_gomyway_1382_champion_missing_reference_opportunities_v1 as miss

v2 = miss.v2
v3 = miss.v3
p1382 = miss.p1382
recall = miss.recall
p1316 = miss.p1316
gate1328 = miss.gate1328
gate1345 = miss.gate1345
gate1370 = miss.gate1370
gate1382 = miss.gate1382

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-never-seen-raw-spectral-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-never-seen-raw-spectral-evidence-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82
WINNER_NAME = "dual6_quarter_40_64"
THRESHOLDS = (2.0, 4.0, 6.0, 8.0, 10.0, 13.0, 16.0, 20.0)


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


def recoverable_units(missing, final_prediction, source):
    return missing & (source - final_prediction)


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

    print("Rebuilding frozen validated 13.82 champion before never-seen raw spectral profiling...", flush=True)

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
    champion_score = grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    # Detection is frozen above. Professional reference is used only below as a downstream training label.
    missing = reference - champion
    profiled_sources = [base_winner, base_alt, base_champion, top1, adaptive_base, proposed]
    union_recoverable: Counter[tuple[int, int, int]] = Counter()
    for source in profiled_sources:
        union_recoverable |= recoverable_units(missing, champion, source)
    never_seen = missing - union_recoverable

    threshold_counts = {f"either_ge_{int(t)}": 0 for t in THRESHOLDS} | {f"both_ge_{int(t)}": 0 for t in THRESHOLDS}
    bucket_values: dict[str, list[tuple[float, float, int]]] = defaultdict(list)
    section_bucket_values: dict[str, list[tuple[float, float, int]]] = defaultdict(list)
    rows: list[dict[str, object]] = []

    print("Profiling raw dual-stem spectral evidence at 13.82 never-seen labeled locations...", flush=True)
    for (measure, step, pitch), count in never_seen.items():
        token = (measure, step, pitch)
        ws = float(winner_scores.get(token, 0.0))
        ats = float(alt_scores.get(token, 0.0))
        mx = max(ws, ats)
        mn = min(ws, ats)
        for t in THRESHOLDS:
            if mx >= t:
                threshold_counts[f"either_ge_{int(t)}"] += int(count)
            if mn >= t:
                threshold_counts[f"both_ge_{int(t)}"] += int(count)
        bucket = f"step{step}_midi{pitch}"
        section_bucket = f"{p1382.section_for(int(measure))}_step{step}_midi{pitch}"
        bucket_values[bucket].append((ws, ats, int(count)))
        section_bucket_values[section_bucket].append((ws, ats, int(count)))
        rows.append({
            "measure": int(measure), "step": int(step), "pitch": int(pitch), "missingUnits": int(count),
            "winnerScore": round(ws, 4), "alternateScore": round(ats, 4),
            "maxScore": round(mx, 4), "minScore": round(mn, 4),
        })

    def summarize(values):
        out = []
        for bucket, vals in values.items():
            units = sum(c for _, _, c in vals)
            max_mean = sum(max(w, a_) * c for w, a_, c in vals) / units
            min_mean = sum(min(w, a_) * c for w, a_, c in vals) / units
            out.append({
                "bucket": bucket,
                "missingUnits": int(units),
                "maxMeanScore": round(float(max_mean), 3),
                "minMeanScore": round(float(min_mean), 3),
                "eitherGe4Units": int(sum(c for w, a_, c in vals if max(w, a_) >= 4.0)),
                "eitherGe8Units": int(sum(c for w, a_, c in vals if max(w, a_) >= 8.0)),
                "bothGe4Units": int(sum(c for w, a_, c in vals if min(w, a_) >= 4.0)),
                "bothGe6Units": int(sum(c for w, a_, c in vals if min(w, a_) >= 6.0)),
            })
        out.sort(key=lambda r: (-int(r["missingUnits"]), -int(r["bothGe4Units"]), -float(r["maxMeanScore"]), str(r["bucket"])))
        return out

    bucket_rows = summarize(bucket_values)
    section_bucket_rows = summarize(section_bucket_values)
    rows.sort(key=lambda r: (-float(r["minScore"]), -float(r["maxScore"]), int(r["measure"]), int(r["step"]), int(r["pitch"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 13.82 never-seen raw spectral profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "benchmarkType": "validated-13.82-never-seen-raw-dual-stem-spectral-evidence-training-profile",
        "championScore": champion_score,
        "missingReferenceUnits": int(sum(missing.values())),
        "recoverableFromProfiledUpstream": int(sum(union_recoverable.values())),
        "neverSeenUnits": int(sum(never_seen.values())),
        "rawSpectralThresholdCoverage": threshold_counts,
        "topNeverSeenStepPitchBuckets": bucket_rows[:50],
        "topNeverSeenSectionStepPitchBuckets": section_bucket_rows[:60],
        "topNeverSeenLocationsByDualStemEvidence": rows[:100],
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-training-label-and-never-seen-audio-evidence-profiling-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "design-reference-free-new-upstream-recall-detector-from-1382-never-seen-dual-stem-spectral-coverage",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "neverSeenUnits": int(sum(never_seen.values())),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 NEVER-SEEN RAW SPECTRAL EVIDENCE PROFILE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Missing / recoverable / never-seen:", sum(missing.values()), "/", sum(union_recoverable.values()), "/", sum(never_seen.values()))
    print("Raw spectral threshold coverage:")
    for t in THRESHOLDS:
        print(f"  either>={int(t)}: {threshold_counts[f'either_ge_{int(t)}']}  both>={int(t)}: {threshold_counts[f'both_ge_{int(t)}']}")
    print("Top never-seen section/step/pitch buckets with raw evidence:")
    for row in section_bucket_rows[:20]:
        print(f"  {row['bucket']}: missing={row['missingUnits']} maxMean={row['maxMeanScore']} minMean={row['minMeanScore']} either>=4={row['eitherGe4Units']} both>=4={row['bothGe4Units']} both>=6={row['bothGe6Units']}")
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
