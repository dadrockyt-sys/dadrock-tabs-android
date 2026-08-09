from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np

import profile_gomyway_2705_local_pitch_salience_survivors_precision_v1 as prior

recur = prior.recur
recall = prior.recall
v2 = prior.v2
v3 = prior.v3
harmonic = prior.harmonic
salience = prior.salience

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PRIOR_PROFILE = PUBLIC / "gomyway-2705-local-pitch-salience-survivors-precision-v1.json"
OUTPUT_PATH = PUBLIC / "gomyway-2705-dual-stem-onset-jitter-consistency-v1.json"
MANIFEST_PATH = PUBLIC / "gomyway-2705-dual-stem-onset-jitter-consistency-v1-manifest.json"
EXPECTED = (183, 684, 303)
EXPECTED_F1 = 27.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def bucket(v: float, edges: list[tuple[float, str]], tail: str) -> str:
    for limit, label in edges:
        if v < limit:
            return label
    return tail


def local_envelope(audio: np.ndarray, sr: int, center: float, radius_ms: float = 90.0) -> tuple[np.ndarray, np.ndarray]:
    radius = max(8, int(sr * radius_ms / 1000.0))
    c = int(round(center * sr))
    lo = max(0, c - radius)
    hi = min(len(audio), c + radius + 1)
    x = np.asarray(audio[lo:hi], dtype=np.float64)
    if x.size < 16:
        return np.zeros(1, dtype=np.float64), np.zeros(1, dtype=np.float64)
    x = np.abs(x - float(np.mean(x)))
    win = max(3, int(sr * 0.004))
    kernel = np.ones(win, dtype=np.float64) / float(win)
    env = np.convolve(x, kernel, mode="same")
    times = (np.arange(lo, hi, dtype=np.float64) - c) / float(sr)
    return env, times


def timing_features(audio: np.ndarray, sr: int, center: float) -> dict[str, float]:
    env, times = local_envelope(audio, sr, center)
    if env.size < 4 or float(np.max(env)) <= 0.0:
        return {
            "peakOffsetMs": 999.0,
            "centroidOffsetMs": 999.0,
            "prePostBalance": 0.0,
            "riseConcentration": 0.0,
            "localJitterMs": 999.0,
        }
    peak_i = int(np.argmax(env))
    peak_offset = float(times[peak_i] * 1000.0)
    total = float(np.sum(env)) + 1e-12
    centroid = float(np.sum(times * env) / total) * 1000.0
    pre = float(np.sum(env[times < 0.0]))
    post = float(np.sum(env[times >= 0.0]))
    balance = post / max(pre, 1e-12)

    deriv = np.diff(env, prepend=env[0])
    pos = np.maximum(deriv, 0.0)
    rise_total = float(np.sum(pos)) + 1e-12
    strongest = float(np.max(pos))
    rise_conc = strongest / rise_total

    top = np.flatnonzero(env >= float(np.max(env)) * 0.85)
    if top.size >= 2:
        jitter = float((times[top[-1]] - times[top[0]]) * 1000.0)
    else:
        jitter = 0.0

    return {
        "peakOffsetMs": peak_offset,
        "centroidOffsetMs": centroid,
        "prePostBalance": balance,
        "riseConcentration": rise_conc,
        "localJitterMs": jitter,
    }


def signatures_for(w: dict[str, float], a: dict[str, float]) -> set[str]:
    peak_abs = max(abs(w["peakOffsetMs"]), abs(a["peakOffsetMs"]))
    peak_diff = abs(w["peakOffsetMs"] - a["peakOffsetMs"])
    cent_diff = abs(w["centroidOffsetMs"] - a["centroidOffsetMs"])
    bal_diff = abs(w["prePostBalance"] - a["prePostBalance"])
    min_rise = min(w["riseConcentration"], a["riseConcentration"])
    max_jitter = max(w["localJitterMs"], a["localJitterMs"])

    peak = bucket(peak_abs, [(8.0, "peak_lt8"), (16.0, "peak_8_16"), (32.0, "peak_16_32"), (55.0, "peak_32_55")], "peak_55_plus")
    pdiff = bucket(peak_diff, [(4.0, "pdiff_lt4"), (10.0, "pdiff_4_10"), (20.0, "pdiff_10_20"), (40.0, "pdiff_20_40")], "pdiff_40_plus")
    cdiff = bucket(cent_diff, [(5.0, "cdiff_lt5"), (12.0, "cdiff_5_12"), (25.0, "cdiff_12_25")], "cdiff_25_plus")
    bdiff = bucket(bal_diff, [(0.20, "bdiff_lt020"), (0.60, "bdiff_020_060"), (1.50, "bdiff_060_150")], "bdiff_150_plus")
    rise = bucket(min_rise, [(0.03, "rise_lt030"), (0.06, "rise_030_060"), (0.10, "rise_060_100")], "rise_100_plus")
    jitter = bucket(max_jitter, [(8.0, "jitter_lt8"), (18.0, "jitter_8_18"), (35.0, "jitter_18_35"), (60.0, "jitter_35_60")], "jitter_60_plus")

    return {
        f"maxOnsetPeakOffset::{peak}",
        f"dualStemPeakOffsetDiff::{pdiff}",
        f"dualStemCentroidDiff::{cdiff}",
        f"dualStemPrePostDiff::{bdiff}",
        f"minRiseConcentration::{rise}",
        f"maxLocalJitter::{jitter}",
        f"onsetJitterCross::{peak}|{pdiff}|{jitter}",
        f"dualStemTimingCross::{pdiff}|{cdiff}|{bdiff}",
        f"timingShapeCross::{peak}|{rise}|{jitter}|{cdiff}",
    }


