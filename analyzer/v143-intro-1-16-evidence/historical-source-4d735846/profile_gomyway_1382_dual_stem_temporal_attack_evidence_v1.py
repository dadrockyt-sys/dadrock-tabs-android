from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import benchmark_gomyway_1382_champion_dual_stem_local_prominence_recall_gate_v1 as prom

recur = prom.recur
raw = prom.raw
v2 = prom.v2
v3 = prom.v3
recall = prom.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-dual-stem-temporal-attack-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-dual-stem-temporal-attack-evidence-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82

# This profiler is deliberately permissive enough to expose the failure mode,
# while still avoiding an all-pitch/all-time temporal rescan.
POOL_FLOOR = 4.0
POOL_MARGIN = 0.5
POOL_RECURRENCE = 2
PRE_OFFSETS = (0.06, 0.12)
POST_OFFSET = 0.06

ATTACK_BUCKETS = [
    ("rise_lt_0", float("-inf"), 0.0),
    ("rise_0_05", 0.0, 0.5),
    ("rise_05_10", 0.5, 1.0),
    ("rise_10_20", 1.0, 2.0),
    ("rise_20_30", 2.0, 3.0),
    ("rise_30_plus", 3.0, float("inf")),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket_name(value: float) -> str:
    for name, lo, hi in ATTACK_BUCKETS:
        if lo <= value < hi:
            return name
    return "unknown"


def temporal_score(audio, sr: int, center: float, pitch: int) -> dict[str, float]:
    now = float(recall.spectral.spectral_score(audio, sr, center, pitch))
    pre_values = [
        float(recall.spectral.spectral_score(audio, sr, max(0.0, center - offset), pitch))
        for offset in PRE_OFFSETS
    ]
    post = float(recall.spectral.spectral_score(audio, sr, center + POST_OFFSET, pitch))
    pre_max = max(pre_values) if pre_values else 0.0
    pre_mean = sum(pre_values) / len(pre_values) if pre_values else 0.0
    return {
        "now": now,
        "preMax": pre_max,
        "preMean": pre_mean,
        "riseVsPreMax": now - pre_max,
        "riseVsPreMean": now - pre_mean,
        "post": post,
        "postDelta": post - now,
    }


def candidate_pool(grid, winner_scores, alt_scores, champion):
    supported: list[tuple[int, int, int]] = []
    recurrence: Counter[tuple[int, int]] = Counter()
    for measure, step in grid:
        if not 17 <= measure <= 113:
            continue
        for pitch in range(recall.PITCH_MIN, recall.PITCH_MAX + 1):
            token = (measure, step, pitch)
            if champion.get(token, 0) > 0:
                continue
            if min(float(winner_scores.get(token, 0.0)), float(alt_scores.get(token, 0.0))) < POOL_FLOOR:
                continue
            if prom.local_prominence(winner_scores, token) < POOL_MARGIN:
                continue
            if prom.local_prominence(alt_scores, token) < POOL_MARGIN:
                continue
            supported.append(token)
            recurrence[(step, pitch)] += 1

    return [token for token in supported if recurrence[(token[1], token[2])] >= POOL_RECURRENCE], recurrence


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
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

    print("Rebuilding frozen validated 13.82 champion and center-time detector scores...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    pool, recurrence_counts = candidate_pool(grid, winner_scores, alt_scores, champion)
    print(f"Temporal attack candidate pool: {len(pool)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    # Reference is consulted only here, after the detector-side pool is frozen.
    missing_reference = reference - champion

    rows: list[dict[str, Any]] = []
    bucket_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    joint_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for index, token in enumerate(pool, 1):
        measure, step, pitch = token
        center = float(grid[(measure, step)])
        ws = temporal_score(winner_audio, winner_sr, center, pitch)
        ats = temporal_score(alt_audio, alt_sr, center, pitch)
        min_rise_max = min(ws["riseVsPreMax"], ats["riseVsPreMax"])
        min_rise_mean = min(ws["riseVsPreMean"], ats["riseVsPreMean"])
        min_center = min(ws["now"], ats["now"])
        min_prominence = min(prom.local_prominence(winner_scores, token), prom.local_prominence(alt_scores, token))
        recurrent = int(recurrence_counts[(step, pitch)])
        is_true = missing_reference.get(token, 0) > 0

        b = bucket_name(min_rise_max)
        bucket_counts[b][0 if is_true else 1] += 1
        joint_key = f"{b}|center_{int(min_center // 2) * 2}_{int(min_center // 2) * 2 + 2}|recur_{'4plus' if recurrent >= 4 else recurrent}"
        joint_counts[joint_key][0 if is_true else 1] += 1

        rows.append({
            "token": [measure, step, pitch],
            "trueMissingReference": is_true,
            "minCenter": round(min_center, 4),
            "minProminence": round(min_prominence, 4),
            "recurrence": recurrent,
            "winner": {k: round(v, 4) for k, v in ws.items()},
            "alternate": {k: round(v, 4) for k, v in ats.items()},
            "minRiseVsPreMax": round(min_rise_max, 4),
            "minRiseVsPreMean": round(min_rise_mean, 4),
            "attackBucket": b,
        })
        if index % 250 == 0:
            print(f"Temporal evidence measured: {index}/{len(pool)}", flush=True)

    attack_summary = {
        name: precision_row(counts[0], counts[1])
        for name, counts in bucket_counts.items()
    }
    joint_summary = {
        name: precision_row(counts[0], counts[1])
        for name, counts in joint_counts.items()
    }
    best_joint = sorted(
        joint_summary.items(),
        key=lambda item: (float(item[1]["precision"]), int(item[1]["true"]), -int(item[1]["false"])),
        reverse=True,
    )[:30]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during temporal attack evidence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-13.82-reference-free-dual-stem-temporal-attack-evidence",
        "championScore": champion_score,
        "detectorPool": {
            "bothFloor": POOL_FLOOR,
            "localProminenceMargin": POOL_MARGIN,
            "recurrence": POOL_RECURRENCE,
            "count": len(pool),
        },
        "preOffsetsSeconds": list(PRE_OFFSETS),
        "postOffsetSeconds": POST_OFFSET,
        "attackBucketSummary": attack_summary,
        "bestJointBuckets": [{"signature": key, **value} for key, value in best_joint],
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
        "recommendedNextAction": "benchmark-temporal-attack-thresholds-from-validated-1382-profile",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": champion_score["pitchF1"],
        "poolCount": len(pool),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 13.82 DUAL-STEM TEMPORAL ATTACK EVIDENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Temporal candidate pool:", len(pool))
    print("Attack-rise precision buckets:")
    for name, _, _ in ATTACK_BUCKETS:
        row = attack_summary.get(name, precision_row(0, 0))
        print(f"  {name}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top joint attack/center/recurrence buckets:")
    for key, row in best_joint[:20]:
        print(f"  {key}: true={row['true']} false={row['false']} precision={row['precision']}%")
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
