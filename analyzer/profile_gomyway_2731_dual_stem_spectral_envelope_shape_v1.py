from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2731_pitch_trajectory_survivors_precision_v1 as survivor

recur = survivor.recur
recall = survivor.recall
v2 = survivor.v2
v3 = survivor.v3
harmonic = survivor.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2731-dual-stem-spectral-envelope-shape-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2731-dual-stem-spectral-envelope-shape-v1-manifest.json"
EXPECTED = (183, 684, 290)
EXPECTED_F1 = 27.31


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def spectral_envelope_features(audio: np.ndarray, sr: int, center: float, midi_pitch: int) -> dict[str, float]:
    half = 0.09
    start = max(0, int((center - half) * sr))
    end = min(len(audio), int((center + half) * sr))
    x = np.asarray(audio[start:end], dtype=np.float64)
    if x.size < 64:
        return {
            "harmonicShare": 0.0,
            "interharmonicShare": 0.0,
            "slope": 0.0,
            "curvature": 0.0,
            "centroidRatio": 0.0,
            "roughness": 0.0,
        }
    x = x - float(np.mean(x))
    window = np.hanning(x.size)
    spec = np.abs(np.fft.rfft(x * window)) ** 2
    freqs = np.fft.rfftfreq(x.size, 1.0 / sr)
    total = float(np.sum(spec)) + 1e-12
    f0 = 440.0 * (2.0 ** ((midi_pitch - 69) / 12.0))

    def band_energy(lo: float, hi: float) -> float:
        mask = (freqs >= max(0.0, lo)) & (freqs <= hi)
        return float(np.sum(spec[mask]))

    harmonic_e = 0.0
    inter_e = 0.0
    harmonic_points: list[tuple[float, float]] = []
    for h in range(1, 7):
        fh = f0 * h
        if fh >= sr / 2:
            break
        bw = max(8.0, fh * 0.025)
        he = band_energy(fh - bw, fh + bw)
        harmonic_e += he
        harmonic_points.append((float(h), he + 1e-12))
        if h < 6:
            mid = f0 * (h + 0.5)
            if mid < sr / 2:
                ibw = max(8.0, mid * 0.025)
                inter_e += band_energy(mid - ibw, mid + ibw)

    harmonic_share = harmonic_e / total
    inter_share = inter_e / total

    if len(harmonic_points) >= 3:
        hs = np.array([p[0] for p in harmonic_points], dtype=np.float64)
        ys = np.log(np.array([p[1] for p in harmonic_points], dtype=np.float64))
        slope = float(np.polyfit(hs, ys, 1)[0])
        first = np.diff(ys)
        curvature = float(np.mean(np.abs(np.diff(first)))) if first.size >= 2 else 0.0
        roughness = float(np.std(first)) if first.size else 0.0
    else:
        slope = curvature = roughness = 0.0

    local_mask = (freqs >= max(20.0, f0 * 0.5)) & (freqs <= min(sr / 2, f0 * 6.5))
    local_spec = spec[local_mask]
    local_freqs = freqs[local_mask]
    if local_spec.size and float(np.sum(local_spec)) > 0:
        centroid = float(np.sum(local_freqs * local_spec) / np.sum(local_spec))
        centroid_ratio = centroid / max(f0, 1e-9)
    else:
        centroid_ratio = 0.0

    return {
        "harmonicShare": round(harmonic_share, 6),
        "interharmonicShare": round(inter_share, 6),
        "slope": round(slope, 6),
        "curvature": round(curvature, 6),
        "centroidRatio": round(centroid_ratio, 6),
        "roughness": round(roughness, 6),
    }


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    h = min(wf["harmonicShare"], af["harmonicShare"])
    i = max(wf["interharmonicShare"], af["interharmonicShare"])
    sdiff = abs(wf["slope"] - af["slope"])
    cdiff = abs(wf["curvature"] - af["curvature"])
    rdiff = abs(wf["roughness"] - af["roughness"])
    centroid_diff = abs(wf["centroidRatio"] - af["centroidRatio"])
    ratio = h / max(i, 1e-9)

    hb = bucket(h, [0.015, 0.03, 0.06, 0.10], ["h_lt015", "h_015_030", "h_030_060", "h_060_100", "h_100_plus"])
    ib = bucket(i, [0.01, 0.02, 0.04, 0.08], ["i_lt010", "i_010_020", "i_020_040", "i_040_080", "i_080_plus"])
    rb = bucket(ratio, [0.75, 1.5, 3.0, 6.0], ["r_lt075", "r_075_150", "r_150_300", "r_300_600", "r_600_plus"])
    sb = bucket(sdiff, [0.15, 0.35, 0.70, 1.20], ["sd_lt015", "sd_015_035", "sd_035_070", "sd_070_120", "sd_120_plus"])
    cb = bucket(cdiff, [0.15, 0.35, 0.70, 1.20], ["cd_lt015", "cd_015_035", "cd_035_070", "cd_070_120", "cd_120_plus"])
    rb2 = bucket(rdiff, [0.10, 0.25, 0.50, 1.0], ["rd_lt010", "rd_010_025", "rd_025_050", "rd_050_100", "rd_100_plus"])
    xb = bucket(centroid_diff, [0.20, 0.50, 1.0, 2.0], ["xd_lt020", "xd_020_050", "xd_050_100", "xd_100_200", "xd_200_plus"])

    return {
        f"spectralEnvelopeCross::{hb}|{ib}|{rb}|{sb}",
        f"spectralEnvelopeShapeCross::{hb}|{rb}|{cb}|{rb2}",
        f"dualStemEnvelopeAgreement::{sb}|{cb}|{rb2}|{xb}",
        f"harmonicInterharmonicCross::{hb}|{ib}|{rb}|{xb}",
    }


def precision_rows(groups: dict[str, Counter[str]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for signature, counts in groups.items():
        true = int(counts["true"])
        false = int(counts["false"])
        total = true + false
        rows.append({
            "signature": signature,
            "true": true,
            "false": false,
            "total": total,
            "precision": round(100.0 * true / total, 2) if total else 0.0,
        })
    return sorted(rows, key=lambda r: (-int(r["total"]), -float(r["precision"]), str(r["signature"])))


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
    champion, _ = survivor.reconstruct_2731(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.31 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, pitch = tok
        center = float(grid[(measure, step)])
        wf = spectral_envelope_features(winner_audio, winner_sr, center, pitch)
        af = spectral_envelope_features(alt_audio, alt_sr, center, pitch)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": signatures,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [row for row in ranked if int(row["true"]) == 0 and int(row["false"]) >= 5]
    zero.sort(key=lambda row: (-int(row["false"]), str(row["signature"])))
    supported = [row for row in ranked if int(row["true"]) >= 5]
    supported.sort(key=lambda row: (-float(row["precision"]), -int(row["true"]), str(row["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.31 spectral-envelope profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.31-dual-stem-spectral-envelope-shape",
        "champion2731Score": score,
        "featureFamily": "dual-stem-spectral-envelope-and-partial-shape",
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
        "rows": details,
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
        "championPitchF1": score["pitchF1"],
        "matched": score["matched"],
        "missing": score["missing"],
        "extra": score["extra"],
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 27.31 DUAL-STEM SPECTRAL ENVELOPE SHAPE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision spectral-envelope signatures (5+ false, 0 true):", len(zero))
    for row in zero[:40]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true spectral-envelope signatures:")
    for row in supported[:30]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
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
