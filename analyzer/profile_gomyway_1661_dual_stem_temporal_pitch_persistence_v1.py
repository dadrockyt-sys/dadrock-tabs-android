from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_1652_harmonic_comb_final_survivor_precision_prune_cv_v1 as b1652
import benchmark_gomyway_1590_harmonic_comb_precision_prune_cv_v1 as b1590

harmonic = b1590.harmonic
recur = b1590.recur
recall = b1590.recall
v2 = b1590.v2
v3 = b1590.v3

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PROFILE_1652_PATH = PUBLIC / "gomyway-1652-harmonic-comb-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-1661-dual-stem-temporal-pitch-persistence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1661-dual-stem-temporal-pitch-persistence-v1-manifest.json"
EXPECTED = (183, 684, 1153)
EXPECTED_F1 = 16.61
FRAME_OFFSETS = (-0.060, -0.030, 0.0, 0.030, 0.060)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def token(row: dict[str, Any]) -> tuple[int, int, int]:
    return tuple(int(v) for v in row["token"])


def reconstruct_1661(grid: Any) -> Counter[tuple[int, int, int]]:
    champion_1652 = b1652.reconstruct_1652(grid)
    payload = v2.load_json(PROFILE_1652_PATH)
    rows = list(payload.get("rows", []))
    row_by_token = {token(row): row for row in rows}
    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion_1652.items():
        row = row_by_token.get(tok)
        if row is not None and (b1652.pred_a(row) or b1652.pred_b(row)):
            pruned[tok] = count
    return champion_1652 - pruned