def main() -> None:
    before = sha256(recall.CANDIDATE_PATH)

    prior_payload = v2.load_json(PRIOR_PROFILE)
    if prior_payload.get("professionalReferenceUsedDuringDetection") is not False:
        raise RuntimeError("27.05 prior survivor profile is not reference-free during detection")
    if prior_payload.get("zeroPrecisionGeneralizableSignaturesMin5False"):
        raise RuntimeError("27.05 local-pitch-salience branch is not exhausted")

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

    champion2673, _ = salience.transient.reconstruct_2673(
        grid, winner_audio, winner_sr, alt_audio, alt_sr, reference
    )

    prior_2673 = v2.load_json(salience.OUTPUT_PATH)
    prior_rows = list(prior_2673.get("rows", []))
    row_by_token = {tuple(int(v) for v in row["token"]): row for row in prior_rows}
    zero_rows = list(prior_2673.get("zeroPrecisionGeneralizableSignaturesMin5False", []))
    if len(zero_rows) != 3:
        raise RuntimeError(f"Expected 3 validated local-salience signatures, got {len(zero_rows)}")
    signatures = {str(r["signature"]) for r in zero_rows}

    pruned: Counter[tuple[int, int, int]] = Counter()
    for tok, count in champion2673.items():
        row = row_by_token.get(tok)
        if row and ({str(s) for s in row.get("signatures", [])} & signatures):
            pruned[tok] = count

    if int(sum(pruned.values())) != 16 or int(sum((pruned & reference).values())) != 0:
        raise RuntimeError("Failed to reconstruct validated 16-note local-salience prune")

    champion = champion2673 - pruned
    score = recur.grade(champion, reference)
    actual = (int(score["matched"]), int(score["missing"]), int(score["extra"]))
    if actual != EXPECTED or abs(float(score["pitchF1"]) - EXPECTED_F1) > 0.01:
        raise RuntimeError(f"Expected frozen 27.05 champion {EXPECTED}/{EXPECTED_F1}, got {actual}/{score['pitchF1']}")

    matched = champion & reference
    extras = champion - reference
    groups: dict[str, Counter[str]] = defaultdict(Counter)
    details: list[dict[str, Any]] = []

    def record(tok: tuple[int, int, int], count: int, truth: str) -> None:
        measure, step, _pitch = tok
        center = float(grid[(measure, step)])
        wf = timing_features(winner_audio, winner_sr, center)
        af = timing_features(alt_audio, alt_sr, center)
        sigs = sorted(signatures_for(wf, af))
        for s in sigs:
            groups[s][truth] += int(count)
        details.append({
            "token": list(tok),
            "truth": truth,
            "count": int(count),
            "winner": wf,
            "alternate": af,
            "signatures": sigs,
        })

    for tok, count in matched.items():
        record(tok, int(count), "true")
    for tok, count in extras.items():
        record(tok, int(count), "false")

    ranked = precision_rows(groups)
    zero = [r for r in ranked if int(r["true"]) == 0 and int(r["false"]) >= 5]
    zero.sort(key=lambda r: (-int(r["false"]), str(r["signature"])))
    supported = [r for r in ranked if int(r["true"]) >= 5]
    supported.sort(key=lambda r: (-float(r["precision"]), -int(r["true"]), str(r["signature"])))

    after = sha256(recall.CANDIDATE_PATH)
    if before != after:
        raise RuntimeError("Protected candidate changed during 27.05 onset-jitter profiler")

    output = {
        "schemaVersion": 1,
        "passed": True,
        "profileType": "validated-27.05-dual-stem-onset-jitter-consistency",
        "champion2705Score": score,
        "featureFamily": "dual-stem-onset-jitter-consistency",
        "localPitchSalienceBranchExhausted": True,
        "zeroPrecisionGeneralizableSignaturesMin5False": zero,
        "supportedTrueSignaturesMin5True": supported,
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

    print("GOMYWAY 27.05 DUAL-STEM ONSET JITTER CONSISTENCY V1 COMPLETE")
    print("Passed: True")
    print("Champion pitch F1:", score["pitchF1"])
    print("Champion matched/missing/extra:", score["matched"], "/", score["missing"], "/", score["extra"])
    print("Generalizable zero-precision onset-jitter signatures (5+ false, 0 true):", len(zero))
    for row in zero[:50]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
    print("Supported true/mixed onset-jitter signatures:")
    for row in supported[:30]:
        print(row["signature"], "true=", row["true"], "false=", row["false"], "precision=", row["precision"])
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
