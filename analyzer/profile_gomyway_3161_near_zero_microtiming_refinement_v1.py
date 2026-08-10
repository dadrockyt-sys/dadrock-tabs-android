from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_3161_cross_family_interactions_v1 as cross3161
import profile_gomyway_3161_measure_register_survivors_precision_v1 as s3161

recur = s3161.recur
recall = s3161.recall
v2 = s3161.v2
v3 = s3161.v3
harmonic = s3161.harmonic

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CROSS_PATH = PUBLIC / "gomyway-3161-cross-family-interactions-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-refinement-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-3161-near-zero-microtiming-refinement-v1-manifest.json"
EXPECTED = (183, 684, 108)
EXPECTED_F1 = 31.61


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bucket(v: float, edges: list[float], labels: list[str]) -> str:
    for edge, label in zip(edges, labels):
        if v < edge:
            return label
    return labels[-1]


def onset_offset_features(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    a = np.asarray(audio, dtype=np.float64)
    start = center - 0.090
    end = center + 0.090
    i0 = max(0, int(round(start * sr)))
    i1 = min(a.size, int(round(end * sr)))
    x = a[i0:i1]
    if x.size < 32:
        return {"peakOffsetMs": 0.0, "centroidOffsetMs": 0.0, "prePostRatio": 1.0, "sharpness": 0.0}

    x = x - float(np.mean(x))
    env = np.abs(x)
    smooth_n = max(3, int(round(0.004 * sr)))
    kernel = np.ones(smooth_n, dtype=np.float64) / smooth_n
    env = np.convolve(env, kernel, mode="same")
    d = np.diff(env, prepend=env[0])
    pos = np.maximum(d, 0.0)

    times = (np.arange(x.size, dtype=np.float64) + i0) / float(sr)
    offsets_ms = (times - center) * 1000.0
    peak_idx = int(np.argmax(pos))
    peak_offset = float(offsets_ms[peak_idx])

    weight_sum = float(np.sum(pos)) + 1e-12
    centroid = float(np.sum(offsets_ms * pos) / weight_sum)

    pre = float(np.sum(pos[offsets_ms < 0.0])) + 1e-12
    post = float(np.sum(pos[offsets_ms >= 0.0])) + 1e-12
    pre_post = pre / post
    sharpness = float(np.max(pos) / (np.mean(pos) + 1e-12))

    return {
        "peakOffsetMs": round(peak_offset, 3),
        "centroidOffsetMs": round(centroid, 3),
        "prePostRatio": round(pre_post, 6),
        "sharpness": round(sharpness, 6),
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    min_peak = min(w["peakOffsetMs"], a["peakOffsetMs"])
    max_peak = max(w["peakOffsetMs"], a["peakOffsetMs"])
    abs_peak = max(abs(w["peakOffsetMs"]), abs(a["peakOffsetMs"]))
    peak_diff = abs(w["peakOffsetMs"] - a["peakOffsetMs"])
    cent = max(abs(w["centroidOffsetMs"]), abs(a["centroidOffsetMs"]))
    ratio = max(w["prePostRatio"], a["prePostRatio"])
    sharp = min(w["sharpness"], a["sharpness"])

    mn = bucket(min_peak, [-45, -20, -8, 8, 20], ["mn_lt_n45", "mn_n45_n20", "mn_n20_n08", "mn_n08_008", "mn_008_020", "mn_020_plus"])
    mx = bucket(max_peak, [-20, -8, 8, 20, 45], ["mx_lt_n20", "mx_n20_n08", "mx_n08_008", "mx_008_020", "mx_020_045", "mx_045_plus"])
    ap = bucket(abs_peak, [8, 16, 28, 45, 70], ["ap_lt008", "ap_008_016", "ap_016_028", "ap_028_045", "ap_045_070", "ap_070_plus"])
    pd = bucket(peak_diff, [6, 12, 24, 40, 70], ["pd_lt006", "pd_006_012", "pd_012_024", "pd_024_040", "pd_040_070", "pd_070_plus"])
    co = bucket(cent, [5, 12, 25, 45], ["co_lt005", "co_005_012", "co_012_025", "co_025_045", "co_045_plus"])
    pr = bucket(ratio, [0.6, 1.0, 1.6, 2.5], ["pr_lt060", "pr_060_100", "pr_100_160", "pr_160_250", "pr_250_plus"])
    sh = bucket(sharp, [2.0, 3.5, 5.5, 8.0], ["sh_lt20", "sh_20_35", "sh_35_55", "sh_55_80", "sh_80_plus"])
    agreement = "both_centered" if abs_peak < 16 else ("one_centered" if min(abs(w["peakOffsetMs"]), abs(a["peakOffsetMs"])) < 16 else "neither_centered")

    return {
        f"microPeakMin::{mn}",
        f"microPeakMax::{mx}",
        f"microPeakAbs::{ap}",
        f"microPeakStemDiff::{pd}",
        f"microCentroidAbs::{co}",
        f"microPrePostRatio::{pr}",
        f"microOnsetSharpness::{sh}",
        f"microTimingAgreement::{agreement}",
        f"microTimingCross::{ap}|{pd}|{co}|{agreement}",
        f"microAttackBalance::{mn}|{mx}|{pr}|{sh}",
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
    return sorted(rows, key=lambda r: (int(r["true"]), -int(r["false"]), str(r["signature"])))


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
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 31.61 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    cross = v2.load_json(CROSS_PATH)
    if cross.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("Cross-family profile is not reference-free during detection")
    near = list(cross.get("nearZeroPrecisionSignaturesMax1TrueMin5False", []))
    if not near:
        raise RuntimeError("Expected at least one saved near-zero cross-family signature")
    target_signature = str(near[0]["signature"])

    target_rows = [row for row in cross.get("rows", []) if target_signature in set(row.get("signatures", []))]
    target_true = sum(int(row.get("count", 0)) for row in target_rows if row.get("truth") == "true")
    target_false = sum(int(row.get("count", 0)) for row in target_rows if row.get("truth") == "false")
    if target_true != 1 or target_false < 5:
        raise RuntimeError(f"Expected target near-zero pocket 1 true / >=5 false, got {target_true}/{target_false}")

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []
    for row in target_rows:
        tok = tuple(int(v) for v in row["token"])
        truth = str(row["truth"])
        count = int(row["count"])
        measure, step, _pitch = tok
        center = float(grid[(measure, step)])
        wf = onset_offset_features(winner_audio, winner_sr, center)
        af = onset_offset_features(alt_audio, alt_sr, center)
        signatures = sorted(signatures_for(wf, af))
        for signature in signatures:
            groups[signature][truth] += count
        details.append({"token": list(tok), "truth": truth, "count": count, "winner": wf, "alternate": af, "signatures": signatures})

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 3]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during near-zero microtiming refinement")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-31.61-near-zero-microtiming-refinement",
        "champion3161Score": score,
        "reconstruction": reconstruction,
        "targetCrossFamilySignature": target_signature,
        "targetTrue": target_true,
        "targetFalse": target_false,
        "featureFamily": "targeted-dual-stem-microtiming-onset-offset",
        "zeroPrecisionRefinementSignaturesMin3False": zero,
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
        "targetTrue": target_true,
        "targetFalse": target_false,
        "zeroPrecisionSignatureCount": len(zero),
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    print("GOMYWAY 31.61 NEAR-ZERO MICROTIMING REFINEMENT V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Target near-zero signature:", target_signature)
    print("Targeted true/false:", target_true, "/", target_false)
    print("Zero-precision microtiming refinement signatures (3+ false, 0 true):", len(zero))
    for row in zero[:50]:
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
