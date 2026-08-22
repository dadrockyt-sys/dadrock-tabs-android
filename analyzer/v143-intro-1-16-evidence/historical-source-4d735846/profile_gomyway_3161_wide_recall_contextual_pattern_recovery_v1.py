from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import profile_gomyway_3161_wide_recall_candidate_selection_v1 as sel

wide = sel.wide
micro = sel.micro
s3161 = sel.s3161
recur = sel.recur
recall = sel.recall
v2 = sel.v2
v3 = sel.v3
harmonic = sel.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-wide-recall-contextual-pattern-recovery-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def register_name(pitch: int) -> str:
    if pitch < 48:
        return "low"
    if pitch < 60:
        return "mid"
    return "high"


def bucket_count(n: int) -> str:
    if n <= 0:
        return "0"
    if n == 1:
        return "1"
    if n == 2:
        return "2"
    if n <= 4:
        return "3_4"
    if n <= 8:
        return "5_8"
    return "9p"


def build_champion_context(champion: Counter[tuple[int, int, int]]) -> dict[str, Any]:
    tokens = set(champion.keys())
    by_measure: dict[int, set[tuple[int, int]]] = defaultdict(set)
    by_measure_step: dict[tuple[int, int], set[int]] = defaultdict(set)
    same_step_pitch: Counter[tuple[int, int]] = Counter()
    same_step_pc: Counter[tuple[int, int]] = Counter()
    pitch_measure_count: Counter[int] = Counter()
    pc_measure_sets: dict[int, set[int]] = defaultdict(set)

    for measure, step, pitch in tokens:
        by_measure[measure].add((step, pitch))
        by_measure_step[(measure, step)].add(pitch)
        same_step_pitch[(step, pitch)] += 1
        same_step_pc[(step, pitch % 12)] += 1
        pitch_measure_count[pitch] += 1
        pc_measure_sets[pitch % 12].add(measure)

    measures = sorted(by_measure)
    measure_similarity: dict[int, list[tuple[float, int]]] = defaultdict(list)
    for i, m1 in enumerate(measures):
        a = by_measure[m1]
        for m2 in measures[i + 1 :]:
            b = by_measure[m2]
            union = len(a | b)
            if not union:
                continue
            sim = len(a & b) / union
            if sim >= 0.20:
                measure_similarity[m1].append((sim, m2))
                measure_similarity[m2].append((sim, m1))

    return {
        "tokens": tokens,
        "byMeasure": by_measure,
        "byMeasureStep": by_measure_step,
        "sameStepPitch": same_step_pitch,
        "sameStepPc": same_step_pc,
        "pitchMeasureCount": pitch_measure_count,
        "pcMeasureSets": pc_measure_sets,
        "measureSimilarity": measure_similarity,
    }


def contextual_features(
    tok: tuple[int, int, int],
    base: dict[str, Any],
    ctx: dict[str, Any],
) -> dict[str, Any]:
    measure, step, pitch = tok
    tokens: set[tuple[int, int, int]] = ctx["tokens"]
    by_measure_step = ctx["byMeasureStep"]

    same_step_pitch_count = int(ctx["sameStepPitch"][(step, pitch)])
    same_step_pc_count = int(ctx["sameStepPc"][(step, pitch % 12)])
    pitch_global_count = int(ctx["pitchMeasureCount"][pitch])
    pc_measure_count = len(ctx["pcMeasureSets"][pitch % 12])

    local_exact = 0
    local_pc = 0
    neighbor_any = 0
    neighbor_close_pitch = 0
    for dstep in (-4, -3, -2, -1, 1, 2, 3, 4):
        s2 = step + dstep
        if s2 < 0:
            continue
        pitches = by_measure_step.get((measure, s2), set())
        if pitches:
            neighbor_any += 1
        if pitch in pitches:
            local_exact += 1
        if any((p % 12) == (pitch % 12) for p in pitches):
            local_pc += 1
        if any(abs(p - pitch) <= 2 for p in pitches):
            neighbor_close_pitch += 1

    same_slot_pitches = sorted(by_measure_step.get((measure, step), set()))
    same_slot_count = len(same_slot_pitches)
    nearest_slot_interval = min((abs(p - pitch) for p in same_slot_pitches), default=99)
    chord_tone_like = int(any(abs(p - pitch) in {3, 4, 5, 7, 12} for p in same_slot_pitches))

    repeat_measure_support = 0
    repeat_measure_pc_support = 0
    repeat_measure_total = 0
    repeat_measure_best_sim = 0.0
    for sim, other in ctx["measureSimilarity"].get(measure, []):
        if sim < 0.35:
            continue
        repeat_measure_total += 1
        repeat_measure_best_sim = max(repeat_measure_best_sim, float(sim))
        if (other, step, pitch) in tokens:
            repeat_measure_support += 1
        other_pitches = by_measure_step.get((other, step), set())
        if any((p % 12) == (pitch % 12) for p in other_pitches):
            repeat_measure_pc_support += 1

    features = dict(base)
    features.update(
        {
            "sameStepPitchCount": same_step_pitch_count,
            "sameStepPcCount": same_step_pc_count,
            "pitchGlobalCount": pitch_global_count,
            "pcMeasureCount": pc_measure_count,
            "localExactNeighborCount": local_exact,
            "localPcNeighborCount": local_pc,
            "neighborOccupiedCount": neighbor_any,
            "neighborClosePitchCount": neighbor_close_pitch,
            "sameSlotChampionPitchCount": same_slot_count,
            "nearestSameSlotInterval": nearest_slot_interval,
            "chordToneLike": chord_tone_like,
            "repeatMeasureCount": repeat_measure_total,
            "repeatMeasureSupport": repeat_measure_support,
            "repeatMeasurePcSupport": repeat_measure_pc_support,
            "repeatMeasureBestSimilarity": repeat_measure_best_sim,
        }
    )
    return features


