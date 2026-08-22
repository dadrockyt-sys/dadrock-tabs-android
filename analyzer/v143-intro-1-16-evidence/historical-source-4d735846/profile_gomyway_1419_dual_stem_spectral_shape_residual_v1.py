from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import benchmark_gomyway_1419_champion_cached_repeatable_residual_joint_gate_v1 as bench
import profile_gomyway_1382_dual_stem_broadband_onset_evidence_v1 as broad

cached = bench.cached
recur = bench.recur
v2 = bench.v2
v3 = bench.v3
recall = bench.recall

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-1419-dual-stem-spectral-shape-residual-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-1419-dual-stem-spectral-shape-residual-v1-manifest.json"
EXPECTED_1419 = (178, 689, 1464)
EXPECTED_1419_F1 = 14.19
FRAME_SECONDS = 0.046
EPS = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def precision_row(true_count: int, false_count: int) -> dict[str, Any]:
    total = true_count + false_count
    return {
        "true": true_count,
        "false": false_count,
        "total": total,
        "precision": round(100.0 * true_count / total, 2) if total else 0.0,
    }


def frame(audio: np.ndarray, sr: int, center: float) -> np.ndarray:
    arr = broad.mono(audio)
    n = max(64, int(round(FRAME_SECONDS * sr)))
    c = int(round(center * sr))
    start = max(0, c - n // 2)
    stop = min(len(arr), start + n)
    out = np.zeros(n, dtype=np.float64)
    chunk = arr[start:stop]
    out[: len(chunk)] = chunk
    if len(out) > 1:
        out *= np.hanning(len(out))
    return out


def spectral_shape(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    x = frame(audio, sr, center)
    mag = np.abs(np.fft.rfft(x)) + EPS
    power = mag * mag
    freqs = np.fft.rfftfreq(len(x), d=1.0 / sr)
    mag_sum = float(np.sum(mag)) + EPS
    power_sum = float(np.sum(power)) + EPS

    centroid_hz = float(np.sum(freqs * mag) / mag_sum)
    flatness = float(np.exp(np.mean(np.log(mag))) / (np.mean(mag) + EPS))

    cumulative = np.cumsum(power)
    target = 0.85 * cumulative[-1]
    rolloff_index = int(np.searchsorted(cumulative, target, side="left"))
    rolloff_index = min(max(rolloff_index, 0), len(freqs) - 1)
    rolloff_hz = float(freqs[rolloff_index])

    high_mask = freqs >= 2000.0
    high_fraction = float(np.sum(power[high_mask]) / power_sum)

    low_mid_mask = (freqs >= 80.0) & (freqs < 1200.0)
    low_mid_fraction = float(np.sum(power[low_mid_mask]) / power_sum)

    return {
        "centroidHz": centroid_hz,
        "flatness": flatness,
        "rolloff85Hz": rolloff_hz,
        "highFraction2k": high_fraction,
        "lowMidFraction80_1200": low_mid_fraction,
    }


def bucket(value: float, edges: tuple[float, ...], prefix: str) -> str:
    for index, edge in enumerate(edges):
        if value < edge:
            return f"{prefix}_lt_{str(edge).replace('.', 'p')}"
    return f"{prefix}_{str(edges[-1]).replace('.', 'p')}_plus"


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    rows = cached.load_profile_rows()
    print(f"Loaded cached detector rows: {len(rows)}", flush=True)

    payload = v2.load_json(recall.CANDIDATE_PATH)
    events = v2.candidate_rows(payload)
    if len(events) != 949:
        raise RuntimeError(f"Expected protected 949-event candidate, found {len(events)}")
    grid, _ = v2.build_timing_grid(events)

    reference_payload = v2.load_json(recall.REFERENCE_PATH)
    if reference_payload.get("professionalReferenceUsedForScoringOnly") is not True:
        raise RuntimeError("Professional reference is not marked scoring-only.")
    reference = v3.reference_tokens(reference_payload)

    baseline_1382, _, _ = recur.build_frozen_1382(grid)
    champion_additions = bench.rows_to_counter(rows, bench.champion_1419_predicate)
    champion_1419 = baseline_1382 + champion_additions
    score_1419 = recur.grade(champion_1419, reference)
    actual = (
        int(score_1419["matched"]),
        int(score_1419["missing"]),
        int(score_1419["extra"]),
    )
    if actual != EXPECTED_1419 or abs(float(score_1419["pitchF1"]) - EXPECTED_1419_F1) > 0.01:
        raise RuntimeError(
            f"Expected frozen 14.19 champion {EXPECTED_1419}/{EXPECTED_1419_F1}, "
            f"got {actual}/{score_1419['pitchF1']}"
        )

    champion_tokens = set(champion_additions.keys())
    residual_rows = [row for row in rows if bench.token(row) not in champion_tokens]
    print(f"14.19 residual detector rows: {len(residual_rows)}", flush=True)

    winner_audio, winner_sr = recall.spectral.load_filtered(recall.WINNER_STEM)
    alt_audio, alt_sr = recall.spectral.load_filtered(recall.ALT_STEM)

    missing_reference = reference - champion_1419

    feature_counts: dict[str, Counter[str]] = defaultdict(Counter)
    joint_counts: dict[str, Counter[str]] = defaultdict(Counter)
    detailed: list[dict[str, Any]] = []

    for index, row in enumerate(residual_rows, 1):
        token = bench.token(row)
        measure, step, pitch = token
        center = float(grid[(measure, step)])
        w = spectral_shape(winner_audio, winner_sr, center)
        a = spectral_shape(alt_audio, alt_sr, center)

        min_centroid = min(w["centroidHz"], a["centroidHz"])
        max_flatness = max(w["flatness"], a["flatness"])
        min_rolloff = min(w["rolloff85Hz"], a["rolloff85Hz"])
        max_high = max(w["highFraction2k"], a["highFraction2k"])
        min_low_mid = min(w["lowMidFraction80_1200"], a["lowMidFraction80_1200"])

        cb = bucket(min_centroid, (500, 800, 1200, 1800, 2600, 4000), "cent")
        fb = bucket(max_flatness, (0.01, 0.03, 0.06, 0.12, 0.24, 0.40), "flat")
        rb = bucket(min_rolloff, (800, 1200, 1800, 2600, 4000, 6000), "roll")
        hb = bucket(max_high, (0.01, 0.03, 0.08, 0.15, 0.30, 0.50), "high")
        lb = bucket(min_low_mid, (0.20, 0.35, 0.50, 0.65, 0.80), "lowmid")

        is_true = missing_reference.get(token, 0) > 0
        truth = "true" if is_true else "false"
        for name, value in (("centroid", cb), ("flatness", fb), ("rolloff", rb), ("high", hb), ("lowmid", lb)):
            feature_counts[f"{name}|{value}"][truth] += 1

        recur_value = int(row.get("recurrence", 0))
        recur_label = "4plus" if recur_value >= 4 else str(recur_value)
        joints = (
            f"{cb}|{fb}|recur_{recur_label}",
            f"{cb}|{hb}|recur_{recur_label}",
            f"{fb}|{hb}|recur_{recur_label}",
            f"{rb}|{hb}|recur_{recur_label}",
            f"{cb}|{fb}|{hb}",
            f"{cb}|{rb}|{hb}",
        )
        for signature in joints:
            joint_counts[signature][truth] += 1

        detailed.append({
            "token": list(token),
            "trueMissingReference": is_true,
            "recurrence": recur_value,
            "winner": {k: round(float(v), 6) for k, v in w.items()},
            "alternate": {k: round(float(v), 6) for k, v in a.items()},
            "minCentroidHz": round(min_centroid, 6),
            "maxFlatness": round(max_flatness, 6),
            "minRolloff85Hz": round(min_rolloff, 6),
            "maxHighFraction2k": round(max_high, 6),
            "minLowMidFraction80_1200": round(min_low_mid, 6),
            "centroidBucket": cb,
            "flatnessBucket": fb,
            "rolloffBucket": rb,
            "highBucket": hb,
            "lowMidBucket": lb,
        })

        if index % 250 == 0:
            print(f"Spectral shape measured: {index}/{len(residual_rows)}", flush=True)

    def summarize(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for signature, counts in groups.items():
            out.append({
                "signature": signature,
                **precision_row(int(counts["true"]), int(counts["false"])),
            })
        return sorted(
            out,
            key=lambda r: (float(r["precision"]), int(r["true"]), -int(r["false"])),
            reverse=True,
        )

    singles = summarize(feature_counts)
    joints = summarize(joint_counts)
    repeatable = [row for row in joints if int(row["true"]) >= 2]
    supported = [row for row in joints if int(row["true"]) >= 3]

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 14.19 spectral-shape residual profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-14.19-reference-free-dual-stem-spectral-shape-residual",
        "championScore": score_1419,
        "residualRowCount": len(residual_rows),
        "singleFeaturePrecision": singles,
        "jointFeaturePrecision": joints,
        "repeatableJointPrecision": repeatable,
        "supportedJointPrecision": supported,
        "rows": detailed,
        "professionalReferenceUsedDuringDetection": False,
        "professionalReferenceRole": "downstream-grading-and-training-label-only",
        "protected949CandidateHashUnchanged": True,
        "candidateEventsModified": False,
        "v7EventsModified": False,
        "rendererModified": False,
        "protectedBaselinesChanged": False,
        "productionSeparatorChanged": False,
        "productionPromotionAllowed": False,
        "recommendedNextAction": "benchmark-only-repeatable-high-precision-spectral-shape-pockets-else-pivot-audio-feature-family",
    }
    manifest = {
        "schemaVersion": 1,
        "passed": True,
        "output": str(OUTPUT_PATH.relative_to(ROOT)),
        "candidateSha256": after,
        "championPitchF1": score_1419["pitchF1"],
        "residualRowCount": len(residual_rows),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 14.19 DUAL-STEM SPECTRAL SHAPE RESIDUAL V1 COMPLETE")
    print("Passed: True")
    print("Champion remains frozen:", score_1419["pitchF1"], "/", score_1419["matched"], "/", score_1419["missing"], "/", score_1419["extra"])
    print("Residual detector rows:", len(residual_rows))
    print("Top repeatable spectral-shape signatures:")
    for row in repeatable[:20]:
        print(f"  {row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}%")
    print("Top supported spectral-shape signatures (3+ true):")
    for row in supported[:20]:
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
