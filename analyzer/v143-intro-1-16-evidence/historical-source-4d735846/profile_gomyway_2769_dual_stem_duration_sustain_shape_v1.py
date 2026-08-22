from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2769_spectral_envelope_survivors_precision_v1 as survivor

recur = survivor.recur
recall = survivor.recall
v2 = survivor.v2
v3 = survivor.v3
harmonic = survivor.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
OUTPUT_PATH = PUBLIC / "gomyway-2769-dual-stem-duration-sustain-shape-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2769-dual-stem-duration-sustain-shape-v1-manifest.json"
EXPECTED = (183, 684, 272)
EXPECTED_F1 = 27.69


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(value: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if value < edge:
            return label
    return labels[-1]


def duration_features(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    pre = 0.06
    post = 0.42
    start = max(0, int((center - pre) * sr))
    end = min(len(audio), int((center + post) * sr))
    x = np.asarray(audio[start:end], dtype=np.float64)
    if x.size < 64:
        return {
            "duration": 0.0,
            "sustainShare": 0.0,
            "decayRatio": 0.0,
            "releaseSharpness": 0.0,
            "tailShare": 0.0,
        }

    x = x - float(np.mean(x))
    frame = max(32, int(0.012 * sr))
    hop = max(16, int(0.006 * sr))
    env: list[float] = []
    for i in range(0, max(1, x.size - frame + 1), hop):
        seg = x[i:i + frame]
        if seg.size < frame:
            break
        env.append(float(np.sqrt(np.mean(seg * seg) + 1e-12)))
    if not env:
        return {
            "duration": 0.0,
            "sustainShare": 0.0,
            "decayRatio": 0.0,
            "releaseSharpness": 0.0,
            "tailShare": 0.0,
        }

    e = np.asarray(env, dtype=np.float64)
    peak_idx = int(np.argmax(e))
    peak = float(e[peak_idx]) + 1e-12
    norm = e / peak

    threshold = 0.22
    active = np.where(norm[peak_idx:] >= threshold)[0]
    if active.size:
        last = peak_idx + int(active[-1])
        duration = (last - peak_idx + 1) * hop / sr
    else:
        duration = 0.0

    post_env = norm[peak_idx:]
    n = max(1, post_env.size)
    first_end = min(n, max(1, int(round(0.08 * sr / hop))))
    mid_start = min(n, max(0, int(round(0.08 * sr / hop))))
    mid_end = min(n, max(mid_start + 1, int(round(0.20 * sr / hop))))
    tail_start = min(n, max(0, int(round(0.22 * sr / hop))))

    early = float(np.mean(post_env[:first_end])) if first_end else 0.0
    mid = float(np.mean(post_env[mid_start:mid_end])) if mid_end > mid_start else 0.0
    tail = float(np.mean(post_env[tail_start:])) if tail_start < n else 0.0
    sustain_share = mid / max(early, 1e-9)
    tail_share = tail / max(early, 1e-9)
    decay_ratio = (early - tail) / max(early, 1e-9)

    if post_env.size >= 3:
        diffs = np.diff(post_env)
        release_sharpness = float(max(0.0, -np.min(diffs)))
    else:
        release_sharpness = 0.0

    return {
        "duration": round(float(duration), 6),
        "sustainShare": round(float(sustain_share), 6),
        "decayRatio": round(float(decay_ratio), 6),
        "releaseSharpness": round(float(release_sharpness), 6),
        "tailShare": round(float(tail_share), 6),
    }


def signatures_for(wf: dict[str, float], af: dict[str, float]) -> set[str]:
    dur_min = min(wf["duration"], af["duration"])
    dur_max = max(wf["duration"], af["duration"])
    dur_diff = abs(wf["duration"] - af["duration"])
    sustain_min = min(wf["sustainShare"], af["sustainShare"])
    sustain_diff = abs(wf["sustainShare"] - af["sustainShare"])
    decay_max = max(wf["decayRatio"], af["decayRatio"])
    release_max = max(wf["releaseSharpness"], af["releaseSharpness"])
    tail_min = min(wf["tailShare"], af["tailShare"])

    dmin = bucket(dur_min, [0.04, 0.08, 0.14, 0.24], ["dmin_lt040", "dmin_040_080", "dmin_080_140", "dmin_140_240", "dmin_240_plus"])
    dmax = bucket(dur_max, [0.06, 0.12, 0.22, 0.36], ["dmax_lt060", "dmax_060_120", "dmax_120_220", "dmax_220_360", "dmax_360_plus"])
    dd = bucket(dur_diff, [0.03, 0.07, 0.14, 0.24], ["dd_lt030", "dd_030_070", "dd_070_140", "dd_140_240", "dd_240_plus"])
    sm = bucket(sustain_min, [0.18, 0.32, 0.50, 0.72], ["smin_lt018", "smin_018_032", "smin_032_050", "smin_050_072", "smin_072_plus"])
    sd = bucket(sustain_diff, [0.10, 0.22, 0.40, 0.65], ["sd_lt010", "sd_010_022", "sd_022_040", "sd_040_065", "sd_065_plus"])
    dec = bucket(decay_max, [0.25, 0.45, 0.65, 0.82], ["dec_lt025", "dec_025_045", "dec_045_065", "dec_065_082", "dec_082_plus"])
    rel = bucket(release_max, [0.08, 0.16, 0.28, 0.45], ["rel_lt008", "rel_008_016", "rel_016_028", "rel_028_045", "rel_045_plus"])
    tail = bucket(tail_min, [0.08, 0.18, 0.32, 0.50], ["tail_lt008", "tail_008_018", "tail_018_032", "tail_032_050", "tail_050_plus"])

    return {
        f"durationCross::{dmin}|{dmax}|{dd}|{sm}",
        f"sustainShapeCross::{sm}|{sd}|{dec}|{tail}",
        f"releaseDecayCross::{dec}|{rel}|{tail}|{dd}",
        f"dualStemDurationAgreement::{dmin}|{dd}|{sd}|{tail}",
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
    champion, _ = survivor.reconstruct_2769(grid, winner_audio, winner_sr, alt_audio, alt_sr, reference)
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.69 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, _pitch = tok
        center = float(grid[(measure, step)])
        wf = duration_features(winner_audio, winner_sr, center)
        af = duration_features(alt_audio, alt_sr, center)
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
        raise RuntimeError("Protected candidate changed during 27.69 duration/sustain-shape profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.69-dual-stem-duration-sustain-shape",
        "champion2769Score": score,
        "featureFamily": "dual-stem-event-duration-sustain-decay-release-shape",
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

    print("GOMYWAY 27.69 DUAL-STEM DURATION SUSTAIN SHAPE V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision duration/sustain signatures (5+ false, 0 true):", len(zero))
    for row in zero[:40]:
        print(f"{row['signature']}: true={row['true']} false={row['false']} precision={row['precision']}")
    print("Top supported-true duration/sustain signatures:")
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
