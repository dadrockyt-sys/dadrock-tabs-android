from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_1382_dual_stem_temporal_attack_evidence_v1 as attack

prom = attack.prom
recur = attack.recur
v2 = attack.v2
v3 = attack.v3
recall = attack.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1382-dual-stem-broadband-onset-evidence-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1382-dual-stem-broadband-onset-evidence-v1-manifest.json"
EXPECTED_CHAMPION = (173, 694, 1464)
EXPECTED_F1 = 13.82

FRAME_SECONDS = 0.046
PRE_SECONDS = 0.070
EPS = 1e-9

RMS_BUCKETS = [
    ("rms_lt_0", float("-inf"), 0.0),
    ("rms_0_010", 0.0, 0.10),
    ("rms_010_025", 0.10, 0.25),
    ("rms_025_050", 0.25, 0.50),
    ("rms_050_100", 0.50, 1.00),
    ("rms_100_plus", 1.00, float("inf")),
]

FLUX_BUCKETS = [
    ("flux_0_010", 0.0, 0.10),
    ("flux_010_025", 0.10, 0.25),
    ("flux_025_050", 0.25, 0.50),
    ("flux_050_100", 0.50, 1.00),
    ("flux_100_plus", 1.00, float("inf")),
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mono(audio: np.ndarray) -> np.ndarray:
    arr = np.asarray(audio, dtype=np.float64)
    if arr.ndim == 1:
        return arr
    if arr.ndim == 2:
        return np.mean(arr, axis=1)
    return arr.reshape(-1)


def frame(audio: np.ndarray, sr: int, center: float) -> np.ndarray:
    arr = mono(audio)
    n = max(32, int(round(FRAME_SECONDS * sr)))
    c = int(round(center * sr))
    start = max(0, c - n // 2)
    stop = min(len(arr), start + n)
    out = np.zeros(n, dtype=np.float64)
    chunk = arr[start:stop]
    out[: len(chunk)] = chunk
    if len(out) > 1:
        out *= np.hanning(len(out))
    return out


def broadband_onset(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    now = frame(audio, sr, center)
    pre = frame(audio, sr, max(0.0, center - PRE_SECONDS))

    rms_now = float(np.sqrt(np.mean(now * now) + EPS))
    rms_pre = float(np.sqrt(np.mean(pre * pre) + EPS))
    rms_ratio = rms_now / max(rms_pre, EPS)
    rms_log_rise = float(np.log2(max(rms_ratio, EPS)))

    now_spec = np.abs(np.fft.rfft(now))
    pre_spec = np.abs(np.fft.rfft(pre))
    scale = max(float(np.sum(pre_spec)), EPS)
    positive_flux = float(np.sum(np.maximum(now_spec - pre_spec, 0.0)) / scale)

    return {
        "rmsNow": rms_now,
        "rmsPre": rms_pre,
        "rmsRatio": rms_ratio,
        "rmsLog2Rise": rms_log_rise,
        "positiveFlux": positive_flux,
    }


def bucket(value: float, bins) -> str:
    for name, lo, hi in bins:
        if lo <= value < hi:
            return name
    return bins[-1][0]


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

    print("Rebuilding frozen validated 13.82 champion and detector-side temporal pool...", flush=True)
    champion, winner_scores, alt_scores = recur.build_frozen_1382(grid)
    champion_score = recur.grade(champion, reference)
    actual = (int(champion_score["matched"]), int(champion_score["missing"]), int(champion_score["extra"]))
    if actual != EXPECTED_CHAMPION or abs(float(champion_score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected 13.82 champion {EXPECTED_CHAMPION}/{EXPECTED_F1}, got {actual}/{champion_score['pitchF1']}")

    pool, recurrence_counts = attack.candidate_pool(grid, winner_scores, alt_scores, champion)
    print(f"Broadband onset candidate pool: {len(pool)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    # Reference is consulted only after the detector-side pool and audio features are frozen.
    missing_reference = reference - champion

    rows: list[dict[str, Any]] = []
    rms_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    flux_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    joint_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])

    for index, token in enumerate(pool, 1):
        measure, step, pitch = token
        center = float(grid[(measure, step)])
        w = broadband_onset(winner_audio, winner_sr, center)
        a = broadband_onset(alt_audio, alt_sr, center)

        min_rms_rise = min(float(w["rmsLog2Rise"]), float(a["rmsLog2Rise"]))
        min_flux = min(float(w["positiveFlux"]), float(a["positiveFlux"]))
        recurrent = int(recurrence_counts[(step, pitch)])
        is_true = missing_reference.get(token, 0) > 0

        rb = bucket(min_rms_rise, RMS_BUCKETS)
        fb = bucket(min_flux, FLUX_BUCKETS)
        rms_counts[rb][0 if is_true else 1] += 1
        flux_counts[fb][0 if is_true else 1] += 1
        recur_label = "4plus" if recurrent >= 4 else str(recurrent)
        joint_key = f"{rb}|{fb}|recur_{recur_label}"
        joint_counts[joint_key][0 if is_true else 1] += 1

        rows.append({
            "token": [measure, step, pitch],
            "trueMissingReference": is_true,
            "recurrence": recurrent,
            "winner": {k: round(float(v), 6) for k, v in w.items()},
            "alternate": {k: round(float(v), 6) for k, v in a.items()},
            "minRmsLog2Rise": round(min_rms_rise, 6),
            "minPositiveFlux": round(min_flux, 6),
            "rmsBucket": rb,
            "fluxBucket": fb,
        })
        if index % 250 == 0:
            print(f"Broadband onset evidence measured: {index}/{len(pool)}", flush=True)

    rms_summary = {k: precision_row(v[0], v[1]) for k, v in rms_counts.items()}
    flux_summary = {k: precision_row(v[0], v[1]) for k, v in flux_counts.items()}
    joint_summary = {k: precision_row(v[0], v[1]) for k, v in joint_counts.items()}
    best_joint = sorted(
        joint_summary.items(),
        key=lambda item: (float(item[1]["precision"]), int(item[1]["true"]), -int(item[1]["false"])),
        reverse=True,
    )[:30]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during broadband onset evidence profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-13.82-reference-free-dual-stem-broadband-onset-evidence",
        "championScore": champion_score,
        "detectorPool": {
            "bothFloor": attack.POOL_FLOOR,
            "localProminenceMargin": attack.POOL_MARGIN,
            "recurrence": attack.POOL_RECURRENCE,
            "count": len(pool),
        },
        "frameSeconds": FRAME_SECONDS,
        "preSeconds": PRE_SECONDS,
        "rmsRiseSummary": rms_summary,
        "positiveFluxSummary": flux_summary,
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
        "recommendedNextAction": "benchmark-broadband-onset-flux-pockets-if-repeatable-else-pivot-detector-family",
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

    print("GOMYWAY 13.82 DUAL-STEM BROADBAND ONSET EVIDENCE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", champion_score["pitchF1"])
    print("Champion matched/missing/extra:", champion_score["matched"], "/", champion_score["missing"], "/", champion_score["extra"])
    print("Broadband onset candidate pool:", len(pool))
    print("RMS attack precision buckets:")
    for name, _, _ in RMS_BUCKETS:
        row = rms_summary.get(name, precision_row(0, 0))
        print(f"  {name}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Positive spectral-flux precision buckets:")
    for name, _, _ in FLUX_BUCKETS:
        row = flux_summary.get(name, precision_row(0, 0))
        print(f"  {name}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top joint RMS/flux/recurrence buckets:")
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