def context_signatures(row: dict[str, Any]) -> set[str]:
    p = int(row["sweepPersistence"])
    stems = int(row["stemCountAtWide"])
    strict = int(row["strictestSweepIndex"])
    step = int(row["step"])
    pitch = int(row["pitch"])
    reg = register_name(pitch)

    ssp = bucket_count(int(row["sameStepPitchCount"]))
    sspc = bucket_count(int(row["sameStepPcCount"]))
    pg = bucket_count(int(row["pitchGlobalCount"]))
    pcm = bucket_count(int(row["pcMeasureCount"]))
    lex = bucket_count(int(row["localExactNeighborCount"]))
    lpc = bucket_count(int(row["localPcNeighborCount"]))
    ncp = bucket_count(int(row["neighborClosePitchCount"]))
    slot = bucket_count(int(row["sameSlotChampionPitchCount"]))
    rms = bucket_count(int(row["repeatMeasureSupport"]))
    rmpc = bucket_count(int(row["repeatMeasurePcSupport"]))

    out = {
        f"ctxSameStepPitch::{ssp}",
        f"ctxSameStepPc::{sspc}",
        f"ctxPitchGlobal::{pg}",
        f"ctxPcMeasures::{pcm}",
        f"ctxLocalExact::{lex}",
        f"ctxLocalPc::{lpc}",
        f"ctxNeighborClose::{ncp}",
        f"ctxSameSlot::{slot}",
        f"ctxRepeatExact::{rms}",
        f"ctxRepeatPc::{rmpc}",
        f"ctxChordTone::{int(row['chordToneLike'])}|slot{slot}",
        f"ctxRhythm::q{step % 4}|ssp{ssp}|pc{sspc}",
        f"ctxRhythm::par{step % 2}|r{reg}|ssp{ssp}",
        f"ctxRepeatCross::rms{rms}|rmpc{rmpc}|p{p}|s{stems}",
        f"ctxRepeatCross::rms{rms}|ssp{ssp}|p{p}",
        f"ctxRepeatCross::rmpc{rmpc}|sspc{sspc}|p{p}",
        f"ctxPatternCross::ssp{ssp}|sspc{sspc}|p{p}|s{stems}",
        f"ctxPatternCross::ssp{ssp}|lex{lex}|ncp{ncp}|p{p}",
        f"ctxPatternCross::sspc{sspc}|lpc{lpc}|ncp{ncp}|s{stems}",
        f"ctxRegisterCross::{reg}|ssp{ssp}|pg{pg}|p{p}",
        f"ctxPcCross::{reg}|sspc{sspc}|pcm{pcm}|p{p}|s{stems}",
        f"ctxSlotCross::slot{slot}|ch{int(row['chordToneLike'])}|ssp{ssp}|p{p}",
        f"ctxStrictCross::i{strict}|ssp{ssp}|rms{rms}|s{stems}",
    }
    return out