def bucket_int(value: int, edges: tuple[int, ...], labels: tuple[str, ...]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def bucket_float(value: float, edges: tuple[float, ...], labels: tuple[str, ...]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def win_count_bucket(value: int) -> str:
    return bucket_int(value, (1, 2, 3, 4, 5), ("wins_0", "wins_1", "wins_2", "wins_3", "wins_4", "wins_5"))


def comb_count_bucket(value: int) -> str:
    return bucket_int(value, (1, 2, 3, 4, 5), ("combframes_0", "combframes_1", "combframes_2", "combframes_3", "combframes_4", "combframes_5"))


def persistent_count_bucket(value: int) -> str:
    return bucket_int(value, (1, 2, 3, 4, 5), ("persist_0", "persist_1", "persist_2", "persist_3", "persist_4", "persist_5"))


def margin_median_bucket(value: float) -> str:
    return bucket_float(value, (0.80, 0.95, 1.05, 1.20), ("medmargin_lt080", "medmargin_080_095", "medmargin_095_105", "medmargin_105_120", "medmargin_120_plus"))


def margin_range_bucket(value: float) -> str:
    return bucket_float(value, (0.15, 0.35, 0.70, 1.20), ("marginrange_lt015", "marginrange_015_035", "marginrange_035_070", "marginrange_070_120", "marginrange_120_plus"))


def disagreement_bucket(value: int) -> str:
    return bucket_int(value, (1, 2, 3, 4), ("temporal_disagree_0", "temporal_disagree_1", "temporal_disagree_2", "temporal_disagree_3", "temporal_disagree_4plus"))


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true_count = int(counts["true"])
        false_count = int(counts["false"])
        total = true_count + false_count
        rows.append({
            "signature": signature,
            "true": true_count,
            "false": false_count,
            "total": total,
            "precision": round(100.0 * true_count / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


def temporal_features(audio: np.ndarray, sample_rate: int, center: float, midi: int) -> dict[str, Any]:
    frames = [harmonic.stem_features(audio, sample_rate, center + offset, midi) for offset in FRAME_OFFSETS]
    margins = [float(frame["neighborMargin"]) for frame in frames]
    combs = [float(frame["combRatio"]) for frame in frames]
    f0shares = [float(frame["fundamentalShare"]) for frame in frames]

    wins = sum(1 for value in margins if value >= 1.0)
    comb_frames = sum(1 for value in combs if value >= 0.006)
    persistent = sum(1 for margin, comb in zip(margins, combs) if margin >= 0.95 and comb >= 0.006)

    return {
        "wins": int(wins),
        "combFrames": int(comb_frames),
        "persistentFrames": int(persistent),
        "medianMargin": float(np.median(margins)),
        "marginRange": float(max(margins) - min(margins)),
        "medianComb": float(np.median(combs)),
        "medianF0Share": float(np.median(f0shares)),
        "frames": frames,
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
        raise RuntimeError("Professional reference is not marked scoring-only")
    reference = v3.reference_tokens(reference_payload)

    profile_1652 = v2.load_json(PROFILE_1652_PATH)
    if profile_1652.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("16.52 harmonic survivor profile is not reference-free during detection")

    champion = reconstruct_1661(grid)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 16.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    winner_audio, winner_sr = harmonic.load_mono(harmonic.legacy.WINNER_STEM)
    alt_audio, alt_sr = harmonic.load_mono(harmonic.legacy.ALT_STEM)

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    matched = champion & reference
    extras = champion - reference

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = temporal_features(winner_audio, winner_sr, center, pitch)
        af = temporal_features(alt_audio, alt_sr, center, pitch)

        min_wins = min(int(wf["wins"]), int(af["wins"]))
        min_comb_frames = min(int(wf["combFrames"]), int(af["combFrames"]))
        min_persistent = min(int(wf["persistentFrames"]), int(af["persistentFrames"]))
        min_median_margin = min(float(wf["medianMargin"]), float(af["medianMargin"]))
        max_margin_range = max(float(wf["marginRange"]), float(af["marginRange"]))
        temporal_disagreement = abs(int(wf["persistentFrames"]) - int(af["persistentFrames"]))

        wins_b = win_count_bucket(min_wins)
        comb_b = comb_count_bucket(min_comb_frames)
        persist_b = persistent_count_bucket(min_persistent)
        medmargin_b = margin_median_bucket(min_median_margin)
        range_b = margin_range_bucket(max_margin_range)
        disagree_b = disagreement_bucket(temporal_disagreement)

        signatures = {
            "minWinFrames": wins_b,
            "minCombFrames": comb_b,
            "minPersistentFrames": persist_b,
            "minMedianMargin": medmargin_b,
            "maxMarginRange": range_b,
            "temporalStemDisagreement": disagree_b,
            "winsPersistence": f"{wins_b}|{persist_b}",
            "combPersistence": f"{comb_b}|{persist_b}",
            "persistenceMargin": f"{persist_b}|{medmargin_b}",
            "persistenceRange": f"{persist_b}|{range_b}",
            "persistenceAgreement": f"{persist_b}|{disagree_b}",
            "winsMargin": f"{wins_b}|{medmargin_b}",
            "temporalCross": f"{persist_b}|{medmargin_b}|{disagree_b}",
        }
        for name, signature in signatures.items():
            groups[f"{name}::{signature}"][truth] += count

        details.append({
            "token": list(tok),
            "truth": truth,
            "count": count,
            "winner": wf,
            "alternate": af,
            "minWinFrames": min_wins,
            "minCombFrames": min_comb_frames,
            "minPersistentFrames": min_persistent,
            "minMedianMargin": min_median_margin,
            "maxMarginRange": max_margin_range,
            "temporalStemDisagreement": temporal_disagreement,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero_precision = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero_precision.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported_true = [r for r in ranked if int(r["true"]) >= 5]
    supported_true.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 16.61 temporal pitch persistence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-16.61-dual-stem-temporal-pitch-persistence",
        "champion1661Score": score,
        "featureFamily": "dual-stem-temporal-pitch-persistence",
        "frameOffsetsSeconds": list(FRAME_OFFSETS),
        "zeroPrecisionGeneralizableSignaturesMin5False": zero_precision,
        "supportedTrueSignaturesMin5True": supported_true,
        "rows": details,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-generalizable-zero-precision-temporal-pitch-persistence-signatures-with-prune-specific-heldout-cv",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "productionPromotionAllowed": False,
    }

    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 16.61 DUAL-STEM TEMPORAL PITCH PERSISTENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision temporal-persistence signatures (5+ false, 0 true):")
    for row in zero_precision[:50]:
        print(f"  {row['signature']}: true=0 false={row['false']} precision=0.0%")
    print("Top supported true temporal-persistence signatures (5+ true):")
    for row in supported_true[:30]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