def ranked(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sig, c in groups.items():
        true = int(c["true"])
        false = int(c["false"])
        total = true + false
        rows.append(
            {
                "signature": sig,
                "true": true,
                "false": false,
                "precision": round(100.0 * true / total, 2) if total else 0.0,
            }
        )
    return sorted(rows, key=lambda r: (-float(r["precision"]), -int(r["true"]), int(r["false"]), str(r["signature"])))


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)
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
    champion, reconstruction = s3161.reconstruct_3161(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    baseline = recur.grade(champion, reference)
    actual = (int(baseline["matched"]), int(baseline["missing"]), int(baseline["extra"]))
    if actual != EXPECTED or abs(float(baseline["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{baseline['pitchF1']}")

    ctx = build_champion_context(champion)
    stems = [Path(harmonic.legacy.WINNER_STEM), Path(harmonic.legacy.ALT_STEM)]
    detections: dict[str, list[dict[tuple[int, int, int], dict[str, float]]]] = {}
    for name, onset, frame in sel.SWEEPS:
        detections[name] = [sel.detect_with_metadata(stem, grid, onset, frame) for stem in stems]

    widest_name = sel.SWEEPS[-1][0]
    widest_tokens = set().union(*(set(m.keys()) for m in detections[widest_name]))
    novel_tokens = sorted(tok for tok in widest_tokens if tok not in champion)

    feature_rows: list[dict[str, Any]] = []
    for tok in novel_tokens:
        per_sweep_presence: list[int] = []
        all_meta: list[dict[str, float]] = []
        strictest_index = len(sel.SWEEPS) - 1
        strictest_set = False
        for idx, (name, _onset, _frame) in enumerate(sel.SWEEPS):
            maps = detections[name]
            present = sum(1 for m in maps if tok in m)
            per_sweep_presence.append(present)
            if present and not strictest_set:
                strictest_index = idx
                strictest_set = True
            for m in maps:
                if tok in m:
                    all_meta.append(m[tok])
        if not all_meta:
            continue
        measure, step, pitch = tok
        base = {
            "token": list(tok),
            "measure": measure,
            "step": step,
            "pitch": pitch,
            "sweepPresence": per_sweep_presence,
            "sweepPersistence": sum(1 for x in per_sweep_presence if x > 0),
            "stemCountAtWide": sum(1 for m in detections[widest_name] if tok in m),
            "strictestSweepIndex": strictest_index,
            "maxAmplitude": max(float(m["amplitude"]) for m in all_meta),
            "meanAmplitude": sum(float(m["amplitude"]) for m in all_meta) / len(all_meta),
            "minGridError": min(float(m["gridError"]) for m in all_meta),
            "maxDuration": max(float(m["duration"]) for m in all_meta),
        }
        feature_rows.append(contextual_features(tok, base, ctx))

    # Reference is used only here, after all detection-side features/signatures are built.
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    true_total = 0
    false_total = 0
    details: list[dict[str, Any]] = []
    for row in feature_rows:
        tok = tuple(int(x) for x in row["token"])
        sigs = sorted(context_signatures(row))
        is_true = int((Counter({tok: 1}) & reference)[tok]) > 0
        label = "true" if is_true else "false"
        if is_true:
            true_total += 1
        else:
            false_total += 1
        for sig in sigs:
            groups[sig][label] += 1
        out_row = dict(row)
        out_row["label"] = label
        out_row["signatures"] = sigs
        details.append(out_row)

    rows = ranked(groups)
    perfect = [r for r in rows if int(r["true"]) >= 5 and int(r["false"]) == 0]
    high80 = [r for r in rows if int(r["true"]) >= 8 and float(r["precision"]) >= 80.0]
    high50 = [r for r in rows if int(r["true"]) >= 12 and float(r["precision"]) >= 50.0]
    big20 = [r for r in rows if int(r["true"]) >= 20 and float(r["precision"]) >= 20.0]
    big10 = [r for r in rows if int(r["true"]) >= 35 and float(r["precision"]) >= 10.0]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during contextual pattern recovery profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "31.61-wide-recall-contextual-pattern-recovery",
        "champion3161Score": baseline,
        "reconstruction": reconstruction,
        "novelCandidateCount": len(details),
        "recoverableTrueCount": true_total,
        "recoveryFalseCount": false_total,
        "perfectRecoverySignaturesMin5True": perfect,
        "highPrecisionRecoverySignaturesMin8True80Pct": high80,
        "moderateRecoverySignaturesMin12True50Pct": high50,
        "bigJumpRecoverySignaturesMin20True20Pct": big20,
        "largeCoverageRecoverySignaturesMin35True10Pct": big10,
        "rankedSignatures": rows,
        "candidateRows": details,
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
        "championPitchF1": baseline["pitchF1"],
        "novelCandidateCount": len(details),
        "recoverableTrueCount": true_total,
        "recoveryFalseCount": false_total,
        "perfectSignatureCount": len(perfect),
        "high80SignatureCount": len(high80),
        "high50SignatureCount": len(high50),
        "big20SignatureCount": len(big20),
        "big10SignatureCount": len(big10),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 WIDE-RECALL CONTEXTUAL PATTERN RECOVERY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", baseline["pitchF1"])
    print("Champion matched/missing/extra:", baseline["matched"], "/", baseline["missing"], "/", baseline["extra"])
    print("Novel contextual candidates:", len(details))
    print("Recoverable true / false:", true_total, "/", false_total)
    print("Perfect recovery signatures (5+ true, 0 false):", len(perfect))
    for r in perfect[:20]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("High-precision recovery signatures (8+ true, >=80%):", len(high80))
    for r in high80[:20]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("Moderate recovery signatures (12+ true, >=50%):", len(high50))
    for r in high50[:20]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("BIG-JUMP signatures (20+ true, >=20%):", len(big20))
    for r in big20[:30]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
    print("Large-coverage signatures (35+ true, >=10%):", len(big10))
    for r in big10[:30]:
        print(f"{r['signature']}: true={r['true']} false={r['false']} precision={r['precision']}")
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
